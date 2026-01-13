"""Risk management formulas.

Risk analysis formulas for portfolio management including VaR, CVaR,
volatility, alpha, tracking error, information ratio, and downside deviation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ValueAtRisk(BaseFormula):
    """Calculate Value at Risk (VaR) for portfolio risk assessment.

        VAR calculation for portfolio risk measurement at specified confidence level

    Example:
        >>> formula = ValueAtRisk()
        >>> result = formula.build("A1:A100", "0.95")
        >>> # Returns: "of:=PERCENTILE(A1:A100;1-0.95)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ValueAtRisk

            Risk formula metadata
        """
        return FormulaMetadata(
            name="VAR",
            category="risk",
            description="Calculate Value at Risk for portfolio risk assessment",
            arguments=(
                FormulaArgument(
                    "returns",
                    "range",
                    required=True,
                    description="Range of portfolio returns",
                ),
                FormulaArgument(
                    "confidence",
                    "number",
                    required=True,
                    description="Confidence level (e.g., 0.95 for 95%)",
                ),
            ),
            return_type="number",
            examples=(
                "=VAR(A1:A100;0.95)",
                "=VAR(B1:B252;0.99)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build VAR formula string.

        Args:
            *args: returns, confidence
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            VAR formula building using PERCENTILE

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        returns = args[0]
        confidence = args[1]

        return f"of:=PERCENTILE({returns};1-{confidence})"


@dataclass(slots=True, frozen=True)
class ConditionalVaR(BaseFormula):
    r"""Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.

        CVaR calculation measuring expected loss beyond VaR threshold

    Example:
        >>> formula = ConditionalVaR()
        >>> result = formula.build("A1:A100", "0.95")
        >>> # Returns: "of:=AVERAGEIF(A1:A100;\"<\"&PERCENTILE(A1:A100;1-0.95);A1:A100)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ConditionalVaR

            Risk formula metadata
        """
        return FormulaMetadata(
            name="CVAR",
            category="risk",
            description="Calculate Conditional VaR (Expected Shortfall)",
            arguments=(
                FormulaArgument(
                    "returns",
                    "range",
                    required=True,
                    description="Range of portfolio returns",
                ),
                FormulaArgument(
                    "confidence",
                    "number",
                    required=True,
                    description="Confidence level (e.g., 0.95 for 95%)",
                ),
            ),
            return_type="number",
            examples=(
                "=CVAR(A1:A100;0.95)",
                "=CVAR(B1:B252;0.99)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CVAR formula string.

        Args:
            *args: returns, confidence
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CVAR formula building using AVERAGEIF and PERCENTILE

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        returns = args[0]
        confidence = args[1]

        return f'of:=AVERAGEIF({returns};"<"&PERCENTILE({returns};1-{confidence});{returns})'


@dataclass(slots=True, frozen=True)
class PortfolioVolatility(BaseFormula):
    """Calculate portfolio volatility (standard deviation of returns).

        Portfolio volatility calculation using standard deviation

    Example:
        >>> formula = PortfolioVolatility()
        >>> result = formula.build("A1:A100")
        >>> # Returns: "of:=STDEV(A1:A100)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PortfolioVolatility

            Risk formula metadata
        """
        return FormulaMetadata(
            name="PORTFOLIO_VOLATILITY",
            category="risk",
            description="Calculate portfolio volatility (standard deviation)",
            arguments=(
                FormulaArgument(
                    "returns",
                    "range",
                    required=True,
                    description="Range of portfolio returns",
                ),
            ),
            return_type="number",
            examples=(
                "=PORTFOLIO_VOLATILITY(A1:A100)",
                "=PORTFOLIO_VOLATILITY(B1:B252)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PORTFOLIO_VOLATILITY formula string.

        Args:
            *args: returns
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Portfolio volatility formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        returns = args[0]

        return f"of:=STDEV({returns})"


@dataclass(slots=True, frozen=True)
class AlphaRatio(BaseFormula):
    """Calculate Jensen's Alpha for risk-adjusted return.

        Alpha ratio calculation measuring excess return vs. expected return

    Example:
        >>> formula = AlphaRatio()
        >>> result = formula.build("A1", "B1", "C1", "D1")
        >>> # Returns: "of:=A1-(B1+(C1*(D1-B1)))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for AlphaRatio

            Risk formula metadata
        """
        return FormulaMetadata(
            name="ALPHA_RATIO",
            category="risk",
            description="Calculate Jensen's Alpha for risk-adjusted return",
            arguments=(
                FormulaArgument(
                    "portfolio_return",
                    "number",
                    required=True,
                    description="Portfolio return",
                ),
                FormulaArgument(
                    "risk_free_rate",
                    "number",
                    required=True,
                    description="Risk-free rate",
                ),
                FormulaArgument(
                    "beta",
                    "number",
                    required=True,
                    description="Portfolio beta",
                ),
                FormulaArgument(
                    "market_return",
                    "number",
                    required=True,
                    description="Market return",
                ),
            ),
            return_type="number",
            examples=(
                "=ALPHA_RATIO(0.12;0.03;1.2;0.10)",
                "=ALPHA_RATIO(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ALPHA_RATIO formula string.

        Args:
            *args: portfolio_return, risk_free_rate, beta, market_return
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Alpha ratio formula: portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate))

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        portfolio_return = args[0]
        risk_free_rate = args[1]
        beta = args[2]
        market_return = args[3]

        return f"of:={portfolio_return}-({risk_free_rate}+({beta}*({market_return}-{risk_free_rate})))"


@dataclass(slots=True, frozen=True)
class TrackingError(BaseFormula):
    """Calculate tracking error (active risk measure).

        Tracking error calculation measuring portfolio deviation from benchmark

    Example:
        >>> formula = TrackingError()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns: "of:=STDEV(A1:A100-B1:B100)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TrackingError

            Risk formula metadata
        """
        return FormulaMetadata(
            name="TRACKING_ERROR",
            category="risk",
            description="Calculate tracking error (active risk measure)",
            arguments=(
                FormulaArgument(
                    "portfolio_returns",
                    "range",
                    required=True,
                    description="Range of portfolio returns",
                ),
                FormulaArgument(
                    "benchmark_returns",
                    "range",
                    required=True,
                    description="Range of benchmark returns",
                ),
            ),
            return_type="number",
            examples=(
                "=TRACKING_ERROR(A1:A100;B1:B100)",
                "=TRACKING_ERROR(C1:C252;D1:D252)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TRACKING_ERROR formula string.

        Args:
            *args: portfolio_returns, benchmark_returns
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Tracking error formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        portfolio_returns = args[0]
        benchmark_returns = args[1]

        return f"of:=STDEV({portfolio_returns}-{benchmark_returns})"


@dataclass(slots=True, frozen=True)
class InformationRatio(BaseFormula):
    """Calculate Information Ratio (risk-adjusted active return).

        Information ratio calculation measuring excess return per unit of tracking error

    Example:
        >>> formula = InformationRatio()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns: "of:=(AVERAGE(A1:A100)-AVERAGE(B1:B100))/STDEV(A1:A100-B1:B100)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for InformationRatio

            Risk formula metadata
        """
        return FormulaMetadata(
            name="INFORMATION_RATIO",
            category="risk",
            description="Calculate Information Ratio (risk-adjusted active return)",
            arguments=(
                FormulaArgument(
                    "portfolio_returns",
                    "range",
                    required=True,
                    description="Range of portfolio returns",
                ),
                FormulaArgument(
                    "benchmark_returns",
                    "range",
                    required=True,
                    description="Range of benchmark returns",
                ),
            ),
            return_type="number",
            examples=(
                "=INFORMATION_RATIO(A1:A100;B1:B100)",
                "=INFORMATION_RATIO(C1:C252;D1:D252)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build INFORMATION_RATIO formula string.

        Args:
            *args: portfolio_returns, benchmark_returns
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Information ratio formula: (average excess return) / tracking error

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        portfolio_returns = args[0]
        benchmark_returns = args[1]

        return f"of:=(AVERAGE({portfolio_returns})-AVERAGE({benchmark_returns}))/STDEV({portfolio_returns}-{benchmark_returns})"


@dataclass(slots=True, frozen=True)
class DownsideDeviation(BaseFormula):
    r"""Calculate downside deviation (downside risk measure).

        Downside deviation calculation focusing on negative returns only

    Example:
        >>> formula = DownsideDeviation()
        >>> result = formula.build("A1:A100", "0")
        >>> # Returns: "of:=SQRT(SUMPRODUCT((A1:A100<0)*(A1:A100-0)^2)/COUNTIF(A1:A100;\"<0\"))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DownsideDeviation

            Risk formula metadata
        """
        return FormulaMetadata(
            name="DOWNSIDE_DEVIATION",
            category="risk",
            description="Calculate downside deviation (downside risk measure)",
            arguments=(
                FormulaArgument(
                    "returns",
                    "range",
                    required=True,
                    description="Range of portfolio returns",
                ),
                FormulaArgument(
                    "target",
                    "number",
                    required=False,
                    description="Target return (default 0)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=DOWNSIDE_DEVIATION(A1:A100;0)",
                "=DOWNSIDE_DEVIATION(B1:B252;0.02)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DOWNSIDE_DEVIATION formula string.

        Args:
            *args: returns, [target]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Downside deviation formula using SUMPRODUCT

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        returns = args[0]
        target = args[1] if len(args) > 1 else 0

        return f'of:=SQRT(SUMPRODUCT(({returns}<{target})*({returns}-{target})^2)/COUNTIF({returns};"<{target}"))'
