"""
End-to-end tests for tc3tools CLI.

Tests the complete CLI workflow including all subcommands.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Get Tools directory
TOOLS_DIR = Path(__file__).parent.parent.parent


def run_tc3tools(*args, cwd=None):
    """Run tc3tools CLI with given arguments using python -m."""
    cmd = [sys.executable, "-m", "tc3tools", *list(args)]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or TOOLS_DIR,
    )
    return result


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.e2e
class TestCLIHelp:
    """Test CLI help commands."""

    def test_main_help(self):
        """Test main help command."""
        result = run_tc3tools("--help")
        assert result.returncode == 0
        assert "tc3tools" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_st2xml_help(self):
        """Test st2xml subcommand help."""
        result = run_tc3tools("st2xml", "--help")
        assert result.returncode == 0
        assert "st2xml" in result.stdout.lower() or "input" in result.stdout.lower()

    def test_xml2st_help(self):
        """Test xml2st subcommand help."""
        result = run_tc3tools("xml2st", "--help")
        assert result.returncode == 0
        assert "xml2st" in result.stdout.lower() or "input" in result.stdout.lower()

    def test_fmt_st_help(self):
        """Test fmt-st subcommand help."""
        result = run_tc3tools("fmt-st", "--help")
        assert result.returncode == 0

    def test_fmt_xml_help(self):
        """Test fmt-xml subcommand help."""
        result = run_tc3tools("fmt-xml", "--help")
        assert result.returncode == 0


@pytest.mark.e2e
class TestST2XMLCommand:
    """Test st2xml CLI command."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def sample_st_file(self, temp_dir):
        """Create a sample ST file for testing."""
        content = """FUNCTION_BLOCK FB_Test
VAR_INPUT
    bEnable : BOOL;
END_VAR
VAR_OUTPUT
    bDone : BOOL;
END_VAR
VAR
    _state : INT;
END_VAR

IF bEnable THEN
    bDone := TRUE;
END_IF
END_FUNCTION_BLOCK"""
        st_file = temp_dir / "FB_Test.st"
        st_file.write_text(content, encoding="utf-8")
        return st_file

    def test_st2xml_single_file(self, temp_dir, sample_st_file):
        """Test converting a single ST file to XML."""
        output_dir = temp_dir / "output"

        # Use positional arguments (input output)
        result = run_tc3tools("st2xml", str(sample_st_file), str(output_dir))

        # Command should succeed
        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Output file should exist
        output_file = output_dir / "FB_Test.TcPOU"
        assert output_file.exists(), f"Expected {output_file} to exist"

        # Output should be valid XML
        content = output_file.read_text(encoding="utf-8")
        assert '<?xml version="1.0"' in content
        assert "<TcPlcObject" in content
        assert "FB_Test" in content

    def test_st2xml_directory(self, temp_dir):
        """Test converting a directory of ST files."""
        # Create multiple ST files
        for name in ["FB_One", "FB_Two"]:
            content = f"""FUNCTION_BLOCK {name}
VAR
    nValue : INT;
END_VAR
END_FUNCTION_BLOCK"""
            (temp_dir / f"{name}.st").write_text(content, encoding="utf-8")

        output_dir = temp_dir / "output"

        # Use positional arguments
        result = run_tc3tools("st2xml", str(temp_dir), str(output_dir))

        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Output files should exist
        assert (output_dir / "FB_One.TcPOU").exists() or len(list(output_dir.glob("*.TcPOU"))) >= 1


@pytest.mark.e2e
class TestXML2STCommand:
    """Test xml2st CLI command."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def sample_xml_file(self, temp_dir):
        """Create a sample TcPOU XML file for testing."""
        content = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Test" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Test
VAR_INPUT
    bEnable : BOOL;
END_VAR
VAR_OUTPUT
    bDone : BOOL;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[IF bEnable THEN
    bDone := TRUE;
END_IF]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""
        xml_file = temp_dir / "FB_Test.TcPOU"
        xml_file.write_text(content, encoding="utf-8")
        return xml_file

    def test_xml2st_single_file(self, temp_dir, sample_xml_file):
        """Test converting a single XML file to ST."""
        output_dir = temp_dir / "output"

        # Use positional arguments
        result = run_tc3tools("xml2st", str(sample_xml_file), str(output_dir))

        # Command should succeed
        assert result.returncode == 0, f"stderr: {result.stderr}"

        # Output file should exist
        output_file = output_dir / "FB_Test.st"
        assert output_file.exists(), f"Expected {output_file} to exist"

        # Output should contain ST code
        content = output_file.read_text(encoding="utf-8")
        assert "FUNCTION_BLOCK FB_Test" in content

    def test_xml2st_directory(self, temp_dir, sample_xml_file):
        """Test converting a directory of XML files."""
        output_dir = temp_dir / "output"

        # Use positional arguments
        result = run_tc3tools("xml2st", str(temp_dir), str(output_dir))

        assert result.returncode == 0, f"stderr: {result.stderr}"


@pytest.mark.e2e
class TestFormatSTCommand:
    """Test fmt-st CLI command."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def unformatted_st_file(self, temp_dir):
        """Create an unformatted ST file for testing."""
        content = """FUNCTION_BLOCK FB_Test
VAR
x:INT;
y:BOOL;
END_VAR
IF x>0 THEN
y:=TRUE;
END_IF
END_FUNCTION_BLOCK"""
        st_file = temp_dir / "FB_Test.st"
        st_file.write_text(content, encoding="utf-8")
        return st_file

    def test_fmt_st_check(self, unformatted_st_file):
        """Test checking ST file format."""
        result = run_tc3tools("fmt-st", str(unformatted_st_file), "--check")
        # May return non-zero if formatting needed, that's OK
        assert result.returncode in [0, 1]

    def test_fmt_st_in_place(self, temp_dir, unformatted_st_file):
        """Test formatting ST file in-place."""
        result = run_tc3tools("fmt-st", str(unformatted_st_file), "--inplace")

        # Command should succeed
        assert result.returncode == 0, f"stderr: {result.stderr}"

        # File should still exist
        assert unformatted_st_file.exists()


@pytest.mark.e2e
class TestFormatXMLCommand:
    """Test fmt-xml CLI command."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def sample_xml_file(self, temp_dir):
        """Create a sample TcPOU XML file."""
        content = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <POU Name="FB_Test" Id="{12345678-1234-1234-1234-123456789abc}" SpecialFunc="None">
    <Declaration><![CDATA[FUNCTION_BLOCK FB_Test
VAR
    x : INT;
END_VAR]]></Declaration>
    <Implementation>
      <ST><![CDATA[x := 1;]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>"""
        xml_file = temp_dir / "FB_Test.TcPOU"
        xml_file.write_text(content, encoding="utf-8")
        return xml_file

    def test_fmt_xml_check(self, sample_xml_file):
        """Test checking XML file format."""
        result = run_tc3tools("fmt-xml", str(sample_xml_file), "--check")
        # Check mode should work
        assert result.returncode in [0, 1]

    def test_fmt_xml_format(self, sample_xml_file):
        """Test formatting XML file."""
        result = run_tc3tools("fmt-xml", str(sample_xml_file))
        assert result.returncode == 0, f"stderr: {result.stderr}"


@pytest.mark.e2e
class TestCLIRoundTrip:
    """Test round-trip conversion via CLI."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_st_to_xml_to_st_roundtrip(self, temp_dir):
        """Test ST -> XML -> ST round-trip via CLI."""
        # Create original ST file
        original_st = """FUNCTION_BLOCK FB_RoundTrip
VAR_INPUT
    nValue : INT;
END_VAR
VAR_OUTPUT
    nResult : INT;
END_VAR

nResult := nValue * 2;
END_FUNCTION_BLOCK"""

        st_file = temp_dir / "FB_RoundTrip.st"
        st_file.write_text(original_st, encoding="utf-8")

        xml_dir = temp_dir / "xml"
        st_out_dir = temp_dir / "st_out"

        # ST -> XML
        result1 = run_tc3tools("st2xml", str(st_file), str(xml_dir))
        assert result1.returncode == 0, f"st2xml failed: {result1.stderr}"

        # Find generated XML file
        xml_files = list(xml_dir.glob("*.TcPOU"))
        assert len(xml_files) >= 1, "No XML file generated"

        # XML -> ST
        result2 = run_tc3tools("xml2st", str(xml_files[0]), str(st_out_dir))
        assert result2.returncode == 0, f"xml2st failed: {result2.stderr}"

        # Check recovered ST
        st_files = list(st_out_dir.glob("*.st"))
        assert len(st_files) >= 1, "No ST file generated"

        recovered_st = st_files[0].read_text(encoding="utf-8")
        assert "FB_RoundTrip" in recovered_st
        assert "nValue" in recovered_st


@pytest.mark.e2e
class TestCLIWithFixtures:
    """Test CLI with fixture files."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory."""
        return Path(__file__).parent.parent / "fixtures"

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_convert_fixture_st_files(self, fixtures_dir, temp_output_dir):
        """Test converting fixture ST files."""
        st_dir = fixtures_dir / "st"
        if not st_dir.exists():
            pytest.skip("ST fixtures not found")

        output_dir = temp_output_dir / "output"

        result = run_tc3tools("st2xml", str(st_dir), str(output_dir))

        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_convert_fixture_xml_files(self, fixtures_dir, temp_output_dir):
        """Test converting fixture XML files."""
        xml_dir = fixtures_dir / "xml"
        if not xml_dir.exists():
            pytest.skip("XML fixtures not found")

        output_dir = temp_output_dir / "output"

        result = run_tc3tools("xml2st", str(xml_dir), str(output_dir))

        assert result.returncode == 0, f"stderr: {result.stderr}"


@pytest.mark.e2e
class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_unknown_command(self):
        """Test unknown command error."""
        result = run_tc3tools("unknown")
        assert result.returncode != 0

    def test_nonexistent_file(self):
        """Test error on nonexistent file."""
        result = run_tc3tools("st2xml", "/nonexistent/path/file.st")
        # Should handle gracefully - check both stdout and stderr for error messages
        combined_output = (result.stdout + result.stderr).lower()
        assert (
            result.returncode != 0 or "error" in combined_output or "not found" in combined_output
        )

    def test_invalid_arguments(self):
        """Test error on invalid arguments."""
        result = run_tc3tools("st2xml", "--invalid-arg")
        assert result.returncode != 0
