"""Spartan protocol constants.

This module defines constants used throughout the Spartan protocol implementation.
"""

# Default port for Spartan protocol (300 - reference to 300 Spartans at Thermopylae)
DEFAULT_PORT = 300

# Line terminator
CRLF = b"\r\n"

# Size limits
MAX_REQUEST_SIZE = 8192  # 8KB for request line
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB default
DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# MIME types
MIME_TYPE_GEMTEXT = "text/gemini"
MIME_TYPE_PLAIN = "text/plain"

# Request timeout
REQUEST_TIMEOUT = 30.0
