"""Spartan protocol request representation.

Spartan request format: host SP path SP content-length CRLF [data]
"""

from dataclasses import dataclass, field


@dataclass
class SpartanRequest:
    """Represents a Spartan protocol request.

    Request format: host SP path SP content-length CRLF [data-block]

    Unlike Gemini which sends a full URL, Spartan sends:
    - hostname (no scheme, no port)
    - absolute path (starting with /)
    - content length in bytes

    Attributes:
        hostname: Target hostname (no scheme, no port).
        path: Absolute path starting with /.
        content_length: Size of content in bytes (0 for GET requests).
        content: Optional data block (for queries/uploads).

    Examples:
        >>> request = SpartanRequest.from_line("example.com /index.gmi 0")
        >>> request.hostname
        'example.com'
        >>> request.path
        '/index.gmi'
        >>> request.is_upload
        False
    """

    hostname: str
    path: str
    content_length: int
    content: bytes = field(default=b"", repr=False)

    @classmethod
    def from_line(cls, line: str) -> "SpartanRequest":
        """Parse a Spartan request from a request line.

        Args:
            line: The request line (without CRLF).
                  Format: "host path content-length"

        Returns:
            A SpartanRequest instance.

        Raises:
            ValueError: If the request line is invalid or malformed.

        Examples:
            >>> request = SpartanRequest.from_line("example.com / 0")
            >>> request.path
            '/'
        """
        parts = line.split(" ")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid Spartan request format: expected 'host path size', "
                f"got {len(parts)} parts"
            )

        hostname, path, size_str = parts

        if not hostname:
            raise ValueError("Hostname cannot be empty")

        if not path.startswith("/"):
            raise ValueError("Path must be absolute (start with /)")

        try:
            content_length = int(size_str)
        except ValueError as e:
            raise ValueError(f"Invalid content length: {size_str}") from e

        if content_length < 0:
            raise ValueError(f"Content length must be non-negative: {content_length}")

        return cls(hostname=hostname, path=path, content_length=content_length)

    @property
    def is_upload(self) -> bool:
        """Check if this request contains upload data."""
        return self.content_length > 0

    @property
    def query(self) -> str | None:
        """Get query string from content if this is a query request.

        In Spartan, query strings are sent as the data block.
        Returns the content decoded as UTF-8 if present.
        """
        if self.content:
            try:
                return self.content.decode("utf-8")
            except UnicodeDecodeError:
                return None
        return None

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"SpartanRequest({self.hostname}{self.path}, {self.content_length} bytes)"
