"""Custom exceptions for the KNAI Provider SDK."""


class KNAIError(Exception):
    """Base exception for all KNAI SDK errors."""

    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (HTTP {self.status_code})"
        return self.message


class SessionExpiredError(KNAIError):
    """Raised when the provider session has expired or is no longer valid."""

    def __init__(self, message: str = "Session has expired", **kwargs):
        super().__init__(message, **kwargs)


class InsufficientBalanceError(KNAIError):
    """Raised when the wallet has insufficient balance for the charge."""

    def __init__(self, message: str = "Insufficient wallet balance", **kwargs):
        super().__init__(message, **kwargs)


class InvalidAPIKeyError(KNAIError):
    """Raised when the provider API key is invalid or unauthorized."""

    def __init__(self, message: str = "Invalid API key", **kwargs):
        super().__init__(message, **kwargs)
