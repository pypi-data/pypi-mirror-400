# Domain-Specific Plugin Examples

Domain plugins extend SpreadsheetDL with specialized formulas and functions for specific fields like science, engineering, and data analysis.

## What You'll Learn

- How to use domain-specific plugins
- Available formulas in each domain
- Integration with core spreadsheet functionality
- Real-world domain-specific workflows

## Time Estimate

- Basic usage: 10 minutes
- Full domain exploration: 45 minutes

## Prerequisites

- Completed 01_basics examples
- Understanding of formulas (02_formulas)

## Available Domain Plugins

SpreadsheetDL includes 9 specialized domain plugins:

1. **Finance** - Budget analysis, NPV, IRR, amortization
2. **Data Science** - Statistical functions, ML metrics, clustering
3. **Biology** - Dilution, concentration, genetics, pharmacokinetics
4. **Chemistry** - Solutions, kinetics, thermodynamics
5. **Physics** - Mechanics, electromagnetism, optics, quantum
6. **Electrical Engineering** - AC circuits, power, filters, digital logic
7. **Mechanical Engineering** - Stress/strain, fluid mechanics, thermal
8. **Civil Engineering** - Beam calculations, soil mechanics, hydrology
9. **Manufacturing** - OEE, quality metrics, inventory, Six Sigma

## Examples in This Directory

1. `01_biology_plugin.py` - Life sciences calculations
2. `02_chemistry_plugin.py` - Chemical calculations
3. `03_physics_plugin.py` - Physics formulas
4. `04_data_science_plugin.py` - Statistical and ML functions
5. `05_engineering_plugins.py` - Combined engineering examples

## Quick Start

```python
from spreadsheet_dl import create_spreadsheet
from spreadsheet_dl.domains.biology import BiologyPlugin

# Create spreadsheet with biology plugin
builder = create_spreadsheet()
builder.register_plugin(BiologyPlugin())

# Use specialized formulas
builder.add_formula("A1", "=DILUTION(10, 100, 50)")  # Dilution calculation
```

## Plugin Discovery

List all available plugins:

```bash
spreadsheet-dl plugin list
```

Enable/disable plugins:

```bash
spreadsheet-dl plugin enable biology
spreadsheet-dl plugin disable biology
```

## Next Steps

- Explore `../04_advanced/01_plugin_system.py` for custom plugin creation
- See domain-specific documentation in `../../docs/api/domain-plugins.md`
- Try combining multiple domain plugins in one spreadsheet

## Common Use Cases

### Research Lab

Combine biology and chemistry plugins for lab calculations:

```python
from spreadsheet_dl.domains.biology.formulas import dilution_factor
from spreadsheet_dl.domains.chemistry.formulas import molarity

# Calculate dilutions and concentrations
result = dilution_factor(stock_conc=10.0, final_conc=1.0, final_volume=100.0)
```

### Engineering Analysis

Use engineering plugins for structural calculations:

```python
from spreadsheet_dl.domains.civil_engineering.formulas import beam_deflection
from spreadsheet_dl.domains.mechanical_engineering.formulas import stress_strain

# Structural analysis
deflection = beam_deflection(load=1000, length=5.0, E=200e9, I=1e-6)
```

### Data Analysis

Leverage data science plugin for statistical work:

```python
from spreadsheet_dl.domains.data_science.formulas import regression_metrics
from spreadsheet_dl.domains.data_science.formulas import time_series_decompose

# Statistical analysis
metrics = regression_metrics(y_true, y_pred)
```

## Tips

- Check plugin documentation for available formulas
- Plugins can be combined in the same spreadsheet
- Most plugins provide both formula functions and helper utilities
- Domain-specific importers available (e.g., FASTA for biology)
