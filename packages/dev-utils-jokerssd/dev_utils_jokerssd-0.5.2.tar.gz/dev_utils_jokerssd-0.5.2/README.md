# Dev Utils

A collection of development utilities, starting with structured logging.

## Installation

```bash
pip install dev-utils-jokerssd
```

## Logging Utils

A powerful wrapper around `structlog` and Python's standard `logging` module to provide structured JSON logging with rotation, async writing, and easy configuration.

### Usage

```python
from dev_utils import LoggingUtils

# Basic Setup
logging_utils = LoggingUtils(
    log_file="app.log",
    log_level="INFO",
    print_output=True,
    json_formatter=True,
    binding_dict={"app_name": "my_app"}
)

logger = logging_utils.get_logger()

# Log something
logger.info("Application started", version="1.0.0")

# Exception logging
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Something went wrong")
```

### Features

-   **Structured JSON Logs**: By default, logs are formatted as JSON for easy parsing by log management tools.
-   **Async Logging**: Uses a background thread for file writing to avoid blocking the main execution path.
-   **Log Rotation**: Automatically rotates log files daily (default).
-   **Context Binding**: Bind global context variables (like `request_id` or `user_id`) to all logs.
-   **Standard API**: Compatible with standard python `logging` (mostly) and `structlog`.

## Lark Wrapper

A wrapper for interaction with Lark/Feishu Custom bots, providing strong typing and error handling.

### Usage

```python
from dev_utils.lark_wrapper import MsgBot, BotType, MsgType, BotStatus

# Initialize the bot
bot = MsgBot(
    chat_id="your-chat-id",
    url="https://open.larksuite.com/open-apis",
    api_name="bot/v2/hook/",
    bot_type=BotType.LARK
)

# Send a text message
response = bot.send_cust_bot_msg(
    message="Hello, World!",
    msg_type=MsgType.TEXT,
    title="Notification"
)

# Check response
if response.status == BotStatus.OK:
    print("Success:", response.msg)
else:
    print("Failed:", response.errors)
```

### Features

-   **Strong Typing**: Uses `BotStatus`, `BotType`, and `BotResponse` for predictable API interactions.
-   **Multi-Platform Support**: Extensible design (currently supports Lark).
-   **Async Support**: `async_send_msg` available for non-blocking operations.
-   **Rich Content**: Supports Post/Rich Text messages via `MsgType.POST`.

