# C4 Architecture Documentation

This directory contains comprehensive C4 architecture documentation for the **arlogi** Python logging library, following the [C4 model](https://c4model.com/) created by Simon Brown.

## About the C4 Model

The C4 model is a simple way to model software architecture at four levels of detail:

1. **Context** - High-level view of the system, its users, and external systems
2. **Container** - Applications, data stores, micro-services, etc.
3. **Component** - Logical components within containers
4. **Code** - Detailed code-level documentation

For more information, visit: <https://c4model.com/>

## Documentation Structure

```text
C4-Documentation/
├── README.md                          # This file
├── c4-context.md                      # System context (Level 1)
├── c4-container.md                    # Container-level documentation (Level 2)
├── c4-component.md                    # Master component index (Level 3)
├── c4-component-core-logging.md       # Core Logging Library component
├── c4-component-test-suite.md         # Test Suite component
├── c4-component-documentation.md      # Documentation System component
├── c4-code-src-arlogi.md              # Source code documentation (Level 4)
├── c4-code-tests.md                   # Test suite code documentation
├── c4-code-tests-example.md           # Example tests code documentation
├── c4-code-docs-reference.md          # API reference docs structure
├── c4-code-docs-scripts.md            # Documentation build scripts
├── c4-code-subdir.md                  # Subdirectory test module
└── apis/                              # API specifications
    └── arlogi-api.yaml                # OpenAPI 3.1.0 specification
```

## Quick Navigation

### Start Here

- **[System Context (c4-context.md)](c4-context.md)** - Begin here for a high-level overview of the arlogi system, its users, and its place in the broader software ecosystem.

### Architecture Levels

- **Level 1: [System Context](c4-context.md)** - Who uses the system and what external systems it interacts with
- **Level 2: [Containers](c4-container.md)** - How the system is deployed (Python package, documentation site, test suite)
- **Level 3: [Components](c4-component.md)** - Logical components and their relationships
- **Level 4: [Code Documentation](#code-level-documents)** - Detailed code-level documentation

### Component Documentation

- **[Core Logging Library](c4-component-core-logging.md)** - The main logging functionality
- **[Test Suite](c4-component-test-suite.md)** - Quality assurance and testing infrastructure
- **[Documentation System](c4-component-documentation.md)** - Documentation generation and deployment

### Code-Level Documents

- **[Source Code (src/arlogi)](c4-code-src-arlogi.md)** - Core library implementation
- **[Test Suite (tests)](c4-code-tests.md)** - Test implementations
- **[Example Tests (tests/example)](c4-code-tests-example.md)** - Example usage
- **[Documentation Scripts (docs/scripts)](c4-code-docs-scripts.md)** - Build automation
- **[API Reference (docs/reference)](c4-code-docs-reference.md)** - Generated documentation
- **[Subdir Tests (subdir)](c4-code-subdir.md)** - Additional test module

### API Specifications

- **[OpenAPI Specification (apis/arlogi-api.yaml)](apis/arlogi-api.yaml)** - Complete API documentation in OpenAPI 3.1.0 format

## System Overview

**arlogi** is a robust, type-safe logging library for Python that extends the standard logging module with modern features and premium aesthetics.

### Key Features

- Custom TRACE level (level 5) for ultra-detailed debugging
- Premium colored output using the `rich` library
- Structured JSON logging for log aggregation systems
- Module-specific configuration capabilities
- Dedicated destination loggers (JSON-only, syslog-only)
- Caller attribution feature to trace log calls across function boundaries
- Type safety with LoggerProtocol

## Personas

The system serves the following primary users:

1. **Application Developer** - Build applications with production-ready logging
2. **Library Developer** - Create reusable libraries with caller attribution
3. **QA/Testing Engineer** - Test applications with automated test mode
4. **DevOps Engineer** - Manage logs in production environments
5. **Documentation User** - Access API documentation and user guides
6. **Contributor/Maintainer** - Contribute to the codebase

## Technology Stack

- **Language**: Python 3.13+
- **Console Output**: Rich 14.2.0+
- **Documentation**: MkDocs 1.5+, Material Theme, MkDocstrings
- **Testing**: pytest 9.0.2+, pytest-cov 7.0.0+
- **Build System**: uv package manager, hatchling

## Reading Guide

### For Non-Technical Stakeholders

Start with the **[System Context](c4-context.md)** document to understand:

- What the system does
- Who uses it
- What problems it solves
- How it fits into the broader ecosystem

### For Developers

1. Read the **[System Context](c4-context.md)** for a high-level overview
2. Review the **[Containers](c4-container.md)** to understand deployment architecture
3. Study the **[Components](c4-component.md)** to understand logical architecture
4. Dive into **[Code-Level Documentation](#code-level-documents)** for implementation details

### For Architects

Focus on:

- **[System Context](c4-context.md)** - System boundaries and external relationships
- **[Containers](c4-container.md)** - Deployment architecture and technology choices
- **[Components](c4-component.md)** - Component boundaries and interactions

### For Contributors

Start with:

- **[Core Logging Library Component](c4-component-core-logging.md)** - Understand the main component
- **[Source Code Documentation](c4-code-src-arlogi.md)** - Detailed implementation
- **[Test Suite Component](c4-component-test-suite.md)** - Testing approach

## Diagrams

Each level of documentation includes Mermaid diagrams that visualize:

- **Context Level** - System context diagram showing users and external systems
- **Container Level** - Container diagram showing deployment units
- **Component Level** - Component diagrams showing logical components and relationships
- **Code Level** - Class hierarchy and module dependency diagrams

These diagrams can be rendered in any Mermaid-compatible viewer, including:

- GitHub/GitLab markdown rendering
- MkDocs with Mermaid extension
- VS Code with Mermaid preview extensions
- Online Mermaid live editor (<https://mermaid.live/>)

## Contributing

When making changes to the arlogi codebase:

1. Update the relevant code-level documentation
2. Review and update component documentation if needed
3. Check if container or context documentation needs updates
4. Ensure all diagrams remain accurate

## Additional Resources

- **[Documentation Index](../index.md)** - Project overview and getting started guide
- **[API Reference](../API_REFERENCE.md)** - Complete API documentation
- **[Developer Guide](../DEVELOPER_GUIDE.md)** - Contribution guidelines
- **[Configuration Guide](../CONFIGURATION_GUIDE.md)** - Configuration options
- **[Live Documentation](http://192.168.168.5/cpaiops/)** - Deployed documentation site

## License

This documentation is part of the arlogi project and follows the same license terms.

---

**Documentation Version**: 1.0
**Last Updated**: 2025-12-28
**C4 Model Version**: Based on <https://c4model.com/>
