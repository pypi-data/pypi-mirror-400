"""Feature engineering and transformation formulas.

Feature engineering formulas for data preprocessing
(Min-Max Normalize, Z-Score Standardize, Log Transform)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class MinMaxNormalize(BaseFormula):
    """Normalize data using min-max scaling.

        Min-max normalization formula (scales to 0-1 range)

    Example:
        >>> formula = MinMaxNormalize()
        >>> result = formula.build("A1", "A1:A100")
        >>> # Returns: "of:=(A1-MIN(A1:A100))/(MAX(A1:A100)-MIN(A1:A100))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MinMaxNormalize

            Formula metadata for min-max normalization
        """
        return FormulaMetadata(
            name="MIN_MAX_NORMALIZE",
            category="feature_engineering",
            description="Normalize value to 0-1 range using min-max scaling",
            arguments=(
                FormulaArgument(
                    "value",
                    "number",
                    required=True,
                    description="Value to normalize (cell reference)",
                ),
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range to calculate min/max from",
                ),
                FormulaArgument(
                    "new_min",
                    "number",
                    required=False,
                    description="New minimum value (default: 0)",
                ),
                FormulaArgument(
                    "new_max",
                    "number",
                    required=False,
                    description="New maximum value (default: 1)",
                ),
            ),
            return_type="number",
            examples=(
                "=MIN_MAX_NORMALIZE(A1;A1:A100)",
                "=MIN_MAX_NORMALIZE(B5;B1:B100;-1;1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MinMaxNormalize formula string.

        Args:
            *args: value, data_range, new_min (optional), new_max (optional)
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Min-max normalization formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        value = args[0]
        data_range = args[1]
        new_min = args[2] if len(args) > 2 else 0
        new_max = args[3] if len(args) > 3 else 1

        # Min-Max normalization: (x - min) / (max - min) * (new_max - new_min) + new_min
        normalized = (
            f"({value}-MIN({data_range}))/(MAX({data_range})-MIN({data_range}))"
        )

        if new_min == 0 and new_max == 1:
            return f"of:={normalized}"
        else:
            return f"of:={normalized}*({new_max}-{new_min})+{new_min}"


@dataclass(slots=True, frozen=True)
class ZScoreStandardize(BaseFormula):
    """Standardize data using z-score normalization.

        Z-score standardization formula (mean=0, std=1)

    Example:
        >>> formula = ZScoreStandardize()
        >>> result = formula.build("A1", "A1:A100")
        >>> # Returns: "of:=(A1-AVERAGE(A1:A100))/STDEV(A1:A100)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ZScoreStandardize

            Formula metadata for z-score standardization
        """
        return FormulaMetadata(
            name="Z_SCORE_STANDARDIZE",
            category="feature_engineering",
            description="Standardize value using z-score (mean=0, std=1)",
            arguments=(
                FormulaArgument(
                    "value",
                    "number",
                    required=True,
                    description="Value to standardize (cell reference)",
                ),
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range to calculate mean/std from",
                ),
            ),
            return_type="number",
            examples=(
                "=Z_SCORE_STANDARDIZE(A1;A1:A100)",
                "=Z_SCORE_STANDARDIZE(B5;B1:B100)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ZScoreStandardize formula string.

        Args:
            *args: value, data_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Z-score standardization formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        value = args[0]
        data_range = args[1]

        # Z-score: (x - mean) / std
        return f"of:=({value}-AVERAGE({data_range}))/STDEV({data_range})"


@dataclass(slots=True, frozen=True)
class LogTransform(BaseFormula):
    """Apply logarithmic transformation to data.

        Log transformation formula for skewed data

    Example:
        >>> formula = LogTransform()
        >>> result = formula.build("A1")
        >>> # Returns: "of:=LN(A1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LogTransform

            Formula metadata for log transformation
        """
        return FormulaMetadata(
            name="LOG_TRANSFORM",
            category="feature_engineering",
            description="Apply logarithmic transformation to reduce skewness",
            arguments=(
                FormulaArgument(
                    "value",
                    "number",
                    required=True,
                    description="Value to transform (cell reference)",
                ),
                FormulaArgument(
                    "base",
                    "text",
                    required=False,
                    description="Log base: 'e' (natural), '10', or '2' (default: 'e')",
                ),
                FormulaArgument(
                    "offset",
                    "number",
                    required=False,
                    description="Offset to add before log (default: 0)",
                ),
            ),
            return_type="number",
            examples=(
                "=LOG_TRANSFORM(A1)",
                '=LOG_TRANSFORM(B5;"10")',
                '=LOG_TRANSFORM(C3;"e";1)',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LogTransform formula string.

        Args:
            *args: value, base (optional), offset (optional)
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Log transformation formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        value = args[0]
        base = args[1] if len(args) > 1 else "e"
        offset = args[2] if len(args) > 2 else 0

        # Determine log function based on base
        base_str = str(base).strip('"').lower()

        # Apply offset if specified
        value_expr = f"({value}+{offset})" if offset != 0 else str(value)

        # Map base to log function
        log_functions = {
            "e": f"of:=LN({value_expr})",
            "10": f"of:=LOG10({value_expr})",
            "2": f"of:=LOG({value_expr};2)",
        }

        return log_functions.get(base_str, f"of:=LOG({value_expr};{base})")


__all__ = [
    "LogTransform",
    "MinMaxNormalize",
    "ZScoreStandardize",
]
