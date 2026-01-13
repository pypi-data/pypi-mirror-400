# SpreadsheetDL Test Suite

Comprehensive test suite for SpreadsheetDL with organized pytest markers for selective test execution.

## Quick Start

```bash
# Run all tests
uv run pytest

# Run only fast unit tests
uv run pytest -m unit

# Run integration tests
uv run pytest -m integration

# Run specific domain tests
uv run pytest -m finance
uv run pytest -m "domain and engineering"
```

## Test Statistics

To get current test counts and distribution, run:

```bash
# Human-readable output
scripts/test_stats.sh

# JSON output (for CI/automation)
scripts/test_stats.sh --json
```

**Note**: Test counts are dynamic and generated on-demand to ensure accuracy.

## Test Organization

Tests are organized using pytest markers at the module level:

```python
pytestmark = [pytest.mark.unit, pytest.mark.builder]
```

### Available Markers

All markers are defined in `pyproject.toml` under `[tool.pytest.ini_options]`.

#### Test Level

- `unit` - Fast, isolated tests (no I/O)
- `integration` - Multi-component tests (slower)

#### Performance

- `slow` - Tests >1 second
- `benchmark` - Performance benchmarks

#### Dependencies

- `requires_yaml` - Needs PyYAML
- `requires_export` - Needs openpyxl/reportlab
- `requires_html` - Needs beautifulsoup4/lxml
- `requires_files` - Creates/reads files

#### Domains

- `domain` - Domain plugin tests
- `finance` - Finance domain
- `science` - Science domains (biology, chemistry, physics)
- `engineering` - Engineering domains (electrical, mechanical, civil)
- `manufacturing` - Manufacturing domain

#### Features

- `mcp` - MCP server
- `cli` - CLI interface
- `validation` - Schema validation
- `rendering` - ODS/XLSX/PDF rendering
- `builder` - Builder API
- `templates` - Template system
- `visualization` - Charts/graphs

## Common Usage Patterns

### Run Fast Tests Only

```bash
# Unit tests only (fastest)
uv run pytest -m unit

# Exclude slow tests
uv run pytest -m "unit and not slow"
```

### Run Feature-Specific Tests

```bash
# MCP server tests
uv run pytest -m mcp

# Builder API tests
uv run pytest -m builder

# Validation tests
uv run pytest -m validation

# CLI tests
uv run pytest -m cli
```

### Run Domain Tests

```bash
# All domain tests
uv run pytest -m domain

# Specific domains
uv run pytest -m finance
uv run pytest -m "domain and engineering"
uv run pytest -m "domain and science"
```

### Run Tests by Dependency

```bash
# Tests that don't need YAML
uv run pytest -m "not requires_yaml"

# Tests that don't need files
uv run pytest -m "not requires_files"

# Tests that need export dependencies
uv run pytest -m requires_export
```

### Complex Combinations

```bash
# Unit finance tests (not integration)
uv run pytest -m "unit and finance and not integration"

# All rendering tests
uv run pytest -m rendering

# Domain tests excluding slow ones
uv run pytest -m "domain and not slow"

# Fast MCP tests
uv run pytest -m "mcp and not slow"
```

## Understanding "N deselected"

When you run a marker-filtered test command like `uv run pytest -m unit`, you may see output like:

```
===== 2915 passed, 406 deselected in 45.2s =====
```

**This is expected behavior.** The "406 deselected" means pytest found 406 tests that do NOT match your filter and correctly skipped them. For example:

- When filtering for `unit`, all `integration` tests are deselected
- When filtering for `finance`, all non-finance tests are deselected

The deselected count helps you understand the total test suite size.

## Test Structure

```
tests/
├── test_*.py              # Core functionality tests
├── domains/               # Domain-specific tests
│   ├── test_finance.py
│   ├── test_biology.py
│   ├── test_engineering.py
│   └── ...
├── cli/                   # CLI-specific tests
│   └── test_commands_coverage.py
└── conftest.py            # Shared fixtures

.claude/hooks/
├── test_hooks.py          # Hook system tests
└── test_quality_enforcement.py
```

## Writing Tests

### Adding Markers to New Tests

```python
"""Test module description."""

from __future__ import annotations

import pytest

# Module-level markers
pytestmark = [pytest.mark.unit, pytest.mark.feature_name]


class TestMyFeature:
    """Test class for my feature."""

    def test_something(self) -> None:
        """Test description."""
        assert True

    @pytest.mark.slow
    def test_slow_operation(self) -> None:
        """This test is marked as slow."""
        # Expensive operation
        pass
```

### Marker Guidelines

1. **Always include a test level marker**: `unit` or `integration`
2. **Add feature markers**: `mcp`, `builder`, `cli`, etc. when testing specific features
3. **Add domain markers**: `finance`, `science`, `engineering` for domain-specific tests
4. **Add dependency markers**: `requires_yaml`, `requires_files`, etc. if external dependencies are needed
5. **Mark slow tests**: Use `@pytest.mark.slow` for tests >1 second

### Example Marker Combinations

```python
# Unit test for MCP server
pytestmark = [pytest.mark.unit, pytest.mark.mcp]

# Integration test for finance domain with file I/O
pytestmark = [pytest.mark.integration, pytest.mark.finance, pytest.mark.requires_files]

# Unit test for builder requiring export dependencies
pytestmark = [pytest.mark.unit, pytest.mark.builder, pytest.mark.requires_export]
```

## CI/CD Integration

Markers enable efficient CI/CD workflows:

```yaml
# Fast feedback - unit tests only
- name: Fast Tests
  run: uv run pytest -m unit

# Feature validation
- name: MCP Tests
  run: uv run pytest -m mcp

# Domain validation
- name: Finance Tests
  run: uv run pytest -m finance

# Full validation
- name: All Tests
  run: uv run pytest
```

## Debugging

### List Tests Without Running

```bash
# See what would run
uv run pytest -m unit --collect-only

# Count tests for a specific marker
uv run pytest -m "unit and finance" --collect-only -q | tail -1

# See all available markers
uv run pytest --markers
```

### Verbose Output

```bash
# Show test names
uv run pytest -m unit -v

# Show test details
uv run pytest -m unit -vv

# Show print statements
uv run pytest -m unit -s
```

### Stop on First Failure

```bash
uv run pytest -m unit -x

# Stop after N failures
uv run pytest -m unit --maxfail=3
```

### Run Specific Test

```bash
# By file
uv run pytest tests/test_builder.py

# By class
uv run pytest tests/test_builder.py::TestBuilder

# By function
uv run pytest tests/test_builder.py::TestBuilder::test_create_sheet
```

## Adding New Markers

If you need to add a new marker:

1. **Define in `pyproject.toml`**:

```toml
[tool.pytest.ini_options]
markers = [
    "new_marker: Description of the new marker",
]
```

1. **Apply to test files**:

```python
pytestmark = [pytest.mark.unit, pytest.mark.new_marker]
```

1. **Document in this file** under "Available Markers"

## Troubleshooting

### Marker Not Registered

If you see "Unknown pytest.mark.X", ensure the marker is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "your_marker: Description",
]
```

### Import Errors

Ensure `import pytest` is present in test files using `pytestmark`.

### Test Not Collected

Check that:

1. Test file starts with `test_`
2. Test function starts with `test_`
3. Markers are defined correctly
4. File is in the `tests/` directory
5. No syntax errors in the file

### Slow Test Suite

To identify slow tests:

```bash
# Run with duration reporting
uv run pytest --durations=10

# Run only fast unit tests
uv run pytest -m "unit and not slow"

# Profile test execution
uv run pytest --durations=0 > test-durations.txt
```

## Best Practices

### Test Organization

- Use **module-level markers** (`pytestmark`) for consistency
- Group related tests in classes
- Use descriptive test names that explain the scenario
- Keep tests focused on a single behavior

### Marker Usage

- Every test file should have at least `unit` or `integration`
- Add feature markers when testing specific components
- Add domain markers for domain-specific functionality
- Mark slow tests proactively to enable fast feedback loops

### Performance

- Unit tests should complete in <100ms each
- Mark tests >1 second as `slow`
- Use mocks for external dependencies in unit tests
- Reserve file I/O and network calls for integration tests

### Maintainability

- Don't duplicate test logic - use fixtures
- Keep test setup/teardown minimal
- Document complex test scenarios with comments
- Avoid hardcoding values - use constants or fixtures
