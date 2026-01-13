"""Chemistry domain utility functions.

Chemistry utility functions for calculations
BATCH-4: Chemistry domain creation
"""

from __future__ import annotations


def calculate_molecular_weight(formula: str) -> float:
    """Calculate molecular weight from chemical formula.

    Args:
        formula: Chemical formula string (e.g., "H2O", "NaCl")

    Returns:
        Molecular weight in g/mol

    Example:
        >>> calculate_molecular_weight("H2O")
        18.015
    """
    # Atomic weights (simplified)
    atomic_weights = {
        "H": 1.008,
        "C": 12.011,
        "N": 14.007,
        "O": 15.999,
        "Na": 22.990,
        "Cl": 35.453,
        "S": 32.065,
        "P": 30.974,
    }

    # Simple parser for basic formulas
    total_weight = 0.0
    i = 0
    while i < len(formula):
        # Get element symbol (1 or 2 characters)
        if i + 1 < len(formula) and formula[i + 1].islower():
            element = formula[i : i + 2]
            i += 2
        else:
            element = formula[i]
            i += 1

        # Get count
        count_str = ""
        while i < len(formula) and formula[i].isdigit():
            count_str += formula[i]
            i += 1
        count = int(count_str) if count_str else 1

        # Add to total
        if element in atomic_weights:
            total_weight += atomic_weights[element] * count

    return total_weight


def calculate_dilution_factor(initial_conc: float, final_conc: float) -> float:
    """Calculate dilution factor.

    Args:
        initial_conc: Initial concentration
        final_conc: Final concentration

    Returns:
        Dilution factor

    Example:
        >>> calculate_dilution_factor(10.0, 1.0)
        10.0
    """
    if final_conc == 0:
        msg = "Final concentration cannot be zero"
        raise ValueError(msg)
    if final_conc < 0 or initial_conc < 0:
        msg = "Concentrations cannot be negative"
        raise ValueError(msg)
    return initial_conc / final_conc


def calculate_concentration_from_absorbance(
    absorbance: float,
    extinction_coef: float,
    path_length: float = 1.0,
) -> float:
    """Calculate concentration from absorbance using Beer's law.

    Args:
        absorbance: Absorbance value
        extinction_coef: Molar extinction coefficient (M⁻¹cm⁻¹)
        path_length: Path length in cm (default: 1.0)

    Returns:
        Concentration in M

    Example:
        >>> calculate_concentration_from_absorbance(0.5, 1000, 1.0)
        0.0005
    """
    if extinction_coef == 0 or path_length == 0:
        msg = "Extinction coefficient and path length must be non-zero"
        raise ValueError(msg)
    return absorbance / (extinction_coef * path_length)


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius.

    Args:
        kelvin: Temperature in Kelvin

    Returns:
        Temperature in Celsius

    Example:
        >>> kelvin_to_celsius(298.15)
        25.0
    """
    return kelvin - 273.15


def celsius_to_kelvin(celsius: float) -> float:
    """Convert Celsius to Kelvin.

    Args:
        celsius: Temperature in Celsius

    Returns:
        Temperature in Kelvin

    Example:
        >>> celsius_to_kelvin(25.0)
        298.15
    """
    return celsius + 273.15


def calculate_ph_from_concentration(h_conc: float) -> float:
    """Calculate pH from H+ concentration.

    Args:
        h_conc: H+ concentration in M

    Returns:
        pH value

    Example:
        >>> calculate_ph_from_concentration(1e-7)
        7.0
    """
    import math

    if h_conc <= 0:
        msg = "H+ concentration must be positive"
        raise ValueError(msg)
    return -math.log10(h_conc)


def calculate_concentration_from_ph(pH: float) -> float:
    """Calculate H+ concentration from pH.

    Args:
        pH: pH value

    Returns:
        H+ concentration in M

    Example:
        >>> calculate_concentration_from_ph(7.0)
        1e-07
    """
    return 10 ** (-pH)


def format_scientific_notation(value: float, precision: int = 3) -> str:
    """Format number in scientific notation.

    Args:
        value: Number to format
        precision: Decimal places (default: 3)

    Returns:
        Formatted string

    Example:
        >>> format_scientific_notation(0.00012345, 2)
        '1.23E-04'
    """
    return f"{value:.{precision}E}"


__all__ = [
    "calculate_concentration_from_absorbance",
    "calculate_concentration_from_ph",
    "calculate_dilution_factor",
    "calculate_molecular_weight",
    "calculate_ph_from_concentration",
    "celsius_to_kelvin",
    "format_scientific_notation",
    "kelvin_to_celsius",
]
