"""Tests for genetics formulas.

Comprehensive tests for genetics formulas (95%+ coverage target)
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.biology.formulas.genetics import (
    Chi2GeneticsFormula,
    HardyWeinbergFormula,
    InbreedingCoefficientFormula,
    LinkageDisequilibriumFormula,
    RecombinationFrequencyFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


def test_hardy_weinberg_formula() -> None:
    """Test Hardy-Weinberg equilibrium formula."""
    formula = HardyWeinbergFormula()

    assert formula.metadata.name == "HARDY_WEINBERG"
    assert formula.metadata.category == "genetics"

    # Test basic calculation (p^2 + 2pq + q^2)
    result = formula.build("0.6", "0.4")
    assert result == "of:=0.6^2 + 2*0.6*0.4 + 0.4^2"
    assert "^2" in result
    assert "2*" in result

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=A1^2 + 2*A1*B1 + B1^2"


def test_linkage_disequilibrium_formula() -> None:
    """Test linkage disequilibrium formula."""
    formula = LinkageDisequilibriumFormula()

    assert formula.metadata.name == "LINKAGE_DISEQUILIBRIUM"
    assert formula.metadata.category == "genetics"

    # Test basic calculation (freq_ab - freq_a * freq_b)
    result = formula.build("0.3", "0.5", "0.6")
    assert result == "of:=0.3 - (0.5 * 0.6)"
    assert " - " in result

    # Test with cell references
    result = formula.build("A1", "B1", "C1")
    assert result == "of:=A1 - (B1 * C1)"


def test_recombination_frequency_formula() -> None:
    """Test recombination frequency formula."""
    formula = RecombinationFrequencyFormula()

    assert formula.metadata.name == "RECOMBINATION_FREQUENCY"
    assert formula.metadata.category == "genetics"

    # Test basic calculation (recombinants / total)
    result = formula.build("15", "100")
    assert result == "of:=15/100"

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=A1/B1"


def test_chi2_genetics_formula() -> None:
    """Test chi-square genetics formula."""
    formula = Chi2GeneticsFormula()

    assert formula.metadata.name == "CHI2_GENETICS"
    assert formula.metadata.category == "genetics"

    # Test with ranges
    result = formula.build("A1:A4", "B1:B4")
    assert result == "of:=SUMPRODUCT((A1:A4 - B1:B4)^2 / B1:B4)"
    assert "SUMPRODUCT" in result
    assert "^2" in result

    # Test with different ranges
    result = formula.build("C1:C10", "D1:D10")
    assert "C1:C10" in result
    assert "D1:D10" in result


def test_inbreeding_coefficient_formula() -> None:
    """Test inbreeding coefficient formula."""
    formula = InbreedingCoefficientFormula()

    assert formula.metadata.name == "INBREEDING_COEFFICIENT"
    assert formula.metadata.category == "genetics"

    # Test basic calculation (1 - Ho/He)
    result = formula.build("0.25", "0.5")
    assert result == "of:=1 - (0.25/0.5)"
    assert "1 -" in result

    # Test with cell references
    result = formula.build("A1", "B1")
    assert result == "of:=1 - (A1/B1)"


def test_hardy_weinberg_argument_validation() -> None:
    """Test Hardy-Weinberg formula argument validation."""
    formula = HardyWeinbergFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("0.6")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("0.6", "0.4", "extra")


def test_linkage_disequilibrium_argument_validation() -> None:
    """Test linkage disequilibrium formula argument validation."""
    formula = LinkageDisequilibriumFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("0.3", "0.5")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("0.3", "0.5", "0.6", "extra")


def test_recombination_frequency_argument_validation() -> None:
    """Test recombination frequency formula argument validation."""
    formula = RecombinationFrequencyFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("15")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("15", "100", "extra")


def test_chi2_genetics_argument_validation() -> None:
    """Test chi-square genetics formula argument validation."""
    formula = Chi2GeneticsFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("A1:A4")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("A1:A4", "B1:B4", "extra")


def test_inbreeding_coefficient_argument_validation() -> None:
    """Test inbreeding coefficient formula argument validation."""
    formula = InbreedingCoefficientFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("0.25")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("0.25", "0.5", "extra")


def test_formula_metadata() -> None:
    """Test all formulas have proper metadata."""
    formulas = [
        HardyWeinbergFormula(),
        LinkageDisequilibriumFormula(),
        RecombinationFrequencyFormula(),
        Chi2GeneticsFormula(),
        InbreedingCoefficientFormula(),
    ]

    for formula in formulas:
        metadata = formula.metadata
        assert metadata.name
        assert metadata.category == "genetics"
        assert metadata.description
        assert len(metadata.arguments) >= 2
        assert metadata.return_type == "number"
        assert len(metadata.examples) >= 1


def test_formula_examples() -> None:
    """Test all formulas have valid examples."""
    formulas = [
        HardyWeinbergFormula(),
        LinkageDisequilibriumFormula(),
        RecombinationFrequencyFormula(),
        Chi2GeneticsFormula(),
        InbreedingCoefficientFormula(),
    ]

    for formula in formulas:
        metadata = formula.metadata
        for example in metadata.examples:
            assert "=" in example
            assert metadata.name in example


def test_hardy_weinberg_with_different_frequencies() -> None:
    """Test Hardy-Weinberg with various allele frequencies."""
    formula = HardyWeinbergFormula()

    # Test with equal frequencies
    result = formula.build("0.5", "0.5")
    assert result == "of:=0.5^2 + 2*0.5*0.5 + 0.5^2"

    # Test with unequal frequencies
    result = formula.build("0.7", "0.3")
    assert result == "of:=0.7^2 + 2*0.7*0.3 + 0.3^2"


def test_chi2_genetics_with_cell_ranges() -> None:
    """Test chi-square genetics formula with cell range references."""
    formula = Chi2GeneticsFormula()

    # Test with different range sizes
    result = formula.build("A1:A10", "B1:B10")
    assert "A1:A10" in result
    assert "B1:B10" in result
    assert "SUMPRODUCT" in result

    result = formula.build("C2:C5", "D2:D5")
    assert "C2:C5" in result
    assert "D2:D5" in result
