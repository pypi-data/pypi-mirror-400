"""
py-telegram-alert: Simple, async-first Telegram alerts for Python.

Basic usage:
    >>> from telegram_alert import TelegramAlert
    >>> alert = TelegramAlert()  # Auto-loads TELEGRAM_TOKEN, TELEGRAM_CHAT_ID from env
    >>> await alert.send("Hello World!")

    >>> # Sync usage for scripts
    >>> alert.send_sync("Quick message!")

    >>> # With formatting helpers
    >>> from telegram_alert import progress_bar
    >>> await alert.send(f"Download: {progress_bar(75, 100)}")
"""

from .client import FileType, TelegramAlert
from .exceptions import ConfigError, RateLimitError, SendError, TelegramAlertError
from .formatters import escape_markdown, progress_bar, truncate

__version__ = "0.2.0"

__all__ = [
    # Main client
    "TelegramAlert",
    # Types
    "FileType",
    # Exceptions
    "TelegramAlertError",
    "ConfigError",
    "RateLimitError",
    "SendError",
    # Formatters
    "escape_markdown",
    "progress_bar",
    "truncate",
]
