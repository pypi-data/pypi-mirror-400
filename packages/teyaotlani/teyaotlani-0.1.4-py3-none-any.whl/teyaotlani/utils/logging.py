"""Structured logging configuration for Teyaotlani.

Uses structlog for structured, context-rich logging.
"""

import hashlib
import logging
import sys
from typing import Any

import structlog


def hash_ip(ip: str) -> str:
    """Hash an IP address for privacy.

    Args:
        ip: The IP address to hash.

    Returns:
        First 8 characters of SHA-256 hash.
    """
    return hashlib.sha256(ip.encode()).hexdigest()[:8]


class IPHashingProcessor:
    """Structlog processor that hashes IP addresses for privacy."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def __call__(
        self, logger: Any, method_name: str, event_dict: dict[str, Any]
    ) -> dict[str, Any]:
        if not self.enabled:
            return event_dict

        # Hash common IP field names
        for key in ("client_ip", "ip", "peer_ip", "remote_ip"):
            if key in event_dict and event_dict[key]:
                event_dict[key] = hash_ip(str(event_dict[key]))

        return event_dict


def configure_logging(
    level: str = "INFO",
    json_format: bool = False,
    hash_ips: bool = True,
) -> None:
    """Configure structured logging for Teyaotlani.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        json_format: If True, output logs as JSON.
        hash_ips: If True, hash IP addresses in logs for privacy.
    """
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, level.upper()),
    )

    # Build processor chain
    processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        IPHashingProcessor(enabled=hash_ips),
    ]

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__).

    Returns:
        A bound structlog logger.
    """
    return structlog.get_logger(name)
