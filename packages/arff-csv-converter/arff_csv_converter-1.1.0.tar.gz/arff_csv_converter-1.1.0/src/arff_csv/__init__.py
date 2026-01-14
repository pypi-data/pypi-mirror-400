"""
ARFF-CSV Converter.

A Python library for converting between CSV and ARFF (Weka) file formats.

This module provides functionality to:
- Convert CSV files to ARFF format (Weka's Attribute-Relation File Format)
- Convert ARFF files to CSV format
- Automatically detect data types and handle nominal attributes
- Preserve data integrity during conversions
"""

from arff_csv.converter import ArffConverter, arff_to_csv, csv_to_arff
from arff_csv.exceptions import (
    ArffCsvError,
    ArffParseError,
    ArffWriteError,
    CsvParseError,
    InvalidAttributeError,
    MissingDataError,
)
from arff_csv.parser import ArffData, ArffParser
from arff_csv.writer import ArffWriter

__version__ = "1.0.0"
__author__ = "Ricardo Montañana"
__email__ = "ricardo.montanana@example.com"

__all__ = [
    "ArffConverter",
    "ArffCsvError",
    "ArffData",
    "ArffParseError",
    "ArffParser",
    "ArffWriteError",
    "ArffWriter",
    "CsvParseError",
    "InvalidAttributeError",
    "MissingDataError",
    "__author__",
    "__email__",
    "__version__",
    "arff_to_csv",
    "csv_to_arff",
]
