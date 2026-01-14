"""
ARFF file writer.

This module provides functionality to write ARFF (Attribute-Relation File Format)
files from pandas DataFrames or ArffData objects.

The writer automatically:
- Infers attribute types from DataFrame dtypes
- Detects nominal attributes from categorical columns or unique value counts
- Handles missing values
- Formats data according to ARFF specifications
"""

from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, TextIO

import numpy as np
import pandas as pd

from arff_csv.exceptions import ArffWriteError
from arff_csv.parser import ArffData, Attribute, AttributeType


class ArffWriter:
    """Writer for ARFF (Attribute-Relation File Format) files.

    This class converts pandas DataFrames to ARFF format, automatically
    inferring attribute types and handling special cases.

    Example:
        >>> writer = ArffWriter()
        >>> writer.write_file(df, "output.arff", relation_name="my_data")
    """

    # Maximum number of unique values to consider a column as nominal
    DEFAULT_NOMINAL_THRESHOLD = 20

    def __init__(
        self,
        missing_value: str = "?",
        nominal_threshold: int | None = None,
        string_quote: str = "'",
    ) -> None:
        """Initialize the writer.

        Args:
            missing_value: String to use for missing values. Defaults to "?".
            nominal_threshold: Maximum unique values for auto-detecting nominal.
                             If None, only categorical columns are treated as nominal.
            string_quote: Quote character for strings. Defaults to single quote.
        """
        self.missing_value = missing_value
        self.nominal_threshold = nominal_threshold
        self.string_quote = string_quote

    def write_file(
        self,
        data: pd.DataFrame | ArffData,
        filepath: str | Path,
        relation_name: str | None = None,
        comments: list[str] | None = None,
    ) -> None:
        """Write data to an ARFF file.

        Args:
            data: DataFrame or ArffData to write.
            filepath: Path to the output file.
            relation_name: Name of the relation. Required if data is DataFrame.
            comments: Optional list of comments to include.

        Raises:
            ArffWriteError: If writing fails.
            ValueError: If relation_name is missing for DataFrame input.
        """
        filepath = Path(filepath)

        try:
            with filepath.open("w", encoding="utf-8") as f:
                self.write(data, f, relation_name, comments)
        except OSError as e:
            raise ArffWriteError(f"Failed to write ARFF file: {e}") from e

    def write_string(
        self,
        data: pd.DataFrame | ArffData,
        relation_name: str | None = None,
        comments: list[str] | None = None,
    ) -> str:
        """Write data to an ARFF string.

        Args:
            data: DataFrame or ArffData to write.
            relation_name: Name of the relation. Required if data is DataFrame.
            comments: Optional list of comments to include.

        Returns:
            ARFF content as a string.

        Raises:
            ValueError: If relation_name is missing for DataFrame input.
        """
        buffer = StringIO()
        self.write(data, buffer, relation_name, comments)
        return buffer.getvalue()

    def write(
        self,
        data: pd.DataFrame | ArffData,
        file_obj: TextIO,
        relation_name: str | None = None,
        comments: list[str] | None = None,
    ) -> None:
        """Write data to a file-like object.

        Args:
            data: DataFrame or ArffData to write.
            file_obj: File-like object to write to.
            relation_name: Name of the relation. Required if data is DataFrame.
            comments: Optional list of comments to include.

        Raises:
            ValueError: If relation_name is missing for DataFrame input.
        """
        if isinstance(data, ArffData):
            self._write_arff_data(data, file_obj)
        else:
            if relation_name is None:
                raise ValueError("relation_name is required when writing a DataFrame")
            self._write_dataframe(data, file_obj, relation_name, comments)

    def _write_arff_data(self, arff_data: ArffData, file_obj: TextIO) -> None:
        """Write ArffData to a file-like object."""
        # Write comments
        for comment in arff_data.comments:
            file_obj.write(f"% {comment}\n")
        if arff_data.comments:
            file_obj.write("\n")

        # Write relation
        self._write_relation(file_obj, arff_data.relation_name)

        # Write attributes
        for attr in arff_data.attributes:
            self._write_attribute(file_obj, attr)

        # Write data section
        file_obj.write("\n@DATA\n")
        self._write_data_rows(file_obj, arff_data.data, arff_data.attributes)

    def _write_dataframe(
        self,
        df: pd.DataFrame,
        file_obj: TextIO,
        relation_name: str,
        comments: list[str] | None = None,
    ) -> None:
        """Write DataFrame to a file-like object."""
        # Write comments
        if comments:
            for comment in comments:
                file_obj.write(f"% {comment}\n")
            file_obj.write("\n")

        # Write relation
        self._write_relation(file_obj, relation_name)

        # Infer attributes from DataFrame
        attributes = self._infer_attributes(df)

        # Write attributes
        for attr in attributes:
            self._write_attribute(file_obj, attr)

        # Write data section
        file_obj.write("\n@DATA\n")
        self._write_data_rows(file_obj, df, attributes)

    def _write_relation(self, file_obj: TextIO, name: str) -> None:
        """Write the @RELATION line."""
        # Quote if contains spaces or special characters
        if " " in name or "," in name or "%" in name:
            name = f"'{name}'"
        file_obj.write(f"@RELATION {name}\n\n")

    def _write_attribute(self, file_obj: TextIO, attr: Attribute) -> None:
        """Write an @ATTRIBUTE line."""
        # Quote attribute name if needed
        name = attr.name
        if " " in name or "," in name or "%" in name:
            name = f"'{name}'"

        if attr.type == AttributeType.NOMINAL and attr.nominal_values:
            # Format nominal values
            values = ", ".join(self._quote_if_needed(v) for v in attr.nominal_values)
            file_obj.write(f"@ATTRIBUTE {name} {{{values}}}\n")
        elif attr.type == AttributeType.DATE:
            if attr.date_format:
                file_obj.write(f"@ATTRIBUTE {name} DATE '{attr.date_format}'\n")
            else:
                file_obj.write(f"@ATTRIBUTE {name} DATE\n")
        elif attr.type == AttributeType.STRING:
            file_obj.write(f"@ATTRIBUTE {name} STRING\n")
        elif attr.type == AttributeType.INTEGER:
            file_obj.write(f"@ATTRIBUTE {name} INTEGER\n")
        else:
            # NUMERIC or REAL
            file_obj.write(f"@ATTRIBUTE {name} NUMERIC\n")

    def _write_data_rows(
        self, file_obj: TextIO, df: pd.DataFrame, attributes: list[Attribute]
    ) -> None:
        """Write data rows."""
        for _, row in df.iterrows():
            values = []
            for attr in attributes:
                value = row[attr.name]
                formatted = self._format_value(value, attr)
                values.append(formatted)
            file_obj.write(",".join(values) + "\n")

    def _format_value(self, value: Any, attr: Attribute) -> str:
        """Format a value for ARFF output."""
        # Handle missing values
        if pd.isna(value):
            return self.missing_value

        # Format based on type
        if attr.is_numeric():
            if isinstance(value, (int, np.integer)):
                return str(int(value))
            elif isinstance(value, (float, np.floating)):
                # Use repr for full precision, but clean up
                if value == int(value):
                    return str(int(value))
                return str(value)
            return str(value)

        if attr.type == AttributeType.DATE:
            if isinstance(value, (datetime, pd.Timestamp)):
                if attr.date_format:
                    return f"'{value.strftime(attr.date_format)}'"
                return f"'{value.isoformat()}'"
            # For string dates, always quote to satisfy ARFF DATE syntax
            return f"'{value!s}'"

        # STRING or NOMINAL
        return self._quote_if_needed(str(value))

    def _quote_if_needed(self, value: str) -> str:
        """Quote a string if it contains special characters."""
        if not value:
            return f"{self.string_quote}{self.string_quote}"

        # Check if quoting is needed
        needs_quoting = (
            " " in value
            or "," in value
            or "%" in value
            or "{" in value
            or "}" in value
            or self.string_quote in value
            or '"' in value
        )

        if needs_quoting:
            # Escape quotes in the value
            escaped = value.replace(self.string_quote, f"\\{self.string_quote}")
            return f"{self.string_quote}{escaped}{self.string_quote}"

        return value

    def _infer_attributes(self, df: pd.DataFrame) -> list[Attribute]:
        """Infer attribute definitions from DataFrame columns.

        Args:
            df: The DataFrame to analyze.

        Returns:
            List of Attribute objects.
        """
        attributes = []

        for col in df.columns:
            dtype = df[col].dtype

            # Check for categorical first
            if isinstance(dtype, pd.CategoricalDtype):
                values = [str(c) for c in dtype.categories]
                attributes.append(
                    Attribute(name=col, type=AttributeType.NOMINAL, nominal_values=values)
                )
                continue

            # Check for datetime
            if pd.api.types.is_datetime64_any_dtype(dtype):
                attributes.append(
                    Attribute(name=col, type=AttributeType.DATE, date_format="%Y-%m-%d %H:%M:%S")
                )
                continue

            # Complex numbers are not supported in ARFF; treat as strings
            if pd.api.types.is_complex_dtype(dtype):
                attributes.append(Attribute(name=col, type=AttributeType.STRING))
                continue

            # Check for boolean (treat as nominal)
            if pd.api.types.is_bool_dtype(dtype):
                attributes.append(
                    Attribute(
                        name=col,
                        type=AttributeType.NOMINAL,
                        nominal_values=["False", "True"],
                    )
                )
                continue

            # Check for integer
            if pd.api.types.is_integer_dtype(dtype):
                attributes.append(Attribute(name=col, type=AttributeType.INTEGER))
                continue

            # Check for numeric (float)
            if pd.api.types.is_numeric_dtype(dtype):
                attributes.append(Attribute(name=col, type=AttributeType.NUMERIC))
                continue

            # Check for object dtype - could be string or nominal
            if pd.api.types.is_object_dtype(dtype):
                # Check if should be treated as nominal
                if self.nominal_threshold is not None:
                    unique_count = df[col].nunique()
                    if unique_count <= self.nominal_threshold:
                        values = sorted(df[col].dropna().unique().astype(str).tolist())
                        attributes.append(
                            Attribute(name=col, type=AttributeType.NOMINAL, nominal_values=values)
                        )
                        continue

                # Treat as string
                attributes.append(Attribute(name=col, type=AttributeType.STRING))
                continue

            # Default to string
            attributes.append(Attribute(name=col, type=AttributeType.STRING))

        return attributes

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        relation_name: str,
        nominal_columns: list[str] | None = None,
        string_columns: list[str] | None = None,
        date_columns: dict[str, str] | None = None,
    ) -> ArffData:
        """Create ArffData from a DataFrame with explicit type specifications.

        This is a convenience method for creating ArffData with full control
        over attribute types.

        Args:
            df: The DataFrame to convert.
            relation_name: Name of the relation.
            nominal_columns: List of column names to treat as nominal.
            string_columns: List of column names to treat as string.
            date_columns: Dict mapping column names to date format strings.

        Returns:
            ArffData object.
        """
        nominal_columns = nominal_columns or []
        string_columns = string_columns or []
        date_columns = date_columns or {}

        # Make a copy to avoid modifying the original
        df = df.copy()

        attributes = []

        for col in df.columns:
            dtype = df[col].dtype

            if col in date_columns:
                attributes.append(
                    Attribute(
                        name=col,
                        type=AttributeType.DATE,
                        date_format=date_columns[col],
                    )
                )
            elif pd.api.types.is_complex_dtype(dtype) or col in string_columns:
                attributes.append(Attribute(name=col, type=AttributeType.STRING))
            elif col in nominal_columns or isinstance(dtype, pd.CategoricalDtype):
                if isinstance(dtype, pd.CategoricalDtype):
                    values = [str(c) for c in dtype.categories]
                else:
                    # Convert column values to strings for consistency
                    # This ensures the values match the nominal categories
                    def convert_to_str(x: Any) -> Any:
                        if pd.isna(x):
                            return x
                        if isinstance(x, (int, np.integer)):
                            return str(x)
                        if isinstance(x, (float, np.floating)) and x == int(x):
                            return str(int(x))
                        return str(x)

                    df[col] = df[col].apply(convert_to_str)
                    values = sorted(df[col].dropna().unique().astype(str).tolist())
                attributes.append(
                    Attribute(name=col, type=AttributeType.NOMINAL, nominal_values=values)
                )
            elif pd.api.types.is_integer_dtype(dtype):
                attributes.append(Attribute(name=col, type=AttributeType.INTEGER))
            elif pd.api.types.is_numeric_dtype(dtype):
                attributes.append(Attribute(name=col, type=AttributeType.NUMERIC))
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                attributes.append(
                    Attribute(
                        name=col,
                        type=AttributeType.DATE,
                        date_format="%Y-%m-%d %H:%M:%S",
                    )
                )
            else:
                attributes.append(Attribute(name=col, type=AttributeType.STRING))

        return ArffData(
            relation_name=relation_name,
            attributes=attributes,
            data=df,
        )
