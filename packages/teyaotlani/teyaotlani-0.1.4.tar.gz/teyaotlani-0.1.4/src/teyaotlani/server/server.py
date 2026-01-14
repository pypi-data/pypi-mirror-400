"""Spartan server implementation.

Provides the main server startup and lifecycle management.
"""

import asyncio
import signal
from pathlib import Path

from ..protocol.constants import DEFAULT_PORT
from ..utils.logging import configure_logging, get_logger
from .config import ServerConfig
from .handler import CombinedHandler, StaticFileHandler, UploadHandler
from .middleware import AccessControl, MiddlewareChain, RateLimiter
from .protocol import SpartanServerProtocol

logger = get_logger(__name__)


async def start_server(
    config: ServerConfig | None = None,
    host: str | None = None,
    port: int | None = None,
    document_root: Path | str | None = None,
    enable_directory_listing: bool = False,
    log_level: str = "INFO",
    json_logs: bool = False,
    hash_ips: bool = True,
) -> None:
    """Start a Spartan protocol server.

    Args:
        config: Server configuration. If None, uses other arguments.
        host: Server host address (default: localhost).
        port: Server port (default: 300).
        document_root: Path to serve files from.
        enable_directory_listing: Whether to enable directory listings.
        log_level: Logging level.
        json_logs: Whether to output logs as JSON.
        hash_ips: Whether to hash client IPs in logs.

    Raises:
        ValueError: If configuration is invalid.
    """
    # Build config from arguments if not provided
    if config is None:
        if document_root is None:
            raise ValueError("document_root is required")

        config = ServerConfig(
            host=host or "localhost",
            port=port or DEFAULT_PORT,
            document_root=document_root,
            enable_directory_listing=enable_directory_listing,
            log_level=log_level,
            json_logs=json_logs,
            hash_client_ips=hash_ips,
        )

    # Validate configuration
    config.validate()

    # Configure logging
    configure_logging(
        level=config.log_level,
        json_format=config.json_logs,
        hash_ips=config.hash_client_ips,
    )

    # Create handlers
    static_handler = StaticFileHandler(
        document_root=config.document_root,
        default_indices=config.index_files,
        enable_directory_listing=config.enable_directory_listing,
        max_file_size=config.max_file_size,
    )

    upload_handler = None
    if config.enable_upload and config.upload_dir:
        upload_handler = UploadHandler(
            upload_dir=config.upload_dir,
            max_size=config.max_upload_size,
            enable_delete=config.enable_delete,
        )

    combined_handler = CombinedHandler(static_handler, upload_handler)

    # Create middleware chain
    middleware = MiddlewareChain()

    rate_limiter = None
    rate_limit_config = config.get_rate_limit_config()
    if rate_limit_config:
        rate_limiter = RateLimiter(rate_limit_config)
        rate_limiter.start()
        middleware.add(rate_limiter)

    access_control_config = config.get_access_control_config()
    if access_control_config:
        access_control = AccessControl(access_control_config)
        middleware.add(access_control)

    # Get event loop
    loop = asyncio.get_running_loop()

    # Create server
    server = await loop.create_server(
        lambda: SpartanServerProtocol(
            request_handler=combined_handler.handle,
            middleware=middleware if middleware.middlewares else None,
        ),
        host=config.host,
        port=config.port,
    )

    # Log startup
    logger.info(
        "server_started",
        host=config.host,
        port=config.port,
        document_root=str(config.document_root),
        directory_listing=config.enable_directory_listing,
        upload_enabled=config.enable_upload,
        rate_limiting=config.enable_rate_limiting,
        access_control=config.enable_access_control,
    )

    print(f"Spartan server running on spartan://{config.host}:{config.port}/")
    print(f"Serving files from: {config.document_root}")
    print("Press Ctrl+C to stop")

    # Handle shutdown
    shutdown_event = asyncio.Event()

    def signal_handler() -> None:
        shutdown_event.set()

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        async with server:
            await shutdown_event.wait()
    finally:
        # Cleanup
        if rate_limiter:
            rate_limiter.stop()

        logger.info("server_stopped")
        print("\nServer stopped.")


def run_server(
    document_root: Path | str,
    host: str = "localhost",
    port: int = DEFAULT_PORT,
    **kwargs: object,
) -> None:
    """Convenience function to run a server synchronously.

    Args:
        document_root: Path to serve files from.
        host: Server host address.
        port: Server port.
        **kwargs: Additional arguments passed to start_server.
    """
    asyncio.run(
        start_server(
            host=host,
            port=port,
            document_root=document_root,
            **kwargs,  # type: ignore[arg-type]
        )
    )
