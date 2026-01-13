"""Production metrics formulas for manufacturing.

Production metrics formulas (CYCLE_TIME, TAKT_TIME, THROUGHPUT, CAPACITY_UTILIZATION)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class CycleTimeFormula(BaseFormula):
    """Manufacturing cycle time calculation.

        CYCLE_TIME formula for production metrics

    Cycle Time = Production Time / Units Produced

    Example:
        >>> formula = CycleTimeFormula()
        >>> result = formula.build(480, 120)
        >>> # Returns: "480/120" (4 minutes per unit)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CYCLE_TIME

            Formula metadata
        """
        return FormulaMetadata(
            name="CYCLE_TIME",
            category="production",
            description="Calculate manufacturing cycle time (production time / units produced)",
            arguments=(
                FormulaArgument(
                    "production_time",
                    "number",
                    required=True,
                    description="Total production time in minutes or cell reference",
                ),
                FormulaArgument(
                    "units_produced",
                    "number",
                    required=True,
                    description="Number of units produced or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=CYCLE_TIME(A1;B1)",
                "=480/120",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CYCLE_TIME formula string.

        Args:
            *args: production_time, units_produced
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CYCLE_TIME formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        production_time, units_produced = args

        # Formula: Production Time / Units Produced
        return f"of:={production_time}/{units_produced}"


@dataclass(slots=True, frozen=True)
class TaktTimeFormula(BaseFormula):
    """Takt time calculation (available time / customer demand).

        TAKT_TIME formula for production metrics

    Takt Time = Available Production Time / Customer Demand

    Example:
        >>> formula = TaktTimeFormula()
        >>> result = formula.build(28800, 1200)
        >>> # Returns: "28800/1200" (24 seconds per unit)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TAKT_TIME

            Formula metadata
        """
        return FormulaMetadata(
            name="TAKT_TIME",
            category="production",
            description="Calculate takt time (available time / customer demand)",
            arguments=(
                FormulaArgument(
                    "available_time",
                    "number",
                    required=True,
                    description="Available production time in seconds or cell reference",
                ),
                FormulaArgument(
                    "demand",
                    "number",
                    required=True,
                    description="Customer demand units or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=TAKT_TIME(A1;B1)",
                "=28800/1200",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TAKT_TIME formula string.

        Args:
            *args: available_time, demand
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TAKT_TIME formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        available_time, demand = args

        # Formula: Available Time / Customer Demand
        return f"of:={available_time}/{demand}"


@dataclass(slots=True, frozen=True)
class ThroughputFormula(BaseFormula):
    """Production throughput rate.

        THROUGHPUT formula for production metrics

    Throughput = Units Produced / Production Time

    Example:
        >>> formula = ThroughputFormula()
        >>> result = formula.build(1200, 480)
        >>> # Returns: "1200/480" (2.5 units per minute)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for THROUGHPUT

            Formula metadata
        """
        return FormulaMetadata(
            name="THROUGHPUT",
            category="production",
            description="Calculate production throughput rate (units / time)",
            arguments=(
                FormulaArgument(
                    "units_produced",
                    "number",
                    required=True,
                    description="Number of units produced or cell reference",
                ),
                FormulaArgument(
                    "production_time",
                    "number",
                    required=True,
                    description="Production time period or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=THROUGHPUT(A1;B1)",
                "=1200/480",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build THROUGHPUT formula string.

        Args:
            *args: units_produced, production_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            THROUGHPUT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        units_produced, production_time = args

        # Formula: Units / Time
        return f"of:={units_produced}/{production_time}"


@dataclass(slots=True, frozen=True)
class CapacityUtilizationFormula(BaseFormula):
    """Capacity utilization percentage.

        CAPACITY_UTILIZATION formula for production metrics

    Capacity Utilization = (Actual Output / Maximum Capacity) * 100

    Example:
        >>> formula = CapacityUtilizationFormula()
        >>> result = formula.build(850, 1000)
        >>> # Returns: "(850/1000)*100" (85%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CAPACITY_UTILIZATION

            Formula metadata
        """
        return FormulaMetadata(
            name="CAPACITY_UTILIZATION",
            category="production",
            description="Calculate capacity utilization percentage",
            arguments=(
                FormulaArgument(
                    "actual_output",
                    "number",
                    required=True,
                    description="Actual production output or cell reference",
                ),
                FormulaArgument(
                    "max_capacity",
                    "number",
                    required=True,
                    description="Maximum production capacity or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=CAPACITY_UTILIZATION(A1;B1)",
                "=(850/1000)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CAPACITY_UTILIZATION formula string.

        Args:
            *args: actual_output, max_capacity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CAPACITY_UTILIZATION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual_output, max_capacity = args

        # Formula: (Actual / Max) * 100
        return f"of:=({actual_output}/{max_capacity})*100"


@dataclass(slots=True, frozen=True)
class OverallEquipmentEffectiveness(BaseFormula):
    """Calculate Overall Equipment Effectiveness (OEE).

        OEE formula combining availability, performance, and quality

    OEE = Availability * Performance * Quality

    Example:
        >>> formula = OverallEquipmentEffectiveness()
        >>> result = formula.build("0.90", "0.95", "0.99")
        >>> # Returns: "0.90*0.95*0.99*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for OEE

            Formula metadata
        """
        return FormulaMetadata(
            name="OEE",
            category="production",
            description="Calculate Overall Equipment Effectiveness percentage",
            arguments=(
                FormulaArgument(
                    "availability",
                    "number",
                    required=True,
                    description="Availability rate (0-1)",
                ),
                FormulaArgument(
                    "performance",
                    "number",
                    required=True,
                    description="Performance rate (0-1)",
                ),
                FormulaArgument(
                    "quality",
                    "number",
                    required=True,
                    description="Quality rate (0-1)",
                ),
            ),
            return_type="number",
            examples=(
                "=OEE(0.90;0.95;0.99)",
                "=OEE(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OEE formula string.

        Args:
            *args: availability, performance, quality
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            OEE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        availability, performance, quality = args

        # OEE = A * P * Q * 100%
        return f"of:={availability}*{performance}*{quality}*100"


__all__ = [
    "CapacityUtilizationFormula",
    "CycleTimeFormula",
    "OverallEquipmentEffectiveness",
    "TaktTimeFormula",
    "ThroughputFormula",
]
