"""Middleware components for Spartan server.

Provides security and rate limiting without requiring TLS:
- RateLimiter: Token bucket rate limiting
- AccessControl: IP-based allow/deny lists
"""

import asyncio
import time
from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from typing import Protocol

from ..utils.logging import get_logger

logger = get_logger(__name__)


class Middleware(Protocol):
    """Protocol for middleware components."""

    async def process_request(
        self,
        request_url: str,
        client_ip: str,
    ) -> tuple[bool, str | None]:
        """Process a request.

        Args:
            request_url: The full request URL.
            client_ip: The client's IP address.

        Returns:
            Tuple of (allow, error_response).
            If allow is True, request proceeds.
            If allow is False, error_response is sent to client.
        """
        ...


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    capacity: int = 10
    """Maximum tokens in bucket (burst capacity)."""

    refill_rate: float = 1.0
    """Tokens added per second."""

    retry_after: int = 30
    """Seconds to wait before retrying (in error message)."""


class TokenBucket:
    """Token bucket for rate limiting.

    Each IP gets its own bucket. Tokens are consumed per request
    and refill over time.
    """

    def __init__(self, capacity: int, refill_rate: float) -> None:
        """Initialize the token bucket.

        Args:
            capacity: Maximum number of tokens.
            refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_update = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens.

        Args:
            tokens: Number of tokens to consume.

        Returns:
            True if tokens were consumed, False if insufficient.
        """
        now = time.monotonic()
        elapsed = now - self.last_update

        # Refill tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False


class RateLimiter:
    """Rate limiting middleware using token bucket algorithm.

    Each client IP gets its own bucket. Exceeding the rate limit
    returns a client error (status 4).
    """

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        """Initialize the rate limiter.

        Args:
            config: Rate limit configuration.
        """
        self.config = config or RateLimitConfig()
        self.buckets: dict[str, TokenBucket] = {}
        self._cleanup_task: asyncio.Task[None] | None = None

    def start(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None:
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._cleanup_loop())
            except RuntimeError:
                pass  # No event loop

    def stop(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Periodically clean up idle buckets."""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            now = time.monotonic()
            to_remove = [
                ip
                for ip, bucket in self.buckets.items()
                if now - bucket.last_update > 600  # 10 minutes idle
            ]
            for ip in to_remove:
                del self.buckets[ip]

            if to_remove:
                logger.debug("rate_limit_cleanup", removed=len(to_remove))

    async def process_request(
        self,
        request_url: str,
        client_ip: str,
    ) -> tuple[bool, str | None]:
        """Process request with rate limiting.

        Args:
            request_url: The request URL (unused).
            client_ip: The client's IP address.

        Returns:
            Tuple of (allow, error_response).
        """
        if client_ip not in self.buckets:
            self.buckets[client_ip] = TokenBucket(
                self.config.capacity, self.config.refill_rate
            )

        if self.buckets[client_ip].consume():
            return True, None

        # Rate limit exceeded
        logger.warning("rate_limit_exceeded", client_ip=client_ip)
        response = (
            f"4 Rate limit exceeded. Retry after {self.config.retry_after} seconds\r\n"
        )
        return False, response


@dataclass
class AccessControlConfig:
    """Configuration for IP-based access control."""

    allow_list: list[str] | None = None
    """CIDR networks to allow (e.g., ["192.168.1.0/24"])."""

    deny_list: list[str] | None = None
    """CIDR networks to deny."""

    default_allow: bool = True
    """Default policy when IP not in any list."""


class AccessControl:
    """IP-based access control middleware.

    Supports allow lists and deny lists with CIDR notation.
    Deny list is checked first (deny takes precedence).
    """

    def __init__(self, config: AccessControlConfig) -> None:
        """Initialize access control.

        Args:
            config: Access control configuration.
        """
        self.config = config
        self.allow_networks: list[IPv4Network | IPv6Network] = []
        self.deny_networks: list[IPv4Network | IPv6Network] = []

        # Parse CIDR networks
        if config.allow_list:
            for cidr in config.allow_list:
                try:
                    self.allow_networks.append(ip_network(cidr, strict=False))
                except ValueError as e:
                    logger.warning("invalid_allow_cidr", cidr=cidr, error=str(e))

        if config.deny_list:
            for cidr in config.deny_list:
                try:
                    self.deny_networks.append(ip_network(cidr, strict=False))
                except ValueError as e:
                    logger.warning("invalid_deny_cidr", cidr=cidr, error=str(e))

    async def process_request(
        self,
        request_url: str,
        client_ip: str,
    ) -> tuple[bool, str | None]:
        """Check if client IP is allowed.

        Args:
            request_url: The request URL (unused).
            client_ip: The client's IP address.

        Returns:
            Tuple of (allow, error_response).
        """
        if self._is_allowed(client_ip):
            return True, None

        logger.warning("access_denied", client_ip=client_ip)
        return False, "4 Access denied\r\n"

    def _is_allowed(self, ip_str: str) -> bool:
        """Check if IP is allowed.

        Args:
            ip_str: The IP address as string.

        Returns:
            True if allowed, False if denied.
        """
        try:
            ip_obj = ip_address(ip_str)
        except ValueError:
            # Invalid IP - deny by default
            return False

        # Deny list takes precedence
        for network in self.deny_networks:
            if ip_obj in network:
                return False

        # Check allow list if configured
        if self.allow_networks:
            for network in self.allow_networks:
                if ip_obj in network:
                    return True
            # Not in allow list
            return False

        # No allow list - use default policy
        return self.config.default_allow


class MiddlewareChain:
    """Chain multiple middleware components together.

    Processes requests through each middleware in order.
    First rejection stops the chain.
    """

    def __init__(self, middlewares: list[Middleware] | None = None) -> None:
        """Initialize the middleware chain.

        Args:
            middlewares: List of middleware components.
        """
        self.middlewares: list[Middleware] = middlewares or []

    def add(self, middleware: Middleware) -> None:
        """Add a middleware to the chain.

        Args:
            middleware: The middleware to add.
        """
        self.middlewares.append(middleware)

    async def process_request(
        self,
        request_url: str,
        client_ip: str,
    ) -> tuple[bool, str | None]:
        """Process request through all middleware.

        Args:
            request_url: The request URL.
            client_ip: The client's IP address.

        Returns:
            Tuple of (allow, error_response).
            If any middleware rejects, returns immediately.
        """
        for middleware in self.middlewares:
            allow, response = await middleware.process_request(request_url, client_ip)
            if not allow:
                return False, response

        return True, None
