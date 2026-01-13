2026-01-05

**What's New**
- `dev_utils/lark_wrapper/const.py`: Added `POST` member to `MsgType` enum.
- `dev_utils/lark_wrapper/messege_lark.py`: Enabled sending `POST` type messages via `send_cust_bot_msg` when a title is present for `TEXT` messages.
- `tests/test_msg_bot.py`: Added a test case for `send_cust_bot_msg` with `MsgType.POST`.

**Bugfix**
- `dev_utils/lark_wrapper/messege_lark.py`: Enhanced `send_cust_bot_msg` to gracefully handle `KeyError` during dynamic message formatting (pre_text, title), preventing failures when template variables are missing.

**Dependencies**
- `uv.lock`: Updated dependencies.

Warnings: None

What's New
  README.md
    - Add comprehensive documentation for the Lark wrapper, including usage examples and feature highlights.

Warnings:
None

What's New:
- Added new enums for message types, bot statuses, and bot types in `dev_utils/lark_wrapper/const.py`.
- Introduced a `BotResponse` dataclass for structured API responses in `dev_utils/lark_wrapper/model.py`.
- Created a new test file `tests/verify_refactor.py` for Lark-related functionalities.

Refactor/Improvements:
- `dev_utils/lark_wrapper/messege_lark.py`:
    - Refactored message sending logic into a private `_send_msg` method for improved error handling and reusability.
    - Enhanced `send_cust_bot_msg` to support `title` and additional `kwargs`, returning an `asyncio.Task`.
- `dev_utils/lark_wrapper/msg_bot.py`:
    - Enhanced `MsgBot` to support different bot types (e.g., Lark) and improved initialization.
    - Added asynchronous message sending capability via `async_send_msg`.
- `tests/test_msg_bot.py`:
    - Updated tests to utilize new enums and configured `chat_id` from `.test_settings.toml`.
    - Added tests for new message types and asynchronous sending.

Dependency Updates:
- `pyproject.toml`: Added `pydantic-gsheets` and `pydantic[email]` to dependencies.
- `uv.lock`: Updated to reflect new and existing dependencies, including significant additions for Google APIs, Pydantic, and related libraries.

Configuration:
- `.gitignore`: Added `.pytest_cache/` and `.test_settings.toml` to the ignore list.

Removals:
- `AGENT.md`: Removed the file.

2025-12-26

What's New:
  - dev_utils/lark_wrapper/messege_lark.py
    - Implemented Lark messaging functionality with the LarkRelated class.
  - dev_utils/lark_wrapper/msg_bot.py
    - Introduced the MsgBot class for a unified messaging interface.
  - dev_utils/lark_wrapper/sheet_utils.py
    - Added the LarkSheetAPI class for interacting with Lark sheets.
  - tests/test_msg_bot.py
    - Added unit tests for the new MsgBot.

Refactor:
  - AGENT.md
    - Removed an outdated testing instruction.

Configuration:
  - pyproject.toml
    - Added 'requests' and 'aiohttp' to dependencies.
    - Added 'pytest' to dev dependencies.
  - uv.lock
    - Updated lock file to reflect dependency changes.

Documentation
* Added AI Coding Assistant instructions (AGENT.md).
* Updated README.md with installation instructions for dev-utils-jokerssd and detailed usage of Logging Utils.

Features
* Introduced new package dev_utils with exports for LoggingUtils, LogTagging, LogType, and AsyncTimedRotatingFileHandler (from dev_utils/__init__.py and dev_utils/logging_utils/__init__.py).

Chore
* Updated package version to 0.2.0 (__version__.py).
* Configured pyproject.toml for building and distributing the dev-utils-jokerssd package.

Warnings:
None

What's New:
- `logging_utils/logging_utils.py` (2025-12-24)
  - Implemented `LoggingUtils` class for structured logging with `structlog`.
  - Supports JSON and plain text output.
  - Features asynchronous file rotation and dynamic context binding.
  - Includes a comprehensive test suite for various logging scenarios.
- `logging_utils/rotateHandler.py` (2025-12-24)
  - Added `AsyncTimedRotatingFileHandler` and other asynchronous logging handlers for efficient log management.

Chore:
- `.gitignore` (2025-12-24)
  - Configured to ignore common Python artifacts, build outputs, and virtual environments.
- `.python-version` (2025-12-24)
  - Set project Python version to 3.12.
- `__version__.py` (2025-12-24)
  - Added initial project version "0.0.1".
- `main.py` (2025-12-24)
  - Created a basic application entry point.
- `pyproject.toml` (2025-12-24)
  - Defined project metadata and dependencies, including `structlog`.
- `uv.lock` (2025-12-24)
  - Locked dependency versions for `dev-utils` and `structlog`.
