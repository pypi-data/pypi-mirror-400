"""Tests for Manufacturing quality formulas.

Comprehensive tests for quality metrics formulas
including defect rate, yield, process capability, and control limits.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing import (
    ControlLimitsFormula,
    DefectRateFormula,
    FirstPassYieldFormula,
    ManufacturingDomainPlugin,
    ProcessCapabilityFormula,
)
from spreadsheet_dl.domains.manufacturing.utils import (
    calculate_defect_rate,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.manufacturing]


# ============================================================================
# Defect Rate Formula Tests
# ============================================================================


class TestDefectRateCalculations:
    """Test defect rate calculations."""

    def test_defect_rate_standard(self) -> None:
        """Test standard defect rate calculation."""
        formula = DefectRateFormula()
        result = formula.build("25", "1000")  # 25 defects in 1000 units
        assert result == "of:=(25/1000)*100"

    def test_defect_rate_low(self) -> None:
        """Test low defect rate (high quality)."""
        formula = DefectRateFormula()
        result = formula.build("5", "10000")
        assert result == "of:=(5/10000)*100"

    def test_defect_rate_high(self) -> None:
        """Test high defect rate (poor quality)."""
        formula = DefectRateFormula()
        result = formula.build("500", "1000")
        assert result == "of:=(500/1000)*100"

    def test_defect_rate_zero(self) -> None:
        """Test zero defect rate (perfect quality)."""
        formula = DefectRateFormula()
        result = formula.build("0", "1000")
        assert result == "of:=(0/1000)*100"

    def test_defect_rate_cell_references(self) -> None:
        """Test defect rate with cell references."""
        formula = DefectRateFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=(A1/B1)*100"

    def test_defect_rate_metadata(self) -> None:
        """Test defect rate formula metadata."""
        formula = DefectRateFormula()
        metadata = formula.metadata

        assert metadata.name == "DEFECT_RATE"
        assert metadata.category == "quality"
        assert len(metadata.arguments) == 2


# ============================================================================
# First Pass Yield Formula Tests
# ============================================================================


class TestFirstPassYieldCalculations:
    """Test first pass yield calculations."""

    def test_first_pass_yield_standard(self) -> None:
        """Test standard first pass yield calculation."""
        formula = FirstPassYieldFormula()
        result = formula.build("950", "1000")  # 95% FPY
        assert result == "of:=(950/1000)*100"

    def test_first_pass_yield_high(self) -> None:
        """Test high first pass yield (excellent quality)."""
        formula = FirstPassYieldFormula()
        result = formula.build("9950", "10000")  # 99.5% FPY
        assert result == "of:=(9950/10000)*100"

    def test_first_pass_yield_low(self) -> None:
        """Test low first pass yield (needs improvement)."""
        formula = FirstPassYieldFormula()
        result = formula.build("800", "1000")  # 80% FPY
        assert result == "of:=(800/1000)*100"

    def test_first_pass_yield_perfect(self) -> None:
        """Test perfect first pass yield."""
        formula = FirstPassYieldFormula()
        result = formula.build("1000", "1000")  # 100% FPY
        assert result == "of:=(1000/1000)*100"

    def test_first_pass_yield_cell_references(self) -> None:
        """Test first pass yield with cell references."""
        formula = FirstPassYieldFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=(A1/B1)*100"

    def test_first_pass_yield_metadata(self) -> None:
        """Test first pass yield formula metadata."""
        formula = FirstPassYieldFormula()
        metadata = formula.metadata

        assert metadata.name == "FIRST_PASS_YIELD"
        assert metadata.category == "quality"
        assert len(metadata.arguments) == 2


# ============================================================================
# Process Capability Formula Tests
# ============================================================================


class TestProcessCapabilityCalculations:
    """Test process capability (Cp) calculations."""

    def test_process_capability_standard(self) -> None:
        """Test standard process capability calculation."""
        formula = ProcessCapabilityFormula()
        result = formula.build("10", "0", "5", "0.5")  # USL=10, LSL=0, mean=5, std=0.5
        assert result == "of:=(10-0)/(6*0.5)"

    def test_process_capability_high_cp(self) -> None:
        """Test high Cp (very capable process)."""
        formula = ProcessCapabilityFormula()
        result = formula.build("100", "80", "90", "1")  # Wide spec, low variation
        assert result == "of:=(100-80)/(6*1)"

    def test_process_capability_low_cp(self) -> None:
        """Test low Cp (needs improvement)."""
        formula = ProcessCapabilityFormula()
        result = formula.build("10", "8", "9", "0.5")  # Narrow spec, higher variation
        assert result == "of:=(10-8)/(6*0.5)"

    def test_process_capability_cell_references(self) -> None:
        """Test process capability with cell references."""
        formula = ProcessCapabilityFormula()
        result = formula.build("A1", "B1", "C1", "D1")
        assert result == "of:=(A1-B1)/(6*D1)"

    def test_process_capability_metadata(self) -> None:
        """Test process capability formula metadata."""
        formula = ProcessCapabilityFormula()
        metadata = formula.metadata

        assert metadata.name == "PROCESS_CAPABILITY"
        assert metadata.category == "quality"
        assert len(metadata.arguments) == 4


# ============================================================================
# Control Limits Formula Tests
# ============================================================================


class TestControlLimitsCalculations:
    """Test control limits (UCL/LCL) calculations."""

    def test_control_limits_upper(self) -> None:
        """Test upper control limit calculation."""
        formula = ControlLimitsFormula()
        result = formula.build("100", "5", "upper")  # mean=100, std=5, UCL
        assert result == "of:=100+(3*5)"

    def test_control_limits_lower(self) -> None:
        """Test lower control limit calculation."""
        formula = ControlLimitsFormula()
        result = formula.build("100", "5", "lower")  # mean=100, std=5, LCL
        assert result == "of:=100-(3*5)"

    def test_control_limits_upper_quoted(self) -> None:
        """Test upper control limit with quoted string."""
        formula = ControlLimitsFormula()
        result = formula.build("50", "2", "'upper'")
        assert result == "of:=50+(3*2)"

    def test_control_limits_lower_quoted(self) -> None:
        """Test lower control limit with quoted string."""
        formula = ControlLimitsFormula()
        result = formula.build("50", "2", "'lower'")
        assert result == "of:=50-(3*2)"

    def test_control_limits_high_variability(self) -> None:
        """Test control limits with high variability."""
        formula = ControlLimitsFormula()
        result_ucl = formula.build("75", "10", "upper")
        result_lcl = formula.build("75", "10", "lower")
        assert result_ucl == "of:=75+(3*10)"
        assert result_lcl == "of:=75-(3*10)"

    def test_control_limits_cell_references(self) -> None:
        """Test control limits with cell references."""
        formula = ControlLimitsFormula()
        result = formula.build("A1", "B1", "upper")
        assert result == "of:=A1+(3*B1)"

    def test_control_limits_default_upper(self) -> None:
        """Test control limits defaults to upper if invalid type."""
        formula = ControlLimitsFormula()
        result = formula.build("100", "5", "invalid")
        assert result == "of:=100+(3*5)"

    def test_control_limits_metadata(self) -> None:
        """Test control limits formula metadata."""
        formula = ControlLimitsFormula()
        metadata = formula.metadata

        assert metadata.name == "CONTROL_LIMITS"
        assert metadata.category == "quality"
        assert len(metadata.arguments) == 3


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestQualityUtilityFunctions:
    """Test quality utility functions."""

    def test_calculate_defect_rate_standard(self) -> None:
        """Test defect rate utility function."""
        rate = calculate_defect_rate(25, 1000)
        assert rate == 2.5  # 2.5%

    def test_calculate_defect_rate_zero(self) -> None:
        """Test defect rate with zero defects."""
        rate = calculate_defect_rate(0, 1000)
        assert rate == 0.0

    def test_calculate_defect_rate_high(self) -> None:
        """Test high defect rate."""
        rate = calculate_defect_rate(100, 1000)
        assert rate == 10.0  # 10%


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestQualityEdgeCases:
    """Test edge cases in quality formulas."""

    def test_defect_rate_validates_arguments(self) -> None:
        """Test defect rate argument validation."""
        formula = DefectRateFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("25")

    def test_first_pass_yield_validates_arguments(self) -> None:
        """Test first pass yield argument validation."""
        formula = FirstPassYieldFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("950")

    def test_process_capability_validates_arguments(self) -> None:
        """Test process capability argument validation."""
        formula = ProcessCapabilityFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("10", "0", "5")

    def test_control_limits_validates_arguments(self) -> None:
        """Test control limits argument validation."""
        formula = ControlLimitsFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("100", "5")


# ============================================================================
# Integration Tests
# ============================================================================


class TestQualityIntegration:
    """Integration tests for quality formulas with plugin."""

    def test_plugin_contains_quality_formulas(self) -> None:
        """Test plugin has quality formulas."""
        plugin = ManufacturingDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("DEFECT_RATE") is not None
        assert plugin.get_formula("FIRST_PASS_YIELD") is not None
        assert plugin.get_formula("PROCESS_CAPABILITY") is not None
        assert plugin.get_formula("CONTROL_LIMITS") is not None

    def test_all_quality_formulas_have_examples(self) -> None:
        """Test all quality formulas have usage examples."""
        formula_instances = [
            DefectRateFormula(),
            FirstPassYieldFormula(),
            ProcessCapabilityFormula(),
            ControlLimitsFormula(),
        ]

        for formula in formula_instances:
            metadata = formula.metadata
            assert len(metadata.examples) > 0, f"{metadata.name} should have examples"

    def test_quality_formulas_with_spc_values(self) -> None:
        """Test quality formulas with realistic SPC values."""
        defect = DefectRateFormula()
        fpy = FirstPassYieldFormula()
        cp = ProcessCapabilityFormula()
        cl = ControlLimitsFormula()

        # Defect rate: 15 defects in 5000 units
        defect_result = defect.build("15", "5000")
        assert defect_result == "of:=(15/5000)*100"

        # FPY: 4850 good in 5000 total
        fpy_result = fpy.build("4850", "5000")
        assert fpy_result == "of:=(4850/5000)*100"

        # Cp: USL=10.05, LSL=9.95, mean=10.0, std=0.01
        cp_result = cp.build("10.05", "9.95", "10.0", "0.01")
        assert cp_result == "of:=(10.05-9.95)/(6*0.01)"

        # Control limits for X-bar chart
        ucl_result = cl.build("10.0", "0.01", "upper")
        lcl_result = cl.build("10.0", "0.01", "lower")
        assert ucl_result == "of:=10.0+(3*0.01)"
        assert lcl_result == "of:=10.0-(3*0.01)"

    def test_plugin_has_all_37_manufacturing_formulas(self) -> None:
        """Test manufacturing plugin has expected formula count."""
        plugin = ManufacturingDomainPlugin()
        plugin.initialize()

        # Manufacturing should have 37 formulas:
        # - Production (4): cycle_time, takt_time, throughput, capacity_utilization
        # - Quality (4): defect_rate, first_pass_yield, process_capability, control_limits
        # - Inventory (6): eoq, reorder_point, safety_stock, inventory_turnover, holding_cost, stockout_cost
        # - Lean (6): value_added_ratio, lead_time, waste_percentage, oee, availability, performance
        # - Supply Chain (6): total_logistics_cost, order_fulfillment_rate, on_time_delivery, supply_chain_cycle_time, cash_to_cash, inventory_days
        # - Six Sigma (11): dpmo, process_sigma, yield_percentage, rolled_throughput_yield, cpk, ppk, sigma_level, defect_opportunity_rate, ppm, process_yield, quality_cost_ratio
        assert len(plugin.list_formulas()) == 37
