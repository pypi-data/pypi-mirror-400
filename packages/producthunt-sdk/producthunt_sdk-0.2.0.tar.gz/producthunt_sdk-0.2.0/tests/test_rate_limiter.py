"""Tests for rate limiter module."""



import time

import httpx
import pytest

from producthunt_sdk.rate_limiter import RateLimiter, RateLimitError, RateLimitInfo


class TestRateLimitInfo:
    """Tests for RateLimitInfo dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        info = RateLimitInfo()
        assert info.limit == 0
        assert info.remaining == 0
        assert info.reset_seconds == 0
        assert info.last_updated > 0

    def test_reset_at_calculation(self):
        """Test reset_at property calculation."""
        info = RateLimitInfo(reset_seconds=60, last_updated=1000.0)
        assert info.reset_at == 1060.0

    def test_is_exhausted_when_remaining_zero(self):
        """Test is_exhausted when remaining is zero and reset is in future."""
        info = RateLimitInfo(remaining=0, reset_seconds=60, last_updated=time.time())
        assert info.is_exhausted is True

    def test_is_not_exhausted_with_remaining(self):
        """Test is_exhausted when there's remaining quota."""
        info = RateLimitInfo(remaining=100, reset_seconds=60, last_updated=time.time())
        assert info.is_exhausted is False

    def test_is_not_exhausted_after_reset(self):
        """Test is_exhausted after reset time has passed."""
        info = RateLimitInfo(remaining=0, reset_seconds=0, last_updated=time.time() - 10)
        assert info.is_exhausted is False

    def test_seconds_until_reset(self):
        """Test seconds_until_reset calculation."""
        info = RateLimitInfo(reset_seconds=60, last_updated=time.time())
        assert 59 <= info.seconds_until_reset <= 60

    def test_seconds_until_reset_past(self):
        """Test seconds_until_reset when reset is in the past."""
        info = RateLimitInfo(reset_seconds=0, last_updated=time.time() - 100)
        assert info.seconds_until_reset == 0


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_default_initialization(self):
        """Test default rate limiter initialization."""
        limiter = RateLimiter()
        assert limiter.auto_wait is True
        assert limiter.max_wait_seconds == 900

    def test_custom_initialization(self):
        """Test custom rate limiter initialization."""
        limiter = RateLimiter(auto_wait=False, max_wait_seconds=60)
        assert limiter.auto_wait is False
        assert limiter.max_wait_seconds == 60

    def test_update_from_response(self):
        """Test updating rate limit info from response headers."""
        limiter = RateLimiter()
        response = httpx.Response(
            200,
            headers={
                "X-Rate-Limit-Limit": "6250",
                "X-Rate-Limit-Remaining": "5000",
                "X-Rate-Limit-Reset": "600",
            },
        )

        info = limiter.update_from_response(response)

        assert info.limit == 6250
        assert info.remaining == 5000
        assert info.reset_seconds == 600

    def test_update_from_response_partial_headers(self):
        """Test updating with only some headers present."""
        limiter = RateLimiter()
        response = httpx.Response(
            200,
            headers={
                "X-Rate-Limit-Remaining": "100",
            },
        )

        info = limiter.update_from_response(response)

        assert info.remaining == 100
        assert info.limit == 0  # Not updated

    def test_sync_wait_if_needed_not_exhausted(self):
        """Test sync_wait_if_needed when not exhausted."""
        limiter = RateLimiter()
        limiter._rate_limit_info = RateLimitInfo(remaining=100)

        # Should not raise or wait
        limiter.sync_wait_if_needed()

    def test_sync_wait_if_needed_exhausted_no_auto_wait(self):
        """Test sync_wait_if_needed raises when exhausted and auto_wait=False."""
        limiter = RateLimiter(auto_wait=False)
        limiter._rate_limit_info = RateLimitInfo(
            remaining=0, reset_seconds=60, last_updated=time.time()
        )

        with pytest.raises(RateLimitError) as exc_info:
            limiter.sync_wait_if_needed()

        assert "Rate limit exceeded" in str(exc_info.value)

    def test_sync_wait_if_needed_exceeds_max_wait(self):
        """Test sync_wait_if_needed raises when wait exceeds max."""
        limiter = RateLimiter(auto_wait=True, max_wait_seconds=30)
        limiter._rate_limit_info = RateLimitInfo(
            remaining=0, reset_seconds=60, last_updated=time.time()
        )

        with pytest.raises(RateLimitError) as exc_info:
            limiter.sync_wait_if_needed()

        assert "exceeds max_wait_seconds" in str(exc_info.value)

    def test_sync_handle_response_429_no_auto_wait(self):
        """Test sync_handle_response raises on 429 without auto_wait."""
        limiter = RateLimiter(auto_wait=False)
        response = httpx.Response(
            429,
            headers={
                "X-Rate-Limit-Limit": "6250",
                "X-Rate-Limit-Remaining": "0",
                "X-Rate-Limit-Reset": "60",
            },
        )

        with pytest.raises(RateLimitError) as exc_info:
            limiter.sync_handle_response(response)

        assert "HTTP 429" in str(exc_info.value)

    def test_sync_handle_response_success(self):
        """Test sync_handle_response with successful response."""
        limiter = RateLimiter()
        response = httpx.Response(
            200,
            headers={
                "X-Rate-Limit-Limit": "6250",
                "X-Rate-Limit-Remaining": "6000",
                "X-Rate-Limit-Reset": "900",
            },
        )

        info = limiter.sync_handle_response(response)

        assert info.remaining == 6000

    def test_rate_limit_info_property(self):
        """Test rate_limit_info property returns current info."""
        limiter = RateLimiter()
        limiter._rate_limit_info = RateLimitInfo(limit=100, remaining=50)

        info = limiter.rate_limit_info

        assert info.limit == 100
        assert info.remaining == 50


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_default_message(self):
        """Test default error message."""
        info = RateLimitInfo(reset_seconds=60, last_updated=time.time())
        error = RateLimitError(info)

        assert "Rate limit exceeded" in str(error)
        assert info == error.rate_limit_info

    def test_custom_message(self):
        """Test custom error message."""
        info = RateLimitInfo()
        error = RateLimitError(info, "Custom message")

        assert str(error) == "Custom message"


@pytest.mark.asyncio
class TestRateLimiterAsync:
    """Async tests for RateLimiter."""

    async def test_wait_if_needed_not_exhausted(self):
        """Test async wait_if_needed when not exhausted."""
        limiter = RateLimiter()
        limiter._rate_limit_info = RateLimitInfo(remaining=100)

        await limiter.wait_if_needed()  # Should not raise

    async def test_wait_if_needed_exhausted_no_auto_wait(self):
        """Test async wait_if_needed raises when exhausted."""
        limiter = RateLimiter(auto_wait=False)
        limiter._rate_limit_info = RateLimitInfo(
            remaining=0, reset_seconds=60, last_updated=time.time()
        )

        with pytest.raises(RateLimitError):
            await limiter.wait_if_needed()

    async def test_handle_response_success(self):
        """Test async handle_response with success."""
        limiter = RateLimiter()
        response = httpx.Response(
            200,
            headers={
                "X-Rate-Limit-Limit": "6250",
                "X-Rate-Limit-Remaining": "6000",
                "X-Rate-Limit-Reset": "900",
            },
        )

        info = await limiter.handle_response(response)

        assert info.remaining == 6000

    async def test_handle_response_429_no_auto_wait(self):
        """Test async handle_response raises on 429."""
        limiter = RateLimiter(auto_wait=False)
        response = httpx.Response(
            429,
            headers={
                "X-Rate-Limit-Remaining": "0",
                "X-Rate-Limit-Reset": "60",
            },
        )

        with pytest.raises(RateLimitError):
            await limiter.handle_response(response)
