"""Tests for Manufacturing inventory formulas.

Comprehensive tests for inventory management formulas
including EOQ, reorder point, safety stock, and turnover.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing import (
    EOQFormula,
    InventoryTurnoverFormula,
    ManufacturingDomainPlugin,
    ReorderPointFormula,
    SafetyStockFormula,
)
from spreadsheet_dl.domains.manufacturing.utils import (
    calculate_eoq,
    calculate_reorder_point,
    calculate_safety_stock,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.manufacturing]


# ============================================================================
# EOQ Formula Tests
# ============================================================================


class TestEOQCalculations:
    """Test Economic Order Quantity calculations."""

    def test_eoq_standard(self) -> None:
        """Test standard EOQ calculation."""
        formula = EOQFormula()
        result = formula.build("1000", "50", "2")  # D=1000, S=50, H=2
        assert result == "of:=SQRT((2*1000*50)/2)"

    def test_eoq_high_demand(self) -> None:
        """Test EOQ with high annual demand."""
        formula = EOQFormula()
        result = formula.build("10000", "100", "5")
        assert "SQRT" in result
        assert "10000" in result

    def test_eoq_high_holding_cost(self) -> None:
        """Test EOQ with high holding cost."""
        formula = EOQFormula()
        result = formula.build("5000", "50", "20")
        assert "20" in result

    def test_eoq_low_order_cost(self) -> None:
        """Test EOQ with low ordering cost."""
        formula = EOQFormula()
        result = formula.build("5000", "10", "5")
        assert "10" in result

    def test_eoq_cell_references(self) -> None:
        """Test EOQ with cell references."""
        formula = EOQFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result
        assert "SQRT" in result

    def test_eoq_metadata(self) -> None:
        """Test EOQ formula metadata."""
        formula = EOQFormula()
        metadata = formula.metadata

        assert metadata.name == "EOQ"
        assert metadata.category == "inventory"
        assert len(metadata.arguments) == 3


# ============================================================================
# Reorder Point Formula Tests
# ============================================================================


class TestReorderPointCalculations:
    """Test reorder point calculations."""

    def test_reorder_point_standard(self) -> None:
        """Test standard reorder point calculation."""
        formula = ReorderPointFormula()
        result = formula.build("100", "7", "50")  # demand=100/day, LT=7, SS=50
        assert result == "of:=(100*7)+50"

    def test_reorder_point_high_demand(self) -> None:
        """Test reorder point with high daily demand."""
        formula = ReorderPointFormula()
        result = formula.build("500", "5", "100")
        assert "500" in result

    def test_reorder_point_long_lead_time(self) -> None:
        """Test reorder point with long lead time."""
        formula = ReorderPointFormula()
        result = formula.build("50", "30", "200")
        assert "30" in result

    def test_reorder_point_no_safety_stock(self) -> None:
        """Test reorder point without safety stock."""
        formula = ReorderPointFormula()
        result = formula.build("100", "7", "0")
        assert result == "of:=(100*7)+0"

    def test_reorder_point_cell_references(self) -> None:
        """Test reorder point with cell references."""
        formula = ReorderPointFormula()
        result = formula.build("D1", "E1", "F1")
        assert result == "of:=(D1*E1)+F1"

    def test_reorder_point_metadata(self) -> None:
        """Test reorder point formula metadata."""
        formula = ReorderPointFormula()
        metadata = formula.metadata

        assert metadata.name == "REORDER_POINT"
        assert metadata.category == "inventory"
        assert len(metadata.arguments) == 3


# ============================================================================
# Safety Stock Formula Tests
# ============================================================================


class TestSafetyStockCalculations:
    """Test safety stock calculations."""

    def test_safety_stock_standard(self) -> None:
        """Test standard safety stock calculation."""
        formula = SafetyStockFormula()
        result = formula.build("1.65", "10", "7")  # Z=1.65 (95%), sigma=10, LT=7
        assert result == "of:=1.65*10*SQRT(7)"

    def test_safety_stock_high_service_level(self) -> None:
        """Test safety stock for high service level (99%)."""
        formula = SafetyStockFormula()
        result = formula.build("2.33", "15", "5")  # Z=2.33 for 99%
        assert "2.33" in result

    def test_safety_stock_high_variability(self) -> None:
        """Test safety stock with high demand variability."""
        formula = SafetyStockFormula()
        result = formula.build("1.65", "50", "7")
        assert "50" in result

    def test_safety_stock_short_lead_time(self) -> None:
        """Test safety stock with short lead time."""
        formula = SafetyStockFormula()
        result = formula.build("1.65", "10", "1")
        assert "SQRT(1)" in result

    def test_safety_stock_cell_references(self) -> None:
        """Test safety stock with cell references."""
        formula = SafetyStockFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=A1*B1*SQRT(C1)"

    def test_safety_stock_metadata(self) -> None:
        """Test safety stock formula metadata."""
        formula = SafetyStockFormula()
        metadata = formula.metadata

        assert metadata.name == "SAFETY_STOCK"
        assert metadata.category == "inventory"
        assert len(metadata.arguments) == 3


# ============================================================================
# Inventory Turnover Formula Tests
# ============================================================================


class TestInventoryTurnoverCalculations:
    """Test inventory turnover calculations."""

    def test_inventory_turnover_standard(self) -> None:
        """Test standard inventory turnover calculation."""
        formula = InventoryTurnoverFormula()
        result = formula.build("1000000", "100000")  # COGS/Avg Inventory
        assert result == "of:=1000000/100000"

    def test_inventory_turnover_high(self) -> None:
        """Test high inventory turnover (fast-moving goods)."""
        formula = InventoryTurnoverFormula()
        result = formula.build("5000000", "250000")  # 20x turnover
        assert result == "of:=5000000/250000"

    def test_inventory_turnover_low(self) -> None:
        """Test low inventory turnover (slow-moving goods)."""
        formula = InventoryTurnoverFormula()
        result = formula.build("500000", "500000")  # 1x turnover
        assert result == "of:=500000/500000"

    def test_inventory_turnover_cell_references(self) -> None:
        """Test inventory turnover with cell references."""
        formula = InventoryTurnoverFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"

    def test_inventory_turnover_metadata(self) -> None:
        """Test inventory turnover formula metadata."""
        formula = InventoryTurnoverFormula()
        metadata = formula.metadata

        assert metadata.name == "INVENTORY_TURNOVER"
        assert metadata.category == "inventory"
        assert len(metadata.arguments) == 2


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestInventoryUtilityFunctions:
    """Test inventory utility functions."""

    def test_calculate_eoq_standard(self) -> None:
        """Test EOQ utility function."""
        eoq = calculate_eoq(annual_demand=1000, order_cost=50, holding_cost=2)
        # EOQ = sqrt((2*1000*50)/2) = sqrt(50000) = ~223.6
        assert 220 < eoq < 230

    def test_calculate_eoq_high_demand(self) -> None:
        """Test EOQ utility with high demand."""
        eoq = calculate_eoq(annual_demand=10000, order_cost=100, holding_cost=5)
        assert eoq > 0

    def test_calculate_reorder_point_standard(self) -> None:
        """Test reorder point utility function."""
        rop = calculate_reorder_point(100, 7, 50)  # demand, lead_time, safety
        assert rop == 100 * 7 + 50  # 750

    def test_calculate_reorder_point_no_safety(self) -> None:
        """Test reorder point without safety stock."""
        rop = calculate_reorder_point(50, 10, 0)
        assert rop == 500

    def test_calculate_safety_stock_standard(self) -> None:
        """Test safety stock utility function."""
        ss = calculate_safety_stock(1.65, 10, 7)
        assert ss > 0

    def test_calculate_safety_stock_high_z(self) -> None:
        """Test safety stock with high Z-score."""
        ss = calculate_safety_stock(2.33, 10, 7)
        ss_low = calculate_safety_stock(1.65, 10, 7)
        assert ss > ss_low


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestInventoryEdgeCases:
    """Test edge cases in inventory formulas."""

    def test_eoq_validates_arguments(self) -> None:
        """Test EOQ argument validation."""
        formula = EOQFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1000", "50")

    def test_reorder_point_validates_arguments(self) -> None:
        """Test reorder point argument validation."""
        formula = ReorderPointFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("100", "7")

    def test_safety_stock_validates_arguments(self) -> None:
        """Test safety stock argument validation."""
        formula = SafetyStockFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1.65", "10")

    def test_inventory_turnover_validates_arguments(self) -> None:
        """Test inventory turnover argument validation."""
        formula = InventoryTurnoverFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1000000")


# ============================================================================
# Integration Tests
# ============================================================================


class TestInventoryIntegration:
    """Integration tests for inventory formulas with plugin."""

    def test_plugin_contains_inventory_formulas(self) -> None:
        """Test plugin has inventory formulas."""
        plugin = ManufacturingDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("EOQ") is not None
        assert plugin.get_formula("REORDER_POINT") is not None
        assert plugin.get_formula("SAFETY_STOCK") is not None
        assert plugin.get_formula("INVENTORY_TURNOVER") is not None

    def test_all_inventory_formulas_have_examples(self) -> None:
        """Test all inventory formulas have usage examples."""
        formula_instances = [
            EOQFormula(),
            ReorderPointFormula(),
            SafetyStockFormula(),
            InventoryTurnoverFormula(),
        ]

        for formula in formula_instances:
            metadata = formula.metadata
            assert len(metadata.examples) > 0, f"{metadata.name} should have examples"

    def test_inventory_formulas_with_realistic_values(self) -> None:
        """Test inventory formulas with realistic business values."""
        # Realistic scenario: Electronics retailer
        eoq = EOQFormula()
        rop = ReorderPointFormula()
        ss = SafetyStockFormula()
        turnover = InventoryTurnoverFormula()

        # EOQ: 10,000 annual demand, $25 order cost, $5 holding cost
        eoq_result = eoq.build("10000", "25", "5")
        assert "SQRT" in eoq_result

        # ROP: 30 units/day demand, 14-day lead time, 100 safety stock
        rop_result = rop.build("30", "14", "100")
        assert rop_result == "of:=(30*14)+100"

        # Safety stock: 95% service, 15 unit std dev, 14-day lead time
        ss_result = ss.build("1.65", "15", "14")
        assert "SQRT(14)" in ss_result

        # Turnover: $2M COGS, $200K avg inventory
        turnover_result = turnover.build("2000000", "200000")
        assert turnover_result == "of:=2000000/200000"
