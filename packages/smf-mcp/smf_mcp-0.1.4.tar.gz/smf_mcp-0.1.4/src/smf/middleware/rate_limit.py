"""
Rate Limiting Middleware.

Implements rate limiting using token bucket algorithm.
"""

import time
from collections import defaultdict
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from smf.settings import Settings


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum tokens
            refill_rate: Tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if rate limited
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity, self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now


class RateLimiter:
    """Rate limiter with per-client token buckets."""

    def __init__(self, per_minute: int, per_hour: int):
        """
        Initialize rate limiter.

        Args:
            per_minute: Requests per minute
            per_hour: Requests per hour
        """
        self.per_minute = per_minute
        self.per_hour = per_hour
        self.buckets_minute: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(per_minute, per_minute / 60.0)
        )
        self.buckets_hour: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(per_hour, per_hour / 3600.0)
        )

    def check(self, client_id: str) -> bool:
        """
        Check if request should be allowed.

        Args:
            client_id: Client identifier

        Returns:
            True if allowed, False if rate limited
        """
        minute_ok = self.buckets_minute[client_id].consume()
        hour_ok = self.buckets_hour[client_id].consume()

        return minute_ok and hour_ok


_rate_limiter: Optional[RateLimiter] = None


def attach_rate_limiting(mcp: FastMCP, settings: Settings) -> None:
    """
    Attach rate limiting middleware to FastMCP server.

    Args:
        mcp: FastMCP server instance
        settings: SMF settings
    """
    global _rate_limiter

    if not settings.rate_limit_enabled:
        return

    _rate_limiter = RateLimiter(
        per_minute=settings.rate_limit_per_minute,
        per_hour=settings.rate_limit_per_hour,
    )

    # Attach rate limiting hooks
    # Note: This is a placeholder - actual implementation depends on FastMCP API
    if hasattr(mcp, "on_call_tool"):
        original_call_tool = getattr(mcp, "on_call_tool", None)

        def rate_limit_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
            # Extract client ID from context (implementation depends on FastMCP)
            client_id = _get_client_id(arguments)
            if not _rate_limiter.check(client_id):
                raise RateLimitError("Rate limit exceeded")

            if original_call_tool:
                original_call_tool(tool_name, arguments)

        mcp.on_call_tool = rate_limit_tool_call


def _get_client_id(arguments: Dict[str, Any]) -> str:
    """
    Extract client ID from request context.

    Args:
        arguments: Tool call arguments

    Returns:
        Client identifier
    """
    # Placeholder - actual implementation depends on FastMCP request context
    return arguments.get("_client_id", "default")


class RateLimitError(Exception):
    """Rate limit exceeded error."""

    pass

