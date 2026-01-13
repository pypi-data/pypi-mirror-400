"""SecBlast API exceptions."""

from __future__ import annotations


class SecBlastError(Exception):
    """Base exception for all SecBlast API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(SecBlastError):
    """Raised when API key is invalid or missing (401)."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401)


class RateLimitError(SecBlastError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit_type: str | None = None,
    ):
        super().__init__(message, status_code=429)
        self.limit_type = limit_type  # "requests" or "bandwidth"


class ValidationError(SecBlastError):
    """Raised when request parameters are invalid (400)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class NotFoundError(SecBlastError):
    """Raised when a resource is not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ServerError(SecBlastError):
    """Raised when the API returns a server error (5xx)."""

    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__(message, status_code=status_code)
