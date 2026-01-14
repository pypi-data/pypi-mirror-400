"""Spartan protocol response representation.

Spartan response format: status SP meta CRLF [body]
"""

from dataclasses import dataclass

from .status import is_redirect, is_success


@dataclass(frozen=True)
class SpartanResponse:
    """Represents a Spartan protocol response.

    Response format: status SP meta CRLF [body]

    Attributes:
        status: Single-digit status code (2, 3, 4, or 5).
        meta: Status-dependent metadata string.
            - For success (2): MIME type (e.g., "text/gemini")
            - For redirect (3): Redirect URL
            - For errors (4, 5): Error message
        body: Response body content (only present for success responses).
        url: Optional URL this response came from.

    Examples:
        >>> response = SpartanResponse(status=2, meta="text/gemini", body="# Hello")
        >>> response.is_success()
        True
        >>> response.mime_type
        'text/gemini'
    """

    status: int
    meta: str
    body: str | bytes | None = None
    url: str | None = None

    def is_success(self) -> bool:
        """Check if this response indicates success (status 2)."""
        return is_success(self.status)

    def is_redirect(self) -> bool:
        """Check if this response indicates a redirect (status 3)."""
        return is_redirect(self.status)

    @property
    def mime_type(self) -> str | None:
        """Get the MIME type from a success response.

        Returns:
            The MIME type if this is a success response, None otherwise.
        """
        if self.is_success():
            # Meta for success responses is the MIME type, possibly with parameters
            return self.meta.split(";")[0].strip()
        return None

    @property
    def redirect_url(self) -> str | None:
        """Get the redirect URL from a redirect response.

        Returns:
            The redirect URL if this is a redirect response, None otherwise.
        """
        if self.is_redirect():
            return self.meta
        return None

    @property
    def charset(self) -> str:
        """Extract charset from MIME type parameters, defaulting to utf-8.

        Returns:
            The charset specified in the meta field, or 'utf-8' if not specified.
        """
        if not self.is_success():
            return "utf-8"

        # Look for charset parameter in meta
        parts = self.meta.split(";")
        for part in parts[1:]:
            key_value = part.strip().split("=", 1)
            if len(key_value) == 2:
                key, value = key_value
                if key.strip().lower() == "charset":
                    return value.strip()

        return "utf-8"

    def to_bytes(self) -> bytes:
        """Serialize response to bytes for transmission.

        Returns:
            ASCII-encoded header followed by optional body.
        """
        header = f"{self.status} {self.meta}\r\n".encode("ascii")

        if self.body:
            if isinstance(self.body, bytes):
                return header + self.body
            return header + self.body.encode("utf-8")

        return header

    @classmethod
    def success(cls, mime_type: str, body: str | bytes) -> "SpartanResponse":
        """Create a success response.

        Args:
            mime_type: The MIME type of the content.
            body: The response body.

        Returns:
            A SpartanResponse with status 2.
        """
        return cls(status=2, meta=mime_type, body=body)

    @classmethod
    def redirect(cls, url: str) -> "SpartanResponse":
        """Create a redirect response.

        Args:
            url: The redirect URL.

        Returns:
            A SpartanResponse with status 3.
        """
        return cls(status=3, meta=url)

    @classmethod
    def client_error(cls, message: str) -> "SpartanResponse":
        """Create a client error response.

        Args:
            message: The error message.

        Returns:
            A SpartanResponse with status 4.
        """
        return cls(status=4, meta=message)

    @classmethod
    def server_error(cls, message: str) -> "SpartanResponse":
        """Create a server error response.

        Args:
            message: The error message.

        Returns:
            A SpartanResponse with status 5.
        """
        return cls(status=5, meta=message)

    def __str__(self) -> str:
        """Return human-readable string representation."""
        lines = [f"Status: {self.status} - {self.meta}"]
        if self.url:
            lines.append(f"URL: {self.url}")
        if self.body:
            size = len(self.body) if isinstance(self.body, bytes) else len(self.body)
            lines.append(f"Body: {size} bytes")
        return "\n".join(lines)
