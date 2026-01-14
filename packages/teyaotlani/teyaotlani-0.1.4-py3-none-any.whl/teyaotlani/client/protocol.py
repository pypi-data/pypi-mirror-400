"""Low-level Spartan client protocol implementation.

Uses asyncio Protocol/Transport pattern for efficient I/O.
"""

import asyncio

from ..protocol.constants import CRLF
from ..protocol.response import SpartanResponse
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Maximum response body size (100 MB)
MAX_RESPONSE_BODY_SIZE = 100 * 1024 * 1024


class SpartanClientProtocol(asyncio.Protocol):
    """Client-side protocol for making Spartan requests.

    This class implements asyncio.Protocol for handling client connections.

    The protocol flow:
    1. Connection established
    2. Send: host path content-length CRLF [content]
    3. Receive: status meta CRLF [body]
    4. Connection closes
    """

    def __init__(
        self,
        hostname: str,
        path: str,
        content: bytes,
        response_future: asyncio.Future[SpartanResponse],
    ) -> None:
        """Initialize the client protocol.

        Args:
            hostname: Target hostname.
            path: Request path.
            content: Content to send (empty for GET requests).
            response_future: Future to resolve with the response.
        """
        self.hostname = hostname
        self.path = path
        self.content = content
        self.response_future = response_future

        self.transport: asyncio.Transport | None = None
        self.buffer = b""
        self.header_received = False
        self.status: int | None = None
        self.meta: str | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called when connection is established.

        Immediately sends the request.

        Args:
            transport: The transport for this connection.
        """
        self.transport = transport  # type: ignore[assignment]
        assert self.transport is not None

        # Build and send request
        content_length = len(self.content)
        request_line = f"{self.hostname} {self.path} {content_length}\r\n"

        self.transport.write(request_line.encode("ascii"))

        if self.content:
            self.transport.write(self.content)

        logger.debug(
            "request_sent",
            hostname=self.hostname,
            path=self.path,
            content_length=content_length,
        )

    def data_received(self, data: bytes) -> None:
        """Called when data is received from server.

        Args:
            data: Raw bytes received.
        """
        self.buffer += data

        # Parse header if not yet received
        if not self.header_received and CRLF in self.buffer:
            header_line, body = self.buffer.split(CRLF, 1)
            self._parse_header(header_line.decode("ascii"))
            self.buffer = body
            self.header_received = True

            # Non-success responses typically have no body
            # but we still wait for connection to close

        # Prevent memory exhaustion
        if len(self.buffer) > MAX_RESPONSE_BODY_SIZE:
            self._set_error(Exception("Response body too large"))
            if self.transport:
                self.transport.close()

    def _parse_header(self, header_line: str) -> None:
        """Parse the response header line.

        Args:
            header_line: The header line (status meta).
        """
        parts = header_line.split(" ", 1)

        try:
            self.status = int(parts[0])
        except ValueError:
            self._set_error(ValueError(f"Invalid status code: {parts[0]}"))
            return

        self.meta = parts[1] if len(parts) > 1 else ""

        # Validate status code
        if self.status not in (2, 3, 4, 5):
            self._set_error(ValueError(f"Invalid status code: {self.status}"))

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when connection is closed.

        Delivers the response via the future.

        Args:
            exc: Exception if connection was lost due to error.
        """
        if self.response_future.done():
            return

        if exc:
            self.response_future.set_exception(exc)
            return

        if self.status is None:
            self.response_future.set_exception(
                ValueError("Connection closed before receiving response")
            )
            return

        # Decode body for success responses
        body: str | bytes | None = None
        if self.status == 2 and self.buffer:
            mime_type = (self.meta or "").split(";")[0].strip().lower()
            is_text = mime_type.startswith("text/") or mime_type == ""

            if is_text:
                # Parse charset from meta
                charset = "utf-8"
                if ";" in (self.meta or ""):
                    for part in self.meta.split(";")[1:]:  # type: ignore[union-attr]
                        key_value = part.strip().split("=", 1)
                        if len(key_value) == 2:
                            key, value = key_value
                            if key.strip().lower() == "charset":
                                charset = value.strip()
                                break

                try:
                    body = self.buffer.decode(charset)
                except UnicodeDecodeError:
                    body = self.buffer  # Fall back to bytes
            else:
                body = self.buffer
        elif self.buffer:
            # Non-success responses might have body
            try:
                body = self.buffer.decode("utf-8")
            except UnicodeDecodeError:
                body = self.buffer

        response = SpartanResponse(
            status=self.status,
            meta=self.meta or "",
            body=body,
        )

        self.response_future.set_result(response)

    def _set_error(self, error: Exception) -> None:
        """Set an error on the response future.

        Args:
            error: The exception to set.
        """
        if not self.response_future.done():
            self.response_future.set_exception(error)
