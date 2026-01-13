"""
TC3Tools - A CLI toolkit for TwinCAT/Beckhoff development workflows.

This package provides tools for:
- Formatting and linting Structured Text (.st) files
- Formatting TwinCAT XML (.TcPOU, .TcDUT, etc.) files
- Converting between Structured Text and TwinCAT XML formats
"""

from tc3tools.core.common import Diagnostic, LocalFileSystem, Severity

__version__ = "0.1.0"
__all__ = [
    "Diagnostic",
    "LocalFileSystem",
    "Severity",
    "__version__",
]
