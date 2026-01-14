"""Natural Payments SDK exceptions."""

from __future__ import annotations


class NaturalError(Exception):
    """Base exception for Natural SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class AuthenticationError(NaturalError):
    """Invalid or missing API key."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401, code="authentication_error")


class InvalidRequestError(NaturalError):
    """Malformed request parameters."""

    def __init__(self, message: str, *, code: str = "invalid_request"):
        super().__init__(message, status_code=400, code=code)


class PaymentError(NaturalError):
    """Payment-specific failure."""

    def __init__(self, message: str, *, code: str = "payment_error"):
        super().__init__(message, status_code=400, code=code)


class InsufficientFundsError(PaymentError):
    """Not enough balance for payment."""

    def __init__(self, message: str = "Insufficient funds"):
        super().__init__(message, code="insufficient_funds")


class RecipientNotFoundError(PaymentError):
    """Invalid recipient."""

    def __init__(self, message: str = "Recipient not found"):
        super().__init__(message, code="recipient_not_found")


class RateLimitError(NaturalError):
    """Too many requests."""

    def __init__(self, message: str = "Rate limit exceeded", *, retry_after: int | None = None):
        super().__init__(message, status_code=429, code="rate_limit_exceeded")
        self.retry_after = retry_after


class ServerError(NaturalError):
    """Internal server error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500, code="server_error")
