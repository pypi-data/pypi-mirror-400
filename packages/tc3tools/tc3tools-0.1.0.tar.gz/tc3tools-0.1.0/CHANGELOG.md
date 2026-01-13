# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial public release
- `fmt-st` command for formatting and linting Structured Text files
- `fmt-xml` command for formatting TwinCAT XML files
- `st2xml` command for converting ST to TwinCAT XML
- `xml2st` command for converting TwinCAT XML to ST
- Support for PROGRAM, FUNCTION_BLOCK, FUNCTION, TYPE, INTERFACE, and GVL
- Method and property extraction with GET/SET accessors
- Syntax checking rules:
  - F001: Filename must match declared entity name
  - B001: Block matching (IF/END_IF, etc.)
- Formatting rules:
  - Consistent 4-space indentation
  - Block opener/closer alignment
  - Parenthesis-based indentation for enums

### Changed

- Restructured project to use `src/` layout
- Migrated from flat module structure to packages (core, converters, formatters)
- Consolidated all tool configuration into `pyproject.toml`

### Developer Experience

- Added type hints throughout codebase
- Added `py.typed` marker for PEP 561 compliance
- Set up Ruff for linting and formatting
- Set up mypy for type checking
- Added pre-commit hooks
- Added GitHub Actions CI/CD
- Added comprehensive test suite (unit, integration, e2e)

## [0.1.0] - 2024-XX-XX

### Added

- First release on PyPI
