# Testing Philosophy

This document explains SpreadsheetDL's testing philosophy and the rationale behind our test strategy.

## Overview

SpreadsheetDL uses a **property-based testing** approach combined with **scientific validation** to ensure formula correctness. This strategy prioritizes tests that verify actual behavior over superficial checks.

## Testing Pyramid

```
                    /\
                   /  \
                  / E2E \
                 /--------\
                /Integration\
               /--------------\
              / Property-Based  \
             /--------------------\
            /  Scientific Validation \
           /--------------------------\
          /      Unit Tests (Core)      \
         /--------------------------------\
```

### Layer Descriptions

1. **Unit Tests (Core)**: Test individual functions in isolation
2. **Scientific Validation**: Verify formulas against NIST/CODATA reference values
3. **Property-Based Tests**: Use Hypothesis to test mathematical properties
4. **Integration Tests**: Test file format roundtrips (ODS, XLSX, CSV)
5. **E2E Tests**: Full workflow testing with real spreadsheet operations

## Property-Based Testing

We use [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing, which generates thousands of test cases automatically.

### Why Property-Based Testing?

Traditional example-based tests verify specific inputs:

```python
# Example-based (limited coverage)
def test_kinetic_energy():
    assert kinetic_energy(10, 5) == 125
```

Property-based tests verify mathematical properties across many inputs:

```python
# Property-based (comprehensive coverage)
@given(st.floats(min_value=0.1, max_value=1e6))
def test_kinetic_energy_non_negative(mass):
    """KE is always non-negative for any positive mass."""
    result = kinetic_energy(mass, 10)
    assert result >= 0
```

### Properties We Test

| Property                    | Description                  | Example                  |
| --------------------------- | ---------------------------- | ------------------------ |
| **Non-negativity**          | Results that must be >= 0    | Energy, resistance, mass |
| **Symmetry**                | Order-independent operations | Parallel resistance      |
| **Inverse relationships**   | Operations that cancel       | Series/parallel duality  |
| **Boundary behavior**       | Behavior at limits           | Zero velocity KE = 0     |
| **Conservation laws**       | Conserved quantities         | Energy conservation      |
| **Dimensional consistency** | Units work out correctly     | KE has energy dimensions |

### Hypothesis Configuration

Our Hypothesis settings in `pyproject.toml`:

```toml
[tool.hypothesis]
profile = "default"

[tool.hypothesis.profiles.default]
max_examples = 100
deadline = 5000

[tool.hypothesis.profiles.ci]
max_examples = 200
deadline = 10000
```

## Scientific Validation

Domain formulas must produce scientifically accurate results. We validate against:

- **NIST CODATA 2018**: Physical constants
- **IUPAC**: Chemical data and atomic weights
- **IEEE**: Electrical engineering standards

### Validation Test Structure

```python
class TestPhysicsValidation:
    """Validate physics formulas against known constants."""

    def test_free_fall_standard_gravity(self):
        """Validate against g_n = 9.80665 m/s^2 (CGPM 1901)."""
        # Test implementation...
```

### Reference Values

Key constants used in validation (CODATA 2018):

| Constant           | Value          | Unit       |
| ------------------ | -------------- | ---------- |
| Speed of light     | 299,792,458    | m/s        |
| Planck constant    | 6.62607015e-34 | J\*s       |
| Boltzmann constant | 1.380649e-23   | J/K        |
| Gas constant       | 8.314462618    | J/(mol\*K) |
| Standard gravity   | 9.80665        | m/s^2      |

## What We Test

### Do Test

- **Mathematical correctness**: Formulas produce correct results
- **Physical properties**: Energy conservation, symmetry, bounds
- **Boundary conditions**: Zero values, limits, edge cases
- **Error handling**: Invalid inputs raise appropriate errors
- **ODF compliance**: Formulas have correct `of:=` prefix

### Do Not Test

- **String matching**: Checking exact formula output strings
- **None checks**: Verifying objects are not None
- **Type existence**: Checking if classes exist
- **Trivial getters**: Testing simple property access

## Test Organization

```
tests/
├── domains/
│   ├── physics/
│   │   ├── test_mechanics.py           # Unit tests
│   │   ├── test_mechanics_properties.py # Property tests
│   │   └── test_kinematics_properties.py
│   ├── chemistry/
│   │   ├── test_chemistry.py
│   │   └── test_stoichiometry_properties.py
│   └── electrical_engineering/
│       ├── test_electrical.py
│       └── test_circuits_properties.py
├── integration/
│   ├── test_xlsx_roundtrip.py
│   ├── test_odf_roundtrip.py
│   └── test_csv_roundtrip.py
└── validation/
    └── test_scientific_accuracy.py
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run property-based tests only
uv run pytest -m property

# Run scientific validation
uv run pytest -m validation

# Run with verbose Hypothesis output
uv run pytest --hypothesis-show-statistics

# Run specific domain
uv run pytest tests/domains/physics/

# Run with coverage
uv run pytest --cov=spreadsheet_dl --cov-report=html
```

## Coverage Targets

| Category        | Target | Rationale             |
| --------------- | ------ | --------------------- |
| Overall         | 70-75% | Quality over quantity |
| Core modules    | 90%+   | Critical path code    |
| Domain formulas | 85%+   | Scientific accuracy   |
| Integration     | 80%+   | File format handling  |

## Test Quality Metrics

Beyond coverage, we track:

1. **Mutation score** (via mutmut): >80% target
2. **Property test examples**: 100-200 per property
3. **Scientific validation coverage**: All CODATA constants
4. **Integration test formats**: ODS, XLSX, CSV, PDF

## Writing New Tests

### Property Test Template

```python
from hypothesis import given, strategies as st
import pytest

class TestNewFormulaProperties:
    """Property-based tests for NewFormula."""

    @given(st.floats(min_value=0.1, max_value=1e6, allow_nan=False))
    def test_result_non_negative(self, value):
        """Result should always be non-negative."""
        formula = NewFormula()
        result = evaluate(formula.build(str(value)))
        assert result >= 0

    @given(
        st.floats(min_value=0.1, max_value=1e3),
        st.floats(min_value=0.1, max_value=1e3),
    )
    def test_symmetry_property(self, a, b):
        """Order should not affect result."""
        formula = SymmetricFormula()
        result1 = evaluate(formula.build(str(a), str(b)))
        result2 = evaluate(formula.build(str(b), str(a)))
        assert abs(result1 - result2) < 1e-10
```

### Validation Test Template

```python
class TestNewDomainValidation:
    """Validate against reference standards."""

    def test_against_nist_value(self):
        """Validate against NIST CODATA 2018 reference.

        Reference: https://physics.nist.gov/cuu/Constants/
        """
        formula = PhysicsFormula()
        result = evaluate(formula.build("inputs"))

        NIST_REFERENCE = 1.234567e-10  # From CODATA 2018

        assert abs(result - NIST_REFERENCE) / NIST_REFERENCE < 1e-6
```

## Avoiding Anti-Patterns

### Bad: Shallow String Tests

```python
# DO NOT DO THIS
def test_formula_output():
    formula = SomeFormula()
    result = formula.build("10", "20")
    assert result is not None  # Useless
    assert "10" in result      # Shallow
    assert result.startswith("of:=")  # Only checks prefix
```

### Good: Property-Based Validation

```python
# DO THIS INSTEAD
@given(st.floats(min_value=0.1, max_value=1e6))
def test_formula_correctness(self, value):
    formula = SomeFormula()
    result = evaluate(formula.build(str(value)))
    # Test actual mathematical property
    assert result == expected_calculation(value)
```

## Continuous Integration

Tests run on every PR with:

1. Full test suite with coverage
2. Extended Hypothesis examples (CI profile)
3. Mutation testing on changed files
4. Scientific validation suite

## Further Reading

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing with Python](https://hypothesis.works/articles/what-is-hypothesis/)
- [NIST CODATA](https://physics.nist.gov/cuu/Constants/)
- [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
