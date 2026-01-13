"""Handler factory for creating logging handlers.

This module provides a centralized factory for creating log handlers,
following the Factory pattern for consistent handler creation and
easier testing.
"""

import logging

from .config import LoggingConfig
from .handlers import (
    ArlogiSyslogHandler,
    ColoredConsoleHandler,
    JSONFileHandler,
    JSONHandler,
)


class HandlerFactory:
    """Factory for creating logging handlers.

    This class encapsulates the creation logic for all handler types,
    making it easier to test and extend with new handler types.
    """

    @staticmethod
    def create_console(config: LoggingConfig) -> ColoredConsoleHandler:
        """Create a colored console handler.

        Args:
            config: Logging configuration

        Returns:
            A configured ColoredConsoleHandler instance

        Example:
            >>> handler = HandlerFactory.create_console(
            ...     LoggingConfig(show_time=True, show_level=True)
            ... )
        """
        return ColoredConsoleHandler(
            show_time=config.show_time,
            show_level=config.show_level,
            show_path=config.show_path,
        )

    @staticmethod
    def create_json_stream() -> JSONHandler:
        """Create a JSON stream handler (outputs to stderr).

        Returns:
            A JSONHandler instance configured for stream output

        Example:
            >>> handler = HandlerFactory.create_json_stream()
        """
        return JSONHandler()

    @staticmethod
    def create_json_file(config: LoggingConfig) -> JSONFileHandler:
        """Create a JSON file handler.

        Args:
            config: Logging configuration with json_file_name set

        Returns:
            A JSONFileHandler instance

        Raises:
            ValueError: If json_file_name is not set in config

        Example:
            >>> config = LoggingConfig(json_file_name="logs/app.jsonl")
            >>> handler = HandlerFactory.create_json_file(config)
        """
        if not config.json_file_name:
            raise ValueError("json_file_name must be set in config")

        return JSONFileHandler(config.json_file_name)

    @staticmethod
    def create_json_handler(config: LoggingConfig) -> logging.Handler:
        """Create the appropriate JSON handler based on configuration.

        Creates either a JSONFileHandler (if json_file_name is set)
        or a JSONHandler for stream output.

        Args:
            config: Logging configuration

        Returns:
            Either JSONFileHandler or JSONHandler based on config

        Example:
            >>> # File handler
            >>> config1 = LoggingConfig(json_file_name="logs/app.jsonl")
            >>> handler1 = HandlerFactory.create_json_handler(config1)
            >>>
            >>> # Stream handler
            >>> config2 = LoggingConfig(json_file_only=True)
            >>> handler2 = HandlerFactory.create_json_handler(config2)
        """
        if config.json_file_name:
            return HandlerFactory.create_json_file(config)
        return HandlerFactory.create_json_stream()

    @staticmethod
    def create_syslog(config: LoggingConfig) -> ArlogiSyslogHandler:
        """Create a syslog handler.

        Args:
            config: Logging configuration with syslog settings

        Returns:
            An ArlogiSyslogHandler instance

        Example:
            >>> config = LoggingConfig(
            ...     use_syslog=True,
            ...     syslog_address="/dev/log"
            ... )
            >>> handler = HandlerFactory.create_syslog(config)
        """
        return ArlogiSyslogHandler(address=config.syslog_address)

    @classmethod
    def create_handlers(
        cls, config: LoggingConfig
    ) -> list[logging.Handler]:
        """Create all handlers based on configuration.

        This is the main factory method that orchestrates the creation
        of all configured handlers.

        Args:
            config: Complete logging configuration

        Returns:
            List of configured handler instances

        Example:
            >>> config = LoggingConfig(
            ...     json_file_name="logs/app.jsonl",
            ...     use_syslog=True
            ... )
            >>> handlers = HandlerFactory.create_handlers(config)
            >>> for handler in handlers:
            ...     logger.addHandler(handler)
        """
        handlers: list[logging.Handler] = []

        # JSON file handler
        if config.json_file_name:
            handlers.append(cls.create_json_file(config))

        # Console handler (show unless json_file_only)
        if config.show_console:
            handlers.append(cls.create_console(config))
        elif config.json_file_only and not config.json_file_name:
            # JSON on console when json_file_only=True but no file specified
            handlers.append(cls.create_json_stream())

        # Syslog handler
        if config.use_syslog:
            handlers.append(cls.create_syslog(config))

        return handlers
