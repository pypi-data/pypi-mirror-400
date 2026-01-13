# Performance Benchmark Suite

Comprehensive performance benchmarks for SpreadsheetDL v4.0.0.

## Overview

This benchmark suite establishes performance baselines and tracks optimization improvements for critical operations:

1. **Large Spreadsheet Rendering** - Target: <5s for 10K rows (2x improvement)
2. **MCP Tool Dispatch** - Target: <100ms for 1000 calls (2x improvement)
3. **Theme Loading** - Target: <50ms for 10 themes (4x improvement)
4. **Formula Parsing** - Target: <100ms for 1000 formulas

## Running Benchmarks

### All Benchmarks

```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only

# With detailed statistics
pytest tests/benchmarks/ --benchmark-only --benchmark-columns=min,max,mean,stddev,median

# Save results for comparison
pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline
```

### Specific Categories

```bash
# Only rendering benchmarks
pytest tests/benchmarks/test_rendering_benchmark.py --benchmark-only

# Only MCP dispatch benchmarks
pytest tests/benchmarks/test_mcp_dispatch_benchmark.py --benchmark-only

# Only theme loading benchmarks
pytest tests/benchmarks/test_theme_loading_benchmark.py --benchmark-only

# Only formula parsing benchmarks
pytest tests/benchmarks/test_formula_parsing_benchmark.py --benchmark-only
```

### Comparing Results

```bash
# Compare against baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

# Compare against specific run
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001
```

## Benchmark Categories

### 1. Rendering Benchmarks (test_rendering_benchmark.py)

Tests ODS rendering performance with various data sizes and complexity:

- `test_render_10k_rows_baseline` - 10,000 rows (baseline target: ~10s → <5s)
- `test_render_1k_rows_medium` - 1,000 rows (measure overhead)
- `test_render_with_styles` - Styled cells (measure style overhead)
- `test_render_multiple_sheets` - 5 sheets × 1K rows (multi-sheet overhead)
- `test_render_with_formulas` - Formula generation overhead

**Optimization Targets**:

- Batch ODF element creation
- Cache style objects
- Lazy initialization of ODF structures
- Memory-efficient streaming for large datasets

### 2. MCP Dispatch Benchmarks (test_mcp_dispatch_benchmark.py)

Tests MCP tool registry and dispatch performance:

- `test_tool_registration_overhead` - Register 100 tools
- `test_tool_lookup_performance` - 1000 tool lookups (baseline: ~200ms → <100ms)
- `test_tool_execution_dispatch` - End-to-end dispatch with handler invocation
- `test_category_lookup_performance` - Category-based filtering
- `test_list_all_tools_performance` - Full tool listing with schemas
- `test_bulk_tool_registration` - Programmatic registration

**Optimization Targets**:

- Pre-compile dispatch table at module load
- Use dict lookup instead of iteration
- Cache tool metadata
- Reduce function call overhead

### 3. Theme Loading Benchmarks (test_theme_loading_benchmark.py)

Tests YAML theme parsing and caching:

- `test_theme_parse_from_yaml` - Load 10 themes (baseline: ~200ms → <50ms)
- `test_theme_cache_effectiveness` - Repeated loading (cache hit rate)
- `test_theme_inheritance_resolution` - Parent theme extends
- `test_color_reference_resolution` - Palette color lookups
- `test_complex_style_parsing` - Full style property parsing

**Optimization Targets**:

- Cache parsed theme objects
- Lazy load themes (only when used)
- Pre-compile regex patterns
- Use faster YAML parser (if available)

### 4. Formula Parsing Benchmarks (test_formula_parsing_benchmark.py)

Tests formula generation and parsing:

- `test_simple_formula_generation` - 1000 simple formulas (target: <100ms)
- `test_complex_formula_generation` - Nested formulas
- `test_cell_reference_parsing` - Various reference formats
- `test_function_call_generation` - Statistical/math functions
- `test_range_expansion` - Large cell ranges
- `test_array_formula_generation` - Array formulas
- `test_conditional_formula_generation` - IF/AND/OR conditionals
- `test_text_formula_generation` - String manipulation

**Optimization Targets**:

- Verify regex patterns compiled once
- Cache common formula patterns
- Optimize hot paths in parser
- Use compiled regex for validation

## Performance Budgets

Target maximum execution times:

| Operation                | Current | Target | Improvement |
| ------------------------ | ------- | ------ | ----------- |
| 10K row rendering        | ~10s    | <5s    | 2x          |
| 1000 MCP tool lookups    | ~200ms  | <100ms | 2x          |
| 10 theme loads           | ~200ms  | <50ms  | 4x          |
| 1000 formula generations | TBD     | <100ms | Baseline    |

## Continuous Integration

Benchmarks run in CI on every PR to:

- Establish baseline for new features
- Detect performance regressions (>10%)
- Track optimization improvements

## Interpreting Results

### Key Metrics

- **Min**: Fastest execution time (best case)
- **Max**: Slowest execution time (worst case)
- **Mean**: Average execution time
- **Median**: Middle value (less affected by outliers)
- **StdDev**: Consistency of performance
- **OPS**: Operations per second (higher is better)

### What to Look For

- **Regression**: Mean time increases >10% from baseline
- **Improvement**: Mean time decreases significantly
- **Variability**: High StdDev indicates inconsistent performance
- **Outliers**: Many outliers suggest GC or system interference

## Optimization Guidelines

### Before Optimizing

1. Run benchmarks to establish baseline
2. Save results: `--benchmark-save=before`
3. Profile code to identify bottlenecks

### After Optimizing

1. Run benchmarks again
2. Compare: `--benchmark-compare=before`
3. Verify improvement meets targets
4. Check for regressions in other areas

### When Optimizing

- Focus on hot paths (most frequently called)
- Batch operations where possible
- Cache expensive computations
- Avoid premature optimization
- Measure, don't guess

## Example Output

```
-------------------------- benchmark: 20 tests --------------------------
Name                                Min       Mean      Median       Max
--------------------------------------------------------------------------
test_simple_formula_generation   45.2ms    52.1ms     51.8ms    68.3ms
test_tool_lookup_performance     75.3us    86.7us     88.1us   144.6us
test_theme_parse_from_yaml      142.8ms   165.3ms    163.2ms   198.7ms
test_render_1k_rows_medium        1.23s     1.34s      1.33s     1.52s
...
```

## Related Documentation

- [Performance Module](/src/spreadsheet_dl/performance.py) - Built-in perf utilities
- [Optimization Guide](/docs/performance.md) - General optimization tips
- [Phase 11 Task](/CLAUDE.md) - Performance optimization phase

## Implementation

- PERF-RENDER-001: Large file rendering optimization
- PERF-MCP-001: Tool dispatch optimization
- PERF-THEME-001: Theme loading optimization
- PERF-FORMULA-001: Formula parsing optimization

**Requirements**:

- pytest>=8.0.0
- pytest-benchmark>=5.2.3
- Python 3.12+
