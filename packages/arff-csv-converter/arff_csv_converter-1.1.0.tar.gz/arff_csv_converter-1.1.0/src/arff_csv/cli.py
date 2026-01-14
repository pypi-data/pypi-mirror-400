"""
Command-line interface for ARFF-CSV converter.

This module provides a command-line interface for converting between
CSV and ARFF file formats.

Usage:
    arff-csv csv2arff input.csv output.arff [options]
    arff-csv csv2arff input.csv --analyze [options]
    arff-csv arff2csv input.arff output.csv [options]
    arff-csv --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

import pandas as pd

from arff_csv import __version__
from arff_csv.converter import ArffConverter
from arff_csv.exceptions import ArffCsvError

# Constants for analysis
DEFAULT_NOMINAL_THRESHOLD = 10  # Max unique values to consider nominal
DEFAULT_PREVIEW_ROWS = 5
BINARY_VALUES = [
    {"0", "1"},
    {"yes", "no"},
    {"true", "false"},
    {"t", "f"},
    {"y", "n"},
    {"si", "no"},
    {"sí", "no"},
]


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="arff-csv",
        description="Convert between CSV and ARFF (Weka) file formats.",
        epilog="For more information, visit: https://github.com/rmontanana/arff-csv-converter",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available conversion commands",
    )

    # CSV to ARFF command
    csv2arff = subparsers.add_parser(
        "csv2arff",
        help="Convert CSV file to ARFF format",
        description="Convert a CSV file to ARFF (Weka) format.",
    )
    csv2arff.add_argument(
        "input",
        type=Path,
        help="Input CSV file path",
    )
    csv2arff.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=None,
        help="Output ARFF file path (not required with --analyze)",
    )
    csv2arff.add_argument(
        "-r",
        "--relation",
        type=str,
        default=None,
        help="Relation name (default: input filename without extension)",
    )
    csv2arff.add_argument(
        "-n",
        "--nominal",
        type=str,
        nargs="+",
        default=None,
        metavar="COL",
        help="Column names to treat as nominal attributes",
    )
    csv2arff.add_argument(
        "-s",
        "--string",
        type=str,
        nargs="+",
        default=None,
        metavar="COL",
        help="Column names to treat as string attributes",
    )
    csv2arff.add_argument(
        "--exclude",
        type=str,
        nargs="+",
        default=None,
        metavar="COL",
        help="Column names to exclude from the conversion",
    )
    csv2arff.add_argument(
        "-m",
        "--missing",
        type=str,
        default="?",
        help="Missing value representation (default: ?)",
    )
    csv2arff.add_argument(
        "-c",
        "--comment",
        type=str,
        nargs="+",
        default=None,
        help="Comments to add to the ARFF file",
    )
    csv2arff.add_argument(
        "--delimiter",
        type=str,
        default=",",
        help="CSV delimiter (default: ,)",
    )
    csv2arff.add_argument(
        "--encoding",
        type=str,
        default="utf-8",
        help="CSV file encoding (default: utf-8)",
    )
    csv2arff.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    # Analysis options
    csv2arff.add_argument(
        "-a",
        "--analyze",
        action="store_true",
        help="Analyze CSV and suggest column types (does not convert)",
    )
    csv2arff.add_argument(
        "--preview-rows",
        type=int,
        default=DEFAULT_PREVIEW_ROWS,
        metavar="N",
        help=f"Number of rows to preview in analysis (default: {DEFAULT_PREVIEW_ROWS})",
    )
    csv2arff.add_argument(
        "--nominal-threshold",
        type=int,
        default=DEFAULT_NOMINAL_THRESHOLD,
        metavar="N",
        help=f"Max unique values to consider a column as nominal (default: {DEFAULT_NOMINAL_THRESHOLD})",
    )

    # ARFF to CSV command
    arff2csv = subparsers.add_parser(
        "arff2csv",
        help="Convert ARFF file to CSV format",
        description="Convert an ARFF (Weka) file to CSV format.",
    )
    arff2csv.add_argument(
        "input",
        type=Path,
        help="Input ARFF file path",
    )
    arff2csv.add_argument(
        "output",
        type=Path,
        help="Output CSV file path",
    )
    arff2csv.add_argument(
        "-m",
        "--missing",
        type=str,
        default="?",
        help="Missing value representation (default: ?)",
    )
    arff2csv.add_argument(
        "--delimiter",
        type=str,
        default=",",
        help="CSV delimiter (default: ,)",
    )
    arff2csv.add_argument(
        "--encoding",
        type=str,
        default="utf-8",
        help="Output CSV file encoding (default: utf-8)",
    )
    arff2csv.add_argument(
        "--include-index",
        action="store_true",
        help="Include row index in the CSV output",
    )
    arff2csv.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    # Info command
    info = subparsers.add_parser(
        "info",
        help="Display information about an ARFF file",
        description="Display detailed information about an ARFF file.",
    )
    info.add_argument(
        "input",
        type=Path,
        help="Input ARFF file path",
    )
    info.add_argument(
        "-m",
        "--missing",
        type=str,
        default="?",
        help="Missing value representation (default: ?)",
    )

    return parser


def analyze_column(
    series: pd.Series,
    col_name: str,
    nominal_threshold: int,
    total_rows: int | None = None,
) -> dict:
    """Analyze a single column and determine its suggested type."""
    result = {
        "name": col_name,
        "dtype": str(series.dtype),
        "non_null": series.count(),
        "null_count": series.isna().sum(),
        "unique_count": series.nunique(),
        "suggested_type": "NUMERIC",
        "reason": "",
        "sample_values": [],
        "exclude_suggested": False,
        "exclude_reason": None,
    }

    # Get sample values (non-null)
    non_null = series.dropna()
    if len(non_null) > 0:
        sample = non_null.head(5).tolist()
        result["sample_values"] = [str(v) for v in sample]

    unique_count = cast("int", result["unique_count"])
    non_null_count = cast("int", result["non_null"])
    total_rows_int = len(series) if total_rows is None else int(total_rows)

    # Check if column is numeric
    is_numeric = pd.api.types.is_numeric_dtype(series)

    # Exclusion suggestions
    if total_rows_int > 0 and unique_count <= 1:
        result["exclude_suggested"] = True
        result["exclude_reason"] = "Single unique value"
    elif total_rows_int > 0 and non_null_count == total_rows_int and unique_count == total_rows_int:
        result["exclude_suggested"] = True
        result["exclude_reason"] = "Unique value for every row"

    # Check for binary/boolean patterns (case-insensitive)
    if len(non_null) > 0:
        normalized_unique = {str(v).lower().strip() for v in non_null.unique()}
        if len(normalized_unique) <= 2:
            for binary_set in BINARY_VALUES:
                if normalized_unique.issubset(binary_set):
                    result["suggested_type"] = "NOMINAL"
                    result["reason"] = "Binary values detected"
                    return result

    # Check for "class" or "target" columns (common in ML datasets)
    col_lower = col_name.lower()
    if col_lower in ("class", "target", "label", "y", "clase", "etiqueta"):
        result["suggested_type"] = "NOMINAL"
        result["reason"] = "Common target/class column name"
        return result

    # For numeric columns
    if is_numeric:
        # Check if it looks like categorical integers
        if (
            pd.api.types.is_integer_dtype(series)
            or (
                pd.api.types.is_float_dtype(series)
                and all(v == int(v) for v in non_null if pd.notna(v))
            )
        ) and unique_count <= nominal_threshold:
            result["suggested_type"] = "NOMINAL"
            result["reason"] = f"Integer with {unique_count} unique values (≤ {nominal_threshold})"
            return result

        # It's a regular numeric column
        if pd.api.types.is_integer_dtype(series):
            result["suggested_type"] = "INTEGER"
            result["reason"] = "Integer values"
        else:
            result["suggested_type"] = "NUMERIC"
            result["reason"] = "Floating point values"
        return result

    # For string/object columns
    if series.dtype == object:
        avg_len = non_null.astype(str).str.len().mean() if len(non_null) > 0 else 0
        # Long text should be treated as string even with few unique values
        if avg_len > 50:
            result["suggested_type"] = "STRING"
            result["reason"] = f"Long text (avg {avg_len:.0f} chars)"
            return result

        # Check if should be nominal
        if unique_count <= nominal_threshold:
            result["suggested_type"] = "NOMINAL"
            result["reason"] = (
                f"Categorical with {unique_count} unique values (≤ {nominal_threshold})"
            )
        else:
            result["suggested_type"] = "STRING"
            result["reason"] = f"Text with {unique_count} unique values (> {nominal_threshold})"
        return result

    # Default
    result["suggested_type"] = "STRING"
    result["reason"] = f"Unknown dtype: {series.dtype}"
    return result


def cmd_analyze_csv(args: argparse.Namespace) -> int:
    """Analyze CSV and suggest column types."""
    try:
        # Read CSV
        df = pd.read_csv(
            args.input,
            sep=args.delimiter,
            encoding=args.encoding,
        )
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        return 1

    df = ArffConverter._normalize_unnamed_columns(df)

    print("=" * 70)
    print(f"CSV ANALYSIS: {args.input}")
    print("=" * 70)
    print()

    # Basic info
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print()

    # Preview
    print(f"DATA PREVIEW (first {args.preview_rows} rows):")
    print("-" * 70)
    print(df.head(args.preview_rows).to_string())
    print()

    # Analyze each column
    print("COLUMN ANALYSIS:")
    print("-" * 70)

    analyses = []
    for col in df.columns:
        analysis = analyze_column(
            df[col],
            col,
            args.nominal_threshold,
            total_rows=len(df),
        )
        analyses.append(analysis)

    # Print analysis in a formatted table
    print(f"{'Column':<25} {'Type':<10} {'Unique':<8} {'Nulls':<8} {'Reason'}")
    print("-" * 70)

    for a in analyses:
        print(
            f"{a['name']:<25} "
            f"{a['suggested_type']:<10} "
            f"{a['unique_count']:<8} "
            f"{a['null_count']:<8} "
            f"{a['reason']}"
        )

    exclude_suggestions = [a for a in analyses if a.get("exclude_suggested")]

    # Collect nominal and string columns
    nominal_cols = [a["name"] for a in analyses if a["suggested_type"] == "NOMINAL"]
    string_cols = [a["name"] for a in analyses if a["suggested_type"] == "STRING"]

    if exclude_suggestions:
        print()
        print("COLUMNS SUGGESTED FOR EXCLUSION:")
        print("-" * 70)
        for a in exclude_suggestions:
            reason = a.get("exclude_reason") or "Suggested for exclusion"
            print(f"  - {a['name']}: {reason}")

    print()
    print("SUGGESTED COMMAND:")
    print("-" * 70)

    # Build command
    output_name = args.output if args.output else args.input.with_suffix(".arff")
    cmd_parts = ["arff-csv", "csv2arff", str(args.input), str(output_name)]

    if args.relation:
        cmd_parts.extend(["--relation", f'"{args.relation}"'])
    else:
        cmd_parts.extend(["--relation", f'"{args.input.stem}"'])

    if nominal_cols:
        cmd_parts.extend(["--nominal", *nominal_cols])

    if string_cols:
        cmd_parts.extend(["--string", *string_cols])

    exclude_cols = []
    if args.exclude:
        exclude_cols.extend(args.exclude)
    if exclude_suggestions:
        for a in exclude_suggestions:
            if a["name"] not in exclude_cols:
                exclude_cols.append(a["name"])
    if exclude_cols:
        cmd_parts.extend(["--exclude", *exclude_cols])

    if args.delimiter != ",":
        cmd_parts.extend(["--delimiter", f'"{args.delimiter}"'])

    if args.encoding != "utf-8":
        cmd_parts.extend(["--encoding", args.encoding])

    print()
    print(" \\\n    ".join(_split_command(cmd_parts)))
    print()

    # Summary
    print("SUMMARY:")
    print("-" * 70)
    numeric_count = len([a for a in analyses if a["suggested_type"] in ("NUMERIC", "INTEGER")])
    print(f"  Numeric columns:  {numeric_count}")
    print(f"  Nominal columns:  {len(nominal_cols)}")
    print(f"  String columns:   {len(string_cols)}")
    if exclude_suggestions:
        print(f"  Suggested excludes: {len(exclude_suggestions)}")

    if nominal_cols:
        print(f"\n  Nominal: {', '.join(nominal_cols)}")
    if string_cols:
        print(f"  String:  {', '.join(string_cols)}")
    if exclude_suggestions:
        exclude_names = [a["name"] for a in exclude_suggestions]
        print(f"  Exclude: {', '.join(exclude_names)}")

    print()

    return 0


def _split_command(parts: list[str], max_line_len: int = 70) -> list[str]:
    """Split command into multiple lines for readability."""
    lines: list[str] = []
    current_line: list[str] = []
    current_len = 0

    for part in parts:
        part_len = len(part) + 1  # +1 for space
        if current_len + part_len > max_line_len and current_line:
            lines.append(" ".join(current_line))
            current_line = [part]
            current_len = part_len
        else:
            current_line.append(part)
            current_len += part_len

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def cmd_csv2arff(args: argparse.Namespace) -> int:
    """Execute the csv2arff command."""
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Handle analyze mode
    if args.analyze:
        # Check for incompatible options
        if args.nominal or args.string:
            print("Error: --analyze cannot be used with --nominal or --string", file=sys.stderr)
            return 1
        return cmd_analyze_csv(args)

    # Normal conversion mode - output is required
    if args.output is None:
        print("Error: Output file is required for conversion", file=sys.stderr)
        print("Use --analyze to analyze the CSV without converting", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"Converting {args.input} to {args.output}...")

    try:
        converter = ArffConverter(missing_value=args.missing)
        arff_data = converter.csv_to_arff(
            csv_path=args.input,
            arff_path=args.output,
            relation_name=args.relation,
            nominal_columns=args.nominal,
            string_columns=args.string,
            comments=args.comment,
            sep=args.delimiter,
            encoding=args.encoding,
            exclude_columns=args.exclude,
        )

        if args.verbose:
            print("Successfully converted to ARFF format.")
            print(f"  Relation: {arff_data.relation_name}")
            print(f"  Attributes: {len(arff_data.attributes)}")
            print(f"  Instances: {len(arff_data.data)}")

        return 0

    except ArffCsvError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def cmd_arff2csv(args: argparse.Namespace) -> int:
    """Execute the arff2csv command."""
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"Converting {args.input} to {args.output}...")

    try:
        converter = ArffConverter(missing_value=args.missing)
        df = converter.arff_to_csv(
            arff_path=args.input,
            csv_path=args.output,
            include_index=args.include_index,
            sep=args.delimiter,
            encoding=args.encoding,
        )

        if args.verbose:
            print("Successfully converted to CSV format.")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Rows: {len(df)}")

        return 0

    except ArffCsvError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """Execute the info command."""
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        from arff_csv.parser import ArffParser

        parser = ArffParser(missing_value=args.missing)
        arff_data = parser.parse_file(args.input)

        print(f"ARFF File: {args.input}")
        print(f"Relation: {arff_data.relation_name}")
        print(f"Instances: {len(arff_data.data)}")
        print(f"Attributes: {len(arff_data.attributes)}")
        print()

        print("Attribute Information:")
        print("-" * 60)
        for attr in arff_data.attributes:
            type_str = attr.type.name
            if attr.nominal_values:
                values_preview = ", ".join(attr.nominal_values[:5])
                if len(attr.nominal_values) > 5:
                    values_preview += f", ... ({len(attr.nominal_values)} total)"
                type_str = f"NOMINAL {{{values_preview}}}"
            elif attr.date_format:
                type_str = f"DATE '{attr.date_format}'"

            print(f"  {attr.name}: {type_str}")

        print()
        print("Data Preview (first 5 rows):")
        print("-" * 60)
        print(arff_data.data.head().to_string())

        if arff_data.comments:
            print()
            print("Comments:")
            print("-" * 60)
            for comment in arff_data.comments[:10]:
                print(f"  % {comment}")
            if len(arff_data.comments) > 10:
                print(f"  ... and {len(arff_data.comments) - 10} more comments")

        return 0

    except ArffCsvError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (uses sys.argv if None).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.command is None:
        parser.print_help()
        return 0

    if parsed_args.command == "csv2arff":
        return cmd_csv2arff(parsed_args)
    elif parsed_args.command == "arff2csv":
        return cmd_arff2csv(parsed_args)
    elif parsed_args.command == "info":
        return cmd_info(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
