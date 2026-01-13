"""Manufacturing costing formulas.

Manufacturing costing formulas (13 formulas)
BATCH-4.3: Manufacturing domain expansion
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class UnitCostFormula(BaseFormula):
    """Calculate unit cost of production.

    UNIT_COST formula for manufacturing costing
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="UNIT_COST",
            category="costing",
            description="Calculate unit cost (total cost / units produced)",
            arguments=(
                FormulaArgument(
                    "total_cost",
                    "number",
                    required=True,
                    description="Total production cost",
                ),
                FormulaArgument(
                    "units_produced",
                    "number",
                    required=True,
                    description="Number of units produced",
                ),
            ),
            return_type="number",
            examples=(
                "=UNIT_COST(50000;1000)",
                "=UNIT_COST(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build UNIT_COST formula string."""
        self.validate_arguments(args)
        total_cost, units_produced = args
        return f"of:={total_cost}/{units_produced}"


@dataclass(slots=True, frozen=True)
class DirectLaborCostFormula(BaseFormula):
    """Calculate direct labor cost.

    DIRECT_LABOR_COST formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="DIRECT_LABOR_COST",
            category="costing",
            description="Calculate direct labor cost (hours * rate)",
            arguments=(
                FormulaArgument(
                    "labor_hours",
                    "number",
                    required=True,
                    description="Direct labor hours",
                ),
                FormulaArgument(
                    "hourly_rate",
                    "number",
                    required=True,
                    description="Hourly labor rate",
                ),
            ),
            return_type="number",
            examples=(
                "=DIRECT_LABOR_COST(100;25)",
                "=DIRECT_LABOR_COST(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DIRECT_LABOR_COST formula string."""
        self.validate_arguments(args)
        labor_hours, hourly_rate = args
        return f"of:={labor_hours}*{hourly_rate}"


@dataclass(slots=True, frozen=True)
class OverheadRateFormula(BaseFormula):
    """Calculate manufacturing overhead rate.

    OVERHEAD_RATE formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="OVERHEAD_RATE",
            category="costing",
            description="Calculate overhead rate (overhead / direct labor hours)",
            arguments=(
                FormulaArgument(
                    "total_overhead",
                    "number",
                    required=True,
                    description="Total manufacturing overhead",
                ),
                FormulaArgument(
                    "direct_labor_hours",
                    "number",
                    required=True,
                    description="Total direct labor hours",
                ),
            ),
            return_type="number",
            examples=(
                "=OVERHEAD_RATE(100000;5000)",
                "=OVERHEAD_RATE(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build OVERHEAD_RATE formula string."""
        self.validate_arguments(args)
        total_overhead, direct_labor_hours = args
        return f"of:={total_overhead}/{direct_labor_hours}"


@dataclass(slots=True, frozen=True)
class BreakEvenUnitsFormula(BaseFormula):
    """Calculate break-even point in units.

    BREAK_EVEN_UNITS formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BREAK_EVEN_UNITS",
            category="costing",
            description="Calculate break-even units (fixed costs / contribution margin)",
            arguments=(
                FormulaArgument(
                    "fixed_costs",
                    "number",
                    required=True,
                    description="Total fixed costs",
                ),
                FormulaArgument(
                    "price_per_unit",
                    "number",
                    required=True,
                    description="Selling price per unit",
                ),
                FormulaArgument(
                    "variable_cost_per_unit",
                    "number",
                    required=True,
                    description="Variable cost per unit",
                ),
            ),
            return_type="number",
            examples=(
                "=BREAK_EVEN_UNITS(50000;100;60)",
                "=BREAK_EVEN_UNITS(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BREAK_EVEN_UNITS formula string."""
        self.validate_arguments(args)
        fixed_costs, price_per_unit, variable_cost = args
        return f"of:={fixed_costs}/({price_per_unit}-{variable_cost})"


@dataclass(slots=True, frozen=True)
class ContributionMarginFormula(BaseFormula):
    """Calculate contribution margin per unit.

    CONTRIBUTION_MARGIN formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CONTRIBUTION_MARGIN",
            category="costing",
            description="Calculate contribution margin (price - variable cost)",
            arguments=(
                FormulaArgument(
                    "selling_price",
                    "number",
                    required=True,
                    description="Selling price per unit",
                ),
                FormulaArgument(
                    "variable_cost",
                    "number",
                    required=True,
                    description="Variable cost per unit",
                ),
            ),
            return_type="number",
            examples=(
                "=CONTRIBUTION_MARGIN(100;60)",
                "=CONTRIBUTION_MARGIN(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CONTRIBUTION_MARGIN formula string."""
        self.validate_arguments(args)
        selling_price, variable_cost = args
        return f"of:={selling_price}-{variable_cost}"


@dataclass(slots=True, frozen=True)
class GrossProfitMarginFormula(BaseFormula):
    """Calculate gross profit margin percentage.

    GROSS_PROFIT_MARGIN formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="GROSS_PROFIT_MARGIN",
            category="costing",
            description="Calculate gross profit margin ((revenue - COGS) / revenue * 100)",
            arguments=(
                FormulaArgument(
                    "revenue",
                    "number",
                    required=True,
                    description="Total revenue",
                ),
                FormulaArgument(
                    "cogs",
                    "number",
                    required=True,
                    description="Cost of goods sold",
                ),
            ),
            return_type="number",
            examples=(
                "=GROSS_PROFIT_MARGIN(100000;60000)",
                "=GROSS_PROFIT_MARGIN(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GROSS_PROFIT_MARGIN formula string."""
        self.validate_arguments(args)
        revenue, cogs = args
        return f"of:=(({revenue}-{cogs})/{revenue})*100"


@dataclass(slots=True, frozen=True)
class StandardCostVarianceFormula(BaseFormula):
    """Calculate standard cost variance.

    STANDARD_COST_VARIANCE formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="STANDARD_COST_VARIANCE",
            category="costing",
            description="Calculate variance (actual cost - standard cost)",
            arguments=(
                FormulaArgument(
                    "actual_cost",
                    "number",
                    required=True,
                    description="Actual cost incurred",
                ),
                FormulaArgument(
                    "standard_cost",
                    "number",
                    required=True,
                    description="Standard (budgeted) cost",
                ),
            ),
            return_type="number",
            examples=(
                "=STANDARD_COST_VARIANCE(55000;50000)",
                "=STANDARD_COST_VARIANCE(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build STANDARD_COST_VARIANCE formula string."""
        self.validate_arguments(args)
        actual_cost, standard_cost = args
        return f"of:={actual_cost}-{standard_cost}"


@dataclass(slots=True, frozen=True)
class MaterialCostVarianceFormula(BaseFormula):
    """Calculate material cost variance.

    MATERIAL_COST_VARIANCE formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MATERIAL_COST_VARIANCE",
            category="costing",
            description="Calculate material variance ((actual qty - std qty) * std price)",
            arguments=(
                FormulaArgument(
                    "actual_quantity",
                    "number",
                    required=True,
                    description="Actual quantity used",
                ),
                FormulaArgument(
                    "standard_quantity",
                    "number",
                    required=True,
                    description="Standard quantity allowed",
                ),
                FormulaArgument(
                    "standard_price",
                    "number",
                    required=True,
                    description="Standard price per unit",
                ),
            ),
            return_type="number",
            examples=(
                "=MATERIAL_COST_VARIANCE(1100;1000;5)",
                "=MATERIAL_COST_VARIANCE(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MATERIAL_COST_VARIANCE formula string."""
        self.validate_arguments(args)
        actual_qty, standard_qty, standard_price = args
        return f"of:=({actual_qty}-{standard_qty})*{standard_price}"


@dataclass(slots=True, frozen=True)
class LaborEfficiencyVarianceFormula(BaseFormula):
    """Calculate labor efficiency variance.

    LABOR_EFFICIENCY_VARIANCE formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LABOR_EFFICIENCY_VARIANCE",
            category="costing",
            description="Calculate labor efficiency variance ((actual hrs - std hrs) * std rate)",
            arguments=(
                FormulaArgument(
                    "actual_hours",
                    "number",
                    required=True,
                    description="Actual labor hours",
                ),
                FormulaArgument(
                    "standard_hours",
                    "number",
                    required=True,
                    description="Standard hours allowed",
                ),
                FormulaArgument(
                    "standard_rate",
                    "number",
                    required=True,
                    description="Standard labor rate",
                ),
            ),
            return_type="number",
            examples=(
                "=LABOR_EFFICIENCY_VARIANCE(110;100;25)",
                "=LABOR_EFFICIENCY_VARIANCE(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LABOR_EFFICIENCY_VARIANCE formula string."""
        self.validate_arguments(args)
        actual_hours, standard_hours, standard_rate = args
        return f"of:=({actual_hours}-{standard_hours})*{standard_rate}"


@dataclass(slots=True, frozen=True)
class ActivityBasedCostFormula(BaseFormula):
    """Calculate activity-based cost.

    ACTIVITY_BASED_COST formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="ACTIVITY_BASED_COST",
            category="costing",
            description="Calculate ABC cost (cost driver rate * activity quantity)",
            arguments=(
                FormulaArgument(
                    "cost_driver_rate",
                    "number",
                    required=True,
                    description="Cost per activity unit",
                ),
                FormulaArgument(
                    "activity_quantity",
                    "number",
                    required=True,
                    description="Number of activity units consumed",
                ),
            ),
            return_type="number",
            examples=(
                "=ACTIVITY_BASED_COST(15;200)",
                "=ACTIVITY_BASED_COST(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ACTIVITY_BASED_COST formula string."""
        self.validate_arguments(args)
        cost_driver_rate, activity_quantity = args
        return f"of:={cost_driver_rate}*{activity_quantity}"


@dataclass(slots=True, frozen=True)
class MachineCostPerHourFormula(BaseFormula):
    """Calculate machine cost per hour.

    MACHINE_COST_PER_HOUR formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="MACHINE_COST_PER_HOUR",
            category="costing",
            description="Calculate machine cost per hour (total machine cost / operating hours)",
            arguments=(
                FormulaArgument(
                    "total_machine_cost",
                    "number",
                    required=True,
                    description="Total machine-related costs",
                ),
                FormulaArgument(
                    "operating_hours",
                    "number",
                    required=True,
                    description="Total operating hours",
                ),
            ),
            return_type="number",
            examples=(
                "=MACHINE_COST_PER_HOUR(80000;2000)",
                "=MACHINE_COST_PER_HOUR(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MACHINE_COST_PER_HOUR formula string."""
        self.validate_arguments(args)
        total_machine_cost, operating_hours = args
        return f"of:={total_machine_cost}/{operating_hours}"


@dataclass(slots=True, frozen=True)
class CostPerDefectFormula(BaseFormula):
    """Calculate cost per defect (cost of quality).

    COST_PER_DEFECT formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="COST_PER_DEFECT",
            category="costing",
            description="Calculate cost per defect (total defect cost / number of defects)",
            arguments=(
                FormulaArgument(
                    "total_defect_cost",
                    "number",
                    required=True,
                    description="Total cost of defects (rework, scrap, warranty)",
                ),
                FormulaArgument(
                    "number_of_defects",
                    "number",
                    required=True,
                    description="Number of defects",
                ),
            ),
            return_type="number",
            examples=(
                "=COST_PER_DEFECT(25000;50)",
                "=COST_PER_DEFECT(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build COST_PER_DEFECT formula string."""
        self.validate_arguments(args)
        total_defect_cost, number_of_defects = args
        return f"of:={total_defect_cost}/{number_of_defects}"


@dataclass(slots=True, frozen=True)
class ScrapRateCostFormula(BaseFormula):
    """Calculate scrap rate cost impact.

    SCRAP_RATE_COST formula
    BATCH-4.3: Manufacturing costing
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SCRAP_RATE_COST",
            category="costing",
            description="Calculate scrap cost (units scrapped * unit cost)",
            arguments=(
                FormulaArgument(
                    "units_scrapped",
                    "number",
                    required=True,
                    description="Number of units scrapped",
                ),
                FormulaArgument(
                    "unit_cost",
                    "number",
                    required=True,
                    description="Cost per unit",
                ),
            ),
            return_type="number",
            examples=(
                "=SCRAP_RATE_COST(50;75)",
                "=SCRAP_RATE_COST(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SCRAP_RATE_COST formula string."""
        self.validate_arguments(args)
        units_scrapped, unit_cost = args
        return f"of:={units_scrapped}*{unit_cost}"


__all__ = [
    "ActivityBasedCostFormula",
    "BreakEvenUnitsFormula",
    "ContributionMarginFormula",
    "CostPerDefectFormula",
    "DirectLaborCostFormula",
    "GrossProfitMarginFormula",
    "LaborEfficiencyVarianceFormula",
    "MachineCostPerHourFormula",
    "MaterialCostVarianceFormula",
    "OverheadRateFormula",
    "ScrapRateCostFormula",
    "StandardCostVarianceFormula",
    "UnitCostFormula",
]
