"""Tests for Manufacturing production formulas.

Comprehensive tests for production metrics formulas
including cycle time, takt time, throughput, and OEE.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing import (
    CapacityUtilizationFormula,
    CycleTimeFormula,
    ManufacturingDomainPlugin,
    TaktTimeFormula,
    ThroughputFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.production import (
    OverallEquipmentEffectiveness,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.manufacturing]


# ============================================================================
# Cycle Time Formula Tests
# ============================================================================


class TestCycleTimeCalculations:
    """Test cycle time calculations."""

    def test_cycle_time_standard(self) -> None:
        """Test standard cycle time calculation."""
        formula = CycleTimeFormula()
        result = formula.build("480", "120")  # 480 min / 120 units
        assert result == "of:=480/120"

    def test_cycle_time_high_volume(self) -> None:
        """Test cycle time with high production volume."""
        formula = CycleTimeFormula()
        result = formula.build("480", "1000")
        assert result == "of:=480/1000"

    def test_cycle_time_low_volume(self) -> None:
        """Test cycle time with low production volume."""
        formula = CycleTimeFormula()
        result = formula.build("480", "10")
        assert result == "of:=480/10"

    def test_cycle_time_cell_references(self) -> None:
        """Test cycle time with cell references."""
        formula = CycleTimeFormula()
        result = formula.build("A2", "B2")
        assert result == "of:=A2/B2"

    def test_cycle_time_metadata(self) -> None:
        """Test cycle time formula metadata."""
        formula = CycleTimeFormula()
        metadata = formula.metadata

        assert metadata.name == "CYCLE_TIME"
        assert metadata.category == "production"
        assert len(metadata.arguments) == 2


# ============================================================================
# Takt Time Formula Tests
# ============================================================================


class TestTaktTimeCalculations:
    """Test takt time calculations."""

    def test_takt_time_standard(self) -> None:
        """Test standard takt time calculation."""
        formula = TaktTimeFormula()
        result = formula.build("28800", "1200")  # 8 hours in seconds / demand
        assert result == "of:=28800/1200"

    def test_takt_time_high_demand(self) -> None:
        """Test takt time with high customer demand."""
        formula = TaktTimeFormula()
        result = formula.build("28800", "5000")
        assert result == "of:=28800/5000"

    def test_takt_time_low_demand(self) -> None:
        """Test takt time with low customer demand."""
        formula = TaktTimeFormula()
        result = formula.build("28800", "100")
        assert result == "of:=28800/100"

    def test_takt_time_cell_references(self) -> None:
        """Test takt time with cell references."""
        formula = TaktTimeFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"

    def test_takt_time_metadata(self) -> None:
        """Test takt time formula metadata."""
        formula = TaktTimeFormula()
        metadata = formula.metadata

        assert metadata.name == "TAKT_TIME"
        assert metadata.category == "production"
        assert len(metadata.arguments) == 2


# ============================================================================
# Throughput Formula Tests
# ============================================================================


class TestThroughputCalculations:
    """Test throughput calculations."""

    def test_throughput_standard(self) -> None:
        """Test standard throughput calculation."""
        formula = ThroughputFormula()
        result = formula.build("1200", "480")  # 1200 units / 480 min
        assert result == "of:=1200/480"

    def test_throughput_high_rate(self) -> None:
        """Test throughput at high production rate."""
        formula = ThroughputFormula()
        result = formula.build("5000", "480")
        assert result == "of:=5000/480"

    def test_throughput_low_rate(self) -> None:
        """Test throughput at low production rate."""
        formula = ThroughputFormula()
        result = formula.build("100", "480")
        assert result == "of:=100/480"

    def test_throughput_cell_references(self) -> None:
        """Test throughput with cell references."""
        formula = ThroughputFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"

    def test_throughput_metadata(self) -> None:
        """Test throughput formula metadata."""
        formula = ThroughputFormula()
        metadata = formula.metadata

        assert metadata.name == "THROUGHPUT"
        assert metadata.category == "production"


# ============================================================================
# Capacity Utilization Formula Tests
# ============================================================================


class TestCapacityUtilizationCalculations:
    """Test capacity utilization calculations."""

    def test_capacity_utilization_standard(self) -> None:
        """Test standard capacity utilization calculation."""
        formula = CapacityUtilizationFormula()
        result = formula.build("850", "1000")  # 85% utilization
        assert result == "of:=(850/1000)*100"

    def test_capacity_utilization_full(self) -> None:
        """Test capacity utilization at full capacity."""
        formula = CapacityUtilizationFormula()
        result = formula.build("1000", "1000")
        assert result == "of:=(1000/1000)*100"

    def test_capacity_utilization_low(self) -> None:
        """Test capacity utilization at low utilization."""
        formula = CapacityUtilizationFormula()
        result = formula.build("500", "1000")
        assert result == "of:=(500/1000)*100"

    def test_capacity_utilization_cell_references(self) -> None:
        """Test capacity utilization with cell references."""
        formula = CapacityUtilizationFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=(A1/B1)*100"

    def test_capacity_utilization_metadata(self) -> None:
        """Test capacity utilization formula metadata."""
        formula = CapacityUtilizationFormula()
        metadata = formula.metadata

        assert metadata.name == "CAPACITY_UTILIZATION"
        assert metadata.category == "production"


# ============================================================================
# OEE Formula Tests
# ============================================================================


class TestOEECalculations:
    """Test Overall Equipment Effectiveness calculations."""

    def test_oee_standard(self) -> None:
        """Test standard OEE calculation."""
        formula = OverallEquipmentEffectiveness()
        result = formula.build("0.90", "0.95", "0.99")  # A, P, Q
        assert result == "of:=0.90*0.95*0.99*100"

    def test_oee_perfect(self) -> None:
        """Test OEE at perfect performance."""
        formula = OverallEquipmentEffectiveness()
        result = formula.build("1.0", "1.0", "1.0")
        assert result == "of:=1.0*1.0*1.0*100"

    def test_oee_low_availability(self) -> None:
        """Test OEE with low availability."""
        formula = OverallEquipmentEffectiveness()
        result = formula.build("0.70", "0.95", "0.99")
        assert "0.70" in result

    def test_oee_low_quality(self) -> None:
        """Test OEE with low quality rate."""
        formula = OverallEquipmentEffectiveness()
        result = formula.build("0.90", "0.95", "0.80")
        assert "0.80" in result

    def test_oee_cell_references(self) -> None:
        """Test OEE with cell references."""
        formula = OverallEquipmentEffectiveness()
        result = formula.build("A1", "A2", "A3")
        assert result == "of:=A1*A2*A3*100"

    def test_oee_metadata(self) -> None:
        """Test OEE formula metadata."""
        formula = OverallEquipmentEffectiveness()
        metadata = formula.metadata

        assert metadata.name == "OEE"
        assert metadata.category == "production"
        assert len(metadata.arguments) == 3


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestProductionEdgeCases:
    """Test edge cases in production formulas."""

    def test_cycle_time_validates_arguments(self) -> None:
        """Test cycle time argument validation."""
        formula = CycleTimeFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("480")

    def test_cycle_time_too_many_arguments(self) -> None:
        """Test cycle time with too many arguments."""
        formula = CycleTimeFormula()
        with pytest.raises(ValueError, match="accepts at most"):
            formula.build("480", "120", "extra")

    def test_takt_time_validates_arguments(self) -> None:
        """Test takt time argument validation."""
        formula = TaktTimeFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("28800")

    def test_oee_validates_arguments(self) -> None:
        """Test OEE argument validation."""
        formula = OverallEquipmentEffectiveness()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("0.90", "0.95")


# ============================================================================
# Integration Tests
# ============================================================================


class TestProductionIntegration:
    """Integration tests for production formulas with plugin."""

    def test_plugin_contains_production_formulas(self) -> None:
        """Test plugin has production formulas."""
        plugin = ManufacturingDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("CYCLE_TIME") is not None
        assert plugin.get_formula("TAKT_TIME") is not None
        assert plugin.get_formula("THROUGHPUT") is not None
        assert plugin.get_formula("CAPACITY_UTILIZATION") is not None

    def test_all_production_formulas_have_metadata(self) -> None:
        """Test all production formulas have complete metadata."""
        formula_instances = [
            CycleTimeFormula(),
            TaktTimeFormula(),
            ThroughputFormula(),
            CapacityUtilizationFormula(),
            OverallEquipmentEffectiveness(),
        ]

        for formula in formula_instances:
            metadata = formula.metadata

            assert metadata.name, f"{type(formula).__name__} missing name"
            assert metadata.category, f"{type(formula).__name__} missing category"
            assert metadata.description, f"{type(formula).__name__} missing desc"
            assert len(metadata.arguments) > 0, f"{type(formula).__name__} missing args"
            assert len(metadata.examples) > 0, (
                f"{type(formula).__name__} missing examples"
            )

    def test_production_formula_examples_are_valid(self) -> None:
        """Test production formula examples are valid ODF syntax."""
        formula_instances = [
            CycleTimeFormula(),
            TaktTimeFormula(),
            ThroughputFormula(),
            CapacityUtilizationFormula(),
        ]

        for formula in formula_instances:
            for example in formula.metadata.examples:
                # Examples should start with = (spreadsheet formula)
                assert example.startswith("="), (
                    f"{formula.metadata.name} example should start with ="
                )
