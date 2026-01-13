"""Mechanical Engineering Domain Plugin for SpreadsheetDL.

    Mechanical Engineering domain plugin
    PHASE-C: Domain plugin implementations
    BATCH2-MECH: Extended with fluid mechanics and heat transfer formulas

Provides mechanical engineering-specific functionality including:
- Stress/strain, moment, thermal, fatigue, and fluid mechanics formulas
- CAD metadata, FEA results, and material database importers
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas
from spreadsheet_dl.domains.mechanical_engineering.formulas.fatigue import (
    FatigueLifeFormula,
    SafetyFactorFormula,
    StressConcentrationFormula,
)
from spreadsheet_dl.domains.mechanical_engineering.formulas.fluid_mechanics import (
    BernoulliEquation,
    DarcyWeisbach,
    DragForce,
    LiftForce,
    PoiseuilleLaw,
    ReynoldsNumber,
)
from spreadsheet_dl.domains.mechanical_engineering.formulas.moment import (
    BendingStressFormula,
    MomentOfInertiaFormula,
    TorsionalStressFormula,
)
from spreadsheet_dl.domains.mechanical_engineering.formulas.stress_strain import (
    StrainFormula,
    StressFormula,
    YoungsModulusFormula,
)
from spreadsheet_dl.domains.mechanical_engineering.formulas.thermal import (
    ConvectionCoefficient,
    FinEfficiency,
    LinearThermalExpansionFormula,
    LogMeanTempDiff,
    NusseltNumber,
    RadiationHeatTransfer,
    ThermalResistance,
    ThermalStressFormula,
)

# Import importers
from spreadsheet_dl.domains.mechanical_engineering.importers.cad_metadata import (
    CADMetadataImporter,
)
from spreadsheet_dl.domains.mechanical_engineering.importers.fea_results import (
    FEAResultsImporter,
)
from spreadsheet_dl.domains.mechanical_engineering.importers.material_db import (
    MaterialDatabaseImporter,
)


class MechanicalEngineeringDomainPlugin(BaseDomainPlugin):
    """Mechanical Engineering domain plugin.

        Complete Mechanical Engineering domain plugin
        PHASE-C: Domain plugin implementations
        BATCH2-MECH: Extended with 12 new formulas

    Provides comprehensive mechanical engineering functionality for SpreadsheetDL
    with formulas and importers tailored for mechanical design and analysis.

    Formulas (23 total):
        Stress/Strain (3):
        - STRESS: Stress calculation
        - STRAIN: Strain calculation
        - YOUNGS_MODULUS: Young's modulus

        Moment (3):
        - MOMENT_OF_INERTIA: Moment of inertia
        - BENDING_STRESS: Bending stress
        - TORSIONAL_STRESS: Torsional stress

        Thermal (8):
        - THERMAL_EXPANSION: Thermal expansion
        - THERMAL_STRESS: Thermal stress
        - CONVECTION_COEFFICIENT: Heat transfer coefficient
        - RADIATION_HEAT_TRANSFER: Radiative heat transfer
        - THERMAL_RESISTANCE: Resistance to heat flow
        - LOG_MEAN_TEMP_DIFF: LMTD for heat exchangers
        - FIN_EFFICIENCY: Extended surface efficiency
        - NUSSELT_NUMBER: Convection characterization

        Fluid Mechanics (6):
        - REYNOLDS_NUMBER: Flow regime determination
        - BERNOULLI_EQUATION: Total energy per unit volume
        - DARCY_WEISBACH: Pressure drop in pipes
        - POISEUILLE_LAW: Viscous flow rate
        - DRAG_FORCE: Fluid resistance force
        - LIFT_FORCE: Aerodynamic lift

        Fatigue (3):
        - FATIGUE_LIFE: Fatigue life calculation
        - SAFETY_FACTOR: Safety factor
        - STRESS_CONCENTRATION: Stress concentration factor

    Importers:
        - CADMetadataImporter: CAD file metadata (STEP/IGES)
        - FEAResultsImporter: FEA results data
        - MaterialDatabaseImporter: Material properties database

    Example:
        >>> plugin = MechanicalEngineeringDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with mechanical engineering plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="mechanical_engineering",
            version="0.1.0",
            description="Mechanical engineering formulas and importers for design and analysis",
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=(
                "mechanical-engineering",
                "stress-analysis",
                "materials",
                "manufacturing",
                "fea",
                "cad",
                "fluid-mechanics",
                "heat-transfer",
            ),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas and importers.

            Plugin initialization with all components
            BATCH2-MECH: Extended registration with new formulas

        Raises:
            Exception: If initialization fails
        """
        # Register stress/strain formulas (3 total)
        self.register_formula("STRESS", StressFormula)
        self.register_formula("STRAIN", StrainFormula)
        self.register_formula("YOUNGS_MODULUS", YoungsModulusFormula)

        # Register moment formulas (3 total)
        self.register_formula("MOMENT_OF_INERTIA", MomentOfInertiaFormula)
        self.register_formula("BENDING_STRESS", BendingStressFormula)
        self.register_formula("TORSIONAL_STRESS", TorsionalStressFormula)

        # Register thermal formulas (8 total - 2 original + 6 new)
        self.register_formula("LINEAR_THERMAL_EXPANSION", LinearThermalExpansionFormula)
        self.register_formula("THERMAL_STRESS", ThermalStressFormula)
        self.register_formula("CONVECTION_COEFFICIENT", ConvectionCoefficient)
        self.register_formula("RADIATION_HEAT_TRANSFER", RadiationHeatTransfer)
        self.register_formula("THERMAL_RESISTANCE", ThermalResistance)
        self.register_formula("LOG_MEAN_TEMP_DIFF", LogMeanTempDiff)
        self.register_formula("FIN_EFFICIENCY", FinEfficiency)
        self.register_formula("NUSSELT_NUMBER", NusseltNumber)

        # Register fluid mechanics formulas (6 total - NEW)
        self.register_formula("REYNOLDS_NUMBER", ReynoldsNumber)
        self.register_formula("BERNOULLI_EQUATION", BernoulliEquation)
        self.register_formula("DARCY_WEISBACH", DarcyWeisbach)
        self.register_formula("POISEUILLE_LAW", PoiseuilleLaw)
        self.register_formula("DRAG_FORCE", DragForce)
        self.register_formula("LIFT_FORCE", LiftForce)

        # Register fatigue formulas (3 total)
        self.register_formula("FATIGUE_LIFE", FatigueLifeFormula)
        self.register_formula("SAFETY_FACTOR", SafetyFactorFormula)
        self.register_formula("STRESS_CONCENTRATION", StressConcentrationFormula)

        # Register importers (3 total)
        self.register_importer("cad_metadata", CADMetadataImporter)
        self.register_importer("fea_results", FEAResultsImporter)
        self.register_importer("material_db", MaterialDatabaseImporter)

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
            BATCH2-MECH: Updated to require 23 formulas (11 original + 12 new)
        """
        required_formulas = (
            23  # 3 stress/strain + 3 moment + 8 thermal + 6 fluid + 3 fatigue
        )
        required_importers = 3

        return (
            len(self._formulas) >= required_formulas
            and len(self._importers) >= required_importers
        )


__all__ = [
    "MechanicalEngineeringDomainPlugin",
]
