"""Physics Domain Plugin for SpreadsheetDL.

    Physics domain plugin
    BATCH-5: Physics domain creation
    Phase 4 Task 4.1: Physics domain expansion

Provides physics-specific functionality including:
- Classical mechanics, electromagnetism, optics, and quantum mechanics formulas
- Thermodynamics and wave physics formulas
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas - Electromagnetism (6 formulas)
from spreadsheet_dl.domains.physics.formulas.electromagnetism import (
    CoulombLawFormula,
    ElectricFieldFormula,
    FaradayLawFormula,
    LorentzForceFormula,
    MagneticForceFormula,
    PoyntingVectorFormula,
)

# Import formulas - Mechanics (7 formulas)
from spreadsheet_dl.domains.physics.formulas.mechanics import (
    AngularMomentumFormula,
    CentripetalForceFormula,
    KineticEnergyFormula,
    MomentumFormula,
    NewtonSecondLawFormula,
    PotentialEnergyFormula,
    WorkEnergyFormula,
)

# Import formulas - Optics (6 formulas)
from spreadsheet_dl.domains.physics.formulas.optics import (
    BraggLawFormula,
    DiffractionGratingFormula,
    LensMakerEquationFormula,
    MagnificationLensFormula,
    SnellsLawFormula,
    ThinFilmInterferenceFormula,
)

# Import formulas - Quantum (6 formulas)
from spreadsheet_dl.domains.physics.formulas.quantum import (
    BohrRadiusFormula,
    DeBroglieWavelengthFormula,
    HeisenbergUncertaintyFormula,
    PhotoelectricEffectFormula,
    PlanckEnergyFormula,
    RydbergFormulaFormula,
)

# Import formulas - Thermodynamics (13 formulas)
from spreadsheet_dl.domains.physics.formulas.thermodynamics import (
    AdiabaticProcessFormula,
    CarnotEfficiencyFormula,
    EntropyChangeFormula,
    HeatTransferFormula,
    IdealGasLawFormula,
    InternalEnergyFormula,
    LatentHeatFormula,
    MeanFreePathFormula,
    RmsVelocityFormula,
    StefanBoltzmannFormula,
    ThermalConductionFormula,
    ThermalExpansionFormula,
    WiensLawFormula,
)

# Import formulas - Waves (12 formulas)
from spreadsheet_dl.domains.physics.formulas.waves import (
    AngularFrequencyFormula,
    BeatFrequencyFormula,
    DopplerEffectFormula,
    ReflectionCoefficientFormula,
    SoundIntensityFormula,
    StandingWaveFormula,
    StringTensionFormula,
    WaveEnergyFormula,
    WaveNumberFormula,
    WavePeriodFormula,
    WavePowerFormula,
    WaveVelocityFormula,
)


class PhysicsDomainPlugin(BaseDomainPlugin):
    """Physics domain plugin.

        Complete Physics domain plugin
        BATCH-5: Physics domain creation
        Phase 4 Task 4.1: Physics domain expansion

    Provides comprehensive physics functionality for SpreadsheetDL
    with formulas for mechanics, electromagnetism, optics, quantum mechanics,
    thermodynamics, and wave physics.

    Formulas (50 total):
        Classical Mechanics (7):
        - NEWTON_SECOND_LAW: F = ma
        - KINETIC_ENERGY: KE = 0.5*m*v^2
        - POTENTIAL_ENERGY: PE = mgh
        - WORK_ENERGY: W = F*d*cos(theta)
        - MOMENTUM: p = mv
        - ANGULAR_MOMENTUM: L = I*omega
        - CENTRIPETAL_FORCE: Fc = mv^2/r

        Electromagnetism (6):
        - COULOMB_LAW: F = k*q1*q2/r^2
        - ELECTRIC_FIELD: E = F/q
        - MAGNETIC_FORCE: F = qvB*sin(theta)
        - FARADAY_LAW: EMF = N*dPhi/dt
        - LORENTZ_FORCE: F = q*(E + v*B)
        - POYNTING_VECTOR: S = E*H

        Optics (6):
        - SNELLS_LAW: n1*sin(theta1) = n2*sin(theta2)
        - LENS_MAKER_EQUATION: 1/f = (n-1)*(1/R1 - 1/R2)
        - MAGNIFICATION_LENS: M = -di/do
        - BRAGG_LAW: n*lambda = 2d*sin(theta)
        - THIN_FILM_INTERFERENCE: 2nt*cos(theta) = m*lambda
        - DIFFRACTION_GRATING: d*sin(theta) = m*lambda

        Quantum Mechanics (6):
        - PLANCK_ENERGY: E = hf
        - DE_BROGLIE_WAVELENGTH: lambda = h/p
        - HEISENBERG_UNCERTAINTY: dx*dp >= hbar/2
        - PHOTOELECTRIC_EFFECT: KE = hf - W
        - BOHR_RADIUS: r_n = n^2*a0
        - RYDBERG_FORMULA: 1/lambda = R*(1/n1^2 - 1/n2^2)

        Thermodynamics (13):
        - IDEAL_GAS_LAW: PV = nRT
        - HEAT_TRANSFER: Q = mc*dT
        - CARNOT_EFFICIENCY: eta = 1 - Tc/Th
        - ENTROPY_CHANGE: dS = Q/T
        - STEFAN_BOLTZMANN: P = epsilon*sigma*A*T^4
        - THERMAL_CONDUCTION: Q/t = kA*dT/L
        - THERMAL_EXPANSION: dL = alpha*L0*dT
        - LATENT_HEAT: Q = mL
        - ADIABATIC_PROCESS: P1*V1^gamma = P2*V2^gamma
        - WIENS_LAW: lambda_max = b/T
        - INTERNAL_ENERGY: U = (f/2)*nRT
        - MEAN_FREE_PATH: lambda = kT/(sqrt(2)*pi*d^2*P)
        - RMS_VELOCITY: v_rms = sqrt(3RT/M)

        Waves (12):
        - WAVE_VELOCITY: v = f*lambda
        - DOPPLER_EFFECT: f' = f*(v + vo)/(v - vs)
        - SOUND_INTENSITY: L = 10*log10(I/I0)
        - STANDING_WAVE: fn = n*v/(2L)
        - BEAT_FREQUENCY: fb = |f1 - f2|
        - WAVE_ENERGY: E = 0.5*rho*A^2*omega^2*V
        - WAVE_POWER: P = 0.5*rho*A^2*omega^2*v*S
        - STRING_TENSION: T = mu*v^2
        - REFLECTION_COEFFICIENT: R = ((Z2-Z1)/(Z2+Z1))^2
        - WAVE_PERIOD: T = 1/f
        - ANGULAR_FREQUENCY: omega = 2*pi*f
        - WAVE_NUMBER: k = 2*pi/lambda

    Example:
        >>> plugin = PhysicsDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with physics plugin information

            Plugin metadata requirements
            BATCH-5: Physics domain metadata
        """
        return PluginMetadata(
            name="physics",
            version="0.1.0",
            description=(
                "Physics formulas for mechanics, electromagnetism, optics, "
                "quantum mechanics, thermodynamics, and wave physics"
            ),
            author="SpreadsheetDL",
            license="MIT",
            tags=(
                "physics",
                "mechanics",
                "electromagnetism",
                "optics",
                "quantum",
                "thermodynamics",
                "waves",
            ),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas.

            Plugin initialization with all components
            BATCH-5: Physics domain initialization
            Phase 4 Task 4.1: Physics domain expansion

        Raises:
            Exception: If initialization fails
        """
        # Register mechanics formulas (7 total)
        self.register_formula("NEWTON_SECOND_LAW", NewtonSecondLawFormula)
        self.register_formula("KINETIC_ENERGY", KineticEnergyFormula)
        self.register_formula("POTENTIAL_ENERGY", PotentialEnergyFormula)
        self.register_formula("WORK_ENERGY", WorkEnergyFormula)
        self.register_formula("MOMENTUM", MomentumFormula)
        self.register_formula("ANGULAR_MOMENTUM", AngularMomentumFormula)
        self.register_formula("CENTRIPETAL_FORCE", CentripetalForceFormula)

        # Register electromagnetism formulas (6 total)
        self.register_formula("COULOMB_LAW", CoulombLawFormula)
        self.register_formula("ELECTRIC_FIELD", ElectricFieldFormula)
        self.register_formula("MAGNETIC_FORCE", MagneticForceFormula)
        self.register_formula("FARADAY_LAW", FaradayLawFormula)
        self.register_formula("LORENTZ_FORCE", LorentzForceFormula)
        self.register_formula("POYNTING_VECTOR", PoyntingVectorFormula)

        # Register optics formulas (6 total)
        self.register_formula("SNELLS_LAW", SnellsLawFormula)
        self.register_formula("LENS_MAKER_EQUATION", LensMakerEquationFormula)
        self.register_formula("MAGNIFICATION_LENS", MagnificationLensFormula)
        self.register_formula("BRAGG_LAW", BraggLawFormula)
        self.register_formula("THIN_FILM_INTERFERENCE", ThinFilmInterferenceFormula)
        self.register_formula("DIFFRACTION_GRATING", DiffractionGratingFormula)

        # Register quantum formulas (6 total)
        self.register_formula("PLANCK_ENERGY", PlanckEnergyFormula)
        self.register_formula("DE_BROGLIE_WAVELENGTH", DeBroglieWavelengthFormula)
        self.register_formula("HEISENBERG_UNCERTAINTY", HeisenbergUncertaintyFormula)
        self.register_formula("PHOTOELECTRIC_EFFECT", PhotoelectricEffectFormula)
        self.register_formula("BOHR_RADIUS", BohrRadiusFormula)
        self.register_formula("RYDBERG_FORMULA", RydbergFormulaFormula)

        # Register thermodynamics formulas (13 total)
        self.register_formula("IDEAL_GAS_LAW", IdealGasLawFormula)
        self.register_formula("HEAT_TRANSFER", HeatTransferFormula)
        self.register_formula("CARNOT_EFFICIENCY", CarnotEfficiencyFormula)
        self.register_formula("ENTROPY_CHANGE", EntropyChangeFormula)
        self.register_formula("STEFAN_BOLTZMANN", StefanBoltzmannFormula)
        self.register_formula("THERMAL_CONDUCTION", ThermalConductionFormula)
        self.register_formula("THERMAL_EXPANSION", ThermalExpansionFormula)
        self.register_formula("LATENT_HEAT", LatentHeatFormula)
        self.register_formula("ADIABATIC_PROCESS", AdiabaticProcessFormula)
        self.register_formula("WIENS_LAW", WiensLawFormula)
        self.register_formula("INTERNAL_ENERGY", InternalEnergyFormula)
        self.register_formula("MEAN_FREE_PATH", MeanFreePathFormula)
        self.register_formula("RMS_VELOCITY", RmsVelocityFormula)

        # Register wave formulas (12 total)
        self.register_formula("WAVE_VELOCITY", WaveVelocityFormula)
        self.register_formula("DOPPLER_EFFECT", DopplerEffectFormula)
        self.register_formula("SOUND_INTENSITY", SoundIntensityFormula)
        self.register_formula("STANDING_WAVE", StandingWaveFormula)
        self.register_formula("BEAT_FREQUENCY", BeatFrequencyFormula)
        self.register_formula("WAVE_ENERGY", WaveEnergyFormula)
        self.register_formula("WAVE_POWER", WavePowerFormula)
        self.register_formula("STRING_TENSION", StringTensionFormula)
        self.register_formula("REFLECTION_COEFFICIENT", ReflectionCoefficientFormula)
        self.register_formula("WAVE_PERIOD", WavePeriodFormula)
        self.register_formula("ANGULAR_FREQUENCY", AngularFrequencyFormula)
        self.register_formula("WAVE_NUMBER", WaveNumberFormula)

    def cleanup(self) -> None:
        """Cleanup plugin resources.

        No resources need explicit cleanup for this plugin.

            Plugin cleanup method
            BATCH-5: Physics domain cleanup
        """
        # No cleanup needed for this plugin

    def validate(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if plugin has required formulas registered

            Plugin validation
            BATCH-5: Physics domain validation
        """
        # Verify we have all required components
        # 7 mechanics + 6 EM + 6 optics + 6 quantum + 13 thermo + 12 waves = 50
        required_formulas = 50

        return len(self._formulas) >= required_formulas


__all__ = [
    "PhysicsDomainPlugin",
]
