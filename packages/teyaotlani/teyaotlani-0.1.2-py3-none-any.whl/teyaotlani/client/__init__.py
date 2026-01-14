"""Spartan client implementation.

This package provides the client-side components:
- SpartanClient: High-level async client
- SpartanClientProtocol: Low-level asyncio protocol
"""

from .protocol import SpartanClientProtocol
from .session import SpartanClient, get, upload

__all__ = [
    "SpartanClient",
    "SpartanClientProtocol",
    "get",
    "upload",
]
