"""
Integration tests for ST to XML conversion.

Tests the complete workflow of converting Structured Text files to TwinCAT XML format.
"""

from pathlib import Path

import pytest

from tc3tools.converters.st_to_xml import STParser, XMLGenerator

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def parser():
    """Create an STParser instance."""
    return STParser()


@pytest.fixture
def generator():
    """Create an XMLGenerator instance."""
    return XMLGenerator()


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def st_fixtures_dir(fixtures_dir):
    """Get the ST fixtures directory path."""
    return fixtures_dir / "st"


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.integration
class TestSTToXMLFunctionBlock:
    """Test ST to XML conversion for Function Blocks."""

    def test_simple_fb_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of simple function block."""
        st_file = st_fixtures_dir / "FB_Sample.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert '<?xml version="1.0"' in xml
        assert "<TcPlcObject" in xml
        assert 'Name="FB_Sample"' in xml
        assert "<Declaration>" in xml
        assert "<Implementation>" in xml
        assert "</TcPlcObject>" in xml

    def test_fb_with_extends_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of function block with EXTENDS."""
        st_file = st_fixtures_dir / "FB_AlwaysFailure.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="FB_AlwaysFailure"' in xml
        assert "EXTENDS" in xml

    def test_fb_with_implements_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of function block with IMPLEMENTS."""
        st_file = st_fixtures_dir / "FB_BaseNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="FB_BaseNode"' in xml
        assert "IMPLEMENTS" in xml


@pytest.mark.integration
class TestSTToXMLProgram:
    """Test ST to XML conversion for Programs."""

    def test_program_conversion(self, parser, generator):
        """Test conversion of program."""
        st_content = """PROGRAM PRG_Main
VAR
    counter : INT;
    bActive : BOOL;
END_VAR

counter := counter + 1;
IF counter > 100 THEN
    bActive := FALSE;
END_IF
END_PROGRAM"""

        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="PRG_Main"' in xml
        assert "PROGRAM" in xml
        assert "counter" in xml


@pytest.mark.integration
class TestSTToXMLFunction:
    """Test ST to XML conversion for Functions."""

    def test_function_conversion(self, parser, generator):
        """Test conversion of function."""
        st_content = """FUNCTION F_Add : INT
VAR_INPUT
    a : INT;
    b : INT;
END_VAR

F_Add := a + b;
END_FUNCTION"""

        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="F_Add"' in xml
        assert "FUNCTION F_Add" in xml


@pytest.mark.integration
class TestSTToXMLDUT:
    """Test ST to XML conversion for DUTs."""

    def test_enum_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of enum."""
        st_file = st_fixtures_dir / "E_NodeStatus.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="E_NodeStatus"' in xml
        assert "<DUT" in xml

    def test_struct_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of struct."""
        st_file = st_fixtures_dir / "ST_Data.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert "<DUT" in xml


@pytest.mark.integration
class TestSTToXMLInterface:
    """Test ST to XML conversion for Interfaces."""

    def test_interface_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of interface."""
        st_file = st_fixtures_dir / "I_TreeNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="I_TreeNode"' in xml
        assert "<Itf" in xml

    def test_interface_with_methods(self, parser, generator, st_fixtures_dir):
        """Test interface methods are converted."""
        st_file = st_fixtures_dir / "I_TreeNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        # Interface should have method elements
        assert "<Method" in xml or "METHOD" in xml


@pytest.mark.integration
class TestSTToXMLGVL:
    """Test ST to XML conversion for GVLs."""

    def test_gvl_conversion(self, parser, generator, st_fixtures_dir):
        """Test conversion of GVL."""
        st_file = st_fixtures_dir / "GVL_Constants.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert "<GVL" in xml
        assert "VAR_GLOBAL" in xml


@pytest.mark.integration
class TestSTToXMLMethods:
    """Test method conversion in POUs."""

    def test_fb_methods_converted(self, parser, generator, st_fixtures_dir):
        """Test that FB methods are properly converted."""
        st_file = st_fixtures_dir / "FB_ActionNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        # Should have Method elements
        assert "FB_ActionNode" in xml
        assert "<Method" in xml or "METHOD" in xml


@pytest.mark.integration
class TestSTToXMLProperties:
    """Test property conversion in POUs."""

    def test_fb_properties_converted(self, parser, generator, st_fixtures_dir):
        """Test that FB properties are properly converted."""
        st_file = st_fixtures_dir / "FB_BaseNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        # Should have Property elements
        assert "<Property" in xml or "PROPERTY" in xml


@pytest.mark.integration
class TestSTToXMLAttributes:
    """Test attribute preservation during conversion."""

    def test_pragma_preserved(self, parser, generator):
        """Test that pragmas are preserved."""
        st_content = """{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_Test :
(
    VALUE_A := 0,
    VALUE_B := 1
);
END_TYPE"""

        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert "qualified_only" in xml
        assert "strict" in xml


@pytest.mark.integration
class TestSTToXMLEdgeCases:
    """Test edge cases in ST to XML conversion."""

    def test_empty_implementation(self, parser, generator):
        """Test FB with empty implementation."""
        st_content = """FUNCTION_BLOCK FB_Empty
VAR
END_VAR

END_FUNCTION_BLOCK"""

        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert 'Name="FB_Empty"' in xml

    def test_special_characters_in_strings(self, parser, generator):
        """Test special characters in string literals."""
        st_content = """FUNCTION_BLOCK FB_Special
VAR
    sText : STRING := 'Temperature: 25°C';
END_VAR

END_FUNCTION_BLOCK"""

        parsed = parser.parse(st_content)
        xml = generator.generate(parsed)

        assert "FB_Special" in xml
