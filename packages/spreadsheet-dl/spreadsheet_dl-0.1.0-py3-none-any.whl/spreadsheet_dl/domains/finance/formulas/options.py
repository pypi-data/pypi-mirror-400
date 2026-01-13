"""Options pricing formulas.

Options pricing formulas including Black-Scholes model for calls and puts,
implied volatility, and Greeks (Delta, Gamma, Theta, Vega, Rho).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BlackScholesCall(BaseFormula):
    """Calculate call option value using Black-Scholes model.

        Black-Scholes formula for European call option pricing

    Example:
        >>> formula = BlackScholesCall()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2")
        >>> # Returns Black-Scholes call option formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BlackScholesCall

            Options formula metadata
        """
        return FormulaMetadata(
            name="BS_CALL",
            category="options",
            description="Calculate call option value using Black-Scholes",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
            ),
            return_type="number",
            examples=(
                "=BS_CALL(100;105;0.05;1;0.2)",
                "=BS_CALL(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BS_CALL formula string.

        Args:
            *args: spot, strike, rate, time, volatility
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Black-Scholes call formula: S*N(d1) - K*exp(-r*t)*N(d2)
            where d1 = (ln(S/K) + (r + v^2/2)*t) / (v*sqrt(t))
            and d2 = d1 - v*sqrt(t)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]

        # d1 = (LN(S/K) + (r + v^2/2)*t) / (v*SQRT(t))
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        # d2 = d1 - v*SQRT(t)
        d2 = f"({d1}-{volatility}*SQRT({time}))"
        # Call = S*N(d1) - K*EXP(-r*t)*N(d2)
        return (
            f"of:={spot}*NORMSDIST({d1})-{strike}*EXP(-{rate}*{time})*NORMSDIST({d2})"
        )


@dataclass(slots=True, frozen=True)
class BlackScholesPut(BaseFormula):
    """Calculate put option value using Black-Scholes model.

        Black-Scholes formula for European put option pricing

    Example:
        >>> formula = BlackScholesPut()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2")
        >>> # Returns Black-Scholes put option formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BlackScholesPut

            Options formula metadata
        """
        return FormulaMetadata(
            name="BS_PUT",
            category="options",
            description="Calculate put option value using Black-Scholes",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
            ),
            return_type="number",
            examples=(
                "=BS_PUT(100;105;0.05;1;0.2)",
                "=BS_PUT(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BS_PUT formula string.

        Args:
            *args: spot, strike, rate, time, volatility
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Black-Scholes put formula: K*exp(-r*t)*N(-d2) - S*N(-d1)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]

        # d1 = (LN(S/K) + (r + v^2/2)*t) / (v*SQRT(t))
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        # d2 = d1 - v*SQRT(t)
        d2 = f"({d1}-{volatility}*SQRT({time}))"
        # Put = K*EXP(-r*t)*N(-d2) - S*N(-d1)
        return f"of:={strike}*EXP(-{rate}*{time})*NORMSDIST(-({d2}))-{spot}*NORMSDIST(-({d1}))"


@dataclass(slots=True, frozen=True)
class ImpliedVolatility(BaseFormula):
    """Derive implied volatility from market option prices.

        Implied volatility calculation using iterative approximation

    Example:
        >>> formula = ImpliedVolatility()
        >>> result = formula.build("10", "100", "105", "0.05", "1", "call")
        >>> # Returns implied volatility approximation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ImpliedVolatility

            Options formula metadata
        """
        return FormulaMetadata(
            name="IMPLIED_VOL",
            category="options",
            description="Derive implied volatility from market prices",
            arguments=(
                FormulaArgument(
                    "option_price",
                    "number",
                    required=True,
                    description="Market option price",
                ),
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "option_type",
                    "text",
                    required=True,
                    description="Option type: 'call' or 'put'",
                ),
            ),
            return_type="number",
            examples=(
                '=IMPLIED_VOL(10;100;105;0.05;1;"call")',
                '=IMPLIED_VOL(A1;A2;A3;A4;A5;"put")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build IMPLIED_VOL formula string.

        Args:
            *args: option_price, spot, strike, rate, time, option_type
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Implied volatility approximation (simplified Brenner-Subrahmanyam)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        option_price = args[0]
        spot = args[1]
        time = args[4]
        # option_type = args[5]  # Not used in approximation formula

        # Simplified approximation: IV ≈ sqrt(2*pi/t) * (C/S)
        return f"of:=SQRT(2*PI()/{time})*({option_price}/{spot})"


@dataclass(slots=True, frozen=True)
class OptionDelta(BaseFormula):
    """Calculate option Delta (first derivative sensitivity).

        Delta calculation measuring option price sensitivity to stock price changes

    Example:
        >>> formula = OptionDelta()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2", "call")
        >>> # Returns Delta formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OptionDelta

            Options formula metadata
        """
        return FormulaMetadata(
            name="OPTION_DELTA",
            category="options",
            description="Calculate option Delta (price sensitivity)",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
                FormulaArgument(
                    "option_type",
                    "text",
                    required=True,
                    description="Option type: 'call' or 'put'",
                ),
            ),
            return_type="number",
            examples=(
                '=OPTION_DELTA(100;105;0.05;1;0.2;"call")',
                '=OPTION_DELTA(A1;A2;A3;A4;A5;"put")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OPTION_DELTA formula string.

        Args:
            *args: spot, strike, rate, time, volatility, option_type
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Delta formula: N(d1) for call, N(d1)-1 for put

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]
        option_type = args[5]

        # d1 = (LN(S/K) + (r + v^2/2)*t) / (v*SQRT(t))
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        # Delta: N(d1) for call, N(d1)-1 for put
        return f'of:=IF({option_type}="call";NORMSDIST({d1});NORMSDIST({d1})-1)'


@dataclass(slots=True, frozen=True)
class OptionGamma(BaseFormula):
    """Calculate option Gamma (second derivative sensitivity).

        Gamma calculation measuring Delta sensitivity to stock price changes

    Example:
        >>> formula = OptionGamma()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2")
        >>> # Returns Gamma formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OptionGamma

            Options formula metadata
        """
        return FormulaMetadata(
            name="OPTION_GAMMA",
            category="options",
            description="Calculate option Gamma (Delta sensitivity)",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
            ),
            return_type="number",
            examples=(
                "=OPTION_GAMMA(100;105;0.05;1;0.2)",
                "=OPTION_GAMMA(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OPTION_GAMMA formula string.

        Args:
            *args: spot, strike, rate, time, volatility
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Gamma formula: N'(d1) / (S * v * sqrt(t))

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]

        # d1 = (LN(S/K) + (r + v^2/2)*t) / (v*SQRT(t))
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        # N'(d1) = EXP(-d1^2/2) / SQRT(2*PI)
        nprime_d1 = f"EXP(-({d1})^2/2)/SQRT(2*PI())"
        # Gamma = N'(d1) / (S * v * sqrt(t))
        return f"of:={nprime_d1}/({spot}*{volatility}*SQRT({time}))"


@dataclass(slots=True, frozen=True)
class OptionTheta(BaseFormula):
    """Calculate option Theta (time decay).

        Theta calculation measuring option price sensitivity to time passage

    Example:
        >>> formula = OptionTheta()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2", "call")
        >>> # Returns Theta formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OptionTheta

            Options formula metadata
        """
        return FormulaMetadata(
            name="OPTION_THETA",
            category="options",
            description="Calculate option Theta (time decay)",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
                FormulaArgument(
                    "option_type",
                    "text",
                    required=True,
                    description="Option type: 'call' or 'put'",
                ),
            ),
            return_type="number",
            examples=(
                '=OPTION_THETA(100;105;0.05;1;0.2;"call")',
                '=OPTION_THETA(A1;A2;A3;A4;A5;"put")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OPTION_THETA formula string.

        Args:
            *args: spot, strike, rate, time, volatility, option_type
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Theta formula (simplified for daily decay)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]
        option_type = args[5]

        # d1 and d2
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        d2 = f"({d1}-{volatility}*SQRT({time}))"
        # N'(d1)
        nprime_d1 = f"EXP(-({d1})^2/2)/SQRT(2*PI())"
        # Theta components (call/put differ in second term)
        term1 = f"-({spot}*{nprime_d1}*{volatility})/(2*SQRT({time}))"
        call_term2 = f"-{rate}*{strike}*EXP(-{rate}*{time})*NORMSDIST({d2})"
        put_term2 = f"{rate}*{strike}*EXP(-{rate}*{time})*NORMSDIST(-({d2}))"

        return (
            f'of:=IF({option_type}="call";{term1}+{call_term2};{term1}+{put_term2})/365'
        )


@dataclass(slots=True, frozen=True)
class OptionVega(BaseFormula):
    """Calculate option Vega (volatility sensitivity).

        Vega calculation measuring option price sensitivity to volatility changes

    Example:
        >>> formula = OptionVega()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2")
        >>> # Returns Vega formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OptionVega

            Options formula metadata
        """
        return FormulaMetadata(
            name="OPTION_VEGA",
            category="options",
            description="Calculate option Vega (volatility sensitivity)",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
            ),
            return_type="number",
            examples=(
                "=OPTION_VEGA(100;105;0.05;1;0.2)",
                "=OPTION_VEGA(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OPTION_VEGA formula string.

        Args:
            *args: spot, strike, rate, time, volatility
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Vega formula: S * sqrt(t) * N'(d1)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]

        # d1 = (LN(S/K) + (r + v^2/2)*t) / (v*SQRT(t))
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        # N'(d1) = EXP(-d1^2/2) / SQRT(2*PI)
        nprime_d1 = f"EXP(-({d1})^2/2)/SQRT(2*PI())"
        # Vega = S * sqrt(t) * N'(d1)
        return f"of:={spot}*SQRT({time})*{nprime_d1}/100"


@dataclass(slots=True, frozen=True)
class OptionRho(BaseFormula):
    """Calculate option Rho (interest rate sensitivity).

        Rho calculation measuring option price sensitivity to interest rate changes

    Example:
        >>> formula = OptionRho()
        >>> result = formula.build("100", "105", "0.05", "1", "0.2", "call")
        >>> # Returns Rho formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OptionRho

            Options formula metadata
        """
        return FormulaMetadata(
            name="OPTION_RHO",
            category="options",
            description="Calculate option Rho (interest rate sensitivity)",
            arguments=(
                FormulaArgument(
                    "spot",
                    "number",
                    required=True,
                    description="Current stock price",
                ),
                FormulaArgument(
                    "strike",
                    "number",
                    required=True,
                    description="Strike price",
                ),
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Risk-free interest rate",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time to maturity (years)",
                ),
                FormulaArgument(
                    "volatility",
                    "number",
                    required=True,
                    description="Volatility (annual)",
                ),
                FormulaArgument(
                    "option_type",
                    "text",
                    required=True,
                    description="Option type: 'call' or 'put'",
                ),
            ),
            return_type="number",
            examples=(
                '=OPTION_RHO(100;105;0.05;1;0.2;"call")',
                '=OPTION_RHO(A1;A2;A3;A4;A5;"put")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OPTION_RHO formula string.

        Args:
            *args: spot, strike, rate, time, volatility, option_type
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Rho formula: K*t*exp(-r*t)*N(d2) for call, -K*t*exp(-r*t)*N(-d2) for put

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        spot = args[0]
        strike = args[1]
        rate = args[2]
        time = args[3]
        volatility = args[4]
        option_type = args[5]

        # d1 and d2
        d1 = f"(LN({spot}/{strike})+({rate}+{volatility}^2/2)*{time})/({volatility}*SQRT({time}))"
        d2 = f"({d1}-{volatility}*SQRT({time}))"
        # Rho: K*t*exp(-r*t)*N(d2) for call, -K*t*exp(-r*t)*N(-d2) for put
        call_rho = f"{strike}*{time}*EXP(-{rate}*{time})*NORMSDIST({d2})/100"
        put_rho = f"-{strike}*{time}*EXP(-{rate}*{time})*NORMSDIST(-({d2}))/100"

        return f'of:=IF({option_type}="call";{call_rho};{put_rho})'
