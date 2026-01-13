"""Tests for Chemistry electrochemistry formulas.

Comprehensive tests for electrochemistry-related formulas
including Nernst equation, cell potentials, Faraday's law, etc.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.chemistry import (
    ChemistryDomainPlugin,
)
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
from spreadsheet_dl.domains.chemistry.formulas.solutions import (
    MolalityFormula,
    MolarityFormula,
    OsmoticPressureFormula,
    pHCalculationFormula,
)
from spreadsheet_dl.domains.chemistry.formulas.thermodynamics import (
    EquilibriumConstantFormula,
    GibbsFreeEnergyFormula,
    VantHoffEquationFormula,
)
from spreadsheet_dl.domains.chemistry.utils import (
    calculate_concentration_from_ph,
    calculate_ph_from_concentration,
    celsius_to_kelvin,
    kelvin_to_celsius,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


# ============================================================================
# Nernst Equation Formula Tests
# ============================================================================


class TestNernstEquationFormula:
    """Test Nernst equation calculations."""

    def test_nernst_equation_standard_conditions(self) -> None:
        """Test Nernst equation at standard conditions (298K)."""
        formula = NernstEquationFormula()
        result = formula.build("0.76", "2", "0.1", "1", "298")
        assert result.startswith("of:=")
        assert "LOG10" in result
        assert "0.76" in result
        assert "0.0592" in result

    def test_nernst_equation_default_temperature(self) -> None:
        """Test Nernst equation with default temperature."""
        formula = NernstEquationFormula()
        result = formula.build("0.76", "2", "0.1", "1")
        assert result.startswith("of:=")
        assert "298" in result

    def test_nernst_equation_elevated_temperature(self) -> None:
        """Test Nernst equation at elevated temperature."""
        formula = NernstEquationFormula()
        result = formula.build("0.76", "2", "0.1", "1", "350")
        assert "350" in result
        assert "298" in result  # Temperature ratio

    def test_nernst_equation_cell_references(self) -> None:
        """Test Nernst equation with cell references."""
        formula = NernstEquationFormula()
        result = formula.build("A1", "B1", "C1", "D1")
        assert "A1" in result
        assert "B1" in result
        assert "C1" in result
        assert "D1" in result

    def test_nernst_equation_metadata(self) -> None:
        """Test Nernst equation formula metadata."""
        formula = NernstEquationFormula()
        metadata = formula.metadata

        assert metadata.name == "NERNST_EQUATION"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 5
        assert metadata.return_type == "number"


# ============================================================================
# Faraday Electrolysis Formula Tests
# ============================================================================


class TestFaradayElectrolysisFormula:
    """Test Faraday's law of electrolysis calculations."""

    def test_faraday_electrolysis_standard(self) -> None:
        """Test standard electrolysis mass calculation."""
        formula = FaradayElectrolysisFormula()
        result = formula.build("2", "3600", "63.5", "2")
        assert result.startswith("of:=")
        assert "2*3600*63.5" in result
        assert "96485" in result

    def test_faraday_electrolysis_custom_constant(self) -> None:
        """Test electrolysis with custom Faraday constant."""
        formula = FaradayElectrolysisFormula()
        result = formula.build("2", "3600", "63.5", "2", "96500")
        assert "96500" in result

    def test_faraday_electrolysis_cell_references(self) -> None:
        """Test electrolysis with cell references."""
        formula = FaradayElectrolysisFormula()
        result = formula.build("A1", "B1", "C1", "D1")
        assert "A1" in result
        assert "B1" in result
        assert "C1" in result

    def test_faraday_electrolysis_metadata(self) -> None:
        """Test Faraday electrolysis formula metadata."""
        formula = FaradayElectrolysisFormula()
        metadata = formula.metadata

        assert metadata.name == "FARADAY_ELECTROLYSIS"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 5


# ============================================================================
# Standard Cell Potential Formula Tests
# ============================================================================


class TestStandardCellPotentialFormula:
    """Test standard cell potential calculations."""

    def test_standard_cell_potential_positive(self) -> None:
        """Test standard cell potential for spontaneous reaction."""
        formula = StandardCellPotentialFormula()
        result = formula.build("0.34", "-0.76")  # Cu cathode, Zn anode
        assert result == "of:=0.34--0.76"

    def test_standard_cell_potential_negative(self) -> None:
        """Test standard cell potential for non-spontaneous reaction."""
        formula = StandardCellPotentialFormula()
        result = formula.build("-0.76", "0.34")  # Reversed
        assert result == "of:=-0.76-0.34"

    def test_standard_cell_potential_cell_references(self) -> None:
        """Test standard cell potential with cell references."""
        formula = StandardCellPotentialFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1-B1"

    def test_standard_cell_potential_metadata(self) -> None:
        """Test standard cell potential formula metadata."""
        formula = StandardCellPotentialFormula()
        metadata = formula.metadata

        assert metadata.name == "STANDARD_CELL_POTENTIAL"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Gibbs Electrochemical Formula Tests
# ============================================================================


class TestGibbsElectrochemicalFormula:
    """Test Gibbs free energy from cell potential calculations."""

    def test_gibbs_electrochemical_standard(self) -> None:
        """Test standard Gibbs electrochemical calculation."""
        formula = GibbsElectrochemicalFormula()
        result = formula.build("2", "1.1")
        assert result.startswith("of:=")
        assert "-" in result  # ΔG = -nFE
        assert "96485" in result
        assert "1000" in result  # Division for kJ/mol

    def test_gibbs_electrochemical_custom_faraday(self) -> None:
        """Test Gibbs with custom Faraday constant."""
        formula = GibbsElectrochemicalFormula()
        result = formula.build("2", "1.1", "96500")
        assert "96500" in result

    def test_gibbs_electrochemical_cell_references(self) -> None:
        """Test Gibbs electrochemical with cell references."""
        formula = GibbsElectrochemicalFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result
        assert "B1" in result

    def test_gibbs_electrochemical_metadata(self) -> None:
        """Test Gibbs electrochemical formula metadata."""
        formula = GibbsElectrochemicalFormula()
        metadata = formula.metadata

        assert metadata.name == "GIBBS_ELECTROCHEMICAL"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 3


# ============================================================================
# Equilibrium Constant Electro Formula Tests
# ============================================================================


class TestEquilibriumConstantElectroFormula:
    """Test equilibrium constant from cell potential calculations."""

    def test_equilibrium_constant_electro_standard(self) -> None:
        """Test equilibrium constant at standard conditions."""
        formula = EquilibriumConstantElectroFormula()
        result = formula.build("2", "1.1")
        assert result.startswith("of:=")
        assert "EXP" in result
        assert "96485" in result
        assert "8.314" in result

    def test_equilibrium_constant_electro_custom_temperature(self) -> None:
        """Test equilibrium constant at custom temperature."""
        formula = EquilibriumConstantElectroFormula()
        result = formula.build("2", "1.1", "350")
        assert "350" in result

    def test_equilibrium_constant_electro_cell_references(self) -> None:
        """Test equilibrium constant with cell references."""
        formula = EquilibriumConstantElectroFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result
        assert "B1" in result

    def test_equilibrium_constant_electro_metadata(self) -> None:
        """Test equilibrium constant electro formula metadata."""
        formula = EquilibriumConstantElectroFormula()
        metadata = formula.metadata

        assert metadata.name == "EQUILIBRIUM_CONSTANT_ELECTRO"
        assert metadata.category == "electrochemistry"


# ============================================================================
# Ohmic Resistance Formula Tests
# ============================================================================


class TestOhmicResistanceFormula:
    """Test ohmic resistance (IR drop) calculations."""

    def test_ohmic_resistance_standard(self) -> None:
        """Test standard IR drop calculation."""
        formula = OhmicResistanceFormula()
        result = formula.build("0.5", "10")
        assert result == "of:=0.5*10"

    def test_ohmic_resistance_high_current(self) -> None:
        """Test IR drop with high current."""
        formula = OhmicResistanceFormula()
        result = formula.build("5", "100")
        assert result == "of:=5*100"

    def test_ohmic_resistance_cell_references(self) -> None:
        """Test IR drop with cell references."""
        formula = OhmicResistanceFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1*B1"

    def test_ohmic_resistance_metadata(self) -> None:
        """Test ohmic resistance formula metadata."""
        formula = OhmicResistanceFormula()
        metadata = formula.metadata

        assert metadata.name == "OHMIC_RESISTANCE"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Overpotential Formula Tests
# ============================================================================


class TestOverpotentialFormula:
    """Test overpotential calculations."""

    def test_overpotential_positive(self) -> None:
        """Test positive overpotential (anodic)."""
        formula = OverpotentialFormula()
        result = formula.build("1.5", "1.23")
        assert result == "of:=1.5-1.23"

    def test_overpotential_negative(self) -> None:
        """Test negative overpotential (cathodic)."""
        formula = OverpotentialFormula()
        result = formula.build("1.0", "1.23")
        assert result == "of:=1.0-1.23"

    def test_overpotential_cell_references(self) -> None:
        """Test overpotential with cell references."""
        formula = OverpotentialFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1-B1"

    def test_overpotential_metadata(self) -> None:
        """Test overpotential formula metadata."""
        formula = OverpotentialFormula()
        metadata = formula.metadata

        assert metadata.name == "OVERPOTENTIAL"
        assert metadata.category == "electrochemistry"


# ============================================================================
# Tafel Equation Formula Tests
# ============================================================================


class TestTafelEquationFormula:
    """Test Tafel equation calculations."""

    def test_tafel_equation_standard(self) -> None:
        """Test standard Tafel equation calculation."""
        formula = TafelEquationFormula()
        result = formula.build("1E-6", "0.01", "0.12")
        assert result.startswith("of:=")
        assert "LOG10" in result
        assert "0.12" in result

    def test_tafel_equation_high_current(self) -> None:
        """Test Tafel equation at high current density."""
        formula = TafelEquationFormula()
        result = formula.build("1E-6", "1", "0.12")
        assert "1" in result

    def test_tafel_equation_cell_references(self) -> None:
        """Test Tafel equation with cell references."""
        formula = TafelEquationFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result
        assert "B1" in result
        assert "C1" in result

    def test_tafel_equation_metadata(self) -> None:
        """Test Tafel equation formula metadata."""
        formula = TafelEquationFormula()
        metadata = formula.metadata

        assert metadata.name == "TAFEL_EQUATION"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 3


# ============================================================================
# Butler-Volmer Formula Tests
# ============================================================================


class TestButlerVolmerFormula:
    """Test Butler-Volmer equation calculations."""

    def test_butler_volmer_standard(self) -> None:
        """Test standard Butler-Volmer calculation."""
        formula = ButlerVolmerFormula()
        result = formula.build("1E-6", "0.1", "0.5", "298")
        assert result.startswith("of:=")
        assert "EXP" in result
        assert "1E-6" in result
        assert "11605" in result  # F/R constant

    def test_butler_volmer_default_parameters(self) -> None:
        """Test Butler-Volmer with default alpha and temperature."""
        formula = ButlerVolmerFormula()
        result = formula.build("1E-6", "0.1")
        assert "0.5" in result  # Default alpha
        assert "298" in result  # Default temperature

    def test_butler_volmer_custom_alpha(self) -> None:
        """Test Butler-Volmer with custom transfer coefficient."""
        formula = ButlerVolmerFormula()
        result = formula.build("1E-6", "0.1", "0.3")
        assert "0.3" in result

    def test_butler_volmer_cell_references(self) -> None:
        """Test Butler-Volmer with cell references."""
        formula = ButlerVolmerFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result
        assert "B1" in result

    def test_butler_volmer_metadata(self) -> None:
        """Test Butler-Volmer formula metadata."""
        formula = ButlerVolmerFormula()
        metadata = formula.metadata

        assert metadata.name == "BUTLER_VOLMER"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 4


# ============================================================================
# Conductivity Formula Tests
# ============================================================================


class TestConductivityFormula:
    """Test ionic conductivity calculations."""

    def test_conductivity_standard(self) -> None:
        """Test standard conductivity calculation."""
        formula = ConductivityFormula()
        result = formula.build("500", "1.0")
        assert result == "of:=1.0/500"

    def test_conductivity_high_resistance(self) -> None:
        """Test conductivity with high resistance."""
        formula = ConductivityFormula()
        result = formula.build("10000", "1.0")
        assert result == "of:=1.0/10000"

    def test_conductivity_cell_references(self) -> None:
        """Test conductivity with cell references."""
        formula = ConductivityFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=B1/A1"

    def test_conductivity_metadata(self) -> None:
        """Test conductivity formula metadata."""
        formula = ConductivityFormula()
        metadata = formula.metadata

        assert metadata.name == "IONIC_CONDUCTIVITY"
        assert metadata.category == "electrochemistry"
        assert len(metadata.arguments) == 2


# ============================================================================
# Related Formula Tests (from other modules)
# ============================================================================


class TestEquilibriumConstantCalculations:
    """Test equilibrium constant at standard conditions (from thermodynamics)."""

    def test_equilibrium_constant_standard_conditions(self) -> None:
        """Test equilibrium constant at standard conditions (298K)."""
        formula = EquilibriumConstantFormula()
        result = formula.build("-10000", "298")
        assert result.startswith("of:=")
        assert "EXP" in result

    def test_equilibrium_constant_elevated_temperature(self) -> None:
        """Test equilibrium constant at elevated temperature."""
        formula = EquilibriumConstantFormula()
        result = formula.build("-20000", "373")
        assert result.startswith("of:=")
        assert "EXP" in result


class TestGibbsFreeEnergyElectrochemistry:
    """Test Gibbs free energy calculations (from thermodynamics)."""

    def test_gibbs_free_energy_spontaneous_reaction(self) -> None:
        """Test Gibbs free energy for spontaneous reaction (negative)."""
        formula = GibbsFreeEnergyFormula()
        result = formula.build("-50", "298", "0.1")
        assert result == "of:=-50-298*0.1"


class TestVantHoffElectrochemistry:
    """Test Van't Hoff equation (from thermodynamics)."""

    def test_vant_hoff_exothermic_reaction(self) -> None:
        """Test Van't Hoff equation for exothermic reaction."""
        formula = VantHoffEquationFormula()
        result = formula.build("1.5", "298", "323", "-50000")
        assert result.startswith("of:=")
        assert "EXP" in result


# ============================================================================
# pH and Solution Electrochemistry Tests
# ============================================================================


class TestpHCalculations:
    """Test pH calculations for electrochemistry applications."""

    def test_ph_neutral_solution(self) -> None:
        """Test pH of neutral solution (pH = 7)."""
        formula = pHCalculationFormula()
        result = formula.build("1e-7")
        assert result.startswith("of:=")
        assert "LOG10" in result


class TestOsmoticPressureElectrochemistry:
    """Test osmotic pressure calculations."""

    def test_osmotic_pressure_dilute_solution(self) -> None:
        """Test osmotic pressure of dilute solution."""
        formula = OsmoticPressureFormula()
        result = formula.build("0.1", "298")
        assert result.startswith("of:=")


class TestMolarityCalculations:
    """Test molarity calculations for electrochemistry."""

    def test_molarity_standard(self) -> None:
        """Test standard molarity calculation."""
        formula = MolarityFormula()
        result = formula.build("2", "0.5")
        assert result == "of:=2/0.5"


class TestMolalityCalculations:
    """Test molality calculations."""

    def test_molality_standard(self) -> None:
        """Test standard molality calculation."""
        formula = MolalityFormula()
        result = formula.build("1.5", "2")
        assert result == "of:=1.5/2"


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestTemperatureConversions:
    """Test temperature conversion utilities for electrochemistry."""

    def test_celsius_to_kelvin_standard(self) -> None:
        """Test standard temperature conversion (25C to K)."""
        kelvin = celsius_to_kelvin(25.0)
        assert abs(kelvin - 298.15) < 0.01

    def test_celsius_to_kelvin_absolute_zero(self) -> None:
        """Test conversion near absolute zero."""
        kelvin = celsius_to_kelvin(-273.15)
        assert abs(kelvin) < 0.01

    def test_kelvin_to_celsius_standard(self) -> None:
        """Test standard temperature conversion (298K to C)."""
        celsius = kelvin_to_celsius(298.15)
        assert abs(celsius - 25.0) < 0.01

    def test_temperature_conversion_roundtrip(self) -> None:
        """Test roundtrip temperature conversion."""
        original = 50.0
        converted = kelvin_to_celsius(celsius_to_kelvin(original))
        assert abs(converted - original) < 0.01


class TestPHConversions:
    """Test pH conversion utilities."""

    def test_ph_from_concentration_neutral(self) -> None:
        """Test pH from neutral concentration."""
        ph = calculate_ph_from_concentration(1e-7)
        assert abs(ph - 7.0) < 0.01

    def test_concentration_from_ph_neutral(self) -> None:
        """Test concentration from neutral pH."""
        conc = calculate_concentration_from_ph(7.0)
        assert abs(conc - 1e-7) < 1e-9

    def test_ph_concentration_roundtrip(self) -> None:
        """Test roundtrip pH-concentration conversion."""
        original_ph = 5.5
        conc = calculate_concentration_from_ph(original_ph)
        result_ph = calculate_ph_from_concentration(conc)
        assert abs(result_ph - original_ph) < 0.01

    def test_ph_from_zero_concentration_raises(self) -> None:
        """Test that zero concentration raises error."""
        with pytest.raises(ValueError):
            calculate_ph_from_concentration(0)

    def test_ph_from_negative_concentration_raises(self) -> None:
        """Test that negative concentration raises error."""
        with pytest.raises(ValueError):
            calculate_ph_from_concentration(-0.001)


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestElectrochemistryEdgeCases:
    """Test edge cases in electrochemistry formulas."""

    def test_nernst_equation_validates_arguments(self) -> None:
        """Test Nernst equation argument validation."""
        formula = NernstEquationFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("0.76", "2", "0.1")  # Missing reactants_activity

    def test_faraday_electrolysis_validates_arguments(self) -> None:
        """Test Faraday electrolysis argument validation."""
        formula = FaradayElectrolysisFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("2", "3600", "63.5")  # Missing n_electrons

    def test_tafel_equation_validates_arguments(self) -> None:
        """Test Tafel equation argument validation."""
        formula = TafelEquationFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1E-6", "0.01")  # Missing Tafel slope

    def test_butler_volmer_validates_arguments(self) -> None:
        """Test Butler-Volmer argument validation."""
        formula = ButlerVolmerFormula()
        with pytest.raises(ValueError, match="requires at least"):
            formula.build("1E-6")  # Missing overpotential


# ============================================================================
# Integration Tests
# ============================================================================


class TestElectrochemistryIntegration:
    """Integration tests for electrochemistry formulas with plugin."""

    def test_plugin_contains_electrochemistry_formulas(self) -> None:
        """Test plugin has electrochemistry formulas."""
        plugin = ChemistryDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("NERNST_EQUATION") is not None
        assert plugin.get_formula("FARADAY_ELECTROLYSIS") is not None
        assert plugin.get_formula("STANDARD_CELL_POTENTIAL") is not None
        assert plugin.get_formula("GIBBS_ELECTROCHEMICAL") is not None
        assert plugin.get_formula("EQUILIBRIUM_CONSTANT_ELECTRO") is not None
        assert plugin.get_formula("OHMIC_RESISTANCE") is not None
        assert plugin.get_formula("OVERPOTENTIAL") is not None
        assert plugin.get_formula("TAFEL_EQUATION") is not None
        assert plugin.get_formula("BUTLER_VOLMER") is not None
        assert plugin.get_formula("IONIC_CONDUCTIVITY") is not None

    def test_all_electrochemistry_formulas_produce_odf(self) -> None:
        """Test all electrochemistry formulas produce valid ODF output."""
        plugin = ChemistryDomainPlugin()
        plugin.initialize()

        test_cases = [
            ("NERNST_EQUATION", ("0.76", "2", "0.1", "1")),
            ("FARADAY_ELECTROLYSIS", ("2", "3600", "63.5", "2")),
            ("STANDARD_CELL_POTENTIAL", ("0.34", "-0.76")),
            ("GIBBS_ELECTROCHEMICAL", ("2", "1.1")),
            ("EQUILIBRIUM_CONSTANT_ELECTRO", ("2", "1.1")),
            ("OHMIC_RESISTANCE", ("0.5", "10")),
            ("OVERPOTENTIAL", ("1.5", "1.23")),
            ("TAFEL_EQUATION", ("1E-6", "0.01", "0.12")),
            ("BUTLER_VOLMER", ("1E-6", "0.1")),
            ("IONIC_CONDUCTIVITY", ("500", "1.0")),
        ]

        for formula_name, args in test_cases:
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula_name} should return ODF formula"
            )

    def test_electrochemistry_formula_count(self) -> None:
        """Test electrochemistry module has 10 formulas."""
        from spreadsheet_dl.domains.chemistry.formulas import electrochemistry

        expected_formulas = [
            "NernstEquationFormula",
            "FaradayElectrolysisFormula",
            "StandardCellPotentialFormula",
            "GibbsElectrochemicalFormula",
            "EquilibriumConstantElectroFormula",
            "OhmicResistanceFormula",
            "OverpotentialFormula",
            "TafelEquationFormula",
            "ButlerVolmerFormula",
            "ConductivityFormula",
        ]

        for formula_name in expected_formulas:
            assert hasattr(electrochemistry, formula_name), f"Missing {formula_name}"
