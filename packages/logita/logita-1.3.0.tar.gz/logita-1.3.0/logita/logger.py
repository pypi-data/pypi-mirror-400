import logging
from colorama import Fore, Style, init
from datetime import datetime
import traceback
import sys

init(autoreset=True)


class Logita:
    """
    Logita is a custom logging utility that supports colored console output,
    file logging, and structured log levels. It simplifies logging with
    timestamps and optional color coding for easier visual parsing.

    Attributes:
        COLOR_DICT (dict): Mapping of log levels to colorama color codes.
        use_colors (bool): Flag to enable or disable colored output.
        logger (logging.Logger): Internal Python logger instance for file logging only.
    """

    COLOR_DICT = {
        "debug": Fore.WHITE,
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "critical": Fore.MAGENTA + Style.BRIGHT,
        "exception": Fore.RED + Style.BRIGHT,
    }

    def __init__(self, use_colors=True, log_file: str | None = None):
        """
        Initializes the Logita logger.

        Args:
            use_colors (bool, optional): Enables colored console output. Defaults to True.
            log_file (str | None, optional): Path to a log file to save logs. Defaults to None.
        """
        self.use_colors = use_colors
        self.logger = logging.getLogger("Logita")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False  # Prevent duplicate logs if other loggers exist

        # Clear existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Only file handler, no console handler
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
            ))
            self.logger.addHandler(file_handler)

    def _format(self, level: str, message: str) -> str:
        """
        Formats the log message with timestamp and optional colors.

        Args:
            level (str): Log level (debug, info, success, warning, error, critical, exception).
            message (str): The message to format.

        Returns:
            str: Formatted message with timestamp and color codes.
        """
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        color = self.COLOR_DICT.get(level, "") if self.use_colors else ""
        reset = Style.RESET_ALL if self.use_colors else ""
        return f"{timestamp} {color}{message}{reset}"

    def _log(self, level: str, message: str, line=True, exc_info=False):
        """
        Internal method to handle logging at various levels.

        Args:
            level (str): Log level.
            message (str): Message to log.
            line (bool, optional): Whether to print a new line. Defaults to True.
            exc_info (bool, optional): Whether to include exception info. Defaults to False.
        """
        formatted = self._format(level, message)
        if line:
            print(formatted, end="\n")
        else:
            print(f"{formatted}", end="\r")  # Overwrite current line

        # Only log to file if handler exists
        if self.logger.hasHandlers():
            log_level = logging.DEBUG if level == "success" else getattr(logging, level.upper(), logging.INFO)
            self.logger.log(log_level, message, exc_info=exc_info)

    # Level-specific logging methods
    def debug(self, message, line=True):
        """
        Logs a message at the DEBUG level.

        This is intended for detailed diagnostic information useful during development
        or troubleshooting. The message will appear in the console (with optional coloring)
        and in the log file if one is configured.

        Args:
            message (str): The message to log.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        self._log("debug", message, line)

    def info(self, message, line=True):
        """
        Logs a message at the INFO level.

        This level is used for general informational messages about the application's
        normal operation. Useful for tracking flow and state changes.

        Args:
            message (str): The message to log.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        self._log("info", message, line)

    def success(self, message, line=True):
        """
        Logs a message indicating a successful operation.

        This is a custom level (internally mapped to DEBUG) to highlight successful
        events or completed actions. It is visually distinguished with green color
        in console output when colors are enabled.

        Args:
            message (str): The message to log.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        self._log("success", message, line)

    def warning(self, message, line=True):
        """
        Logs a message at the WARNING level.

        Use this to indicate potential issues, non-critical errors, or situations
        that require attention but do not stop program execution.

        Args:
            message (str): The message to log.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        self._log("warning", message, line)

    def error(self, message, line=True):
        """
        Logs a message at the ERROR level.

        This level is used to indicate serious problems that have occurred,
        such as exceptions or failed operations that may affect program flow.

        Args:
            message (str): The message to log.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        self._log("error", message, line)

    def critical(self, message, line=True):
        """
        Logs a message at the CRITICAL level.

        This level indicates very severe errors that may cause the program to
        terminate or require immediate attention.

        Args:
            message (str): The message to log.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        self._log("critical", message, line)

    def exception(self, message, line=True):
        """
        Logs an exception message including the full traceback.

        This is used inside exception handling blocks to provide detailed
        error information. The traceback will be appended to the message,
        helping with debugging and error analysis.

        Args:
            message (str): A custom message describing the exception.
            line (bool, optional): Whether to print the message with a newline.
                                   If False, the message overwrites the current line. Defaults to True.
        """
        tb = traceback.format_exc()
        full_message = f"{message}\n{tb}" if tb.strip() else message
        self._log("exception", full_message, line, exc_info=True)

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception(f"Exception captured in context: {exc_val}")
        return False
