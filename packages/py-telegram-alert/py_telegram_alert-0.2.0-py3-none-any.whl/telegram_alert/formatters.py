"""
Text formatting utilities for Telegram messages.
"""


def escape_markdown(text: str) -> str:
    """
    Escape text for safe Telegram MarkdownV2 transmission.

    Escapes MarkdownV2 special characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
    Preserves unicode characters (emojis, international text).

    Args:
        text: Raw text to escape

    Returns:
        Escaped text safe for MarkdownV2 parse mode
    """
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for char in special_chars:
        text = text.replace(char, f"\\{char}")

    return text


def progress_bar(
    value: float,
    max_value: float,
    width: int = 20,
    filled: str = "\u2588",
    empty: str = "\u2591",
) -> str:
    """
    Render a text progress bar.

    Args:
        value: Current value
        max_value: Maximum value (for percentage calculation)
        width: Bar width in characters (default 20)
        filled: Character for filled portion (default: full block)
        empty: Character for empty portion (default: light shade)

    Returns:
        Formatted progress bar string like "[████████░░░░] 8.0/10"

    Example:
        >>> progress_bar(75, 100)
        '[███████████████░░░░░] 75.0/100'
    """
    if max_value <= 0:
        ratio = 0.0
    else:
        ratio = min(1.0, max(0.0, value / max_value))

    filled_count = int(ratio * width)
    empty_count = width - filled_count

    bar = filled * filled_count + empty * empty_count

    # Format cleanly: integers as integers, floats with 1 decimal
    if value == int(value) and max_value == int(max_value):
        return f"[{bar}] {int(value)}/{int(max_value)}"
    return f"[{bar}] {value:.1f}/{max_value:.1f}"


def truncate(text: str, max_length: int = 4096, suffix: str = "...") -> str:
    """
    Truncate text to fit Telegram's message length limit.

    Telegram messages have a 4096 character limit. This function
    truncates at that boundary while preserving whole words.

    Args:
        text: Text to truncate
        max_length: Maximum length (default 4096, Telegram's limit)
        suffix: Suffix to append when truncated (default "...")

    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text

    # Leave room for suffix
    cut_at = max_length - len(suffix)

    # Try to break at word boundary
    truncated = text[:cut_at]
    last_space = truncated.rfind(" ")
    if last_space > cut_at * 0.8:  # Only break at space if reasonably close
        truncated = truncated[:last_space]

    return truncated + suffix
