"""Utility functions for civil engineering calculations.

    Civil engineering utility functions

Provides helper functions for:
- Unit conversions (kN/lbf, m/ft, MPa/psi, kN/m to lb/ft)
- Load combination generators (ASCE 7, Eurocode)
- Soil mechanics calculations
- Concrete mix proportioning
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ============================================================================
# Unit Conversions
# ============================================================================


def kn_to_lbf(kn: float) -> float:
    """Convert kilonewtons to pounds force.

    Args:
        kn: Force in kilonewtons

    Returns:
        Force in pounds force

    Example:
        >>> kn_to_lbf(10.0)  # doctest: +ELLIPSIS
        2248.089...
    """
    return kn * 224.80894309971045


def lbf_to_kn(lbf: float) -> float:
    """Convert pounds force to kilonewtons.

    Args:
        lbf: Force in pounds force

    Returns:
        Force in kilonewtons

    Example:
        >>> lbf_to_kn(1000.0)  # doctest: +ELLIPSIS
        4.448...
    """
    return lbf * 0.0044482216152605


def m_to_ft(m: float) -> float:
    """Convert meters to feet.

    Args:
        m: Length in meters

    Returns:
        Length in feet

    Example:
        >>> m_to_ft(10.0)  # doctest: +ELLIPSIS
        32.8083...
    """
    return m * 3.280839895013123


def ft_to_m(ft: float) -> float:
    """Convert feet to meters.

    Args:
        ft: Length in feet

    Returns:
        Length in meters

    Example:
        >>> ft_to_m(100.0)
        30.48
    """
    return ft * 0.3048


def mpa_to_psi(mpa: float) -> float:
    """Convert megapascals to pounds per square inch.

    Args:
        mpa: Pressure in megapascals

    Returns:
        Pressure in psi

    Example:
        >>> mpa_to_psi(10.0)  # doctest: +ELLIPSIS
        1450.3773...
    """
    return mpa * 145.03773800721997


def psi_to_mpa(psi: float) -> float:
    """Convert pounds per square inch to megapascals.

    Args:
        psi: Pressure in psi

    Returns:
        Pressure in megapascals

    Example:
        >>> psi_to_mpa(1000.0)  # doctest: +ELLIPSIS
        6.8947...
    """
    return psi * 0.006894757293168361


def knpm_to_lbpft(knpm: float) -> float:
    """Convert kilonewtons per meter to pounds per foot.

    Args:
        knpm: Load in kN/m

    Returns:
        Load in lb/ft

    Example:
        >>> knpm_to_lbpft(10.0)  # doctest: +ELLIPSIS
        685.2177...
    """
    return knpm * 68.52177857954263


def lbpft_to_knpm(lbpft: float) -> float:
    """Convert pounds per foot to kilonewtons per meter.

    Args:
        lbpft: Load in lb/ft

    Returns:
        Load in kN/m

    Example:
        >>> lbpft_to_knpm(100.0)  # doctest: +ELLIPSIS
        1.4593...
    """
    return lbpft * 0.014593902937206283


# ============================================================================
# Load Combinations
# ============================================================================


class LoadCombinationCode(str, Enum):
    """Building code standard for load combinations."""

    ASCE_7_16 = "ASCE_7_16"
    ASCE_7_22 = "ASCE_7_22"
    EUROCODE = "Eurocode"
    IBC_2018 = "IBC_2018"
    IBC_2021 = "IBC_2021"


@dataclass
class LoadCombination:
    """Load combination with factors.

    Attributes:
        name: Combination identifier (e.g., "1.4D")
        description: Human-readable description
        dead_factor: Dead load factor
        live_factor: Live load factor
        wind_factor: Wind load factor
        seismic_factor: Seismic load factor
        snow_factor: Snow load factor
    """

    name: str
    description: str
    dead_factor: float = 0.0
    live_factor: float = 0.0
    wind_factor: float = 0.0
    seismic_factor: float = 0.0
    snow_factor: float = 0.0


def get_load_combinations(
    code: LoadCombinationCode = LoadCombinationCode.ASCE_7_16,
) -> list[LoadCombination]:
    """Get load combinations for specified building code.

    Args:
        code: Building code standard

    Returns:
        List of LoadCombination objects

    Example:
        >>> combos = get_load_combinations(LoadCombinationCode.ASCE_7_16)
        >>> len(combos)
        7
    """
    if code in (LoadCombinationCode.ASCE_7_16, LoadCombinationCode.ASCE_7_22):
        return _get_asce7_combinations()
    elif code == LoadCombinationCode.EUROCODE:
        return _get_eurocode_combinations()
    elif code in (LoadCombinationCode.IBC_2018, LoadCombinationCode.IBC_2021):
        return _get_ibc_combinations()
    else:
        return _get_asce7_combinations()


def _get_asce7_combinations() -> list[LoadCombination]:
    """Get ASCE 7 load combinations (Strength Design)."""
    return [
        LoadCombination(
            name="1.4D",
            description="Dead load only",
            dead_factor=1.4,
        ),
        LoadCombination(
            name="1.2D + 1.6L + 0.5(Lr or S)",
            description="Dead + Live + Roof/Snow",
            dead_factor=1.2,
            live_factor=1.6,
            snow_factor=0.5,
        ),
        LoadCombination(
            name="1.2D + 1.6(Lr or S) + (L or 0.5W)",
            description="Dead + Roof/Snow + Live/Wind",
            dead_factor=1.2,
            live_factor=0.5,
            snow_factor=1.6,
            wind_factor=0.5,
        ),
        LoadCombination(
            name="1.2D + 1.0W + L + 0.5(Lr or S)",
            description="Dead + Wind + Live + Roof/Snow",
            dead_factor=1.2,
            live_factor=1.0,
            wind_factor=1.0,
            snow_factor=0.5,
        ),
        LoadCombination(
            name="1.2D + 1.0E + L + 0.2S",
            description="Dead + Seismic + Live + Snow",
            dead_factor=1.2,
            live_factor=1.0,
            seismic_factor=1.0,
            snow_factor=0.2,
        ),
        LoadCombination(
            name="0.9D + 1.0W",
            description="Dead + Wind (uplift)",
            dead_factor=0.9,
            wind_factor=1.0,
        ),
        LoadCombination(
            name="0.9D + 1.0E",
            description="Dead + Seismic (uplift)",
            dead_factor=0.9,
            seismic_factor=1.0,
        ),
    ]


def _get_eurocode_combinations() -> list[LoadCombination]:
    """Get Eurocode load combinations (Ultimate Limit State)."""
    return [
        LoadCombination(
            name="1.35D",
            description="Permanent actions only",
            dead_factor=1.35,
        ),
        LoadCombination(
            name="1.35D + 1.5L",
            description="Permanent + Variable",
            dead_factor=1.35,
            live_factor=1.5,
        ),
        LoadCombination(
            name="1.35D + 1.5W + 0.75L",
            description="Permanent + Wind + Variable",
            dead_factor=1.35,
            live_factor=0.75,
            wind_factor=1.5,
        ),
        LoadCombination(
            name="1.0D + 1.5W",
            description="Permanent + Wind (favorable)",
            dead_factor=1.0,
            wind_factor=1.5,
        ),
        LoadCombination(
            name="1.0D + 1.0E + 0.3L",
            description="Permanent + Seismic + Variable",
            dead_factor=1.0,
            live_factor=0.3,
            seismic_factor=1.0,
        ),
    ]


def _get_ibc_combinations() -> list[LoadCombination]:
    """Get IBC load combinations (similar to ASCE 7)."""
    return _get_asce7_combinations()


# ============================================================================
# Soil Mechanics
# ============================================================================


def bearing_capacity_factors(phi: float) -> tuple[float, float, float]:
    """Calculate Terzaghi bearing capacity factors.

    Args:
        phi: Angle of internal friction (degrees)

    Returns:
        Tuple of (Nc, Nq, Ngamma) bearing capacity factors

    Example:
        >>> nc, nq, ng = bearing_capacity_factors(30.0)
        >>> round(nc, 2)
        30.14
    """
    import math

    phi_rad = math.radians(phi)

    # Nq factor
    Nq = (
        math.exp(math.pi * math.tan(phi_rad))
        * (math.tan(math.pi / 4 + phi_rad / 2)) ** 2
    )

    # Nc factor
    Nc = (Nq - 1) / math.tan(phi_rad) if phi > 0 else 5.14

    # Ngamma factor (Terzaghi's approximation)
    Ngamma = 2 * (Nq + 1) * math.tan(phi_rad)

    return Nc, Nq, Ngamma


def consolidation_settlement(
    H: float,
    Cc: float,
    e0: float,
    p0: float,
    delta_p: float,
) -> float:
    """Calculate consolidation settlement using Terzaghi's theory.

    Args:
        H: Layer thickness (mm)
        Cc: Compression index
        e0: Initial void ratio
        p0: Initial effective stress (kPa)
        delta_p: Stress increase (kPa)

    Returns:
        Settlement (mm)

    Example:
        >>> s = consolidation_settlement(5000, 0.3, 0.8, 100, 50)
        >>> round(s, 1)
        146.7
    """
    import math

    return H * Cc / (1 + e0) * math.log10((p0 + delta_p) / p0)


# ============================================================================
# Concrete Mix Design
# ============================================================================


@dataclass
class ConcreteMix:
    """Concrete mix proportions.

    Attributes:
        cement: Cement content (kg/m³)
        water: Water content (kg/m³)
        fine_aggregate: Fine aggregate content (kg/m³)
        coarse_aggregate: Coarse aggregate content (kg/m³)
        wc_ratio: Water-cement ratio
        target_strength: Target 28-day strength (MPa)
    """

    cement: float
    water: float
    fine_aggregate: float
    coarse_aggregate: float
    wc_ratio: float
    target_strength: float


def calculate_cement_content(
    target_strength: float,
    wc_ratio: float,
) -> float:
    """Estimate cement content from target strength and w/c ratio.

    Uses empirical Abrams' law: f'c = A / B^(w/c)

    Args:
        target_strength: Target 28-day strength (MPa)
        wc_ratio: Water-cement ratio

    Returns:
        Cement content (kg/m³)

    Example:
        >>> cement = calculate_cement_content(25.0, 0.5)
        >>> round(cement)
        350
    """
    # Typical relationship for normal weight concrete
    # Assuming standard water content of 175 kg/m³
    water_content = 175.0
    cement = water_content / wc_ratio
    return cement


def design_concrete_mix(
    target_strength: float,
    max_wc_ratio: float = 0.6,
    slump: int = 75,
) -> ConcreteMix:
    """Design basic concrete mix proportions.

    Args:
        target_strength: Target 28-day strength (MPa)
        max_wc_ratio: Maximum water-cement ratio
        slump: Target slump (mm)

    Returns:
        ConcreteMix with proportions

    Example:
        >>> mix = design_concrete_mix(25.0, 0.5, 75)
        >>> round(mix.cement)
        350
    """
    # Calculate required w/c ratio for target strength
    # Using Abrams' law approximation
    import math

    # Empirical constants
    A = 100.0  # Strength constant
    B = 3.0  # Base constant

    wc_ratio = math.log(A / target_strength) / math.log(B)
    wc_ratio = min(wc_ratio, max_wc_ratio)

    # Water content based on slump and max aggregate size
    water_content = 175.0  # kg/m³ for 75mm slump, 20mm aggregate

    # Cement content
    cement = water_content / wc_ratio

    # Total aggregate = 1 m³ - (cement + water volumes) - air
    cement_volume = cement / 3150  # SG of cement = 3.15
    water_volume = water_content / 1000  # SG of water = 1.0
    air_volume = 0.02  # 2% entrained air
    aggregate_volume = 1.0 - cement_volume - water_volume - air_volume

    # Fine/coarse aggregate ratio (typically 40/60)
    fine_ratio = 0.40
    coarse_ratio = 0.60

    fine_aggregate = aggregate_volume * fine_ratio * 2650  # SG = 2.65
    coarse_aggregate = aggregate_volume * coarse_ratio * 2700  # SG = 2.70

    return ConcreteMix(
        cement=cement,
        water=water_content,
        fine_aggregate=fine_aggregate,
        coarse_aggregate=coarse_aggregate,
        wc_ratio=wc_ratio,
        target_strength=target_strength,
    )


# ============================================================================
# Structural Calculations
# ============================================================================


def beam_self_weight(
    width: float,
    height: float,
    length: float,
    density: float = 2400.0,
) -> float:
    """Calculate beam self-weight as distributed load.

    Args:
        width: Beam width (mm)
        height: Beam height (mm)
        length: Beam length (mm)
        density: Material density (kg/m³), default concrete

    Returns:
        Distributed load (kN/m)

    Example:
        >>> w = beam_self_weight(300, 500, 6000)
        >>> round(w, 2)
        3.53
    """
    # Convert to meters
    area = (width / 1000) * (height / 1000)  # m²
    # Weight = Area * Length * Density * g / Length
    # = Area * Density * g
    g = 9.81  # m/s²
    return area * density * g / 1000  # kN/m


__all__ = [
    # Concrete mix design
    "ConcreteMix",
    "LoadCombination",
    # Load combinations
    "LoadCombinationCode",
    # Structural calculations
    "beam_self_weight",
    # Soil mechanics
    "bearing_capacity_factors",
    "calculate_cement_content",
    "consolidation_settlement",
    "design_concrete_mix",
    "ft_to_m",
    "get_load_combinations",
    # Unit conversions
    "kn_to_lbf",
    "knpm_to_lbpft",
    "lbf_to_kn",
    "lbpft_to_knpm",
    "m_to_ft",
    "mpa_to_psi",
    "psi_to_mpa",
]
