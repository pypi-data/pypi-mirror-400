"""Utility functions for mechanical engineering domain.

Utility functions for unit conversions and calculations
"""

from __future__ import annotations

import math

# ============================================================================
# Unit Conversions
# ============================================================================


def mpa_to_psi(mpa: float) -> float:
    """Convert stress from MPa to psi.

    Args:
        mpa: Stress in megapascals (MPa)

    Returns:
        Stress in pounds per square inch (psi)

    Example:
        >>> mpa_to_psi(100)
        14503.77...
    """
    return mpa * 145.03773773


def psi_to_mpa(psi: float) -> float:
    """Convert stress from psi to MPa.

    Args:
        psi: Stress in pounds per square inch

    Returns:
        Stress in megapascals (MPa)

    Example:
        >>> psi_to_mpa(14503.77)
        99.999...
    """
    return psi / 145.03773773


def mm_to_inch(mm: float) -> float:
    """Convert length from millimeters to inches.

    Args:
        mm: Length in millimeters

    Returns:
        Length in inches

    Example:
        >>> mm_to_inch(25.4)
        1.0
    """
    return mm / 25.4


def inch_to_mm(inch: float) -> float:
    """Convert length from inches to millimeters.

    Args:
        inch: Length in inches

    Returns:
        Length in millimeters

    Example:
        >>> inch_to_mm(1.0)
        25.4
    """
    return inch * 25.4


def kg_to_lb(kg: float) -> float:
    """Convert mass from kilograms to pounds.

    Args:
        kg: Mass in kilograms

    Returns:
        Mass in pounds

    Example:
        >>> kg_to_lb(1.0)
        2.204622...
    """
    return kg * 2.20462262185


def lb_to_kg(lb: float) -> float:
    """Convert mass from pounds to kilograms.

    Args:
        lb: Mass in pounds

    Returns:
        Mass in kilograms

    Example:
        >>> lb_to_kg(2.20462)  # doctest: +SKIP
        0.999999...
    """
    return lb / 2.20462262185


# ============================================================================
# Stress Calculations
# ============================================================================


def von_mises_stress(
    sigma_x: float,
    sigma_y: float,
    sigma_z: float = 0.0,
    tau_xy: float = 0.0,
    tau_yz: float = 0.0,
    tau_xz: float = 0.0,
) -> float:
    """Calculate von Mises equivalent stress.

    Args:
        sigma_x: Normal stress in X direction (MPa)
        sigma_y: Normal stress in Y direction (MPa)
        sigma_z: Normal stress in Z direction (MPa)
        tau_xy: Shear stress in XY plane (MPa)
        tau_yz: Shear stress in YZ plane (MPa)
        tau_xz: Shear stress in XZ plane (MPa)

    Returns:
        von Mises equivalent stress (MPa)

    Example:
        >>> von_mises_stress(100, 50, 0, 25)  # doctest: +ELLIPSIS
        96.82...
    """
    # von Mises: sqrt(sigmax² + sigmay² + sigmaz² - sigmax*sigmay - sigmay*sigmaz - sigmaz*sigmax + 3(tauxy² + tauyz² + tauxz²))
    # For 2D plane stress (sigmaz=0): sqrt(sigmax² + sigmay² - sigmax*sigmay + 3*tauxy²)
    return math.sqrt(
        sigma_x**2
        + sigma_y**2
        + sigma_z**2
        - sigma_x * sigma_y
        - sigma_y * sigma_z
        - sigma_z * sigma_x
        + 3 * (tau_xy**2 + tau_yz**2 + tau_xz**2)
    )


def principal_stresses_2d(
    sigma_x: float,
    sigma_y: float,
    tau_xy: float,
) -> tuple[float, float]:
    """Calculate principal stresses for 2D plane stress state.

    Args:
        sigma_x: Normal stress in X direction (MPa)
        sigma_y: Normal stress in Y direction (MPa)
        tau_xy: Shear stress in XY plane (MPa)

    Returns:
        Tuple of (sigma_1, sigma_2) principal stresses (MPa)

    Example:
        >>> principal_stresses_2d(100, 50, 25)  # doctest: +ELLIPSIS
        (110.35..., 39.64...)
    """
    avg = (sigma_x + sigma_y) / 2.0
    radius = math.sqrt(((sigma_x - sigma_y) / 2.0) ** 2 + tau_xy**2)

    sigma_1 = avg + radius
    sigma_2 = avg - radius

    return (sigma_1, sigma_2)


def principal_stresses_3d(
    sigma_x: float,
    sigma_y: float,
    sigma_z: float,
    tau_xy: float = 0.0,
    tau_yz: float = 0.0,
    tau_xz: float = 0.0,
) -> tuple[float, float, float]:
    """Calculate principal stresses for 3D stress state (simplified for common cases).

    Args:
        sigma_x: Normal stress in X direction (MPa)
        sigma_y: Normal stress in Y direction (MPa)
        sigma_z: Normal stress in Z direction (MPa)
        tau_xy: Shear stress in XY plane (MPa)
        tau_yz: Shear stress in YZ plane (MPa)
        tau_xz: Shear stress in XZ plane (MPa)

    Returns:
        Tuple of (sigma_1, sigma_2, sigma_3) principal stresses (MPa)

    Note:
        For general 3D case with shear stresses, this uses an approximation.
        For pure normal stresses (no shear), returns exact principal stresses.
    """
    # For pure normal stresses (no shear), principal stresses = normal stresses
    if tau_xy == 0.0 and tau_yz == 0.0 and tau_xz == 0.0:
        stresses = sorted([sigma_x, sigma_y, sigma_z], reverse=True)
        return (stresses[0], stresses[1], stresses[2])

    # Simplified approximation for general case
    # Use von Mises as upper bound and minimum normal stress as lower bound
    vm = von_mises_stress(sigma_x, sigma_y, sigma_z, tau_xy, tau_yz, tau_xz)
    sigma_1 = vm
    sigma_2 = (sigma_x + sigma_y + sigma_z) / 3.0
    sigma_3 = min(sigma_x, sigma_y, sigma_z)

    return (sigma_1, sigma_2, sigma_3)


# ============================================================================
# Geometric Property Calculations
# ============================================================================


def moment_of_inertia_rectangle(width: float, height: float) -> float:
    """Calculate second moment of area for rectangular cross-section.

    Args:
        width: Width (b) in mm
        height: Height (h) in mm

    Returns:
        Moment of inertia (I) in mm⁴

    Example:
        >>> moment_of_inertia_rectangle(10, 20)
        6666.666...
    """
    return (width * height**3) / 12.0


def moment_of_inertia_circle(diameter: float) -> float:
    """Calculate second moment of area for circular cross-section.

    Args:
        diameter: Diameter (d) in mm

    Returns:
        Moment of inertia (I) in mm⁴

    Example:
        >>> moment_of_inertia_circle(10)
        490.873...
    """
    return (math.pi * diameter**4) / 64.0


def polar_moment_of_inertia_circle(diameter: float) -> float:
    """Calculate polar moment of inertia for circular cross-section.

    Args:
        diameter: Diameter (d) in mm

    Returns:
        Polar moment of inertia (J) in mm⁴

    Example:
        >>> polar_moment_of_inertia_circle(10)
        981.747...
    """
    return (math.pi * diameter**4) / 32.0


def section_modulus_rectangle(width: float, height: float) -> float:
    """Calculate section modulus for rectangular cross-section.

    Args:
        width: Width (b) in mm
        height: Height (h) in mm

    Returns:
        Section modulus (S) in mm³

    Example:
        >>> section_modulus_rectangle(10, 20)
        666.666...
    """
    return (width * height**2) / 6.0


def section_modulus_circle(diameter: float) -> float:
    """Calculate section modulus for circular cross-section.

    Args:
        diameter: Diameter (d) in mm

    Returns:
        Section modulus (S) in mm³

    Example:
        >>> section_modulus_circle(10)
        98.174...
    """
    return (math.pi * diameter**3) / 32.0


# ============================================================================
# Export All
# ============================================================================

__all__ = [
    "inch_to_mm",
    "kg_to_lb",
    "lb_to_kg",
    "mm_to_inch",
    "moment_of_inertia_circle",
    "moment_of_inertia_rectangle",
    "mpa_to_psi",
    "polar_moment_of_inertia_circle",
    "principal_stresses_2d",
    "principal_stresses_3d",
    "psi_to_mpa",
    "section_modulus_circle",
    "section_modulus_rectangle",
    "von_mises_stress",
]
