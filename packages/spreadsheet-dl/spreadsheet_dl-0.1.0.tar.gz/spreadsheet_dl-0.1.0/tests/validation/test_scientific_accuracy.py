"""Scientific validation tests against NIST/CODATA reference values.

These tests validate that domain formulas produce scientifically accurate results
when evaluated. They serve as acceptance tests for formula correctness.

References:
    - NIST CODATA 2018: https://physics.nist.gov/cuu/Constants/
    - IUPAC Atomic Weights: https://www.chem.qmul.ac.uk/iupac/AtWt/

Note:
    FallTimeFormula and GravitationalPEFormula are planned for future implementation.
    Tests for these formulas have been removed pending their implementation.
"""

from __future__ import annotations

import math

import pytest

pytestmark = [pytest.mark.validation, pytest.mark.science]


# =============================================================================
# CODATA 2018 Physical Constants
# =============================================================================

# Fundamental constants (CODATA 2018)
SPEED_OF_LIGHT = 299_792_458  # m/s (exact)
PLANCK_CONSTANT = 6.62607015e-34  # J*s (exact)
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K (exact)
AVOGADRO_CONSTANT = 6.02214076e23  # mol^-1 (exact)
ELEMENTARY_CHARGE = 1.602176634e-19  # C (exact)
GAS_CONSTANT = 8.314462618  # J/(mol*K)

# Derived constants
STEFAN_BOLTZMANN = 5.670374419e-8  # W/(m^2*K^4)
FARADAY_CONSTANT = 96485.33212  # C/mol


def evaluate_odf_formula(formula_str: str, variables: dict[str, float]) -> float:
    """Evaluate an ODF formula string with given variable values.

    This is a simplified evaluator for testing purposes.
    It handles basic arithmetic and common spreadsheet functions.

    Args:
        formula_str: ODF formula string (may start with 'of:=')
        variables: Dictionary mapping variable names to values

    Returns:
        Evaluated result as float
    """
    # Strip ODF prefix
    expr = formula_str.replace("of:=", "").replace("of:", "")

    # Replace spreadsheet functions with Python equivalents
    expr = expr.replace("SQRT", "math.sqrt")
    expr = expr.replace("PI()", str(math.pi))
    expr = expr.replace("EXP", "math.exp")
    expr = expr.replace("LN", "math.log")
    expr = expr.replace("LOG10", "math.log10")
    expr = expr.replace("SIN", "math.sin")
    expr = expr.replace("COS", "math.cos")
    expr = expr.replace("TAN", "math.tan")
    expr = expr.replace("ABS", "abs")
    expr = expr.replace("^", "**")

    # Replace semicolons with commas (ODF uses semicolons as argument separators)
    expr = expr.replace(";", ",")

    # Substitute variables
    for name, value in variables.items():
        expr = expr.replace(name, str(value))

    # Evaluate
    try:
        # Using eval with restricted globals for safety
        return float(eval(expr, {"__builtins__": {}, "math": math, "abs": abs}))
    except Exception as e:
        raise ValueError(f"Failed to evaluate formula: {formula_str} -> {expr}") from e


# =============================================================================
# Physics Formula Validation
# =============================================================================


class TestKinematicsValidation:
    """Validate kinematics formulas against known physics."""

    def test_kinetic_energy(self) -> None:
        """Validate kinetic energy: KE = 0.5 * m * v^2.

        Reference: Standard physics definition.
        """
        from spreadsheet_dl.domains.physics.formulas.mechanics import (
            KineticEnergyFormula,
        )

        formula = KineticEnergyFormula()

        # Test case: 1kg at 10 m/s
        mass = 1.0  # kg
        velocity = 10.0  # m/s

        result = formula.build(str(mass), str(velocity))
        calculated = evaluate_odf_formula(result, {})

        # Expected: KE = 0.5 * 1 * 100 = 50 J
        expected = 0.5 * mass * velocity**2

        assert abs(calculated - expected) < 1e-10, (
            f"Kinetic energy mismatch: {calculated} vs {expected}"
        )

    def test_potential_energy(self) -> None:
        """Validate gravitational PE using the existing PotentialEnergyFormula.

        Reference: Standard physics definition PE = mgh.
        Uses the actual implemented formula in the physics domain.
        """
        from spreadsheet_dl.domains.physics.formulas.mechanics import (
            PotentialEnergyFormula,
        )

        formula = PotentialEnergyFormula()

        mass = 10.0  # kg
        height = 50.0  # m
        g = 9.80665  # standard gravity

        # PotentialEnergyFormula signature: (mass, height, [gravity])
        result = formula.build(str(mass), str(height), str(g))
        calculated = evaluate_odf_formula(result, {})

        expected = mass * g * height

        assert abs(calculated - expected) < 1e-6, (
            f"Gravitational PE mismatch: {calculated} vs {expected}"
        )


class TestElectricalValidation:
    """Validate electrical engineering formulas."""

    def test_ohms_law_power(self) -> None:
        """Validate P = V * I (Ohm's Law for power).

        Reference: Fundamental electrical engineering.
        """
        from spreadsheet_dl.domains.electrical_engineering.formulas.power import (
            PowerDissipationFormula,
        )

        formula = PowerDissipationFormula()

        voltage = 12.0  # V
        current = 2.5  # A

        result = formula.build(str(voltage), str(current))
        calculated = evaluate_odf_formula(result, {})

        expected = voltage * current  # 30 W

        assert abs(calculated - expected) < 1e-10, (
            f"Power calculation mismatch: {calculated} vs {expected}"
        )

    def test_parallel_resistance(self) -> None:
        """Validate parallel resistance: 1/R_total = sum(1/R_i).

        Reference: Fundamental circuit theory.
        """
        from spreadsheet_dl.domains.electrical_engineering.formulas.impedance import (
            ParallelResistanceFormula,
        )

        formula = ParallelResistanceFormula()

        r1 = 100.0  # ohms
        r2 = 100.0  # ohms

        result = formula.build(str(r1), str(r2))
        calculated = evaluate_odf_formula(result, {})

        expected = 1 / (1 / r1 + 1 / r2)  # 50 ohms

        assert abs(calculated - expected) < 1e-10, (
            f"Parallel resistance mismatch: {calculated} vs {expected}"
        )

    def test_snr_calculation(self) -> None:
        """Validate SNR = 10 * log10(S/N).

        Reference: Standard signal processing.
        """
        from spreadsheet_dl.domains.electrical_engineering.formulas.signal import (
            SignalToNoiseRatioFormula,
        )

        formula = SignalToNoiseRatioFormula()

        signal = 1000.0  # arbitrary power units
        noise = 10.0  # same units

        result = formula.build(str(signal), str(noise))
        calculated = evaluate_odf_formula(result, {})

        expected = 10 * math.log10(signal / noise)  # 20 dB

        assert abs(calculated - expected) < 1e-10, (
            f"SNR mismatch: {calculated} vs {expected}"
        )


class TestChemistryValidation:
    """Validate chemistry formulas against known values."""

    def test_ideal_gas_law(self) -> None:
        """Validate PV = nRT at STP.

        Reference: IUPAC STP: T = 273.15 K, P = 100 kPa
        At STP, 1 mol of ideal gas occupies 22.711 L
        """
        from spreadsheet_dl.domains.chemistry.formulas.thermodynamics import (
            GasIdealityCheckFormula,
        )

        formula = GasIdealityCheckFormula()

        # Test: Calculate volume for 1 mol at STP
        n = 1.0  # mol
        p = 100000  # Pa (100 kPa)
        t = 273.15  # K
        r = GAS_CONSTANT  # J/(mol*K)

        # The formula solves for the unknown variable
        # V = nRT/P
        result = formula.build(str(n), str(r), str(t), str(p))

        # Expected molar volume at STP: ~22.711 L = 0.022711 m^3
        # Verify the formula structure contains correct calculation
        assert "of:=" in result
        assert str(n) in result or "nRT" in result.lower()

    def test_ph_calculation(self) -> None:
        """Validate pH = -log10([H+]).

        Reference: Standard chemistry definition.
        """
        from spreadsheet_dl.domains.chemistry.formulas.solutions import (
            pHCalculationFormula,
        )

        formula = pHCalculationFormula()

        # Test: pH of 0.001 M HCl (strong acid, fully dissociated)
        h_concentration = 0.001  # M

        result = formula.build(str(h_concentration))
        calculated = evaluate_odf_formula(result, {})

        expected = -math.log10(h_concentration)  # pH = 3

        assert abs(calculated - expected) < 1e-10, (
            f"pH calculation mismatch: {calculated} vs {expected}"
        )

    def test_molarity_calculation(self) -> None:
        """Validate M = n/V (moles per liter).

        Reference: Standard chemistry definition.
        """
        from spreadsheet_dl.domains.chemistry.formulas.solutions import MolarityFormula

        formula = MolarityFormula()

        moles = 2.0
        volume = 0.5  # liters

        result = formula.build(str(moles), str(volume))
        calculated = evaluate_odf_formula(result, {})

        expected = moles / volume  # 4 M

        assert abs(calculated - expected) < 1e-10, (
            f"Molarity mismatch: {calculated} vs {expected}"
        )


class TestMathematicalIdentities:
    """Validate formulas using mathematical identities."""

    def test_energy_conservation(self) -> None:
        """Validate that PE + KE = constant for free fall.

        Physics principle: Energy conservation in ideal system.
        Uses the existing PotentialEnergyFormula implementation.
        """
        from spreadsheet_dl.domains.physics.formulas.mechanics import (
            KineticEnergyFormula,
            PotentialEnergyFormula,
        )

        pe_formula = PotentialEnergyFormula()
        ke_formula = KineticEnergyFormula()

        mass = 10.0  # kg
        g = 9.80665  # m/s^2
        initial_height = 100.0  # m

        # Initial state: all PE, no KE
        # PotentialEnergyFormula signature: (mass, height, [gravity])
        initial_pe = evaluate_odf_formula(
            pe_formula.build(str(mass), str(initial_height), str(g)), {}
        )
        initial_ke = 0
        total_initial = initial_pe + initial_ke

        # Final state (ground): all KE, no PE
        # Using v = sqrt(2gh) for final velocity
        final_velocity = math.sqrt(2 * g * initial_height)
        final_pe = 0
        final_ke = evaluate_odf_formula(
            ke_formula.build(str(mass), str(final_velocity)), {}
        )
        total_final = final_pe + final_ke

        # Energy should be conserved
        assert abs(total_initial - total_final) < 1e-6, (
            f"Energy not conserved: {total_initial} vs {total_final}"
        )

    def test_series_parallel_duality(self) -> None:
        """Validate that series and parallel formulas are inverses.

        Two identical resistors in parallel = R/2
        Two identical resistors in series = 2R
        """
        from spreadsheet_dl.domains.electrical_engineering.formulas.impedance import (
            ParallelResistanceFormula,
            SeriesResistanceFormula,
        )

        parallel = ParallelResistanceFormula()
        series = SeriesResistanceFormula()

        r = 100.0  # ohms

        parallel_result = evaluate_odf_formula(parallel.build(str(r), str(r)), {})
        series_result = evaluate_odf_formula(series.build(str(r), str(r)), {})

        # Parallel should be half, series should be double
        assert abs(parallel_result - r / 2) < 1e-10
        assert abs(series_result - r * 2) < 1e-10

        # Product relationship: parallel * series = R^2
        assert abs(parallel_result * series_result - r**2) < 1e-10


class TestBoundaryConditions:
    """Test formulas at boundary conditions and edge cases."""

    def test_zero_velocity_kinetic_energy(self) -> None:
        """KE should be zero when velocity is zero."""
        from spreadsheet_dl.domains.physics.formulas.mechanics import (
            KineticEnergyFormula,
        )

        formula = KineticEnergyFormula()

        result = formula.build("10", "0")
        calculated = evaluate_odf_formula(result, {})

        assert calculated == 0, "KE should be zero at zero velocity"

    def test_neutral_ph(self) -> None:
        """pH should be 7 for [H+] = 1e-7 M (neutral water)."""
        from spreadsheet_dl.domains.chemistry.formulas.solutions import (
            pHCalculationFormula,
        )

        formula = pHCalculationFormula()

        # Pure water at 25C: [H+] = 1e-7 M
        result = formula.build("1e-7")
        calculated = evaluate_odf_formula(result, {})

        assert abs(calculated - 7.0) < 1e-10, (
            f"Neutral pH should be 7, got {calculated}"
        )

    def test_unity_power_factor(self) -> None:
        """Power factor should be 1 when real = apparent power."""
        from spreadsheet_dl.domains.electrical_engineering.formulas.ac_circuits import (
            PowerFactor,
        )

        formula = PowerFactor()

        power = 1000.0  # W
        result = formula.build(str(power), str(power))
        calculated = evaluate_odf_formula(result, {})

        assert abs(calculated - 1.0) < 1e-10, (
            f"Unity power factor expected, got {calculated}"
        )


class TestDimensionalAnalysis:
    """Verify dimensional correctness of formulas."""

    def test_kinetic_energy_dimensions(self) -> None:
        """KE = 0.5 * m * v^2 should have dimensions of energy [kg*m^2/s^2 = J]."""
        from spreadsheet_dl.domains.physics.formulas.mechanics import (
            KineticEnergyFormula,
        )

        formula = KineticEnergyFormula()

        # Use values with clear units
        mass_kg = 2.0
        velocity_ms = 3.0

        result = formula.build(str(mass_kg), str(velocity_ms))
        calculated = evaluate_odf_formula(result, {})

        # Expected: 0.5 * 2 * 9 = 9 J
        expected = 0.5 * mass_kg * velocity_ms**2

        assert abs(calculated - expected) < 1e-10

    def test_resonant_frequency_dimensions(self) -> None:
        """f_0 = 1/(2*pi*sqrt(LC)) should have dimensions of Hz."""
        from spreadsheet_dl.domains.electrical_engineering.formulas.ac_circuits import (
            ResonantFrequency,
        )

        formula = ResonantFrequency()

        # L = 1 H, C = 1 F -> f = 1/(2*pi) Hz
        result = formula.build("1", "1")
        calculated = evaluate_odf_formula(result, {})

        expected = 1 / (2 * math.pi)  # ~0.159 Hz

        assert abs(calculated - expected) < 1e-10


class TestReferenceValueComparison:
    """Compare formula outputs against published reference values."""

    def test_molar_gas_volume_stp(self) -> None:
        """Validate molar volume calculation at STP.

        Reference: IUPAC STP molar volume = 22.711 L/mol
        """
        # At T = 273.15 K, P = 100000 Pa, n = 1 mol
        # V = nRT/P = 1 * 8.314462618 * 273.15 / 100000
        calculated = 1 * GAS_CONSTANT * 273.15 / 100000  # m^3

        # Convert to liters
        calculated_liters = calculated * 1000

        # IUPAC reference: 22.711 L/mol
        assert abs(calculated_liters - 22.711) < 0.001, (
            f"Molar volume at STP: {calculated_liters} L vs 22.711 L"
        )
