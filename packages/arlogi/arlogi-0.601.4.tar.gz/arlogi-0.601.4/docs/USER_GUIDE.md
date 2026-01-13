# Arlogi User Guide

Complete user guide for the arlogi logging library. Learn how to install, configure, and use arlogi effectively.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Caller Attribution](#caller-attribution)
- [Output Handlers](#output-handlers)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements

- Python 3.13 or higher (required)
- `rich` >= 14.2.0 (automatically installed)

Arlogi requires Python 3.13+ as specified in the project configuration.

### Using pip

```bash
pip install arlogi
```

### Using uv

```bash
uv add arlogi
```

### From Source

```bash
git clone https://github.com/your-org/arlogi.git
cd arlogi
pip install -e .
```

---

## Quick Start

### Minimal Setup

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

# 1. Configure logging using the modern architecture
config = LoggingConfig(level="INFO")
LoggerFactory._apply_configuration(config)

# 2. Get a logger
logger = get_logger(__name__)

# 3. Log a message
logger.info("Hello, Arlogi!")
```

**Output:**

```text
I  Hello, Arlogi!    your_module.py:7
```

---

## Basic Usage

### Log Levels

```python
from arlogi import get_logger, TRACE

logger = get_logger(__name__)

# Ultra-detailed debugging
logger.trace("Variable value: x = %s", x, caller_depth=0)

# Detailed information for troubleshooting
logger.debug("SQL query: %s", query, caller_depth=1)

# General information about application flow
logger.info("User logged in successfully", user_id=123)

# Something unexpected, but application continues
logger.warning("Configuration file not found, using defaults")

# Error occurred, application can continue
logger.error("Failed to connect to database", database="users")

# Serious error, application may not continue
logger.critical("Out of memory, shutting down")
```

### Logging Exceptions

```python
from arlogi import get_logger

logger = get_logger(__name__)

def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except Exception as e:
        # Logs exception with full traceback
        logger.exception("Failed to process data", data_id=data.get("id"))
        raise
```

### Structured Logging

```python
from arlogi import get_logger

logger = get_logger(__name__)

# Add extra fields for structured logging
logger.info(
    "API request processed",
    request_id="req-abc-123",
    method="GET",
    path="/api/users",
    status_code=200,
    duration_ms=45
)
```

---

## Configuration

### Basic Configuration

Configure `arlogi` using the `LoggingConfig` pattern. This approach clearly separates configuration data from initialization logic and provides a type-safe interface.

```python
from arlogi import LoggingConfig, LoggerFactory

# 1. Create the configuration object
config = LoggingConfig(
    level="INFO",
    module_levels={"app.db": "DEBUG"},
    json_file_name="logs/app.jsonl",
    show_time=True
)

# 2. Apply it globally
LoggerFactory._apply_configuration(config)
```

> [!TIP]
> This pattern is highly recommended for production applications, especially when configuration is sourced from complex environment logic or external files.

---

### Per-Module Levels

```python
from arlogi import LoggingConfig, LoggerFactory

config = LoggingConfig(
    level="INFO",
    module_levels={
        "app.database": "DEBUG",      # Verbose database logging
        "app.network": "TRACE",       # Ultra-detailed network logs
        "app.security": "WARNING",    # Only security warnings and above
        "app.performance": "ERROR"    # Only performance errors
    }
)
LoggerFactory._apply_configuration(config)
```

### JSON File Logging

```python
from arlogi import LoggingConfig, LoggerFactory

# Console + JSON file
config = LoggingConfig(
    level="INFO",
    json_file_name="logs/app.jsonl"
)
LoggerFactory._apply_configuration(config)
```

**JSON Output Format:**

```json
{
  "timestamp": "2025-12-28T10:30:00.123456",
  "level": "INFO",
  "logger_name": "app.main",
  "message": "User logged in",
  "module": "main",
  "function": "login",
  "line_number": 42
}
```

### JSON-Only Output

```python
from arlogi import LoggingConfig, LoggerFactory

# JSON output only (no console)
config = LoggingConfig(
    level="INFO",
    json_file_only=True
)
LoggerFactory._apply_configuration(config)
```

### Syslog Integration

```python
from arlogi import LoggingConfig, LoggerFactory

# Add syslog to root logger
config = LoggingConfig(
    level="INFO",
    use_syslog=True,
    syslog_address="/dev/log"  # or ("localhost", 514)
)
LoggerFactory._apply_configuration(config)
```

### Complete Configuration

```python
from arlogi import LoggingConfig, LoggerFactory

config = LoggingConfig(
    level="INFO",
    module_levels={
        "app.db": "DEBUG",
        "app.api": "TRACE"
    },
    json_file_name="logs/app.jsonl",
    use_syslog=True,
    show_time=True,
    show_level=True,
    show_path=True
)
LoggerFactory._apply_configuration(config)
```

---

## Caller Attribution

### Understanding Depth Values

The `from_` parameter controls which function is shown in the log:

```python
from arlogi import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Main entry point", caller_depth=0)  # Shows: main()
    process_data()

def process_data():
    logger.info("Processing", caller_depth=0)        # Shows: process_data()
    logger.info("Called from main", caller_depth=1)  # Shows: main()
    validate()

def validate():
    logger.info("Validating", caller_depth=0)        # Shows: validate()
    logger.info("From process", caller_depth=1)      # Shows: process_data()
    logger.info("From main", caller_depth=2)         # Shows: main()
```

### Cross-Module Attribution

```python
# file: app/utils.py
from arlogi import get_logger

logger = get_logger(__name__)

def fetch_user(user_id):
    logger.info("Fetching user", caller_depth=1)  # Shows caller
    # ... fetch logic
    return user

# file: app/main.py
from arlogi import get_logger
from app.utils import fetch_user

logger = get_logger(__name__)

def handle_request(user_id):
    logger.info("Request received", caller_depth=0)
    user = fetch_user(user_id)  # utils.py shows: handle_request()
    logger.info("Request complete", caller_depth=0)
```

### Best Practices

| Use Case                | Recommended `caller_depth`        |
| ----------------------- | --------------------------------- |
| Library/Utility code    | `caller_depth=1` (show caller)           |
| Application code        | `caller_depth=0` (show current function) |
| Debugging complex flows | `caller_depth=2+` (show deeper context)  |

---

## Output Handlers

### Console Handler

```python
from arlogi import get_logger
from arlogi.handlers import ColoredConsoleHandler

logger = get_logger(__name__)

# Custom colors
handler = ColoredConsoleHandler(
    show_time=True,
    show_level=True,
    show_path=True,
    level_styles={
        "info": "blue",
        "warning": "yellow",
        "error": "bold red"
    }
)
```

**Available Color Options:**

- `grey37`, `grey50`, `grey75`
- `blue`, `cyan`, `green`, `yellow`, `red`
- `bold blue`, `bold red`, etc.

### JSON Logger

```python
from arlogi import get_json_logger

# JSON to file
audit_logger = get_json_logger("audit", "logs/audit.jsonl")
audit_logger.info("User action", extra={"user_id": 123})

# JSON to stderr
json_logger = get_json_logger()
json_logger.info("Structured log", extra={"key": "value"})
```

### Syslog Logger

```python
from arlogi import get_syslog_logger

# Dedicated syslog logger
security_logger = get_syslog_logger("security")
security_logger.warning("Brute force attempt", extra={"ip": "192.168.1.1"})
```

---

## Common Patterns

### Application Startup

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

def main():
    # 1. Configure logging first using modern architecture
    config = LoggingConfig(
        level="INFO",
        module_levels={
            "app.database": "DEBUG",
            "app.network": "TRACE"
        },
        json_file_name="logs/app.jsonl"
    )
    LoggerFactory._apply_configuration(config)

    logger = get_logger("app.main")
    logger.info("Application starting up")

    # Initialize components
    # init_database()
    # init_api_server()

    logger.info("Application ready")

if __name__ == "__main__":
    main()
```

### Request/Response Logging

```python
from arlogi import get_logger
import time

logger = get_logger("app.api")

def handle_request(request):
    request_id = generate_id()
    start_time = time.time()

    logger.info(
        "Request received",
        caller_depth=1,
        request_id=request_id,
        method=request.method,
        path=request.path
    )

    try:
        result = process_request(request)
        duration = (time.time() - start_time) * 1000

        logger.info(
            "Request completed",
            caller_depth=1,
            request_id=request_id,
            status_code=200,
            duration_ms=round(duration, 2)
        )
        return result

    except Exception as e:
        duration = (time.time() - start_time) * 1000

        logger.exception(
            "Request failed",
            caller_depth=1,
            request_id=request_id,
            error=str(e),
            duration_ms=round(duration, 2)
        )
        raise
```

### Database Operation Logging

```python
from arlogi import get_logger
import time

logger = get_logger("app.database")

def execute_query(query, params=None):
    start_time = time.time()

    logger.trace(
        "Executing query",
        caller_depth=1,
        query=query,
        params=params
    )

    try:
        result = db.execute(query, params)
        duration = (time.time() - start_time) * 1000

        logger.debug(
            "Query executed successfully",
            caller_depth=1,
            query=truncate(query, 100),
            duration_ms=round(duration, 2),
            rows_affected=result.rowcount
        )

        return result

    except Exception as e:
        duration = (time.time() - start_time) * 1000

        logger.error(
            "Query execution failed",
            caller_depth=1,
            query=query,
            duration_ms=round(duration, 2),
            error=str(e)
        )
        raise
```

### Background Task Logging

```python
from arlogi import get_logger
import asyncio

logger = get_logger("app.tasks")

async def process_task(task_id, data):
    logger.info(
        "Task started",
        caller_depth=1,
        task_id=task_id,
        data_size=len(data)
    )

    try:
        # Process the task
        result = await async_process(data)

        logger.info(
            "Task completed",
            caller_depth=1,
            task_id=task_id,
            result_size=len(result)
        )
        return result

    except Exception as e:
        logger.exception(
            "Task failed",
            caller_depth=1,
            task_id=task_id,
            error=str(e)
        )
        raise
```

---

## Troubleshooting

### Issue: Logs Not Appearing

**Symptoms:** No log output in console

**Solutions:**

1. Check configuration is applied correctly

```python
from arlogi import LoggingConfig, LoggerFactory
config = LoggingConfig(level="DEBUG")  # Show all logs
LoggerFactory._apply_configuration(config)
```

2. Verify logger name matches module levels

```python
# If module_levels={"app.db": "DEBUG"}
logger = get_logger("app.db")  # Must match exactly
```

3. Check test mode detection

```python
from arlogi import is_test_mode
print(f"Test mode: {is_test_mode()}")
```

### Issue: Duplicate Logs

**Symptoms:** Same message appears multiple times

**Solutions:**

1. Check for multiple configuration calls

```python
# Only apply configuration once at startup
config = LoggingConfig(level="INFO")
LoggerFactory._apply_configuration(config)
```

2. Check logger propagation

```python
logger = get_logger("my_module")
logger.propagate = False  # Disable if needed
```

### Issue: Caller Attribution Shows Wrong Function

**Symptoms:** Attribution shows incorrect function name

**Solutions:**

1. Adjust the `from_` depth

```python
logger.info("Message", caller_depth=0)  # Current function
logger.info("Message", caller_depth=1)  # Caller
logger.info("Message", caller_depth=2)  # Caller's caller
```

2. Check for wrapper functions

```python
# If using decorators
@log_decorator
def my_function():
    pass

# Use caller_depth=2 to skip the decorator
```

### Issue: Rich Colors Not Working

**Symptoms:** Console output has no colors

**Solutions:**

1. Install rich dependency

```bash
pip install rich
```

2. Check terminal supports colors

```python
from rich.console import Console
console = Console()
console.print("[bold red]Test colors[/bold red]")
```

### Issue: JSON File Not Created

**Symptoms:** JSON log file doesn't exist

**Solutions:**

1. Check directory permissions

```bash
mkdir -p logs
chmod 755 logs
```

2. Use absolute path

```python
config = LoggingConfig(json_file_name="/var/log/myapp/app.jsonl")
LoggerFactory._apply_configuration(config)
```

### Issue: Syslog Not Working

**Symptoms:** Syslog messages not appearing

**Solutions:**

1. Verify syslog address

```python
# For Unix socket
config = LoggingConfig(syslog_address="/dev/log", use_syslog=True)
LoggerFactory._apply_configuration(config)

# For network syslog
config = LoggingConfig(syslog_address=("localhost", 514), use_syslog=True)
LoggerFactory._apply_configuration(config)
```

2. Check syslog is running

```bash
# Linux
systemctl status rsyslog

# macOS
log show --predicate 'eventMessage contains "test"'
```

---

## Advanced Usage

### Conditional Logging

```python
from arlogi import get_logger

logger = get_logger(__name__)

# Only log if enabled (avoid string formatting overhead)
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Expensive debug info: %s", expensive_operation())
```

### Context Managers

```python
from contextlib import contextmanager
from arlogi import get_logger

logger = get_logger(__name__)

@contextmanager
def log_context(operation_name):
    logger.info("Starting: %s", operation_name, caller_depth=1)
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(
            "Completed: %s",
            operation_name,
            caller_depth=1,
            duration_ms=round(duration * 1000, 2)
        )

# Usage
with log_context("database_migration"):
    run_migration()
```

### Lazy Log Evaluation

```python
from arlogi import get_logger

logger = get_logger(__name__)

# Use lambda for expensive operations
logger.debug(lambda: expensive_debug_info())
```

---

## Best Practices

### DO

- Use descriptive log messages
- Include context (request IDs, user IDs, etc.)
- Use appropriate log levels
- Log exceptions with `logger.exception()`
- Use `caller_depth=1` in library/utility code

### DON'T

- Log sensitive data (passwords, tokens, PII)
- Use `print()` statements
- Log at inappropriate levels (ERROR for expected conditions)
- Create too many loggers (use module hierarchy)
- Include large objects in log messages

---

## Performance Tips

1. **Use lazy evaluation for expensive operations**

   ```python
   logger.debug(lambda: expensive_debug_info())
   ```

2. **Check log level before complex operations**

   ```python
   if logger.isEnabledFor(logging.DEBUG):
       logger.debug("Complex info: %s", complex_operation())
   ```

3. **Use structured logging for parsing**

   ```python
   logger.info("Event", extra={"structured": "data"})
   ```

4. **Avoid excessive string formatting**

   ```python
   # Good
   logger.info("User %s logged in", user.name)

   # Avoid
   logger.info(f"User {user.name} logged in")  # Formatting happens even if log is disabled
   ```

---

## Getting Help

- **Documentation**: [Documentation Index](index.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/arlogi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/arlogi/discussions)

---

## License

MIT License - see LICENSE file for details.
