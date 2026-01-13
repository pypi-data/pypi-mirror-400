#!/usr/bin/env python3
"""
ST to TcPOU Converter.

Converts Structured Text (.st) files to TwinCAT POU XML format
(.TcPOU, .TcDUT, .TcIO, .TcGVL).

Handles PROGRAM, FUNCTION_BLOCK, FUNCTION, TYPE, INTERFACE, and GVL declarations
with method extraction.
"""

from __future__ import annotations

import re
import shutil
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import ClassVar

# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================


class FileType(Enum):
    """Supported TwinCAT file types."""

    PROGRAM = "PROGRAM"
    FUNCTION_BLOCK = "FUNCTION_BLOCK"
    FUNCTION = "FUNCTION"
    TYPE = "TYPE"
    GVL = "VAR_GLOBAL"
    INTERFACE = "INTERFACE"


@dataclass
class STMethod:
    """Represents a method extracted from an ST file."""

    name: str
    return_type: str
    declaration: str
    implementation: str
    access_specifier: str = ""


@dataclass
class STPropertyAccessor:
    """Represents a GET or SET accessor of a property."""

    declaration: str
    implementation: str


@dataclass
class STProperty:
    """Represents a property extracted from an ST file."""

    name: str
    return_type: str
    declaration: str
    get_accessor: STPropertyAccessor | None = None
    set_accessor: STPropertyAccessor | None = None
    access_specifier: str = ""


@dataclass
class ParsedContent:
    """Holds all parsed content from an ST file."""

    name: str
    file_type: FileType
    return_type: str
    declaration: str
    implementation: str
    methods: list[STMethod] = field(default_factory=list)
    properties: list[STProperty] = field(default_factory=list)


# =============================================================================
# TEXT UTILITIES
# =============================================================================


class TextUtils:
    """Utility class for text transformations."""

    @staticmethod
    def normalize_indentation(content: str) -> str:
        """Remove common leading indentation from all lines."""
        if not content:
            return content

        lines = content.split("\n")

        min_indent = float("inf")
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)

        if min_indent == float("inf") or min_indent == 0:
            return content

        return "\n".join(line[int(min_indent) :] if line.strip() else "" for line in lines)

    @staticmethod
    def strip_leading_block_comments(content: str) -> str:
        """Remove leading block comments (* ... *) from content."""
        content = content.strip()
        while content.startswith("(*"):
            end_comment = content.find("*)")
            if end_comment != -1:
                content = content[end_comment + 2 :].strip()
            else:
                break
        return content

    @staticmethod
    def strip_trailing_block_comments(content: str) -> str:
        """Remove trailing block comments (* ... *) from content."""
        content = content.rstrip()
        while content.endswith("*)"):
            start_comment = content.rfind("(*")
            if start_comment != -1:
                content = content[:start_comment].rstrip()
            else:
                break
        return content


# =============================================================================
# PARSER
# =============================================================================


class STParser:
    """Parses Structured Text content and extracts components."""

    PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "file_type": re.compile(
            r"^\s*(PROGRAM|FUNCTION_BLOCK|FUNCTION|TYPE|INTERFACE)\s+(?:ABSTRACT\s+)?(\w+)(?:\s*:\s*(\w+(?:\([^)]+\))?))?",
            re.MULTILINE,
        ),
        "var_global": re.compile(r"^\s*VAR_GLOBAL", re.MULTILINE),
        "method": re.compile(
            r"((?:\{[^}]+\}\s*)*METHOD\s+(?:PRIVATE|PUBLIC|PROTECTED|INTERNAL)?\s*(?:ABSTRACT\s+)?(\w+)(?:\s*:\s*(\w+(?:\([^)]+\))?))?.*?END_METHOD)",
            re.DOTALL,
        ),
        "method_header": re.compile(
            r"^((?:\{[^}]+\}\s*)*)METHOD\s+(PRIVATE|PUBLIC|PROTECTED|INTERNAL)?\s*(?:ABSTRACT\s+)?(\w+)(?:\s*:\s*(\w+(?:\([^)]+\))?))?",
            re.MULTILINE,
        ),
        "property": re.compile(
            r"(PROPERTY\s+(?:PRIVATE|PUBLIC|PROTECTED|INTERNAL)?\s*(\w+)\s*:\s*(\w+(?:\([^)]+\))?).*?END_PROPERTY)",
            re.DOTALL,
        ),
        "property_header": re.compile(
            r"^PROPERTY\s+(PRIVATE|PUBLIC|PROTECTED|INTERNAL)?\s*(\w+)\s*:\s*(\w+(?:\([^)]+\))?)",
            re.MULTILINE,
        ),
        "property_get": re.compile(r"(GET\s.*?END_GET)", re.DOTALL),
        "property_set": re.compile(r"(SET\s.*?END_SET)", re.DOTALL),
        "end_get": re.compile(r"END_GET", re.IGNORECASE),
        "end_set": re.compile(r"END_SET", re.IGNORECASE),
        "end_var": re.compile(r"END_VAR", re.IGNORECASE),
        "end_method": re.compile(r"END_METHOD", re.IGNORECASE),
        "end_program": re.compile(r"END_PROGRAM", re.IGNORECASE),
        "end_function_block": re.compile(r"END_FUNCTION_BLOCK", re.IGNORECASE),
        "end_function": re.compile(r"END_FUNCTION", re.IGNORECASE),
        "end_interface": re.compile(r"END_INTERFACE", re.IGNORECASE),
    }

    def parse(self, content: str, filename_hint: str = "") -> ParsedContent:
        """Parse ST content and return structured data."""
        file_type, name, return_type = self._detect_file_type(content, filename_hint)

        if file_type == FileType.GVL:
            return self._parse_gvl(content, name)
        elif file_type == FileType.TYPE:
            return self._parse_type(content, name)
        elif file_type == FileType.INTERFACE:
            return self._parse_interface(content, name)
        else:
            return self._parse_pou(content, name, file_type, return_type)

    def _detect_file_type(self, content: str, filename_hint: str = "") -> tuple[FileType, str, str]:
        """Detect file type and extract name."""
        match = self.PATTERNS["file_type"].search(content)
        if match:
            type_str = match.group(1)
            name = match.group(2)
            return_type = match.group(3) or ""
            file_type = FileType[type_str.upper().replace(" ", "_")]
            return file_type, name, return_type

        if self.PATTERNS["var_global"].search(content):
            name = self._extract_gvl_name(filename_hint)
            return FileType.GVL, name, ""

        raise ValueError("Could not detect file type from content")

    def _extract_gvl_name(self, filename_hint: str) -> str:
        """Extract GVL name from filename."""
        if filename_hint:
            if filename_hint.startswith("GVL_"):
                return filename_hint
            return f"GVL_{filename_hint}"
        return "GVL_Unnamed"

    def _parse_gvl(self, content: str, name: str) -> ParsedContent:
        """Parse GVL content."""
        return ParsedContent(
            name=name,
            file_type=FileType.GVL,
            return_type="",
            declaration=content.strip(),
            implementation="",
        )

    def _parse_type(self, content: str, name: str) -> ParsedContent:
        """Parse TYPE (DUT) content."""
        return ParsedContent(
            name=name,
            file_type=FileType.TYPE,
            return_type="",
            declaration=content.strip(),
            implementation="",
        )

    def _parse_interface(self, content: str, name: str) -> ParsedContent:
        """Parse INTERFACE content."""
        methods = self._extract_interface_methods(content)
        declaration = self._extract_interface_declaration(content)

        return ParsedContent(
            name=name,
            file_type=FileType.INTERFACE,
            return_type="",
            declaration=declaration,
            implementation="",
            methods=methods,
        )

    def _extract_interface_declaration(self, content: str) -> str:
        """Extract interface declaration (before first method)."""
        method_match = re.search(r"\bMETHOD\b", content)
        if method_match:
            return content[: method_match.start()].strip()

        end_match = self.PATTERNS["end_interface"].search(content)
        if end_match:
            return content[: end_match.start()].strip()

        return content.strip()

    def _extract_interface_methods(self, content: str) -> list[STMethod]:
        """Extract method signatures from interface."""
        methods = []
        pattern = re.compile(r"(METHOD\s+(\w+)(?:\s*:\s*(\w+))?.*?END_METHOD)", re.DOTALL)

        for match in pattern.finditer(content):
            full_method = match.group(1)
            method_name = match.group(2)
            return_type = match.group(3) or ""

            var_matches = list(self.PATTERNS["end_var"].finditer(full_method))
            if var_matches:
                declaration = full_method[: var_matches[-1].end()].strip()
            else:
                lines = full_method.split("\n")
                declaration = lines[0].strip()

            methods.append(
                STMethod(
                    name=method_name,
                    return_type=return_type,
                    declaration=declaration,
                    implementation="",
                )
            )

        return methods

    def _parse_pou(
        self, content: str, name: str, file_type: FileType, return_type: str
    ) -> ParsedContent:
        """Parse PROGRAM, FUNCTION_BLOCK, or FUNCTION."""
        methods = self._extract_methods(content)
        properties = self._extract_properties(content)
        declaration = self._extract_declaration(content)
        implementation = self._extract_implementation(content, file_type)

        return ParsedContent(
            name=name,
            file_type=file_type,
            return_type=return_type,
            declaration=declaration,
            implementation=implementation,
            methods=methods,
            properties=properties,
        )

    def _extract_methods(self, content: str) -> list[STMethod]:
        """Extract all methods from content."""
        methods = []

        for match in self.PATTERNS["method"].finditer(content):
            full_method = match.group(1)
            method_name = match.group(2)
            return_type = match.group(3) or ""

            header_match = self.PATTERNS["method_header"].search(full_method)
            access_specifier = (
                header_match.group(2) if header_match and header_match.group(2) else ""
            )

            declaration, implementation = self._split_method_content(full_method)

            methods.append(
                STMethod(
                    name=method_name,
                    return_type=return_type,
                    declaration=declaration,
                    implementation=implementation,
                    access_specifier=access_specifier,
                )
            )

        return methods

    def _extract_properties(self, content: str) -> list[STProperty]:
        """Extract all properties from content."""
        properties = []

        for match in self.PATTERNS["property"].finditer(content):
            full_property = match.group(1)
            prop_name = match.group(2)
            return_type = match.group(3) or ""

            header_match = self.PATTERNS["property_header"].search(full_property)
            access_specifier = (
                header_match.group(1) if header_match and header_match.group(1) else ""
            )

            declaration = (
                f"PROPERTY {access_specifier + ' ' if access_specifier else ''}"
                f"{prop_name} : {return_type}".strip()
            )

            get_accessor = None
            get_match = self.PATTERNS["property_get"].search(full_property)
            if get_match:
                get_accessor = self._parse_accessor(get_match.group(1), "get")

            set_accessor = None
            set_match = self.PATTERNS["property_set"].search(full_property)
            if set_match:
                set_accessor = self._parse_accessor(set_match.group(1), "set")

            properties.append(
                STProperty(
                    name=prop_name,
                    return_type=return_type,
                    declaration=declaration,
                    get_accessor=get_accessor,
                    set_accessor=set_accessor,
                    access_specifier=access_specifier,
                )
            )

        return properties

    def _parse_accessor(self, accessor_content: str, accessor_type: str) -> STPropertyAccessor:
        """Parse a GET or SET accessor into declaration and implementation."""
        var_matches = list(self.PATTERNS["end_var"].finditer(accessor_content))

        if accessor_type == "get":
            end_pattern = self.PATTERNS["end_get"]
        else:
            end_pattern = self.PATTERNS["end_set"]

        var_start_match = re.search(r"\bVAR\b", accessor_content)

        if not var_matches:
            end_match = end_pattern.search(accessor_content)
            if end_match:
                lines = accessor_content[: end_match.start()].strip().split("\n")
                impl_lines = lines[1:] if len(lines) > 1 else []
                implementation = "\n".join(impl_lines)
                return STPropertyAccessor(
                    declaration="",
                    implementation=TextUtils.normalize_indentation(implementation).strip(),
                )
            return STPropertyAccessor(declaration="", implementation="")

        if var_start_match:
            last_end_var = var_matches[-1]
            declaration = accessor_content[var_start_match.start() : last_end_var.end()].strip()
        else:
            declaration = ""

        last_end_var = var_matches[-1]
        end_match = end_pattern.search(accessor_content, last_end_var.end())
        if end_match:
            implementation = accessor_content[last_end_var.end() : end_match.start()]
        else:
            implementation = accessor_content[last_end_var.end() :]

        implementation = TextUtils.normalize_indentation(implementation).strip()
        return STPropertyAccessor(declaration=declaration, implementation=implementation)

    def _split_method_content(self, method_content: str) -> tuple[str, str]:
        """Split method into declaration and implementation."""
        var_matches = list(self.PATTERNS["end_var"].finditer(method_content))

        if not var_matches:
            end_method_match = self.PATTERNS["end_method"].search(method_content)
            if end_method_match:
                content_before_end = method_content[: end_method_match.start()].strip()
                lines = content_before_end.split("\n")

                declaration_lines = []
                implementation_lines = []
                found_method = False

                for line in lines:
                    stripped = line.strip()
                    if not found_method:
                        declaration_lines.append(line)
                        if stripped.upper().startswith("METHOD ") or "METHOD " in stripped.upper():
                            found_method = True
                    else:
                        implementation_lines.append(line)

                declaration = "\n".join(declaration_lines).strip()
                implementation = "\n".join(implementation_lines)
                return declaration, TextUtils.normalize_indentation(implementation).strip()
            return method_content.strip(), ""

        last_end_var = var_matches[-1]
        declaration = method_content[: last_end_var.end()].strip()

        end_method_match = self.PATTERNS["end_method"].search(method_content, last_end_var.end())
        if end_method_match:
            implementation = method_content[last_end_var.end() : end_method_match.start()]
        else:
            implementation = method_content[last_end_var.end() :]

        implementation = TextUtils.normalize_indentation(implementation)
        return declaration, implementation.strip()

    def _extract_declaration(self, content: str) -> str:
        """Extract declaration part."""
        method_match = self.PATTERNS["method"].search(content)
        property_match = self.PATTERNS["property"].search(content)

        first_member_pos = len(content)
        if method_match:
            first_member_pos = min(first_member_pos, method_match.start())
        if property_match:
            first_member_pos = min(first_member_pos, property_match.start())

        search_content = content[:first_member_pos] if first_member_pos < len(content) else content

        var_matches = list(self.PATTERNS["end_var"].finditer(search_content))
        if var_matches:
            return content[: var_matches[-1].end()].strip()

        if first_member_pos < len(content):
            declaration = content[:first_member_pos]
            declaration = TextUtils.strip_trailing_block_comments(declaration)
            return (
                declaration.strip() if declaration.strip() else self._extract_header_line(content)
            )

        return self._extract_header_line(content)

    def _extract_header_line(self, content: str) -> str:
        """Extract the header line."""
        match = self.PATTERNS["file_type"].search(content)
        if match:
            return content[: match.end()].strip()
        return content.strip().split("\n")[0] if content.strip() else ""

    def _extract_implementation(self, content: str, file_type: FileType) -> str:
        """Extract main implementation body."""
        method_matches = list(self.PATTERNS["method"].finditer(content))
        property_matches = list(self.PATTERNS["property"].finditer(content))

        first_method_pos = method_matches[0].start() if method_matches else len(content)
        first_property_pos = property_matches[0].start() if property_matches else len(content)
        first_member_pos = min(first_method_pos, first_property_pos)

        pre_member_content = content[:first_member_pos]
        var_matches = list(self.PATTERNS["end_var"].finditer(pre_member_content))

        end_pattern = self._get_end_pattern(file_type)
        end_match = end_pattern.search(content)
        end_pos = end_match.start() if end_match else len(content)

        implementation_parts = []

        if var_matches:
            last_end_var = var_matches[-1]
            boundary = min(first_member_pos, end_pos)
            impl = content[last_end_var.end() : boundary].strip()
            impl = TextUtils.strip_leading_block_comments(impl)
            if impl:
                implementation_parts.append(impl)

        all_members = method_matches + property_matches
        if all_members:
            last_member_end = max(m.end() for m in all_members)
            post_member_impl = content[last_member_end:end_pos].strip()
            if post_member_impl:
                implementation_parts.append(post_member_impl)

        return "\n\n".join(implementation_parts)

    def _get_end_pattern(self, file_type: FileType) -> re.Pattern[str]:
        """Get END_xxx pattern for file type."""
        patterns = {
            FileType.PROGRAM: self.PATTERNS["end_program"],
            FileType.FUNCTION_BLOCK: self.PATTERNS["end_function_block"],
            FileType.FUNCTION: self.PATTERNS["end_function"],
        }
        return patterns.get(
            file_type,
            re.compile(r"END_(PROGRAM|FUNCTION_BLOCK|FUNCTION)", re.IGNORECASE),
        )


# =============================================================================
# XML GENERATOR
# =============================================================================


class XMLGenerator:
    """Generates TwinCAT XML from parsed content."""

    def generate(self, parsed: ParsedContent) -> str:
        """Generate complete XML for parsed content."""
        generators = {
            FileType.GVL: self._generate_gvl_xml,
            FileType.TYPE: self._generate_dut_xml,
            FileType.INTERFACE: self._generate_itf_xml,
        }
        generator = generators.get(parsed.file_type, self._generate_pou_xml)
        return generator(parsed)

    def _generate_pou_xml(self, parsed: ParsedContent) -> str:
        """Generate TcPOU XML."""
        methods_xml = self._generate_methods_xml(parsed.methods)
        properties_xml = self._generate_properties_xml(parsed.properties)
        declaration = self._escape_xml(parsed.declaration)
        implementation = self._escape_xml(parsed.implementation)

        return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.12">
  <POU Name="{parsed.name}" Id="{{{uuid.uuid4()}}}" SpecialFunc="None">
    <Declaration><![CDATA[{declaration}]]></Declaration>
    <Implementation>
      <ST><![CDATA[{implementation}]]></ST>
    </Implementation>
{methods_xml}{properties_xml}  </POU>
</TcPlcObject>"""

    def _generate_methods_xml(self, methods: list[STMethod]) -> str:
        """Generate XML for methods."""
        if not methods:
            return ""

        parts = []
        for method in methods:
            declaration = self._escape_xml(method.declaration)
            implementation = self._escape_xml(method.implementation)

            parts.append(
                f"""    <Method Name="{method.name}" Id="{{{uuid.uuid4()}}}">
      <Declaration><![CDATA[{declaration}]]></Declaration>
      <Implementation>
        <ST><![CDATA[{implementation}]]></ST>
      </Implementation>
    </Method>
"""
            )
        return "".join(parts)

    def _generate_properties_xml(self, properties: list[STProperty]) -> str:
        """Generate XML for properties."""
        if not properties:
            return ""

        parts = []
        for prop in properties:
            declaration = self._escape_xml(prop.declaration)

            accessors_xml = ""

            if prop.get_accessor:
                get_decl = self._escape_xml(prop.get_accessor.declaration)
                get_impl = self._escape_xml(prop.get_accessor.implementation)
                accessors_xml += f"""      <Get Name="Get" Id="{{{uuid.uuid4()}}}">
        <Declaration><![CDATA[{get_decl}]]></Declaration>
        <Implementation>
          <ST><![CDATA[{get_impl}]]></ST>
        </Implementation>
      </Get>
"""

            if prop.set_accessor:
                set_decl = self._escape_xml(prop.set_accessor.declaration)
                set_impl = self._escape_xml(prop.set_accessor.implementation)
                accessors_xml += f"""      <Set Name="Set" Id="{{{uuid.uuid4()}}}">
        <Declaration><![CDATA[{set_decl}]]></Declaration>
        <Implementation>
          <ST><![CDATA[{set_impl}]]></ST>
        </Implementation>
      </Set>
"""

            parts.append(
                f"""    <Property Name="{prop.name}" Id="{{{uuid.uuid4()}}}">
      <Declaration><![CDATA[{declaration}]]></Declaration>
{accessors_xml}    </Property>
"""
            )
        return "".join(parts)

    def _generate_gvl_xml(self, parsed: ParsedContent) -> str:
        """Generate TcGVL XML."""
        declaration = self._escape_xml(parsed.declaration)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.12">
  <GVL Name="{parsed.name}" Id="{{{uuid.uuid4()}}}">
    <Declaration><![CDATA[{declaration}]]></Declaration>
  </GVL>
</TcPlcObject>"""

    def _generate_dut_xml(self, parsed: ParsedContent) -> str:
        """Generate TcDUT XML."""
        declaration = self._escape_xml(parsed.declaration)
        return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.12">
  <DUT Name="{parsed.name}" Id="{{{uuid.uuid4()}}}">
    <Declaration><![CDATA[{declaration}]]></Declaration>
  </DUT>
</TcPlcObject>"""

    def _generate_itf_xml(self, parsed: ParsedContent) -> str:
        """Generate TcIO XML for interfaces."""
        declaration = self._escape_xml(parsed.declaration)
        methods_xml = self._generate_interface_methods_xml(parsed.methods)

        return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.12">
  <Itf Name="{parsed.name}" Id="{{{uuid.uuid4()}}}">
    <Declaration><![CDATA[{declaration}]]></Declaration>
{methods_xml}  </Itf>
</TcPlcObject>"""

    def _generate_interface_methods_xml(self, methods: list[STMethod]) -> str:
        """Generate XML for interface methods (no implementation)."""
        if not methods:
            return ""

        parts = []
        for method in methods:
            declaration = self._escape_xml(method.declaration)
            parts.append(
                f"""    <Method Name="{method.name}" Id="{{{uuid.uuid4()}}}">
      <Declaration><![CDATA[{declaration}]]></Declaration>
    </Method>
"""
            )
        return "".join(parts)

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters in CDATA."""
        return text.replace("]]>", "]]]]><![CDATA[>")


# =============================================================================
# OUTPUT MANAGER
# =============================================================================


class OutputManager:
    """Manages output directory creation and cleaning."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def prepare(self) -> None:
        """Prepare output directory (clean if exists, create if not)."""
        if self.output_dir.exists():
            print(f"Cleaning output directory: {self.output_dir}")
            shutil.rmtree(self.output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory: {self.output_dir}")

    def get_output_path(
        self,
        input_path: Path,
        file_type: FileType,
        name: str,
        input_root: Path,
    ) -> Path:
        """Calculate output path maintaining directory structure."""
        extensions = {
            FileType.PROGRAM: ".TcPOU",
            FileType.FUNCTION_BLOCK: ".TcPOU",
            FileType.FUNCTION: ".TcPOU",
            FileType.TYPE: ".TcDUT",
            FileType.GVL: ".TcGVL",
            FileType.INTERFACE: ".TcIO",
        }
        extension = extensions.get(file_type, ".TcPOU")

        try:
            relative_path = input_path.parent.relative_to(input_root)
            output_subdir = self.output_dir / relative_path
        except ValueError:
            output_subdir = self.output_dir

        return output_subdir / f"{name}{extension}"

    def write_file(self, path: Path, content: str) -> None:
        """Write content to file, creating directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# =============================================================================
# FILE FILTER
# =============================================================================


class FileFilter:
    """Filters files to determine which should be processed."""

    EXCLUDE_PATTERNS: ClassVar[list[str]] = ["__pycache__", ".git", "node_modules", ".venv", "venv"]

    def __init__(self, exclude_patterns: list[str] | None = None) -> None:
        self.exclude_patterns = exclude_patterns or self.EXCLUDE_PATTERNS

    def get_st_files(self, directory: Path) -> list[Path]:
        """Get all .st files in directory that should be processed."""
        files = []
        for path in directory.rglob("*.st"):
            if self._should_process(path):
                files.append(path)
        return sorted(files)

    def _should_process(self, path: Path) -> bool:
        """Check if file should be processed."""
        path_str = str(path)
        return not any(pattern in path_str for pattern in self.exclude_patterns)


# =============================================================================
# CONVERTER
# =============================================================================


class STConverter:
    """Orchestrates the ST to TcPOU conversion process."""

    def __init__(self, ignore_folders: list[str] | None = None) -> None:
        self.parser = STParser()
        self.xml_generator = XMLGenerator()
        exclude_patterns = FileFilter.EXCLUDE_PATTERNS.copy()
        if ignore_folders:
            exclude_patterns.extend(ignore_folders)
        self.file_filter = FileFilter(exclude_patterns)

    def convert(self, input_path: str, output_path: str) -> bool:
        """Convert ST files to TcPOU format."""
        input_dir = Path(input_path).resolve()
        output_dir = Path(output_path).resolve()

        if not input_dir.exists():
            print(f"Error: Input path does not exist: {input_path}")
            return False

        output_manager = OutputManager(output_dir)
        output_manager.prepare()

        if input_dir.is_file():
            if input_dir.suffix.lower() != ".st":
                print(f"Error: Input file must be a .st file: {input_path}")
                return False
            files = [input_dir]
            input_root = input_dir.parent
        else:
            files = self.file_filter.get_st_files(input_dir)
            input_root = input_dir

        if not files:
            print(f"No .st files found in {input_path}")
            return True

        print(f"Found {len(files)} .st files to convert")
        print("-" * 50)

        success_count = 0
        error_count = 0

        for file_path in files:
            result = self._convert_file(file_path, input_root, output_manager)
            if result:
                success_count += 1
            else:
                error_count += 1

        print("-" * 50)
        print(f"Conversion complete: {success_count} succeeded, {error_count} failed")

        return error_count == 0

    def _convert_file(
        self,
        input_path: Path,
        input_root: Path,
        output_manager: OutputManager,
    ) -> bool:
        """Convert a single ST file."""
        try:
            content = input_path.read_text(encoding="utf-8")
            filename_hint = input_path.stem

            parsed = self.parser.parse(content, filename_hint)
            xml_content = self.xml_generator.generate(parsed)

            output_path = output_manager.get_output_path(
                input_path, parsed.file_type, parsed.name, input_root
            )
            output_manager.write_file(output_path, xml_content)

            relative_output = output_path.relative_to(output_manager.output_dir)
            print(f"[OK] {input_path.name} -> {relative_output}")
            return True

        except Exception as e:
            print(f"[FAIL] {input_path.name}: {e}")
            return False


__all__ = [
    "FileFilter",
    "FileType",
    "OutputManager",
    "ParsedContent",
    "STConverter",
    "STMethod",
    "STParser",
    "STProperty",
    "STPropertyAccessor",
    "TextUtils",
    "XMLGenerator",
]
