"""Tests for Biology cell biology formulas.

Comprehensive tests for cell biology-related formulas
including cell density, viability, growth rate, and biochemistry calculations.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.biology import (
    BiologyDomainPlugin,
    BradfordAssayFormula,
    ConcentrationFormula,
    DilutionFactorFormula,
    EnzymeActivityFormula,
    FoldChangeFormula,
    GCContentFormula,
    MeltingTempFormula,
    MichaelisMentenFormula,
    PopulationGrowthFormula,
    ShannonDiversityFormula,
    SimpsonIndexFormula,
    SpeciesRichnessFormula,
)
from spreadsheet_dl.domains.biology.formulas.cell_biology import (
    CellDensity,
    DoublingTime,
    SpecificGrowthRate,
    ViabilityPercent,
)
from spreadsheet_dl.domains.biology.utils import (
    calculate_dilution,
    calculate_gc_content,
    calculate_melting_temp,
    calculate_od_to_concentration,
    complement_dna,
    format_scientific_notation,
    is_valid_dna,
    is_valid_rna,
    normalize_sequence,
    reverse_complement,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


# ============================================================================
# Cell Density Formula Tests
# ============================================================================


class TestCellDensityFormula:
    """Test cell density calculations."""

    def test_cell_density_standard(self) -> None:
        """Test standard cell density calculation."""
        formula = CellDensity()
        result = formula.build("1000000", "0.001")
        assert result == "of:=1000000/0.001"

    def test_cell_density_high_count(self) -> None:
        """Test cell density with high cell count."""
        formula = CellDensity()
        result = formula.build("10000000", "1")
        assert result == "of:=10000000/1"

    def test_cell_density_low_volume(self) -> None:
        """Test cell density with low volume."""
        formula = CellDensity()
        result = formula.build("5000", "0.0001")
        assert result == "of:=5000/0.0001"

    def test_cell_density_cell_references(self) -> None:
        """Test cell density with cell references."""
        formula = CellDensity()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"

    def test_cell_density_metadata(self) -> None:
        """Test cell density formula metadata."""
        formula = CellDensity()
        metadata = formula.metadata

        assert metadata.name == "CELL_DENSITY"
        assert metadata.category == "cell_biology"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"


# ============================================================================
# Viability Percent Formula Tests
# ============================================================================


class TestViabilityPercentFormula:
    """Test cell viability percentage calculations."""

    def test_viability_percent_standard(self) -> None:
        """Test standard viability calculation."""
        formula = ViabilityPercent()
        result = formula.build("900", "1000")
        assert result == "of:=900/1000*100"

    def test_viability_percent_high(self) -> None:
        """Test high viability (near 100%)."""
        formula = ViabilityPercent()
        result = formula.build("990", "1000")
        assert result == "of:=990/1000*100"

    def test_viability_percent_low(self) -> None:
        """Test low viability."""
        formula = ViabilityPercent()
        result = formula.build("500", "1000")
        assert result == "of:=500/1000*100"

    def test_viability_percent_perfect(self) -> None:
        """Test perfect viability (100%)."""
        formula = ViabilityPercent()
        result = formula.build("1000", "1000")
        assert result == "of:=1000/1000*100"

    def test_viability_percent_cell_references(self) -> None:
        """Test viability with cell references."""
        formula = ViabilityPercent()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1*100"

    def test_viability_percent_metadata(self) -> None:
        """Test viability formula metadata."""
        formula = ViabilityPercent()
        metadata = formula.metadata

        assert metadata.name == "VIABILITY_PERCENT"
        assert metadata.category == "cell_biology"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"


# ============================================================================
# Doubling Time Formula Tests
# ============================================================================


class TestDoublingTimeFormula:
    """Test population doubling time calculations."""

    def test_doubling_time_standard(self) -> None:
        """Test standard doubling time calculation."""
        formula = DoublingTime()
        result = formula.build("0.693")
        assert result == "of:=LN(2)/0.693"

    def test_doubling_time_fast_growth(self) -> None:
        """Test doubling time for fast-growing cells."""
        formula = DoublingTime()
        result = formula.build("1.0")
        assert result == "of:=LN(2)/1.0"

    def test_doubling_time_slow_growth(self) -> None:
        """Test doubling time for slow-growing cells."""
        formula = DoublingTime()
        result = formula.build("0.1")
        assert result == "of:=LN(2)/0.1"

    def test_doubling_time_cell_reference(self) -> None:
        """Test doubling time with cell reference."""
        formula = DoublingTime()
        result = formula.build("A1")
        assert result == "of:=LN(2)/A1"

    def test_doubling_time_metadata(self) -> None:
        """Test doubling time formula metadata."""
        formula = DoublingTime()
        metadata = formula.metadata

        assert metadata.name == "DOUBLING_TIME"
        assert metadata.category == "cell_biology"
        assert len(metadata.arguments) == 1
        assert metadata.return_type == "number"


# ============================================================================
# Specific Growth Rate Formula Tests
# ============================================================================


class TestSpecificGrowthRateFormula:
    """Test specific growth rate calculations."""

    def test_specific_growth_rate_standard(self) -> None:
        """Test standard specific growth rate calculation."""
        formula = SpecificGrowthRate()
        result = formula.build("1000000", "100000", "5")
        assert result == "of:=(LN(1000000)-LN(100000))/5"

    def test_specific_growth_rate_high_growth(self) -> None:
        """Test specific growth rate with high final density."""
        formula = SpecificGrowthRate()
        result = formula.build("10000000", "1000000", "10")
        assert result == "of:=(LN(10000000)-LN(1000000))/10"

    def test_specific_growth_rate_short_time(self) -> None:
        """Test specific growth rate over short time."""
        formula = SpecificGrowthRate()
        result = formula.build("200000", "100000", "1")
        assert result == "of:=(LN(200000)-LN(100000))/1"

    def test_specific_growth_rate_cell_references(self) -> None:
        """Test specific growth rate with cell references."""
        formula = SpecificGrowthRate()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=(LN(A1)-LN(B1))/C1"

    def test_specific_growth_rate_metadata(self) -> None:
        """Test specific growth rate formula metadata."""
        formula = SpecificGrowthRate()
        metadata = formula.metadata

        assert metadata.name == "SPECIFIC_GROWTH_RATE"
        assert metadata.category == "cell_biology"
        assert len(metadata.arguments) == 3
        assert metadata.return_type == "number"


# ============================================================================
# Biochemistry Formula Tests
# ============================================================================


class TestBradfordAssayCalculations:
    """Test Bradford assay protein concentration calculations."""

    def test_bradford_assay_standard(self) -> None:
        """Test standard Bradford assay calculation."""
        formula = BradfordAssayFormula()
        result = formula.build("A1", "0.0015", "0.02")
        assert "A1" in result
        assert "0.0015" in result

    def test_bradford_assay_with_dilution(self) -> None:
        """Test Bradford assay with dilution factor."""
        formula = BradfordAssayFormula()
        result = formula.build("A1", "0.0015", "0.02", "10")
        assert "10" in result

    def test_bradford_assay_cell_references(self) -> None:
        """Test Bradford assay with cell references."""
        formula = BradfordAssayFormula()
        result = formula.build("B2", "C2", "D2")
        assert "B2" in result
        assert "C2" in result
        assert "D2" in result

    def test_bradford_assay_high_absorbance(self) -> None:
        """Test Bradford assay with high absorbance value."""
        formula = BradfordAssayFormula()
        result = formula.build("1.5", "0.0015", "0.02")
        assert "1.5" in result


class TestEnzymeActivityCalculations:
    """Test enzyme activity calculations."""

    def test_enzyme_activity_standard(self) -> None:
        """Test standard enzyme activity calculation."""
        formula = EnzymeActivityFormula()
        result = formula.build("A1", "B1", "C1", "6220")
        assert "/" in result
        assert "6220" in result

    def test_enzyme_activity_different_extinction(self) -> None:
        """Test enzyme activity with different extinction coefficient."""
        formula = EnzymeActivityFormula()
        result = formula.build("0.5", "0.1", "1.0", "34000")
        assert "34000" in result

    def test_enzyme_activity_cell_references(self) -> None:
        """Test enzyme activity with cell references."""
        formula = EnzymeActivityFormula()
        result = formula.build("A1", "B1", "C1", "D1")
        assert "A1" in result


class TestMichaelisMentenCalculations:
    """Test Michaelis-Menten kinetics calculations."""

    def test_michaelis_menten_standard(self) -> None:
        """Test standard Michaelis-Menten calculation."""
        formula = MichaelisMentenFormula()
        result = formula.build("A1", "10", "2.5")
        assert "10" in result
        assert "2.5" in result
        assert "/" in result

    def test_michaelis_menten_high_substrate(self) -> None:
        """Test Michaelis-Menten at high substrate concentration."""
        formula = MichaelisMentenFormula()
        result = formula.build("100", "50", "5")
        assert "100" in result

    def test_michaelis_menten_low_substrate(self) -> None:
        """Test Michaelis-Menten at low substrate concentration."""
        formula = MichaelisMentenFormula()
        result = formula.build("0.1", "50", "5")
        assert "0.1" in result

    def test_michaelis_menten_cell_references(self) -> None:
        """Test Michaelis-Menten with cell references."""
        formula = MichaelisMentenFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result
        assert "B1" in result


class TestDilutionFactorFormula:
    """Test serial dilution factor calculations."""

    def test_dilution_factor_standard(self) -> None:
        """Test standard dilution factor calculation."""
        formula = DilutionFactorFormula()
        result = formula.build("10", "3")
        assert "POWER" in result
        assert "10" in result
        assert "3" in result

    def test_dilution_factor_two_fold(self) -> None:
        """Test 2-fold serial dilution."""
        formula = DilutionFactorFormula()
        result = formula.build("2", "5")
        assert "POWER" in result

    def test_dilution_factor_cell_references(self) -> None:
        """Test dilution factor with cell references."""
        formula = DilutionFactorFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result


# ============================================================================
# Molecular Biology Formula Tests
# ============================================================================


class TestConcentrationFormula:
    """Test nucleic acid concentration calculations."""

    def test_concentration_dna_standard(self) -> None:
        """Test standard DNA concentration calculation."""
        formula = ConcentrationFormula()
        result = formula.build("A1", "10")
        assert "A1" in result
        assert "50" in result

    def test_concentration_cell_references(self) -> None:
        """Test concentration with cell references."""
        formula = ConcentrationFormula()
        result = formula.build("B2", "C2")
        assert "B2" in result


class TestFoldChangeCalculations:
    """Test fold change (2^-ddCt) calculations."""

    def test_fold_change_standard(self) -> None:
        """Test standard fold change calculation."""
        formula = FoldChangeFormula()
        result = formula.build("A1", "A2", "B1", "B2")
        assert "POWER" in result
        assert "A1" in result

    def test_fold_change_all_cell_references(self) -> None:
        """Test fold change with all cell references."""
        formula = FoldChangeFormula()
        result = formula.build("C1", "C2", "D1", "D2")
        assert "C1" in result
        assert "D1" in result


class TestGCContentFormula:
    """Test GC content calculations."""

    def test_gc_content_standard(self) -> None:
        """Test standard GC content calculation."""
        formula = GCContentFormula()
        result = formula.build("A1")
        assert "LEN" in result
        assert "SUBSTITUTE" in result

    def test_gc_content_cell_reference(self) -> None:
        """Test GC content with cell reference."""
        formula = GCContentFormula()
        result = formula.build("B5")
        assert "B5" in result


class TestMeltingTempFormula:
    """Test DNA melting temperature calculations."""

    def test_melting_temp_standard(self) -> None:
        """Test standard melting temperature calculation."""
        formula = MeltingTempFormula()
        result = formula.build("A1")
        assert "4*" in result or "2*" in result

    def test_melting_temp_cell_reference(self) -> None:
        """Test melting temperature with cell reference."""
        formula = MeltingTempFormula()
        result = formula.build("C3")
        assert "C3" in result


# ============================================================================
# Ecology Formula Tests
# ============================================================================


class TestShannonDiversityFormula:
    """Test Shannon diversity index calculations."""

    def test_shannon_diversity_standard(self) -> None:
        """Test standard Shannon diversity calculation."""
        formula = ShannonDiversityFormula()
        result = formula.build("A1:A10")
        assert "LN" in result or "LOG" in result.upper()

    def test_shannon_diversity_large_range(self) -> None:
        """Test Shannon diversity with large range."""
        formula = ShannonDiversityFormula()
        result = formula.build("B2:B100")
        assert "B2:B100" in result

    def test_shannon_diversity_single_column(self) -> None:
        """Test Shannon diversity with single column reference."""
        formula = ShannonDiversityFormula()
        result = formula.build("C:C")
        assert "C:C" in result


class TestSimpsonIndexFormula:
    """Test Simpson's diversity index calculations."""

    def test_simpson_index_standard(self) -> None:
        """Test standard Simpson's index calculation."""
        formula = SimpsonIndexFormula()
        result = formula.build("A1:A10")
        assert "1-" in result or "1 -" in result

    def test_simpson_index_inverse(self) -> None:
        """Test Simpson's reciprocal index (1/D)."""
        formula = SimpsonIndexFormula()
        result = formula.build("A1:A10", "1")
        assert "1/" in result

    def test_simpson_index_default(self) -> None:
        """Test Simpson's diversity index default (1-D)."""
        formula = SimpsonIndexFormula()
        result = formula.build("B5:B20")
        assert "B5:B20" in result


class TestSpeciesRichnessFormula:
    """Test species richness calculations."""

    def test_species_richness_standard(self) -> None:
        """Test standard species richness calculation."""
        formula = SpeciesRichnessFormula()
        result = formula.build("A1:A10")
        assert "COUNTIF" in result

    def test_species_richness_large_range(self) -> None:
        """Test species richness with large range."""
        formula = SpeciesRichnessFormula()
        result = formula.build("C2:C500")
        assert "C2:C500" in result


class TestPopulationGrowthFormula:
    """Test population growth calculations."""

    def test_population_growth_exponential(self) -> None:
        """Test exponential population growth."""
        formula = PopulationGrowthFormula()
        result = formula.build("1000", "0.1", "10")
        assert "EXP" in result or "1000" in result

    def test_population_growth_logistic(self) -> None:
        """Test logistic population growth with carrying capacity."""
        formula = PopulationGrowthFormula()
        result = formula.build("100", "0.05", "10", "1000")
        assert "1000" in result

    def test_population_growth_cell_references(self) -> None:
        """Test population growth with cell references."""
        formula = PopulationGrowthFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestGCContentUtility:
    """Test GC content utility calculations."""

    def test_gc_content_fifty_percent(self) -> None:
        """Test 50% GC content."""
        gc = calculate_gc_content("ATGC")
        assert abs(gc - 50.0) < 0.1

    def test_gc_content_hundred_percent(self) -> None:
        """Test 100% GC content."""
        gc = calculate_gc_content("GGCC")
        assert abs(gc - 100.0) < 0.1

    def test_gc_content_zero_percent(self) -> None:
        """Test 0% GC content."""
        gc = calculate_gc_content("AATT")
        assert abs(gc - 0.0) < 0.1

    def test_gc_content_empty_sequence(self) -> None:
        """Test GC content of empty sequence."""
        gc = calculate_gc_content("")
        assert gc == 0.0

    def test_gc_content_lowercase(self) -> None:
        """Test GC content with lowercase input."""
        gc = calculate_gc_content("atgc")
        assert abs(gc - 50.0) < 0.1

    def test_gc_content_long_sequence(self) -> None:
        """Test GC content of longer sequence."""
        gc = calculate_gc_content("ATGCATGCATGCATGC")
        assert abs(gc - 50.0) < 0.1


class TestMeltingTempUtility:
    """Test melting temperature utility calculations."""

    def test_melting_temp_short_sequence(self) -> None:
        """Test melting temp of short sequence."""
        tm = calculate_melting_temp("ATGC")
        assert tm > 0

    def test_melting_temp_gc_rich(self) -> None:
        """Test melting temp of GC-rich sequence."""
        tm_gc = calculate_melting_temp("GGGGCCCC")
        tm_at = calculate_melting_temp("AAAATTTT")
        assert tm_gc > tm_at

    def test_melting_temp_different_lengths(self) -> None:
        """Test melting temp scales with length."""
        tm_short = calculate_melting_temp("ATGC")
        tm_long = calculate_melting_temp("ATGCATGCATGC")
        assert tm_long > tm_short


class TestODToConcentration:
    """Test OD to concentration conversion."""

    def test_od_to_concentration_dna(self) -> None:
        """Test DNA OD conversion (1 A260 = 50 ug/mL)."""
        conc = calculate_od_to_concentration(1.0, "DNA")
        assert abs(conc - 50.0) < 0.1

    def test_od_to_concentration_rna(self) -> None:
        """Test RNA OD conversion (1 A260 = 40 ug/mL)."""
        conc = calculate_od_to_concentration(1.0, "RNA")
        assert abs(conc - 40.0) < 0.1

    def test_od_to_concentration_high_od(self) -> None:
        """Test concentration at high OD."""
        conc = calculate_od_to_concentration(2.0, "DNA")
        assert abs(conc - 100.0) < 0.1


class TestDilutionUtility:
    """Test serial dilution utility calculations."""

    def test_dilution_ten_fold(self) -> None:
        """Test 10-fold serial dilution."""
        dilution = calculate_dilution(10, 3)
        assert dilution == 1000

    def test_dilution_two_fold(self) -> None:
        """Test 2-fold serial dilution."""
        dilution = calculate_dilution(2, 5)
        assert dilution == 32

    def test_dilution_single_step(self) -> None:
        """Test single dilution step."""
        dilution = calculate_dilution(5, 1)
        assert dilution == 5


class TestSequenceValidation:
    """Test DNA/RNA sequence validation utilities."""

    def test_is_valid_dna_true(self) -> None:
        """Test valid DNA sequence."""
        assert is_valid_dna("ATGCATGC") is True

    def test_is_valid_dna_false(self) -> None:
        """Test invalid DNA sequence (contains U)."""
        assert is_valid_dna("AUGCAUGC") is False

    def test_is_valid_rna_true(self) -> None:
        """Test valid RNA sequence."""
        assert is_valid_rna("AUGCAUGC") is True

    def test_is_valid_rna_false(self) -> None:
        """Test invalid RNA sequence (contains T)."""
        assert is_valid_rna("ATGCATGC") is False

    def test_is_valid_dna_lowercase(self) -> None:
        """Test valid DNA with lowercase."""
        assert is_valid_dna("atgcatgc") is True


class TestSequenceOperations:
    """Test DNA sequence operation utilities."""

    def test_complement_dna_standard(self) -> None:
        """Test DNA complement."""
        comp = complement_dna("ATGC")
        assert comp == "TACG"

    def test_reverse_complement_standard(self) -> None:
        """Test reverse complement."""
        rc = reverse_complement("ATGC")
        assert rc == "GCAT"

    def test_normalize_sequence_lowercase(self) -> None:
        """Test sequence normalization."""
        normalized = normalize_sequence("atgc")
        assert normalized == "ATGC"

    def test_normalize_sequence_whitespace(self) -> None:
        """Test sequence normalization removes whitespace."""
        normalized = normalize_sequence("AT GC")
        assert normalized == "ATGC"


class TestScientificNotationBiology:
    """Test scientific notation formatting for biology."""

    def test_format_scientific_cell_count(self) -> None:
        """Test formatting cell counts."""
        formatted = format_scientific_notation(1.5e6)
        assert "e" in formatted.lower() or "E" in formatted

    def test_format_scientific_concentration(self) -> None:
        """Test formatting molar concentrations."""
        formatted = format_scientific_notation(2.5e-9)
        assert "e" in formatted.lower() or "E" in formatted


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestCellBiologyEdgeCases:
    """Test edge cases in cell biology formulas."""

    def test_cell_density_validates_arguments(self) -> None:
        """Test cell density argument validation."""
        formula = CellDensity()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1000000")

    def test_viability_percent_validates_arguments(self) -> None:
        """Test viability percent argument validation."""
        formula = ViabilityPercent()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("900")

    def test_doubling_time_validates_arguments(self) -> None:
        """Test doubling time argument validation."""
        formula = DoublingTime()
        with pytest.raises(ValueError, match="accepts at most"):
            formula.build("0.693", "extra")

    def test_specific_growth_rate_validates_arguments(self) -> None:
        """Test specific growth rate argument validation."""
        formula = SpecificGrowthRate()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1000000", "100000")

    def test_fold_change_validates_arguments(self) -> None:
        """Test fold change argument validation."""
        formula = FoldChangeFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1", "A2")

    def test_fold_change_too_many_arguments(self) -> None:
        """Test fold change with too many arguments."""
        formula = FoldChangeFormula()
        with pytest.raises(ValueError, match="accepts at most"):
            formula.build("A1", "A2", "B1", "B2", "extra")

    def test_bradford_assay_validates_arguments(self) -> None:
        """Test Bradford assay argument validation."""
        formula = BradfordAssayFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1", "0.0015")


# ============================================================================
# Integration Tests
# ============================================================================


class TestCellBiologyIntegration:
    """Integration tests for cell biology formulas with plugin."""

    def test_plugin_contains_cell_biology_formulas(self) -> None:
        """Test plugin has cell biology formulas."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("CELL_DENSITY") is not None
        assert plugin.get_formula("VIABILITY_PERCENT") is not None
        assert plugin.get_formula("DOUBLING_TIME") is not None
        assert plugin.get_formula("SPECIFIC_GROWTH_RATE") is not None

    def test_plugin_contains_biochemistry_formulas(self) -> None:
        """Test plugin has biochemistry formulas."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("BRADFORD_ASSAY") is not None
        assert plugin.get_formula("ENZYME_ACTIVITY") is not None
        assert plugin.get_formula("MICHAELIS_MENTEN") is not None
        assert plugin.get_formula("DILUTION_FACTOR") is not None

    def test_plugin_contains_molecular_formulas(self) -> None:
        """Test plugin has molecular biology formulas."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("CONCENTRATION") is not None
        assert plugin.get_formula("FOLD_CHANGE") is not None
        assert plugin.get_formula("GC_CONTENT") is not None
        assert plugin.get_formula("MELTING_TEMP") is not None

    def test_plugin_contains_ecology_formulas(self) -> None:
        """Test plugin has ecology formulas."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("SHANNON_DIVERSITY") is not None
        assert plugin.get_formula("SIMPSON_INDEX") is not None
        assert plugin.get_formula("SPECIES_RICHNESS") is not None
        assert plugin.get_formula("POPULATION_GROWTH") is not None

    def test_plugin_has_importers(self) -> None:
        """Test plugin has importers registered."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        assert plugin.get_importer("plate_reader") is not None
        assert plugin.get_importer("fasta") is not None
        assert plugin.get_importer("genbank") is not None

    def test_all_cell_biology_formulas_produce_output(self) -> None:
        """Test all cell biology formulas produce valid output."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        test_cases = [
            ("CELL_DENSITY", ("1000000", "0.001")),
            ("VIABILITY_PERCENT", ("900", "1000")),
            ("DOUBLING_TIME", ("0.693",)),
            ("SPECIFIC_GROWTH_RATE", ("1000000", "100000", "5")),
        ]

        for formula_name, args in test_cases:
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            result = formula.build(*args)
            assert len(result) > 0, f"{formula_name} should return formula"

    def test_all_formulas_have_metadata(self) -> None:
        """Test all formulas have proper metadata."""
        plugin = BiologyDomainPlugin()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            assert metadata.name
            assert metadata.category
            assert metadata.description
            assert len(metadata.arguments) > 0
