"""Thermodynamics formulas for physics.

Physics thermodynamics formulas (13 formulas)
Phase 4 Task 4.1: Physics domain expansion
"""

# ruff: noqa: RUF001, RUF002, RUF003
# Greek letters (α, σ, etc.) and mathematical symbols are intentional scientific notation

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class IdealGasLawFormula(BaseFormula):
    """Calculate ideal gas law properties.

        IDEAL_GAS_LAW formula (PV = nRT)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = IdealGasLawFormula()
        >>> result = formula.build("101325", "1", "8.314", "300")
        >>> # Returns: "of:=101325*1/(8.314*300)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for IDEAL_GAS_LAW
        """
        return FormulaMetadata(
            name="IDEAL_GAS_LAW",
            category="thermodynamics",
            description="Calculate ideal gas law: PV = nRT (solve for n)",
            arguments=(
                FormulaArgument(
                    "pressure",
                    "number",
                    required=True,
                    description="Pressure (Pa)",
                ),
                FormulaArgument(
                    "volume",
                    "number",
                    required=True,
                    description="Volume (m³)",
                ),
                FormulaArgument(
                    "gas_constant",
                    "number",
                    required=False,
                    description="Gas constant (J/(mol·K))",
                    default=8.314,
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=IDEAL_GAS_LAW(101325;1;8.314;300)",
                "=IDEAL_GAS_LAW(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build IDEAL_GAS_LAW formula string.

        Args:
            *args: pressure, volume, [gas_constant], temperature
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pressure = args[0]
        volume = args[1]
        gas_constant = args[2] if len(args) > 2 else 8.314
        temperature = args[3] if len(args) > 3 else args[2]

        # n = PV / RT
        return f"of:={pressure}*{volume}/({gas_constant}*{temperature})"


@dataclass(slots=True, frozen=True)
class HeatTransferFormula(BaseFormula):
    """Calculate heat transfer.

        HEAT_TRANSFER formula (Q = mcΔT)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = HeatTransferFormula()
        >>> result = formula.build("1", "4186", "10")
        >>> # Returns: "of:=1*4186*10"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for HEAT_TRANSFER
        """
        return FormulaMetadata(
            name="HEAT_TRANSFER",
            category="thermodynamics",
            description="Calculate heat transfer (Q = mcΔT)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "specific_heat",
                    "number",
                    required=True,
                    description="Specific heat capacity (J/(kg·K))",
                ),
                FormulaArgument(
                    "delta_temp",
                    "number",
                    required=True,
                    description="Temperature change (K or °C)",
                ),
            ),
            return_type="number",
            examples=(
                "=HEAT_TRANSFER(1;4186;10)",
                "=HEAT_TRANSFER(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build HEAT_TRANSFER formula string.

        Args:
            *args: mass, specific_heat, delta_temp
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        specific_heat = args[1]
        delta_temp = args[2]

        # Q = mcΔT
        return f"of:={mass}*{specific_heat}*{delta_temp}"


@dataclass(slots=True, frozen=True)
class CarnotEfficiencyFormula(BaseFormula):
    """Calculate Carnot efficiency.

        CARNOT_EFFICIENCY formula (η = 1 - Tc/Th)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = CarnotEfficiencyFormula()
        >>> result = formula.build("300", "600")
        >>> # Returns: "of:=1-300/600"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CARNOT_EFFICIENCY
        """
        return FormulaMetadata(
            name="CARNOT_EFFICIENCY",
            category="thermodynamics",
            description="Calculate Carnot engine efficiency (η = 1 - Tc/Th)",
            arguments=(
                FormulaArgument(
                    "temp_cold",
                    "number",
                    required=True,
                    description="Cold reservoir temperature (K)",
                ),
                FormulaArgument(
                    "temp_hot",
                    "number",
                    required=True,
                    description="Hot reservoir temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=CARNOT_EFFICIENCY(300;600)",
                "=CARNOT_EFFICIENCY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CARNOT_EFFICIENCY formula string.

        Args:
            *args: temp_cold, temp_hot
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        temp_cold = args[0]
        temp_hot = args[1]

        # η = 1 - Tc/Th
        return f"of:=1-{temp_cold}/{temp_hot}"


@dataclass(slots=True, frozen=True)
class EntropyChangeFormula(BaseFormula):
    """Calculate entropy change.

        ENTROPY_CHANGE formula (ΔS = Q/T)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = EntropyChangeFormula()
        >>> result = formula.build("1000", "300")
        >>> # Returns: "of:=1000/300"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ENTROPY_CHANGE
        """
        return FormulaMetadata(
            name="ENTROPY_CHANGE",
            category="thermodynamics",
            description="Calculate entropy change for reversible process (ΔS = Q/T)",
            arguments=(
                FormulaArgument(
                    "heat",
                    "number",
                    required=True,
                    description="Heat transferred (J)",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=ENTROPY_CHANGE(1000;300)",
                "=ENTROPY_CHANGE(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENTROPY_CHANGE formula string.

        Args:
            *args: heat, temperature
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        heat = args[0]
        temperature = args[1]

        # ΔS = Q/T
        return f"of:={heat}/{temperature}"


@dataclass(slots=True, frozen=True)
class StefanBoltzmannFormula(BaseFormula):
    """Calculate blackbody radiation power.

        STEFAN_BOLTZMANN formula (P = εσAT⁴)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = StefanBoltzmannFormula()
        >>> result = formula.build("1", "1", "300")
        >>> # Returns: "of:=1*5.67E-8*1*300^4"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for STEFAN_BOLTZMANN
        """
        return FormulaMetadata(
            name="STEFAN_BOLTZMANN",
            category="thermodynamics",
            description="Calculate blackbody radiation power (P = εσAT⁴)",
            arguments=(
                FormulaArgument(
                    "emissivity",
                    "number",
                    required=True,
                    description="Emissivity (0-1)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Surface area (m²)",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=STEFAN_BOLTZMANN(1;1;300)",
                "=STEFAN_BOLTZMANN(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build STEFAN_BOLTZMANN formula string.

        Args:
            *args: emissivity, area, temperature
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        emissivity = args[0]
        area = args[1]
        temperature = args[2]

        # P = εσAT⁴ (σ = 5.67×10⁻⁸ W/(m²·K⁴))
        return f"of:={emissivity}*5.67E-8*{area}*{temperature}^4"


@dataclass(slots=True, frozen=True)
class ThermalConductionFormula(BaseFormula):
    """Calculate heat conduction through a material.

        THERMAL_CONDUCTION formula (Q/t = kA(ΔT/L))
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = ThermalConductionFormula()
        >>> result = formula.build("0.6", "1", "20", "0.1")
        >>> # Returns: "of:=0.6*1*20/0.1"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for THERMAL_CONDUCTION
        """
        return FormulaMetadata(
            name="THERMAL_CONDUCTION",
            category="thermodynamics",
            description="Calculate heat conduction rate (Q/t = kAΔT/L)",
            arguments=(
                FormulaArgument(
                    "conductivity",
                    "number",
                    required=True,
                    description="Thermal conductivity (W/(m·K))",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Cross-sectional area (m²)",
                ),
                FormulaArgument(
                    "delta_temp",
                    "number",
                    required=True,
                    description="Temperature difference (K)",
                ),
                FormulaArgument(
                    "thickness",
                    "number",
                    required=True,
                    description="Material thickness (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=THERMAL_CONDUCTION(0.6;1;20;0.1)",
                "=THERMAL_CONDUCTION(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build THERMAL_CONDUCTION formula string.

        Args:
            *args: conductivity, area, delta_temp, thickness
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        conductivity = args[0]
        area = args[1]
        delta_temp = args[2]
        thickness = args[3]

        # Q/t = kAΔT/L
        return f"of:={conductivity}*{area}*{delta_temp}/{thickness}"


@dataclass(slots=True, frozen=True)
class ThermalExpansionFormula(BaseFormula):
    """Calculate linear thermal expansion.

        THERMAL_EXPANSION formula (ΔL = αL₀ΔT)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = ThermalExpansionFormula()
        >>> result = formula.build("12E-6", "1", "50")
        >>> # Returns: "of:=12E-6*1*50"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for THERMAL_EXPANSION
        """
        return FormulaMetadata(
            name="THERMAL_EXPANSION",
            category="thermodynamics",
            description="Calculate linear thermal expansion (ΔL = αL₀ΔT)",
            arguments=(
                FormulaArgument(
                    "coefficient",
                    "number",
                    required=True,
                    description="Linear expansion coefficient (1/K)",
                ),
                FormulaArgument(
                    "length",
                    "number",
                    required=True,
                    description="Original length (m)",
                ),
                FormulaArgument(
                    "delta_temp",
                    "number",
                    required=True,
                    description="Temperature change (K or °C)",
                ),
            ),
            return_type="number",
            examples=(
                "=THERMAL_EXPANSION(12E-6;1;50)",
                "=THERMAL_EXPANSION(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build THERMAL_EXPANSION formula string.

        Args:
            *args: coefficient, length, delta_temp
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        coefficient = args[0]
        length = args[1]
        delta_temp = args[2]

        # ΔL = αL₀ΔT
        return f"of:={coefficient}*{length}*{delta_temp}"


@dataclass(slots=True, frozen=True)
class LatentHeatFormula(BaseFormula):
    """Calculate heat for phase change.

        LATENT_HEAT formula (Q = mL)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = LatentHeatFormula()
        >>> result = formula.build("1", "334000")
        >>> # Returns: "of:=1*334000"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LATENT_HEAT
        """
        return FormulaMetadata(
            name="LATENT_HEAT",
            category="thermodynamics",
            description="Calculate heat for phase change (Q = mL)",
            arguments=(
                FormulaArgument(
                    "mass",
                    "number",
                    required=True,
                    description="Mass (kg)",
                ),
                FormulaArgument(
                    "latent_heat",
                    "number",
                    required=True,
                    description="Specific latent heat (J/kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=LATENT_HEAT(1;334000)",
                "=LATENT_HEAT(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LATENT_HEAT formula string.

        Args:
            *args: mass, latent_heat
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        mass = args[0]
        latent_heat = args[1]

        # Q = mL
        return f"of:={mass}*{latent_heat}"


@dataclass(slots=True, frozen=True)
class AdiabaticProcessFormula(BaseFormula):
    """Calculate adiabatic process relationship.

        ADIABATIC_PROCESS formula (P₁V₁^γ = P₂V₂^γ)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = AdiabaticProcessFormula()
        >>> result = formula.build("101325", "1", "0.5", "1.4")
        >>> # Returns: "of:=101325*(1/0.5)^1.4"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ADIABATIC_PROCESS
        """
        return FormulaMetadata(
            name="ADIABATIC_PROCESS",
            category="thermodynamics",
            description="Calculate final pressure in adiabatic process",
            arguments=(
                FormulaArgument(
                    "pressure_initial",
                    "number",
                    required=True,
                    description="Initial pressure (Pa)",
                ),
                FormulaArgument(
                    "volume_initial",
                    "number",
                    required=True,
                    description="Initial volume (m³)",
                ),
                FormulaArgument(
                    "volume_final",
                    "number",
                    required=True,
                    description="Final volume (m³)",
                ),
                FormulaArgument(
                    "gamma",
                    "number",
                    required=False,
                    description="Heat capacity ratio (Cp/Cv)",
                    default=1.4,
                ),
            ),
            return_type="number",
            examples=(
                "=ADIABATIC_PROCESS(101325;1;0.5;1.4)",
                "=ADIABATIC_PROCESS(A1;B1;C1;D1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ADIABATIC_PROCESS formula string.

        Args:
            *args: pressure_initial, volume_initial, volume_final, [gamma]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pressure_initial = args[0]
        volume_initial = args[1]
        volume_final = args[2]
        gamma = args[3] if len(args) > 3 else 1.4

        # P₂ = P₁(V₁/V₂)^γ
        return f"of:={pressure_initial}*({volume_initial}/{volume_final})^{gamma}"


@dataclass(slots=True, frozen=True)
class WiensLawFormula(BaseFormula):
    """Calculate peak wavelength from Wien's displacement law.

        WIENS_LAW formula (λmax = b/T)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = WiensLawFormula()
        >>> result = formula.build("5778")
        >>> # Returns: "of:=2.898E-3/5778"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WIENS_LAW
        """
        return FormulaMetadata(
            name="WIENS_LAW",
            category="thermodynamics",
            description="Calculate peak wavelength using Wien's law (λmax = b/T)",
            arguments=(
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=WIENS_LAW(5778)",
                "=WIENS_LAW(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WIENS_LAW formula string.

        Args:
            *args: temperature
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        temperature = args[0]

        # λmax = b/T (b = 2.898×10⁻³ m·K)
        return f"of:=2.898E-3/{temperature}"


@dataclass(slots=True, frozen=True)
class InternalEnergyFormula(BaseFormula):
    """Calculate internal energy of an ideal gas.

        INTERNAL_ENERGY formula (U = (f/2)nRT)
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = InternalEnergyFormula()
        >>> result = formula.build("3", "1", "300")
        >>> # Returns: "of:=(3/2)*1*8.314*300"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for INTERNAL_ENERGY
        """
        return FormulaMetadata(
            name="INTERNAL_ENERGY",
            category="thermodynamics",
            description="Calculate internal energy of ideal gas (U = (f/2)nRT)",
            arguments=(
                FormulaArgument(
                    "degrees_freedom",
                    "number",
                    required=True,
                    description="Degrees of freedom (3 for monatomic, 5 for diatomic)",
                ),
                FormulaArgument(
                    "moles",
                    "number",
                    required=True,
                    description="Amount of substance (mol)",
                ),
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=INTERNAL_ENERGY(3;1;300)",
                "=INTERNAL_ENERGY(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build INTERNAL_ENERGY formula string.

        Args:
            *args: degrees_freedom, moles, temperature
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        degrees_freedom = args[0]
        moles = args[1]
        temperature = args[2]

        # U = (f/2)nRT (R = 8.314 J/(mol·K))
        return f"of:=({degrees_freedom}/2)*{moles}*8.314*{temperature}"


@dataclass(slots=True, frozen=True)
class MeanFreePathFormula(BaseFormula):
    """Calculate mean free path of gas molecules.

        MEAN_FREE_PATH formula (λ = kT/(√2 π d² P))
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = MeanFreePathFormula()
        >>> result = formula.build("300", "3.7E-10", "101325")
        >>> # Returns: "of:=1.38E-23*300/(SQRT(2)*PI()*3.7E-10^2*101325)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for MEAN_FREE_PATH
        """
        return FormulaMetadata(
            name="MEAN_FREE_PATH",
            category="thermodynamics",
            description="Calculate mean free path of gas molecules",
            arguments=(
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
                FormulaArgument(
                    "diameter",
                    "number",
                    required=True,
                    description="Molecular diameter (m)",
                ),
                FormulaArgument(
                    "pressure",
                    "number",
                    required=True,
                    description="Pressure (Pa)",
                ),
            ),
            return_type="number",
            examples=(
                "=MEAN_FREE_PATH(300;3.7E-10;101325)",
                "=MEAN_FREE_PATH(A1;B1;C1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build MEAN_FREE_PATH formula string.

        Args:
            *args: temperature, diameter, pressure
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        temperature = args[0]
        diameter = args[1]
        pressure = args[2]

        # λ = kT/(√2 π d² P) (k = 1.38×10⁻²³ J/K)
        return f"of:=1.38E-23*{temperature}/(SQRT(2)*PI()*{diameter}^2*{pressure})"


@dataclass(slots=True, frozen=True)
class RmsVelocityFormula(BaseFormula):
    """Calculate root-mean-square velocity of gas molecules.

        RMS_VELOCITY formula (v_rms = √(3RT/M))
        Phase 4: Physics thermodynamics

    Example:
        >>> formula = RmsVelocityFormula()
        >>> result = formula.build("300", "0.028")
        >>> # Returns: "of:=SQRT(3*8.314*300/0.028)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RMS_VELOCITY
        """
        return FormulaMetadata(
            name="RMS_VELOCITY",
            category="thermodynamics",
            description="Calculate RMS velocity of gas molecules (v_rms = √(3RT/M))",
            arguments=(
                FormulaArgument(
                    "temperature",
                    "number",
                    required=True,
                    description="Temperature (K)",
                ),
                FormulaArgument(
                    "molar_mass",
                    "number",
                    required=True,
                    description="Molar mass (kg/mol)",
                ),
            ),
            return_type="number",
            examples=(
                "=RMS_VELOCITY(300;0.028)",
                "=RMS_VELOCITY(A1;B1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RMS_VELOCITY formula string.

        Args:
            *args: temperature, molar_mass
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        temperature = args[0]
        molar_mass = args[1]

        # v_rms = √(3RT/M) (R = 8.314 J/(mol·K))
        return f"of:=SQRT(3*8.314*{temperature}/{molar_mass})"


__all__ = [
    "AdiabaticProcessFormula",
    "CarnotEfficiencyFormula",
    "EntropyChangeFormula",
    "HeatTransferFormula",
    "IdealGasLawFormula",
    "InternalEnergyFormula",
    "LatentHeatFormula",
    "MeanFreePathFormula",
    "RmsVelocityFormula",
    "StefanBoltzmannFormula",
    "ThermalConductionFormula",
    "ThermalExpansionFormula",
    "WiensLawFormula",
]
