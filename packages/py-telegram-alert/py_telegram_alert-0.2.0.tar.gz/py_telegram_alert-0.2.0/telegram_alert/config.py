"""
Configuration loading for telegram-alert.

Handles environment variable detection with .env file support.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ConfigError


@dataclass
class TelegramConfig:
    """Telegram configuration container."""

    token: str
    chat_ids: list[str]

    @property
    def api_url(self) -> str:
        """Construct the Telegram Bot API URL."""
        return f"https://api.telegram.org/bot{self.token}/sendMessage"


def _load_dotenv() -> bool:
    """
    Load .env file from current or parent directories.

    Returns:
        True if .env was found and loaded, False otherwise.
    """
    from dotenv import load_dotenv

    current = Path.cwd()
    for path in [current, *current.parents]:
        env_file = path / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return True

    # Fallback: let dotenv search normally
    load_dotenv()
    return False


def load_config(
    token: str | None = None,
    chat_id: str | list[str] | None = None,
) -> TelegramConfig:
    """
    Load Telegram configuration from arguments or environment.

    Priority:
    1. Explicit arguments
    2. Environment variables (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

    Args:
        token: Bot token (optional, falls back to env)
        chat_id: Chat ID or list of chat IDs (optional, falls back to env)

    Returns:
        TelegramConfig with validated credentials

    Raises:
        ConfigError: If token or chat_id cannot be resolved
    """
    # Load .env file
    _load_dotenv()

    # Resolve token
    resolved_token = token or os.getenv("TELEGRAM_TOKEN")
    if not resolved_token:
        raise ConfigError(
            "Missing Telegram token. "
            "Provide token argument or set TELEGRAM_TOKEN in your .env file."
        )

    # Resolve chat_id(s)
    if chat_id is not None:
        # Explicit argument provided
        if isinstance(chat_id, list):
            resolved_chat_ids = chat_id
        else:
            resolved_chat_ids = [chat_id]
    else:
        # Fall back to environment variable
        env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not env_chat_id:
            raise ConfigError(
                "Missing Telegram chat ID. "
                "Provide chat_id argument or set TELEGRAM_CHAT_ID in your .env file."
            )
        # Support comma-separated list in env var
        resolved_chat_ids = [cid.strip() for cid in env_chat_id.split(",")]

    if not resolved_chat_ids:
        raise ConfigError("At least one chat ID is required.")

    return TelegramConfig(token=resolved_token, chat_ids=resolved_chat_ids)
