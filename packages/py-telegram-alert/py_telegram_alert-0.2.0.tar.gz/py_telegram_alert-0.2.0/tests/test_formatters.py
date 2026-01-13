"""Tests for text formatters."""

import pytest

from telegram_alert import escape_markdown, progress_bar, truncate


class TestEscapeMarkdown:
    """Tests for escape_markdown function."""

    def test_escapes_special_chars(self):
        """Should escape all MarkdownV2 special characters."""
        text = "Hello_world *bold* [link](url) `code`"
        result = escape_markdown(text)

        assert "\\_" in result
        assert "\\*" in result
        assert "\\[" in result
        assert "\\]" in result
        assert "\\(" in result
        assert "\\)" in result
        assert "\\`" in result

    def test_preserves_unicode(self):
        """Should preserve emojis and international text."""
        text = "Hello 🎉 World! Café résumé 日本語"
        result = escape_markdown(text)

        assert "🎉" in result
        assert "Café" in result
        assert "日本語" in result

    def test_empty_string(self):
        """Should handle empty string."""
        assert escape_markdown("") == ""

    def test_plain_text(self):
        """Should not modify plain text without special chars."""
        text = "Hello World"
        assert escape_markdown(text) == "Hello World"

    def test_escapes_dots_and_exclamation(self):
        """Should escape dots and exclamation marks."""
        text = "Hello! Price is $100.00"
        result = escape_markdown(text)

        assert "\\!" in result
        assert "\\." in result


class TestProgressBar:
    """Tests for progress_bar function."""

    def test_full_bar(self):
        """Should show full bar at 100%."""
        result = progress_bar(100, 100, width=10)
        assert "\u2588" * 10 in result
        assert "100/100" in result

    def test_half_bar(self):
        """Should show half bar at 50%."""
        result = progress_bar(50, 100, width=10)
        filled_count = result.count("\u2588")
        assert filled_count == 5

    def test_empty_bar(self):
        """Should show empty bar at 0%."""
        result = progress_bar(0, 100, width=10)
        empty_count = result.count("\u2591")
        assert empty_count == 10

    def test_integer_formatting(self):
        """Should show integers without decimal places."""
        result = progress_bar(75, 100, width=10)
        assert "75/100" in result
        assert "75.0" not in result

    def test_float_formatting(self):
        """Should show floats with one decimal place."""
        result = progress_bar(75.5, 100.0, width=10)
        assert "75.5/100.0" in result

    def test_custom_chars(self):
        """Should support custom fill characters."""
        result = progress_bar(50, 100, width=10, filled="#", empty="-")
        assert "#####-----" in result

    def test_zero_max(self):
        """Should handle zero max value."""
        result = progress_bar(50, 0, width=10)
        # Should show empty bar, not crash
        assert "\u2591" in result


class TestTruncate:
    """Tests for truncate function."""

    def test_short_text_unchanged(self):
        """Short text should not be modified."""
        text = "Hello World"
        assert truncate(text, max_length=100) == text

    def test_long_text_truncated(self):
        """Long text should be truncated with suffix."""
        text = "A" * 100
        result = truncate(text, max_length=50)
        assert len(result) <= 50
        assert result.endswith("...")

    def test_breaks_at_word_boundary(self):
        """Should try to break at word boundary."""
        text = "Hello World this is a test message"
        result = truncate(text, max_length=20)
        # Should not cut mid-word if possible
        assert not result.endswith("t...")

    def test_custom_suffix(self):
        """Should support custom suffix."""
        text = "A" * 100
        result = truncate(text, max_length=50, suffix="[more]")
        assert result.endswith("[more]")

    def test_telegram_default_limit(self):
        """Default limit should be 4096 (Telegram max)."""
        text = "A" * 5000
        result = truncate(text)
        assert len(result) <= 4096
