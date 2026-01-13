"""Exceptions for Product Hunt SDK."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .rate_limiter import RateLimitInfo


class ProductHuntError(Exception):
    """Base exception for Product Hunt SDK."""

    pass


class AuthenticationError(ProductHuntError):
    """Raised when authentication fails."""

    pass


class GraphQLError(ProductHuntError):
    """Raised when the GraphQL API returns errors."""

    def __init__(self, errors: list[dict[str, Any]], message: str | None = None):
        self.errors = errors
        self.message = message or self._format_errors()
        super().__init__(self.message)

    def _format_errors(self) -> str:
        messages = [e.get("message", str(e)) for e in self.errors]
        return "; ".join(messages)


class RateLimitError(ProductHuntError):
    """Raised when rate limit is exceeded."""

    def __init__(self, rate_limit_info: "RateLimitInfo", message: str | None = None):
        self.rate_limit_info = rate_limit_info
        self.message = message or (
            f"Rate limit exceeded. Resets in {rate_limit_info.seconds_until_reset:.1f} seconds."
        )
        super().__init__(self.message)


class MutationError(ProductHuntError):
    """Raised when a mutation returns errors."""

    def __init__(self, errors: list[dict[str, Any]], message: str | None = None):
        self.errors = errors
        self.message = message or self._format_errors()
        super().__init__(self.message)

    def _format_errors(self) -> str:
        messages = [
            f"{e.get('field', 'unknown')}: {e.get('message', str(e))}"
            for e in self.errors
        ]
        return "; ".join(messages)
