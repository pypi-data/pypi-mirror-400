"""Biology Domain Plugin for SpreadsheetDL.

    Biology domain plugin
    PHASE-C: Domain plugin implementations

Provides biology-specific functionality including:
- Molecular biology, biochemistry, and ecology formulas
- FASTA, GenBank, and plate reader importers
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas
from spreadsheet_dl.domains.biology.formulas.biochemistry import (
    BradfordAssayFormula,
    DilutionFactorFormula,
    EnzymeActivityFormula,
    MichaelisMentenFormula,
)
from spreadsheet_dl.domains.biology.formulas.cell_biology import (
    CellDensity,
    DoublingTime,
    SpecificGrowthRate,
    ViabilityPercent,
)
from spreadsheet_dl.domains.biology.formulas.ecology import (
    PopulationGrowthFormula,
    ShannonDiversityFormula,
    SimpsonIndexFormula,
    SpeciesRichnessFormula,
)
from spreadsheet_dl.domains.biology.formulas.genetics import (
    Chi2GeneticsFormula,
    HardyWeinbergFormula,
    InbreedingCoefficientFormula,
    LinkageDisequilibriumFormula,
    RecombinationFrequencyFormula,
)
from spreadsheet_dl.domains.biology.formulas.molecular import (
    ConcentrationFormula,
    FoldChangeFormula,
    GCContentFormula,
    MeltingTempFormula,
)
from spreadsheet_dl.domains.biology.formulas.pharmacokinetics import (
    ClearanceFormula,
    HalfLifeFormula,
    LoadingDoseFormula,
    MaintenanceDoseFormula,
    VolumeOfDistributionFormula,
)

# Import importers
from spreadsheet_dl.domains.biology.importers.fasta import FASTAImporter
from spreadsheet_dl.domains.biology.importers.genbank import GenBankImporter
from spreadsheet_dl.domains.biology.importers.plate_reader import PlateReaderImporter


class BiologyDomainPlugin(BaseDomainPlugin):
    """Biology domain plugin.

        Complete Biology domain plugin
        PHASE-C: Domain plugin implementations

    Provides comprehensive biology functionality for SpreadsheetDL
    with formulas and importers tailored for research workflows.

    Formulas (26 total):
        Cell Biology (4):
        - CELL_DENSITY: Cell density calculation
        - VIABILITY_PERCENT: Cell viability percentage
        - DOUBLING_TIME: Population doubling time
        - SPECIFIC_GROWTH_RATE: Specific growth rate

        Molecular Biology (4):
        - CONCENTRATION: Nucleic acid concentration
        - FOLD_CHANGE: Gene expression fold change
        - GC_CONTENT: GC content percentage
        - MELTING_TEMP: DNA melting temperature

        Biochemistry (4):
        - BRADFORD_ASSAY: Protein concentration
        - ENZYME_ACTIVITY: Enzyme specific activity
        - MICHAELIS_MENTEN: Michaelis-Menten kinetics
        - DILUTION_FACTOR: Serial dilution calculations

        Ecology (4):
        - SHANNON_DIVERSITY: Shannon diversity index
        - SIMPSON_INDEX: Simpson's diversity index
        - SPECIES_RICHNESS: Species richness
        - POPULATION_GROWTH: Population growth rate

        Pharmacokinetics (5):
        - CLEARANCE: Drug elimination rate
        - VOLUME_OF_DISTRIBUTION: Apparent volume of distribution
        - HALF_LIFE: Elimination half-life
        - LOADING_DOSE: Initial loading dose
        - MAINTENANCE_DOSE: Steady-state dosing

        Genetics (5):
        - HARDY_WEINBERG: Allele frequency equilibrium
        - LINKAGE_DISEQUILIBRIUM: Non-random association
        - RECOMBINATION_FREQUENCY: Genetic distance
        - CHI2_GENETICS: Goodness of fit test
        - INBREEDING_COEFFICIENT: Relatedness measure

    Importers:
        - PlateReaderImporter: Plate reader data (CSV/XML)
        - FASTAImporter: FASTA sequence files
        - GenBankImporter: GenBank sequence files

    Example:
        >>> plugin = BiologyDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with biology plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="biology",
            version="0.1.0",
            description=(
                "Biology templates, formulas, and importers for research and analysis"
            ),
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=("biology", "research", "genetics", "ecology", "lab-notebook"),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas and importers.

            Plugin initialization with all components

        Raises:
            Exception: If initialization fails
        """
        # Register cell biology formulas (4 total)
        self.register_formula("CELL_DENSITY", CellDensity)
        self.register_formula("VIABILITY_PERCENT", ViabilityPercent)
        self.register_formula("DOUBLING_TIME", DoublingTime)
        self.register_formula("SPECIFIC_GROWTH_RATE", SpecificGrowthRate)

        # Register molecular biology formulas (4 total)
        self.register_formula("CONCENTRATION", ConcentrationFormula)
        self.register_formula("FOLD_CHANGE", FoldChangeFormula)
        self.register_formula("GC_CONTENT", GCContentFormula)
        self.register_formula("MELTING_TEMP", MeltingTempFormula)

        # Register biochemistry formulas (4 total)
        self.register_formula("BRADFORD_ASSAY", BradfordAssayFormula)
        self.register_formula("ENZYME_ACTIVITY", EnzymeActivityFormula)
        self.register_formula("MICHAELIS_MENTEN", MichaelisMentenFormula)
        self.register_formula("DILUTION_FACTOR", DilutionFactorFormula)

        # Register ecology formulas (4 total)
        self.register_formula("SHANNON_DIVERSITY", ShannonDiversityFormula)
        self.register_formula("SIMPSON_INDEX", SimpsonIndexFormula)
        self.register_formula("SPECIES_RICHNESS", SpeciesRichnessFormula)
        self.register_formula("POPULATION_GROWTH", PopulationGrowthFormula)

        # Register pharmacokinetics formulas (5 total)
        self.register_formula("CLEARANCE", ClearanceFormula)
        self.register_formula("VOLUME_OF_DISTRIBUTION", VolumeOfDistributionFormula)
        self.register_formula("HALF_LIFE", HalfLifeFormula)
        self.register_formula("LOADING_DOSE", LoadingDoseFormula)
        self.register_formula("MAINTENANCE_DOSE", MaintenanceDoseFormula)

        # Register genetics formulas (5 total)
        self.register_formula("HARDY_WEINBERG", HardyWeinbergFormula)
        self.register_formula("LINKAGE_DISEQUILIBRIUM", LinkageDisequilibriumFormula)
        self.register_formula("RECOMBINATION_FREQUENCY", RecombinationFrequencyFormula)
        self.register_formula("CHI2_GENETICS", Chi2GeneticsFormula)
        self.register_formula("INBREEDING_COEFFICIENT", InbreedingCoefficientFormula)

        # Register importers (3 total)
        self.register_importer("plate_reader", PlateReaderImporter)
        self.register_importer("fasta", FASTAImporter)
        self.register_importer("genbank", GenBankImporter)

    def cleanup(self) -> None:
        """Cleanup plugin resources.

        No resources need explicit cleanup for this plugin.

            Plugin cleanup method
        """
        # No cleanup needed for this plugin
        pass

    def validate(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if plugin has required formulas and importers registered

            Plugin validation
        """
        # Verify we have all required components
        required_formulas = 26  # 4 cell biology + 4 molecular + 4 biochemistry + 4 ecology + 5 pharmacokinetics + 5 genetics
        required_importers = 3

        return (
            len(self._formulas) >= required_formulas
            and len(self._importers) >= required_importers
        )


__all__ = [
    "BiologyDomainPlugin",
]
