"""
Tests for custom exceptions.
"""

from __future__ import annotations

import pytest

from arff_csv.exceptions import (
    ArffCsvError,
    ArffParseError,
    ArffWriteError,
    CsvParseError,
    InvalidAttributeError,
    MissingDataError,
)


class TestArffCsvError:
    """Tests for base ArffCsvError."""

    def test_message_only(self) -> None:
        """Test error with message only."""
        error = ArffCsvError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details is None

    def test_message_with_details(self) -> None:
        """Test error with message and details."""
        error = ArffCsvError("Test error", "additional info")
        assert str(error) == "Test error: additional info"
        assert error.message == "Test error"
        assert error.details == "additional info"

    def test_inheritance(self) -> None:
        """Test that ArffCsvError is an Exception."""
        error = ArffCsvError("Test")
        assert isinstance(error, Exception)


class TestArffParseError:
    """Tests for ArffParseError."""

    def test_basic_error(self) -> None:
        """Test basic parse error."""
        error = ArffParseError("Parse failed")
        assert "Parse failed" in str(error)

    def test_with_line_number(self) -> None:
        """Test error with line number."""
        error = ArffParseError("Parse failed", line_number=42)
        assert "line 42" in str(error)
        assert error.line_number == 42

    def test_with_line_content(self) -> None:
        """Test error with line content."""
        error = ArffParseError("Parse failed", line_number=42, line_content="invalid data")
        assert "line 42" in str(error)
        assert "invalid data" in str(error)
        assert error.line_content == "invalid data"

    def test_inheritance(self) -> None:
        """Test inheritance from ArffCsvError."""
        error = ArffParseError("Test")
        assert isinstance(error, ArffCsvError)

    def test_catchable_as_base(self) -> None:
        """Test that ArffParseError can be caught as ArffCsvError."""
        with pytest.raises(ArffCsvError):
            raise ArffParseError("Test error")


class TestArffWriteError:
    """Tests for ArffWriteError."""

    def test_basic_error(self) -> None:
        """Test basic write error."""
        error = ArffWriteError("Write failed")
        assert str(error) == "Write failed"

    def test_with_details(self) -> None:
        """Test write error with details."""
        error = ArffWriteError("Write failed", "file not writable")
        assert "Write failed: file not writable" in str(error)

    def test_inheritance(self) -> None:
        """Test inheritance from ArffCsvError."""
        error = ArffWriteError("Test")
        assert isinstance(error, ArffCsvError)


class TestCsvParseError:
    """Tests for CsvParseError."""

    def test_basic_error(self) -> None:
        """Test basic CSV parse error."""
        error = CsvParseError("CSV parse failed")
        assert "CSV parse failed" in str(error)

    def test_with_row_number(self) -> None:
        """Test error with row number."""
        error = CsvParseError("Invalid data", row_number=10)
        assert "row 10" in str(error)
        assert error.row_number == 10

    def test_inheritance(self) -> None:
        """Test inheritance from ArffCsvError."""
        error = CsvParseError("Test")
        assert isinstance(error, ArffCsvError)


class TestInvalidAttributeError:
    """Tests for InvalidAttributeError."""

    def test_basic_error(self) -> None:
        """Test basic attribute error."""
        error = InvalidAttributeError("Invalid type")
        assert "Invalid type" in str(error)

    def test_with_attribute_name(self) -> None:
        """Test error with attribute name."""
        error = InvalidAttributeError("Invalid type", attribute_name="age")
        assert "attribute 'age'" in str(error)
        assert error.attribute_name == "age"

    def test_inheritance(self) -> None:
        """Test inheritance from ArffCsvError."""
        error = InvalidAttributeError("Test")
        assert isinstance(error, ArffCsvError)


class TestMissingDataError:
    """Tests for MissingDataError."""

    def test_basic_error(self) -> None:
        """Test basic missing data error."""
        error = MissingDataError("Data section missing")
        assert str(error) == "Data section missing"

    def test_with_details(self) -> None:
        """Test error with details."""
        error = MissingDataError("Required field missing", "field_name")
        assert "Required field missing: field_name" in str(error)

    def test_inheritance(self) -> None:
        """Test inheritance from ArffCsvError."""
        error = MissingDataError("Test")
        assert isinstance(error, ArffCsvError)


class TestExceptionHierarchy:
    """Tests for exception hierarchy behavior."""

    def test_catch_all_with_base(self) -> None:
        """Test catching all converter errors with base class."""
        exceptions = [
            ArffParseError("parse"),
            ArffWriteError("write"),
            CsvParseError("csv"),
            InvalidAttributeError("attr"),
            MissingDataError("missing"),
        ]

        for exc in exceptions:
            with pytest.raises(ArffCsvError):
                raise exc

    def test_specific_catch(self) -> None:
        """Test catching specific exceptions."""
        with pytest.raises(ArffParseError):
            raise ArffParseError("Test")

        with pytest.raises(CsvParseError):
            raise CsvParseError("Test")

    def test_exception_not_caught_wrongly(self) -> None:
        """Test that exceptions are not caught by wrong handlers."""
        with pytest.raises(ArffParseError):
            try:
                raise ArffParseError("Test")
            except CsvParseError:
                pass  # Should not catch ArffParseError
