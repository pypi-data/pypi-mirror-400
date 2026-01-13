"""Length and measurement value objects for consistent dimension handling.

Provides immutable Length class supporting multiple units with
conversion and arithmetic operations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class LengthUnit(Enum):
    """Supported length units."""

    PT = "pt"  # Points (1/72 inch)
    PX = "px"  # Pixels (screen-dependent)
    EM = "em"  # Relative to font size
    CM = "cm"  # Centimeters
    MM = "mm"  # Millimeters
    IN = "in"  # Inches
    PERCENT = "%"  # Percentage


# Conversion factors to points (base unit)
_TO_POINTS: dict[LengthUnit, float] = {
    LengthUnit.PT: 1.0,
    LengthUnit.PX: 0.75,  # Assume 96 DPI
    LengthUnit.EM: 12.0,  # Assume 12pt base font
    LengthUnit.CM: 28.3465,  # 72/2.54
    LengthUnit.MM: 2.83465,  # 72/25.4
    LengthUnit.IN: 72.0,
    LengthUnit.PERCENT: 0.0,  # Cannot convert percentage
}

# Pattern for parsing length strings
_LENGTH_PATTERN = re.compile(
    r"^(-?\d+(?:\.\d+)?)\s*(pt|px|em|cm|mm|in|%)$", re.IGNORECASE
)


@dataclass(frozen=True)
class Length:
    """Immutable length value with unit.

    Supports creation from numeric values with units, parsing from strings,
    unit conversion, and arithmetic operations.

    Examples:
        # Creation
        width = Length(12, LengthUnit.PT)
        width = Length(12, "pt")
        margin = Length.parse("2.5cm")
        height = Length.pt(36)
        col_width = Length.cm(2.5)

        # Conversion
        points = margin.to_points()  # ~70.87pt
        cm_value = margin.to_cm()

        # Arithmetic
        total = Length.pt(12) + Length.pt(4)  # 16pt
        double = Length.pt(12) * 2  # 24pt

        # String representation
        print(str(margin))  # "2.5cm"
    """

    value: float
    unit: LengthUnit

    def __init__(self, value: float, unit: LengthUnit | str) -> None:
        """Create a Length with value and unit.

        Args:
            value: Numeric value
            unit: LengthUnit or string like "pt", "cm", "in"
        """
        object.__setattr__(self, "value", float(value))

        if isinstance(unit, str):
            unit_lower = unit.lower()
            for lu in LengthUnit:
                if lu.value == unit_lower:
                    object.__setattr__(self, "unit", lu)
                    return
            raise ValueError(f"Unknown unit: {unit}. Valid: pt, px, em, cm, mm, in, %")
        else:
            object.__setattr__(self, "unit", unit)

    @classmethod
    def parse(cls, s: str) -> Length:
        """Parse length from string like "12pt", "2.5cm".

        Args:
            s: Length string

        Returns:
            Length instance

        Raises:
            ValueError: If string cannot be parsed
        """
        s = s.strip()
        match = _LENGTH_PATTERN.match(s)
        if not match:
            raise ValueError(
                f"Invalid length format: '{s}'. Expected format like '12pt', '2.5cm'"
            )
        value = float(match.group(1))
        unit_str = match.group(2).lower()
        return cls(value, unit_str)

    @classmethod
    def pt(cls, value: float) -> Length:
        """Create Length in points."""
        return cls(value, LengthUnit.PT)

    @classmethod
    def px(cls, value: float) -> Length:
        """Create Length in pixels."""
        return cls(value, LengthUnit.PX)

    @classmethod
    def cm(cls, value: float) -> Length:
        """Create Length in centimeters."""
        return cls(value, LengthUnit.CM)

    @classmethod
    def mm(cls, value: float) -> Length:
        """Create Length in millimeters."""
        return cls(value, LengthUnit.MM)

    @classmethod
    def inches(cls, value: float) -> Length:
        """Create Length in inches."""
        return cls(value, LengthUnit.IN)

    @classmethod
    def em(cls, value: float) -> Length:
        """Create Length in em units."""
        return cls(value, LengthUnit.EM)

    @classmethod
    def percent(cls, value: float) -> Length:
        """Create Length as percentage."""
        return cls(value, LengthUnit.PERCENT)

    def to_points(self) -> float:
        """Convert to points.

        Returns:
            Value in points

        Raises:
            ValueError: If unit cannot be converted (percentage)
        """
        if self.unit == LengthUnit.PERCENT:
            raise ValueError("Cannot convert percentage to points without context")
        return self.value * _TO_POINTS[self.unit]

    def to_cm(self) -> float:
        """Convert to centimeters."""
        points = self.to_points()
        return points / _TO_POINTS[LengthUnit.CM]

    def to_mm(self) -> float:
        """Convert to millimeters."""
        points = self.to_points()
        return points / _TO_POINTS[LengthUnit.MM]

    def to_inches(self) -> float:
        """Convert to inches."""
        points = self.to_points()
        return points / _TO_POINTS[LengthUnit.IN]

    def to_px(self) -> float:
        """Convert to pixels (at 96 DPI)."""
        points = self.to_points()
        return points / _TO_POINTS[LengthUnit.PX]

    def to_unit(self, unit: LengthUnit | str) -> Length:
        """Convert to specified unit.

        Args:
            unit: Target unit

        Returns:
            New Length in target unit
        """
        if isinstance(unit, str):
            for lu in LengthUnit:
                if lu.value == unit.lower():
                    unit = lu
                    break
            else:
                raise ValueError(f"Unknown unit: {unit}")

        if unit == self.unit:
            return self

        if self.unit == LengthUnit.PERCENT or unit == LengthUnit.PERCENT:
            raise ValueError("Cannot convert to/from percentage")

        points = self.to_points()
        new_value = points / _TO_POINTS[unit]
        return Length(new_value, unit)

    def __add__(self, other: Length) -> Length:
        """Add two lengths (must be same unit or convertible)."""
        if not isinstance(other, Length):
            return NotImplemented

        if self.unit == other.unit:
            return Length(self.value + other.value, self.unit)

        # Convert to points, add, keep first operand's unit
        total_points = self.to_points() + other.to_points()
        return Length(total_points / _TO_POINTS[self.unit], self.unit)

    def __sub__(self, other: Length) -> Length:
        """Subtract two lengths."""
        if not isinstance(other, Length):
            return NotImplemented

        if self.unit == other.unit:
            return Length(self.value - other.value, self.unit)

        total_points = self.to_points() - other.to_points()
        return Length(total_points / _TO_POINTS[self.unit], self.unit)

    def __mul__(self, factor: float) -> Length:
        """Multiply length by scalar."""
        if not isinstance(factor, (int, float)):
            return NotImplemented
        return Length(self.value * factor, self.unit)

    def __rmul__(self, factor: float) -> Length:
        """Right multiply length by scalar."""
        return self.__mul__(factor)

    def __truediv__(self, factor: float) -> Length:
        """Divide length by scalar."""
        if not isinstance(factor, (int, float)):
            return NotImplemented
        if factor == 0:
            raise ZeroDivisionError("Cannot divide length by zero")
        return Length(self.value / factor, self.unit)

    def __neg__(self) -> Length:
        """Negate length."""
        return Length(-self.value, self.unit)

    def __abs__(self) -> Length:
        """Absolute value of length."""
        return Length(abs(self.value), self.unit)

    def __eq__(self, other: object) -> bool:
        """Compare lengths for equality."""
        if not isinstance(other, Length):
            return NotImplemented

        if self.unit == other.unit:
            return abs(self.value - other.value) < 1e-9

        # Convert to points for comparison
        try:
            return abs(self.to_points() - other.to_points()) < 1e-6
        except ValueError:
            return False

    def __lt__(self, other: Length) -> bool:
        """Compare lengths."""
        if not isinstance(other, Length):
            return NotImplemented

        if self.unit == other.unit:
            return self.value < other.value

        return self.to_points() < other.to_points()

    def __le__(self, other: Length) -> bool:
        """Compare lengths."""
        return self == other or self < other

    def __gt__(self, other: Length) -> bool:
        """Compare lengths."""
        if not isinstance(other, Length):
            return NotImplemented
        return other < self

    def __ge__(self, other: Length) -> bool:
        """Compare lengths."""
        return self == other or self > other

    def __str__(self) -> str:
        """Return string representation like '12pt' or '2.5cm'."""
        if self.value == int(self.value):
            return f"{int(self.value)}{self.unit.value}"
        return f"{self.value}{self.unit.value}"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Length({self.value}, {self.unit.value!r})"


# Convenience functions
def pt(value: float) -> Length:
    """Create Length in points."""
    return Length.pt(value)


def cm(value: float) -> Length:
    """Create Length in centimeters."""
    return Length.cm(value)


def mm(value: float) -> Length:
    """Create Length in millimeters."""
    return Length.mm(value)


def inches(value: float) -> Length:
    """Create Length in inches."""
    return Length.inches(value)


def parse_length(s: str) -> Length:
    """Parse length from string."""
    return Length.parse(s)
