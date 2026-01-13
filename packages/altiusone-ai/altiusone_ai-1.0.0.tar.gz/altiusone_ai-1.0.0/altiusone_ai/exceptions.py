"""
AltiusOne AI SDK - Exceptions
=============================
Custom exceptions for the SDK.
"""


class AltiusOneError(Exception):
    """Base exception for AltiusOne AI SDK."""

    pass


class AuthenticationError(AltiusOneError):
    """Raised when API key is invalid or missing."""

    pass


class RateLimitError(AltiusOneError):
    """Raised when rate limit is exceeded."""

    pass


class APIError(AltiusOneError):
    """Raised when API returns an error."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
