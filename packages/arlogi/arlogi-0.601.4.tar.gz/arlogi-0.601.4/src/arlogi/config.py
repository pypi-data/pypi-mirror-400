"""Logging configuration dataclass for type-safe setup.

This module provides a structured, validated configuration for logging setup,
following the Builder pattern for flexible construction.
"""

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoggingConfig:
    """Immutable configuration for arlogi logging setup.

    Attributes:
        level: Global root log level (int or string like "INFO")
        module_levels: Per-module level overrides (e.g., {"app.db": "DEBUG"})
        json_file_name: Path to JSON log file (None for no JSON file logging)
        json_file_only: If True, only output to JSON (no console)
        use_syslog: Enable syslog output
        syslog_address: Syslog server address (default: "/dev/log")
        show_time: Show timestamps in console output
        show_level: Show log levels in console output
        show_path: Show file paths in console output
    """

    level: int | str = logging.INFO
    module_levels: dict[str, str | int] | None = None
    json_file_name: str | None = None
    json_file_only: bool = False
    use_syslog: bool = False
    syslog_address: str | tuple[str, int] = "/dev/log"
    show_time: bool = False
    show_level: bool = True
    show_path: bool = True

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate level
        self._validate_level(self.level)

        # Validate module levels if provided
        if self.module_levels:
            for name, m_level in self.module_levels.items():
                if not isinstance(name, str) or not name:
                    raise ValueError(f"Invalid module name: {name!r}")
                self._validate_level(m_level)

    @staticmethod
    def _validate_level(level: int | str) -> None:
        """Validate a log level value.

        Args:
            level: Log level as int or str

        Raises:
            ValueError: If level is invalid
        """
        if isinstance(level, str):
            # Check for custom TRACE level (valid but not in logging module)
            if level.upper() == "TRACE":
                return

            try:
                getattr(logging, level.upper())
            except AttributeError as e:
                valid = ", ".join(
                    name for name in dir(logging)
                    if name.isupper() and name not in ("NOTSET",)
                )
                raise ValueError(
                    f"Invalid log level: {level!r}. "
                    f"Valid levels: TRACE, {valid}"
                ) from e
        elif not isinstance(level, int):
            raise ValueError(
                f"Log level must be int or str, got {type(level).__name__}"
            )

    @property
    def resolved_level(self) -> int:
        """Get the global level as an integer.

        Returns:
            The resolved log level as an integer
        """
        if isinstance(self.level, str):
            return getattr(logging, self.level.upper())
        return self.level

    @property
    def show_console(self) -> bool:
        """Determine if console output should be shown.

        Returns:
            True if console output should be displayed
        """
        return not self.json_file_only

    @property
    def has_json_output(self) -> bool:
        """Determine if JSON output is configured.

        Returns:
            True if JSON file or JSON-only output is enabled
        """
        return self.json_file_name is not None or self.json_file_only

    def resolve_module_level(self, name: str, level: str | int) -> int:
        """Resolve a module level to an integer.

        Args:
            name: Module name (for error messages)
            level: Level as string or int

        Returns:
            The level as an integer
        """
        if isinstance(level, str):
            upper_level = level.upper()
            # Handle custom TRACE level
            if upper_level == "TRACE":
                from .levels import TRACE_LEVEL_NUM
                return TRACE_LEVEL_NUM
            return getattr(logging, upper_level)
        # level is already an int
        return level

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "level": self.level,
            "module_levels": self.module_levels,
            "json_file_name": self.json_file_name,
            "json_file_only": self.json_file_only,
            "use_syslog": self.use_syslog,
            "syslog_address": self.syslog_address,
            "show_time": self.show_time,
            "show_level": self.show_level,
            "show_path": self.show_path,
        }

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "LoggingConfig":
        """Create LoggingConfig from keyword arguments.

        This factory method provides backward compatibility with the
        legacy setup_logging() function signature.

        Args:
            **kwargs: Configuration keyword arguments

        Returns:
            A new LoggingConfig instance

        Raises:
            TypeError: If unknown keyword arguments are provided

        Example:
            >>> config = LoggingConfig.from_kwargs(
            ...     level="INFO",
            ...     module_levels={"app.db": "DEBUG"},
            ...     json_file_name="logs/app.jsonl"
            ... )
        """
        valid_keys = {
            "level", "module_levels", "json_file_name", "json_file_only",
            "use_syslog", "syslog_address", "show_time", "show_level", "show_path"
        }

        # Check for unknown keys to catch typos early
        unknown = set(kwargs.keys()) - valid_keys
        if unknown:
            raise TypeError(
                f"LoggingConfig() got unknown keyword argument(s): {', '.join(sorted(unknown))}. "
                f"Valid arguments: {', '.join(sorted(valid_keys))}"
            )

        return cls(**kwargs)


def is_test_mode() -> bool:
    """Detect if running under a test runner.

    Checks for pytest, unittest, or the PYTEST_CURRENT_TEST environment
    variable to determine if the code is running in a test context.

    Returns:
        True if running in a test environment
    """
    return (
        "pytest" in sys.modules
        or "unittest" in sys.modules
        or os.environ.get("PYTEST_CURRENT_TEST") is not None
    )


def get_default_level() -> int:
    """Get the default log level based on the current environment.

    Returns DEBUG in test mode for better test visibility,
    otherwise returns INFO.

    Returns:
        logging.DEBUG if in test mode, logging.INFO otherwise
    """
    return logging.DEBUG if is_test_mode() else logging.INFO
