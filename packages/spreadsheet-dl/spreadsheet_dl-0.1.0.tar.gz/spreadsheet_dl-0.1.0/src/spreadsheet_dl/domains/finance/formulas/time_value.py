"""Time value of money formulas.

Financial formulas for present value, future value, and related calculations
(PV, FV, NPV, IRR, PMT, RATE, NPER)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class PresentValue(BaseFormula):
    """Calculate present value of future cash flows.

        PV formula for discounting future cash flows to present value

    Example:
        >>> formula = PresentValue()
        >>> result = formula.build("0.05", "10", "100", "0")
        >>> # Returns: "of:=PV(0.05;10;100;0;0)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PV

            Formula metadata
        """
        return FormulaMetadata(
            name="PV",
            category="time_value",
            description="Calculate present value of future cash flows",
            arguments=(
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Interest rate per period",
                ),
                FormulaArgument(
                    "nper",
                    "number",
                    required=True,
                    description="Number of payment periods",
                ),
                FormulaArgument(
                    "pmt",
                    "number",
                    required=True,
                    description="Payment amount per period",
                ),
                FormulaArgument(
                    "fv",
                    "number",
                    required=False,
                    description="Future value (lump sum)",
                    default=0,
                ),
                FormulaArgument(
                    "type",
                    "number",
                    required=False,
                    description="0=end of period, 1=beginning",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=PV(0.05;10;100;0;0)",
                "=PV(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PV formula string.

        Args:
            *args: rate, nper, pmt, [fv], [type]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PV formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate = args[0]
        nper = args[1]
        pmt = args[2]
        fv = args[3] if len(args) > 3 else 0
        pmt_type = args[4] if len(args) > 4 else 0

        return f"of:=PV({rate};{nper};{pmt};{fv};{pmt_type})"


@dataclass(slots=True, frozen=True)
class FutureValue(BaseFormula):
    """Calculate future value with compound interest.

        FV formula for calculating future value of investments

    Example:
        >>> formula = FutureValue()
        >>> result = formula.build("0.05", "10", "100", "1000")
        >>> # Returns: "of:=FV(0.05;10;100;1000;0)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for FV

            Formula metadata
        """
        return FormulaMetadata(
            name="FV",
            category="time_value",
            description="Calculate future value with compound interest",
            arguments=(
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Interest rate per period",
                ),
                FormulaArgument(
                    "nper",
                    "number",
                    required=True,
                    description="Number of payment periods",
                ),
                FormulaArgument(
                    "pmt",
                    "number",
                    required=True,
                    description="Payment amount per period",
                ),
                FormulaArgument(
                    "pv",
                    "number",
                    required=False,
                    description="Present value (lump sum)",
                    default=0,
                ),
                FormulaArgument(
                    "type",
                    "number",
                    required=False,
                    description="0=end of period, 1=beginning",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=FV(0.05;10;100;1000;0)",
                "=FV(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FV formula string.

        Args:
            *args: rate, nper, pmt, [pv], [type]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            FV formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate = args[0]
        nper = args[1]
        pmt = args[2]
        pv = args[3] if len(args) > 3 else 0
        pmt_type = args[4] if len(args) > 4 else 0

        return f"of:=FV({rate};{nper};{pmt};{pv};{pmt_type})"


@dataclass(slots=True, frozen=True)
class NetPresentValue(BaseFormula):
    """Calculate net present value of cash flows.

        NPV formula for investment analysis

    Example:
        >>> formula = NetPresentValue()
        >>> result = formula.build("0.10", "A1:A5")
        >>> # Returns: "of:=NPV(0.10;A1:A5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for NPV

            Formula metadata
        """
        return FormulaMetadata(
            name="NPV",
            category="time_value",
            description="Calculate net present value of cash flows",
            arguments=(
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Discount rate per period",
                ),
                FormulaArgument(
                    "values",
                    "range",
                    required=True,
                    description="Range of cash flow values",
                ),
            ),
            return_type="number",
            examples=(
                "=NPV(0.10;A1:A5)",
                "=NPV(A1;B1:B10)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build NPV formula string.

        Args:
            *args: rate, values
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            NPV formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate = args[0]
        values = args[1]

        return f"of:=NPV({rate};{values})"


@dataclass(slots=True, frozen=True)
class InternalRateOfReturn(BaseFormula):
    """Calculate internal rate of return.

        IRR formula for investment return calculation

    Example:
        >>> formula = InternalRateOfReturn()
        >>> result = formula.build("A1:A5")
        >>> # Returns: "of:=IRR(A1:A5;0.1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for IRR

            Formula metadata
        """
        return FormulaMetadata(
            name="IRR",
            category="time_value",
            description="Calculate internal rate of return",
            arguments=(
                FormulaArgument(
                    "values",
                    "range",
                    required=True,
                    description="Range of cash flow values",
                ),
                FormulaArgument(
                    "guess",
                    "number",
                    required=False,
                    description="Initial guess for IRR calculation",
                    default=0.1,
                ),
            ),
            return_type="number",
            examples=(
                "=IRR(A1:A5;0.1)",
                "=IRR(B1:B10)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build IRR formula string.

        Args:
            *args: values, [guess]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            IRR formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        values = args[0]
        guess = args[1] if len(args) > 1 else 0.1

        return f"of:=IRR({values};{guess})"


@dataclass(slots=True, frozen=True)
class PaymentFormula(BaseFormula):
    """Calculate loan payment amount.

        PMT formula for loan payment calculation

    Example:
        >>> formula = PaymentFormula()
        >>> result = formula.build("0.05", "360", "200000")
        >>> # Returns: "of:=PMT(0.05;360;200000;0;0)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PMT

            Formula metadata
        """
        return FormulaMetadata(
            name="PMT",
            category="time_value",
            description="Calculate loan payment amount",
            arguments=(
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Interest rate per period",
                ),
                FormulaArgument(
                    "nper",
                    "number",
                    required=True,
                    description="Number of payment periods",
                ),
                FormulaArgument(
                    "pv",
                    "number",
                    required=True,
                    description="Present value (loan amount)",
                ),
                FormulaArgument(
                    "fv",
                    "number",
                    required=False,
                    description="Future value (balloon payment)",
                    default=0,
                ),
                FormulaArgument(
                    "type",
                    "number",
                    required=False,
                    description="0=end of period, 1=beginning",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=PMT(0.05/12;360;200000)",
                "=PMT(A1;A2;A3;0;0)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PMT formula string.

        Args:
            *args: rate, nper, pv, [fv], [type]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PMT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate = args[0]
        nper = args[1]
        pv = args[2]
        fv = args[3] if len(args) > 3 else 0
        pmt_type = args[4] if len(args) > 4 else 0

        return f"of:=PMT({rate};{nper};{pv};{fv};{pmt_type})"


@dataclass(slots=True, frozen=True)
class RateFormula(BaseFormula):
    """Calculate interest rate per period.

        RATE formula for interest rate calculation

    Example:
        >>> formula = RateFormula()
        >>> result = formula.build("360", "-1000", "200000")
        >>> # Returns: "of:=RATE(360;-1000;200000;0;0;0.1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RATE

            Formula metadata
        """
        return FormulaMetadata(
            name="RATE",
            category="time_value",
            description="Calculate interest rate per period",
            arguments=(
                FormulaArgument(
                    "nper",
                    "number",
                    required=True,
                    description="Number of payment periods",
                ),
                FormulaArgument(
                    "pmt",
                    "number",
                    required=True,
                    description="Payment amount per period",
                ),
                FormulaArgument(
                    "pv",
                    "number",
                    required=True,
                    description="Present value",
                ),
                FormulaArgument(
                    "fv",
                    "number",
                    required=False,
                    description="Future value",
                    default=0,
                ),
                FormulaArgument(
                    "type",
                    "number",
                    required=False,
                    description="0=end of period, 1=beginning",
                    default=0,
                ),
                FormulaArgument(
                    "guess",
                    "number",
                    required=False,
                    description="Initial guess for calculation",
                    default=0.1,
                ),
            ),
            return_type="number",
            examples=(
                "=RATE(360;-1000;200000)",
                "=RATE(A1;A2;A3;0;0;0.1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RATE formula string.

        Args:
            *args: nper, pmt, pv, [fv], [type], [guess]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RATE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        nper = args[0]
        pmt = args[1]
        pv = args[2]
        fv = args[3] if len(args) > 3 else 0
        pmt_type = args[4] if len(args) > 4 else 0
        guess = args[5] if len(args) > 5 else 0.1

        return f"of:=RATE({nper};{pmt};{pv};{fv};{pmt_type};{guess})"


@dataclass(slots=True, frozen=True)
class PeriodsFormula(BaseFormula):
    """Calculate number of payment periods.

        NPER formula for period calculation

    Example:
        >>> formula = PeriodsFormula()
        >>> result = formula.build("0.05", "-1000", "200000")
        >>> # Returns: "of:=NPER(0.05;-1000;200000;0;0)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for NPER

            Formula metadata
        """
        return FormulaMetadata(
            name="NPER",
            category="time_value",
            description="Calculate number of payment periods",
            arguments=(
                FormulaArgument(
                    "rate",
                    "number",
                    required=True,
                    description="Interest rate per period",
                ),
                FormulaArgument(
                    "pmt",
                    "number",
                    required=True,
                    description="Payment amount per period",
                ),
                FormulaArgument(
                    "pv",
                    "number",
                    required=True,
                    description="Present value",
                ),
                FormulaArgument(
                    "fv",
                    "number",
                    required=False,
                    description="Future value",
                    default=0,
                ),
                FormulaArgument(
                    "type",
                    "number",
                    required=False,
                    description="0=end of period, 1=beginning",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=NPER(0.05;-1000;200000)",
                "=NPER(A1/12;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build NPER formula string.

        Args:
            *args: rate, pmt, pv, [fv], [type]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            NPER formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        rate = args[0]
        pmt = args[1]
        pv = args[2]
        fv = args[3] if len(args) > 3 else 0
        pmt_type = args[4] if len(args) > 4 else 0

        return f"of:=NPER({rate};{pmt};{pv};{fv};{pmt_type})"
