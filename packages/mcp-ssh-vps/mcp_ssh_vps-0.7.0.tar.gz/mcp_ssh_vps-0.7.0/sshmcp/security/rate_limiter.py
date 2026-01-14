"""Rate limiting for command execution."""

import threading
import time
from collections import defaultdict
from typing import NamedTuple

import structlog

logger = structlog.get_logger()


class RateLimitConfig(NamedTuple):
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: float = 0):
        super().__init__(message)
        self.retry_after = retry_after


class TokenBucket:
    """Token bucket rate limiter implementation."""

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.

        Args:
            rate: Tokens per second to add.
            capacity: Maximum tokens in bucket.
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume.

        Returns:
            True if tokens were consumed, False if not enough tokens.
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Add tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def time_until_available(self, tokens: int = 1) -> float:
        """
        Calculate time until tokens are available.

        Args:
            tokens: Number of tokens needed.

        Returns:
            Seconds until tokens available (0 if available now).
        """
        with self._lock:
            if self.tokens >= tokens:
                return 0
            needed = tokens - self.tokens
            return needed / self.rate


class RateLimiter:
    """Rate limiter for SSH command execution."""

    def __init__(self, config: RateLimitConfig | None = None):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration.
        """
        self.config = config or RateLimitConfig()
        self._buckets: dict[str, dict[str, TokenBucket]] = defaultdict(dict)
        self._lock = threading.Lock()

    def _get_bucket(self, host: str, limit_type: str) -> TokenBucket:
        """Get or create a token bucket for host and limit type."""
        with self._lock:
            if limit_type not in self._buckets[host]:
                if limit_type == "minute":
                    rate = self.config.requests_per_minute / 60.0
                    capacity = self.config.burst_size
                elif limit_type == "hour":
                    rate = self.config.requests_per_hour / 3600.0
                    capacity = self.config.burst_size * 2
                else:
                    rate = 1.0
                    capacity = 10

                self._buckets[host][limit_type] = TokenBucket(rate, capacity)

            return self._buckets[host][limit_type]

    def check_rate_limit(self, host: str) -> None:
        """
        Check if request is within rate limits.

        Args:
            host: Host name to check rate limit for.

        Raises:
            RateLimitExceeded: If rate limit is exceeded.
        """
        # Check minute limit
        minute_bucket = self._get_bucket(host, "minute")
        if not minute_bucket.consume():
            retry_after = minute_bucket.time_until_available()
            logger.warning(
                "rate_limit_exceeded",
                host=host,
                limit_type="minute",
                retry_after=retry_after,
            )
            raise RateLimitExceeded(
                f"Rate limit exceeded for {host}. Try again in {retry_after:.1f}s",
                retry_after=retry_after,
            )

        # Check hour limit
        hour_bucket = self._get_bucket(host, "hour")
        if not hour_bucket.consume():
            retry_after = hour_bucket.time_until_available()
            logger.warning(
                "rate_limit_exceeded",
                host=host,
                limit_type="hour",
                retry_after=retry_after,
            )
            raise RateLimitExceeded(
                f"Hourly rate limit exceeded for {host}. Try again in {retry_after:.1f}s",
                retry_after=retry_after,
            )

    def get_remaining(self, host: str) -> dict:
        """
        Get remaining rate limit for host.

        Args:
            host: Host name.

        Returns:
            Dictionary with remaining limits.
        """
        minute_bucket = self._get_bucket(host, "minute")
        hour_bucket = self._get_bucket(host, "hour")

        return {
            "host": host,
            "minute": {
                "remaining": int(minute_bucket.tokens),
                "limit": self.config.requests_per_minute,
            },
            "hour": {
                "remaining": int(hour_bucket.tokens),
                "limit": self.config.requests_per_hour,
            },
        }

    def reset(self, host: str | None = None) -> None:
        """
        Reset rate limits.

        Args:
            host: Host to reset, or None for all hosts.
        """
        with self._lock:
            if host is None:
                self._buckets.clear()
            elif host in self._buckets:
                del self._buckets[host]


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def init_rate_limiter(config: RateLimitConfig | None = None) -> RateLimiter:
    """
    Initialize the global rate limiter with config.

    Args:
        config: Rate limit configuration.

    Returns:
        Initialized RateLimiter.
    """
    global _rate_limiter
    _rate_limiter = RateLimiter(config)
    return _rate_limiter
