"""Tests for Chemistry domain plugin.

Comprehensive tests for Chemistry domain (95%+ coverage target)
BATCH-4: Chemistry domain creation
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.chemistry import (
    ActivationEnergyFormula,
    BufferCapacityFormula,
    ChemistryDomainPlugin,
    ClausiusClapeyronFormula,
    EnthalpyChangeFormula,
    EquilibriumConstantFormula,
    GasIdealityCheckFormula,
    GibbsFreeEnergyFormula,
    HalfLifeFirstOrderFormula,
    HalfLifeSecondOrderFormula,
    IntegratedRateLawFormula,
    MolalityFormula,
    MolarityFormula,
    MoleFractionFormula,
    OsmoticPressureFormula,
    RaoultsLawFormula,
    RateConstantFormula,
    ReactionEntropyChangeFormula,
    RealGasVanDerWaalsFormula,
    VantHoffEquationFormula,
    pHCalculationFormula,
)
from spreadsheet_dl.domains.chemistry.utils import (
    calculate_concentration_from_absorbance,
    calculate_concentration_from_ph,
    calculate_dilution_factor,
    calculate_molecular_weight,
    calculate_ph_from_concentration,
    celsius_to_kelvin,
    format_scientific_notation,
    kelvin_to_celsius,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = ChemistryDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "chemistry"
    assert metadata.version == "0.1.0"
    assert "chemistry" in metadata.tags
    assert "thermodynamics" in metadata.tags
    assert "kinetics" in metadata.tags
    assert "solutions" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = ChemistryDomainPlugin()
    plugin.initialize()

    # Verify thermodynamics formulas registered (8 total)
    assert plugin.get_formula("GIBBS_FREE_ENERGY") == GibbsFreeEnergyFormula
    assert plugin.get_formula("ENTHALPY_CHANGE") == EnthalpyChangeFormula
    assert plugin.get_formula("REACTION_ENTROPY_CHANGE") == ReactionEntropyChangeFormula
    assert plugin.get_formula("EQUILIBRIUM_CONSTANT") == EquilibriumConstantFormula
    assert plugin.get_formula("VANT_HOFF_EQUATION") == VantHoffEquationFormula
    assert plugin.get_formula("CLAUSIUS_CLAPEYRON") == ClausiusClapeyronFormula
    assert plugin.get_formula("GAS_IDEALITY_CHECK") == GasIdealityCheckFormula
    assert plugin.get_formula("REAL_GAS_VAN_DER_WAALS") == RealGasVanDerWaalsFormula

    # Verify solutions formulas registered (7 total)
    assert plugin.get_formula("MOLARITY") == MolarityFormula
    assert plugin.get_formula("MOLALITY") == MolalityFormula
    assert plugin.get_formula("MOLE_FRACTION") == MoleFractionFormula
    assert plugin.get_formula("RAOULTS_LAW") == RaoultsLawFormula
    assert plugin.get_formula("OSMOTIC_PRESSURE") == OsmoticPressureFormula
    assert plugin.get_formula("PH_CALCULATION") == pHCalculationFormula
    assert plugin.get_formula("BUFFER_CAPACITY") == BufferCapacityFormula

    # Verify kinetics formulas registered (5 total)
    assert plugin.get_formula("RATE_CONSTANT") == RateConstantFormula
    assert plugin.get_formula("HALF_LIFE_FIRST_ORDER") == HalfLifeFirstOrderFormula
    assert plugin.get_formula("HALF_LIFE_SECOND_ORDER") == HalfLifeSecondOrderFormula
    assert plugin.get_formula("INTEGRATED_RATE_LAW") == IntegratedRateLawFormula
    assert plugin.get_formula("ACTIVATION_ENERGY") == ActivationEnergyFormula

    # Verify total count (8 thermodynamics + 7 solutions + 5 kinetics + 10 stoichiometry + 10 electrochemistry)
    assert len(plugin.list_formulas()) == 40


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = ChemistryDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = ChemistryDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Thermodynamics Formula Tests
# ============================================================================


def test_gibbs_free_energy_formula() -> None:
    """Test GIBBS_FREE_ENERGY formula."""
    formula = GibbsFreeEnergyFormula()
    metadata = formula.metadata

    assert metadata.name == "GIBBS_FREE_ENERGY"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 3

    # Test build
    result = formula.build("100", "298", "0.5")
    assert result == "of:=100-298*0.5"
    assert result.startswith("of:=")


def test_enthalpy_change_formula() -> None:
    """Test ENTHALPY_CHANGE formula."""
    formula = EnthalpyChangeFormula()
    metadata = formula.metadata

    assert metadata.name == "ENTHALPY_CHANGE"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 2

    result = formula.build("200", "150")
    assert result == "of:=200-150"


def test_entropy_change_formula() -> None:
    """Test REACTION_ENTROPY_CHANGE formula."""
    formula = ReactionEntropyChangeFormula()
    metadata = formula.metadata

    assert metadata.name == "REACTION_ENTROPY_CHANGE"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 2

    result = formula.build("0.5", "0.3")
    assert result == "of:=0.5-0.3"


def test_equilibrium_constant_formula() -> None:
    """Test EQUILIBRIUM_CONSTANT formula."""
    formula = EquilibriumConstantFormula()
    metadata = formula.metadata

    assert metadata.name == "EQUILIBRIUM_CONSTANT"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 3

    result = formula.build("-10", "298")
    assert "EXP" in result
    assert result.startswith("of:=")


def test_vant_hoff_equation_formula() -> None:
    """Test VANT_HOFF_EQUATION formula."""
    formula = VantHoffEquationFormula()
    metadata = formula.metadata

    assert metadata.name == "VANT_HOFF_EQUATION"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 5

    result = formula.build("1.5", "298", "323", "-50")
    assert "EXP" in result
    assert result.startswith("of:=")


def test_clausius_clapeyron_formula() -> None:
    """Test CLAUSIUS_CLAPEYRON formula."""
    formula = ClausiusClapeyronFormula()
    metadata = formula.metadata

    assert metadata.name == "CLAUSIUS_CLAPEYRON"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 5

    result = formula.build("100", "373", "400", "40.7")
    assert "EXP" in result
    assert result.startswith("of:=")


def test_ideal_gas_law_formula() -> None:
    """Test GAS_IDEALITY_CHECK formula."""
    formula = GasIdealityCheckFormula()
    metadata = formula.metadata

    assert metadata.name == "GAS_IDEALITY_CHECK"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 5

    result = formula.build("2", "10", "1", "298")
    assert "/" in result
    assert "*" in result
    assert result.startswith("of:=")


def test_real_gas_van_der_waals_formula() -> None:
    """Test REAL_GAS_VAN_DER_WAALS formula."""
    formula = RealGasVanDerWaalsFormula()
    metadata = formula.metadata

    assert metadata.name == "REAL_GAS_VAN_DER_WAALS"
    assert metadata.category == "thermodynamics"
    assert len(metadata.arguments) == 7

    result = formula.build("10", "2", "1", "300", "1.36", "0.0318")
    assert "^2" in result  # Squared terms
    assert result.startswith("of:=")


# ============================================================================
# Solutions Formula Tests
# ============================================================================


def test_molarity_formula() -> None:
    """Test MOLARITY formula."""
    formula = MolarityFormula()
    metadata = formula.metadata

    assert metadata.name == "MOLARITY"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 2

    result = formula.build("2", "0.5")
    assert result == "of:=2/0.5"


def test_molality_formula() -> None:
    """Test MOLALITY formula."""
    formula = MolalityFormula()
    metadata = formula.metadata

    assert metadata.name == "MOLALITY"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 2

    result = formula.build("1.5", "2")
    assert result == "of:=1.5/2"


def test_mole_fraction_formula() -> None:
    """Test MOLE_FRACTION formula."""
    formula = MoleFractionFormula()
    metadata = formula.metadata

    assert metadata.name == "MOLE_FRACTION"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 2

    result = formula.build("3", "10")
    assert result == "of:=3/10"


def test_raoults_law_formula() -> None:
    """Test RAOULTS_LAW formula."""
    formula = RaoultsLawFormula()
    metadata = formula.metadata

    assert metadata.name == "RAOULTS_LAW"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 2

    result = formula.build("100", "0.8")
    assert result == "of:=100*0.8"


def test_osmotic_pressure_formula() -> None:
    """Test OSMOTIC_PRESSURE formula."""
    formula = OsmoticPressureFormula()
    metadata = formula.metadata

    assert metadata.name == "OSMOTIC_PRESSURE"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 3

    result = formula.build("1.5", "298")
    assert "*" in result
    assert result.startswith("of:=")


def test_ph_calculation_formula() -> None:
    """Test PH_CALCULATION formula."""
    formula = pHCalculationFormula()
    metadata = formula.metadata

    assert metadata.name == "PH_CALCULATION"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 1

    result = formula.build("0.001")
    assert "LOG10" in result
    assert result.startswith("of:=")


def test_buffer_capacity_formula() -> None:
    """Test BUFFER_CAPACITY formula."""
    formula = BufferCapacityFormula()
    metadata = formula.metadata

    assert metadata.name == "BUFFER_CAPACITY"
    assert metadata.category == "solutions"
    assert len(metadata.arguments) == 3

    result = formula.build("0.1", "1.8e-5", "4.74")
    assert "2.303" in result
    assert "^2" in result
    assert result.startswith("of:=")


# ============================================================================
# Kinetics Formula Tests
# ============================================================================


def test_rate_constant_formula() -> None:
    """Test RATE_CONSTANT formula."""
    formula = RateConstantFormula()
    metadata = formula.metadata

    assert metadata.name == "RATE_CONSTANT"
    assert metadata.category == "kinetics"
    assert len(metadata.arguments) == 4

    result = formula.build("1e13", "50", "298")
    assert "EXP" in result
    assert result.startswith("of:=")


def test_half_life_first_order_formula() -> None:
    """Test HALF_LIFE_FIRST_ORDER formula."""
    formula = HalfLifeFirstOrderFormula()
    metadata = formula.metadata

    assert metadata.name == "HALF_LIFE_FIRST_ORDER"
    assert metadata.category == "kinetics"
    assert len(metadata.arguments) == 1

    result = formula.build("0.0693")
    assert "LN(2)" in result
    assert result.startswith("of:=")


def test_half_life_second_order_formula() -> None:
    """Test HALF_LIFE_SECOND_ORDER formula."""
    formula = HalfLifeSecondOrderFormula()
    metadata = formula.metadata

    assert metadata.name == "HALF_LIFE_SECOND_ORDER"
    assert metadata.category == "kinetics"
    assert len(metadata.arguments) == 2

    result = formula.build("0.1", "2")
    assert "/" in result
    assert result.startswith("of:=")


def test_integrated_rate_law_formula() -> None:
    """Test INTEGRATED_RATE_LAW formula."""
    formula = IntegratedRateLawFormula()
    metadata = formula.metadata

    assert metadata.name == "INTEGRATED_RATE_LAW"
    assert metadata.category == "kinetics"
    assert len(metadata.arguments) == 4

    # Test first order
    result = formula.build("2", "0.1", "10", "1")
    assert "IF" in result
    assert "EXP" in result
    assert result.startswith("of:=")


def test_activation_energy_formula() -> None:
    """Test ACTIVATION_ENERGY formula."""
    formula = ActivationEnergyFormula()
    metadata = formula.metadata

    assert metadata.name == "ACTIVATION_ENERGY"
    assert metadata.category == "kinetics"
    assert len(metadata.arguments) == 5

    result = formula.build("0.01", "0.05", "298", "323")
    assert "LN" in result
    assert result.startswith("of:=")


# ============================================================================
# Formula Argument Validation Tests
# ============================================================================


def test_formula_argument_validation_too_few() -> None:
    """Test formula validation with too few arguments."""
    formula = GibbsFreeEnergyFormula()

    with pytest.raises(ValueError, match="requires at least"):
        formula.build("100", "298")  # Missing entropy


def test_formula_argument_validation_too_many() -> None:
    """Test formula validation with too many arguments."""
    formula = pHCalculationFormula()

    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("0.001", "extra", "args")


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_calculate_molecular_weight() -> None:
    """Test molecular weight calculation."""
    # Water H2O
    mw = calculate_molecular_weight("H2O")
    assert 17.0 < mw < 19.0

    # Carbon dioxide CO2
    mw = calculate_molecular_weight("CO2")
    assert 43.0 < mw < 45.0


def test_calculate_dilution_factor() -> None:
    """Test dilution factor calculation."""
    factor = calculate_dilution_factor(10.0, 1.0)
    assert factor == 10.0

    with pytest.raises(ValueError):
        calculate_dilution_factor(10.0, 0.0)


def test_calculate_concentration_from_absorbance() -> None:
    """Test Beer's law concentration calculation."""
    conc = calculate_concentration_from_absorbance(0.5, 1000, 1.0)
    assert conc == 0.0005

    with pytest.raises(ValueError):
        calculate_concentration_from_absorbance(0.5, 0, 1.0)


def test_kelvin_to_celsius() -> None:
    """Test Kelvin to Celsius conversion."""
    celsius = kelvin_to_celsius(298.15)
    assert abs(celsius - 25.0) < 0.01


def test_celsius_to_kelvin() -> None:
    """Test Celsius to Kelvin conversion."""
    kelvin = celsius_to_kelvin(25.0)
    assert abs(kelvin - 298.15) < 0.01


def test_calculate_ph_from_concentration() -> None:
    """Test pH calculation from H+ concentration."""
    pH = calculate_ph_from_concentration(1e-7)
    assert abs(pH - 7.0) < 0.01

    pH = calculate_ph_from_concentration(1e-3)
    assert abs(pH - 3.0) < 0.01

    with pytest.raises(ValueError):
        calculate_ph_from_concentration(0)


def test_calculate_concentration_from_ph() -> None:
    """Test H+ concentration from pH."""
    conc = calculate_concentration_from_ph(7.0)
    assert abs(conc - 1e-7) < 1e-9

    conc = calculate_concentration_from_ph(3.0)
    assert abs(conc - 1e-3) < 1e-5


def test_format_scientific_notation() -> None:
    """Test scientific notation formatting."""
    formatted = format_scientific_notation(0.00012345, 2)
    assert "E-04" in formatted or "e-04" in formatted


# ============================================================================
# Formula Metadata Tests
# ============================================================================


def test_all_formulas_have_metadata() -> None:
    """Test that all formulas have complete metadata."""
    plugin = ChemistryDomainPlugin()
    plugin.initialize()

    for formula_name in plugin.list_formulas():
        formula_class = plugin.get_formula(formula_name)
        assert formula_class is not None

        formula = formula_class()
        metadata = formula.metadata

        # Check required metadata fields
        assert metadata.name
        assert metadata.category
        assert metadata.description
        assert len(metadata.arguments) > 0
        assert metadata.return_type


def test_all_formulas_have_examples() -> None:
    """Test that all formulas have usage examples."""
    plugin = ChemistryDomainPlugin()
    plugin.initialize()

    for formula_name in plugin.list_formulas():
        formula_class = plugin.get_formula(formula_name)
        assert formula_class is not None

        formula = formula_class()
        metadata = formula.metadata

        # Each formula should have at least one example
        assert len(metadata.examples) > 0


def test_all_formulas_build_returns_odf() -> None:
    """Test that all formulas return ODF formula strings."""
    plugin = ChemistryDomainPlugin()
    plugin.initialize()

    # Test with dummy arguments
    test_args = {
        "GIBBS_FREE_ENERGY": ("100", "298", "0.5"),
        "ENTHALPY_CHANGE": ("200", "150"),
        "REACTION_ENTROPY_CHANGE": ("0.5", "0.3"),
        "EQUILIBRIUM_CONSTANT": ("-10", "298"),
        "VANT_HOFF_EQUATION": ("1.5", "298", "323", "-50"),
        "CLAUSIUS_CLAPEYRON": ("100", "373", "400", "40.7"),
        "GAS_IDEALITY_CHECK": ("2", "10", "1", "298"),
        "REAL_GAS_VAN_DER_WAALS": ("10", "2", "1", "300", "1.36", "0.0318"),
        "MOLARITY": ("2", "0.5"),
        "MOLALITY": ("1.5", "2"),
        "MOLE_FRACTION": ("3", "10"),
        "RAOULTS_LAW": ("100", "0.8"),
        "OSMOTIC_PRESSURE": ("1.5", "298"),
        "PH_CALCULATION": ("0.001",),
        "BUFFER_CAPACITY": ("0.1", "1.8e-5", "4.74"),
        "RATE_CONSTANT": ("1e13", "50", "298"),
        "HALF_LIFE_FIRST_ORDER": ("0.0693",),
        "HALF_LIFE_SECOND_ORDER": ("0.1", "2"),
        "INTEGRATED_RATE_LAW": ("2", "0.1", "10"),
        "ACTIVATION_ENERGY": ("0.01", "0.05", "298", "323"),
    }

    for formula_name in plugin.list_formulas():
        formula_class = plugin.get_formula(formula_name)
        assert formula_class is not None

        formula = formula_class()
        args = test_args.get(formula_name, ())

        if args:
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula_name} should return ODF formula"
            )
