"""
Tests for the main converter module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest

from arff_csv.converter import ArffConverter, arff_to_csv, csv_to_arff
from arff_csv.exceptions import CsvParseError

if TYPE_CHECKING:
    from pathlib import Path


class TestArffConverter:
    """Tests for ArffConverter class."""

    def test_csv_to_arff(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test CSV to ARFF conversion."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(
            sample_csv_file,
            output_path,
            relation_name="test_data",
        )

        assert output_path.exists()
        assert arff_data.relation_name == "test_data"
        assert len(arff_data.data) > 0

    def test_csv_to_arff_default_relation_name(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test CSV to ARFF with default relation name."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(sample_csv_file, output_path)

        # Relation name should be the CSV filename without extension
        assert arff_data.relation_name == "sample"

    def test_csv_to_arff_with_nominal_columns(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test CSV to ARFF with specified nominal columns."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(
            sample_csv_file,
            output_path,
            nominal_columns=["name"],
        )

        # Find name attribute
        name_attr = next(a for a in arff_data.attributes if a.name == "name")
        from arff_csv.parser import AttributeType

        assert name_attr.type == AttributeType.NOMINAL

    def test_csv_to_arff_with_comments(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test CSV to ARFF with comments."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        comments = ["Test comment 1", "Test comment 2"]
        arff_data = converter.csv_to_arff(
            sample_csv_file,
            output_path,
            comments=comments,
        )

        assert arff_data.comments == comments

        # Check that comments are in the file
        content = output_path.read_text()
        assert "% Test comment 1" in content
        assert "% Test comment 2" in content

    def test_csv_to_arff_not_found(self, temp_dir: Path) -> None:
        """Test error when CSV file not found."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        with pytest.raises(FileNotFoundError):
            converter.csv_to_arff("/nonexistent.csv", output_path)

    def test_csv_to_arff_with_excluded_columns(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test CSV to ARFF excluding specific columns."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(
            sample_csv_file,
            output_path,
            exclude_columns=["id"],
        )

        assert "id" not in arff_data.data.columns
        assert all(attr.name != "id" for attr in arff_data.attributes)

    def test_csv_to_arff_exclude_missing_column(
        self, sample_csv_file: Path, temp_dir: Path
    ) -> None:
        """Test error when excluding a column that does not exist."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        with pytest.raises(CsvParseError):
            converter.csv_to_arff(
                sample_csv_file,
                output_path,
                exclude_columns=["does_not_exist"],
            )

    def test_arff_to_csv(self, sample_arff_file: Path, temp_dir: Path) -> None:
        """Test ARFF to CSV conversion."""
        converter = ArffConverter()
        output_path = temp_dir / "output.csv"

        df = converter.arff_to_csv(sample_arff_file, output_path)

        assert output_path.exists()
        assert len(df) > 0
        assert "sepallength" in df.columns

    def test_arff_to_csv_not_found(self, temp_dir: Path) -> None:
        """Test error when ARFF file not found."""
        converter = ArffConverter()
        output_path = temp_dir / "output.csv"

        with pytest.raises(FileNotFoundError):
            converter.arff_to_csv("/nonexistent.arff", output_path)

    def test_round_trip_conversion(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test round-trip CSV -> ARFF -> CSV conversion."""
        converter = ArffConverter()
        arff_path = temp_dir / "intermediate.arff"
        csv_output = temp_dir / "output.csv"

        # CSV -> ARFF
        converter.csv_to_arff(sample_csv_file, arff_path)

        # ARFF -> CSV
        df = converter.arff_to_csv(arff_path, csv_output)

        # Read original
        original = pd.read_csv(sample_csv_file)

        # Compare shapes
        assert df.shape == original.shape

    def test_csv_to_arff_string(self, sample_csv_file: Path) -> None:
        """Test converting CSV to ARFF string."""
        converter = ArffConverter()

        content = converter.csv_to_arff_string(
            sample_csv_file,
            relation_name="test",
        )

        assert "@RELATION test" in content
        assert "@DATA" in content

    def test_arff_to_csv_string(self, sample_arff_file: Path) -> None:
        """Test converting ARFF to CSV string."""
        converter = ArffConverter()

        content = converter.arff_to_csv_string(sample_arff_file)

        assert "sepallength" in content
        assert "5.1" in content

    def test_dataframe_to_arff(self, sample_dataframe: pd.DataFrame, temp_dir: Path) -> None:
        """Test converting DataFrame to ARFF file."""
        converter = ArffConverter()
        output_path = temp_dir / "output.arff"

        arff_data = converter.dataframe_to_arff(
            sample_dataframe,
            output_path,
            relation_name="test",
        )

        assert output_path.exists()
        assert arff_data.relation_name == "test"
        assert len(arff_data.attributes) == len(sample_dataframe.columns)

    def test_arff_to_dataframe(self, sample_arff_file: Path) -> None:
        """Test loading ARFF into DataFrame."""
        converter = ArffConverter()

        df = converter.arff_to_dataframe(sample_arff_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_dataframe_to_arff_string(self, sample_dataframe: pd.DataFrame) -> None:
        """Test converting DataFrame to ARFF string."""
        converter = ArffConverter()

        content = converter.dataframe_to_arff_string(
            sample_dataframe,
            relation_name="test",
        )

        assert "@RELATION test" in content
        assert "@DATA" in content

    def test_arff_string_to_dataframe(self, sample_arff_content: str) -> None:
        """Test loading ARFF string into DataFrame."""
        converter = ArffConverter()

        df = converter.arff_string_to_dataframe(sample_arff_content)

        assert isinstance(df, pd.DataFrame)
        assert "sepallength" in df.columns

    def test_csv_kwargs_passed(self, temp_dir: Path) -> None:
        """Test that CSV kwargs are passed correctly."""
        # Create a CSV with custom delimiter
        csv_path = temp_dir / "custom.csv"
        csv_path.write_text("a;b;c\n1;2;3\n4;5;6")

        converter = ArffConverter()
        arff_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(
            csv_path,
            arff_path,
            sep=";",
        )

        assert len(arff_data.data.columns) == 3
        assert "a" in arff_data.data.columns

    def test_unnamed_columns_are_normalized(self, temp_dir: Path) -> None:
        """Test that pandas Unnamed columns are renamed to Unnamed_<n>."""
        csv_path = temp_dir / "unnamed.csv"
        csv_path.write_text(",b,c\n1,2,3\n4,5,6")

        converter = ArffConverter()
        arff_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(csv_path, arff_path)

        assert "Unnamed_0" in arff_data.data.columns
        attr_names = [a.name for a in arff_data.attributes]
        assert "Unnamed_0" in attr_names


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_csv_to_arff_function(self, sample_csv_file: Path, temp_dir: Path) -> None:
        """Test csv_to_arff convenience function."""
        output_path = temp_dir / "output.arff"

        arff_data = csv_to_arff(
            sample_csv_file,
            output_path,
            relation_name="test",
        )

        assert output_path.exists()
        assert arff_data.relation_name == "test"

    def test_arff_to_csv_function(self, sample_arff_file: Path, temp_dir: Path) -> None:
        """Test arff_to_csv convenience function."""
        output_path = temp_dir / "output.csv"

        df = arff_to_csv(sample_arff_file, output_path)

        assert output_path.exists()
        assert isinstance(df, pd.DataFrame)

    def test_csv_to_arff_with_custom_missing(self, temp_dir: Path) -> None:
        """Test csv_to_arff with custom missing value."""
        # Create CSV with custom missing value
        csv_path = temp_dir / "input.csv"
        csv_path.write_text("a,b\n1,2\nNA,3\n4,NA")

        output_path = temp_dir / "output.arff"

        csv_to_arff(
            csv_path,
            output_path,
            missing_value="NA",
        )

        content = output_path.read_text()
        assert "NA" in content

    def test_arff_to_csv_include_index(self, sample_arff_file: Path, temp_dir: Path) -> None:
        """Test arff_to_csv with index included."""
        output_path = temp_dir / "output.csv"

        arff_to_csv(sample_arff_file, output_path, include_index=True)

        # Read the CSV and check for index column
        df = pd.read_csv(output_path)
        # First column should be unnamed (index)
        assert "Unnamed_0" in df.columns or df.columns[0].startswith("Unnamed")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_csv(self, temp_dir: Path) -> None:
        """Test handling of empty CSV (headers only)."""
        csv_path = temp_dir / "empty.csv"
        csv_path.write_text("a,b,c\n")

        converter = ArffConverter()
        arff_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(csv_path, arff_path)

        assert len(arff_data.data) == 0
        assert len(arff_data.attributes) == 3

    def test_csv_with_special_characters(self, temp_dir: Path) -> None:
        """Test CSV with special characters in values."""
        csv_path = temp_dir / "special.csv"
        csv_path.write_text('a,b\n"hello, world","test\'s value"\n')

        converter = ArffConverter()
        arff_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(csv_path, arff_path)

        assert arff_data.data.iloc[0]["a"] == "hello, world"
        assert arff_data.data.iloc[0]["b"] == "test's value"

    def test_large_dataset(self, temp_dir: Path) -> None:
        """Test with a larger dataset."""
        # Create a DataFrame with 1000 rows
        df = pd.DataFrame(
            {
                "id": range(1000),
                "value": [i * 0.1 for i in range(1000)],
                "category": pd.Categorical(["A", "B", "C"] * 333 + ["A"]),
            }
        )

        csv_path = temp_dir / "large.csv"
        df.to_csv(csv_path, index=False)

        converter = ArffConverter()
        arff_path = temp_dir / "large.arff"
        csv_output = temp_dir / "output.csv"

        # Convert to ARFF
        converter.csv_to_arff(csv_path, arff_path)

        # Convert back to CSV
        result = converter.arff_to_csv(arff_path, csv_output)

        assert len(result) == 1000

    def test_unicode_content(self, temp_dir: Path) -> None:
        """Test handling of Unicode content."""
        csv_path = temp_dir / "unicode.csv"
        csv_path.write_text("name,value\nÄlice,1\nBöb,2\n日本語,3\n", encoding="utf-8")

        converter = ArffConverter()
        arff_path = temp_dir / "output.arff"

        arff_data = converter.csv_to_arff(csv_path, arff_path)

        assert "Älice" in arff_data.data["name"].values or "Älice" in str(
            arff_data.data["name"].values
        )
