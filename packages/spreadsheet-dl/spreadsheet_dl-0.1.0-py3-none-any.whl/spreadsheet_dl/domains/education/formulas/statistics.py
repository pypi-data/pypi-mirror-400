"""Statistical formulas for education.

Statistical formulas
(STANDARD_DEVIATION, PERCENTILE_RANK, CORRELATION)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class StandardDeviationFormula(BaseFormula):
    """Calculate standard deviation of grades.

        STANDARD_DEVIATION formula for grade statistics

    Calculates standard deviation (sample or population).

    Example:
        >>> formula = StandardDeviationFormula()
        >>> result = formula.build("A1:A30")
        >>> # Returns: "STDEV(A1:A30)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for STANDARD_DEVIATION

            Formula metadata
        """
        return FormulaMetadata(
            name="STANDARD_DEVIATION",
            category="education",
            description="Calculate standard deviation of grades",
            arguments=(
                FormulaArgument(
                    "grades_range",
                    "range",
                    required=True,
                    description="Range of grade values",
                ),
                FormulaArgument(
                    "population",
                    "boolean",
                    required=False,
                    description="Use population SD (True) or sample SD (False)",
                    default=False,
                ),
            ),
            return_type="number",
            examples=(
                "=STANDARD_DEVIATION(B2:B30)",
                "=STANDARD_DEVIATION(grades;TRUE)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build STANDARD_DEVIATION formula string.

        Args:
            *args: grades_range, [population]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            STANDARD_DEVIATION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grades_range = args[0]
        population = args[1] if len(args) > 1 else False

        if population and str(population).upper() in ("TRUE", "1", "YES"):
            return f"of:=STDEVP({grades_range})"
        else:
            return f"of:=STDEV({grades_range})"


@dataclass(slots=True, frozen=True)
class PercentileRankFormula(BaseFormula):
    """Calculate percentile rank of a grade.

        PERCENTILE_RANK formula for grade ranking

    Calculates the percentile rank of a value within a dataset.

    Example:
        >>> formula = PercentileRankFormula()
        >>> result = formula.build("A1", "A1:A30")
        >>> # Returns: "PERCENTRANK(A1:A30;A1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PERCENTILE_RANK

            Formula metadata
        """
        return FormulaMetadata(
            name="PERCENTILE_RANK",
            category="education",
            description="Calculate percentile rank of a grade",
            arguments=(
                FormulaArgument(
                    "grade",
                    "number",
                    required=True,
                    description="Grade value to rank",
                ),
                FormulaArgument(
                    "all_grades",
                    "range",
                    required=True,
                    description="Range of all grades",
                ),
                FormulaArgument(
                    "significance",
                    "number",
                    required=False,
                    description="Number of significant digits",
                    default=3,
                ),
            ),
            return_type="number",
            examples=(
                "=PERCENTILE_RANK(B2;B$2:B$30)",
                "=PERCENTILE_RANK(grade;all_grades;2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PERCENTILE_RANK formula string.

        Args:
            *args: grade, all_grades, [significance]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PERCENTILE_RANK formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grade = args[0]
        all_grades = args[1]
        significance = args[2] if len(args) > 2 else 3

        return f"of:=PERCENTRANK({all_grades};{grade};{significance})"


@dataclass(slots=True, frozen=True)
class CorrelationFormula(BaseFormula):
    """Calculate correlation coefficient between two datasets.

        CORRELATION formula for grade correlation

    Calculates Pearson correlation coefficient.

    Example:
        >>> formula = CorrelationFormula()
        >>> result = formula.build("A1:A30", "B1:B30")
        >>> # Returns: "CORREL(A1:A30;B1:B30)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CORRELATION

            Formula metadata
        """
        return FormulaMetadata(
            name="CORRELATION",
            category="education",
            description="Calculate Pearson correlation coefficient",
            arguments=(
                FormulaArgument(
                    "range1",
                    "range",
                    required=True,
                    description="First data range (e.g., test scores)",
                ),
                FormulaArgument(
                    "range2",
                    "range",
                    required=True,
                    description="Second data range (e.g., homework grades)",
                ),
            ),
            return_type="number",
            examples=(
                "=CORRELATION(B2:B30;C2:C30)",
                "=CORRELATION(test_scores;homework_grades)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CORRELATION formula string.

        Args:
            *args: range1, range2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CORRELATION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        range1 = args[0]
        range2 = args[1]

        return f"of:=CORREL({range1};{range2})"


__all__ = [
    "CorrelationFormula",
    "PercentileRankFormula",
    "StandardDeviationFormula",
]
