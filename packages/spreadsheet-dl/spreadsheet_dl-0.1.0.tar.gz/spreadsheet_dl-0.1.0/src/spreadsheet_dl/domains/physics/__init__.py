"""Physics Domain Plugin for SpreadsheetDL.

    Physics domain plugin
    BATCH-5: Physics domain creation

Provides physics-specific functionality including:
- Classical mechanics, electromagnetism, optics, and quantum mechanics formulas
- Utility functions for physics calculations

Features:
    - 25 specialized formulas for physics calculations
    - 7 mechanics formulas (Newton, energy, momentum, etc.)
    - 6 electromagnetism formulas (Coulomb, Faraday, Lorentz, etc.)
    - 6 optics formulas (Snell, lenses, diffraction, etc.)
    - 6 quantum formulas (Planck, de Broglie, Heisenberg, etc.)
"""

from __future__ import annotations

# Formulas - Electromagnetism (6 formulas)
from spreadsheet_dl.domains.physics.formulas.electromagnetism import (
    CoulombLawFormula,
    ElectricFieldFormula,
    FaradayLawFormula,
    LorentzForceFormula,
    MagneticForceFormula,
    PoyntingVectorFormula,
)

# Formulas - Mechanics (7 formulas)
from spreadsheet_dl.domains.physics.formulas.mechanics import (
    AngularMomentumFormula,
    CentripetalForceFormula,
    KineticEnergyFormula,
    MomentumFormula,
    NewtonSecondLawFormula,
    PotentialEnergyFormula,
    WorkEnergyFormula,
)

# Formulas - Optics (6 formulas)
from spreadsheet_dl.domains.physics.formulas.optics import (
    BraggLawFormula,
    DiffractionGratingFormula,
    LensMakerEquationFormula,
    MagnificationLensFormula,
    SnellsLawFormula,
    ThinFilmInterferenceFormula,
)

# Formulas - Quantum (6 formulas)
from spreadsheet_dl.domains.physics.formulas.quantum import (
    BohrRadiusFormula,
    DeBroglieWavelengthFormula,
    HeisenbergUncertaintyFormula,
    PhotoelectricEffectFormula,
    PlanckEnergyFormula,
    RydbergFormulaFormula,
)

# Plugin
from spreadsheet_dl.domains.physics.plugin import PhysicsDomainPlugin

# Utils
from spreadsheet_dl.domains.physics.utils import (
    calculate_escape_velocity,
    calculate_schwarzschild_radius,
    convert_ev_to_joules,
    convert_joules_to_ev,
    degrees_to_radians,
    electron_mass,
    elementary_charge,
    frequency_to_wavelength,
    gravitational_constant,
    planck_constant,
    proton_mass,
    radians_to_degrees,
    reduced_planck_constant,
    speed_of_light,
    wavelength_to_frequency,
)

__all__ = [
    "AngularMomentumFormula",
    "BohrRadiusFormula",
    "BraggLawFormula",
    "CentripetalForceFormula",
    "CoulombLawFormula",
    "DeBroglieWavelengthFormula",
    "DiffractionGratingFormula",
    "ElectricFieldFormula",
    "FaradayLawFormula",
    "HeisenbergUncertaintyFormula",
    "KineticEnergyFormula",
    "LensMakerEquationFormula",
    "LorentzForceFormula",
    "MagneticForceFormula",
    "MagnificationLensFormula",
    "MomentumFormula",
    "NewtonSecondLawFormula",
    "PhotoelectricEffectFormula",
    "PhysicsDomainPlugin",
    "PlanckEnergyFormula",
    "PotentialEnergyFormula",
    "PoyntingVectorFormula",
    "RydbergFormulaFormula",
    "SnellsLawFormula",
    "ThinFilmInterferenceFormula",
    "WorkEnergyFormula",
    "calculate_escape_velocity",
    "calculate_schwarzschild_radius",
    "convert_ev_to_joules",
    "convert_joules_to_ev",
    "degrees_to_radians",
    "electron_mass",
    "elementary_charge",
    "frequency_to_wavelength",
    "gravitational_constant",
    "planck_constant",
    "proton_mass",
    "radians_to_degrees",
    "reduced_planck_constant",
    "speed_of_light",
    "wavelength_to_frequency",
]
