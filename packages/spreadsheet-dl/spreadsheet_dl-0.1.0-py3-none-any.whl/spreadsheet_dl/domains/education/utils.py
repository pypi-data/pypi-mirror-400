"""Education domain utility functions.

    Education domain utilities

Provides helper functions for grade calculations, GPA conversions,
and other educational computations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Grade point mappings (standard 4.0 scale)
GRADE_POINTS = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0,
}

# Letter grade thresholds (percentage)
GRADE_THRESHOLDS = {
    "A+": 97,
    "A": 93,
    "A-": 90,
    "B+": 87,
    "B": 83,
    "B-": 80,
    "C+": 77,
    "C": 73,
    "C-": 70,
    "D+": 67,
    "D": 63,
    "D-": 60,
    "F": 0,
}


def calculate_grade_average(grades: Sequence[float | int | None]) -> float | None:
    """Calculate simple average of grades.

    Args:
        grades: Sequence of grade values (None values are excluded)

    Returns:
        Average grade or None if no valid grades

        Grade average calculation

    Example:
        >>> calculate_grade_average([85, 90, 88, None, 92])
        88.75
    """
    valid_grades = [g for g in grades if g is not None]
    if not valid_grades:
        return None
    return sum(valid_grades) / len(valid_grades)


def calculate_weighted_grade(
    grades: Sequence[float | int],
    weights: Sequence[float | int],
) -> float:
    """Calculate weighted average of grades.

    Args:
        grades: Sequence of grade values
        weights: Sequence of weights (must match grades length)

    Returns:
        Weighted average grade

        Weighted grade calculation

    Example:
        >>> calculate_weighted_grade([85, 90, 95], [0.3, 0.3, 0.4])
        90.5
    """
    if len(grades) != len(weights):
        msg = "Grades and weights must have same length"
        raise ValueError(msg)

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(g * w for g, w in zip(grades, weights, strict=True))
    return weighted_sum / total_weight


def calculate_letter_grade(
    percentage: float,
    thresholds: dict[str, int] | None = None,
) -> str:
    """Convert percentage to letter grade.

    Args:
        percentage: Grade percentage (0-100)
        thresholds: Optional custom thresholds (defaults to standard)

    Returns:
        Letter grade (A+, A, A-, etc.)

        Letter grade conversion

    Example:
        >>> calculate_letter_grade(92)
        'A-'
        >>> calculate_letter_grade(85)
        'B'
    """
    thresholds = thresholds or GRADE_THRESHOLDS

    for grade, threshold in sorted(thresholds.items(), key=lambda x: -x[1]):
        if percentage >= threshold:
            return grade

    return "F"


def grade_to_points(grade: str) -> float:
    """Convert letter grade to grade points.

    Args:
        grade: Letter grade (A, B+, etc.)

    Returns:
        Grade points (0.0-4.0)

        Grade to points conversion

    Example:
        >>> grade_to_points("B+")
        3.3
    """
    return GRADE_POINTS.get(grade.upper(), 0.0)


def points_to_grade(points: float) -> str:
    """Convert grade points to letter grade.

    Args:
        points: Grade points (0.0-4.0)

    Returns:
        Letter grade

        Points to grade conversion

    Example:
        >>> points_to_grade(3.5)
        'B+'
    """
    # Reverse lookup with tolerance
    for grade, pts in sorted(GRADE_POINTS.items(), key=lambda x: -x[1]):
        if points >= pts - 0.15:  # Tolerance for rounding
            return grade
    return "F"


def calculate_gpa(
    grades: Sequence[str],
    credits: Sequence[float | int] | None = None,
) -> float:
    """Calculate GPA from letter grades.

    Args:
        grades: Sequence of letter grades
        credits: Optional credit hours per course (equal weight if None)

    Returns:
        GPA on 4.0 scale

        GPA calculation

    Example:
        >>> calculate_gpa(["A", "B+", "B", "A-"])
        3.5
        >>> calculate_gpa(["A", "B"], [4, 3])
        3.57...
    """
    if not grades:
        return 0.0

    points = [grade_to_points(g) for g in grades]

    if credits is None:
        # Equal weight
        return sum(points) / len(points)
    else:
        if len(credits) != len(grades):
            msg = "Grades and credits must have same length"
            raise ValueError(msg)

        total_credits = sum(credits)
        if total_credits == 0:
            return 0.0

        weighted_sum = sum(p * c for p, c in zip(points, credits, strict=True))
        return weighted_sum / total_credits


def calculate_attendance_rate(
    days_present: int,
    total_days: int,
) -> float:
    """Calculate attendance rate percentage.

    Args:
        days_present: Number of days attended
        total_days: Total number of school days

    Returns:
        Attendance percentage (0-100)

        Attendance rate calculation

    Example:
        >>> calculate_attendance_rate(85, 90)
        94.44...
    """
    if total_days == 0:
        return 0.0
    return (days_present / total_days) * 100


def format_percentage(
    value: float,
    decimals: int = 1,
    include_symbol: bool = True,
) -> str:
    """Format a value as a percentage string.

    Args:
        value: Percentage value (0-100)
        decimals: Number of decimal places
        include_symbol: Whether to include % symbol

    Returns:
        Formatted percentage string

        Percentage formatting

    Example:
        >>> format_percentage(85.678, 1)
        '85.7%'
    """
    formatted = f"{value:.{decimals}f}"
    if include_symbol:
        return f"{formatted}%"
    return formatted


__all__ = [
    "calculate_attendance_rate",
    "calculate_gpa",
    "calculate_grade_average",
    "calculate_letter_grade",
    "calculate_weighted_grade",
    "format_percentage",
    "grade_to_points",
    "points_to_grade",
]
