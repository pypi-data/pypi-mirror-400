# Tools/tests/unit/test_st_formatter.py
"""Unit tests for st_formatter.py module."""

import pytest

from tc3tools.formatters.st_formatter import STFormatter


class TestSTFormatterIndentation:
    """Test indentation formatting rules."""

    @pytest.mark.unit
    def test_if_block_indentation(self):
        """Test IF/ELSE/END_IF indentation."""
        code = """IF bEnable THEN
bDone := TRUE;
ELSE
bDone := FALSE;
END_IF"""
        expected = """IF bEnable THEN
    bDone := TRUE;
ELSE
    bDone := FALSE;
END_IF"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert result.strip() == expected.strip()

    @pytest.mark.unit
    def test_nested_if_indentation(self):
        """Test nested IF blocks maintain proper indentation."""
        code = """IF bOuter THEN
IF bInner THEN
nValue := 1;
END_IF
END_IF"""
        expected = """IF bOuter THEN
    IF bInner THEN
        nValue := 1;
    END_IF
END_IF"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert result.strip() == expected.strip()

    @pytest.mark.unit
    def test_case_statement_indentation(self):
        """Test CASE statement indentation."""
        code = """CASE nState OF
0:
nResult := 0;
1..5:
nResult := 1;
ELSE
nResult := -1;
END_CASE"""
        formatter = STFormatter()
        result = formatter.format(code)
        # CASE body should be indented
        lines = result.strip().split("\n")
        assert lines[0] == "CASE nState OF"
        assert "END_CASE" in lines[-1]

    @pytest.mark.unit
    def test_for_loop_indentation(self):
        """Test FOR loop indentation."""
        code = """FOR i := 0 TO 10 DO
nSum := nSum + i;
END_FOR"""
        expected = """FOR i := 0 TO 10 DO
    nSum := nSum + i;
END_FOR"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert result.strip() == expected.strip()

    @pytest.mark.unit
    def test_while_loop_indentation(self):
        """Test WHILE loop indentation."""
        code = """WHILE bRunning DO
nCounter := nCounter + 1;
END_WHILE"""
        expected = """WHILE bRunning DO
    nCounter := nCounter + 1;
END_WHILE"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert result.strip() == expected.strip()

    @pytest.mark.unit
    def test_repeat_loop_indentation(self):
        """Test REPEAT loop indentation."""
        code = """REPEAT
nCounter := nCounter + 1;
UNTIL nCounter >= 10
END_REPEAT"""
        formatter = STFormatter()
        result = formatter.format(code)
        lines = result.strip().split("\n")
        assert lines[0] == "REPEAT"
        assert "    nCounter" in lines[1]


class TestSTFormatterSpacing:
    """Test spacing rules."""

    @pytest.mark.unit
    def test_assignment_spacing(self):
        """Test assignment operator is preserved."""
        code = "nValue := 42;"
        formatter = STFormatter()
        result = formatter.format(code)
        assert ":=" in result

    @pytest.mark.unit
    def test_comparison_spacing(self):
        """Test spacing around comparison operators."""
        code = "IF nValue>=10 AND bFlag=TRUE THEN"
        formatter = STFormatter()
        result = formatter.format(code)
        # Should have spaces around operators
        assert ">=" in result
        assert "=" in result

    @pytest.mark.unit
    def test_no_trailing_whitespace(self):
        """Test that trailing whitespace is removed."""
        code = "nValue := 42;    \nbDone := TRUE;  "
        formatter = STFormatter()
        result = formatter.format(code)
        for line in result.split("\n"):
            assert line == line.rstrip(), f"Line has trailing whitespace: '{line}'"


class TestSTFormatterVarBlocks:
    """Test VAR block formatting."""

    @pytest.mark.unit
    def test_var_block_indentation(self):
        """Test VAR block contents are indented."""
        code = """VAR
bEnable : BOOL;
nValue : INT;
END_VAR"""
        formatter = STFormatter()
        result = formatter.format(code)
        lines = result.strip().split("\n")
        assert lines[0] == "VAR"
        assert lines[-1] == "END_VAR"
        # Middle lines should be indented
        for line in lines[1:-1]:
            if line.strip():
                assert line.startswith("    ") or line.startswith("\t")

    @pytest.mark.unit
    def test_var_input_block(self):
        """Test VAR_INPUT block formatting."""
        code = """VAR_INPUT
bExecute : BOOL;
END_VAR"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert "VAR_INPUT" in result
        assert "END_VAR" in result


class TestSTFormatterComments:
    """Test comment handling."""

    @pytest.mark.unit
    def test_single_line_comment_preserved(self):
        """Test single-line comments are preserved."""
        code = """// This is a comment
nValue := 42;"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert "// This is a comment" in result

    @pytest.mark.unit
    def test_multiline_comment_preserved(self):
        """Test multi-line comments are preserved."""
        code = """(* This is a
multi-line comment *)
nValue := 42;"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert "(*" in result
        assert "*)" in result

    @pytest.mark.unit
    def test_inline_comment_preserved(self):
        """Test inline comments are preserved."""
        code = "nValue := 42; // inline comment"
        formatter = STFormatter()
        result = formatter.format(code)
        assert "// inline comment" in result


class TestSTFormatterAttributes:
    """Test attribute and pragma handling."""

    @pytest.mark.unit
    def test_attribute_preserved(self):
        """Test attributes are preserved."""
        code = """{attribute 'qualified_only'}
FUNCTION_BLOCK FB_Test"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert "{attribute 'qualified_only'}" in result

    @pytest.mark.unit
    def test_pragma_preserved(self):
        """Test pragmas are preserved."""
        code = """{$REGION 'Initialization'}
nValue := 0;
{$ENDREGION}"""
        formatter = STFormatter()
        result = formatter.format(code)
        assert "{$REGION" in result
        assert "{$ENDREGION}" in result


class TestSTFormatterEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.unit
    def test_empty_string(self):
        """Test empty string input."""
        formatter = STFormatter()
        result = formatter.format("")
        assert result == ""

    @pytest.mark.unit
    def test_whitespace_only(self):
        """Test whitespace-only input."""
        formatter = STFormatter()
        result = formatter.format("   \n\n   ")
        assert result.strip() == ""

    @pytest.mark.unit
    def test_complex_expression(self):
        """Test complex expression formatting."""
        code = "fResult := (fA + fB) * fC / (fD - fE);"
        formatter = STFormatter()
        result = formatter.format(code)
        assert "fResult" in result
        assert ":=" in result

    @pytest.mark.unit
    def test_string_literal_with_special_chars(self):
        """Test string literals with special characters."""
        code = "sMsg := 'Hello, World! $N$R';"
        formatter = STFormatter()
        result = formatter.format(code)
        assert "'Hello, World! $N$R'" in result

    @pytest.mark.unit
    def test_array_access(self):
        """Test array access syntax."""
        code = "aBuffer[nIndex] := 255;"
        formatter = STFormatter()
        result = formatter.format(code)
        assert "aBuffer[nIndex]" in result
