"""Filter design formulas for electrical engineering.

Filter design formulas (cutoff frequencies, Q factor, attenuation)
"""

from __future__ import annotations

from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


class LowPassCutoffFormula(BaseFormula):
    """RC low-pass filter cutoff frequency.

    Calculates cutoff frequency for RC low-pass filter: fc = 1 / (2π * R * C).

        LOW_PASS_CUTOFF formula

    Example:
        >>> formula = LowPassCutoffFormula()
        >>> formula.build("1000", "1e-6")
        '1/(2*PI()*1000*1e-6)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LOW_PASS_CUTOFF",
            category="electrical_engineering",
            description="RC low-pass filter cutoff frequency: fc = 1 / (2π * R * C)",
            arguments=(
                FormulaArgument(
                    name="resistance",
                    type="number",
                    required=True,
                    description="Resistance in ohms (Ω)",
                ),
                FormulaArgument(
                    name="capacitance",
                    type="number",
                    required=True,
                    description="Capacitance in farads (F)",
                ),
            ),
            return_type="number",
            examples=(
                "=LOW_PASS_CUTOFF(1000, 1e-6)  # 159.15 Hz",
                "=LOW_PASS_CUTOFF(10000, 100e-9)  # 159.15 Hz",
                "=LOW_PASS_CUTOFF(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: resistance, capacitance

        Returns:
            ODF formula string: 1/(2*PI()*resistance*capacitance)
        """
        self.validate_arguments(args)
        resistance, capacitance = args
        return f"of:=1/(2*PI()*{resistance}*{capacitance})"


class HighPassCutoffFormula(BaseFormula):
    """CR high-pass filter cutoff frequency.

    Calculates cutoff frequency for CR high-pass filter: fc = 1 / (2π * R * C).

        HIGH_PASS_CUTOFF formula

    Example:
        >>> formula = HighPassCutoffFormula()
        >>> formula.build("1000", "1e-6")
        '1/(2*PI()*1000*1e-6)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="HIGH_PASS_CUTOFF",
            category="electrical_engineering",
            description="CR high-pass filter cutoff frequency: fc = 1 / (2π * R * C)",
            arguments=(
                FormulaArgument(
                    name="resistance",
                    type="number",
                    required=True,
                    description="Resistance in ohms (Ω)",
                ),
                FormulaArgument(
                    name="capacitance",
                    type="number",
                    required=True,
                    description="Capacitance in farads (F)",
                ),
            ),
            return_type="number",
            examples=(
                "=HIGH_PASS_CUTOFF(1000, 1e-6)  # 159.15 Hz",
                "=HIGH_PASS_CUTOFF(10000, 100e-9)  # 159.15 Hz",
                "=HIGH_PASS_CUTOFF(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: resistance, capacitance

        Returns:
            ODF formula string: 1/(2*PI()*resistance*capacitance)
        """
        self.validate_arguments(args)
        resistance, capacitance = args
        return f"of:=1/(2*PI()*{resistance}*{capacitance})"


class BandPassCenterFormula(BaseFormula):
    """Bandpass filter center frequency.

    Calculates center frequency for LC bandpass filter: fc = 1 / (2π * √(L * C)).

        BAND_PASS_CENTER formula

    Example:
        >>> formula = BandPassCenterFormula()
        >>> formula.build("1e-3", "1e-9")
        '1/(2*PI()*SQRT(1e-3*1e-9))'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="BAND_PASS_CENTER",
            category="electrical_engineering",
            description="Bandpass filter center frequency: fc = 1 / (2π * √(L * C))",
            arguments=(
                FormulaArgument(
                    name="inductance",
                    type="number",
                    required=True,
                    description="Inductance in henries (H)",
                ),
                FormulaArgument(
                    name="capacitance",
                    type="number",
                    required=True,
                    description="Capacitance in farads (F)",
                ),
            ),
            return_type="number",
            examples=(
                "=BAND_PASS_CENTER(1e-3, 1e-9)  # 159.15 kHz",
                "=BAND_PASS_CENTER(100e-6, 100e-12)  # 1.59 MHz",
                "=BAND_PASS_CENTER(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: inductance, capacitance

        Returns:
            ODF formula string: 1/(2*PI()*SQRT(inductance*capacitance))
        """
        self.validate_arguments(args)
        inductance, capacitance = args
        return f"of:=1/(2*PI()*SQRT({inductance}*{capacitance}))"


class QFactorFormula(BaseFormula):
    """Quality factor for resonant circuits.

    Calculates quality factor: Q = f0 / BW.

        Q_FACTOR formula

    Example:
        >>> formula = QFactorFormula()
        >>> formula.build("1000", "100")
        '1000/100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="Q_FACTOR",
            category="electrical_engineering",
            description="Quality factor for resonant circuits: Q = f0 / BW",
            arguments=(
                FormulaArgument(
                    name="resonant_freq",
                    type="number",
                    required=True,
                    description="Resonant frequency in hertz (Hz)",
                ),
                FormulaArgument(
                    name="bandwidth",
                    type="number",
                    required=True,
                    description="Bandwidth in hertz (Hz)",
                ),
            ),
            return_type="number",
            examples=(
                "=Q_FACTOR(1000, 100)  # Q = 10",
                "=Q_FACTOR(1e6, 10e3)  # Q = 100",
                "=Q_FACTOR(A2, B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: resonant_freq, bandwidth

        Returns:
            ODF formula string: resonant_freq/bandwidth
        """
        self.validate_arguments(args)
        resonant_freq, bandwidth = args
        return f"of:={resonant_freq}/{bandwidth}"


class FilterAttenuationFormula(BaseFormula):
    """Filter attenuation at frequency.

    Calculates filter attenuation in dB: A = -20 * n * log10(f / fc).

        FILTER_ATTENUATION formula

    Example:
        >>> formula = FilterAttenuationFormula()
        >>> formula.build("10000", "1000", "2")
        '-20*2*LOG10(10000/1000)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="FILTER_ATTENUATION",
            category="electrical_engineering",
            description="Filter attenuation at frequency: A = -20 * n * log10(f / fc)",
            arguments=(
                FormulaArgument(
                    name="frequency",
                    type="number",
                    required=True,
                    description="Frequency in hertz (Hz)",
                ),
                FormulaArgument(
                    name="cutoff_freq",
                    type="number",
                    required=True,
                    description="Cutoff frequency in hertz (Hz)",
                ),
                FormulaArgument(
                    name="order",
                    type="number",
                    required=True,
                    description="Filter order (poles)",
                ),
            ),
            return_type="number",
            examples=(
                "=FILTER_ATTENUATION(10000, 1000, 2)  # -40 dB/decade",
                "=FILTER_ATTENUATION(100, 1000, 1)  # +20 dB (f < fc)",
                "=FILTER_ATTENUATION(A2, B2, C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: frequency, cutoff_freq, order

        Returns:
            ODF formula string: -20*order*LOG10(frequency/cutoff_freq)
        """
        self.validate_arguments(args)
        frequency, cutoff_freq, order = args
        return f"of:=-20*{order}*LOG10({frequency}/{cutoff_freq})"


__all__ = [
    "BandPassCenterFormula",
    "FilterAttenuationFormula",
    "HighPassCutoffFormula",
    "LowPassCutoffFormula",
    "QFactorFormula",
]
