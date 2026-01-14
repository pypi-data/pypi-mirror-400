"""
Custom exceptions for the ARFF-CSV converter.

This module defines a hierarchy of exceptions for handling errors
during ARFF and CSV file parsing, writing, and conversion.
"""


class ArffCsvError(Exception):
    """Base exception for all ARFF-CSV converter errors.

    All custom exceptions in this module inherit from this class,
    allowing users to catch all converter-related errors with a single
    exception handler.

    Attributes:
        message: A human-readable description of the error.
        details: Optional additional details about the error.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: A human-readable description of the error.
            details: Optional additional details about the error.
        """
        self.message = message
        self.details = details
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the exception message."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ArffParseError(ArffCsvError):
    """Exception raised when parsing an ARFF file fails.

    This exception is raised when the ARFF file contains syntax errors,
    invalid attribute definitions, or malformed data sections.

    Attributes:
        message: Description of the parsing error.
        line_number: The line number where the error occurred (if available).
        line_content: The content of the problematic line (if available).
    """

    def __init__(
        self,
        message: str,
        line_number: int | None = None,
        line_content: str | None = None,
    ) -> None:
        """Initialize the parse error.

        Args:
            message: Description of the parsing error.
            line_number: The line number where the error occurred.
            line_content: The content of the problematic line.
        """
        self.line_number = line_number
        self.line_content = line_content
        details = None
        if line_number is not None:
            details = f"line {line_number}"
            if line_content:
                details += f": '{line_content}'"
        super().__init__(message, details)


class ArffWriteError(ArffCsvError):
    """Exception raised when writing an ARFF file fails.

    This exception is raised when there's an error during the ARFF
    file generation process, such as I/O errors or data validation failures.
    """

    pass


class CsvParseError(ArffCsvError):
    """Exception raised when parsing a CSV file fails.

    This exception is raised when the CSV file cannot be read or
    contains invalid data that cannot be processed.

    Attributes:
        message: Description of the parsing error.
        row_number: The row number where the error occurred (if available).
    """

    def __init__(self, message: str, row_number: int | None = None) -> None:
        """Initialize the CSV parse error.

        Args:
            message: Description of the parsing error.
            row_number: The row number where the error occurred.
        """
        self.row_number = row_number
        details = f"row {row_number}" if row_number is not None else None
        super().__init__(message, details)


class InvalidAttributeError(ArffCsvError):
    """Exception raised for invalid attribute definitions.

    This exception is raised when an attribute definition is malformed,
    contains an unsupported type, or has invalid nominal values.

    Attributes:
        message: Description of the error.
        attribute_name: The name of the invalid attribute.
    """

    def __init__(self, message: str, attribute_name: str | None = None) -> None:
        """Initialize the attribute error.

        Args:
            message: Description of the error.
            attribute_name: The name of the invalid attribute.
        """
        self.attribute_name = attribute_name
        details = f"attribute '{attribute_name}'" if attribute_name else None
        super().__init__(message, details)


class MissingDataError(ArffCsvError):
    """Exception raised when required data is missing.

    This exception is raised when required data is not found,
    such as missing relation name, attributes, or data section.
    """

    pass
