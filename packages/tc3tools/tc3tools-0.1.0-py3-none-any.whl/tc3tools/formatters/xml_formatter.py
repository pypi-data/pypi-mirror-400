#!/usr/bin/env python3
"""
TwinCAT XML Formatter.

Formats TwinCAT .TcPOU XML files by normalizing indentation in CDATA sections
and formatting XML structure.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from xml.dom import minidom

if TYPE_CHECKING:
    from xml.dom.minidom import Node


class TcPOUFormatter:
    """Formats TwinCAT .TcPOU XML files."""

    def _strip_whitespace_text_nodes(self, node: Node) -> None:
        """Remove whitespace-only TEXT_NODEs to avoid prettyxml blank-line spam."""
        for child in list(node.childNodes):
            if child.nodeType == child.TEXT_NODE and (
                child.data is None or child.data.strip() == ""
            ):
                node.removeChild(child)  # type: ignore[misc]
                child.unlink()
            elif child.hasChildNodes():
                self._strip_whitespace_text_nodes(child)

    def normalize_cdata(self, text: str) -> str:
        """Normalize indentation in CDATA content (StructuredText code)."""
        lines = text.split("\n")
        if len(lines) <= 1:
            return text  # Single line or empty - nothing to normalize

        # First line starts right after <![CDATA[ so it has no leading whitespace.
        # Calculate min indent from lines 2+ only.
        non_empty_subsequent = [line for line in lines[1:] if line.strip()]
        if not non_empty_subsequent:
            return text  # Only first line has content

        # Find minimum indentation of subsequent non-empty lines
        min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_subsequent)

        if min_indent == 0:
            return text  # Already normalized

        # Remove the common indentation from lines 2+
        normalized = [lines[0]]  # Keep first line as-is
        for line in lines[1:]:
            if line.strip():  # Non-empty line
                normalized.append(line[min_indent:] if len(line) >= min_indent else line.lstrip())
            else:  # Empty line
                normalized.append("")

        return "\n".join(normalized)

    def format_file(self, file_path: Path, *, check_only: bool = False) -> tuple[bool, str]:
        """Format a single .TcPOU XML file."""
        try:
            # Read as bytes to let the XML parser respect the declared encoding
            content = file_path.read_bytes()

            # Parse XML
            dom = minidom.parseString(content)

            # CDATA_SECTION_NODE type constant
            CDATA_SECTION_NODE = 4

            # Normalize all CDATA sections in ST elements
            for node in dom.getElementsByTagName("ST"):
                if node.firstChild and node.firstChild.nodeType == CDATA_SECTION_NODE:
                    cdata = node.firstChild.data  # type: ignore[union-attr]
                    node.firstChild.data = self.normalize_cdata(cdata)  # type: ignore[union-attr]
                elif not node.firstChild:
                    # Ensure empty ST elements have an empty CDATA section
                    cdata_node = dom.createCDATASection("")
                    node.appendChild(cdata_node)

            # Normalize all CDATA sections in Declaration elements
            for node in dom.getElementsByTagName("Declaration"):
                if node.firstChild and node.firstChild.nodeType == CDATA_SECTION_NODE:
                    cdata = node.firstChild.data  # type: ignore[union-attr]
                    node.firstChild.data = self.normalize_cdata(cdata)  # type: ignore[union-attr]
                elif not node.firstChild:
                    # Ensure empty Declaration elements have an empty CDATA section
                    cdata_node = dom.createCDATASection("")
                    node.appendChild(cdata_node)

            # Remove whitespace-only text nodes for stable pretty printing
            self._strip_whitespace_text_nodes(dom)

            # Format XML with proper indentation
            formatted = dom.toprettyxml(indent="  ", newl="\n", encoding="utf-8")

            # Remove extra blank lines and clean up
            formatted_str = formatted.decode("utf-8")
            # Collapse blank lines created by prettyxml
            formatted_str = re.sub(r"\n{3,}", "\n\n", formatted_str)
            # Remove trailing whitespace
            formatted_str = "\n".join(line.rstrip() for line in formatted_str.split("\n"))

            if check_only:
                original_str = content.decode("utf-8", errors="replace")
                if original_str != formatted_str:
                    return True, "Would format"
                return True, "Already formatted"

            file_path.write_text(formatted_str, encoding="utf-8", newline="\n")

            return True, "Formatted"

        except Exception as e:
            return False, str(e)

    def process(self, target: Path, check: bool) -> int:
        """Process target path for formatting."""
        workspace_root = Path.cwd().resolve()

        if target.is_file():
            tcpou_files = [target.resolve()]
        else:
            tcpou_dir = target.resolve()
            tcpou_files = [p.resolve() for p in tcpou_dir.rglob("*.TcPOU")]

        if not tcpou_files:
            print(f"No .TcPOU files found under {target}")
            return 0

        mode = "CHECK" if check else "FORMAT"
        print(f"Mode: {mode}")
        print(f"Found {len(tcpou_files)} .TcPOU files")
        print("=" * 60)

        success_count = 0
        error_count = 0
        would_change_count = 0

        for file_path in sorted(tcpou_files):
            try:
                relative_path = file_path.relative_to(workspace_root)
            except ValueError:
                relative_path = file_path

            success, message = self.format_file(file_path, check_only=check)

            if success:
                if check and message == "Would format":
                    print(f"[X] {relative_path} (needs formatting)")
                    would_change_count += 1
                else:
                    print(f"[OK] {relative_path}")
                success_count += 1
            else:
                print(f"[ERROR] {relative_path}: {message}")
                error_count += 1

        print("=" * 60)

        if check:
            print(
                f"Summary: {success_count} checked, {would_change_count} need formatting, {error_count} errors"
            )
            if would_change_count > 0 or error_count > 0:
                return 1
            else:
                return 0
        else:
            print(f"Summary: {success_count} formatted, {error_count} errors")
            return 1 if error_count > 0 else 0


__all__ = ["TcPOUFormatter"]
