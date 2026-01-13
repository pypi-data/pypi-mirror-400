# Scripts Reference

Quality and maintenance scripts for the SpreadsheetDL project.

## Quick Reference

| Script          | Purpose                                    | When to Use                               |
| --------------- | ------------------------------------------ | ----------------------------------------- |
| `check.sh`      | Quick quality check (lint + format check)  | Before commits, after significant changes |
| `lint.sh`       | Run all configured linters                 | When checking for issues                  |
| `format.sh`     | Format all code files                      | When formatting is needed                 |
| `clean.sh`      | Clean build artifacts and caches           | When builds are stale                     |
| `doctor.sh`     | Environment health check                   | When tools seem broken                    |
| `validate.sh`   | **Full validation suite (recommended CI)** | **Before releases, in CI pipelines**      |
| `fix.sh`        | Auto-fix common issues                     | After lint failures                       |
| `test_stats.sh` | Generate dynamic test statistics           | When you need current test counts         |

## Quality Scripts

### check.sh

Quick quality check combining lint and format verification.

```bash
./scripts/check.sh           # Run all checks
./scripts/check.sh --json    # Machine-readable output
./scripts/check.sh -v        # Verbose output
```

### lint.sh

Run all linters across the codebase.

```bash
./scripts/lint.sh            # Run all linters
./scripts/lint.sh --python   # Python only
./scripts/lint.sh --shell    # Shell scripts only
./scripts/lint.sh --yaml     # YAML files only
./scripts/lint.sh --markdown # Markdown files only
./scripts/lint.sh --json     # JSON output
```

### format.sh

Run all formatters.

```bash
./scripts/format.sh          # Format all files
./scripts/format.sh --check  # Check only, don't modify
./scripts/format.sh --python # Python only
./scripts/format.sh --yaml   # YAML only
```

### validate.sh

Full validation suite including tests.

```bash
./scripts/validate.sh        # Run complete validation
```

Includes:

1. Ruff lint check
2. Ruff format check
3. Mypy type check
4. Pytest suite
5. ODS generation test
6. ODS analysis test
7. Report generation test

### doctor.sh

Check development environment setup.

```bash
./scripts/doctor.sh          # Check tool availability
./scripts/doctor.sh --json   # Machine-readable output
```

Checks:

- Core tools (git, bash)
- Python tools (python3, uv, ruff, mypy)
- JS tools (node, npm, prettier, markdownlint)
- Shell tools (shellcheck, shfmt)
- YAML tools (yamllint)
- Configuration files presence

### clean.sh

Clean build artifacts and caches.

```bash
./scripts/clean.sh           # Clean all artifacts
./scripts/clean.sh -v        # Verbose output
```

Removes:

- `__pycache__/` directories
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `dist/` and `build/`
- `*.egg-info/`
- `htmlcov/` and `.coverage`

### fix.sh

Auto-fix common issues.

```bash
./scripts/fix.sh             # Auto-fix all files
./scripts/fix.sh --python    # Python only
```

### test_stats.sh

Generate dynamic test statistics.

```bash
./scripts/test_stats.sh      # Human-readable output
./scripts/test_stats.sh --json # JSON output for CI/automation
```

Provides current test counts by:

- Test level (unit, integration)
- Domain (finance, science, engineering, manufacturing)
- Feature (mcp, cli, builder, validation, rendering, templates, visualization)
- Performance (slow, benchmark)

**Note**: Statistics are always generated fresh from the current test suite, ensuring accuracy.

## Tool Wrappers

Individual tool scripts in `scripts/tools/` provide consistent interfaces:

```bash
scripts/tools/<tool>.sh [--check|--fix|--format|--json|-v] [paths...]
```

### Python Tools

| Script    | Tool | Purpose               |
| --------- | ---- | --------------------- |
| `ruff.sh` | Ruff | Python linting/format |
| `mypy.sh` | Mypy | Python type checking  |

### Universal Tools

| Script            | Tool         | Purpose                 |
| ----------------- | ------------ | ----------------------- |
| `markdownlint.sh` | markdownlint | Markdown linting        |
| `prettier.sh`     | Prettier     | Multi-format formatting |
| `shellcheck.sh`   | ShellCheck   | Shell script linting    |
| `yamllint.sh`     | yamllint     | YAML linting            |
| `jsonc.sh`        | Custom       | JSON/JSONC validation   |

### Diagram Tools

| Script        | Tool     | Purpose                |
| ------------- | -------- | ---------------------- |
| `mermaid.sh`  | mmdc     | Mermaid diagram render |
| `plantuml.sh` | PlantUML | PlantUML diagrams      |

## Utility Scripts

Additional utility scripts for specific tasks:

### setup.sh

Initialize development environment with all required dependencies.

```bash
./scripts/setup.sh              # Interactive setup
./scripts/setup.sh --dev        # Install dev dependencies
./scripts/setup.sh --check-only # Check without installing
```

### docs.sh

Documentation build and serve utilities.

```bash
./scripts/docs.sh build   # Build documentation
./scripts/docs.sh serve   # Serve documentation locally
./scripts/docs.sh deploy  # Deploy to GitHub Pages
./scripts/docs.sh lint    # Check docstring coverage
./scripts/docs.sh check   # Full documentation quality check
```

### test_integration.sh

Comprehensive script integration testing.

```bash
./scripts/test_integration.sh           # Run integration tests
./scripts/test_integration.sh -v        # Verbose output
./scripts/test_integration.sh --verbose # Verbose output
```

### audit_scripts.sh

Analyze all scripts for consistency and best practices.

```bash
./scripts/audit_scripts.sh  # Audit all scripts
```

### prepare_public_release.sh

Prepare project for public release (clean sensitive data).

```bash
./scripts/prepare_public_release.sh  # Interactive release prep
```

### generate_tree.sh

Generate directory tree visualization.

```bash
./scripts/generate_tree.sh  # Generate project tree
```

### setup_claude_config.sh

Setup Claude Code configuration.

```bash
./scripts/setup_claude_config.sh  # Configure Claude Code
```

### validate_tools.sh

Validate tool installations and versions.

```bash
./scripts/validate_tools.sh  # Check all tools
```

### validate_vscode.sh

Validate VS Code configuration and extensions.

```bash
./scripts/validate_vscode.sh  # Check VS Code setup
```

### check_dependencies.sh

Check project dependencies and versions.

```bash
./scripts/check_dependencies.sh  # Verify dependencies
```

### install_extensions.sh

Install recommended VS Code extensions.

```bash
./scripts/install_extensions.sh  # Install extensions
```

## Maintenance Scripts

Located in `scripts/maintenance/`:

### archive_coordination.sh

Archive old coordination files.

```bash
./scripts/maintenance/archive_coordination.sh           # Archive >30 days
./scripts/maintenance/archive_coordination.sh --days 7  # Archive >7 days
./scripts/maintenance/archive_coordination.sh --dry-run # Preview only
```

### context_optimizer.py

Analyze project for context optimization opportunities.

```bash
uv run python scripts/maintenance/context_optimizer.py
uv run python scripts/maintenance/context_optimizer.py --report
uv run python scripts/maintenance/context_optimizer.py --suggestions
```

### batch_file_processor.py

Process files in batches to reduce context overhead.

```bash
uv run python scripts/maintenance/batch_file_processor.py <dir> "*.json"
uv run python scripts/maintenance/batch_file_processor.py . "*.py" --batch-size 20
```

### json_summarizer.py

Extract key metrics from large JSON files.

```bash
uv run python scripts/maintenance/json_summarizer.py report.json
uv run python scripts/maintenance/json_summarizer.py report.json --keys status,errors
```

## Common Library

`scripts/lib/common.sh` provides shared functions:

- Color output (with terminal detection)
- `print_header`, `print_pass`, `print_fail`, `print_skip`
- `has_tool` - Check if tool is installed
- `require_tool` - Require tool with install hint
- `has_uv`, `run_py_tool` - UV integration
- `find_files` - Find files by pattern
- `enable_json`, `json_result` - JSON output mode
- Counter management (`increment_passed`, etc.)

## Environment Variables

| Variable      | Purpose                         |
| ------------- | ------------------------------- |
| `REPO_ROOT`   | Repository root (auto-detected) |
| `JSON_OUTPUT` | Enable JSON mode                |

## Exit Codes

| Code | Meaning                         |
| ---- | ------------------------------- |
| 0    | Success (or gracefully skipped) |
| 1    | Failures found                  |
| 2    | Tool/configuration error        |

## Integration

### Pre-commit

Scripts are invoked by pre-commit hooks defined in `.pre-commit-config.yaml`.

### CI

The `validate.sh` script runs in CI via `.github/workflows/ci.yml`.

### Claude Code

Scripts are referenced in `CLAUDE.md` for quality workflows.

---

**Last Updated**: 2026-01-06
