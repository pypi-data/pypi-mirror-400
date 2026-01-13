"""Statistical formulas for data science.

Statistical formulas (TTEST, FTEST, ZTEST, CHISQ_TEST)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class TTestFormula(BaseFormula):
    """T-test for comparing means of two samples.

        TTEST formula for statistical testing

    Example:
        >>> formula = TTestFormula()
        >>> result = formula.build("A1:A10", "B1:B10", 2, 1)
        >>> # Returns: "TTEST(A1:A10;B1:B10;2;1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TTEST

            Formula metadata
        """
        return FormulaMetadata(
            name="TTEST",
            category="statistical",
            description="Performs Student's t-test on two data samples",
            arguments=(
                FormulaArgument(
                    "array1",
                    "range",
                    required=True,
                    description="First data array or range",
                ),
                FormulaArgument(
                    "array2",
                    "range",
                    required=True,
                    description="Second data array or range",
                ),
                FormulaArgument(
                    "tails",
                    "number",
                    required=False,
                    description="Number of tails (1 or 2)",
                    default=2,
                ),
                FormulaArgument(
                    "type",
                    "number",
                    required=False,
                    description="Test type (1=paired, 2=two-sample equal variance, 3=two-sample unequal variance)",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=TTEST(A1:A10;B1:B10;2;1)",
                "=TTEST(range1;range2;1;2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TTEST formula string.

        Args:
            *args: array1, array2, [tails], [type]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TTEST formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        array1 = args[0]
        array2 = args[1]
        tails = args[2] if len(args) > 2 else 2
        type_arg = args[3] if len(args) > 3 else 1

        return f"of:=TTEST({array1};{array2};{tails};{type_arg})"


@dataclass(slots=True, frozen=True)
class FTestFormula(BaseFormula):
    """F-test for comparing variances of two samples.

        FTEST formula for variance comparison

    Example:
        >>> formula = FTestFormula()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns: "FTEST(A1:A10;B1:B10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for FTEST

            Formula metadata
        """
        return FormulaMetadata(
            name="FTEST",
            category="statistical",
            description="Performs F-test to compare variances of two populations",
            arguments=(
                FormulaArgument(
                    "array1",
                    "range",
                    required=True,
                    description="First data array or range",
                ),
                FormulaArgument(
                    "array2",
                    "range",
                    required=True,
                    description="Second data array or range",
                ),
            ),
            return_type="number",
            examples=(
                "=FTEST(A1:A10;B1:B10)",
                "=FTEST(range1;range2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FTEST formula string.

        Args:
            *args: array1, array2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            FTEST formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        array1 = args[0]
        array2 = args[1]

        return f"of:=FTEST({array1};{array2})"


@dataclass(slots=True, frozen=True)
class ZTestFormula(BaseFormula):
    """Z-test for hypothesis testing with known population variance.

        ZTEST formula for hypothesis testing

    Example:
        >>> formula = ZTestFormula()
        >>> result = formula.build("A1:A10", 50)
        >>> # Returns: "ZTEST(A1:A10;50)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ZTEST

            Formula metadata
        """
        return FormulaMetadata(
            name="ZTEST",
            category="statistical",
            description="Performs one-sample z-test",
            arguments=(
                FormulaArgument(
                    "array",
                    "range",
                    required=True,
                    description="Data array or range",
                ),
                FormulaArgument(
                    "x",
                    "number",
                    required=True,
                    description="Hypothesized population mean",
                ),
                FormulaArgument(
                    "sigma",
                    "number",
                    required=False,
                    description="Known population standard deviation",
                    default=None,
                ),
            ),
            return_type="number",
            examples=(
                "=ZTEST(A1:A10;50)",
                "=ZTEST(A1:A10;50;5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ZTEST formula string.

        Args:
            *args: array, x, [sigma]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ZTEST formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        array = args[0]
        x = args[1]
        sigma = args[2] if len(args) > 2 else None

        if sigma is not None:
            return f"of:=ZTEST({array};{x};{sigma})"
        return f"of:=ZTEST({array};{x})"


@dataclass(slots=True, frozen=True)
class ChiSquareTestFormula(BaseFormula):
    """Chi-square test for independence or goodness of fit.

        CHISQ_TEST formula for categorical data analysis

    Example:
        >>> formula = ChiSquareTestFormula()
        >>> result = formula.build("A1:B5", "D1:E5")
        >>> # Returns: "CHITEST(A1:B5;D1:E5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CHISQ_TEST

            Formula metadata
        """
        return FormulaMetadata(
            name="CHISQ_TEST",
            category="statistical",
            description="Performs chi-square test for independence",
            arguments=(
                FormulaArgument(
                    "observed_range",
                    "range",
                    required=True,
                    description="Range of observed frequencies",
                ),
                FormulaArgument(
                    "expected_range",
                    "range",
                    required=True,
                    description="Range of expected frequencies",
                ),
            ),
            return_type="number",
            examples=(
                "=CHITEST(A1:B5;D1:E5)",
                "=CHITEST(observed;expected)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CHISQ_TEST formula string.

        Args:
            *args: observed_range, expected_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (uses CHITEST which is the ODF name)

            CHISQ_TEST formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        observed = args[0]
        expected = args[1]

        # ODF uses CHITEST function name
        return f"of:=CHITEST({observed};{expected})"


__all__ = [
    "ChiSquareTestFormula",
    "FTestFormula",
    "TTestFormula",
    "ZTestFormula",
]
