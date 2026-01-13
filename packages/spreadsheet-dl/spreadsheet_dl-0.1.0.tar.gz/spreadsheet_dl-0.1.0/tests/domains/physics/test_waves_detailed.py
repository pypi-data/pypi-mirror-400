"""Tests for Physics waves and optics formulas.

Comprehensive tests for waves, optics, and quantum mechanics formulas
including electromagnetic waves, diffraction, and quantum effects.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.physics import (
    BohrRadiusFormula,
    BraggLawFormula,
    CoulombLawFormula,
    DeBroglieWavelengthFormula,
    DiffractionGratingFormula,
    ElectricFieldFormula,
    FaradayLawFormula,
    HeisenbergUncertaintyFormula,
    LensMakerEquationFormula,
    LorentzForceFormula,
    MagneticForceFormula,
    MagnificationLensFormula,
    PhotoelectricEffectFormula,
    PhysicsDomainPlugin,
    PlanckEnergyFormula,
    PoyntingVectorFormula,
    RydbergFormulaFormula,
    SnellsLawFormula,
    ThinFilmInterferenceFormula,
)
from spreadsheet_dl.domains.physics.utils import (
    calculate_escape_velocity,
    calculate_schwarzschild_radius,
    frequency_to_wavelength,
    wavelength_to_frequency,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


# ============================================================================
# Optics Formula Tests
# ============================================================================


class TestSnellsLawCalculations:
    """Test Snell's law refraction calculations."""

    def test_snells_law_air_to_glass(self) -> None:
        """Test refraction from air to glass."""
        formula = SnellsLawFormula()
        result = formula.build("1.0", "30", "1.5")
        assert "ASIN" in result
        assert "SIN" in result
        assert "RADIANS" in result
        assert "DEGREES" in result
        assert result.startswith("of:=")

    def test_snells_law_glass_to_air(self) -> None:
        """Test refraction from glass to air."""
        formula = SnellsLawFormula()
        result = formula.build("1.5", "20", "1.0")
        assert result.startswith("of:=")

    def test_snells_law_water_to_glass(self) -> None:
        """Test refraction from water to glass."""
        formula = SnellsLawFormula()
        result = formula.build("1.33", "45", "1.5")
        assert "1.33" in result

    def test_snells_law_cell_references(self) -> None:
        """Test Snell's law with cell references."""
        formula = SnellsLawFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result


class TestLensMakerEquationCalculations:
    """Test lens maker equation calculations."""

    def test_lens_maker_convex_lens(self) -> None:
        """Test lens maker equation for convex lens."""
        formula = LensMakerEquationFormula()
        result = formula.build("1.5", "10", "-10")
        assert result == "of:=1/((1.5-1)*(1/10-1/-10))"

    def test_lens_maker_plano_convex(self) -> None:
        """Test lens maker equation for plano-convex lens."""
        formula = LensMakerEquationFormula()
        result = formula.build("1.5", "20", "1e10")  # R2 ~ infinity
        assert "1.5" in result

    def test_lens_maker_cell_references(self) -> None:
        """Test lens maker with cell references."""
        formula = LensMakerEquationFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result


class TestMagnificationLensCalculations:
    """Test lens magnification calculations."""

    def test_magnification_lens_standard(self) -> None:
        """Test standard lens magnification."""
        formula = MagnificationLensFormula()
        result = formula.build("20", "10")  # di=20, do=10
        assert result == "of:=-20/10"

    def test_magnification_lens_virtual_image(self) -> None:
        """Test magnification for virtual image."""
        formula = MagnificationLensFormula()
        result = formula.build("-15", "10")
        assert "-15" in result

    def test_magnification_lens_cell_references(self) -> None:
        """Test magnification with cell references."""
        formula = MagnificationLensFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result


class TestBraggLawCalculations:
    """Test Bragg's law X-ray diffraction calculations."""

    def test_bragg_law_first_order(self) -> None:
        """Test Bragg's law for first-order diffraction."""
        formula = BraggLawFormula()
        result = formula.build("1", "0.154", "30")  # n=1, d=0.154nm, theta=30
        assert "SIN" in result
        assert "RADIANS" in result
        assert result.startswith("of:=")

    def test_bragg_law_second_order(self) -> None:
        """Test Bragg's law for second-order diffraction."""
        formula = BraggLawFormula()
        result = formula.build("2", "0.154", "45")
        assert "2" in result

    def test_bragg_law_cell_references(self) -> None:
        """Test Bragg's law with cell references."""
        formula = BraggLawFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result


class TestThinFilmInterferenceCalculations:
    """Test thin film interference calculations."""

    def test_thin_film_normal_incidence(self) -> None:
        """Test thin film interference at normal incidence."""
        formula = ThinFilmInterferenceFormula()
        result = formula.build("1.5", "100", "0", "1")
        assert result == "of:=2*1.5*100*COS(RADIANS(0))/1"

    def test_thin_film_default_parameters(self) -> None:
        """Test thin film with default parameters."""
        formula = ThinFilmInterferenceFormula()
        result = formula.build("1.5", "100")
        assert "COS" in result
        assert result.startswith("of:=")

    def test_thin_film_angled_incidence(self) -> None:
        """Test thin film at angled incidence."""
        formula = ThinFilmInterferenceFormula()
        result = formula.build("1.33", "200", "30", "2")
        assert "30" in result


class TestDiffractionGratingCalculations:
    """Test diffraction grating calculations."""

    def test_diffraction_grating_first_order(self) -> None:
        """Test diffraction grating first-order maximum."""
        formula = DiffractionGratingFormula()
        result = formula.build("1000", "30", "1")  # d=1000nm, theta=30, m=1
        assert result == "of:=1000*SIN(RADIANS(30))/1"

    def test_diffraction_grating_second_order(self) -> None:
        """Test diffraction grating second-order maximum."""
        formula = DiffractionGratingFormula()
        result = formula.build("500", "45", "2")
        assert "/2" in result

    def test_diffraction_grating_default_order(self) -> None:
        """Test diffraction grating with default order."""
        formula = DiffractionGratingFormula()
        result = formula.build("1000", "30")
        assert "SIN" in result


# ============================================================================
# Electromagnetism Formula Tests
# ============================================================================


class TestCoulombLawCalculations:
    """Test Coulomb's law calculations."""

    def test_coulomb_law_standard(self) -> None:
        """Test standard Coulomb's law calculation."""
        formula = CoulombLawFormula()
        result = formula.build("1e-6", "2e-6", "0.1")
        assert "8.99" in result or "899" in result
        assert result.startswith("of:=")

    def test_coulomb_law_point_charges(self) -> None:
        """Test Coulomb's law for point charges."""
        formula = CoulombLawFormula()
        result = formula.build("1e-9", "1e-9", "0.01")
        assert result.startswith("of:=")

    def test_coulomb_law_cell_references(self) -> None:
        """Test Coulomb's law with cell references."""
        formula = CoulombLawFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result


class TestElectricFieldCalculations:
    """Test electric field calculations."""

    def test_electric_field_standard(self) -> None:
        """Test standard electric field calculation."""
        formula = ElectricFieldFormula()
        result = formula.build("100", "1e-6")  # V=100, q=1uC
        assert result == "of:=100/1e-6"

    def test_electric_field_high_voltage(self) -> None:
        """Test electric field at high voltage."""
        formula = ElectricFieldFormula()
        result = formula.build("10000", "0.001")
        assert "10000" in result


class TestMagneticForceCalculations:
    """Test magnetic force calculations."""

    def test_magnetic_force_perpendicular(self) -> None:
        """Test magnetic force at perpendicular angle."""
        formula = MagneticForceFormula()
        result = formula.build("1e-6", "1e6", "0.5", "90")
        assert "SIN" in result
        assert "RADIANS" in result
        assert result.startswith("of:=")

    def test_magnetic_force_parallel(self) -> None:
        """Test magnetic force at parallel angle (zero)."""
        formula = MagneticForceFormula()
        result = formula.build("1e-6", "1e6", "0.5", "0")
        assert "0" in result


class TestFaradayLawCalculations:
    """Test Faraday's law of induction calculations."""

    def test_faraday_law_standard(self) -> None:
        """Test standard Faraday's law calculation."""
        formula = FaradayLawFormula()
        result = formula.build("100", "0.5", "0.1")  # N=100, dPhi=0.5, dt=0.1
        assert result == "of:=100*0.5/0.1"

    def test_faraday_law_fast_change(self) -> None:
        """Test Faraday's law with fast flux change."""
        formula = FaradayLawFormula()
        result = formula.build("50", "1.0", "0.01")
        assert "0.01" in result


class TestLorentzForceCalculations:
    """Test Lorentz force calculations."""

    def test_lorentz_force_standard(self) -> None:
        """Test standard Lorentz force calculation."""
        formula = LorentzForceFormula()
        result = formula.build("1e-6", "1000", "1e5", "0.5")
        assert result == "of:=1e-6*(1000+1e5*0.5)"

    def test_lorentz_force_electric_only(self) -> None:
        """Test Lorentz force with only electric component."""
        formula = LorentzForceFormula()
        result = formula.build("1e-6", "5000", "0", "0")
        assert "5000" in result


class TestPoyntingVectorCalculations:
    """Test Poynting vector calculations."""

    def test_poynting_vector_standard(self) -> None:
        """Test standard Poynting vector calculation."""
        formula = PoyntingVectorFormula()
        result = formula.build("100", "0.1")  # E=100, B=0.1
        assert result == "of:=100*0.1"


# ============================================================================
# Quantum Mechanics Formula Tests
# ============================================================================


class TestPlanckEnergyCalculations:
    """Test Planck energy calculations."""

    def test_planck_energy_visible_light(self) -> None:
        """Test Planck energy for visible light."""
        formula = PlanckEnergyFormula()
        result = formula.build("5e14")  # 500 THz (green light)
        assert "6.626e-34" in result
        assert result.startswith("of:=")

    def test_planck_energy_xray(self) -> None:
        """Test Planck energy for X-rays."""
        formula = PlanckEnergyFormula()
        result = formula.build("1e18")  # X-ray frequency
        assert result.startswith("of:=")


class TestDeBroglieWavelengthCalculations:
    """Test de Broglie wavelength calculations."""

    def test_de_broglie_electron(self) -> None:
        """Test de Broglie wavelength for electron."""
        formula = DeBroglieWavelengthFormula()
        result = formula.build("1e-24")  # Typical electron momentum
        assert "6.626e-34" in result
        assert result.startswith("of:=")

    def test_de_broglie_high_momentum(self) -> None:
        """Test de Broglie wavelength at high momentum."""
        formula = DeBroglieWavelengthFormula()
        result = formula.build("1e-20")
        assert result.startswith("of:=")


class TestHeisenbergUncertaintyCalculations:
    """Test Heisenberg uncertainty calculations."""

    def test_heisenberg_position_uncertainty(self) -> None:
        """Test Heisenberg uncertainty for position."""
        formula = HeisenbergUncertaintyFormula()
        result = formula.build("1e-10")  # 0.1 nm position uncertainty
        assert "1.055e-34" in result
        assert result.startswith("of:=")

    def test_heisenberg_small_uncertainty(self) -> None:
        """Test Heisenberg uncertainty with small position."""
        formula = HeisenbergUncertaintyFormula()
        result = formula.build("1e-15")  # 1 fm uncertainty
        assert result.startswith("of:=")


class TestPhotoelectricEffectCalculations:
    """Test photoelectric effect calculations."""

    def test_photoelectric_effect_standard(self) -> None:
        """Test standard photoelectric effect."""
        formula = PhotoelectricEffectFormula()
        result = formula.build("5e14", "2e-19")  # freq, work function
        assert "6.626e-34" in result
        assert result.startswith("of:=")

    def test_photoelectric_effect_high_frequency(self) -> None:
        """Test photoelectric effect at high frequency."""
        formula = PhotoelectricEffectFormula()
        result = formula.build("1e15", "3e-19")
        assert result.startswith("of:=")


class TestBohrRadiusCalculations:
    """Test Bohr radius calculations."""

    def test_bohr_radius_ground_state(self) -> None:
        """Test Bohr radius for ground state (n=1)."""
        formula = BohrRadiusFormula()
        result = formula.build("1")
        assert "5.29e-11" in result

    def test_bohr_radius_excited_state(self) -> None:
        """Test Bohr radius for excited state (n=2)."""
        formula = BohrRadiusFormula()
        result = formula.build("2")
        assert result == "of:=2^2*5.29e-11"

    def test_bohr_radius_high_n(self) -> None:
        """Test Bohr radius for high quantum number."""
        formula = BohrRadiusFormula()
        result = formula.build("5")
        assert "5" in result


class TestRydbergFormulaCalculations:
    """Test Rydberg formula calculations."""

    def test_rydberg_lyman_series(self) -> None:
        """Test Rydberg formula for Lyman series (n1=1)."""
        formula = RydbergFormulaFormula()
        result = formula.build("1", "2")  # Lyman alpha
        assert "1.097" in result or "1097" in result
        assert result.startswith("of:=")

    def test_rydberg_balmer_series(self) -> None:
        """Test Rydberg formula for Balmer series (n1=2)."""
        formula = RydbergFormulaFormula()
        result = formula.build("2", "3")  # H-alpha
        assert result.startswith("of:=")


# ============================================================================
# Wave Utility Function Tests
# ============================================================================


class TestWavelengthFrequencyConversions:
    """Test wavelength-frequency conversions."""

    def test_wavelength_to_frequency_visible(self) -> None:
        """Test wavelength to frequency for visible light."""
        freq = wavelength_to_frequency(500e-9)  # 500 nm
        assert freq > 0
        assert isinstance(freq, float)

    def test_frequency_to_wavelength_visible(self) -> None:
        """Test frequency to wavelength for visible light."""
        wavelength = frequency_to_wavelength(5e14)  # 500 THz
        assert wavelength > 0
        assert isinstance(wavelength, float)

    def test_wavelength_frequency_roundtrip(self) -> None:
        """Test wavelength-frequency roundtrip conversion."""
        original = 500e-9
        freq = wavelength_to_frequency(original)
        result = frequency_to_wavelength(freq)
        assert abs(result - original) < 1e-15


class TestAstrophysicsUtilities:
    """Test astrophysics utility functions."""

    def test_escape_velocity_earth(self) -> None:
        """Test escape velocity for Earth."""
        v_escape = calculate_escape_velocity(5.972e24, 6.371e6)
        assert v_escape > 11000  # ~11.2 km/s
        assert v_escape < 12000

    def test_escape_velocity_moon(self) -> None:
        """Test escape velocity for Moon."""
        v_escape = calculate_escape_velocity(7.342e22, 1.737e6)
        assert v_escape > 2000  # ~2.4 km/s
        assert v_escape < 3000

    def test_schwarzschild_radius_sun(self) -> None:
        """Test Schwarzschild radius for Sun."""
        r_s = calculate_schwarzschild_radius(1.989e30)
        assert r_s > 2900  # ~3 km
        assert r_s < 3000

    def test_schwarzschild_radius_earth_mass(self) -> None:
        """Test Schwarzschild radius for Earth mass."""
        r_s = calculate_schwarzschild_radius(5.972e24)
        assert r_s > 0
        assert r_s < 0.01  # ~9 mm


# ============================================================================
# Integration Tests
# ============================================================================


class TestWavesIntegration:
    """Integration tests for waves and optics formulas with plugin."""

    def test_plugin_contains_optics_formulas(self) -> None:
        """Test plugin has optics formulas."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("SNELLS_LAW") is not None
        assert plugin.get_formula("LENS_MAKER_EQUATION") is not None
        assert plugin.get_formula("MAGNIFICATION_LENS") is not None
        assert plugin.get_formula("BRAGG_LAW") is not None
        assert plugin.get_formula("THIN_FILM_INTERFERENCE") is not None
        assert plugin.get_formula("DIFFRACTION_GRATING") is not None

    def test_plugin_contains_em_formulas(self) -> None:
        """Test plugin has electromagnetism formulas."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("COULOMB_LAW") is not None
        assert plugin.get_formula("ELECTRIC_FIELD") is not None
        assert plugin.get_formula("MAGNETIC_FORCE") is not None
        assert plugin.get_formula("FARADAY_LAW") is not None
        assert plugin.get_formula("LORENTZ_FORCE") is not None
        assert plugin.get_formula("POYNTING_VECTOR") is not None

    def test_plugin_contains_quantum_formulas(self) -> None:
        """Test plugin has quantum formulas."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("PLANCK_ENERGY") is not None
        assert plugin.get_formula("DE_BROGLIE_WAVELENGTH") is not None
        assert plugin.get_formula("HEISENBERG_UNCERTAINTY") is not None
        assert plugin.get_formula("PHOTOELECTRIC_EFFECT") is not None
        assert plugin.get_formula("BOHR_RADIUS") is not None
        assert plugin.get_formula("RYDBERG_FORMULA") is not None

    def test_all_optics_formulas_produce_odf(self) -> None:
        """Test all optics formulas produce valid ODF output."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        test_cases = [
            ("SNELLS_LAW", ("1.0", "30", "1.5")),
            ("LENS_MAKER_EQUATION", ("1.5", "10", "-10")),
            ("MAGNIFICATION_LENS", ("20", "10")),
            ("BRAGG_LAW", ("1", "0.154", "30")),
            ("THIN_FILM_INTERFERENCE", ("1.5", "100")),
            ("DIFFRACTION_GRATING", ("1000", "30")),
        ]

        for formula_name, args in test_cases:
            formula_class = plugin.get_formula(formula_name)
            assert formula_class is not None, f"Formula {formula_name} not found"
            formula = formula_class()
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula_name} should return ODF formula"
            )

    def test_all_quantum_formulas_produce_odf(self) -> None:
        """Test all quantum formulas produce valid ODF output."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        test_cases = [
            ("PLANCK_ENERGY", ("5e14",)),
            ("DE_BROGLIE_WAVELENGTH", ("1e-24",)),
            ("HEISENBERG_UNCERTAINTY", ("1e-10",)),
            ("PHOTOELECTRIC_EFFECT", ("5e14", "2e-19")),
            ("BOHR_RADIUS", ("2",)),
            ("RYDBERG_FORMULA", ("1", "2")),
        ]

        for formula_name, args in test_cases:
            formula_class = plugin.get_formula(formula_name)
            assert formula_class is not None, f"Formula {formula_name} not found"
            formula = formula_class()
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula_name} should return ODF formula"
            )
