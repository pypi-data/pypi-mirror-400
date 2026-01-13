# Arlogi API Reference

Complete API reference for the arlogi logging library v0.601.04.

---

## Table of Contents

- [Modern Configuration](#modern-configuration)
- [Public API Functions](#public-api-functions)
- [Logger Protocol](#logger-protocol)
- [Handler Classes](#handler-classes)
- [Log Levels](#log-levels)
- [Advanced API](#advanced-api)

---

## Modern Configuration

### `LoggingConfig`

The primary way to configure `arlogi` is using the `LoggingConfig` dataclass applied via `LoggerFactory._apply_configuration()`.

```python
from arlogi import LoggingConfig, LoggerFactory

# 1. Define configuration
config = LoggingConfig(
    level="INFO",
    module_levels={"app.db": "DEBUG"},
    json_file_name="logs/app.jsonl"
)

# 2. Apply configuration
LoggerFactory._apply_configuration(config)
```

**Attributes:**

| Attribute        | Type                            | Default        | Description           |
| ---------------- | ------------------------------- | -------------- | --------------------- |
| `level`          | `int \| str`                    | `logging.INFO` | Global root log level |
| `module_levels`  | `Dict[str, str \| int] \| None` | `None`         | Per-module overrides  |
| `json_file_name` | `str \| None`                   | `None`         | JSON log file path    |
| `json_file_only` | `bool`                          | `False`        | Only JSON output      |
| `use_syslog`     | `bool`                          | `False`        | Enable syslog         |
| `syslog_address` | `str \| tuple`                  | `"/dev/log"`   | Syslog address        |
| `show_time`      | `bool`                          | `False`        | Show timestamps       |
| `show_level`     | `bool`                          | `True`         | Show levels           |
| `show_path`      | `bool`                          | `True`         | Show paths            |

**Methods:**

#### `LoggingConfig.from_kwargs(**kwargs)`

Create a config from keyword arguments. Useful for dynamic configuration from user inputs or environment filters.

#### `LoggingConfig.to_dict()`

Convert configuration to a dictionary for serialization.

#### `LoggingConfig.resolve_module_level(name, level)`

Resolve a module level string to an integer.

```python
level_int = config.resolve_module_level("app.db", "DEBUG")
```

**Properties:**

| Property          | Type   | Description                       |
| ----------------- | ------ | --------------------------------- |
| `resolved_level`  | `int`  | Global level as integer           |
| `show_console`    | `bool` | Whether console output is enabled |
| `has_json_output` | `bool` | Whether JSON output is configured |

---

## Public API Functions

### `get_logger(name, level=None)`

Get a logger instance with caller attribution support.

```python
from arlogi import get_logger

logger = get_logger("my_app.module")
logger.info("Application started", caller_depth=1)
```

**Parameters:**

| Parameter | Type                 | Default    | Description                        |
| --------- | -------------------- | ---------- | ---------------------------------- |
| `name`    | `str`                | _required_ | Logger name (typically `__name__`) |
| `level`   | `int \| str \| None` | `None`     | Optional level override            |

**Returns:** `LoggerProtocol` - A logger instance

---

### `get_json_logger(name, json_file_name=None)`

Get a logger that only outputs JSON, bypassing root handlers.

```python
from arlogi import get_json_logger

audit_logger = get_json_logger("audit", "logs/audit.jsonl")
audit_logger.info("User logged in", extra={"user_id": 123})
```

**Parameters:**

| Parameter        | Type          | Default  | Description        |
| ---------------- | ------------- | -------- | ------------------ |
| `name`           | `str`         | `"json"` | Logger name suffix |
| `json_file_name` | `str \| None` | `None`   | Optional file path |

**Returns:** `LoggerProtocol` - A JSON-only logger instance

---

### `get_syslog_logger(name, address="/dev/log")`

Get a logger that only outputs to Syslog.

```python
from arlogi import get_syslog_logger

syslog_logger = get_syslog_logger("security")
syslog_logger.warning("Unauthorized access attempt")
```

**Parameters:**

| Parameter | Type           | Default      | Description           |
| --------- | -------------- | ------------ | --------------------- |
| `name`    | `str`          | `"syslog"`   | Logger name suffix    |
| `address` | `str \| tuple` | `"/dev/log"` | Syslog server address |

**Returns:** `LoggerProtocol` - A syslog-only logger instance

---

### `cleanup_json_logger(name)`

Clean up handlers for a JSON logger to free resources.

```python
from arlogi import get_json_logger, cleanup_json_logger

logger = get_json_logger("temp", "logs/temp.json")
logger.info("Done logging")
cleanup_json_logger("temp")  # Close the file handle
```

**Parameters:**

| Parameter | Type     | Default   | Description                           |
| --------- | -------- | --------- | ------------------------------------- |
| `name`    | `str`    | `"json"`  | Logger name suffix (must match name used in get_json_logger) |

---

### `cleanup_syslog_logger(name)`

Clean up handlers for a syslog logger to free resources.

```python
from arlogi import get_syslog_logger, cleanup_syslog_logger

logger = get_syslog_logger("temp")
logger.info("Done logging")
cleanup_syslog_logger("temp")  # Close the socket
```

**Parameters:**

| Parameter | Type     | Default      | Description                           |
| --------- | -------- | ------------ | ------------------------------------- |
| `name`    | `str`    | `"syslog"`   | Logger name suffix                    |

---

## Logger Protocol

### `LoggerProtocol`

Protocol defining the interface for arlogi loggers.

**Methods:**

#### Standard Logging Methods

All methods support caller attribution via the `caller_depth` parameter.

```python
logger.trace(msg, *args, caller_depth=0, **kwargs)
logger.debug(msg, *args, caller_depth=0, **kwargs)
logger.info(msg, *args, caller_depth=0, **kwargs)
logger.warning(msg, *args, caller_depth=0, **kwargs)
logger.error(msg, *args, caller_depth=0, **kwargs)
logger.critical(msg, *args, caller_depth=0, **kwargs)
logger.exception(msg, *args, caller_depth=0, **kwargs)
logger.log(level, msg, *args, caller_depth=0, **kwargs)
```

**Caller Attribution Parameter:**

| Parameter     | Type          | Description                                  |
| ------------- | ------------- | -------------------------------------------- |
| `caller_depth` | `int \| None` | Stack depth (0=current, 1=caller, 2+=deeper) |

#### Level Management

```python
logger.setLevel(level)      # Set logger level
logger.isEnabledFor(level)  # Check if level is enabled
logger.getEffectiveLevel()  # Get effective level
```

#### Properties

| Property | Type  | Description |
| -------- | ----- | ----------- |
| `name`   | `str` | Logger name |

---

## Handler Classes

### `ColoredConsoleHandler`

Rich-based colored console handler with premium formatting.

```python
from arlogi.handlers import ColoredConsoleHandler

handler = ColoredConsoleHandler(
    show_time=True,
    show_level=True,
    show_path=True,
    level_styles={"info": "blue", "error": "red"}
)
```

**Parameters:**

| Parameter      | Type                     | Default         | Description            |
| -------------- | ------------------------ | --------------- | ---------------------- |
| `show_time`    | `bool`                   | `False`         | Show timestamps        |
| `show_level`   | `bool`                   | `True`          | Show log levels        |
| `show_path`    | `bool`                   | `True`          | Show file paths        |
| `level_styles` | `Dict[str, str] \| None` | `None`          | Custom level colors    |
| `project_root` | `str \| None`            | `auto-detected` | Project root for paths |

**Level Color Options:**

| Level    | Default Color | Alternative Colors            |
| -------- | ------------- | ----------------------------- |
| TRACE    | `grey37`      | `dim cyan`, `dim blue`        |
| DEBUG    | `grey37`      | `dim cyan`, `grey50`          |
| INFO     | `grey75`      | `white`, `green`              |
| WARNING  | `yellow`      | `orange`, `bold yellow`       |
| ERROR    | `red`         | `bold red`, `bright_red`      |
| CRITICAL | `bold red`    | `red on white`, `reverse red` |

---

### `JSONHandler`

Stream handler that outputs JSON to stderr.

```python
from arlogi.handlers import JSONHandler

handler = JSONHandler()
```

**JSON Output Format:**

```json
{
  "timestamp": "2025-12-28T10:30:00.123456",
  "level": "INFO",
  "logger_name": "my_app",
  "message": "User logged in",
  "module": "main",
  "function": "login",
  "line_number": 42,
  "user_id": 123,
  "ip": "192.168.1.1"
}
```

---

### `JSONFileHandler`

File handler that outputs JSON to a file.

```python
from arlogi.handlers import JSONFileHandler

handler = JSONFileHandler(
    filename="logs/app.jsonl",
    mode="a",
    encoding="utf-8"
)
```

**Parameters:**

| Parameter  | Type          | Default    | Description        |
| ---------- | ------------- | ---------- | ------------------ |
| `filename` | `str`         | _required_ | Path to log file   |
| `mode`     | `str`         | `"a"`      | File open mode     |
| `encoding` | `str \| None` | `None`     | File encoding      |
| `delay`    | `bool`        | `False`    | Delay file opening |

**Note:** Parent directories are created automatically.

---

### `ArlogiSyslogHandler`

Syslog handler with automatic fallback support.

```python
from arlogi.handlers import ArlogiSyslogHandler

handler = ArlogiSyslogHandler(
    address="/dev/log",  # or ("localhost", 514)
    facility="user",
    socktype=None
)
```

**Parameters:**

| Parameter  | Type           | Default      | Description           |
| ---------- | -------------- | ------------ | --------------------- |
| `address`  | `str \| tuple` | `"/dev/log"` | Syslog server address |
| `facility` | `int \| str`   | `LOG_USER`   | Syslog facility       |
| `socktype` | `int \| None`  | `None`       | Socket type           |

**Fallback Behavior:**

1. Tries the specified address
2. If `/dev/log` fails, tries UDP on `localhost:514`
3. If all fail, silently continues (won't crash the app)

---

## Log Levels

### Standard Python Levels

```python
import logging

logging.DEBUG    # 10
logging.INFO     # 20
logging.WARNING  # 30
logging.ERROR    # 40
logging.CRITICAL # 50
```

### Custom Arlogi Level

```python
from arlogi import TRACE

TRACE  # 5 - Below DEBUG for ultra-detailed logging
```

### Level Usage Guidelines

| Level    | Value | Use Case                            |
| -------- | ----- | ----------------------------------- |
| TRACE    | 5     | Function entry/exit, variable dumps |
| DEBUG    | 10    | Detailed troubleshooting info       |
| INFO     | 20    | General application flow            |
| WARNING  | 30    | Unexpected but recoverable issues   |
| ERROR    | 40    | Errors that don't stop execution    |
| CRITICAL | 50    | Serious failures, possible shutdown |

---

## Advanced API

### `LoggerFactory`

Factory for creating and configuring loggers.

```python
from arlogi import LoggerFactory

# Direct setup
LoggerFactory.setup(level="INFO")

# Get logger
logger = LoggerFactory.get_logger("my_app")

# Get dedicated loggers
json_logger = LoggerFactory.get_json_logger("audit")
syslog_logger = LoggerFactory.get_syslog_logger("security")
```

**Class Methods:**

| Method                               | Description                      |
| ------------------------------------ | -------------------------------- |
| `setup(**kwargs)`                    | Configure logging                |
| `_apply_configuration(config)`       | Apply LoggingConfig              |
| `get_logger(name, level)`            | Get a logger                     |
| `get_json_logger(name, file)`        | Get JSON-only logger             |
| `get_syslog_logger(name, addr)`      | Get syslog-only logger           |
| `cleanup_json_logger(name)`          | Clean up JSON logger handlers    |
| `cleanup_syslog_logger(name)`        | Clean up syslog logger handlers  |
| `is_test_mode()`                     | Check if in test environment     |
| `get_global_logger()`                | Get global application logger    |

**Internal Methods:**

| Method                             | Description           |
| ---------------------------------- | --------------------- |
| `_initialize_trace_level()`        | Register TRACE level  |
| `_configure_root_logger(config)`   | Set root logger level |
| `_clear_and_add_handlers(config)`  | Configure handlers    |
| `_configure_module_levels(config)` | Set module levels     |

---

### `HandlerFactory`

Factory for creating log handlers.

```python
from arlogi import HandlerFactory, LoggingConfig

config = LoggingConfig(show_time=True, show_level=True)

# Create individual handlers
console = HandlerFactory.create_console(config)
json_file = HandlerFactory.create_json_file(config)
syslog = HandlerFactory.create_syslog(config)

# Create all handlers at once
handlers = HandlerFactory.create_handlers(config)
```

**Static Methods:**

| Method                        | Returns                 | Description              |
| ----------------------------- | ----------------------- | ------------------------ |
| `create_console(config)`      | `ColoredConsoleHandler` | Console handler          |
| `create_json_stream()`        | `JSONHandler`           | Stream JSON handler      |
| `create_json_file(config)`    | `JSONFileHandler`       | File JSON handler        |
| `create_json_handler(config)` | `Handler`               | Appropriate JSON handler |
| `create_syslog(config)`       | `ArlogiSyslogHandler`   | Syslog handler           |
| `create_handlers(config)`     | `List[Handler]`         | All configured handlers  |

---

### Utility Functions

#### `is_test_mode()`

Detect if running under a test runner.

```python
from arlogi import is_test_mode

if is_test_mode():
    logger.debug("Test mode detected")
```

**Returns:** `bool` - True if pytest, unittest, or PYTEST_CURRENT_TEST is detected

---

#### `get_default_level()`

Get the default log level based on environment.

```python
from arlogi import get_default_level

level = get_default_level()  # DEBUG in tests, INFO otherwise
```

**Returns:** `int` - `logging.DEBUG` if in test mode, `logging.INFO` otherwise

---

## Type Hints

### LoggerProtocol

```python
from typing import Protocol, Any

@runtime_checkable
class LoggerProtocol(Protocol):
    def trace(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def debug(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def info(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def warning(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def error(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def critical(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def fatal(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def exception(self, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def log(self, level: int, msg: Any, *args: Any, caller_depth: int | None = None, **kwargs: Any) -> None: ...
    def setLevel(self, level: int | str) -> None: ...
    def isEnabledFor(self, level: int) -> bool: ...
    def getEffectiveLevel(self) -> int: ...
    @property
    def name(self) -> str: ...
```

---

## Examples

### Modern Basic Usage

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

config = LoggingConfig(level="INFO")
LoggerFactory._apply_configuration(config)

logger = get_logger("my_app")
logger.info("Application started")
```

### Caller Attribution

```python
def outer_function():
    logger.info("Processing data", caller_depth=1)

def inner_function():
    logger.debug("Step 1", caller_depth=0)  # Shows inner_function
    logger.debug("Step 2", caller_depth=1)  # Shows outer_function
```

### Advanced Module Configuration

```python
from arlogi import LoggingConfig, LoggerFactory

config = LoggingConfig(
    level="INFO",
    module_levels={
        "app.database": "DEBUG",
        "app.network": "TRACE",
        "app.security": "WARNING"
    }
)
LoggerFactory._apply_configuration(config)
```

### JSON Logging

```python
from arlogi import LoggingConfig, LoggerFactory, get_json_logger

# With console + JSON file
config = LoggingConfig(json_file_name="logs/app.jsonl")
LoggerFactory._apply_configuration(config)

# JSON only to console
config = LoggingConfig(json_file_only=True)
LoggerFactory._apply_configuration(config)

# Dedicated JSON logger
audit = get_json_logger("audit", "logs/audit.jsonl")
audit.info("User action", extra={"user_id": 123})
```

### Syslog

```python
from arlogi import LoggingConfig, LoggerFactory, get_syslog_logger

# Add syslog to root logger
config = LoggingConfig(use_syslog=True)
LoggerFactory._apply_configuration(config)

# Dedicated syslog logger
syslog = get_syslog_logger("security")
syslog.warning("Security event")
```

---

## Error Handling

All arlogi functions handle errors gracefully:

- Invalid log levels raise `ValueError` with helpful messages
- Syslog connection failures fall back automatically
- JSON file handler creates parent directories automatically
- Test mode detection prevents double logging in pytest

---

## Version History

| Version  | Changes                                                           |
| -------- | ----------------------------------------------------------------- |
| 0.601.04 | Enhanced resource cleanup, improved test mode detection          |
| 0.601.00 | Added cleanup_json_logger, cleanup_syslog_logger                 |
| 0.512.28 | Added LoggingConfig, HandlerFactory, reduced complexity           |
| 0.512.20 | Initial caller attribution support                               |
| 0.512.0  | First stable release                                              |

---

## License

MIT License - see LICENSE file for details.
