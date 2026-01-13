from .config import LoggingConfig, get_default_level, is_test_mode
from .factory import (
    LoggerFactory,
    cleanup_json_logger,
    cleanup_syslog_logger,
    get_json_logger,
    get_logger,
    get_syslog_logger,
    setup_logging,
)
from .handler_factory import HandlerFactory
from .levels import TRACE_LEVEL_NUM as TRACE
from .types import LoggerProtocol

__all__ = [
    # Public API
    "get_logger",
    "get_json_logger",
    "get_syslog_logger",
    "cleanup_json_logger",
    "cleanup_syslog_logger",
    "setup_logging",
    "TRACE",
    # Advanced / Internal API
    "LoggerFactory",
    "LoggerProtocol",
    "LoggingConfig",
    "HandlerFactory",
    "is_test_mode",
    "get_default_level",
]
