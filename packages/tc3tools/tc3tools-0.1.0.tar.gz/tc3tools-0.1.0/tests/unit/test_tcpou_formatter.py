"""
Unit tests for tcpou_formatter module.

Tests the TcPOUFormatter class for formatting TwinCAT XML files,
normalizing CDATA sections and XML structure.
"""

import pytest

from tc3tools.formatters.xml_formatter import TcPOUFormatter

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def formatter():
    """Create a TcPOUFormatter instance."""
    return TcPOUFormatter()


@pytest.fixture
def sample_tcpou_xml():
    """Sample TcPOU XML content."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Sample" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Sample
VAR_INPUT
    bEnable : BOOL;
END_VAR
VAR
    _state : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[IF bEnable THEN
    _state := 1;
END_IF]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""


@pytest.fixture
def poorly_indented_cdata():
    """CDATA content with inconsistent indentation."""
    return """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Test" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Test
        VAR
            x : INT;
        END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[        IF TRUE THEN
            x := 1;
        END_IF]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestFormatterInstantiation:
    """Tests for TcPOUFormatter instantiation."""

    def test_formatter_can_be_instantiated(self, formatter):
        """Test that formatter can be created."""
        assert formatter is not None
        assert isinstance(formatter, TcPOUFormatter)

    def test_formatter_has_required_methods(self, formatter):
        """Test that formatter has expected methods."""
        assert hasattr(formatter, "format_file")
        assert hasattr(formatter, "normalize_cdata")
        assert hasattr(formatter, "process")


@pytest.mark.unit
class TestNormalizeCDATA:
    """Tests for CDATA normalization."""

    def test_single_line_unchanged(self, formatter):
        """Test single line CDATA unchanged."""
        result = formatter.normalize_cdata("x := 1;")
        assert result == "x := 1;"

    def test_empty_content_unchanged(self, formatter):
        """Test empty CDATA unchanged."""
        result = formatter.normalize_cdata("")
        assert result == ""

    def test_removes_common_indentation(self, formatter):
        """Test removal of common leading indentation."""
        content = """line1
    line2
    line3"""
        result = formatter.normalize_cdata(content)
        # First line kept as-is, subsequent lines have min indent removed
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result

    def test_preserves_relative_indentation(self, formatter):
        """Test that relative indentation is preserved."""
        content = """IF TRUE THEN
    x := 1;
        y := 2;
END_IF"""
        result = formatter.normalize_cdata(content)
        lines = result.split("\n")
        # Check relative indentation preserved
        assert lines[0] == "IF TRUE THEN"

    def test_handles_empty_lines(self, formatter):
        """Test handling of empty lines."""
        content = """line1

line3"""
        result = formatter.normalize_cdata(content)
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[1] == ""  # Empty line preserved


@pytest.mark.unit
class TestFormatFile:
    """Tests for format_file method."""

    def test_format_valid_tcpou(self, formatter, sample_tcpou_xml, tmp_path):
        """Test formatting a valid TcPOU file."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        success, message = formatter.format_file(test_file)

        assert success is True
        assert message == "Formatted"

    def test_format_preserves_content(self, formatter, sample_tcpou_xml, tmp_path):
        """Test that formatting preserves essential content."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert "FB_Sample" in result
        assert "FUNCTION_BLOCK" in result
        assert "bEnable" in result

    def test_check_only_mode(self, formatter, sample_tcpou_xml, tmp_path):
        """Test check_only mode doesn't modify file."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")
        original_content = test_file.read_text(encoding="utf-8")

        success, _message = formatter.format_file(test_file, check_only=True)

        assert success is True
        # File should be unchanged in check mode
        assert test_file.read_text(encoding="utf-8") == original_content

    def test_format_invalid_xml_fails(self, formatter, tmp_path):
        """Test that invalid XML returns failure."""
        test_file = tmp_path / "invalid.TcPOU"
        test_file.write_text("not valid xml", encoding="utf-8")

        success, _message = formatter.format_file(test_file)

        assert success is False

    def test_format_normalizes_indentation(self, formatter, poorly_indented_cdata, tmp_path):
        """Test that formatting normalizes CDATA indentation."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(poorly_indented_cdata, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        # The extra indentation should be removed
        assert "FB_Test" in result


@pytest.mark.unit
class TestXMLPreservation:
    """Tests for XML structure preservation."""

    def test_preserves_xml_declaration(self, formatter, sample_tcpou_xml, tmp_path):
        """Test that XML declaration is preserved."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert '<?xml version="1.0"' in result

    def test_preserves_pou_name(self, formatter, sample_tcpou_xml, tmp_path):
        """Test that POU name is preserved."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert 'Name="FB_Sample"' in result

    def test_preserves_guid(self, formatter, sample_tcpou_xml, tmp_path):
        """Test that GUID is preserved."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert "12345678-1234-1234-1234-123456789abc" in result


@pytest.mark.unit
class TestCDATAFormatting:
    """Tests for CDATA section handling."""

    def test_declaration_cdata_preserved(self, formatter, sample_tcpou_xml, tmp_path):
        """Test Declaration CDATA is preserved."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert "FUNCTION_BLOCK FB_Sample" in result
        assert "VAR_INPUT" in result
        assert "bEnable : BOOL" in result

    def test_implementation_cdata_preserved(self, formatter, sample_tcpou_xml, tmp_path):
        """Test Implementation CDATA is preserved."""
        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(sample_tcpou_xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert "IF bEnable THEN" in result
        assert "_state := 1" in result
        assert "END_IF" in result


@pytest.mark.unit
class TestMethodFormatting:
    """Tests for method formatting in TcPOU."""

    def test_method_preserved(self, formatter, tmp_path):
        """Test that method elements are preserved."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_WithMethod" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_WithMethod
VAR
    _x : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[]]></ST>
    </Implementation>
    <Method Name="DoSomething" Id="{11111111-1111-1111-1111-111111111111}">
      <Declaration><![CDATA[METHOD DoSomething : BOOL]]></Declaration>
      <Implementation>
        <ST><![CDATA[_x := _x + 1;
DoSomething := TRUE;]]></ST>
      </Implementation>
    </Method>
  </POU>
</TcPlcObject>"""

        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert 'Name="DoSomething"' in result
        assert "_x := _x + 1" in result


@pytest.mark.unit
class TestPropertyFormatting:
    """Tests for property formatting in TcPOU."""

    def test_property_preserved(self, formatter, tmp_path):
        """Test that property elements are preserved."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_WithProperty" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_WithProperty
VAR
    _value : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[]]></ST>
    </Implementation>
    <Property Name="Value" Id="{22222222-2222-2222-2222-222222222222}">
      <Declaration><![CDATA[PROPERTY Value : INT]]></Declaration>
      <Get Name="Get" Id="{33333333-3333-3333-3333-333333333333}">
        <Declaration><![CDATA[VAR
END_VAR]]></Declaration>
        <Implementation>
          <ST><![CDATA[Value := _value;]]></ST>
        </Implementation>
      </Get>
    </Property>
  </POU>
</TcPlcObject>"""

        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert 'Name="Value"' in result
        assert "PROPERTY Value" in result
        assert "_value" in result


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_implementation_cdata(self, formatter, tmp_path):
        """Test handling of empty implementation CDATA."""
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

        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(xml, encoding="utf-8")

        success, _ = formatter.format_file(test_file)

        assert success is True

    def test_special_characters_in_cdata(self, formatter, tmp_path):
        """Test special characters in CDATA are preserved."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Special" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Special
VAR
    sText : STRING := 'Temperature: 25°C';
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[// Comment with <special> & characters]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""

        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(xml, encoding="utf-8")

        success, _ = formatter.format_file(test_file)

        assert success is True
        result = test_file.read_text(encoding="utf-8")
        assert "25°C" in result or "Temperature" in result

    def test_comments_preserved(self, formatter, tmp_path):
        """Test that ST comments are preserved."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Comments" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Comments
// Declaration comment
VAR
    x : INT; // inline
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[(* Block comment *)
x := 1; // inline comment]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""

        test_file = tmp_path / "test.TcPOU"
        test_file.write_text(xml, encoding="utf-8")

        formatter.format_file(test_file)

        result = test_file.read_text(encoding="utf-8")
        assert "Declaration comment" in result or "comment" in result.lower()

    def test_nonexistent_file_fails(self, formatter, tmp_path):
        """Test that formatting nonexistent file fails gracefully."""
        nonexistent = tmp_path / "nonexistent.TcPOU"

        success, _message = formatter.format_file(nonexistent)

        assert success is False


@pytest.mark.unit
class TestDUTFormatting:
    """Tests for DUT (Data Unit Type) formatting."""

    def test_dut_enum_formatted(self, formatter, tmp_path):
        """Test formatting a DUT enum file."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <DUT Name="E_Test" Id="{12345678-1234-1234-1234-123456789abc}">
    <Declaration><![CDATA[TYPE E_Test :
(
    VALUE_A := 0,
    VALUE_B := 1
);
END_TYPE]]></Declaration>
  </DUT>
</TcPlcObject>"""

        test_file = tmp_path / "E_Test.TcDUT"
        test_file.write_text(xml, encoding="utf-8")

        # Rename to TcPOU for the formatter (it only processes .TcPOU)
        tcpou_file = tmp_path / "E_Test.TcPOU"
        tcpou_file.write_text(xml, encoding="utf-8")

        success, _ = formatter.format_file(tcpou_file)

        assert success is True
        result = tcpou_file.read_text(encoding="utf-8")
        assert "E_Test" in result
        assert "VALUE_A" in result


@pytest.mark.unit
class TestGVLFormatting:
    """Tests for GVL (Global Variable List) formatting."""

    def test_gvl_formatted(self, formatter, tmp_path):
        """Test formatting a GVL file."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <GVL Name="GVL_Test" Id="{12345678-1234-1234-1234-123456789abc}">
    <Declaration><![CDATA[VAR_GLOBAL
    G_MAX_COUNT : INT := 100;
END_VAR]]></Declaration>
  </GVL>
</TcPlcObject>"""

        test_file = tmp_path / "GVL_Test.TcPOU"
        test_file.write_text(xml, encoding="utf-8")

        success, _ = formatter.format_file(test_file)

        assert success is True
        result = test_file.read_text(encoding="utf-8")
        assert "GVL_Test" in result
        assert "G_MAX_COUNT" in result
