"""Rate limiter for Product Hunt API.

Handles both complexity-based (GraphQL) and request-based rate limiting.
- GraphQL: 6,250 complexity points per 15 minutes
- Other endpoints: 450 requests per 15 minutes

Rate limit headers:
- X-Rate-Limit-Limit: Application limit for the 15 minute period
- X-Rate-Limit-Remaining: Remaining quota for the reset period
- X-Rate-Limit-Reset: Seconds until the rate limit is reset
"""

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response

from .exceptions import RateLimitError

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    """Current rate limit status."""

    limit: int = 0
    remaining: int = 0
    reset_seconds: int = 0
    last_updated: float = field(default_factory=time.time)

    @property
    def reset_at(self) -> float:
        """Unix timestamp when the rate limit resets."""
        return self.last_updated + self.reset_seconds

    @property
    def is_exhausted(self) -> bool:
        """Check if the rate limit is exhausted."""
        return self.remaining <= 0 and time.time() < self.reset_at

    @property
    def seconds_until_reset(self) -> float:
        """Seconds until the rate limit resets."""
        return max(0, self.reset_at - time.time())


class RateLimiter:
    """Handles rate limiting for Product Hunt API requests.

    Features:
    - Tracks rate limit status from response headers
    - Automatically waits when rate limited (if auto_wait=True)
    - Provides rate limit information for manual handling
    """

    HEADER_LIMIT = "X-Rate-Limit-Limit"
    HEADER_REMAINING = "X-Rate-Limit-Remaining"
    HEADER_RESET = "X-Rate-Limit-Reset"

    def __init__(self, auto_wait: bool = True, max_wait_seconds: float = 900):
        """Initialize the rate limiter.

        Args:
            auto_wait: If True, automatically wait when rate limited.
            max_wait_seconds: Maximum seconds to wait for rate limit reset.
                              Default is 900 (15 minutes).
        """
        self.auto_wait = auto_wait
        self.max_wait_seconds = max_wait_seconds
        self._rate_limit_info = RateLimitInfo()
        self._async_lock = asyncio.Lock()  # For async operations
        self._sync_lock = threading.Lock()  # For sync operations

    @property
    def rate_limit_info(self) -> RateLimitInfo:
        """Get current rate limit information."""
        return self._rate_limit_info

    def update_from_response(self, response: "Response") -> RateLimitInfo:
        """Update rate limit info from response headers (thread-safe).

        Args:
            response: The HTTP response from the API.

        Returns:
            Updated rate limit information.
        """
        with self._sync_lock:
            headers = response.headers

            limit = headers.get(self.HEADER_LIMIT)
            remaining = headers.get(self.HEADER_REMAINING)
            reset = headers.get(self.HEADER_RESET)

            if limit is not None:
                self._rate_limit_info.limit = int(limit)
            if remaining is not None:
                self._rate_limit_info.remaining = int(remaining)
            if reset is not None:
                self._rate_limit_info.reset_seconds = int(reset)
                self._rate_limit_info.last_updated = time.time()

            logger.debug(
                "Updated rate limit info from response",
                extra={
                    "limit": self._rate_limit_info.limit,
                    "remaining": self._rate_limit_info.remaining,
                    "reset_seconds": self._rate_limit_info.reset_seconds
                }
            )

            return self._rate_limit_info

    async def wait_if_needed(self) -> None:
        """Wait if rate limit is exhausted.

        Raises:
            RateLimitError: If rate limit is exhausted and auto_wait is False,
                           or if wait time exceeds max_wait_seconds.
        """
        async with self._async_lock:
            if not self._rate_limit_info.is_exhausted:
                return

            wait_time = self._rate_limit_info.seconds_until_reset

            logger.warning(
                "Rate limit exhausted, waiting for reset",
                extra={
                    "wait_time_seconds": wait_time,
                    "remaining": self._rate_limit_info.remaining
                }
            )

            if not self.auto_wait:
                raise RateLimitError(self._rate_limit_info)

            if wait_time > self.max_wait_seconds:
                logger.error(
                    "Wait time exceeds maximum",
                    extra={
                        "wait_time_seconds": wait_time,
                        "max_wait_seconds": self.max_wait_seconds
                    }
                )
                raise RateLimitError(
                    self._rate_limit_info,
                    f"Rate limit exceeded. Wait time ({wait_time:.1f}s) exceeds "
                    f"max_wait_seconds ({self.max_wait_seconds}s).",
                )

            logger.info(f"Waiting {wait_time:.1f}s for rate limit reset")
            await asyncio.sleep(wait_time)

    async def handle_response(self, response: "Response") -> RateLimitInfo:
        """Handle response and update rate limit info.

        Args:
            response: The HTTP response from the API.

        Returns:
            Updated rate limit information.

        Raises:
            RateLimitError: If response is 429 and auto_wait is False.
        """
        info = self.update_from_response(response)

        if response.status_code == 429:
            logger.warning("Received 429 Too Many Requests response")
            if self.auto_wait:
                await self.wait_if_needed()
            else:
                logger.error("Rate limit exceeded and auto_wait is disabled")
                raise RateLimitError(info, "Rate limit exceeded (HTTP 429).")

        return info

    def sync_wait_if_needed(self) -> None:
        """Synchronous version of wait_if_needed (thread-safe)."""
        wait_time = 0.0
        with self._sync_lock:
            if not self._rate_limit_info.is_exhausted:
                return

            wait_time = self._rate_limit_info.seconds_until_reset

            logger.warning(
                "Rate limit exhausted, waiting for reset",
                extra={
                    "wait_time_seconds": wait_time,
                    "remaining": self._rate_limit_info.remaining
                }
            )

            if not self.auto_wait:
                raise RateLimitError(self._rate_limit_info)

            if wait_time > self.max_wait_seconds:
                logger.error(
                    "Wait time exceeds maximum",
                    extra={
                        "wait_time_seconds": wait_time,
                        "max_wait_seconds": self.max_wait_seconds
                    }
                )
                raise RateLimitError(
                    self._rate_limit_info,
                    f"Rate limit exceeded. Wait time ({wait_time:.1f}s) exceeds "
                    f"max_wait_seconds ({self.max_wait_seconds}s).",
                )

        # Sleep outside the lock to allow other threads to proceed
        if wait_time > 0:
            logger.info(f"Waiting {wait_time:.1f}s for rate limit reset")
            time.sleep(wait_time)

    def sync_handle_response(self, response: "Response") -> RateLimitInfo:
        """Synchronous version of handle_response."""
        info = self.update_from_response(response)

        if response.status_code == 429:
            logger.warning("Received 429 Too Many Requests response")
            if self.auto_wait:
                self.sync_wait_if_needed()
            else:
                logger.error("Rate limit exceeded and auto_wait is disabled")
                raise RateLimitError(info, "Rate limit exceeded (HTTP 429).")

        return info
