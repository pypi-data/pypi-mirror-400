"""Quality metrics formulas for manufacturing.

Quality metrics formulas (DEFECT_RATE, FIRST_PASS_YIELD, PROCESS_CAPABILITY, CONTROL_LIMITS)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class DefectRateFormula(BaseFormula):
    """Defect rate calculation (defects / total units).

        DEFECT_RATE formula for quality metrics

    Defect Rate = (Defects / Total Units) * 100

    Example:
        >>> formula = DefectRateFormula()
        >>> result = formula.build(25, 1000)
        >>> # Returns: "(25/1000)*100" (2.5%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DEFECT_RATE

            Formula metadata
        """
        return FormulaMetadata(
            name="DEFECT_RATE",
            category="quality",
            description="Calculate defect rate percentage (defects / total units * 100)",
            arguments=(
                FormulaArgument(
                    "defects",
                    "number",
                    required=True,
                    description="Number of defective units or cell reference",
                ),
                FormulaArgument(
                    "total_units",
                    "number",
                    required=True,
                    description="Total number of units inspected or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=DEFECT_RATE(A1;B1)",
                "=(25/1000)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DEFECT_RATE formula string.

        Args:
            *args: defects, total_units
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            DEFECT_RATE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        defects, total_units = args

        # Formula: (Defects / Total) * 100
        return f"of:=({defects}/{total_units})*100"


@dataclass(slots=True, frozen=True)
class FirstPassYieldFormula(BaseFormula):
    """First pass yield percentage.

        FIRST_PASS_YIELD formula for quality metrics

    First Pass Yield = (Good Units / Total Units) * 100

    Example:
        >>> formula = FirstPassYieldFormula()
        >>> result = formula.build(950, 1000)
        >>> # Returns: "(950/1000)*100" (95%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for FIRST_PASS_YIELD

            Formula metadata
        """
        return FormulaMetadata(
            name="FIRST_PASS_YIELD",
            category="quality",
            description="Calculate first pass yield percentage (good units / total * 100)",
            arguments=(
                FormulaArgument(
                    "good_units",
                    "number",
                    required=True,
                    description="Number of units passing first inspection or cell reference",
                ),
                FormulaArgument(
                    "total_units",
                    "number",
                    required=True,
                    description="Total number of units produced or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=FIRST_PASS_YIELD(A1;B1)",
                "=(950/1000)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FIRST_PASS_YIELD formula string.

        Args:
            *args: good_units, total_units
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            FIRST_PASS_YIELD formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        good_units, total_units = args

        # Formula: (Good / Total) * 100
        return f"of:=({good_units}/{total_units})*100"


@dataclass(slots=True, frozen=True)
class ProcessCapabilityFormula(BaseFormula):
    """Process capability index (Cp, Cpk).

        PROCESS_CAPABILITY formula for quality metrics

    Cp = (USL - LSL) / (6 * StdDev)
    Cpk = MIN((USL - Mean) / (3 * StdDev), (Mean - LSL) / (3 * StdDev))

    Example:
        >>> formula = ProcessCapabilityFormula()
        >>> result = formula.build(10, 0, 5, 0.5)
        >>> # Returns Cp: "(10-0)/(6*0.5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PROCESS_CAPABILITY

            Formula metadata
        """
        return FormulaMetadata(
            name="PROCESS_CAPABILITY",
            category="quality",
            description="Calculate process capability index Cp",
            arguments=(
                FormulaArgument(
                    "usl",
                    "number",
                    required=True,
                    description="Upper specification limit or cell reference",
                ),
                FormulaArgument(
                    "lsl",
                    "number",
                    required=True,
                    description="Lower specification limit or cell reference",
                ),
                FormulaArgument(
                    "mean",
                    "number",
                    required=True,
                    description="Process mean or cell reference",
                ),
                FormulaArgument(
                    "stddev",
                    "number",
                    required=True,
                    description="Process standard deviation or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=PROCESS_CAPABILITY(A1;B1;C1;D1)",
                "=(10-0)/(6*0.5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PROCESS_CAPABILITY formula string.

        Args:
            *args: usl, lsl, mean, stddev
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string for Cp

            PROCESS_CAPABILITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        usl, lsl, _mean, stddev = args

        # Formula: Cp = (USL - LSL) / (6 * StdDev)
        return f"of:=({usl}-{lsl})/(6*{stddev})"


@dataclass(slots=True, frozen=True)
class ControlLimitsFormula(BaseFormula):
    """Statistical control limits (UCL, LCL).

        CONTROL_LIMITS formula for quality metrics

    UCL = Mean + (3 * StdDev)
    LCL = Mean - (3 * StdDev)

    Example:
        >>> formula = ControlLimitsFormula()
        >>> result = formula.build(100, 5, "upper")
        >>> # Returns: "100+(3*5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CONTROL_LIMITS

            Formula metadata
        """
        return FormulaMetadata(
            name="CONTROL_LIMITS",
            category="quality",
            description="Calculate statistical control limits (UCL/LCL)",
            arguments=(
                FormulaArgument(
                    "mean",
                    "number",
                    required=True,
                    description="Process mean or cell reference",
                ),
                FormulaArgument(
                    "stddev",
                    "number",
                    required=True,
                    description="Process standard deviation or cell reference",
                ),
                FormulaArgument(
                    "limit_type",
                    "string",
                    required=True,
                    description="'upper' for UCL or 'lower' for LCL",
                ),
            ),
            return_type="number",
            examples=(
                "=CONTROL_LIMITS(A1;B1;'upper')",
                "=100+(3*5)",
                "=100-(3*5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CONTROL_LIMITS formula string.

        Args:
            *args: mean, stddev, limit_type ('upper' or 'lower')
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CONTROL_LIMITS formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mean, stddev, limit_type = args

        # Normalize limit_type string (remove quotes if present)
        limit_str = str(limit_type).strip("'\"").lower()

        if limit_str == "upper":
            # UCL = Mean + (3 * StdDev)
            return f"of:={mean}+(3*{stddev})"
        elif limit_str == "lower":
            # LCL = Mean - (3 * StdDev)
            return f"of:={mean}-(3*{stddev})"
        else:
            # Default to upper if unrecognized
            return f"of:={mean}+(3*{stddev})"


__all__ = [
    "ControlLimitsFormula",
    "DefectRateFormula",
    "FirstPassYieldFormula",
    "ProcessCapabilityFormula",
]
