# Testing Quick Reference

Quick reference for running tests in SpreadsheetDL. For comprehensive testing documentation, see [tests/README.md](./tests/README.md).

## Run Tests

```bash
# All tests
uv run pytest

# By test level
uv run pytest -m unit                    # Fast unit tests only
uv run pytest -m integration             # Integration tests

# By domain
uv run pytest -m finance                 # Finance domain
uv run pytest -m science                 # Science domains
uv run pytest -m engineering             # Engineering
uv run pytest -m manufacturing           # Manufacturing
uv run pytest -m domain                  # All domain plugins

# By feature
uv run pytest -m mcp                     # MCP server
uv run pytest -m cli                     # CLI interface
uv run pytest -m builder                 # Builder API
uv run pytest -m validation              # Schema validation
uv run pytest -m rendering               # ODS/XLSX/PDF rendering
uv run pytest -m templates               # Template system
uv run pytest -m visualization           # Charts and graphs

# By performance
uv run pytest -m slow                    # Only slow tests
uv run pytest -m benchmark               # Performance benchmarks

# By dependencies
uv run pytest -m requires_yaml           # Tests needing PyYAML
uv run pytest -m requires_export         # Tests needing export libs
uv run pytest -m requires_html           # Tests needing HTML libs
uv run pytest -m requires_files          # Tests with file I/O
```

## Common Patterns

```bash
# Fast tests without slow ones
uv run pytest -m "unit and not slow"

# Domain-specific unit tests
uv run pytest -m "unit and finance"
uv run pytest -m "unit and science"
uv run pytest -m "unit and engineering"

# Combined domain filters
uv run pytest -m "domain and engineering"
uv run pytest -m "domain and science"

# Feature-specific unit tests
uv run pytest -m "unit and mcp"
uv run pytest -m "unit and cli"
uv run pytest -m "unit and builder"

# Tests without specific dependencies
uv run pytest -m "not requires_files"
uv run pytest -m "not requires_yaml"

# Multiple criteria
uv run pytest -m "finance and not slow"
uv run pytest -m "(mcp or cli) and unit"
```

## Current Statistics

To get current test counts and distribution:

```bash
# Human-readable output
scripts/test_stats.sh

# JSON output (for CI/automation)
scripts/test_stats.sh --json
```

## Available Markers

### Test Level

- `unit` - Fast, isolated
- `integration` - Multi-component

### Domains

- `finance` - Finance domain
- `science` - Science domains
- `engineering` - Engineering
- `manufacturing` - Manufacturing
- `domain` - Domain plugins

### Features

- `mcp` - MCP server
- `cli` - CLI interface
- `builder` - Builder API
- `validation` - Schema validation
- `rendering` - ODS/XLSX/PDF
- `templates` - Templates
- `visualization` - Charts

### Other

- `slow` - Tests >1 second
- `benchmark` - Performance tests
- `requires_yaml` - Needs PyYAML
- `requires_export` - Needs export libs
- `requires_html` - Needs HTML libs
- `requires_files` - File I/O

## Comprehensive Documentation

For detailed information, see:

- **[Full Testing Guide](./tests/README.md)** - Complete documentation on test organization, markers, usage patterns, debugging, CI/CD integration, and best practices
- **[Test Statistics Script](./scripts/test_stats.sh)** - Dynamic test count generation
- **[pytest Documentation](https://docs.pytest.org/en/stable/how-to/mark.html)** - Official pytest marker documentation

## Quick Tips

**Adding new markers**: Define in `pyproject.toml` under `[tool.pytest.ini_options]` and document in [tests/README.md](./tests/README.md).

**Debugging tests**: Use `--collect-only` to see what tests would run, `-v` for verbose output, `-x` to stop on first failure. See [tests/README.md](./tests/README.md#debugging) for more.
