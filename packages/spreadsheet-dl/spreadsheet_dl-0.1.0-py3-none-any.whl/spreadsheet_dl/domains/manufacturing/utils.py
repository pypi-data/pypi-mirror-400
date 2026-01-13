"""Manufacturing domain utility functions.

Manufacturing utility functions
"""

from __future__ import annotations

from typing import Any


def calculate_oee(availability: float, performance: float, quality: float) -> float:
    """Calculate Overall Equipment Effectiveness (OEE).

        OEE calculation utility

    Args:
        availability: Availability percentage (0-100)
        performance: Performance percentage (0-100)
        quality: Quality percentage (0-100)

    Returns:
        OEE percentage (0-100)

    Example:
        >>> oee = calculate_oee(95.0, 98.0, 99.5)
        >>> # Returns: 92.621 (95% * 98% * 99.5%)
    """
    return (availability / 100) * (performance / 100) * (quality / 100) * 100


def calculate_defect_rate(defects: int, total: int) -> float:
    """Calculate defect rate percentage.

        Defect rate calculation

    Args:
        defects: Number of defective units
        total: Total number of units inspected

    Returns:
        Defect rate percentage

    Example:
        >>> rate = calculate_defect_rate(25, 1000)
        >>> # Returns: 2.5
    """
    if total == 0:
        return 0.0
    return (defects / total) * 100


def calculate_first_pass_yield(good_units: int, total_units: int) -> float:
    """Calculate first pass yield percentage.

        First pass yield calculation

    Args:
        good_units: Number of units passing first inspection
        total_units: Total number of units produced

    Returns:
        First pass yield percentage

    Example:
        >>> fpy = calculate_first_pass_yield(950, 1000)
        >>> # Returns: 95.0
    """
    if total_units == 0:
        return 0.0
    return (good_units / total_units) * 100


def calculate_cycle_time(production_time: float, units_produced: int) -> float:
    """Calculate manufacturing cycle time.

        Cycle time calculation

    Args:
        production_time: Total production time in minutes
        units_produced: Number of units produced

    Returns:
        Cycle time in minutes per unit

    Example:
        >>> cycle_time = calculate_cycle_time(480, 120)
        >>> # Returns: 4.0 (4 minutes per unit)
    """
    if units_produced == 0:
        return 0.0
    return production_time / units_produced


def calculate_takt_time(available_time: float, demand: int) -> float:
    """Calculate takt time.

        Takt time calculation

    Args:
        available_time: Available production time in seconds
        demand: Customer demand in units

    Returns:
        Takt time in seconds per unit

    Example:
        >>> takt = calculate_takt_time(28800, 1200)
        >>> # Returns: 24.0 (24 seconds per unit)
    """
    if demand == 0:
        return 0.0
    return available_time / demand


def calculate_eoq(
    annual_demand: float, order_cost: float, holding_cost: float
) -> float:
    """Calculate Economic Order Quantity.

        EOQ calculation

    Args:
        annual_demand: Annual demand in units
        order_cost: Cost per order
        holding_cost: Annual holding cost per unit

    Returns:
        Economic order quantity

    Example:
        >>> eoq = calculate_eoq(10000, 50, 5)
        >>> # Returns: 447.21 (approximately)
    """
    if holding_cost == 0:
        return 0.0
    return float(((2 * annual_demand * order_cost) / holding_cost) ** 0.5)


def calculate_reorder_point(
    demand_rate: float, lead_time: float, safety_stock: float
) -> float:
    """Calculate inventory reorder point.

        Reorder point calculation

    Args:
        demand_rate: Average daily demand
        lead_time: Lead time in days
        safety_stock: Safety stock quantity

    Returns:
        Reorder point quantity

    Example:
        >>> rop = calculate_reorder_point(50, 7, 100)
        >>> # Returns: 450.0
    """
    return (demand_rate * lead_time) + safety_stock


def calculate_safety_stock(
    z_score: float, demand_stddev: float, lead_time: float
) -> float:
    """Calculate safety stock quantity.

        Safety stock calculation

    Args:
        z_score: Z-score for desired service level (e.g., 1.65 for 95%)
        demand_stddev: Standard deviation of demand
        lead_time: Lead time in days

    Returns:
        Safety stock quantity

    Example:
        >>> safety = calculate_safety_stock(1.65, 15, 7)
        >>> # Returns: 65.45 (approximately)
    """
    return float(z_score * demand_stddev * (lead_time**0.5))


def parse_manufacturing_date(date_str: str) -> str:
    """Parse various manufacturing date formats to ISO format.

        Date parsing utility

    Args:
        date_str: Date string in various formats

    Returns:
        ISO format date string (YYYY-MM-DD)

    Example:
        >>> iso_date = parse_manufacturing_date("12/25/2024")
        >>> # Returns: "2024-12-25"
    """
    from datetime import datetime

    # Common manufacturing date formats
    formats = [
        "%Y-%m-%d",  # ISO
        "%m/%d/%Y",  # US
        "%d/%m/%Y",  # EU
        "%Y/%m/%d",  # Asian
        "%d.%m.%Y",  # German
        "%d-%m-%Y",  # UK
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If all fail, return original
    return date_str


def format_manufacturing_number(value: Any, decimals: int = 2) -> str:
    """Format number for manufacturing reports.

        Number formatting utility

    Args:
        value: Numeric value to format
        decimals: Number of decimal places

    Returns:
        Formatted number string

    Example:
        >>> formatted = format_manufacturing_number(1234.5678)
        >>> # Returns: "1,234.57"
    """
    try:
        num = float(value)
        return f"{num:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def calculate_dpmo(defects: int, units: int, opportunities: int) -> float:
    """Calculate Defects Per Million Opportunities.

        DPMO calculation utility

    Args:
        defects: Number of defects
        units: Number of units inspected
        opportunities: Defect opportunities per unit

    Returns:
        DPMO value

    Example:
        >>> dpmo = calculate_dpmo(25, 1000, 5)
        >>> # Returns: 5000.0
    """
    if units == 0 or opportunities == 0:
        return 0.0
    return (defects / (units * opportunities)) * 1000000


def calculate_process_cycle_efficiency(
    value_add_time: float, lead_time: float
) -> float:
    """Calculate Process Cycle Efficiency (PCE).

        PCE calculation utility

    Args:
        value_add_time: Value-adding time
        lead_time: Total lead time

    Returns:
        PCE percentage

    Example:
        >>> pce = calculate_process_cycle_efficiency(120, 720)
        >>> # Returns: 16.67
    """
    if lead_time == 0:
        return 0.0
    return (value_add_time / lead_time) * 100


def calculate_kanban_quantity(
    demand: float, lead_time: float, safety_factor: float
) -> float:
    """Calculate optimal kanban quantity.

        Kanban quantity calculation

    Args:
        demand: Daily demand in units
        lead_time: Lead time in days
        safety_factor: Safety factor (e.g., 0.2 for 20%)

    Returns:
        Optimal kanban quantity

    Example:
        >>> kanban_qty = calculate_kanban_quantity(100, 5, 0.2)
        >>> # Returns: 600.0
    """
    return (demand * lead_time) * (1 + safety_factor)


__all__ = [
    "calculate_cycle_time",
    "calculate_defect_rate",
    "calculate_dpmo",
    "calculate_eoq",
    "calculate_first_pass_yield",
    "calculate_kanban_quantity",
    "calculate_oee",
    "calculate_process_cycle_efficiency",
    "calculate_reorder_point",
    "calculate_safety_stock",
    "calculate_takt_time",
    "format_manufacturing_number",
    "parse_manufacturing_date",
]
