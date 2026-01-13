"""Grade calculation formulas.

Grade calculation formulas
(GRADE_AVERAGE, WEIGHTED_GRADE, GRADE_CURVE)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class GradeAverageFormula(BaseFormula):
    """Calculate simple grade average.

        GRADE_AVERAGE formula for grade calculation

    Calculates the arithmetic mean of a range of grades.

    Example:
        >>> formula = GradeAverageFormula()
        >>> result = formula.build("A1:A10")
        >>> # Returns: "AVERAGE(A1:A10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GRADE_AVERAGE

            Formula metadata
        """
        return FormulaMetadata(
            name="GRADE_AVERAGE",
            category="education",
            description="Calculate simple grade average from a range",
            arguments=(
                FormulaArgument(
                    "grades_range",
                    "range",
                    required=True,
                    description="Range of grade values",
                ),
                FormulaArgument(
                    "exclude_zeros",
                    "boolean",
                    required=False,
                    description="Exclude zero values from average",
                    default=False,
                ),
            ),
            return_type="number",
            examples=(
                "=GRADE_AVERAGE(B2:B30)",
                "=GRADE_AVERAGE(grades;TRUE)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GRADE_AVERAGE formula string.

        Args:
            *args: grades_range, [exclude_zeros]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            GRADE_AVERAGE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grades_range = args[0]
        exclude_zeros = args[1] if len(args) > 1 else False

        if exclude_zeros and str(exclude_zeros).upper() in ("TRUE", "1", "YES"):
            # Use AVERAGEIF to exclude zeros
            return f'of:=AVERAGEIF({grades_range};"<>0")'
        else:
            return f"of:=AVERAGE({grades_range})"


@dataclass(slots=True, frozen=True)
class WeightedGradeFormula(BaseFormula):
    """Calculate weighted grade average.

        WEIGHTED_GRADE formula for weighted calculations

    Calculates weighted average using grades and corresponding weights.

    Example:
        >>> formula = WeightedGradeFormula()
        >>> result = formula.build("A1:A5", "B1:B5")
        >>> # Returns: "SUMPRODUCT(A1:A5;B1:B5)/SUM(B1:B5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WEIGHTED_GRADE

            Formula metadata
        """
        return FormulaMetadata(
            name="WEIGHTED_GRADE",
            category="education",
            description="Calculate weighted grade average",
            arguments=(
                FormulaArgument(
                    "grades_range",
                    "range",
                    required=True,
                    description="Range of grade values",
                ),
                FormulaArgument(
                    "weights_range",
                    "range",
                    required=True,
                    description="Range of weight values (must match grades range)",
                ),
            ),
            return_type="number",
            examples=(
                "=WEIGHTED_GRADE(B2:B10;C2:C10)",
                "=WEIGHTED_GRADE(grades;weights)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WEIGHTED_GRADE formula string.

        Args:
            *args: grades_range, weights_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            WEIGHTED_GRADE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grades_range = args[0]
        weights_range = args[1]

        # Weighted average = SUMPRODUCT(grades, weights) / SUM(weights)
        return f"of:=SUMPRODUCT({grades_range};{weights_range})/SUM({weights_range})"


@dataclass(slots=True, frozen=True)
class GradeCurveFormula(BaseFormula):
    """Apply grade curve adjustment.

        GRADE_CURVE formula for curve adjustments

    Adjusts grades based on various curving methods.

    Example:
        >>> formula = GradeCurveFormula()
        >>> result = formula.build("A1", "A1:A30", "linear", "10")
        >>> # Returns formula for linear curve adjustment
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GRADE_CURVE

            Formula metadata
        """
        return FormulaMetadata(
            name="GRADE_CURVE",
            category="education",
            description="Apply grade curve adjustment",
            arguments=(
                FormulaArgument(
                    "grade",
                    "number",
                    required=True,
                    description="Individual grade to curve",
                ),
                FormulaArgument(
                    "all_grades",
                    "range",
                    required=True,
                    description="Range of all grades for curve calculation",
                ),
                FormulaArgument(
                    "method",
                    "text",
                    required=False,
                    description="Curve method: linear, sqrt, or bell",
                    default="linear",
                ),
                FormulaArgument(
                    "adjustment",
                    "number",
                    required=False,
                    description="Adjustment factor (points to add or percentage)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=GRADE_CURVE(B2;B$2:B$30;linear;10)",
                "=GRADE_CURVE(grade;all_grades;sqrt)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GRADE_CURVE formula string.

        Args:
            *args: grade, all_grades, [method], [adjustment]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            GRADE_CURVE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grade = args[0]
        all_grades = args[1]
        method = str(args[2]).lower() if len(args) > 2 else "linear"
        adjustment = args[3] if len(args) > 3 else 0

        if method == "sqrt":
            # Square root curve: scaled to 100
            return f"of:=SQRT({grade})*10"
        elif method == "bell":
            # Bell curve: normalize to mean=75, sd=10
            return f"of:=75+10*({grade}-AVERAGE({all_grades}))/STDEV({all_grades})"
        else:
            # Linear: add fixed points
            return f"of:=MIN({grade}+{adjustment};100)"


@dataclass(slots=True, frozen=True)
class CurveGradesFormula(BaseFormula):
    """Apply distribution-based grade curve adjustment.

        Curve grades to target mean and standard deviation

    Example:
        >>> formula = CurveGradesFormula()
        >>> result = formula.build("A1", "A1:A30", "75", "10")
        >>> # Returns curved grade for target distribution
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CurveGrades

            Formula metadata
        """
        return FormulaMetadata(
            name="CURVE_GRADES",
            category="education",
            description="Curve grades to target mean and standard deviation",
            arguments=(
                FormulaArgument(
                    "grade",
                    "number",
                    required=True,
                    description="Individual grade to curve",
                ),
                FormulaArgument(
                    "all_grades",
                    "range",
                    required=True,
                    description="Range of all grades",
                ),
                FormulaArgument(
                    "target_mean",
                    "number",
                    required=False,
                    description="Target mean (default 75)",
                    default=75,
                ),
                FormulaArgument(
                    "target_sd",
                    "number",
                    required=False,
                    description="Target standard deviation (default 10)",
                    default=10,
                ),
            ),
            return_type="number",
            examples=(
                "=CURVE_GRADES(A1;A$1:A$30)",
                "=CURVE_GRADES(A1;A$1:A$30;80;12)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CurveGrades formula string.

        Args:
            *args: grade, all_grades, [target_mean], [target_sd]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CurveGrades formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grade = args[0]
        all_grades = args[1]
        target_mean = args[2] if len(args) > 2 else 75
        target_sd = args[3] if len(args) > 3 else 10

        # Curved = target_mean + ((grade - actual_mean) / actual_sd) * target_sd
        return f"of:={target_mean}+(({grade}-AVERAGE({all_grades}))/STDEV({all_grades}))*{target_sd}"


@dataclass(slots=True, frozen=True)
class StandardScoreFormula(BaseFormula):
    """Calculate z-score based standard score.

        Z-score transformation for grading

    Example:
        >>> formula = StandardScoreFormula()
        >>> result = formula.build("85", "75", "10")
        >>> # Returns z-score
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for StandardScore

            Formula metadata
        """
        return FormulaMetadata(
            name="STANDARD_SCORE",
            category="education",
            description="Calculate z-score based standard score",
            arguments=(
                FormulaArgument(
                    "grade",
                    "number",
                    required=True,
                    description="Individual grade",
                ),
                FormulaArgument(
                    "mean",
                    "number",
                    required=True,
                    description="Mean grade",
                ),
                FormulaArgument(
                    "standard_deviation",
                    "number",
                    required=True,
                    description="Standard deviation",
                ),
            ),
            return_type="number",
            examples=(
                "=STANDARD_SCORE(85;75;10)",
                "=STANDARD_SCORE(A1;AVERAGE(A:A);STDEV(A:A))",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build StandardScore formula string.

        Args:
            *args: grade, mean, standard_deviation
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            StandardScore formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grade = args[0]
        mean = args[1]
        sd = args[2]

        # z = (x - mean) / sd
        return f"of:=({grade}-{mean})/{sd}"


@dataclass(slots=True, frozen=True)
class PercentileRankFormula(BaseFormula):
    """Calculate percentile rank in grade distribution.

        Position in distribution as percentile

    Example:
        >>> formula = PercentileRankFormula()
        >>> result = formula.build("A1", "A$1:A$30")
        >>> # Returns percentile rank (0-100)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PercentileRank

            Formula metadata
        """
        return FormulaMetadata(
            name="PERCENTILE_RANK_GRADE",
            category="education",
            description="Calculate percentile rank in grade distribution",
            arguments=(
                FormulaArgument(
                    "grade",
                    "number",
                    required=True,
                    description="Individual grade",
                ),
                FormulaArgument(
                    "all_grades",
                    "range",
                    required=True,
                    description="Range of all grades",
                ),
            ),
            return_type="number",
            examples=(
                "=PERCENTILE_RANK_GRADE(A1;A$1:A$30)",
                "=PERCENTILE_RANK_GRADE(B5;B$2:B$100)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PercentileRank formula string.

        Args:
            *args: grade, all_grades
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PercentileRank formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grade = args[0]
        all_grades = args[1]

        # Percentile = (count below + 0.5*count equal) / total * 100
        return f"of:=PERCENTRANK({all_grades};{grade};3)*100"


@dataclass(slots=True, frozen=True)
class WeightedGPAFormula(BaseFormula):
    """Calculate weighted GPA with course credits.

        GPA with credit hour weighting

    Example:
        >>> formula = WeightedGPAFormula()
        >>> result = formula.build("A1:A5", "B1:B5")
        >>> # Returns weighted GPA
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WeightedGPA

            Formula metadata
        """
        return FormulaMetadata(
            name="WEIGHTED_GPA",
            category="education",
            description="Calculate weighted GPA with course credits",
            arguments=(
                FormulaArgument(
                    "grade_points",
                    "range",
                    required=True,
                    description="Range of grade point values (0-4 scale)",
                ),
                FormulaArgument(
                    "credits",
                    "range",
                    required=True,
                    description="Range of credit hours",
                ),
            ),
            return_type="number",
            examples=(
                "=WEIGHTED_GPA(A1:A5;B1:B5)",
                "=WEIGHTED_GPA(grade_points;credits)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WeightedGPA formula string.

        Args:
            *args: grade_points, credits
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            WeightedGPA formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        grade_points = args[0]
        credits = args[1]

        # GPA = sum(grade_points * credits) / sum(credits)
        return f"of:=SUMPRODUCT({grade_points};{credits})/SUM({credits})"


@dataclass(slots=True, frozen=True)
class PassFailThresholdFormula(BaseFormula):
    """Determine pass/fail based on threshold.

        Binary pass/fail grading

    Returns 1 for pass (score >= threshold) or 0 for fail.

    Example:
        >>> formula = PassFailThresholdFormula()
        >>> result = formula.build("85", "70")
        >>> # Returns: "IF(85>=70;1;0)" which is 1 (pass)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PASS_FAIL_THRESHOLD

            Formula metadata
        """
        return FormulaMetadata(
            name="PASS_FAIL_THRESHOLD",
            category="education",
            description="Binary pass (1) or fail (0) based on threshold",
            arguments=(
                FormulaArgument(
                    "score",
                    "number",
                    required=True,
                    description="Student score",
                ),
                FormulaArgument(
                    "threshold",
                    "number",
                    required=True,
                    description="Passing threshold",
                ),
            ),
            return_type="number",
            examples=(
                "=PASS_FAIL_THRESHOLD(85;70)",
                "=PASS_FAIL_THRESHOLD(A1;60)",
                "=PASS_FAIL_THRESHOLD(B3;C3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PassFailThreshold formula string.

        Args:
            *args: score, threshold
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PassFailThreshold formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        score = args[0]
        threshold = args[1]

        # Pass (1) if score >= threshold, else fail (0)
        return f"of:=IF({score}>={threshold};1;0)"


@dataclass(slots=True, frozen=True)
class RubricScoreFormula(BaseFormula):
    """Calculate criteria-based rubric scoring.

        Aggregate rubric criteria scores

    Example:
        >>> formula = RubricScoreFormula()
        >>> result = formula.build("A1:A4", "B1:B4", "100")
        >>> # Returns total rubric score
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RubricScore

            Formula metadata
        """
        return FormulaMetadata(
            name="RUBRIC_SCORE",
            category="education",
            description="Calculate criteria-based rubric score",
            arguments=(
                FormulaArgument(
                    "criteria_scores",
                    "range",
                    required=True,
                    description="Range of criteria scores",
                ),
                FormulaArgument(
                    "criteria_weights",
                    "range",
                    required=True,
                    description="Range of criteria weights/points",
                ),
                FormulaArgument(
                    "scale",
                    "number",
                    required=False,
                    description="Output scale (default 100)",
                    default=100,
                ),
            ),
            return_type="number",
            examples=(
                "=RUBRIC_SCORE(A1:A4;B1:B4)",
                "=RUBRIC_SCORE(scores;weights;100)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RubricScore formula string.

        Args:
            *args: criteria_scores, criteria_weights, [scale]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RubricScore formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        scores = args[0]
        weights = args[1]
        scale = args[2] if len(args) > 2 else 100

        # Total = sum(scores * weights) / sum(weights) * scale
        return f"of:=SUMPRODUCT({scores};{weights})/SUM({weights})*{scale}"


__all__ = [
    "CurveGradesFormula",
    "GradeAverageFormula",
    "GradeCurveFormula",
    "PassFailThresholdFormula",
    "PercentileRankFormula",
    "RubricScoreFormula",
    "StandardScoreFormula",
    "WeightedGPAFormula",
    "WeightedGradeFormula",
]
