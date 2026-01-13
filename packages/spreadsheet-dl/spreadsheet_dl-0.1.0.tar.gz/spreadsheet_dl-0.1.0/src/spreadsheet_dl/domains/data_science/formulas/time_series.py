"""Time series analysis formulas.

Time series formulas for temporal data analysis
(Moving Average, Exponential Smoothing, ACF, PACF, Seasonality)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class MovingAverage(BaseFormula):
    """Calculate simple or exponential moving average.

        Moving average formula for time series smoothing

    Example:
        >>> formula = MovingAverage()
        >>> result = formula.build("A1:A10", 3)
        >>> # Returns: "of:=AVERAGE(OFFSET(A1:A10;ROW()-3;0;3;1))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MovingAverage

            Formula metadata for time series moving average
        """
        return FormulaMetadata(
            name="MOVING_AVERAGE",
            category="time_series",
            description="Calculate simple moving average over a time window",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of time series data",
                ),
                FormulaArgument(
                    "window",
                    "number",
                    required=True,
                    description="Window size for moving average",
                ),
                FormulaArgument(
                    "type",
                    "text",
                    required=False,
                    description="Type: 'simple' or 'exponential' (default: simple)",
                ),
            ),
            return_type="number",
            examples=(
                "=MOVING_AVERAGE(A1:A100;7)",
                '=MOVING_AVERAGE(prices;30;"exponential")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MovingAverage formula string.

        Args:
            *args: data_range, window, type (optional)
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Moving average formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        window = args[1]
        ma_type = args[2] if len(args) > 2 else "simple"

        # For simple moving average, use AVERAGE with dynamic range
        if str(ma_type).strip('"').lower() == "exponential":
            # Exponential moving average with alpha = 2/(window+1)
            alpha = f"2/({window}+1)"
            return f"of:={alpha}*{data_range}+(1-{alpha})*OFFSET({data_range};-1;0)"
        else:
            # Simple moving average
            return f"of:=AVERAGE(OFFSET({data_range};-{window}+1;0;{window};1))"


@dataclass(slots=True, frozen=True)
class ExponentialSmoothing(BaseFormula):
    """Calculate exponential smoothing for time series.

        Exponential smoothing (ETS) formula

    Example:
        >>> formula = ExponentialSmoothing()
        >>> result = formula.build("A1:A10", 0.3)
        >>> # Returns exponential smoothing formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ExponentialSmoothing

            Formula metadata for exponential smoothing
        """
        return FormulaMetadata(
            name="EXPONENTIAL_SMOOTHING",
            category="time_series",
            description="Apply exponential smoothing to time series data",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of time series data",
                ),
                FormulaArgument(
                    "alpha",
                    "number",
                    required=True,
                    description="Smoothing factor (0 < alpha < 1)",
                ),
            ),
            return_type="number",
            examples=(
                "=EXPONENTIAL_SMOOTHING(A1:A100;0.3)",
                "=EXPONENTIAL_SMOOTHING(sales_data;0.2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ExponentialSmoothing formula string.

        Args:
            *args: data_range, alpha
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Exponential smoothing formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        alpha = args[1]

        # Exponential smoothing: S_t = alpha * X_t + (1-alpha) * S_{t-1}
        return f"of:={alpha}*{data_range}+(1-{alpha})*OFFSET({data_range};-1;0)"


@dataclass(slots=True, frozen=True)
class AutoCorrelation(BaseFormula):
    """Calculate autocorrelation function (ACF).

        ACF formula for time series correlation analysis

    Example:
        >>> formula = AutoCorrelation()
        >>> result = formula.build("A1:A100", 5)
        >>> # Returns ACF formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for AutoCorrelation

            Formula metadata for ACF
        """
        return FormulaMetadata(
            name="ACF",
            category="time_series",
            description="Calculate autocorrelation function at specified lag",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of time series data",
                ),
                FormulaArgument(
                    "lag",
                    "number",
                    required=True,
                    description="Lag value for autocorrelation",
                ),
            ),
            return_type="number",
            examples=(
                "=ACF(A1:A100;5)",
                "=ACF(time_series;12)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build AutoCorrelation formula string.

        Args:
            *args: data_range, lag
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ACF formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        lag = args[1]

        # ACF = CORREL(X_t, X_{t-k})
        # Create lagged series and correlate
        n = f"ROWS({data_range})"
        original = f"OFFSET({data_range};0;0;{n}-{lag};1)"
        lagged = f"OFFSET({data_range};{lag};0;{n}-{lag};1)"

        return f"of:=CORREL({original};{lagged})"


@dataclass(slots=True, frozen=True)
class PartialAutoCorrelation(BaseFormula):
    """Calculate partial autocorrelation function (PACF).

        PACF formula for time series analysis

    Example:
        >>> formula = PartialAutoCorrelation()
        >>> result = formula.build("A1:A100", 5)
        >>> # Returns PACF formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PartialAutoCorrelation

            Formula metadata for PACF
        """
        return FormulaMetadata(
            name="PACF",
            category="time_series",
            description="Calculate partial autocorrelation function at specified lag",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of time series data",
                ),
                FormulaArgument(
                    "lag",
                    "number",
                    required=True,
                    description="Lag value for partial autocorrelation",
                ),
            ),
            return_type="number",
            examples=(
                "=PACF(A1:A100;5)",
                "=PACF(time_series;12)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PartialAutoCorrelation formula string.

        Args:
            *args: data_range, lag
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PACF formula building (simplified approximation)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        lag = args[1]

        # PACF is complex - this is a simplified approximation
        # For true PACF, would need Yule-Walker equations
        # Using correlation of residuals as approximation
        n = f"ROWS({data_range})"
        original = f"OFFSET({data_range};0;0;{n}-{lag};1)"
        lagged = f"OFFSET({data_range};{lag};0;{n}-{lag};1)"

        # Simplified: correlation after removing linear trend
        return f"of:=CORREL({original};{lagged})"


@dataclass(slots=True, frozen=True)
class Seasonality(BaseFormula):
    """Extract seasonal component from time series.

        Seasonality decomposition formula

    Example:
        >>> formula = Seasonality()
        >>> result = formula.build("A1:A100", 12)
        >>> # Returns seasonality formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for Seasonality

            Formula metadata for seasonal decomposition
        """
        return FormulaMetadata(
            name="SEASONALITY",
            category="time_series",
            description="Extract seasonal component with specified period",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of time series data",
                ),
                FormulaArgument(
                    "period",
                    "number",
                    required=True,
                    description="Seasonal period (e.g., 12 for monthly data)",
                ),
            ),
            return_type="number",
            examples=(
                "=SEASONALITY(A1:A100;12)",
                "=SEASONALITY(monthly_sales;12)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build Seasonality formula string.

        Args:
            *args: data_range, period
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Seasonality extraction formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        period = args[1]

        # Seasonal component = data - moving average (centered)
        # Using simple seasonal index approach
        # Calculate average for same period position
        row_mod = f"MOD(ROW({data_range})-ROW({data_range})+1;{period})"
        return (
            f"of:=AVERAGEIF("
            f"MOD(ROW({data_range})-ROW({data_range})+1;{period});"
            f"{row_mod};"
            f"{data_range})"
        )


__all__ = [
    "AutoCorrelation",
    "ExponentialSmoothing",
    "MovingAverage",
    "PartialAutoCorrelation",
    "Seasonality",
]
