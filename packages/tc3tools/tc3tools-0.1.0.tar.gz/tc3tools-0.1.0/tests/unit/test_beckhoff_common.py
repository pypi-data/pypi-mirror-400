"""
Unit tests for beckhoff_common module.

Tests the shared components for Beckhoff Tools including diagnostic types,
severity enum, and file system interfaces.
"""

import pytest

from tc3tools.core.common import Diagnostic, LocalFileSystem, Severity

# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_error_exists(self):
        """Test ERROR severity level exists."""
        assert hasattr(Severity, "ERROR")
        assert Severity.ERROR is not None

    def test_severity_warning_exists(self):
        """Test WARNING severity level exists."""
        assert hasattr(Severity, "WARNING")
        assert Severity.WARNING is not None

    def test_severity_info_exists(self):
        """Test INFO severity level exists."""
        assert hasattr(Severity, "INFO")
        assert Severity.INFO is not None

    def test_severity_values_are_unique(self):
        """Test all severity values are unique."""
        values = [Severity.ERROR.value, Severity.WARNING.value, Severity.INFO.value]
        assert len(values) == len(set(values))


@pytest.mark.unit
class TestDiagnostic:
    """Tests for Diagnostic dataclass."""

    def test_diagnostic_creation(self):
        """Test creating a diagnostic."""
        diag = Diagnostic(
            line_number=10,
            column=5,
            message="Test error",
            severity=Severity.ERROR,
            rule_id="TEST001",
        )
        assert diag.line_number == 10
        assert diag.column == 5
        assert diag.message == "Test error"
        assert diag.severity == Severity.ERROR
        assert diag.rule_id == "TEST001"

    def test_diagnostic_with_line_content(self):
        """Test diagnostic with line content."""
        diag = Diagnostic(
            line_number=10,
            column=5,
            message="Test error",
            severity=Severity.ERROR,
            rule_id="TEST001",
            line_content="x := 1;",
        )
        assert diag.line_content == "x := 1;"

    def test_diagnostic_str_representation(self):
        """Test string representation of diagnostic."""
        diag = Diagnostic(
            line_number=10,
            column=5,
            message="Test error",
            severity=Severity.ERROR,
            rule_id="TEST001",
        )
        result = str(diag)
        assert "[ERROR]" in result
        assert "Line 10" in result
        assert "Test error" in result
        assert "TEST001" in result

    def test_diagnostic_warning_str(self):
        """Test warning severity in string output."""
        diag = Diagnostic(
            line_number=20,
            column=1,
            message="Warning message",
            severity=Severity.WARNING,
            rule_id="WARN001",
        )
        result = str(diag)
        assert "[WARNING]" in result

    def test_diagnostic_info_str(self):
        """Test info severity in string output."""
        diag = Diagnostic(
            line_number=30,
            column=1,
            message="Info message",
            severity=Severity.INFO,
            rule_id="INFO001",
        )
        result = str(diag)
        assert "[INFO]" in result


@pytest.mark.unit
class TestLocalFileSystem:
    """Tests for LocalFileSystem class."""

    def test_filesystem_instantiation(self):
        """Test that LocalFileSystem can be instantiated."""
        fs = LocalFileSystem()
        assert fs is not None
        assert isinstance(fs, LocalFileSystem)

    def test_read_text_file(self, tmp_path):
        """Test reading a text file."""
        # Create temp file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!", encoding="utf-8")

        fs = LocalFileSystem()
        content = fs.read_text(test_file)

        assert content == "Hello, World!"

    def test_write_text_file(self, tmp_path):
        """Test writing a text file."""
        test_file = tmp_path / "output.txt"

        fs = LocalFileSystem()
        fs.write_text(test_file, "Test content")

        assert test_file.exists()
        assert test_file.read_text() == "Test content"

    def test_collect_files_single_file(self, tmp_path):
        """Test collecting files with single file as root."""
        # Create a test file
        test_file = tmp_path / "test.st"
        test_file.write_text("test", encoding="utf-8")

        fs = LocalFileSystem()
        files = list(fs.collect_files(test_file, [".st"]))

        assert len(files) == 1
        assert files[0] == test_file

    def test_collect_files_directory(self, tmp_path):
        """Test collecting files from directory."""
        # Create test files
        (tmp_path / "file1.st").write_text("test1", encoding="utf-8")
        (tmp_path / "file2.st").write_text("test2", encoding="utf-8")
        (tmp_path / "file3.txt").write_text("test3", encoding="utf-8")

        fs = LocalFileSystem()
        st_files = list(fs.collect_files(tmp_path, [".st"]))

        assert len(st_files) == 2
        assert all(f.suffix == ".st" for f in st_files)

    def test_collect_files_recursive(self, tmp_path):
        """Test collecting files recursively."""
        # Create directory structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "file1.st").write_text("test1", encoding="utf-8")
        (subdir / "file2.st").write_text("test2", encoding="utf-8")

        fs = LocalFileSystem()
        files = list(fs.collect_files(tmp_path, [".st"]))

        assert len(files) == 2

    def test_collect_files_multiple_extensions(self, tmp_path):
        """Test collecting files with multiple extensions."""
        # Create test files with different extensions
        (tmp_path / "file1.st").write_text("test1", encoding="utf-8")
        (tmp_path / "file2.TcPOU").write_text("test2", encoding="utf-8")
        (tmp_path / "file3.txt").write_text("test3", encoding="utf-8")

        fs = LocalFileSystem()
        files = list(fs.collect_files(tmp_path, [".st", ".TcPOU"]))

        assert len(files) == 2

    def test_collect_files_no_matches(self, tmp_path):
        """Test collecting files when no matches exist."""
        (tmp_path / "file1.txt").write_text("test1", encoding="utf-8")

        fs = LocalFileSystem()
        files = list(fs.collect_files(tmp_path, [".st"]))

        assert len(files) == 0

    def test_make_dirs(self, tmp_path):
        """Test creating directories."""
        target_file = tmp_path / "subdir1" / "subdir2" / "file.txt"

        fs = LocalFileSystem()
        fs.make_dirs(target_file)

        assert target_file.parent.exists()
        assert target_file.parent.is_dir()

    def test_read_text_utf8(self, tmp_path):
        """Test reading UTF-8 encoded file."""
        test_file = tmp_path / "utf8.txt"
        test_file.write_text("Temperature: 25°C", encoding="utf-8")

        fs = LocalFileSystem()
        content = fs.read_text(test_file)

        assert "°C" in content

    def test_write_text_utf8(self, tmp_path):
        """Test writing UTF-8 content."""
        test_file = tmp_path / "utf8_out.txt"

        fs = LocalFileSystem()
        fs.write_text(test_file, "Temperature: 25°C")

        content = test_file.read_text(encoding="utf-8")
        assert "°C" in content


@pytest.mark.unit
class TestDiagnosticEdgeCases:
    """Edge case tests for Diagnostic."""

    def test_diagnostic_zero_line_number(self):
        """Test diagnostic with zero line number."""
        diag = Diagnostic(
            line_number=0, column=0, message="Test", severity=Severity.INFO, rule_id="TEST"
        )
        assert diag.line_number == 0

    def test_diagnostic_empty_message(self):
        """Test diagnostic with empty message."""
        diag = Diagnostic(
            line_number=1, column=1, message="", severity=Severity.WARNING, rule_id="TEST"
        )
        assert diag.message == ""

    def test_diagnostic_special_characters_in_message(self):
        """Test diagnostic with special characters in message."""
        message = "Missing ';' after <statement> in 'function'"
        diag = Diagnostic(
            line_number=1, column=1, message=message, severity=Severity.ERROR, rule_id="SYNTAX001"
        )
        assert diag.message == message
        assert "<statement>" in str(diag)
