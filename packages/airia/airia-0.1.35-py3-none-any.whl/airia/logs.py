import logging
import os
import sys
import uuid
from contextvars import ContextVar
from typing import BinaryIO, Optional, TextIO, Union

# Create a context variable to store correlation ID
correlation_id_context: ContextVar[str] = ContextVar("correlation_id", default="")

# ANSI color codes
RESET = "\033[0m"
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
}
GREY = "\033[90m"  # Grey for metadata
MAGENTA = "\033[35m"  # Magenta for correlation ID


def _enable_windows_ansi_support():
    """Enable ANSI color support on Windows."""
    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            # If it fails, colors just won't work on Windows
            pass


# Enable Windows ANSI support at module load
_enable_windows_ansi_support()


def get_correlation_id() -> str:
    """
    Get the current correlation ID from context or return empty string if not set.

    Returns:
        str: The current correlation ID
    """
    return correlation_id_context.get()


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set a correlation ID in the current context.

    Args:
        correlation_id (Optional[str]): The correlation ID to set. If None, a new UUID will be generated.

    Returns:
        str: The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_context.set(correlation_id)
    return correlation_id


def clear_correlation_id() -> None:
    """Clear the correlation ID from the current context."""
    correlation_id_context.set("")


class CorrelationIdFilter(logging.Filter):
    """Filter to inject correlation_id into log records."""

    def filter(self, record):
        """Add correlation_id to the log record."""
        record.correlation_id = get_correlation_id() or "no-correlation-id"
        return True


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log output using ANSI codes."""

    def __init__(self, fmt: Optional[str] = None, use_colors: bool = True):
        """
        Initialize the colored formatter.

        Args:
            fmt: The format string for log messages
            use_colors: Whether to use ANSI color codes
        """
        super().__init__(fmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        if not self.use_colors:
            return super().format(record)

        # Get the color for this log level
        level_color = COLORS.get(record.levelname, "")

        # Save the original values
        orig_levelname = record.levelname
        orig_msg = record.msg

        # Color the level name
        record.levelname = f"{level_color}{record.levelname}{RESET}"

        # Format the message
        formatted = super().format(record)

        # Restore original values
        record.levelname = orig_levelname
        record.msg = orig_msg

        # Add colors to specific parts of the formatted message
        # Color the correlation ID if present
        if hasattr(record, "correlation_id"):
            formatted = formatted.replace(
                f"[{record.correlation_id}]",
                f"{MAGENTA}[{record.correlation_id}]{RESET}",
            )

        # Color the timestamp (first part before |)
        parts = formatted.split("|", 1)
        if len(parts) > 1:
            timestamp_part = parts[0].split("]", 1)
            if len(timestamp_part) > 1:
                # Has correlation ID
                formatted = (
                    timestamp_part[0]
                    + "]"
                    + f"{GREY}{timestamp_part[1]}{RESET}|"
                    + parts[1]
                )
            else:
                # No correlation ID
                formatted = f"{GREY}{parts[0]}{RESET}|{parts[1]}"

        return formatted


def configure_logging(
    format_string: Optional[str] = None,
    level: str = "INFO",
    sink: Union[os.PathLike[str], TextIO, BinaryIO] = sys.stderr,
    include_correlation_id: bool = True,
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure the logger with custom settings using Python's standard logging module.

    Args:
        format_string (Optional[str]): The format string for log messages.
                                      If None, a default format will be used.
        level (str): The minimum logging level. Default: "INFO"
        sink: Where to send the log. Default: sys.stderr
              Can be a file path, TextIO, or BinaryIO.
        include_correlation_id (bool): Whether to include correlation ID in log messages.
                                      Default: True
        use_colors (bool): Whether to use colored output for console logging.
                          Automatically disabled for file output. Default: True

    Returns:
        logging.Logger: The configured logger object

    Example:
        ```python
        from airia import configure_logging

        # Basic configuration with colors
        logger = configure_logging()

        # Disable colors
        logger = configure_logging(use_colors=False)

        # File-based logging (colors automatically disabled)
        file_logger = configure_logging(
            level="DEBUG",
            sink="app.log",
            include_correlation_id=True
        )

        # Console output
        console_logger = configure_logging(
            level="INFO",
            sink=sys.stdout
        )
        ```
    """
    logger = logging.getLogger("airia")
    logger.handlers.clear()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Determine if this is file or console output
    is_file_output = isinstance(sink, (str, os.PathLike))

    # Create handler based on sink type
    if is_file_output:
        handler = logging.FileHandler(str(sink))
        # Disable colors for file output
        use_colors = False
    elif hasattr(sink, "write"):
        handler = logging.StreamHandler(sink)  # type: ignore
    else:
        handler = logging.StreamHandler(sys.stderr)

    # Create formatter
    if format_string is None:
        if include_correlation_id:
            format_string = "[%(correlation_id)s] %(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        else:
            format_string = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    # Use ColoredFormatter for console, regular Formatter for files
    if use_colors and not is_file_output:
        formatter = ColoredFormatter(format_string, use_colors=True)
    else:
        formatter = logging.Formatter(format_string)

    handler.setFormatter(formatter)

    # Add correlation ID filter if enabled
    if include_correlation_id:
        handler.addFilter(CorrelationIdFilter())

    logger.addHandler(handler)

    return logger


# Example usage:
if __name__ == "__main__":
    # Basic configuration (uses sys.stderr with colors)
    log = configure_logging()
    log.debug("Debug message")
    log.info("Basic logging configured successfully")
    log.warning("This is a warning")
    log.error("This is an error")

    # Set a correlation ID
    set_correlation_id("request-123")
    log.info("This log has a correlation ID")

    # Change correlation ID
    set_correlation_id("request-456")
    log.info("This log has a different correlation ID")

    # Use auto-generated correlation ID
    set_correlation_id()
    log.info("This log has an auto-generated correlation ID")

    # File-based logging (colors automatically disabled)
    file_log = configure_logging(
        level="DEBUG",
        sink="app.log",
    )
    file_log.debug("File logging configured successfully")

    # Stream-based logging with colors
    stream_log = configure_logging(level="INFO", sink=sys.stdout)
    stream_log.info("Stream logging configured successfully")

    # Disable colors explicitly
    no_color_log = configure_logging(use_colors=False)
    no_color_log.info("Logging without colors")
