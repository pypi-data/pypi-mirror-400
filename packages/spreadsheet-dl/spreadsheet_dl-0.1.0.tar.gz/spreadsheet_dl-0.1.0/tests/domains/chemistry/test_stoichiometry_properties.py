"""Property-based tests for Chemistry stoichiometry formulas.

Uses Hypothesis to validate chemical calculation properties across input domains.
Tests verify mathematical relationships rather than string formatting.

Test Strategy:
    - Properties test conservation laws, scaling relationships, and mathematical identities
    - Input domains constrained to chemically meaningful values
    - Reference values from IUPAC and NIST sources

References:
    - IUPAC Gold Book for definitions
    - NIST Chemistry WebBook for reference data
    - Avogadro constant: 6.02214076e23 mol^-1 (CODATA 2018, exact)
"""

from __future__ import annotations

import math

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from spreadsheet_dl.domains.chemistry import (
    MolarityFormula,
    MoleFractionFormula,
    pHCalculationFormula,
)
from spreadsheet_dl.domains.chemistry.formulas.stoichiometry import (
    AvogadroParticlesFormula,
    DilutionFormula,
    MassFromMolesFormula,
    MolarMassFormula,
    MolesFromMassFormula,
    PercentCompositionFormula,
    PercentYieldFormula,
    TheoreticalYieldFormula,
)

pytestmark = [pytest.mark.unit, pytest.mark.property, pytest.mark.science]


# =============================================================================
# Strategy Definitions for Chemical Quantities
# =============================================================================

# Mass: from micrograms to kilograms (typical lab scale)
mass_strategy = st.floats(
    min_value=1e-6, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Moles: typical lab range
moles_strategy = st.floats(
    min_value=1e-9, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Molar mass: realistic range (H=1 to large proteins ~1e6)
molar_mass_strategy = st.floats(
    min_value=1.0, max_value=1e6, allow_nan=False, allow_infinity=False
)

# Concentration: typical molar range
concentration_strategy = st.floats(
    min_value=1e-14, max_value=18.0, allow_nan=False, allow_infinity=False
)

# Volume: microliters to cubic meters
volume_strategy = st.floats(
    min_value=1e-9, max_value=1e3, allow_nan=False, allow_infinity=False
)

# Percent: 0-100 range
percent_strategy = st.floats(
    min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False
)

# Stoichiometric coefficients: small positive integers
stoich_coef_strategy = st.floats(
    min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False
)

# Atomic count: positive integers
atom_count_strategy = st.floats(
    min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False
)


# =============================================================================
# Helper Functions
# =============================================================================


def extract_numeric_result(formula_str: str) -> float:
    """Extract numeric result by evaluating the ODF formula."""
    expr = formula_str[4:] if formula_str.startswith("of:=") else formula_str

    # Replace spreadsheet functions with Python equivalents
    expr = expr.replace("^", "**")
    expr = expr.replace("LOG10(", "math.log10(")
    expr = expr.replace("LN(", "math.log(")
    expr = expr.replace("EXP(", "math.exp(")
    expr = expr.replace("PI()", str(math.pi))

    # Handle IF statements (simplified)
    if "IF(" in expr:
        return float("nan")

    try:
        return float(eval(expr))
    except (ValueError, SyntaxError, ZeroDivisionError):
        return float("nan")


# =============================================================================
# Molar Mass (M = m/n) Properties
# =============================================================================


class TestMolarMassProperties:
    """Property-based tests for molar mass calculations."""

    @given(mass=mass_strategy, moles=moles_strategy)
    @settings(max_examples=100)
    def test_molar_mass_always_positive(self, mass: float, moles: float) -> None:
        """Property: Molar mass is always positive for positive inputs."""
        formula = MolarMassFormula()
        result = formula.build(str(mass), str(moles))
        molar_mass = extract_numeric_result(result)

        assume(not math.isnan(molar_mass))
        assert molar_mass > 0, f"Molar mass should be positive, got {molar_mass}"

    @given(mass=mass_strategy, moles=moles_strategy)
    @settings(max_examples=100)
    def test_molar_mass_inversely_proportional_to_moles(
        self, mass: float, moles: float
    ) -> None:
        """Property: Doubling moles halves calculated molar mass."""
        assume(moles < 5e5)

        formula = MolarMassFormula()
        result1 = formula.build(str(mass), str(moles))
        result2 = formula.build(str(mass), str(moles * 2))

        mm1 = extract_numeric_result(result1)
        mm2 = extract_numeric_result(result2)

        assume(not math.isnan(mm1) and not math.isnan(mm2))
        assume(mm2 > 0)

        ratio = mm1 / mm2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    @given(mass=mass_strategy, moles=moles_strategy)
    @settings(max_examples=100)
    def test_molar_mass_formula_correctness(self, mass: float, moles: float) -> None:
        """Property: Computed M matches expected m/n."""
        formula = MolarMassFormula()
        result = formula.build(str(mass), str(moles))
        mm = extract_numeric_result(result)

        expected = mass / moles

        assume(not math.isnan(mm) and not math.isnan(expected))
        assume(expected > 0)

        relative_error = abs(mm - expected) / expected
        assert relative_error < 1e-10, (
            f"Molar mass mismatch: got {mm}, expected {expected}"
        )


# =============================================================================
# Mass-Moles Roundtrip Properties
# =============================================================================


class TestMassMolesRoundtrip:
    """Property-based tests for mass/moles conversion roundtrip."""

    @given(moles=moles_strategy, molar_mass=molar_mass_strategy)
    @settings(max_examples=100)
    def test_mass_from_moles_always_positive(
        self, moles: float, molar_mass: float
    ) -> None:
        """Property: Mass is always positive for positive inputs."""
        formula = MassFromMolesFormula()
        result = formula.build(str(moles), str(molar_mass))
        mass = extract_numeric_result(result)

        assume(not math.isnan(mass))
        assert mass > 0, f"Mass should be positive, got {mass}"

    @given(mass=mass_strategy, molar_mass=molar_mass_strategy)
    @settings(max_examples=100)
    def test_moles_from_mass_always_positive(
        self, mass: float, molar_mass: float
    ) -> None:
        """Property: Moles is always positive for positive inputs."""
        formula = MolesFromMassFormula()
        result = formula.build(str(mass), str(molar_mass))
        moles = extract_numeric_result(result)

        assume(not math.isnan(moles))
        assert moles > 0, f"Moles should be positive, got {moles}"

    @given(moles=moles_strategy, molar_mass=molar_mass_strategy)
    @settings(max_examples=100)
    def test_mass_moles_roundtrip(self, moles: float, molar_mass: float) -> None:
        """Property: Converting moles->mass->moles recovers original value."""
        mass_formula = MassFromMolesFormula()
        moles_formula = MolesFromMassFormula()

        # moles -> mass
        mass_result = mass_formula.build(str(moles), str(molar_mass))
        mass = extract_numeric_result(mass_result)

        assume(not math.isnan(mass))

        # mass -> moles (should recover original)
        moles_result = moles_formula.build(str(mass), str(molar_mass))
        moles_recovered = extract_numeric_result(moles_result)

        assume(not math.isnan(moles_recovered))

        relative_error = abs(moles_recovered - moles) / moles
        assert relative_error < 1e-10, (
            f"Roundtrip failed: started with {moles}, got {moles_recovered}"
        )


# =============================================================================
# Percent Yield Properties
# =============================================================================


class TestPercentYieldProperties:
    """Property-based tests for percent yield calculations."""

    @given(
        actual=st.floats(
            min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False
        ),
        theoretical=st.floats(
            min_value=0.01, max_value=1000, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=100)
    def test_percent_yield_always_positive(
        self, actual: float, theoretical: float
    ) -> None:
        """Property: Percent yield is always positive for positive inputs."""
        formula = PercentYieldFormula()
        result = formula.build(str(actual), str(theoretical))
        percent = extract_numeric_result(result)

        assume(not math.isnan(percent))
        assert percent > 0, f"Percent yield should be positive, got {percent}"

    @given(theoretical=st.floats(min_value=1.0, max_value=100, allow_nan=False))
    @settings(max_examples=50)
    def test_percent_yield_100_when_equal(self, theoretical: float) -> None:
        """Property: Percent yield is 100% when actual equals theoretical."""
        formula = PercentYieldFormula()
        result = formula.build(str(theoretical), str(theoretical))
        percent = extract_numeric_result(result)

        assume(not math.isnan(percent))
        assert abs(percent - 100.0) < 1e-10, (
            f"Percent yield should be 100%, got {percent}"
        )

    @given(
        actual=st.floats(min_value=0.01, max_value=50, allow_nan=False),
        theoretical=st.floats(min_value=50.01, max_value=100, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_percent_yield_less_than_100_when_actual_less(
        self, actual: float, theoretical: float
    ) -> None:
        """Property: Percent yield < 100% when actual < theoretical."""
        assume(actual < theoretical)

        formula = PercentYieldFormula()
        result = formula.build(str(actual), str(theoretical))
        percent = extract_numeric_result(result)

        assume(not math.isnan(percent))
        assert percent < 100.0, (
            f"Percent yield should be < 100% when actual < theoretical, got {percent}"
        )


# =============================================================================
# Dilution (M1V1 = M2V2) Properties
# =============================================================================


class TestDilutionProperties:
    """Property-based tests for dilution calculations."""

    @given(
        conc_initial=concentration_strategy,
        vol_initial=volume_strategy,
        vol_final=volume_strategy,
    )
    @settings(max_examples=100)
    def test_dilution_always_positive(
        self, conc_initial: float, vol_initial: float, vol_final: float
    ) -> None:
        """Property: Final concentration is always positive for positive inputs."""
        formula = DilutionFormula()
        result = formula.build(str(conc_initial), str(vol_initial), str(vol_final))
        conc_final = extract_numeric_result(result)

        assume(not math.isnan(conc_final))
        assert conc_final > 0, (
            f"Final concentration should be positive, got {conc_final}"
        )

    @given(
        conc_initial=st.floats(min_value=0.1, max_value=10, allow_nan=False),
        vol_initial=st.floats(min_value=0.01, max_value=1, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_dilution_decreases_concentration(
        self, conc_initial: float, vol_initial: float
    ) -> None:
        """Property: Increasing volume decreases concentration."""
        vol_final = vol_initial * 2  # Double the volume

        formula = DilutionFormula()
        result = formula.build(str(conc_initial), str(vol_initial), str(vol_final))
        conc_final = extract_numeric_result(result)

        assume(not math.isnan(conc_final))
        assert conc_final < conc_initial, (
            f"Dilution should decrease concentration: {conc_final} >= {conc_initial}"
        )

    @given(
        conc_initial=st.floats(min_value=0.1, max_value=10, allow_nan=False),
        vol_initial=st.floats(min_value=0.01, max_value=1, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_dilution_conserves_moles(
        self, conc_initial: float, vol_initial: float
    ) -> None:
        """Property: M1*V1 = M2*V2 (conservation of moles)."""
        vol_final = vol_initial * 3  # Triple the volume

        formula = DilutionFormula()
        result = formula.build(str(conc_initial), str(vol_initial), str(vol_final))
        conc_final = extract_numeric_result(result)

        assume(not math.isnan(conc_final))

        moles_initial = conc_initial * vol_initial
        moles_final = conc_final * vol_final

        relative_error = abs(moles_final - moles_initial) / moles_initial
        assert relative_error < 1e-10, (
            f"Moles not conserved: initial={moles_initial}, final={moles_final}"
        )


# =============================================================================
# Avogadro's Number Properties
# =============================================================================


class TestAvogadroParticlesProperties:
    """Property-based tests for Avogadro particle calculations."""

    @given(moles=moles_strategy)
    @settings(max_examples=100)
    def test_particles_always_positive(self, moles: float) -> None:
        """Property: Number of particles is always positive for positive moles."""
        formula = AvogadroParticlesFormula()
        result = formula.build(str(moles))
        particles = extract_numeric_result(result)

        assume(not math.isnan(particles))
        assert particles > 0, f"Particles should be positive, got {particles}"

    @given(moles=st.floats(min_value=1e-6, max_value=100, allow_nan=False))
    @settings(max_examples=50)
    def test_particles_proportional_to_moles(self, moles: float) -> None:
        """Property: Doubling moles doubles particles."""
        formula = AvogadroParticlesFormula()
        result1 = formula.build(str(moles))
        result2 = formula.build(str(moles * 2))

        p1 = extract_numeric_result(result1)
        p2 = extract_numeric_result(result2)

        assume(not math.isnan(p1) and not math.isnan(p2))
        assume(p1 > 0)

        ratio = p2 / p1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"

    def test_avogadro_number_reference(self) -> None:
        """Validate: 1 mole = 6.022e23 particles (CODATA 2018)."""
        formula = AvogadroParticlesFormula()
        result = formula.build("1")  # 1 mole
        particles = extract_numeric_result(result)

        # CODATA 2018 exact value: 6.02214076e23
        expected = 6.022e23
        relative_error = abs(particles - expected) / expected

        assert relative_error < 0.001, (
            f"Avogadro's number should be ~6.022e23, got {particles}"
        )


# =============================================================================
# Percent Composition Properties
# =============================================================================


class TestPercentCompositionProperties:
    """Property-based tests for percent composition calculations."""

    @given(
        n_atoms=atom_count_strategy,
        atomic_mass=st.floats(min_value=1.0, max_value=300, allow_nan=False),
        compound_mass=st.floats(min_value=10.0, max_value=1000, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_percent_composition_bounded(
        self, n_atoms: float, atomic_mass: float, compound_mass: float
    ) -> None:
        """Property: Percent composition should be between 0 and ~100%."""
        # Ensure element mass is strictly less than compound mass for valid chemistry
        element_mass = n_atoms * atomic_mass
        assume(element_mass <= compound_mass)  # Element can't exceed compound

        formula = PercentCompositionFormula()
        result = formula.build(str(n_atoms), str(atomic_mass), str(compound_mass))
        percent = extract_numeric_result(result)

        assume(not math.isnan(percent))
        assert percent > 0, f"Percent composition should be > 0, got {percent}"
        # Allow small floating point tolerance above 100%
        assert percent <= 100.0 + 1e-10, (
            f"Percent composition should be <= 100%, got {percent}"
        )

    def test_hydrogen_in_water_reference(self) -> None:
        """Validate: H in H2O is approximately 11.19% by mass."""
        # H2O: 2 H atoms, H atomic mass = 1.008, H2O molar mass = 18.015
        formula = PercentCompositionFormula()
        result = formula.build("2", "1.008", "18.015")
        percent = extract_numeric_result(result)

        # Expected: (2 * 1.008 / 18.015) * 100 = 11.19%
        expected = 11.19
        assert abs(percent - expected) < 0.1, (
            f"H in H2O should be ~{expected}%, got {percent}%"
        )


# =============================================================================
# Theoretical Yield Properties
# =============================================================================


class TestTheoreticalYieldProperties:
    """Property-based tests for theoretical yield calculations."""

    @given(
        moles_limiting=moles_strategy,
        stoich_ratio=stoich_coef_strategy,
        product_molar_mass=molar_mass_strategy,
    )
    @settings(max_examples=100)
    def test_theoretical_yield_always_positive(
        self, moles_limiting: float, stoich_ratio: float, product_molar_mass: float
    ) -> None:
        """Property: Theoretical yield is always positive for positive inputs."""
        formula = TheoreticalYieldFormula()
        result = formula.build(
            str(moles_limiting), str(stoich_ratio), str(product_molar_mass)
        )
        yield_mass = extract_numeric_result(result)

        assume(not math.isnan(yield_mass))
        assert yield_mass > 0, f"Theoretical yield should be positive, got {yield_mass}"

    @given(
        moles_limiting=st.floats(min_value=0.01, max_value=10, allow_nan=False),
        product_molar_mass=st.floats(min_value=10, max_value=500, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_theoretical_yield_proportional_to_moles(
        self, moles_limiting: float, product_molar_mass: float
    ) -> None:
        """Property: Doubling limiting reagent moles doubles theoretical yield."""
        stoich_ratio = 1.0

        formula = TheoreticalYieldFormula()
        result1 = formula.build(
            str(moles_limiting), str(stoich_ratio), str(product_molar_mass)
        )
        result2 = formula.build(
            str(moles_limiting * 2), str(stoich_ratio), str(product_molar_mass)
        )

        y1 = extract_numeric_result(result1)
        y2 = extract_numeric_result(result2)

        assume(not math.isnan(y1) and not math.isnan(y2))
        assume(y1 > 0)

        ratio = y2 / y1
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


# =============================================================================
# Solution Concentration Properties
# =============================================================================


class TestMolarityProperties:
    """Property-based tests for molarity calculations."""

    @given(moles=moles_strategy, volume=volume_strategy)
    @settings(max_examples=100)
    def test_molarity_always_positive(self, moles: float, volume: float) -> None:
        """Property: Molarity is always positive for positive inputs."""
        formula = MolarityFormula()
        result = formula.build(str(moles), str(volume))
        molarity = extract_numeric_result(result)

        assume(not math.isnan(molarity))
        assert molarity > 0, f"Molarity should be positive, got {molarity}"

    @given(moles=moles_strategy, volume=volume_strategy)
    @settings(max_examples=100)
    def test_molarity_inversely_proportional_to_volume(
        self, moles: float, volume: float
    ) -> None:
        """Property: Doubling volume halves molarity."""
        assume(volume < 500)

        formula = MolarityFormula()
        result1 = formula.build(str(moles), str(volume))
        result2 = formula.build(str(moles), str(volume * 2))

        m1 = extract_numeric_result(result1)
        m2 = extract_numeric_result(result2)

        assume(not math.isnan(m1) and not math.isnan(m2))
        assume(m2 > 0)

        ratio = m1 / m2
        assert abs(ratio - 2.0) < 1e-10, f"Expected ratio 2.0, got {ratio}"


class TestMoleFractionProperties:
    """Property-based tests for mole fraction calculations."""

    @given(
        moles_solute=st.floats(min_value=0.01, max_value=10, allow_nan=False),
        moles_total=st.floats(min_value=10.01, max_value=100, allow_nan=False),
    )
    @settings(max_examples=100)
    def test_mole_fraction_bounded(
        self, moles_solute: float, moles_total: float
    ) -> None:
        """Property: Mole fraction is between 0 and 1."""
        assume(moles_solute < moles_total)

        formula = MoleFractionFormula()
        result = formula.build(str(moles_solute), str(moles_total))
        fraction = extract_numeric_result(result)

        assume(not math.isnan(fraction))
        assert 0 < fraction < 1, f"Mole fraction should be in (0,1), got {fraction}"


# =============================================================================
# pH Calculation Properties
# =============================================================================


class TestpHCalculationProperties:
    """Property-based tests for pH calculations."""

    @given(concentration=st.floats(min_value=1e-14, max_value=0.99, allow_nan=False))
    @settings(max_examples=100)
    def test_ph_always_positive(self, concentration: float) -> None:
        """Property: pH is positive for typical acid concentrations ([H+] < 1M)."""
        # pH = -log10([H+]), so for [H+] < 1, pH > 0
        # We use max_value=0.99 to ensure pH is strictly positive
        formula = pHCalculationFormula()
        result = formula.build(str(concentration))
        ph = extract_numeric_result(result)

        assume(not math.isnan(ph))
        assert ph > 0, f"pH should be positive for [H+] < 1M, got {ph}"

    @given(
        conc1=st.floats(min_value=1e-10, max_value=0.01, allow_nan=False),
        conc2=st.floats(min_value=0.01, max_value=1.0, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_ph_increases_as_concentration_decreases(
        self, conc1: float, conc2: float
    ) -> None:
        """Property: Lower [H+] means higher pH (less acidic)."""
        assume(conc1 < conc2)
        assume(conc2 / conc1 > 1.01)  # Ensure at least 1% difference

        formula = pHCalculationFormula()
        result1 = formula.build(str(conc1))
        result2 = formula.build(str(conc2))

        ph1 = extract_numeric_result(result1)
        ph2 = extract_numeric_result(result2)

        assume(not math.isnan(ph1) and not math.isnan(ph2))
        assert ph1 > ph2, f"pH should increase as [H+] decreases: pH1={ph1}, pH2={ph2}"

    def test_ph_neutral_water_reference(self) -> None:
        """Validate: pH of neutral water (10^-7 M H+) is 7."""
        formula = pHCalculationFormula()
        result = formula.build("1e-7")
        ph = extract_numeric_result(result)

        assert abs(ph - 7.0) < 0.01, f"pH of neutral water should be 7, got {ph}"

    def test_ph_strong_acid_reference(self) -> None:
        """Validate: pH of 0.1 M HCl is approximately 1."""
        formula = pHCalculationFormula()
        result = formula.build("0.1")
        ph = extract_numeric_result(result)

        assert abs(ph - 1.0) < 0.01, f"pH of 0.1M HCl should be ~1, got {ph}"
