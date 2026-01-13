"""Factory for creating logger instances with caller attribution support.

This module provides the LoggerFactory class for creating and configuring
loggers, along with the TraceLogger class that adds custom TRACE level
and caller attribution features.
"""

import logging
from typing import Any

from .config import LoggingConfig, get_default_level, is_test_mode
from .handler_factory import HandlerFactory
from .handlers import ArlogiSyslogHandler, JSONFileHandler, JSONHandler
from .levels import TRACE_LEVEL_NUM, register_trace_level
from .types import LoggerProtocol


class TraceLogger(logging.Logger):
    """Custom logger class with trace() and caller attribution support.

    This logger extends the standard Python Logger with:
    - A custom TRACE level (below DEBUG)
    - Caller attribution via caller_depth parameter
    - Automatic extra field handling from unknown kwargs
    """

    def _get_caller_info(self, depth: int) -> tuple[str, str]:
        """Find the name of the module and function at the specified depth.

        Args:
            depth: Stack depth to inspect (0 = current function)

        Returns:
            Tuple of (module_name, function_name)
        """
        try:
            import sys

            # Stack frame offsets:
            # 0: _get_caller_info
            # 1: _process_params
            # 2: info/debug/... (wrapper method)
            # 3: actual call site (depth 0)
            # 4: caller of call site (depth 1)
            frame = sys._getframe(depth + 3)
            module = frame.f_globals.get("__name__", "unknown")
            name = frame.f_code.co_name
            return module, name
        except (ValueError, AttributeError):
            return "unknown", "unknown"

    def _process_params(
        self, msg: Any, kwargs: dict[str, Any]
    ) -> tuple[Any, dict[str, Any]]:
        """Process caller attribution and move arbitrary kwargs to 'extra'.

        Args:
            msg: The log message
            kwargs: Keyword arguments including optional caller_depth

        Returns:
            Tuple of (processed_message, processed_kwargs)
        """
        # 1. Handle caller attribution
        caller_depth_val = kwargs.pop("caller_depth", None)

        if caller_depth_val is not None:
            try:
                from rich.markup import escape

                depth = int(caller_depth_val)
                m0, _ = self._get_caller_info(0)
                mN, nN = self._get_caller_info(depth)

                # Format based on depth:
                # 0: [function_name()]
                # 1+: [from .function_name()] (same module)
                #     [from module.function_name()] (different module)
                if depth >= 1:
                    if mN == m0:
                        attribution = f"from .{nN}()"
                    else:
                        attribution = f"from {mN}.{nN}()"
                else:
                    attribution = f"{nN}()"

                # Add attribution as suffix (RichHandler indents multi-line)
                safe_attribution = escape(f"[{attribution}]")
                suffix = f"\n{safe_attribution}"

                if isinstance(msg, str):
                    msg = msg + suffix
                else:
                    msg = str(msg) + suffix
            except (ValueError, TypeError, ImportError):
                pass

        # 2. Move unknown kwargs to 'extra' for structured logging
        standard_kwargs = {"exc_info", "stack_info", "stacklevel", "extra"}
        extra = kwargs.get("extra", {})

        # Collect unknown kwargs
        custom_kwargs = {}
        for key in list(kwargs.keys()):
            if key not in standard_kwargs:
                custom_kwargs[key] = kwargs.pop(key)

        if custom_kwargs:
            if not isinstance(extra, dict):
                extra = {"_original_extra": extra}
            extra.update(custom_kwargs)
            kwargs["extra"] = extra

        # Ensure log entries point to user's code, not this wrapper
        kwargs.setdefault("stacklevel", 2)
        return msg, kwargs

    # Standard logging methods with caller attribution support
    def trace(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a message with TRACE level (below DEBUG).

        Args:
            msg: The message to log
            *args: Format arguments for the message
            **kwargs: Optional caller_depth for caller attribution
        """
        msg, kwargs = self._process_params(msg, kwargs)
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, msg, args, **kwargs)

    def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().debug(msg, *args, **kwargs)

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().info(msg, *args, **kwargs)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().warning(msg, *args, **kwargs)

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().error(msg, *args, **kwargs)

    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().critical(msg, *args, **kwargs)

    def exception(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log an exception with traceback."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().exception(msg, *args, **kwargs)

    def log(self, level: int, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a message at the specified level."""
        msg, kwargs = self._process_params(msg, kwargs)
        super().log(level, msg, *args, **kwargs)


class LoggerFactory:
    """Factory for creating and configuring logger instances.

    This factory manages the global logging configuration and provides
    methods to get logger instances with various configurations.
    """

    _initialized = False
    _global_logger: TraceLogger | None = None

    @classmethod
    def setup(
        cls,
        level: int | str = logging.INFO,
        module_levels: dict[str, str | int] | None = None,
        json_file_name: str | None = None,
        json_file_only: bool = False,
        use_syslog: bool = False,
        syslog_address: str | tuple[str, int] = "/dev/log",
        show_time: bool = False,
        show_level: bool = True,
        show_path: bool = True,
    ) -> None:
        """Centralized logging setup for arlogi.

        This method configures the root logger with the specified handlers
        and levels. It can be called multiple times to update configuration.

        Args:
            level: Global root log level
            module_levels: Per-module level overrides
            json_file_name: Path to JSON log file
            json_file_only: If True, only output JSON (no console)
            use_syslog: Enable syslog output
            syslog_address: Syslog server address
            show_time: Show timestamps in console output
            show_level: Show log levels in console output
            show_path: Show file paths in console output
        """
        config = LoggingConfig.from_kwargs(
            level=level,
            module_levels=module_levels,
            json_file_name=json_file_name,
            json_file_only=json_file_only,
            use_syslog=use_syslog,
            syslog_address=syslog_address,
            show_time=show_time,
            show_level=show_level,
            show_path=show_path,
        )
        cls._apply_configuration(config)

    @classmethod
    def _apply_configuration(cls, config: LoggingConfig) -> None:
        """Apply a LoggingConfig to the root logger.

        Args:
            config: The logging configuration to apply
        """
        cls._initialize_trace_level()
        cls._configure_root_logger(config)

        if not is_test_mode():
            cls._clear_and_add_handlers(config)

        cls._configure_module_levels(config)
        cls._initialized = True

    @classmethod
    def _initialize_trace_level(cls) -> None:
        """Register the custom TRACE level with Python's logging module."""
        register_trace_level()
        logging.setLoggerClass(TraceLogger)

    @classmethod
    def _configure_root_logger(cls, config: LoggingConfig) -> None:
        """Configure the root logger level.

        Args:
            config: The logging configuration
        """
        root = logging.getLogger()
        root.setLevel(config.resolved_level)

    @classmethod
    def _clear_and_add_handlers(cls, config: LoggingConfig) -> None:
        """Clear existing handlers and add configured ones.

        Args:
            config: The logging configuration
        """
        root = logging.getLogger()

        # Remove existing handlers
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        # Add configured handlers via factory
        handlers = HandlerFactory.create_handlers(config)
        for handler in handlers:
            root.addHandler(handler)

    @classmethod
    def _configure_module_levels(cls, config: LoggingConfig) -> None:
        """Apply module-specific log level overrides.

        Args:
            config: The logging configuration
        """
        if config.module_levels:
            for name, m_level in config.module_levels.items():
                logger = logging.getLogger(name)
                resolved_level = config.resolve_module_level(name, m_level)
                logger.setLevel(resolved_level)
                # Ensure propagation to root for inherited settings
                logger.propagate = True

    @staticmethod
    def is_test_mode() -> bool:
        """Detect if running under a test runner.

        Returns:
            True if pytest, unittest, or PYTEST_CURRENT_TEST is detected
        """
        return is_test_mode()

    @classmethod
    def get_logger(cls, name: str, level: int | str | None = None) -> LoggerProtocol:
        """Get a logger instance conforming to LoggerProtocol.

        Auto-initializes with default settings if called before setup().

        Args:
            name: Logger name (typically __name__ of the module)
            level: Optional level override for this logger

        Returns:
            A logger instance supporting caller attribution
        """
        if not cls._initialized:
            cls.setup(level=get_default_level())

        logger = logging.getLogger(name)
        if level is not None:
            logger.setLevel(level)

        return logger  # type: ignore

    @classmethod
    def get_json_logger(
        cls, name: str = "json", json_file_name: str | None = None
    ) -> LoggerProtocol:
        """Get a logger that only outputs to JSON, bypassing root handlers.

        Args:
            name: Logger name suffix
            json_file_name: Optional file path for JSON output

        Returns:
            A JSON-only logger instance
        """
        logger = logging.getLogger(f"arlogi.json.{name}")
        logger.propagate = False

        # Close existing handlers to prevent resource leaks
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        if json_file_name:
            logger.addHandler(JSONFileHandler(json_file_name))
        else:
            logger.addHandler(JSONHandler())

        logger.setLevel(logging.DEBUG)
        return logger  # type: ignore

    @classmethod
    def get_syslog_logger(
        cls, name: str = "syslog", address: str | tuple[str, int] = "/dev/log"
    ) -> LoggerProtocol:
        """Get a logger that only outputs to Syslog, bypassing root handlers.

        Args:
            name: Logger name suffix
            address: Syslog server address

        Returns:
            A syslog-only logger instance
        """
        logger = logging.getLogger(f"arlogi.syslog.{name}")
        logger.propagate = False

        # Close existing handlers to prevent resource leaks
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        logger.addHandler(ArlogiSyslogHandler(address=address))
        logger.setLevel(logging.DEBUG)
        return logger  # type: ignore

    @classmethod
    def cleanup_json_logger(cls, name: str = "json") -> None:
        """Clean up handlers for a JSON logger to free resources.

        This method closes all handlers associated with the named JSON logger
        and removes them from the logger. Use this to explicitly release file
        handles and other resources when you're done with a logger.

        Args:
            name: Logger name suffix (must match the name used in get_json_logger)

        Example:
            >>> logger = get_json_logger("temp", "logs/temp.json")
            >>> logger.info("Done logging")
            >>> cleanup_json_logger("temp")  # Close the file handle
        """
        logger_name = f"arlogi.json.{name}"
        logger = logging.getLogger(logger_name)

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    @classmethod
    def cleanup_syslog_logger(cls, name: str = "syslog") -> None:
        """Clean up handlers for a syslog logger to free resources.

        Args:
            name: Logger name suffix

        Example:
            >>> logger = get_syslog_logger("temp")
            >>> logger.info("Done logging")
            >>> cleanup_syslog_logger("temp")  # Close the socket
        """
        logger_name = f"arlogi.syslog.{name}"
        logger = logging.getLogger(logger_name)

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    @classmethod
    def get_global_logger(cls) -> LoggerProtocol:
        """Get or initialize the global logger instance.

        Returns:
            The global application logger instance
        """
        if cls._global_logger is None:
            cls._global_logger = cls.get_logger("app")  # type: ignore
        return cls._global_logger  # type: ignore


# Public API helper functions

def setup_logging(
    level: int | str = logging.INFO,
    module_levels: dict[str, str | int] | None = None,
    json_file_name: str | None = None,
    json_file_only: bool = False,
    use_syslog: bool = False,
    syslog_address: str | tuple[str, int] = "/dev/log",
    show_time: bool = False,
    show_level: bool = True,
    show_path: bool = True,
) -> None:
    """Set up arlogi logging with the specified configuration.

    This is a convenience wrapper around LoggerFactory.setup().

    Args:
        level: Global root log level
        module_levels: Per-module level overrides
        json_file_name: Path to JSON log file
        json_file_only: If True, only output JSON (no console)
        use_syslog: Enable syslog output
        syslog_address: Syslog server address
        show_time: Show timestamps in console output
        show_level: Show log levels in console output
        show_path: Show file paths in console output
    """
    LoggerFactory.setup(
        level=level,
        module_levels=module_levels,
        json_file_name=json_file_name,
        json_file_only=json_file_only,
        use_syslog=use_syslog,
        syslog_address=syslog_address,
        show_time=show_time,
        show_level=show_level,
        show_path=show_path,
    )


def get_logger(name: str, level: int | str | None = None) -> LoggerProtocol:
    """Get a logger instance with caller attribution support.

    Args:
        name: Logger name (typically __name__)
        level: Optional level override

    Returns:
        A logger instance
    """
    return LoggerFactory.get_logger(name, level)


def get_json_logger(
    name: str = "json", json_file_name: str | None = None
) -> LoggerProtocol:
    """Get a dedicated JSON-only logger.

    Args:
        name: Logger name suffix
        json_file_name: Optional file path for JSON output

    Returns:
        A JSON-only logger instance
    """
    return LoggerFactory.get_json_logger(name, json_file_name=json_file_name)


def get_syslog_logger(
    name: str = "syslog", address: str | tuple[str, int] = "/dev/log"
) -> LoggerProtocol:
    """Get a dedicated syslog-only logger.

    Args:
        name: Logger name suffix
        address: Syslog server address

    Returns:
        A syslog-only logger instance
    """
    return LoggerFactory.get_syslog_logger(name, address)


def cleanup_json_logger(name: str = "json") -> None:
    """Clean up handlers for a JSON logger to free resources.

    This function closes all handlers associated with the named JSON logger
    and removes them from the logger. Use this to explicitly release file
    handles and other resources when you're done with a logger.

    Args:
        name: Logger name suffix (must match the name used in get_json_logger)

    Example:
        >>> logger = get_json_logger("temp", "logs/temp.json")
        >>> logger.info("Done logging")
        >>> cleanup_json_logger("temp")  # Close the file handle
    """
    LoggerFactory.cleanup_json_logger(name)


def cleanup_syslog_logger(name: str = "syslog") -> None:
    """Clean up handlers for a syslog logger to free resources.

    Args:
        name: Logger name suffix

    Example:
        >>> logger = get_syslog_logger("temp")
        >>> logger.info("Done logging")
        >>> cleanup_syslog_logger("temp")  # Close the socket
    """
    LoggerFactory.cleanup_syslog_logger(name)
