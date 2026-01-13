# Arlogi Architecture Documentation

This document describes the architecture, design patterns, and internal structure of the arlogi logging library.

---

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagrams](#architecture-diagrams)
- [Design Patterns](#design-patterns)
- [Component Reference](#component-reference)
- [Data Flow](#data-flow)
- [Extensibility](#extensibility)

---

## System Overview

Arlogi is a Python logging library built on top of the standard `logging` module. It provides:

- **Custom TRACE level** (below DEBUG) for ultra-detailed logging
- **Caller attribution** via stack frame inspection
- **Multiple output handlers**: Rich console, JSON files, Syslog
- **Type-safe configuration** via dataclasses
- **Factory pattern** for handler creation

### Technology Stack

| Component       | Technology        | Purpose                            |
| --------------- | ----------------- | ---------------------------------- |
| Core Logging    | `logging` module  | Python standard library foundation |
| Console Output  | `rich`            | Premium colored terminal output    |
| Type Safety     | `typing.Protocol` | Runtime-checkable type hints       |
| Configuration   | `dataclasses`     | Immutable configuration objects    |
| Structured Logs | `json`            | Machine-readable log output        |

---

## Architecture Diagrams

### C4 Context Diagram

```mermaid
graph TB
    subgraph "Your Application"
        App[Application Code]
    end

    subgraph "arlogi"
    subgraph "arlogi"
        API[Public API<br/>LoggingConfig, get_logger]
        Logger[LoggerFactory<br/>TraceLogger]
        Handlers[Handlers<br/>Console, JSON, Syslog]
    end

    subgraph "External Systems"
        Console[Terminal]
        Files[Log Files]
        Syslog[Syslog Server]
    end

    App --> API
    API --> Logger
    Logger --> Handlers
    Handlers --> Console
    Handlers --> Files
    Handlers --> Syslog
```

### C4 Container Diagram

```mermaid
graph TB
    subgraph "arlogi Library"
        subgraph "Public API Layer"
            Init[__init__.py<br/>Public Exports]
            Factory[factory.py<br/>LoggerFactory]
        end

        subgraph "Configuration Layer"
            Config[config.py<br/>LoggingConfig]
            HF[handler_factory.py<br/>HandlerFactory]
        end

        subgraph "Core Layer"
            Levels[levels.py<br/>TRACE Registration]
            Types[types.py<br/>LoggerProtocol]
            TraceLog[TraceLogger<br/>Caller Attribution]
        end

        subgraph "Handlers Layer"
            Console[ColoredConsoleHandler<br/>Rich Output]
            JSON[JSONHandler<br/>Structured Logs]
            SyslogHandler[ArlogiSyslogHandler<br/>Syslog Output]
        end
    end

    Init --> Factory
    Factory --> Config
    Factory --> HF
    Factory --> TraceLog
    HF --> Console
    HF --> JSON
    HF --> SyslogHandler
    TraceLog --> Types
    TraceLog --> Levels
```

### Component Dependency Diagram

```mermaid
graph LR
    subgraph "Public Module"
        Init[__init__.py]
    end

    subgraph "Core Modules"
        Factory[factory.py]
        Config[config.py]
        HandlerFac[handler_factory.py]
        Handlers[handlers.py]
        Levels[levels.py]
        Types[types.py]
    end

    Init --> Factory
    Init --> Config
    Init --> HandlerFac
    Init --> Levels
    Init --> Types

    Factory --> Config
    Factory --> HandlerFac
    Factory --> Handlers
    Factory --> Levels

    HandlerFac --> Handlers
```

### Sequence Diagram: Logging Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Config as LoggingConfig
    participant Factory as LoggerFactory
    participant Logger as TraceLogger
    participant Handler as ColoredConsoleHandler
    participant Rich as RichHandler
    participant Console as Terminal

    App->>Config: LoggingConfig(level="INFO")
    App->>Factory: _apply_configuration(config)
    Factory->>Logger: Root Logger level set
    Factory->>Handler: Handlers created/added
    App->>Logger: logger.info("msg", caller_depth=1)
    Logger->>Logger: _process_params (attribution)
    Logger->>Handler: emit(record)
    Handler->>Rich: _log_render(...)
    Rich->>Console: Print formatted output
```

### Class Diagram

```mermaid
classDiagram
    class LoggingConfig {
        <<frozen dataclass>>
        +int|str level
        +dict module_levels
        +str json_file_name
        +bool json_file_only
        +bool use_syslog
        +str|tuple syslog_address
        +bool show_time
        +bool show_level
        +bool show_path
        +resolved_level() int
        +show_console() bool
        +has_json_output() bool
        +from_kwargs(**kwargs) LoggingConfig
        +to_dict() dict
    }

    class HandlerFactory {
        <<factory>>
        +create_console(config) ColoredConsoleHandler
        +create_json_stream() JSONHandler
        +create_json_file(config) JSONFileHandler
        +create_json_handler(config) Handler
        +create_syslog(config) ArlogiSyslogHandler
        +create_handlers(config) List~Handler~
    }

    class LoggerFactory {
        <<factory>>
        _initialized: bool
        _global_logger: TraceLogger|None
        +_apply_configuration(config) None
        +get_logger(name, level) LoggerProtocol
        +get_json_logger(name, file) LoggerProtocol
        +get_syslog_logger(name, addr) LoggerProtocol
        +cleanup_json_logger(name) None
        +cleanup_syslog_logger(name) None
        +is_test_mode() bool
        -_initialize_trace_level() None
        -_configure_root_logger(config) None
        -_clear_and_add_handlers(config) None
        -_configure_module_levels(config) None
    }

    class TraceLogger {
        extends Logger
        +_get_caller_info(depth) tuple
        +_process_params(msg, kwargs) tuple
        +trace(msg, *args, **kwargs) None
        +debug(msg, *args, **kwargs) None
        +info(msg, *args, **kwargs) None
        +warning(msg, *args, **kwargs) None
        +error(msg, *args, **kwargs) None
        +critical(msg, *args, **kwargs) None
        +exception(msg, *args, **kwargs) None
        +log(level, msg, *args, **kwargs) None
    }

    class LoggerProtocol {
        <<protocol>>
        +trace(msg, *args, **kwargs) None
        +debug(msg, *args, **kwargs) None
        +info(msg, *args, **kwargs) None
        +warning(msg, *args, **kwargs) None
        +error(msg, *args, **kwargs) None
        +critical(msg, *args, **kwargs) None
        +exception(msg, *args, **kwargs) None
        +log(level, msg, *args, **kwargs) None
        +setLevel(level) None
        +isEnabledFor(level) bool
        +getEffectiveLevel() int
        +name: str
    }

    class ColoredConsoleHandler {
        extends RichHandler
        -level_styles: dict
        -project_root: str
        +_find_project_root() str
        +render(record, traceback, message) Any
        +get_level_text(record) Any
        +render_message(record, message) Any
    }

    class JSONHandler {
        extends StreamHandler
    }

    class JSONFileHandler {
        extends FileHandler
    }

    class ArlogiSyslogHandler {
        extends SysLogHandler
    }

    LoggingConfig ..> HandlerFactory : uses
    LoggingConfig ..> LoggerFactory : uses
    LoggerFactory ..> HandlerFactory : uses
    LoggerFactory ..> TraceLogger : creates
    TraceLogger ..|> LoggerProtocol : implements
    HandlerFactory ..> ColoredConsoleHandler : creates
    HandlerFactory ..> JSONHandler : creates
    HandlerFactory ..> JSONFileHandler : creates
    HandlerFactory ..> ArlogiSyslogHandler : creates
```

---

## Design Patterns

### Factory Pattern

**HandlerFactory** encapsulates handler creation logic:

```python
# Instead of direct instantiation
handler = ColoredConsoleHandler(show_time=True)

# Use factory for consistency and testability
handler = HandlerFactory.create_console(config)
```

**Benefits:**

- Single responsibility per factory method
- Easy to add new handler types
- Simplified testing with mock factories

### Builder Pattern

**LoggingConfig.from_kwargs()** provides flexible configuration:

```python
# Build configuration from multiple sources
config = LoggingConfig.from_kwargs(
    level="INFO",
    module_levels={"app.db": "DEBUG"}
)
LoggerFactory._apply_configuration(config)
```

### Protocol Pattern

**LoggerProtocol** defines the logger interface:

```python
@runtime_checkable
class LoggerProtocol(Protocol):
    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None: ...
```

**Benefits:**

- Type safety without inheritance
- Runtime checking with `isinstance()`
- Structural subtyping support

### Strategy Pattern

Different handlers implement different output strategies:

```python
# Console strategy
console = ColoredConsoleHandler()

# JSON strategy
json_handler = JSONHandler()

# Syslog strategy
syslog = ArlogiSyslogHandler()
```

---

## Component Reference

### Core Modules

| Module               | Responsibility                    | Lines of Code |
| -------------------- | --------------------------------- | ------------- |
| `factory.py`         | Logger creation and configuration | ~450          |
| `handlers.py`        | Output handler implementations    | ~340          |
| `config.py`          | Configuration dataclass           | ~195          |
| `handler_factory.py` | Handler factory                   | ~170          |
| `levels.py`          | TRACE level registration          | ~20           |
| `types.py`           | Logger protocol definition        | ~25           |

### File Structure

```text
src/arlogi/
├── __init__.py              # Public API exports
├── config.py                # LoggingConfig dataclass
├── config_builder.py        # Configuration builder utilities (if present)
├── factory.py               # LoggerFactory, TraceLogger
├── handler_factory.py       # HandlerFactory
├── handlers.py              # All handler classes
├── levels.py                # TRACE level registration
└── types.py                 # LoggerProtocol
```

---

## Data Flow

### Initialization Flow

The initialization process uses the `LoggingConfig` pattern for type-safe configuration:

```mermaid
graph TD
    A[LoggingConfig init] --> B["LoggerFactory._apply_configuration"]

    B --> C[_initialize_trace_level]
    B --> D[_configure_root_logger]
    B --> E[is_test_mode?]
    E -->|No| F[_clear_and_add_handlers]
    E -->|Yes| G[Skip - use pytest handlers]
    F --> H[HandlerFactory.create_handlers]
    H --> I[Add handlers to root]
    B --> J[_configure_module_levels]
```

### Logging Call Flow

```mermaid
graph TD
    A[logger.info] --> B[_process_params]
    B --> C{from_ set?}
    C -->|Yes| D[_get_caller_info]
    C -->|No| E[Skip attribution]
    D --> F[Build attribution string]
    F --> G[Append to message]
    E --> G
    G --> H["super().info"]
    H --> I[Logging.Logger.info]
    I --> J[Handler.emit]
    J --> K{Handler Type}
    K -->|Console| L[ColoredConsoleHandler]
    K -->|JSON| M[JSONHandler]
    K -->|Syslog| N[ArlogiSyslogHandler]
```

---

## Extensibility

### Adding Custom Handlers

```python
from arlogi import HandlerFactory, LoggingConfig
from arlogi.handlers import ColoredConsoleHandler

class CustomConsoleHandler(ColoredConsoleHandler):
    """Custom handler with additional formatting."""

    def emit(self, record):
        # Custom pre-processing
        record.custom_field = "custom_value"
        super().emit(record)

# Extend HandlerFactory
class ExtendedHandlerFactory(HandlerFactory):
    @staticmethod
    def create_custom(config):
        return CustomConsoleHandler(
            show_time=config.show_time,
            show_level=config.show_level
        )
```

### Adding Custom Log Levels

```python
import logging
from arlogi.levels import TRACE_LEVEL_NUM

# Define a new level
VERBOSE = 8  # Between TRACE (5) and DEBUG (10)

# Register it
logging.addLevelName(VERBOSE, "VERBOSE")
setattr(logging, "VERBOSE", VERBOSE)

# Use it
logger.log(VERBOSE, "Verbose message")
```

### Custom Configuration Sources

```python
from arlogi import LoggingConfig
import yaml

def config_from_yaml(file_path):
    """Load LoggingConfig from YAML file."""
    with open(file_path) as f:
        data = yaml.safe_load(f)
    return LoggingConfig(**data)

# Use it
config = config_from_yaml("logging_config.yaml")
```

---

## Performance Considerations

### Caller Attribution Overhead

| Operation            | Time   | Notes                  |
| -------------------- | ------ | ---------------------- |
| Standard log call    | ~0.5μs | No attribution         |
| Log with `caller_depth=`    | ~1.5μs | Stack frame inspection |
| Deep stack (depth=5) | ~3μs   | Multiple frame walks   |

**Optimization Tip:** Use `from_` only in development/debug builds.

### Memory Usage

| Component         | Memory          | Notes                  |
| ----------------- | --------------- | ---------------------- |
| LoggingConfig     | ~200 bytes      | Immutable, shared      |
| TraceLogger       | ~1KB            | Per logger instance    |
| Handler instances | ~500 bytes each | Varies by handler type |

---

## Error Handling Strategy

### Graceful Degradation

```mermaid
graph TD
    A[Logging Call] --> B{Handler Available?}
    B -->|Yes| C[Emit to Handler]
    B -->|No| D[Fallback to Stderr]
    C --> E{Emit Success?}
    E -->|Yes| F[Continue]
    E -->|No| D
    D --> F
```

### Error Boundaries

| Component             | Error Handling                        |
| --------------------- | ------------------------------------- |
| LoggingConfig         | Validates on init, raises ValueError  |
| HandlerFactory        | Raises ValueError for invalid config  |
| LoggerFactory         | Silently falls back on handler errors |
| ColoredConsoleHandler | Falls back to basic formatting        |
| ArlogiSyslogHandler   | Falls back to UDP, then silent        |

---

## Testing Strategy

### Test Mode Detection

```python
def is_test_mode() -> bool:
    return (
        "pytest" in sys.modules
        or "unittest" in sys.modules
        or os.environ.get("PYTEST_CURRENT_TEST") is not None
    )
```

In test mode:

- Default level is DEBUG (not INFO)
- Handlers are NOT added to root (prevents double logging)
- Works seamlessly with `caplog` fixture

---

## Version Compatibility

| Python | arlogi | Status              |
| ------ | ------ | ------------------- |
| 3.13+  | 0.601+ | Supported           |
| 3.12   | 0.512+ | Supported (with uv) |
| 3.11   | 0.512+ | Supported (with uv) |
| <3.11  | -      | Not supported       |

---

## Future Enhancements

### Planned Features

1. **Async Handlers** - AsyncIO-compatible log handlers
2. **Log Rotation** - Built-in rotation for JSON files
3. **Filter Support** - Per-handler log filtering
4. **Context Injection** - Automatic request/context IDs
5. **Metrics Integration** - OpenTelemetry integration

### Extension Points

- Custom formatters via `Formatter` subclassing
- Custom filters via `Filter` subclassing
- Custom handlers via `Handler` subclassing
- Configuration plugins via `LoggingConfig` inheritance

---

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Rich Library](https://rich.readthedocs.io/)
- [C4 Model](https://c4model.com/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
