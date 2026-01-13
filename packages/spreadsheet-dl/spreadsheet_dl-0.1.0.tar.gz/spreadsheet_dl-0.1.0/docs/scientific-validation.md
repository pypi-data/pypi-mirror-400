# Scientific Validation

This document describes how SpreadsheetDL validates domain formulas against authoritative scientific references.

## Overview

SpreadsheetDL's domain plugins contain 317+ specialized formulas across physics, chemistry, electrical engineering, and other scientific domains. To ensure accuracy, we validate these formulas against:

- **NIST CODATA**: Internationally recommended values of fundamental physical constants
- **IUPAC**: International Union of Pure and Applied Chemistry standards
- **IEEE**: Electrical engineering standards and conventions

## Reference Standards

### CODATA 2018 Fundamental Constants

The following constants are used as reference values in validation tests:

| Constant                  | Symbol | Value           | Uncertainty | Unit         |
| ------------------------- | ------ | --------------- | ----------- | ------------ |
| Speed of light in vacuum  | c      | 299,792,458     | exact       | m/s          |
| Planck constant           | h      | 6.62607015e-34  | exact       | J\*s         |
| Elementary charge         | e      | 1.602176634e-19 | exact       | C            |
| Boltzmann constant        | k      | 1.380649e-23    | exact       | J/K          |
| Avogadro constant         | N_A    | 6.02214076e23   | exact       | mol^-1       |
| Molar gas constant        | R      | 8.314462618     | exact       | J/(mol\*K)   |
| Standard gravity          | g_n    | 9.80665         | exact       | m/s^2        |
| Stefan-Boltzmann constant | sigma  | 5.670374419e-8  | exact       | W/(m^2\*K^4) |
| Faraday constant          | F      | 96485.33212     | exact       | C/mol        |

Source: [NIST CODATA 2018](https://physics.nist.gov/cuu/Constants/)

### IUPAC Standard Conditions

| Condition            | Value              | Notes                      |
| -------------------- | ------------------ | -------------------------- |
| Standard Temperature | 273.15 K (0 C)     | IUPAC STP since 1982       |
| Standard Pressure    | 100,000 Pa (1 bar) | Changed from 1 atm in 1982 |
| Molar Volume at STP  | 22.711 L/mol       | For ideal gas              |

### IEEE/SI Derived Units

| Quantity             | Unit      | Definition  |
| -------------------- | --------- | ----------- |
| Energy               | Joule (J) | kg\*m^2/s^2 |
| Power                | Watt (W)  | J/s         |
| Electrical Potential | Volt (V)  | W/A         |
| Resistance           | Ohm       | V/A         |
| Capacitance          | Farad (F) | C/V         |
| Inductance           | Henry (H) | Wb/A        |

## Validation Categories

### 1. Physical Constants Validation

Verify that formulas using physical constants produce correct results:

```python
def test_ideal_gas_at_stp():
    """1 mol of ideal gas at STP occupies 22.711 L."""
    n = 1  # mol
    R = 8.314462618  # J/(mol*K) - CODATA 2018
    T = 273.15  # K - IUPAC STP
    P = 100000  # Pa - IUPAC STP

    V = n * R * T / P  # m^3
    V_liters = V * 1000

    assert abs(V_liters - 22.711) < 0.001
```

### 2. Mathematical Identity Validation

Verify formulas satisfy known mathematical relationships:

```python
def test_energy_conservation():
    """PE + KE = constant in ideal free fall."""
    # Initial: all potential energy
    # Final: all kinetic energy
    # Total should be conserved
```

### 3. Boundary Condition Validation

Verify correct behavior at physical limits:

```python
def test_zero_velocity_kinetic_energy():
    """KE = 0 when v = 0."""
    ke = kinetic_energy(mass=10, velocity=0)
    assert ke == 0

def test_neutral_ph():
    """pH = 7 for pure water at 25C."""
    ph = calculate_ph(h_concentration=1e-7)
    assert abs(ph - 7.0) < 1e-10
```

### 4. Dimensional Analysis

Verify formulas produce dimensionally correct results:

```python
def test_kinetic_energy_dimensions():
    """KE = 0.5*m*v^2 has dimensions [kg*m^2/s^2] = [J]."""
    # Mass in kg, velocity in m/s
    # Result should be in Joules
```

## Validation Test Structure

### Location

```
tests/validation/
├── __init__.py
└── test_scientific_accuracy.py
```

### Test Classes

| Class                          | Purpose                      |
| ------------------------------ | ---------------------------- |
| `TestKinematicsValidation`     | Classical mechanics formulas |
| `TestElectricalValidation`     | Circuit analysis formulas    |
| `TestChemistryValidation`      | Chemical calculations        |
| `TestMathematicalIdentities`   | Conservation laws, symmetry  |
| `TestBoundaryConditions`       | Edge case behavior           |
| `TestDimensionalAnalysis`      | Unit consistency             |
| `TestReferenceValueComparison` | NIST/CODATA values           |

### Running Validation Tests

```bash
# Run all validation tests
uv run pytest -m validation

# Run with verbose output
uv run pytest -m validation -v

# Run specific validation category
uv run pytest tests/validation/test_scientific_accuracy.py::TestChemistryValidation
```

## Formula Evaluation

For testing, we evaluate ODF formula strings to verify correctness:

```python
def evaluate_odf_formula(formula_str: str, variables: dict) -> float:
    """Evaluate an ODF formula for testing.

    Handles:
    - ODF prefix stripping (of:=)
    - Spreadsheet functions (SQRT, PI, EXP, LN, etc.)
    - Variable substitution
    - Basic arithmetic
    """
    # Implementation in test_scientific_accuracy.py
```

## Tolerance Guidelines

Different types of calculations require different precision tolerances:

| Calculation Type         | Relative Tolerance | Absolute Tolerance |
| ------------------------ | ------------------ | ------------------ |
| Exact calculations       | 0                  | 1e-15              |
| Physical constants       | 1e-9               | varies             |
| Engineering calculations | 1e-6               | varies             |
| Logarithmic results      | 1e-10              | 1e-10              |

## Adding New Validations

When adding new domain formulas, include validation tests:

### 1. Identify Reference Source

```python
"""
Reference: NIST CODATA 2018
URL: https://physics.nist.gov/cuu/Constants/
Constant: Speed of light = 299,792,458 m/s (exact)
"""
```

### 2. Document the Physics/Chemistry

```python
def test_new_formula():
    """Validate [formula name] against [reference].

    Physics: [Brief explanation of the underlying principle]

    Reference value: [value with uncertainty and source]
    """
```

### 3. Use Appropriate Tolerances

```python
# For exact relationships
assert result == expected

# For physical constants
assert abs(result - reference) / reference < 1e-9

# For engineering calculations
assert abs(result - expected) < tolerance
```

## Validated Domains

### Physics

| Formula          | Property Validated | Reference           |
| ---------------- | ------------------ | ------------------- |
| Kinetic Energy   | KE = 0.5*m*v^2     | Classical mechanics |
| Gravitational PE | PE = m*g*h         | Standard gravity    |
| Free Fall        | t = sqrt(2h/g)     | Kinematics          |
| Wave Speed       | v = f\*lambda      | Wave mechanics      |

### Chemistry

| Formula        | Property Validated | Reference  |
| -------------- | ------------------ | ---------- |
| Ideal Gas Law  | PV = nRT           | IUPAC STP  |
| pH Calculation | pH = -log10([H+])  | Definition |
| Molarity       | M = n/V            | Definition |

### Electrical Engineering

| Formula             | Property Validated    | Reference         |
| ------------------- | --------------------- | ----------------- |
| Ohm's Law Power     | P = V\*I              | Fundamental       |
| Parallel Resistance | 1/R = sum(1/R_i)      | Circuit theory    |
| SNR                 | SNR = 10\*log10(S/N)  | Definition        |
| Resonant Frequency  | f = 1/(2*pi*sqrt(LC)) | AC circuit theory |

## Reporting Issues

If you find a formula that produces incorrect results:

1. **Document the expected value** with reference source
2. **Provide minimal reproduction** code
3. **Include tolerance used** for comparison
4. **Open GitHub issue** with "scientific-accuracy" label

## Further Reading

- [NIST CODATA Fundamental Physical Constants](https://physics.nist.gov/cuu/Constants/)
- [IUPAC Gold Book](https://goldbook.iupac.org/)
- [IEEE Standard for SI Units](https://standards.ieee.org/)
- [Dimensional Analysis](https://en.wikipedia.org/wiki/Dimensional_analysis)
