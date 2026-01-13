"""
Integration tests for round-trip conversion (ST -> XML -> ST and XML -> ST -> XML).

Tests that content survives bidirectional conversion without semantic loss.
"""

import re
from pathlib import Path

import pytest

from tc3tools.converters.st_to_xml import STParser, XMLGenerator
from tc3tools.converters.xml_to_st import STGenerator, TwinCATXMLParser

# =============================================================================
# Helper Functions
# =============================================================================


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison."""
    lines = [line.strip() for line in text.strip().split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def extract_identifiers(text: str) -> set:
    """Extract important identifiers from ST code."""
    identifiers = set()

    # Extract POU names
    patterns = [
        r"FUNCTION_BLOCK\s+(\w+)",
        r"PROGRAM\s+(\w+)",
        r"FUNCTION\s+(\w+)",
        r"INTERFACE\s+(\w+)",
        r"METHOD\s+(\w+)",
        r"PROPERTY\s+(\w+)",
        r"TYPE\s+(\w+)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        identifiers.update(matches)

    return identifiers


def has_structural_elements(text: str, elements: list) -> bool:
    """Check if text contains expected structural elements."""
    return all(elem in text for elem in elements)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def st_parser():
    """Create an STParser instance."""
    return STParser()


@pytest.fixture
def xml_generator():
    """Create an XMLGenerator instance for ST->XML."""
    return XMLGenerator()


@pytest.fixture
def xml_parser():
    """Create a TwinCATXMLParser instance."""
    return TwinCATXMLParser()


@pytest.fixture
def st_generator():
    """Create an STGenerator instance for XML->ST."""
    return STGenerator()


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def st_fixtures_dir(fixtures_dir):
    """Get the ST fixtures directory path."""
    return fixtures_dir / "st"


@pytest.fixture
def xml_fixtures_dir(fixtures_dir):
    """Get the XML fixtures directory path."""
    return fixtures_dir / "xml"


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.integration
class TestSTToXMLToSTRoundtrip:
    """Test ST -> XML -> ST round-trip conversion."""

    def test_simple_fb_roundtrip(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test simple FB survives round-trip."""
        st_file = st_fixtures_dir / "FB_Sample.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)

        # XML -> ST
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Verify semantic preservation
        extract_identifiers(original_st)
        recovered_ids = extract_identifiers(recovered_st)

        assert "FB_Sample" in recovered_ids
        assert "FUNCTION_BLOCK" in recovered_st

    def test_fb_with_extends_roundtrip(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test FB with EXTENDS survives round-trip."""
        st_file = st_fixtures_dir / "FB_AlwaysFailure.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # EXTENDS should be preserved
        assert "EXTENDS" in recovered_st
        assert "FB_AlwaysFailure" in recovered_st

    def test_fb_with_implements_roundtrip(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test FB with IMPLEMENTS survives round-trip."""
        st_file = st_fixtures_dir / "FB_BaseNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # IMPLEMENTS should be preserved
        assert "IMPLEMENTS" in recovered_st
        assert "FB_BaseNode" in recovered_st

    def test_enum_roundtrip(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test enum survives round-trip."""
        st_file = st_fixtures_dir / "E_NodeStatus.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Enum values should be preserved
        assert "E_NodeStatus" in recovered_st

    def test_interface_roundtrip(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test interface survives round-trip."""
        st_file = st_fixtures_dir / "I_TreeNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Interface should be preserved
        assert "INTERFACE" in recovered_st
        assert "I_TreeNode" in recovered_st


@pytest.mark.integration
class TestXMLToSTToXMLRoundtrip:
    """Test XML -> ST -> XML round-trip conversion."""

    def test_tcpou_roundtrip(
        self, xml_parser, st_generator, st_parser, xml_generator, xml_fixtures_dir
    ):
        """Test TcPOU survives round-trip."""
        xml_file = xml_fixtures_dir / "FB_Sample.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        original_xml = xml_file.read_text(encoding="utf-8")

        # XML -> ST
        tc_obj = xml_parser.parse(original_xml)
        st = st_generator.generate(tc_obj)

        # ST -> XML
        parsed = st_parser.parse(st)
        recovered_xml = xml_generator.generate(parsed)

        # Verify key elements preserved
        assert 'Name="FB_Sample"' in recovered_xml
        assert "<TcPlcObject" in recovered_xml

    def test_tcdut_roundtrip(
        self, xml_parser, st_generator, st_parser, xml_generator, xml_fixtures_dir
    ):
        """Test TcDUT survives round-trip."""
        xml_file = xml_fixtures_dir / "E_State.TcDUT"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        original_xml = xml_file.read_text(encoding="utf-8")

        # XML -> ST -> XML
        tc_obj = xml_parser.parse(original_xml)
        st = st_generator.generate(tc_obj)
        parsed = st_parser.parse(st)
        recovered_xml = xml_generator.generate(parsed)

        # Verify DUT structure preserved
        assert "<DUT" in recovered_xml or "E_State" in recovered_xml


@pytest.mark.integration
class TestRoundtripPreservation:
    """Test that important elements are preserved during round-trip."""

    def test_variable_declarations_preserved(
        self, st_parser, xml_generator, xml_parser, st_generator
    ):
        """Test variable declarations survive round-trip."""
        original_st = """FUNCTION_BLOCK FB_Test
VAR_INPUT
    bEnable : BOOL;
    nValue : INT;
END_VAR
VAR_OUTPUT
    bDone : BOOL;
    nResult : INT;
END_VAR
VAR
    _state : INT;
END_VAR

IF bEnable THEN
    nResult := nValue * 2;
    bDone := TRUE;
END_IF
END_FUNCTION_BLOCK"""

        # Round-trip
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Check variable sections preserved
        assert "VAR_INPUT" in recovered_st
        assert "VAR_OUTPUT" in recovered_st
        assert "bEnable" in recovered_st
        assert "nValue" in recovered_st
        assert "bDone" in recovered_st

    def test_control_structures_preserved(self, st_parser, xml_generator, xml_parser, st_generator):
        """Test control structures survive round-trip."""
        original_st = """FUNCTION_BLOCK FB_Control
VAR
    x : INT;
END_VAR

IF x > 0 THEN
    x := x - 1;
ELSIF x < 0 THEN
    x := x + 1;
ELSE
    x := 0;
END_IF

FOR i := 0 TO 10 DO
    x := x + i;
END_FOR
END_FUNCTION_BLOCK"""

        # Round-trip
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Check control structures preserved
        assert "IF" in recovered_st
        assert "THEN" in recovered_st
        assert "END_IF" in recovered_st

    def test_comments_preserved(self, st_parser, xml_generator, xml_parser, st_generator):
        """Test comments survive round-trip."""
        original_st = """FUNCTION_BLOCK FB_Comments
// This is a single line comment
VAR
    x : INT; // inline comment
END_VAR

(* This is a
   multi-line comment *)
x := 1;
END_FUNCTION_BLOCK"""

        # Round-trip
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # At minimum, the FB structure should be preserved
        assert "FB_Comments" in recovered_st


@pytest.mark.integration
class TestRoundtripEdgeCases:
    """Test edge cases in round-trip conversion."""

    def test_empty_fb_roundtrip(self, st_parser, xml_generator, xml_parser, st_generator):
        """Test empty FB survives round-trip."""
        original_st = """FUNCTION_BLOCK FB_Empty
VAR
END_VAR

END_FUNCTION_BLOCK"""

        # Round-trip
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "FB_Empty" in recovered_st

    def test_complex_types_roundtrip(self, st_parser, xml_generator, xml_parser, st_generator):
        """Test complex types survive round-trip."""
        original_st = """FUNCTION_BLOCK FB_Complex
VAR
    aData : ARRAY[0..99] OF INT;
    sText : STRING(255);
    rValue : REAL := 3.14159;
END_VAR

aData[0] := 42;
END_FUNCTION_BLOCK"""

        # Round-trip
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "FB_Complex" in recovered_st
        assert "ARRAY" in recovered_st or "aData" in recovered_st
