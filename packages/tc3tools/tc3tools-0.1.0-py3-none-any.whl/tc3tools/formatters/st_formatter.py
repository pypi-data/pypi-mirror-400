#!/usr/bin/env python3
"""
Structured Text (ST) Formatter and Syntax Checker.

Refactored to follow SOLID principles:
- SRP: Separate responsibilities for Checking, Formatting, and File I/O.
- OCP: Open for extension (new rules, new formatters).
- DIP: High-level orchestrator depends on abstractions.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from tc3tools.core.common import Diagnostic, IFileSystem, Severity

# =============================================================================
# DOMAIN ENTITIES
# =============================================================================


@dataclass
class CheckResult:
    """Result of syntax checking."""

    is_valid: bool
    diagnostics: list[Diagnostic] = field(default_factory=list)


class CheckContext:
    """Context information for syntax checking."""

    def __init__(self, filename: str) -> None:
        self.filename = filename


# =============================================================================
# INTERFACES
# =============================================================================


class ISyntaxRule(ABC):
    """Interface for syntax checking rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Return unique rule identifier."""
        ...

    @abstractmethod
    def check(self, lines: list[str], context: CheckContext) -> list[Diagnostic]:
        """Check lines and return diagnostics."""
        ...


class ISyntaxChecker(Protocol):
    """Interface for syntax checker."""

    def check(self, content: str, filename: str) -> CheckResult:
        """Check content and return result."""
        ...


class IFormatter(Protocol):
    """Interface for code formatter."""

    def format(self, content: str) -> str:
        """Format content and return formatted string."""
        ...


# =============================================================================
# IMPLEMENTATIONS: UTILS
# =============================================================================


class TextUtils:
    """Utility class for text manipulation."""

    @staticmethod
    def remove_comments_and_strings(line: str) -> str:
        """Remove comments and string literals for analysis."""
        # Remove strings
        clean = re.sub(r"'[^']*'", "''", line)
        clean = re.sub(r'"[^"]*"', '""', clean)
        # Remove single line comments
        clean = re.sub(r"//.*$", "", clean)
        # Remove multi-line comments (simple approximation for single line)
        clean = re.sub(r"\(\*.*?\*\)", "", clean)
        return clean.strip()

    @staticmethod
    def get_clean_lines(lines: list[str]) -> list[str]:
        """Get lines with comments/strings removed, handling multi-line comments."""
        result = []
        in_comment = False
        for line in lines:
            clean = line
            if in_comment:
                if "*)" in clean:
                    clean = clean.split("*)", 1)[1]
                    in_comment = False
                else:
                    result.append("")
                    continue

            clean = re.sub(r"//.*$", "", clean)
            clean = re.sub(r"'[^']*'", "''", clean)
            clean = re.sub(r'"[^"]*"', '""', clean)

            while "(*" in clean:
                start = clean.find("(*")
                end = clean.find("*)", start)
                if end != -1:
                    clean = clean[:start] + clean[end + 2 :]
                else:
                    clean = clean[:start]
                    in_comment = True
                    break
            result.append(clean.strip())
        return result


# =============================================================================
# IMPLEMENTATIONS: SYNTAX RULES
# =============================================================================


class FileNameMatchRule(ISyntaxRule):
    """Rule to check if filename matches declared entity name."""

    @property
    def rule_id(self) -> str:
        return "F001"

    def check(self, lines: list[str], context: CheckContext) -> list[Diagnostic]:
        filename = Path(context.filename).stem
        if filename.startswith("GVL_"):
            return []

        clean_lines = TextUtils.get_clean_lines(lines)
        patterns = [
            r"^\s*PROGRAM\s+(\w+)",
            r"^\s*FUNCTION_BLOCK\s+(?:ABSTRACT\s+|FINAL\s+)?(\w+)",
            r"^\s*FUNCTION\s+(\w+)",
            r"^\s*INTERFACE\s+(\w+)",
            r"^\s*TYPE\s+(\w+)",
        ]

        for i, line in enumerate(clean_lines):
            for pat in patterns:
                match = re.match(pat, line, re.IGNORECASE)
                if match:
                    name = match.group(1)
                    if name != filename:
                        return [
                            Diagnostic(
                                i + 1,
                                1,
                                f"File '{filename}' matches '{name}'",
                                Severity.ERROR,
                                self.rule_id,
                            )
                        ]
                    return []
        return []


class BlockMatchingRule(ISyntaxRule):
    """Rule to check for matching block open/close statements."""

    @property
    def rule_id(self) -> str:
        return "B001"

    def check(self, lines: list[str], context: CheckContext) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        stack: list[tuple[str, int]] = []
        clean_lines = TextUtils.get_clean_lines(lines)

        # Simplified block tracking
        opens = {
            "PROGRAM": "END_PROGRAM",
            "FUNCTION_BLOCK": "END_FUNCTION_BLOCK",
            "FUNCTION": "END_FUNCTION",
            "METHOD": "END_METHOD",
            "PROPERTY": "END_PROPERTY",
            "ACTION": "END_ACTION",
            "VAR": "END_VAR",
            "VAR_INPUT": "END_VAR",
            "VAR_OUTPUT": "END_VAR",
            "VAR_IN_OUT": "END_VAR",
            "VAR_GLOBAL": "END_VAR",
            "VAR_TEMP": "END_VAR",
            "VAR_STAT": "END_VAR",
            "VAR_CONFIG": "END_VAR",
            "IF": "END_IF",
            "CASE": "END_CASE",
            "FOR": "END_FOR",
            "WHILE": "END_WHILE",
            "REPEAT": "END_REPEAT",
            "STRUCT": "END_STRUCT",
            "TYPE": "END_TYPE",
            "INTERFACE": "END_INTERFACE",
        }

        # Reverse map for END_VAR
        var_blocks = {k for k, v in opens.items() if v == "END_VAR"}

        for i, line in enumerate(clean_lines):
            if not line:
                continue

            # Check for Opens
            for k in opens:
                if re.search(rf"\b{k}\b", line, re.IGNORECASE):
                    closer = opens[k]
                    if re.search(rf"\b{closer}\b", line, re.IGNORECASE):
                        continue

                    if k == "PROPERTY" and any(s[0] == "INTERFACE" for s in stack):
                        continue

                    stack.append((k, i + 1))
                    break

            # Check for Closes
            for _k, v in opens.items():
                closer = v
                if re.search(rf"\b{closer}\b", line, re.IGNORECASE):
                    if stack:
                        top, _ = stack[-1]
                        expected = opens.get(top)
                        if closer == expected or (closer == "END_VAR" and top in var_blocks):
                            stack.pop()
                    break

        return diagnostics


# =============================================================================
# IMPLEMENTATIONS: CHECKER & FORMATTER
# =============================================================================


class STSyntaxChecker:
    """Syntax checker for Structured Text files."""

    def __init__(self) -> None:
        self.rules: list[ISyntaxRule] = [FileNameMatchRule(), BlockMatchingRule()]

    def check(self, content: str, filename: str) -> CheckResult:
        """Check content for syntax issues."""
        lines = content.splitlines()
        context = CheckContext(filename)
        diags: list[Diagnostic] = []
        for rule in self.rules:
            diags.extend(rule.check(lines, context))
        return CheckResult(len([d for d in diags if d.severity == Severity.ERROR]) == 0, diags)


# =============================================================================
# FORMATTING RULES (SOLID: OCP, SRP)
# =============================================================================


@dataclass
class IndentResult:
    """Result of indent calculation."""

    current_delta: int = 0
    next_delta: int = 0


class IFormattingRule(ABC):
    """Interface for formatting rules."""

    @abstractmethod
    def apply(self, clean_line: str) -> IndentResult:
        """Apply rule and return indent changes."""
        ...


class StandardOpenerRule(IFormattingRule):
    """Rule for standard block openers."""

    def __init__(self) -> None:
        self.openers = {
            "PROGRAM",
            "FUNCTION_BLOCK",
            "FUNCTION",
            "METHOD",
            "PROPERTY",
            "ACTION",
            "INTERFACE",
            "VAR",
            "VAR_INPUT",
            "VAR_OUTPUT",
            "VAR_IN_OUT",
            "VAR_GLOBAL",
            "VAR_TEMP",
            "VAR_STAT",
            "VAR_CONFIG",
            "TYPE",
            "STRUCT",
            "CASE",
            "FOR",
            "WHILE",
            "REPEAT",
        }

    def apply(self, clean_line: str) -> IndentResult:
        # IF is handled separately
        if re.match(r"^IF\b", clean_line):
            return IndentResult()

        for o in self.openers:
            if re.match(rf"^{o}\b", clean_line):
                if o == "PROPERTY" and "INTERFACE" in clean_line:
                    return IndentResult()
                return IndentResult(next_delta=1)
        return IndentResult()


class StandardCloserRule(IFormattingRule):
    """Rule for standard block closers."""

    def __init__(self) -> None:
        self.closers = {
            "END_PROGRAM",
            "END_FUNCTION_BLOCK",
            "END_FUNCTION",
            "END_METHOD",
            "END_PROPERTY",
            "END_ACTION",
            "END_INTERFACE",
            "END_VAR",
            "END_IF",
            "END_CASE",
            "END_FOR",
            "END_WHILE",
            "END_REPEAT",
            "END_STRUCT",
            "END_TYPE",
            "UNTIL",
        }

    def apply(self, clean_line: str) -> IndentResult:
        for c in self.closers:
            if re.match(rf"^{c}\b", clean_line):
                return IndentResult(current_delta=-1, next_delta=-1)
        return IndentResult()


class MiddleBlockRule(IFormattingRule):
    """Rule for middle block statements (ELSE, ELSIF)."""

    def __init__(self) -> None:
        self.middles = {"ELSE", "ELSIF"}

    def apply(self, clean_line: str) -> IndentResult:
        for m in self.middles:
            if re.match(rf"^{m}\b", clean_line):
                return IndentResult(current_delta=-1)
        return IndentResult()


class IfBlockRule(IFormattingRule):
    """Rule for IF blocks."""

    def apply(self, clean_line: str) -> IndentResult:
        if re.match(r"^IF\b", clean_line) and "THEN" in clean_line and "END_IF" not in clean_line:
            return IndentResult(next_delta=1)
        return IndentResult()


class StructRule(IFormattingRule):
    """Rule for STRUCT blocks."""

    def apply(self, clean_line: str) -> IndentResult:
        if re.match(r"^STRUCT\b", clean_line):
            return IndentResult(current_delta=-1, next_delta=-1)
        return IndentResult()


class ParenthesisRule(IFormattingRule):
    """Rule for parenthesis-based indentation."""

    def apply(self, clean_line: str) -> IndentResult:
        res = IndentResult()

        if clean_line.endswith("(") and not clean_line.startswith("("):
            res.next_delta += 1

        if clean_line.startswith(")"):
            res.current_delta -= 1
            res.next_delta -= 1

        if clean_line.startswith("("):
            res.current_delta -= 1

        return res


class STFormatter:
    """Formatter for Structured Text files.

    Note: Multi-line CASE label blocks (where label and body are on separate lines)
    may not format ideally. Single-line case labels like "1: DoSomething();" work correctly.
    """

    INDENT_STR = "    "

    def __init__(self) -> None:
        self.rules: list[IFormattingRule] = [
            StandardCloserRule(),
            MiddleBlockRule(),
            StandardOpenerRule(),
            IfBlockRule(),
            StructRule(),
            ParenthesisRule(),
        ]

    def format(self, content: str) -> str:
        """Format Structured Text content."""
        lines = content.splitlines()
        formatted_lines: list[str] = []
        current_indent = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue

            clean = TextUtils.remove_comments_and_strings(stripped).upper()

            current_delta = 0
            next_delta = 0

            for rule in self.rules:
                res = rule.apply(clean)
                current_delta += res.current_delta
                next_delta += res.next_delta

            print_indent = max(0, current_indent + current_delta)
            formatted_lines.append((self.INDENT_STR * print_indent) + stripped)
            current_indent = max(0, current_indent + next_delta)

        return "\n".join(formatted_lines)


# =============================================================================
# SERVICE
# =============================================================================


class STToolService:
    """Service for processing Structured Text files."""

    def __init__(self, fs: IFileSystem, checker: ISyntaxChecker, formatter: IFormatter) -> None:
        self.fs = fs
        self.checker = checker
        self.formatter = formatter

    def process(self, path: Path, check: bool, format_code: bool, inplace: bool) -> int:
        """Process ST files for checking and/or formatting."""
        files = list(self.fs.collect_files(path, [".st"]))
        if not files:
            print(f"No .st files found in {path}")
            return 0

        exit_code = 0
        formatted_count = 0
        unchanged_count = 0

        for file_path in files:
            content = self.fs.read_text(file_path)

            if check:
                result = self.checker.check(content, file_path.name)
                self._print_diagnostics(result.diagnostics, str(file_path))
                if not result.is_valid:
                    exit_code = 1

            if format_code:
                formatted = self.formatter.format(content)
                needs_formatting = formatted != content

                if inplace:
                    if needs_formatting:
                        self.fs.write_text(file_path, formatted)
                        print(f"Formatted: {file_path}")
                        formatted_count += 1
                    else:
                        unchanged_count += 1
                else:
                    if len(files) == 1:
                        print(formatted)
                    else:
                        if needs_formatting:
                            print(f"[NEEDS FORMAT] {file_path}")
                            formatted_count += 1
                        else:
                            unchanged_count += 1

        if format_code and len(files) > 1:
            if inplace:
                print(f"\nSummary: {formatted_count} formatted, {unchanged_count} unchanged")
            else:
                print(
                    f"\nSummary: {formatted_count} need formatting, {unchanged_count} already formatted"
                )
                if formatted_count > 0:
                    print("Run with --inplace to apply changes")
                    exit_code = 1

        return exit_code

    def _print_diagnostics(self, diagnostics: list[Diagnostic], filename: str) -> None:
        if not diagnostics:
            return
        print(f"Diagnostics for {filename}:")
        for d in diagnostics:
            print(f"  {d}")


# Re-export for backward compatibility
__all__ = [
    "CheckContext",
    "CheckResult",
    "IFormatter",
    "IFormattingRule",
    "ISyntaxChecker",
    "ISyntaxRule",
    "IndentResult",
    "STFormatter",
    "STSyntaxChecker",
    "STToolService",
    "TextUtils",
]
