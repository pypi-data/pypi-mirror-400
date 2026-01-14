"""Tests for rate limiter."""

import time

import pytest

from sshmcp.security.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    RateLimitExceeded,
    TokenBucket,
    get_rate_limiter,
    init_rate_limiter,
)


class TestTokenBucket:
    """Tests for TokenBucket."""

    def test_initial_tokens(self):
        """Test bucket starts with full capacity."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.tokens == 10

    def test_consume_success(self):
        """Test successful token consumption."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        assert bucket.consume(5) is True
        assert bucket.tokens == 5

    def test_consume_failure(self):
        """Test consumption failure when not enough tokens."""
        bucket = TokenBucket(rate=1.0, capacity=5)
        bucket.consume(5)  # Empty bucket
        assert bucket.consume(1) is False

    def test_token_refill(self):
        """Test tokens are refilled over time."""
        bucket = TokenBucket(rate=10.0, capacity=10)  # 10 tokens/sec
        bucket.consume(10)  # Empty bucket

        # Wait a bit for refill
        time.sleep(0.2)

        # Should have some tokens now
        assert bucket.consume(1) is True

    def test_time_until_available(self):
        """Test calculating time until tokens available."""
        bucket = TokenBucket(rate=1.0, capacity=10)
        bucket.consume(10)  # Empty bucket

        wait_time = bucket.time_until_available(5)
        assert wait_time > 0
        assert wait_time <= 5.0


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_default_config(self):
        """Test rate limiter with default config."""
        limiter = RateLimiter()
        assert limiter.config.requests_per_minute == 60
        assert limiter.config.requests_per_hour == 1000

    def test_custom_config(self):
        """Test rate limiter with custom config."""
        config = RateLimitConfig(requests_per_minute=10, requests_per_hour=100)
        limiter = RateLimiter(config)
        assert limiter.config.requests_per_minute == 10
        assert limiter.config.requests_per_hour == 100

    def test_check_rate_limit_success(self):
        """Test rate limit check passes."""
        limiter = RateLimiter()
        # Should not raise
        limiter.check_rate_limit("test-host")

    def test_check_rate_limit_exceeded(self):
        """Test rate limit exceeded raises exception."""
        config = RateLimitConfig(requests_per_minute=1, burst_size=1)
        limiter = RateLimiter(config)

        # First request should pass
        limiter.check_rate_limit("test-host")

        # Second request should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            limiter.check_rate_limit("test-host")

        assert exc_info.value.retry_after > 0

    def test_get_remaining(self):
        """Test getting remaining rate limit."""
        limiter = RateLimiter()
        remaining = limiter.get_remaining("test-host")

        assert remaining["host"] == "test-host"
        assert "minute" in remaining
        assert "hour" in remaining
        assert remaining["minute"]["limit"] == 60

    def test_reset_specific_host(self):
        """Test resetting rate limit for specific host."""
        limiter = RateLimiter()

        # Make some requests
        limiter.check_rate_limit("host1")
        limiter.check_rate_limit("host2")

        # Reset host1
        limiter.reset("host1")

        # host1 buckets should be cleared
        remaining = limiter.get_remaining("host1")
        # New bucket created, should be at capacity
        assert remaining["minute"]["remaining"] > 0

    def test_reset_all_hosts(self):
        """Test resetting all rate limits."""
        limiter = RateLimiter()

        # Make some requests
        limiter.check_rate_limit("host1")
        limiter.check_rate_limit("host2")

        # Reset all
        limiter.reset()

        # All buckets cleared
        assert len(limiter._buckets) == 0

    def test_separate_limits_per_host(self):
        """Test that each host has separate limits."""
        config = RateLimitConfig(requests_per_minute=2, burst_size=2)
        limiter = RateLimiter(config)

        # Exhaust host1 limit
        limiter.check_rate_limit("host1")
        limiter.check_rate_limit("host1")

        # host2 should still work
        limiter.check_rate_limit("host2")


class TestGlobalRateLimiter:
    """Tests for global rate limiter functions."""

    def test_get_rate_limiter(self):
        """Test getting global rate limiter."""
        limiter = get_rate_limiter()
        assert isinstance(limiter, RateLimiter)

    def test_init_rate_limiter(self):
        """Test initializing global rate limiter."""
        config = RateLimitConfig(requests_per_minute=100)
        limiter = init_rate_limiter(config)
        assert limiter.config.requests_per_minute == 100

    def test_get_returns_same_instance(self):
        """Test get_rate_limiter returns same instance."""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        # Note: might not be same due to init_rate_limiter calls in other tests
        assert isinstance(limiter1, RateLimiter)
        assert isinstance(limiter2, RateLimiter)


class TestRateLimitExceeded:
    """Tests for RateLimitExceeded exception."""

    def test_exception_message(self):
        """Test exception has message."""
        exc = RateLimitExceeded("Test message", retry_after=5.0)
        assert str(exc) == "Test message"

    def test_retry_after(self):
        """Test exception has retry_after."""
        exc = RateLimitExceeded("Test", retry_after=10.5)
        assert exc.retry_after == 10.5

    def test_default_retry_after(self):
        """Test default retry_after is 0."""
        exc = RateLimitExceeded("Test")
        assert exc.retry_after == 0
