"""Teyaotlani - Modern Spartan protocol implementation.

A modern, async-first implementation of the Spartan protocol
for Python, featuring both client and server capabilities.

Examples:
    # Client usage
    >>> import asyncio
    >>> from teyaotlani import SpartanClient
    >>>
    >>> async def main():
    ...     async with SpartanClient() as client:
    ...         response = await client.get("spartan://example.com/")
    ...         print(response.body)
    >>>
    >>> asyncio.run(main())

    # Quick get
    >>> from teyaotlani import get
    >>> response = asyncio.run(get("spartan://example.com/"))
"""

from .client.session import SpartanClient, get, upload
from .protocol.constants import DEFAULT_PORT
from .protocol.request import SpartanRequest
from .protocol.response import SpartanResponse
from .protocol.status import (
    StatusCode,
    interpret_status,
    is_error,
    is_redirect,
    is_success,
)
from .server.config import ServerConfig
from .server.server import run_server, start_server

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Client
    "SpartanClient",
    "get",
    "upload",
    # Protocol
    "SpartanRequest",
    "SpartanResponse",
    "StatusCode",
    "interpret_status",
    "is_error",
    "is_redirect",
    "is_success",
    "DEFAULT_PORT",
    # Server
    "ServerConfig",
    "start_server",
    "run_server",
]
