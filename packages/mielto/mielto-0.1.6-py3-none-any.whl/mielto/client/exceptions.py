"""Exception classes for Mielto API."""

from typing import Any, Dict, Optional


class MieltoError(Exception):
    """Base exception for all Mielto errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(MieltoError):
    """Exception raised for authentication errors (401)."""

    pass


class PermissionError(MieltoError):
    """Exception raised for permission errors (403)."""

    pass


class NotFoundError(MieltoError):
    """Exception raised when a resource is not found (404)."""

    pass


class ValidationError(MieltoError):
    """Exception raised for validation errors (422)."""

    pass


class RateLimitError(MieltoError):
    """Exception raised when rate limit is exceeded (429)."""

    pass


class ServerError(MieltoError):
    """Exception raised for server errors (5xx)."""

    pass


class TimeoutError(MieltoError):
    """Exception raised when a request times out."""

    pass


class ConnectionError(MieltoError):
    """Exception raised when a connection error occurs."""

    pass


class PaymentRequiredError(MieltoError):
    """Exception raised when a payment is required."""

    pass


class CreditLimitExceededError(MieltoError):
    """Exception raised when a credit limit is exceeded."""

    pass


class OverageLimitExceededError(MieltoError):
    """Exception raised when an overage limit is exceeded."""

    pass


__all__ = [
    "MieltoError",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "ConnectionError",
    "PaymentRequiredError",
    "CreditLimitExceededError",
    "OverageLimitExceededError",
]
