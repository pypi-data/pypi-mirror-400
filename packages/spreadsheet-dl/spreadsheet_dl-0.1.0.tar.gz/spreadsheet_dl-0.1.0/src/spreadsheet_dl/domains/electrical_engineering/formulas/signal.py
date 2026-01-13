"""Signal analysis formulas for electrical engineering.

Signal formulas (SNR, BANDWIDTH, RISE_TIME, PROPAGATION_DELAY)
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


class SignalToNoiseRatioFormula(BaseFormula):
    """Signal-to-noise ratio formula: SNR = 10 * log10(S/N).

    Calculates SNR in decibels given signal and noise power.

        SIGNAL_TO_NOISE_RATIO formula

    Example:
        >>> formula = SignalToNoiseRatioFormula()
        >>> formula.build("100", "1")
        'of:=10*LOG10(100/1)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SIGNAL_TO_NOISE_RATIO",
            category="electrical_engineering",
            description="Calculate SNR in decibels: SNR = 10 * log10(S/N)",
            arguments=(
                FormulaArgument(
                    name="signal_power",
                    type="number",
                    required=True,
                    description="Signal power (watts or arbitrary units)",
                ),
                FormulaArgument(
                    name="noise_power",
                    type="number",
                    required=True,
                    description="Noise power (same units as signal)",
                ),
            ),
            return_type="number",
            examples=(
                "=SIGNAL_TO_NOISE_RATIO(100, 1)  # 20 dB",
                "=SIGNAL_TO_NOISE_RATIO(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: signal_power, noise_power

        Returns:
            ODF formula string: of:=10*LOG10(signal_power/noise_power)
        """
        self.validate_arguments(args)
        signal_power, noise_power = args
        return f"of:=10*LOG10({signal_power}/{noise_power})"


class BandwidthFormula(BaseFormula):
    """Bandwidth formula: BW = 0.35 / rise_time.

    Calculates bandwidth from rise time.

        BANDWIDTH formula

    Example:
        >>> formula = BandwidthFormula()
        >>> formula.build("3.5e-9")
        'of:=0.35/3.5e-9'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BANDWIDTH",
            category="electrical_engineering",
            description="Calculate bandwidth from rise time: BW = 0.35 / rise_time",
            arguments=(
                FormulaArgument(
                    name="rise_time",
                    type="number",
                    required=True,
                    description="Rise time in seconds (s)",
                ),
            ),
            return_type="number",
            examples=(
                "=BANDWIDTH(3.5e-9)  # 100 MHz for 3.5ns rise time",
                "=BANDWIDTH(A2)  # Using cell reference",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: rise_time

        Returns:
            ODF formula string: of:=0.35/rise_time
        """
        self.validate_arguments(args)
        (rise_time,) = args
        return f"of:=0.35/{rise_time}"


class RiseTimeFormula(BaseFormula):
    """Rise time formula: t_r = 2.2 * R * C.

    Calculates rise time from resistance and capacitance (RC circuit).

        RISE_TIME formula

    Example:
        >>> formula = RiseTimeFormula()
        >>> formula.build("10e-9", "1000")
        'of:=2.2*1000*10e-9'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="RISE_TIME",
            category="electrical_engineering",
            description="Calculate rise time from RC: t_r = 2.2 * R * C",
            arguments=(
                FormulaArgument(
                    name="capacitance",
                    type="number",
                    required=True,
                    description="Capacitance in farads (F)",
                ),
                FormulaArgument(
                    name="resistance",
                    type="number",
                    required=True,
                    description="Resistance in ohms (Ω)",
                ),
            ),
            return_type="number",
            examples=(
                "=RISE_TIME(10e-9, 1000)  # 22μs for 10nF and 1kΩ",
                "=RISE_TIME(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: capacitance, resistance

        Returns:
            ODF formula string: of:=2.2*resistance*capacitance
        """
        self.validate_arguments(args)
        capacitance, resistance = args
        return f"of:=2.2*{resistance}*{capacitance}"


class PropagationDelayFormula(BaseFormula):
    """Propagation delay formula: t_pd = length / velocity.

    Calculates propagation delay from trace length and signal velocity.

        PROPAGATION_DELAY formula

    Example:
        >>> formula = PropagationDelayFormula()
        >>> formula.build("100", "2e8")
        'of:=100/2e8'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="PROPAGATION_DELAY",
            category="electrical_engineering",
            description="Calculate propagation delay: t_pd = length / velocity",
            arguments=(
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Trace length in millimeters (mm)",
                ),
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Signal velocity in mm/s (typically 1.5-2e8 mm/s for PCB)",
                ),
            ),
            return_type="number",
            examples=(
                "=PROPAGATION_DELAY(100, 2e8)  # 0.5ns delay",
                "=PROPAGATION_DELAY(A2, 1.8e8)  # Common FR4 velocity",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: length, velocity

        Returns:
            ODF formula string: of:=length/velocity
        """
        self.validate_arguments(args)
        length, velocity = args
        return f"of:={length}/{velocity}"


__all__ = [
    "BandwidthFormula",
    "PropagationDelayFormula",
    "RiseTimeFormula",
    "SignalToNoiseRatioFormula",
]
