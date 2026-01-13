# Tools/tests/README.md
# tc3tools Test Suite

This directory contains comprehensive tests for the tc3tools CLI and its underlying modules.

## Directory Structure

```
tests/
├── __init__.py              # Test package marker
├── conftest.py              # Pytest fixtures and configuration
├── README.md                # This file
├── fixtures/                # Test fixture files
│   ├── st/                  # Structured Text source files
│   │   ├── FB_SimpleBlock.st
│   │   ├── FB_WithMethods.st
│   │   ├── FB_WithProperties.st
│   │   ├── FB_EdgeCases.st
│   │   ├── PRG_Main.st
│   │   ├── FC_Calculate.st
│   │   ├── E_Status.st
│   │   ├── ST_Data.st
│   │   ├── GVL_Constants.st
│   │   └── I_Device.st
│   └── xml/                 # TcPOU/TcDUT/TcGVL/TcIO XML files
│       ├── FB_SimpleBlock.TcPOU
│       ├── FB_WithMethods.TcPOU
│       ├── E_Status.TcDUT
│       ├── ST_Data.TcDUT
│       ├── GVL_Constants.TcGVL
│       └── I_Device.TcIO
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_st_formatter.py
│   ├── test_st_to_tcpou_converter.py
│   ├── test_tcpou_to_st_converter.py
│   ├── test_tcpou_formatter.py
│   └── test_beckhoff_common.py
├── integration/             # Integration tests
│   ├── __init__.py
│   ├── test_st_to_xml.py
│   ├── test_xml_to_st.py
│   └── test_roundtrip.py
└── e2e/                     # End-to-end tests
    ├── __init__.py
    └── test_tc3tools_cli.py
```

## Test Categories

### Unit Tests (`tests/unit/`)
Test individual functions and classes in isolation:
- `test_st_formatter.py` - ST code formatting rules
- `test_st_to_tcpou_converter.py` - ST to XML conversion logic
- `test_tcpou_to_st_converter.py` - XML to ST conversion logic
- `test_tcpou_formatter.py` - XML file formatting
- `test_beckhoff_common.py` - Shared utility functions

### Integration Tests (`tests/integration/`)
Test interactions between modules:
- `test_st_to_xml.py` - Full ST to XML conversion pipeline
- `test_xml_to_st.py` - Full XML to ST conversion pipeline
- `test_roundtrip.py` - Round-trip conversion verification

### End-to-End Tests (`tests/e2e/`)
Test the CLI tool as a whole:
- `test_tc3tools_cli.py` - CLI commands, arguments, error handling

## Running Tests

### Run all tests
```bash
cd Tools
pytest
```

### Run tests by category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_st_formatter.py
```

### Run specific test
```bash
pytest tests/unit/test_st_formatter.py::TestSTFormatterIndentation::test_if_block_indentation
```

### Verbose output
```bash
pytest -v --tb=long
```

## Test Fixtures

### ST Fixtures (`fixtures/st/`)
Standalone Structured Text files covering:
- Basic function blocks with VAR_INPUT/OUTPUT
- Methods (PUBLIC/PRIVATE access modifiers)
- Properties (GET/SET accessors)
- Programs with FB instantiation
- Functions with return types
- Enums with attributes
- Structs with nested structures
- Global Variable Lists (GVL)
- Interfaces with methods and properties
- Edge cases (attributes, pragmas, EXTENDS, IMPLEMENTS)

### XML Fixtures (`fixtures/xml/`)
Corresponding TcPOU/TcDUT/TcGVL/TcIO files:
- Valid XML structure with CDATA sections
- Methods and properties in XML format
- DUTs (enums and structs)
- GVLs with CONSTANT/RETAIN sections
- Interface definitions

## Adding New Tests

1. **Unit tests**: Add to appropriate `tests/unit/test_*.py` file
2. **Integration tests**: Add to `tests/integration/` directory
3. **E2E tests**: Add to `tests/e2e/test_tc3tools_cli.py`
4. **New fixtures**: Add to `tests/fixtures/st/` or `tests/fixtures/xml/`

### Test Naming Convention
- Test classes: `TestFeatureName`
- Test methods: `test_specific_behavior`
- Use descriptive names that indicate what's being tested

### Markers
Use pytest markers to categorize tests:
```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_module_interaction():
    pass

@pytest.mark.e2e
def test_cli_command():
    pass
```

## CI/CD Integration

Tests are automatically run via GitHub Actions on:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Changes to files in `Tools/` directory

See `.github/workflows/tests.yml` for configuration.
