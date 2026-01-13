"""Tests for renewable energy formulas.

Comprehensive tests for renewable energy formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.environmental.formulas.renewable import (
    CapacityFactorFormula,
    EnergyPaybackTimeFormula,
    EnergyReturnInvestmentFormula,
    LevelizedCostEnergyFormula,
    SolarPanelOutputFormula,
    WindTurbinePowerFormula,
)
from spreadsheet_dl.domains.environmental.utils import (
    calculate_energy_payback_time,
    calculate_eroi,
    calculate_solar_panel_output,
    calculate_wind_turbine_power,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Solar Panel Output Formula Tests
# ============================================================================


def test_solar_panel_output_metadata() -> None:
    """Test solar panel output formula metadata."""
    formula = SolarPanelOutputFormula()

    assert formula.metadata.name == "SOLAR_PANEL_OUTPUT"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 3


def test_solar_panel_output_formula() -> None:
    """Test solar panel output formula calculation."""
    formula = SolarPanelOutputFormula()

    result = formula.build("1000", "1.6", "0.18")
    assert result == "of:=1000*1.6*0.18"


def test_solar_panel_output_utility() -> None:
    """Test solar panel output utility function."""
    # Standard conditions: 1000 W/m^2, 1.6 m^2, 18% efficiency
    power = calculate_solar_panel_output(1000, 1.6, 0.18)
    assert abs(power - 288.0) < 0.1

    # Low light conditions
    power_low = calculate_solar_panel_output(200, 1.6, 0.18)
    assert power_low < power


def test_solar_panel_realistic_scenarios() -> None:
    """Test solar panel with realistic scenarios."""
    # Residential 5kW system
    # ~28 panels, 1.6m^2 each, 20% efficiency, full sun
    power_per_panel = calculate_solar_panel_output(1000, 1.6, 0.20)
    total_power = power_per_panel * 28
    assert 8000 < total_power < 10000  # ~9 kW peak (28 * 320W panels)


# ============================================================================
# Wind Turbine Power Formula Tests
# ============================================================================


def test_wind_turbine_power_metadata() -> None:
    """Test wind turbine power formula metadata."""
    formula = WindTurbinePowerFormula()

    assert formula.metadata.name == "WIND_TURBINE_POWER"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 4


def test_wind_turbine_power_formula() -> None:
    """Test wind turbine power formula calculation."""
    formula = WindTurbinePowerFormula()

    result = formula.build("1.225", "2827", "12", "0.4")
    assert result == "of:=0.5*1.225*2827*12^3*0.4"


def test_wind_turbine_power_utility() -> None:
    """Test wind turbine power utility function."""
    # 30m diameter turbine (area = 707 m^2), 12 m/s wind
    power = calculate_wind_turbine_power(1.225, 707, 12, 0.4)
    assert 250000 < power < 350000  # ~300 kW


def test_wind_turbine_velocity_relationship() -> None:
    """Test wind turbine power scales with velocity cubed."""
    # Double wind speed should give ~8x power
    power_6ms = calculate_wind_turbine_power(1.225, 707, 6, 0.4)
    power_12ms = calculate_wind_turbine_power(1.225, 707, 12, 0.4)

    ratio = power_12ms / power_6ms
    assert abs(ratio - 8.0) < 0.1


def test_wind_turbine_betz_limit() -> None:
    """Test wind turbine respects Betz limit."""
    formula = WindTurbinePowerFormula()

    # Power coefficient should not exceed 0.593 (Betz limit)
    result = formula.build("1.225", "2827", "12", "0.593")
    assert "0.593" in result


# ============================================================================
# Energy Payback Time Formula Tests
# ============================================================================


def test_energy_payback_time_metadata() -> None:
    """Test energy payback time formula metadata."""
    formula = EnergyPaybackTimeFormula()

    assert formula.metadata.name == "ENERGY_PAYBACK_TIME"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 2


def test_energy_payback_time_formula() -> None:
    """Test energy payback time formula calculation."""
    formula = EnergyPaybackTimeFormula()

    result = formula.build("50000", "2500")
    assert result == "of:=50000/2500"


def test_energy_payback_time_utility() -> None:
    """Test energy payback time utility function."""
    # Solar panel: 50,000 kWh input, 2,500 kWh/year output
    epbt = calculate_energy_payback_time(50000, 2500)
    assert abs(epbt - 20.0) < 0.1

    # Better efficiency
    epbt_better = calculate_energy_payback_time(50000, 5000)
    assert epbt_better < epbt


def test_energy_payback_time_realistic() -> None:
    """Test EPBT with realistic solar panel data."""
    # Modern solar panel: ~1-3 years EPBT
    # 1.6 m^2 panel, 300W, produces ~450 kWh/year
    # Manufacturing energy: ~1000 kWh
    epbt = calculate_energy_payback_time(1000, 450)
    assert 1.5 < epbt < 3.0


# ============================================================================
# Capacity Factor Formula Tests
# ============================================================================


def test_capacity_factor_metadata() -> None:
    """Test capacity factor formula metadata."""
    formula = CapacityFactorFormula()

    assert formula.metadata.name == "CAPACITY_FACTOR"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 3


def test_capacity_factor_formula() -> None:
    """Test capacity factor formula calculation."""
    formula = CapacityFactorFormula()

    result = formula.build("175200", "1000", "8760")
    assert result == "of:=175200/(1000*8760)"


def test_capacity_factor_realistic_values() -> None:
    """Test capacity factor with realistic renewable energy data."""
    formula = CapacityFactorFormula()

    # Solar: ~20% capacity factor
    # 1000 kW rated, 8760 hours/year, 1,752,000 kWh actual
    _ = formula.build("1752000", "1000", "8760")
    # Result should be 0.2 when calculated

    # Wind: ~35% capacity factor
    _ = formula.build("3066000", "1000", "8760")
    # Result should be 0.35 when calculated


def test_capacity_factor_bounds() -> None:
    """Test capacity factor stays within valid bounds."""
    formula = CapacityFactorFormula()

    # Maximum possible (100% capacity factor)
    _ = formula.build("8760000", "1000", "8760")
    # Should evaluate to 1.0

    # Zero output
    _ = formula.build("0", "1000", "8760")
    # Should evaluate to 0.0


# ============================================================================
# Levelized Cost of Energy Formula Tests
# ============================================================================


def test_levelized_cost_energy_metadata() -> None:
    """Test LCOE formula metadata."""
    formula = LevelizedCostEnergyFormula()

    assert formula.metadata.name == "LEVELIZED_COST_ENERGY"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 5


def test_levelized_cost_energy_formula() -> None:
    """Test LCOE formula structure."""
    formula = LevelizedCostEnergyFormula()

    result = formula.build("1000000", "50000", "100000", "25", "0.05")

    # Should use SUMPRODUCT and SEQUENCE for NPV
    assert "SUMPRODUCT" in result
    assert "SEQUENCE" in result
    assert "1000000" in result  # CAPEX
    assert "50000" in result  # OPEX
    assert "100000" in result  # Energy
    assert "0.05" in result  # Discount rate


def test_levelized_cost_energy_components() -> None:
    """Test LCOE formula components."""
    formula = LevelizedCostEnergyFormula()

    result = formula.build("2000000", "100000", "500000", "20", "0.06")

    # Verify NPV calculations for OPEX and Energy
    assert "/(1+0.06)^SEQUENCE(20)" in result


# ============================================================================
# Energy Return on Investment Formula Tests
# ============================================================================


def test_energy_return_investment_metadata() -> None:
    """Test EROI formula metadata."""
    formula = EnergyReturnInvestmentFormula()

    assert formula.metadata.name == "ENERGY_RETURN_INVESTMENT"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 2


def test_energy_return_investment_formula() -> None:
    """Test EROI formula calculation."""
    formula = EnergyReturnInvestmentFormula()

    result = formula.build("500000", "50000")
    assert result == "of:=500000/50000"


def test_energy_return_investment_utility() -> None:
    """Test EROI utility function."""
    # Solar PV: typically EROI of 10-20
    eroi_solar = calculate_eroi(500000, 50000)
    assert abs(eroi_solar - 10.0) < 0.1

    # Wind: typically EROI of 15-25
    eroi_wind = calculate_eroi(1000000, 50000)
    assert abs(eroi_wind - 20.0) < 0.1


def test_energy_return_investment_realistic() -> None:
    """Test EROI with realistic energy system data."""
    # Coal plant: EROI ~30-40 (but with emissions)
    eroi_coal = calculate_eroi(30000000, 1000000)
    assert 20 < eroi_coal < 40

    # Modern solar: EROI ~10-15
    eroi_solar = calculate_eroi(12500000, 1000000)
    assert 10 < eroi_solar < 15


def test_eroi_sustainability_threshold() -> None:
    """Test EROI sustainability thresholds."""
    # EROI < 5 is generally unsustainable
    eroi_low = calculate_eroi(400000, 100000)
    assert eroi_low == 4.0

    # EROI > 10 is generally sustainable
    eroi_good = calculate_eroi(1500000, 100000)
    assert eroi_good == 15.0


# ============================================================================
# Formula Validation Tests
# ============================================================================


def test_solar_panel_requires_three_args() -> None:
    """Test solar panel formula requires three arguments."""
    formula = SolarPanelOutputFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("1000", "1.6")


def test_wind_turbine_requires_four_args() -> None:
    """Test wind turbine formula requires four arguments."""
    formula = WindTurbinePowerFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("1.225", "2827", "12")


def test_epbt_requires_two_args() -> None:
    """Test EPBT formula requires two arguments."""
    formula = EnergyPaybackTimeFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("50000")


def test_capacity_factor_requires_three_args() -> None:
    """Test capacity factor formula requires three arguments."""
    formula = CapacityFactorFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("175200", "1000")


def test_lcoe_requires_five_args() -> None:
    """Test LCOE formula requires five arguments."""
    formula = LevelizedCostEnergyFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("1000000", "50000", "100000", "25")


def test_eroi_requires_two_args() -> None:
    """Test EROI formula requires two arguments."""
    formula = EnergyReturnInvestmentFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("500000")


# ============================================================================
# Integration Tests
# ============================================================================


def test_solar_system_complete_analysis() -> None:
    """Test complete analysis of solar energy system."""
    # 5 kW residential system
    panel_area = 1.6  # m^2
    num_panels = 28
    efficiency = 0.20
    irradiance = 1000  # W/m^2 peak

    # Power output
    total_power = calculate_solar_panel_output(
        irradiance, panel_area * num_panels, efficiency
    )
    assert 8000 < total_power < 10000  # ~9 kW peak

    # EROI
    lifetime_output = 150000  # kWh over 25 years
    manufacturing_input = 15000  # kWh
    eroi = calculate_eroi(lifetime_output, manufacturing_input)
    assert 8 < eroi < 12

    # EPBT
    annual_output = 6000  # kWh/year
    epbt = calculate_energy_payback_time(manufacturing_input, annual_output)
    assert 2 < epbt < 3


def test_wind_farm_analysis() -> None:
    """Test complete analysis of wind farm."""
    # 2 MW turbine
    rotor_diameter = 90  # meters
    rotor_area = 3.14159 * (rotor_diameter / 2) ** 2
    wind_speed = 12  # m/s
    power_coeff = 0.45

    # Power output
    power = calculate_wind_turbine_power(1.225, rotor_area, wind_speed, power_coeff)
    assert 2500000 < power < 3500000  # ~3 MW at 12 m/s wind speed

    # EROI (wind typically higher than solar)
    lifetime_output = 100000000  # kWh over 20 years
    manufacturing_input = 4000000  # kWh
    eroi = calculate_eroi(lifetime_output, manufacturing_input)
    assert 20 < eroi < 30


def test_technology_comparison() -> None:
    """Test comparison between renewable technologies."""
    # Solar PV
    solar_eroi = calculate_eroi(150000, 15000)

    # Wind
    wind_eroi = calculate_eroi(200000, 10000)

    # Wind should have higher EROI
    assert wind_eroi > solar_eroi
