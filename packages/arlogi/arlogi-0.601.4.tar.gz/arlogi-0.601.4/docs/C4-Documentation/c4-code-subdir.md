# C4 Code Level: subdir

## Overview
- **Name**: Subdirectory Test Module
- **Description**: Test directory demonstrating the arlogi library's functionality from a nested subdirectory location
- **Location**: `/subdir/`
- **Language**: Python
- **Purpose**: This directory serves as an example/test location to verify that the arlogi logging library works correctly when imported from subdirectories and demonstrates relative path handling

## Code Elements

### Functions/Methods

#### `main()` (implicit main execution)
- **Signature**: No explicit function - script-level execution
- **Description**: Main execution block that demonstrates the arlogi library functionality
- **Location**: `subdir/test_nested.py:1-19`
- **Dependencies**: `arlogi.setup_logging`, `arlogi.get_logger`

### Classes/Modules

#### `test_nested.py` Module
- **Description**: Test script demonstrating arlogi library usage from a subdirectory
- **Location**: `subdir/test_nested.py`
- **Elements**:
  - Imports `setup_logging` and `get_logger` from arlogi
  - Configures logging with specific settings (INFO level, no timestamps, show level and path)
  - Creates a logger instance with name "test.subdir"
  - Logs informational and error messages
- **Dependencies**:
  - `arlogi` (main library package)
  - `arlogi.factory` (provides setup_logging and get_logger)

## Dependencies

### Internal Dependencies
- **arlogi**: Main logging library package
  - `arlogi.factory`: Provides `setup_logging` and `get_logger` functions
  - `arlogi.config`: Provides logging configuration classes and utilities

### External Dependencies
- **logging**: Python's built-in logging module (likely used by arlogi internally)

## Relationships

This is a simple test module that demonstrates the arlogi library's functionality. Since this is a procedural script rather than OOP code, we'll use a flowchart to show the execution flow:

```mermaid
---
title: Test Execution Flow for subdir/test_nested.py
---
flowchart TB
    subgraph Import
        A[import arlogi<br>setup_logging<br>get_logger]
    end
    subgraph Setup
        B[setup_logging<br>level=INFO<br>show_time=False<br>show_level=True<br>show_path=True]
    end
    subgraph Logger Creation
        C[logger =<br>get_logger<br>"test.subdir"]
    end
    subgraph Logging
        D[logger.info<br>"Message from subdir"]
        E[logger.error<br>"Error from subdir"]
    end

    A --> B
    B --> C
    C --> D
    C --> E
```

## Notes

- This test file serves as validation that the arlogi library works correctly when imported from subdirectories
- The logger name "test.subdir" suggests hierarchical logging naming conventions
- The configuration demonstrates practical logging setup with path visibility enabled
- This appears to be part of the test suite for the arlogi library
- The cache file indicates this test has been run with pytest