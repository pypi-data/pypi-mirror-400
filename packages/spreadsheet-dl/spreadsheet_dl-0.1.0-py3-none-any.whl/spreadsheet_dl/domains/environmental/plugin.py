"""Environmental Domain Plugin for SpreadsheetDL.

    Environmental domain plugin
    PHASE-C: Domain plugin implementations

Provides environmental science-specific functionality including:
- Pollution and sustainability formulas
- Sensor network and satellite data importers
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas
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
from spreadsheet_dl.domains.environmental.formulas.renewable import (
    CapacityFactorFormula,
    EnergyPaybackTimeFormula,
    EnergyReturnInvestmentFormula,
    LevelizedCostEnergyFormula,
    SolarPanelOutputFormula,
    WindTurbinePowerFormula,
)
from spreadsheet_dl.domains.environmental.formulas.water_quality import (
    BODCalculationFormula,
    WaterQualityIndexFormula,
)

# Import importers
from spreadsheet_dl.domains.environmental.importers.lab_results import (
    LabResultsImporter,
)
from spreadsheet_dl.domains.environmental.importers.satellite_data import (
    SatelliteDataImporter,
)
from spreadsheet_dl.domains.environmental.importers.sensor_network import (
    SensorNetworkImporter,
)


class EnvironmentalDomainPlugin(BaseDomainPlugin):
    """Environmental domain plugin.

        Complete Environmental domain plugin
        PHASE-C: Domain plugin implementations

    Provides comprehensive environmental science functionality for SpreadsheetDL
    with formulas and importers tailored for environmental monitoring,
    assessment, and sustainability tracking.

    Formulas (22 total):
        Air Quality (3):
        - AQI_CALCULATION: Air Quality Index
        - EMISSION_RATE: Pollutant emission rate
        - POLLUTION_INDEX: Pollution severity index

        Water Quality (2):
        - WATER_QUALITY_INDEX: WQI calculation
        - BOD_CALCULATION: Biochemical oxygen demand

        Ecology (3):
        - SHANNON_DIVERSITY: Shannon diversity index
        - SIMPSON_INDEX: Simpson's diversity index
        - SPECIES_RICHNESS: Species count

        Carbon/Sustainability (4):
        - CARBON_EQUIVALENT: CO2 equivalent
        - ECOLOGICAL_FOOTPRINT: Ecological footprint
        - SUSTAINABILITY_SCORE: Sustainability metric
        - ENVIRONMENTAL_IMPACT_SCORE: Impact assessment

        Climate Modeling (4):
        - RADIATIVE_FORCING: Climate forcing from CO2
        - CLIMATE_SENSITIVITY: Temperature response to CO2 doubling
        - SEA_LEVEL_RISE: Thermal expansion calculation
        - ICE_SHEET_MELTING: Mass balance equation

        Renewable Energy (6):
        - SOLAR_PANEL_OUTPUT: Solar PV power output
        - WIND_TURBINE_POWER: Wind turbine power
        - ENERGY_PAYBACK_TIME: Energy payback time
        - CAPACITY_FACTOR: Capacity factor
        - LEVELIZED_COST_ENERGY: Levelized cost of energy
        - ENERGY_RETURN_INVESTMENT: EROI ratio

    Importers:
        - SensorNetworkImporter: IoT sensor data
        - LabResultsImporter: Laboratory analysis results
        - SatelliteDataImporter: Remote sensing data

    Example:
        >>> plugin = EnvironmentalDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with environmental plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="environmental",
            version="0.1.0",
            description=("Environmental monitoring formulas and importers"),
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=(
                "environmental",
                "monitoring",
                "sustainability",
                "ecology",
                "pollution",
            ),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas and importers.

            Plugin initialization with all components

        Raises:
            Exception: If initialization fails
        """
        # Register air quality formulas (3)
        self.register_formula("AQI_CALCULATION", AQICalculationFormula)
        self.register_formula("EMISSION_RATE", EmissionRateFormula)
        self.register_formula("POLLUTION_INDEX", PollutionIndexFormula)

        # Register water quality formulas (2)
        self.register_formula("WATER_QUALITY_INDEX", WaterQualityIndexFormula)
        self.register_formula("BOD_CALCULATION", BODCalculationFormula)

        # Register ecology formulas (3)
        self.register_formula(
            "ECOSYSTEM_SHANNON_DIVERSITY", EcosystemShannonDiversityFormula
        )
        self.register_formula("ECOSYSTEM_SIMPSON_INDEX", EcosystemSimpsonIndexFormula)
        self.register_formula(
            "ECOSYSTEM_SPECIES_RICHNESS", EcosystemSpeciesRichnessFormula
        )

        # Register carbon/sustainability formulas (4)
        self.register_formula("CARBON_EQUIVALENT", CarbonEquivalentFormula)
        self.register_formula("ECOLOGICAL_FOOTPRINT", EcologicalFootprintFormula)
        self.register_formula("SUSTAINABILITY_SCORE", SustainabilityScoreFormula)
        self.register_formula(
            "ENVIRONMENTAL_IMPACT_SCORE", EnvironmentalImpactScoreFormula
        )

        # Register climate modeling formulas (4)
        self.register_formula("RADIATIVE_FORCING", RadiativeForcingFormula)
        self.register_formula("CLIMATE_SENSITIVITY", ClimateSensitivityFormula)
        self.register_formula("SEA_LEVEL_RISE", SeaLevelRiseFormula)
        self.register_formula("ICE_SHEET_MELTING", IceSheetMeltingFormula)

        # Register renewable energy formulas (6)
        self.register_formula("SOLAR_PANEL_OUTPUT", SolarPanelOutputFormula)
        self.register_formula("WIND_TURBINE_POWER", WindTurbinePowerFormula)
        self.register_formula("ENERGY_PAYBACK_TIME", EnergyPaybackTimeFormula)
        self.register_formula("CAPACITY_FACTOR", CapacityFactorFormula)
        self.register_formula("LEVELIZED_COST_ENERGY", LevelizedCostEnergyFormula)
        self.register_formula("ENERGY_RETURN_INVESTMENT", EnergyReturnInvestmentFormula)

        # Register importers (3 total)
        self.register_importer("sensor_network", SensorNetworkImporter)
        self.register_importer("lab_results", LabResultsImporter)
        self.register_importer("satellite_data", SatelliteDataImporter)

    def cleanup(self) -> None:
        """Cleanup plugin resources.

        No resources need explicit cleanup for this plugin.

            Plugin cleanup method
        """
        pass

    def validate(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if plugin has required formulas and importers registered

            Plugin validation
        """
        required_formulas = (
            22  # 3 air + 2 water + 3 ecology + 4 carbon + 4 climate + 6 renewable
        )
        required_importers = 3

        return (
            len(self._formulas) >= required_formulas
            and len(self._importers) >= required_importers
        )


__all__ = [
    "EnvironmentalDomainPlugin",
]
