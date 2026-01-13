"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest

# Fixture directories
FIXTURES_DIR = Path(__file__).parent / "fixtures"
ST_FIXTURES_DIR = FIXTURES_DIR / "st"
XML_FIXTURES_DIR = FIXTURES_DIR / "xml"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def st_fixtures_dir() -> Path:
    return ST_FIXTURES_DIR


@pytest.fixture
def xml_fixtures_dir() -> Path:
    return XML_FIXTURES_DIR


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def st_simple_block(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "FB_SimpleBlock.st").read_text(encoding="utf-8")


@pytest.fixture
def st_with_methods(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "FB_WithMethods.st").read_text(encoding="utf-8")


@pytest.fixture
def st_with_properties(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "FB_WithProperties.st").read_text(encoding="utf-8")


@pytest.fixture
def st_edge_cases(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "FB_EdgeCases.st").read_text(encoding="utf-8")


@pytest.fixture
def st_enum(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "E_Status.st").read_text(encoding="utf-8")


@pytest.fixture
def st_struct(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "ST_Data.st").read_text(encoding="utf-8")


@pytest.fixture
def st_gvl(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "GVL_Constants.st").read_text(encoding="utf-8")


@pytest.fixture
def st_interface(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "I_Device.st").read_text(encoding="utf-8")


@pytest.fixture
def st_program(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "PRG_Main.st").read_text(encoding="utf-8")


@pytest.fixture
def st_function(st_fixtures_dir: Path) -> str:
    return (st_fixtures_dir / "FC_Calculate.st").read_text(encoding="utf-8")


@pytest.fixture
def xml_simple_block(xml_fixtures_dir: Path) -> str:
    return (xml_fixtures_dir / "FB_SimpleBlock.TcPOU").read_text(encoding="utf-8")


@pytest.fixture
def xml_with_methods(xml_fixtures_dir: Path) -> str:
    return (xml_fixtures_dir / "FB_WithMethods.TcPOU").read_text(encoding="utf-8")


@pytest.fixture
def xml_enum(xml_fixtures_dir: Path) -> str:
    return (xml_fixtures_dir / "E_Status.TcDUT").read_text(encoding="utf-8")


@pytest.fixture
def xml_gvl(xml_fixtures_dir: Path) -> str:
    return (xml_fixtures_dir / "GVL_Constants.TcGVL").read_text(encoding="utf-8")


@pytest.fixture
def xml_interface(xml_fixtures_dir: Path) -> str:
    return (xml_fixtures_dir / "I_Device.TcIO").read_text(encoding="utf-8")


@pytest.fixture
def st_parser():
    from tc3tools.converters.st_to_xml import STParser

    return STParser()


@pytest.fixture
def xml_parser():
    from tc3tools.converters.xml_to_st import TwinCATXMLParser

    return TwinCATXMLParser()


@pytest.fixture
def st_formatter():
    from tc3tools.formatters.st_formatter import STFormatter

    return STFormatter()


@pytest.fixture
def tcpou_formatter():
    from tc3tools.formatters.xml_formatter import TcPOUFormatter

    return TcPOUFormatter()


@pytest.fixture
def xml_generator():
    from tc3tools.converters.st_to_xml import XMLGenerator

    return XMLGenerator()


@pytest.fixture
def st_generator():
    from tc3tools.converters.xml_to_st import STGenerator

    return STGenerator()
