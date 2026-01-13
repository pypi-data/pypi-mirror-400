# Benchmark Infrastructure

Performance tracking for SpreadsheetDL core operations.

## Overview

This directory contains benchmark results and performance regression tracking for critical operations:

- Formula parsing and evaluation
- ODS/XLSX rendering
- Template engine processing
- MCP tool dispatch
- Theme loading and application

## Running Benchmarks

### Run All Benchmarks

```bash
uv run pytest tests/benchmarks/ --benchmark-only
```

### Run Specific Benchmark Suite

```bash
uv run pytest tests/benchmarks/test_rendering_benchmark.py --benchmark-only
```

### Save Results with Timestamp

```bash
uv run pytest tests/benchmarks/ --benchmark-only \
  --benchmark-json=.benchmarks/results/$(date +%Y%m%d-%H%M%S).json
```

### Compare Against Baseline

```bash
# Save current as baseline
uv run pytest tests/benchmarks/ --benchmark-only \
  --benchmark-save=baseline

# Compare future runs
uv run pytest tests/benchmarks/ --benchmark-only \
  --benchmark-compare=baseline
```

## Benchmark Suites

Located in `tests/benchmarks/`:

| Suite                               | Focus Area      | Key Metrics                  |
| ----------------------------------- | --------------- | ---------------------------- |
| `test_formula_parsing_benchmark.py` | Formula engine  | Parse time, eval time        |
| `test_rendering_benchmark.py`       | ODS/XLSX output | Render time, memory usage    |
| `test_theme_loading_benchmark.py`   | Theme system    | Load time, cache performance |
| `test_mcp_dispatch_benchmark.py`    | MCP server      | Tool dispatch latency        |

## Performance Targets

### v4.x Release Targets

| Operation                      | Target | Max Acceptable |
| ------------------------------ | ------ | -------------- |
| Formula parsing (100 formulas) | <10ms  | <20ms          |
| ODS render (1000 rows)         | <500ms | <1000ms        |
| XLSX render (1000 rows)        | <800ms | <1500ms        |
| Theme loading                  | <50ms  | <100ms         |
| MCP tool dispatch              | <10ms  | <25ms          |

## Regression Detection

### CI Integration

Add to `.github/workflows/ci.yml`:

```yaml
benchmark:
  name: Performance Benchmarks
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install uv
      uses: astral-sh/setup-uv@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: uv sync --dev
    - name: Run benchmarks
      run: |
        uv run pytest tests/benchmarks/ --benchmark-only \
          --benchmark-json=benchmark-results.json
    - name: Store results
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: benchmark-results.json
        fail-on-alert: true
        alert-threshold: '110%' # Fail if 10% slower
```

## Directory Structure

```
.benchmarks/
├── .gitkeep                          # Preserves directory
├── README.md                         # This file
├── results/                          # Timestamped JSON results
│   └── YYYYMMDD-HHMMSS.json
├── history/                          # Historical comparison data
│   └── vX.Y.Z-baseline.json
└── analysis/                         # Performance analysis reports
    └── regression-analysis.md
```

## Retention Policy

- **Recent results** (30 days): All timestamped results
- **Historical baselines**: Major version releases (v4.0.0, v4.1.0, etc.)
- **Analysis reports**: Kept indefinitely

Clean old results:

```bash
find .benchmarks/results/ -name "*.json" -mtime +30 -delete
```

## Analysis Tools

### Generate Performance Report

```bash
python scripts/analyze_benchmarks.py --input .benchmarks/results/*.json \
  --output .benchmarks/analysis/$(date +%Y-%m)-report.md
```

### Compare Versions

```bash
uv run pytest tests/benchmarks/ --benchmark-only \
  --benchmark-compare=.benchmarks/history/v4.0.0-baseline.json \
  --benchmark-compare-fail=mean:10%  # Fail if mean >10% slower
```

## Best Practices

1. **Run benchmarks in consistent environment** (same hardware, no background tasks)
2. **Multiple iterations** (pytest-benchmark handles this automatically)
3. **Baseline on stable commits** (after major features, before releases)
4. **Track memory usage** for operations processing large datasets
5. **Separate micro vs. macro benchmarks** (unit operations vs. full workflows)

## Dependencies

Required packages (already in dev dependencies):

```toml
[project.optional-dependencies]
dev = [
    "pytest-benchmark>=4.0.0",
    # ... other deps
]
```

## Troubleshooting

### Benchmarks Too Slow

- Check for debug mode (should use release builds)
- Verify no profiling tools active
- Ensure sufficient system resources

### High Variance

- Close background applications
- Run multiple times and take median
- Check for thermal throttling on laptops

### Comparison Failures

- Ensure same Python version
- Verify same dependency versions
- Check for environmental differences

## See Also

- `tests/benchmarks/README.md` - Benchmark test documentation
- `.github/workflows/ci.yml` - CI integration
- `docs/development/benchmarking.md` - Developer guide
