"""Tests for pharmacokinetics formulas.

Comprehensive tests for pharmacokinetics formulas (95%+ coverage target)
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.biology.formulas.pharmacokinetics import (
    ClearanceFormula,
    HalfLifeFormula,
    LoadingDoseFormula,
    MaintenanceDoseFormula,
    VolumeOfDistributionFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


def test_clearance_formula() -> None:
    """Test clearance formula."""
    formula = ClearanceFormula()

    assert formula.metadata.name == "CLEARANCE"
    assert formula.metadata.category == "pharmacokinetics"

    # Test basic calculation (dose / auc)
    result = formula.build("500", "125")
    assert result == "of:=500/125"

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=A1/B1"


def test_volume_of_distribution_formula() -> None:
    """Test volume of distribution formula."""
    formula = VolumeOfDistributionFormula()

    assert formula.metadata.name == "VOLUME_OF_DISTRIBUTION"
    assert formula.metadata.category == "pharmacokinetics"

    # Test basic calculation (dose / concentration)
    result = formula.build("500", "10")
    assert result == "of:=500/10"

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=A1/B1"


def test_half_life_formula() -> None:
    """Test half-life formula."""
    formula = HalfLifeFormula()

    assert formula.metadata.name == "HALF_LIFE"
    assert formula.metadata.category == "pharmacokinetics"

    # Test basic calculation (0.693 * Vd / CL)
    result = formula.build("50", "4")
    assert result == "of:=0.693*50/4"
    assert "0.693" in result

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=0.693*A1/B1"


def test_loading_dose_formula() -> None:
    """Test loading dose formula."""
    formula = LoadingDoseFormula()

    assert formula.metadata.name == "LOADING_DOSE"
    assert formula.metadata.category == "pharmacokinetics"

    # Test basic calculation (target_conc * volume_dist)
    result = formula.build("10", "50")
    assert result == "of:=10*50"

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=A1*B1"


def test_maintenance_dose_formula() -> None:
    """Test maintenance dose formula."""
    formula = MaintenanceDoseFormula()

    assert formula.metadata.name == "MAINTENANCE_DOSE"
    assert formula.metadata.category == "pharmacokinetics"

    # Test basic calculation (clearance * target_conc * dosing_interval)
    result = formula.build("4", "10", "12")
    assert result == "of:=4*10*12"

    # Test with cell references
    result = formula.build("A1", "B1", "C1")
    assert result == "of:=A1*B1*C1"


def test_clearance_argument_validation() -> None:
    """Test clearance formula argument validation."""
    formula = ClearanceFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("500")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("500", "125", "extra")


def test_volume_of_distribution_argument_validation() -> None:
    """Test volume of distribution formula argument validation."""
    formula = VolumeOfDistributionFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("500")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("500", "10", "extra")


def test_half_life_argument_validation() -> None:
    """Test half-life formula argument validation."""
    formula = HalfLifeFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("50")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("50", "4", "extra")


def test_loading_dose_argument_validation() -> None:
    """Test loading dose formula argument validation."""
    formula = LoadingDoseFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("10")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("10", "50", "extra")


def test_maintenance_dose_argument_validation() -> None:
    """Test maintenance dose formula argument validation."""
    formula = MaintenanceDoseFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("4", "10")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("4", "10", "12", "extra")


def test_formula_metadata() -> None:
    """Test all formulas have proper metadata."""
    formulas = [
        ClearanceFormula(),
        VolumeOfDistributionFormula(),
        HalfLifeFormula(),
        LoadingDoseFormula(),
        MaintenanceDoseFormula(),
    ]

    for formula in formulas:
        metadata = formula.metadata
        assert metadata.name
        assert metadata.category == "pharmacokinetics"
        assert metadata.description
        assert len(metadata.arguments) >= 2
        assert metadata.return_type == "number"
        assert len(metadata.examples) >= 1


def test_formula_examples() -> None:
    """Test all formulas have valid examples."""
    formulas = [
        ClearanceFormula(),
        VolumeOfDistributionFormula(),
        HalfLifeFormula(),
        LoadingDoseFormula(),
        MaintenanceDoseFormula(),
    ]

    for formula in formulas:
        metadata = formula.metadata
        for example in metadata.examples:
            assert "=" in example
            assert metadata.name in example
