# Contributing to SpreadsheetDL

First off, thank you for considering contributing to SpreadsheetDL! It's people like you that make SpreadsheetDL such a great tool.

## Versioning and Compatibility

SpreadsheetDL follows [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

**Stability Commitment:**

- Backwards compatibility - Maintained within major versions
- Deprecation warnings - Added before removing features
- Migration guides - Provided for major version upgrades
- Semantic versioning - Strictly followed for all releases

## Code of Conduct

This project and everyone participating in it is governed by the [SpreadsheetDL Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, YAML templates, etc.)
- **Describe the behavior you observed and what you expected**
- **Include your environment details** (Python version, OS, SpreadsheetDL version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the test suite (`uv run pytest`)
5. Run linting (`uv run ruff check src/ tests/`)
6. Commit your changes using [conventional commits](https://www.conventionalcommits.org/)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/spreadsheet-dl.git
cd spreadsheet-dl

# Install dependencies
uv sync --dev

# Run tests to verify setup
uv run pytest
```

### Development Commands

#### Running Tests

For comprehensive test documentation including markers, organization, and selective execution, see **[tests/README.md](tests/README.md)**.

Quick reference:

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=spreadsheet_dl --cov-report=term-missing

# Run specific test categories (see tests/README.md for all markers)
uv run pytest -m unit                    # Fast unit tests only
uv run pytest -m "domain and finance"    # Finance domain tests
uv run pytest -m "not slow"              # Exclude slow tests
uv run pytest -m property                # Property-based tests only
uv run pytest -m validation              # Scientific validation tests
```

#### Other Commands

```bash
# Lint code
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Type check
uv run mypy src/

# Build and serve documentation locally
scripts/docs.sh serve
```

## Coding Standards

### Style Guide

- Follow PEP 8 (enforced by ruff)
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and small

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semi-colons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(builder): add support for conditional formatting
fix(renderer): correct datetime serialization order
docs(api): add ChartBuilder examples
test(mcp): increase coverage to 95%
```

### Testing

- Write tests for all new features
- Maintain or improve test coverage
- Use descriptive test names that explain the scenario
- Follow the existing test structure
- **Prefer property-based tests** for domain formulas

### Documentation

- Update documentation for any user-facing changes
- Add docstrings to all public functions
- Include code examples where helpful
- Keep README.md up to date

## Property-Based Testing Guide

SpreadsheetDL uses **property-based testing** with [Hypothesis](https://hypothesis.readthedocs.io/) for domain formulas. This approach provides much stronger guarantees than traditional example-based testing.

### Why Property-Based Testing?

Traditional tests verify specific examples:

```python
# Traditional (weak)
def test_kinetic_energy():
    assert kinetic_energy(10, 5) == 125
```

Property-based tests verify mathematical properties across many random inputs:

```python
# Property-based (strong)
@given(st.floats(min_value=0.1, max_value=1e6))
def test_kinetic_energy_non_negative(mass):
    """KE is always non-negative."""
    result = kinetic_energy(mass, 10)
    assert result >= 0
```

### Writing Property Tests for Domain Formulas

When contributing domain formulas, include property tests that verify:

1. **Non-negativity**: Energy, resistance, mass cannot be negative
2. **Symmetry**: Order-independent operations (parallel resistance)
3. **Inverse relationships**: Operations that cancel each other
4. **Boundary behavior**: Behavior at zero, infinity, or other limits
5. **Conservation laws**: Physical quantities that must be conserved
6. **Dimensional consistency**: Units must work out correctly

### Property Test Template

```python
"""Property-based tests for [Domain] formulas."""

from hypothesis import given, strategies as st, assume
import pytest

pytestmark = [pytest.mark.property, pytest.mark.domain]


class TestNewFormulaProperties:
    """Property tests for NewFormula."""

    @given(st.floats(min_value=0.1, max_value=1e6, allow_nan=False))
    def test_result_non_negative(self, value):
        """Result should always be non-negative for positive inputs."""
        formula = NewFormula()
        result = evaluate(formula.build(str(value)))
        assert result >= 0

    @given(
        st.floats(min_value=0.1, max_value=1e3, allow_nan=False),
        st.floats(min_value=0.1, max_value=1e3, allow_nan=False),
    )
    def test_symmetry(self, a, b):
        """Order should not affect result for commutative operation."""
        formula = SymmetricFormula()
        result1 = evaluate(formula.build(str(a), str(b)))
        result2 = evaluate(formula.build(str(b), str(a)))
        assert abs(result1 - result2) < 1e-10

    @given(st.floats(min_value=1e-6, max_value=1e6, allow_nan=False))
    def test_inverse_relationship(self, value):
        """Applying operation and inverse should return original."""
        forward = ForwardFormula()
        inverse = InverseFormula()
        result = evaluate(inverse.build(evaluate(forward.build(str(value)))))
        assert abs(result - value) / value < 1e-6  # Relative tolerance
```

### Hypothesis Configuration

Our Hypothesis settings are in `pyproject.toml`:

```toml
[tool.hypothesis]
profile = "default"

[tool.hypothesis.profiles.default]
max_examples = 100
deadline = 5000
```

For CI, we use extended examples:

```toml
[tool.hypothesis.profiles.ci]
max_examples = 200
deadline = 10000
```

### Running Property Tests

```bash
# Run all property tests
uv run pytest -m property

# Run with Hypothesis statistics
uv run pytest -m property --hypothesis-show-statistics

# Run with more examples (CI profile)
uv run pytest -m property --hypothesis-profile=ci
```

### What NOT to Test with Properties

Avoid property tests for:

- Simple getters/setters
- Configuration loading
- String formatting
- UI/CLI output

Use property tests for:

- Mathematical formulas
- Physical calculations
- Algorithmic correctness
- Data transformations

For more details, see [docs/testing-philosophy.md](docs/testing-philosophy.md).

## Scientific Validation

Domain formulas must be validated against authoritative scientific references:

- **Physics**: NIST CODATA 2018 constants
- **Chemistry**: IUPAC standards
- **Engineering**: IEEE/SI conventions

See [docs/scientific-validation.md](docs/scientific-validation.md) for reference values and validation methodology.

### Validation Test Example

```python
def test_molar_volume_at_stp():
    """Validate against IUPAC STP molar volume.

    Reference: IUPAC Gold Book
    Value: 22.711 L/mol at 273.15 K and 100 kPa
    """
    formula = IdealGasLawFormula()
    # Test with CODATA 2018 gas constant
    result = evaluate(formula.build("1", "8.314462618", "273.15", "100000"))
    expected = 0.022711  # m^3
    assert abs(result - expected) / expected < 0.001
```

## Documentation Checklist

Before submitting a PR that includes new code, ensure:

- [ ] All new public functions have docstrings
- [ ] Docstrings follow Google style format
- [ ] Args section lists all parameters with descriptions
- [ ] Returns section describes the return value
- [ ] Raises section documents all exceptions (if applicable)
- [ ] Examples are included for complex functionality
- [ ] Doctests pass: `uv run pytest --doctest-modules src/spreadsheet_dl/`
- [ ] User-facing docs updated if behavior changes
- [ ] CHANGELOG.md updated for user-visible changes
- [ ] **Property tests included** for domain formulas
- [ ] **Scientific validation** for formulas using physical constants

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Brief one-line description.

    Extended description if needed. Can span multiple lines
    and provide additional context.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter. Defaults to 0.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.

    Examples:
        >>> example_function("value", 10)
        True
    """
```

For detailed templates, see `.claude/templates/docstring.md`.

### Branding & Naming

Please review [BRANDING.md](BRANDING.md) for official guidelines on:

- Name usage (SpreadsheetDL vs spreadsheet-dl vs spreadsheet_dl)
- Taglines and terminology
- Tone and style

## Project Structure

```
spreadsheet-dl/
├── docs/                   # Documentation
│   ├── testing-philosophy.md    # Testing approach
│   └── scientific-validation.md # Validation methodology
├── examples/               # Usage examples
├── src/spreadsheet_dl/     # Source code
│   ├── domains/            # Domain plugins
│   ├── schema/             # Data models
│   ├── template_engine/    # Template system
│   ├── themes/             # YAML theme files
│   ├── builder.py          # Fluent builder API
│   ├── charts.py           # Chart builder
│   ├── mcp_server.py       # MCP server
│   └── renderer.py         # ODS renderer
└── tests/                  # Test suite
    ├── domains/            # Domain-specific tests
    │   └── physics/
    │       ├── test_mechanics.py           # Unit tests
    │       └── test_mechanics_properties.py # Property tests
    ├── integration/        # Format roundtrip tests
    └── validation/         # Scientific accuracy tests
```

## Getting Help

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bugs and feature requests

## Recognition

Contributors are recognized in:

- The CHANGELOG.md for significant contributions
- The GitHub contributors page
- Special thanks in release notes for major features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SpreadsheetDL!
