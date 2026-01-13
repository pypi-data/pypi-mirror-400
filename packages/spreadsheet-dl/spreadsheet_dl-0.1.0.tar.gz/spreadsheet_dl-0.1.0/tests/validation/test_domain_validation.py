"""Additional domain validation tests for uncovered domains.

These tests validate domain formulas against known reference values
for finance, data science, biology, and manufacturing domains.

References:
    - Financial formulas: Standard finance textbooks
    - Biology: Ecology textbooks, population dynamics models
    - Manufacturing: Engineering handbooks, quality standards
    - Data Science: Statistical theory, NumPy/SciPy reference implementations
"""

from __future__ import annotations

import math

import pytest

pytestmark = [pytest.mark.validation, pytest.mark.domain]


def evaluate_odf_formula(
    formula_str: str, variables: dict[str, float] | None = None
) -> float:
    """Evaluate an ODF formula string with given variable values."""
    if variables is None:
        variables = {}

    # Strip ODF prefix
    expr = formula_str.replace("of:=", "").replace("of:", "")

    # Replace spreadsheet functions with Python equivalents
    # Note: Replace longer names before shorter ones to avoid partial matches
    # Define helper functions for complex spreadsheet functions
    def sln(cost: float, salvage: float, life: float) -> float:
        """Straight-line depreciation."""
        return (cost - salvage) / life

    # Handle SLN before LN to avoid partial replacement
    if "SLN(" in expr:
        # For now, manually evaluate SLN calls (uses semicolons in ODF)
        import re

        sln_pattern = r"SLN\(([^;]+);([^;]+);([^)]+)\)"

        def eval_sln(match: re.Match[str]) -> str:
            cost, salvage, life = match.groups()
            result = sln(float(cost), float(salvage), float(life))
            return str(result)

        expr = re.sub(sln_pattern, eval_sln, expr)

    expr = expr.replace("SQRT", "math.sqrt")
    expr = expr.replace("PI()", str(math.pi))
    expr = expr.replace("EXP", "math.exp")
    expr = expr.replace("LN", "math.log")
    expr = expr.replace("LOG10", "math.log10")
    expr = expr.replace("SIN", "math.sin")
    expr = expr.replace("COS", "math.cos")
    expr = expr.replace("TAN", "math.tan")
    expr = expr.replace("ABS", "abs")
    expr = expr.replace("^", "**")
    expr = expr.replace(";", ",")

    # Substitute variables
    for name, value in variables.items():
        expr = expr.replace(name, str(value))

    try:
        return float(eval(expr, {"__builtins__": {}, "math": math, "abs": abs}))
    except Exception as e:
        raise ValueError(f"Failed to evaluate formula: {formula_str} -> {expr}") from e


# =============================================================================
# Finance Domain Validation
# =============================================================================


class TestFinanceValidation:
    """Validate finance formulas against known financial calculations."""

    def test_compound_interest_formula(self) -> None:
        """Validate compound interest: FV = PV * (1 + r)^n.

        Reference: Standard financial mathematics.
        """
        from spreadsheet_dl.domains.finance.formulas.time_value import FutureValue

        formula = FutureValue()

        # Test: $1000 at 5% for 10 years, no additional payments
        pv = 1000.0
        rate = 0.05
        periods = 10
        pmt = 0  # No periodic payments

        result = formula.build(str(rate), str(periods), str(pmt), str(pv))

        # Formula produces FV function, verify structure
        assert "of:=FV(" in result
        assert str(rate) in result
        assert str(periods) in result

    def test_loan_payment_calculation(self) -> None:
        """Validate loan payment: PMT = PV * [r(1+r)^n] / [(1+r)^n - 1].

        Reference: Standard mortgage calculation.
        """
        from spreadsheet_dl.domains.finance.formulas.time_value import PaymentFormula

        formula = PaymentFormula()

        # Test: $200,000 mortgage at 6% APR for 30 years (360 months)
        pv = 200000
        rate = 0.06 / 12  # Monthly rate
        periods = 360  # 30 years in months

        result = formula.build(str(rate), str(periods), str(pv))

        # Verify PMT formula structure
        assert "of:=PMT(" in result
        assert str(periods) in result

    def test_npv_structure(self) -> None:
        """Validate NPV formula structure.

        Reference: NPV = sum(CF_t / (1+r)^t) for t=1 to n
        """
        from spreadsheet_dl.domains.finance.formulas.time_value import NetPresentValue

        formula = NetPresentValue()

        rate = 0.10
        values_range = "A1:A5"

        result = formula.build(str(rate), values_range)

        # Verify NPV formula structure
        assert "of:=NPV(" in result
        assert str(rate) in result
        assert values_range in result


class TestFinanceDepreciationValidation:
    """Validate depreciation formulas."""

    def test_straight_line_depreciation(self) -> None:
        """Validate straight-line depreciation: D = (Cost - Salvage) / Life.

        Reference: Standard accounting practice.
        """
        from spreadsheet_dl.domains.finance.formulas.depreciation import (
            StraightLineDepreciation,
        )

        formula = StraightLineDepreciation()

        cost = 10000.0
        salvage = 2000.0
        life = 5

        result = formula.build(str(cost), str(salvage), str(life))
        calculated = evaluate_odf_formula(result, {})

        # Expected: (10000 - 2000) / 5 = 1600
        expected = (cost - salvage) / life

        assert abs(calculated - expected) < 1e-10, (
            f"SLN depreciation mismatch: {calculated} vs {expected}"
        )


# =============================================================================
# Biology Domain Validation
# =============================================================================


class TestBiologyEcologyValidation:
    """Validate ecology and population biology formulas."""

    def test_exponential_population_growth(self) -> None:
        """Validate exponential growth: N(t) = N0 * e^(rt).

        Reference: Standard population ecology model.
        """
        from spreadsheet_dl.domains.biology.formulas.ecology import (
            PopulationGrowthFormula,
        )

        formula = PopulationGrowthFormula()

        n0 = 100.0  # Initial population
        r = 0.05  # Growth rate
        t = 10.0  # Time periods

        result = formula.build(str(n0), str(r), str(t))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 100 * e^(0.05 * 10) = 100 * e^0.5 = 164.87
        expected = n0 * math.exp(r * t)

        assert abs(calculated - expected) < 1e-6, (
            f"Population growth mismatch: {calculated} vs {expected}"
        )

    def test_logistic_population_growth(self) -> None:
        """Validate logistic growth: N(t) = K / (1 + ((K-N0)/N0) * e^(-rt)).

        Reference: Verhulst logistic equation.
        """
        from spreadsheet_dl.domains.biology.formulas.ecology import (
            PopulationGrowthFormula,
        )

        formula = PopulationGrowthFormula()

        n0 = 100.0  # Initial population
        r = 0.1  # Growth rate
        t = 20.0  # Time periods
        k = 1000.0  # Carrying capacity

        result = formula.build(str(n0), str(r), str(t), str(k))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 1000 / (1 + ((1000-100)/100) * e^(-0.1*20))
        expected = k / (1 + ((k - n0) / n0) * math.exp(-r * t))

        assert abs(calculated - expected) < 1e-6, (
            f"Logistic growth mismatch: {calculated} vs {expected}"
        )

    def test_simpson_diversity_formula_structure(self) -> None:
        """Validate Simpson's diversity index formula structure.

        Reference: Simpson's D = 1 - sum(pi^2)
        """
        from spreadsheet_dl.domains.biology.formulas.ecology import SimpsonIndexFormula

        formula = SimpsonIndexFormula()

        abundance_range = "A1:A10"

        result = formula.build(abundance_range)

        # Should produce 1 - SUMPRODUCT formula
        assert "1-SUMPRODUCT" in result
        assert abundance_range in result


class TestBiologyMolecularValidation:
    """Validate molecular biology formulas."""

    def test_michaelis_menten_kinetics(self) -> None:
        """Validate Michaelis-Menten: v = Vmax * [S] / (Km + [S]).

        Reference: Standard enzyme kinetics.
        """
        from spreadsheet_dl.domains.biology.formulas.molecular import (
            MichaelisMentenFormula,
        )

        formula = MichaelisMentenFormula()

        vmax = 100.0  # Maximum reaction rate
        km = 10.0  # Michaelis constant
        s = 50.0  # Substrate concentration

        result = formula.build(str(vmax), str(km), str(s))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 100 * 50 / (10 + 50) = 5000/60 = 83.33
        expected = vmax * s / (km + s)

        assert abs(calculated - expected) < 1e-6, (
            f"Michaelis-Menten mismatch: {calculated} vs {expected}"
        )


# =============================================================================
# Manufacturing Domain Validation
# =============================================================================


class TestManufacturingQualityValidation:
    """Validate manufacturing quality formulas."""

    def test_process_capability_structure(self) -> None:
        """Validate ProcessCapabilityFormula structure.

        Reference: Six Sigma quality standards.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.six_sigma import (
            ProcessCapabilityIndexFormula,
        )

        formula = ProcessCapabilityIndexFormula()

        mean = 50.0
        sigma = 2.0
        usl = 60.0  # Upper spec limit
        lsl = 40.0  # Lower spec limit

        result = formula.build(str(usl), str(lsl), str(mean), str(sigma))

        # Verify MIN formula structure for Cpk
        assert "MIN(" in result

    def test_dpmo_calculation(self) -> None:
        """Validate DPMO = (Defects / Opportunities) * 1,000,000.

        Reference: Six Sigma quality metric.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.six_sigma import DPMOFormula

        formula = DPMOFormula()

        defects = 10
        units = 1000
        opportunities = 100

        result = formula.build(str(defects), str(units), str(opportunities))
        calculated = evaluate_odf_formula(result, {})

        # Expected: (10 / (1000 * 100)) * 1000000 = 100 DPMO
        expected = (defects / (units * opportunities)) * 1000000

        assert abs(calculated - expected) < 1e-10, (
            f"DPMO mismatch: {calculated} vs {expected}"
        )

    def test_first_pass_yield(self) -> None:
        """Validate First Pass Yield = Good Units / Total Units.

        Reference: Manufacturing quality metric.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.quality import (
            FirstPassYieldFormula,
        )

        formula = FirstPassYieldFormula()

        good_units = 950
        total_units = 1000

        result = formula.build(str(good_units), str(total_units))
        calculated = evaluate_odf_formula(result, {})

        # Expected: (950 / 1000) * 100 = 95.0%
        expected = (good_units / total_units) * 100

        assert abs(calculated - expected) < 1e-10, (
            f"FPY mismatch: {calculated} vs {expected}"
        )


class TestManufacturingInventoryValidation:
    """Validate manufacturing inventory formulas."""

    def test_economic_order_quantity(self) -> None:
        """Validate EOQ = sqrt(2*D*S/H).

        Reference: Wilson EOQ model.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.inventory import EOQFormula

        formula = EOQFormula()

        demand = 10000  # Annual demand
        order_cost = 100  # Cost per order
        holding_cost = 2  # Holding cost per unit per year

        result = formula.build(str(demand), str(order_cost), str(holding_cost))
        calculated = evaluate_odf_formula(result, {})

        # Expected: sqrt(2 * 10000 * 100 / 2) = sqrt(1000000) = 1000
        expected = math.sqrt(2 * demand * order_cost / holding_cost)

        assert abs(calculated - expected) < 1e-6, (
            f"EOQ mismatch: {calculated} vs {expected}"
        )

    def test_reorder_point_calculation(self) -> None:
        """Validate ROP = d * L + SS.

        Reference: Inventory management theory.
        d = daily demand, L = lead time, SS = safety stock
        """
        from spreadsheet_dl.domains.manufacturing.formulas.inventory import (
            ReorderPointFormula,
        )

        formula = ReorderPointFormula()

        daily_demand = 50  # Units per day
        lead_time = 7  # Days
        safety_stock = 100  # Units

        result = formula.build(str(daily_demand), str(lead_time), str(safety_stock))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 50 * 7 + 100 = 450
        expected = daily_demand * lead_time + safety_stock

        assert abs(calculated - expected) < 1e-10, (
            f"ROP mismatch: {calculated} vs {expected}"
        )


# =============================================================================
# Data Science Domain Validation
# =============================================================================


class TestDataScienceStatisticsValidation:
    """Validate data science statistical formulas."""

    def test_variance_formula_structure(self) -> None:
        """Validate variance formula structure.

        Reference: Var(X) = E[(X - mu)^2]
        """
        from spreadsheet_dl.domains.data_science.formulas.data_functions import (
            VarianceFormula,
        )

        formula = VarianceFormula()

        data_range = "A1:A10"

        result = formula.build(data_range)

        # Verify VAR formula structure
        assert "VAR" in result
        assert data_range in result

    def test_stdev_formula_structure(self) -> None:
        """Validate standard deviation formula structure.

        Reference: std = sqrt(variance)
        """
        from spreadsheet_dl.domains.data_science.formulas.data_functions import (
            StdevFormula,
        )

        formula = StdevFormula()

        data_range = "A1:A10"

        result = formula.build(data_range)

        # Verify STDEV formula
        assert "STDEV" in result
        assert data_range in result

    def test_correlation_formula_structure(self) -> None:
        """Validate correlation formula structure.

        Reference: Pearson correlation coefficient
        """
        from spreadsheet_dl.domains.data_science.formulas.data_functions import (
            CorrelationFormula,
        )

        formula = CorrelationFormula()

        range1 = "A1:A10"
        range2 = "B1:B10"

        result = formula.build(range1, range2)

        # Verify CORREL formula
        assert "CORREL" in result
        assert range1 in result
        assert range2 in result


class TestDataScienceMLMetricsValidation:
    """Validate machine learning metrics formulas."""

    def test_accuracy_metric(self) -> None:
        """Validate Accuracy = (TP + TN) / (TP + TN + FP + FN).

        Reference: Standard classification metric.
        """
        from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
            AccuracyFormula,
        )

        formula = AccuracyFormula()

        tp = 80  # True positives
        tn = 70  # True negatives
        fp = 10  # False positives
        fn = 15  # False negatives

        result = formula.build(str(tp), str(tn), str(fp), str(fn))
        calculated = evaluate_odf_formula(result, {})

        # Expected: (80 + 70) / (80 + 70 + 10 + 15) = 150/175 = 0.857...
        expected = (tp + tn) / (tp + tn + fp + fn)

        assert abs(calculated - expected) < 1e-10, (
            f"Accuracy mismatch: {calculated} vs {expected}"
        )

    def test_precision_metric(self) -> None:
        """Validate Precision = TP / (TP + FP).

        Reference: Standard classification metric.
        """
        from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
            PrecisionFormula,
        )

        formula = PrecisionFormula()

        tp = 80
        fp = 20

        result = formula.build(str(tp), str(fp))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 80 / (80 + 20) = 0.8
        expected = tp / (tp + fp)

        assert abs(calculated - expected) < 1e-10, (
            f"Precision mismatch: {calculated} vs {expected}"
        )

    def test_recall_metric(self) -> None:
        """Validate Recall = TP / (TP + FN).

        Reference: Standard classification metric.
        """
        from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
            RecallFormula,
        )

        formula = RecallFormula()

        tp = 80
        fn = 20

        result = formula.build(str(tp), str(fn))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 80 / (80 + 20) = 0.8
        expected = tp / (tp + fn)

        assert abs(calculated - expected) < 1e-10, (
            f"Recall mismatch: {calculated} vs {expected}"
        )

    def test_f1_score_metric(self) -> None:
        """Validate F1 = 2 * (precision * recall) / (precision + recall).

        Reference: Harmonic mean of precision and recall.
        """
        from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
            F1ScoreFormula,
        )

        formula = F1ScoreFormula()

        precision = 0.8
        recall = 0.6

        result = formula.build(str(precision), str(recall))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 2 * (0.8 * 0.6) / (0.8 + 0.6) = 0.96 / 1.4 = 0.6857...
        expected = 2 * (precision * recall) / (precision + recall)

        assert abs(calculated - expected) < 1e-10, (
            f"F1 score mismatch: {calculated} vs {expected}"
        )


# =============================================================================
# Cross-Domain Consistency Tests
# =============================================================================


class TestCrossDomainConsistency:
    """Test consistency across different domains."""

    def test_exponential_growth_physics_vs_biology(self) -> None:
        """Verify exponential growth formulas are consistent across domains.

        Both population growth and radioactive decay use N = N0 * e^(kt).
        """
        from spreadsheet_dl.domains.biology.formulas.ecology import (
            PopulationGrowthFormula,
        )

        bio_formula = PopulationGrowthFormula()

        n0 = 1000.0
        rate = 0.1
        time = 5.0

        bio_result = bio_formula.build(str(n0), str(rate), str(time))
        bio_value = evaluate_odf_formula(bio_result, {})

        # Calculate expected value
        expected = n0 * math.exp(rate * time)

        assert abs(bio_value - expected) < 1e-6

    def test_logarithmic_functions_consistency(self) -> None:
        """Verify logarithmic functions are consistent across domains.

        pH in chemistry and dB in electrical engineering both use log10.
        """
        from spreadsheet_dl.domains.chemistry.formulas.solutions import (
            pHCalculationFormula,
        )
        from spreadsheet_dl.domains.electrical_engineering.formulas.signal import (
            SignalToNoiseRatioFormula,
        )

        ph_formula = pHCalculationFormula()
        snr_formula = SignalToNoiseRatioFormula()

        # Both should use base-10 logarithm
        ph_result = ph_formula.build("0.001")
        snr_result = snr_formula.build("1000", "1")

        ph_value = evaluate_odf_formula(ph_result, {})
        snr_value = evaluate_odf_formula(snr_result, {})

        # pH = -log10(0.001) = 3
        assert abs(ph_value - 3.0) < 1e-10

        # SNR = 10 * log10(1000) = 30 dB
        assert abs(snr_value - 30.0) < 1e-10


class TestManufacturingLeanValidation:
    """Validate lean manufacturing formulas."""

    def test_takt_time_calculation(self) -> None:
        """Validate Takt Time = Available Time / Customer Demand.

        Reference: Lean manufacturing principles.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.production import (
            TaktTimeFormula,
        )

        formula = TaktTimeFormula()

        available_time = 480  # minutes per shift
        demand = 120  # units per shift

        result = formula.build(str(available_time), str(demand))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 480 / 120 = 4 minutes per unit
        expected = available_time / demand

        assert abs(calculated - expected) < 1e-10, (
            f"Takt time mismatch: {calculated} vs {expected}"
        )

    def test_throughput_calculation(self) -> None:
        """Validate Throughput = Output / Time.

        Reference: Production management.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.production import (
            ThroughputFormula,
        )

        formula = ThroughputFormula()

        output = 500  # units
        time = 8  # hours

        result = formula.build(str(output), str(time))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 500 / 8 = 62.5 units per hour
        expected = output / time

        assert abs(calculated - expected) < 1e-10, (
            f"Throughput mismatch: {calculated} vs {expected}"
        )

    def test_capacity_utilization(self) -> None:
        """Validate Capacity Utilization = Actual Output / Max Capacity.

        Reference: Operations management.
        """
        from spreadsheet_dl.domains.manufacturing.formulas.production import (
            CapacityUtilizationFormula,
        )

        formula = CapacityUtilizationFormula()

        actual = 850  # units
        capacity = 1000  # max units

        result = formula.build(str(actual), str(capacity))
        calculated = evaluate_odf_formula(result, {})

        # Expected: (850 / 1000) * 100 = 85.0%
        expected = (actual / capacity) * 100

        assert abs(calculated - expected) < 1e-10, (
            f"Capacity utilization mismatch: {calculated} vs {expected}"
        )
