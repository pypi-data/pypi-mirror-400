#!/usr/bin/env python3
"""
TC3Tools CLI - Unified CLI for TwinCAT operations.

Commands:
  fmt-st      Format and check Structured Text (.st) files.
  fmt-xml     Format TwinCAT XML (.TcPOU) files.
  st2xml      Convert Structured Text to TwinCAT XML.
  xml2st      Convert TwinCAT XML to Structured Text.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tc3tools.converters.st_to_xml import STConverter
from tc3tools.converters.xml_to_st import ConverterService, STGenerator, TwinCATXMLParser
from tc3tools.core.common import LocalFileSystem
from tc3tools.formatters.st_formatter import STFormatter, STSyntaxChecker, STToolService
from tc3tools.formatters.xml_formatter import TcPOUFormatter


def cmd_fmt_st(args: argparse.Namespace) -> int:
    """Handler for fmt-st command."""
    fs = LocalFileSystem()
    checker = STSyntaxChecker()
    formatter = STFormatter()
    service = STToolService(fs, checker, formatter)

    path = Path(args.input).resolve()
    if not path.exists():
        print(f"Error: Input path not found: {path}")
        return 1

    return service.process(path, args.check, args.format, args.inplace)


def cmd_fmt_xml(args: argparse.Namespace) -> int:
    """Handler for fmt-xml command."""
    formatter = TcPOUFormatter()
    path = Path(args.input).resolve()
    if not path.exists():
        print(f"Error: Input path not found: {path}")
        return 1

    return formatter.process(path, args.check)


def cmd_xml2st(args: argparse.Namespace) -> int:
    """Handler for xml2st command."""
    fs = LocalFileSystem()
    parser = TwinCATXMLParser()
    generator = STGenerator()
    service = ConverterService(parser, generator, fs)

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists():
        print(f"Error: Input path not found: {input_path}")
        return 1

    count = service.convert(input_path, output_path)
    print(f"Converted {count} files.")
    return 0 if count > 0 else 1


def cmd_st2xml(args: argparse.Namespace) -> int:
    """Handler for st2xml command."""
    converter = STConverter(ignore_folders=args.ignore)

    input_path = str(Path(args.input).resolve())
    output_path = str(Path(args.output).resolve())

    success = converter.convert(input_path, output_path)
    return 0 if success else 1


def main() -> int:
    """Main entry point for tc3tools CLI."""
    parser = argparse.ArgumentParser(
        description="TC3Tools - Unified CLI for TwinCAT operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # --- fmt-st ---
    p_fmt_st = subparsers.add_parser("fmt-st", help="Format/Check Structured Text (.st)")
    p_fmt_st.add_argument(
        "input", nargs="?", default=".", help="Input file or directory (default: .)"
    )
    p_fmt_st.add_argument("--check", "-c", action="store_true", help="Check syntax only")
    p_fmt_st.add_argument("--format", "-f", action="store_true", help="Format code")
    p_fmt_st.add_argument("--inplace", "-i", action="store_true", help="Modify files in-place")
    p_fmt_st.set_defaults(func=cmd_fmt_st)

    # --- fmt-xml ---
    p_fmt_xml = subparsers.add_parser("fmt-xml", help="Format TwinCAT XML (.TcPOU)")
    p_fmt_xml.add_argument(
        "input", nargs="?", default=".", help="Input file or directory (default: .)"
    )
    p_fmt_xml.add_argument("--check", "-c", action="store_true", help="Check only, do not write")
    p_fmt_xml.set_defaults(func=cmd_fmt_xml)

    # --- xml2st ---
    p_xml2st = subparsers.add_parser("xml2st", help="Convert TwinCAT XML to Structured Text")
    p_xml2st.add_argument(
        "input", nargs="?", default=".", help="Input file or directory (default: .)"
    )
    p_xml2st.add_argument(
        "output",
        nargs="?",
        default="st_export",
        help="Output directory for .st files (default: st_export)",
    )
    p_xml2st.set_defaults(func=cmd_xml2st)

    # --- st2xml ---
    p_st2xml = subparsers.add_parser("st2xml", help="Convert Structured Text to TwinCAT XML")
    p_st2xml.add_argument(
        "input", nargs="?", default=".", help="Input file or directory (default: .)"
    )
    p_st2xml.add_argument(
        "output",
        nargs="?",
        default="tcpou_export",
        help="Output directory for XML files (default: tcpou_export)",
    )
    p_st2xml.add_argument("--ignore", nargs="*", help="Folders to ignore")
    p_st2xml.set_defaults(func=cmd_st2xml)

    args = parser.parse_args()

    # Validate fmt-st args
    if args.command == "fmt-st" and not args.check and not args.format:
        print("Error: fmt-st requires --check or --format")
        return 1

    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
