"""Tests for filter design formulas in electrical engineering.

Tests for filter cutoff, Q factor, and attenuation formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.electrical_engineering.formulas.filters import (
    BandPassCenterFormula,
    FilterAttenuationFormula,
    HighPassCutoffFormula,
    LowPassCutoffFormula,
    QFactorFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.engineering]


# ============================================================================
# Cutoff Frequency Formula Tests
# ============================================================================


def test_low_pass_cutoff_formula() -> None:
    """Test low-pass filter cutoff frequency formula."""
    formula = LowPassCutoffFormula()

    # Test metadata
    assert formula.metadata.name == "LOW_PASS_CUTOFF"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "number"

    # Test formula building: fc = 1/(2*PI()*R*C)
    result = formula.build("1000", "1e-6")
    assert result == "of:=1/(2*PI()*1000*1e-6)"

    # Test with cell references
    result = formula.build("A2", "B2")
    assert result == "of:=1/(2*PI()*A2*B2)"


def test_high_pass_cutoff_formula() -> None:
    """Test high-pass filter cutoff frequency formula."""
    formula = HighPassCutoffFormula()

    # Test metadata
    assert formula.metadata.name == "HIGH_PASS_CUTOFF"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "number"

    # Test formula building: fc = 1/(2*PI()*R*C)
    result = formula.build("10000", "100e-9")
    assert result == "of:=1/(2*PI()*10000*100e-9)"

    # Test with cell references
    result = formula.build("A2", "B2")
    assert result == "of:=1/(2*PI()*A2*B2)"


def test_band_pass_center_formula() -> None:
    """Test bandpass filter center frequency formula."""
    formula = BandPassCenterFormula()

    # Test metadata
    assert formula.metadata.name == "BAND_PASS_CENTER"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "number"

    # Test formula building: fc = 1/(2*PI()*SQRT(L*C))
    result = formula.build("1e-3", "1e-9")
    assert result == "of:=1/(2*PI()*SQRT(1e-3*1e-9))"

    # Test with cell references
    result = formula.build("A2", "B2")
    assert result == "of:=1/(2*PI()*SQRT(A2*B2))"


# ============================================================================
# Q Factor and Attenuation Formula Tests
# ============================================================================


def test_q_factor_formula() -> None:
    """Test quality factor formula."""
    formula = QFactorFormula()

    # Test metadata
    assert formula.metadata.name == "Q_FACTOR"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "number"

    # Test formula building: Q = f0 / BW
    result = formula.build("1000", "100")
    assert result == "of:=1000/100"

    # Test with cell references
    result = formula.build("A2", "B2")
    assert result == "of:=A2/B2"


def test_filter_attenuation_formula() -> None:
    """Test filter attenuation formula."""
    formula = FilterAttenuationFormula()

    # Test metadata
    assert formula.metadata.name == "FILTER_ATTENUATION"
    assert formula.metadata.category == "electrical_engineering"
    assert len(formula.metadata.arguments) == 3
    assert formula.metadata.return_type == "number"

    # Test formula building: A = -20*n*log10(f/fc)
    result = formula.build("10000", "1000", "2")
    assert result == "of:=-20*2*LOG10(10000/1000)"

    # Test with cell references
    result = formula.build("A2", "B2", "C2")
    assert result == "of:=-20*C2*LOG10(A2/B2)"


# ============================================================================
# Validation Tests
# ============================================================================


def test_low_pass_cutoff_validation() -> None:
    """Test low-pass cutoff formula argument validation."""
    formula = LowPassCutoffFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1000")

    # Too many arguments
    with pytest.raises(ValueError, match="at most 2 arguments"):
        formula.build("1000", "1e-6", "extra")


def test_high_pass_cutoff_validation() -> None:
    """Test high-pass cutoff formula argument validation."""
    formula = HighPassCutoffFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1000")

    # Too many arguments
    with pytest.raises(ValueError, match="at most 2 arguments"):
        formula.build("1000", "1e-6", "extra")


def test_band_pass_center_validation() -> None:
    """Test bandpass center formula argument validation."""
    formula = BandPassCenterFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1e-3")

    # Too many arguments
    with pytest.raises(ValueError, match="at most 2 arguments"):
        formula.build("1e-3", "1e-9", "extra")


def test_q_factor_validation() -> None:
    """Test Q factor formula argument validation."""
    formula = QFactorFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("1000")

    # Too many arguments
    with pytest.raises(ValueError, match="at most 2 arguments"):
        formula.build("1000", "100", "extra")


def test_filter_attenuation_validation() -> None:
    """Test filter attenuation formula argument validation."""
    formula = FilterAttenuationFormula()

    # Too few arguments
    with pytest.raises(ValueError, match="at least 3 arguments"):
        formula.build("10000", "1000")

    # Too many arguments
    with pytest.raises(ValueError, match="at most 3 arguments"):
        formula.build("10000", "1000", "2", "extra")


# ============================================================================
# Metadata Completeness Tests
# ============================================================================


def test_all_filter_formulas_have_complete_metadata() -> None:
    """Ensure all filter formulas have proper metadata."""
    formulas = [
        LowPassCutoffFormula,
        HighPassCutoffFormula,
        BandPassCenterFormula,
        QFactorFormula,
        FilterAttenuationFormula,
    ]

    for formula_class in formulas:
        formula = formula_class()  # type: ignore[abstract]
        metadata = formula.metadata

        # Check required metadata fields
        assert metadata.name
        assert metadata.category == "electrical_engineering"
        assert metadata.description
        assert len(metadata.arguments) > 0
        assert metadata.return_type
        assert len(metadata.examples) > 0

        # Check each argument has required fields
        for arg in metadata.arguments:
            assert arg.name
            assert arg.type
            assert isinstance(arg.required, bool)
            assert arg.description


# ============================================================================
# Formula Examples Tests
# ============================================================================


def test_low_pass_cutoff_examples() -> None:
    """Test low-pass cutoff formula examples are valid."""
    formula = LowPassCutoffFormula()
    assert len(formula.metadata.examples) >= 1
    for example in formula.metadata.examples:
        assert "LOW_PASS_CUTOFF" in example or "# " in example


def test_high_pass_cutoff_examples() -> None:
    """Test high-pass cutoff formula examples are valid."""
    formula = HighPassCutoffFormula()
    assert len(formula.metadata.examples) >= 1
    for example in formula.metadata.examples:
        assert "HIGH_PASS_CUTOFF" in example or "# " in example


def test_band_pass_center_examples() -> None:
    """Test bandpass center formula examples are valid."""
    formula = BandPassCenterFormula()
    assert len(formula.metadata.examples) >= 1
    for example in formula.metadata.examples:
        assert "BAND_PASS_CENTER" in example or "# " in example


def test_q_factor_examples() -> None:
    """Test Q factor formula examples are valid."""
    formula = QFactorFormula()
    assert len(formula.metadata.examples) >= 1
    for example in formula.metadata.examples:
        assert "Q_FACTOR" in example or "# " in example


def test_filter_attenuation_examples() -> None:
    """Test filter attenuation formula examples are valid."""
    formula = FilterAttenuationFormula()
    assert len(formula.metadata.examples) >= 1
    for example in formula.metadata.examples:
        assert "FILTER_ATTENUATION" in example or "# " in example


# ============================================================================
# Edge Cases and Practical Scenarios
# ============================================================================


def test_low_pass_cutoff_typical_values() -> None:
    """Test low-pass cutoff with typical component values."""
    formula = LowPassCutoffFormula()

    # Common RC filter: 1kΩ and 1μF should give ~159Hz
    result = formula.build("1000", "0.000001")
    assert result == "of:=1/(2*PI()*1000*0.000001)"


def test_high_pass_cutoff_typical_values() -> None:
    """Test high-pass cutoff with typical component values."""
    formula = HighPassCutoffFormula()

    # Audio high-pass filter: 10kΩ and 100nF
    result = formula.build("10000", "1e-7")
    assert result == "of:=1/(2*PI()*10000*1e-7)"


def test_band_pass_center_typical_values() -> None:
    """Test bandpass center with typical LC values."""
    formula = BandPassCenterFormula()

    # RF filter: 1mH and 1nF
    result = formula.build("0.001", "1e-9")
    assert result == "of:=1/(2*PI()*SQRT(0.001*1e-9))"


def test_q_factor_typical_values() -> None:
    """Test Q factor with typical resonant circuit values."""
    formula = QFactorFormula()

    # High-Q filter: 1MHz resonance, 10kHz bandwidth = Q=100
    result = formula.build("1000000", "10000")
    assert result == "of:=1000000/10000"

    # Low-Q filter: 1kHz resonance, 500Hz bandwidth = Q=2
    result = formula.build("1000", "500")
    assert result == "of:=1000/500"


def test_filter_attenuation_various_orders() -> None:
    """Test filter attenuation with different filter orders."""
    formula = FilterAttenuationFormula()

    # First-order filter (6 dB/octave or 20 dB/decade)
    result = formula.build("10000", "1000", "1")
    assert result == "of:=-20*1*LOG10(10000/1000)"

    # Second-order filter (12 dB/octave or 40 dB/decade)
    result = formula.build("10000", "1000", "2")
    assert result == "of:=-20*2*LOG10(10000/1000)"

    # Fourth-order filter (24 dB/octave or 80 dB/decade)
    result = formula.build("10000", "1000", "4")
    assert result == "of:=-20*4*LOG10(10000/1000)"


def test_formulas_with_scientific_notation() -> None:
    """Test filter formulas with scientific notation values."""
    low_pass = LowPassCutoffFormula()
    high_pass = HighPassCutoffFormula()
    band_pass = BandPassCenterFormula()

    # Scientific notation for very small capacitance values
    assert low_pass.build("1e3", "1e-9") == "of:=1/(2*PI()*1e3*1e-9)"
    assert high_pass.build("1e4", "1e-12") == "of:=1/(2*PI()*1e4*1e-12)"
    assert band_pass.build("1e-6", "1e-12") == "of:=1/(2*PI()*SQRT(1e-6*1e-12))"


def test_q_factor_edge_cases() -> None:
    """Test Q factor formula edge cases."""
    formula = QFactorFormula()

    # Very high Q (narrow bandwidth)
    result = formula.build("1e6", "100")
    assert result == "of:=1e6/100"

    # Q = 1 (critical damping)
    result = formula.build("1000", "1000")
    assert result == "of:=1000/1000"


def test_filter_attenuation_below_cutoff() -> None:
    """Test filter attenuation formula for frequencies below cutoff."""
    formula = FilterAttenuationFormula()

    # Frequency below cutoff (f < fc) gives positive attenuation value
    result = formula.build("100", "1000", "1")
    assert result == "of:=-20*1*LOG10(100/1000)"


# ============================================================================
# Integration Tests
# ============================================================================


def test_filter_design_workflow() -> None:
    """Test complete filter design workflow using formulas."""
    # Design a low-pass filter with 1kHz cutoff
    lp_cutoff = LowPassCutoffFormula()
    q_factor = QFactorFormula()
    attenuation = FilterAttenuationFormula()

    # Calculate cutoff frequency
    cutoff_formula = lp_cutoff.build("1000", "1.59e-7")
    assert cutoff_formula == "of:=1/(2*PI()*1000*1.59e-7)"

    # Calculate Q factor
    q_formula = q_factor.build("1000", "200")
    assert q_formula == "of:=1000/200"

    # Calculate attenuation at 10kHz
    atten_formula = attenuation.build("10000", "1000", "2")
    assert atten_formula == "of:=-20*2*LOG10(10000/1000)"
