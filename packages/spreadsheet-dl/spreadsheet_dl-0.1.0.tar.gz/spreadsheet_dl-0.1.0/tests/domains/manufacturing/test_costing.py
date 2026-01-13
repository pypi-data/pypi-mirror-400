"""Tests for Manufacturing costing formulas.

Comprehensive tests for manufacturing costing formulas
including unit cost, overhead, break-even, and variance analysis.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing.formulas.costing import (
    ActivityBasedCostFormula,
    BreakEvenUnitsFormula,
    ContributionMarginFormula,
    CostPerDefectFormula,
    DirectLaborCostFormula,
    GrossProfitMarginFormula,
    LaborEfficiencyVarianceFormula,
    MachineCostPerHourFormula,
    MaterialCostVarianceFormula,
    OverheadRateFormula,
    ScrapRateCostFormula,
    StandardCostVarianceFormula,
    UnitCostFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.manufacturing]


# ============================================================================
# Unit Cost Formula Tests
# ============================================================================


class TestUnitCostCalculations:
    """Test unit cost calculations."""

    def test_unit_cost_standard(self) -> None:
        """Test standard unit cost calculation."""
        formula = UnitCostFormula()
        result = formula.build("50000", "1000")
        assert result == "of:=50000/1000"

    def test_unit_cost_high_volume(self) -> None:
        """Test unit cost with high production volume."""
        formula = UnitCostFormula()
        result = formula.build("100000", "10000")
        assert result == "of:=100000/10000"

    def test_unit_cost_low_volume(self) -> None:
        """Test unit cost with low production volume."""
        formula = UnitCostFormula()
        result = formula.build("5000", "100")
        assert result == "of:=5000/100"

    def test_unit_cost_cell_references(self) -> None:
        """Test unit cost with cell references."""
        formula = UnitCostFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"


class TestDirectLaborCostCalculations:
    """Test direct labor cost calculations."""

    def test_direct_labor_cost_standard(self) -> None:
        """Test standard direct labor cost calculation."""
        formula = DirectLaborCostFormula()
        result = formula.build("100", "25")  # 100 hours at $25/hr
        assert result == "of:=100*25"

    def test_direct_labor_cost_overtime(self) -> None:
        """Test direct labor cost with overtime rate."""
        formula = DirectLaborCostFormula()
        result = formula.build("40", "37.50")  # Overtime rate
        assert result == "of:=40*37.50"

    def test_direct_labor_cost_cell_references(self) -> None:
        """Test direct labor cost with cell references."""
        formula = DirectLaborCostFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1*B1"


class TestOverheadRateCalculations:
    """Test overhead rate calculations."""

    def test_overhead_rate_standard(self) -> None:
        """Test standard overhead rate calculation."""
        formula = OverheadRateFormula()
        result = formula.build("100000", "5000")  # $100K overhead, 5000 hours
        assert result == "of:=100000/5000"

    def test_overhead_rate_high_overhead(self) -> None:
        """Test overhead rate with high overhead costs."""
        formula = OverheadRateFormula()
        result = formula.build("500000", "10000")
        assert result == "of:=500000/10000"

    def test_overhead_rate_cell_references(self) -> None:
        """Test overhead rate with cell references."""
        formula = OverheadRateFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"


# ============================================================================
# Break-Even Analysis Tests
# ============================================================================


class TestBreakEvenUnitsCalculations:
    """Test break-even units calculations."""

    def test_break_even_standard(self) -> None:
        """Test standard break-even calculation."""
        formula = BreakEvenUnitsFormula()
        result = formula.build("50000", "100", "60")  # FC=$50K, P=$100, VC=$60
        assert result == "of:=50000/(100-60)"

    def test_break_even_high_margin(self) -> None:
        """Test break-even with high contribution margin."""
        formula = BreakEvenUnitsFormula()
        result = formula.build("100000", "200", "50")
        assert result == "of:=100000/(200-50)"

    def test_break_even_low_margin(self) -> None:
        """Test break-even with low contribution margin."""
        formula = BreakEvenUnitsFormula()
        result = formula.build("25000", "50", "45")
        assert result == "of:=25000/(50-45)"

    def test_break_even_cell_references(self) -> None:
        """Test break-even with cell references."""
        formula = BreakEvenUnitsFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=A1/(B1-C1)"


class TestContributionMarginCalculations:
    """Test contribution margin calculations."""

    def test_contribution_margin_standard(self) -> None:
        """Test standard contribution margin calculation."""
        formula = ContributionMarginFormula()
        result = formula.build("100", "60")  # Price=$100, VC=$60
        assert result == "of:=100-60"

    def test_contribution_margin_high_price(self) -> None:
        """Test contribution margin with high price."""
        formula = ContributionMarginFormula()
        result = formula.build("500", "150")
        assert result == "of:=500-150"

    def test_contribution_margin_cell_references(self) -> None:
        """Test contribution margin with cell references."""
        formula = ContributionMarginFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1-B1"


class TestGrossProfitMarginCalculations:
    """Test gross profit margin calculations."""

    def test_gross_profit_margin_standard(self) -> None:
        """Test standard gross profit margin calculation."""
        formula = GrossProfitMarginFormula()
        result = formula.build("100000", "60000")  # Rev=$100K, COGS=$60K
        assert result == "of:=((100000-60000)/100000)*100"

    def test_gross_profit_margin_high_cogs(self) -> None:
        """Test gross profit margin with high COGS."""
        formula = GrossProfitMarginFormula()
        result = formula.build("200000", "180000")
        assert "200000" in result
        assert "180000" in result

    def test_gross_profit_margin_cell_references(self) -> None:
        """Test gross profit margin with cell references."""
        formula = GrossProfitMarginFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result
        assert "B1" in result


# ============================================================================
# Variance Analysis Tests
# ============================================================================


class TestStandardCostVarianceCalculations:
    """Test standard cost variance calculations."""

    def test_standard_cost_variance_unfavorable(self) -> None:
        """Test unfavorable cost variance (actual > standard)."""
        formula = StandardCostVarianceFormula()
        result = formula.build("55000", "50000")
        assert result == "of:=55000-50000"

    def test_standard_cost_variance_favorable(self) -> None:
        """Test favorable cost variance (actual < standard)."""
        formula = StandardCostVarianceFormula()
        result = formula.build("48000", "50000")
        assert result == "of:=48000-50000"

    def test_standard_cost_variance_cell_references(self) -> None:
        """Test standard cost variance with cell references."""
        formula = StandardCostVarianceFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1-B1"


class TestMaterialCostVarianceCalculations:
    """Test material cost variance calculations."""

    def test_material_cost_variance_unfavorable(self) -> None:
        """Test unfavorable material variance."""
        formula = MaterialCostVarianceFormula()
        result = formula.build("1100", "1000", "5")  # Used 100 more units
        assert result == "of:=(1100-1000)*5"

    def test_material_cost_variance_favorable(self) -> None:
        """Test favorable material variance."""
        formula = MaterialCostVarianceFormula()
        result = formula.build("950", "1000", "5")
        assert result == "of:=(950-1000)*5"

    def test_material_cost_variance_cell_references(self) -> None:
        """Test material cost variance with cell references."""
        formula = MaterialCostVarianceFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=(A1-B1)*C1"


class TestLaborEfficiencyVarianceCalculations:
    """Test labor efficiency variance calculations."""

    def test_labor_efficiency_variance_unfavorable(self) -> None:
        """Test unfavorable labor efficiency variance."""
        formula = LaborEfficiencyVarianceFormula()
        result = formula.build("110", "100", "25")  # Used 10 more hours
        assert result == "of:=(110-100)*25"

    def test_labor_efficiency_variance_favorable(self) -> None:
        """Test favorable labor efficiency variance."""
        formula = LaborEfficiencyVarianceFormula()
        result = formula.build("95", "100", "25")
        assert result == "of:=(95-100)*25"

    def test_labor_efficiency_variance_cell_references(self) -> None:
        """Test labor efficiency variance with cell references."""
        formula = LaborEfficiencyVarianceFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=(A1-B1)*C1"


# ============================================================================
# Activity-Based Costing Tests
# ============================================================================


class TestActivityBasedCostCalculations:
    """Test activity-based cost calculations."""

    def test_activity_based_cost_standard(self) -> None:
        """Test standard ABC calculation."""
        formula = ActivityBasedCostFormula()
        result = formula.build("15", "200")  # $15/activity * 200 activities
        assert result == "of:=15*200"

    def test_activity_based_cost_machine_hours(self) -> None:
        """Test ABC with machine hours as driver."""
        formula = ActivityBasedCostFormula()
        result = formula.build("50", "100")  # $50/hour * 100 hours
        assert result == "of:=50*100"

    def test_activity_based_cost_cell_references(self) -> None:
        """Test ABC with cell references."""
        formula = ActivityBasedCostFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1*B1"


class TestMachineCostPerHourCalculations:
    """Test machine cost per hour calculations."""

    def test_machine_cost_per_hour_standard(self) -> None:
        """Test standard machine cost per hour."""
        formula = MachineCostPerHourFormula()
        result = formula.build("80000", "2000")  # $80K cost, 2000 hours
        assert result == "of:=80000/2000"

    def test_machine_cost_per_hour_high_utilization(self) -> None:
        """Test machine cost with high utilization."""
        formula = MachineCostPerHourFormula()
        result = formula.build("100000", "4000")
        assert result == "of:=100000/4000"

    def test_machine_cost_per_hour_cell_references(self) -> None:
        """Test machine cost per hour with cell references."""
        formula = MachineCostPerHourFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"


# ============================================================================
# Quality Cost Tests
# ============================================================================


class TestCostPerDefectCalculations:
    """Test cost per defect calculations."""

    def test_cost_per_defect_standard(self) -> None:
        """Test standard cost per defect."""
        formula = CostPerDefectFormula()
        result = formula.build("25000", "50")  # $25K total, 50 defects
        assert result == "of:=25000/50"

    def test_cost_per_defect_high_cost(self) -> None:
        """Test cost per defect with high failure costs."""
        formula = CostPerDefectFormula()
        result = formula.build("100000", "25")
        assert result == "of:=100000/25"

    def test_cost_per_defect_cell_references(self) -> None:
        """Test cost per defect with cell references."""
        formula = CostPerDefectFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"


class TestScrapRateCostCalculations:
    """Test scrap rate cost calculations."""

    def test_scrap_rate_cost_standard(self) -> None:
        """Test standard scrap rate cost."""
        formula = ScrapRateCostFormula()
        result = formula.build("50", "75")  # 50 units scrapped at $75 each
        assert result == "of:=50*75"

    def test_scrap_rate_cost_high_value_parts(self) -> None:
        """Test scrap cost with high-value parts."""
        formula = ScrapRateCostFormula()
        result = formula.build("10", "500")
        assert result == "of:=10*500"

    def test_scrap_rate_cost_cell_references(self) -> None:
        """Test scrap rate cost with cell references."""
        formula = ScrapRateCostFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1*B1"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestCostingEdgeCases:
    """Test edge cases in costing formulas."""

    def test_unit_cost_validates_arguments(self) -> None:
        """Test unit cost argument validation."""
        formula = UnitCostFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("50000")

    def test_break_even_validates_arguments(self) -> None:
        """Test break-even argument validation."""
        formula = BreakEvenUnitsFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("50000", "100")

    def test_material_variance_validates_arguments(self) -> None:
        """Test material variance argument validation."""
        formula = MaterialCostVarianceFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1100", "1000")


# ============================================================================
# Formula Metadata Tests
# ============================================================================


class TestCostingFormulaMetadata:
    """Test costing formula metadata."""

    def test_unit_cost_metadata(self) -> None:
        """Test unit cost formula metadata."""
        formula = UnitCostFormula()
        metadata = formula.metadata

        assert metadata.name == "UNIT_COST"
        assert metadata.category == "costing"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"

    def test_break_even_metadata(self) -> None:
        """Test break-even formula metadata."""
        formula = BreakEvenUnitsFormula()
        metadata = formula.metadata

        assert metadata.name == "BREAK_EVEN_UNITS"
        assert metadata.category == "costing"
        assert len(metadata.arguments) == 3

    def test_all_costing_formulas_have_examples(self) -> None:
        """Test all costing formulas have examples."""
        formula_instances = [
            UnitCostFormula(),
            DirectLaborCostFormula(),
            OverheadRateFormula(),
            BreakEvenUnitsFormula(),
            ContributionMarginFormula(),
            GrossProfitMarginFormula(),
            StandardCostVarianceFormula(),
            MaterialCostVarianceFormula(),
            LaborEfficiencyVarianceFormula(),
            ActivityBasedCostFormula(),
            MachineCostPerHourFormula(),
            CostPerDefectFormula(),
            ScrapRateCostFormula(),
        ]

        for formula in formula_instances:
            assert len(formula.metadata.examples) > 0, (
                f"{formula.metadata.name} should have examples"
            )


# ============================================================================
# Integration Tests
# ============================================================================


class TestCostingIntegration:
    """Integration tests for costing formulas."""

    def test_all_costing_formulas_produce_odf(self) -> None:
        """Test all costing formulas produce valid ODF output."""
        test_cases = [
            (UnitCostFormula(), ("50000", "1000")),
            (DirectLaborCostFormula(), ("100", "25")),
            (OverheadRateFormula(), ("100000", "5000")),
            (BreakEvenUnitsFormula(), ("50000", "100", "60")),
            (ContributionMarginFormula(), ("100", "60")),
            (GrossProfitMarginFormula(), ("100000", "60000")),
            (StandardCostVarianceFormula(), ("55000", "50000")),
            (MaterialCostVarianceFormula(), ("1100", "1000", "5")),
            (LaborEfficiencyVarianceFormula(), ("110", "100", "25")),
            (ActivityBasedCostFormula(), ("15", "200")),
            (MachineCostPerHourFormula(), ("80000", "2000")),
            (CostPerDefectFormula(), ("25000", "50")),
            (ScrapRateCostFormula(), ("50", "75")),
        ]

        for formula, args in test_cases:
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula.metadata.name} should return ODF formula"
            )

    def test_costing_formula_count(self) -> None:
        """Test total count of costing formulas."""
        from spreadsheet_dl.domains.manufacturing.formulas import costing

        # Should have 13 costing formulas
        expected_formulas = [
            "UnitCostFormula",
            "DirectLaborCostFormula",
            "OverheadRateFormula",
            "BreakEvenUnitsFormula",
            "ContributionMarginFormula",
            "GrossProfitMarginFormula",
            "StandardCostVarianceFormula",
            "MaterialCostVarianceFormula",
            "LaborEfficiencyVarianceFormula",
            "ActivityBasedCostFormula",
            "MachineCostPerHourFormula",
            "CostPerDefectFormula",
            "ScrapRateCostFormula",
        ]

        for formula_name in expected_formulas:
            assert hasattr(costing, formula_name), f"Missing {formula_name}"
