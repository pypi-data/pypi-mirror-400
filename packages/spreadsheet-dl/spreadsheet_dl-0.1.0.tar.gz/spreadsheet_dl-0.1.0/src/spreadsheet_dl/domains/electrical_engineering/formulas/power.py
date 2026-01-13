"""Power calculation formulas for electrical engineering.

Power formulas (POWER_DISSIPATION, VOLTAGE_DROP, CURRENT_CALC, THERMAL_RESISTANCE)
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


class PowerDissipationFormula(BaseFormula):
    """Power dissipation formula: P = V * I.

    Calculates power dissipation given voltage and current.

        POWER_DISSIPATION formula

    Example:
        >>> formula = PowerDissipationFormula()
        >>> formula.build("5", "0.1")
        'of:=5*0.1'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="POWER_DISSIPATION",
            category="electrical_engineering",
            description="Calculate power dissipation from voltage and current: P = V * I",
            arguments=(
                FormulaArgument(
                    name="voltage",
                    type="number",
                    required=True,
                    description="Voltage in volts (V)",
                ),
                FormulaArgument(
                    name="current",
                    type="number",
                    required=True,
                    description="Current in amperes (A)",
                ),
            ),
            return_type="number",
            examples=(
                "=POWER_DISSIPATION(5, 0.1)  # 0.5 watts",
                "=POWER_DISSIPATION(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: voltage, current

        Returns:
            ODF formula string: of:=voltage*current
        """
        self.validate_arguments(args)
        voltage, current = args
        return f"of:={voltage}*{current}"


class VoltageDropFormula(BaseFormula):
    """Voltage drop formula: V = I * R * (length/1000).

    Calculates voltage drop in a conductor given current, resistance, and length.

        VOLTAGE_DROP formula

    Example:
        >>> formula = VoltageDropFormula()
        >>> formula.build("2", "0.05", "1000")
        'of:=2*0.05*(1000/1000)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="VOLTAGE_DROP",
            category="electrical_engineering",
            description="Calculate voltage drop: V = I * R * (length/1000)",
            arguments=(
                FormulaArgument(
                    name="current",
                    type="number",
                    required=True,
                    description="Current in amperes (A)",
                ),
                FormulaArgument(
                    name="resistance",
                    type="number",
                    required=True,
                    description="Resistance per meter (Ω/m)",
                ),
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Length in millimeters (mm)",
                ),
            ),
            return_type="number",
            examples=(
                "=VOLTAGE_DROP(2, 0.05, 1000)  # 0.1V drop over 1m at 2A",
                "=VOLTAGE_DROP(A2, B2, C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: current, resistance, length

        Returns:
            ODF formula string: of:=current*resistance*(length/1000)
        """
        self.validate_arguments(args)
        current, resistance, length = args
        return f"of:={current}*{resistance}*({length}/1000)"


class CurrentCalcFormula(BaseFormula):
    """Current calculation formula: I = P / V.

    Calculates current given power and voltage.

        CURRENT_CALC formula

    Example:
        >>> formula = CurrentCalcFormula()
        >>> formula.build("10", "5")
        'of:=10/5'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CURRENT_CALC",
            category="electrical_engineering",
            description="Calculate current from power and voltage: I = P / V",
            arguments=(
                FormulaArgument(
                    name="power",
                    type="number",
                    required=True,
                    description="Power in watts (W)",
                ),
                FormulaArgument(
                    name="voltage",
                    type="number",
                    required=True,
                    description="Voltage in volts (V)",
                ),
            ),
            return_type="number",
            examples=(
                "=CURRENT_CALC(10, 5)  # 2 amperes",
                "=CURRENT_CALC(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: power, voltage

        Returns:
            ODF formula string: of:=power/voltage
        """
        self.validate_arguments(args)
        power, voltage = args
        return f"of:={power}/{voltage}"


class ComponentThermalResistanceFormula(BaseFormula):
    """Component thermal resistance formula: θ = ΔT / P.

    Calculates thermal resistance of electronic components given temperature rise and power dissipation.

        COMPONENT_THERMAL_RESISTANCE formula

    Example:
        >>> formula = ComponentThermalResistanceFormula()
        >>> formula.build("50", "10")
        'of:=50/10'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="COMPONENT_THERMAL_RESISTANCE",
            category="electrical_engineering",
            description="Calculate component thermal resistance: θ = ΔT / P",
            arguments=(
                FormulaArgument(
                    name="temp_rise",
                    type="number",
                    required=True,
                    description="Temperature rise in degrees Celsius (°C)",
                ),
                FormulaArgument(
                    name="power",
                    type="number",
                    required=True,
                    description="Power dissipation in watts (W)",
                ),
            ),
            return_type="number",
            examples=(
                "=THERMAL_RESISTANCE(50, 10)  # 5 °C/W",
                "=THERMAL_RESISTANCE(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: temp_rise, power

        Returns:
            ODF formula string: of:=temp_rise/power
        """
        self.validate_arguments(args)
        temp_rise, power = args
        return f"of:={temp_rise}/{power}"


__all__ = [
    "ComponentThermalResistanceFormula",
    "CurrentCalcFormula",
    "PowerDissipationFormula",
    "VoltageDropFormula",
]
