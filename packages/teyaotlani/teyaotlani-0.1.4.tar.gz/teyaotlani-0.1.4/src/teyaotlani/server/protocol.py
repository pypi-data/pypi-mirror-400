"""Low-level Spartan server protocol implementation.

This module implements the Spartan server protocol using asyncio's
Protocol/Transport pattern for efficient, non-blocking I/O.

Spartan protocol:
- Request: host SP path SP content-length CRLF [data]
- Response: status SP meta CRLF [body]
- Plaintext (no TLS by default)
- ASCII encoding for headers
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from ..protocol.constants import CRLF, MAX_REQUEST_SIZE, REQUEST_TIMEOUT
from ..protocol.request import SpartanRequest
from ..protocol.response import SpartanResponse
from ..protocol.status import StatusCode
from ..utils.logging import get_logger

if TYPE_CHECKING:
    from .middleware import MiddlewareChain

logger = get_logger(__name__)


class SpartanServerProtocol(asyncio.Protocol):
    """Server-side protocol for handling Spartan requests.

    This class implements asyncio.Protocol for handling server connections.
    It manages the connection lifecycle, receives requests, and sends responses.

    The protocol flow:
    1. Client connects (plaintext TCP by default)
    2. Client sends: host path content-length CRLF
    3. If content-length > 0: Client sends content bytes
    4. Server sends: status meta CRLF
    5. If status is 2: Server sends response body
    6. Connection closes

    Attributes:
        request_handler: Callback function that takes a SpartanRequest and
            returns a SpartanResponse.
        middleware: Optional middleware chain for request processing.
        transport: The transport handling the connection.
        buffer: Buffer for accumulating incoming data.
        peer_name: Remote peer address information.
    """

    def __init__(
        self,
        request_handler: Callable[
            [SpartanRequest], SpartanResponse | Awaitable[SpartanResponse]
        ],
        middleware: "MiddlewareChain | None" = None,
    ) -> None:
        """Initialize the server protocol.

        Args:
            request_handler: Callback that processes requests and returns responses.
                Can be sync or async.
            middleware: Optional middleware chain for request processing.
        """
        self.request_handler = request_handler
        self.middleware = middleware
        self.transport: asyncio.Transport | None = None
        self.buffer = b""
        self.peer_name: tuple[str, int] | None = None
        self.request_start_time: float | None = None
        self.timeout_handle: asyncio.TimerHandle | None = None

        # Request parsing state
        self.request: SpartanRequest | None = None
        self.request_line_received = False

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when a client connects.

        Args:
            transport: The transport handling this connection.
        """
        self.transport = transport  # type: ignore[assignment]
        if self.transport:
            self.peer_name = self.transport.get_extra_info("peername")
        self.request_start_time = time.time()

        # Set timeout for receiving request
        try:
            loop = asyncio.get_running_loop()
            self.timeout_handle = loop.call_later(REQUEST_TIMEOUT, self._handle_timeout)
        except RuntimeError:
            # No event loop running (probably in tests)
            self.timeout_handle = None

        logger.debug(
            "connection_established",
            client_ip=self.peer_name[0] if self.peer_name else "unknown",
            client_port=self.peer_name[1] if self.peer_name else 0,
        )

    def data_received(self, data: bytes) -> None:
        """Called when data is received from the client.

        This method may be called multiple times as data arrives. We accumulate
        data in a buffer until we receive a complete request.

        Spartan request: host path content-length CRLF [data]

        Args:
            data: Raw bytes received from the client.
        """
        self.buffer += data

        # State 1: Waiting for request line
        if not self.request_line_received:
            # DoS protection: Check buffer size without CRLF
            if len(self.buffer) > MAX_REQUEST_SIZE and CRLF not in self.buffer:
                self._send_error_response(
                    StatusCode.CLIENT_ERROR, "Request exceeds maximum size"
                )
                return

            # Check if we have a complete request line
            if CRLF in self.buffer:
                request_line, remaining = self.buffer.split(CRLF, 1)

                # Check request line size
                if len(request_line) + 2 > MAX_REQUEST_SIZE:
                    self._send_error_response(
                        StatusCode.CLIENT_ERROR, "Request exceeds maximum size"
                    )
                    return

                self.buffer = remaining
                self.request_line_received = True

                # Parse request line (ASCII)
                try:
                    line = request_line.decode("ascii")
                except UnicodeDecodeError:
                    self._send_error_response(
                        StatusCode.CLIENT_ERROR, "Invalid ASCII encoding in request"
                    )
                    return

                try:
                    self.request = SpartanRequest.from_line(line)
                except ValueError as e:
                    self._send_error_response(StatusCode.CLIENT_ERROR, str(e))
                    return

                # If no content expected, process immediately
                if self.request.content_length == 0:
                    self._cancel_timeout()
                    self._process_request()
                    return

        # State 2: Accumulating content bytes
        if self.request_line_received and self.request:
            if len(self.buffer) >= self.request.content_length:
                self._cancel_timeout()

                # Extract exactly the expected bytes
                self.request.content = self.buffer[: self.request.content_length]
                self._process_request()

    def _process_request(self) -> None:
        """Process the complete Spartan request."""
        if not self.request:
            return

        client_ip = self.peer_name[0] if self.peer_name else "unknown"

        # Process through middleware if present
        if self.middleware:
            try:
                loop = asyncio.get_running_loop()
                task = loop.create_task(
                    self.middleware.process_request(
                        f"spartan://{self.request.hostname}{self.request.path}",
                        client_ip,
                    )
                )
                task.add_done_callback(
                    lambda t: self._handle_middleware_result(t, client_ip)
                )
                return
            except RuntimeError:
                logger.warning("middleware_skipped", reason="no_event_loop")

        # No middleware - route directly
        self._route_request(client_ip)

    def _handle_middleware_result(
        self, task: asyncio.Task[tuple[bool, str | None]], client_ip: str
    ) -> None:
        """Handle middleware processing result.

        Args:
            task: The completed middleware task.
            client_ip: Client IP address for logging.
        """
        try:
            allow, error_response = task.result()

            if not allow:
                if self.transport and error_response:
                    self.transport.write(error_response.encode("ascii"))
                    self.transport.close()
                return

            self._route_request(client_ip)

        except Exception as e:
            logger.error("middleware_error", client_ip=client_ip, error=str(e))
            self._send_error_response(StatusCode.SERVER_ERROR, "Middleware error")

    def _route_request(self, client_ip: str) -> None:
        """Route request to handler and send response.

        Args:
            client_ip: Client IP address for logging.
        """
        if not self.request:
            return

        try:
            result = self.request_handler(self.request)

            # Check if async handler
            if asyncio.iscoroutine(result):
                try:
                    loop = asyncio.get_running_loop()
                    task = loop.create_task(result)
                    task.add_done_callback(
                        lambda t: self._handle_async_result(t, client_ip)
                    )
                    return
                except RuntimeError:
                    self._send_error_response(
                        StatusCode.SERVER_ERROR, "Async handler requires event loop"
                    )
                    return

            # Sync handler - send response directly
            # Type narrowing: after iscoroutine check, result is SpartanResponse
            assert isinstance(result, SpartanResponse)
            self._send_response(result)

        except Exception as e:
            logger.error("handler_error", client_ip=client_ip, error=str(e))
            self._send_error_response(StatusCode.SERVER_ERROR, f"Server error: {e}")

    def _handle_async_result(
        self, task: asyncio.Task[SpartanResponse], client_ip: str
    ) -> None:
        """Handle async handler result.

        Args:
            task: The completed handler task.
            client_ip: Client IP address for logging.
        """
        try:
            response = task.result()
            self._send_response(response)
        except Exception as e:
            logger.error("async_handler_error", client_ip=client_ip, error=str(e))
            self._send_error_response(StatusCode.SERVER_ERROR, f"Handler error: {e}")

    def _send_response(self, response: SpartanResponse) -> None:
        """Send SpartanResponse to client.

        Args:
            response: The response to send.
        """
        if not self.transport:
            return

        # Calculate duration
        duration_ms = 0.0
        if self.request_start_time:
            duration_ms = (time.time() - self.request_start_time) * 1000

        # Log request
        logger.info(
            "request_completed",
            client_ip=self.peer_name[0] if self.peer_name else "unknown",
            status=response.status,
            path=self.request.path if self.request else "unknown",
            content_length=self.request.content_length if self.request else 0,
            body_size=len(response.body) if response.body else 0,
            duration_ms=round(duration_ms, 2),
        )

        # Send response
        self.transport.write(response.to_bytes())
        self.transport.close()

    def _send_error_response(self, status: StatusCode, message: str) -> None:
        """Send error response and close connection.

        Args:
            status: The error status code.
            message: The error message.
        """
        response = SpartanResponse(status=status.value, meta=message)
        self._send_response(response)

    def _cancel_timeout(self) -> None:
        """Cancel the request timeout."""
        if self.timeout_handle:
            self.timeout_handle.cancel()
            self.timeout_handle = None

    def _handle_timeout(self) -> None:
        """Handle request timeout."""
        if self.transport and not self.transport.is_closing():
            logger.warning(
                "request_timeout",
                client_ip=self.peer_name[0] if self.peer_name else "unknown",
            )
            response = b"5 Request timeout\r\n"
            self.transport.write(response)
            self.transport.close()

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when the connection is closed.

        Args:
            exc: Exception if connection was lost due to error.
        """
        self._cancel_timeout()
        self.transport = None

        if exc:
            logger.debug(
                "connection_lost",
                client_ip=self.peer_name[0] if self.peer_name else "unknown",
                error=str(exc),
            )
