"""Logging handlers for arlogi.

This module provides custom logging handlers including:
- ColoredConsoleHandler: Rich-based colored console output
- JSONHandler/JSONFileHandler: Structured JSON logging
- ArlogiSyslogHandler: Syslog integration with fallback support
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.logging import RichHandler


class ColoredConsoleHandler(RichHandler):
    """A logging handler that uses rich for colored console output.

    Features:
    - Automatic project root detection for relative file paths (cached)
    - Customizable color schemes per log level
    - Rich traceback support
    - Compact single-character level indicators (T, D, I, W, E, C)
    """

    # Class-level cache for project root to avoid repeated filesystem operations
    _project_root_cache: str | None = None

    def __init__(
        self,
        show_time: bool = False,
        show_level: bool = True,
        show_path: bool = True,
        level_styles: dict[str, str] | None = None,
        project_root: str | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        """Initialize the colored console handler.

        Args:
            show_time: Whether to show timestamps in output
            show_level: Whether to show log levels
            show_path: Whether to show file paths
            level_styles: Custom color styles per level (e.g., {"info": "blue"})
            project_root: Project root for relative path calculation
            *args: Additional positional arguments for RichHandler
            **kwargs: Additional keyword arguments for RichHandler
        """
        # Default level styles: INFO is lighter (grey75) than DEBUG/TRACE (grey37)
        default_styles = {
            "trace": "grey37",
            "debug": "grey37",
            "info": "grey75",
            "warning": "yellow",
            "error": "red",
            "critical": "bold red",
        }
        if level_styles:
            default_styles.update(level_styles)

        # Default to a console that supports colors and directed to stdout
        if "console" not in kwargs:
            kwargs["console"] = Console(force_terminal=True, file=sys.stdout)

        # Enable rich tracebacks by default for enhanced error display
        kwargs.setdefault("rich_tracebacks", True)
        kwargs.setdefault("markup", True)

        super().__init__(
            *args,
            show_time=show_time,
            show_level=show_level,
            show_path=show_path,
            **kwargs,
        )

        # Set level styles after initialization (for compatibility with older rich versions)
        self.level_styles = default_styles

        # Store project root for relative path calculation (use cache if available)
        self.project_root = project_root or self._find_project_root()

    def _find_project_root(self) -> str:
        """Find the project root by looking for common indicators.

        Searches upward from the current directory for files like
        .git, pyproject.toml, setup.py, etc.

        Result is cached at class level to avoid repeated filesystem operations.

        Returns:
            The absolute path to the project root, or current directory if not found
        """
        # Return cached value if available
        if ColoredConsoleHandler._project_root_cache is not None:
            return ColoredConsoleHandler._project_root_cache

        current = os.getcwd()

        # Common project root indicators
        indicators = [
            ".git",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            ".hg",
            ".svn"
        ]

        # Walk up the directory tree looking for indicators
        while current != os.path.dirname(current):  # Stop at filesystem root
            for indicator in indicators:
                if os.path.exists(os.path.join(current, indicator)):
                    ColoredConsoleHandler._project_root_cache = os.path.abspath(current)
                    return ColoredConsoleHandler._project_root_cache
            current = os.path.dirname(current)

        # If no indicators found, fall back to current working directory
        ColoredConsoleHandler._project_root_cache = os.getcwd()
        return ColoredConsoleHandler._project_root_cache

    def render(
        self,
        *,
        record: logging.LogRecord,
        traceback: Any,
        message_renderable: Any,
    ) -> Any:
        """Override render method to show relative paths from project root.

        Args:
            record: The log record to render
            traceback: Optional traceback information
            message_renderable: The formatted message

        Returns:
            A renderable object for Rich to display
        """
        from pathlib import Path

        # Calculate relative path instead of just filename
        try:
            relpath = os.path.relpath(record.pathname, self.project_root)
            path = relpath
        except (ValueError, OSError):
            # Fallback to filename if relative path calculation fails
            path = Path(record.pathname).name

        level = self.get_level_text(record)
        time_format = None if self.formatter is None else self.formatter.datefmt
        from datetime import datetime
        log_time = datetime.fromtimestamp(record.created)

        log_renderable = self._log_render(
            self.console,
            [message_renderable] if not traceback else [message_renderable, traceback],
            log_time=log_time,
            time_format=time_format,
            level=level,
            path=path,
            line_no=record.lineno,
            link_path=None,  # Disable links to avoid file:// URLs
        )
        return log_renderable

    def get_level_text(self, record: logging.LogRecord) -> Any:
        """Get level text as a single character with styling.

        Args:
            record: The log record

        Returns:
            A Rich Text object with the level character
        """
        from rich.text import Text

        level_name = record.levelname
        # Map TRACE to T, DEBUG to D, etc.
        char = level_name[0]

        style = self.level_styles.get(level_name.lower(), "default")
        # Compact single character indicator
        return Text(f"{char} ", style=style)

    def render_message(self, record: logging.LogRecord, message: str) -> Any:
        """Render message text with level-specific styling.

        Args:
            record: The log record
            message: The message to render

        Returns:
            A Rich Text object with the styled message
        """
        message_text = super().render_message(record, message)

        # Apply style to the entire message text
        level_name = record.levelname.lower()
        style = self.level_styles.get(level_name, "default")

        message_text.style = style
        return message_text


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured log output.

    Outputs log records as JSON with standard fields plus any extra
    fields added via the `extra` parameter.

    Includes robust error handling for JSON serialization failures.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record

        Note:
            If JSON serialization fails, falls back to a basic format
            with error information to prevent logging crashes.
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record (excluding standard logging attributes)
        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message"
        }

        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_data[key] = value

        # Try to serialize with error handling
        try:
            return json.dumps(log_data, default=str)
        except (TypeError, ValueError) as e:
            # Fallback to basic format on serialization failure
            return json.dumps({
                "timestamp": log_data.get("timestamp"),
                "level": log_data.get("level"),
                "logger_name": log_data.get("logger_name"),
                "message": str(log_data.get("message", "")),
                "module": log_data.get("module"),
                "function": log_data.get("function"),
                "line_number": log_data.get("line_number"),
                "error": f"JSON serialization failed: {e}"
            })


class JSONHandler(logging.StreamHandler):
    """A logging handler that outputs log records as JSON to a stream.

    Defaults to stderr for compatibility with log aggregation tools.

    Properly manages custom streams to prevent resource leaks.
    """

    def __init__(self, stream: Any = None):
        """Initialize the JSON stream handler.

        Args:
            stream: The stream to write to (defaults to sys.stderr if None)

        Note:
            Custom streams are tracked and closed when the handler is closed.
            System streams (sys.stderr, sys.stdout) are not closed.
        """
        # Track whether we own the stream for cleanup purposes
        self._owns_stream = stream is not None
        super().__init__(stream)
        self.setFormatter(JSONFormatter())

    def close(self):
        """Close the handler and the stream if we own it.

        Only closes custom streams, not system streams like sys.stderr.
        """
        try:
            # Flush before closing
            self.flush()

            # Close custom stream if we own it
            if self._owns_stream and self.stream and hasattr(self.stream, 'close'):
                # Don't close system streams
                if self.stream not in (sys.stderr, sys.stdout):
                    self.stream.close()
        finally:
            # Always call parent close
            super().close()


class JSONFileHandler(logging.FileHandler):
    """A logging handler that outputs log records as JSON to a file.

    Automatically creates parent directories if they don't exist.
    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        encoding: str | None = None,
        delay: bool = False
    ):
        """Initialize the JSON file handler.

        Args:
            filename: Path to the log file
            mode: File open mode (default: "a" for append)
            encoding: File encoding (default: None for system default)
            delay: Whether to delay file opening until first emit

        Note:
            Thread-safe: Uses exist_ok=True to safely handle concurrent
            directory creation from multiple threads.
        """
        # Ensure parent directory exists
        # Thread-safe: exist_ok=True handles race conditions where multiple
        # threads might try to create the same directory
        parent_dir = os.path.dirname(os.path.abspath(filename))
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        super().__init__(filename, mode, encoding, delay)
        self.setFormatter(JSONFormatter())


class ArlogiSyslogHandler(logging.handlers.SysLogHandler):
    """A robust syslog handler with standard formatting and automatic fallback.

    Features:
    - Standard arlogi formatting for consistent syslog messages
    - Automatic fallback to UDP on localhost:514 if /dev/log fails
    - Graceful degradation - won't crash the application if syslog is unavailable
    """

    def __init__(
        self,
        address: str | tuple[str, int] = "/dev/log",
        facility: int | str = logging.handlers.SysLogHandler.LOG_USER,
        socktype: int | None = None,
    ):
        """Initialize the syslog handler.

        Args:
            address: Syslog server address (default: "/dev/log" for Unix socket)
            facility: Syslog facility (default: LOG_USER)
            socktype: Socket type (SOCK_STREAM or SOCK_DGRAM)
        """
        try:
            super().__init__(address=address, facility=facility, socktype=socktype)
            self.setFormatter(
                logging.Formatter("%(name)s[%(process)d]: %(levelname)s: %(message)s")
            )
        except Exception as e:
            # Fallback for systems without /dev/log (e.g., macOS or some containers)
            if address == "/dev/log":
                # Try UDP on localhost as a last resort
                try:
                    super().__init__(
                        address=("localhost", 514),
                        facility=facility,
                        socktype=socktype
                    )
                except Exception:
                    # If everything fails, silently continue - don't crash
                    # the application just because logging setup failed
                    pass
            else:
                raise e
