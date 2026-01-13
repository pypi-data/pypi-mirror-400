# Logita

Logita is a lightweight and customizable Python logging utility focused on improving developer experience in the console, with optional file logging support. It provides colored output, structured log levels, and a simple API designed primarily for CLI tools, scripts, and developer-facing applications.

## Features

- Timestamped log messages printed directly to the console.
- Optional colored output using `colorama`.
- Supported log levels:
  - debug
  - info
  - success (custom semantic level)
  - warning
  - error
  - critical
  - exception (with full traceback support)
- Optional file logging using Python's built-in `logging` module.
- Ability to print logs with or without a newline (useful for progress output).
- Context manager support (`with` statement) for automatic exception capturing.
- No dependency on global logging configuration.

## Installation

```bash
pip install logita
```

Ensure `colorama` is installed:

```bash
pip install colorama
```

## Basic Usage

```python
from logita import Logita

with Logita(use_colors=True) as log:
    log.info("Informational message")
    log.success("Operation completed successfully")
    log.warning("Potential issue detected")
    log.error("An error occurred")
    log.debug("Processing...", line=False)
    log.debug(" done")
    log.critical("Critical failure")
    log.exception("Unhandled exception")
```

## File Logging

Logita can optionally persist logs to a file while still printing to the console:

```python
log = Logita(use_colors=True, log_file="app.log")
log.info("This message appears in the console and in the log file")
```

File logs use the following format:

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] message
```

## Constructor Parameters

- `use_colors` (bool, default: True)
  Enables or disables colored console output.

- `log_file` (str | None, default: None)
  Path to a file where logs will be written using the standard `logging` module.

## Design Notes

- Console output is handled explicitly via `print` for full control over formatting and colors.
- File logging is isolated and handled by an internal `logging.Logger` instance.
- Logita is best suited for scripts, CLI tools, and developer utilities.
- It is not designed to replace full-featured logging frameworks in highly concurrent or distributed systems.

## License

MIT License
