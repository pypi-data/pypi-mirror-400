"""High-level Spartan client API.

Provides a simple async/await interface for making Spartan requests.
"""

import asyncio
from types import TracebackType

from ..protocol.response import SpartanResponse
from ..utils.url import parse_url, validate_url
from .protocol import SpartanClientProtocol


class SpartanClient:
    """High-level Spartan client with async/await API.

    This class provides a simple, high-level interface for making
    Spartan requests. Handles connection management and timeouts.

    Spartan is plaintext by default (no TLS, no TOFU).

    Examples:
        >>> # Basic usage
        >>> async with SpartanClient() as client:
        ...     response = await client.get("spartan://example.com/")
        ...     print(response.body)

        >>> # With custom timeout
        >>> client = SpartanClient(timeout=60)
        >>> response = await client.get("spartan://example.com/")

        >>> # Upload content
        >>> response = await client.upload(
        ...     "spartan://example.com/file.txt",
        ...     b"Hello, world!"
        ... )
    """

    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize the Spartan client.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout

    async def __aenter__(self) -> "SpartanClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        pass

    async def get(self, url: str) -> SpartanResponse:
        """Get a Spartan resource.

        Args:
            url: The Spartan URL to get.

        Returns:
            A SpartanResponse with status, meta, and optional body.

        Raises:
            ValueError: If the URL is invalid.
            TimeoutError: If the request times out.
            ConnectionError: If the connection fails.

        Examples:
            >>> response = await client.get("spartan://example.com/")
            >>> if response.is_success():
            ...     print(response.body)
        """
        validate_url(url)
        return await self._request(url, b"")

    async def upload(
        self,
        url: str,
        content: bytes | str,
    ) -> SpartanResponse:
        """Upload content to a Spartan server.

        Spartan integrates upload into the core protocol
        (content-length > 0 in the request).

        Args:
            url: The target URL.
            content: The content to upload.

        Returns:
            A SpartanResponse indicating success or failure.

        Raises:
            ValueError: If the URL is invalid.
            TimeoutError: If the request times out.
            ConnectionError: If the connection fails.

        Examples:
            >>> response = await client.upload(
            ...     "spartan://example.com/file.txt",
            ...     "Hello, world!"
            ... )
        """
        validate_url(url)

        # Convert content to bytes
        if isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content

        return await self._request(url, content_bytes)

    async def query(
        self,
        url: str,
        query: str,
    ) -> SpartanResponse:
        """Send a query to a Spartan server.

        In Spartan, queries are sent as the data block (like uploads).

        Args:
            url: The target URL.
            query: The query string.

        Returns:
            A SpartanResponse.

        Examples:
            >>> response = await client.query(
            ...     "spartan://example.com/search",
            ...     "hello world"
            ... )
        """
        return await self.upload(url, query)

    async def _request(self, url: str, content: bytes) -> SpartanResponse:
        """Make a Spartan request.

        Args:
            url: The target URL.
            content: Content to send (empty for GET).

        Returns:
            A SpartanResponse.
        """
        parsed = parse_url(url)

        loop = asyncio.get_running_loop()
        response_future: asyncio.Future[SpartanResponse] = loop.create_future()

        # Create protocol
        protocol = SpartanClientProtocol(
            hostname=parsed.hostname,
            path=parsed.path,
            content=content,
            response_future=response_future,
        )

        # Connect
        try:
            transport, _ = await asyncio.wait_for(
                loop.create_connection(
                    lambda: protocol,
                    host=parsed.hostname,
                    port=parsed.port,
                ),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Connection timeout: {url}") from e
        except OSError as e:
            raise ConnectionError(f"Connection failed: {e}") from e

        # Wait for response
        try:
            response = await asyncio.wait_for(
                response_future,
                timeout=self.timeout,
            )
            response = SpartanResponse(
                status=response.status,
                meta=response.meta,
                body=response.body,
                url=url,
            )
            return response
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Request timeout: {url}") from e
        finally:
            transport.close()


async def get(url: str, timeout: float = 30.0) -> SpartanResponse:
    """Convenience function to get a Spartan URL.

    Args:
        url: The Spartan URL to get.
        timeout: Request timeout in seconds.

    Returns:
        A SpartanResponse.

    Examples:
        >>> response = await teyaotlani.get("spartan://example.com/")
    """
    async with SpartanClient(timeout=timeout) as client:
        return await client.get(url)


async def upload(
    url: str,
    content: bytes | str,
    timeout: float = 30.0,
) -> SpartanResponse:
    """Convenience function to upload content.

    Args:
        url: The target URL.
        content: The content to upload.
        timeout: Request timeout in seconds.

    Returns:
        A SpartanResponse.
    """
    async with SpartanClient(timeout=timeout) as client:
        return await client.upload(url, content)
