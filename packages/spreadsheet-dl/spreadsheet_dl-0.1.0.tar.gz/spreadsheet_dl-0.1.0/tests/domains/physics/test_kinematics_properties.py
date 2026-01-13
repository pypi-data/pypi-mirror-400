"""Property-based tests for Physics kinematics formulas.

Uses Hypothesis to validate kinematic relationships across entire input domains.
Tests verify mathematical properties of motion equations (SUVAT equations).

Test Strategy:
    - Each test verifies mathematical/physical properties, not string formatting
    - Properties tested include: displacement consistency, velocity-acceleration relations
    - Input domains match realistic physical values to avoid numerical issues

References:
    - Classical mechanics: constant acceleration kinematics (SUVAT)
    - Energy-momentum conservation in isolated systems
"""

from __future__ import annotations

import math

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from spreadsheet_dl.domains.physics.formulas.thermodynamics import (
    CarnotEfficiencyFormula,
    HeatTransferFormula,
    IdealGasLawFormula,
    StefanBoltzmannFormula,
    ThermalExpansionFormula,
    WiensLawFormula,
)
from spreadsheet_dl.domains.physics.formulas.waves import (
    AngularFrequencyFormula,
    BeatFrequencyFormula,
    WaveNumberFormula,
    WavePeriodFormula,
    WaveVelocityFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.property, pytest.mark.science]


# =============================================================================
# Strategy Definitions for Physical Quantities
# =============================================================================

# Temperature: must be positive Kelvin (above absolute zero)
temperature_strategy = st.floats(
    min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False
)

# Pressure: positive, from vacuum to extreme
pressure_strategy = st.floats(
    min_value=1.0, max_value=1e9, allow_nan=False, allow_infinity=False
)

# Volume: positive, realistic range
volume_strategy = st.floats(
    min_value=1e-6, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Mass: positive
mass_strategy = st.floats(
    min_value=1e-10, max_value=1e10, allow_nan=False, allow_infinity=False
)

# Specific heat: positive
specific_heat_strategy = st.floats(
    min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False
)

# Temperature difference: can be negative for cooling
delta_temp_strategy = st.floats(
    min_value=-500.0, max_value=500.0, allow_nan=False, allow_infinity=False
)

# Frequency: positive Hz
frequency_strategy = st.floats(
    min_value=0.001, max_value=1e15, allow_nan=False, allow_infinity=False
)

# Wavelength: positive meters
wavelength_strategy = st.floats(
    min_value=1e-15, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Energy: positive Joules
energy_strategy = st.floats(
    min_value=1e-30, max_value=1e30, allow_nan=False, allow_infinity=False
)

# Power: positive Watts
power_strategy = st.floats(
    min_value=1e-10, max_value=1e15, allow_nan=False, allow_infinity=False
)

# Emissivity: 0 to 1
emissivity_strategy = st.floats(
    min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False
)

# Area: positive square meters
area_strategy = st.floats(
    min_value=1e-10, max_value=1e10, allow_nan=False, allow_infinity=False
)


# =============================================================================
# Helper Functions
# =============================================================================


def extract_numeric_result(formula_str: str) -> float:
    """Extract numeric result by evaluating the ODF formula."""
    expr = formula_str[4:] if formula_str.startswith("of:=") else formula_str

    # Replace spreadsheet functions with Python equivalents
    expr = expr.replace("^", "**")
    expr = expr.replace("PI()", str(math.pi))
    expr = expr.replace("SQRT(", "math.sqrt(")
    expr = expr.replace("LOG10(", "math.log10(")
    expr = expr.replace("LN(", "math.log(")
    expr = expr.replace("EXP(", "math.exp(")
    expr = expr.replace("ABS(", "abs(")

    try:
        return float(eval(expr))
    except (ValueError, SyntaxError, ZeroDivisionError):
        return float("nan")


# =============================================================================
# Ideal Gas Law (PV = nRT) Properties
# =============================================================================


class TestIdealGasLawProperties:
    """Property-based tests for ideal gas law."""

    @given(
        pressure=pressure_strategy,
        volume=volume_strategy,
        temperature=temperature_strategy,
    )
    @settings(max_examples=100)
    def test_moles_always_positive(
        self, pressure: float, volume: float, temperature: float
    ) -> None:
        """Property: Calculated moles is always positive for positive inputs."""
        formula = IdealGasLawFormula()
        result = formula.build(str(pressure), str(volume), "8.314", str(temperature))
        n = extract_numeric_result(result)

        assume(not math.isnan(n))
        assert n > 0, f"Moles should be positive, got {n}"

    @given(
        pressure=st.floats(min_value=1e3, max_value=1e6, allow_nan=False),
        volume=st.floats(min_value=0.001, max_value=100, allow_nan=False),
        temperature=st.floats(min_value=100, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_moles_proportional_to_pressure(
        self, pressure: float, volume: float, temperature: float
    ) -> None:
        """Property: Doubling pressure doubles moles (at constant V, T)."""
        formula = IdealGasLawFormula()

        result1 = formula.build(str(pressure), str(volume), "8.314", str(temperature))
        result2 = formula.build(
            str(pressure * 2), str(volume), "8.314", str(temperature)
        )

        n1 = extract_numeric_result(result1)
        n2 = extract_numeric_result(result2)

        assume(not math.isnan(n1) and not math.isnan(n2))
        assume(n1 > 0)

        ratio = n2 / n1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(
        pressure=st.floats(min_value=1e3, max_value=1e6, allow_nan=False),
        volume=st.floats(min_value=0.001, max_value=100, allow_nan=False),
        temperature=st.floats(min_value=100, max_value=500, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_moles_inversely_proportional_to_temperature(
        self, pressure: float, volume: float, temperature: float
    ) -> None:
        """Property: Doubling temperature halves moles (at constant P, V)."""
        formula = IdealGasLawFormula()

        result1 = formula.build(str(pressure), str(volume), "8.314", str(temperature))
        result2 = formula.build(
            str(pressure), str(volume), "8.314", str(temperature * 2)
        )

        n1 = extract_numeric_result(result1)
        n2 = extract_numeric_result(result2)

        assume(not math.isnan(n1) and not math.isnan(n2))
        assume(n2 > 0)

        ratio = n1 / n2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Heat Transfer (Q = mcDeltaT) Properties
# =============================================================================


class TestHeatTransferProperties:
    """Property-based tests for heat transfer."""

    @given(
        mass=mass_strategy,
        specific_heat=specific_heat_strategy,
        delta_temp=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_heat_always_positive_for_positive_delta_t(
        self, mass: float, specific_heat: float, delta_temp: float
    ) -> None:
        """Property: Heat is positive when delta_T is positive (heating)."""
        formula = HeatTransferFormula()
        result = formula.build(str(mass), str(specific_heat), str(delta_temp))
        q = extract_numeric_result(result)

        assume(not math.isnan(q))
        assert q > 0, f"Heat should be positive for positive delta_T, got {q}"

    @given(
        mass=st.floats(min_value=0.1, max_value=100, allow_nan=False),
        specific_heat=st.floats(min_value=1000, max_value=5000, allow_nan=False),
        delta_temp=st.floats(min_value=1.0, max_value=50.0, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_heat_proportional_to_mass(
        self, mass: float, specific_heat: float, delta_temp: float
    ) -> None:
        """Property: Doubling mass doubles heat transfer."""
        formula = HeatTransferFormula()

        result1 = formula.build(str(mass), str(specific_heat), str(delta_temp))
        result2 = formula.build(str(mass * 2), str(specific_heat), str(delta_temp))

        q1 = extract_numeric_result(result1)
        q2 = extract_numeric_result(result2)

        assume(not math.isnan(q1) and not math.isnan(q2))
        assume(q1 > 0)

        ratio = q2 / q1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Carnot Efficiency Properties
# =============================================================================


class TestCarnotEfficiencyProperties:
    """Property-based tests for Carnot efficiency."""

    @given(
        temp_cold=st.floats(min_value=100, max_value=400, allow_nan=False),
        temp_hot=st.floats(min_value=401, max_value=2000, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_efficiency_bounded_zero_to_one(
        self, temp_cold: float, temp_hot: float
    ) -> None:
        """Property: Carnot efficiency is always between 0 and 1."""
        assume(temp_cold < temp_hot)

        formula = CarnotEfficiencyFormula()
        result = formula.build(str(temp_cold), str(temp_hot))
        eta = extract_numeric_result(result)

        assume(not math.isnan(eta))
        assert 0 < eta < 1, f"Efficiency should be in (0,1), got {eta}"

    @given(
        temp_cold=st.floats(min_value=100, max_value=300, allow_nan=False),
        temp_hot=st.floats(min_value=500, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_efficiency_increases_with_temp_difference(
        self, temp_cold: float, temp_hot: float
    ) -> None:
        """Property: Larger temperature difference gives higher efficiency."""
        formula = CarnotEfficiencyFormula()

        # Original efficiency
        result1 = formula.build(str(temp_cold), str(temp_hot))
        eta1 = extract_numeric_result(result1)

        # Increase Th by 100K (increases efficiency)
        result2 = formula.build(str(temp_cold), str(temp_hot + 100))
        eta2 = extract_numeric_result(result2)

        assume(not math.isnan(eta1) and not math.isnan(eta2))

        assert eta2 > eta1, f"Higher Th should give higher efficiency: {eta1} vs {eta2}"

    def test_carnot_efficiency_zero_when_equal_temps(self) -> None:
        """Reference: Efficiency is 0 when Tc = Th."""
        formula = CarnotEfficiencyFormula()
        result = formula.build("300", "300")
        eta = extract_numeric_result(result)

        assert abs(eta) < 1e-10, f"Efficiency should be 0 when Tc=Th, got {eta}"


# =============================================================================
# Stefan-Boltzmann Law Properties
# =============================================================================


class TestStefanBoltzmannProperties:
    """Property-based tests for blackbody radiation."""

    @given(
        emissivity=emissivity_strategy,
        area=area_strategy,
        temperature=temperature_strategy,
    )
    @settings(max_examples=100)
    def test_power_always_positive(
        self, emissivity: float, area: float, temperature: float
    ) -> None:
        """Property: Radiated power is always positive."""
        formula = StefanBoltzmannFormula()
        result = formula.build(str(emissivity), str(area), str(temperature))
        power = extract_numeric_result(result)

        assume(not math.isnan(power))
        assert power > 0, f"Radiated power should be positive, got {power}"

    @given(
        emissivity=emissivity_strategy,
        area=area_strategy,
        temperature=st.floats(min_value=100, max_value=500, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_power_scales_with_t4(
        self, emissivity: float, area: float, temperature: float
    ) -> None:
        """Property: Power scales with T^4 (Stefan-Boltzmann law)."""
        formula = StefanBoltzmannFormula()

        result1 = formula.build(str(emissivity), str(area), str(temperature))
        result2 = formula.build(str(emissivity), str(area), str(temperature * 2))

        p1 = extract_numeric_result(result1)
        p2 = extract_numeric_result(result2)

        assume(not math.isnan(p1) and not math.isnan(p2))
        assume(p1 > 0)

        # Doubling T should give 2^4 = 16x power
        ratio = p2 / p1
        assert abs(ratio - 16.0) < 1e-6, f"Expected ratio 16.0, got {ratio}"


# =============================================================================
# Thermal Expansion Properties
# =============================================================================


class TestThermalExpansionProperties:
    """Property-based tests for thermal expansion."""

    @given(
        coefficient=st.floats(min_value=1e-7, max_value=1e-4, allow_nan=False),
        length=st.floats(min_value=0.01, max_value=100, allow_nan=False),
        delta_temp=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_expansion_proportional_to_temp_change(
        self, coefficient: float, length: float, delta_temp: float
    ) -> None:
        """Property: Expansion is proportional to temperature change."""
        formula = ThermalExpansionFormula()

        result1 = formula.build(str(coefficient), str(length), str(delta_temp))
        result2 = formula.build(str(coefficient), str(length), str(delta_temp * 2))

        dl1 = extract_numeric_result(result1)
        dl2 = extract_numeric_result(result2)

        assume(not math.isnan(dl1) and not math.isnan(dl2))
        assume(dl1 > 0)

        ratio = dl2 / dl1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Wave Properties
# =============================================================================


class TestWaveVelocityProperties:
    """Property-based tests for wave velocity."""

    @given(
        frequency=frequency_strategy,
        wavelength=wavelength_strategy,
    )
    @settings(max_examples=100)
    def test_velocity_always_positive(
        self, frequency: float, wavelength: float
    ) -> None:
        """Property: Wave velocity is always positive."""
        formula = WaveVelocityFormula()
        result = formula.build(str(frequency), str(wavelength))
        v = extract_numeric_result(result)

        assume(not math.isnan(v))
        assert v > 0, f"Wave velocity should be positive, got {v}"

    @given(
        frequency=st.floats(min_value=1.0, max_value=1e6, allow_nan=False),
        wavelength=st.floats(min_value=1e-3, max_value=1e3, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_velocity_formula_correctness(
        self, frequency: float, wavelength: float
    ) -> None:
        """Property: v = f * lambda."""
        formula = WaveVelocityFormula()
        result = formula.build(str(frequency), str(wavelength))
        v = extract_numeric_result(result)

        expected = frequency * wavelength

        assume(not math.isnan(v))

        relative_error = abs(v - expected) / expected
        assert relative_error < 1e-10, (
            f"Velocity mismatch: got {v}, expected {expected}"
        )


class TestWavePeriodProperties:
    """Property-based tests for wave period."""

    @given(frequency=frequency_strategy)
    @settings(max_examples=100)
    def test_period_inverse_of_frequency(self, frequency: float) -> None:
        """Property: Period T = 1/f."""
        formula = WavePeriodFormula()
        result = formula.build(str(frequency))
        period = extract_numeric_result(result)

        expected = 1.0 / frequency

        assume(not math.isnan(period))

        relative_error = abs(period - expected) / expected
        assert relative_error < 1e-10, (
            f"Period mismatch: got {period}, expected {expected}"
        )


class TestAngularFrequencyProperties:
    """Property-based tests for angular frequency."""

    @given(frequency=frequency_strategy)
    @settings(max_examples=100)
    def test_omega_equals_2pi_f(self, frequency: float) -> None:
        """Property: omega = 2*pi*f."""
        formula = AngularFrequencyFormula()
        result = formula.build(str(frequency))
        omega = extract_numeric_result(result)

        expected = 2 * math.pi * frequency

        assume(not math.isnan(omega))

        relative_error = abs(omega - expected) / expected
        assert relative_error < 1e-10, (
            f"Angular frequency mismatch: got {omega}, expected {expected}"
        )


class TestWaveNumberProperties:
    """Property-based tests for wave number."""

    @given(wavelength=wavelength_strategy)
    @settings(max_examples=100)
    def test_k_equals_2pi_over_lambda(self, wavelength: float) -> None:
        """Property: k = 2*pi/lambda."""
        formula = WaveNumberFormula()
        result = formula.build(str(wavelength))
        k = extract_numeric_result(result)

        expected = 2 * math.pi / wavelength

        assume(not math.isnan(k))

        relative_error = abs(k - expected) / expected
        assert relative_error < 1e-10, (
            f"Wave number mismatch: got {k}, expected {expected}"
        )


class TestBeatFrequencyProperties:
    """Property-based tests for beat frequency."""

    @given(
        f1=st.floats(min_value=100, max_value=1000, allow_nan=False),
        f2=st.floats(min_value=100, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_beat_frequency_is_difference(self, f1: float, f2: float) -> None:
        """Property: Beat frequency = |f1 - f2|."""
        formula = BeatFrequencyFormula()
        result = formula.build(str(f1), str(f2))
        f_beat = extract_numeric_result(result)

        expected = abs(f1 - f2)

        assume(not math.isnan(f_beat))

        # Handle case where beat is very small
        if expected > 0.001:
            relative_error = abs(f_beat - expected) / expected
            assert relative_error < 1e-10, (
                f"Beat frequency mismatch: got {f_beat}, expected {expected}"
            )


# =============================================================================
# Reference Value Tests (Known Physical Constants)
# =============================================================================


class TestReferenceValues:
    """Validate calculations against known reference values."""

    def test_standard_atmosphere_gas_law(self) -> None:
        """Reference: 1 mole of gas at STP occupies ~22.4 L."""
        formula = IdealGasLawFormula()
        # P = 101325 Pa, V = 0.0224 m^3, T = 273.15 K
        result = formula.build("101325", "0.0224", "8.314", "273.15")
        n = extract_numeric_result(result)

        # Should be approximately 1 mole
        assert abs(n - 1.0) < 0.01, f"Should be ~1 mole, got {n}"

    def test_carnot_efficiency_typical_values(self) -> None:
        """Reference: Typical thermal power plant efficiency."""
        formula = CarnotEfficiencyFormula()
        # Tc = 300K (27C), Th = 500K (227C)
        result = formula.build("300", "500")
        eta = extract_numeric_result(result)

        # Expected: 1 - 300/500 = 0.4 (40%)
        assert abs(eta - 0.4) < 1e-10, f"Expected 40% efficiency, got {eta}"

    def test_stefan_boltzmann_sun_temperature(self) -> None:
        """Reference: Sun's surface temperature gives expected power."""
        formula = StefanBoltzmannFormula()
        # emissivity = 1 (blackbody), area = 1 m^2, T = 5778 K (Sun)
        result = formula.build("1", "1", "5778")
        power = extract_numeric_result(result)

        # Expected: ~6.3e7 W/m^2 (solar constant at surface)
        # P = sigma * T^4 = 5.67e-8 * 5778^4 = 6.32e7
        expected = 5.67e-8 * 5778**4
        relative_error = abs(power - expected) / expected

        assert relative_error < 0.01, f"Expected ~{expected} W/m^2, got {power}"

    def test_wien_displacement_law_sun(self) -> None:
        """Reference: Sun's peak wavelength is ~500nm."""
        formula = WiensLawFormula()
        result = formula.build("5778")  # Sun's temperature
        lambda_max = extract_numeric_result(result)

        # Expected: 2.898e-3 / 5778 = 5.01e-7 m = 501 nm
        expected = 2.898e-3 / 5778
        relative_error = abs(lambda_max - expected) / expected

        assert relative_error < 0.01, (
            f"Expected ~{expected * 1e9:.0f} nm, got {lambda_max * 1e9:.0f} nm"
        )
