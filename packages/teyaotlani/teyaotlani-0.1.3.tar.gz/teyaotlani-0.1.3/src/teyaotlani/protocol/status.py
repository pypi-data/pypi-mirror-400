"""Spartan protocol status codes.

Spartan uses single-digit status codes (2-5) unlike Gemini's two-digit codes.
"""

from enum import IntEnum


class StatusCode(IntEnum):
    """Spartan protocol status codes.

    Status codes:
        2 - Success: Meta contains MIME type, body follows
        3 - Redirect: Meta contains redirect URL
        4 - Client error: Meta contains error message
        5 - Server error: Meta contains error message
    """

    SUCCESS = 2
    REDIRECT = 3
    CLIENT_ERROR = 4
    SERVER_ERROR = 5


def interpret_status(status: int) -> str:
    """Return human-readable status category name.

    Args:
        status: Single-digit status code (2-5).

    Returns:
        Human-readable status category.

    Examples:
        >>> interpret_status(2)
        'SUCCESS'
        >>> interpret_status(4)
        'CLIENT ERROR'
    """
    if status == 2:
        return "SUCCESS"
    if status == 3:
        return "REDIRECT"
    if status == 4:
        return "CLIENT ERROR"
    if status == 5:
        return "SERVER ERROR"
    return "UNKNOWN"


def is_success(status: int) -> bool:
    """Check if status indicates success."""
    return status == StatusCode.SUCCESS


def is_redirect(status: int) -> bool:
    """Check if status indicates redirect."""
    return status == StatusCode.REDIRECT


def is_error(status: int) -> bool:
    """Check if status indicates any error (client or server)."""
    return status in (StatusCode.CLIENT_ERROR, StatusCode.SERVER_ERROR)
