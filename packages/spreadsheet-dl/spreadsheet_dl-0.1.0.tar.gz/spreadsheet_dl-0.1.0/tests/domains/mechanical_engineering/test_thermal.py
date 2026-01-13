"""Tests for Mechanical Engineering Thermal formulas.

BATCH2-MECH: Tests for original and 6 new heat transfer formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.mechanical_engineering.formulas.thermal import (
    ConvectionCoefficient,
    FinEfficiency,
    LinearThermalExpansionFormula,
    LogMeanTempDiff,
    NusseltNumber,
    RadiationHeatTransfer,
    ThermalResistance,
    ThermalStressFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.engineering]


# ============================================================================
# Original Thermal Formula Tests
# ============================================================================


def test_thermal_expansion_formula_metadata() -> None:
    """Test LinearThermalExpansionFormula metadata."""
    formula = LinearThermalExpansionFormula()
    assert formula.metadata.name == "LINEAR_THERMAL_EXPANSION"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 3


def test_thermal_expansion_formula_build() -> None:
    """Test LinearThermalExpansionFormula formula building."""
    formula = LinearThermalExpansionFormula()
    result = formula.build("11.7e-6", "1000", "100")
    assert result == "of:=11.7e-6*1000*100"


def test_thermal_expansion_formula_validation() -> None:
    """Test LinearThermalExpansionFormula argument validation."""
    formula = LinearThermalExpansionFormula()

    # Valid: 3 arguments
    formula.validate_arguments(("11.7e-6", "1000", "100"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 3"):
        formula.validate_arguments(("11.7e-6", "1000"))


def test_thermal_stress_formula_metadata() -> None:
    """Test ThermalStressFormula metadata."""
    formula = ThermalStressFormula()
    assert formula.metadata.name == "THERMAL_STRESS"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 3


def test_thermal_stress_formula_build() -> None:
    """Test ThermalStressFormula formula building."""
    formula = ThermalStressFormula()
    result = formula.build("200000", "11.7e-6", "100")
    assert result == "of:=200000*11.7e-6*100"


def test_thermal_stress_formula_validation() -> None:
    """Test ThermalStressFormula argument validation."""
    formula = ThermalStressFormula()

    # Valid: 3 arguments
    formula.validate_arguments(("200000", "11.7e-6", "100"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 3"):
        formula.validate_arguments(("200000", "11.7e-6"))


# ============================================================================
# Convection Coefficient Tests
# ============================================================================


def test_convection_coefficient_metadata() -> None:
    """Test ConvectionCoefficient metadata."""
    formula = ConvectionCoefficient()
    assert formula.metadata.name == "CONVECTION_COEFFICIENT"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 3


def test_convection_coefficient_build() -> None:
    """Test ConvectionCoefficient formula building."""
    formula = ConvectionCoefficient()
    result = formula.build("10", "0.6", "0.1")
    assert result == "of:=10*0.6/0.1"


def test_convection_coefficient_with_cell_refs() -> None:
    """Test ConvectionCoefficient with cell references."""
    formula = ConvectionCoefficient()
    result = formula.build("A2", "B2", "C2")
    assert result == "of:=A2*B2/C2"


def test_convection_coefficient_validation() -> None:
    """Test ConvectionCoefficient argument validation."""
    formula = ConvectionCoefficient()

    # Valid: 3 arguments
    formula.validate_arguments(("10", "0.6", "0.1"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 3"):
        formula.validate_arguments(("10", "0.6"))


# ============================================================================
# Radiation Heat Transfer Tests
# ============================================================================


def test_radiation_heat_transfer_metadata() -> None:
    """Test RadiationHeatTransfer metadata."""
    formula = RadiationHeatTransfer()
    assert formula.metadata.name == "RADIATION_HEAT_TRANSFER"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 4


def test_radiation_heat_transfer_build() -> None:
    """Test RadiationHeatTransfer formula building."""
    formula = RadiationHeatTransfer()
    result = formula.build("0.9", "1.5", "400", "300")
    assert result == "of:=0.9*5.67e-8*1.5*(400^4-300^4)"


def test_radiation_heat_transfer_with_cell_refs() -> None:
    """Test RadiationHeatTransfer with cell references."""
    formula = RadiationHeatTransfer()
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=A2*5.67e-8*B2*(C2^4-D2^4)"


def test_radiation_heat_transfer_validation() -> None:
    """Test RadiationHeatTransfer argument validation."""
    formula = RadiationHeatTransfer()

    # Valid: 4 arguments
    formula.validate_arguments(("0.9", "1.5", "400", "300"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 4"):
        formula.validate_arguments(("0.9", "1.5", "400"))


# ============================================================================
# Thermal Resistance Tests
# ============================================================================


def test_thermal_resistance_metadata() -> None:
    """Test ThermalResistance metadata."""
    formula = ThermalResistance()
    assert formula.metadata.name == "THERMAL_RESISTANCE"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 3


def test_thermal_resistance_build() -> None:
    """Test ThermalResistance formula building."""
    formula = ThermalResistance()
    result = formula.build("0.1", "0.5", "2")
    assert result == "of:=0.1/(0.5*2)"


def test_thermal_resistance_with_cell_refs() -> None:
    """Test ThermalResistance with cell references."""
    formula = ThermalResistance()
    result = formula.build("A2", "B2", "C2")
    assert result == "of:=A2/(B2*C2)"


def test_thermal_resistance_validation() -> None:
    """Test ThermalResistance argument validation."""
    formula = ThermalResistance()

    # Valid: 3 arguments
    formula.validate_arguments(("0.1", "0.5", "2"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 3"):
        formula.validate_arguments(("0.1", "0.5"))


# ============================================================================
# Log Mean Temperature Difference Tests
# ============================================================================


def test_log_mean_temp_diff_metadata() -> None:
    """Test LogMeanTempDiff metadata."""
    formula = LogMeanTempDiff()
    assert formula.metadata.name == "LOG_MEAN_TEMP_DIFF"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 2


def test_log_mean_temp_diff_build() -> None:
    """Test LogMeanTempDiff formula building."""
    formula = LogMeanTempDiff()
    result = formula.build("50", "30")
    assert result == "of:=(50-30)/LN(50/30)"


def test_log_mean_temp_diff_with_cell_refs() -> None:
    """Test LogMeanTempDiff with cell references."""
    formula = LogMeanTempDiff()
    result = formula.build("A2", "B2")
    assert result == "of:=(A2-B2)/LN(A2/B2)"


def test_log_mean_temp_diff_validation() -> None:
    """Test LogMeanTempDiff argument validation."""
    formula = LogMeanTempDiff()

    # Valid: 2 arguments
    formula.validate_arguments(("50", "30"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 2"):
        formula.validate_arguments(("50",))


# ============================================================================
# Fin Efficiency Tests
# ============================================================================


def test_fin_efficiency_metadata() -> None:
    """Test FinEfficiency metadata."""
    formula = FinEfficiency()
    assert formula.metadata.name == "FIN_EFFICIENCY"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 2


def test_fin_efficiency_build() -> None:
    """Test FinEfficiency formula building."""
    formula = FinEfficiency()
    result = formula.build("0.9", "1.5")
    assert result == "of:=0.9/1.5"


def test_fin_efficiency_with_cell_refs() -> None:
    """Test FinEfficiency with cell references."""
    formula = FinEfficiency()
    result = formula.build("A2", "B2")
    assert result == "of:=A2/B2"


def test_fin_efficiency_validation() -> None:
    """Test FinEfficiency argument validation."""
    formula = FinEfficiency()

    # Valid: 2 arguments
    formula.validate_arguments(("0.9", "1.5"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 2"):
        formula.validate_arguments(("0.9",))


# ============================================================================
# Nusselt Number Tests
# ============================================================================


def test_nusselt_number_metadata() -> None:
    """Test NusseltNumber metadata."""
    formula = NusseltNumber()
    assert formula.metadata.name == "NUSSELT_NUMBER"
    assert formula.metadata.category == "mechanical_engineering"
    assert len(formula.metadata.arguments) == 3


def test_nusselt_number_build() -> None:
    """Test NusseltNumber formula building."""
    formula = NusseltNumber()
    result = formula.build("50", "0.1", "0.6")
    assert result == "of:=50*0.1/0.6"


def test_nusselt_number_with_cell_refs() -> None:
    """Test NusseltNumber with cell references."""
    formula = NusseltNumber()
    result = formula.build("A2", "B2", "C2")
    assert result == "of:=A2*B2/C2"


def test_nusselt_number_validation() -> None:
    """Test NusseltNumber argument validation."""
    formula = NusseltNumber()

    # Valid: 3 arguments
    formula.validate_arguments(("50", "0.1", "0.6"))

    # Invalid: too few arguments
    with pytest.raises(ValueError, match="at least 3"):
        formula.validate_arguments(("50", "0.1"))


# ============================================================================
# Integration Tests
# ============================================================================


def test_new_formulas_have_of_prefix() -> None:
    """Test that all new formulas return ODF format with 'of:=' prefix."""
    formulas_and_args = [
        (ConvectionCoefficient(), ("10", "0.6", "0.1")),
        (RadiationHeatTransfer(), ("0.9", "1.5", "400", "300")),
        (ThermalResistance(), ("0.1", "0.5", "2")),
        (LogMeanTempDiff(), ("50", "30")),
        (FinEfficiency(), ("0.9", "1.5")),
        (NusseltNumber(), ("50", "0.1", "0.6")),
    ]

    for formula, args in formulas_and_args:
        result = formula.build(*args)
        assert result.startswith("of:="), (
            f"{formula.metadata.name} should start with 'of:='"
        )


def test_all_thermal_formulas_return_number() -> None:
    """Test that all thermal formulas declare number return type."""
    formulas = [
        LinearThermalExpansionFormula(),
        ThermalStressFormula(),
        ConvectionCoefficient(),
        RadiationHeatTransfer(),
        ThermalResistance(),
        LogMeanTempDiff(),
        FinEfficiency(),
        NusseltNumber(),
    ]

    for formula in formulas:
        assert formula.metadata.return_type == "number"


def test_all_thermal_formulas_have_examples() -> None:
    """Test that all thermal formulas have usage examples."""
    formulas = [
        LinearThermalExpansionFormula(),
        ThermalStressFormula(),
        ConvectionCoefficient(),
        RadiationHeatTransfer(),
        ThermalResistance(),
        LogMeanTempDiff(),
        FinEfficiency(),
        NusseltNumber(),
    ]

    for formula in formulas:
        assert len(formula.metadata.examples) > 0
        assert any("=" in example for example in formula.metadata.examples)


def test_original_formulas_still_work() -> None:
    """Test that original thermal formulas are not affected by extensions."""
    # Test LinearThermalExpansionFormula
    expansion = LinearThermalExpansionFormula()
    result = expansion.build("11.7e-6", "1000", "100")
    assert "11.7e-6*1000*100" in result

    # Test ThermalStressFormula
    stress = ThermalStressFormula()
    result = stress.build("200000", "11.7e-6", "100")
    assert "200000*11.7e-6*100" in result
