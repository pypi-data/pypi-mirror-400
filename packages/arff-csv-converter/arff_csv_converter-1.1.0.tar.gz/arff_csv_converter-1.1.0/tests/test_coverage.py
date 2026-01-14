"""
Additional tests for increased code coverage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest

from arff_csv.cli import main
from arff_csv.converter import ArffConverter
from arff_csv.exceptions import ArffParseError, CsvParseError
from arff_csv.parser import ArffParser, AttributeType
from arff_csv.writer import ArffWriter

if TYPE_CHECKING:
    from pathlib import Path


class TestCLICoverage:
    """Additional CLI tests for coverage."""

    def test_csv2arff_arff_error(self, temp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test csv2arff with ArffCsvError (invalid CSV)."""
        # Create an invalid CSV that will cause a parsing error
        csv_path = temp_dir / "invalid.csv"
        csv_path.write_text("a,b,c\n1,2\n3,4,5,6")  # Inconsistent columns

        output_path = temp_dir / "output.arff"

        result = main(
            [
                "csv2arff",
                str(csv_path),
                str(output_path),
            ]
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err or "error" in captured.err.lower()

    def test_arff2csv_arff_error(self, temp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test arff2csv with ArffCsvError (invalid ARFF)."""
        # Create an invalid ARFF
        arff_path = temp_dir / "invalid.arff"
        arff_path.write_text("@RELATION test\n@DATA\n")  # No attributes, empty data

        output_path = temp_dir / "output.csv"

        result = main(
            [
                "arff2csv",
                str(arff_path),
                str(output_path),
            ]
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_info_with_many_nominal_values(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test info command with nominal attribute having >5 values."""
        arff_content = """@RELATION test
@ATTRIBUTE category {val1, val2, val3, val4, val5, val6, val7}
@DATA
val1
val2
val3
"""
        arff_path = temp_dir / "many_nominal.arff"
        arff_path.write_text(arff_content)

        result = main(["info", str(arff_path)])

        assert result == 0
        captured = capsys.readouterr()
        assert "... (7 total)" in captured.out

    def test_info_with_date_format(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test info command with date attribute having format."""
        arff_content = """@RELATION test
@ATTRIBUTE event_date DATE 'yyyy-MM-dd'
@ATTRIBUTE value NUMERIC
@DATA
'2024-01-15',100
"""
        arff_path = temp_dir / "date_format.arff"
        arff_path.write_text(arff_content)

        result = main(["info", str(arff_path)])

        assert result == 0
        captured = capsys.readouterr()
        assert "DATE 'yyyy-MM-dd'" in captured.out

    def test_info_with_many_comments(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test info command with more than 10 comments."""
        comments = "\n".join([f"% Comment {i}" for i in range(15)])
        arff_content = f"""{comments}
@RELATION test
@ATTRIBUTE a NUMERIC
@DATA
1
"""
        arff_path = temp_dir / "many_comments.arff"
        arff_path.write_text(arff_content)

        result = main(["info", str(arff_path)])

        assert result == 0
        captured = capsys.readouterr()
        assert "... and 5 more comments" in captured.out

    def test_info_arff_parse_error(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test info command with invalid ARFF file."""
        arff_path = temp_dir / "invalid.arff"
        arff_path.write_text("@RELATION test\n@DATA\n")

        result = main(["info", str(arff_path)])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_csv2arff_with_string_columns(self, temp_dir: Path) -> None:
        """Test csv2arff with string columns option."""
        csv_path = temp_dir / "input.csv"
        csv_path.write_text("id,name,desc\n1,Alice,Hello\n2,Bob,World")

        output_path = temp_dir / "output.arff"

        result = main(
            [
                "csv2arff",
                str(csv_path),
                str(output_path),
                "-s",
                "name",
                "desc",
            ]
        )

        assert result == 0
        content = output_path.read_text()
        assert "STRING" in content

    def test_csv2arff_unexpected_error(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test csv2arff with unexpected error."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,2")
        output_path = temp_dir / "output.arff"

        # Mock to raise an unexpected error
        def mock_csv_to_arff(*_args, **_kwargs):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(ArffConverter, "csv_to_arff", mock_csv_to_arff)

        result = main(
            [
                "csv2arff",
                str(csv_path),
                str(output_path),
            ]
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err

    def test_arff2csv_unexpected_error(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test arff2csv with unexpected error."""
        arff_path = temp_dir / "test.arff"
        arff_path.write_text("@RELATION test\n@ATTRIBUTE a NUMERIC\n@DATA\n1")
        output_path = temp_dir / "output.csv"

        # Mock to raise an unexpected error
        def mock_arff_to_csv(*_args, **_kwargs):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(ArffConverter, "arff_to_csv", mock_arff_to_csv)

        result = main(
            [
                "arff2csv",
                str(arff_path),
                str(output_path),
            ]
        )

        assert result == 1
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err

    def test_info_unexpected_error(
        self, temp_dir: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test info command with unexpected error."""
        arff_path = temp_dir / "test.arff"
        arff_path.write_text("@RELATION test\n@ATTRIBUTE a NUMERIC\n@DATA\n1")

        # Mock to raise an unexpected error
        def mock_parse_file(*_args, **_kwargs):
            raise RuntimeError("Unexpected error")

        monkeypatch.setattr(ArffParser, "parse_file", mock_parse_file)

        result = main(["info", str(arff_path)])

        assert result == 1
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err


class TestConverterCoverage:
    """Additional converter tests for coverage."""

    def test_csv_to_arff_string_with_comments(self, sample_csv_file: Path) -> None:
        """Test csv_to_arff_string with comments."""
        converter = ArffConverter()
        comments = ["Test comment 1", "Test comment 2"]

        content = converter.csv_to_arff_string(
            sample_csv_file,
            relation_name="test",
            comments=comments,
        )

        assert "% Test comment 1" in content
        assert "% Test comment 2" in content

    def test_csv_to_arff_string_file_not_found(self) -> None:
        """Test csv_to_arff_string with non-existent file."""
        converter = ArffConverter()

        with pytest.raises(FileNotFoundError):
            converter.csv_to_arff_string("/nonexistent/file.csv")

    def test_csv_to_arff_string_csv_error(self, temp_dir: Path) -> None:
        """Test csv_to_arff_string with CSV parse error."""
        csv_path = temp_dir / "bad.csv"
        csv_path.write_text("a,b\n1,2,3,4,5")  # Too many columns

        converter = ArffConverter()

        with pytest.raises(CsvParseError):
            converter.csv_to_arff_string(csv_path)

    def test_dataframe_to_arff_with_comments(
        self, sample_dataframe: pd.DataFrame, temp_dir: Path
    ) -> None:
        """Test dataframe_to_arff with comments."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"
        comments = ["DataFrame conversion", "With comments"]

        arff_data = converter.dataframe_to_arff(
            sample_dataframe,
            output_path,
            relation_name="test",
            comments=comments,
        )

        assert arff_data.comments == comments
        content = output_path.read_text()
        assert "% DataFrame conversion" in content

    def test_dataframe_to_arff_string_with_comments(self, sample_dataframe: pd.DataFrame) -> None:
        """Test dataframe_to_arff_string with comments."""
        converter = ArffConverter()
        comments = ["String conversion", "With comments"]

        content = converter.dataframe_to_arff_string(
            sample_dataframe,
            relation_name="test",
            comments=comments,
        )

        assert "% String conversion" in content

    def test_csv_to_arff_with_date_columns(self, temp_dir: Path) -> None:
        """Test csv_to_arff with date columns."""
        csv_path = temp_dir / "dates.csv"
        csv_path.write_text("date,value\n2024-01-15,100\n2024-02-20,200")

        output_path = temp_dir / "dates.arff"

        converter = ArffConverter()
        arff_data = converter.csv_to_arff(
            csv_path,
            output_path,
            date_columns={"date": "%Y-%m-%d"},
        )

        date_attr = next(a for a in arff_data.attributes if a.name == "date")
        assert date_attr.type == AttributeType.DATE

    def test_csv_to_arff_string_with_date_columns(self, temp_dir: Path) -> None:
        """Test csv_to_arff_string with date columns."""
        csv_path = temp_dir / "dates.csv"
        csv_path.write_text("date,value\n2024-01-15,100\n2024-02-20,200")

        converter = ArffConverter()
        content = converter.csv_to_arff_string(
            csv_path,
            date_columns={"date": "%Y-%m-%d"},
        )

        assert "@ATTRIBUTE date DATE" in content

    def test_csv_to_arff_string_with_string_columns(self, temp_dir: Path) -> None:
        """Test csv_to_arff_string with string columns."""
        csv_path = temp_dir / "strings.csv"
        csv_path.write_text("name,value\nAlice,100\nBob,200")

        converter = ArffConverter()
        content = converter.csv_to_arff_string(
            csv_path,
            string_columns=["name"],
        )

        assert "@ATTRIBUTE name STRING" in content

    def test_csv_to_arff_string_with_nominal_columns(self, temp_dir: Path) -> None:
        """Test csv_to_arff_string with nominal columns."""
        csv_path = temp_dir / "nominal.csv"
        csv_path.write_text("category,value\nA,100\nB,200\nA,300")

        converter = ArffConverter()
        content = converter.csv_to_arff_string(
            csv_path,
            nominal_columns=["category"],
        )

        assert "{A, B}" in content


class TestParserCoverage:
    """Additional parser tests for coverage."""

    def test_parse_nominal_with_quoted_values(self) -> None:
        """Test parsing nominal values with quotes."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE category {"value with spaces", 'another value', simple}
@DATA
'value with spaces'
'another value'
simple
"""
        arff_data = parser.parse_string(content)
        assert "value with spaces" in arff_data.attributes[0].nominal_values

    def test_parse_date_without_format(self) -> None:
        """Test parsing DATE attribute without explicit format."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE event_date DATE
@DATA
2024-01-15
"""
        arff_data = parser.parse_string(content)
        assert arff_data.attributes[0].type == AttributeType.DATE
        assert arff_data.attributes[0].date_format is None

    def test_parse_sparse_invalid_index(self) -> None:
        """Test parsing sparse format with invalid (non-numeric) index."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE a NUMERIC
@ATTRIBUTE b NUMERIC
@DATA
{abc 1.0}
"""
        with pytest.raises(ArffParseError, match="Invalid sparse index"):
            parser.parse_string(content)

    def test_parse_sparse_out_of_range(self) -> None:
        """Test parsing sparse format with out of range index."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE a NUMERIC
@ATTRIBUTE b NUMERIC
@DATA
{10 1.0}
"""
        with pytest.raises(ArffParseError, match="out of range"):
            parser.parse_string(content)

    def test_parse_sparse_invalid_format(self) -> None:
        """Test parsing sparse format with invalid pair format."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE a NUMERIC
@ATTRIBUTE b NUMERIC
@DATA
{0}
"""
        with pytest.raises(ArffParseError, match="Invalid sparse format"):
            parser.parse_string(content)

    def test_parse_attribute_unclosed_quote(self) -> None:
        """Test parsing attribute with unclosed quote."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE 'unclosed NUMERIC
@DATA
"""
        with pytest.raises(ArffParseError, match="Unclosed quote"):
            parser.parse_string(content)

    def test_parse_attribute_missing_type(self) -> None:
        """Test parsing attribute without type."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE name_only
@DATA
"""
        with pytest.raises(ArffParseError, match="missing type"):
            parser.parse_string(content)

    def test_parse_unknown_directive(self) -> None:
        """Test parsing unknown @ directive."""
        parser = ArffParser()
        content = """
@RELATION test
@UNKNOWN_DIRECTIVE something
@ATTRIBUTE a NUMERIC
@DATA
1
"""
        with pytest.raises(ArffParseError, match="Unknown directive"):
            parser.parse_string(content)

    def test_parse_empty_sparse_row(self) -> None:
        """Test parsing empty sparse row."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE a NUMERIC
@ATTRIBUTE b NUMERIC
@DATA
{}
"""
        arff_data = parser.parse_string(content)
        assert pd.isna(arff_data.data.iloc[0]["a"])
        assert pd.isna(arff_data.data.iloc[0]["b"])

    def test_parse_date_with_invalid_format(self) -> None:
        """Test parsing date with invalid format - should keep as string."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE event_date DATE 'yyyy-MM-dd'
@DATA
'invalid-date'
"""
        arff_data = parser.parse_string(content)
        # Should not raise, date parsing failure is handled gracefully
        assert len(arff_data.data) == 1

    def test_parse_nominal_without_values(self) -> None:
        """Test nominal attribute converted to categorical properly."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE category {A, B, C}
@DATA
A
B
C
"""
        arff_data = parser.parse_string(content)
        assert arff_data.data["category"].dtype.name == "category"

    def test_parse_sparse_negative_index(self) -> None:
        """Test parsing sparse format with negative index."""
        parser = ArffParser()
        content = """
@RELATION test
@ATTRIBUTE a NUMERIC
@ATTRIBUTE b NUMERIC
@DATA
{-1 1.0}
"""
        with pytest.raises(ArffParseError, match="out of range"):
            parser.parse_string(content)


class TestWriterCoverage:
    """Additional writer tests for coverage."""

    def test_write_datetime_with_timestamp(self) -> None:
        """Test writing datetime values as Timestamp."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-15 10:30:00", "2024-02-20 14:45:00"]),
                "value": [1, 2],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "@ATTRIBUTE date DATE" in content

    def test_write_empty_string_value(self) -> None:
        """Test writing empty string values."""
        df = pd.DataFrame(
            {
                "text": ["hello", "", "world"],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "''" in content  # Empty string should be quoted

    def test_write_value_with_curly_braces(self) -> None:
        """Test writing values with curly braces."""
        df = pd.DataFrame(
            {
                "text": ["normal", "{special}", "value"],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "'{special}'" in content

    def test_write_nominal_with_special_chars(self) -> None:
        """Test writing nominal values with special characters."""
        df = pd.DataFrame(
            {
                "category": pd.Categorical(["a b", "c,d", "e%f"]),
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        # Values with special chars should be quoted
        assert "'" in content

    def test_from_dataframe_with_datetime_column(self) -> None:
        """Test from_dataframe with datetime column detection."""
        df = pd.DataFrame(
            {
                "created": pd.to_datetime(["2024-01-15", "2024-02-20"]),
                "value": [1, 2],
            }
        )

        arff_data = ArffWriter.from_dataframe(df, relation_name="test")

        created_attr = next(a for a in arff_data.attributes if a.name == "created")
        assert created_attr.type == AttributeType.DATE

    def test_write_integer_as_float_whole_number(self) -> None:
        """Test writing float values that are whole numbers."""
        df = pd.DataFrame(
            {
                "value": [1.0, 2.0, 3.0],  # Whole numbers as float
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        # Should be written as integers (without decimal)
        data_section = content.split("@DATA")[1]
        assert "1.0" not in data_section

    def test_write_date_without_format(self) -> None:
        """Test writing date attribute without format uses isoformat."""
        from arff_csv.parser import ArffData, Attribute

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-15", "2024-02-20"]),
            }
        )

        # Create ArffData with date attribute without format
        attrs = [Attribute(name="date", type=AttributeType.DATE, date_format=None)]
        arff_data = ArffData(relation_name="test", attributes=attrs, data=df)

        writer = ArffWriter()
        content = writer.write_string(arff_data)

        assert "@ATTRIBUTE date DATE\n" in content

    def test_write_value_with_double_quote(self) -> None:
        """Test writing values with double quotes."""
        df = pd.DataFrame(
            {
                "text": ['hello "world"', "normal"],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        # Should be quoted
        assert "'" in content

    def test_infer_attributes_default_to_string(self) -> None:
        """Test that unknown dtypes default to string."""
        # Create a DataFrame with a complex dtype
        df = pd.DataFrame(
            {
                "data": pd.array([1 + 2j, 3 + 4j], dtype=complex),
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "@ATTRIBUTE data STRING" in content

    def test_write_date_value_as_string(self) -> None:
        """Test writing date when value is string not datetime."""
        from arff_csv.parser import ArffData, Attribute

        df = pd.DataFrame(
            {
                "date": ["2024-01-15", "2024-02-20"],  # String, not datetime
            }
        )

        attrs = [Attribute(name="date", type=AttributeType.DATE, date_format="%Y-%m-%d")]
        arff_data = ArffData(relation_name="test", attributes=attrs, data=df)

        writer = ArffWriter()
        content = writer.write_string(arff_data)

        # Should quote the string dates
        assert "'2024-01-15'" in content


class TestCLIStringColumns:
    """Test CLI with string columns."""

    def test_csv2arff_string_option(self, temp_dir: Path) -> None:
        """Test the -s/--string option."""
        csv_path = temp_dir / "test.csv"
        csv_path.write_text("a,b\n1,hello\n2,world")

        output_path = temp_dir / "output.arff"

        result = main(
            [
                "csv2arff",
                str(csv_path),
                str(output_path),
                "--string",
                "b",
            ]
        )

        assert result == 0
        content = output_path.read_text()
        assert "@ATTRIBUTE b STRING" in content


class TestMainFunction:
    """Tests for main function edge cases."""

    def test_main_unknown_command_returns_1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that unknown command falls through to else branch."""
        from arff_csv import cli

        # Create a mock namespace with an unknown command
        class MockNamespace:
            command = "unknown_command"

        # Mock parse_args to return our mock namespace
        original_create_parser = cli.create_parser

        def mock_create_parser():
            parser = original_create_parser()
            original_parse_args = parser.parse_args

            def mock_parse_args(args=None):
                if args == ["test_unknown"]:
                    return MockNamespace()
                return original_parse_args(args)

            parser.parse_args = mock_parse_args
            return parser

        monkeypatch.setattr(cli, "create_parser", mock_create_parser)

        result = main(["test_unknown"])
        assert result == 1
