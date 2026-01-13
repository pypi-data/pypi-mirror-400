"""Tests for climate modeling formulas.

Comprehensive tests for climate modeling formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.environmental.formulas.climate import (
    ClimateSensitivityFormula,
    IceSheetMeltingFormula,
    RadiativeForcingFormula,
    SeaLevelRiseFormula,
)
from spreadsheet_dl.domains.environmental.utils import (
    calculate_climate_sensitivity,
    calculate_ice_sheet_mass_balance,
    calculate_radiative_forcing,
    calculate_sea_level_rise,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Radiative Forcing Formula Tests
# ============================================================================


def test_radiative_forcing_metadata() -> None:
    """Test radiative forcing formula metadata."""
    formula = RadiativeForcingFormula()

    assert formula.metadata.name == "RADIATIVE_FORCING"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 2
    assert formula.metadata.return_type == "number"


def test_radiative_forcing_formula() -> None:
    """Test radiative forcing formula calculation."""
    formula = RadiativeForcingFormula()

    result = formula.build("400", "280")
    assert result == "of:=5.35*LN(400/280)"


def test_radiative_forcing_default_reference() -> None:
    """Test radiative forcing with default reference CO2."""
    formula = RadiativeForcingFormula()

    result = formula.build("400")
    assert result == "of:=5.35*LN(400/280)"


def test_radiative_forcing_utility() -> None:
    """Test radiative forcing utility function."""
    # CO2 doubling from 280 to 560 ppm
    rf = calculate_radiative_forcing(560, 280)
    assert abs(rf - 3.71) < 0.1  # Should be ~3.7 W/m^2

    # Current CO2 (~400 ppm)
    rf_current = calculate_radiative_forcing(400, 280)
    assert 1.5 < rf_current < 2.5


# ============================================================================
# Climate Sensitivity Formula Tests
# ============================================================================


def test_climate_sensitivity_metadata() -> None:
    """Test climate sensitivity formula metadata."""
    formula = ClimateSensitivityFormula()

    assert formula.metadata.name == "CLIMATE_SENSITIVITY"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 2


def test_climate_sensitivity_formula() -> None:
    """Test climate sensitivity formula calculation."""
    formula = ClimateSensitivityFormula()

    result = formula.build("3.7", "0.8")
    assert result == "of:=3.7/0.8"


def test_climate_sensitivity_default_feedback() -> None:
    """Test climate sensitivity with default feedback parameter."""
    formula = ClimateSensitivityFormula()

    result = formula.build("3.7")
    assert result == "of:=3.7/0.8"


def test_climate_sensitivity_utility() -> None:
    """Test climate sensitivity utility function."""
    # Standard forcing from CO2 doubling
    temp_change = calculate_climate_sensitivity(3.7, 0.8)
    assert abs(temp_change - 4.625) < 0.01

    # Lower feedback (higher sensitivity)
    temp_change_high = calculate_climate_sensitivity(3.7, 0.5)
    assert temp_change_high > temp_change


# ============================================================================
# Sea Level Rise Formula Tests
# ============================================================================


def test_sea_level_rise_metadata() -> None:
    """Test sea level rise formula metadata."""
    formula = SeaLevelRiseFormula()

    assert formula.metadata.name == "SEA_LEVEL_RISE"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 3


def test_sea_level_rise_formula() -> None:
    """Test sea level rise formula calculation."""
    formula = SeaLevelRiseFormula()

    result = formula.build("1.5", "3700", "0.000214")
    assert result == "of:=1.5*3700*0.000214"


def test_sea_level_rise_defaults() -> None:
    """Test sea level rise with default parameters."""
    formula = SeaLevelRiseFormula()

    result = formula.build("1.5")
    assert result == "of:=1.5*3700*0.000214"


def test_sea_level_rise_utility() -> None:
    """Test sea level rise utility function."""
    # 1.5°C warming
    slr = calculate_sea_level_rise(1.5)
    assert 1.0 < slr < 1.5  # Should be ~1.2 meters

    # 2°C warming
    slr_2c = calculate_sea_level_rise(2.0)
    assert slr_2c > slr


def test_sea_level_rise_custom_parameters() -> None:
    """Test sea level rise with custom ocean parameters."""
    formula = SeaLevelRiseFormula()

    result = formula.build("1.0", "4000", "0.0002")
    assert "4000" in result
    assert "0.0002" in result


# ============================================================================
# Ice Sheet Melting Formula Tests
# ============================================================================


def test_ice_sheet_melting_metadata() -> None:
    """Test ice sheet melting formula metadata."""
    formula = IceSheetMeltingFormula()

    assert formula.metadata.name == "ICE_SHEET_MELTING"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 3


def test_ice_sheet_melting_formula() -> None:
    """Test ice sheet melting formula without area."""
    formula = IceSheetMeltingFormula()

    result = formula.build("250", "180")
    assert result == "of:=250-180"


def test_ice_sheet_melting_with_area() -> None:
    """Test ice sheet melting formula with area parameter."""
    formula = IceSheetMeltingFormula()

    result = formula.build("250", "180", "15000000")
    assert result == "of:=(250-180)*15000000/1000"


def test_ice_sheet_melting_utility() -> None:
    """Test ice sheet mass balance utility function."""
    # Positive mass balance (accumulation > ablation)
    mb = calculate_ice_sheet_mass_balance(250, 180)
    assert mb == 70

    # Negative mass balance (melting)
    mb_neg = calculate_ice_sheet_mass_balance(180, 250)
    assert mb_neg == -70


def test_ice_sheet_melting_edge_cases() -> None:
    """Test ice sheet melting with edge cases."""
    formula = IceSheetMeltingFormula()

    # Equal accumulation and ablation
    result = formula.build("200", "200")
    assert result == "of:=200-200"

    # Zero ablation
    result = formula.build("250", "0")
    assert result == "of:=250-0"


# ============================================================================
# Formula Validation Tests
# ============================================================================


def test_radiative_forcing_requires_co2() -> None:
    """Test radiative forcing requires at least CO2 current."""
    formula = RadiativeForcingFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build()


def test_climate_sensitivity_requires_forcing() -> None:
    """Test climate sensitivity requires forcing parameter."""
    formula = ClimateSensitivityFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build()


def test_sea_level_rise_requires_temp_change() -> None:
    """Test sea level rise requires temperature change."""
    formula = SeaLevelRiseFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build()


def test_ice_sheet_melting_requires_two_params() -> None:
    """Test ice sheet melting requires accumulation and ablation."""
    formula = IceSheetMeltingFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("250")


# ============================================================================
# Integration Tests
# ============================================================================


def test_climate_calculation_chain() -> None:
    """Test chained climate calculations."""
    # CO2 increase from pre-industrial
    rf = calculate_radiative_forcing(400, 280)
    assert rf > 0

    # Temperature response to forcing
    temp_change = calculate_climate_sensitivity(rf, 0.8)
    assert temp_change > 0

    # Sea level rise from temperature change
    slr = calculate_sea_level_rise(temp_change)
    assert slr > 0


def test_realistic_climate_scenarios() -> None:
    """Test with realistic climate change scenarios."""
    # RCP4.5 scenario (~550 ppm by 2100)
    rf_rcp45 = calculate_radiative_forcing(550, 280)
    temp_rcp45 = calculate_climate_sensitivity(rf_rcp45, 0.8)
    slr_rcp45 = calculate_sea_level_rise(temp_rcp45)

    # RCP8.5 scenario (~900 ppm by 2100)
    rf_rcp85 = calculate_radiative_forcing(900, 280)
    temp_rcp85 = calculate_climate_sensitivity(rf_rcp85, 0.8)
    slr_rcp85 = calculate_sea_level_rise(temp_rcp85)

    # Higher emissions should lead to greater impacts
    assert rf_rcp85 > rf_rcp45
    assert temp_rcp85 > temp_rcp45
    assert slr_rcp85 > slr_rcp45


def test_antarctic_ice_sheet_example() -> None:
    """Test with Antarctic ice sheet data."""
    # Simplified example: accumulation vs ablation
    accumulation = 2000  # Gt/year
    ablation = 2100  # Gt/year (net loss)

    mb = calculate_ice_sheet_mass_balance(accumulation, ablation)
    assert mb < 0  # Net loss


def test_greenland_ice_sheet_example() -> None:
    """Test with Greenland ice sheet data."""
    # Simplified example
    accumulation = 600  # Gt/year
    ablation = 550  # Gt/year (net gain)

    mb = calculate_ice_sheet_mass_balance(accumulation, ablation)
    assert mb > 0  # Net gain
