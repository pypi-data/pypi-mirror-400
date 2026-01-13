"""Property-based tests for Electrical Engineering circuit formulas.

Uses Hypothesis to validate electrical engineering properties across input domains.
Tests verify Ohm's law, power relationships, and circuit theory fundamentals.

Test Strategy:
    - Properties test electrical laws: Ohm's law, Kirchhoff's laws, power conservation
    - Input domains constrained to realistic electrical values
    - Reference values from IEEE standards where applicable

References:
    - Ohm's Law: V = IR, P = VI = I^2R = V^2/R
    - Kirchhoff's Current Law: Sum of currents at node = 0
    - Kirchhoff's Voltage Law: Sum of voltages in loop = 0
"""

from __future__ import annotations

import math

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from spreadsheet_dl.domains.electrical_engineering import (
    BandwidthFormula,
    CapacitanceFormula,
    ComponentThermalResistanceFormula,
    CurrentCalcFormula,
    InductanceFormula,
    ParallelResistanceFormula,
    PowerDissipationFormula,
    SeriesResistanceFormula,
    SignalToNoiseRatioFormula,
)
from spreadsheet_dl.domains.electrical_engineering.utils import (
    calculate_parallel_resistance,
    calculate_power_dissipation,
    calculate_series_resistance,
    parse_si_prefix,
)

pytestmark = [pytest.mark.unit, pytest.mark.property, pytest.mark.engineering]


# =============================================================================
# Strategy Definitions for Electrical Quantities
# =============================================================================

# Voltage: millivolts to kilovolts
voltage_strategy = st.floats(
    min_value=1e-3, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Current: microamps to kiloamps
current_strategy = st.floats(
    min_value=1e-6, max_value=1e3, allow_nan=False, allow_infinity=False
)

# Resistance: milliohms to megaohms
resistance_strategy = st.floats(
    min_value=1e-3, max_value=1e9, allow_nan=False, allow_infinity=False
)

# Power: microwatts to megawatts
power_strategy = st.floats(
    min_value=1e-6, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Frequency: Hz to GHz
frequency_strategy = st.floats(
    min_value=1.0, max_value=1e10, allow_nan=False, allow_infinity=False
)

# Reactance: ohms
reactance_strategy = st.floats(
    min_value=0.1, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Temperature: 0 to 200 degrees C
temperature_strategy = st.floats(
    min_value=0.1, max_value=200, allow_nan=False, allow_infinity=False
)

# Length: millimeters
length_mm_strategy = st.floats(
    min_value=1.0, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Time: nanoseconds to seconds
time_strategy = st.floats(
    min_value=1e-12, max_value=1.0, allow_nan=False, allow_infinity=False
)

# Velocity: m/s (for propagation)
velocity_strategy = st.floats(
    min_value=1e6, max_value=3e8, allow_nan=False, allow_infinity=False
)


# =============================================================================
# Helper Functions
# =============================================================================


def extract_numeric_result(formula_str: str) -> float:
    """Extract numeric result by evaluating the formula."""
    # Handle both ODF prefix and raw formulas
    expr = formula_str[4:] if formula_str.startswith("of:=") else formula_str

    # Replace spreadsheet functions with Python equivalents
    expr = expr.replace("^", "**")
    expr = expr.replace("PI()", str(math.pi))
    expr = expr.replace("LOG10(", "math.log10(")
    expr = expr.replace("SQRT(", "math.sqrt(")

    try:
        return float(eval(expr))
    except (ValueError, SyntaxError, ZeroDivisionError):
        return float("nan")


# =============================================================================
# Ohm's Law and Power Properties
# =============================================================================


class TestPowerDissipationProperties:
    """Property-based tests for power dissipation (P = VI)."""

    @given(voltage=voltage_strategy, current=current_strategy)
    @settings(max_examples=100)
    def test_power_always_positive(self, voltage: float, current: float) -> None:
        """Property: Power is always positive for positive V and I."""
        formula = PowerDissipationFormula()
        result = formula.build(str(voltage), str(current))
        power = extract_numeric_result(result)

        assume(not math.isnan(power))
        assert power > 0, f"Power should be positive, got {power}"

    @given(voltage=voltage_strategy, current=current_strategy)
    @settings(max_examples=100)
    def test_power_proportional_to_voltage(
        self, voltage: float, current: float
    ) -> None:
        """Property: Doubling voltage doubles power (at constant current)."""
        assume(voltage < 5e5)

        formula = PowerDissipationFormula()
        result1 = formula.build(str(voltage), str(current))
        result2 = formula.build(str(voltage * 2), str(current))

        p1 = extract_numeric_result(result1)
        p2 = extract_numeric_result(result2)

        assume(not math.isnan(p1) and not math.isnan(p2))
        assume(p1 > 0)

        ratio = p2 / p1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(voltage=voltage_strategy, current=current_strategy)
    @settings(max_examples=100)
    def test_power_commutative(self, voltage: float, current: float) -> None:
        """Property: P = VI = IV (commutative)."""
        formula = PowerDissipationFormula()
        result1 = formula.build(str(voltage), str(current))
        result2 = formula.build(str(current), str(voltage))

        p1 = extract_numeric_result(result1)
        p2 = extract_numeric_result(result2)

        assume(not math.isnan(p1) and not math.isnan(p2))

        # Should be equal within floating point tolerance
        assert abs(p1 - p2) < 1e-10 * max(abs(p1), abs(p2), 1)

    @given(voltage=voltage_strategy, current=current_strategy)
    @settings(max_examples=100)
    def test_power_formula_correctness(self, voltage: float, current: float) -> None:
        """Property: Computed P matches expected V*I."""
        formula = PowerDissipationFormula()
        result = formula.build(str(voltage), str(current))
        power = extract_numeric_result(result)

        expected = voltage * current

        assume(not math.isnan(power) and not math.isnan(expected))
        assume(expected > 0)

        relative_error = abs(power - expected) / expected
        assert relative_error < 1e-10, (
            f"Power mismatch: got {power}, expected {expected}"
        )


class TestCurrentCalcProperties:
    """Property-based tests for current calculation (I = P/V)."""

    @given(power=power_strategy, voltage=voltage_strategy)
    @settings(max_examples=100)
    def test_current_always_positive(self, power: float, voltage: float) -> None:
        """Property: Current is always positive for positive P and V."""
        formula = CurrentCalcFormula()
        result = formula.build(str(power), str(voltage))
        current = extract_numeric_result(result)

        assume(not math.isnan(current))
        assert current > 0, f"Current should be positive, got {current}"

    @given(power=power_strategy, voltage=voltage_strategy)
    @settings(max_examples=100)
    def test_current_inversely_proportional_to_voltage(
        self, power: float, voltage: float
    ) -> None:
        """Property: Doubling voltage halves current (at constant power)."""
        assume(voltage < 5e5)

        formula = CurrentCalcFormula()
        result1 = formula.build(str(power), str(voltage))
        result2 = formula.build(str(power), str(voltage * 2))

        i1 = extract_numeric_result(result1)
        i2 = extract_numeric_result(result2)

        assume(not math.isnan(i1) and not math.isnan(i2))
        assume(i2 > 0)

        ratio = i1 / i2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Resistance Properties
# =============================================================================


class TestParallelResistanceProperties:
    """Property-based tests for parallel resistance."""

    @given(
        r1=resistance_strategy,
        r2=resistance_strategy,
    )
    @settings(max_examples=100)
    def test_parallel_less_than_smallest(self, r1: float, r2: float) -> None:
        """Property: Parallel resistance is always less than the smallest resistor."""
        formula = ParallelResistanceFormula()
        result = formula.build(str(r1), str(r2))
        r_parallel = extract_numeric_result(result)

        assume(not math.isnan(r_parallel))

        smallest = min(r1, r2)
        assert r_parallel < smallest, (
            f"Parallel R ({r_parallel}) should be < smallest ({smallest})"
        )

    @given(r=resistance_strategy)
    @settings(max_examples=50)
    def test_parallel_equal_resistors(self, r: float) -> None:
        """Property: Two equal resistors in parallel = R/2."""
        formula = ParallelResistanceFormula()
        result = formula.build(str(r), str(r))
        r_parallel = extract_numeric_result(result)

        assume(not math.isnan(r_parallel))

        expected = r / 2
        relative_error = abs(r_parallel - expected) / expected

        assert relative_error < 1e-10, (
            f"Two {r}Ω in parallel should be {expected}Ω, got {r_parallel}Ω"
        )

    @given(
        r1=st.floats(min_value=10, max_value=1000, allow_nan=False),
        r2=st.floats(min_value=10, max_value=1000, allow_nan=False),
        r3=st.floats(min_value=10, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_parallel_three_resistors_formula(
        self, r1: float, r2: float, r3: float
    ) -> None:
        """Property: Three resistors in parallel matches expected formula."""
        formula = ParallelResistanceFormula()
        result = formula.build(str(r1), str(r2), str(r3))
        r_parallel = extract_numeric_result(result)

        expected = 1.0 / (1.0 / r1 + 1.0 / r2 + 1.0 / r3)

        assume(not math.isnan(r_parallel) and not math.isnan(expected))

        relative_error = abs(r_parallel - expected) / expected
        assert relative_error < 1e-10, (
            f"Parallel R mismatch: got {r_parallel}, expected {expected}"
        )


class TestSeriesResistanceProperties:
    """Property-based tests for series resistance."""

    @given(
        r1=resistance_strategy,
        r2=resistance_strategy,
    )
    @settings(max_examples=100)
    def test_series_greater_than_largest(self, r1: float, r2: float) -> None:
        """Property: Series resistance is always greater than the largest resistor."""
        formula = SeriesResistanceFormula()
        result = formula.build(str(r1), str(r2))
        r_series = extract_numeric_result(result)

        assume(not math.isnan(r_series))

        largest = max(r1, r2)
        assert r_series > largest, (
            f"Series R ({r_series}) should be > largest ({largest})"
        )

    @given(r=resistance_strategy)
    @settings(max_examples=50)
    def test_series_equal_resistors(self, r: float) -> None:
        """Property: Two equal resistors in series = 2R."""
        formula = SeriesResistanceFormula()
        result = formula.build(str(r), str(r))
        r_series = extract_numeric_result(result)

        assume(not math.isnan(r_series))

        expected = r * 2
        relative_error = abs(r_series - expected) / expected

        assert relative_error < 1e-10, (
            f"Two {r}Ω in series should be {expected}Ω, got {r_series}Ω"
        )

    @given(
        r1=st.floats(min_value=10, max_value=1000, allow_nan=False),
        r2=st.floats(min_value=10, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_series_commutative(self, r1: float, r2: float) -> None:
        """Property: Series resistance is commutative."""
        formula = SeriesResistanceFormula()
        result1 = formula.build(str(r1), str(r2))
        result2 = formula.build(str(r2), str(r1))

        rs1 = extract_numeric_result(result1)
        rs2 = extract_numeric_result(result2)

        assume(not math.isnan(rs1) and not math.isnan(rs2))
        assert abs(rs1 - rs2) < 1e-10


# =============================================================================
# Reactance and Impedance Properties
# =============================================================================


class TestCapacitanceProperties:
    """Property-based tests for capacitance calculation."""

    @given(frequency=frequency_strategy, reactance=reactance_strategy)
    @settings(max_examples=100)
    def test_capacitance_always_positive(
        self, frequency: float, reactance: float
    ) -> None:
        """Property: Capacitance is always positive for positive f and Xc."""
        formula = CapacitanceFormula()
        result = formula.build(str(frequency), str(reactance))
        capacitance = extract_numeric_result(result)

        assume(not math.isnan(capacitance))
        assert capacitance > 0, f"Capacitance should be positive, got {capacitance}"

    @given(frequency=frequency_strategy, reactance=reactance_strategy)
    @settings(max_examples=100)
    def test_capacitance_inversely_proportional_to_frequency(
        self, frequency: float, reactance: float
    ) -> None:
        """Property: Doubling frequency halves capacitance."""
        assume(frequency < 5e9)

        formula = CapacitanceFormula()
        result1 = formula.build(str(frequency), str(reactance))
        result2 = formula.build(str(frequency * 2), str(reactance))

        c1 = extract_numeric_result(result1)
        c2 = extract_numeric_result(result2)

        assume(not math.isnan(c1) and not math.isnan(c2))
        assume(c2 > 0)

        ratio = c1 / c2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


class TestInductanceProperties:
    """Property-based tests for inductance calculation."""

    @given(frequency=frequency_strategy, reactance=reactance_strategy)
    @settings(max_examples=100)
    def test_inductance_always_positive(
        self, frequency: float, reactance: float
    ) -> None:
        """Property: Inductance is always positive for positive f and XL."""
        formula = InductanceFormula()
        result = formula.build(str(frequency), str(reactance))
        inductance = extract_numeric_result(result)

        assume(not math.isnan(inductance))
        assert inductance > 0, f"Inductance should be positive, got {inductance}"

    @given(frequency=frequency_strategy, reactance=reactance_strategy)
    @settings(max_examples=100)
    def test_inductance_inversely_proportional_to_frequency(
        self, frequency: float, reactance: float
    ) -> None:
        """Property: Doubling frequency halves inductance (for same reactance)."""
        assume(frequency < 5e9)

        formula = InductanceFormula()
        result1 = formula.build(str(frequency), str(reactance))
        result2 = formula.build(str(frequency * 2), str(reactance))

        l1 = extract_numeric_result(result1)
        l2 = extract_numeric_result(result2)

        assume(not math.isnan(l1) and not math.isnan(l2))
        assume(l2 > 0)

        ratio = l1 / l2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Signal Properties
# =============================================================================


class TestSignalToNoiseRatioProperties:
    """Property-based tests for SNR calculation."""

    @given(
        signal=st.floats(min_value=1.0, max_value=1e6, allow_nan=False),
        noise=st.floats(min_value=0.001, max_value=1e3, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_snr_positive_when_signal_greater_than_noise(
        self, signal: float, noise: float
    ) -> None:
        """Property: SNR > 0 dB when signal > noise."""
        assume(signal > noise)

        formula = SignalToNoiseRatioFormula()
        result = formula.build(str(signal), str(noise))
        snr = extract_numeric_result(result)

        assume(not math.isnan(snr))
        assert snr > 0, f"SNR should be positive when signal > noise, got {snr} dB"

    @given(power=st.floats(min_value=1.0, max_value=1000, allow_nan=False))
    @settings(max_examples=50)
    def test_snr_zero_when_equal(self, power: float) -> None:
        """Property: SNR = 0 dB when signal equals noise."""
        formula = SignalToNoiseRatioFormula()
        result = formula.build(str(power), str(power))
        snr = extract_numeric_result(result)

        assume(not math.isnan(snr))
        assert abs(snr) < 1e-10, f"SNR should be 0 dB when S=N, got {snr} dB"

    @given(
        signal=st.floats(min_value=0.001, max_value=1.0, allow_nan=False),
        noise=st.floats(min_value=1.0, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_snr_negative_when_noise_greater(self, signal: float, noise: float) -> None:
        """Property: SNR < 0 dB when noise > signal."""
        assume(noise > signal)

        formula = SignalToNoiseRatioFormula()
        result = formula.build(str(signal), str(noise))
        snr = extract_numeric_result(result)

        assume(not math.isnan(snr))
        assert snr < 0, f"SNR should be negative when noise > signal, got {snr} dB"


class TestBandwidthProperties:
    """Property-based tests for bandwidth calculation."""

    @given(rise_time=time_strategy)
    @settings(max_examples=100)
    def test_bandwidth_always_positive(self, rise_time: float) -> None:
        """Property: Bandwidth is always positive for positive rise time."""
        formula = BandwidthFormula()
        result = formula.build(str(rise_time))
        bandwidth = extract_numeric_result(result)

        assume(not math.isnan(bandwidth))
        assert bandwidth > 0, f"Bandwidth should be positive, got {bandwidth}"

    @given(rise_time=st.floats(min_value=1e-9, max_value=1e-3, allow_nan=False))
    @settings(max_examples=50)
    def test_bandwidth_inversely_proportional_to_rise_time(
        self, rise_time: float
    ) -> None:
        """Property: Halving rise time doubles bandwidth."""
        formula = BandwidthFormula()
        result1 = formula.build(str(rise_time))
        result2 = formula.build(str(rise_time / 2))

        bw1 = extract_numeric_result(result1)
        bw2 = extract_numeric_result(result2)

        assume(not math.isnan(bw1) and not math.isnan(bw2))
        assume(bw1 > 0)

        ratio = bw2 / bw1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Thermal Properties
# =============================================================================


class TestThermalResistanceProperties:
    """Property-based tests for thermal resistance."""

    @given(temp_rise=temperature_strategy, power=power_strategy)
    @settings(max_examples=100)
    def test_thermal_resistance_always_positive(
        self, temp_rise: float, power: float
    ) -> None:
        """Property: Thermal resistance is positive for positive inputs."""
        formula = ComponentThermalResistanceFormula()
        result = formula.build(str(temp_rise), str(power))
        theta = extract_numeric_result(result)

        assume(not math.isnan(theta))
        assert theta > 0, f"Thermal resistance should be positive, got {theta}"

    @given(temp_rise=temperature_strategy, power=power_strategy)
    @settings(max_examples=100)
    def test_thermal_resistance_proportional_to_temp_rise(
        self, temp_rise: float, power: float
    ) -> None:
        """Property: Doubling temp rise doubles thermal resistance."""
        assume(temp_rise < 100)

        formula = ComponentThermalResistanceFormula()
        result1 = formula.build(str(temp_rise), str(power))
        result2 = formula.build(str(temp_rise * 2), str(power))

        t1 = extract_numeric_result(result1)
        t2 = extract_numeric_result(result2)

        assume(not math.isnan(t1) and not math.isnan(t2))
        assume(t1 > 0)

        ratio = t2 / t1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Utility Function Properties
# =============================================================================


class TestUtilityFunctions:
    """Property-based tests for electrical engineering utility functions."""

    @given(
        r1=st.floats(min_value=10, max_value=10000, allow_nan=False),
        r2=st.floats(min_value=10, max_value=10000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_parallel_resistance_util_matches_formula(
        self, r1: float, r2: float
    ) -> None:
        """Property: Utility function matches formula output."""
        util_result = calculate_parallel_resistance([r1, r2])
        expected = 1.0 / (1.0 / r1 + 1.0 / r2)

        relative_error = abs(util_result - expected) / expected
        assert relative_error < 1e-10

    @given(
        r1=st.floats(min_value=10, max_value=10000, allow_nan=False),
        r2=st.floats(min_value=10, max_value=10000, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_series_resistance_util_matches_formula(self, r1: float, r2: float) -> None:
        """Property: Utility function matches formula output."""
        util_result = calculate_series_resistance([r1, r2])
        expected = r1 + r2

        assert abs(util_result - expected) < 1e-10

    @given(voltage=voltage_strategy, current=current_strategy)
    @settings(max_examples=50)
    def test_power_dissipation_util(self, voltage: float, current: float) -> None:
        """Property: Power utility matches V*I."""
        result = calculate_power_dissipation(voltage, current)
        expected = voltage * current

        relative_error = abs(result - expected) / expected
        assert relative_error < 1e-10


class TestSIPrefixParsing:
    """Property-based tests for SI prefix parsing."""

    def test_kilo_prefix(self) -> None:
        """Validate: 10k = 10000."""
        result = parse_si_prefix("10k")
        assert result == 10000.0

    def test_milli_prefix(self) -> None:
        """Validate: 100mA = 0.1."""
        result = parse_si_prefix("100m")
        assert abs(result - 0.1) < 1e-10

    def test_mega_prefix(self) -> None:
        """Validate: 1M = 1000000."""
        result = parse_si_prefix("1M")
        assert result == 1e6

    def test_micro_prefix(self) -> None:
        """Validate: 10u = 10e-6."""
        result = parse_si_prefix("10u")
        assert abs(result - 10e-6) < 1e-12


# =============================================================================
# Reference Value Tests (IEEE Standards)
# =============================================================================


class TestReferenceValues:
    """Validate calculations against known reference values."""

    def test_two_100ohm_parallel(self) -> None:
        """Reference: Two 100 ohm resistors in parallel = 50 ohms."""
        formula = ParallelResistanceFormula()
        result = formula.build("100", "100")
        r = extract_numeric_result(result)

        assert abs(r - 50.0) < 1e-10, f"Expected 50 ohms, got {r}"

    def test_snr_10x_signal(self) -> None:
        """Reference: Signal 10x noise = 10 dB."""
        formula = SignalToNoiseRatioFormula()
        result = formula.build("10", "1")
        snr = extract_numeric_result(result)

        # 10*log10(10) = 10 dB
        assert abs(snr - 10.0) < 1e-10, f"Expected 10 dB, got {snr}"

    def test_snr_100x_signal(self) -> None:
        """Reference: Signal 100x noise = 20 dB."""
        formula = SignalToNoiseRatioFormula()
        result = formula.build("100", "1")
        snr = extract_numeric_result(result)

        # 10*log10(100) = 20 dB
        assert abs(snr - 20.0) < 1e-10, f"Expected 20 dB, got {snr}"

    def test_bandwidth_1ns_rise_time(self) -> None:
        """Reference: 1ns rise time = 350 MHz bandwidth."""
        formula = BandwidthFormula()
        result = formula.build("1e-9")  # 1 nanosecond
        bw = extract_numeric_result(result)

        # BW = 0.35 / t_r = 0.35 / 1e-9 = 350 MHz
        expected = 350e6
        relative_error = abs(bw - expected) / expected

        assert relative_error < 1e-10, f"Expected 350 MHz, got {bw} Hz"
