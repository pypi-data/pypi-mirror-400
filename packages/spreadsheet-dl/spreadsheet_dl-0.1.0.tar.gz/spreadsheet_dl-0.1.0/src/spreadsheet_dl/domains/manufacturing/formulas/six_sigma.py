"""Six Sigma quality formulas for manufacturing.

Six Sigma formulas (10 total)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class DPMOFormula(BaseFormula):
    """Defects Per Million Opportunities calculation.

        DPMO formula for Six Sigma quality

    DPMO = (Defects / (Units * Opportunities)) * 1000000

    Example:
        >>> formula = DPMOFormula()
        >>> result = formula.build(25, 1000, 5)
        >>> # Returns: "(25/(1000*5))*1000000" (5000 DPMO)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DPMO

            Formula metadata
        """
        return FormulaMetadata(
            name="DPMO",
            category="six_sigma",
            description="Calculate Defects Per Million Opportunities",
            arguments=(
                FormulaArgument(
                    "defects",
                    "number",
                    required=True,
                    description="Total number of defects or cell reference",
                ),
                FormulaArgument(
                    "units",
                    "number",
                    required=True,
                    description="Number of units inspected or cell reference",
                ),
                FormulaArgument(
                    "opportunities",
                    "number",
                    required=True,
                    description="Defect opportunities per unit or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=DPMO(A1;B1;C1)",
                "=(25/(1000*5))*1000000",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DPMO formula string.

        Args:
            *args: defects, units, opportunities
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            DPMO formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        defects, units, opportunities = args

        # Formula: (Defects / (Units * Opportunities)) * 1,000,000
        return f"of:=({defects}/({units}*{opportunities}))*1000000"


@dataclass(slots=True, frozen=True)
class SigmaLevelFormula(BaseFormula):
    """Sigma level calculation from DPMO.

        SIGMA_LEVEL formula for Six Sigma quality

    Approximation: Sigma Level ≈ 0.8406 + SQRT(29.37 - 2.221 * LN(DPMO))

    Example:
        >>> formula = SigmaLevelFormula()
        >>> result = formula.build(6210)
        >>> # Returns sigma level approximation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SIGMA_LEVEL

            Formula metadata
        """
        return FormulaMetadata(
            name="SIGMA_LEVEL",
            category="six_sigma",
            description="Calculate sigma level from DPMO using approximation",
            arguments=(
                FormulaArgument(
                    "dpmo",
                    "number",
                    required=True,
                    description="Defects per million opportunities or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=SIGMA_LEVEL(A1)",
                "=0.8406+SQRT(29.37-2.221*LN(6210))",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SIGMA_LEVEL formula string.

        Args:
            *args: dpmo
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SIGMA_LEVEL formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        (dpmo,) = args

        # Formula: Approximation using natural log
        # Sigma ≈ 0.8406 + SQRT(29.37 - 2.221 * LN(DPMO))
        return f"of:=0.8406+SQRT(29.37-2.221*LN({dpmo}))"


@dataclass(slots=True, frozen=True)
class ProcessCapabilityIndexFormula(BaseFormula):
    """Process Capability Index (Cpk) calculation.

        CPK formula for Six Sigma quality

    Cpk = MIN((USL - Mean) / (3 * StdDev), (Mean - LSL) / (3 * StdDev))

    Example:
        >>> formula = ProcessCapabilityIndexFormula()
        >>> result = formula.build(10, 0, 5, 0.5)
        >>> # Returns: "MIN((10-5)/(3*0.5);(5-0)/(3*0.5))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CPK

            Formula metadata
        """
        return FormulaMetadata(
            name="CPK",
            category="six_sigma",
            description="Calculate process capability index Cpk",
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
                "=CPK(A1;B1;C1;D1)",
                "=MIN((10-5)/(3*0.5);(5-0)/(3*0.5))",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CPK formula string.

        Args:
            *args: usl, lsl, mean, stddev
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CPK formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        usl, lsl, mean, stddev = args

        # Formula: MIN((USL - Mean) / (3 * StdDev), (Mean - LSL) / (3 * StdDev))
        cpu = f"({usl}-{mean})/(3*{stddev})"
        cpl = f"({mean}-{lsl})/(3*{stddev})"
        return f"of:=MIN({cpu};{cpl})"


@dataclass(slots=True, frozen=True)
class ProcessPerformanceIndexFormula(BaseFormula):
    """Process Performance Index (Ppk) calculation.

        PPK formula for Six Sigma quality

    Ppk = MIN((USL - Mean) / (3 * Overall StdDev), (Mean - LSL) / (3 * Overall StdDev))

    Example:
        >>> formula = ProcessPerformanceIndexFormula()
        >>> result = formula.build(10, 0, 5, 0.6)
        >>> # Returns: "MIN((10-5)/(3*0.6);(5-0)/(3*0.6))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PPK

            Formula metadata
        """
        return FormulaMetadata(
            name="PPK",
            category="six_sigma",
            description="Calculate process performance index Ppk",
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
                    "overall_stddev",
                    "number",
                    required=True,
                    description="Overall process standard deviation or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=PPK(A1;B1;C1;D1)",
                "=MIN((10-5)/(3*0.6);(5-0)/(3*0.6))",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PPK formula string.

        Args:
            *args: usl, lsl, mean, overall_stddev
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PPK formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        usl, lsl, mean, overall_stddev = args

        # Formula: MIN((USL - Mean) / (3 * Overall Sigma), (Mean - LSL) / (3 * Overall Sigma))
        ppu = f"({usl}-{mean})/(3*{overall_stddev})"
        ppl = f"({mean}-{lsl})/(3*{overall_stddev})"
        return f"of:=MIN({ppu};{ppl})"


@dataclass(slots=True, frozen=True)
class YieldCalculationFormula(BaseFormula):
    """Rolled Throughput Yield calculation.

        RTY formula for Six Sigma quality

    RTY = Yield1 * Yield2 * ... * YieldN

    Example:
        >>> formula = YieldCalculationFormula()
        >>> result = formula.build(0.98, 0.95, 0.99)
        >>> # Returns: "0.98*0.95*0.99"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RTY

            Formula metadata
        """
        return FormulaMetadata(
            name="RTY",
            category="six_sigma",
            description="Calculate Rolled Throughput Yield (product of individual yields)",
            arguments=(
                FormulaArgument(
                    "yield1",
                    "number",
                    required=True,
                    description="First process yield (0-1) or cell reference",
                ),
                FormulaArgument(
                    "yield2",
                    "number",
                    required=True,
                    description="Second process yield (0-1) or cell reference",
                ),
                FormulaArgument(
                    "yield3",
                    "number",
                    required=False,
                    description="Third process yield (0-1) or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=RTY(A1;B1;C1)",
                "=0.98*0.95*0.99",
                "=A1*B1",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RTY formula string.

        Args:
            *args: yield1, yield2, [yield3, ...]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RTY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        if len(args) < 2:
            msg = f"{self.metadata.name} requires at least 2 arguments"
            raise ValueError(msg)

        # Formula: Multiply all yields together
        return "of:=" + "*".join(str(arg) for arg in args)


@dataclass(slots=True, frozen=True)
class DefectRateFormula(BaseFormula):
    """Defect rate calculation.

        DEFECT_RATE formula for Six Sigma quality

    Defect Rate = (Defects / Total Units) * 100

    Example:
        >>> formula = DefectRateFormula()
        >>> result = formula.build(15, 1000)
        >>> # Returns: "(15/1000)*100" (1.5%)
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
            category="six_sigma",
            description="Calculate defect rate percentage",
            arguments=(
                FormulaArgument(
                    "defects",
                    "number",
                    required=True,
                    description="Number of defects or cell reference",
                ),
                FormulaArgument(
                    "total_units",
                    "number",
                    required=True,
                    description="Total units inspected or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=DEFECT_RATE(A1;B1)",
                "=(15/1000)*100",
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

        # Formula: (Defects / Total Units) * 100
        return f"of:=({defects}/{total_units})*100"


@dataclass(slots=True, frozen=True)
class ProcessSigmaFormula(BaseFormula):
    """Process sigma calculation from specification limits.

        PROCESS_SIGMA formula for Six Sigma quality

    Process Sigma = (USL - LSL) / (6 * StdDev)

    Example:
        >>> formula = ProcessSigmaFormula()
        >>> result = formula.build(10, 0, 0.5)
        >>> # Returns: "(10-0)/(6*0.5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PROCESS_SIGMA

            Formula metadata
        """
        return FormulaMetadata(
            name="PROCESS_SIGMA",
            category="six_sigma",
            description="Calculate process sigma from specification limits",
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
                    "stddev",
                    "number",
                    required=True,
                    description="Process standard deviation or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=PROCESS_SIGMA(A1;B1;C1)",
                "=(10-0)/(6*0.5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PROCESS_SIGMA formula string.

        Args:
            *args: usl, lsl, stddev
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PROCESS_SIGMA formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        usl, lsl, stddev = args

        # Formula: (USL - LSL) / (6 * StdDev)
        return f"of:=({usl}-{lsl})/(6*{stddev})"


@dataclass(slots=True, frozen=True)
class ControlLimitFormula(BaseFormula):
    """Control limit calculation for control charts.

        CONTROL_LIMIT formula for Six Sigma quality

    UCL = Mean + (Z * StdDev)
    LCL = Mean - (Z * StdDev)

    Example:
        >>> formula = ControlLimitFormula()
        >>> result = formula.build(100, 5, 3, "upper")
        >>> # Returns: "100+(3*5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CONTROL_LIMIT

            Formula metadata
        """
        return FormulaMetadata(
            name="CONTROL_LIMIT",
            category="six_sigma",
            description="Calculate control limit (UCL/LCL) for control charts",
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
                    "z_value",
                    "number",
                    required=True,
                    description="Z-score (typically 3 for 3-sigma) or cell reference",
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
                "=CONTROL_LIMIT(A1;B1;3;'upper')",
                "=100+(3*5)",
                "=100-(3*5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CONTROL_LIMIT formula string.

        Args:
            *args: mean, stddev, z_value, limit_type
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CONTROL_LIMIT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mean, stddev, z_value, limit_type = args

        # Normalize limit_type string
        limit_str = str(limit_type).strip("'\"").lower()

        if limit_str == "upper":
            # UCL = Mean + (Z * StdDev)
            return f"of:={mean}+({z_value}*{stddev})"
        else:
            # LCL = Mean - (Z * StdDev)
            return f"of:={mean}-({z_value}*{stddev})"


@dataclass(slots=True, frozen=True)
class ZScoreQualityFormula(BaseFormula):
    """Z-score calculation for quality metrics.

        Z_SCORE formula for Six Sigma quality

    Z-Score = (Value - Mean) / StdDev

    Example:
        >>> formula = ZScoreQualityFormula()
        >>> result = formula.build(105, 100, 5)
        >>> # Returns: "(105-100)/5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for Z_SCORE

            Formula metadata
        """
        return FormulaMetadata(
            name="Z_SCORE",
            category="six_sigma",
            description="Calculate Z-score for quality metrics",
            arguments=(
                FormulaArgument(
                    "value",
                    "number",
                    required=True,
                    description="Observed value or cell reference",
                ),
                FormulaArgument(
                    "mean",
                    "number",
                    required=True,
                    description="Population mean or cell reference",
                ),
                FormulaArgument(
                    "stddev",
                    "number",
                    required=True,
                    description="Population standard deviation or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=Z_SCORE(A1;B1;C1)",
                "=(105-100)/5",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build Z_SCORE formula string.

        Args:
            *args: value, mean, stddev
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Z_SCORE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        value, mean, stddev = args

        # Formula: (Value - Mean) / StdDev
        return f"of:=({value}-{mean})/{stddev}"


@dataclass(slots=True, frozen=True)
class GaugeRnRFormula(BaseFormula):
    """Gauge R&R (Repeatability and Reproducibility) calculation.

        GAUGE_RNR formula for Six Sigma quality

    GRR = SQRT(Repeatability² + Reproducibility²)

    Example:
        >>> formula = GaugeRnRFormula()
        >>> result = formula.build(0.5, 0.3)
        >>> # Returns: "SQRT(0.5^2+0.3^2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GAUGE_RNR

            Formula metadata
        """
        return FormulaMetadata(
            name="GAUGE_RNR",
            category="six_sigma",
            description="Calculate Gauge R&R (measurement system analysis)",
            arguments=(
                FormulaArgument(
                    "repeatability",
                    "number",
                    required=True,
                    description="Repeatability variance or cell reference",
                ),
                FormulaArgument(
                    "reproducibility",
                    "number",
                    required=True,
                    description="Reproducibility variance or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=GAUGE_RNR(A1;B1)",
                "=SQRT(0.5^2+0.3^2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GAUGE_RNR formula string.

        Args:
            *args: repeatability, reproducibility
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            GAUGE_RNR formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        repeatability, reproducibility = args

        # Formula: SQRT(Repeatability² + Reproducibility²)
        return f"of:=SQRT({repeatability}^2+{reproducibility}^2)"


__all__ = [
    "ControlLimitFormula",
    "DPMOFormula",
    "DefectRateFormula",
    "GaugeRnRFormula",
    "ProcessCapabilityIndexFormula",
    "ProcessPerformanceIndexFormula",
    "ProcessSigmaFormula",
    "SigmaLevelFormula",
    "YieldCalculationFormula",
    "ZScoreQualityFormula",
]
