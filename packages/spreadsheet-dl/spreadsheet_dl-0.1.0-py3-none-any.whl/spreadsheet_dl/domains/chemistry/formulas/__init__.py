"""Chemistry domain formulas.

Chemistry formula implementations (40 formulas)
BATCH-4: Chemistry domain creation
BATCH-4.2: Chemistry domain expansion (+20 formulas)
"""

from __future__ import annotations

from spreadsheet_dl.domains.chemistry.formulas.electrochemistry import (
    ButlerVolmerFormula,
    ConductivityFormula,
    EquilibriumConstantElectroFormula,
    FaradayElectrolysisFormula,
    GibbsElectrochemicalFormula,
    NernstEquationFormula,
    OhmicResistanceFormula,
    OverpotentialFormula,
    StandardCellPotentialFormula,
    TafelEquationFormula,
)
from spreadsheet_dl.domains.chemistry.formulas.kinetics import (
    ActivationEnergyFormula,
    HalfLifeFirstOrderFormula,
    HalfLifeSecondOrderFormula,
    IntegratedRateLawFormula,
    RateConstantFormula,
)
from spreadsheet_dl.domains.chemistry.formulas.solutions import (
    BufferCapacityFormula,
    MolalityFormula,
    MolarityFormula,
    MoleFractionFormula,
    OsmoticPressureFormula,
    RaoultsLawFormula,
    pHCalculationFormula,
)
from spreadsheet_dl.domains.chemistry.formulas.stoichiometry import (
    AvogadroParticlesFormula,
    DilutionFormula,
    EmpiricalFormulaRatioFormula,
    LimitingReagentFormula,
    MassFromMolesFormula,
    MolarMassFormula,
    MolesFromMassFormula,
    PercentCompositionFormula,
    PercentYieldFormula,
    TheoreticalYieldFormula,
)
from spreadsheet_dl.domains.chemistry.formulas.thermodynamics import (
    ClausiusClapeyronFormula,
    EnthalpyChangeFormula,
    EquilibriumConstantFormula,
    GasIdealityCheckFormula,
    GibbsFreeEnergyFormula,
    ReactionEntropyChangeFormula,
    RealGasVanDerWaalsFormula,
    VantHoffEquationFormula,
)

__all__ = [
    # Kinetics (5 formulas)
    "ActivationEnergyFormula",
    # Stoichiometry (10 formulas)
    "AvogadroParticlesFormula",
    # Solutions (7 formulas)
    "BufferCapacityFormula",
    # Electrochemistry (10 formulas)
    "ButlerVolmerFormula",
    # Thermodynamics (8 formulas)
    "ClausiusClapeyronFormula",
    "ConductivityFormula",
    "DilutionFormula",
    "EmpiricalFormulaRatioFormula",
    "EnthalpyChangeFormula",
    "EquilibriumConstantElectroFormula",
    "EquilibriumConstantFormula",
    "FaradayElectrolysisFormula",
    "GasIdealityCheckFormula",
    "GibbsElectrochemicalFormula",
    "GibbsFreeEnergyFormula",
    "HalfLifeFirstOrderFormula",
    "HalfLifeSecondOrderFormula",
    "IntegratedRateLawFormula",
    "LimitingReagentFormula",
    "MassFromMolesFormula",
    "MolalityFormula",
    "MolarMassFormula",
    "MolarityFormula",
    "MoleFractionFormula",
    "MolesFromMassFormula",
    "NernstEquationFormula",
    "OhmicResistanceFormula",
    "OsmoticPressureFormula",
    "OverpotentialFormula",
    "PercentCompositionFormula",
    "PercentYieldFormula",
    "RaoultsLawFormula",
    "RateConstantFormula",
    "ReactionEntropyChangeFormula",
    "RealGasVanDerWaalsFormula",
    "StandardCellPotentialFormula",
    "TafelEquationFormula",
    "TheoreticalYieldFormula",
    "VantHoffEquationFormula",
    "pHCalculationFormula",
]
