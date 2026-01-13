"""Regression analysis and error metrics formulas.

Data science formulas for regression model evaluation
(MSE, RMSE, R², MAE, MAPE)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class MeanSquaredError(BaseFormula):
    """Calculate mean squared error for regression models.

        MSE formula for regression error measurement

    Example:
        >>> formula = MeanSquaredError()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns: "of:=SUMPRODUCT((A1:A10-B1:B10)^2)/COUNT(A1:A10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MSE

            Formula metadata
        """
        return FormulaMetadata(
            name="MSE",
            category="regression",
            description="Calculate mean squared error",
            arguments=(
                FormulaArgument(
                    "actual",
                    "range",
                    required=True,
                    description="Range of actual values",
                ),
                FormulaArgument(
                    "predicted",
                    "range",
                    required=True,
                    description="Range of predicted values",
                ),
            ),
            return_type="number",
            examples=(
                "=MSE(A1:A10;B1:B10)",
                "=MSE(actual_range;predicted_range)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MSE formula string.

        Args:
            *args: actual, predicted
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MSE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual = args[0]
        predicted = args[1]

        # MSE = SUM((actual - predicted)^2) / n
        return f"of:=SUMPRODUCT(({actual}-{predicted})^2)/COUNT({actual})"


@dataclass(slots=True, frozen=True)
class RootMeanSquaredError(BaseFormula):
    """Calculate root mean squared error for regression models.

        RMSE formula (square root of MSE)

    Example:
        >>> formula = RootMeanSquaredError()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns: "of:=SQRT(SUMPRODUCT((A1:A10-B1:B10)^2)/COUNT(A1:A10))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RMSE

            Formula metadata
        """
        return FormulaMetadata(
            name="RMSE",
            category="regression",
            description="Calculate root mean squared error",
            arguments=(
                FormulaArgument(
                    "actual",
                    "range",
                    required=True,
                    description="Range of actual values",
                ),
                FormulaArgument(
                    "predicted",
                    "range",
                    required=True,
                    description="Range of predicted values",
                ),
            ),
            return_type="number",
            examples=(
                "=RMSE(A1:A10;B1:B10)",
                "=RMSE(actual_range;predicted_range)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RMSE formula string.

        Args:
            *args: actual, predicted
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RMSE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual = args[0]
        predicted = args[1]

        # RMSE = SQRT(MSE)
        return f"of:=SQRT(SUMPRODUCT(({actual}-{predicted})^2)/COUNT({actual}))"


@dataclass(slots=True, frozen=True)
class RSquared(BaseFormula):
    """Calculate coefficient of determination (R²).

        R² formula for model goodness of fit

    Example:
        >>> formula = RSquared()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns complex R² formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for R²

            Formula metadata
        """
        return FormulaMetadata(
            name="R_SQUARED",
            category="regression",
            description="Calculate coefficient of determination (R²)",
            arguments=(
                FormulaArgument(
                    "actual",
                    "range",
                    required=True,
                    description="Range of actual values",
                ),
                FormulaArgument(
                    "predicted",
                    "range",
                    required=True,
                    description="Range of predicted values",
                ),
            ),
            return_type="number",
            examples=(
                "=R_SQUARED(A1:A10;B1:B10)",
                "=R_SQUARED(actual_range;predicted_range)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build R² formula string.

        Args:
            *args: actual, predicted
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            R² formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual = args[0]
        predicted = args[1]

        # R² = 1 - (SS_res / SS_tot)
        # SS_res = SUM((actual - predicted)^2)
        # SS_tot = SUM((actual - mean(actual))^2)
        return (
            f"of:=1-(SUMPRODUCT(({actual}-{predicted})^2)/"
            f"SUMPRODUCT(({actual}-AVERAGE({actual}))^2))"
        )


@dataclass(slots=True, frozen=True)
class MeanAbsoluteError(BaseFormula):
    """Calculate mean absolute error for regression models.

        MAE formula for regression error measurement

    Example:
        >>> formula = MeanAbsoluteError()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns: "of:=SUMPRODUCT(ABS(A1:A10-B1:B10))/COUNT(A1:A10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MAE

            Formula metadata
        """
        return FormulaMetadata(
            name="MAE",
            category="regression",
            description="Calculate mean absolute error",
            arguments=(
                FormulaArgument(
                    "actual",
                    "range",
                    required=True,
                    description="Range of actual values",
                ),
                FormulaArgument(
                    "predicted",
                    "range",
                    required=True,
                    description="Range of predicted values",
                ),
            ),
            return_type="number",
            examples=(
                "=MAE(A1:A10;B1:B10)",
                "=MAE(actual_range;predicted_range)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MAE formula string.

        Args:
            *args: actual, predicted
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MAE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual = args[0]
        predicted = args[1]

        # MAE = SUM(ABS(actual - predicted)) / n
        return f"of:=SUMPRODUCT(ABS({actual}-{predicted}))/COUNT({actual})"


@dataclass(slots=True, frozen=True)
class MeanAbsolutePercentageError(BaseFormula):
    """Calculate mean absolute percentage error for regression models.

        MAPE formula for regression error measurement in percentage

    Example:
        >>> formula = MeanAbsolutePercentageError()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns MAPE formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MAPE

            Formula metadata
        """
        return FormulaMetadata(
            name="MAPE",
            category="regression",
            description="Calculate mean absolute percentage error",
            arguments=(
                FormulaArgument(
                    "actual",
                    "range",
                    required=True,
                    description="Range of actual values",
                ),
                FormulaArgument(
                    "predicted",
                    "range",
                    required=True,
                    description="Range of predicted values",
                ),
            ),
            return_type="number",
            examples=(
                "=MAPE(A1:A10;B1:B10)",
                "=MAPE(actual_range;predicted_range)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MAPE formula string.

        Args:
            *args: actual, predicted
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            MAPE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual = args[0]
        predicted = args[1]

        # MAPE = (100/n) * SUM(ABS((actual - predicted) / actual))
        return (
            f"of:=(100/COUNT({actual}))*"
            f"SUMPRODUCT(ABS(({actual}-{predicted})/{actual}))"
        )
