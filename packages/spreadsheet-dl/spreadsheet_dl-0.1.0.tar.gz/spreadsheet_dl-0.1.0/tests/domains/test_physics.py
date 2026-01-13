"""Tests for Physics domain plugin.

Comprehensive tests for Physics domain (95%+ coverage target)
BATCH-5: Physics domain creation
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.physics import (
    AngularMomentumFormula,
    BohrRadiusFormula,
    BraggLawFormula,
    CentripetalForceFormula,
    CoulombLawFormula,
    DeBroglieWavelengthFormula,
    DiffractionGratingFormula,
    ElectricFieldFormula,
    FaradayLawFormula,
    HeisenbergUncertaintyFormula,
    KineticEnergyFormula,
    LensMakerEquationFormula,
    LorentzForceFormula,
    MagneticForceFormula,
    MagnificationLensFormula,
    MomentumFormula,
    NewtonSecondLawFormula,
    PhotoelectricEffectFormula,
    PhysicsDomainPlugin,
    PlanckEnergyFormula,
    PotentialEnergyFormula,
    PoyntingVectorFormula,
    RydbergFormulaFormula,
    SnellsLawFormula,
    ThinFilmInterferenceFormula,
    WorkEnergyFormula,
)
from spreadsheet_dl.domains.physics.utils import (
    calculate_escape_velocity,
    calculate_schwarzschild_radius,
    convert_ev_to_joules,
    convert_joules_to_ev,
    degrees_to_radians,
    electron_mass,
    elementary_charge,
    frequency_to_wavelength,
    gravitational_constant,
    planck_constant,
    proton_mass,
    radians_to_degrees,
    reduced_planck_constant,
    speed_of_light,
    wavelength_to_frequency,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = PhysicsDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "physics"
    assert metadata.version == "0.1.0"
    assert "physics" in metadata.tags
    assert "mechanics" in metadata.tags
    assert "electromagnetism" in metadata.tags
    assert "optics" in metadata.tags
    assert "quantum" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = PhysicsDomainPlugin()
    plugin.initialize()

    # Verify mechanics formulas registered (7 total)
    assert plugin.get_formula("NEWTON_SECOND_LAW") == NewtonSecondLawFormula
    assert plugin.get_formula("KINETIC_ENERGY") == KineticEnergyFormula
    assert plugin.get_formula("POTENTIAL_ENERGY") == PotentialEnergyFormula
    assert plugin.get_formula("WORK_ENERGY") == WorkEnergyFormula
    assert plugin.get_formula("MOMENTUM") == MomentumFormula
    assert plugin.get_formula("ANGULAR_MOMENTUM") == AngularMomentumFormula
    assert plugin.get_formula("CENTRIPETAL_FORCE") == CentripetalForceFormula

    # Verify electromagnetism formulas registered (6 total)
    assert plugin.get_formula("COULOMB_LAW") == CoulombLawFormula
    assert plugin.get_formula("ELECTRIC_FIELD") == ElectricFieldFormula
    assert plugin.get_formula("MAGNETIC_FORCE") == MagneticForceFormula
    assert plugin.get_formula("FARADAY_LAW") == FaradayLawFormula
    assert plugin.get_formula("LORENTZ_FORCE") == LorentzForceFormula
    assert plugin.get_formula("POYNTING_VECTOR") == PoyntingVectorFormula

    # Verify optics formulas registered (6 total)
    assert plugin.get_formula("SNELLS_LAW") == SnellsLawFormula
    assert plugin.get_formula("LENS_MAKER_EQUATION") == LensMakerEquationFormula
    assert plugin.get_formula("MAGNIFICATION_LENS") == MagnificationLensFormula
    assert plugin.get_formula("BRAGG_LAW") == BraggLawFormula
    assert plugin.get_formula("THIN_FILM_INTERFERENCE") == ThinFilmInterferenceFormula
    assert plugin.get_formula("DIFFRACTION_GRATING") == DiffractionGratingFormula

    # Verify quantum formulas registered (6 total)
    assert plugin.get_formula("PLANCK_ENERGY") == PlanckEnergyFormula
    assert plugin.get_formula("DE_BROGLIE_WAVELENGTH") == DeBroglieWavelengthFormula
    assert plugin.get_formula("HEISENBERG_UNCERTAINTY") == HeisenbergUncertaintyFormula
    assert plugin.get_formula("PHOTOELECTRIC_EFFECT") == PhotoelectricEffectFormula
    assert plugin.get_formula("BOHR_RADIUS") == BohrRadiusFormula
    assert plugin.get_formula("RYDBERG_FORMULA") == RydbergFormulaFormula

    # Verify total count
    assert len(plugin.list_formulas()) == 50


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = PhysicsDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = PhysicsDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Mechanics Formula Tests
# ============================================================================


def test_newton_second_law_formula() -> None:
    """Test NEWTON_SECOND_LAW formula."""
    formula = NewtonSecondLawFormula()
    metadata = formula.metadata

    assert metadata.name == "NEWTON_SECOND_LAW"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 2

    # Test build
    result = formula.build("10", "2")
    assert result == "of:=10*2"
    assert result.startswith("of:=")


def test_kinetic_energy_formula() -> None:
    """Test KINETIC_ENERGY formula."""
    formula = KineticEnergyFormula()
    metadata = formula.metadata

    assert metadata.name == "KINETIC_ENERGY"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 2

    result = formula.build("10", "5")
    assert result == "of:=0.5*10*5^2"


def test_potential_energy_formula() -> None:
    """Test POTENTIAL_ENERGY formula."""
    formula = PotentialEnergyFormula()
    metadata = formula.metadata

    assert metadata.name == "POTENTIAL_ENERGY"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 3

    # Test with default gravity
    result = formula.build("10", "5")
    assert result == "of:=10*9.81*5"

    # Test with custom gravity
    result = formula.build("10", "5", "10")
    assert result == "of:=10*10*5"


def test_work_energy_formula() -> None:
    """Test WORK_ENERGY formula."""
    formula = WorkEnergyFormula()
    metadata = formula.metadata

    assert metadata.name == "WORK_ENERGY"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 3

    result = formula.build("100", "5", "0")
    assert "COS" in result
    assert "RADIANS" in result
    assert result.startswith("of:=")


def test_momentum_formula() -> None:
    """Test MOMENTUM formula."""
    formula = MomentumFormula()
    metadata = formula.metadata

    assert metadata.name == "MOMENTUM"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 2

    result = formula.build("10", "5")
    assert result == "of:=10*5"


def test_angular_momentum_formula() -> None:
    """Test ANGULAR_MOMENTUM formula."""
    formula = AngularMomentumFormula()
    metadata = formula.metadata

    assert metadata.name == "ANGULAR_MOMENTUM"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 2

    result = formula.build("5", "10")
    assert result == "of:=5*10"


def test_centripetal_force_formula() -> None:
    """Test CENTRIPETAL_FORCE formula."""
    formula = CentripetalForceFormula()
    metadata = formula.metadata

    assert metadata.name == "CENTRIPETAL_FORCE"
    assert metadata.category == "mechanics"
    assert len(metadata.arguments) == 3

    result = formula.build("10", "5", "2")
    assert result == "of:=10*5^2/2"


# ============================================================================
# Electromagnetism Formula Tests
# ============================================================================


def test_coulomb_law_formula() -> None:
    """Test COULOMB_LAW formula."""
    formula = CoulombLawFormula()
    metadata = formula.metadata

    assert metadata.name == "COULOMB_LAW"
    assert metadata.category == "electromagnetism"
    assert len(metadata.arguments) == 4

    # Test with default k constant
    result = formula.build("1e-6", "2e-6", "0.1")
    assert "8.99" in result or "899" in result  # Accept various float formats
    assert result.startswith("of:=")


def test_electric_field_formula() -> None:
    """Test ELECTRIC_FIELD formula."""
    formula = ElectricFieldFormula()
    metadata = formula.metadata

    assert metadata.name == "ELECTRIC_FIELD"
    assert metadata.category == "electromagnetism"
    assert len(metadata.arguments) == 2

    result = formula.build("100", "1e-6")
    assert result == "of:=100/1e-6"


def test_magnetic_force_formula() -> None:
    """Test MAGNETIC_FORCE formula."""
    formula = MagneticForceFormula()
    metadata = formula.metadata

    assert metadata.name == "MAGNETIC_FORCE"
    assert metadata.category == "electromagnetism"
    assert len(metadata.arguments) == 4

    result = formula.build("1e-6", "1e6", "0.5", "90")
    assert "SIN" in result
    assert "RADIANS" in result
    assert result.startswith("of:=")


def test_faraday_law_formula() -> None:
    """Test FARADAY_LAW formula."""
    formula = FaradayLawFormula()
    metadata = formula.metadata

    assert metadata.name == "FARADAY_LAW"
    assert metadata.category == "electromagnetism"
    assert len(metadata.arguments) == 3

    result = formula.build("100", "0.5", "0.1")
    assert result == "of:=100*0.5/0.1"


def test_lorentz_force_formula() -> None:
    """Test LORENTZ_FORCE formula."""
    formula = LorentzForceFormula()
    metadata = formula.metadata

    assert metadata.name == "LORENTZ_FORCE"
    assert metadata.category == "electromagnetism"
    assert len(metadata.arguments) == 4

    result = formula.build("1e-6", "1000", "1e5", "0.5")
    assert result == "of:=1e-6*(1000+1e5*0.5)"


def test_poynting_vector_formula() -> None:
    """Test POYNTING_VECTOR formula."""
    formula = PoyntingVectorFormula()
    metadata = formula.metadata

    assert metadata.name == "POYNTING_VECTOR"
    assert metadata.category == "electromagnetism"
    assert len(metadata.arguments) == 2

    result = formula.build("100", "0.1")
    assert result == "of:=100*0.1"


# ============================================================================
# Optics Formula Tests
# ============================================================================


def test_snells_law_formula() -> None:
    """Test SNELLS_LAW formula."""
    formula = SnellsLawFormula()
    metadata = formula.metadata

    assert metadata.name == "SNELLS_LAW"
    assert metadata.category == "optics"
    assert len(metadata.arguments) == 3

    result = formula.build("1.0", "30", "1.5")
    assert "ASIN" in result
    assert "SIN" in result
    assert "RADIANS" in result
    assert "DEGREES" in result
    assert result.startswith("of:=")


def test_lens_maker_equation_formula() -> None:
    """Test LENS_MAKER_EQUATION formula."""
    formula = LensMakerEquationFormula()
    metadata = formula.metadata

    assert metadata.name == "LENS_MAKER_EQUATION"
    assert metadata.category == "optics"
    assert len(metadata.arguments) == 3

    result = formula.build("1.5", "10", "-10")
    assert result == "of:=1/((1.5-1)*(1/10-1/-10))"


def test_magnification_lens_formula() -> None:
    """Test MAGNIFICATION_LENS formula."""
    formula = MagnificationLensFormula()
    metadata = formula.metadata

    assert metadata.name == "MAGNIFICATION_LENS"
    assert metadata.category == "optics"
    assert len(metadata.arguments) == 2

    result = formula.build("20", "10")
    assert result == "of:=-20/10"


def test_bragg_law_formula() -> None:
    """Test BRAGG_LAW formula."""
    formula = BraggLawFormula()
    metadata = formula.metadata

    assert metadata.name == "BRAGG_LAW"
    assert metadata.category == "optics"
    assert len(metadata.arguments) == 3

    result = formula.build("1", "0.154", "30")
    assert "SIN" in result
    assert "RADIANS" in result
    assert result.startswith("of:=")


def test_thin_film_interference_formula() -> None:
    """Test THIN_FILM_INTERFERENCE formula."""
    formula = ThinFilmInterferenceFormula()
    metadata = formula.metadata

    assert metadata.name == "THIN_FILM_INTERFERENCE"
    assert metadata.category == "optics"
    assert len(metadata.arguments) == 4

    # Test with defaults
    result = formula.build("1.5", "100")
    assert "COS" in result
    assert result.startswith("of:=")

    # Test with all parameters
    result = formula.build("1.5", "100", "0", "1")
    assert result == "of:=2*1.5*100*COS(RADIANS(0))/1"


def test_diffraction_grating_formula() -> None:
    """Test DIFFRACTION_GRATING formula."""
    formula = DiffractionGratingFormula()
    metadata = formula.metadata

    assert metadata.name == "DIFFRACTION_GRATING"
    assert metadata.category == "optics"
    assert len(metadata.arguments) == 3

    result = formula.build("1000", "30", "1")
    assert result == "of:=1000*SIN(RADIANS(30))/1"


# ============================================================================
# Quantum Mechanics Formula Tests
# ============================================================================


def test_planck_energy_formula() -> None:
    """Test PLANCK_ENERGY formula."""
    formula = PlanckEnergyFormula()
    metadata = formula.metadata

    assert metadata.name == "PLANCK_ENERGY"
    assert metadata.category == "quantum"
    assert len(metadata.arguments) == 2

    result = formula.build("5e14")
    assert "6.626e-34" in result
    assert result.startswith("of:=")


def test_de_broglie_wavelength_formula() -> None:
    """Test DE_BROGLIE_WAVELENGTH formula."""
    formula = DeBroglieWavelengthFormula()
    metadata = formula.metadata

    assert metadata.name == "DE_BROGLIE_WAVELENGTH"
    assert metadata.category == "quantum"
    assert len(metadata.arguments) == 2

    result = formula.build("1e-24")
    assert "6.626e-34" in result
    assert result.startswith("of:=")


def test_heisenberg_uncertainty_formula() -> None:
    """Test HEISENBERG_UNCERTAINTY formula."""
    formula = HeisenbergUncertaintyFormula()
    metadata = formula.metadata

    assert metadata.name == "HEISENBERG_UNCERTAINTY"
    assert metadata.category == "quantum"
    assert len(metadata.arguments) == 2

    result = formula.build("1e-10")
    assert "1.055e-34" in result
    assert result.startswith("of:=")


def test_photoelectric_effect_formula() -> None:
    """Test PHOTOELECTRIC_EFFECT formula."""
    formula = PhotoelectricEffectFormula()
    metadata = formula.metadata

    assert metadata.name == "PHOTOELECTRIC_EFFECT"
    assert metadata.category == "quantum"
    assert len(metadata.arguments) == 3

    result = formula.build("5e14", "2e-19")
    assert "6.626e-34" in result
    assert result.startswith("of:=")


def test_bohr_radius_formula() -> None:
    """Test BOHR_RADIUS formula."""
    formula = BohrRadiusFormula()
    metadata = formula.metadata

    assert metadata.name == "BOHR_RADIUS"
    assert metadata.category == "quantum"
    assert len(metadata.arguments) == 2

    result = formula.build("2")
    assert result == "of:=2^2*5.29e-11"


def test_rydberg_formula_formula() -> None:
    """Test RYDBERG_FORMULA formula."""
    formula = RydbergFormulaFormula()
    metadata = formula.metadata

    assert metadata.name == "RYDBERG_FORMULA"
    assert metadata.category == "quantum"
    assert len(metadata.arguments) == 3

    result = formula.build("1", "2")
    assert "1.097" in result or "1097" in result  # Accept various float formats
    assert result.startswith("of:=")


# ============================================================================
# Validation Tests
# ============================================================================


def test_formula_validation_too_few_args() -> None:
    """Test formula validation with too few arguments."""
    formula = NewtonSecondLawFormula()

    with pytest.raises(ValueError, match="at least 2 arguments"):
        formula.build("10")


def test_formula_validation_too_many_args() -> None:
    """Test formula validation with too many arguments."""
    formula = MomentumFormula()

    with pytest.raises(ValueError, match="at most 2 arguments"):
        formula.build("10", "5", "extra")


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_speed_of_light() -> None:
    """Test speed_of_light constant."""
    c = speed_of_light()
    assert c == 299792458.0
    assert isinstance(c, float)


def test_planck_constant_func() -> None:
    """Test planck_constant function."""
    h = planck_constant()
    assert h == 6.62607015e-34
    assert isinstance(h, float)


def test_reduced_planck_constant_func() -> None:
    """Test reduced_planck_constant function."""
    hbar = reduced_planck_constant()
    assert hbar > 0
    assert hbar < planck_constant()


def test_gravitational_constant_func() -> None:
    """Test gravitational_constant function."""
    g = gravitational_constant()
    assert g == 6.6743e-11
    assert isinstance(g, float)


def test_electron_mass_func() -> None:
    """Test electron_mass function."""
    me = electron_mass()
    assert me == 9.1093837015e-31
    assert isinstance(me, float)


def test_proton_mass_func() -> None:
    """Test proton_mass function."""
    mp = proton_mass()
    assert mp == 1.67262192369e-27
    assert isinstance(mp, float)
    assert mp > electron_mass()


def test_elementary_charge_func() -> None:
    """Test elementary_charge function."""
    e = elementary_charge()
    assert e == 1.602176634e-19
    assert isinstance(e, float)


def test_convert_ev_to_joules() -> None:
    """Test convert_ev_to_joules function."""
    energy_j = convert_ev_to_joules(1.0)
    assert energy_j == elementary_charge()


def test_convert_joules_to_ev() -> None:
    """Test convert_joules_to_ev function."""
    energy_ev = convert_joules_to_ev(elementary_charge())
    assert abs(energy_ev - 1.0) < 1e-10


def test_wavelength_to_frequency() -> None:
    """Test wavelength_to_frequency function."""
    freq = wavelength_to_frequency(500e-9)
    assert freq > 0
    assert isinstance(freq, float)


def test_frequency_to_wavelength() -> None:
    """Test frequency_to_wavelength function."""
    wavelength = frequency_to_wavelength(5e14)
    assert wavelength > 0
    assert isinstance(wavelength, float)


def test_wavelength_frequency_roundtrip() -> None:
    """Test wavelength <-> frequency conversion roundtrip."""
    original_wavelength = 500e-9
    freq = wavelength_to_frequency(original_wavelength)
    result_wavelength = frequency_to_wavelength(freq)
    assert abs(result_wavelength - original_wavelength) < 1e-15


def test_calculate_escape_velocity() -> None:
    """Test calculate_escape_velocity function."""
    # Earth's mass and radius (approximate)
    v_escape = calculate_escape_velocity(5.972e24, 6.371e6)
    assert v_escape > 11000  # Should be around 11.2 km/s
    assert v_escape < 12000


def test_calculate_schwarzschild_radius() -> None:
    """Test calculate_schwarzschild_radius function."""
    # Sun's mass
    r_s = calculate_schwarzschild_radius(1.989e30)
    assert r_s > 2900  # Should be around 3 km
    assert r_s < 3000


def test_degrees_to_radians_func() -> None:
    """Test degrees_to_radians function."""
    import math

    radians = degrees_to_radians(180)
    assert abs(radians - math.pi) < 1e-10


def test_radians_to_degrees_func() -> None:
    """Test radians_to_degrees function."""
    import math

    degrees = radians_to_degrees(math.pi)
    assert abs(degrees - 180.0) < 1e-10


def test_angle_conversion_roundtrip() -> None:
    """Test angle conversion roundtrip."""
    original_degrees = 45.0
    radians = degrees_to_radians(original_degrees)
    result_degrees = radians_to_degrees(radians)
    assert abs(result_degrees - original_degrees) < 1e-10


# ============================================================================
# Integration Tests
# ============================================================================


def test_all_formulas_have_metadata() -> None:
    """Test that all formulas have proper metadata."""
    from typing import Any

    formulas: list[type[Any]] = [
        NewtonSecondLawFormula,
        KineticEnergyFormula,
        PotentialEnergyFormula,
        WorkEnergyFormula,
        MomentumFormula,
        AngularMomentumFormula,
        CentripetalForceFormula,
        CoulombLawFormula,
        ElectricFieldFormula,
        MagneticForceFormula,
        FaradayLawFormula,
        LorentzForceFormula,
        PoyntingVectorFormula,
        SnellsLawFormula,
        LensMakerEquationFormula,
        MagnificationLensFormula,
        BraggLawFormula,
        ThinFilmInterferenceFormula,
        DiffractionGratingFormula,
        PlanckEnergyFormula,
        DeBroglieWavelengthFormula,
        HeisenbergUncertaintyFormula,
        PhotoelectricEffectFormula,
        BohrRadiusFormula,
        RydbergFormulaFormula,
    ]

    for formula_class in formulas:
        formula = formula_class()
        metadata = formula.metadata

        assert metadata.name
        assert metadata.category
        assert metadata.description
        assert len(metadata.arguments) > 0
        assert metadata.return_type
        assert len(metadata.examples) > 0


def test_all_formulas_produce_valid_output() -> None:
    """Test that all formulas produce valid ODF output."""
    test_cases = [
        (NewtonSecondLawFormula, ["10", "2"]),
        (KineticEnergyFormula, ["10", "5"]),
        (PotentialEnergyFormula, ["10", "5"]),
        (WorkEnergyFormula, ["100", "5"]),
        (MomentumFormula, ["10", "5"]),
        (AngularMomentumFormula, ["5", "10"]),
        (CentripetalForceFormula, ["10", "5", "2"]),
        (CoulombLawFormula, ["1e-6", "2e-6", "0.1"]),
        (ElectricFieldFormula, ["100", "1e-6"]),
        (MagneticForceFormula, ["1e-6", "1e6", "0.5"]),
        (FaradayLawFormula, ["100", "0.5", "0.1"]),
        (LorentzForceFormula, ["1e-6", "1000", "1e5", "0.5"]),
        (PoyntingVectorFormula, ["100", "0.1"]),
        (SnellsLawFormula, ["1.0", "30", "1.5"]),
        (LensMakerEquationFormula, ["1.5", "10", "-10"]),
        (MagnificationLensFormula, ["20", "10"]),
        (BraggLawFormula, ["1", "0.154", "30"]),
        (ThinFilmInterferenceFormula, ["1.5", "100"]),
        (DiffractionGratingFormula, ["1000", "30"]),
        (PlanckEnergyFormula, ["5e14"]),
        (DeBroglieWavelengthFormula, ["1e-24"]),
        (HeisenbergUncertaintyFormula, ["1e-10"]),
        (PhotoelectricEffectFormula, ["5e14", "2e-19"]),
        (BohrRadiusFormula, ["2"]),
        (RydbergFormulaFormula, ["1", "2"]),
    ]

    for formula_class, args in test_cases:
        formula = formula_class()
        result = formula.build(*args)

        assert result.startswith("of:=")
        assert len(result) > 4
