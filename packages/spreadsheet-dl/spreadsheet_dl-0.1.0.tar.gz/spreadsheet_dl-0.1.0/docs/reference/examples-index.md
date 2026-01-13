# Example Scripts Index

SpreadsheetDL includes comprehensive example scripts demonstrating all major features. Examples are organized by complexity and topic area.

## Quick Navigation

- [Basics](#basics) - Getting started examples
- [Formulas](#formulas) - Working with formulas and calculations
- [Charts](#charts) - Visualization and charting
- [Advanced](#advanced) - Plugins, MCP server, templates
- [Standalone Scripts](#standalone-scripts) - Legacy examples

---

## Basics

Located in `examples/01_basics/`

### 01_hello_budget.py

**Purpose:** Introduction to SpreadsheetDL with a simple budget spreadsheet.

**Topics covered:**

- Creating a workbook
- Adding sheets
- Setting cell values
- Basic formatting

**Run:** `uv run python examples/01_basics/01_hello_budget.py`

### 02_create_custom_budget.py

**Purpose:** Create a customized budget with multiple categories.

**Topics covered:**

- Custom sheet structure
- Multiple data rows
- Cell formulas (SUM, AVERAGE)
- Output to ODS file

**Run:** `uv run python examples/01_basics/02_create_custom_budget.py`

### 03_import_csv.py

**Purpose:** Import data from CSV files into a spreadsheet.

**Topics covered:**

- CSV file reading
- Data transformation
- Populating sheets from external data

**Run:** `uv run python examples/01_basics/03_import_csv.py`

### 04_progress_indicators.py

**Purpose:** Display progress indicators during long operations.

**Topics covered:**

- Rich library integration
- Progress bars
- Spinners
- Console output

**Run:** `uv run python examples/01_basics/04_progress_indicators.py`

---

## Formulas

Located in `examples/02_formulas/`

### 01_analyze_budget.py

**Purpose:** Analyze budget data using built-in formulas.

**Topics covered:**

- SUM formulas
- AVERAGE calculations
- Budget vs. actual comparisons
- Variance analysis

**Run:** `uv run python examples/02_formulas/01_analyze_budget.py`

### 02_generate_reports.py

**Purpose:** Generate formatted reports from spreadsheet data.

**Topics covered:**

- Report generation
- Multi-sheet reports
- Summary statistics
- Formatted output

**Run:** `uv run python examples/02_formulas/02_generate_reports.py`

### 03_custom_reports.py

**Purpose:** Create custom report templates with advanced formatting.

**Topics covered:**

- Custom templates
- Header/footer styling
- Conditional formatting
- Print layout

**Run:** `uv run python examples/02_formulas/03_custom_reports.py`

### 04_realistic_workflow.py

**Purpose:** Complete end-to-end budget workflow example.

**Topics covered:**

- Data entry
- Formula calculations
- Report generation
- Export to multiple formats

**Run:** `uv run python examples/02_formulas/04_realistic_workflow.py`

---

## Charts

Located in `examples/03_charts/`

### 01_basic_charts.py

**Purpose:** Create basic chart types (bar, line, pie).

**Topics covered:**

- ChartSpec usage
- Bar charts
- Line charts
- Pie charts
- Chart positioning

**Run:** `uv run python examples/03_charts/01_basic_charts.py`

### 02_chart_builder_advanced.py

**Purpose:** Advanced chart building with the fluent API.

**Topics covered:**

- ChartBuilder fluent interface
- Multi-series charts
- Axis customization
- Legend configuration

**Run:** `uv run python examples/03_charts/02_chart_builder_advanced.py`

### 03_chart_colors.py

**Purpose:** Customize chart colors and themes.

**Topics covered:**

- Color schemes
- Custom palettes
- Theme integration
- Gradient effects

**Run:** `uv run python examples/03_charts/03_chart_colors.py`

### 04_sparklines.py

**Purpose:** Add sparklines for inline data visualization.

**Topics covered:**

- SparklineSpec usage
- Line sparklines
- Column sparklines
- Win/loss sparklines
- Sparkline colors

**Run:** `uv run python examples/03_charts/04_sparklines.py`

---

## Advanced

Located in `examples/04_advanced/`

### 01_plugin_system.py

**Purpose:** Create and use domain plugins.

**Topics covered:**

- Plugin architecture
- Custom formula registration
- Domain-specific calculations
- Plugin lifecycle

**Run:** `uv run python examples/04_advanced/01_plugin_system.py`

### 02_mcp_basics.py

**Purpose:** Introduction to MCP server integration.

**Topics covered:**

- MCP configuration
- Tool invocation
- Basic operations
- Error handling

**Run:** `uv run python examples/04_advanced/02_mcp_basics.py`

### 03_mcp_server_usage.py

**Purpose:** Complete MCP server usage patterns.

**Topics covered:**

- Server initialization
- All tool categories
- Batch operations
- Advanced queries

**Run:** `uv run python examples/04_advanced/03_mcp_server_usage.py`

---

## Template Engine

Located in `examples/template_engine/`

### 01_basic_loading.py

**Purpose:** Load and render YAML templates.

**Run:** `uv run python examples/template_engine/01_basic_loading.py`

### 02_variable_substitution.py

**Purpose:** Use variables in templates.

**Run:** `uv run python examples/template_engine/02_variable_substitution.py`

### 03_conditional_rendering.py

**Purpose:** Conditional sections in templates.

**Run:** `uv run python examples/template_engine/03_conditional_rendering.py`

### 04_component_composition.py

**Purpose:** Compose templates from components.

**Run:** `uv run python examples/template_engine/04_component_composition.py`

### 05_complete_template.py

**Purpose:** Complete template with all features.

**Run:** `uv run python examples/template_engine/05_complete_template.py`

### 06_builtin_functions.py

**Purpose:** Built-in template functions.

**Run:** `uv run python examples/template_engine/06_builtin_functions.py`

### 07_custom_template.py

**Purpose:** Create custom template functions.

**Run:** `uv run python examples/template_engine/07_custom_template.py`

### 08_error_handling.py

**Purpose:** Template error handling.

**Run:** `uv run python examples/template_engine/08_error_handling.py`

### run_all.py

**Purpose:** Run all template examples in sequence.

**Run:** `uv run python examples/template_engine/run_all.py`

---

## Standalone Scripts

Legacy examples in `examples/` root directory.

| Script                         | Purpose               |
| ------------------------------ | --------------------- |
| `create_budget.py`             | Quick budget creation |
| `analyze_budget.py`            | Budget analysis       |
| `generate_report.py`           | Report generation     |
| `realistic_budget_workflow.py` | Complete workflow     |
| `example_budget.py`            | Budget example        |
| `example_chart.py`             | Chart example         |
| `example_import.py`            | Import example        |
| `example_mcp.py`               | MCP example           |
| `example_plugin.py`            | Plugin example        |
| `example_report.py`            | Report example        |
| `chart_builder_advanced.py`    | Advanced charts       |
| `chart_colors_demo.py`         | Color demo            |
| `sparklines_demo.py`           | Sparklines demo       |
| `demo_progress.py`             | Progress demo         |
| `template_engine_usage.py`     | Template usage        |
| `mcp_server_usage.py`          | MCP server usage      |

---

## Running Examples

### Prerequisites

```bash
# Install development dependencies
uv sync

# Or install example dependencies only
uv add rich pandas
```

### Run Individual Example

```bash
uv run python examples/01_basics/01_hello_budget.py
```

### Run All Organized Examples

```bash
# Basics
for f in examples/01_basics/*.py; do uv run python "$f"; done

# Formulas
for f in examples/02_formulas/*.py; do uv run python "$f"; done

# Charts
for f in examples/03_charts/*.py; do uv run python "$f"; done

# Advanced
for f in examples/04_advanced/*.py; do uv run python "$f"; done
```

### Run Template Engine Examples

```bash
uv run python examples/template_engine/run_all.py
```

---

## Output Files

Examples generate output files in the current directory:

| Example Category | Output Files                      |
| ---------------- | --------------------------------- |
| Basics           | `budget.ods`, `custom_budget.ods` |
| Formulas         | `analysis.ods`, `report.ods`      |
| Charts           | `charts.ods`, `sparklines.ods`    |
| Templates        | `template_output.ods`             |

Clean up output files:

```bash
rm -f *.ods *.xlsx *.csv *.pdf
```

---

## Example Structure

Each example follows a consistent structure:

```python
"""Example description.

Purpose:
    What this example demonstrates.

Topics covered:
    - Topic 1
    - Topic 2

Output:
    Description of output files.
"""

from spreadsheet_dl import ...

def main():
    # Example code
    pass

if __name__ == "__main__":
    main()
```

---

## See Also

- [Tutorial: Create Your First Budget](../tutorials/01-create-budget.md)
- [API Reference](../api/index.md)
- [Formula Reference](formula-reference.md)
