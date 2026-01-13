"""
Tests for Supply Chain formulas.

    Comprehensive tests for Supply Chain formulas (5 formulas, 15+ tests)
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing.formulas.supply_chain import (
    ABCAnalysisFormula,
    BullwhipEffectFormula,
    CashConversionCycleFormula,
    NewsvendorModelFormula,
    ServiceLevelFormula,
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.domain,
    pytest.mark.manufacturing,
    pytest.mark.supply_chain,
]


# ============================================================================
# Bullwhip Effect Tests
# ============================================================================


def test_bullwhip_effect_metadata() -> None:
    """Test BULLWHIP_EFFECT metadata."""
    formula = BullwhipEffectFormula()
    assert formula.metadata.name == "BULLWHIP_EFFECT"
    assert formula.metadata.category == "supply_chain"
    assert len(formula.metadata.arguments) == 2


def test_bullwhip_effect_build() -> None:
    """Test BULLWHIP_EFFECT formula building."""
    formula = BullwhipEffectFormula()
    result = formula.build("400", "100")
    assert result == "of:=400/100"


def test_bullwhip_effect_with_cells() -> None:
    """Test BULLWHIP_EFFECT with cell references."""
    formula = BullwhipEffectFormula()
    result = formula.build("A1", "B1")
    assert result == "of:=A1/B1"


def test_bullwhip_effect_no_amplification() -> None:
    """Test BULLWHIP_EFFECT with equal variance (ratio=1)."""
    formula = BullwhipEffectFormula()
    result = formula.build("100", "100")
    assert result == "of:=100/100"


# ============================================================================
# Newsvendor Model Tests
# ============================================================================


def test_newsvendor_metadata() -> None:
    """Test NEWSVENDOR_QUANTITY metadata."""
    formula = NewsvendorModelFormula()
    assert formula.metadata.name == "NEWSVENDOR_QUANTITY"
    assert formula.metadata.category == "supply_chain"
    assert len(formula.metadata.arguments) == 3


def test_newsvendor_build() -> None:
    """Test NEWSVENDOR_QUANTITY formula building."""
    formula = NewsvendorModelFormula()
    result = formula.build("10", "6", "2")
    assert result == "of:=(10-6)/(10-2)"


def test_newsvendor_with_cells() -> None:
    """Test NEWSVENDOR_QUANTITY with cell references."""
    formula = NewsvendorModelFormula()
    result = formula.build("C1", "D1", "E1")
    assert result == "of:=(C1-D1)/(C1-E1)"


def test_newsvendor_high_cost() -> None:
    """Test NEWSVENDOR_QUANTITY with high cost scenario."""
    formula = NewsvendorModelFormula()
    result = formula.build("10", "8", "1")
    assert "(10-8)" in result
    assert "(10-1)" in result


# ============================================================================
# ABC Analysis Tests
# ============================================================================


def test_abc_analysis_metadata() -> None:
    """Test ABC_SCORE metadata."""
    formula = ABCAnalysisFormula()
    assert formula.metadata.name == "ABC_SCORE"
    assert formula.metadata.category == "supply_chain"


def test_abc_analysis_build() -> None:
    """Test ABC_SCORE formula building."""
    formula = ABCAnalysisFormula()
    result = formula.build("50000", "200000")
    assert result == "of:=(50000/200000)*100"


def test_abc_analysis_class_a() -> None:
    """Test ABC_SCORE for Class A item (high value)."""
    formula = ABCAnalysisFormula()
    result = formula.build("150000", "200000")
    assert result == "of:=(150000/200000)*100"


def test_abc_analysis_class_c() -> None:
    """Test ABC_SCORE for Class C item (low value)."""
    formula = ABCAnalysisFormula()
    result = formula.build("1000", "200000")
    assert result == "of:=(1000/200000)*100"


# ============================================================================
# Service Level Tests
# ============================================================================


def test_service_level_metadata() -> None:
    """Test SERVICE_LEVEL metadata."""
    formula = ServiceLevelFormula()
    assert formula.metadata.name == "SERVICE_LEVEL"
    assert formula.metadata.category == "supply_chain"


def test_service_level_build() -> None:
    """Test SERVICE_LEVEL formula building."""
    formula = ServiceLevelFormula()
    result = formula.build("950", "1000")
    assert result == "of:=(950/1000)*100"


def test_service_level_perfect() -> None:
    """Test SERVICE_LEVEL with 100% fulfillment."""
    formula = ServiceLevelFormula()
    result = formula.build("1000", "1000")
    assert result == "of:=(1000/1000)*100"


def test_service_level_with_cells() -> None:
    """Test SERVICE_LEVEL with cell references."""
    formula = ServiceLevelFormula()
    result = formula.build("F1", "G1")
    assert result == "of:=(F1/G1)*100"


# ============================================================================
# Cash Conversion Cycle Tests
# ============================================================================


def test_cash_conversion_cycle_metadata() -> None:
    """Test CASH_CONVERSION_CYCLE metadata."""
    formula = CashConversionCycleFormula()
    assert formula.metadata.name == "CASH_CONVERSION_CYCLE"
    assert formula.metadata.category == "supply_chain"
    assert len(formula.metadata.arguments) == 3


def test_cash_conversion_cycle_build() -> None:
    """Test CASH_CONVERSION_CYCLE formula building."""
    formula = CashConversionCycleFormula()
    result = formula.build("45", "30", "35")
    assert result == "of:=45+30-35"


def test_cash_conversion_cycle_positive() -> None:
    """Test CASH_CONVERSION_CYCLE with positive cycle."""
    formula = CashConversionCycleFormula()
    result = formula.build("60", "40", "30")
    assert result == "of:=60+40-30"


def test_cash_conversion_cycle_negative() -> None:
    """Test CASH_CONVERSION_CYCLE that could result in negative value."""
    formula = CashConversionCycleFormula()
    result = formula.build("20", "10", "50")
    assert result == "of:=20+10-50"


def test_cash_conversion_cycle_with_cells() -> None:
    """Test CASH_CONVERSION_CYCLE with cell references."""
    formula = CashConversionCycleFormula()
    result = formula.build("H1", "I1", "J1")
    assert result == "of:=H1+I1-J1"


# ============================================================================
# Argument Validation Tests
# ============================================================================


def test_bullwhip_too_few_args() -> None:
    """Test BULLWHIP_EFFECT with too few arguments."""
    formula = BullwhipEffectFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("400")


def test_newsvendor_too_few_args() -> None:
    """Test NEWSVENDOR_QUANTITY with too few arguments."""
    formula = NewsvendorModelFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("10", "6")


def test_abc_too_many_args() -> None:
    """Test ABC_SCORE with too many arguments."""
    formula = ABCAnalysisFormula()
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("50000", "200000", "extra")


def test_service_level_too_many_args() -> None:
    """Test SERVICE_LEVEL with too many arguments."""
    formula = ServiceLevelFormula()
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("950", "1000", "extra")


def test_cash_conversion_cycle_too_few_args() -> None:
    """Test CASH_CONVERSION_CYCLE with too few arguments."""
    formula = CashConversionCycleFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("45", "30")
