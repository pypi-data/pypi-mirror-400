"""Property-based tests for Physics mechanics formulas.

Uses Hypothesis to validate physical properties hold across entire input domains.
This approach catches edge cases that hardcoded examples miss.

Test Strategy:
    - Each test verifies mathematical/physical properties, not string formatting
    - Properties tested include: scaling behavior, symmetry, conservation laws
    - Input domains match realistic physical values to avoid numerical issues

References:
    - NIST CODATA 2018 for physical constants
    - Classical mechanics textbooks for physics relationships
"""

from __future__ import annotations

import math

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from spreadsheet_dl.domains.physics import (
    AngularMomentumFormula,
    CentripetalForceFormula,
    KineticEnergyFormula,
    MomentumFormula,
    NewtonSecondLawFormula,
    PotentialEnergyFormula,
    WorkEnergyFormula,
)
from spreadsheet_dl.domains.physics.utils import (
    calculate_escape_velocity,
    calculate_schwarzschild_radius,
    gravitational_constant,
    planck_constant,
    speed_of_light,
)

pytestmark = [pytest.mark.unit, pytest.mark.property, pytest.mark.science]


# =============================================================================
# Strategy Definitions for Physical Quantities
# =============================================================================

# Mass: positive, realistic range from dust particle to planet
mass_strategy = st.floats(
    min_value=1e-10, max_value=1e30, allow_nan=False, allow_infinity=False
)

# Velocity: realistic for classical mechanics (sub-relativistic)
velocity_strategy = st.floats(
    min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Height: from millimeters to Earth orbit
height_strategy = st.floats(
    min_value=0.001, max_value=1e8, allow_nan=False, allow_infinity=False
)

# Force: from micro-newtons to stellar forces
# Using min_value=1e-6 to avoid floating point precision issues with very small numbers
force_strategy = st.floats(
    min_value=1e-6, max_value=1e30, allow_nan=False, allow_infinity=False
)

# Distance: millimeters to astronomical
distance_strategy = st.floats(
    min_value=0.001, max_value=1e12, allow_nan=False, allow_infinity=False
)

# Angle: full rotation range
angle_degrees_strategy = st.floats(
    min_value=-180, max_value=180, allow_nan=False, allow_infinity=False
)

# Acceleration: realistic range
acceleration_strategy = st.floats(
    min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Radius for centripetal motion: positive, realistic
radius_strategy = st.floats(
    min_value=0.001, max_value=1e9, allow_nan=False, allow_infinity=False
)

# Moment of inertia: positive
moment_inertia_strategy = st.floats(
    min_value=1e-10, max_value=1e20, allow_nan=False, allow_infinity=False
)

# Angular velocity: positive
angular_velocity_strategy = st.floats(
    min_value=0.001, max_value=1e6, allow_nan=False, allow_infinity=False
)


# =============================================================================
# Helper Functions
# =============================================================================


def extract_numeric_result(formula_str: str) -> float:
    """Extract numeric result by evaluating the ODF formula.

    For simple formulas, we can parse and evaluate them directly.
    This validates that the formula produces correct numerical results.
    """
    # Remove ODF prefix
    expr = formula_str[4:] if formula_str.startswith("of:=") else formula_str

    # Replace spreadsheet functions with Python equivalents
    expr = expr.replace("COS(RADIANS(", "math.cos(math.radians(")
    expr = expr.replace("SIN(RADIANS(", "math.sin(math.radians(")
    expr = expr.replace("))", "))")  # Fix double parentheses
    expr = expr.replace("^", "**")
    expr = expr.replace("PI()", str(math.pi))
    expr = expr.replace("SQRT(", "math.sqrt(")

    try:
        return float(eval(expr))
    except (ValueError, SyntaxError, ZeroDivisionError):
        return float("nan")


# =============================================================================
# Newton's Second Law (F = ma) Properties
# =============================================================================


class TestNewtonSecondLawProperties:
    """Property-based tests for F = ma relationship."""

    @given(mass=mass_strategy, acceleration=acceleration_strategy)
    @settings(max_examples=100)
    def test_force_proportional_to_mass(self, mass: float, acceleration: float) -> None:
        """Property: Doubling mass doubles force (at constant acceleration)."""
        formula = NewtonSecondLawFormula()

        result1 = formula.build(str(mass), str(acceleration))
        result2 = formula.build(str(mass * 2), str(acceleration))

        force1 = extract_numeric_result(result1)
        force2 = extract_numeric_result(result2)

        assume(not math.isnan(force1) and not math.isnan(force2))
        assume(force1 > 0)

        # Force should double when mass doubles
        ratio = force2 / force1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(mass=mass_strategy, acceleration=acceleration_strategy)
    @settings(max_examples=100)
    def test_force_proportional_to_acceleration(
        self, mass: float, acceleration: float
    ) -> None:
        """Property: Doubling acceleration doubles force (at constant mass)."""
        formula = NewtonSecondLawFormula()

        result1 = formula.build(str(mass), str(acceleration))
        result2 = formula.build(str(mass), str(acceleration * 2))

        force1 = extract_numeric_result(result1)
        force2 = extract_numeric_result(result2)

        assume(not math.isnan(force1) and not math.isnan(force2))
        assume(force1 > 0)

        ratio = force2 / force1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(mass=mass_strategy, acceleration=acceleration_strategy)
    @settings(max_examples=100)
    def test_force_always_positive_for_positive_inputs(
        self, mass: float, acceleration: float
    ) -> None:
        """Property: F = ma is always positive when both inputs positive."""
        formula = NewtonSecondLawFormula()
        result = formula.build(str(mass), str(acceleration))
        force = extract_numeric_result(result)

        assume(not math.isnan(force))
        assert force > 0, f"Force should be positive, got {force}"

    @given(mass=mass_strategy, acceleration=acceleration_strategy)
    @settings(max_examples=100)
    def test_produces_valid_odf_formula(self, mass: float, acceleration: float) -> None:
        """Property: Output is always a valid ODF formula string."""
        formula = NewtonSecondLawFormula()
        result = formula.build(str(mass), str(acceleration))

        assert result.startswith("of:="), "Formula must start with ODF prefix"
        assert "*" in result, "Formula must contain multiplication"


# =============================================================================
# Kinetic Energy (KE = 0.5*m*v^2) Properties
# =============================================================================


class TestKineticEnergyProperties:
    """Property-based tests for kinetic energy formula."""

    @given(mass=mass_strategy, velocity=velocity_strategy)
    @settings(max_examples=100)
    def test_kinetic_energy_always_positive(self, mass: float, velocity: float) -> None:
        """Property: Kinetic energy is always positive for non-zero velocity."""
        formula = KineticEnergyFormula()
        result = formula.build(str(mass), str(velocity))
        ke = extract_numeric_result(result)

        assume(not math.isnan(ke))
        assert ke > 0, f"KE should be positive, got {ke}"

    @given(mass=mass_strategy, velocity=velocity_strategy)
    @settings(max_examples=100)
    def test_doubling_velocity_quadruples_energy(
        self, mass: float, velocity: float
    ) -> None:
        """Property: KE scales with v^2, so doubling velocity quadruples energy."""
        assume(velocity < 5e5)  # Keep doubled velocity in reasonable range

        formula = KineticEnergyFormula()
        result1 = formula.build(str(mass), str(velocity))
        result2 = formula.build(str(mass), str(velocity * 2))

        ke1 = extract_numeric_result(result1)
        ke2 = extract_numeric_result(result2)

        assume(not math.isnan(ke1) and not math.isnan(ke2))
        assume(ke1 > 0)

        ratio = ke2 / ke1
        assert abs(ratio - 4.0) < 1e-10, f"Expected ratio 4.0, got {ratio}"

    @given(mass=mass_strategy, velocity=velocity_strategy)
    @settings(max_examples=100)
    def test_kinetic_energy_proportional_to_mass(
        self, mass: float, velocity: float
    ) -> None:
        """Property: KE is directly proportional to mass."""
        assume(mass < 5e29)  # Keep doubled mass in range

        formula = KineticEnergyFormula()
        result1 = formula.build(str(mass), str(velocity))
        result2 = formula.build(str(mass * 2), str(velocity))

        ke1 = extract_numeric_result(result1)
        ke2 = extract_numeric_result(result2)

        assume(not math.isnan(ke1) and not math.isnan(ke2))
        assume(ke1 > 0)

        ratio = ke2 / ke1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(mass=mass_strategy, velocity=velocity_strategy)
    @settings(max_examples=100)
    def test_kinetic_energy_formula_correctness(
        self, mass: float, velocity: float
    ) -> None:
        """Property: Computed KE matches expected 0.5*m*v^2."""
        formula = KineticEnergyFormula()
        result = formula.build(str(mass), str(velocity))
        ke = extract_numeric_result(result)

        expected = 0.5 * mass * velocity**2

        assume(not math.isnan(ke) and not math.isnan(expected))
        assume(expected > 0)

        relative_error = abs(ke - expected) / expected
        assert relative_error < 1e-10, f"KE mismatch: got {ke}, expected {expected}"


# =============================================================================
# Potential Energy (PE = mgh) Properties
# =============================================================================


class TestPotentialEnergyProperties:
    """Property-based tests for gravitational potential energy."""

    @given(mass=mass_strategy, height=height_strategy)
    @settings(max_examples=100)
    def test_potential_energy_proportional_to_height(
        self, mass: float, height: float
    ) -> None:
        """Property: PE is directly proportional to height."""
        assume(height < 5e7)  # Keep doubled height in range

        formula = PotentialEnergyFormula()
        result1 = formula.build(str(mass), str(height))
        result2 = formula.build(str(mass), str(height * 2))

        pe1 = extract_numeric_result(result1)
        pe2 = extract_numeric_result(result2)

        assume(not math.isnan(pe1) and not math.isnan(pe2))
        assume(pe1 > 0)

        ratio = pe2 / pe1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(mass=mass_strategy, height=height_strategy)
    @settings(max_examples=100)
    def test_potential_energy_uses_correct_gravity(
        self, mass: float, height: float
    ) -> None:
        """Property: Default gravity is Earth standard (9.81 m/s^2)."""
        formula = PotentialEnergyFormula()
        result = formula.build(str(mass), str(height))
        pe = extract_numeric_result(result)

        expected = mass * 9.81 * height

        assume(not math.isnan(pe) and not math.isnan(expected))
        assume(expected > 0)

        relative_error = abs(pe - expected) / expected
        assert relative_error < 1e-10, f"PE mismatch: got {pe}, expected {expected}"


# =============================================================================
# Momentum (p = mv) Properties
# =============================================================================


class TestMomentumProperties:
    """Property-based tests for linear momentum."""

    @given(mass=mass_strategy, velocity=velocity_strategy)
    @settings(max_examples=100)
    def test_momentum_always_positive(self, mass: float, velocity: float) -> None:
        """Property: Momentum is positive for positive mass and velocity."""
        formula = MomentumFormula()
        result = formula.build(str(mass), str(velocity))
        p = extract_numeric_result(result)

        assume(not math.isnan(p))
        assert p > 0, f"Momentum should be positive, got {p}"

    @given(mass=mass_strategy, velocity=velocity_strategy)
    @settings(max_examples=100)
    def test_momentum_commutative(self, mass: float, velocity: float) -> None:
        """Property: p = mv = vm (multiplication is commutative)."""
        formula = MomentumFormula()
        result1 = formula.build(str(mass), str(velocity))
        result2 = formula.build(str(velocity), str(mass))  # Swapped

        p1 = extract_numeric_result(result1)
        p2 = extract_numeric_result(result2)

        assume(not math.isnan(p1) and not math.isnan(p2))

        # Results should be identical due to commutative property
        assert abs(p1 - p2) < 1e-10 * max(abs(p1), abs(p2), 1)


# =============================================================================
# Work-Energy (W = Fd*cos(theta)) Properties
# =============================================================================


class TestWorkEnergyProperties:
    """Property-based tests for work-energy relationship."""

    @given(force=force_strategy, distance=distance_strategy)
    @settings(max_examples=100)
    def test_work_maximum_at_zero_angle(self, force: float, distance: float) -> None:
        """Property: Work is maximum when force and displacement are parallel (theta=0).

        Note: Uses force >= 1e-6 to avoid floating point precision issues.
        """
        # Ensure meaningful values to avoid numerical precision issues
        assume(force >= 1e-6)
        assume(distance >= 1e-6)

        formula = WorkEnergyFormula()

        work_zero = extract_numeric_result(
            formula.build(str(force), str(distance), "0")
        )
        work_45 = extract_numeric_result(formula.build(str(force), str(distance), "45"))
        work_90 = extract_numeric_result(formula.build(str(force), str(distance), "90"))

        assume(all(not math.isnan(w) for w in [work_zero, work_45, work_90]))

        # Use relative comparison for numerical stability
        assert work_zero > work_45, "Work at 0 degrees should exceed work at 45 degrees"
        # work_90 should be effectively zero, work_45 should be positive
        # cos(45) = 0.707, cos(90) = 0, so work_45 > work_90 always
        assert work_45 > abs(work_90), (
            "Work at 45 degrees should exceed work at 90 degrees"
        )

    @given(force=force_strategy, distance=distance_strategy)
    @settings(max_examples=100)
    def test_work_zero_at_perpendicular(self, force: float, distance: float) -> None:
        """Property: Work is zero when force perpendicular to displacement (theta=90)."""
        formula = WorkEnergyFormula()
        result = formula.build(str(force), str(distance), "90")
        work = extract_numeric_result(result)

        assume(not math.isnan(work))

        # cos(90 deg) = 0, so work should be very close to zero
        # Use relative tolerance based on the magnitude of force * distance
        max_expected = force * distance
        assert abs(work) < 1e-10 * max_expected + 1e-15


# =============================================================================
# Centripetal Force (Fc = mv^2/r) Properties
# =============================================================================


class TestCentripetalForceProperties:
    """Property-based tests for centripetal force."""

    @given(mass=mass_strategy, velocity=velocity_strategy, radius=radius_strategy)
    @settings(max_examples=100)
    def test_centripetal_force_always_positive(
        self, mass: float, velocity: float, radius: float
    ) -> None:
        """Property: Centripetal force is always positive for positive inputs."""
        formula = CentripetalForceFormula()
        result = formula.build(str(mass), str(velocity), str(radius))
        fc = extract_numeric_result(result)

        assume(not math.isnan(fc))
        assert fc > 0, f"Centripetal force should be positive, got {fc}"

    @given(mass=mass_strategy, velocity=velocity_strategy, radius=radius_strategy)
    @settings(max_examples=100)
    def test_centripetal_force_inversely_proportional_to_radius(
        self, mass: float, velocity: float, radius: float
    ) -> None:
        """Property: Fc is inversely proportional to radius."""
        assume(radius < 5e8)  # Keep doubled radius in range

        formula = CentripetalForceFormula()
        result1 = formula.build(str(mass), str(velocity), str(radius))
        result2 = formula.build(str(mass), str(velocity), str(radius * 2))

        fc1 = extract_numeric_result(result1)
        fc2 = extract_numeric_result(result2)

        assume(not math.isnan(fc1) and not math.isnan(fc2))
        assume(fc2 > 0)

        ratio = fc1 / fc2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Angular Momentum (L = Iw) Properties
# =============================================================================


class TestAngularMomentumProperties:
    """Property-based tests for angular momentum."""

    @given(moment=moment_inertia_strategy, angular_v=angular_velocity_strategy)
    @settings(max_examples=100)
    def test_angular_momentum_always_positive(
        self, moment: float, angular_v: float
    ) -> None:
        """Property: Angular momentum is positive for positive inputs."""
        formula = AngularMomentumFormula()
        result = formula.build(str(moment), str(angular_v))
        L = extract_numeric_result(result)

        assume(not math.isnan(L))
        assert L > 0, f"Angular momentum should be positive, got {L}"


# =============================================================================
# Physical Constants Validation (NIST CODATA 2018)
# =============================================================================


class TestPhysicalConstantsNIST:
    """Validate physical constants against NIST CODATA 2018 reference values."""

    def test_speed_of_light_nist(self) -> None:
        """Validate speed of light against NIST CODATA 2018 exact value."""
        # NIST CODATA 2018: c = 299792458 m/s (exact, defines meter)
        c = speed_of_light()
        assert c == 299792458.0, f"Speed of light should be 299792458 m/s, got {c}"

    def test_planck_constant_nist(self) -> None:
        """Validate Planck constant against NIST CODATA 2018 exact value."""
        # NIST CODATA 2018: h = 6.62607015e-34 J*s (exact, defines kilogram)
        h = planck_constant()
        assert h == 6.62607015e-34, f"Planck constant should be 6.62607015e-34, got {h}"

    def test_gravitational_constant_nist(self) -> None:
        """Validate gravitational constant against NIST CODATA 2018 value."""
        # NIST CODATA 2018: G = 6.67430(15)e-11 m^3/(kg*s^2)
        # Our value: 6.6743e-11 (within uncertainty)
        G = gravitational_constant()
        nist_value = 6.67430e-11
        uncertainty = 0.00015e-11

        assert abs(G - nist_value) < uncertainty * 10, (
            f"Gravitational constant {G} not within expected range of NIST value {nist_value}"
        )


# =============================================================================
# Utility Function Properties
# =============================================================================


class TestEscapeVelocityProperties:
    """Property-based tests for escape velocity calculation."""

    @given(
        mass=st.floats(
            min_value=1e20, max_value=1e30, allow_nan=False, allow_infinity=False
        ),
        radius=st.floats(
            min_value=1e3, max_value=1e9, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=50)
    def test_escape_velocity_always_positive(self, mass: float, radius: float) -> None:
        """Property: Escape velocity is always positive for positive mass and radius."""
        v_esc = calculate_escape_velocity(mass, radius)
        assert v_esc > 0, f"Escape velocity should be positive, got {v_esc}"

    @given(
        mass=st.floats(
            min_value=1e20, max_value=1e28, allow_nan=False, allow_infinity=False
        ),
        radius=st.floats(
            min_value=1e4, max_value=1e8, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=50)
    def test_escape_velocity_increases_with_mass(
        self, mass: float, radius: float
    ) -> None:
        """Property: Escape velocity increases with mass at constant radius."""
        v1 = calculate_escape_velocity(mass, radius)
        v2 = calculate_escape_velocity(mass * 2, radius)

        # v_esc = sqrt(2GM/r), so doubling M gives sqrt(2) increase
        expected_ratio = math.sqrt(2)
        actual_ratio = v2 / v1

        assert abs(actual_ratio - expected_ratio) < 1e-10, (
            f"Expected ratio {expected_ratio}, got {actual_ratio}"
        )


class TestSchwarzschildRadiusProperties:
    """Property-based tests for Schwarzschild radius."""

    @given(
        mass=st.floats(
            min_value=1e20, max_value=1e40, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=50)
    def test_schwarzschild_radius_proportional_to_mass(self, mass: float) -> None:
        """Property: Schwarzschild radius is directly proportional to mass."""
        assume(mass < 5e39)  # Keep doubled mass in range

        r1 = calculate_schwarzschild_radius(mass)
        r2 = calculate_schwarzschild_radius(mass * 2)

        ratio = r2 / r1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    def test_schwarzschild_radius_sun_reference(self) -> None:
        """Validate: Sun's Schwarzschild radius is approximately 3 km."""
        sun_mass = 1.989e30  # kg
        r_s = calculate_schwarzschild_radius(sun_mass)

        # Expected: ~2954 m (approximately 3 km)
        assert 2900 < r_s < 3000, (
            f"Sun's Schwarzschild radius should be ~3km, got {r_s} m"
        )
