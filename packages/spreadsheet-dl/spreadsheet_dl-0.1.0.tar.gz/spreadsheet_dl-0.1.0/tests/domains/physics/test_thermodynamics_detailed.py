"""Tests for Physics thermodynamics and related formulas.

Comprehensive tests for thermodynamics-related physics formulas
including energy, work, heat transfer calculations.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.physics import (
    AngularMomentumFormula,
    CentripetalForceFormula,
    KineticEnergyFormula,
    MomentumFormula,
    NewtonSecondLawFormula,
    PhysicsDomainPlugin,
    PotentialEnergyFormula,
    WorkEnergyFormula,
)
from spreadsheet_dl.domains.physics.utils import (
    convert_ev_to_joules,
    convert_joules_to_ev,
    degrees_to_radians,
    electron_mass,
    elementary_charge,
    gravitational_constant,
    planck_constant,
    proton_mass,
    radians_to_degrees,
    reduced_planck_constant,
    speed_of_light,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


# ============================================================================
# Energy Formula Tests
# ============================================================================


class TestKineticEnergyCalculations:
    """Test kinetic energy calculations."""

    def test_kinetic_energy_standard(self) -> None:
        """Test standard kinetic energy calculation."""
        formula = KineticEnergyFormula()
        result = formula.build("10", "5")  # mass=10, velocity=5
        assert result == "of:=0.5*10*5^2"

    def test_kinetic_energy_high_velocity(self) -> None:
        """Test kinetic energy at high velocity."""
        formula = KineticEnergyFormula()
        result = formula.build("1", "1000")
        assert "1000" in result
        assert "^2" in result

    def test_kinetic_energy_heavy_object(self) -> None:
        """Test kinetic energy of heavy object."""
        formula = KineticEnergyFormula()
        result = formula.build("1000", "10")
        assert "1000" in result

    def test_kinetic_energy_cell_references(self) -> None:
        """Test kinetic energy with cell references."""
        formula = KineticEnergyFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result
        assert "B1" in result


class TestPotentialEnergyCalculations:
    """Test potential energy calculations."""

    def test_potential_energy_default_gravity(self) -> None:
        """Test potential energy with default gravity."""
        formula = PotentialEnergyFormula()
        result = formula.build("10", "5")  # mass=10, height=5
        assert result == "of:=10*9.81*5"

    def test_potential_energy_custom_gravity(self) -> None:
        """Test potential energy with custom gravity."""
        formula = PotentialEnergyFormula()
        result = formula.build("10", "5", "10")  # g=10
        assert result == "of:=10*10*5"

    def test_potential_energy_moon_gravity(self) -> None:
        """Test potential energy with Moon's gravity."""
        formula = PotentialEnergyFormula()
        result = formula.build("100", "10", "1.62")
        assert "1.62" in result

    def test_potential_energy_cell_references(self) -> None:
        """Test potential energy with cell references."""
        formula = PotentialEnergyFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result
        assert "B1" in result


class TestWorkEnergyCalculations:
    """Test work-energy calculations."""

    def test_work_energy_horizontal_force(self) -> None:
        """Test work with horizontal force (angle=0)."""
        formula = WorkEnergyFormula()
        result = formula.build("100", "5", "0")
        assert "COS" in result
        assert "RADIANS" in result
        assert result.startswith("of:=")

    def test_work_energy_perpendicular_force(self) -> None:
        """Test work with perpendicular force (angle=90)."""
        formula = WorkEnergyFormula()
        result = formula.build("100", "5", "90")
        assert "90" in result

    def test_work_energy_angled_force(self) -> None:
        """Test work with angled force (angle=45)."""
        formula = WorkEnergyFormula()
        result = formula.build("50", "10", "45")
        assert "45" in result

    def test_work_energy_cell_references(self) -> None:
        """Test work-energy with cell references."""
        formula = WorkEnergyFormula()
        result = formula.build("A1", "B1", "C1")
        assert "A1" in result


# ============================================================================
# Mechanics Formula Tests
# ============================================================================


class TestNewtonSecondLawCalculations:
    """Test Newton's second law calculations."""

    def test_newton_second_law_standard(self) -> None:
        """Test standard F=ma calculation."""
        formula = NewtonSecondLawFormula()
        result = formula.build("10", "2")  # mass=10, accel=2
        assert result == "of:=10*2"

    def test_newton_second_law_high_acceleration(self) -> None:
        """Test F=ma with high acceleration."""
        formula = NewtonSecondLawFormula()
        result = formula.build("5", "100")
        assert result == "of:=5*100"

    def test_newton_second_law_cell_references(self) -> None:
        """Test F=ma with cell references."""
        formula = NewtonSecondLawFormula()
        result = formula.build("A1", "B1")
        assert result == "of:=A1*B1"


class TestMomentumCalculations:
    """Test momentum calculations."""

    def test_momentum_standard(self) -> None:
        """Test standard p=mv calculation."""
        formula = MomentumFormula()
        result = formula.build("10", "5")
        assert result == "of:=10*5"

    def test_momentum_high_velocity(self) -> None:
        """Test momentum at high velocity."""
        formula = MomentumFormula()
        result = formula.build("1", "1e6")
        assert result == "of:=1*1e6"

    def test_momentum_cell_references(self) -> None:
        """Test momentum with cell references."""
        formula = MomentumFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result


class TestAngularMomentumCalculations:
    """Test angular momentum calculations."""

    def test_angular_momentum_standard(self) -> None:
        """Test standard L=Iw calculation."""
        formula = AngularMomentumFormula()
        result = formula.build("5", "10")  # I=5, omega=10
        assert result == "of:=5*10"

    def test_angular_momentum_high_inertia(self) -> None:
        """Test angular momentum with high moment of inertia."""
        formula = AngularMomentumFormula()
        result = formula.build("1000", "2")
        assert result == "of:=1000*2"

    def test_angular_momentum_cell_references(self) -> None:
        """Test angular momentum with cell references."""
        formula = AngularMomentumFormula()
        result = formula.build("A1", "B1")
        assert "A1" in result


class TestCentripetalForceCalculations:
    """Test centripetal force calculations."""

    def test_centripetal_force_standard(self) -> None:
        """Test standard centripetal force calculation."""
        formula = CentripetalForceFormula()
        result = formula.build("10", "5", "2")  # m=10, v=5, r=2
        assert result == "of:=10*5^2/2"

    def test_centripetal_force_high_velocity(self) -> None:
        """Test centripetal force at high velocity."""
        formula = CentripetalForceFormula()
        result = formula.build("1", "100", "10")
        assert "100" in result
        assert "^2" in result

    def test_centripetal_force_small_radius(self) -> None:
        """Test centripetal force with small radius."""
        formula = CentripetalForceFormula()
        result = formula.build("5", "10", "0.5")
        assert "0.5" in result


# ============================================================================
# Physical Constants Tests
# ============================================================================


class TestPhysicalConstants:
    """Test physical constant functions."""

    def test_speed_of_light_value(self) -> None:
        """Test speed of light constant."""
        c = speed_of_light()
        assert c == 299792458.0
        assert isinstance(c, float)

    def test_planck_constant_value(self) -> None:
        """Test Planck constant."""
        h = planck_constant()
        assert h == 6.62607015e-34
        assert isinstance(h, float)

    def test_reduced_planck_constant_value(self) -> None:
        """Test reduced Planck constant."""
        hbar = reduced_planck_constant()
        assert hbar > 0
        assert hbar < planck_constant()

    def test_gravitational_constant_value(self) -> None:
        """Test gravitational constant."""
        g = gravitational_constant()
        assert g == 6.6743e-11
        assert isinstance(g, float)

    def test_electron_mass_value(self) -> None:
        """Test electron mass."""
        me = electron_mass()
        assert me == 9.1093837015e-31
        assert isinstance(me, float)

    def test_proton_mass_value(self) -> None:
        """Test proton mass."""
        mp = proton_mass()
        assert mp == 1.67262192369e-27
        assert mp > electron_mass()

    def test_elementary_charge_value(self) -> None:
        """Test elementary charge."""
        e = elementary_charge()
        assert e == 1.602176634e-19
        assert isinstance(e, float)


# ============================================================================
# Energy Conversion Tests
# ============================================================================


class TestEnergyConversions:
    """Test energy unit conversions."""

    def test_ev_to_joules_one_ev(self) -> None:
        """Test converting 1 eV to Joules."""
        energy_j = convert_ev_to_joules(1.0)
        assert energy_j == elementary_charge()

    def test_ev_to_joules_multiple(self) -> None:
        """Test converting multiple eV to Joules."""
        energy_j = convert_ev_to_joules(10.0)
        assert abs(energy_j - 10 * elementary_charge()) < 1e-25

    def test_joules_to_ev_one_joule(self) -> None:
        """Test converting Joules to eV."""
        energy_ev = convert_joules_to_ev(elementary_charge())
        assert abs(energy_ev - 1.0) < 1e-10

    def test_joules_to_ev_roundtrip(self) -> None:
        """Test roundtrip eV conversion."""
        original = 5.0
        joules = convert_ev_to_joules(original)
        result = convert_joules_to_ev(joules)
        assert abs(result - original) < 1e-10


# ============================================================================
# Angle Conversion Tests
# ============================================================================


class TestAngleConversions:
    """Test angle unit conversions."""

    def test_degrees_to_radians_180(self) -> None:
        """Test converting 180 degrees to radians."""
        import math

        radians = degrees_to_radians(180)
        assert abs(radians - math.pi) < 1e-10

    def test_degrees_to_radians_90(self) -> None:
        """Test converting 90 degrees to radians."""
        import math

        radians = degrees_to_radians(90)
        assert abs(radians - math.pi / 2) < 1e-10

    def test_degrees_to_radians_360(self) -> None:
        """Test converting 360 degrees to radians."""
        import math

        radians = degrees_to_radians(360)
        assert abs(radians - 2 * math.pi) < 1e-10

    def test_radians_to_degrees_pi(self) -> None:
        """Test converting pi radians to degrees."""
        import math

        degrees = radians_to_degrees(math.pi)
        assert abs(degrees - 180.0) < 1e-10

    def test_radians_to_degrees_half_pi(self) -> None:
        """Test converting pi/2 radians to degrees."""
        import math

        degrees = radians_to_degrees(math.pi / 2)
        assert abs(degrees - 90.0) < 1e-10

    def test_angle_conversion_roundtrip(self) -> None:
        """Test roundtrip angle conversion."""
        original = 45.0
        radians = degrees_to_radians(original)
        result = radians_to_degrees(radians)
        assert abs(result - original) < 1e-10


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestThermodynamicsEdgeCases:
    """Test edge cases in thermodynamics formulas."""

    def test_newton_second_law_validates_arguments(self) -> None:
        """Test Newton's law argument validation."""
        formula = NewtonSecondLawFormula()
        with pytest.raises(ValueError, match="at least 2 arguments"):
            formula.build("10")

    def test_momentum_validates_arguments(self) -> None:
        """Test momentum argument validation."""
        formula = MomentumFormula()
        with pytest.raises(ValueError, match="at most 2 arguments"):
            formula.build("10", "5", "extra")

    def test_kinetic_energy_validates_arguments(self) -> None:
        """Test kinetic energy argument validation."""
        formula = KineticEnergyFormula()
        with pytest.raises(ValueError, match="at least 2 arguments"):
            formula.build("10")


# ============================================================================
# Integration Tests
# ============================================================================


class TestThermodynamicsIntegration:
    """Integration tests for thermodynamics formulas with plugin."""

    def test_plugin_contains_mechanics_formulas(self) -> None:
        """Test plugin has mechanics formulas."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        assert plugin.get_formula("NEWTON_SECOND_LAW") is not None
        assert plugin.get_formula("KINETIC_ENERGY") is not None
        assert plugin.get_formula("POTENTIAL_ENERGY") is not None
        assert plugin.get_formula("WORK_ENERGY") is not None
        assert plugin.get_formula("MOMENTUM") is not None
        assert plugin.get_formula("ANGULAR_MOMENTUM") is not None
        assert plugin.get_formula("CENTRIPETAL_FORCE") is not None

    def test_all_mechanics_formulas_produce_odf(self) -> None:
        """Test all mechanics formulas produce valid ODF output."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        test_cases = [
            ("NEWTON_SECOND_LAW", ("10", "2")),
            ("KINETIC_ENERGY", ("10", "5")),
            ("POTENTIAL_ENERGY", ("10", "5")),
            ("WORK_ENERGY", ("100", "5", "0")),
            ("MOMENTUM", ("10", "5")),
            ("ANGULAR_MOMENTUM", ("5", "10")),
            ("CENTRIPETAL_FORCE", ("10", "5", "2")),
        ]

        for formula_name, args in test_cases:
            formula_class = plugin.get_formula(formula_name)
            assert formula_class is not None, f"Formula {formula_name} not found"
            formula = formula_class()
            result = formula.build(*args)
            assert result.startswith("of:="), (
                f"{formula_name} should return ODF formula"
            )

    def test_plugin_total_formula_count(self) -> None:
        """Test plugin has expected number of formulas."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        # Physics plugin should have 50 formulas total
        assert len(plugin.list_formulas()) == 50
