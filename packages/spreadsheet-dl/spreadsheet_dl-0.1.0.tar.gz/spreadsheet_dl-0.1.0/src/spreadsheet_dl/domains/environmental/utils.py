"""Environmental domain utility functions.

    Environmental domain utilities

Provides helper functions for environmental calculations,
unit conversions, and data processing.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Molecular weights for unit conversions (g/mol)
MOLECULAR_WEIGHTS = {
    "O3": 48.0,
    "NO2": 46.0,
    "SO2": 64.1,
    "CO": 28.0,
}

# Standard conditions for gas conversion
STANDARD_TEMP_K = 298.15  # 25 C
STANDARD_PRESSURE_KPA = 101.325  # 1 atm


def ppm_to_ugm3(ppm: float, molecular_weight: float) -> float:
    """Convert gas concentration from ppm to ug/m3.

    Args:
        ppm: Concentration in parts per million
        molecular_weight: Molecular weight of gas (g/mol)

    Returns:
        Concentration in micrograms per cubic meter

        Unit conversion for air quality

    Example:
        >>> ppm_to_ugm3(0.1, 48.0)  # O3  # doctest: +ELLIPSIS
        196.3...
    """
    # ug/m3 = ppm * MW * 1000 / (24.45)
    # 24.45 is molar volume at 25C, 1atm
    return ppm * molecular_weight * 1000 / 24.45


def ugm3_to_ppm(ugm3: float, molecular_weight: float) -> float:
    """Convert gas concentration from ug/m3 to ppm.

    Args:
        ugm3: Concentration in micrograms per cubic meter
        molecular_weight: Molecular weight of gas (g/mol)

    Returns:
        Concentration in parts per million

        Unit conversion for air quality

    Example:
        >>> ugm3_to_ppm(196.0, 48.0)  # O3  # doctest: +ELLIPSIS
        0.099...
    """
    return ugm3 * 24.45 / (molecular_weight * 1000)


def calculate_aqi(pm25: float) -> int:
    """Calculate Air Quality Index from PM2.5 concentration.

    Args:
        pm25: PM2.5 concentration in ug/m3

    Returns:
        AQI value (0-500+)

        AQI calculation utility

    Example:
        >>> calculate_aqi(35.5)
        101
    """
    # EPA AQI breakpoints for PM2.5 (24-hour average)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]

    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if bp_lo <= pm25 <= bp_hi:
            # Linear interpolation
            aqi = ((i_hi - i_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + i_lo
            return round(aqi)

    # Above highest breakpoint
    if pm25 > 500.4:
        return 500

    return 0


def calculate_wqi(
    do_saturation: float,
    bod: float,
    ph: float,
    turbidity: float = 0,
) -> float:
    """Calculate Water Quality Index (simplified).

    Args:
        do_saturation: Dissolved oxygen saturation (%)
        bod: Biochemical oxygen demand (mg/L)
        ph: pH value
        turbidity: Turbidity (NTU, optional)

    Returns:
        WQI score (0-100)

        WQI calculation utility

    Example:
        >>> calculate_wqi(95, 2, 7.2)  # doctest: +ELLIPSIS
        90.66...
    """
    # DO sub-index: 100 at 100% saturation
    do_index = min(do_saturation, 100)

    # BOD sub-index: 100 at 0, decreasing
    bod_index = max(0, 100 - bod * 10)

    # pH sub-index: 100 at pH 7, decreasing away
    ph_index = max(0, 100 - abs(ph - 7) * 15)

    if turbidity > 0:
        turb_index = max(0, 100 - turbidity * 2)
        return (do_index + bod_index + ph_index + turb_index) / 4
    else:
        return (do_index + bod_index + ph_index) / 3


def calculate_bod(
    initial_do: float,
    final_do: float,
    sample_volume: float,
    bottle_volume: float = 300,
) -> float:
    """Calculate Biochemical Oxygen Demand.

    Args:
        initial_do: Initial dissolved oxygen (mg/L)
        final_do: Final dissolved oxygen (mg/L)
        sample_volume: Sample volume (mL)
        bottle_volume: BOD bottle volume (mL, default 300)

    Returns:
        BOD value (mg/L)

        BOD calculation utility

    Example:
        >>> calculate_bod(8.5, 3.2, 30)
        53.0
    """
    return (initial_do - final_do) * (bottle_volume / sample_volume)


def calculate_shannon_diversity(counts: Sequence[int | float]) -> float:
    """Calculate Shannon Diversity Index.

    Args:
        counts: Sequence of species counts

    Returns:
        Shannon diversity index (H')

        Shannon diversity calculation

    Example:
        >>> calculate_shannon_diversity([10, 10, 10, 10])
        1.386...
    """
    total = sum(counts)
    if total == 0:
        return 0.0

    h_prime = 0.0
    for count in counts:
        if count > 0:
            p_i = count / total
            h_prime -= p_i * math.log(p_i)

    return h_prime


def calculate_simpson_index(counts: Sequence[int | float]) -> float:
    """Calculate Simpson's Diversity Index (1-D).

    Args:
        counts: Sequence of species counts

    Returns:
        Simpson's diversity index (1-D)

        Simpson index calculation

    Example:
        >>> calculate_simpson_index([10, 10, 10, 10])
        0.75
    """
    total = sum(counts)
    if total == 0:
        return 0.0

    d = 0.0
    for count in counts:
        p_i = count / total
        d += p_i * p_i

    return 1 - d


def calculate_carbon_equivalent(
    amount: float,
    gas_type: str = "co2",
) -> float:
    """Convert emissions to CO2 equivalent.

    Args:
        amount: Emission amount (kg or tonnes)
        gas_type: Gas type (co2, ch4, n2o, hfc, pfc, sf6)

    Returns:
        CO2 equivalent

        Carbon equivalent calculation

    Example:
        >>> calculate_carbon_equivalent(100, "ch4")
        2800
    """
    gwp_map = {
        "co2": 1,
        "ch4": 28,
        "n2o": 265,
        "hfc": 1430,
        "pfc": 6630,
        "sf6": 23500,
    }

    gwp = gwp_map.get(gas_type.lower(), 1)
    return amount * gwp


def calculate_ecological_footprint(
    carbon_kg: float,
    food_factor: float = 0,
    housing_m2: float = 0,
) -> float:
    """Calculate ecological footprint in global hectares.

    Args:
        carbon_kg: Annual CO2 emissions (kg)
        food_factor: Food consumption factor (optional)
        housing_m2: Housing area in square meters (optional)

    Returns:
        Ecological footprint (global hectares)

        Ecological footprint calculation

    Example:
        >>> calculate_ecological_footprint(5000)
        1.35
    """
    # Carbon: 1 tonne CO2 = ~0.27 gha
    carbon_gha = (carbon_kg / 1000) * 0.27

    footprint = carbon_gha

    if food_factor > 0:
        footprint += food_factor * 0.8

    if housing_m2 > 0:
        footprint += housing_m2 * 0.0001

    return footprint


def format_concentration(
    value: float,
    unit: str = "ug/m3",
    decimals: int = 1,
) -> str:
    """Format concentration value with unit.

    Args:
        value: Concentration value
        unit: Unit string
        decimals: Number of decimal places

    Returns:
        Formatted concentration string

        Concentration formatting

    Example:
        >>> format_concentration(35.56, "ug/m3", 1)
        '35.6 ug/m3'
    """
    return f"{value:.{decimals}f} {unit}"


def calculate_radiative_forcing(
    co2_current: float,
    co2_reference: float = 280.0,
) -> float:
    """Calculate radiative forcing from CO2 concentration.

    Args:
        co2_current: Current CO2 concentration (ppm)
        co2_reference: Reference CO2 concentration (ppm, default 280)

    Returns:
        Radiative forcing (W/m^2)

        Radiative forcing calculation

    Example:
        >>> calculate_radiative_forcing(400, 280)  # doctest: +ELLIPSIS
        1.89...
    """
    return 5.35 * math.log(co2_current / co2_reference)


def calculate_climate_sensitivity(
    radiative_forcing: float,
    climate_feedback: float = 0.8,
) -> float:
    """Calculate temperature response to radiative forcing.

    Args:
        radiative_forcing: Radiative forcing (W/m^2)
        climate_feedback: Climate feedback parameter (W/m^2/K, default 0.8)

    Returns:
        Temperature change (degrees C)

        Climate sensitivity calculation

    Example:
        >>> calculate_climate_sensitivity(3.7, 0.8)
        4.625
    """
    return radiative_forcing / climate_feedback


def calculate_sea_level_rise(
    temp_change: float,
    ocean_depth: float = 3700.0,
    expansion_coeff: float = 0.000214,
) -> float:
    """Calculate sea level rise from thermal expansion.

    Args:
        temp_change: Ocean temperature change (degrees C)
        ocean_depth: Mean ocean depth (meters, default 3700)
        expansion_coeff: Thermal expansion coefficient (1/K, default 0.000214)

    Returns:
        Sea level rise (meters)

        Sea level rise calculation

    Example:
        >>> calculate_sea_level_rise(1.5)  # doctest: +ELLIPSIS
        1.18...
    """
    return temp_change * ocean_depth * expansion_coeff


def calculate_ice_sheet_mass_balance(
    accumulation: float,
    ablation: float,
) -> float:
    """Calculate ice sheet mass balance.

    Args:
        accumulation: Snow accumulation rate (Gt/year)
        ablation: Ice ablation rate (Gt/year)

    Returns:
        Net mass balance (Gt/year)

        Ice sheet mass balance calculation

    Example:
        >>> calculate_ice_sheet_mass_balance(250, 180)
        70
    """
    return accumulation - ablation


def calculate_solar_panel_output(
    irradiance: float,
    area: float,
    efficiency: float,
) -> float:
    """Calculate solar panel power output.

    Args:
        irradiance: Solar irradiance (W/m^2)
        area: Panel area (m^2)
        efficiency: Panel efficiency (0-1)

    Returns:
        Power output (watts)

        Solar panel output calculation

    Example:
        >>> calculate_solar_panel_output(1000, 1.6, 0.18)
        288.0
    """
    return irradiance * area * efficiency


def calculate_wind_turbine_power(
    air_density: float,
    area: float,
    velocity: float,
    power_coeff: float,
) -> float:
    """Calculate wind turbine power output.

    Args:
        air_density: Air density (kg/m^3)
        area: Swept area (m^2)
        velocity: Wind velocity (m/s)
        power_coeff: Power coefficient (0-0.593)

    Returns:
        Power output (watts)

        Wind turbine power calculation

    Example:
        >>> calculate_wind_turbine_power(1.225, 2827, 12, 0.4)  # doctest: +ELLIPSIS
        1194163.2
    """
    return 0.5 * air_density * area * (velocity**3) * power_coeff


def calculate_energy_payback_time(
    energy_input: float,
    annual_output: float,
) -> float:
    """Calculate energy payback time.

    Args:
        energy_input: Total energy input for manufacturing (kWh)
        annual_output: Annual energy output (kWh/year)

    Returns:
        Energy payback time (years)

        EPBT calculation

    Example:
        >>> calculate_energy_payback_time(50000, 2500)
        20.0
    """
    return energy_input / annual_output


def calculate_eroi(
    energy_output: float,
    energy_input: float,
) -> float:
    """Calculate Energy Return on Investment.

    Args:
        energy_output: Total lifetime energy output (kWh)
        energy_input: Total energy input for system (kWh)

    Returns:
        EROI ratio

        EROI calculation

    Example:
        >>> calculate_eroi(500000, 50000)
        10.0
    """
    return energy_output / energy_input


__all__ = [
    "calculate_aqi",
    "calculate_bod",
    "calculate_carbon_equivalent",
    "calculate_climate_sensitivity",
    "calculate_ecological_footprint",
    "calculate_energy_payback_time",
    "calculate_eroi",
    "calculate_ice_sheet_mass_balance",
    "calculate_radiative_forcing",
    "calculate_sea_level_rise",
    "calculate_shannon_diversity",
    "calculate_simpson_index",
    "calculate_solar_panel_output",
    "calculate_wind_turbine_power",
    "calculate_wqi",
    "format_concentration",
    "ppm_to_ugm3",
    "ugm3_to_ppm",
]
