# Arlogi Library Documentation

**Version:** 0.601.04
**Python:** 3.13+
**License:** MIT

Comprehensive documentation for the arlogi logging library - a robust, type-safe, and highly configurable logging solution for Python applications.

---

## Key Features

- **🎯 Caller Attribution**: Trace log calls across function boundaries using `caller_depth` parameter
- **📊 Custom TRACE Level**: Ultra-detailed logging below DEBUG (level 5)
- **🎨 Rich Console Output**: Beautiful colored terminal output with Rich library
- **📝 JSON Logging**: Structured JSON logs for machine parsing and analysis
- **🔧 Type-Safe Configuration**: Modern `LoggingConfig` dataclass for compile-time safety
- **🧪 Test-Aware**: Automatic test mode detection for seamless pytest integration
- **🔌 Multiple Handlers**: Console, JSON file, and Syslog support
- **🏗️ Modular Handlers**: Dedicated JSON-only and syslog-only loggers

---

## Quick Start

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

# Configure logging using modern architecture
config = LoggingConfig(level="INFO")
LoggerFactory._apply_configuration(config)

# Get logger and log
logger = get_logger(__name__)
logger.info("Hello, Arlogi!", caller_depth=0)
```

**Output:**

```text
INFO    Hello, Arlogi!        [module()]
```

---

## Documentation Guide

### Getting Started

- **Installation and basic usage**: Get started with arlogi quickly
- **Caller Attribution Feature**: Learn about the unique `caller_depth` parameter

## Documentation

### 📖 User Documentation

1. **[User Guide](USER_GUIDE.md)**
   - Installation and setup
   - Basic usage patterns
   - Configuration options
   - Caller attribution guide
   - Common patterns
   - Troubleshooting tips

2. **[Configuration Guide](CONFIGURATION_GUIDE.md)**
   - Modern `LoggingConfig` architecture
   - Global configuration patterns
   - Per-module level overrides
   - Handler configuration
   - Environment-specific setups
   - Dynamic configuration

3. **[Caller Attribution Examples](CALLER_ATTRIBUTION_EXAMPLES.md)**
   - Basic depth usage (`caller_depth=0`, `caller_depth=1`)
   - Cross-module attribution
   - Real-world patterns (web APIs, databases, background jobs)
   - Performance considerations
   - Testing examples

### 🔧 Developer Documentation

4. **[Developer Guide](DEVELOPER_GUIDE.md)**
   - Development setup
   - Project structure
   - Testing strategies
   - Code quality standards
   - Release process
   - Contributing guidelines

5. **[Architecture Documentation](ARCHITECTURE.md)**
   - System design overview
   - Architecture diagrams (C4 model)
   - Design patterns
   - Component reference
   - Data flow
   - Extensibility points

### 📚 API Reference

6. **[API Reference](API_REFERENCE.md)**
   - Public API functions
   - `LoggingConfig` reference
   - `LoggerProtocol` interface
   - Handler classes
   - Log levels
   - Type hints
   - Examples

---

## Key Features by Category

### 🎯 Caller Attribution

| Feature | Description | Documentation |
|---------|-------------|---------------|
| `caller_depth=0` | Shows current function | [Examples](CALLER_ATTRIBUTION_EXAMPLES.md#using-caller_depth0-current-function) |
| `caller_depth=1` | Shows immediate caller | [Examples](CALLER_ATTRIBUTION_EXAMPLES.md#using-caller_depth1-immediate-caller) |
| `caller_depth=2+` | Shows deeper context | [Examples](CALLER_ATTRIBUTION_EXAMPLES.md#using-caller_depth2-callers-caller) |
| Cross-module | Tracks across modules | [Examples](CALLER_ATTRIBUTION_EXAMPLES.md#cross-module-attribution) |

### 🔧 Configuration

| Feature | Description | Documentation |
|---------|-------------|---------------|
| `LoggingConfig` | Type-safe configuration | [Config Guide](CONFIGURATION_GUIDE.md#basic-setup) |
| Module Levels | Per-module overrides | [Config Guide](CONFIGURATION_GUIDE.md#per-module-configuration) |
| JSON Logging | Structured output | [Config Guide](CONFIGURATION_GUIDE.md#json-file-configuration) |
| Syslog | System log integration | [Config Guide](CONFIGURATION_GUIDE.md#syslog-configuration-modern) |

### 📊 Log Levels

| Level | Value | Use Case |
|-------|-------|----------|
| `TRACE` | 5 | Function entry/exit, variable dumps |
| `DEBUG` | 10 | Detailed troubleshooting |
| `INFO` | 20 | General application flow |
| `WARNING` | 30 | Unexpected but recoverable |
| `ERROR` | 40 | Errors that don't stop execution |
| `CRITICAL` | 50 | Serious failures |

### 🎨 Handlers

| Handler | Purpose | Documentation |
|---------|---------|---------------|
| `ColoredConsoleHandler` | Rich console output | [API Reference](API_REFERENCE.md#coloredconsolehandler) |
| `JSONHandler` | JSON to stderr | [API Reference](API_REFERENCE.md#jsonhandler) |
| `JSONFileHandler` | JSON to file | [API Reference](API_REFERENCE.md#jsonfilehandler) |
| `ArlogiSyslogHandler` | Syslog output | [API Reference](API_REFERENCE.md#arlogisysloghandler) |

---

## Quick Reference

### Basic Setup

```python
from arlogi import LoggingConfig, LoggerFactory, get_logger

# Configure
config = LoggingConfig(level="INFO")
LoggerFactory._apply_configuration(config)

# Use
logger = get_logger(__name__)
logger.info("Application started", caller_depth=0)
```

### With JSON Logging

```python
config = LoggingConfig(
    level="INFO",
    json_file_name="logs/app.jsonl"
)
LoggerFactory._apply_configuration(config)
```

### Per-Module Levels

```python
config = LoggingConfig(
    level="INFO",
    module_levels={
        "app.database": "DEBUG",
        "app.network": "TRACE"
    }
)
LoggerFactory._apply_configuration(config)
```

### Dedicated JSON Logger

```python
from arlogi import get_json_logger, cleanup_json_logger

audit_logger = get_json_logger("audit", "logs/audit.jsonl")
audit_logger.info("User action", user_id=123)

# Clean up when done
cleanup_json_logger("audit")
```

---

## Performance Notes

- **Standard log call**: ~0.5μs (no attribution)
- **Log with `caller_depth`**: ~1.5μs (stack frame inspection)
- **Deep stack (depth=5)**: ~3μs (multiple frame walks)

For optimal performance, use `caller_depth` only when needed for debugging or context tracking.

---

## Testing Integration

Arlogi automatically detects test environments (pytest, unittest) and:

- Sets default level to DEBUG (instead of INFO)
- Skips handler setup to prevent double logging
- Works seamlessly with `caplog` fixture

No special configuration needed!

---

## Requirements

- **Python**: 3.13 or higher
- **Dependencies**: `rich` >= 14.2.0 (automatically installed)

---

## Additional Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/your-org/arlogi/issues)
- **Changelog**: Check project repository for version history

---

## License

MIT License
