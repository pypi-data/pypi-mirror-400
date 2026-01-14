"""
Main converter module for ARFF-CSV conversions.

This module provides the main ArffConverter class and convenience functions
for converting between CSV and ARFF file formats.

Example:
    >>> from arff_csv import csv_to_arff, arff_to_csv
    >>> csv_to_arff("input.csv", "output.arff", relation_name="my_data")
    >>> arff_to_csv("input.arff", "output.csv")
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from arff_csv.exceptions import CsvParseError
from arff_csv.parser import ArffData, ArffParser
from arff_csv.writer import ArffWriter


class ArffConverter:
    """Main converter class for ARFF-CSV conversions.

    This class provides methods to convert between CSV and ARFF formats,
    with options for customizing the conversion process.

    Attributes:
        parser: The ArffParser instance used for reading ARFF files.
        writer: The ArffWriter instance used for writing ARFF files.

    Example:
        >>> converter = ArffConverter()
        >>> converter.csv_to_arff("data.csv", "data.arff", relation_name="dataset")
        >>> converter.arff_to_csv("data.arff", "data.csv")
    """

    def __init__(
        self,
        missing_value: str = "?",
        nominal_threshold: int | None = None,
        string_quote: str = "'",
    ) -> None:
        """Initialize the converter.

        Args:
            missing_value: String used to represent missing values.
                          Defaults to "?" (ARFF standard).
            nominal_threshold: Maximum number of unique values for a column
                             to be automatically treated as nominal when
                             converting CSV to ARFF. If None, only categorical
                             columns are treated as nominal.
            string_quote: Quote character for strings in ARFF output.
        """
        self.parser = ArffParser(missing_value=missing_value)
        self.writer = ArffWriter(
            missing_value=missing_value,
            nominal_threshold=nominal_threshold,
            string_quote=string_quote,
        )
        self.missing_value = missing_value

    @staticmethod
    def _apply_column_filters(
        df: pd.DataFrame,
        exclude_columns: list[str] | None,
        nominal_columns: list[str] | None,
        string_columns: list[str] | None,
        date_columns: dict[str, str] | None,
    ) -> tuple[pd.DataFrame, list[str], list[str], dict[str, str]]:
        """Apply column exclusions and align type hints with the remaining columns."""
        exclude_columns = exclude_columns or []
        nominal_columns = nominal_columns or []
        string_columns = string_columns or []
        date_columns = date_columns or {}

        missing_excludes = [col for col in exclude_columns if col not in df.columns]
        if missing_excludes:
            missing_list = ", ".join(missing_excludes)
            raise CsvParseError(f"Exclude columns not found in CSV: {missing_list}")

        filtered_df = df.drop(columns=exclude_columns) if exclude_columns else df
        filtered_columns = set(filtered_df.columns)

        filtered_nominal = [col for col in nominal_columns if col in filtered_columns]
        filtered_string = [col for col in string_columns if col in filtered_columns]
        filtered_dates = {col: fmt for col, fmt in date_columns.items() if col in filtered_columns}

        return filtered_df, filtered_nominal, filtered_string, filtered_dates

    @staticmethod
    def _normalize_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Rename pandas-generated Unnamed columns to `Unnamed_<n>` without spaces/colons."""
        new_cols: list[str] = []
        for idx, col in enumerate(df.columns):
            if isinstance(col, str) and col.startswith("Unnamed"):
                # Typical pandas pattern: "Unnamed: <number>"
                parts = col.split(":")
                suffix = parts[1].strip() if len(parts) > 1 else str(idx)
                if not suffix.isdigit():
                    suffix = str(idx)
                new_cols.append(f"Unnamed_{suffix}")
            else:
                new_cols.append(col)

        if new_cols == list(df.columns):
            return df

        renamed = df.copy()
        renamed.columns = new_cols
        return renamed

    @staticmethod
    def _validate_column_alignment(
        csv_path: Path,
        csv_kwargs: dict[str, Any],
    ) -> None:
        """Validate that the parsed DataFrame does not have more columns than the header."""
        # Only validate when we have a header row
        if csv_kwargs.get("header", "infer") is None:
            return

        delimiter = str(csv_kwargs.get("sep", csv_kwargs.get("delimiter", ",")))
        encoding = str(csv_kwargs.get("encoding", "utf-8"))

        try:
            with csv_path.open("r", encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, None)

                if not header:
                    return

                expected_columns = len(header)
                if not expected_columns:
                    return

                for idx, row in enumerate(reader, start=2):  # start=2 accounts for header row
                    if len(row) != expected_columns:
                        raise CsvParseError(
                            "CSV file has rows with a different number of columns than the header",
                            row_number=idx,
                        )
        except OSError:
            # If we cannot read the header, skip validation
            return

    def csv_to_arff(
        self,
        csv_path: str | Path,
        arff_path: str | Path,
        relation_name: str | None = None,
        nominal_columns: list[str] | None = None,
        string_columns: list[str] | None = None,
        date_columns: dict[str, str] | None = None,
        exclude_columns: list[str] | None = None,
        comments: list[str] | None = None,
        **csv_kwargs: Any,
    ) -> ArffData:
        """Convert a CSV file to ARFF format.

        Args:
            csv_path: Path to the input CSV file.
            arff_path: Path to the output ARFF file.
            relation_name: Name of the relation. Defaults to the CSV filename
                          (without extension).
            nominal_columns: List of column names to treat as nominal attributes.
            string_columns: List of column names to treat as string attributes.
            date_columns: Dict mapping column names to date format strings.
            exclude_columns: List of column names to exclude from the conversion.
            comments: List of comments to include in the ARFF file.
            **csv_kwargs: Additional keyword arguments passed to pd.read_csv().

        Returns:
            ArffData object containing the converted data.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
            CsvParseError: If the CSV file cannot be parsed.
        """
        csv_path = Path(csv_path)
        arff_path = Path(arff_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Determine relation name
        if relation_name is None:
            relation_name = csv_path.stem

        # Read CSV
        try:
            df = pd.read_csv(csv_path, **csv_kwargs)
        except Exception as e:
            raise CsvParseError(f"Failed to read CSV file: {e}") from e

        df = self._normalize_unnamed_columns(df)
        self._validate_column_alignment(
            csv_path=csv_path,
            csv_kwargs=csv_kwargs,
        )

        # Exclude requested columns
        df, nominal_columns, string_columns, date_columns = self._apply_column_filters(
            df=df,
            exclude_columns=exclude_columns,
            nominal_columns=nominal_columns,
            string_columns=string_columns,
            date_columns=date_columns,
        )

        # Create ArffData
        arff_data = ArffWriter.from_dataframe(
            df,
            relation_name=relation_name,
            nominal_columns=nominal_columns,
            string_columns=string_columns,
            date_columns=date_columns,
        )

        if comments:
            arff_data.comments = comments

        # Write ARFF
        self.writer.write_file(arff_data, arff_path)

        return arff_data

    def arff_to_csv(
        self,
        arff_path: str | Path,
        csv_path: str | Path,
        include_index: bool = False,
        **csv_kwargs: Any,
    ) -> pd.DataFrame:
        """Convert an ARFF file to CSV format.

        Args:
            arff_path: Path to the input ARFF file.
            csv_path: Path to the output CSV file.
            include_index: Whether to include the DataFrame index in the CSV.
            **csv_kwargs: Additional keyword arguments passed to df.to_csv().

        Returns:
            pandas DataFrame containing the converted data.

        Raises:
            FileNotFoundError: If the ARFF file does not exist.
            ArffParseError: If the ARFF file cannot be parsed.
        """
        arff_path = Path(arff_path)
        csv_path = Path(csv_path)

        # Parse ARFF
        arff_data = self.parser.parse_file(arff_path)

        # Write CSV
        arff_data.data.to_csv(csv_path, index=include_index, **csv_kwargs)

        return arff_data.data

    def csv_to_arff_string(
        self,
        csv_path: str | Path,
        relation_name: str | None = None,
        nominal_columns: list[str] | None = None,
        string_columns: list[str] | None = None,
        date_columns: dict[str, str] | None = None,
        exclude_columns: list[str] | None = None,
        comments: list[str] | None = None,
        **csv_kwargs: Any,
    ) -> str:
        """Convert a CSV file to ARFF string.

        Args:
            csv_path: Path to the input CSV file.
            relation_name: Name of the relation.
            nominal_columns: List of column names to treat as nominal.
            string_columns: List of column names to treat as string.
            date_columns: Dict mapping column names to date format strings.
            exclude_columns: List of column names to exclude from the conversion.
            comments: List of comments to include.
            **csv_kwargs: Additional arguments passed to pd.read_csv().

        Returns:
            ARFF content as a string.
        """
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        if relation_name is None:
            relation_name = csv_path.stem

        try:
            df = pd.read_csv(csv_path, **csv_kwargs)
        except Exception as e:
            raise CsvParseError(f"Failed to read CSV file: {e}") from e

        df = self._normalize_unnamed_columns(df)
        self._validate_column_alignment(
            csv_path=csv_path,
            csv_kwargs=csv_kwargs,
        )

        # Exclude requested columns
        df, nominal_columns, string_columns, date_columns = self._apply_column_filters(
            df=df,
            exclude_columns=exclude_columns,
            nominal_columns=nominal_columns,
            string_columns=string_columns,
            date_columns=date_columns,
        )

        arff_data = ArffWriter.from_dataframe(
            df,
            relation_name=relation_name,
            nominal_columns=nominal_columns,
            string_columns=string_columns,
            date_columns=date_columns,
        )

        if comments:
            arff_data.comments = comments

        return self.writer.write_string(arff_data)

    def arff_to_csv_string(
        self,
        arff_path: str | Path,
        include_index: bool = False,
        **csv_kwargs: Any,
    ) -> str:
        """Convert an ARFF file to CSV string.

        Args:
            arff_path: Path to the input ARFF file.
            include_index: Whether to include the DataFrame index.
            **csv_kwargs: Additional arguments passed to df.to_csv().

        Returns:
            CSV content as a string.
        """
        arff_data = self.parser.parse_file(arff_path)
        return str(arff_data.data.to_csv(index=include_index, **csv_kwargs))

    def dataframe_to_arff(
        self,
        df: pd.DataFrame,
        arff_path: str | Path,
        relation_name: str,
        nominal_columns: list[str] | None = None,
        string_columns: list[str] | None = None,
        date_columns: dict[str, str] | None = None,
        comments: list[str] | None = None,
    ) -> ArffData:
        """Convert a DataFrame to ARFF file.

        Args:
            df: The DataFrame to convert.
            arff_path: Path to the output ARFF file.
            relation_name: Name of the relation.
            nominal_columns: List of column names to treat as nominal.
            string_columns: List of column names to treat as string.
            date_columns: Dict mapping column names to date format strings.
            comments: List of comments to include.

        Returns:
            ArffData object containing the converted data.
        """
        arff_data = ArffWriter.from_dataframe(
            df,
            relation_name=relation_name,
            nominal_columns=nominal_columns,
            string_columns=string_columns,
            date_columns=date_columns,
        )

        if comments:
            arff_data.comments = comments

        self.writer.write_file(arff_data, arff_path)

        return arff_data

    def arff_to_dataframe(self, arff_path: str | Path) -> pd.DataFrame:
        """Load an ARFF file into a DataFrame.

        Args:
            arff_path: Path to the ARFF file.

        Returns:
            pandas DataFrame containing the data.
        """
        arff_data = self.parser.parse_file(arff_path)
        return arff_data.data

    def dataframe_to_arff_string(
        self,
        df: pd.DataFrame,
        relation_name: str,
        nominal_columns: list[str] | None = None,
        string_columns: list[str] | None = None,
        date_columns: dict[str, str] | None = None,
        comments: list[str] | None = None,
    ) -> str:
        """Convert a DataFrame to ARFF string.

        Args:
            df: The DataFrame to convert.
            relation_name: Name of the relation.
            nominal_columns: List of column names to treat as nominal.
            string_columns: List of column names to treat as string.
            date_columns: Dict mapping column names to date format strings.
            comments: List of comments to include.

        Returns:
            ARFF content as a string.
        """
        arff_data = ArffWriter.from_dataframe(
            df,
            relation_name=relation_name,
            nominal_columns=nominal_columns,
            string_columns=string_columns,
            date_columns=date_columns,
        )

        if comments:
            arff_data.comments = comments

        return self.writer.write_string(arff_data)

    def arff_string_to_dataframe(self, arff_content: str) -> pd.DataFrame:
        """Load ARFF content from a string into a DataFrame.

        Args:
            arff_content: ARFF file content as a string.

        Returns:
            pandas DataFrame containing the data.
        """
        arff_data = self.parser.parse_string(arff_content)
        return arff_data.data


# Convenience functions


def csv_to_arff(
    csv_path: str | Path,
    arff_path: str | Path,
    relation_name: str | None = None,
    nominal_columns: list[str] | None = None,
    string_columns: list[str] | None = None,
    date_columns: dict[str, str] | None = None,
    comments: list[str] | None = None,
    exclude_columns: list[str] | None = None,
    missing_value: str = "?",
    **csv_kwargs: Any,
) -> ArffData:
    """Convert a CSV file to ARFF format.

    This is a convenience function that creates an ArffConverter and
    performs the conversion.

    Args:
        csv_path: Path to the input CSV file.
        arff_path: Path to the output ARFF file.
        relation_name: Name of the relation. Defaults to CSV filename.
        nominal_columns: List of column names to treat as nominal.
        string_columns: List of column names to treat as string.
        date_columns: Dict mapping column names to date format strings.
        comments: List of comments to include in the ARFF file.
        exclude_columns: List of column names to exclude from the conversion.
        missing_value: String used to represent missing values.
        **csv_kwargs: Additional arguments passed to pd.read_csv().

    Returns:
        ArffData object containing the converted data.

    Example:
        >>> csv_to_arff("iris.csv", "iris.arff", nominal_columns=["class"])
    """
    converter = ArffConverter(missing_value=missing_value)
    return converter.csv_to_arff(
        csv_path=csv_path,
        arff_path=arff_path,
        relation_name=relation_name,
        nominal_columns=nominal_columns,
        string_columns=string_columns,
        date_columns=date_columns,
        comments=comments,
        exclude_columns=exclude_columns,
        **csv_kwargs,
    )


def arff_to_csv(
    arff_path: str | Path,
    csv_path: str | Path,
    include_index: bool = False,
    missing_value: str = "?",
    **csv_kwargs: Any,
) -> pd.DataFrame:
    """Convert an ARFF file to CSV format.

    This is a convenience function that creates an ArffConverter and
    performs the conversion.

    Args:
        arff_path: Path to the input ARFF file.
        csv_path: Path to the output CSV file.
        include_index: Whether to include the DataFrame index.
        missing_value: String used to represent missing values.
        **csv_kwargs: Additional arguments passed to df.to_csv().

    Returns:
        pandas DataFrame containing the converted data.

    Example:
        >>> df = arff_to_csv("iris.arff", "iris.csv")
    """
    converter = ArffConverter(missing_value=missing_value)
    return converter.arff_to_csv(
        arff_path=arff_path,
        csv_path=csv_path,
        include_index=include_index,
        **csv_kwargs,
    )
