"""Physics domain formulas.

Physics formula implementations (50 formulas)
BATCH-5: Physics domain creation
Phase 4 Task 4.1: Physics domain expansion
"""

from __future__ import annotations

from spreadsheet_dl.domains.physics.formulas.electromagnetism import (
    CoulombLawFormula,
    ElectricFieldFormula,
    FaradayLawFormula,
    LorentzForceFormula,
    MagneticForceFormula,
    PoyntingVectorFormula,
)
from spreadsheet_dl.domains.physics.formulas.mechanics import (
    AngularMomentumFormula,
    CentripetalForceFormula,
    KineticEnergyFormula,
    MomentumFormula,
    NewtonSecondLawFormula,
    PotentialEnergyFormula,
    WorkEnergyFormula,
)
from spreadsheet_dl.domains.physics.formulas.optics import (
    BraggLawFormula,
    DiffractionGratingFormula,
    LensMakerEquationFormula,
    MagnificationLensFormula,
    SnellsLawFormula,
    ThinFilmInterferenceFormula,
)
from spreadsheet_dl.domains.physics.formulas.quantum import (
    BohrRadiusFormula,
    DeBroglieWavelengthFormula,
    HeisenbergUncertaintyFormula,
    PhotoelectricEffectFormula,
    PlanckEnergyFormula,
    RydbergFormulaFormula,
)
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

__all__ = [
    # Thermodynamics (13)
    "AdiabaticProcessFormula",
    # Waves (12)
    "AngularFrequencyFormula",
    # Mechanics (7)
    "AngularMomentumFormula",
    "BeatFrequencyFormula",
    # Quantum (6)
    "BohrRadiusFormula",
    # Optics (6)
    "BraggLawFormula",
    "CarnotEfficiencyFormula",
    "CentripetalForceFormula",
    # Electromagnetism (6)
    "CoulombLawFormula",
    "DeBroglieWavelengthFormula",
    "DiffractionGratingFormula",
    "DopplerEffectFormula",
    "ElectricFieldFormula",
    "EntropyChangeFormula",
    "FaradayLawFormula",
    "HeatTransferFormula",
    "HeisenbergUncertaintyFormula",
    "IdealGasLawFormula",
    "InternalEnergyFormula",
    "KineticEnergyFormula",
    "LatentHeatFormula",
    "LensMakerEquationFormula",
    "LorentzForceFormula",
    "MagneticForceFormula",
    "MagnificationLensFormula",
    "MeanFreePathFormula",
    "MomentumFormula",
    "NewtonSecondLawFormula",
    "PhotoelectricEffectFormula",
    "PlanckEnergyFormula",
    "PotentialEnergyFormula",
    "PoyntingVectorFormula",
    "ReflectionCoefficientFormula",
    "RmsVelocityFormula",
    "RydbergFormulaFormula",
    "SnellsLawFormula",
    "SoundIntensityFormula",
    "StandingWaveFormula",
    "StefanBoltzmannFormula",
    "StringTensionFormula",
    "ThermalConductionFormula",
    "ThermalExpansionFormula",
    "ThinFilmInterferenceFormula",
    "WaveEnergyFormula",
    "WaveNumberFormula",
    "WavePeriodFormula",
    "WavePowerFormula",
    "WaveVelocityFormula",
    "WiensLawFormula",
    "WorkEnergyFormula",
]
