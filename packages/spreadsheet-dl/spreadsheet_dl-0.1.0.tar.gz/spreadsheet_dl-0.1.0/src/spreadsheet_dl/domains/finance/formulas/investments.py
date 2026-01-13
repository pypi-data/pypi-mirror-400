"""Investment analysis formulas.

Financial formulas for investment returns and risk analysis
(ROI, CAGR, CompoundInterest, SharpeRatio, PortfolioBeta)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ReturnOnInvestment(BaseFormula):
    """Calculate return on investment percentage.

        ROI formula for investment performance measurement

    Example:
        >>> formula = ReturnOnInvestment()
        >>> result = formula.build("150000", "100000")
        >>> # Returns: "(150000-100000)/100000*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ROI

            Formula metadata
        """
        return FormulaMetadata(
            name="ROI",
            category="investments",
            description="Calculate return on investment percentage",
            arguments=(
                FormulaArgument(
                    "current_value",
                    "number",
                    required=True,
                    description="Current investment value",
                ),
                FormulaArgument(
                    "initial_value",
                    "number",
                    required=True,
                    description="Initial investment amount",
                ),
            ),
            return_type="number",
            examples=(
                "=ROI(150000;100000)",
                "=ROI(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ROI formula string.

        Args:
            *args: current_value, initial_value
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ROI formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        current_value = args[0]
        initial_value = args[1]

        # ROI = (Current Value - Initial Value) / Initial Value * 100
        return f"of:=({current_value}-{initial_value})/{initial_value}*100"


@dataclass(slots=True, frozen=True)
class CompoundAnnualGrowthRate(BaseFormula):
    """Calculate compound annual growth rate.

        CAGR formula for annualized investment return

    Example:
        >>> formula = CompoundAnnualGrowthRate()
        >>> result = formula.build("150000", "100000", "5")
        >>> # Returns: "(POWER(150000/100000;1/5)-1)*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CAGR

            Formula metadata
        """
        return FormulaMetadata(
            name="CAGR",
            category="investments",
            description="Calculate compound annual growth rate",
            arguments=(
                FormulaArgument(
                    "ending_value",
                    "number",
                    required=True,
                    description="Ending investment value",
                ),
                FormulaArgument(
                    "beginning_value",
                    "number",
                    required=True,
                    description="Beginning investment value",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Number of years",
                ),
            ),
            return_type="number",
            examples=(
                "=CAGR(150000;100000;5)",
                "=CAGR(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CAGR formula string.

        Args:
            *args: ending_value, beginning_value, years
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CAGR formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        ending_value = args[0]
        beginning_value = args[1]
        years = args[2]

        # CAGR = (Ending Value / Beginning Value)^(1 / Years) - 1
        return f"of:=(POWER({ending_value}/{beginning_value};1/{years})-1)*100"


@dataclass(slots=True, frozen=True)
class CompoundInterest(BaseFormula):
    """Calculate compound interest.

        Compound interest formula for investment growth

    Example:
        >>> formula = CompoundInterest()
        >>> result = formula.build("10000", "0.05", "12", "10")
        >>> # Returns: "10000*POWER(1+0.05/12;12*10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CompoundInterest

            Formula metadata
        """
        return FormulaMetadata(
            name="COMPOUND_INTEREST",
            category="investments",
            description="Calculate compound interest",
            arguments=(
                FormulaArgument(
                    "principal",
                    "number",
                    required=True,
                    description="Initial principal amount",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Annual interest rate (as decimal)",
                ),
                FormulaArgument(
                    "compounds_per_year",
                    "number",
                    required=True,
                    description="Number of compounding periods per year",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Number of years",
                ),
            ),
            return_type="number",
            examples=(
                "=COMPOUND_INTEREST(10000;0.05;12;10)",
                "=COMPOUND_INTEREST(A1;A2;A3;A4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CompoundInterest formula string.

        Args:
            *args: principal, rate, compounds_per_year, years
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CompoundInterest formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        principal = args[0]
        rate = args[1]
        compounds_per_year = args[2]
        years = args[3]

        # A = P(1 + r/n)^(nt)
        return (
            f"of:={principal}*POWER(1+{rate}/{compounds_per_year};"
            f"{compounds_per_year}*{years})"
        )


@dataclass(slots=True, frozen=True)
class SharpeRatio(BaseFormula):
    """Calculate Sharpe ratio (risk-adjusted return).

        Sharpe ratio formula for investment risk analysis

    Example:
        >>> formula = SharpeRatio()
        >>> result = formula.build("0.12", "0.02", "0.15")
        >>> # Returns: "(0.12-0.02)/0.15"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SharpeRatio

            Formula metadata
        """
        return FormulaMetadata(
            name="SHARPE_RATIO",
            category="investments",
            description="Calculate Sharpe ratio (risk-adjusted return metric)",
            arguments=(
                FormulaArgument(
                    "portfolio_return",
                    "number",
                    required=True,
                    description="Expected portfolio return",
                ),
                FormulaArgument(
                    "risk_free_rate",
                    "number",
                    required=True,
                    description="Risk-free rate of return",
                ),
                FormulaArgument(
                    "std_deviation",
                    "number",
                    required=True,
                    description="Standard deviation of portfolio returns",
                ),
            ),
            return_type="number",
            examples=(
                "=SHARPE_RATIO(0.12;0.02;0.15)",
                "=SHARPE_RATIO(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SharpeRatio formula string.

        Args:
            *args: portfolio_return, risk_free_rate, std_deviation
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SharpeRatio formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        portfolio_return = args[0]
        risk_free_rate = args[1]
        std_deviation = args[2]

        # Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Standard Deviation
        return f"of:=({portfolio_return}-{risk_free_rate})/{std_deviation}"


@dataclass(slots=True, frozen=True)
class PortfolioBeta(BaseFormula):
    """Calculate portfolio beta (market volatility).

        Beta formula for measuring portfolio volatility relative to market

    Example:
        >>> formula = PortfolioBeta()
        >>> result = formula.build("A1:A10", "B1:B10")
        >>> # Returns: "of:=COVAR(A1:A10;B1:B10)/VAR(B1:B10)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PortfolioBeta

            Formula metadata
        """
        return FormulaMetadata(
            name="PORTFOLIO_BETA",
            category="investments",
            description="Calculate portfolio beta (volatility vs market)",
            arguments=(
                FormulaArgument(
                    "portfolio_returns",
                    "range",
                    required=True,
                    description="Range of portfolio return values",
                ),
                FormulaArgument(
                    "market_returns",
                    "range",
                    required=True,
                    description="Range of market return values",
                ),
            ),
            return_type="number",
            examples=(
                "=PORTFOLIO_BETA(A1:A10;B1:B10)",
                "=PORTFOLIO_BETA(C2:C100;D2:D100)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PortfolioBeta formula string.

        Args:
            *args: portfolio_returns, market_returns
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PortfolioBeta formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        portfolio_returns = args[0]
        market_returns = args[1]

        # Beta = Covariance(Portfolio, Market) / Variance(Market)
        return f"of:=COVAR({portfolio_returns};{market_returns})/VAR({market_returns})"
