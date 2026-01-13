"""Chemistry Domain Plugin for SpreadsheetDL.

    Chemistry domain plugin
    BATCH-4: Chemistry domain creation

Provides chemistry-specific functionality including:
- Thermodynamics, solutions, kinetics, stoichiometry, and electrochemistry formulas
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas - Electrochemistry (10 formulas)
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

# Import formulas - Kinetics (5 formulas)
from spreadsheet_dl.domains.chemistry.formulas.kinetics import (
    ActivationEnergyFormula,
    HalfLifeFirstOrderFormula,
    HalfLifeSecondOrderFormula,
    IntegratedRateLawFormula,
    RateConstantFormula,
)

# Import formulas - Solutions (7 formulas)
from spreadsheet_dl.domains.chemistry.formulas.solutions import (
    BufferCapacityFormula,
    MolalityFormula,
    MolarityFormula,
    MoleFractionFormula,
    OsmoticPressureFormula,
    RaoultsLawFormula,
    pHCalculationFormula,
)

# Import formulas - Stoichiometry (10 formulas)
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

# Import formulas - Thermodynamics (8 formulas)
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


class ChemistryDomainPlugin(BaseDomainPlugin):
    """Chemistry domain plugin.

        Complete Chemistry domain plugin
        BATCH-4: Chemistry domain creation

    Provides comprehensive chemistry functionality for SpreadsheetDL
    with formulas for thermodynamics, solutions, kinetics, stoichiometry, and electrochemistry.

    Formulas (40 total):
        Thermodynamics (8):
        - GIBBS_FREE_ENERGY: Gibbs free energy change
        - ENTHALPY_CHANGE: Enthalpy change for reaction
        - REACTION_ENTROPY_CHANGE: Reaction entropy change
        - EQUILIBRIUM_CONSTANT: Equilibrium constant from Gibbs
        - VANT_HOFF_EQUATION: Temperature dependence of K
        - CLAUSIUS_CLAPEYRON: Vapor pressure
        - GAS_IDEALITY_CHECK: Verify PV/(nRT) = 1 for ideal gas
        - REAL_GAS_VAN_DER_WAALS: Van der Waals equation

        Solutions (7):
        - MOLARITY: Moles per liter
        - MOLALITY: Moles per kg solvent
        - MOLE_FRACTION: Component ratio
        - RAOULTS_LAW: Vapor pressure lowering
        - OSMOTIC_PRESSURE: Colligative property
        - PH_CALCULATION: pH from H+ concentration
        - BUFFER_CAPACITY: Buffer capacity

        Kinetics (5):
        - RATE_CONSTANT: Arrhenius equation
        - HALF_LIFE_FIRST_ORDER: First-order half-life
        - HALF_LIFE_SECOND_ORDER: Second-order half-life
        - INTEGRATED_RATE_LAW: Concentration vs time
        - ACTIVATION_ENERGY: Activation energy from rate constants

        Stoichiometry (10):
        - MOLAR_MASS: Calculate molar mass from mass and moles
        - MASS_FROM_MOLES: Calculate mass from moles
        - MOLES_FROM_MASS: Calculate moles from mass
        - LIMITING_REAGENT: Find limiting reagent
        - THEORETICAL_YIELD: Calculate theoretical yield
        - PERCENT_YIELD: Calculate percent yield
        - PERCENT_COMPOSITION: Calculate percent composition
        - EMPIRICAL_FORMULA_RATIO: Calculate empirical formula ratio
        - DILUTION: Dilution calculations (M1V1 = M2V2)
        - AVOGADRO_PARTICLES: Convert between moles and particles

        Electrochemistry (10):
        - NERNST_EQUATION: Nernst equation for cell potential
        - FARADAY_ELECTROLYSIS: Faraday's laws of electrolysis
        - STANDARD_CELL_POTENTIAL: Standard cell potential
        - GIBBS_ELECTROCHEMICAL: Gibbs free energy from cell potential
        - EQUILIBRIUM_CONSTANT_ELECTRO: Equilibrium constant from cell potential
        - OHMIC_RESISTANCE: Ohmic resistance
        - OVERPOTENTIAL: Overpotential calculation
        - TAFEL_EQUATION: Tafel equation
        - BUTLER_VOLMER: Butler-Volmer equation
        - CONDUCTIVITY: Electrical conductivity

    Example:
        >>> plugin = ChemistryDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with chemistry plugin information

            Plugin metadata requirements
            BATCH-4: Chemistry domain metadata
        """
        return PluginMetadata(
            name="chemistry",
            version="0.1.0",
            description=(
                "Chemistry formulas for thermodynamics, solutions, kinetics, stoichiometry, and electrochemistry"
            ),
            author="SpreadsheetDL",
            license="MIT",
            tags=(
                "chemistry",
                "thermodynamics",
                "kinetics",
                "solutions",
                "stoichiometry",
                "electrochemistry",
            ),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas.

            Plugin initialization with all components
            BATCH-4: Chemistry domain initialization

        Raises:
            Exception: If initialization fails
        """
        # Register thermodynamics formulas (8 total)
        self.register_formula("GIBBS_FREE_ENERGY", GibbsFreeEnergyFormula)
        self.register_formula("ENTHALPY_CHANGE", EnthalpyChangeFormula)
        self.register_formula("REACTION_ENTROPY_CHANGE", ReactionEntropyChangeFormula)
        self.register_formula("EQUILIBRIUM_CONSTANT", EquilibriumConstantFormula)
        self.register_formula("VANT_HOFF_EQUATION", VantHoffEquationFormula)
        self.register_formula("CLAUSIUS_CLAPEYRON", ClausiusClapeyronFormula)
        self.register_formula("GAS_IDEALITY_CHECK", GasIdealityCheckFormula)
        self.register_formula("REAL_GAS_VAN_DER_WAALS", RealGasVanDerWaalsFormula)

        # Register solutions formulas (7 total)
        self.register_formula("MOLARITY", MolarityFormula)
        self.register_formula("MOLALITY", MolalityFormula)
        self.register_formula("MOLE_FRACTION", MoleFractionFormula)
        self.register_formula("RAOULTS_LAW", RaoultsLawFormula)
        self.register_formula("OSMOTIC_PRESSURE", OsmoticPressureFormula)
        self.register_formula("PH_CALCULATION", pHCalculationFormula)
        self.register_formula("BUFFER_CAPACITY", BufferCapacityFormula)

        # Register kinetics formulas (5 total)
        self.register_formula("RATE_CONSTANT", RateConstantFormula)
        self.register_formula("HALF_LIFE_FIRST_ORDER", HalfLifeFirstOrderFormula)
        self.register_formula("HALF_LIFE_SECOND_ORDER", HalfLifeSecondOrderFormula)
        self.register_formula("INTEGRATED_RATE_LAW", IntegratedRateLawFormula)
        self.register_formula("ACTIVATION_ENERGY", ActivationEnergyFormula)

        # Register stoichiometry formulas (10 total)
        self.register_formula("MOLAR_MASS", MolarMassFormula)
        self.register_formula("MASS_FROM_MOLES", MassFromMolesFormula)
        self.register_formula("MOLES_FROM_MASS", MolesFromMassFormula)
        self.register_formula("LIMITING_REAGENT", LimitingReagentFormula)
        self.register_formula("THEORETICAL_YIELD", TheoreticalYieldFormula)
        self.register_formula("PERCENT_YIELD", PercentYieldFormula)
        self.register_formula("PERCENT_COMPOSITION", PercentCompositionFormula)
        self.register_formula("EMPIRICAL_FORMULA_RATIO", EmpiricalFormulaRatioFormula)
        self.register_formula("DILUTION", DilutionFormula)
        self.register_formula("AVOGADRO_PARTICLES", AvogadroParticlesFormula)

        # Register electrochemistry formulas (10 total)
        self.register_formula("NERNST_EQUATION", NernstEquationFormula)
        self.register_formula("FARADAY_ELECTROLYSIS", FaradayElectrolysisFormula)
        self.register_formula("STANDARD_CELL_POTENTIAL", StandardCellPotentialFormula)
        self.register_formula("GIBBS_ELECTROCHEMICAL", GibbsElectrochemicalFormula)
        self.register_formula(
            "EQUILIBRIUM_CONSTANT_ELECTRO", EquilibriumConstantElectroFormula
        )
        self.register_formula("OHMIC_RESISTANCE", OhmicResistanceFormula)
        self.register_formula("OVERPOTENTIAL", OverpotentialFormula)
        self.register_formula("TAFEL_EQUATION", TafelEquationFormula)
        self.register_formula("BUTLER_VOLMER", ButlerVolmerFormula)
        self.register_formula("IONIC_CONDUCTIVITY", ConductivityFormula)

    def cleanup(self) -> None:
        """Cleanup plugin resources.

        No resources need explicit cleanup for this plugin.

            Plugin cleanup method
            BATCH-4: Chemistry domain cleanup
        """
        # No cleanup needed for this plugin
        pass

    def validate(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if plugin has required formulas registered

            Plugin validation
            BATCH-4: Chemistry domain validation
        """
        # Verify we have all required components
        required_formulas = 40  # 8 thermodynamics + 7 solutions + 5 kinetics + 10 stoichiometry + 10 electrochemistry

        return len(self._formulas) >= required_formulas


__all__ = [
    "ChemistryDomainPlugin",
]
