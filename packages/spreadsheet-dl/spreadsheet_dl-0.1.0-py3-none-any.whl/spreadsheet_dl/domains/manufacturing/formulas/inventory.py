"""Inventory metrics formulas for manufacturing.

Inventory metrics formulas (EOQ, REORDER_POINT, SAFETY_STOCK, INVENTORY_TURNOVER)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class EOQFormula(BaseFormula):
    """Economic Order Quantity calculation.

        EOQ formula for inventory optimization

    EOQ = SQRT((2 * Demand * Order Cost) / Holding Cost)

    Example:
        >>> formula = EOQFormula()
        >>> result = formula.build(10000, 50, 5)
        >>> # Returns: "SQRT((2*10000*50)/5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for EOQ

            Formula metadata
        """
        return FormulaMetadata(
            name="EOQ",
            category="inventory",
            description="Calculate Economic Order Quantity",
            arguments=(
                FormulaArgument(
                    "annual_demand",
                    "number",
                    required=True,
                    description="Annual demand in units or cell reference",
                ),
                FormulaArgument(
                    "order_cost",
                    "number",
                    required=True,
                    description="Cost per order or cell reference",
                ),
                FormulaArgument(
                    "holding_cost",
                    "number",
                    required=True,
                    description="Annual holding cost per unit or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=EOQ(A1;B1;C1)",
                "=SQRT((2*10000*50)/5)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build EOQ formula string.

        Args:
            *args: annual_demand, order_cost, holding_cost
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            EOQ formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        annual_demand, order_cost, holding_cost = args

        # Formula: SQRT((2 * D * S) / H)
        return f"of:=SQRT((2*{annual_demand}*{order_cost})/{holding_cost})"


@dataclass(slots=True, frozen=True)
class ReorderPointFormula(BaseFormula):
    """Reorder point calculation.

        REORDER_POINT formula for inventory management

    Reorder Point = (Demand Rate * Lead Time) + Safety Stock

    Example:
        >>> formula = ReorderPointFormula()
        >>> result = formula.build(50, 7, 100)
        >>> # Returns: "(50*7)+100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for REORDER_POINT

            Formula metadata
        """
        return FormulaMetadata(
            name="REORDER_POINT",
            category="inventory",
            description="Calculate inventory reorder point",
            arguments=(
                FormulaArgument(
                    "demand_rate",
                    "number",
                    required=True,
                    description="Average daily demand or cell reference",
                ),
                FormulaArgument(
                    "lead_time",
                    "number",
                    required=True,
                    description="Lead time in days or cell reference",
                ),
                FormulaArgument(
                    "safety_stock",
                    "number",
                    required=True,
                    description="Safety stock quantity or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=REORDER_POINT(A1;B1;C1)",
                "=(50*7)+100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build REORDER_POINT formula string.

        Args:
            *args: demand_rate, lead_time, safety_stock
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            REORDER_POINT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        demand_rate, lead_time, safety_stock = args

        # Formula: (Demand * Lead Time) + Safety Stock
        return f"of:=({demand_rate}*{lead_time})+{safety_stock}"


@dataclass(slots=True, frozen=True)
class SafetyStockFormula(BaseFormula):
    """Safety stock calculation.

        SAFETY_STOCK formula for inventory management

    Safety Stock = Z-Score * StdDev * SQRT(Lead Time)

    Example:
        >>> formula = SafetyStockFormula()
        >>> result = formula.build(1.65, 15, 7)
        >>> # Returns: "1.65*15*SQRT(7)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SAFETY_STOCK

            Formula metadata
        """
        return FormulaMetadata(
            name="SAFETY_STOCK",
            category="inventory",
            description="Calculate safety stock quantity",
            arguments=(
                FormulaArgument(
                    "z_score",
                    "number",
                    required=True,
                    description="Z-score for service level (e.g., 1.65 for 95%) or cell reference",
                ),
                FormulaArgument(
                    "demand_stddev",
                    "number",
                    required=True,
                    description="Standard deviation of demand or cell reference",
                ),
                FormulaArgument(
                    "lead_time",
                    "number",
                    required=True,
                    description="Lead time in days or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=SAFETY_STOCK(A1;B1;C1)",
                "=1.65*15*SQRT(7)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SAFETY_STOCK formula string.

        Args:
            *args: z_score, demand_stddev, lead_time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SAFETY_STOCK formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        z_score, demand_stddev, lead_time = args

        # Formula: Z * sigma * SQRT(LT)
        return f"of:={z_score}*{demand_stddev}*SQRT({lead_time})"


@dataclass(slots=True, frozen=True)
class InventoryTurnoverFormula(BaseFormula):
    """Inventory turnover ratio.

        INVENTORY_TURNOVER formula for inventory analysis

    Inventory Turnover = Cost of Goods Sold / Average Inventory

    Example:
        >>> formula = InventoryTurnoverFormula()
        >>> result = formula.build(1200000, 200000)
        >>> # Returns: "1200000/200000"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for INVENTORY_TURNOVER

            Formula metadata
        """
        return FormulaMetadata(
            name="INVENTORY_TURNOVER",
            category="inventory",
            description="Calculate inventory turnover ratio",
            arguments=(
                FormulaArgument(
                    "cogs",
                    "number",
                    required=True,
                    description="Cost of goods sold or cell reference",
                ),
                FormulaArgument(
                    "avg_inventory",
                    "number",
                    required=True,
                    description="Average inventory value or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=INVENTORY_TURNOVER(A1;B1)",
                "=1200000/200000",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build INVENTORY_TURNOVER formula string.

        Args:
            *args: cogs, avg_inventory
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            INVENTORY_TURNOVER formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        cogs, avg_inventory = args

        # Formula: COGS / Average Inventory
        return f"of:={cogs}/{avg_inventory}"


__all__ = [
    "EOQFormula",
    "InventoryTurnoverFormula",
    "ReorderPointFormula",
    "SafetyStockFormula",
]
