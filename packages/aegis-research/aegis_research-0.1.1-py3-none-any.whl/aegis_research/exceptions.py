"""
Custom exceptions for the Aegis Research SDK.
"""


class AegisError(Exception):
    """Base exception for Aegis Research SDK."""
    pass


class AuthenticationError(AegisError):
    """Raised when API key is invalid or missing."""
    pass


class RateLimitError(AegisError):
    """Raised when rate limit is exceeded."""
    pass


class InsufficientCreditsError(AegisError):
    """Raised when there are not enough credits for the request."""
    pass


class ResearchError(AegisError):
    """Raised when research execution fails."""
    pass
