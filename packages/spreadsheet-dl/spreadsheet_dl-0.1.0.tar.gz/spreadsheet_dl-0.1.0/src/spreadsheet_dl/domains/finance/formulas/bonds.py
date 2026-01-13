"""Bond analytics formulas.

Bond pricing and analytics formulas including bond price, yield to maturity,
Macaulay duration, modified duration, and convexity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BondPrice(BaseFormula):
    """Calculate bond price (present value of cash flows).

        Bond pricing formula discounting coupon payments and face value

    Example:
        >>> formula = BondPrice()
        >>> result = formula.build("1000", "0.05", "0.06", "10", "2")
        >>> # Returns bond price formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BondPrice

            Bond formula metadata
        """
        return FormulaMetadata(
            name="BOND_PRICE",
            category="bonds",
            description="Calculate bond price (present value of cash flows)",
            arguments=(
                FormulaArgument(
                    "face_value",
                    "number",
                    required=True,
                    description="Face value (par value) of bond",
                ),
                FormulaArgument(
                    "coupon_rate",
                    "number",
                    required=True,
                    description="Annual coupon rate",
                ),
                FormulaArgument(
                    "yield_rate",
                    "number",
                    required=True,
                    description="Yield to maturity (annual)",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Years to maturity",
                ),
                FormulaArgument(
                    "frequency",
                    "number",
                    required=False,
                    description="Coupon payments per year (default 2)",
                    default=2,
                ),
            ),
            return_type="number",
            examples=(
                "=BOND_PRICE(1000;0.05;0.06;10;2)",
                "=BOND_PRICE(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BOND_PRICE formula string.

        Args:
            *args: face_value, coupon_rate, yield_rate, years, [frequency]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Bond price = PV of coupons + PV of face value
            Using PV formula for annuity and lump sum

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        face_value = args[0]
        coupon_rate = args[1]
        yield_rate = args[2]
        years = args[3]
        frequency = args[4] if len(args) > 4 else 2

        # Coupon payment per period
        coupon = f"({face_value}*{coupon_rate}/{frequency})"
        # Yield per period
        yield_per_period = f"({yield_rate}/{frequency})"
        # Total periods
        periods = f"({years}*{frequency})"

        # PV of coupon payments (annuity)
        pv_coupons = (
            f"({coupon}*(1-(1+{yield_per_period})^(-{periods}))/{yield_per_period})"
        )
        # PV of face value (lump sum)
        pv_face = f"({face_value}/(1+{yield_per_period})^{periods})"

        return f"of:={pv_coupons}+{pv_face}"


@dataclass(slots=True, frozen=True)
class YieldToMaturity(BaseFormula):
    """Calculate yield to maturity (internal rate of return of bond).

        YTM calculation using iterative approximation

    Example:
        >>> formula = YieldToMaturity()
        >>> result = formula.build("950", "1000", "0.05", "10", "2")
        >>> # Returns YTM approximation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for YieldToMaturity

            Bond formula metadata
        """
        return FormulaMetadata(
            name="YTM",
            category="bonds",
            description="Calculate yield to maturity (IRR of bond)",
            arguments=(
                FormulaArgument(
                    "price",
                    "number",
                    required=True,
                    description="Current bond price",
                ),
                FormulaArgument(
                    "face_value",
                    "number",
                    required=True,
                    description="Face value of bond",
                ),
                FormulaArgument(
                    "coupon_rate",
                    "number",
                    required=True,
                    description="Annual coupon rate",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Years to maturity",
                ),
                FormulaArgument(
                    "frequency",
                    "number",
                    required=False,
                    description="Coupon payments per year (default 2)",
                    default=2,
                ),
            ),
            return_type="number",
            examples=(
                "=YTM(950;1000;0.05;10;2)",
                "=YTM(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build YTM formula string.

        Args:
            *args: price, face_value, coupon_rate, years, [frequency]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            YTM approximation formula (simplified)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        price = args[0]
        face_value = args[1]
        coupon_rate = args[2]
        years = args[3]

        # Coupon payment
        coupon = f"({face_value}*{coupon_rate})"
        # Approximate YTM = (C + (F-P)/n) / ((F+P)/2)
        numerator = f"({coupon}+({face_value}-{price})/{years})"
        denominator = f"(({face_value}+{price})/2)"

        return f"of:={numerator}/{denominator}"


@dataclass(slots=True, frozen=True)
class MacDuration(BaseFormula):
    """Calculate Macaulay duration.

        Macaulay duration calculation measuring weighted average time to cash flows

    Example:
        >>> formula = MacDuration()
        >>> result = formula.build("1000", "0.05", "0.06", "10", "2")
        >>> # Returns Macaulay duration formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MacDuration

            Bond formula metadata
        """
        return FormulaMetadata(
            name="MACDURATION",
            category="bonds",
            description="Calculate Macaulay duration",
            arguments=(
                FormulaArgument(
                    "face_value",
                    "number",
                    required=True,
                    description="Face value of bond",
                ),
                FormulaArgument(
                    "coupon_rate",
                    "number",
                    required=True,
                    description="Annual coupon rate",
                ),
                FormulaArgument(
                    "yield_rate",
                    "number",
                    required=True,
                    description="Yield to maturity",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Years to maturity",
                ),
                FormulaArgument(
                    "frequency",
                    "number",
                    required=False,
                    description="Coupon payments per year (default 2)",
                    default=2,
                ),
            ),
            return_type="number",
            examples=(
                "=MACDURATION(1000;0.05;0.06;10;2)",
                "=MACDURATION(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MACDURATION formula string.

        Args:
            *args: face_value, coupon_rate, yield_rate, years, [frequency]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Macaulay duration using DURATION function

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        coupon_rate = args[1]
        yield_rate = args[2]
        years = args[3]
        frequency = args[4] if len(args) > 4 else 2

        # Use settlement date as today and maturity as years from now
        # DURATION(settlement, maturity, coupon, yield, frequency, basis)
        settlement = "TODAY()"
        maturity = f"TODAY()+{years}*365"

        return f"of:=DURATION({settlement};{maturity};{coupon_rate};{yield_rate};{frequency};0)"


@dataclass(slots=True, frozen=True)
class ModifiedDuration(BaseFormula):
    """Calculate modified duration (price sensitivity to yield changes).

        Modified duration calculation adjusting Macaulay duration by yield

    Example:
        >>> formula = ModifiedDuration()
        >>> result = formula.build("1000", "0.05", "0.06", "10", "2")
        >>> # Returns modified duration formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ModifiedDuration

            Bond formula metadata
        """
        return FormulaMetadata(
            name="MODDURATION",
            category="bonds",
            description="Calculate modified duration (price sensitivity)",
            arguments=(
                FormulaArgument(
                    "face_value",
                    "number",
                    required=True,
                    description="Face value of bond",
                ),
                FormulaArgument(
                    "coupon_rate",
                    "number",
                    required=True,
                    description="Annual coupon rate",
                ),
                FormulaArgument(
                    "yield_rate",
                    "number",
                    required=True,
                    description="Yield to maturity",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Years to maturity",
                ),
                FormulaArgument(
                    "frequency",
                    "number",
                    required=False,
                    description="Coupon payments per year (default 2)",
                    default=2,
                ),
            ),
            return_type="number",
            examples=(
                "=MODDURATION(1000;0.05;0.06;10;2)",
                "=MODDURATION(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MODDURATION formula string.

        Args:
            *args: face_value, coupon_rate, yield_rate, years, [frequency]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Modified duration using MDURATION function

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        coupon_rate = args[1]
        yield_rate = args[2]
        years = args[3]
        frequency = args[4] if len(args) > 4 else 2

        # Use settlement date as today and maturity as years from now
        # MDURATION(settlement, maturity, coupon, yield, frequency, basis)
        settlement = "TODAY()"
        maturity = f"TODAY()+{years}*365"

        return f"of:=MDURATION({settlement};{maturity};{coupon_rate};{yield_rate};{frequency};0)"


@dataclass(slots=True, frozen=True)
class Convexity(BaseFormula):
    """Calculate bond convexity (second-order price sensitivity).

        Convexity calculation measuring curvature of price-yield relationship

    Example:
        >>> formula = Convexity()
        >>> result = formula.build("1000", "0.05", "0.06", "10", "2")
        >>> # Returns convexity approximation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for Convexity

            Bond formula metadata
        """
        return FormulaMetadata(
            name="CONVEXITY",
            category="bonds",
            description="Calculate convexity (second-order price sensitivity)",
            arguments=(
                FormulaArgument(
                    "face_value",
                    "number",
                    required=True,
                    description="Face value of bond",
                ),
                FormulaArgument(
                    "coupon_rate",
                    "number",
                    required=True,
                    description="Annual coupon rate",
                ),
                FormulaArgument(
                    "yield_rate",
                    "number",
                    required=True,
                    description="Yield to maturity",
                ),
                FormulaArgument(
                    "years",
                    "number",
                    required=True,
                    description="Years to maturity",
                ),
                FormulaArgument(
                    "frequency",
                    "number",
                    required=False,
                    description="Coupon payments per year (default 2)",
                    default=2,
                ),
            ),
            return_type="number",
            examples=(
                "=CONVEXITY(1000;0.05;0.06;10;2)",
                "=CONVEXITY(A1;A2;A3;A4;A5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CONVEXITY formula string.

        Args:
            *args: face_value, coupon_rate, yield_rate, years, [frequency]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Convexity approximation formula

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        coupon_rate = args[1]
        yield_rate = args[2]
        years = args[3]
        frequency = args[4] if len(args) > 4 else 2

        # Yield per period
        yield_per_period = f"({yield_rate}/{frequency})"

        # Simplified convexity approximation
        # Convexity ≈ (Duration^2 + Duration + 1/frequency) / (1 + y/frequency)^2
        duration_term = f"DURATION(TODAY();TODAY()+{years}*365;{coupon_rate};{yield_rate};{frequency};0)"
        convexity_approx = f"({duration_term}^2+{duration_term}+1/{frequency})/(1+{yield_per_period})^2"

        return f"of:={convexity_approx}"
