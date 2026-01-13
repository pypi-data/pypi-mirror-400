"""Tests for Mechanical Engineering Fluid Mechanics formulas.

BATCH2-MECH: Tests for 6 fluid mechanics formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.mechanical_engineering.formulas.fluid_mechanics import (
    BernoulliEquation,
    DarcyWeisbach,
    DragForce,
    LiftForce,
    PoiseuilleLaw,
    ReynoldsNumber,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.engineering]


# ============================================================================
# Reynolds Number Tests
# ============================================================================


def test_reynolds_number_metadata() -> None:
    """Test ReynoldsNumber metadata."""
    formula = ReynoldsNumber()
    assert formula.metadata.name == "REYNOLDS_NUMBER"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 3


def test_reynolds_number_build() -> None:
    """Test ReynoldsNumber formula building."""
    formula = ReynoldsNumber()
    result = formula.build("10", "0.1", "1e-6")
    assert result == "of:=10*0.1/1e-6"


def test_reynolds_number_with_cell_refs() -> None:
    """Test ReynoldsNumber with cell references."""
    formula = ReynoldsNumber()
    result = formula.build("A2", "B2", "C2")
    assert result == "of:=A2*B2/C2"


def test_reynolds_number_validation() -> None:
    """Test ReynoldsNumber argument validation."""
    formula = ReynoldsNumber()

    # Valid: 3 arguments
    formula.validate_arguments(("10", "0.1", "1e-6"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 3"):
        formula.validate_arguments(("10", "0.1"))

    # Invalid: too many arguments
    with pytest.raises(ValueError, match="at most 3"):
        formula.validate_arguments(("10", "0.1", "1e-6", "extra"))


# ============================================================================
# Bernoulli Equation Tests
# ============================================================================


def test_bernoulli_equation_metadata() -> None:
    """Test BernoulliEquation metadata."""
    formula = BernoulliEquation()
    assert formula.metadata.name == "BERNOULLI_EQUATION"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 5


def test_bernoulli_equation_build() -> None:
    """Test BernoulliEquation formula building."""
    formula = BernoulliEquation()
    result = formula.build("100000", "10", "5", "1000", "9.81")
    assert result == "of:=100000+0.5*1000*10^2+1000*9.81*5"


def test_bernoulli_equation_with_cell_refs() -> None:
    """Test BernoulliEquation with cell references."""
    formula = BernoulliEquation()
    result = formula.build("A2", "B2", "C2", "D2", "E2")
    assert result == "of:=A2+0.5*D2*B2^2+D2*E2*C2"


def test_bernoulli_equation_validation() -> None:
    """Test BernoulliEquation argument validation."""
    formula = BernoulliEquation()

    # Valid: 5 arguments
    formula.validate_arguments(("100000", "10", "5", "1000", "9.81"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 5"):
        formula.validate_arguments(("100000", "10", "5", "1000"))


# ============================================================================
# Darcy-Weisbach Tests
# ============================================================================


def test_darcy_weisbach_metadata() -> None:
    """Test DarcyWeisbach metadata."""
    formula = DarcyWeisbach()
    assert formula.metadata.name == "DARCY_WEISBACH"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 5


def test_darcy_weisbach_build() -> None:
    """Test DarcyWeisbach formula building."""
    formula = DarcyWeisbach()
    result = formula.build("0.02", "100", "0.1", "5", "1000")
    assert result == "of:=0.02*(100/0.1)*(0.5*1000*5^2)"


def test_darcy_weisbach_with_cell_refs() -> None:
    """Test DarcyWeisbach with cell references."""
    formula = DarcyWeisbach()
    result = formula.build("A2", "B2", "C2", "D2", "E2")
    assert result == "of:=A2*(B2/C2)*(0.5*E2*D2^2)"


def test_darcy_weisbach_validation() -> None:
    """Test DarcyWeisbach argument validation."""
    formula = DarcyWeisbach()

    # Valid: 5 arguments
    formula.validate_arguments(("0.02", "100", "0.1", "5", "1000"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 5"):
        formula.validate_arguments(("0.02", "100", "0.1", "5"))


# ============================================================================
# Poiseuille's Law Tests
# ============================================================================


def test_poiseuille_law_metadata() -> None:
    """Test PoiseuilleLaw metadata."""
    formula = PoiseuilleLaw()
    assert formula.metadata.name == "POISEUILLE_LAW"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 4


def test_poiseuille_law_build() -> None:
    """Test PoiseuilleLaw formula building."""
    formula = PoiseuilleLaw()
    result = formula.build("1000", "0.01", "1", "0.001")
    assert result == "of:=(PI()*0.01^4*1000)/(8*0.001*1)"


def test_poiseuille_law_with_cell_refs() -> None:
    """Test PoiseuilleLaw with cell references."""
    formula = PoiseuilleLaw()
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=(PI()*B2^4*A2)/(8*D2*C2)"


def test_poiseuille_law_validation() -> None:
    """Test PoiseuilleLaw argument validation."""
    formula = PoiseuilleLaw()

    # Valid: 4 arguments
    formula.validate_arguments(("1000", "0.01", "1", "0.001"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 4"):
        formula.validate_arguments(("1000", "0.01", "1"))


# ============================================================================
# Drag Force Tests
# ============================================================================


def test_drag_force_metadata() -> None:
    """Test DragForce metadata."""
    formula = DragForce()
    assert formula.metadata.name == "DRAG_FORCE"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 4


def test_drag_force_build() -> None:
    """Test DragForce formula building."""
    formula = DragForce()
    result = formula.build("0.5", "1.2", "30", "2.5")
    assert result == "of:=0.5*0.5*1.2*30^2*2.5"


def test_drag_force_with_cell_refs() -> None:
    """Test DragForce with cell references."""
    formula = DragForce()
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=0.5*A2*B2*C2^2*D2"


def test_drag_force_validation() -> None:
    """Test DragForce argument validation."""
    formula = DragForce()

    # Valid: 4 arguments
    formula.validate_arguments(("0.5", "1.2", "30", "2.5"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 4"):
        formula.validate_arguments(("0.5", "1.2", "30"))


# ============================================================================
# Lift Force Tests
# ============================================================================


def test_lift_force_metadata() -> None:
    """Test LiftForce metadata."""
    formula = LiftForce()
    assert formula.metadata.name == "LIFT_FORCE"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 4


def test_lift_force_build() -> None:
    """Test LiftForce formula building."""
    formula = LiftForce()
    result = formula.build("1.2", "1.2", "50", "15")
    assert result == "of:=0.5*1.2*1.2*50^2*15"


def test_lift_force_with_cell_refs() -> None:
    """Test LiftForce with cell references."""
    formula = LiftForce()
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=0.5*A2*B2*C2^2*D2"


def test_lift_force_validation() -> None:
    """Test LiftForce argument validation."""
    formula = LiftForce()

    # Valid: 4 arguments
    formula.validate_arguments(("1.2", "1.2", "50", "15"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 4"):
        formula.validate_arguments(("1.2", "1.2", "50"))


# ============================================================================
# Integration Tests
# ============================================================================


def test_all_formulas_have_of_prefix() -> None:
    """Test that all formulas return ODF format with 'of:=' prefix."""
    formulas_and_args = [
        (ReynoldsNumber(), ("10", "0.1", "1e-6")),
        (BernoulliEquation(), ("100000", "10", "5", "1000", "9.81")),
        (DarcyWeisbach(), ("0.02", "100", "0.1", "5", "1000")),
        (PoiseuilleLaw(), ("1000", "0.01", "1", "0.001")),
        (DragForce(), ("0.5", "1.2", "30", "2.5")),
        (LiftForce(), ("1.2", "1.2", "50", "15")),
    ]

    for formula, args in formulas_and_args:
        result = formula.build(*args)
        assert result.startswith("of:="), (
            f"{formula.metadata.name} should start with 'of:='"
        )


def test_all_formulas_return_number() -> None:
    """Test that all formulas declare number return type."""
    formulas = [
        ReynoldsNumber(),
        BernoulliEquation(),
        DarcyWeisbach(),
        PoiseuilleLaw(),
        DragForce(),
        LiftForce(),
    ]

    for formula in formulas:
        assert formula.metadata.return_type == "number"


def test_all_formulas_have_examples() -> None:
    """Test that all formulas have usage examples."""
    formulas = [
        ReynoldsNumber(),
        BernoulliEquation(),
        DarcyWeisbach(),
        PoiseuilleLaw(),
        DragForce(),
        LiftForce(),
    ]

    for formula in formulas:
        assert len(formula.metadata.examples) > 0
        assert any("=" in example for example in formula.metadata.examples)
