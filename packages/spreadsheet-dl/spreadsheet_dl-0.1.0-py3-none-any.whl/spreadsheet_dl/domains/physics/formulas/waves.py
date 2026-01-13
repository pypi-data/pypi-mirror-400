"""Wave physics formulas.

Physics wave formulas (12 formulas)
Phase 4 Task 4.1: Physics domain expansion
"""

# ruff: noqa: RUF002, RUF003
# Greek letters (λ, ρ, etc.) and mathematical symbols are intentional scientific notation

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class WaveVelocityFormula(BaseFormula):
    """Calculate wave velocity.

        WAVE_VELOCITY formula (v = fλ)
        Phase 4: Physics waves

    Example:
        >>> formula = WaveVelocityFormula()
        >>> result = formula.build("440", "0.78")
        >>> # Returns: "of:=440*0.78"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WAVE_VELOCITY
        """
        return FormulaMetadata(
            name="WAVE_VELOCITY",
            category="waves",
            description="Calculate wave velocity (v = fλ)",
            arguments=(
                FormulaArgument(
                    "frequency",
                    "number",
                    required=True,
                    description="Frequency (Hz)",
                ),
                FormulaArgument(
                    "wavelength",
                    "number",
                    required=True,
                    description="Wavelength (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=WAVE_VELOCITY(440;0.78)",
                "=WAVE_VELOCITY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WAVE_VELOCITY formula string.

        Args:
            *args: frequency, wavelength
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency = args[0]
        wavelength = args[1]

        # v = fλ
        return f"of:={frequency}*{wavelength}"


@dataclass(slots=True, frozen=True)
class DopplerEffectFormula(BaseFormula):
    """Calculate Doppler shifted frequency.

        DOPPLER_EFFECT formula (f' = f(v + vo)/(v - vs))
        Phase 4: Physics waves

    Example:
        >>> formula = DopplerEffectFormula()
        >>> result = formula.build("1000", "343", "0", "30")
        >>> # Returns: "of:=1000*(343+0)/(343-30)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DOPPLER_EFFECT
        """
        return FormulaMetadata(
            name="DOPPLER_EFFECT",
            category="waves",
            description="Calculate Doppler shifted frequency",
            arguments=(
                FormulaArgument(
                    "source_freq",
                    "number",
                    required=True,
                    description="Source frequency (Hz)",
                ),
                FormulaArgument(
                    "wave_velocity",
                    "number",
                    required=True,
                    description="Wave velocity in medium (m/s)",
                ),
                FormulaArgument(
                    "observer_velocity",
                    "number",
                    required=False,
                    description="Observer velocity toward source (m/s)",
                    default=0,
                ),
                FormulaArgument(
                    "source_velocity",
                    "number",
                    required=False,
                    description="Source velocity toward observer (m/s)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=DOPPLER_EFFECT(1000;343;0;30)",
                "=DOPPLER_EFFECT(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DOPPLER_EFFECT formula string.

        Args:
            *args: source_freq, wave_velocity, [observer_velocity], [source_velocity]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        source_freq = args[0]
        wave_velocity = args[1]
        observer_velocity = args[2] if len(args) > 2 else 0
        source_velocity = args[3] if len(args) > 3 else 0

        # f' = f(v + vo)/(v - vs)
        return f"of:={source_freq}*({wave_velocity}+{observer_velocity})/({wave_velocity}-{source_velocity})"


@dataclass(slots=True, frozen=True)
class SoundIntensityFormula(BaseFormula):
    """Calculate sound intensity level in decibels.

        SOUND_INTENSITY formula (L = 10*log10(I/I0))
        Phase 4: Physics waves

    Example:
        >>> formula = SoundIntensityFormula()
        >>> result = formula.build("1E-6")
        >>> # Returns: "of:=10*LOG10(1E-6/1E-12)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SOUND_INTENSITY
        """
        return FormulaMetadata(
            name="SOUND_INTENSITY",
            category="waves",
            description="Calculate sound intensity level in decibels",
            arguments=(
                FormulaArgument(
                    "intensity",
                    "number",
                    required=True,
                    description="Sound intensity (W/m²)",
                ),
                FormulaArgument(
                    "reference",
                    "number",
                    required=False,
                    description="Reference intensity (W/m²)",
                    default=1e-12,
                ),
            ),
            return_type="number",
            examples=(
                "=SOUND_INTENSITY(1E-6)",
                "=SOUND_INTENSITY(A1;1E-12)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SOUND_INTENSITY formula string.

        Args:
            *args: intensity, [reference]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        intensity = args[0]
        reference = args[1] if len(args) > 1 else "1E-12"

        # L = 10*log10(I/I0)
        return f"of:=10*LOG10({intensity}/{reference})"


@dataclass(slots=True, frozen=True)
class StandingWaveFormula(BaseFormula):
    """Calculate standing wave frequency for a string.

        STANDING_WAVE formula (fn = n*v/(2L))
        Phase 4: Physics waves

    Example:
        >>> formula = StandingWaveFormula()
        >>> result = formula.build("1", "343", "0.5")
        >>> # Returns: "of:=1*343/(2*0.5)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for STANDING_WAVE
        """
        return FormulaMetadata(
            name="STANDING_WAVE",
            category="waves",
            description="Calculate standing wave frequency (fn = nv/2L)",
            arguments=(
                FormulaArgument(
                    "harmonic",
                    "number",
                    required=True,
                    description="Harmonic number (1, 2, 3, ...)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Wave velocity (m/s)",
                ),
                FormulaArgument(
                    "length",
                    "number",
                    required=True,
                    description="String/pipe length (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=STANDING_WAVE(1;343;0.5)",
                "=STANDING_WAVE(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build STANDING_WAVE formula string.

        Args:
            *args: harmonic, velocity, length
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        harmonic = args[0]
        velocity = args[1]
        length = args[2]

        # fn = n*v/(2L)
        return f"of:={harmonic}*{velocity}/(2*{length})"


@dataclass(slots=True, frozen=True)
class BeatFrequencyFormula(BaseFormula):
    """Calculate beat frequency between two waves.

        BEAT_FREQUENCY formula (fb = |f1 - f2|)
        Phase 4: Physics waves

    Example:
        >>> formula = BeatFrequencyFormula()
        >>> result = formula.build("440", "442")
        >>> # Returns: "of:=ABS(440-442)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BEAT_FREQUENCY
        """
        return FormulaMetadata(
            name="BEAT_FREQUENCY",
            category="waves",
            description="Calculate beat frequency (fb = |f1 - f2|)",
            arguments=(
                FormulaArgument(
                    "frequency1",
                    "number",
                    required=True,
                    description="First frequency (Hz)",
                ),
                FormulaArgument(
                    "frequency2",
                    "number",
                    required=True,
                    description="Second frequency (Hz)",
                ),
            ),
            return_type="number",
            examples=(
                "=BEAT_FREQUENCY(440;442)",
                "=BEAT_FREQUENCY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BEAT_FREQUENCY formula string.

        Args:
            *args: frequency1, frequency2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency1 = args[0]
        frequency2 = args[1]

        # fb = |f1 - f2|
        return f"of:=ABS({frequency1}-{frequency2})"


@dataclass(slots=True, frozen=True)
class WaveEnergyFormula(BaseFormula):
    """Calculate wave energy.

        WAVE_ENERGY formula (E = 0.5*ρ*A²*ω²*V)
        Phase 4: Physics waves

    Example:
        >>> formula = WaveEnergyFormula()
        >>> result = formula.build("1000", "0.1", "10", "1")
        >>> # Returns: "of:=0.5*1000*0.1^2*10^2*1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WAVE_ENERGY
        """
        return FormulaMetadata(
            name="WAVE_ENERGY",
            category="waves",
            description="Calculate mechanical wave energy",
            arguments=(
                FormulaArgument(
                    "density",
                    "number",
                    required=True,
                    description="Medium density (kg/m³)",
                ),
                FormulaArgument(
                    "amplitude",
                    "number",
                    required=True,
                    description="Wave amplitude (m)",
                ),
                FormulaArgument(
                    "angular_freq",
                    "number",
                    required=True,
                    description="Angular frequency (rad/s)",
                ),
                FormulaArgument(
                    "volume",
                    "number",
                    required=True,
                    description="Volume of medium (m³)",
                ),
            ),
            return_type="number",
            examples=(
                "=WAVE_ENERGY(1000;0.1;10;1)",
                "=WAVE_ENERGY(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WAVE_ENERGY formula string.

        Args:
            *args: density, amplitude, angular_freq, volume
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        density = args[0]
        amplitude = args[1]
        angular_freq = args[2]
        volume = args[3]

        # E = 0.5*ρ*A²*ω²*V
        return f"of:=0.5*{density}*{amplitude}^2*{angular_freq}^2*{volume}"


@dataclass(slots=True, frozen=True)
class WavePowerFormula(BaseFormula):
    """Calculate wave power transmission.

        WAVE_POWER formula (P = 0.5*ρ*A²*ω²*v*S)
        Phase 4: Physics waves

    Example:
        >>> formula = WavePowerFormula()
        >>> result = formula.build("1000", "0.1", "10", "343", "1")
        >>> # Returns: "of:=0.5*1000*0.1^2*10^2*343*1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WAVE_POWER
        """
        return FormulaMetadata(
            name="WAVE_POWER",
            category="waves",
            description="Calculate wave power transmission",
            arguments=(
                FormulaArgument(
                    "density",
                    "number",
                    required=True,
                    description="Medium density (kg/m³)",
                ),
                FormulaArgument(
                    "amplitude",
                    "number",
                    required=True,
                    description="Wave amplitude (m)",
                ),
                FormulaArgument(
                    "angular_freq",
                    "number",
                    required=True,
                    description="Angular frequency (rad/s)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Wave velocity (m/s)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Cross-sectional area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=WAVE_POWER(1000;0.1;10;343;1)",
                "=WAVE_POWER(A1;B1;C1;D1;E1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WAVE_POWER formula string.

        Args:
            *args: density, amplitude, angular_freq, velocity, area
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        density = args[0]
        amplitude = args[1]
        angular_freq = args[2]
        velocity = args[3]
        area = args[4]

        # P = 0.5*ρ*A²*ω²*v*S
        return f"of:=0.5*{density}*{amplitude}^2*{angular_freq}^2*{velocity}*{area}"


@dataclass(slots=True, frozen=True)
class StringTensionFormula(BaseFormula):
    """Calculate string tension from wave velocity.

        STRING_TENSION formula (T = μv²)
        Phase 4: Physics waves

    Example:
        >>> formula = StringTensionFormula()
        >>> result = formula.build("0.01", "100")
        >>> # Returns: "of:=0.01*100^2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for STRING_TENSION
        """
        return FormulaMetadata(
            name="STRING_TENSION",
            category="waves",
            description="Calculate string tension from wave velocity (T = μv²)",
            arguments=(
                FormulaArgument(
                    "linear_density",
                    "number",
                    required=True,
                    description="Linear mass density (kg/m)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Wave velocity (m/s)",
                ),
            ),
            return_type="number",
            examples=(
                "=STRING_TENSION(0.01;100)",
                "=STRING_TENSION(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build STRING_TENSION formula string.

        Args:
            *args: linear_density, velocity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        linear_density = args[0]
        velocity = args[1]

        # T = μv²
        return f"of:={linear_density}*{velocity}^2"


@dataclass(slots=True, frozen=True)
class ReflectionCoefficientFormula(BaseFormula):
    """Calculate wave reflection coefficient.

        REFLECTION_COEFFICIENT formula (R = ((Z2-Z1)/(Z2+Z1))²)
        Phase 4: Physics waves

    Example:
        >>> formula = ReflectionCoefficientFormula()
        >>> result = formula.build("415", "1.5E6")
        >>> # Returns: "of:=((1.5E6-415)/(1.5E6+415))^2"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for REFLECTION_COEFFICIENT
        """
        return FormulaMetadata(
            name="REFLECTION_COEFFICIENT",
            category="waves",
            description="Calculate wave reflection coefficient",
            arguments=(
                FormulaArgument(
                    "impedance1",
                    "number",
                    required=True,
                    description="Acoustic impedance of medium 1 (Pa·s/m)",
                ),
                FormulaArgument(
                    "impedance2",
                    "number",
                    required=True,
                    description="Acoustic impedance of medium 2 (Pa·s/m)",
                ),
            ),
            return_type="number",
            examples=(
                "=REFLECTION_COEFFICIENT(415;1.5E6)",
                "=REFLECTION_COEFFICIENT(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build REFLECTION_COEFFICIENT formula string.

        Args:
            *args: impedance1, impedance2
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        impedance1 = args[0]
        impedance2 = args[1]

        # R = ((Z2-Z1)/(Z2+Z1))²
        return f"of:=(({impedance2}-{impedance1})/({impedance2}+{impedance1}))^2"


@dataclass(slots=True, frozen=True)
class WavePeriodFormula(BaseFormula):
    """Calculate wave period from frequency.

        WAVE_PERIOD formula (T = 1/f)
        Phase 4: Physics waves

    Example:
        >>> formula = WavePeriodFormula()
        >>> result = formula.build("440")
        >>> # Returns: "of:=1/440"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WAVE_PERIOD
        """
        return FormulaMetadata(
            name="WAVE_PERIOD",
            category="waves",
            description="Calculate wave period from frequency (T = 1/f)",
            arguments=(
                FormulaArgument(
                    "frequency",
                    "number",
                    required=True,
                    description="Frequency (Hz)",
                ),
            ),
            return_type="number",
            examples=(
                "=WAVE_PERIOD(440)",
                "=WAVE_PERIOD(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WAVE_PERIOD formula string.

        Args:
            *args: frequency
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency = args[0]

        # T = 1/f
        return f"of:=1/{frequency}"


@dataclass(slots=True, frozen=True)
class AngularFrequencyFormula(BaseFormula):
    """Calculate angular frequency from frequency.

        ANGULAR_FREQUENCY formula (ω = 2πf)
        Phase 4: Physics waves

    Example:
        >>> formula = AngularFrequencyFormula()
        >>> result = formula.build("440")
        >>> # Returns: "of:=2*PI()*440"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ANGULAR_FREQUENCY
        """
        return FormulaMetadata(
            name="ANGULAR_FREQUENCY",
            category="waves",
            description="Calculate angular frequency (ω = 2πf)",
            arguments=(
                FormulaArgument(
                    "frequency",
                    "number",
                    required=True,
                    description="Frequency (Hz)",
                ),
            ),
            return_type="number",
            examples=(
                "=ANGULAR_FREQUENCY(440)",
                "=ANGULAR_FREQUENCY(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ANGULAR_FREQUENCY formula string.

        Args:
            *args: frequency
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        frequency = args[0]

        # ω = 2πf
        return f"of:=2*PI()*{frequency}"


@dataclass(slots=True, frozen=True)
class WaveNumberFormula(BaseFormula):
    """Calculate wave number from wavelength.

        WAVE_NUMBER formula (k = 2π/λ)
        Phase 4: Physics waves

    Example:
        >>> formula = WaveNumberFormula()
        >>> result = formula.build("0.78")
        >>> # Returns: "of:=2*PI()/0.78"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WAVE_NUMBER
        """
        return FormulaMetadata(
            name="WAVE_NUMBER",
            category="waves",
            description="Calculate wave number (k = 2π/λ)",
            arguments=(
                FormulaArgument(
                    "wavelength",
                    "number",
                    required=True,
                    description="Wavelength (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=WAVE_NUMBER(0.78)",
                "=WAVE_NUMBER(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WAVE_NUMBER formula string.

        Args:
            *args: wavelength
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        wavelength = args[0]

        # k = 2π/λ
        return f"of:=2*PI()/{wavelength}"


__all__ = [
    "AngularFrequencyFormula",
    "BeatFrequencyFormula",
    "DopplerEffectFormula",
    "ReflectionCoefficientFormula",
    "SoundIntensityFormula",
    "StandingWaveFormula",
    "StringTensionFormula",
    "WaveEnergyFormula",
    "WaveNumberFormula",
    "WavePeriodFormula",
    "WavePowerFormula",
    "WaveVelocityFormula",
]
