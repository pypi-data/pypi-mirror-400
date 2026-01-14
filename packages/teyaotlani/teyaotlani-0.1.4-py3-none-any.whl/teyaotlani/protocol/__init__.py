"""Spartan protocol primitives.

This package contains the core protocol definitions for Spartan:
- Request/response dataclasses
- Status codes
- Protocol constants
"""

from .constants import (
    CRLF,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_PORT,
    MAX_REQUEST_SIZE,
    MAX_UPLOAD_SIZE,
    MIME_TYPE_GEMTEXT,
    MIME_TYPE_PLAIN,
    REQUEST_TIMEOUT,
)
from .request import SpartanRequest
from .response import SpartanResponse
from .status import StatusCode, interpret_status, is_error, is_redirect, is_success

__all__ = [
    # Constants
    "CRLF",
    "DEFAULT_MAX_FILE_SIZE",
    "DEFAULT_PORT",
    "MAX_REQUEST_SIZE",
    "MAX_UPLOAD_SIZE",
    "MIME_TYPE_GEMTEXT",
    "MIME_TYPE_PLAIN",
    "REQUEST_TIMEOUT",
    # Request/Response
    "SpartanRequest",
    "SpartanResponse",
    # Status
    "StatusCode",
    "interpret_status",
    "is_error",
    "is_redirect",
    "is_success",
]
