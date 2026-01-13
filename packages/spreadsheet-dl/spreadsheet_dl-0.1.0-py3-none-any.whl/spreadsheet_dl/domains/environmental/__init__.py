"""Environmental Domain Plugin for SpreadsheetDL.

    Environmental domain plugin
    PHASE-C: Domain plugin implementations

Provides environmental science-specific functionality including:
- Pollution index and emissions calculations
- Water quality metrics (BOD, WQI)
- Ecological diversity indices (Shannon, Simpson)
- Sustainability scoring formulas
- Sensor network, lab results, and satellite data importers

Example:
    >>> from spreadsheet_dl.domains.environmental import EnvironmentalDomainPlugin
    >>> plugin = EnvironmentalDomainPlugin()
    >>> plugin.initialize()
"""

# Plugin
# Formulas - Air Quality
from spreadsheet_dl.domains.environmental.formulas.air_quality import (
    AQICalculationFormula,
    EmissionRateFormula,
    PollutionIndexFormula,
)

# Formulas - Carbon
from spreadsheet_dl.domains.environmental.formulas.carbon import (
    CarbonEquivalentFormula,
    EcologicalFootprintFormula,
    EnvironmentalImpactScoreFormula,
    SustainabilityScoreFormula,
)

# Formulas - Climate
from spreadsheet_dl.domains.environmental.formulas.climate import (
    ClimateSensitivityFormula,
    IceSheetMeltingFormula,
    RadiativeForcingFormula,
    SeaLevelRiseFormula,
)

# Formulas - Ecology
from spreadsheet_dl.domains.environmental.formulas.ecology import (
    EcosystemShannonDiversityFormula,
    EcosystemSimpsonIndexFormula,
    EcosystemSpeciesRichnessFormula,
)

# Formulas - Renewable Energy
from spreadsheet_dl.domains.environmental.formulas.renewable import (
    CapacityFactorFormula,
    EnergyPaybackTimeFormula,
    EnergyReturnInvestmentFormula,
    LevelizedCostEnergyFormula,
    SolarPanelOutputFormula,
    WindTurbinePowerFormula,
)

# Formulas - Water Quality
from spreadsheet_dl.domains.environmental.formulas.water_quality import (
    BODCalculationFormula,
    WaterQualityIndexFormula,
)

# Importers
from spreadsheet_dl.domains.environmental.importers import (
    LabResultsImporter,
    SatelliteDataImporter,
    SensorNetworkImporter,
)
from spreadsheet_dl.domains.environmental.plugin import EnvironmentalDomainPlugin

# Utils
from spreadsheet_dl.domains.environmental.utils import (
    calculate_aqi,
    calculate_bod,
    calculate_carbon_equivalent,
    calculate_ecological_footprint,
    calculate_shannon_diversity,
    calculate_simpson_index,
    calculate_wqi,
    format_concentration,
    ppm_to_ugm3,
    ugm3_to_ppm,
)

__all__ = [
    # Formulas - Air Quality
    "AQICalculationFormula",
    # Formulas - Water Quality
    "BODCalculationFormula",
    "CapacityFactorFormula",
    # Formulas - Carbon
    "CarbonEquivalentFormula",
    # Formulas - Climate
    "ClimateSensitivityFormula",
    "EcologicalFootprintFormula",
    # Formulas - Ecology
    "EcosystemShannonDiversityFormula",
    "EcosystemSimpsonIndexFormula",
    "EcosystemSpeciesRichnessFormula",
    "EmissionRateFormula",
    "EnergyPaybackTimeFormula",
    "EnergyReturnInvestmentFormula",
    # Plugin
    "EnvironmentalDomainPlugin",
    "EnvironmentalImpactScoreFormula",
    # Formulas - Climate
    "IceSheetMeltingFormula",
    # Importers
    "LabResultsImporter",
    "LevelizedCostEnergyFormula",
    "PollutionIndexFormula",
    "RadiativeForcingFormula",
    "SatelliteDataImporter",
    "SeaLevelRiseFormula",
    "SensorNetworkImporter",
    "SolarPanelOutputFormula",
    "SustainabilityScoreFormula",
    "WaterQualityIndexFormula",
    "WindTurbinePowerFormula",
    # Utils
    "calculate_aqi",
    "calculate_bod",
    "calculate_carbon_equivalent",
    "calculate_ecological_footprint",
    "calculate_shannon_diversity",
    "calculate_simpson_index",
    "calculate_wqi",
    "format_concentration",
    "ppm_to_ugm3",
    "ugm3_to_ppm",
]
