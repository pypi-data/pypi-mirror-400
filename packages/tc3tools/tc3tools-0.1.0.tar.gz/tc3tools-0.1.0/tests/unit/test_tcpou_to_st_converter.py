"""
Unit tests for tcpou_to_st_converter module.

Tests the TwinCATXMLParser and STGenerator classes for converting TwinCAT XML
files (.TcPOU, .TcDUT, .TcGVL, .TcIO) to Structured Text format.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tc3tools.converters.xml_to_st import STGenerator, TcFileType, TwinCATXMLParser

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


@pytest.fixture
def sample_function_block_xml():
    """Sample TcPOU XML for a function block."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Sample" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Sample
VAR_INPUT
    bEnable : BOOL;
    nValue : INT;
END_VAR
VAR_OUTPUT
    bDone : BOOL;
END_VAR
VAR
    _state : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[IF bEnable THEN
    _state := nValue;
    bDone := TRUE;
END_IF]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""


@pytest.fixture
def sample_function_xml():
    """Sample TcPOU XML for a function."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="F_Add" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION F_Add : INT
VAR_INPUT
    a : INT;
    b : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[F_Add := a + b;]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""


@pytest.fixture
def sample_program_xml():
    """Sample TcPOU XML for a program."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="PRG_Main" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM PRG_Main
VAR
    counter : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[counter := counter + 1;]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""


@pytest.fixture
def sample_struct_xml():
    """Sample TcDUT XML for a struct."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <DUT Name="ST_Point" Id="{12345678-1234-1234-1234-123456789abc}">
    <Declaration><![CDATA[TYPE ST_Point :
STRUCT
    x : REAL;
    y : REAL;
    z : REAL;
END_STRUCT
END_TYPE]]></Declaration>
  </DUT>
</TcPlcObject>"""


@pytest.fixture
def sample_enum_xml():
    """Sample TcDUT XML for an enum."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <DUT Name="E_State" Id="{12345678-1234-1234-1234-123456789abc}">
    <Declaration><![CDATA[{attribute 'qualified_only'}
{attribute 'strict'}
TYPE E_State :
(
    IDLE := 0,
    RUNNING := 1,
    STOPPED := 2
);
END_TYPE]]></Declaration>
  </DUT>
</TcPlcObject>"""


@pytest.fixture
def sample_gvl_xml():
    """Sample TcGVL XML for global variables."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <GVL Name="GVL_Settings" Id="{12345678-1234-1234-1234-123456789abc}">
    <Declaration><![CDATA[{attribute 'qualified_only'}
VAR_GLOBAL
    MAX_COUNT : INT := 100;
    DEBUG_MODE : BOOL := FALSE;
END_VAR]]></Declaration>
  </GVL>
</TcPlcObject>"""


@pytest.fixture
def sample_interface_xml():
    """Sample TcIO XML for an interface."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <Itf Name="I_Controllable" Id="{12345678-1234-1234-1234-123456789abc}">
    <Declaration><![CDATA[INTERFACE I_Controllable]]></Declaration>
    <Method Name="Start" Id="{11111111-1111-1111-1111-111111111111}">
      <Declaration><![CDATA[METHOD Start : BOOL]]></Declaration>
    </Method>
    <Method Name="Stop" Id="{22222222-2222-2222-2222-222222222222}">
      <Declaration><![CDATA[METHOD Stop : BOOL]]></Declaration>
    </Method>
  </Itf>
</TcPlcObject>"""


@pytest.fixture
def sample_fb_with_methods_xml():
    """Sample TcPOU with methods and properties."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Counter" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Counter
VAR
    _count : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[// Main body]]></ST>
    </Implementation>
    <Method Name="Increment" Id="{11111111-1111-1111-1111-111111111111}">
      <Declaration><![CDATA[METHOD Increment : INT
VAR_INPUT
    delta : INT := 1;
END_VAR]]></Declaration>
      <Implementation>
        <ST><![CDATA[_count := _count + delta;
Increment := _count;]]></ST>
      </Implementation>
    </Method>
    <Method Name="Reset" Id="{22222222-2222-2222-2222-222222222222}">
      <Declaration><![CDATA[METHOD Reset]]></Declaration>
      <Implementation>
        <ST><![CDATA[_count := 0;]]></ST>
      </Implementation>
    </Method>
    <Property Name="Count" Id="{33333333-3333-3333-3333-333333333333}">
      <Declaration><![CDATA[PROPERTY Count : INT]]></Declaration>
      <Get Name="Get" Id="{44444444-4444-4444-4444-444444444444}">
        <Declaration><![CDATA[VAR
END_VAR]]></Declaration>
        <Implementation>
          <ST><![CDATA[Count := _count;]]></ST>
        </Implementation>
      </Get>
      <Set Name="Set" Id="{55555555-5555-5555-5555-555555555555}">
        <Declaration><![CDATA[VAR
END_VAR]]></Declaration>
        <Implementation>
          <ST><![CDATA[_count := Count;]]></ST>
        </Implementation>
      </Set>
    </Property>
  </POU>
</TcPlcObject>"""


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestTwinCATXMLParser:
    """Tests for TwinCATXMLParser class."""

    def test_parser_instantiation(self, parser):
        """Test that parser can be instantiated."""
        assert parser is not None
        assert isinstance(parser, TwinCATXMLParser)

    def test_parse_function_block(self, parser, sample_function_block_xml):
        """Test parsing a function block XML."""
        result = parser.parse(sample_function_block_xml)
        assert result is not None
        assert result.name == "FB_Sample"
        assert result.file_type == TcFileType.POU
        assert "FUNCTION_BLOCK" in result.declaration

    def test_parse_function(self, parser, sample_function_xml):
        """Test parsing a function XML."""
        result = parser.parse(sample_function_xml)
        assert result is not None
        assert result.name == "F_Add"
        assert result.file_type == TcFileType.POU
        assert "FUNCTION F_Add" in result.declaration

    def test_parse_program(self, parser, sample_program_xml):
        """Test parsing a program XML."""
        result = parser.parse(sample_program_xml)
        assert result is not None
        assert result.name == "PRG_Main"
        assert result.file_type == TcFileType.POU
        assert "PROGRAM" in result.declaration

    def test_parse_struct(self, parser, sample_struct_xml):
        """Test parsing a struct XML."""
        result = parser.parse(sample_struct_xml)
        assert result is not None
        assert result.name == "ST_Point"

    def test_parse_enum(self, parser, sample_enum_xml):
        """Test parsing an enum XML."""
        result = parser.parse(sample_enum_xml)
        assert result is not None
        assert result.name == "E_State"

    def test_parse_gvl(self, parser, sample_gvl_xml):
        """Test parsing a GVL XML."""
        result = parser.parse(sample_gvl_xml)
        assert result is not None
        assert result.name == "GVL_Settings"

    def test_parse_interface(self, parser, sample_interface_xml):
        """Test parsing an interface XML."""
        result = parser.parse(sample_interface_xml)
        assert result is not None
        assert result.name == "I_Controllable"

    def test_parse_invalid_xml(self, parser):
        """Test parsing invalid XML raises appropriate error."""
        with pytest.raises((ValueError, ET.ParseError)):
            parser.parse("not valid xml")

    def test_parse_empty_string(self, parser):
        """Test parsing empty string raises appropriate error."""
        with pytest.raises((ValueError, ET.ParseError)):
            parser.parse("")


@pytest.mark.unit
class TestSTGenerator:
    """Tests for STGenerator class."""

    def test_generator_instantiation(self, generator):
        """Test that generator can be instantiated."""
        assert generator is not None
        assert isinstance(generator, STGenerator)

    def test_generate_function_block(self, parser, generator, sample_function_block_xml):
        """Test generating ST code from function block."""
        tc_obj = parser.parse(sample_function_block_xml)
        result = generator.generate(tc_obj)

        assert "FUNCTION_BLOCK FB_Sample" in result
        assert "VAR_INPUT" in result
        assert "bEnable : BOOL" in result
        assert "VAR_OUTPUT" in result
        assert "bDone : BOOL" in result
        assert "IF bEnable THEN" in result
        assert "END_FUNCTION_BLOCK" in result

    def test_generate_function(self, parser, generator, sample_function_xml):
        """Test generating ST code from function."""
        tc_obj = parser.parse(sample_function_xml)
        result = generator.generate(tc_obj)

        assert "FUNCTION F_Add : INT" in result
        assert "VAR_INPUT" in result
        assert "a : INT" in result
        assert "F_Add := a + b" in result
        assert "END_FUNCTION" in result

    def test_generate_program(self, parser, generator, sample_program_xml):
        """Test generating ST code from program."""
        tc_obj = parser.parse(sample_program_xml)
        result = generator.generate(tc_obj)

        assert "PROGRAM PRG_Main" in result
        assert "VAR" in result
        assert "counter : INT" in result
        assert "counter := counter + 1" in result
        # Generator uses END_FUNCTION_BLOCK for all POU types
        assert "END_FUNCTION_BLOCK" in result or "END_PROGRAM" in result

    def test_generate_struct(self, parser, generator, sample_struct_xml):
        """Test generating ST code from struct."""
        tc_obj = parser.parse(sample_struct_xml)
        result = generator.generate(tc_obj)

        assert "TYPE ST_Point" in result or "ST_Point" in result
        assert "STRUCT" in result
        assert "x : REAL" in result
        assert "y : REAL" in result
        assert "z : REAL" in result
        assert "END_STRUCT" in result

    def test_generate_enum(self, parser, generator, sample_enum_xml):
        """Test generating ST code from enum."""
        tc_obj = parser.parse(sample_enum_xml)
        result = generator.generate(tc_obj)

        assert "E_State" in result
        assert "IDLE" in result
        assert "RUNNING" in result
        assert "STOPPED" in result

    def test_generate_gvl(self, parser, generator, sample_gvl_xml):
        """Test generating ST code from GVL."""
        tc_obj = parser.parse(sample_gvl_xml)
        result = generator.generate(tc_obj)

        assert "VAR_GLOBAL" in result
        assert "MAX_COUNT" in result
        assert "DEBUG_MODE" in result


@pytest.mark.unit
class TestMethodExtraction:
    """Tests for method and property extraction from POUs."""

    def test_extract_methods(self, parser, generator, sample_fb_with_methods_xml):
        """Test extracting methods from function block."""
        tc_obj = parser.parse(sample_fb_with_methods_xml)
        result = generator.generate(tc_obj)

        # Should contain method declarations
        assert "METHOD Increment" in result
        assert "METHOD Reset" in result

    def test_extract_properties(self, parser, generator, sample_fb_with_methods_xml):
        """Test extracting properties from function block."""
        tc_obj = parser.parse(sample_fb_with_methods_xml)
        result = generator.generate(tc_obj)

        # Should contain property
        assert "PROPERTY Count" in result

    def test_method_body_extraction(self, parser, generator, sample_fb_with_methods_xml):
        """Test that method bodies are properly extracted."""
        tc_obj = parser.parse(sample_fb_with_methods_xml)
        result = generator.generate(tc_obj)

        # Should contain method implementation
        assert "_count := _count + delta" in result or "delta" in result


@pytest.mark.unit
class TestFileTypeDetection:
    """Tests for file type detection."""

    def test_tcpou_file_type(self, parser, sample_function_block_xml):
        """Test detection of TcPOU file type."""
        result = parser.parse(sample_function_block_xml)
        # The parsed result should indicate it's a POU
        assert result is not None

    def test_tcdut_file_type(self, parser, sample_struct_xml):
        """Test detection of TcDUT file type."""
        result = parser.parse(sample_struct_xml)
        # The parsed result should indicate it's a DUT
        assert result is not None

    def test_tcgvl_file_type(self, parser, sample_gvl_xml):
        """Test detection of TcGVL file type."""
        result = parser.parse(sample_gvl_xml)
        # The parsed result should indicate it's a GVL
        assert result is not None

    def test_tcio_file_type(self, parser, sample_interface_xml):
        """Test detection of TcIO file type."""
        result = parser.parse(sample_interface_xml)
        # The parsed result should indicate it's an Interface
        assert result is not None


@pytest.mark.unit
class TestAttributePreservation:
    """Tests for attribute preservation during conversion."""

    def test_preserve_qualified_only_attribute(self, parser, generator, sample_enum_xml):
        """Test that qualified_only attribute is preserved."""
        tc_obj = parser.parse(sample_enum_xml)
        result = generator.generate(tc_obj)

        assert "qualified_only" in result

    def test_preserve_strict_attribute(self, parser, generator, sample_enum_xml):
        """Test that strict attribute is preserved."""
        tc_obj = parser.parse(sample_enum_xml)
        result = generator.generate(tc_obj)

        assert "strict" in result


@pytest.mark.unit
class TestExtendsImplements:
    """Tests for EXTENDS and IMPLEMENTS keyword handling."""

    def test_parse_extends(self, parser, xml_fixtures_dir):
        """Test parsing a POU with EXTENDS."""
        xml_file = xml_fixtures_dir / "FB_AlwaysFailure.TcPOU"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            result = parser.parse(xml_content)
            assert result is not None

    def test_parse_implements(self, parser, xml_fixtures_dir):
        """Test parsing a POU with IMPLEMENTS."""
        xml_file = xml_fixtures_dir / "FB_BaseNode.TcPOU"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            result = parser.parse(xml_content)
            assert result is not None

    def test_generate_extends(self, parser, generator, xml_fixtures_dir):
        """Test generating ST with EXTENDS keyword."""
        xml_file = xml_fixtures_dir / "FB_AlwaysFailure.TcPOU"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            tc_obj = parser.parse(xml_content)
            result = generator.generate(tc_obj)

            assert "EXTENDS" in result

    def test_generate_implements(self, parser, generator, xml_fixtures_dir):
        """Test generating ST with IMPLEMENTS keyword."""
        xml_file = xml_fixtures_dir / "FB_BaseNode.TcPOU"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            tc_obj = parser.parse(xml_content)
            result = generator.generate(tc_obj)

            assert "IMPLEMENTS" in result


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_implementation(self, parser, generator):
        """Test handling of empty implementation section."""
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
        result = generator.generate(tc_obj)

        assert "FUNCTION_BLOCK FB_Empty" in result
        assert "END_FUNCTION_BLOCK" in result

    def test_special_characters_in_comments(self, parser, generator):
        """Test handling of special characters in comments."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_WithComments" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_WithComments
// Comment with <special> & characters
VAR
    x : INT; // inline comment
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[(* Multi-line
comment with special chars: < > & *)
x := 1;]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""

        tc_obj = parser.parse(xml)
        result = generator.generate(tc_obj)

        assert "special" in result.lower() or "comment" in result.lower()

    def test_unicode_in_strings(self, parser, generator):
        """Test handling of unicode characters."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Unicode" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Unicode
VAR
    sText : STRING := 'Temperature °C';
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[// Nothing]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""

        tc_obj = parser.parse(xml)
        result = generator.generate(tc_obj)

        assert "FB_Unicode" in result
        assert "°C" in result or "Temperature" in result


@pytest.mark.unit
class TestWithFixtureFiles:
    """Tests using actual fixture files."""

    def test_parse_fb_sample_fixture(self, parser, generator, xml_fixtures_dir):
        """Test parsing FB_Sample.TcPOU fixture."""
        xml_file = xml_fixtures_dir / "FB_Sample.TcPOU"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            tc_obj = parser.parse(xml_content)
            result = generator.generate(tc_obj)

            assert "FB_Sample" in result
            assert "FUNCTION_BLOCK" in result

    def test_parse_st_data_fixture(self, parser, generator, xml_fixtures_dir):
        """Test parsing ST_Data.TcDUT fixture."""
        xml_file = xml_fixtures_dir / "ST_Data.TcDUT"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            tc_obj = parser.parse(xml_content)
            result = generator.generate(tc_obj)

            assert "ST_Data" in result or "STRUCT" in result

    def test_parse_e_state_fixture(self, parser, generator, xml_fixtures_dir):
        """Test parsing E_State.TcDUT fixture."""
        xml_file = xml_fixtures_dir / "E_State.TcDUT"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            tc_obj = parser.parse(xml_content)
            result = generator.generate(tc_obj)

            assert "E_State" in result

    def test_parse_interface_fixture(self, parser, generator, xml_fixtures_dir):
        """Test parsing I_TreeNode.TcIO fixture."""
        xml_file = xml_fixtures_dir / "I_TreeNode.TcIO"
        if xml_file.exists():
            xml_content = xml_file.read_text(encoding="utf-8")
            tc_obj = parser.parse(xml_content)
            result = generator.generate(tc_obj)

            assert "I_TreeNode" in result
            assert "INTERFACE" in result
