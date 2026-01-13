"""Tests for TelegramAlert client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from telegram_alert import ConfigError, RateLimitError, SendError, TelegramAlert


class TestTelegramAlertInit:
    """Tests for TelegramAlert initialization."""

    def test_init_with_explicit_config(self):
        """Should accept explicit token and chat_id."""
        alert = TelegramAlert(token="test-token", chat_id="123456")
        assert alert.chat_id == "123456"
        assert "test-token" in alert.api_url

    def test_init_with_list_of_chat_ids(self):
        """Should accept list of chat IDs."""
        alert = TelegramAlert(token="test-token", chat_id=["123", "456", "789"])
        assert alert.chat_ids == ["123", "456", "789"]
        assert alert.chat_id == "123"  # First one is primary

    def test_init_from_env(self, monkeypatch):
        """Should load config from environment variables."""
        monkeypatch.setenv("TELEGRAM_TOKEN", "env-token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "789")

        alert = TelegramAlert()
        assert alert.chat_id == "789"
        assert "env-token" in alert.api_url

    def test_init_comma_separated_chat_ids(self, monkeypatch):
        """Should parse comma-separated chat IDs from env."""
        monkeypatch.setenv("TELEGRAM_TOKEN", "env-token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "123, 456, 789")

        alert = TelegramAlert()
        assert alert.chat_ids == ["123", "456", "789"]

    def test_init_missing_token_raises(self, monkeypatch):
        """Should raise ConfigError when token is missing."""
        monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        with patch("telegram_alert.config._load_dotenv"):
            with pytest.raises(ConfigError) as exc_info:
                TelegramAlert()
            assert "token" in str(exc_info.value).lower()

    def test_init_missing_chat_id_raises(self, monkeypatch):
        """Should raise ConfigError when chat_id is missing."""
        monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        with patch("telegram_alert.config._load_dotenv"):
            with pytest.raises(ConfigError) as exc_info:
                TelegramAlert()
            assert "chat" in str(exc_info.value).lower()


class TestTelegramAlertSend:
    """Tests for send method."""

    @pytest.fixture
    def alert(self):
        """Create alert with test credentials."""
        return TelegramAlert(token="test-token", chat_id="123")

    @pytest.fixture
    def mock_response(self):
        """Create successful mock response."""
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        return response

    @pytest.mark.asyncio
    async def test_send_success(self, alert, mock_response):
        """Should return True on successful send."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send("Test message")
            assert result is True
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_includes_chat_id(self, alert, mock_response):
        """Should include chat_id in request payload."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Test")
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["chat_id"] == "123"

    @pytest.mark.asyncio
    async def test_send_silent(self, alert, mock_response):
        """Should set disable_notification when silent=True."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Test", silent=True)
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["disable_notification"] is True

    @pytest.mark.asyncio
    async def test_send_plain_text(self, alert, mock_response):
        """Should not include parse_mode for plain text."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Test", parse_mode=None)
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert "parse_mode" not in payload

    @pytest.mark.asyncio
    async def test_send_markdown(self, alert, mock_response):
        """Should include parse_mode and escape for MarkdownV2."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Hello_world", parse_mode="MarkdownV2")
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["parse_mode"] == "MarkdownV2"
            assert "\\_" in payload["text"]  # Escaped underscore

    @pytest.mark.asyncio
    async def test_send_to_multiple_chats(self, mock_response):
        """Should broadcast to all chat IDs."""
        alert = TelegramAlert(token="test-token", chat_id=["111", "222", "333"])

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send("Broadcast")
            assert result is True
            assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_send_to_specific_chat(self, alert, mock_response):
        """Should send to specific chat via send_to."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_to("999", "Specific message")
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["chat_id"] == "999"


class TestTelegramAlertTest:
    """Tests for test() method."""

    @pytest.mark.asyncio
    async def test_test_success(self):
        """Should return True when credentials are valid."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.test()
            assert result is True

    @pytest.mark.asyncio
    async def test_test_failure(self):
        """Should return False when credentials are invalid."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.test()
            assert result is False


class TestTelegramAlertContextManager:
    """Tests for context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Should close client on exit."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        async with alert:
            # Force client creation
            alert._client = AsyncMock()

        # Client should be closed
        assert alert._client is None


class TestTelegramAlertSendSync:
    """Tests for send_sync method."""

    def test_send_sync_success(self):
        """Should work as sync wrapper."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = alert.send_sync("Test")
            assert result is True


class TestTelegramAlertSendFile:
    """Tests for send_file method."""

    @pytest.fixture
    def alert(self):
        """Create alert with test credentials."""
        return TelegramAlert(token="test-token", chat_id="123")

    @pytest.fixture
    def mock_response(self):
        """Create successful mock response."""
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        return response

    @pytest.mark.asyncio
    async def test_send_file_from_path(self, alert, mock_response, tmp_path):
        """Should send file from path."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send_file(test_file)
            assert result is True
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_file_from_bytes(self, alert, mock_response):
        """Should send file from bytes with filename."""
        file_content = b"Binary content"

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send_file(file_content, filename="data.bin")
            assert result is True

    @pytest.mark.asyncio
    async def test_send_file_bytes_without_filename_raises(self, alert):
        """Should raise ValueError when bytes provided without filename."""
        with pytest.raises(ValueError) as exc_info:
            await alert.send_file(b"Binary content")
        assert "filename" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_file_not_found_raises(self, alert):
        """Should raise SendError when file doesn't exist."""
        with pytest.raises(SendError) as exc_info:
            await alert.send_file("/nonexistent/path/file.txt")
        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_file_auto_detects_photo(self, alert, mock_response, tmp_path):
        """Should auto-detect photo type from extension."""
        test_file = tmp_path / "image.jpg"
        test_file.write_bytes(b"fake image data")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file(test_file)
            call_args = mock_client.post.call_args
            url = call_args.args[0]
            assert "sendPhoto" in url

    @pytest.mark.asyncio
    async def test_send_file_auto_detects_video(self, alert, mock_response, tmp_path):
        """Should auto-detect video type from extension."""
        test_file = tmp_path / "video.mp4"
        test_file.write_bytes(b"fake video data")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file(test_file)
            call_args = mock_client.post.call_args
            url = call_args.args[0]
            assert "sendVideo" in url

    @pytest.mark.asyncio
    async def test_send_file_unknown_extension_defaults_to_document(
        self, alert, mock_response, tmp_path
    ):
        """Should default to document for unknown extensions."""
        test_file = tmp_path / "data.xyz"
        test_file.write_bytes(b"unknown format")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file(test_file)
            call_args = mock_client.post.call_args
            url = call_args.args[0]
            assert "sendDocument" in url

    @pytest.mark.asyncio
    async def test_send_file_explicit_type_overrides_detection(
        self, alert, mock_response, tmp_path
    ):
        """Should use explicit file_type over auto-detection."""
        test_file = tmp_path / "image.jpg"
        test_file.write_bytes(b"fake data")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file(test_file, file_type="document")
            call_args = mock_client.post.call_args
            url = call_args.args[0]
            assert "sendDocument" in url

    @pytest.mark.asyncio
    async def test_send_file_with_caption(self, alert, mock_response, tmp_path):
        """Should include caption in request."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file(test_file, caption="My caption")
            call_args = mock_client.post.call_args
            data = call_args.kwargs["data"]
            assert data["caption"] == "My caption"

    @pytest.mark.asyncio
    async def test_send_file_with_markdown_caption(self, alert, mock_response, tmp_path):
        """Should escape caption with parse_mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file(test_file, caption="Hello_world", parse_mode="MarkdownV2")
            call_args = mock_client.post.call_args
            data = call_args.kwargs["data"]
            assert data["parse_mode"] == "MarkdownV2"
            assert "\\_" in data["caption"]

    @pytest.mark.asyncio
    async def test_send_file_to_multiple_chats(self, mock_response, tmp_path):
        """Should broadcast file to all chat IDs."""
        alert = TelegramAlert(token="test-token", chat_id=["111", "222", "333"])
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send_file(test_file)
            assert result is True
            assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_send_file_to_specific_chat(self, alert, mock_response, tmp_path):
        """Should send file to specific chat via send_file_to."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_file_to("999", test_file)
            call_args = mock_client.post.call_args
            data = call_args.kwargs["data"]
            assert data["chat_id"] == "999"

    def test_send_file_sync_success(self, tmp_path):
        """Should work as sync wrapper."""
        alert = TelegramAlert(token="test-token", chat_id="123")
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = alert.send_file_sync(test_file)
            assert result is True
