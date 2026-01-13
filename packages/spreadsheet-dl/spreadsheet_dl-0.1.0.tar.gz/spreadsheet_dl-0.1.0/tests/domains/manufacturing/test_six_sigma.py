"""
Tests for Six Sigma formulas.

    Comprehensive tests for Six Sigma formulas (10 formulas, 30+ tests)
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing.formulas.six_sigma import (
    ControlLimitFormula,
    DefectRateFormula,
    DPMOFormula,
    GaugeRnRFormula,
    ProcessCapabilityIndexFormula,
    ProcessPerformanceIndexFormula,
    ProcessSigmaFormula,
    SigmaLevelFormula,
    YieldCalculationFormula,
    ZScoreQualityFormula,
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.domain,
    pytest.mark.manufacturing,
    pytest.mark.six_sigma,
]


# ============================================================================
# DPMO Tests
# ============================================================================


def test_dpmo_metadata() -> None:
    """Test DPMO metadata."""
    formula = DPMOFormula()
    assert formula.metadata.name == "DPMO"
    assert formula.metadata.category == "six_sigma"
    assert len(formula.metadata.arguments) == 3


def test_dpmo_build() -> None:
    """Test DPMO formula building."""
    formula = DPMOFormula()
    result = formula.build("25", "1000", "5")
    assert result == "of:=(25/(1000*5))*1000000"


def test_dpmo_with_cells() -> None:
    """Test DPMO with cell references."""
    formula = DPMOFormula()
    result = formula.build("A1", "B1", "C1")
    assert result == "of:=(A1/(B1*C1))*1000000"


# ============================================================================
# Sigma Level Tests
# ============================================================================


def test_sigma_level_metadata() -> None:
    """Test SIGMA_LEVEL metadata."""
    formula = SigmaLevelFormula()
    assert formula.metadata.name == "SIGMA_LEVEL"
    assert formula.metadata.category == "six_sigma"


def test_sigma_level_build() -> None:
    """Test SIGMA_LEVEL formula building."""
    formula = SigmaLevelFormula()
    result = formula.build("6210")
    assert "SQRT" in result
    assert "LN" in result
    assert "6210" in result


def test_sigma_level_with_cell() -> None:
    """Test SIGMA_LEVEL with cell reference."""
    formula = SigmaLevelFormula()
    result = formula.build("D1")
    assert "D1" in result


# ============================================================================
# CPK Tests
# ============================================================================


def test_cpk_metadata() -> None:
    """Test CPK metadata."""
    formula = ProcessCapabilityIndexFormula()
    assert formula.metadata.name == "CPK"
    assert formula.metadata.category == "six_sigma"
    assert len(formula.metadata.arguments) == 4


def test_cpk_build() -> None:
    """Test CPK formula building."""
    formula = ProcessCapabilityIndexFormula()
    result = formula.build("10", "0", "5", "0.5")
    assert "MIN" in result
    assert "10-5" in result or "5-0" in result


def test_cpk_centered_process() -> None:
    """Test CPK with centered process."""
    formula = ProcessCapabilityIndexFormula()
    result = formula.build("10", "0", "5", "0.5")
    # Should have both CPU and CPL calculations
    assert "MIN(" in result
    assert ";" in result


# ============================================================================
# PPK Tests
# ============================================================================


def test_ppk_metadata() -> None:
    """Test PPK metadata."""
    formula = ProcessPerformanceIndexFormula()
    assert formula.metadata.name == "PPK"
    assert formula.metadata.category == "six_sigma"


def test_ppk_build() -> None:
    """Test PPK formula building."""
    formula = ProcessPerformanceIndexFormula()
    result = formula.build("10", "0", "5", "0.6")
    assert "MIN" in result


def test_ppk_different_sigma() -> None:
    """Test PPK with different overall sigma."""
    formula = ProcessPerformanceIndexFormula()
    result = formula.build("10", "0", "5", "0.8")
    assert "0.8" in result


# ============================================================================
# RTY Tests
# ============================================================================


def test_rty_metadata() -> None:
    """Test RTY metadata."""
    formula = YieldCalculationFormula()
    assert formula.metadata.name == "RTY"
    assert formula.metadata.category == "six_sigma"


def test_rty_build_two_processes() -> None:
    """Test RTY with two processes."""
    formula = YieldCalculationFormula()
    result = formula.build("0.98", "0.95")
    assert result == "of:=0.98*0.95"


def test_rty_build_three_processes() -> None:
    """Test RTY with three processes."""
    formula = YieldCalculationFormula()
    result = formula.build("0.98", "0.95", "0.99")
    assert result == "of:=0.98*0.95*0.99"


def test_rty_too_few_args() -> None:
    """Test RTY with too few arguments."""
    formula = YieldCalculationFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("0.98")


# ============================================================================
# Defect Rate Tests
# ============================================================================


def test_defect_rate_metadata() -> None:
    """Test DEFECT_RATE metadata."""
    formula = DefectRateFormula()
    assert formula.metadata.name == "DEFECT_RATE"
    assert formula.metadata.category == "six_sigma"


def test_defect_rate_build() -> None:
    """Test DEFECT_RATE formula building."""
    formula = DefectRateFormula()
    result = formula.build("15", "1000")
    assert result == "of:=(15/1000)*100"


def test_defect_rate_zero_defects() -> None:
    """Test DEFECT_RATE with zero defects."""
    formula = DefectRateFormula()
    result = formula.build("0", "1000")
    assert result == "of:=(0/1000)*100"


# ============================================================================
# Process Sigma Tests
# ============================================================================


def test_process_sigma_metadata() -> None:
    """Test PROCESS_SIGMA metadata."""
    formula = ProcessSigmaFormula()
    assert formula.metadata.name == "PROCESS_SIGMA"
    assert formula.metadata.category == "six_sigma"


def test_process_sigma_build() -> None:
    """Test PROCESS_SIGMA formula building."""
    formula = ProcessSigmaFormula()
    result = formula.build("10", "0", "0.5")
    assert result == "of:=(10-0)/(6*0.5)"


def test_process_sigma_narrow_limits() -> None:
    """Test PROCESS_SIGMA with narrow limits."""
    formula = ProcessSigmaFormula()
    result = formula.build("5", "4", "0.1")
    assert result == "of:=(5-4)/(6*0.1)"


# ============================================================================
# Control Limit Tests
# ============================================================================


def test_control_limit_metadata() -> None:
    """Test CONTROL_LIMIT metadata."""
    formula = ControlLimitFormula()
    assert formula.metadata.name == "CONTROL_LIMIT"
    assert formula.metadata.category == "six_sigma"
    assert len(formula.metadata.arguments) == 4


def test_control_limit_upper() -> None:
    """Test CONTROL_LIMIT upper limit."""
    formula = ControlLimitFormula()
    result = formula.build("100", "5", "3", "upper")
    assert result == "of:=100+(3*5)"


def test_control_limit_lower() -> None:
    """Test CONTROL_LIMIT lower limit."""
    formula = ControlLimitFormula()
    result = formula.build("100", "5", "3", "lower")
    assert result == "of:=100-(3*5)"


def test_control_limit_quoted_type() -> None:
    """Test CONTROL_LIMIT with quoted limit type."""
    formula = ControlLimitFormula()
    result = formula.build("100", "5", "3", "'upper'")
    assert "+" in result


# ============================================================================
# Z-Score Tests
# ============================================================================


def test_z_score_metadata() -> None:
    """Test Z_SCORE metadata."""
    formula = ZScoreQualityFormula()
    assert formula.metadata.name == "Z_SCORE"
    assert formula.metadata.category == "six_sigma"


def test_z_score_build() -> None:
    """Test Z_SCORE formula building."""
    formula = ZScoreQualityFormula()
    result = formula.build("105", "100", "5")
    assert result == "of:=(105-100)/5"


def test_z_score_negative() -> None:
    """Test Z_SCORE with value below mean."""
    formula = ZScoreQualityFormula()
    result = formula.build("95", "100", "5")
    assert result == "of:=(95-100)/5"


# ============================================================================
# Gauge R&R Tests
# ============================================================================


def test_gauge_rnr_metadata() -> None:
    """Test GAUGE_RNR metadata."""
    formula = GaugeRnRFormula()
    assert formula.metadata.name == "GAUGE_RNR"
    assert formula.metadata.category == "six_sigma"


def test_gauge_rnr_build() -> None:
    """Test GAUGE_RNR formula building."""
    formula = GaugeRnRFormula()
    result = formula.build("0.5", "0.3")
    assert "SQRT" in result
    assert "0.5^2" in result
    assert "0.3^2" in result


def test_gauge_rnr_with_cells() -> None:
    """Test GAUGE_RNR with cell references."""
    formula = GaugeRnRFormula()
    result = formula.build("E1", "F1")
    assert result == "of:=SQRT(E1^2+F1^2)"


# ============================================================================
# Edge Cases and Argument Validation
# ============================================================================


def test_dpmo_too_few_args() -> None:
    """Test DPMO with too few arguments."""
    formula = DPMOFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("25", "1000")


def test_cpk_too_many_args() -> None:
    """Test CPK with too many arguments."""
    formula = ProcessCapabilityIndexFormula()
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("10", "0", "5", "0.5", "extra")


def test_sigma_level_single_arg() -> None:
    """Test SIGMA_LEVEL requires exactly one argument."""
    formula = SigmaLevelFormula()
    with pytest.raises(ValueError):
        formula.build("6210", "extra")
