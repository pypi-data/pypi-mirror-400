"""
Integration tests for ALL fixture files.

This module ensures comprehensive testing of all ST and XML fixture files
for bidirectional conversion (ST -> XML and XML -> ST).
"""

from pathlib import Path

import pytest

from tc3tools.converters.st_to_xml import STParser, XMLGenerator
from tc3tools.converters.xml_to_st import STGenerator, TwinCATXMLParser

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def st_parser():
    """Create an STParser instance."""
    return STParser()


@pytest.fixture
def xml_generator():
    """Create an XMLGenerator instance."""
    return XMLGenerator()


@pytest.fixture
def xml_parser():
    """Create a TwinCATXMLParser instance."""
    return TwinCATXMLParser()


@pytest.fixture
def st_generator():
    """Create an STGenerator instance."""
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
# Parameterized tests for ALL ST files
# =============================================================================

# List of all ST fixture files
ST_FIXTURE_FILES = [
    "E_NodeStatus.st",
    "E_Status.st",
    "FB_ActionNode.st",
    "FB_AlwaysFailure.st",
    "FB_AlwaysSuccess.st",
    "FB_BaseNode.st",
    "FB_ConditionNode.st",
    "FB_EdgeCases.st",
    "FB_Sample.st",
    "FB_SimpleBlock.st",
    "FB_WithMethods.st",
    "FB_WithProperties.st",
    "FC_Calculate.st",
    "GVL_Constants.st",
    "I_Device.st",
    "I_Errorable.st",
    "I_TreeNode.st",
    "PRG_Main.st",
    "ST_Data.st",
]


@pytest.mark.integration
class TestAllSTToXML:
    """Test ST to XML conversion for all ST fixture files."""

    @pytest.mark.parametrize("filename", ST_FIXTURE_FILES)
    def test_st_to_xml_conversion(self, st_parser, xml_generator, st_fixtures_dir, filename):
        """Test that each ST file can be converted to XML."""
        st_file = st_fixtures_dir / filename
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")

        # Parse ST content
        parsed = st_parser.parse(st_content)
        assert parsed is not None, f"Failed to parse {filename}"

        # Generate XML
        xml = xml_generator.generate(parsed)
        assert xml is not None, f"Failed to generate XML for {filename}"
        assert '<?xml version="1.0"' in xml, f"Missing XML declaration in {filename}"
        assert "<TcPlcObject" in xml, f"Missing TcPlcObject in {filename}"

        # Get expected name from filename
        name = filename.replace(".st", "")

        # Note: ST_Data.st contains multiple types (ST_NestedData comes first),
        # and GVLs may use default names when parsed from ST content.
        # The key test is that conversion succeeds and produces valid XML.
        if filename not in ["GVL_Constants.st", "ST_Data.st"]:
            assert f'Name="{name}"' in xml, f"Name not found in XML for {filename}"
        else:
            # For files with special handling, just verify a Name attribute exists
            assert 'Name="' in xml, f"No Name attribute in XML for {filename}"

    @pytest.mark.parametrize("filename", ST_FIXTURE_FILES)
    def test_st_structure_preserved(self, st_parser, xml_generator, st_fixtures_dir, filename):
        """Test that key structural elements are preserved in conversion."""
        st_file = st_fixtures_dir / filename
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        st_content = st_file.read_text(encoding="utf-8")
        parsed = st_parser.parse(st_content)
        xml = xml_generator.generate(parsed)

        # Check for expected elements based on file type
        if filename.startswith("FB_"):
            assert "FUNCTION_BLOCK" in xml, f"FUNCTION_BLOCK not found in {filename}"
        elif filename.startswith("PRG_"):
            assert "PROGRAM" in xml, f"PROGRAM not found in {filename}"
        elif filename.startswith("FC_"):
            assert "FUNCTION" in xml, f"FUNCTION not found in {filename}"
        elif filename.startswith("E_") or filename.startswith("ST_"):
            assert "TYPE" in xml, f"TYPE declaration not found in {filename}"
        elif filename.startswith("I_"):
            assert "INTERFACE" in xml, f"INTERFACE not found in {filename}"
        elif filename.startswith("GVL_"):
            assert "VAR_GLOBAL" in xml, f"VAR_GLOBAL not found in {filename}"


# =============================================================================
# Parameterized tests for ALL XML files
# =============================================================================

# List of all XML fixture files
XML_FIXTURE_FILES = [
    "E_NodeStatus.TcDUT",
    "E_State.TcDUT",
    "E_Status.TcDUT",
    "FB_ActionNode.TcPOU",
    "FB_AlwaysFailure.TcPOU",
    "FB_AlwaysSuccess.TcPOU",
    "FB_BaseNode.TcPOU",
    "FB_ConditionNode.TcPOU",
    "FB_EdgeCases.TcPOU",
    "FB_Sample.TcPOU",
    "FB_SimpleBlock.TcPOU",
    "FB_WithMethods.TcPOU",
    "FB_WithProperties.TcPOU",
    "FC_Calculate.TcPOU",
    "GVL_Constants.TcGVL",
    "GVL_Settings.TcGVL",
    "I_Device.TcIO",
    "I_Errorable.TcIO",
    "I_TreeNode.TcIO",
    "PRG_Main.TcPOU",
    "ST_Data.TcDUT",
    "ST_NestedData.TcDUT",
]


@pytest.mark.integration
class TestAllXMLToST:
    """Test XML to ST conversion for all XML fixture files."""

    @pytest.mark.parametrize("filename", XML_FIXTURE_FILES)
    def test_xml_to_st_conversion(self, xml_parser, st_generator, xml_fixtures_dir, filename):
        """Test that each XML file can be converted to ST."""
        xml_file = xml_fixtures_dir / filename
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")

        # Parse XML content
        tc_obj = xml_parser.parse(xml_content)
        assert tc_obj is not None, f"Failed to parse {filename}"

        # Generate ST
        st = st_generator.generate(tc_obj)
        assert st is not None, f"Failed to generate ST for {filename}"

        # Get expected name from filename
        name = filename.split(".")[0]

        # Note: GVLs don't include their name in the ST output (VAR_GLOBAL blocks are anonymous in ST)
        # The key test is that conversion succeeds and produces valid ST code.
        if filename.endswith(".TcGVL"):
            # For GVLs, verify it contains VAR_GLOBAL
            assert "VAR_GLOBAL" in st, f"VAR_GLOBAL not found in ST output for {filename}"
        else:
            assert name in st, f"Name '{name}' not found in ST output for {filename}"

    @pytest.mark.parametrize("filename", XML_FIXTURE_FILES)
    def test_xml_structure_elements_extracted(
        self, xml_parser, st_generator, xml_fixtures_dir, filename
    ):
        """Test that key structural elements are extracted from XML."""
        xml_file = xml_fixtures_dir / filename
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        xml_content = xml_file.read_text(encoding="utf-8")
        tc_obj = xml_parser.parse(xml_content)
        st = st_generator.generate(tc_obj)

        # Check for expected elements based on file type
        if filename.endswith(".TcPOU"):
            name = filename.split(".")[0]
            if name.startswith("FB_"):
                assert "FUNCTION_BLOCK" in st, f"FUNCTION_BLOCK not found in {filename}"
            elif name.startswith("PRG_"):
                assert "PROGRAM" in st, f"PROGRAM not found in {filename}"
            elif name.startswith("FC_"):
                assert "FUNCTION" in st, f"FUNCTION not found in {filename}"
        elif filename.endswith(".TcDUT"):
            assert "TYPE" in st, f"TYPE not found in {filename}"
        elif filename.endswith(".TcGVL"):
            assert "VAR_GLOBAL" in st, f"VAR_GLOBAL not found in {filename}"
        elif filename.endswith(".TcIO"):
            assert "INTERFACE" in st, f"INTERFACE not found in {filename}"


# =============================================================================
# Round-trip tests for matching ST/XML pairs
# =============================================================================

# ST files with matching XML files
MATCHING_ST_XML_PAIRS = [
    ("E_NodeStatus.st", "E_NodeStatus.TcDUT"),
    ("E_Status.st", "E_Status.TcDUT"),
    ("FB_ActionNode.st", "FB_ActionNode.TcPOU"),
    ("FB_AlwaysFailure.st", "FB_AlwaysFailure.TcPOU"),
    ("FB_AlwaysSuccess.st", "FB_AlwaysSuccess.TcPOU"),
    ("FB_BaseNode.st", "FB_BaseNode.TcPOU"),
    ("FB_ConditionNode.st", "FB_ConditionNode.TcPOU"),
    ("FB_EdgeCases.st", "FB_EdgeCases.TcPOU"),
    ("FB_Sample.st", "FB_Sample.TcPOU"),
    ("FB_SimpleBlock.st", "FB_SimpleBlock.TcPOU"),
    ("FB_WithMethods.st", "FB_WithMethods.TcPOU"),
    ("FB_WithProperties.st", "FB_WithProperties.TcPOU"),
    ("FC_Calculate.st", "FC_Calculate.TcPOU"),
    ("GVL_Constants.st", "GVL_Constants.TcGVL"),
    ("I_Device.st", "I_Device.TcIO"),
    ("I_Errorable.st", "I_Errorable.TcIO"),
    ("I_TreeNode.st", "I_TreeNode.TcIO"),
    ("PRG_Main.st", "PRG_Main.TcPOU"),
    ("ST_Data.st", "ST_Data.TcDUT"),
]


@pytest.mark.integration
class TestSTXMLPairRoundTrip:
    """Test round-trip conversion for matching ST/XML pairs."""

    @pytest.mark.parametrize("st_filename,xml_filename", MATCHING_ST_XML_PAIRS)
    def test_st_roundtrip(
        self,
        st_parser,
        xml_generator,
        xml_parser,
        st_generator,
        st_fixtures_dir,
        st_filename,
        xml_filename,
    ):
        """Test ST -> XML -> ST round-trip preserves key elements."""
        st_file = st_fixtures_dir / st_filename
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)

        # XML -> ST
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Check key elements preserved
        name = st_filename.replace(".st", "")

        # GVLs don't include name in ST output (VAR_GLOBAL is anonymous)
        if st_filename.startswith("GVL_"):
            assert "VAR_GLOBAL" in recovered_st, (
                f"VAR_GLOBAL not preserved in round-trip for {st_filename}"
            )
        else:
            assert name in recovered_st, (
                f"Name '{name}' not preserved in round-trip for {st_filename}"
            )

        # Check structural elements
        if "FUNCTION_BLOCK" in original_st:
            assert "FUNCTION_BLOCK" in recovered_st
        if "PROGRAM" in original_st:
            assert "PROGRAM" in recovered_st
        if "FUNCTION " in original_st and "FUNCTION_BLOCK" not in original_st:
            assert "FUNCTION " in recovered_st
        if "INTERFACE" in original_st:
            assert "INTERFACE" in recovered_st

    @pytest.mark.parametrize("st_filename,xml_filename", MATCHING_ST_XML_PAIRS)
    def test_xml_roundtrip(
        self,
        st_parser,
        xml_generator,
        xml_parser,
        st_generator,
        xml_fixtures_dir,
        st_filename,
        xml_filename,
    ):
        """Test XML -> ST -> XML round-trip preserves key elements."""
        xml_file = xml_fixtures_dir / xml_filename
        if not xml_file.exists():
            pytest.skip(f"Fixture not found: {xml_file}")

        original_xml = xml_file.read_text(encoding="utf-8")

        # XML -> ST
        tc_obj = xml_parser.parse(original_xml)
        st = st_generator.generate(tc_obj)

        # ST -> XML
        parsed = st_parser.parse(st)
        recovered_xml = xml_generator.generate(parsed)

        # Check key elements preserved
        name = xml_filename.split(".")[0]

        # GVLs may get a different name when round-tripped through ST
        # (since ST doesn't encode the GVL name in VAR_GLOBAL blocks)
        if xml_filename.endswith(".TcGVL"):
            # Just verify the GVL structure is preserved
            assert "<GVL" in recovered_xml, (
                f"GVL element not preserved in round-trip for {xml_filename}"
            )
            assert "VAR_GLOBAL" in recovered_xml, (
                f"VAR_GLOBAL not preserved in round-trip for {xml_filename}"
            )
        else:
            assert f'Name="{name}"' in recovered_xml, (
                f"Name not preserved in round-trip for {xml_filename}"
            )

        # Check structural elements
        if "<Declaration>" in original_xml:
            assert "<Declaration>" in recovered_xml
        if "<Implementation>" in original_xml:
            assert "<Implementation>" in recovered_xml


# =============================================================================
# Specific feature tests
# =============================================================================


@pytest.mark.integration
class TestSpecificFeatures:
    """Test specific features across fixture files."""

    def test_extends_preserved_in_fb(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test EXTENDS is preserved through conversion."""
        st_file = st_fixtures_dir / "FB_AlwaysFailure.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "EXTENDS" in recovered_st, "EXTENDS not preserved"

    def test_implements_preserved_in_fb(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test IMPLEMENTS is preserved through conversion."""
        st_file = st_fixtures_dir / "FB_BaseNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "IMPLEMENTS" in recovered_st, "IMPLEMENTS not preserved"

    def test_methods_preserved_in_fb(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test methods are preserved through conversion."""
        st_file = st_fixtures_dir / "FB_WithMethods.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "METHOD" in recovered_st, "METHOD not preserved"

    def test_properties_preserved_in_fb(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test properties are preserved through conversion."""
        st_file = st_fixtures_dir / "FB_WithProperties.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "PROPERTY" in recovered_st, "PROPERTY not preserved"

    def test_interface_methods_preserved(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test interface methods are preserved through conversion."""
        st_file = st_fixtures_dir / "I_TreeNode.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        assert "METHOD" in recovered_st, "Interface methods not preserved"

    def test_var_blocks_preserved(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test VAR blocks are preserved through conversion."""
        st_file = st_fixtures_dir / "FB_Sample.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Check VAR blocks preserved
        if "VAR_INPUT" in original_st:
            assert "VAR_INPUT" in recovered_st, "VAR_INPUT not preserved"
        if "VAR_OUTPUT" in original_st:
            assert "VAR_OUTPUT" in recovered_st, "VAR_OUTPUT not preserved"
        if "VAR\n" in original_st or "VAR\r\n" in original_st:
            assert "VAR" in recovered_st, "VAR not preserved"

    def test_enum_values_preserved(
        self, st_parser, xml_generator, xml_parser, st_generator, st_fixtures_dir
    ):
        """Test enum values are preserved through conversion."""
        st_file = st_fixtures_dir / "E_NodeStatus.st"
        if not st_file.exists():
            pytest.skip(f"Fixture not found: {st_file}")

        original_st = st_file.read_text(encoding="utf-8")

        # ST -> XML -> ST
        parsed = st_parser.parse(original_st)
        xml = xml_generator.generate(parsed)
        tc_obj = xml_parser.parse(xml)
        recovered_st = st_generator.generate(tc_obj)

        # Check type preserved
        assert "E_NodeStatus" in recovered_st, "Enum name not preserved"
