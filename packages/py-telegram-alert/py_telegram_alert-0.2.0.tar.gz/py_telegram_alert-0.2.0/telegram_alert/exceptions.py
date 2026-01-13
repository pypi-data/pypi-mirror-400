"""
Custom exceptions for telegram-alert.
"""


class TelegramAlertError(Exception):
    """Base exception for telegram-alert."""

    pass


class ConfigError(TelegramAlertError):
    """Raised when configuration is missing or invalid."""

    pass


class RateLimitError(TelegramAlertError):
    """Raised when rate limit is exceeded after all retries."""

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f" (retry after {retry_after}s)"
        super().__init__(msg)


class SendError(TelegramAlertError):
    """Raised when message send fails."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)
