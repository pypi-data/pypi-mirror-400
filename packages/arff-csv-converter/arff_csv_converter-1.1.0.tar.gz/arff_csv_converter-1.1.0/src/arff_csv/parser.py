"""
ARFF file parser.

This module provides functionality to parse ARFF (Attribute-Relation File Format)
files, which are commonly used by the Weka machine learning toolkit.

The ARFF format consists of:
- A relation name (header)
- Attribute definitions (name and type)
- Data section with instances

Supported attribute types:
- NUMERIC / REAL / INTEGER: Numeric values
- STRING: String values (quoted)
- NOMINAL: Categorical values defined as {value1, value2, ...}
- DATE: Date values with optional format specification

Example ARFF file:
    @RELATION iris

    @ATTRIBUTE sepallength NUMERIC
    @ATTRIBUTE class {Iris-setosa, Iris-versicolor, Iris-virginica}

    @DATA
    5.1,Iris-setosa
    7.0,Iris-versicolor
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TextIO

import numpy as np
import pandas as pd

from arff_csv.exceptions import ArffParseError, MissingDataError


class AttributeType(Enum):
    """Enumeration of supported ARFF attribute types."""

    NUMERIC = auto()
    REAL = auto()
    INTEGER = auto()
    STRING = auto()
    NOMINAL = auto()
    DATE = auto()


@dataclass
class Attribute:
    """Represents an ARFF attribute definition.

    Attributes:
        name: The name of the attribute.
        type: The type of the attribute (NUMERIC, STRING, NOMINAL, DATE).
        nominal_values: List of possible values for NOMINAL attributes.
        date_format: Format string for DATE attributes.
    """

    name: str
    type: AttributeType
    nominal_values: list[str] | None = None
    date_format: str | None = None

    def is_numeric(self) -> bool:
        """Check if the attribute is numeric."""
        return self.type in (
            AttributeType.NUMERIC,
            AttributeType.REAL,
            AttributeType.INTEGER,
        )


@dataclass
class ArffData:
    """Container for parsed ARFF data.

    This class holds all information extracted from an ARFF file,
    including metadata and the data itself.

    Attributes:
        relation_name: The name of the relation (dataset).
        attributes: List of attribute definitions.
        data: The data as a pandas DataFrame.
        comments: List of comments found in the file.
    """

    relation_name: str
    attributes: list[Attribute]
    data: pd.DataFrame
    comments: list[str] = field(default_factory=list)

    def get_attribute_names(self) -> list[str]:
        """Get list of attribute names."""
        return [attr.name for attr in self.attributes]

    def get_numeric_attributes(self) -> list[str]:
        """Get list of numeric attribute names."""
        return [attr.name for attr in self.attributes if attr.is_numeric()]

    def get_nominal_attributes(self) -> list[str]:
        """Get list of nominal attribute names."""
        return [
            attr.name for attr in self.attributes if attr.type == AttributeType.NOMINAL
        ]

    def get_date_attributes(self) -> list[str]:
        """Get list of date attribute names."""
        return [
            attr.name for attr in self.attributes if attr.type == AttributeType.DATE
        ]


class ArffParser:
    """Parser for ARFF (Attribute-Relation File Format) files.

    This class provides methods to parse ARFF files and extract
    the relation name, attributes, and data.

    Example:
        >>> parser = ArffParser()
        >>> arff_data = parser.parse_file("data.arff")
        >>> print(arff_data.relation_name)
        >>> print(arff_data.data.head())
    """

    # Regex patterns for parsing ARFF elements
    _RELATION_PATTERN = re.compile(r"^@relation\s+(.+)$", re.IGNORECASE)
    _ATTRIBUTE_PATTERN = re.compile(r"^@attribute\s+(.+)$", re.IGNORECASE)
    _DATA_PATTERN = re.compile(r"^@data\s*$", re.IGNORECASE)
    _COMMENT_PATTERN = re.compile(r"%(.*)$")

    # Pattern for quoted strings
    _QUOTED_STRING = re.compile(r'^["\'](.+)["\']$')

    # Pattern for nominal values
    _NOMINAL_PATTERN = re.compile(r"^\{(.+)\}$")

    def __init__(self, missing_value: str = "?") -> None:
        """Initialize the parser.

        Args:
            missing_value: The string used to represent missing values.
                          Defaults to "?" (ARFF standard).
        """
        self.missing_value = missing_value

    def parse_file(self, filepath: str | Path) -> ArffData:
        """Parse an ARFF file from disk.

        Args:
            filepath: Path to the ARFF file.

        Returns:
            ArffData containing the parsed relation, attributes, and data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ArffParseError: If the file contains syntax errors.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"ARFF file not found: {filepath}")

        with filepath.open(encoding="utf-8") as f:
            return self.parse(f)

    def parse_string(self, content: str) -> ArffData:
        """Parse ARFF content from a string.

        Args:
            content: ARFF file content as a string.

        Returns:
            ArffData containing the parsed relation, attributes, and data.

        Raises:
            ArffParseError: If the content contains syntax errors.
        """
        from io import StringIO

        return self.parse(StringIO(content))

    def parse(self, file_obj: TextIO) -> ArffData:
        """Parse ARFF content from a file-like object.

        Args:
            file_obj: A file-like object containing ARFF content.

        Returns:
            ArffData containing the parsed relation, attributes, and data.

        Raises:
            ArffParseError: If the content contains syntax errors.
            MissingDataError: If required sections are missing.
        """
        relation_name: str | None = None
        attributes: list[Attribute] = []
        data_rows: list[list[str]] = []
        comments: list[str] = []
        in_data_section = False
        line_number = 0

        for line in file_obj:
            line_number += 1
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Handle comments (both full-line and inline)
            if "%" in line:
                # Check if the line starts with a comment
                comment_match = self._COMMENT_PATTERN.match(line)
                if comment_match:
                    # Full-line comment
                    comments.append(comment_match.group(1).strip())
                    continue
                else:
                    # Inline comment - strip it from the line
                    # Find % that's not inside quotes
                    comment_pos = -1
                    in_quotes = False
                    quote_char = None

                    for i, char in enumerate(line):
                        if char in ('"', "'") and not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char and in_quotes:
                            in_quotes = False
                            quote_char = None
                        elif char == "%" and not in_quotes:
                            comment_pos = i
                            break

                    if comment_pos > 0:
                        comment_text = line[comment_pos + 1 :].strip()
                        if comment_text:
                            comments.append(comment_text)
                        line = line[:comment_pos].strip()
                        if not line:
                            continue

            # Parse based on current section
            if in_data_section:
                # Parse data row
                row = self._parse_data_row(line, len(attributes), line_number)
                data_rows.append(row)
            else:
                # Parse header section
                if self._DATA_PATTERN.match(line):
                    in_data_section = True
                    continue

                relation_match = self._RELATION_PATTERN.match(line)
                if relation_match:
                    relation_name = self._clean_string(relation_match.group(1))
                    continue

                attr_match = self._ATTRIBUTE_PATTERN.match(line)
                if attr_match:
                    attr = self._parse_attribute(attr_match.group(1), line_number)
                    attributes.append(attr)
                    continue

                # Unknown line in header section
                if line.startswith("@"):
                    raise ArffParseError(
                        f"Unknown directive: {line.split()[0]}",
                        line_number,
                        line,
                    )

        # Validate parsed content
        if relation_name is None:
            raise MissingDataError("No @RELATION found in ARFF file")

        if not attributes:
            raise MissingDataError("No @ATTRIBUTE definitions found in ARFF file")

        # Create DataFrame
        df = self._create_dataframe(data_rows, attributes)

        return ArffData(
            relation_name=relation_name,
            attributes=attributes,
            data=df,
            comments=comments,
        )

    def _clean_string(self, s: str) -> str:
        """Remove quotes from a string if present."""
        s = s.strip()
        match = self._QUOTED_STRING.match(s)
        if match:
            return match.group(1)
        return s

    def _parse_attribute(self, attr_def: str, line_number: int) -> Attribute:
        """Parse an attribute definition.

        Args:
            attr_def: The attribute definition string (after @ATTRIBUTE).
            line_number: Current line number for error reporting.

        Returns:
            Parsed Attribute object.

        Raises:
            ArffParseError: If the attribute definition is invalid.
        """
        attr_def = attr_def.strip()

        # Handle quoted attribute names
        if attr_def.startswith(("'", '"')):
            quote_char = attr_def[0]
            end_quote = attr_def.find(quote_char, 1)
            if end_quote == -1:
                raise ArffParseError(
                    "Unclosed quote in attribute name",
                    line_number,
                    attr_def,
                )
            name = attr_def[1:end_quote]
            type_def = attr_def[end_quote + 1 :].strip()
        else:
            # Split on first whitespace
            parts = attr_def.split(None, 1)
            if len(parts) < 2:
                raise ArffParseError(
                    "Invalid attribute definition (missing type)",
                    line_number,
                    attr_def,
                )
            name = parts[0]
            type_def = parts[1].strip()

        # Parse attribute type
        type_def_upper = type_def.upper()

        if type_def_upper in ("NUMERIC", "REAL"):
            return Attribute(name=name, type=AttributeType.NUMERIC)

        if type_def_upper == "INTEGER":
            return Attribute(name=name, type=AttributeType.INTEGER)

        if type_def_upper == "STRING":
            return Attribute(name=name, type=AttributeType.STRING)

        if type_def_upper.startswith("DATE"):
            date_format = None
            if len(type_def) > 4:
                date_format = self._clean_string(type_def[4:].strip())
            return Attribute(
                name=name, type=AttributeType.DATE, date_format=date_format
            )

        # Check for nominal type
        nominal_match = self._NOMINAL_PATTERN.match(type_def)
        if nominal_match:
            values_str = nominal_match.group(1)
            values = self._parse_nominal_values(values_str)
            return Attribute(
                name=name, type=AttributeType.NOMINAL, nominal_values=values
            )

        raise ArffParseError(
            f"Unknown attribute type: {type_def}",
            line_number,
            attr_def,
        )

    def _parse_nominal_values(self, values_str: str) -> list[str]:
        """Parse nominal values from a string like 'val1, val2, val3'.

        Handles quoted values and values with commas inside quotes.
        """
        values: list[str] = []
        current = ""
        in_quotes = False
        quote_char = None

        for char in values_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == "," and not in_quotes:
                value = current.strip()
                if value:
                    values.append(self._clean_string(value))
                current = ""
            else:
                current += char

        # Don't forget the last value
        value = current.strip()
        if value:
            values.append(self._clean_string(value))

        return values

    def _parse_data_row(
        self, line: str, num_attributes: int, line_number: int
    ) -> list[str]:
        """Parse a data row.

        Handles:
        - Comma-separated values
        - Quoted strings with commas
        - Missing values (?)
        - Sparse format {index value, ...}

        Args:
            line: The data line to parse.
            num_attributes: Expected number of attributes.
            line_number: Current line number for error reporting.

        Returns:
            List of string values for the row.

        Raises:
            ArffParseError: If the row is malformed.
        """
        # Check for sparse format
        if line.startswith("{") and line.endswith("}"):
            return self._parse_sparse_row(line, num_attributes, line_number)

        # Parse regular format
        values: list[str] = []
        current = ""
        in_quotes = False
        quote_char = None

        for char in line:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current += char
            elif char == "," and not in_quotes:
                values.append(self._clean_value(current))
                current = ""
            else:
                current += char

        # Add the last value
        values.append(self._clean_value(current))

        if len(values) != num_attributes:
            raise ArffParseError(
                f"Wrong number of values (expected {num_attributes}, got {len(values)})",
                line_number,
                line,
            )

        return values

    def _parse_sparse_row(
        self, line: str, num_attributes: int, line_number: int
    ) -> list[str]:
        """Parse a sparse format data row.

        Sparse format: {index value, index value, ...}
        Unspecified indices are treated as 0 or missing.
        """
        # Initialize with missing values
        values = [self.missing_value] * num_attributes

        # Remove braces
        content = line[1:-1].strip()
        if not content:
            return values

        # Parse index-value pairs
        pairs = content.split(",")
        for pair in pairs:
            pair = pair.strip()
            if not pair:
                continue

            parts = pair.split(None, 1)
            if len(parts) != 2:
                raise ArffParseError(
                    "Invalid sparse format",
                    line_number,
                    line,
                )

            try:
                idx = int(parts[0])
                if idx < 0 or idx >= num_attributes:
                    raise ArffParseError(
                        f"Sparse index out of range: {idx}",
                        line_number,
                        line,
                    )
                values[idx] = self._clean_value(parts[1])
            except ValueError as e:
                raise ArffParseError(
                    f"Invalid sparse index: {parts[0]}",
                    line_number,
                    line,
                ) from e

        return values

    def _clean_value(self, value: str) -> str:
        """Clean a data value, removing whitespace and quotes."""
        value = value.strip()
        if not value:
            return self.missing_value

        # Remove surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
            value = value[1:-1]

        return value

    def _create_dataframe(
        self, data_rows: list[list[str]], attributes: list[Attribute]
    ) -> pd.DataFrame:
        """Create a pandas DataFrame from parsed data.

        Args:
            data_rows: List of data rows (each row is a list of strings).
            attributes: List of attribute definitions.

        Returns:
            pandas DataFrame with appropriate dtypes.
        """
        if not data_rows:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=[attr.name for attr in attributes])

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=[attr.name for attr in attributes])

        # Convert types
        for attr in attributes:
            col = attr.name
            # Replace missing values with NaN
            df[col] = df[col].mask(df[col] == self.missing_value, np.nan)

            if attr.is_numeric():
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif attr.type == AttributeType.NOMINAL:
                # Convert to categorical
                if attr.nominal_values:
                    # Ensure data values are strings to match category strings
                    # This handles cases where numeric-looking values need to match
                    df[col] = df[col].apply(
                        lambda x: str(x).strip() if pd.notna(x) else x
                    )
                    df[col] = pd.Categorical(
                        df[col],
                        categories=attr.nominal_values,
                        ordered=False,
                    )
            elif attr.type == AttributeType.DATE:
                # Try to parse dates
                try:
                    if attr.date_format:
                        df[col] = pd.to_datetime(df[col], format=attr.date_format)
                    else:
                        df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    # Keep as string if parsing fails
                    pass

        return df
