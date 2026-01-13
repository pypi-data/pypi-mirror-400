"""Utility functions for electrical engineering domain.

Helper functions for EE domain
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


def parse_si_prefix(value: str) -> float:
    """Parse value with SI prefix (e.g., "10k", "100mA", "3.3V").

    Args:
        value: String value with optional SI prefix

    Returns:
        Numeric value in base units

    Example:
        >>> parse_si_prefix("10k")
        10000.0
        >>> parse_si_prefix("100mA")
        0.1
        >>> parse_si_prefix("3.3V")
        3.3
    """
    # SI prefixes
    prefixes = {
        "T": 1e12,  # tera
        "G": 1e9,  # giga
        "M": 1e6,  # mega
        "k": 1e3,  # kilo
        "m": 1e-3,  # milli
        "u": 1e-6,  # micro (μ)
        "μ": 1e-6,  # micro
        "n": 1e-9,  # nano
        "p": 1e-12,  # pico
        "f": 1e-15,  # femto
    }

    # Remove whitespace
    value = value.strip()

    # Extract numeric part and suffix
    match = re.match(r"([-+]?[0-9]*\.?[0-9]+)([a-zA-Zμ]*)", value)
    if not match:
        msg = f"Invalid value format: {value}"
        raise ValueError(msg)

    num_str, suffix = match.groups()
    num = float(num_str)

    # Check for SI prefix (first character of suffix)
    if suffix and suffix[0] in prefixes:
        num *= prefixes[suffix[0]]

    return num


def format_si_prefix(
    value: float,
    unit: str = "",
    precision: int = 2,
) -> str:
    """Format value with appropriate SI prefix.

    Args:
        value: Numeric value to format
        unit: Unit symbol (e.g., "Ω", "V", "A")
        precision: Number of decimal places

    Returns:
        Formatted string with SI prefix

    Example:
        >>> format_si_prefix(10000, "Ω")
        '10.00kΩ'
        >>> format_si_prefix(0.001, "A")
        '1.00mA'
    """
    if value == 0:
        return f"0{unit}"

    # SI prefixes in order
    prefixes = [
        (1e12, "T"),
        (1e9, "G"),
        (1e6, "M"),
        (1e3, "k"),
        (1, ""),
        (1e-3, "m"),
        (1e-6, "μ"),
        (1e-9, "n"),
        (1e-12, "p"),
        (1e-15, "f"),
    ]

    abs_value = abs(value)
    for scale, prefix in prefixes:
        if abs_value >= scale:
            scaled = value / scale
            return f"{scaled:.{precision}f}{prefix}{unit}"

    # Fallback for very small values
    return f"{value:.{precision}e}{unit}"


def calculate_parallel_resistance(resistances: Sequence[float]) -> float:
    """Calculate total parallel resistance.

    Args:
        resistances: List of resistance values in ohms

    Returns:
        Total parallel resistance in ohms

    Raises:
        ValueError: If any resistance is zero or negative

    Example:
        >>> calculate_parallel_resistance([100, 100])
        50.0
        >>> calculate_parallel_resistance([1000, 2000, 3000])
        545.45...
    """
    if not resistances:
        msg = "At least one resistance value required"
        raise ValueError(msg)

    if any(r <= 0 for r in resistances):
        msg = "All resistances must be positive"
        raise ValueError(msg)

    # 1/R_total = 1/R1 + 1/R2 + ...
    reciprocal_sum = sum(1.0 / r for r in resistances)
    return 1.0 / reciprocal_sum


def calculate_series_resistance(resistances: Sequence[float]) -> float:
    """Calculate total series resistance.

    Args:
        resistances: List of resistance values in ohms

    Returns:
        Total series resistance in ohms

    Example:
        >>> calculate_series_resistance([100, 100])
        200
        >>> calculate_series_resistance([1000, 2000, 3000])
        6000
    """
    return sum(resistances)


def calculate_power_dissipation(voltage: float, current: float) -> float:
    """Calculate power dissipation: P = V * I.

    Args:
        voltage: Voltage in volts
        current: Current in amperes

    Returns:
        Power in watts

    Example:
        >>> calculate_power_dissipation(5.0, 0.1)
        0.5
    """
    return voltage * current


def calculate_voltage_drop(
    current: float,
    resistance_per_meter: float,
    length_mm: float,
) -> float:
    """Calculate voltage drop in a trace/wire.

    Args:
        current: Current in amperes
        resistance_per_meter: Resistance per meter in ohms/m
        length_mm: Length in millimeters

    Returns:
        Voltage drop in volts

    Example:
        >>> calculate_voltage_drop(2.0, 0.05, 1000)  # 1m trace
        0.1
    """
    length_m = length_mm / 1000.0
    return current * resistance_per_meter * length_m


def calculate_thermal_resistance(temp_rise: float, power: float) -> float:
    """Calculate thermal resistance: θ = ΔT / P.

    Args:
        temp_rise: Temperature rise in degrees Celsius
        power: Power dissipation in watts

    Returns:
        Thermal resistance in °C/W

    Raises:
        ValueError: If power is zero

    Example:
        >>> calculate_thermal_resistance(50, 10)
        5.0
    """
    if power == 0:
        msg = "Power cannot be zero"
        raise ValueError(msg)
    return temp_rise / power


def calculate_propagation_delay(length_mm: float, velocity_mm_per_s: float) -> float:
    """Calculate signal propagation delay.

    Args:
        length_mm: Trace length in millimeters
        velocity_mm_per_s: Signal velocity in mm/s (typically 1.5-2e8 for FR4)

    Returns:
        Propagation delay in seconds

    Example:
        >>> calculate_propagation_delay(100, 2e8)  # 100mm at c/1.5
        5e-07
    """
    return length_mm / velocity_mm_per_s


def calculate_characteristic_impedance(
    inductance_per_length: float,
    capacitance_per_length: float,
) -> float:
    """Calculate characteristic impedance: Z0 = sqrt(L/C).

    Args:
        inductance_per_length: Inductance per unit length (H/m)
        capacitance_per_length: Capacitance per unit length (F/m)

    Returns:
        Characteristic impedance in ohms

    Example:
        >>> calculate_characteristic_impedance(2.5e-7, 1e-10)
        50.0
    """
    return math.sqrt(inductance_per_length / capacitance_per_length)


def group_by_value(
    components: Sequence[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group components by value (for BOM consolidation).

    Args:
        components: List of component dictionaries with 'value' key

    Returns:
        Dictionary mapping values to lists of components

    Example:
        >>> components = [
        ...     {"ref": "R1", "value": "10k"},
        ...     {"ref": "R2", "value": "10k"},
        ...     {"ref": "C1", "value": "100nF"},
        ... ]
        >>> grouped = group_by_value(components)
        >>> len(grouped["10k"])
        2
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    for comp in components:
        value = comp.get("value", "")
        if value not in groups:
            groups[value] = []
        groups[value].append(comp)
    return groups


def expand_ref_designators(ref_range: str) -> list[str]:
    """Expand reference designator range (e.g., "R1-R10" -> ["R1", "R2", ...]).

    Args:
        ref_range: Reference designator or range

    Returns:
        List of individual reference designators

    Example:
        >>> expand_ref_designators("R1-R5")
        ['R1', 'R2', 'R3', 'R4', 'R5']
        >>> expand_ref_designators("C10")
        ['C10']
    """
    # Check for range format: "R1-R10"
    range_match = re.match(r"([A-Z]+)(\d+)-\1(\d+)", ref_range)
    if range_match:
        prefix, start, end = range_match.groups()
        start_num = int(start)
        end_num = int(end)
        return [f"{prefix}{i}" for i in range(start_num, end_num + 1)]

    # Single reference
    return [ref_range]


__all__ = [
    "calculate_characteristic_impedance",
    "calculate_parallel_resistance",
    "calculate_power_dissipation",
    "calculate_propagation_delay",
    "calculate_series_resistance",
    "calculate_thermal_resistance",
    "calculate_voltage_drop",
    "expand_ref_designators",
    "format_si_prefix",
    "group_by_value",
    "parse_si_prefix",
]
