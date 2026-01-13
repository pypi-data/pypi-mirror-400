"""
Rate limiting for XuguDB MCP Server.

Protects against abuse by limiting query rate and resource usage.
"""
import asyncio
import time
from collections import deque
from typing import Dict, Any
from dataclasses import dataclass

from ..config.settings import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    remaining: int
    reset_time: float
    retry_after: float | None = None
    limit_type: str | None = None


class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
    ):
        """Initialize sliding window rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: deque = deque()
        self._lock = asyncio.Lock()

    async def check(self) -> RateLimitResult:
        """Check if request is allowed.

        Returns:
            RateLimitResult with check result
        """
        async with self._lock:
            now = time.time()

            # Remove old requests outside the window
            while self._requests and self._requests[0] <= now - self.window_seconds:
                self._requests.popleft()

            # Check if limit exceeded
            if len(self._requests) >= self.max_requests:
                # Calculate when the oldest request will expire
                oldest_request = self._requests[0]
                retry_after = oldest_request + self.window_seconds - now

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=oldest_request + self.window_seconds,
                    retry_after=retry_after,
                    limit_type="sliding_window",
                )

            # Add current request
            self._requests.append(now)

            return RateLimitResult(
                allowed=True,
                remaining=self.max_requests - len(self._requests),
                reset_time=now + self.window_seconds,
                limit_type="sliding_window",
            )

    def clear(self):
        """Clear the rate limiter."""
        self._requests.clear()


class TokenBucketRateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        rate: float,  # tokens per second
        capacity: int,  # maximum tokens
    ):
        """Initialize token bucket rate limiter.

        Args:
            rate: Token refill rate (tokens per second)
            capacity: Maximum bucket capacity
        """
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_update = time.time()
        self._lock = asyncio.Lock()

    async def check(self, tokens: int = 1) -> RateLimitResult:
        """Check if request is allowed.

        Args:
            tokens: Number of tokens required

        Returns:
            RateLimitResult with check result
        """
        async with self._lock:
            now = time.time()

            # Refill tokens
            elapsed = now - self._last_update
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last_update = now

            # Check if enough tokens
            if self._tokens < tokens:
                # Calculate wait time for required tokens
                wait_time = (tokens - self._tokens) / self.rate

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=now + wait_time,
                    retry_after=wait_time,
                    limit_type="token_bucket",
                )

            # Consume tokens
            self._tokens -= tokens

            return RateLimitResult(
                allowed=True,
                remaining=int(self._tokens),
                reset_time=now + (self.capacity - self._tokens) / self.rate,
                limit_type="token_bucket",
            )


class RateLimiter:
    """Main rate limiter with multiple strategies."""

    def __init__(
        self,
        enabled: bool = True,
        max_queries_per_minute: int = 100,
        max_concurrent: int = 10,
    ):
        """Initialize rate limiter.

        Args:
            enabled: Whether rate limiting is enabled
            max_queries_per_minute: Maximum queries per minute
            max_concurrent: Maximum concurrent queries
        """
        self.settings = get_settings()
        self.enabled = enabled and self.settings.security.rate_limit_enabled
        self.max_queries_per_minute = max_queries_per_minute or self.settings.security.rate_limit_max_queries
        self.max_concurrent = max_concurrent

        # Rate limiters
        self._sliding_window = SlidingWindowRateLimiter(
            max_requests=self.max_queries_per_minute,
            window_seconds=60,
        )

        # Token bucket for burst protection
        self._token_bucket = TokenBucketRateLimiter(
            rate=self.max_queries_per_minute / 60,  # tokens per second
            capacity=self.max_queries_per_minute // 2,  # half of minute limit
        )

        # Concurrent query tracking
        self._concurrent = 0
        self._concurrent_lock = asyncio.Lock()

        # Per-client tracking (by IP or session ID)
        self._client_limiters: Dict[str, SlidingWindowRateLimiter] = {}
        self._client_limiters_lock = asyncio.Lock()

        # Statistics
        self._stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "concurrent_rejections": 0,
        }
        self._stats_lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        client_id: str | None = None,
    ) -> RateLimitResult:
        """Check if request is allowed.

        Args:
            client_id: Optional client identifier for per-client limiting

        Returns:
            RateLimitResult with check result
        """
        if not self.enabled:
            return RateLimitResult(
                allowed=True,
                remaining=self.max_queries_per_minute,
                reset_time=time.time() + 60,
            )

        async with self._stats_lock:
            self._stats["total_requests"] += 1

        # Check concurrent limit
        async with self._concurrent_lock:
            if self._concurrent >= self.max_concurrent:
                async with self._stats_lock:
                    self._stats["concurrent_rejections"] += 1
                    self._stats["blocked_requests"] += 1

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=time.time() + 1,
                    retry_after=0.1,
                    limit_type="concurrent",
                )

        # Check sliding window limit
        result = await self._sliding_window.check()
        if not result.allowed:
            async with self._stats_lock:
                self._stats["blocked_requests"] += 1
            return result

        # Check token bucket
        result = await self._token_bucket.check()
        if not result.allowed:
            async with self._stats_lock:
                self._stats["blocked_requests"] += 1
            return result

        # Check per-client limit if client_id provided
        if client_id:
            client_result = await self._check_client_limit(client_id)
            if not client_result.allowed:
                async with self._stats_lock:
                    self._stats["blocked_requests"] += 1
                return client_result

        async with self._stats_lock:
            self._stats["allowed_requests"] += 1

        return RateLimitResult(
            allowed=True,
            remaining=result.remaining,
            reset_time=result.reset_time,
            limit_type="combined",
        )

    async def _check_client_limit(self, client_id: str) -> RateLimitResult:
        """Check per-client rate limit.

        Args:
            client_id: Client identifier

        Returns:
            RateLimitResult with check result
        """
        async with self._client_limiters_lock:
            if client_id not in self._client_limiters:
                # Per-client limit: 80% of global limit
                client_limit = max(10, self.max_queries_per_minute * 8 // 10)
                self._client_limiters[client_id] = SlidingWindowRateLimiter(
                    max_requests=client_limit,
                    window_seconds=60,
                )

            return await self._client_limiters[client_id].check()

    async def acquire_concurrent(self) -> bool:
        """Acquire a concurrent query slot.

        Returns:
            True if slot acquired, False if at limit
        """
        async with self._concurrent_lock:
            if self._concurrent >= self.max_concurrent:
                return False
            self._concurrent += 1
            return True

    async def release_concurrent(self):
        """Release a concurrent query slot."""
        async with self._concurrent_lock:
            if self._concurrent > 0:
                self._concurrent -= 1

    async def __aenter__(self):
        """Acquire concurrent slot as context manager."""
        acquired = await self.acquire_concurrent()
        if not acquired:
            raise Exception("Concurrent query limit exceeded")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release concurrent slot when exiting context."""
        await self.release_concurrent()

    def get_statistics(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        return {
            **self._stats,
            "current_concurrent": self._concurrent,
            "max_concurrent": self.max_concurrent,
            "max_queries_per_minute": self.max_queries_per_minute,
            "enabled": self.enabled,
            "tracked_clients": len(self._client_limiters),
        }

    def reset_statistics(self):
        """Reset statistics."""
        self._stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "concurrent_rejections": 0,
        }

    def clear_client(self, client_id: str):
        """Clear client-specific rate limiter.

        Args:
            client_id: Client identifier to clear
        """
        if client_id in self._client_limiters:
            self._client_limiters[client_id].clear()
            del self._client_limiters[client_id]


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance.

    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def reset_rate_limiter():
    """Reset global rate limiter (useful for testing)."""
    global _rate_limiter
    _rate_limiter = None
