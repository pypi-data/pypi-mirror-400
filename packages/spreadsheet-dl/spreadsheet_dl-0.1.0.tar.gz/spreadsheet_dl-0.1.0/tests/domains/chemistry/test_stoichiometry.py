"""Tests for Chemistry stoichiometry formulas.

Comprehensive tests for stoichiometry-related formulas
including mole calculations, limiting reagents, and mass relationships.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.chemistry import (
    ChemistryDomainPlugin,
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
from spreadsheet_dl.domains.chemistry.utils import (
    calculate_dilution_factor,
    calculate_molecular_weight,
    format_scientific_notation,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


# ============================================================================
# Molar Mass Formula Tests
# ============================================================================


class TestMolarMassFormula:
    """Test molar mass calculations."""

    def test_molar_mass_standard(self) -> None:
        """Test standard molar mass calculation."""
        formula = MolarMassFormula()
        result = formula.build("58.44", "1")
        assert result == "of:=58.44/1"

    def test_molar_mass_multiple_moles(self) -> None:
        """Test molar mass with multiple moles."""
        formula = MolarMassFormula()
        result = formula.build("180.16", "2")
        assert result == "of:=180.16/2"

    def test_molar_mass_fractional_moles(self) -> None:
        """Test molar mass with fractional moles."""
        formula = MolarMassFormula()
        result = formula.build("18.015", "0.5")
        assert result == "of:=18.015/0.5"

    def test_molar_mass_cell_references(self) -> None:
        """Test molar mass with cell references."""
        formula = MolarMassFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"

    def test_molar_mass_metadata(self) -> None:
        """Test molar mass formula metadata."""
        formula = MolarMassFormula()
        metadata = formula.metadata

        assert metadata.name == "MOLAR_MASS"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"


# ============================================================================
# Mass From Moles Formula Tests
# ============================================================================


class TestMassFromMolesFormula:
    """Test mass from moles calculations."""

    def test_mass_from_moles_standard(self) -> None:
        """Test standard mass calculation from moles."""
        formula = MassFromMolesFormula()
        result = formula.build("2", "18.015")
        assert result == "of:=2*18.015"

    def test_mass_from_moles_large_molar_mass(self) -> None:
        """Test mass calculation with large molar mass."""
        formula = MassFromMolesFormula()
        result = formula.build("0.5", "342.3")
        assert result == "of:=0.5*342.3"

    def test_mass_from_moles_small_amount(self) -> None:
        """Test mass calculation with small amount."""
        formula = MassFromMolesFormula()
        result = formula.build("0.001", "180.16")
        assert result == "of:=0.001*180.16"

    def test_mass_from_moles_cell_references(self) -> None:
        """Test mass from moles with cell references."""
        formula = MassFromMolesFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1*B1"

    def test_mass_from_moles_metadata(self) -> None:
        """Test mass from moles formula metadata."""
        formula = MassFromMolesFormula()
        metadata = formula.metadata

        assert metadata.name == "MASS_FROM_MOLES"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Moles From Mass Formula Tests
# ============================================================================


class TestMolesFromMassFormula:
    """Test moles from mass calculations."""

    def test_moles_from_mass_standard(self) -> None:
        """Test standard moles calculation from mass."""
        formula = MolesFromMassFormula()
        result = formula.build("36.03", "18.015")
        assert result == "of:=36.03/18.015"

    def test_moles_from_mass_large_mass(self) -> None:
        """Test moles calculation with large mass."""
        formula = MolesFromMassFormula()
        result = formula.build("1000", "58.44")
        assert result == "of:=1000/58.44"

    def test_moles_from_mass_small_mass(self) -> None:
        """Test moles calculation with small mass."""
        formula = MolesFromMassFormula()
        result = formula.build("0.5", "180.16")
        assert result == "of:=0.5/180.16"

    def test_moles_from_mass_cell_references(self) -> None:
        """Test moles from mass with cell references."""
        formula = MolesFromMassFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1/B1"

    def test_moles_from_mass_metadata(self) -> None:
        """Test moles from mass formula metadata."""
        formula = MolesFromMassFormula()
        metadata = formula.metadata

        assert metadata.name == "MOLES_FROM_MASS"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Limiting Reagent Formula Tests
# ============================================================================


class TestLimitingReagentFormula:
    """Test limiting reagent calculations."""

    def test_limiting_reagent_a_limiting(self) -> None:
        """Test when reagent A is limiting."""
        formula = LimitingReagentFormula()
        result = formula.build("1", "2", "3", "2")
        assert result.startswith("of:=")
        assert "IF" in result
        assert '"A"' in result
        assert '"B"' in result

    def test_limiting_reagent_b_limiting(self) -> None:
        """Test when reagent B is limiting."""
        formula = LimitingReagentFormula()
        result = formula.build("4", "2", "1", "2")
        assert result.startswith("of:=")
        assert "IF" in result

    def test_limiting_reagent_equal_ratios(self) -> None:
        """Test when both reagents have equal ratios."""
        formula = LimitingReagentFormula()
        result = formula.build("2", "1", "4", "2")
        assert result.startswith("of:=")

    def test_limiting_reagent_cell_references(self) -> None:
        """Test limiting reagent with cell references."""
        formula = LimitingReagentFormula()
        result = formula.build("A1", "B1", "C1", "D1")
        assert "A1" in result
        assert "B1" in result
        assert "C1" in result
        assert "D1" in result

    def test_limiting_reagent_metadata(self) -> None:
        """Test limiting reagent formula metadata."""
        formula = LimitingReagentFormula()
        metadata = formula.metadata

        assert metadata.name == "LIMITING_REAGENT"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 4


# ============================================================================
# Theoretical Yield Formula Tests
# ============================================================================


class TestTheoreticalYieldFormula:
    """Test theoretical yield calculations."""

    def test_theoretical_yield_standard(self) -> None:
        """Test standard theoretical yield calculation."""
        formula = TheoreticalYieldFormula()
        result = formula.build("2", "1", "18.015")
        assert result == "of:=2*1*18.015"

    def test_theoretical_yield_fractional_ratio(self) -> None:
        """Test theoretical yield with fractional stoichiometric ratio."""
        formula = TheoreticalYieldFormula()
        result = formula.build("1.5", "0.5", "44.01")
        assert result == "of:=1.5*0.5*44.01"

    def test_theoretical_yield_large_molar_mass(self) -> None:
        """Test theoretical yield with large product molar mass."""
        formula = TheoreticalYieldFormula()
        result = formula.build("0.1", "2", "342.3")
        assert result == "of:=0.1*2*342.3"

    def test_theoretical_yield_cell_references(self) -> None:
        """Test theoretical yield with cell references."""
        formula = TheoreticalYieldFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=A1*B1*C1"

    def test_theoretical_yield_metadata(self) -> None:
        """Test theoretical yield formula metadata."""
        formula = TheoreticalYieldFormula()
        metadata = formula.metadata

        assert metadata.name == "THEORETICAL_YIELD"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 3


# ============================================================================
# Percent Yield Formula Tests
# ============================================================================


class TestPercentYieldFormula:
    """Test percent yield calculations."""

    def test_percent_yield_standard(self) -> None:
        """Test standard percent yield calculation."""
        formula = PercentYieldFormula()
        result = formula.build("85", "100")
        assert result == "of:=(85/100)*100"

    def test_percent_yield_high(self) -> None:
        """Test high percent yield (near 100%)."""
        formula = PercentYieldFormula()
        result = formula.build("98.5", "100")
        assert result == "of:=(98.5/100)*100"

    def test_percent_yield_low(self) -> None:
        """Test low percent yield."""
        formula = PercentYieldFormula()
        result = formula.build("45", "100")
        assert result == "of:=(45/100)*100"

    def test_percent_yield_fractional_values(self) -> None:
        """Test percent yield with fractional values."""
        formula = PercentYieldFormula()
        result = formula.build("3.5", "5.0")
        assert result == "of:=(3.5/5.0)*100"

    def test_percent_yield_cell_references(self) -> None:
        """Test percent yield with cell references."""
        formula = PercentYieldFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=(A1/B1)*100"

    def test_percent_yield_metadata(self) -> None:
        """Test percent yield formula metadata."""
        formula = PercentYieldFormula()
        metadata = formula.metadata

        assert metadata.name == "PERCENT_YIELD"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Percent Composition Formula Tests
# ============================================================================


class TestPercentCompositionFormula:
    """Test percent composition calculations."""

    def test_percent_composition_hydrogen_in_water(self) -> None:
        """Test percent composition of hydrogen in water."""
        formula = PercentCompositionFormula()
        result = formula.build("2", "1.008", "18.015")
        assert result == "of:=(2*1.008/18.015)*100"

    def test_percent_composition_oxygen_in_water(self) -> None:
        """Test percent composition of oxygen in water."""
        formula = PercentCompositionFormula()
        result = formula.build("1", "16.0", "18.015")
        assert result == "of:=(1*16.0/18.015)*100"

    def test_percent_composition_carbon_in_glucose(self) -> None:
        """Test percent composition of carbon in glucose."""
        formula = PercentCompositionFormula()
        result = formula.build("6", "12.01", "180.16")
        assert result == "of:=(6*12.01/180.16)*100"

    def test_percent_composition_cell_references(self) -> None:
        """Test percent composition with cell references."""
        formula = PercentCompositionFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=(A1*B1/C1)*100"

    def test_percent_composition_metadata(self) -> None:
        """Test percent composition formula metadata."""
        formula = PercentCompositionFormula()
        metadata = formula.metadata

        assert metadata.name == "PERCENT_COMPOSITION"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 3


# ============================================================================
# Empirical Formula Ratio Formula Tests
# ============================================================================


class TestEmpiricalFormulaRatioFormula:
    """Test empirical formula ratio calculations."""

    def test_empirical_formula_ratio_carbon(self) -> None:
        """Test empirical formula ratio for carbon."""
        formula = EmpiricalFormulaRatioFormula()
        result = formula.build("40", "12.01", "0.833")
        assert result == "of:=(40/12.01)/0.833"

    def test_empirical_formula_ratio_hydrogen(self) -> None:
        """Test empirical formula ratio for hydrogen."""
        formula = EmpiricalFormulaRatioFormula()
        result = formula.build("6.67", "1.008", "0.833")
        assert result == "of:=(6.67/1.008)/0.833"

    def test_empirical_formula_ratio_oxygen(self) -> None:
        """Test empirical formula ratio for oxygen."""
        formula = EmpiricalFormulaRatioFormula()
        result = formula.build("53.33", "16.0", "0.833")
        assert result == "of:=(53.33/16.0)/0.833"

    def test_empirical_formula_ratio_cell_references(self) -> None:
        """Test empirical formula ratio with cell references."""
        formula = EmpiricalFormulaRatioFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=(A1/B1)/C1"

    def test_empirical_formula_ratio_metadata(self) -> None:
        """Test empirical formula ratio formula metadata."""
        formula = EmpiricalFormulaRatioFormula()
        metadata = formula.metadata

        assert metadata.name == "EMPIRICAL_FORMULA_RATIO"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 3


# ============================================================================
# Dilution Formula Tests
# ============================================================================


class TestDilutionFormula:
    """Test dilution calculations."""

    def test_dilution_ten_fold(self) -> None:
        """Test 10-fold dilution."""
        formula = DilutionFormula()
        result = formula.build("6", "0.1", "1")
        assert result == "of:=6*0.1/1"

    def test_dilution_hundred_fold(self) -> None:
        """Test 100-fold dilution."""
        formula = DilutionFormula()
        result = formula.build("10", "0.01", "1")
        assert result == "of:=10*0.01/1"

    def test_dilution_concentrated_stock(self) -> None:
        """Test dilution from concentrated stock."""
        formula = DilutionFormula()
        result = formula.build("12", "0.1", "1")
        assert result == "of:=12*0.1/1"

    def test_dilution_large_final_volume(self) -> None:
        """Test dilution with large final volume."""
        formula = DilutionFormula()
        result = formula.build("1", "50", "500")
        assert result == "of:=1*50/500"

    def test_dilution_cell_references(self) -> None:
        """Test dilution with cell references."""
        formula = DilutionFormula()
        result = formula.build("A1", "B1", "C1")
        assert result == "of:=A1*B1/C1"

    def test_dilution_metadata(self) -> None:
        """Test dilution formula metadata."""
        formula = DilutionFormula()
        metadata = formula.metadata

        assert metadata.name == "DILUTION"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 3


# ============================================================================
# Avogadro Particles Formula Tests
# ============================================================================


class TestAvogadroParticlesFormula:
    """Test Avogadro's number particle calculations."""

    def test_avogadro_particles_one_mole(self) -> None:
        """Test particles in one mole."""
        formula = AvogadroParticlesFormula()
        result = formula.build("1")
        assert result == "of:=1*6.022E23"

    def test_avogadro_particles_multiple_moles(self) -> None:
        """Test particles in multiple moles."""
        formula = AvogadroParticlesFormula()
        result = formula.build("2")
        assert result == "of:=2*6.022E23"

    def test_avogadro_particles_fractional_moles(self) -> None:
        """Test particles in fractional moles."""
        formula = AvogadroParticlesFormula()
        result = formula.build("0.5")
        assert result == "of:=0.5*6.022E23"

    def test_avogadro_particles_custom_constant(self) -> None:
        """Test particles with custom Avogadro constant."""
        formula = AvogadroParticlesFormula()
        result = formula.build("1", "6.02214076E23")
        assert result == "of:=1*6.02214076E23"

    def test_avogadro_particles_cell_references(self) -> None:
        """Test particles with cell references."""
        formula = AvogadroParticlesFormula()
        result = formula.build("A1")
        assert result == "of:=A1*6.022E23"

    def test_avogadro_particles_metadata(self) -> None:
        """Test Avogadro particles formula metadata."""
        formula = AvogadroParticlesFormula()
        metadata = formula.metadata

        assert metadata.name == "AVOGADRO_PARTICLES"
        assert metadata.category == "stoichiometry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestMolecularWeightCalculations:
    """Test molecular weight calculation utilities."""

    def test_molecular_weight_water(self) -> None:
        """Test molecular weight of water (H2O)."""
        mw = calculate_molecular_weight("H2O")
        assert 17.0 < mw < 19.0

    def test_molecular_weight_carbon_dioxide(self) -> None:
        """Test molecular weight of carbon dioxide (CO2)."""
        mw = calculate_molecular_weight("CO2")
        assert 43.0 < mw < 45.0

    def test_molecular_weight_glucose(self) -> None:
        """Test molecular weight of glucose (C6H12O6)."""
        mw = calculate_molecular_weight("C6H12O6")
        assert 178.0 < mw < 182.0

    def test_molecular_weight_sodium_chloride(self) -> None:
        """Test molecular weight of sodium chloride (NaCl)."""
        mw = calculate_molecular_weight("NaCl")
        assert 57.0 < mw < 59.0


class TestDilutionFactorCalculations:
    """Test dilution factor calculation utilities."""

    def test_dilution_factor_ten_fold(self) -> None:
        """Test 10-fold dilution factor."""
        factor = calculate_dilution_factor(10.0, 1.0)
        assert factor == 10.0

    def test_dilution_factor_hundred_fold(self) -> None:
        """Test 100-fold dilution factor."""
        factor = calculate_dilution_factor(100.0, 1.0)
        assert factor == 100.0

    def test_dilution_factor_fractional(self) -> None:
        """Test fractional dilution factor."""
        factor = calculate_dilution_factor(5.0, 2.0)
        assert factor == 2.5

    def test_dilution_factor_zero_raises(self) -> None:
        """Test that zero final volume raises error."""
        with pytest.raises(ValueError):
            calculate_dilution_factor(10.0, 0.0)

    def test_dilution_factor_negative_raises(self) -> None:
        """Test that negative values raise error."""
        with pytest.raises(ValueError):
            calculate_dilution_factor(10.0, -1.0)


class TestScientificNotation:
    """Test scientific notation formatting."""

    def test_format_scientific_small_number(self) -> None:
        """Test formatting small numbers."""
        formatted = format_scientific_notation(0.00012345, 2)
        assert "e" in formatted.lower() or "E" in formatted

    def test_format_scientific_large_number(self) -> None:
        """Test formatting large numbers."""
        formatted = format_scientific_notation(6.022e23, 3)
        assert "e" in formatted.lower() or "E" in formatted


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestStoichiometryEdgeCases:
    """Test edge cases in stoichiometry formulas."""

    def test_molar_mass_validates_arguments(self) -> None:
        """Test molar mass argument validation."""
        formula = MolarMassFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("58.44")

    def test_limiting_reagent_validates_arguments(self) -> None:
        """Test limiting reagent argument validation."""
        formula = LimitingReagentFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1", "2", "3")

    def test_theoretical_yield_validates_arguments(self) -> None:
        """Test theoretical yield argument validation."""
        formula = TheoreticalYieldFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("2", "1")

    def test_percent_composition_validates_arguments(self) -> None:
        """Test percent composition argument validation."""
        formula = PercentCompositionFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("2", "1.008")

    def test_dilution_validates_arguments(self) -> None:
        """Test dilution argument validation."""
        formula = DilutionFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("6", "0.1")


# ============================================================================
# Integration Tests
# ============================================================================


class TestStoichiometryIntegration:
    """Integration tests for stoichiometry formulas with plugin."""

    def test_plugin_contains_stoichiometry_formulas(self) -> None:
        """Test plugin has stoichiometry formulas."""
        plugin = ChemistryDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("MOLAR_MASS") is not None
        assert plugin.get_formula("MASS_FROM_MOLES") is not None
        assert plugin.get_formula("MOLES_FROM_MASS") is not None
        assert plugin.get_formula("LIMITING_REAGENT") is not None
        assert plugin.get_formula("THEORETICAL_YIELD") is not None
        assert plugin.get_formula("PERCENT_YIELD") is not None
        assert plugin.get_formula("PERCENT_COMPOSITION") is not None
        assert plugin.get_formula("EMPIRICAL_FORMULA_RATIO") is not None
        assert plugin.get_formula("DILUTION") is not None
        assert plugin.get_formula("AVOGADRO_PARTICLES") is not None

    def test_all_stoichiometry_formulas_produce_odf(self) -> None:
        """Test all stoichiometry formulas produce valid ODF output."""
        plugin = ChemistryDomainPlugin()
        plugin.initialize()

        test_cases = [
            ("MOLAR_MASS", ("58.44", "1")),
            ("MASS_FROM_MOLES", ("2", "18.015")),
            ("MOLES_FROM_MASS", ("36.03", "18.015")),
            ("LIMITING_REAGENT", ("1", "2", "3", "2")),
            ("THEORETICAL_YIELD", ("2", "1", "18.015")),
            ("PERCENT_YIELD", ("85", "100")),
            ("PERCENT_COMPOSITION", ("2", "1.008", "18.015")),
            ("EMPIRICAL_FORMULA_RATIO", ("40", "12.01", "0.833")),
            ("DILUTION", ("6", "0.1", "1")),
            ("AVOGADRO_PARTICLES", ("1",)),
        ]

        for formula_name, args in test_cases:
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula_name} should return ODF formula"
            )

    def test_stoichiometry_formula_count(self) -> None:
        """Test stoichiometry module has 10 formulas."""
        from spreadsheet_dl.domains.chemistry.formulas import stoichiometry

        expected_formulas = [
            "MolarMassFormula",
            "MassFromMolesFormula",
            "MolesFromMassFormula",
            "LimitingReagentFormula",
            "TheoreticalYieldFormula",
            "PercentYieldFormula",
            "PercentCompositionFormula",
            "EmpiricalFormulaRatioFormula",
            "DilutionFormula",
            "AvogadroParticlesFormula",
        ]

        for formula_name in expected_formulas:
            assert hasattr(stoichiometry, formula_name), f"Missing {formula_name}"
