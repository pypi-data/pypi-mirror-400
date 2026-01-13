"""Custom exceptions for Firecrawl API errors."""

__all__ = [
    "AuthenticationError",
    "FirecrawlError",
    "PaymentRequiredError",
    "RateLimitError",
]


class FirecrawlError(Exception):
    """Base exception for all Firecrawl errors."""


class RateLimitError(FirecrawlError):
    """HTTP 429 - Rate limit exceeded."""


class PaymentRequiredError(FirecrawlError):
    """HTTP 402 - Payment/credits required."""


class AuthenticationError(FirecrawlError):
    """HTTP 401 - Invalid or missing API key."""
