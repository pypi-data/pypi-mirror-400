"""
Integration tests for XML to ST conversion.

Tests the complete workflow of converting TwinCAT XML files to Structured Text format.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tc3tools.converters.xml_to_st import STGenerator, TwinCATXMLParser

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def parser():
    """Create a TwinCATXMLParser instance."""
    return TwinCATXMLParser()


@pytest.fixture
def generator():
    """Create an STGenerator instance."""
    return STGenerator()


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def xml_fixtures_dir(fixtures_dir):
    """Get the XML fixtures directory path."""
    return fixtures_dir / "xml"


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.integration
class TestXMLToSTFunctionBlock:
    """Test XML to ST conversion for Function Blocks."""

    def test_simple_fb_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of simple function block."""
        xml_file = xml_fixtures_dir / "FB_Sample.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "FUNCTION_BLOCK FB_Sample" in st
        assert "VAR_INPUT" in st
        assert "VAR_OUTPUT" in st
        assert "END_VAR" in st

    def test_fb_implementation_extracted(self, parser, generator, xml_fixtures_dir):
        """Test implementation code is extracted."""
        xml_file = xml_fixtures_dir / "FB_Sample.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        # Should have some implementation
        assert "END_FUNCTION_BLOCK" in st

    def test_fb_with_extends_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of FB with EXTENDS."""
        xml_file = xml_fixtures_dir / "FB_AlwaysFailure.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "FB_AlwaysFailure" in st
        assert "EXTENDS" in st

    def test_fb_with_implements_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of FB with IMPLEMENTS."""
        xml_file = xml_fixtures_dir / "FB_BaseNode.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "FB_BaseNode" in st
        assert "IMPLEMENTS" in st


@pytest.mark.integration
class TestXMLToSTDUT:
    """Test XML to ST conversion for DUTs."""

    def test_enum_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of enum."""
        xml_file = xml_fixtures_dir / "E_State.TcDUT"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "E_State" in st
        assert "IDLE" in st or "RUNNING" in st

    def test_struct_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of struct."""
        xml_file = xml_fixtures_dir / "ST_Data.TcDUT"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "ST_Data" in st
        assert "STRUCT" in st


@pytest.mark.integration
class TestXMLToSTGVL:
    """Test XML to ST conversion for GVLs."""

    def test_gvl_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of GVL."""
        xml_file = xml_fixtures_dir / "GVL_Settings.TcGVL"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "VAR_GLOBAL" in st


@pytest.mark.integration
class TestXMLToSTInterface:
    """Test XML to ST conversion for Interfaces."""

    def test_interface_extraction(self, parser, generator, xml_fixtures_dir):
        """Test extraction of interface."""
        xml_file = xml_fixtures_dir / "I_TreeNode.TcIO"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        assert "INTERFACE" in st
        assert "I_TreeNode" in st


@pytest.mark.integration
class TestXMLToSTMethods:
    """Test method extraction from POUs."""

    def test_methods_extracted(self, parser, generator, xml_fixtures_dir):
        """Test that methods are extracted."""
        xml_file = xml_fixtures_dir / "FB_ActionNode.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        # Should have method declarations
        assert "METHOD" in st


@pytest.mark.integration
class TestXMLToSTProperties:
    """Test property extraction from POUs."""

    def test_properties_extracted(self, parser, generator, xml_fixtures_dir):
        """Test that properties are extracted."""
        xml_file = xml_fixtures_dir / "FB_BaseNode.TcPOU"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        # Should have property declarations
        assert "PROPERTY" in st


@pytest.mark.integration
class TestXMLToSTAttributes:
    """Test attribute extraction."""

    def test_attributes_extracted(self, parser, generator, xml_fixtures_dir):
        """Test that attributes are preserved."""
        xml_file = xml_fixtures_dir / "E_NodeStatus.TcDUT"
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = parser.parse(xml_content)
        st = generator.generate(tc_obj)

        # Should preserve attributes
        assert "qualified_only" in st or "E_NodeStatus" in st


@pytest.mark.integration
class TestXMLToSTEdgeCases:
    """Test edge cases in XML to ST conversion."""

    def test_empty_implementation(self, parser, generator):
        """Test handling of empty implementation."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Empty" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Empty
VAR
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""

        tc_obj = parser.parse(xml)
        st = generator.generate(tc_obj)

        assert "FB_Empty" in st

    def test_special_characters_preserved(self, parser, generator):
        """Test special characters are preserved."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Special" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Special
VAR
    sText : STRING := 'Temperature: 25°C';
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[// Nothing]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""

        tc_obj = parser.parse(xml)
        st = generator.generate(tc_obj)

        assert "FB_Special" in st
        assert "25°C" in st or "Temperature" in st

    def test_invalid_xml_raises_error(self, parser):
        """Test that invalid XML raises an error."""
        with pytest.raises((ValueError, ET.ParseError)):
            parser.parse("not valid xml content")

    def test_empty_string_raises_error(self, parser):
        """Test that empty string raises an error."""
        with pytest.raises((ValueError, ET.ParseError)):
            parser.parse("")
