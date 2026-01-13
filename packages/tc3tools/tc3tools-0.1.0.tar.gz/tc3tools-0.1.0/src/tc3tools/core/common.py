"""
Shared components for TC3Tools.

This module contains common types, interfaces, and utilities
used across the tc3tools package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

# =============================================================================
# DOMAIN ENTITIES
# =============================================================================


class Severity(Enum):
    """Severity levels for diagnostic messages."""

    ERROR = auto()
    WARNING = auto()
    INFO = auto()


@dataclass
class Diagnostic:
    """Represents a diagnostic message from syntax checking or formatting."""

    line_number: int
    column: int
    message: str
    severity: Severity
    rule_id: str
    line_content: str = ""

    def __str__(self) -> str:
        """Return human-readable diagnostic string."""
        return f"[{self.severity.name}] Line {self.line_number}: {self.message} ({self.rule_id})"


# =============================================================================
# INTERFACES
# =============================================================================


class IFileSystem(Protocol):
    """Interface for file system operations.

    This protocol defines the contract for file system access,
    enabling dependency injection and testing with mock implementations.
    """

    def collect_files(self, root: Path, extensions: list[str]) -> Iterator[Path]:
        """Collect files matching the given extensions under root."""
        ...

    def read_text(self, path: Path) -> str:
        """Read text content from a file."""
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file."""
        ...

    def make_dirs(self, path: Path) -> None:
        """Create directories for the given path."""
        ...


# =============================================================================
# IMPLEMENTATIONS
# =============================================================================


class LocalFileSystem:
    """Local file system implementation of IFileSystem."""

    def collect_files(self, root: Path, extensions: list[str]) -> Iterator[Path]:
        """Collect files matching extensions under root directory.

        Args:
            root: Starting directory or file path
            extensions: List of file extensions to match (e.g., ['.st', '.TcPOU'])

        Yields:
            Paths to matching files
        """
        if root.is_file():
            # Check if file matches any extension
            if any(root.name.endswith(ext) for ext in extensions):
                yield root
        else:
            for ext in extensions:
                # rglob pattern needs * prefix
                pattern = f"*{ext}" if not ext.startswith("*") else ext
                yield from root.rglob(pattern)

    def read_text(self, path: Path) -> str:
        """Read text content from a file with UTF-8 encoding."""
        return path.read_text(encoding="utf-8", errors="replace")

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file with UTF-8 encoding."""
        path.write_text(content, encoding="utf-8")

    def make_dirs(self, path: Path) -> None:
        """Create parent directories for the given path."""
        path.parent.mkdir(parents=True, exist_ok=True)
