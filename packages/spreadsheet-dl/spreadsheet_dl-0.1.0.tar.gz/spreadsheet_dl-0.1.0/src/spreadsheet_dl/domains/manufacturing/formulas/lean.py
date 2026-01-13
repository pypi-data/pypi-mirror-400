"""Lean manufacturing formulas for manufacturing.

Lean manufacturing formulas (10 total)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ValueStreamEfficiencyFormula(BaseFormula):
    """Value stream efficiency calculation.

        VALUE_STREAM_EFFICIENCY formula for lean manufacturing

    Value Stream Efficiency = (Value-Add Time / Total Time) * 100

    Example:
        >>> formula = ValueStreamEfficiencyFormula()
        >>> result = formula.build(120, 600)
        >>> # Returns: "(120/600)*100" (20%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for VALUE_STREAM_EFFICIENCY

            Formula metadata
        """
        return FormulaMetadata(
            name="VALUE_STREAM_EFFICIENCY",
            category="lean",
            description="Calculate value stream efficiency (value-add time / total time * 100)",
            arguments=(
                FormulaArgument(
                    "value_add_time",
                    "number",
                    required=True,
                    description="Value-adding time in minutes or cell reference",
                ),
                FormulaArgument(
                    "total_time",
                    "number",
                    required=True,
                    description="Total process time in minutes or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=VALUE_STREAM_EFFICIENCY(A1;B1)",
                "=(120/600)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build VALUE_STREAM_EFFICIENCY formula string.

        Args:
            *args: value_add_time, total_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            VALUE_STREAM_EFFICIENCY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        value_add_time, total_time = args

        # Formula: (Value-Add Time / Total Time) * 100
        return f"of:=({value_add_time}/{total_time})*100"


@dataclass(slots=True, frozen=True)
class LeadTimeFormula(BaseFormula):
    """Lead time calculation (order to delivery).

        LEAD_TIME formula for lean manufacturing

    Lead Time = Delivery Date - Order Date

    Example:
        >>> formula = LeadTimeFormula()
        >>> result = formula.build("B1", "A1")
        >>> # Returns: "B1-A1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LEAD_TIME

            Formula metadata
        """
        return FormulaMetadata(
            name="LEAD_TIME",
            category="lean",
            description="Calculate lead time (delivery date - order date)",
            arguments=(
                FormulaArgument(
                    "delivery_date",
                    "number",
                    required=True,
                    description="Delivery date or cell reference",
                ),
                FormulaArgument(
                    "order_date",
                    "number",
                    required=True,
                    description="Order date or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=LEAD_TIME(B1;A1)",
                "=B1-A1",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LEAD_TIME formula string.

        Args:
            *args: delivery_date, order_date
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LEAD_TIME formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        delivery_date, order_date = args

        # Formula: Delivery Date - Order Date
        return f"of:={delivery_date}-{order_date}"


@dataclass(slots=True, frozen=True)
class ProcessCycleEfficiencyFormula(BaseFormula):
    """Process cycle efficiency calculation.

        PROCESS_CYCLE_EFFICIENCY formula for lean manufacturing

    PCE = (Value-Add Time / Lead Time) * 100

    Example:
        >>> formula = ProcessCycleEfficiencyFormula()
        >>> result = formula.build(120, 720)
        >>> # Returns: "(120/720)*100" (16.67%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PROCESS_CYCLE_EFFICIENCY

            Formula metadata
        """
        return FormulaMetadata(
            name="PROCESS_CYCLE_EFFICIENCY",
            category="lean",
            description="Calculate process cycle efficiency (value-add time / lead time * 100)",
            arguments=(
                FormulaArgument(
                    "value_add_time",
                    "number",
                    required=True,
                    description="Value-adding time or cell reference",
                ),
                FormulaArgument(
                    "lead_time",
                    "number",
                    required=True,
                    description="Total lead time or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=PROCESS_CYCLE_EFFICIENCY(A1;B1)",
                "=(120/720)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PROCESS_CYCLE_EFFICIENCY formula string.

        Args:
            *args: value_add_time, lead_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PROCESS_CYCLE_EFFICIENCY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        value_add_time, lead_time = args

        # Formula: (Value-Add Time / Lead Time) * 100
        return f"of:=({value_add_time}/{lead_time})*100"


@dataclass(slots=True, frozen=True)
class TaktTimeFormula(BaseFormula):
    """Takt time calculation (available time / demand).

        TAKT_TIME formula for lean manufacturing

    Takt Time = Available Time / Customer Demand

    Example:
        >>> formula = TaktTimeFormula()
        >>> result = formula.build(28800, 1200)
        >>> # Returns: "28800/1200" (24 seconds)
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
            category="lean",
            description="Calculate takt time (available time / customer demand)",
            arguments=(
                FormulaArgument(
                    "available_time",
                    "number",
                    required=True,
                    description="Available production time in seconds or cell reference",
                ),
                FormulaArgument(
                    "customer_demand",
                    "number",
                    required=True,
                    description="Customer demand in units or cell reference",
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
            *args: available_time, customer_demand
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TAKT_TIME formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        available_time, customer_demand = args

        # Formula: Available Time / Customer Demand
        return f"of:={available_time}/{customer_demand}"


@dataclass(slots=True, frozen=True)
class CycleTimeFormula(BaseFormula):
    """Cycle time to complete one unit.

        CYCLE_TIME formula for lean manufacturing

    Cycle Time = Production Time / Units Produced

    Example:
        >>> formula = CycleTimeFormula()
        >>> result = formula.build(480, 120)
        >>> # Returns: "480/120" (4 minutes)
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
            category="lean",
            description="Calculate cycle time (time to complete one unit)",
            arguments=(
                FormulaArgument(
                    "production_time",
                    "number",
                    required=True,
                    description="Total production time or cell reference",
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
class TotalProductiveMaintenanceFormula(BaseFormula):
    """Total Productive Maintenance (TPM) availability metric.

        TPM_AVAILABILITY formula for lean manufacturing

    TPM Availability = (Operating Time / Planned Production Time) * 100

    Example:
        >>> formula = TotalProductiveMaintenanceFormula()
        >>> result = formula.build(420, 480)
        >>> # Returns: "(420/480)*100" (87.5%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TPM_AVAILABILITY

            Formula metadata
        """
        return FormulaMetadata(
            name="TPM_AVAILABILITY",
            category="lean",
            description="Calculate TPM availability (operating time / planned time * 100)",
            arguments=(
                FormulaArgument(
                    "operating_time",
                    "number",
                    required=True,
                    description="Actual operating time or cell reference",
                ),
                FormulaArgument(
                    "planned_time",
                    "number",
                    required=True,
                    description="Planned production time or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=TPM_AVAILABILITY(A1;B1)",
                "=(420/480)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TPM_AVAILABILITY formula string.

        Args:
            *args: operating_time, planned_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TPM_AVAILABILITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        operating_time, planned_time = args

        # Formula: (Operating Time / Planned Time) * 100
        return f"of:=({operating_time}/{planned_time})*100"


@dataclass(slots=True, frozen=True)
class SingleMinuteExchangeFormula(BaseFormula):
    """SMED changeover time calculation.

        SMED_CHANGEOVER formula for lean manufacturing

    SMED Changeover Time = Stop Time - Start Time

    Example:
        >>> formula = SingleMinuteExchangeFormula()
        >>> result = formula.build(125, 110)
        >>> # Returns: "125-110" (15 minutes)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SMED_CHANGEOVER

            Formula metadata
        """
        return FormulaMetadata(
            name="SMED_CHANGEOVER",
            category="lean",
            description="Calculate SMED changeover time (stop time - start time)",
            arguments=(
                FormulaArgument(
                    "stop_time",
                    "number",
                    required=True,
                    description="Changeover stop time or cell reference",
                ),
                FormulaArgument(
                    "start_time",
                    "number",
                    required=True,
                    description="Changeover start time or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=SMED_CHANGEOVER(A1;B1)",
                "=125-110",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SMED_CHANGEOVER formula string.

        Args:
            *args: stop_time, start_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SMED_CHANGEOVER formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        stop_time, start_time = args

        # Formula: Stop Time - Start Time
        return f"of:={stop_time}-{start_time}"


@dataclass(slots=True, frozen=True)
class KanbanCalculationFormula(BaseFormula):
    """Optimal kanban quantity calculation.

        KANBAN_QUANTITY formula for lean manufacturing

    Kanban Quantity = ((Demand * Lead Time) * (1 + Safety Factor))

    Example:
        >>> formula = KanbanCalculationFormula()
        >>> result = formula.build(100, 5, 0.2)
        >>> # Returns: "((100*5)*(1+0.2))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for KANBAN_QUANTITY

            Formula metadata
        """
        return FormulaMetadata(
            name="KANBAN_QUANTITY",
            category="lean",
            description="Calculate optimal kanban quantity ((demand * lead time) * (1 + safety factor))",
            arguments=(
                FormulaArgument(
                    "demand",
                    "number",
                    required=True,
                    description="Daily demand in units or cell reference",
                ),
                FormulaArgument(
                    "lead_time",
                    "number",
                    required=True,
                    description="Lead time in days or cell reference",
                ),
                FormulaArgument(
                    "safety_factor",
                    "number",
                    required=True,
                    description="Safety factor (e.g., 0.2 for 20%) or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=KANBAN_QUANTITY(A1;B1;C1)",
                "=((100*5)*(1+0.2))",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build KANBAN_QUANTITY formula string.

        Args:
            *args: demand, lead_time, safety_factor
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            KANBAN_QUANTITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        demand, lead_time, safety_factor = args

        # Formula: ((Demand * Lead Time) * (1 + Safety Factor))
        return f"of:=(({demand}*{lead_time})*(1+{safety_factor}))"


@dataclass(slots=True, frozen=True)
class LittlesLawFormula(BaseFormula):
    """Little's Law: WIP = Throughput * Lead Time.

        LITTLES_LAW formula for lean manufacturing

    WIP = Throughput * Lead Time

    Example:
        >>> formula = LittlesLawFormula()
        >>> result = formula.build(10, 5)
        >>> # Returns: "10*5" (50 units)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LITTLES_LAW

            Formula metadata
        """
        return FormulaMetadata(
            name="LITTLES_LAW",
            category="lean",
            description="Calculate WIP using Little's Law (throughput * lead time)",
            arguments=(
                FormulaArgument(
                    "throughput",
                    "number",
                    required=True,
                    description="Throughput rate (units/time) or cell reference",
                ),
                FormulaArgument(
                    "lead_time",
                    "number",
                    required=True,
                    description="Lead time in same time unit or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=LITTLES_LAW(A1;B1)",
                "=10*5",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LITTLES_LAW formula string.

        Args:
            *args: throughput, lead_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LITTLES_LAW formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        throughput, lead_time = args

        # Formula: WIP = Throughput * Lead Time
        return f"of:={throughput}*{lead_time}"


@dataclass(slots=True, frozen=True)
class FlowEfficiencyFormula(BaseFormula):
    """Flow efficiency calculation.

        FLOW_EFFICIENCY formula for lean manufacturing

    Flow Efficiency = (Touch Time / Elapsed Time) * 100

    Example:
        >>> formula = FlowEfficiencyFormula()
        >>> result = formula.build(60, 480)
        >>> # Returns: "(60/480)*100" (12.5%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for FLOW_EFFICIENCY

            Formula metadata
        """
        return FormulaMetadata(
            name="FLOW_EFFICIENCY",
            category="lean",
            description="Calculate flow efficiency (touch time / elapsed time * 100)",
            arguments=(
                FormulaArgument(
                    "touch_time",
                    "number",
                    required=True,
                    description="Active work time or cell reference",
                ),
                FormulaArgument(
                    "elapsed_time",
                    "number",
                    required=True,
                    description="Total elapsed time or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=FLOW_EFFICIENCY(A1;B1)",
                "=(60/480)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build FLOW_EFFICIENCY formula string.

        Args:
            *args: touch_time, elapsed_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            FLOW_EFFICIENCY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        touch_time, elapsed_time = args

        # Formula: (Touch Time / Elapsed Time) * 100
        return f"of:=({touch_time}/{elapsed_time})*100"


__all__ = [
    "CycleTimeFormula",
    "FlowEfficiencyFormula",
    "KanbanCalculationFormula",
    "LeadTimeFormula",
    "LittlesLawFormula",
    "ProcessCycleEfficiencyFormula",
    "SingleMinuteExchangeFormula",
    "TaktTimeFormula",
    "TotalProductiveMaintenanceFormula",
    "ValueStreamEfficiencyFormula",
]
