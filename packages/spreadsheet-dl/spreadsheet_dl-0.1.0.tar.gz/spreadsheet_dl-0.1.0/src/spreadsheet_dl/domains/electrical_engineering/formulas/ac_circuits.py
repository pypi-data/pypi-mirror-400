"""AC circuit analysis formulas.

Electrical engineering formulas for AC circuit calculations
(RMS, PowerFactor, ComplexImpedance, Reactance, ResonantFrequency)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class RMSValue(BaseFormula):
    """Calculate RMS (Root Mean Square) voltage or current.

        RMS formula for AC signal analysis

    Example:
        >>> formula = RMSValue()
        >>> result = formula.build("170")
        >>> # Returns: "of:=170/SQRT(2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RMS

            Formula metadata
        """
        return FormulaMetadata(
            name="RMS_VALUE",
            category="ac_circuits",
            description="Calculate RMS voltage or current from peak value",
            arguments=(
                FormulaArgument(
                    "peak_value",
                    "number",
                    required=True,
                    description="Peak voltage or current",
                ),
            ),
            return_type="number",
            examples=(
                "=RMS_VALUE(170)",
                "=RMS_VALUE(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RMS formula string.

        Args:
            *args: peak_value
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RMS formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        peak_value = args[0]

        # RMS = Peak / sqrt(2)
        return f"of:={peak_value}/SQRT(2)"


@dataclass(slots=True, frozen=True)
class PowerFactor(BaseFormula):
    """Calculate power factor (cosine of phase angle).

        Power factor formula for AC circuits

    Example:
        >>> formula = PowerFactor()
        >>> result = formula.build("1000", "1200")
        >>> # Returns: "of:=1000/1200"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for PowerFactor

            Formula metadata
        """
        return FormulaMetadata(
            name="POWER_FACTOR",
            category="ac_circuits",
            description="Calculate power factor from real and apparent power",
            arguments=(
                FormulaArgument(
                    "real_power",
                    "number",
                    required=True,
                    description="Real power (W)",
                ),
                FormulaArgument(
                    "apparent_power",
                    "number",
                    required=True,
                    description="Apparent power (VA)",
                ),
            ),
            return_type="number",
            examples=(
                "=POWER_FACTOR(1000;1200)",
                "=POWER_FACTOR(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build PowerFactor formula string.

        Args:
            *args: real_power, apparent_power
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            PowerFactor formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        real_power = args[0]
        apparent_power = args[1]

        # PF = Real Power / Apparent Power = cos(φ)
        return f"of:={real_power}/{apparent_power}"


@dataclass(slots=True, frozen=True)
class ComplexImpedance(BaseFormula):
    """Calculate AC impedance magnitude.

        Complex impedance magnitude formula

    Example:
        >>> formula = ComplexImpedance()
        >>> result = formula.build("50", "30")
        >>> # Returns: "of:=SQRT(50^2+30^2)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ComplexImpedance

            Formula metadata
        """
        return FormulaMetadata(
            name="COMPLEX_IMPEDANCE",
            category="ac_circuits",
            description="Calculate impedance magnitude from resistance and reactance",
            arguments=(
                FormulaArgument(
                    "resistance",
                    "number",
                    required=True,
                    description="Resistance (Ω)",
                ),
                FormulaArgument(
                    "reactance",
                    "number",
                    required=True,
                    description="Reactance (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=COMPLEX_IMPEDANCE(50;30)",
                "=COMPLEX_IMPEDANCE(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ComplexImpedance formula string.

        Args:
            *args: resistance, reactance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ComplexImpedance formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        resistance = args[0]
        reactance = args[1]

        # |Z| = sqrt(R² + X²)
        return f"of:=SQRT({resistance}^2+{reactance}^2)"


@dataclass(slots=True, frozen=True)
class Reactance(BaseFormula):
    """Calculate inductive or capacitive reactance.

        Reactance formula for inductors and capacitors

    Example:
        >>> formula = Reactance()
        >>> result = formula.build("60", "0.1", "L")
        >>> # Returns: "of:=2*PI()*60*0.1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for Reactance

            Formula metadata
        """
        return FormulaMetadata(
            name="REACTANCE",
            category="ac_circuits",
            description="Calculate inductive (XL) or capacitive (XC) reactance",
            arguments=(
                FormulaArgument(
                    "frequency",
                    "number",
                    required=True,
                    description="Frequency (Hz)",
                ),
                FormulaArgument(
                    "component_value",
                    "number",
                    required=True,
                    description="Inductance (H) or Capacitance (F)",
                ),
                FormulaArgument(
                    "component_type",
                    "text",
                    required=True,
                    description="'L' for inductor or 'C' for capacitor",
                ),
            ),
            return_type="number",
            examples=(
                '=REACTANCE(60;0.1;"L")',
                '=REACTANCE(60;0.000001;"C")',
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build Reactance formula string.

        Args:
            *args: frequency, component_value, component_type
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Reactance formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency = args[0]
        component_value = args[1]
        component_type = args[2]

        # XL = 2πfL for inductors
        # XC = 1/(2πfC) for capacitors
        return (
            f'of:=IF({component_type}="L";'
            f"2*PI()*{frequency}*{component_value};"
            f"1/(2*PI()*{frequency}*{component_value}))"
        )


@dataclass(slots=True, frozen=True)
class ResonantFrequency(BaseFormula):
    """Calculate resonant frequency of LC circuit.

        Resonant frequency formula for LC circuits

    Example:
        >>> formula = ResonantFrequency()
        >>> result = formula.build("0.1", "0.000001")
        >>> # Returns: "of:=1/(2*PI()*SQRT(0.1*0.000001))"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ResonantFrequency

            Formula metadata
        """
        return FormulaMetadata(
            name="RESONANT_FREQUENCY",
            category="ac_circuits",
            description="Calculate resonant frequency of LC circuit",
            arguments=(
                FormulaArgument(
                    "inductance",
                    "number",
                    required=True,
                    description="Inductance (H)",
                ),
                FormulaArgument(
                    "capacitance",
                    "number",
                    required=True,
                    description="Capacitance (F)",
                ),
            ),
            return_type="number",
            examples=(
                "=RESONANT_FREQUENCY(0.1;0.000001)",
                "=RESONANT_FREQUENCY(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ResonantFrequency formula string.

        Args:
            *args: inductance, capacitance
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ResonantFrequency formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        inductance = args[0]
        capacitance = args[1]

        # f₀ = 1 / (2π√(LC))
        return f"of:=1/(2*PI()*SQRT({inductance}*{capacitance}))"
