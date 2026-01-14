"""Unit tests for User Defined Attributes module."""

import pytest

from taskng.core.uda import (
    format_uda_value,
    parse_udas_from_text,
    validate_uda_value,
)


class TestParseUdasFromText:
    """Tests for parse_udas_from_text function."""

    def test_empty_string(self) -> None:
        """Should return empty text and empty dict."""
        text, udas = parse_udas_from_text("")
        assert text == ""
        assert udas == {}

    def test_no_udas(self) -> None:
        """Should return original text without UDAs."""
        text, udas = parse_udas_from_text("Simple task description")
        assert text == "Simple task description"
        assert udas == {}

    def test_single_uda(self) -> None:
        """Should extract single UDA."""
        text, udas = parse_udas_from_text("Task client:Acme")
        assert text == "Task"
        assert udas == {"client": "Acme"}

    def test_multiple_udas(self) -> None:
        """Should extract multiple UDAs."""
        text, udas = parse_udas_from_text("Task client:Acme size:L")
        assert text == "Task"
        assert udas == {"client": "Acme", "size": "L"}

    def test_uda_in_middle(self) -> None:
        """Should extract UDA from middle of text."""
        text, udas = parse_udas_from_text("Fix client:Acme bug")
        assert text == "Fix bug"
        assert udas == {"client": "Acme"}

    def test_reserved_words_excluded(self) -> None:
        """Should not treat reserved words as UDAs."""
        reserved = [
            "project",
            "priority",
            "due",
            "wait",
            "scheduled",
            "recur",
            "until",
            "status",
        ]
        for word in reserved:
            text, udas = parse_udas_from_text(f"Task {word}:value")
            assert word not in udas

    def test_uda_with_numbers(self) -> None:
        """Should extract UDA with numeric value."""
        text, udas = parse_udas_from_text("Task sprint:5")
        assert udas == {"sprint": "5"}

    def test_uda_with_underscore(self) -> None:
        """Should extract UDA name with underscore."""
        text, udas = parse_udas_from_text("Task story_points:8")
        assert udas == {"story_points": "8"}

    def test_uda_value_with_hyphen(self) -> None:
        """Should extract UDA value with hyphen."""
        text, udas = parse_udas_from_text("Task level:high-priority")
        assert udas == {"level": "high-priority"}

    def test_uda_name_starting_with_letter(self) -> None:
        """Should only match UDA names starting with letter or underscore."""
        text, udas = parse_udas_from_text("Task _private:value")
        assert udas == {"_private": "value"}

    def test_uda_name_with_numbers(self) -> None:
        """Should match UDA name containing numbers."""
        text, udas = parse_udas_from_text("Task field2:value")
        assert udas == {"field2": "value"}

    def test_removes_uda_from_text(self) -> None:
        """Should remove UDA pattern from text."""
        text, udas = parse_udas_from_text("Task client:Acme description")
        assert "client:Acme" not in text
        assert udas == {"client": "Acme"}

    def test_case_sensitive_reserved_words(self) -> None:
        """Reserved words should be case-insensitive."""
        text, udas = parse_udas_from_text("Task PROJECT:Work")
        assert "PROJECT" not in udas
        assert "project" not in udas


class TestValidateUdaValue:
    """Tests for validate_uda_value function."""

    def test_none_returns_empty_string(self) -> None:
        """Should return empty string for None."""
        result = validate_uda_value(None)
        assert result == ""

    def test_none_with_numeric_type(self) -> None:
        """Should return empty string for None even with numeric type."""
        result = validate_uda_value(None, "numeric")
        assert result == ""

    def test_string_value(self) -> None:
        """Should return string as-is."""
        result = validate_uda_value("test")
        assert result == "test"

    def test_numeric_string(self) -> None:
        """Should validate numeric string."""
        result = validate_uda_value("42", "numeric")
        assert result == "42"

    def test_numeric_float_string(self) -> None:
        """Should validate float string."""
        result = validate_uda_value("3.14", "numeric")
        assert result == "3.14"

    def test_numeric_integer(self) -> None:
        """Should validate integer."""
        result = validate_uda_value(42, "numeric")
        assert result == "42"

    def test_numeric_float(self) -> None:
        """Should validate float."""
        result = validate_uda_value(3.14, "numeric")
        assert result == "3.14"

    def test_invalid_numeric_raises_error(self) -> None:
        """Should raise ValueError for invalid numeric."""
        with pytest.raises(ValueError) as exc_info:
            validate_uda_value("not-a-number", "numeric")
        assert "Invalid numeric value" in str(exc_info.value)

    def test_invalid_numeric_none_type(self) -> None:
        """Should handle None separately before numeric validation."""
        # None is handled before numeric check
        result = validate_uda_value(None, "numeric")
        assert result == ""

    def test_converts_to_string(self) -> None:
        """Should convert any value to string."""
        result = validate_uda_value(123)
        assert result == "123"
        assert isinstance(result, str)

    def test_boolean_as_string(self) -> None:
        """Should convert boolean to string."""
        result = validate_uda_value(True)
        assert result == "True"

    def test_negative_numeric(self) -> None:
        """Should validate negative numeric."""
        result = validate_uda_value("-5", "numeric")
        assert result == "-5"

    def test_scientific_notation(self) -> None:
        """Should validate scientific notation."""
        result = validate_uda_value("1e10", "numeric")
        assert result == "1e10"


class TestFormatUdaValue:
    """Tests for format_uda_value function."""

    def test_empty_string_returns_empty(self) -> None:
        """Should return empty string for empty input."""
        result = format_uda_value("")
        assert result == ""

    def test_none_value_coerced(self) -> None:
        """Empty string check handles falsy values."""
        result = format_uda_value("")
        assert result == ""

    def test_string_value_unchanged(self) -> None:
        """Should return string value unchanged."""
        result = format_uda_value("test")
        assert result == "test"

    def test_string_type_default(self) -> None:
        """Should use string type by default."""
        result = format_uda_value("42")
        assert result == "42"

    def test_numeric_integer_formatted(self) -> None:
        """Should format integer without decimal."""
        result = format_uda_value("42.0", "numeric")
        assert result == "42"

    def test_numeric_float_preserved(self) -> None:
        """Should preserve float with decimal."""
        result = format_uda_value("3.14", "numeric")
        assert result == "3.14"

    def test_numeric_negative_integer(self) -> None:
        """Should format negative integer."""
        result = format_uda_value("-5.0", "numeric")
        assert result == "-5"

    def test_numeric_negative_float(self) -> None:
        """Should preserve negative float."""
        result = format_uda_value("-3.14", "numeric")
        assert result == "-3.14"

    def test_numeric_invalid_returns_original(self) -> None:
        """Should return original value if not valid numeric."""
        result = format_uda_value("not-a-number", "numeric")
        assert result == "not-a-number"

    def test_numeric_zero(self) -> None:
        """Should format zero correctly."""
        result = format_uda_value("0.0", "numeric")
        assert result == "0"

    def test_numeric_small_float(self) -> None:
        """Should preserve small float."""
        result = format_uda_value("0.5", "numeric")
        assert result == "0.5"

    def test_numeric_large_integer(self) -> None:
        """Should format large integer."""
        result = format_uda_value("1000000.0", "numeric")
        assert result == "1000000"

    def test_date_type_unchanged(self) -> None:
        """Should return date value unchanged."""
        result = format_uda_value("2024-01-15", "date")
        assert result == "2024-01-15"

    def test_duration_type_unchanged(self) -> None:
        """Should return duration value unchanged."""
        result = format_uda_value("2h", "duration")
        assert result == "2h"
