"""Environmental domain formulas.

    Environmental domain formula extensions

Provides 22 specialized formulas for environmental science:
- Air quality (AQI, emission rate, pollution index)
- Water quality (WQI, BOD)
- Ecology (Shannon diversity, Simpson index, species richness)
- Carbon/Sustainability (CO2 equivalent, footprint, impact score)
- Climate modeling (radiative forcing, climate sensitivity, sea level, ice sheets)
- Renewable energy (solar, wind, EPBT, LCOE, capacity factor, EROI)
"""

from spreadsheet_dl.domains.environmental.formulas.air_quality import (
    AQICalculationFormula,
    EmissionRateFormula,
    PollutionIndexFormula,
)
from spreadsheet_dl.domains.environmental.formulas.carbon import (
    CarbonEquivalentFormula,
    EcologicalFootprintFormula,
    EnvironmentalImpactScoreFormula,
    SustainabilityScoreFormula,
)
from spreadsheet_dl.domains.environmental.formulas.climate import (
    CarbonBudgetFormula,
    ClimateSensitivityFormula,
    IceSheetMeltingFormula,
    RadiativeForcingFormula,
    SeaLevelRiseFormula,
)
from spreadsheet_dl.domains.environmental.formulas.ecology import (
    EcosystemShannonDiversityFormula,
    EcosystemSimpsonIndexFormula,
    EcosystemSpeciesRichnessFormula,
)
from spreadsheet_dl.domains.environmental.formulas.lifecycle import (
    AcidificationPotential,
    EutrophicationPotential,
    GlobalWarmingPotential,
)
from spreadsheet_dl.domains.environmental.formulas.renewable import (
    BatteryStorageCapacityFormula,
    CapacityFactorFormula,
    CarbonIntensityFormula,
    EnergyPaybackTimeFormula,
    EnergyReturnInvestmentFormula,
    GridStabilityIndexFormula,
    LevelizedCostEnergyFormula,
    SolarPanelEfficiencyFormula,
    SolarPanelOutputFormula,
    WindCapacityFactorFormula,
    WindTurbinePowerFormula,
)
from spreadsheet_dl.domains.environmental.formulas.water_quality import (
    BODCalculationFormula,
    WaterQualityIndexFormula,
)

__all__ = [
    "AQICalculationFormula",
    "AcidificationPotential",
    "BODCalculationFormula",
    "BatteryStorageCapacityFormula",
    "CapacityFactorFormula",
    "CarbonBudgetFormula",
    "CarbonEquivalentFormula",
    "CarbonIntensityFormula",
    "ClimateSensitivityFormula",
    "EcologicalFootprintFormula",
    "EcosystemShannonDiversityFormula",
    "EcosystemSimpsonIndexFormula",
    "EcosystemSpeciesRichnessFormula",
    "EmissionRateFormula",
    "EnergyPaybackTimeFormula",
    "EnergyReturnInvestmentFormula",
    "EnvironmentalImpactScoreFormula",
    "EutrophicationPotential",
    "GlobalWarmingPotential",
    "GridStabilityIndexFormula",
    "IceSheetMeltingFormula",
    "LevelizedCostEnergyFormula",
    "PollutionIndexFormula",
    "RadiativeForcingFormula",
    "SeaLevelRiseFormula",
    "SolarPanelEfficiencyFormula",
    "SolarPanelOutputFormula",
    "SustainabilityScoreFormula",
    "WaterQualityIndexFormula",
    "WindCapacityFactorFormula",
    "WindTurbinePowerFormula",
]
