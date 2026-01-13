# Domain Plugin Development Guide

PHASE0-003

Complete guide for developing SpreadsheetDL domain plugins.

## Table of Contents

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
- [Creating Your First Plugin](#creating-your-first-plugin)
- [Working with Templates](#working-with-templates)
- [Adding Custom Formulas](#adding-custom-formulas)
- [Building Data Importers](#building-data-importers)
- [Registration and Discovery](#registration-and-discovery)
- [Testing Your Plugin](#testing-your-plugin)
- [Distribution](#distribution)
- [Best Practices](#best-practices)
- [Reference: Finance Plugin](#reference-finance-plugin)

## Introduction

SpreadsheetDL v0.1 introduces a powerful domain plugin architecture that enables you to extend the core platform with domain-specific functionality. Whether you're building tools for data science, engineering, education, or any other domain, the plugin system provides a structured framework for templates, formulas, and data importers.

### What is a Domain Plugin?

A domain plugin is a Python package that extends SpreadsheetDL with:

- **Templates**: Pre-configured spreadsheet layouts for common use cases
- **Formulas**: Domain-specific calculation functions
- **Importers**: Tools for importing data from external sources
- **Metadata**: Rich documentation and discovery information

### Why Use Plugins?

- **Modularity**: Keep domain logic separate from core platform
- **Reusability**: Share templates and tools across projects
- **Discoverability**: Users can find and install domain-specific functionality
- **Type Safety**: Full type hint support with mypy validation
- **Documentation**: Automatic API documentation generation

## Architecture Overview

The domain plugin system is built on four base classes:

```
BaseDomainPlugin (Core)
├── BaseTemplate (Spreadsheet Templates)
├── BaseFormula (Formula Extensions)
└── BaseImporter[T] (Data Importers)
```

### Component Responsibilities

**BaseDomainPlugin**:

- Plugin lifecycle management (initialize, cleanup)
- Component registration (templates, formulas, importers)
- Dependency declaration
- Metadata and versioning

**BaseTemplate**:

- Generate SpreadsheetBuilder instances
- Apply domain-specific formatting and structure
- Support customization and themes

**BaseFormula**:

- Define domain-specific calculation functions
- Integrate with FormulaBuilder
- Provide argument validation

**BaseImporter[T]**:

- Import data from external sources
- Transform and validate imported data
- Report progress and errors

## Getting Started

### Prerequisites

- Python 3.12+
- SpreadsheetDL 0.1.0+
- Basic understanding of SpreadsheetBuilder API
- Familiarity with Python type hints

### Project Structure

Recommended structure for a domain plugin:

```
spreadsheet_dl_science/          # Your plugin package
├── __init__.py                  # Plugin exports
├── plugin.py                    # ScienceDomainPlugin class
├── templates/
│   ├── __init__.py
│   ├── experiment_log.py        # ExperimentLogTemplate
│   └── data_analysis.py         # DataAnalysisTemplate
├── formulas/
│   ├── __init__.py
│   ├── statistics.py            # Statistical formulas
│   └── chemistry.py             # Chemistry formulas
├── importers/
│   ├── __init__.py
│   ├── csv_data.py              # CSVDataImporter
│   └── api_data.py              # APIDataImporter
└── tests/
    ├── __init__.py
    ├── test_plugin.py
    ├── test_templates.py
    ├── test_formulas.py
    └── test_importers.py
```

### Installation

Install SpreadsheetDL and development dependencies:

```bash
uv pip install spreadsheet-dl[dev]>=0.1.0
```

Or with uv:

```bash
uv add spreadsheet-dl[dev]>=0.1.0
```

## Creating Your First Plugin

Let's create a simple science domain plugin step by step.

### Step 1: Define Plugin Class

Create `plugin.py`:

```python
"""Science Domain Plugin for SpreadsheetDL."""

from spreadsheet_dl.domains.base import (
    BaseDomainPlugin,
    PluginMetadata,
    PluginDependency,
)


class ScienceDomainPlugin(BaseDomainPlugin):
    """
    Science domain plugin.

    Implements:
        SCIENCE-001: Science domain plugin

    Provides templates, formulas, and importers for scientific
    workflows including experiment tracking, data analysis,
    and statistical calculations.
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="science",
            version="1.0.0",
            description="Scientific analysis and experiment tracking",
            author="Your Name",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl-science",
            tags=("science", "experiments", "statistics", "data"),
            min_spreadsheet_dl_version="0.1.0",
        )

    @property
    def dependencies(self) -> list[PluginDependency]:
        """Declare plugin dependencies."""
        # Optional: depend on other plugins
        return []

    def initialize(self) -> None:
        """
        Initialize plugin resources.

        Called once when plugin is loaded. Register all
        templates, formulas, and importers here.
        """
        # Import here to avoid circular dependencies
        from .templates.experiment_log import ExperimentLogTemplate
        from .formulas.statistics import TTestFormula, ChiSquareFormula
        from .importers.csv_data import CSVDataImporter

        # Register templates
        self.register_template("experiment_log", ExperimentLogTemplate)

        # Register formulas
        self.register_formula("TTEST", TTestFormula)
        self.register_formula("CHISQ", ChiSquareFormula)

        # Register importers
        self.register_importer("csv", CSVDataImporter)

    def cleanup(self) -> None:
        """
        Cleanup plugin resources.

        Called when plugin is unloaded. Release any resources,
        close connections, etc.
        """
        # No cleanup needed for this plugin
        pass

    def validate(self) -> bool:
        """
        Validate plugin configuration.

        Returns:
            True if plugin is properly configured
        """
        # Ensure we registered at least one component
        return (
            len(self._templates) > 0 or
            len(self._formulas) > 0 or
            len(self._importers) > 0
        )
```

### Step 2: Create Plugin Metadata

The `PluginMetadata` class defines discoverable information about your plugin:

- **name**: Unique identifier (lowercase, no spaces) - used for plugin lookup
- **version**: Semantic version (e.g., "1.0.0")
- **description**: Human-readable description shown in plugin listings
- **author**: Plugin maintainer
- **license**: SPDX license identifier (e.g., "MIT", "Apache-2.0")
- **homepage**: Plugin documentation or repository URL
- **tags**: Searchable keywords for discovery
- **min_spreadsheet_dl_version**: Minimum required SpreadsheetDL version

### Step 3: Implement Lifecycle Methods

**initialize()**:

- Called once when plugin loads
- Register all templates, formulas, and importers
- Setup any required resources

**cleanup()**:

- Called when plugin unloads
- Release resources, close connections
- Safe to call even if initialize() failed

**validate()** (optional):

- Called after initialize() to verify configuration
- Return True if plugin is ready, False otherwise

## Working with Templates

Templates generate pre-configured spreadsheets for common use cases.

### Creating a Template

Create `templates/experiment_log.py`:

```python
"""Experiment log template."""

from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.domains.base import BaseTemplate, TemplateMetadata


class ExperimentLogTemplate(BaseTemplate):
    """
    Scientific experiment log template.

    Implements:
        SCIENCE-TMPL-001: Experiment log template

    Features:
    - Experiment metadata section
    - Materials and methods tracking
    - Observations and results tables
    - Statistical analysis area
    - Professional formatting
    """

    @property
    def metadata(self) -> TemplateMetadata:
        """Get template metadata."""
        return TemplateMetadata(
            name="Experiment Log",
            description="Track scientific experiments with observations and results",
            category="science",
            tags=("experiment", "lab", "research"),
            version="1.0.0",
            author="Your Name",
        )

    def generate(self) -> SpreadsheetBuilder:
        """
        Generate experiment log spreadsheet.

        Returns:
            Configured SpreadsheetBuilder instance
        """
        builder = SpreadsheetBuilder(theme=self._theme)

        # Set workbook properties
        builder.workbook_properties(
            title="Experiment Log",
            author=self.get_config("researcher_name", "Researcher"),
            subject="Scientific Experiment",
            description="Laboratory experiment tracking and analysis",
            keywords=["experiment", "science", "research"],
        )

        # Create main experiment sheet
        self._create_experiment_sheet(builder)

        # Create data analysis sheet
        self._create_analysis_sheet(builder)

        return builder

    def _create_experiment_sheet(self, builder: SpreadsheetBuilder) -> None:
        """Create the main experiment tracking sheet."""
        builder.sheet("Experiment")

        # Define columns
        builder.column("Field", width="150pt")
        builder.column("Value", width="300pt")
        builder.column("Notes", width="200pt")

        builder.freeze(rows=1)

        # Header
        builder.row(style="header_primary")
        builder.cell("Experiment Log", colspan=3)

        # Metadata section
        builder.row(style="section_header")
        builder.cell("Experiment Information", colspan=3)

        metadata_fields = [
            ("Experiment ID", self.get_config("experiment_id", "")),
            ("Date", "=TODAY()"),
            ("Researcher", self.get_config("researcher_name", "")),
            ("Hypothesis", ""),
            ("Objective", ""),
        ]

        for field_name, default_value in metadata_fields:
            builder.row()
            builder.cell(field_name, style="label")
            builder.cell(default_value, style="input")
            builder.cell("", style="input")

        # Materials section
        builder.row()
        builder.row(style="section_header")
        builder.cell("Materials", colspan=3)

        builder.row(style="header_secondary")
        builder.cell("Item")
        builder.cell("Quantity")
        builder.cell("Specifications")

        for _ in range(10):
            builder.row()
            builder.cell("", style="input")
            builder.cell("", style="input")
            builder.cell("", style="input")

        # Observations section
        builder.row()
        builder.row(style="section_header")
        builder.cell("Observations", colspan=3)

        builder.row(style="header_secondary")
        builder.cell("Time")
        builder.cell("Observation")
        builder.cell("Measurements")

        for _ in range(15):
            builder.row()
            builder.cell("", style="input")
            builder.cell("", style="input")
            builder.cell("", style="input")

    def _create_analysis_sheet(self, builder: SpreadsheetBuilder) -> None:
        """Create data analysis sheet."""
        builder.sheet("Analysis")

        builder.column("Metric", width="150pt")
        builder.column("Value", width="100pt", type="number")
        builder.column("Unit", width="80pt")
        builder.column("Statistical Significance", width="120pt")

        builder.freeze(rows=1)

        builder.row(style="header_primary")
        builder.cell("Statistical Analysis", colspan=4)

        builder.row(style="header_secondary")
        builder.cell("Metric")
        builder.cell("Value")
        builder.cell("Unit")
        builder.cell("Significance")

        # Placeholder rows for analysis
        metrics = [
            "Mean",
            "Median",
            "Standard Deviation",
            "Sample Size",
            "Confidence Interval (95%)",
            "P-Value",
        ]

        for metric in metrics:
            builder.row()
            builder.cell(metric, style="label")
            builder.cell("", style="input")
            builder.cell("", style="input")
            builder.cell("", style="input")

    def validate(self) -> bool:
        """
        Validate template configuration.

        Returns:
            True if configuration is valid
        """
        # Could add validation for required config fields
        return True

    def customize(self, builder: SpreadsheetBuilder) -> SpreadsheetBuilder:
        """
        Apply customizations to generated builder.

        Args:
            builder: SpreadsheetBuilder instance

        Returns:
            Customized builder
        """
        # Example: Add logo if configured
        if self.get_config("add_logo"):
            # Add logo to first sheet
            pass

        return builder
```

### Template Best Practices

1. **Use configuration options**: Accept customization via `__init__(**kwargs)`
2. **Provide sensible defaults**: Template should work with no configuration
3. **Include rich metadata**: Help users discover your template
4. **Reference requirement IDs**: Document which requirements are implemented
5. **Freeze panes**: Make navigation easier with `builder.freeze()`
6. **Use consistent styling**: Leverage theme system
7. **Add helper methods**: Break complex generation into private methods

## Adding Custom Formulas

Formulas extend the calculation capabilities with domain-specific functions.

### Creating a Formula

Create `formulas/statistics.py`:

```python
"""Statistical formulas for science domain."""

from typing import Any

from spreadsheet_dl.domains.base import (
    BaseFormula,
    FormulaArgument,
    FormulaMetadata,
)


class TTestFormula(BaseFormula):
    """
    T-test statistical formula.

    Implements:
        SCIENCE-FORM-001: T-test formula

    Performs Student's t-test to compare two samples.
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="TTEST",
            category="statistical",
            description="Perform Student's t-test on two data samples",
            arguments=(
                FormulaArgument(
                    name="array1",
                    type="range",
                    required=True,
                    description="First data array (sample 1)",
                ),
                FormulaArgument(
                    name="array2",
                    type="range",
                    required=True,
                    description="Second data array (sample 2)",
                ),
                FormulaArgument(
                    name="tails",
                    type="number",
                    required=False,
                    default=2,
                    description="Number of tails (1 or 2)",
                ),
                FormulaArgument(
                    name="type",
                    type="number",
                    required=False,
                    default=1,
                    description="Test type (1=paired, 2=equal variance, 3=unequal)",
                ),
            ),
            return_type="number",
            examples=(
                "=TTEST(A1:A10, B1:B10, 2, 1)",
                "=TTEST(Data1, Data2, 1, 2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """
        Build ODF formula string.

        Args:
            *args: Formula arguments (array1, array2, tails, type)
            **kwargs: Keyword arguments (unused)

        Returns:
            ODF formula string (without leading =)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        # Extract arguments
        array1 = args[0]
        array2 = args[1]
        tails = args[2] if len(args) > 2 else 2
        test_type = args[3] if len(args) > 3 else 1

        # Build ODF formula (semicolon-separated in ODF)
        return f"TTEST({array1};{array2};{tails};{test_type})"

    def validate_arguments(self, args: tuple[Any, ...]) -> None:
        """
        Validate formula arguments.

        Args:
            args: Arguments to validate

        Raises:
            ValueError: If arguments are invalid
        """
        # Call parent validation first
        super().validate_arguments(args)

        # Additional custom validation
        if len(args) >= 3:
            tails = args[2]
            if isinstance(tails, (int, float)) and tails not in (1, 2):
                msg = "tails must be 1 or 2"
                raise ValueError(msg)

        if len(args) >= 4:
            test_type = args[3]
            if isinstance(test_type, (int, float)) and test_type not in (1, 2, 3):
                msg = "type must be 1, 2, or 3"
                raise ValueError(msg)


class ChiSquareFormula(BaseFormula):
    """
    Chi-square test formula.

    Implements:
        SCIENCE-FORM-002: Chi-square test
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CHISQ",
            category="statistical",
            description="Perform chi-square test for independence",
            arguments=(
                FormulaArgument(
                    name="observed",
                    type="range",
                    required=True,
                    description="Observed frequencies",
                ),
                FormulaArgument(
                    name="expected",
                    type="range",
                    required=True,
                    description="Expected frequencies",
                ),
            ),
            return_type="number",
            examples=(
                "=CHISQ(A1:C3, D1:F3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string."""
        self.validate_arguments(args)

        observed = args[0]
        expected = args[1]

        return f"CHISQ.TEST({observed};{expected})"
```

### Formula Best Practices

1. **Use uppercase names**: Formula names must be UPPERCASE (enforced)
2. **Validate arguments**: Override `validate_arguments()` for custom validation
3. **Document examples**: Provide realistic usage examples
4. **Follow ODF syntax**: Use semicolons to separate arguments
5. **Handle optional args**: Provide sensible defaults
6. **Rich metadata**: Include comprehensive descriptions

## Building Data Importers

Importers bring data from external sources into spreadsheets.

### Creating an Importer

Create `importers/csv_data.py`:

```python
"""CSV data importer for science domain."""

from pathlib import Path
import csv
from typing import Any

from spreadsheet_dl.domains.base import (
    BaseImporter,
    ImporterMetadata,
    ImportResult,
)


class CSVDataImporter(BaseImporter[list[dict[str, Any]]]):
    """
    CSV data importer.

    Implements:
        SCIENCE-IMP-001: CSV data import

    Imports scientific data from CSV files with automatic
    type detection and validation.
    """

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="CSV Data Importer",
            description="Import experimental data from CSV files",
            supported_formats=("csv", "txt", "tsv"),
            category="science",
        )

    def validate_source(self, source: Path | str) -> bool:
        """
        Validate data source.

        Args:
            source: Path to data source file

        Returns:
            True if source is valid
        """
        path = Path(source) if isinstance(source, str) else source

        # Check file exists
        if not path.exists():
            return False

        # Check file extension
        if path.suffix.lower() not in (".csv", ".txt", ".tsv"):
            return False

        # Check file is readable
        try:
            with path.open() as f:
                f.read(1)
            return True
        except (OSError, PermissionError):
            return False

    def import_data(
        self,
        source: Path | str,
    ) -> ImportResult[list[dict[str, Any]]]:
        """
        Import data from CSV source.

        Args:
            source: Path to CSV file

        Returns:
            ImportResult with imported data

        Raises:
            ValueError: If source is invalid
            IOError: If source cannot be read
        """
        # Validate source
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid source file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        # Get configuration
        delimiter = self.get_config("delimiter", ",")
        if path.suffix.lower() == ".tsv":
            delimiter = "\t"

        encoding = self.get_config("encoding", "utf-8")
        skip_rows = self.get_config("skip_rows", 0)

        errors: list[str] = []
        warnings: list[str] = []
        data: list[dict[str, Any]] = []

        try:
            with path.open(encoding=encoding) as csvfile:
                # Skip header rows if configured
                for _ in range(skip_rows):
                    next(csvfile, None)

                # Read CSV
                reader = csv.DictReader(csvfile, delimiter=delimiter)

                total_rows = 0
                for row_num, row in enumerate(reader, start=1):
                    total_rows = row_num

                    # Progress callback
                    if row_num % 100 == 0:
                        self.on_progress(row_num, row_num)  # Total unknown

                    # Transform row
                    transformed_row = self._transform_row(row, row_num, warnings)
                    data.append(transformed_row)

                # Final progress
                self.on_progress(total_rows, total_rows)

        except UnicodeDecodeError as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Encoding error: {e}. Try setting encoding parameter."],
            )
        except csv.Error as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"CSV parsing error: {e}"],
            )
        except OSError as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"File read error: {e}"],
            )

        # Transform data if configured
        if self.get_config("auto_transform", True):
            data = self.transform(data)

        return ImportResult(
            success=True,
            data=data,
            records_imported=len(data),
            errors=errors,
            warnings=warnings,
            metadata={
                "source_file": str(path),
                "delimiter": delimiter,
                "encoding": encoding,
                "total_rows": len(data),
            },
        )

    def _transform_row(
        self,
        row: dict[str, str],
        row_num: int,
        warnings: list[str],
    ) -> dict[str, Any]:
        """
        Transform a single row, converting types.

        Args:
            row: Raw row data
            row_num: Row number (for error reporting)
            warnings: List to append warnings to

        Returns:
            Transformed row with type conversions
        """
        transformed: dict[str, Any] = {}

        for key, value in row.items():
            # Try to convert to number
            try:
                if "." in value:
                    transformed[key] = float(value)
                else:
                    transformed[key] = int(value)
            except ValueError:
                # Keep as string
                transformed[key] = value

        return transformed

    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Transform imported data.

        Args:
            data: Raw imported data

        Returns:
            Transformed data
        """
        # Apply any configured transformations
        if self.get_config("normalize_column_names", False):
            data = [
                {key.lower().replace(" ", "_"): value for key, value in row.items()}
                for row in data
            ]

        return data
```

### Importer Best Practices

1. **Generic type parameter**: Specify return type (e.g., `BaseImporter[list[dict]]`)
2. **Validate before import**: Always check source validity
3. **Comprehensive error handling**: Catch and report specific errors
4. **Progress reporting**: Call `self.on_progress()` for long operations
5. **Configuration support**: Accept options via `__init__(**kwargs)`
6. **Transform hook**: Use `transform()` for post-processing
7. **Rich result metadata**: Include useful information in ImportResult

## Registration and Discovery

### Registering Your Plugin

In your package's `__init__.py`:

```python
"""Science domain plugin for SpreadsheetDL."""

from spreadsheet_dl.domains.base import BaseDomainPlugin
from .plugin import ScienceDomainPlugin

# Auto-register plugin when imported
BaseDomainPlugin.register_plugin(ScienceDomainPlugin)

__all__ = ["ScienceDomainPlugin"]
```

### Loading Plugins

Users can load your plugin in their code:

```python
from spreadsheet_dl.domains.base import BaseDomainPlugin
import spreadsheet_dl_science  # Auto-registers

# Get plugin class
plugin_class = BaseDomainPlugin.get_plugin_class("science")

# Instantiate and initialize
plugin = plugin_class()
plugin.initialize()

# Use templates
template_class = plugin.get_template("experiment_log")
template = template_class(researcher_name="Dr. Smith")
builder = template.generate()
builder.save("experiment.ods")
```

### Plugin Discovery

List all registered plugins:

```python
from spreadsheet_dl.domains.base import BaseDomainPlugin

# List all plugin names
plugins = BaseDomainPlugin.list_plugins()
print(plugins)  # ['finance', 'science', ...]

# Get plugin metadata
plugin_class = BaseDomainPlugin.get_plugin_class("science")
plugin = plugin_class()
print(plugin.metadata.description)
print(plugin.metadata.tags)
```

## Testing Your Plugin

### Unit Tests Structure

Create comprehensive tests for all components:

```python
"""Tests for science domain plugin."""

import pytest
from pathlib import Path

from spreadsheet_dl.domains.base import (
    BaseDomainPlugin,
    PluginStatus,
)
from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl_science import ScienceDomainPlugin
from spreadsheet_dl_science.templates.experiment_log import ExperimentLogTemplate
from spreadsheet_dl_science.formulas.statistics import TTestFormula
from spreadsheet_dl_science.importers.csv_data import CSVDataImporter


class TestSciencePlugin:
    """Test science domain plugin."""

    def test_plugin_metadata(self):
        """Test plugin metadata is correct."""
        plugin = ScienceDomainPlugin()
        metadata = plugin.metadata

        assert metadata.name == "science"
        assert metadata.version == "1.0.0"
        assert "science" in metadata.tags

    def test_plugin_initialize(self):
        """Test plugin initialization."""
        plugin = ScienceDomainPlugin()
        assert plugin.status == PluginStatus.UNINITIALIZED

        plugin.initialize()

        assert "experiment_log" in plugin.list_templates()
        assert "TTEST" in plugin.list_formulas()
        assert "csv" in plugin.list_importers()

    def test_plugin_registration(self):
        """Test global plugin registration."""
        # Should auto-register on import
        assert "science" in BaseDomainPlugin.list_plugins()

        plugin_class = BaseDomainPlugin.get_plugin_class("science")
        assert plugin_class == ScienceDomainPlugin


class TestExperimentLogTemplate:
    """Test experiment log template."""

    def test_template_metadata(self):
        """Test template metadata."""
        template = ExperimentLogTemplate()
        metadata = template.metadata

        assert metadata.name == "Experiment Log"
        assert metadata.category == "science"

    def test_template_generation(self):
        """Test template generates valid spreadsheet."""
        template = ExperimentLogTemplate(
            researcher_name="Dr. Smith",
            experiment_id="EXP-001",
        )

        builder = template.generate()

        assert isinstance(builder, SpreadsheetBuilder)
        assert template.get_config("researcher_name") == "Dr. Smith"

    def test_template_validation(self):
        """Test template validation."""
        template = ExperimentLogTemplate()
        assert template.validate()


class TestTTestFormula:
    """Test T-test formula."""

    def test_formula_metadata(self):
        """Test formula metadata."""
        formula = TTestFormula()
        metadata = formula.metadata

        assert metadata.name == "TTEST"
        assert metadata.category == "statistical"
        assert len(metadata.arguments) == 4

    def test_formula_build_required_args(self):
        """Test building formula with required args only."""
        formula = TTestFormula()
        result = formula.build("A1:A10", "B1:B10")

        assert result == "TTEST(A1:A10;B1:B10;2;1)"

    def test_formula_build_all_args(self):
        """Test building formula with all arguments."""
        formula = TTestFormula()
        result = formula.build("A1:A10", "B1:B10", 1, 2)

        assert result == "TTEST(A1:A10;B1:B10;1;2)"

    def test_formula_validation_invalid_tails(self):
        """Test validation fails with invalid tails."""
        formula = TTestFormula()

        with pytest.raises(ValueError, match="tails must be 1 or 2"):
            formula.validate_arguments(("A1:A10", "B1:B10", 3))


class TestCSVDataImporter:
    """Test CSV data importer."""

    def test_importer_metadata(self):
        """Test importer metadata."""
        importer = CSVDataImporter()
        metadata = importer.metadata

        assert metadata.name == "CSV Data Importer"
        assert "csv" in metadata.supported_formats

    def test_importer_validate_source(self, tmp_path: Path):
        """Test source validation."""
        importer = CSVDataImporter()

        # Create test file
        test_file = tmp_path / "test.csv"
        test_file.write_text("col1,col2\n1,2\n")

        assert importer.validate_source(test_file)
        assert not importer.validate_source(tmp_path / "nonexistent.csv")

    def test_importer_import_data(self, tmp_path: Path):
        """Test data import."""
        importer = CSVDataImporter()

        # Create test CSV
        test_file = tmp_path / "test.csv"
        test_file.write_text("experiment,temperature,result\nEXP1,25.5,positive\nEXP2,30.0,negative\n")

        result = importer.import_data(test_file)

        assert result.success
        assert result.records_imported == 2
        assert len(result.data) == 2
        assert result.data[0]["experiment"] == "EXP1"
        assert result.data[0]["temperature"] == 25.5  # Auto-converted

    def test_importer_invalid_source(self):
        """Test import with invalid source."""
        importer = CSVDataImporter()

        result = importer.import_data("/nonexistent/file.csv")

        assert not result.success
        assert len(result.errors) > 0
```

### Test Coverage Requirements

Aim for 95%+ coverage:

```bash
uv run pytest --cov=spreadsheet_dl_science --cov-report=html
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_templates.py

# Run specific test
uv run pytest tests/test_templates.py::TestExperimentLogTemplate::test_template_generation
```

## Distribution

### Package Configuration

Create `pyproject.toml`:

```toml
[project]
name = "spreadsheet-dl-science"
version = "1.0.0"
description = "Science domain plugin for SpreadsheetDL"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "spreadsheet-dl>=0.1.0",
]
keywords = ["spreadsheet", "science", "experiments", "data"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
]

[project.urls]
Homepage = "https://github.com/lair-click-bats/spreadsheet-dl-science"
Documentation = "https://spreadsheet-dl-science.readthedocs.io"
Repository = "https://github.com/lair-click-bats/spreadsheet-dl-science"
Issues = "https://github.com/lair-click-bats/spreadsheet-dl-science/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "SIM"]
```

### Publishing to PyPI

```bash
# Build package
uv build

# Upload to PyPI
uv publish
```

### Installation by Users

```bash
uv pip install spreadsheet-dl-science
```

## Best Practices

### Code Quality

1. **Type hints everywhere**: Use 100% type hint coverage
2. **Docstrings**: Document all public APIs with requirement IDs
3. **Error handling**: Provide clear, actionable error messages
4. **Validation**: Validate inputs early and fail fast
5. **Naming**: Use clear, descriptive names following Python conventions

### Performance

1. **Lazy imports**: Import heavy dependencies in `initialize()` not at module level
2. **Progress reporting**: Call `on_progress()` for long-running operations
3. **Memory efficiency**: Process large files in chunks
4. **Caching**: Cache expensive computations when appropriate

### Documentation

1. **README**: Include installation, quick start, and examples
2. **API docs**: Auto-generate with Sphinx or mkdocs
3. **Examples**: Provide complete, working examples
4. **Changelog**: Maintain CHANGELOG.md following Keep a Changelog
5. **Migration guides**: Document breaking changes

### Versioning

Follow Semantic Versioning (semver):

- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes

### Security

1. **Input validation**: Never trust user input
2. **Path traversal**: Validate file paths in importers
3. **Dependencies**: Keep dependencies minimal and up-to-date
4. **Secrets**: Never hardcode credentials
5. **Code injection**: Sanitize formula inputs

## Reference: Finance Plugin

The Finance plugin is the reference implementation demonstrating all plugin features.

### Plugin Structure

```python
class FinanceDomainPlugin(BaseDomainPlugin):
    """Finance domain plugin."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="finance",
            version="0.1.0",
            description="Financial analysis and reporting",
            author="SpreadsheetDL Team",
            license="MIT",
            tags=("finance", "budget", "accounting", "investment"),
        )

    def initialize(self) -> None:
        # Templates
        self.register_template("enterprise_budget", EnterpriseBudgetTemplate)
        self.register_template("cash_flow", CashFlowTrackerTemplate)
        self.register_template("invoice", InvoiceTemplate)

        # Formulas (if we add them)
        # self.register_formula("PMT", PMTFormula)

        # Importers
        self.register_importer("bank_csv", BankCSVImporter)
```

### Template Example: EnterpriseBudgetTemplate

The Finance plugin's `EnterpriseBudgetTemplate` demonstrates:

- Complex multi-sheet structure
- Category hierarchy with subcategories
- Formula references across sheets
- Professional formatting
- Configurable options (fiscal_year, departments, categories)
- Helper methods for sheet generation
- Theme integration

Key features to emulate:

```python
class EnterpriseBudgetTemplate(BaseTemplate):
    fiscal_year: int = 2024
    departments: list[str] = field(default_factory=lambda: ["General"])
    categories: list[BudgetCategory] = field(default_factory=list)

    def generate(self) -> SpreadsheetBuilder:
        builder = SpreadsheetBuilder(theme=self.theme)

        # Set workbook properties
        builder.workbook_properties(...)

        # Create multiple sheets
        self._create_summary_sheet(builder)
        for dept in self.departments:
            self._create_department_sheet(builder, dept)
        self._create_variance_sheet(builder)

        return builder
```

### Template Example: CashFlowTrackerTemplate

Demonstrates:

- Period-based tracking (weekly/monthly)
- Running balance calculations
- Sectioned data (Operating, Investing, Financing)
- Dynamic column generation
- Projection capabilities

### Importer Example: CSVImporter

The Finance plugin's CSV importer shows:

- Bank format detection
- Transaction categorization
- Type conversion
- Error handling and reporting
- Progress callbacks
- Configurable delimiters and encodings

### Learning from Finance Plugin

Study these files in `src/spreadsheet_dl/domains/finance/`:

- `plugin.py` - Plugin class (when created)
- `templates/professional.py` - Professional templates
- `templates/financial_statements.py` - Financial statement templates
- `csv_import.py` - CSV importer with categorization
- `categories.py` - Category management system

## Next Steps

1. **Plan your domain**: Identify templates, formulas, and importers needed
2. **Create plugin structure**: Set up package following recommended layout
3. **Implement base plugin**: Create plugin class with metadata
4. **Build templates**: Start with one simple template
5. **Add formulas**: Implement domain-specific calculations
6. **Create importers**: Build data import tools
7. **Write tests**: Achieve 95%+ coverage
8. **Document**: Write README and examples
9. **Publish**: Share with community

## Support

- **Documentation**: https://lair-click-bats.github.io/spreadsheet-dl/
- **Issues**: https://github.com/lair-click-bats/spreadsheet-dl/issues
- **Community**: https://discord.gg/spreadsheet-dl

---

PHASE0-003 - Domain plugin development guide
