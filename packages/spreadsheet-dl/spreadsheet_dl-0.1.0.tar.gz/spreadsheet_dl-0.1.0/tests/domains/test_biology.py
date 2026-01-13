"""
Tests for Biology domain plugin.

    Comprehensive tests for Biology domain (95%+ coverage target)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.domains.biology import (
    BiologyDomainPlugin,
    BradfordAssayFormula,
    ConcentrationFormula,
    DilutionFactorFormula,
    EnzymeActivityFormula,
    FASTAImporter,
    FoldChangeFormula,
    GCContentFormula,
    GenBankImporter,
    MeltingTempFormula,
    MichaelisMentenFormula,
    PlateReaderImporter,
    PopulationGrowthFormula,
    ShannonDiversityFormula,
    SimpsonIndexFormula,
    SpeciesRichnessFormula,
)
from spreadsheet_dl.domains.biology.utils import (
    calculate_dilution,
    calculate_gc_content,
    calculate_melting_temp,
    calculate_od_to_concentration,
    format_scientific_notation,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = BiologyDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "biology"
    assert metadata.version == "0.1.0"
    assert "biology" in metadata.tags
    assert "research" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = BiologyDomainPlugin()
    plugin.initialize()

    # Verify molecular biology formulas registered (4 total)
    assert plugin.get_formula("CONCENTRATION") == ConcentrationFormula
    assert plugin.get_formula("FOLD_CHANGE") == FoldChangeFormula
    assert plugin.get_formula("GC_CONTENT") == GCContentFormula
    assert plugin.get_formula("MELTING_TEMP") == MeltingTempFormula

    # Verify biochemistry formulas registered (4 total)
    assert plugin.get_formula("BRADFORD_ASSAY") == BradfordAssayFormula
    assert plugin.get_formula("ENZYME_ACTIVITY") == EnzymeActivityFormula
    assert plugin.get_formula("MICHAELIS_MENTEN") == MichaelisMentenFormula
    assert plugin.get_formula("DILUTION_FACTOR") == DilutionFactorFormula

    # Verify ecology formulas registered (4 total)
    assert plugin.get_formula("SHANNON_DIVERSITY") == ShannonDiversityFormula
    assert plugin.get_formula("SIMPSON_INDEX") == SimpsonIndexFormula
    assert plugin.get_formula("SPECIES_RICHNESS") == SpeciesRichnessFormula
    assert plugin.get_formula("POPULATION_GROWTH") == PopulationGrowthFormula

    # Verify importers registered (3 total)
    assert plugin.get_importer("plate_reader") == PlateReaderImporter
    assert plugin.get_importer("fasta") == FASTAImporter
    assert plugin.get_importer("genbank") == GenBankImporter


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = BiologyDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = BiologyDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Molecular Biology Formula Tests
# ============================================================================


def test_concentration_formula() -> None:
    """Test nucleic acid concentration formula."""
    formula = ConcentrationFormula()

    assert formula.metadata.name == "CONCENTRATION"
    assert formula.metadata.category == "molecular_biology"

    # Test basic calculation (A260 * 50 * dilution)
    result = formula.build("A1", "10")
    assert "A1" in result
    assert "50" in result


def test_fold_change_formula() -> None:
    """Test fold change (2^-ddCt) formula."""
    formula = FoldChangeFormula()

    assert formula.metadata.name == "FOLD_CHANGE"
    assert len(formula.metadata.arguments) == 4

    result = formula.build("A1", "A2", "B1", "B2")
    assert "POWER" in result
    assert "A1" in result


def test_gc_content_formula() -> None:
    """Test GC content formula."""
    formula = GCContentFormula()

    assert formula.metadata.name == "GC_CONTENT"

    result = formula.build("A1")
    assert "LEN" in result
    assert "SUBSTITUTE" in result


def test_melting_temp_formula() -> None:
    """Test DNA melting temperature formula."""
    formula = MeltingTempFormula()

    assert formula.metadata.name == "MELTING_TEMP"

    result = formula.build("A1")
    # Tm = 4(G+C) + 2(A+T)
    assert "4*" in result or "2*" in result


# ============================================================================
# Biochemistry Formula Tests
# ============================================================================


def test_bradford_assay_formula() -> None:
    """Test Bradford assay protein concentration formula."""
    formula = BradfordAssayFormula()

    assert formula.metadata.name == "BRADFORD_ASSAY"
    assert formula.metadata.category == "biochemistry"

    # Test with slope, intercept
    result = formula.build("A1", "0.0015", "0.02")
    assert "0.0015" in result
    assert "A1" in result

    # Test with dilution factor
    result = formula.build("A1", "0.0015", "0.02", "10")
    assert "10" in result


def test_enzyme_activity_formula() -> None:
    """Test enzyme activity formula."""
    formula = EnzymeActivityFormula()

    assert formula.metadata.name == "ENZYME_ACTIVITY"

    result = formula.build("A1", "B1", "C1", "6220")
    assert "/" in result
    assert "6220" in result


def test_michaelis_menten_formula() -> None:
    """Test Michaelis-Menten kinetics formula."""
    formula = MichaelisMentenFormula()

    assert formula.metadata.name == "MICHAELIS_MENTEN"

    result = formula.build("A1", "10", "2.5")
    # V = (Vmax * [S]) / (Km + [S])
    assert "10" in result
    assert "2.5" in result
    assert "/" in result


def test_dilution_factor_formula() -> None:
    """Test serial dilution formula."""
    formula = DilutionFactorFormula()

    assert formula.metadata.name == "DILUTION_FACTOR"

    result = formula.build("10", "3")
    assert "POWER" in result
    assert "10" in result
    assert "3" in result


# ============================================================================
# Ecology Formula Tests
# ============================================================================


def test_shannon_diversity_formula() -> None:
    """Test Shannon diversity index formula."""
    formula = ShannonDiversityFormula()

    assert formula.metadata.name == "SHANNON_DIVERSITY"

    result = formula.build("A1:A10")
    assert "LN" in result or "LOG" in result.upper()


def test_simpson_index_formula() -> None:
    """Test Simpson's diversity index formula."""
    formula = SimpsonIndexFormula()

    assert formula.metadata.name == "SIMPSON_INDEX"

    result = formula.build("A1:A10")
    # 1 - SUM(pi^2)
    assert "1-" in result or "1 -" in result


def test_species_richness_formula() -> None:
    """Test species richness formula."""
    formula = SpeciesRichnessFormula()

    assert formula.metadata.name == "SPECIES_RICHNESS"

    result = formula.build("A1:A10")
    assert "COUNTIF" in result


def test_population_growth_formula() -> None:
    """Test population growth formula."""
    formula = PopulationGrowthFormula()

    assert formula.metadata.name == "POPULATION_GROWTH"

    result = formula.build("1000", "0.1", "10")
    # Exponential growth: N0 * e^(rt)
    assert "EXP" in result or "1000" in result


# ============================================================================
# Importer Tests
# ============================================================================


def test_plate_reader_importer_csv() -> None:
    """Test plate reader CSV importer."""
    importer = PlateReaderImporter()

    assert importer.metadata.name == "Plate Reader Importer"
    assert "csv" in importer.metadata.supported_formats

    # Create test CSV file in plate layout format
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Plate Reader - Absorbance 450nm\n")
        f.write(",1,2,3,4,5,6,7,8,9,10,11,12\n")
        f.write("A,0.125,0.250,0.500,,,,,,,,,\n")
        f.write("B,,,,,,,,,,,\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 3
        assert "wells" in result.data
        assert len(result.data["wells"]) == 3
    finally:
        csv_path.unlink()


def test_fasta_importer() -> None:
    """Test FASTA sequence importer."""
    importer = FASTAImporter()

    assert importer.metadata.name == "FASTA Importer"
    assert "fasta" in importer.metadata.supported_formats

    # Create test FASTA file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(">seq1 Test sequence 1\n")
        f.write("ATGCATGCATGC\n")
        f.write(">seq2 Test sequence 2\n")
        f.write("GCTAGCTAGCTA\n")
        fasta_path = Path(f.name)

    try:
        result = importer.import_data(fasta_path)

        assert result.success is True
        assert result.records_imported == 2
    finally:
        fasta_path.unlink()


def test_genbank_importer() -> None:
    """Test GenBank importer."""
    importer = GenBankImporter()

    assert importer.metadata.name == "GenBank Importer"
    assert (
        "gb" in importer.metadata.supported_formats
        or "gbk" in importer.metadata.supported_formats
    )


def test_importer_invalid_file() -> None:
    """Test importer with invalid file."""
    importer = PlateReaderImporter()

    result = importer.import_data("/nonexistent/file.csv")

    assert result.success is False
    assert len(result.errors) > 0


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_calculate_gc_content() -> None:
    """Test GC content calculation."""
    # 50% GC
    gc = calculate_gc_content("ATGC")
    assert abs(gc - 50.0) < 0.1

    # 100% GC
    gc = calculate_gc_content("GGCC")
    assert abs(gc - 100.0) < 0.1

    # 0% GC
    gc = calculate_gc_content("AATT")
    assert abs(gc - 0.0) < 0.1


def test_calculate_melting_temp() -> None:
    """Test melting temperature calculation."""
    # Short sequence: Tm = 4(G+C) + 2(A+T)
    tm = calculate_melting_temp("ATGC")
    assert tm > 0


def test_calculate_od_to_concentration() -> None:
    """Test OD to concentration conversion."""
    # DNA: A260 of 1.0 = 50 ug/mL
    conc = calculate_od_to_concentration(1.0, "DNA")
    assert abs(conc - 50.0) < 0.1

    # RNA: A260 of 1.0 = 40 ug/mL
    conc = calculate_od_to_concentration(1.0, "RNA")
    assert abs(conc - 40.0) < 0.1


def test_calculate_dilution() -> None:
    """Test serial dilution calculation."""
    # 10^3 = 1000
    dilution = calculate_dilution(10, 3)
    assert dilution == 1000

    # 2^5 = 32
    dilution = calculate_dilution(2, 5)
    assert dilution == 32


def test_format_scientific_notation() -> None:
    """Test scientific notation formatting."""
    formatted = format_scientific_notation(0.00123)
    assert "e" in formatted.lower() or "E" in formatted


# ============================================================================
# Integration Tests
# ============================================================================


def test_formula_argument_validation() -> None:
    """Test formula argument validation."""
    formula = FoldChangeFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("A1", "A2")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("A1", "A2", "B1", "B2", "extra")


def test_importer_validation() -> None:
    """Test importer source validation."""
    importer = PlateReaderImporter()

    # Non-existent file
    assert importer.validate_source(Path("/nonexistent.csv")) is False

    # Create temp file for validation
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        temp_path = Path(f.name)

    try:
        assert importer.validate_source(temp_path) is True
    finally:
        temp_path.unlink()


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


def test_empty_sequence_gc_content() -> None:
    """Test GC content with empty sequence."""
    gc = calculate_gc_content("")
    assert gc == 0.0


def test_diversity_formulas_with_cell_references() -> None:
    """Test diversity formulas with cell range references."""
    shannon = ShannonDiversityFormula()
    result = shannon.build("B2:B100")
    assert "B2:B100" in result

    simpson = SimpsonIndexFormula()
    result = simpson.build("C3:C50")
    assert "C3:C50" in result


def test_fasta_importer_with_multiline_sequences() -> None:
    """Test FASTA importer with multiline sequences."""
    importer = FASTAImporter()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as f:
        f.write(">seq1 Multi-line sequence\n")
        f.write("ATGCATGCATGC\n")
        f.write("GCTAGCTAGCTA\n")
        f.write("ATGCATGCATGC\n")
        fasta_path = Path(f.name)

    try:
        result = importer.import_data(fasta_path)
        assert result.success is True
        # Should combine multiline sequences
        if result.data:
            seq = result.data[0].get("sequence", "")
            assert len(seq) >= 12  # At least first line
    finally:
        fasta_path.unlink()


def test_plate_reader_with_empty_wells() -> None:
    """Test plate reader importer with empty wells."""
    importer = PlateReaderImporter()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Well,Absorbance\n")
        f.write("A1,0.125\n")
        f.write("A2,\n")  # Empty value
        f.write("A3,0.500\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        assert result.success is True
        # Should handle empty wells gracefully
    finally:
        csv_path.unlink()
