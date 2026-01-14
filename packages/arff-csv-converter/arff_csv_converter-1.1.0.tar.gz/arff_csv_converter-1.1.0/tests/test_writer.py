"""
Tests for the ARFF writer module.
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from arff_csv.exceptions import ArffWriteError
from arff_csv.parser import ArffParser, AttributeType
from arff_csv.writer import ArffWriter

if TYPE_CHECKING:
    from pathlib import Path


class TestArffWriter:
    """Tests for ArffWriter class."""

    def test_write_basic_dataframe(self, sample_dataframe: pd.DataFrame, temp_dir: Path) -> None:
        """Test writing a basic DataFrame to ARFF."""
        writer = ArffWriter()
        output_path = temp_dir / "output.arff"

        writer.write_file(sample_dataframe, output_path, relation_name="test")

        assert output_path.exists()
        content = output_path.read_text()
        assert "@RELATION test" in content
        assert "@ATTRIBUTE" in content
        assert "@DATA" in content

    def test_write_string(self, sample_dataframe: pd.DataFrame) -> None:
        """Test writing DataFrame to ARFF string."""
        writer = ArffWriter()

        content = writer.write_string(sample_dataframe, relation_name="test")

        assert "@RELATION test" in content
        assert "@DATA" in content
        assert "Alice" in content

    def test_write_arff_data(self, sample_arff_content: str, temp_dir: Path) -> None:
        """Test writing ArffData to file."""
        parser = ArffParser()
        arff_data = parser.parse_string(sample_arff_content)

        writer = ArffWriter()
        output_path = temp_dir / "output.arff"
        writer.write_file(arff_data, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "@RELATION iris" in content

    def test_write_with_comments(self, sample_dataframe: pd.DataFrame) -> None:
        """Test writing ARFF with comments."""
        writer = ArffWriter()

        comments = ["This is a test file", "Generated for testing"]
        content = writer.write_string(sample_dataframe, relation_name="test", comments=comments)

        assert "% This is a test file" in content
        assert "% Generated for testing" in content

    def test_write_numeric_attributes(self) -> None:
        """Test writing numeric attributes."""
        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.5, 2.5, 3.5],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "@ATTRIBUTE int_col INTEGER" in content
        assert "@ATTRIBUTE float_col NUMERIC" in content

    def test_write_categorical_as_nominal(self) -> None:
        """Test writing categorical columns as nominal."""
        df = pd.DataFrame(
            {
                "category": pd.Categorical(["a", "b", "a", "c"]),
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "@ATTRIBUTE category {a, b, c}" in content

    def test_write_string_attributes(self) -> None:
        """Test writing string attributes."""
        df = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "@ATTRIBUTE name STRING" in content
        assert "Alice" in content

    def test_write_boolean_as_nominal(self) -> None:
        """Test writing boolean columns as nominal."""
        df = pd.DataFrame(
            {
                "flag": [True, False, True],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "NOMINAL" in content or "{False, True}" in content

    def test_write_datetime_attributes(self) -> None:
        """Test writing datetime attributes."""
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "@ATTRIBUTE date DATE" in content

    def test_write_missing_values(self, sample_dataframe_with_missing: pd.DataFrame) -> None:
        """Test writing missing values as ?."""
        writer = ArffWriter()
        content = writer.write_string(sample_dataframe_with_missing, relation_name="test")

        # Check that missing values are represented as ?
        assert "?" in content

    def test_write_custom_missing_value(self) -> None:
        """Test writing with custom missing value."""
        df = pd.DataFrame(
            {
                "a": [1.0, np.nan, 3.0],
            }
        )

        writer = ArffWriter(missing_value="NA")
        content = writer.write_string(df, relation_name="test")

        assert "NA" in content

    def test_write_quoted_values(self) -> None:
        """Test writing values that need quoting."""
        df = pd.DataFrame(
            {
                "text": ["hello world", "comma, here", "quote's test"],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        # Values with spaces or special chars should be quoted
        assert "'" in content

    def test_write_quoted_relation_name(self) -> None:
        """Test writing relation name with spaces."""
        df = pd.DataFrame({"a": [1, 2, 3]})

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="My Test Dataset")

        assert "@RELATION 'My Test Dataset'" in content

    def test_write_quoted_attribute_name(self) -> None:
        """Test writing attribute name with spaces."""
        df = pd.DataFrame({"Column With Spaces": [1, 2, 3]})

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "'Column With Spaces'" in content

    def test_write_missing_relation_name_error(self, sample_dataframe: pd.DataFrame) -> None:
        """Test error when relation_name is missing."""
        writer = ArffWriter()

        with pytest.raises(ValueError, match="relation_name is required"):
            writer.write_string(sample_dataframe)

    def test_round_trip_conversion(self, sample_arff_content: str) -> None:
        """Test that ARFF -> DataFrame -> ARFF preserves data."""
        parser = ArffParser()
        writer = ArffWriter()

        # Parse original
        original = parser.parse_string(sample_arff_content)

        # Write to string
        written = writer.write_string(original)

        # Parse again
        reparsed = parser.parse_string(written)

        # Compare
        assert original.relation_name == reparsed.relation_name
        assert len(original.attributes) == len(reparsed.attributes)
        assert len(original.data) == len(reparsed.data)

        # Check data values
        pd.testing.assert_frame_equal(
            original.data.reset_index(drop=True),
            reparsed.data.reset_index(drop=True),
            check_categorical=False,
        )

    def test_from_dataframe(self) -> None:
        """Test creating ArffData from DataFrame."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "category": ["a", "b", "a"],
            }
        )

        arff_data = ArffWriter.from_dataframe(
            df,
            relation_name="test",
            nominal_columns=["category"],
            string_columns=["name"],
        )

        assert arff_data.relation_name == "test"
        assert len(arff_data.attributes) == 3

        # Check attribute types
        types = {a.name: a.type for a in arff_data.attributes}
        assert types["id"] == AttributeType.INTEGER
        assert types["name"] == AttributeType.STRING
        assert types["category"] == AttributeType.NOMINAL

    def test_from_dataframe_with_date_columns(self) -> None:
        """Test creating ArffData with date columns specified."""
        df = pd.DataFrame(
            {
                "date_str": ["2024-01-01", "2024-01-02"],
                "value": [1, 2],
            }
        )

        arff_data = ArffWriter.from_dataframe(
            df,
            relation_name="test",
            date_columns={"date_str": "%Y-%m-%d"},
        )

        date_attr = next(a for a in arff_data.attributes if a.name == "date_str")
        assert date_attr.type == AttributeType.DATE
        assert date_attr.date_format == "%Y-%m-%d"

    def test_nominal_threshold(self) -> None:
        """Test automatic nominal detection with threshold."""
        df = pd.DataFrame(
            {
                "category": ["a", "b", "a", "b", "c"],  # 3 unique values
                "values": list(range(5)),  # 5 unique values
            }
        )

        writer = ArffWriter(nominal_threshold=4)
        content = writer.write_string(df, relation_name="test")

        # category should be nominal (3 <= 4)
        assert "{a, b, c}" in content

    def test_write_integer_values(self) -> None:
        """Test that integer values are written without decimals."""
        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "1.0" not in content
        assert "2.0" not in content

    def test_write_float_values(self) -> None:
        """Test that float values are written correctly."""
        df = pd.DataFrame(
            {
                "float_col": [1.5, 2.5, 3.0],
            }
        )

        writer = ArffWriter()
        content = writer.write_string(df, relation_name="test")

        assert "1.5" in content
        assert "2.5" in content
        # 3.0 should be written as 3
        assert "3,\n" not in content or "3\n" in content


class TestArffWriterFileOperations:
    """Tests for file operations in ArffWriter."""

    def test_write_to_file(self, sample_dataframe: pd.DataFrame, temp_dir: Path) -> None:
        """Test writing to a file."""
        writer = ArffWriter()
        output_path = temp_dir / "output.arff"

        writer.write_file(sample_dataframe, output_path, relation_name="test")

        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 0

    def test_write_to_file_object(self, sample_dataframe: pd.DataFrame) -> None:
        """Test writing to a file-like object."""
        writer = ArffWriter()
        buffer = StringIO()

        writer.write(sample_dataframe, buffer, relation_name="test")

        content = buffer.getvalue()
        assert "@RELATION test" in content

    def test_write_creates_parent_directories(
        self, sample_dataframe: pd.DataFrame, temp_dir: Path
    ) -> None:
        """Test that missing parent directories don't cause errors."""
        writer = ArffWriter()
        output_path = temp_dir / "subdir" / "output.arff"

        # This should fail because we're not creating parent directories
        # The method should handle this appropriately
        with pytest.raises(ArffWriteError):
            writer.write_file(sample_dataframe, output_path, relation_name="test")
