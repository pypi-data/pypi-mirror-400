# SpreadsheetDL Documentation

**The Spreadsheet Definition Language for Python**

Define complex spreadsheets in Python or YAML, export to ODS/XLSX/PDF. Built-in domain plugins for engineering, science, and finance. Native MCP server for Claude integration.

## Overview

SpreadsheetDL is a universal spreadsheet definition language that lets you create professional spreadsheets programmatically using a declarative, high-level API. Instead of writing cell-by-cell imperative code (like openpyxl/xlsxwriter), you define the structure once and export to multiple formats.

## Quick Links

- [Installation Guide](installation.md) - Get started quickly
- [User Guide](user-guide.md) - Comprehensive usage instructions
- [API Reference](api/index.md) - Complete API documentation
- [CLI Reference](cli.md) - Command-line interface documentation
- [Examples](examples/index.md) - Practical usage examples
- [Error Codes](error-codes.md) - Error code reference

## Guides

### Getting Started

- [Installation Guide](installation.md) - Quick setup instructions
- [Getting Started](getting-started.md) - Your first spreadsheet
- [User Guide](user-guide.md) - Comprehensive usage guide

### Core Guides

- [Integration Guide](guides/integration.md) - **NEW** How modules work together, data flow, integration patterns
- [Performance Guide](guides/performance.md) - **NEW** Benchmarks, optimization techniques, best practices
- [Cookbook](guides/cookbook.md) - **NEW** 25+ practical recipes for common tasks
- [Troubleshooting Guide](guides/troubleshooting.md) - Common issues and solutions
- [Migration Guide](guides/migration-guide.md) - Upgrading from older versions

### Advanced Guides

- [Builder API Reference](api/builder.md) - Fluent API for spreadsheet construction
- [Theme Creation Guide](guides/theme-creation.md) - Create custom visual themes
- [Style Composition Guide](guides/style-composition.md) - Advanced styling techniques
- [Best Practices Guide](guides/best-practices.md) - Development best practices
- [Plugin Development Guide](guides/plugin-development.md) - Create custom plugins

## Features

### Core Platform (v0.1.0)

- ✅ **Declarative Builder API** - Define spreadsheets using fluent, chainable methods
- ✅ **Type-Safe Formulas** - FormulaBuilder with 60+ functions, circular reference detection
- ✅ **Theme System** - YAML-based themes (5 built-in: default, corporate, minimal, dark, high_contrast)
- ✅ **Chart Builder** - 60+ chart types (column, bar, line, area, pie, scatter, combo, sparklines)
- ✅ **Multi-Format Export** - ODS (native), XLSX, PDF from single definition
- ✅ **Advanced Formatting** - Conditional formatting, data validation, named ranges, cell merging
- ✅ **Template Engine** - Schema-driven template system with component composition
- ✅ **MCP Server** - Native server with 18 tools for spreadsheet and budget operations, Claude Desktop integration
- ✅ **Streaming I/O** - Handle 100k+ row spreadsheets efficiently
- ✅ **Round-Trip Editing** - Read, modify, and write existing ODS files
- ✅ **CLI & Python API** - Both command-line and programmatic interfaces

### Domain Plugins (Official)

#### 💰 Finance Domain

- **Formulas**: NPV, IRR, PMT, PV, FV (financial functions)
- **Importers**: Bank CSV (50+ banks), Plaid API integration
- **Utils**: Account management, budget analytics, alerts, recurring expenses
- **Features**: WebDAV upload (Nextcloud), multi-currency support, auto-categorization

#### 🔬 Data Science Domain

- **Formulas**: Statistical tests (TTEST, FTEST, ZTEST), ML metrics (confusion matrix, F1, precision, recall)
- **Importers**: Scientific CSV, MLflow experiment import, Jupyter notebook
- **Utils**: Plotting helpers, statistical utilities

#### ⚙️ Engineering Domains

- **Electrical**: Pin mapping formulas, power budget calculations, component importers
- **Mechanical**: Stress analysis formulas, tolerance calculations, material properties, CAD importers
- **Civil**: Load calculation formulas, structural analysis, concrete mix formulas, survey importers

## Version

Current version: **v0.1.0** 🎉 _Initial Public Beta Release_

### What's New in v0.1.0

This is the first public release of SpreadsheetDL! Features include all capabilities developed during internal versions (v4.x series shown below for reference).

**Key Highlights:**

- Universal spreadsheet definition language with declarative API
- 60+ type-safe formulas with circular reference detection
- Multi-format export (ODS, XLSX, PDF)
- 5 built-in themes with YAML customization
- Domain plugins for finance, science, and engineering
- MCP server integration for AI tools
- 3000+ tests including property-based and scientific validation

See [CHANGELOG.md](../CHANGELOG.md) for complete release history.

---

### Development History (Internal Versions)

The sections below document features developed during internal iterations prior to public release.

#### What's New in v0.1.0 (Internal)

- **Property-Based Testing** - 103+ new property-based tests using Hypothesis
  - Physics kinematics and mechanics validation
  - Chemistry stoichiometry tests
  - Electrical engineering circuit tests
  - Conservation laws and dimensional consistency

- **Scientific Validation** - Tests against NIST CODATA 2018 reference values
  - Physics: Free fall, kinetic energy, gravitational PE
  - Chemistry: Ideal gas law, pH calculation, molarity
  - Electrical: Ohm's law power, parallel resistance, SNR

- **Bug Fixes** - ODF formula prefix consistency for electrical engineering

#### What's New in v0.1.0 (Internal)

- **Template Engine** - Define custom spreadsheets declaratively in YAML
  - Variable substitution with `${...}` syntax
  - Built-in functions (month_name, format_currency, etc.)
  - Conditional content rendering
  - Reusable components for your own templates

- **Enhanced Theme System**
  - Color palette management with accessibility checking
  - Font pairing system with pre-built pairings
  - Typography hierarchy with type scales

- **ChartBuilder** - Fluent API for charts
  - Column, bar, line, area, pie, scatter charts
  - Sparklines for inline visualizations
  - Trendlines with forecasting
  - Full styling and positioning control

- **Extended Builder API**
  - Workbook properties (title, author, etc.)
  - Named ranges
  - Sheet freezing and protection
  - Alternating row styles
  - Chart integration

- **FormulaBuilder Enhancement**
  - Financial functions (PMT, PV, FV, NPV, IRR)
  - Date/time functions
  - Lookup functions (VLOOKUP, INDEX/MATCH)
  - Text and statistical functions
  - Array formula support

## Installation

```bash
# Using uv (recommended for development)
git clone https://github.com/lair-click-bats/spreadsheet-dl.git
cd spreadsheet-dl
uv sync

# Install with theme support
uv sync --extra config
```

## Basic Usage

```python
from spreadsheet_dl import OdsGenerator, BudgetAnalyzer

# Create a budget
generator = OdsGenerator()
generator.create_budget_spreadsheet("budget_2025_01.ods")

# Analyze spending
analyzer = BudgetAnalyzer("budget_2025_01.ods")
summary = analyzer.get_summary()
print(f"Total spent: ${summary.total_spent}")
```

### Using the Builder API

```python
from spreadsheet_dl.builder import SpreadsheetBuilder, formula
from spreadsheet_dl.charts import ChartBuilder

# Create spreadsheet with fluent API
builder = SpreadsheetBuilder(theme="professional")

builder.sheet("Budget") \
    .column("Category", width="150pt") \
    .column("Budget", width="100pt", type="currency") \
    .column("Actual", width="100pt", type="currency") \
    .freeze(rows=1) \
    .header_row() \
    .data_rows(10, alternate_styles=["row_even", "row_odd"]) \
    .total_row(formulas=["Total", "=SUM(B2:B11)", "=SUM(C2:C11)"])

# Add a chart
chart = ChartBuilder() \
    .column_chart() \
    .title("Budget vs Actual") \
    .series("Budget", "B2:B11") \
    .series("Actual", "C2:C11") \
    .position("E2") \
    .build()

builder.chart(chart)
builder.save("budget.ods")
```

## CLI Quick Start

```bash
# Generate budget
uv run spreadsheet-dl generate -o ./budgets/

# Add expense (directly modifies ODS files)
uv run spreadsheet-dl expense 25.50 "Lunch" -c "Dining Out"

# Analyze budget
uv run spreadsheet-dl analyze budget.ods

# View dashboard
uv run spreadsheet-dl dashboard budget.ods
```

## Architecture

```
spreadsheet-dl/
├── src/spreadsheet_dl/
│   ├── ods_generator.py    # Create ODS files
│   ├── ods_editor.py       # Modify existing ODS files
│   ├── budget_analyzer.py  # Analyze budgets
│   ├── builder.py          # Fluent builder API
│   ├── charts.py           # Chart builder (NEW)
│   ├── cli.py              # Command-line interface
│   ├── exceptions.py       # Comprehensive error hierarchy
│   ├── schema/             # Data classes and styles
│   ├── template_engine/    # Template system (NEW)
│   │   ├── schema.py       # Template data structures
│   │   ├── loader.py       # YAML template loading
│   │   ├── renderer.py     # Template rendering
│   │   └── components.py   # Pre-built components
│   └── ...
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## Error Handling

SpreadsheetDL uses structured error codes for programmatic error handling:

```python
from spreadsheet_dl.exceptions import InvalidAmountError

try:
    # Process expense
    ...
except InvalidAmountError as e:
    print(f"Error [{e.error_code}]: {e.message}")
    print(f"Suggestion: {e.suggestion}")
    # Output:
    # Error [FT-VAL-401]: Invalid amount 'abc': Not a valid number
    # Suggestion: Enter a numeric value without letters (e.g., 99.99 or 99).
```

See [Error Codes Reference](error-codes.md) for complete documentation.

## License

MIT License - See LICENSE file for details.
