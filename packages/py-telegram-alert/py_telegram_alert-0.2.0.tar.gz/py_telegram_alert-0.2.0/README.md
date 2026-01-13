# py-telegram-alert

Simple, async-first Telegram alerts for Python.

[![PyPI version](https://badge.fury.io/py/py-telegram-alert.svg)](https://badge.fury.io/py/py-telegram-alert)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Installation

```bash
pip install py-telegram-alert
```

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 2. Get Your Chat ID

1. Message your new bot (send any message)
2. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id":` in the response - that's your chat ID

### 3. Configure Your Credentials

Rename `.env.example` to `.env` and fill in your values:

```env
TELEGRAM_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here
```

### 4. Send Messages

```python
from telegram_alert import TelegramAlert

alert = TelegramAlert()

# Async
await alert.send("Hello World!")

# Sync (for simple scripts)
alert.send_sync("Hello World!")
```

That's it!

## Examples

### Basic Messages

```python
from telegram_alert import TelegramAlert

alert = TelegramAlert()
await alert.send("Server started successfully")
```

### Silent Messages

Send without notification sound:

```python
await alert.send("Background task complete", silent=True)
```

### Test Your Credentials

Verify your bot token works without sending a message:

```python
alert = TelegramAlert()
if alert.test_sync():
    print("Credentials are valid!")
else:
    print("Check your .env file")
```

### Multiple Chat IDs

Send to multiple chats at once:

```python
# Option 1: Comma-separated in .env
# TELEGRAM_CHAT_ID=123456,789012,345678

# Option 2: Pass a list
alert = TelegramAlert(chat_id=["123456", "789012"])
await alert.send("Broadcast message")  # Sends to all

# Option 3: Send to specific chat
await alert.send_to("999999", "Just for this chat")
```

### Formatted Messages

```python
# HTML formatting
await alert.send("<b>Bold</b> and <i>italic</i>", parse_mode="HTML")

# MarkdownV2 (auto-escaped)
await alert.send("*Bold* and _italic_", parse_mode="MarkdownV2")
```

### Progress Bar

```python
from telegram_alert import progress_bar

msg = f"Download: {progress_bar(75, 100)}"
await alert.send(msg)
# Output: Download: [███████████████░░░░░] 75/100
```

### Context Manager

Reuse connections for better performance:

```python
async with TelegramAlert() as alert:
    await alert.send("Message 1")
    await alert.send("Message 2")  # Reuses connection
```

### File Attachments

Send photos, documents, videos, audio, and more:

```python
# Send a file (type auto-detected from extension)
await alert.send_file("screenshot.png")
await alert.send_file("report.pdf", caption="Monthly report")

# Send with explicit type
await alert.send_file("data.bin", file_type="document")

# Send raw bytes
await alert.send_file(image_bytes, filename="chart.png")

# With formatted caption
await alert.send_file("photo.jpg", caption="*Important* update", parse_mode="MarkdownV2")

# Sync version
alert.send_file_sync("export.csv", caption="Data export")
```

**Supported file types** (auto-detected from extension):
- `photo` - jpg, jpeg, png, webp
- `video` - mp4, mov, avi, mkv, webm
- `audio` - mp3, wav, flac, m4a
- `voice` - ogg
- `animation` - gif
- `document` - everything else (default)

### Error Handling

```python
from telegram_alert import TelegramAlert, ConfigError, SendError, RateLimitError

try:
    alert = TelegramAlert()
    await alert.send("Test message")
except ConfigError as e:
    print(f"Check your .env file: {e}")
except RateLimitError as e:
    print(f"Too many messages, retry after {e.retry_after}s")
except SendError as e:
    print(f"Failed to send: {e}")
```

### Sync Usage

For simple scripts that don't use async:

```python
from telegram_alert import TelegramAlert

alert = TelegramAlert()
alert.send_sync("Deployment complete!")
```

> **Note:** `send_sync()` won't work in Jupyter notebooks or async frameworks (FastAPI, etc.) since they already have an event loop running. In those environments, use `await alert.send()` directly.

## API Reference

### TelegramAlert

```python
alert = TelegramAlert(
    token="...",           # Optional, falls back to TELEGRAM_TOKEN
    chat_id="...",         # Optional, falls back to TELEGRAM_CHAT_ID (can be list)
    rate_limit_delay=1.0,  # Seconds between messages
)

# Async methods
await alert.send(message, parse_mode=None, silent=False, ...)
await alert.send_to(chat_id, message, ...)
await alert.send_file(file, caption=None, file_type=None, filename=None, ...)
await alert.send_file_to(chat_id, file, ...)
await alert.test()  # Verify credentials
await alert.close()  # Close connections

# Sync wrappers
alert.send_sync(message, ...)
alert.send_to_sync(chat_id, message, ...)
alert.send_file_sync(file, ...)
alert.send_file_to_sync(chat_id, file, ...)
alert.test_sync()

# Properties
alert.chat_id      # Primary chat ID
alert.chat_ids     # All configured chat IDs
```

### Formatters

- `escape_markdown(text)` - Escape MarkdownV2 special characters (preserves emojis)
- `progress_bar(value, max_value, width=20)` - Visual progress bar
- `truncate(text, max_length=4096)` - Truncate to Telegram's 4096 char limit

### Exceptions

- `ConfigError` - Missing or invalid `.env` configuration
- `SendError` - Message failed to send
- `RateLimitError` - Too many messages (has `.retry_after` seconds)

## License

GPL-3.0
