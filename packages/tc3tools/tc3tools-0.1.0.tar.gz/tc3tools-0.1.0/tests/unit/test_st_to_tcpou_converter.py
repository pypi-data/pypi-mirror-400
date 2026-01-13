# Tools/tests/unit/test_st_to_tcpou_converter.py
"""Unit tests for st_to_tcpou_converter.py module."""

import pytest

from tc3tools.converters.st_to_xml import (
    FileType,
    STParser,
    XMLGenerator,
)


class TestSTParserPOUTypeDetection:
    """Test POU type detection from ST code."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.mark.unit
    def test_detect_function_block(self, parser):
        """Test detection of FUNCTION_BLOCK."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    nValue : INT;
END_VAR"""
        result = parser.parse(code, "FB_Test")
        assert result.file_type == FileType.FUNCTION_BLOCK
        assert result.name == "FB_Test"

    @pytest.mark.unit
    def test_detect_program(self, parser):
        """Test detection of PROGRAM."""
        code = """PROGRAM PRG_Main
VAR
    bRunning : BOOL;
END_VAR"""
        result = parser.parse(code, "PRG_Main")
        assert result.file_type == FileType.PROGRAM
        assert result.name == "PRG_Main"

    @pytest.mark.unit
    def test_detect_function(self, parser):
        """Test detection of FUNCTION."""
        code = """FUNCTION FC_Calculate : REAL
VAR_INPUT
    fInput : REAL;
END_VAR"""
        result = parser.parse(code, "FC_Calculate")
        assert result.file_type == FileType.FUNCTION
        assert result.name == "FC_Calculate"
        assert result.return_type == "REAL"

    @pytest.mark.unit
    def test_detect_fb_with_extends(self, parser):
        """Test detection of FB with EXTENDS."""
        code = """FUNCTION_BLOCK FB_Child EXTENDS FB_Base
VAR
    nExtra : INT;
END_VAR"""
        result = parser.parse(code, "FB_Child")
        assert result.file_type == FileType.FUNCTION_BLOCK
        assert result.name == "FB_Child"
        assert "EXTENDS" in result.declaration

    @pytest.mark.unit
    def test_detect_fb_with_implements(self, parser):
        """Test detection of FB with IMPLEMENTS."""
        code = """FUNCTION_BLOCK FB_Device IMPLEMENTS I_Device
VAR
    _id : UDINT;
END_VAR"""
        result = parser.parse(code, "FB_Device")
        assert result.file_type == FileType.FUNCTION_BLOCK
        assert result.name == "FB_Device"
        assert "IMPLEMENTS" in result.declaration

    @pytest.mark.unit
    def test_detect_fb_with_multiple_implements(self, parser):
        """Test detection of FB with multiple IMPLEMENTS."""
        code = """FUNCTION_BLOCK FB_Device IMPLEMENTS I_Device, I_Errorable
VAR
    _id : UDINT;
END_VAR"""
        result = parser.parse(code, "FB_Device")
        assert result.file_type == FileType.FUNCTION_BLOCK
        assert "IMPLEMENTS" in result.declaration


class TestSTParserDUTTypeDetection:
    """Test DUT type detection."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.mark.unit
    def test_detect_enum(self, parser):
        """Test detection of ENUM type."""
        code = """TYPE E_Status :
(
    Idle := 0,
    Running := 1
);
END_TYPE"""
        result = parser.parse(code, "E_Status")
        assert result.file_type == FileType.TYPE
        assert result.name == "E_Status"

    @pytest.mark.unit
    def test_detect_struct(self, parser):
        """Test detection of STRUCT type."""
        code = """TYPE ST_Data :
STRUCT
    nId : UDINT;
    sName : STRING;
END_STRUCT
END_TYPE"""
        result = parser.parse(code, "ST_Data")
        assert result.file_type == FileType.TYPE
        assert result.name == "ST_Data"


class TestSTParserGVLDetection:
    """Test GVL detection."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.mark.unit
    def test_detect_gvl(self, parser):
        """Test detection of GVL."""
        code = """VAR_GLOBAL
    g_bReady : BOOL;
END_VAR"""
        result = parser.parse(code, "GVL_Test")
        assert result.file_type == FileType.GVL

    @pytest.mark.unit
    def test_detect_gvl_constant(self, parser):
        """Test detection of GVL CONSTANT."""
        code = """VAR_GLOBAL CONSTANT
    GC_MAX : INT := 100;
END_VAR"""
        result = parser.parse(code, "GVL_Constants")
        assert result.file_type == FileType.GVL


class TestSTParserInterfaceDetection:
    """Test Interface detection."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.mark.unit
    def test_detect_interface(self, parser):
        """Test detection of INTERFACE."""
        code = """INTERFACE I_Device

METHOD Initialize : BOOL
END_METHOD

END_INTERFACE"""
        result = parser.parse(code, "I_Device")
        assert result.file_type == FileType.INTERFACE
        assert result.name == "I_Device"

    @pytest.mark.unit
    def test_interface_methods_extracted(self, parser):
        """Test interface methods are extracted."""
        code = """INTERFACE I_Device

METHOD Initialize : BOOL
END_METHOD

METHOD Execute : BOOL
END_METHOD

END_INTERFACE"""
        result = parser.parse(code, "I_Device")
        assert len(result.methods) >= 2


class TestSTParserMethodParsing:
    """Test method parsing from ST code."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.mark.unit
    def test_parse_method(self, parser):
        """Test parsing method from FB."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    _value : INT;
END_VAR

METHOD Initialize : BOOL
VAR_INPUT
    nStartValue : INT;
END_VAR
Initialize := TRUE;
END_METHOD

END_FUNCTION_BLOCK"""
        result = parser.parse(code, "FB_Test")
        assert len(result.methods) == 1
        assert result.methods[0].name == "Initialize"
        assert result.methods[0].return_type == "BOOL"

    @pytest.mark.unit
    def test_parse_multiple_methods(self, parser):
        """Test parsing multiple methods."""
        code = """FUNCTION_BLOCK FB_Test

METHOD First : BOOL
First := TRUE;
END_METHOD

METHOD Second : INT
Second := 42;
END_METHOD

END_FUNCTION_BLOCK"""
        result = parser.parse(code, "FB_Test")
        assert len(result.methods) == 2


class TestSTParserPropertyParsing:
    """Test property parsing from ST code."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.mark.unit
    def test_parse_property_with_get(self, parser):
        """Test parsing property with GET."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    _value : INT;
END_VAR

PROPERTY Value : INT
    GET
    Value := _value;
    END_GET
END_PROPERTY

END_FUNCTION_BLOCK"""
        result = parser.parse(code, "FB_Test")
        assert len(result.properties) == 1
        assert result.properties[0].name == "Value"
        assert result.properties[0].get_accessor is not None

    @pytest.mark.unit
    def test_parse_property_with_get_set(self, parser):
        """Test parsing property with GET and SET."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    _value : INT;
END_VAR

PROPERTY Value : INT
    GET
    Value := _value;
    END_GET
    SET
    _value := Value;
    END_SET
END_PROPERTY

END_FUNCTION_BLOCK"""
        result = parser.parse(code, "FB_Test")
        assert len(result.properties) == 1
        assert result.properties[0].get_accessor is not None
        assert result.properties[0].set_accessor is not None


class TestXMLGenerator:
    """Test XML generation."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.fixture
    def generator(self):
        return XMLGenerator()

    @pytest.mark.unit
    def test_generate_valid_xml(self, parser, generator):
        """Test that generated XML is valid."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    nValue : INT;
END_VAR

nValue := 42;

END_FUNCTION_BLOCK"""
        parsed = parser.parse(code, "FB_Test")
        xml_content = generator.generate(parsed)

        assert '<?xml version="1.0"' in xml_content
        assert "<TcPlcObject" in xml_content
        assert "FB_Test" in xml_content
        assert "</TcPlcObject>" in xml_content

    @pytest.mark.unit
    def test_cdata_sections(self, parser, generator):
        """Test CDATA sections in generated XML."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    nValue : INT;
END_VAR

nValue := 42;

END_FUNCTION_BLOCK"""
        parsed = parser.parse(code, "FB_Test")
        xml_content = generator.generate(parsed)

        assert "<![CDATA[" in xml_content
        assert "]]>" in xml_content


class TestSTParserEdgeCases:
    """Test edge cases."""

    @pytest.fixture
    def parser(self):
        return STParser()

    @pytest.fixture
    def generator(self):
        return XMLGenerator()

    @pytest.mark.unit
    def test_attributes_preserved(self, parser, generator):
        """Test that attributes are preserved in conversion."""
        code = """{attribute 'qualified_only'}
FUNCTION_BLOCK FB_Test
VAR
    nValue : INT;
END_VAR

END_FUNCTION_BLOCK"""
        parsed = parser.parse(code, "FB_Test")
        xml_content = generator.generate(parsed)

        assert "qualified_only" in xml_content

    @pytest.mark.unit
    def test_complex_types(self, parser, generator):
        """Test complex type declarations."""
        code = """FUNCTION_BLOCK FB_Test
VAR
    aBuffer : ARRAY[0..255] OF BYTE;
    sName : STRING(80);
    pData : POINTER TO INT;
END_VAR

END_FUNCTION_BLOCK"""
        parsed = parser.parse(code, "FB_Test")
        xml_content = generator.generate(parsed)

        assert "ARRAY[0..255] OF BYTE" in xml_content
        assert "STRING(80)" in xml_content
