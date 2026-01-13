"""Physics domain utility functions.

Physics utility functions for calculations
BATCH-5: Physics domain creation
"""

from __future__ import annotations

import math


def speed_of_light() -> float:
    """Get speed of light in vacuum.

    Returns:
        Speed of light (m/s)

    Example:
        >>> speed_of_light()
        299792458.0
    """
    return 299792458.0  # m/s


def planck_constant() -> float:
    """Get Planck constant.

    Returns:
        Planck constant (J·s)

    Example:
        >>> planck_constant()
        6.62607015e-34
    """
    return 6.62607015e-34  # J·s


def reduced_planck_constant() -> float:
    """Get reduced Planck constant (ℏ = h/2π).

    Returns:
        Reduced Planck constant (J·s)

    Example:
        >>> reduced_planck_constant()
        1.054571817e-34
    """
    return planck_constant() / (2 * math.pi)


def gravitational_constant() -> float:
    """Get gravitational constant.

    Returns:
        Gravitational constant (N·m²/kg²)

    Example:
        >>> gravitational_constant()
        6.6743e-11
    """
    return 6.6743e-11  # N·m²/kg²


def electron_mass() -> float:
    """Get electron rest mass.

    Returns:
        Electron mass (kg)

    Example:
        >>> electron_mass()
        9.1093837015e-31
    """
    return 9.1093837015e-31  # kg


def proton_mass() -> float:
    """Get proton rest mass.

    Returns:
        Proton mass (kg)

    Example:
        >>> proton_mass()
        1.67262192369e-27
    """
    return 1.67262192369e-27  # kg


def elementary_charge() -> float:
    """Get elementary charge.

    Returns:
        Elementary charge (C)

    Example:
        >>> elementary_charge()
        1.602176634e-19
    """
    return 1.602176634e-19  # C


def convert_ev_to_joules(energy_ev: float) -> float:
    """Convert energy from electronvolts to joules.

    Args:
        energy_ev: Energy in electronvolts (eV)

    Returns:
        Energy in joules (J)

    Example:
        >>> convert_ev_to_joules(1.0)
        1.602176634e-19
    """
    return energy_ev * elementary_charge()


def convert_joules_to_ev(energy_j: float) -> float:
    """Convert energy from joules to electronvolts.

    Args:
        energy_j: Energy in joules (J)

    Returns:
        Energy in electronvolts (eV)

    Example:
        >>> convert_joules_to_ev(1.602176634e-19)
        1.0
    """
    return energy_j / elementary_charge()


def wavelength_to_frequency(wavelength: float) -> float:
    """Convert wavelength to frequency.

    Args:
        wavelength: Wavelength (m)

    Returns:
        Frequency (Hz)

    Example:
        >>> wavelength_to_frequency(500e-9)
        599584916000000.0
    """
    return speed_of_light() / wavelength


def frequency_to_wavelength(frequency: float) -> float:
    """Convert frequency to wavelength.

    Args:
        frequency: Frequency (Hz)

    Returns:
        Wavelength (m)

    Example:
        >>> frequency_to_wavelength(5e14)
        5.99584916e-07
    """
    return speed_of_light() / frequency


def calculate_escape_velocity(mass: float, radius: float) -> float:
    """Calculate escape velocity from celestial body.

    Args:
        mass: Mass of body (kg)
        radius: Radius of body (m)

    Returns:
        Escape velocity (m/s)

    Example:
        >>> calculate_escape_velocity(5.972e24, 6.371e6)
        11181.821296822126
    """
    return math.sqrt(2 * gravitational_constant() * mass / radius)


def calculate_schwarzschild_radius(mass: float) -> float:
    """Calculate Schwarzschild radius (black hole event horizon).

    Args:
        mass: Mass (kg)

    Returns:
        Schwarzschild radius (m)

    Example:
        >>> calculate_schwarzschild_radius(1.989e30)
        2953.250077322729
    """
    return 2 * gravitational_constant() * mass / speed_of_light() ** 2


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians.

    Args:
        degrees: Angle in degrees

    Returns:
        Angle in radians

    Example:
        >>> degrees_to_radians(180)
        3.141592653589793
    """
    return degrees * math.pi / 180


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees.

    Args:
        radians: Angle in radians

    Returns:
        Angle in degrees

    Example:
        >>> radians_to_degrees(math.pi)
        180.0
    """
    return radians * 180 / math.pi


__all__ = [
    "calculate_escape_velocity",
    "calculate_schwarzschild_radius",
    "convert_ev_to_joules",
    "convert_joules_to_ev",
    "degrees_to_radians",
    "electron_mass",
    "elementary_charge",
    "frequency_to_wavelength",
    "gravitational_constant",
    "planck_constant",
    "proton_mass",
    "radians_to_degrees",
    "reduced_planck_constant",
    "speed_of_light",
    "wavelength_to_frequency",
]
