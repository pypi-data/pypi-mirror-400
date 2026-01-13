"""Civil Engineering Domain Plugin for SpreadsheetDL.

Provides comprehensive civil engineering functionality including:
- Beam, soil, concrete, and load formulas
- Survey data, structural results, and building code importers

    Civil Engineering domain plugin

Example:
    >>> from spreadsheet_dl.domains.civil_engineering import CivilEngineeringDomainPlugin
    >>> plugin = CivilEngineeringDomainPlugin()
    >>> plugin.initialize()
    >>> formulas = plugin.list_formulas()
"""

# Import all formulas
from spreadsheet_dl.domains.civil_engineering.formulas import (
    BeamDeflectionFormula,
    BearingCapacityFormula,
    BearingCapacityTerzaghi,
    ConcreteStrengthFormula,
    ConsolidationSettlement,
    CrackWidthFormula,
    DeadLoadFormula,
    LiveLoadFormula,
    MomentFormula,
    ReinforcementRatioFormula,
    SeismicLoadFormula,
    SettlementElastic,
    SettlementFormula,
    ShearStressFormula,
    SoilPressureFormula,
    StoppingDistance,
    TrafficFlow,
    WindLoadFormula,
)

# Import all importers
from spreadsheet_dl.domains.civil_engineering.importers import (
    BuildingCodesImporter,
    StructuralResultsImporter,
    SurveyDataImporter,
)
from spreadsheet_dl.domains.civil_engineering.plugin import (
    CivilEngineeringDomainPlugin,
)

# Import utilities
from spreadsheet_dl.domains.civil_engineering.utils import (
    ConcreteMix,
    LoadCombination,
    LoadCombinationCode,
    beam_self_weight,
    bearing_capacity_factors,
    calculate_cement_content,
    consolidation_settlement,
    design_concrete_mix,
    ft_to_m,
    get_load_combinations,
    kn_to_lbf,
    knpm_to_lbpft,
    lbf_to_kn,
    lbpft_to_knpm,
    m_to_ft,
    mpa_to_psi,
    psi_to_mpa,
)

__all__ = [
    # Formulas - Beam
    "BeamDeflectionFormula",
    # Formulas - Soil
    "BearingCapacityFormula",
    # Formulas - Foundation
    "BearingCapacityTerzaghi",
    # Importers
    "BuildingCodesImporter",
    # Plugin
    "CivilEngineeringDomainPlugin",
    # Utilities
    "ConcreteMix",
    # Formulas - Concrete
    "ConcreteStrengthFormula",
    "ConsolidationSettlement",
    "CrackWidthFormula",
    # Formulas - Loads
    "DeadLoadFormula",
    "LiveLoadFormula",
    "LoadCombination",
    "LoadCombinationCode",
    "MomentFormula",
    "ReinforcementRatioFormula",
    "SeismicLoadFormula",
    "SettlementElastic",
    "SettlementFormula",
    "ShearStressFormula",
    "SoilPressureFormula",
    "StoppingDistance",
    "StructuralResultsImporter",
    "SurveyDataImporter",
    "TrafficFlow",
    "WindLoadFormula",
    "beam_self_weight",
    "bearing_capacity_factors",
    "calculate_cement_content",
    "consolidation_settlement",
    "design_concrete_mix",
    "ft_to_m",
    "get_load_combinations",
    "kn_to_lbf",
    "knpm_to_lbpft",
    "lbf_to_kn",
    "lbpft_to_knpm",
    "m_to_ft",
    "mpa_to_psi",
    "psi_to_mpa",
]
