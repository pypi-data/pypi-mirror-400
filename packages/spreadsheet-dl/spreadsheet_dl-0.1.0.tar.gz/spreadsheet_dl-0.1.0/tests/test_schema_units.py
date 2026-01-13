"""
Tests for schema/units.py - Length value object.

Implements tests for : Length Value Object
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.schema.units import (
    Length,
    LengthUnit,
    cm,
    inches,
    mm,
    parse_length,
    pt,
)

pytestmark = [pytest.mark.unit, pytest.mark.validation]


class TestLengthCreation:
    """Tests for Length creation."""

    def test_create_with_enum_unit(self) -> None:
        """Test creating Length with LengthUnit enum."""
        length = Length(12, LengthUnit.PT)
        assert length.value == 12
        assert length.unit == LengthUnit.PT

    def test_create_with_string_unit(self) -> None:
        """Test creating Length with string unit."""
        length = Length(2.5, "cm")
        assert length.value == 2.5
        assert length.unit == LengthUnit.CM

    def test_create_with_invalid_unit_raises(self) -> None:
        """Test invalid unit raises error."""
        with pytest.raises(ValueError, match="Unknown unit"):
            Length(10, "invalid")

    def test_parse_valid_string(self) -> None:
        """Test parsing valid length string."""
        length = Length.parse("12pt")
        assert length.value == 12
        assert length.unit == LengthUnit.PT

    def test_parse_with_decimal(self) -> None:
        """Test parsing decimal values."""
        length = Length.parse("2.5cm")
        assert length.value == 2.5
        assert length.unit == LengthUnit.CM

    def test_parse_with_spaces(self) -> None:
        """Test parsing with leading/trailing spaces."""
        length = Length.parse("  12pt  ")
        assert length.value == 12

    def test_parse_negative_value(self) -> None:
        """Test parsing negative values."""
        length = Length.parse("-5mm")
        assert length.value == -5
        assert length.unit == LengthUnit.MM

    def test_parse_invalid_format_raises(self) -> None:
        """Test invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid length format"):
            Length.parse("invalid")

    def test_parse_no_unit_raises(self) -> None:
        """Test missing unit raises error."""
        with pytest.raises(ValueError, match="Invalid length format"):
            Length.parse("12")

    def test_factory_methods(self) -> None:
        """Test factory methods."""
        assert Length.pt(12).unit == LengthUnit.PT
        assert Length.px(12).unit == LengthUnit.PX
        assert Length.cm(2.5).unit == LengthUnit.CM
        assert Length.mm(25).unit == LengthUnit.MM
        assert Length.inches(1).unit == LengthUnit.IN
        assert Length.em(1.5).unit == LengthUnit.EM
        assert Length.percent(50).unit == LengthUnit.PERCENT


class TestLengthConversion:
    """Tests for Length unit conversion."""

    def test_to_points_from_pt(self) -> None:
        """Test converting pt to points."""
        length = Length.pt(72)
        assert length.to_points() == 72

    def test_to_points_from_inches(self) -> None:
        """Test converting inches to points."""
        length = Length.inches(1)
        assert length.to_points() == 72

    def test_to_points_from_cm(self) -> None:
        """Test converting cm to points."""
        length = Length.cm(2.54)
        assert abs(length.to_points() - 72) < 0.1  # 1 inch = 2.54 cm = 72pt

    def test_to_cm(self) -> None:
        """Test converting to cm."""
        length = Length.inches(1)
        assert abs(length.to_cm() - 2.54) < 0.01

    def test_to_mm(self) -> None:
        """Test converting to mm."""
        length = Length.cm(1)
        assert abs(length.to_mm() - 10) < 0.1

    def test_to_inches(self) -> None:
        """Test converting to inches."""
        length = Length.pt(72)
        assert length.to_inches() == 1.0

    def test_to_unit(self) -> None:
        """Test converting to specified unit."""
        length = Length.pt(72)
        converted = length.to_unit(LengthUnit.IN)
        assert converted.value == 1.0
        assert converted.unit == LengthUnit.IN

    def test_to_unit_same_unit(self) -> None:
        """Test converting to same unit returns self."""
        length = Length.pt(72)
        converted = length.to_unit(LengthUnit.PT)
        assert converted is length

    def test_percent_conversion_raises(self) -> None:
        """Test percentage cannot be converted to points."""
        length = Length.percent(50)
        with pytest.raises(ValueError, match="Cannot convert percentage"):
            length.to_points()


class TestLengthArithmetic:
    """Tests for Length arithmetic operations."""

    def test_add_same_unit(self) -> None:
        """Test adding lengths with same unit."""
        result = Length.pt(12) + Length.pt(4)
        assert result.value == 16
        assert result.unit == LengthUnit.PT

    def test_add_different_units(self) -> None:
        """Test adding lengths with different units."""
        result = Length.pt(72) + Length.inches(1)  # 72pt + 72pt
        assert abs(result.value - 144) < 0.1
        assert result.unit == LengthUnit.PT

    def test_subtract_same_unit(self) -> None:
        """Test subtracting lengths."""
        result = Length.pt(16) - Length.pt(4)
        assert result.value == 12

    def test_multiply_by_scalar(self) -> None:
        """Test multiplying by scalar."""
        result = Length.pt(12) * 2
        assert result.value == 24
        assert result.unit == LengthUnit.PT

    def test_rmul_by_scalar(self) -> None:
        """Test right multiply."""
        result = 2 * Length.pt(12)
        assert result.value == 24

    def test_divide_by_scalar(self) -> None:
        """Test dividing by scalar."""
        result = Length.pt(24) / 2
        assert result.value == 12

    def test_divide_by_zero_raises(self) -> None:
        """Test division by zero raises error."""
        with pytest.raises(ZeroDivisionError):
            Length.pt(12) / 0

    def test_negate(self) -> None:
        """Test negation."""
        result = -Length.pt(12)
        assert result.value == -12

    def test_absolute(self) -> None:
        """Test absolute value."""
        result = abs(Length.pt(-12))
        assert result.value == 12


class TestLengthComparison:
    """Tests for Length comparison."""

    def test_equal_same_unit(self) -> None:
        """Test equality with same unit."""
        assert Length.pt(12) == Length.pt(12)

    def test_equal_different_units(self) -> None:
        """Test equality with different units (converted)."""
        assert Length.inches(1) == Length.pt(72)

    def test_not_equal(self) -> None:
        """Test inequality."""
        assert Length.pt(12) != Length.pt(24)

    def test_less_than(self) -> None:
        """Test less than."""
        assert Length.pt(12) < Length.pt(24)

    def test_less_than_different_units(self) -> None:
        """Test less than with different units."""
        assert Length.pt(36) < Length.inches(1)

    def test_greater_than(self) -> None:
        """Test greater than."""
        assert Length.pt(24) > Length.pt(12)

    def test_less_than_or_equal(self) -> None:
        """Test less than or equal."""
        assert Length.pt(12) <= Length.pt(12)
        assert Length.pt(12) <= Length.pt(24)

    def test_greater_than_or_equal(self) -> None:
        """Test greater than or equal."""
        assert Length.pt(12) >= Length.pt(12)
        assert Length.pt(24) >= Length.pt(12)


class TestLengthStringRepresentation:
    """Tests for Length string representation."""

    def test_str_integer(self) -> None:
        """Test string representation with integer value."""
        length = Length.pt(12)
        assert str(length) == "12pt"

    def test_str_decimal(self) -> None:
        """Test string representation with decimal value."""
        length = Length.cm(2.5)
        assert str(length) == "2.5cm"

    def test_repr(self) -> None:
        """Test repr."""
        length = Length.pt(12)
        assert repr(length) == "Length(12.0, 'pt')"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_pt_function(self) -> None:
        """Test pt() convenience function."""
        length = pt(12)
        assert length.value == 12
        assert length.unit == LengthUnit.PT

    def test_cm_function(self) -> None:
        """Test cm() convenience function."""
        length = cm(2.5)
        assert length.value == 2.5
        assert length.unit == LengthUnit.CM

    def test_mm_function(self) -> None:
        """Test mm() convenience function."""
        length = mm(25)
        assert length.value == 25
        assert length.unit == LengthUnit.MM

    def test_inches_function(self) -> None:
        """Test inches() convenience function."""
        length = inches(1)
        assert length.value == 1
        assert length.unit == LengthUnit.IN

    def test_parse_length_function(self) -> None:
        """Test parse_length() convenience function."""
        length = parse_length("12pt")
        assert length.value == 12
        assert length.unit == LengthUnit.PT
