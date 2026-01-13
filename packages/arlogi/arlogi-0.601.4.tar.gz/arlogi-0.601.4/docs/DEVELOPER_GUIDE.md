# Arlogi Developer Guide

This guide is for contributors and maintainers of the arlogi library.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Release Process](#release-process)
- [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- Python 3.13 or higher (required by project configuration)
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Clone Repository

```bash
git clone https://github.com/your-org/arlogi.git
cd arlogi
```

### Install Dependencies

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

### Development Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/arlogi --cov-report=html

# Run linter
uv run ruff check src/arlogi tests

# Format code
uv run ruff format src/arlogi tests

# Check with radon (complexity analysis)
uv run radon cc src/arlogi -a -nb
```

---

## Project Structure

```text
arlogi/
├── src/
│   └── arlogi/
│       ├── __init__.py              # Public API exports
│       ├── config.py                # LoggingConfig dataclass
│       ├── config_builder.py        # Configuration builder utilities
│       ├── factory.py               # LoggerFactory, TraceLogger
│       ├── handler_factory.py       # HandlerFactory
│       ├── handlers.py              # Handler implementations
│       ├── levels.py                # TRACE level registration
│       └── types.py                 # LoggerProtocol
├── tests/
│   ├── test_core.py                 # Core functionality tests
│   ├── test_features.py             # Feature tests
│   ├── test_resource_management.py  # Resource cleanup tests
│   ├── test_thread_safety.py        # Thread safety tests
│   └── example/
│       └── example.py               # Example usage
├── docs/
│   ├── API_REFERENCE.md             # Complete API documentation
│   ├── ARCHITECTURE.md              # Architecture diagrams
│   ├── USER_GUIDE.md                # User guide
│   ├── CONFIGURATION_GUIDE.md       # Configuration reference
│   ├── CALLER_ATTRIBUTION_EXAMPLES.md # Caller attribution examples
│   ├── index.md                     # Documentation index
│   └── DEVELOPER_GUIDE.md           # This file
├── pyproject.toml                   # Project configuration
├── uv.lock                          # Dependency lock file
├── .ruff.toml                       # Ruff linter configuration
└── README.md                        # Project README
```

### Module Responsibilities

| Module               | Responsibility                     | Complexity Target |
| -------------------- | ---------------------------------- | ----------------- |
| `config.py`          | Configuration validation & storage | < 5 per method    |
| `factory.py`         | Logger creation & orchestration    | < 5 per method    |
| `handler_factory.py` | Handler creation                   | < 3 per method    |
| `handlers.py`        | Output handlers                    | < 10 per method   |
| `levels.py`          | TRACE level registration           | N/A (simple)      |
| `types.py`           | Protocol definitions               | N/A (declarative) |

---

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_core.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/arlogi --cov-report=term-missing
```

### Coverage Requirements

| Module               | Target Coverage | Status |
| -------------------- | --------------- | ------ |
| `config.py`          | 80%             | 80%    |
| `factory.py`         | 80%             | 75%    |
| `handler_factory.py` | 70%             | 49%    |
| `handlers.py`        | 60%             | 36%    |
| `levels.py`          | 90%             | 85%    |

### Test Categories

#### Unit Tests

Test individual functions and methods in isolation.

```python
def test_logging_config_validation():
    """Test that invalid log levels raise ValueError."""
    with pytest.raises(ValueError):
        LoggingConfig(level="INVALID")

def test_direct_config_apply():
    """Test that direct LoggingConfig application works."""
    config = LoggingConfig(level="DEBUG")
    LoggerFactory._apply_configuration(config)
    assert logging.getLogger().level == logging.DEBUG
```

#### Integration Tests

Test interactions between components.

```python
def test_setup_with_json_file():
    """Test that configuration creates JSON file handler."""
    config = LoggingConfig(json_file_name="logs/test.jsonl")
    LoggerFactory._apply_configuration(config)
    root = logging.getLogger()
    assert any(isinstance(h, JSONFileHandler) for h in root.handlers)
```

#### Feature Tests

Test end-to-end functionality.

```python
def test_caller_attribution():
    """Test that caller attribution shows correct function."""
    logger = get_logger("test")
    logger.info("Test message", caller_depth=1)
    # Verify output contains parent function name
```

### Writing Tests

#### Test Structure

```python
import pytest
from arlogi import LoggingConfig, LoggerFactory, get_logger

class TestLoggerFactory:
    """Tests for LoggerFactory class."""

    def setup_method(self):
        """Reset logging state before each test."""
        # Clear existing handlers
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a valid logger."""
        logger = get_logger("test")
        assert logger is not None
        assert logger.name == "test"

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
    def test_logger_respects_level(self, level):
        """Test that logger respects configured level."""
        config = LoggingConfig(level=level)
        LoggerFactory._apply_configuration(config)
        logger = get_logger("test")
        assert logger.getEffectiveLevel() == getattr(logging, level)
```

#### Test Fixtures

```python
@pytest.fixture
def temp_log_file(tmp_path):
    """Create a temporary log file path."""
    return tmp_path / "test.jsonl"

@pytest.fixture
def configured_logger(temp_log_file):
    """Create a logger configured for testing."""
    config = LoggingConfig(
        level="DEBUG",
        json_file_name=str(temp_log_file)
    )
    LoggerFactory._apply_configuration(config)
    return get_logger("test")
```

### Test Mode Detection

Tests should work correctly with arlogi's test mode detection:

```python
def test_test_mode_detection():
    """Verify is_test_mode() returns True during pytest."""
    from arlogi import is_test_mode
    assert is_test_mode() is True
```

---

## Code Quality

### Linting with Ruff

```bash
# Check for issues
uv run ruff check src/arlogi tests

# Auto-fix issues
uv run ruff check --fix src/arlogi tests

# Format code
uv run ruff format src/arlogi tests
```

### Ruff Configuration

Key rules from `.ruff.toml`:

| Rule | Description           | Severity |
| ---- | --------------------- | -------- |
| C901 | Complexity limit (10) | Error    |
| F401 | Unused imports        | Error    |
| F841 | Unused variables      | Error    |
| SIM  | Simplify code         | Warning  |

### Complexity Limits

| Metric                | Limit     | Enforcement        |
| --------------------- | --------- | ------------------ |
| Cyclomatic Complexity | 10        | Ruff C901          |
| Method Length         | 30 lines  | Code review        |
| Class Length          | 300 lines | Code review        |
| Module Length         | 500 lines | Consider splitting |

### Code Style Guidelines

#### Naming Conventions

```python
# Classes: PascalCase
class LoggingConfig:
    pass

# Functions/Variables: snake_case
def get_logger(name):
    pass

# Constants: UPPER_SNAKE_CASE
TRACE_LEVEL_NUM = 5

# Private methods: _leading_underscore
def _internal_method(self):
    pass
```

#### Docstring Format

```python
def complex_function(arg1, arg2):
    """Brief description of function.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: If arg1 is invalid

    Examples:
        >>> complex_function("a", "b")
        "result"
    """
    pass
```

#### Type Hints

```python
from typing import Any, List, Dict, Optional

# Always use type hints for public APIs
def process_data(
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process data with options."""
    pass
```

### Pre-commit Hooks

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "Running ruff check..."
uv run ruff check src/arlogi tests

echo "Running ruff format..."
uv run ruff format --check src/arlogi tests

echo "Running tests..."
uv run pytest tests/ -q

echo "All checks passed!"
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

---

## Release Process

### Version Management

Arlogi uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. **Update Version**

   ```bash
   # Update pyproject.toml
   version = "0.513.0"
   ```

2. **Update Changelog**

   ```markdown
   ## [0.513.0] - 2025-12-28

   ### Added

   - New feature X

   ### Changed

   - Improved Y

   ### Fixed

   - Bug Z
   ```

3. **Run Full Test Suite**

   ```bash
   uv run pytest --cov=src/arlogi
   ```

4. **Create Git Tag**

   ```bash
   git tag -a v0.513.0 -m "Release v0.513.0"
   git push origin v0.513.0
   ```

5. **Build Distribution**

   ```bash
   uv build
   ```

6. **Publish to PyPI**

   ```bash
   uv publish
   ```

### Release Notes Template

```markdown
# Release {version}

## Summary

{Brief description of release}

## What's New

- Feature 1
- Feature 2

## Breaking Changes

- Breaking change 1 (migration guide)

## Bug Fixes

- Bug fix 1
- Bug fix 2

## Upgrading

See [MIGRATION.md](docs/MIGRATION.md) for upgrade instructions.
```

---

## Contributing

### Contribution Workflow

1. **Fork Repository**

   ```bash
   # Fork on GitHub, then clone
   git clone https://github.com/YOUR_USERNAME/arlogi.git
   cd arlogi
   git remote add upstream https://github.com/original/arlogi.git
   ```

2. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

4. **Run Quality Checks**

   ```bash
   uv run ruff check src/arlogi tests
   uv run pytest tests/
   ```

5. **Commit Changes**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and Create PR**

   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Examples:**

```text
feat(factory): add LoggingConfig support

feat(factory): add cleanup_json_logger and cleanup_syslog_logger

fix(handlers): resolve unused variable warning

docs(api): update handler examples
```

### Pull Request Guidelines

#### PR Title

```text
feat: add async handler support
```

#### PR Description Template

```markdown
## Summary

Brief description of changes.

## Changes

- Added async handler class
- Updated tests
- Updated documentation

## Testing

- Added unit tests for async handler
- Manual testing with asyncio application

## Checklist

- [ ] Tests pass
- [ ] No linting errors
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Code Review Criteria

PRs are reviewed against:

1. **Functionality**
   - Does it work as intended?
   - Are edge cases handled?

2. **Code Quality**
   - Is code readable?
   - Are names descriptive?
   - Is complexity acceptable?

3. **Testing**
   - Are tests comprehensive?
   - Is coverage adequate?

4. **Documentation**
   - Are docstrings complete?
   - Is user documentation updated?

5. **Backward Compatibility**
   - Are breaking changes documented?
   - Is migration path clear?

---

## Architecture Decisions

### Current Architecture

Arlogi follows SOLID principles:

- **S**: Each class has single responsibility
- **O**: HandlerFactory is extensible
- **L**: All handlers are substitutable
- **I**: LoggerProtocol is focused
- **D**: Depends on abstractions (Protocol)

### Decision Records

Significant architectural decisions should be documented:

```markdown
# ADR-001: Use Protocol for Logger Interface

## Status

Accepted

## Context

Need type-safe logger interface that doesn't require inheritance.

## Decision

Use `typing.Protocol` for `LoggerProtocol`.

## Consequences

- Pros: Type safety without inheritance
- Cons: Requires Python 3.8+
```

---

## Performance Guidelines

### Performance Targets

| Operation                   | Target | Notes                     |
| --------------------------- | ------ | ------------------------- |
| Log call (no attribution)   | < 1μs  | Standard logging overhead |
| Log call (with attribution) | < 5μs  | Stack frame inspection    |
| Handler emit                | < 10μs | I/O excluded              |

### Profiling

```python
import cProfile
import pstats

def profile_logging():
    pr = cProfile.Profile()
    pr.enable()

    # Logging code
    for _ in range(10000):
        logger.info("Test message")

    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Optimization Checklist

- [ ] Avoid expensive string formatting when disabled
- [ ] Use lazy evaluation for complex operations
- [ ] Minimize stack frame inspection depth
- [ ] Cache repeated operations
- [ ] Use efficient data structures

---

## Documentation

### Updating Documentation

1. **API Changes**: Update `API_REFERENCE.md`
2. **New Features**: Update `USER_GUIDE.md`
3. **Architecture Changes**: Update `ARCHITECTURE.md`
4. **Examples**: Update `tests/example/example.py`

### Docstring Standards

All public APIs must have docstrings:

```python
def public_function(arg1: str) -> bool:
    """Brief description.

    Extended description if needed.

    Args:
        arg1: Description

    Returns:
        Description of return

    Raises:
        ValueError: When arg1 is invalid

    Examples:
        >>> public_function("test")
        True
    """
    pass
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv sync
      - name: Run linting
        run: uv run ruff check src/arlogi tests
      - name: Run tests
        run: uv run pytest --cov=src/arlogi
```

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/your-org/arlogi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/arlogi/discussions)
- **Email**: <maintainers@example.com>

---

## License

Contributions are licensed under the MIT License. See LICENSE for details.

By contributing, you agree that your contributions will be licensed under the MIT License.
