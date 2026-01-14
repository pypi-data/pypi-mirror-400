"""
Tests for the CSV analyze functionality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from arff_csv.cli import DEFAULT_NOMINAL_THRESHOLD, analyze_column, main

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


class TestAnalyzeColumn:
    """Tests for the analyze_column function."""

    def test_analyze_numeric_float(self) -> None:
        """Test analysis of float column."""
        series = pd.Series([1.5, 2.7, 3.9, 4.1, 5.3])
        result = analyze_column(series, "value", DEFAULT_NOMINAL_THRESHOLD)

        assert result["name"] == "value"
        assert result["suggested_type"] == "NUMERIC"
        assert result["unique_count"] == 5
        assert "Floating point" in result["reason"]

    def test_analyze_numeric_integer(self) -> None:
        """Test analysis of integer column with many values."""
        series = pd.Series(list(range(100)))
        result = analyze_column(series, "count", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "INTEGER"
        assert "Integer values" in result["reason"]

    def test_analyze_binary_01(self) -> None:
        """Test analysis of binary 0/1 column."""
        series = pd.Series([0, 1, 0, 1, 0, 1])
        result = analyze_column(series, "flag", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "Binary" in result["reason"]

    def test_analyze_binary_yes_no(self) -> None:
        """Test analysis of yes/no column."""
        series = pd.Series(["yes", "no", "yes", "no"])
        result = analyze_column(series, "response", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "Binary" in result["reason"]

    def test_analyze_binary_true_false(self) -> None:
        """Test analysis of true/false column."""
        series = pd.Series(["True", "False", "true", "FALSE"])
        result = analyze_column(series, "active", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "Binary" in result["reason"]

    def test_analyze_class_column(self) -> None:
        """Test analysis of column named 'class'."""
        series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        result = analyze_column(series, "class", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "target/class" in result["reason"].lower()

    def test_analyze_target_column(self) -> None:
        """Test analysis of column named 'target'."""
        series = pd.Series(list(range(20)))
        result = analyze_column(series, "target", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "target/class" in result["reason"].lower()

    def test_analyze_label_column(self) -> None:
        """Test analysis of column named 'label'."""
        series = pd.Series(["a", "b", "c"] * 10)
        result = analyze_column(series, "label", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"

    def test_analyze_categorical_integer(self) -> None:
        """Test analysis of integer column with few unique values."""
        series = pd.Series([1, 2, 3, 1, 2, 3, 1, 2, 3])
        result = analyze_column(series, "category", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "unique values" in result["reason"]

    def test_analyze_categorical_string(self) -> None:
        """Test analysis of string column with few unique values."""
        series = pd.Series(["A", "B", "C", "A", "B", "C"])
        result = analyze_column(series, "category", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "Categorical" in result["reason"]

    def test_analyze_string_many_unique(self) -> None:
        """Test analysis of string column with many unique values."""
        series = pd.Series([f"text_{i}" for i in range(50)])
        result = analyze_column(series, "description", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "STRING"
        assert "unique values" in result["reason"]

    def test_analyze_string_long_text(self) -> None:
        """Test analysis of string column with long text."""
        series = pd.Series(["x" * 100, "y" * 100, "z" * 100])
        result = analyze_column(series, "content", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "STRING"
        assert "Long text" in result["reason"]

    def test_analyze_with_nulls(self) -> None:
        """Test analysis of column with null values."""
        series = pd.Series([1.0, 2.0, None, 4.0, None])
        result = analyze_column(series, "value", DEFAULT_NOMINAL_THRESHOLD)

        assert result["null_count"] == 2
        assert result["non_null"] == 3

    def test_analyze_custom_threshold(self) -> None:
        """Test analysis with custom nominal threshold."""
        series = pd.Series([1, 2, 3, 4, 5, 1, 2, 3, 4, 5])  # 5 unique values

        # With threshold=3, should NOT be nominal
        result = analyze_column(series, "value", nominal_threshold=3)
        assert result["suggested_type"] == "INTEGER"

        # With threshold=10, should be nominal
        result = analyze_column(series, "value", nominal_threshold=10)
        assert result["suggested_type"] == "NOMINAL"

    def test_analyze_float_as_integer(self) -> None:
        """Test analysis of float column with integer values."""
        series = pd.Series([1.0, 2.0, 3.0, 1.0, 2.0])  # Floats that are whole numbers
        result = analyze_column(series, "value", DEFAULT_NOMINAL_THRESHOLD)

        # Should detect as nominal since unique count is low and values are whole numbers
        assert result["suggested_type"] == "NOMINAL"

    def test_analyze_sample_values(self) -> None:
        """Test that sample values are captured."""
        series = pd.Series(["apple", "banana", "cherry", "date", "elderberry", "fig"])
        result = analyze_column(series, "fruit", DEFAULT_NOMINAL_THRESHOLD)

        assert len(result["sample_values"]) == 5
        assert "apple" in result["sample_values"]


class TestAnalyzeCLI:
    """Tests for the --analyze CLI option."""

    def test_analyze_basic(self, temp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test basic analyze functionality."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b,c,class\n1,1.5,hello,0\n2,2.5,world,1\n3,3.5,foo,0")

        result = main(["csv2arff", str(csv_path), "--analyze"])

        assert result == 0
        captured = capsys.readouterr()
        assert "CSV ANALYSIS" in captured.out
        assert "COLUMN ANALYSIS" in captured.out
        assert "SUGGESTED COMMAND" in captured.out

    def test_analyze_detects_nominal(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that analyze correctly detects nominal columns."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("flag,category,class\n0,A,1\n1,B,2\n0,A,1\n1,C,0")

        result = main(["csv2arff", str(csv_path), "--analyze"])

        assert result == 0
        captured = capsys.readouterr()
        assert "--nominal" in captured.out
        assert "class" in captured.out

    def test_analyze_detects_binary(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that analyze correctly detects binary columns."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("active,value\nyes,10\nno,20\nyes,30")

        result = main(["csv2arff", str(csv_path), "--analyze"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Binary" in captured.out
        assert "NOMINAL" in captured.out

    def test_analyze_preview_rows(self, temp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test --preview-rows option."""
        csv_path = temp_dir / "test.csv"
        lines = ["a,b"] + [f"{i},{i * 2}" for i in range(20)]
        csv_path.write_text("\n".join(lines))

        result = main(["csv2arff", str(csv_path), "--analyze", "--preview-rows", "3"])

        assert result == 0
        captured = capsys.readouterr()
        assert "first 3 rows" in captured.out

    def test_analyze_nominal_threshold(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test --nominal-threshold option."""
        csv_path = temp_dir / "test.csv"
        # Column with 5 unique values
        csv_path.write_text("cat\n1\n2\n3\n4\n5\n1\n2\n3")

        # With threshold=3, should NOT suggest as nominal
        result = main(["csv2arff", str(csv_path), "--analyze", "--nominal-threshold", "3"])

        assert result == 0
        captured = capsys.readouterr()
        # Should be INTEGER, not NOMINAL
        assert "INTEGER" in captured.out

    def test_analyze_with_output_path(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test analyze with output path specified."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,2\n3,4")
        output_path = temp_dir / "output.arff"

        result = main(["csv2arff", str(csv_path), str(output_path), "--analyze"])

        assert result == 0
        captured = capsys.readouterr()
        # Should show output path in suggested command
        assert "output.arff" in captured.out

    def test_analyze_error_with_nominal_option(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that --analyze cannot be used with --nominal."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,2")

        result = main(["csv2arff", str(csv_path), "--analyze", "--nominal", "a"])

        assert result == 1
        captured = capsys.readouterr()
        assert "cannot be used" in captured.err

    def test_analyze_error_with_string_option(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that --analyze cannot be used with --string."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,2")

        result = main(["csv2arff", str(csv_path), "--analyze", "--string", "a"])

        assert result == 1
        captured = capsys.readouterr()
        assert "cannot be used" in captured.err

    def test_analyze_file_not_found(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test analyze with non-existent file."""
        result = main(["csv2arff", "/nonexistent/file.csv", "--analyze"])

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_analyze_shows_summary(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that analyze shows summary section."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("num,cat,text,class\n1.5,A,hello,0\n2.5,B,world,1")

        result = main(["csv2arff", str(csv_path), "--analyze"])

        assert result == 0
        captured = capsys.readouterr()
        assert "SUMMARY" in captured.out
        assert "Numeric columns" in captured.out
        assert "Nominal columns" in captured.out
        assert "String columns" in captured.out

    def test_analyze_with_custom_delimiter(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test analyze with custom delimiter."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a;b;c\n1;2;3\n4;5;6")

        result = main(["csv2arff", str(csv_path), "--analyze", "--delimiter", ";"])

        assert result == 0
        captured = capsys.readouterr()
        assert "CSV ANALYSIS" in captured.out
        assert '--delimiter ";"' in captured.out

    def test_analyze_with_relation(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test analyze with --relation option."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,2")

        result = main(["csv2arff", str(csv_path), "--analyze", "--relation", "my_dataset"])

        assert result == 0
        captured = capsys.readouterr()
        assert '"my_dataset"' in captured.out

    def test_analyze_string_columns_detected(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that string columns are properly detected."""
        csv_path = temp_dir / "test.csv"
        # Create unique long text values
        lines = ["description,value"]
        for i in range(20):
            lines.append(f"unique_description_{i}_{'x' * 50},{i}")
        csv_path.write_text("\n".join(lines))

        result = main(["csv2arff", str(csv_path), "--analyze"])

        assert result == 0
        captured = capsys.readouterr()
        assert "STRING" in captured.out
        assert "--string" in captured.out

    def test_conversion_without_output_fails(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that conversion without output file fails (without --analyze)."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,2")

        result = main(["csv2arff", str(csv_path)])

        assert result == 1
        captured = capsys.readouterr()
        assert "Output file is required" in captured.err

    def test_analyze_invalid_csv(self, temp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test analyze with invalid CSV file."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_bytes(b"\xff\xfe")  # Invalid UTF-8

        result = main(["csv2arff", str(csv_path), "--analyze"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err


class TestAnalyzeEdgeCases:
    """Edge case tests for analyze functionality."""

    def test_analyze_empty_column(self) -> None:
        """Test analysis of column with all null values."""
        series = pd.Series([None, None, None])
        result = analyze_column(series, "empty", DEFAULT_NOMINAL_THRESHOLD)

        assert result["null_count"] == 3
        assert result["non_null"] == 0
        assert len(result["sample_values"]) == 0

    def test_analyze_single_value(self) -> None:
        """Test analysis of column with single unique value."""
        series = pd.Series([42, 42, 42, 42])
        result = analyze_column(series, "constant", DEFAULT_NOMINAL_THRESHOLD)

        assert result["unique_count"] == 1
        # Single value should be nominal (constant)
        assert result["suggested_type"] == "NOMINAL"

    def test_analyze_mixed_case_binary(self) -> None:
        """Test analysis of binary column with mixed case."""
        series = pd.Series(["Yes", "NO", "yes", "No", "YES", "no"])
        result = analyze_column(series, "response", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "Binary" in result["reason"]

    def test_analyze_spanish_binary(self) -> None:
        """Test analysis of Spanish si/no binary column."""
        series = pd.Series(["si", "no", "si", "no"])
        result = analyze_column(series, "respuesta", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "Binary" in result["reason"]

    def test_analyze_column_named_y(self) -> None:
        """Test analysis of column named 'y' (common target name)."""
        series = pd.Series(list(range(100)))
        result = analyze_column(series, "y", DEFAULT_NOMINAL_THRESHOLD)

        assert result["suggested_type"] == "NOMINAL"
        assert "target/class" in result["reason"].lower()
