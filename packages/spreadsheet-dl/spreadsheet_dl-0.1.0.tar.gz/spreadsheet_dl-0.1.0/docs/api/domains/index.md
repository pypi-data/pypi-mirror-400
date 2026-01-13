# Domain Plugins

SpreadsheetDL provides 11 specialized domain plugins with extensive formulas for science, engineering, and business applications.

## Domain Overview

| Domain                                                     | Description                                            |
| ---------------------------------------------------------- | ------------------------------------------------------ |
| [Physics](physics/plugin.md)                               | Mechanics, electromagnetism, optics, quantum mechanics |
| [Chemistry](chemistry/plugin.md)                           | Thermodynamics, solutions, reaction kinetics           |
| [Biology](biology/plugin.md)                               | Pharmacokinetics, genetics, plate reader analysis      |
| [Data Science](data_science/plugin.md)                     | Statistical tests, ML metrics, time series             |
| [Electrical Engineering](electrical_engineering/plugin.md) | Power calculations, signal processing, filter design   |
| [Mechanical Engineering](mechanical_engineering/plugin.md) | Stress analysis, thermal, fluid mechanics              |
| [Civil Engineering](civil_engineering/plugin.md)           | Structural loads, concrete, foundation design          |
| [Environmental](environmental/plugin.md)                   | Air/water quality, carbon footprint, climate modeling  |
| [Manufacturing](manufacturing/plugin.md)                   | OEE, lean metrics, Six Sigma, supply chain             |
| [Education](education/plugin.md)                           | Assessment theory, grading, learning analytics         |
| [Finance](finance/__init__.md)                             | NPV, IRR, options pricing, risk metrics                |

## Using Domain Plugins

### Loading a Plugin

```python
from spreadsheet_dl.domains.physics import PhysicsDomainPlugin

# Create and initialize
plugin = PhysicsDomainPlugin()
plugin.initialize()

# List available formulas
formulas = plugin.list_formulas()
print(f"Available: {len(formulas)} formulas")

# Get a specific formula
kinetic_energy = plugin.get_formula("KINETIC_ENERGY")
```

### Using Domain Formulas

```python
from spreadsheet_dl import create_spreadsheet, formula
from spreadsheet_dl.domains.physics import PhysicsDomainPlugin

# Load physics formulas
physics = PhysicsDomainPlugin()
physics.initialize()

# Use in spreadsheet
builder = create_spreadsheet(theme="default")
f = formula()

builder.sheet("Experiment") \
    .column("Mass (kg)", type="number") \
    .column("Velocity (m/s)", type="number") \
    .column("Kinetic Energy (J)", type="number") \
    .header_row() \
    .row().cell(10).cell(5).cell(formula="=0.5*A2*B2^2")

builder.save("physics_experiment.ods")
```

### Plugin Architecture

All domain plugins inherit from `BaseDomainPlugin` and provide:

- **Formulas**: Domain-specific calculations
- **Importers**: Data format parsers (CSV, lab equipment, etc.)
- **Utils**: Helper functions and constants

## Domain Categories

### Physical Sciences

- **[Physics](physics/plugin.md)** - Classical and modern physics
- **[Chemistry](chemistry/plugin.md)** - Reactions, thermodynamics, solutions

### Life Sciences

- **[Biology](biology/plugin.md)** - Pharmacokinetics, genetics, plate layouts

### Engineering

- **[Electrical Engineering](electrical_engineering/plugin.md)** - Circuits, power, signals
- **[Mechanical Engineering](mechanical_engineering/plugin.md)** - Stress, thermal, fluids
- **[Civil Engineering](civil_engineering/plugin.md)** - Structures, foundations
- **[Environmental](environmental/plugin.md)** - Climate, air/water quality

### Data & Analytics

- **[Data Science](data_science/plugin.md)** - Statistics, ML metrics

### Business & Industry

- **[Manufacturing](manufacturing/plugin.md)** - OEE, lean, Six Sigma
- **[Education](education/plugin.md)** - Assessment, grading
- **[Finance](finance/__init__.md)** - Financial calculations, budgeting

## Creating Custom Plugins

See [Plugin Development Guide](../../guides/plugin-development.md) for creating your own domain plugins.

```python
from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

class MyDomainPlugin(BaseDomainPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_domain",
            version="1.0.0",
            description="Custom domain plugin",
            author="Your Name",
            license="MIT",
            tags=("custom", "domain"),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        self.register_formula("MY_FORMULA", MyFormula)

    def cleanup(self) -> None:
        pass

    def validate(self) -> bool:
        return len(self._formulas) > 0
```

## API Reference

::: spreadsheet_dl.domains
