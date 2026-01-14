"""URL parsing utilities for Spartan protocol.

Spartan URLs use the spartan:// scheme with default port 300.
"""

from dataclasses import dataclass
from urllib.parse import urlparse

from ..protocol.constants import DEFAULT_PORT


@dataclass
class ParsedURL:
    """Parsed Spartan URL components.

    Attributes:
        scheme: URL scheme (should be "spartan").
        hostname: Server hostname.
        port: Server port (default: 300).
        path: URL path (default: "/").
        normalized: Normalized URL string.
    """

    scheme: str
    hostname: str
    port: int
    path: str
    normalized: str


def parse_url(url: str) -> ParsedURL:
    """Parse a Spartan URL.

    Args:
        url: The URL to parse (e.g., "spartan://example.com/page.gmi").

    Returns:
        A ParsedURL with extracted components.

    Raises:
        ValueError: If the URL is invalid.

    Examples:
        >>> parsed = parse_url("spartan://example.com/hello")
        >>> parsed.hostname
        'example.com'
        >>> parsed.path
        '/hello'
    """
    parsed = urlparse(url)

    # Validate scheme
    if parsed.scheme.lower() != "spartan":
        raise ValueError(f"Invalid scheme: {parsed.scheme} (expected 'spartan')")

    # Validate hostname
    if not parsed.hostname:
        raise ValueError("URL must include hostname")

    # Get port (default 300)
    port = parsed.port or DEFAULT_PORT

    # Get path (default /)
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    # Include query in path if present (Spartan handles queries via data block)
    # but we preserve them in the path for now
    if parsed.query:
        path = f"{path}?{parsed.query}"

    # Build normalized URL
    if port == DEFAULT_PORT:
        normalized = f"spartan://{parsed.hostname}{path}"
    else:
        normalized = f"spartan://{parsed.hostname}:{port}{path}"

    return ParsedURL(
        scheme="spartan",
        hostname=parsed.hostname,
        port=port,
        path=path,
        normalized=normalized,
    )


def validate_url(url: str) -> None:
    """Validate a Spartan URL.

    Args:
        url: The URL to validate.

    Raises:
        ValueError: If the URL is invalid.
    """
    parse_url(url)  # Will raise if invalid


def build_url(hostname: str, path: str = "/", port: int = DEFAULT_PORT) -> str:
    """Build a Spartan URL from components.

    Args:
        hostname: Server hostname.
        path: URL path.
        port: Server port.

    Returns:
        A normalized Spartan URL.

    Examples:
        >>> build_url("example.com", "/hello")
        'spartan://example.com/hello'
    """
    if not path.startswith("/"):
        path = "/" + path

    if port == DEFAULT_PORT:
        return f"spartan://{hostname}{path}"
    return f"spartan://{hostname}:{port}{path}"
