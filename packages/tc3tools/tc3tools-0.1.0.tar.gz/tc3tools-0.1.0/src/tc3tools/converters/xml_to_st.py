#!/usr/bin/env python3
"""
TwinCAT XML to Structured Text Converter.

Refactored to follow SOLID principles:
- SRP: Separate responsibilities for Parsing, Generation, and File I/O.
- OCP: Open for extension (e.g., new generators or parsers) without modifying core logic.
- DIP: High-level orchestrator depends on abstractions (Interfaces).
"""

from __future__ import annotations

import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from tc3tools.core.common import IFileSystem

# =============================================================================
# DOMAIN ENTITIES
# =============================================================================


class TcFileType(Enum):
    """TwinCAT file types."""

    POU = "POU"
    DUT = "DUT"
    GVL = "GVL"
    INTERFACE = "Itf"
    UNKNOWN = "Unknown"


@dataclass
class TcMethod:
    """Represents a method in a TwinCAT POU."""

    name: str
    declaration: str
    implementation: str


@dataclass
class TcAccessor:
    """Represents a property accessor (GET/SET)."""

    declaration: str
    implementation: str


@dataclass
class TcProperty:
    """Represents a property in a TwinCAT POU."""

    name: str
    declaration: str
    getter: TcAccessor | None = None
    setter: TcAccessor | None = None


@dataclass
class TcObject:
    """Represents a parsed TwinCAT object."""

    name: str
    file_type: TcFileType
    declaration: str
    implementation: str
    methods: list[TcMethod] = field(default_factory=list)
    properties: list[TcProperty] = field(default_factory=list)


# =============================================================================
# INTERFACES (PROTOCOLS)
# =============================================================================


class IParser(Protocol):
    """Abstracts the parsing of source content into a domain object."""

    def parse(self, content: str, filename_hint: str = "") -> TcObject:
        """Parse content and return TcObject."""
        ...


class IGenerator(Protocol):
    """Abstracts the generation of output code from a domain object."""

    def generate(self, obj: TcObject) -> str:
        """Generate code from TcObject."""
        ...


# =============================================================================
# IMPLEMENTATIONS
# =============================================================================


class XmlUtils:
    """Helper for XML string manipulation."""

    @staticmethod
    def unescape_cdata(text: str | None) -> str:
        """Unescape CDATA content."""
        if not text:
            return ""
        return text.replace("]]]]><![CDATA[>", "]]>")


class TwinCATXMLParser:
    """Parses TwinCAT XML format into TcObject."""

    def parse(self, content: str, filename_hint: str = "") -> TcObject:
        """Parse TwinCAT XML content."""
        root = ET.fromstring(content)

        child = None
        for elem in root:
            if elem.tag:
                child = elem
                break

        if child is None:
            raise ValueError("No child element found in TcPlcObject")

        tag = child.tag
        name = child.attrib.get("Name") or child.attrib.get("Id") or filename_hint
        file_type = self._map_tag_to_type(tag)

        declaration = ""
        implementation = ""
        methods: list[TcMethod] = []
        properties: list[TcProperty] = []

        for sub in child:
            tag_lower = sub.tag.lower()

            if tag_lower == "declaration":
                declaration = XmlUtils.unescape_cdata(sub.text or "")

            elif tag_lower == "implementation":
                implementation = self._extract_implementation(sub)

            elif tag_lower == "method":
                methods.append(self._parse_method(sub))

            elif tag_lower == "property":
                properties.append(self._parse_property(sub))

        return TcObject(
            name=name,
            file_type=file_type,
            declaration=declaration,
            implementation=implementation,
            methods=methods,
            properties=properties,
        )

    def _map_tag_to_type(self, tag: str) -> TcFileType:
        """Map XML tag to file type."""
        tag_lower = tag.lower()
        if tag_lower == "pou":
            return TcFileType.POU
        if tag_lower == "dut":
            return TcFileType.DUT
        if tag_lower == "gvl":
            return TcFileType.GVL
        if tag_lower == "itf":
            return TcFileType.INTERFACE
        return TcFileType.UNKNOWN

    def _extract_implementation(self, element: ET.Element) -> str:
        """Extract implementation from element."""
        st = element.find("ST")
        if st is not None:
            return XmlUtils.unescape_cdata(st.text or "")
        return XmlUtils.unescape_cdata(element.text or "")

    def _parse_method(self, element: ET.Element) -> TcMethod:
        """Parse a method element."""
        name = element.attrib.get("Name", "Unknown")
        decl = ""
        impl = ""

        decl_el = element.find("Declaration")
        if decl_el is not None:
            decl = XmlUtils.unescape_cdata(decl_el.text or "")

        impl_el = element.find("Implementation")
        if impl_el is not None:
            st_el = impl_el.find("ST")
            if st_el is not None:
                impl = XmlUtils.unescape_cdata(st_el.text or "")

        return TcMethod(name, decl, impl)

    def _parse_property(self, element: ET.Element) -> TcProperty:
        """Parse a property element."""
        name = element.attrib.get("Name", "Unknown")
        decl = ""
        getter: TcAccessor | None = None
        setter: TcAccessor | None = None

        decl_el = element.find("Declaration")
        if decl_el is not None:
            decl = XmlUtils.unescape_cdata(decl_el.text or "")

        for acc in element:
            tag_lower = acc.tag.lower()
            if tag_lower == "get":
                getter = self._parse_accessor(acc)
            elif tag_lower == "set":
                setter = self._parse_accessor(acc)

        return TcProperty(name, decl, getter, setter)

    def _parse_accessor(self, element: ET.Element) -> TcAccessor:
        """Parse an accessor element (GET/SET)."""
        decl = ""
        impl = ""

        decl_sub = element.find("Declaration")
        if decl_sub is not None:
            decl = XmlUtils.unescape_cdata(decl_sub.text or "")

        impl_sub = element.find("Implementation")
        if impl_sub is not None:
            st = impl_sub.find("ST")
            if st is not None:
                impl = XmlUtils.unescape_cdata(st.text or "")

        return TcAccessor(decl, impl)


class STGenerator:
    """Generates Structured Text (.st) from TcObject."""

    def generate(self, obj: TcObject) -> str:
        """Generate ST code from TcObject."""
        parts = []

        header = self._derive_header(obj)
        if header:
            parts.append(header)

        if obj.declaration:
            parts.append(self._format_block(obj.declaration))

        if obj.implementation:
            impl_text = self._format_block(obj.implementation)
            if impl_text.strip():
                parts.append(impl_text)

        for method in obj.methods:
            parts.append(self._generate_method(method))

        for prop in obj.properties:
            parts.append(self._generate_property(prop))

        footer = self._derive_footer(obj)
        if footer:
            joined = "\n".join(parts).upper()
            if footer.upper() not in joined:
                parts.append(footer)

        return "\n\n".join(p.strip() for p in parts if p and p.strip()) + "\n"

    def _format_block(self, text: str, indent: str = "") -> str:
        """Format a text block with optional indentation."""
        dedented = textwrap.dedent(text).strip("\n")
        if indent:
            return textwrap.indent(dedented, indent)
        return dedented

    def _derive_header(self, obj: TcObject) -> str:
        """Derive header from object."""
        if obj.declaration:
            decl_upper = obj.declaration.upper()
            keywords = [
                "FUNCTION_BLOCK",
                "PROGRAM",
                "FUNCTION",
                "TYPE",
                "VAR_GLOBAL",
                "INTERFACE",
            ]
            if any(kw in decl_upper for kw in keywords):
                return ""

        if obj.file_type == TcFileType.POU:
            return f"FUNCTION_BLOCK {obj.name}"
        if obj.file_type == TcFileType.DUT:
            return f"TYPE {obj.name} : ( /* DUT */ )"
        if obj.file_type == TcFileType.GVL:
            return f"VAR_GLOBAL\n/* {obj.name} */\nEND_VAR"
        if obj.file_type == TcFileType.INTERFACE:
            return f"INTERFACE {obj.name}"
        return ""

    def _derive_footer(self, obj: TcObject) -> str:
        """Derive footer from object."""
        if obj.file_type == TcFileType.POU:
            return "END_FUNCTION_BLOCK"
        if obj.file_type == TcFileType.DUT:
            return "END_TYPE"
        if obj.file_type == TcFileType.INTERFACE:
            return "END_INTERFACE"
        return ""

    def _generate_method(self, method: TcMethod) -> str:
        """Generate method ST code."""
        parts = []
        if method.declaration:
            parts.append(self._format_block(method.declaration))
        else:
            parts.append(f"METHOD {method.name}")

        if method.implementation and method.implementation.strip():
            parts.append(self._format_block(method.implementation, indent="    "))

        if "END_METHOD" not in (method.declaration + method.implementation).upper():
            parts.append("END_METHOD")

        return "\n".join(parts)

    def _generate_property(self, prop: TcProperty) -> str:
        """Generate property ST code."""
        parts = []
        if prop.declaration:
            parts.append(self._format_block(prop.declaration))
        else:
            parts.append(f"PROPERTY {prop.name} : UNKNOWN")

        if prop.getter and (prop.getter.declaration or prop.getter.implementation):
            parts.append("GET")
            if prop.getter.declaration:
                parts.append(self._format_block(prop.getter.declaration))
            if prop.getter.implementation and prop.getter.implementation.strip():
                parts.append(self._format_block(prop.getter.implementation, indent="    "))
            if "END_GET" not in (prop.getter.declaration + prop.getter.implementation).upper():
                parts.append("END_GET")

        if prop.setter and (prop.setter.declaration or prop.setter.implementation):
            parts.append("SET")
            if prop.setter.declaration:
                parts.append(self._format_block(prop.setter.declaration))
            if prop.setter.implementation and prop.setter.implementation.strip():
                parts.append(self._format_block(prop.setter.implementation, indent="    "))
            if "END_SET" not in (prop.setter.declaration + prop.setter.implementation).upper():
                parts.append("END_SET")

        if "END_PROPERTY" not in prop.declaration.upper():
            parts.append("END_PROPERTY")

        return "\n".join(parts)


# =============================================================================
# SERVICE / ORCHESTRATOR
# =============================================================================


class ConverterService:
    """Orchestrates the conversion process."""

    def __init__(self, parser: IParser, generator: IGenerator, fs: IFileSystem) -> None:
        self.parser = parser
        self.generator = generator
        self.fs = fs

    def convert(self, input_root: Path, output_root: Path) -> int:
        """Convert TwinCAT XML files to ST."""
        extensions = [".TcPOU", ".TcDUT", ".TcGVL", ".TcTLEO", ".TcIO"]
        files = list(self.fs.collect_files(input_root, extensions))

        if not files:
            print(f"No TwinCAT files found under {input_root}")
            return 0

        effective_root = input_root.parent if input_root.is_file() else input_root

        success_count = 0
        for file_path in files:
            try:
                self._process_file(file_path, effective_root, output_root)
                success_count += 1
            except Exception as e:
                print(f"Failed to convert {file_path}: {e}")

        return success_count

    def _process_file(self, file_path: Path, input_root: Path, output_root: Path) -> None:
        """Process a single file."""
        content = self.fs.read_text(file_path)
        tc_object = self.parser.parse(content, filename_hint=file_path.stem)
        st_code = self.generator.generate(tc_object)

        try:
            rel_path = file_path.relative_to(input_root)
        except ValueError:
            rel_path = Path(file_path.name)

        out_path = output_root / rel_path.with_suffix(".st")
        self.fs.make_dirs(out_path)
        self.fs.write_text(out_path, st_code)
        print(f"Wrote {out_path}")


__all__ = [
    "ConverterService",
    "IGenerator",
    "IParser",
    "STGenerator",
    "TcAccessor",
    "TcFileType",
    "TcMethod",
    "TcObject",
    "TcProperty",
    "TwinCATXMLParser",
    "XmlUtils",
]
