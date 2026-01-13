# tc3tools

[![PyPI - Version](https://img.shields.io/pypi/v/tc3tools.svg)](https://pypi.org/project/tc3tools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tc3tools.svg)](https://pypi.org/project/tc3tools)
[![CI](https://github.com/BhanuKiranChaluvadi/tctool/actions/workflows/ci.yml/badge.svg)](https://github.com/BhanuKiranChaluvadi/tctool/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/BhanuKiranChaluvadi/tctool/branch/main/graph/badge.svg)](https://codecov.io/gh/BhanuKiranChaluvadi/tctool)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A CLI toolkit for **TwinCAT/Beckhoff** development workflows. Format, lint, and convert Structured Text (ST) and TwinCAT XML files.

## Features

- 🎨 **Format ST files** - Consistent indentation and code style for Structured Text
- ✅ **Lint ST files** - Check for syntax issues and naming conventions
- 📄 **Format XML files** - Normalize TwinCAT .TcPOU XML files
- 🔄 **Convert ST ↔ XML** - Bidirectional conversion between formats

## Installation

```bash
pip install tc3tools
```

For development:

```bash
pip install tc3tools[dev]
```

## Quick Start

### Format Structured Text Files

```bash
# Check formatting (dry-run)
tc3tools fmt-st --check --format .

# Format files in-place
tc3tools fmt-st --format --inplace .

# Format a single file
tc3tools fmt-st --format --inplace ./src/FB_Controller.st
```

### Lint Structured Text Files

```bash
# Check syntax and naming conventions
tc3tools fmt-st --check .
```

### Format TwinCAT XML Files

```bash
# Check XML formatting
tc3tools fmt-xml --check ./TcPOU/src

# Format XML files
tc3tools fmt-xml ./TcPOU/src
```

### Convert Between Formats

```bash
# Convert ST to TwinCAT XML
tc3tools st2xml ./src ./TcPOU/output

# Convert ST to XML, ignoring certain folders
tc3tools st2xml ./src ./TcPOU/output --ignore Tests Documentation

# Convert TwinCAT XML to ST
tc3tools xml2st ./TcPOU/src ./st_export
```

## Commands

| Command | Description |
|---------|-------------|
| `fmt-st` | Format and check Structured Text (.st) files |
| `fmt-xml` | Format TwinCAT XML (.TcPOU) files |
| `st2xml` | Convert Structured Text to TwinCAT XML |
| `xml2st` | Convert TwinCAT XML to Structured Text |

### Command Options

#### `fmt-st`

```
tc3tools fmt-st [OPTIONS] [INPUT]

Arguments:
  INPUT           Input file or directory (default: .)

Options:
  -c, --check     Check syntax only
  -f, --format    Format code
  -i, --inplace   Modify files in-place
```

#### `fmt-xml`

```
tc3tools fmt-xml [OPTIONS] [INPUT]

Arguments:
  INPUT           Input file or directory (default: .)

Options:
  -c, --check     Check only, do not write
```

#### `st2xml`

```
tc3tools st2xml [OPTIONS] [INPUT] [OUTPUT]

Arguments:
  INPUT           Input file or directory (default: .)
  OUTPUT          Output directory (default: tcpou_export)

Options:
  --ignore        Folders to ignore
```

#### `xml2st`

```
tc3tools xml2st [OPTIONS] [INPUT] [OUTPUT]

Arguments:
  INPUT           Input file or directory (default: .)
  OUTPUT          Output directory (default: st_export)
```

## Supported File Types

### Input Formats

| Extension | Description |
|-----------|-------------|
| `.st` | Structured Text source files |
| `.TcPOU` | TwinCAT POU (Program Organization Unit) |
| `.TcDUT` | TwinCAT DUT (Data Unit Type) |
| `.TcGVL` | TwinCAT GVL (Global Variable List) |
| `.TcIO` | TwinCAT Interface |

### Supported Constructs

- `PROGRAM`
- `FUNCTION_BLOCK` (including `ABSTRACT`)
- `FUNCTION`
- `TYPE` (STRUCT, ENUM)
- `INTERFACE`
- `VAR_GLOBAL` (GVL)
- Methods and Properties with GET/SET accessors

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/BhanuKiranChaluvadi/tctool.git
cd tc3tools

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tc3tools --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e
```

### Code Quality

```bash
# Lint and format check
ruff check .
ruff format --check .

# Type checking
mypy src/tc3tools

# Auto-fix issues
ruff check --fix .
ruff format .
```

## Project Structure

```
tc3tools/
├── src/tc3tools/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # CLI entry point
│   ├── py.typed            # PEP 561 marker
│   ├── core/
│   │   ├── __init__.py
│   │   └── common.py       # Shared interfaces and utilities
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── st_to_xml.py    # ST → TwinCAT XML
│   │   └── xml_to_st.py    # TwinCAT XML → ST
│   └── formatters/
│       ├── __init__.py
│       ├── st_formatter.py # ST formatting and linting
│       └── xml_formatter.py # XML formatting
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.
