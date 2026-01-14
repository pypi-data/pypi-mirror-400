"""Spartan server implementation.

This package provides the server-side components:
- SpartanServerProtocol: Low-level asyncio protocol
- StaticFileHandler: Serves static files
- UploadHandler: Handles file uploads
- RateLimiter: Rate limiting middleware
- AccessControl: IP-based access control
- ServerConfig: Configuration management
"""

from .config import ServerConfig
from .handler import CombinedHandler, RequestHandler, StaticFileHandler, UploadHandler
from .middleware import (
    AccessControl,
    AccessControlConfig,
    MiddlewareChain,
    RateLimitConfig,
    RateLimiter,
)
from .protocol import SpartanServerProtocol
from .server import run_server, start_server

__all__ = [
    # Protocol
    "SpartanServerProtocol",
    # Handlers
    "RequestHandler",
    "StaticFileHandler",
    "UploadHandler",
    "CombinedHandler",
    # Middleware
    "RateLimiter",
    "RateLimitConfig",
    "AccessControl",
    "AccessControlConfig",
    "MiddlewareChain",
    # Config
    "ServerConfig",
    # Server
    "start_server",
    "run_server",
]
