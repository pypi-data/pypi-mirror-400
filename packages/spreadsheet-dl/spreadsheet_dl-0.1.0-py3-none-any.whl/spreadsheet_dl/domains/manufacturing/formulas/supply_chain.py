"""Supply chain formulas for manufacturing.

Supply chain formulas (5 total)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class BullwhipEffectFormula(BaseFormula):
    """Bullwhip effect (demand amplification ratio) calculation.

        BULLWHIP_EFFECT formula for supply chain

    Bullwhip Ratio = Variance of Orders / Variance of Demand

    Example:
        >>> formula = BullwhipEffectFormula()
        >>> result = formula.build(400, 100)
        >>> # Returns: "400/100" (4.0 ratio)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BULLWHIP_EFFECT

            Formula metadata
        """
        return FormulaMetadata(
            name="BULLWHIP_EFFECT",
            category="supply_chain",
            description="Calculate bullwhip effect (demand amplification ratio)",
            arguments=(
                FormulaArgument(
                    "order_variance",
                    "number",
                    required=True,
                    description="Variance of orders placed or cell reference",
                ),
                FormulaArgument(
                    "demand_variance",
                    "number",
                    required=True,
                    description="Variance of customer demand or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=BULLWHIP_EFFECT(A1;B1)",
                "=400/100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BULLWHIP_EFFECT formula string.

        Args:
            *args: order_variance, demand_variance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            BULLWHIP_EFFECT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        order_variance, demand_variance = args

        # Formula: Variance of Orders / Variance of Demand
        return f"of:={order_variance}/{demand_variance}"


@dataclass(slots=True, frozen=True)
class NewsvendorModelFormula(BaseFormula):
    """Newsvendor model optimal order quantity under uncertainty.

        NEWSVENDOR_QUANTITY formula for supply chain

    Critical Ratio = (Price - Cost) / (Price - Salvage Value)
    Optimal Q corresponds to this service level

    Example:
        >>> formula = NewsvendorModelFormula()
        >>> result = formula.build(10, 6, 2)
        >>> # Returns: "(10-6)/(10-2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for NEWSVENDOR_QUANTITY

            Formula metadata
        """
        return FormulaMetadata(
            name="NEWSVENDOR_QUANTITY",
            category="supply_chain",
            description="Calculate newsvendor critical ratio (optimal order quantity under uncertainty)",
            arguments=(
                FormulaArgument(
                    "selling_price",
                    "number",
                    required=True,
                    description="Selling price per unit or cell reference",
                ),
                FormulaArgument(
                    "cost",
                    "number",
                    required=True,
                    description="Cost per unit or cell reference",
                ),
                FormulaArgument(
                    "salvage_value",
                    "number",
                    required=True,
                    description="Salvage value per unit or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=NEWSVENDOR_QUANTITY(A1;B1;C1)",
                "=(10-6)/(10-2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build NEWSVENDOR_QUANTITY formula string.

        Args:
            *args: selling_price, cost, salvage_value
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string (critical ratio)

            NEWSVENDOR_QUANTITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        selling_price, cost, salvage_value = args

        # Formula: Critical Ratio = (Price - Cost) / (Price - Salvage Value)
        return f"of:=({selling_price}-{cost})/({selling_price}-{salvage_value})"


@dataclass(slots=True, frozen=True)
class ABCAnalysisFormula(BaseFormula):
    """ABC analysis inventory classification score.

        ABC_SCORE formula for supply chain

    ABC Score = (Item Value / Total Value) * 100

    Example:
        >>> formula = ABCAnalysisFormula()
        >>> result = formula.build(50000, 200000)
        >>> # Returns: "(50000/200000)*100" (25%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ABC_SCORE

            Formula metadata
        """
        return FormulaMetadata(
            name="ABC_SCORE",
            category="supply_chain",
            description="Calculate ABC analysis classification score (item value / total value * 100)",
            arguments=(
                FormulaArgument(
                    "item_value",
                    "number",
                    required=True,
                    description="Annual item value (usage * cost) or cell reference",
                ),
                FormulaArgument(
                    "total_value",
                    "number",
                    required=True,
                    description="Total inventory value or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=ABC_SCORE(A1;B1)",
                "=(50000/200000)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ABC_SCORE formula string.

        Args:
            *args: item_value, total_value
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ABC_SCORE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        item_value, total_value = args

        # Formula: (Item Value / Total Value) * 100
        return f"of:=({item_value}/{total_value})*100"


@dataclass(slots=True, frozen=True)
class ServiceLevelFormula(BaseFormula):
    """Service level (fill rate) calculation.

        SERVICE_LEVEL formula for supply chain

    Service Level = (Orders Fulfilled / Total Orders) * 100

    Example:
        >>> formula = ServiceLevelFormula()
        >>> result = formula.build(950, 1000)
        >>> # Returns: "(950/1000)*100" (95%)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SERVICE_LEVEL

            Formula metadata
        """
        return FormulaMetadata(
            name="SERVICE_LEVEL",
            category="supply_chain",
            description="Calculate service level / fill rate percentage",
            arguments=(
                FormulaArgument(
                    "orders_fulfilled",
                    "number",
                    required=True,
                    description="Number of orders fulfilled or cell reference",
                ),
                FormulaArgument(
                    "total_orders",
                    "number",
                    required=True,
                    description="Total number of orders or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=SERVICE_LEVEL(A1;B1)",
                "=(950/1000)*100",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SERVICE_LEVEL formula string.

        Args:
            *args: orders_fulfilled, total_orders
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SERVICE_LEVEL formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        orders_fulfilled, total_orders = args

        # Formula: (Orders Fulfilled / Total Orders) * 100
        return f"of:=({orders_fulfilled}/{total_orders})*100"


@dataclass(slots=True, frozen=True)
class CashConversionCycleFormula(BaseFormula):
    """Cash Conversion Cycle calculation.

        CASH_CONVERSION_CYCLE formula for supply chain

    CCC = Days Inventory Outstanding + Days Sales Outstanding - Days Payable Outstanding

    Example:
        >>> formula = CashConversionCycleFormula()
        >>> result = formula.build(45, 30, 35)
        >>> # Returns: "45+30-35" (40 days)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CASH_CONVERSION_CYCLE

            Formula metadata
        """
        return FormulaMetadata(
            name="CASH_CONVERSION_CYCLE",
            category="supply_chain",
            description="Calculate cash conversion cycle (DIO + DSO - DPO)",
            arguments=(
                FormulaArgument(
                    "dio",
                    "number",
                    required=True,
                    description="Days Inventory Outstanding or cell reference",
                ),
                FormulaArgument(
                    "dso",
                    "number",
                    required=True,
                    description="Days Sales Outstanding or cell reference",
                ),
                FormulaArgument(
                    "dpo",
                    "number",
                    required=True,
                    description="Days Payable Outstanding or cell reference",
                ),
            ),
            return_type="number",
            examples=(
                "=CASH_CONVERSION_CYCLE(A1;B1;C1)",
                "=45+30-35",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CASH_CONVERSION_CYCLE formula string.

        Args:
            *args: dio, dso, dpo
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CASH_CONVERSION_CYCLE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        dio, dso, dpo = args

        # Formula: DIO + DSO - DPO
        return f"of:={dio}+{dso}-{dpo}"


__all__ = [
    "ABCAnalysisFormula",
    "BullwhipEffectFormula",
    "CashConversionCycleFormula",
    "NewsvendorModelFormula",
    "ServiceLevelFormula",
]
