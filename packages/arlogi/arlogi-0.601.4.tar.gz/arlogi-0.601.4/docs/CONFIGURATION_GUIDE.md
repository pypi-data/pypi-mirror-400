# Configuration Guide

Complete guide to configuring arlogi logging for your applications, including global setup, per-module configuration, and advanced handler configuration.

## Quick Configuration

### Basic Setup

Configure `arlogi` using the `LoggingConfig` pattern. This approach clearly separates configuration data from initialization logic and provides a type-safe interface.

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

# 1. Configuration as a dataclass
config = LoggingConfig(
    level="INFO",
    module_levels={"app.db": "DEBUG"},
    json_file_name="logs/app.jsonl"
)

# 2. Apply via factory
LoggerFactory._apply_configuration(config)

# 3. Use loggers
logger = get_logger("my_app")
logger.info("Application started using LoggingConfig")
```

### Complete Production Setup

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

config = LoggingConfig(
    level="INFO",
    module_levels={
        "app.network": "TRACE",
        "app.database": "DEBUG",
        "app.security": "WARNING"
    },
    json_file_name="logs/app.jsonl",
    json_file_only=False,
    use_syslog=True,
    show_time=False,
    show_level=True,
    show_path=True
)
LoggerFactory._apply_configuration(config)

logger = get_logger("app.main")
logger.info("Production logging configured")
```

## Configuration Reference

### `LoggingConfig` Attributes

| Parameter        | Type             | Default | Description                           |
| ---------------- | ---------------- | ------- | ------------------------------------- | -------------------------------- |
| `level`          | `int             | str`    | `"INFO"`                              | Global log level for all modules |
| `module_levels`  | `Dict[str, str]` | `{}`    | Per-module log level overrides        |
| `json_file_name` | `str             | None`   | `None`                                | JSON log file path               |
| `json_file_only` | `bool`           | `False` | Output only to JSON file (no console) |
| `use_syslog`     | `bool`           | `False` | Enable syslog output                  |
| `syslog_address` | `str             | tuple`  | `"/dev/log"`                          | Syslog server address            |
| `show_time`      | `bool`           | `False` | Show timestamps in console output     |
| `show_level`     | `bool`           | `True`  | Show log levels in console output     |
| `show_path`      | `bool`           | `True`  | Show file paths in console output     |

### Log Levels

```python
import logging
from arlogi import TRACE

# Available levels (from lowest to highest)
TRACE     # 5  - Custom ultra-detailed debugging
logging.DEBUG    # 10 - Standard debugging
logging.INFO     # 20 - General information
logging.WARNING  # 30 - Warnings
logging.ERROR    # 40 - Errors
logging.CRITICAL # 50 - Critical failures

# Can use string names in LoggingConfig
config = LoggingConfig(level="INFO")     # Same as logging.INFO
config = LoggingConfig(level="DEBUG")    # Same as logging.DEBUG
config = LoggingConfig(level=TRACE)      # Custom level
```

## Per-Module Configuration

### Module-Level Overrides

### Module-Level Overrides

```python
from arlogi import LoggingConfig, LoggerFactory

config = LoggingConfig(
    level="INFO",  # Global level
    module_levels={
        # Ultra-detailed logging for network operations
        "app.network": "TRACE",

        # Detailed logging for database operations
        "app.database": "DEBUG",

        # Quiet security logging (warnings only)
        "app.security": "WARNING"
    }
)
LoggerFactory._apply_configuration(config)
```

### Module Hierarchy Matching

```python
from arlogi import LoggingConfig, LoggerFactory

config = LoggingConfig(
    level="INFO",
    module_levels={
        # Affects: app.network.http, app.network.tcp, app.network.udp
        "app.network": "TRACE",

        # Affects: app.database.mysql, app.database.postgresql
        "app.database": "DEBUG",

        # Affects: app.cache.redis, app.cache.memory
        "app.cache": "INFO",

        # Specific module override
        "app.network.http.client": "DEBUG"
    }
)
LoggerFactory._apply_configuration(config)

# Examples:
# get_logger("app.network.http") -> TRACE level
# get_logger("app.network.tcp") -> TRACE level
# get_logger("app.database.mysql") -> DEBUG level
# get_logger("app.network.http.client") -> DEBUG level (specific override)
# get_logger("app.other") -> INFO level (global)
```

## Handler Configuration

### Console Handler Configuration

### Console Handler Configuration

```python
from arlogi import LoggingConfig, LoggerFactory

# Basic console configuration
config = LoggingConfig(
    level="INFO",
    show_time=True,
    show_level=True,
    show_path=True
)
LoggerFactory._apply_configuration(config)

# Disable console output (JSON file only)
config = LoggingConfig(
    level="INFO",
    json_file_name="logs/app.jsonl",
    json_file_only=True
)
LoggerFactory._apply_configuration(config)
```

### JSON File Configuration

```python
from arlogi import LoggingConfig, LoggerFactory

# Basic JSON file logging
config = LoggingConfig(json_file_name="logs/app.jsonl")
LoggerFactory._apply_configuration(config)

# JSON-only logging
config = LoggingConfig(
    level="INFO",
    json_file_name="logs/app.jsonl",
    json_file_only=True
)
LoggerFactory._apply_configuration(config)
```

#### JSON File Structure

```json
{
  "timestamp": "2025-12-20T22:45:30.123456Z",
  "level": "INFO",
  "name": "app.main",
  "message": "User logged in successfully",
  "module": "main",
  "function": "handle_login",
  "line": 42,
  "caller": "auth.authenticate",
  "user_id": 12345,
  "session_id": "sess_abc123"
}
```

#### Custom JSON Handlers

```python
from arlogi import get_logger, get_json_logger
from arlogi.handlers import JSONFileHandler

# Default JSON logger
json_logger = get_json_logger("audit", "logs/audit.jsonl")

# Custom JSON handler with specific configuration
handler = JSONFileHandler(
    filename="logs/custom.jsonl",
    mode="a",           # Append mode
    encoding="utf-8",   # File encoding
    delay=False         # Delay file creation
)

import logging
custom_logger = get_logger("custom")
custom_logger.addHandler(handler)
custom_logger.setLevel(logging.INFO)

custom_logger.info("Custom JSON logging", custom_field="value")
```

### Syslog Configuration (Modern)

```python
from arlogi import LoggingConfig, LoggerFactory

# Local syslog
config = LoggingConfig(
    level="INFO",
    use_syslog=True,
    syslog_address="/dev/log"  # Default
)
LoggerFactory._apply_configuration(config)

# Remote syslog server
config = LoggingConfig(
    level="INFO",
    use_syslog=True,
    syslog_address=("syslog.example.com", 514)
)
LoggerFactory._apply_configuration(config)

# Syslog-only logger
from arlogi import get_syslog_logger
syslog_logger = get_syslog_logger("security")
syslog_logger.error("Security event detected")
```

#### Syslog Handler Details

```python
from arlogi.handlers import ArlogiSyslogHandler

# Local Unix domain socket
handler = ArlogiSyslogHandler(address="/dev/log")

# Remote UDP syslog
handler = ArlogiSyslogHandler(
    address=("logs.example.com", 514),
    facility="user",
    socktype="UDP"
)

# Remote TCP syslog
handler = ArlogiSyslogHandler(
    address=("logs.example.com", 514),
    facility="daemon",
    socktype="TCP"
)

# Custom facility
import syslog
handler = ArlogiSyslogHandler(
    address="/dev/log",
    facility=syslog.LOG_LOCAL0
)
```

## Application Structure Examples

### Microservice Configuration

```python
# config/logging.py
from arlogi import LoggingConfig, LoggerFactory

def setup_service_logging(service_name, environment="production"):
    """Configure logging for microservice"""

    if environment == "development":
        # Development: verbose console logging
        config = LoggingConfig(
            level="DEBUG",
            show_time=True,
            show_level=True,
            show_path=True
        )
    elif environment == "testing":
        # Testing: JSON-only for automated analysis
        config = LoggingConfig(
            level="INFO",
            json_file_name=f"logs/{service_name}.jsonl",
            json_file_only=True
        )
    else:
        # Production: console + JSON + syslog
        config = LoggingConfig(
            level="INFO",
            module_levels={
                f"{service_name}.network": "DEBUG",
                f"{service_name}.database": "DEBUG"
            },
            json_file_name=f"logs/{service_name}.jsonl",
            use_syslog=True,
            show_time=False,
            show_level=True,
            show_path=True
        )

    LoggerFactory._apply_configuration(config)

# main.py
from config.logging import setup_service_logging
from arlogi import get_logger

setup_service_logging("user-service", environment="production")

logger = get_logger("user-service.main")
logger.info("User service started")
```

### Web Application Configuration

```python
# app/config.py
from arlogi import LoggingConfig, LoggerFactory

class LoggingSetup:
    @staticmethod
    def configure(app_name, environment="development"):
        """Configure logging for web application"""

        module_levels = {
            f"{app_name}.network": "DEBUG",
            f"{app_name}.database": "DEBUG",
            f"{app_name}.auth": "INFO",
            f"{app_name}.api": "INFO"
        }

        if environment == "development":
            config = LoggingConfig(
                level="DEBUG",
                show_time=True,
                show_path=True,
                module_levels=module_levels
            )

        elif environment == "staging":
            config = LoggingConfig(
                level="INFO",
                json_file_name=f"logs/{app_name}-staging.jsonl",
                use_syslog=True,
                syslog_address=("staging-logs.company.com", 514),
                module_levels=module_levels
            )

        elif environment == "production":
            config = LoggingConfig(
                level="WARNING",  # Less verbose in production
                module_levels={
                    f"{app_name}.auth": "ERROR",      # Only auth errors
                    f"{app_name}.api": "WARNING",     # API warnings
                    f"{app_name}.business": "INFO",   # Business events
                    **module_levels
                },
                json_file_name=f"logs/{app_name}.jsonl",
                use_syslog=True,
                syslog_address=("logs.company.com", 514)
            )

        LoggerFactory._apply_configuration(config)

# app.py
from app.config import LoggingSetup
from arlogi import get_logger

LoggingSetup.configure("myapp", environment="production")

app_logger = get_logger("myapp.app")
app_logger.info("Web application started")
```

### CLI Application Configuration

```python
# cli/config.py
import os
from arlogi import LoggingConfig, LoggerFactory

def setup_cli_logging(verbosity=0, log_file=None):
    """Configure logging for CLI application"""

    if verbosity >= 2:
        # Very verbose: DEBUG level with console details
        config = LoggingConfig(
            level="DEBUG",
            show_time=True,
            show_level=True,
            show_path=True,
            json_file_name=log_file
        )
    elif verbosity >= 1:
        # Verbose: INFO level with basic console
        config = LoggingConfig(
            level="INFO",
            show_time=False,
            show_level=True,
            show_path=False,
            json_file_name=log_file
        )
    else:
        # Quiet: ERROR level only
        config = LoggingConfig(
            level="ERROR",
            json_file_name=log_file,
            json_file_only=not log_file
        )

    LoggerFactory._apply_configuration(config)

# cli/main.py
import argparse
from cli.config import setup_cli_logging
from arlogi import get_logger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("--log-file", help="Log to file")
    args = parser.parse_args()

    setup_cli_logging(args.verbose, args.log_file)

    logger = get_logger("cli.main")
    logger.info("CLI application started", verbose=args.verbose)

if __name__ == "__main__":
    main()
```

## Environment-Specific Configuration

### Development Environment

```python
from arlogi import LoggingConfig, LoggerFactory

def configure_development():
    """Development: maximum verbosity for debugging"""
    config = LoggingConfig(
        level="DEBUG",
        module_levels={"app.*": "TRACE"},
        show_time=True
    )
    LoggerFactory._apply_configuration(config)
```

### Testing Environment

```python
from arlogi import LoggingConfig, LoggerFactory

def configure_testing():
    """Testing: structured logs for automated analysis"""
    config = LoggingConfig(
        level="INFO",
        json_file_name="logs/tests.jsonl",
        json_file_only=True
    )
    LoggerFactory._apply_configuration(config)
```

### Staging Environment

```python
from arlogi import LoggingConfig, LoggerFactory

def configure_staging():
    """Staging: production-like with extra debugging"""
    config = LoggingConfig(
        level="INFO",
        module_levels={
            "app.auth": "DEBUG",      # Debug authentication
            "app.payments": "DEBUG",  # Debug payments
            "app.api": "INFO"
        },
        json_file_name="logs/staging.jsonl",
        use_syslog=True,
        syslog_address=("staging-logs.company.com", 514),
        show_time=False,
        show_level=True,
        show_path=False
    )
    LoggerFactory._apply_configuration(config)
```

### Production Environment

```python
from arlogi import LoggingConfig, LoggerFactory

def configure_production():
    """Production: essential logging only"""
    config = LoggingConfig(
        level="WARNING",
        module_levels={
            "app.auth": "ERROR",
            "app.business": "INFO",
        },
        json_file_name="logs/production.jsonl",
        use_syslog=True
    )
    LoggerFactory._apply_configuration(config)
```

## Dynamic Configuration

### Runtime Level Adjustment

```python
from arlogi import get_logger

# Get logger and adjust level at runtime
logger = get_logger("app.module")

# Check current level
print(f"Current level: {logger.level}")

# Adjust level dynamically
logger.setLevel("DEBUG")
logger.info("Level changed to DEBUG")

# Or use numeric levels
import logging
logger.setLevel(logging.INFO)
logger.info("Level changed to INFO")
```

### Configuration from Environment Variables

```python
import os
from arlogi import LoggingConfig, LoggerFactory

def configure_from_env():
    """Configure logging from environment variables"""

    # Basic configuration
    level = os.getenv("LOG_LEVEL", "INFO")
    json_file = os.getenv("LOG_FILE", None)
    syslog_enabled = os.getenv("LOG_SYSLOG", "false").lower() == "true"

    config_kwargs = {
        "level": level,
        "json_file_name": json_file,
        "use_syslog": syslog_enabled
    }

    # Console formatting from environment
    if os.getenv("LOG_SHOW_TIME", "false").lower() == "true":
        config_kwargs["show_time"] = True

    if os.getenv("LOG_SHOW_PATH", "true").lower() == "false":
        config_kwargs["show_path"] = False

    # Module levels from environment (comma-separated)
    module_levels_str = os.getenv("LOG_MODULE_LEVELS", "")
    if module_levels_str:
        module_levels = {}
        for item in module_levels_str.split(","):
            if ":" in item:
                module, level = item.strip().split(":", 1)
                module_levels[module.strip()] = level.strip()
        config_kwargs["module_levels"] = module_levels

    config = LoggingConfig(**config_kwargs)
    LoggerFactory._apply_configuration(config)

# Usage
configure_from_env()
```

### Configuration File Support

```python
import json
import yaml
from pathlib import Path
from arlogi import LoggingConfig, LoggerFactory

def load_config_from_file(config_path):
    """Load logging configuration from JSON or YAML file"""

    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if config_file.suffix.lower() == '.json':
        with open(config_file, 'r') as f:
            data = json.load(f)
    elif config_file.suffix.lower() in ['.yaml', '.yml']:
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported config file format: {config_file.suffix}")

    config = LoggingConfig(**data)
    LoggerFactory._apply_configuration(config)

# config.json example:
# {
#   "level": "INFO",
#   "module_levels": {
#     "app.database": "DEBUG",
#     "app.auth": "WARNING"
#   },
#   "json_file_name": "logs/app.jsonl",
#   "show_time": false,
#   "show_level": true,
#   "show_path": true
# }

# Usage
load_config_from_file("config/logging.json")
```

## Advanced Handler Configuration

### Multiple JSON Files

```python
from arlogi import get_logger
from arlogi.handlers import JSONFileHandler
import logging

# Create separate loggers for different purposes
app_logger = get_logger("app")
security_logger = get_logger("security")
audit_logger = get_logger("audit")

# Add separate JSON handlers
security_handler = JSONFileHandler("logs/security.jsonl")
audit_handler = JSONFileHandler("logs/audit.jsonl")

security_logger.addHandler(security_handler)
security_logger.setLevel(logging.WARNING)

audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

# Usage
app_logger.info("Application message")          # Goes to console/default
security_logger.warning("Security event")      # Goes to security.jsonl
audit_logger.info("Audit trail entry")         # Goes to audit.jsonl
```

### Custom Formatters

```python
import logging
from arlogi.handlers import ColoredConsoleHandler

# Create custom console handler
handler = ColoredConsoleHandler(
    show_time=True,
    show_level=True,
    show_path=True,
    level_styles={
        "TRACE": "dim blue",
        "DEBUG": "dim cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red"
    }
)

# Add to specific logger
logger = get_logger("custom")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("Custom formatted message")
```

### Filtering Logs

```python
import logging

class BusinessEventFilter(logging.Filter):
    """Filter to only allow business event logs"""

    def filter(self, record):
        return hasattr(record, 'event_type')

# Create logger with filter
logger = get_logger("business")
business_filter = BusinessEventFilter()

# Add filter to all handlers
for handler in logger.handlers:
    handler.addFilter(business_filter)

# These will be logged
logger.info("User registered", event_type="user_signup")
logger.info("Order placed", event_type="order_created")

# These will be filtered out
logger.info("Debug message")
logger.debug("Technical details")
```

## Configuration Validation

### Validate Configuration

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger
import logging

def validate_logging_config():
    """Validate and test logging configuration"""

    # Configure logging
    config = LoggingConfig(level="DEBUG")
    LoggerFactory._apply_configuration(config)

    try:
        # Test basic logging
        logger = get_logger("validation")
        logger.info("Configuration validation started")

        # Test all log levels
        logger.trace("TRACE level test")
        logger.debug("DEBUG level test")
        logger.info("INFO level test")
        logger.warning("WARNING level test")
        logger.error("ERROR level test")

        # Test caller attribution
        logger.info("Caller attribution test", caller_depth=0)

        # Test structured logging
        logger.info("Structured data test", key="value", number=42)

        # Test exception logging
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception test")

        print("✅ Logging configuration validated successfully")
        return True

    except Exception as e:
        print(f"❌ Logging configuration validation failed: {e}")
        return False

# Usage
if validate_logging_config():
    print("Ready to start application")
else:
    print("Fix logging configuration before starting")
```

## Performance Optimization

### High-Performance Configuration

```python
from arlogi import LoggingConfig, LoggerFactory

def configure_high_performance():
    """Optimize for high-performance applications"""

    config = LoggingConfig(
        level="WARNING",  # Minimal logging
        json_file_name="logs/perf.jsonl",
        show_time=False,  # Fast console output
        show_level=False,
        show_path=False
    )
    LoggerFactory._apply_configuration(config)

def configure_balanced():
    """Balance between performance and observability"""

    config = LoggingConfig(
        level="INFO",
        module_levels={
            "app.critical": "DEBUG",  # Only critical modules verbose
        },
        json_file_name="logs/balanced.jsonl",
        show_time=False,  # Faster console
        show_level=True,
        show_path=False
    )
    LoggerFactory._apply_configuration(config)
```

### Conditional Logging

```python
import os
from arlogi import LoggingConfig, LoggerFactory

DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

if DEBUG_MODE:
    # Development configuration
    config = LoggingConfig(
        level="DEBUG",
        show_time=True,
        show_path=True
    )
else:
    # Production configuration
    config = LoggingConfig(
        level="INFO",
        json_file_name="logs/production.jsonl"
    )

LoggerFactory._apply_configuration(config)

# Usage in code
from arlogi import get_logger

logger = get_logger("performance")

def expensive_operation():
    if DEBUG_MODE:
        logger.debug("Starting expensive operation", caller_depth=1,
                    debug_data=get_debug_info())

    # Expensive operation here
    result = perform_calculation()

    if DEBUG_MODE:
        logger.debug("Expensive operation completed", caller_depth=1,
                    result=result)

    return result
```

This comprehensive configuration guide covers all aspects of setting up arlogi logging for different application types and environments.
