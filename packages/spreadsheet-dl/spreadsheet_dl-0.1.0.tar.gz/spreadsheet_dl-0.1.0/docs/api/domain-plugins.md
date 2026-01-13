# Domain Plugin API Reference

Complete API reference for domain plugin development.

## Table of Contents

- [Overview](#overview)
- [BaseDomainPlugin](#basedomainplugin)
- [PluginMetadata](#pluginmetadata)
- [PluginDependency](#plugindependency)
- [PluginStatus](#pluginstatus)
- [BaseTemplate](#basetemplate)
- [TemplateMetadata](#templatemetadata)
- [BaseFormula](#baseformula)
- [FormulaMetadata](#formulametadata)
- [FormulaArgument](#formulaargument)
- [BaseImporter](#baseimporter)
- [ImporterMetadata](#importermetadata)
- [ImportResult](#importresult)

## Overview

The domain plugin API provides four core abstract base classes for extending SpreadsheetDL:

```python
from spreadsheet_dl.domains.base import (
    BaseDomainPlugin,      # Core plugin interface
    BaseTemplate,          # Spreadsheet template generation
    BaseFormula,           # Custom formula functions
    BaseImporter,          # Data import tools
)
```

All base classes use Python's ABC (Abstract Base Class) module and require implementation of abstract methods.

## BaseDomainPlugin

Core plugin interface providing lifecycle management and component registration.

### Class Definition

```python
class BaseDomainPlugin(ABC):
    """Abstract base class for domain plugins."""
```

### Abstract Properties

#### metadata

```python
@property
@abstractmethod
def metadata(self) -> PluginMetadata:
    """
    Get plugin metadata.

    Returns:
        PluginMetadata instance with name, version, description, etc.
    """
```

**Required**: Yes

**Returns**: `PluginMetadata` instance

**Example**:

```python
@property
def metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="finance",
        version="0.1.0",
        description="Financial analysis and reporting",
        author="SpreadsheetDL Team",
        license="MIT",
        tags=("finance", "budget", "accounting"),
    )
```

### Abstract Methods

#### initialize()

```python
@abstractmethod
def initialize(self) -> None:
    """
    Initialize plugin resources.

    Called once when plugin is loaded. Use this to:
    - Register templates via register_template()
    - Register formulas via register_formula()
    - Register importers via register_importer()
    - Setup any plugin-specific resources

    Raises:
        Exception: On initialization failure
    """
```

**Required**: Yes

**Raises**: Any exception on initialization failure

**Example**:

```python
def initialize(self) -> None:
    from .templates import BudgetTemplate, InvoiceTemplate
    from .formulas import PMTFormula
    from .importers import CSVImporter

    self.register_template("budget", BudgetTemplate)
    self.register_template("invoice", InvoiceTemplate)
    self.register_formula("PMT", PMTFormula)
    self.register_importer("csv", CSVImporter)
```

#### cleanup()

```python
@abstractmethod
def cleanup(self) -> None:
    """
    Cleanup plugin resources.

    Called when plugin is unloaded or application exits.
    Use this to release resources, close connections, etc.
    """
```

**Required**: Yes

**Example**:

```python
def cleanup(self) -> None:
    if self._database:
        self._database.close()
    if self._cache:
        self._cache.clear()
```

### Optional Properties

#### dependencies

```python
@property
def dependencies(self) -> Sequence[PluginDependency]:
    """
    Declare plugin dependencies.

    Returns:
        Sequence of PluginDependency instances
    """
    return []
```

**Required**: No (defaults to empty list)

**Returns**: Sequence of `PluginDependency` instances

**Example**:

```python
@property
def dependencies(self) -> list[PluginDependency]:
    return [
        PluginDependency("finance", min_version="0.1.0"),
        PluginDependency("charts", optional=True),
    ]
```

### Optional Methods

#### validate()

```python
def validate(self) -> bool:
    """
    Validate plugin configuration.

    Called after initialize() to verify plugin is properly configured.

    Returns:
        True if valid, False otherwise
    """
    return True
```

**Required**: No (defaults to True)

**Returns**: `bool` - True if plugin is valid

**Example**:

```python
def validate(self) -> bool:
    # Ensure at least one template registered
    if len(self._templates) == 0:
        return False
    # Verify external dependencies available
    try:
        import required_library
        return True
    except ImportError:
        return False
```

### Template Registry Methods

#### register_template()

```python
def register_template(
    self,
    name: str,
    template_class: type[BaseTemplate],
) -> None:
    """
    Register a template class.

    Args:
        name: Unique template identifier within this plugin
        template_class: Template class (must extend BaseTemplate)

    Raises:
        ValueError: If name already registered or invalid class
    """
```

**Args**:

- `name` (str): Unique identifier (within plugin)
- `template_class` (type[BaseTemplate]): Template class

**Raises**:

- `ValueError`: If name empty, already registered, or class invalid

**Example**:

```python
self.register_template("budget", BudgetTemplate)
self.register_template("invoice", InvoiceTemplate)
```

#### get_template()

```python
def get_template(self, name: str) -> type[BaseTemplate] | None:
    """
    Get registered template class by name.

    Args:
        name: Template identifier

    Returns:
        Template class or None if not found
    """
```

**Args**:

- `name` (str): Template identifier

**Returns**: `type[BaseTemplate] | None`

**Example**:

```python
template_class = plugin.get_template("budget")
if template_class:
    template = template_class(fiscal_year=2024)
    builder = template.generate()
```

#### list_templates()

```python
def list_templates(self) -> list[str]:
    """
    List all registered template names.

    Returns:
        List of template identifiers
    """
```

**Returns**: `list[str]` - Template names

**Example**:

```python
templates = plugin.list_templates()
# ['budget', 'invoice', 'cash_flow']
```

### Formula Registry Methods

#### register_formula()

```python
def register_formula(
    self,
    name: str,
    formula_class: type[BaseFormula],
) -> None:
    """
    Register a formula class.

    Args:
        name: Formula function name (uppercase, e.g., "PMT")
        formula_class: Formula class (must extend BaseFormula)

    Raises:
        ValueError: If name already registered or invalid class
    """
```

**Args**:

- `name` (str): Formula name (MUST be uppercase)
- `formula_class` (type[BaseFormula]): Formula class

**Raises**:

- `ValueError`: If name not uppercase, already registered, or class invalid

**Example**:

```python
self.register_formula("PMT", PMTFormula)
self.register_formula("IRR", IRRFormula)
```

#### get_formula()

```python
def get_formula(self, name: str) -> type[BaseFormula] | None:
    """
    Get registered formula class by name.

    Args:
        name: Formula function name (case-insensitive lookup)

    Returns:
        Formula class or None if not found
    """
```

**Args**:

- `name` (str): Formula name (case-insensitive)

**Returns**: `type[BaseFormula] | None`

**Example**:

```python
formula_class = plugin.get_formula("PMT")
# Also works with lowercase
formula_class = plugin.get_formula("pmt")
```

#### list_formulas()

```python
def list_formulas(self) -> list[str]:
    """
    List all registered formula names.

    Returns:
        List of formula function names (uppercase)
    """
```

**Returns**: `list[str]` - Formula names

**Example**:

```python
formulas = plugin.list_formulas()
# ['PMT', 'IRR', 'NPV']
```

### Importer Registry Methods

#### register_importer()

```python
def register_importer(
    self,
    name: str,
    importer_class: type[BaseImporter[Any]],
) -> None:
    """
    Register an importer class.

    Args:
        name: Unique importer identifier
        importer_class: Importer class (must extend BaseImporter)

    Raises:
        ValueError: If name already registered or invalid class
    """
```

**Args**:

- `name` (str): Importer identifier
- `importer_class` (type[BaseImporter]): Importer class

**Raises**:

- `ValueError`: If name empty, already registered, or class invalid

**Example**:

```python
self.register_importer("csv", CSVImporter)
self.register_importer("plaid", PlaidImporter)
```

#### get_importer()

```python
def get_importer(self, name: str) -> type[BaseImporter[Any]] | None:
    """
    Get registered importer class by name.

    Args:
        name: Importer identifier

    Returns:
        Importer class or None if not found
    """
```

**Args**:

- `name` (str): Importer identifier

**Returns**: `type[BaseImporter] | None`

**Example**:

```python
importer_class = plugin.get_importer("csv")
if importer_class:
    importer = importer_class(delimiter=",")
    result = importer.import_data("transactions.csv")
```

#### list_importers()

```python
def list_importers(self) -> list[str]:
    """
    List all registered importer names.

    Returns:
        List of importer identifiers
    """
```

**Returns**: `list[str]` - Importer names

### Lifecycle Properties

#### status

```python
@property
def status(self) -> PluginStatus:
    """Get current plugin status."""
```

**Returns**: `PluginStatus` enum value

**Example**:

```python
if plugin.status == PluginStatus.READY:
    # Plugin is initialized and ready
    pass
```

#### is_ready

```python
@property
def is_ready(self) -> bool:
    """Check if plugin is initialized and ready."""
```

**Returns**: `bool` - True if status is READY

**Example**:

```python
if plugin.is_ready:
    template = plugin.get_template("budget")
```

#### error_message

```python
@property
def error_message(self) -> str | None:
    """Get error message if status is ERROR."""
```

**Returns**: `str | None` - Error message or None

**Example**:

```python
if plugin.status == PluginStatus.ERROR:
    print(f"Plugin error: {plugin.error_message}")
```

### Class Methods (Global Registry)

#### register_plugin()

```python
@classmethod
def register_plugin(cls, plugin_class: type[BaseDomainPlugin]) -> None:
    """
    Register a plugin class globally.

    Args:
        plugin_class: Plugin class to register

    Raises:
        ValueError: If plugin name already registered
    """
```

**Args**:

- `plugin_class` (type[BaseDomainPlugin]): Plugin class to register

**Raises**:

- `ValueError`: If plugin already registered

**Example**:

```python
BaseDomainPlugin.register_plugin(FinanceDomainPlugin)
```

#### get_plugin_class()

```python
@classmethod
def get_plugin_class(cls, name: str) -> type[BaseDomainPlugin] | None:
    """
    Get registered plugin class by name.

    Args:
        name: Plugin identifier

    Returns:
        Plugin class or None if not found
    """
```

**Args**:

- `name` (str): Plugin name

**Returns**: `type[BaseDomainPlugin] | None`

**Example**:

```python
plugin_class = BaseDomainPlugin.get_plugin_class("finance")
plugin = plugin_class()
plugin.initialize()
```

#### list_plugins()

```python
@classmethod
def list_plugins(cls) -> list[str]:
    """
    List all registered plugin names.

    Returns:
        List of plugin identifiers
    """
```

**Returns**: `list[str]` - Registered plugin names

**Example**:

```python
available = BaseDomainPlugin.list_plugins()
# ['finance', 'science', 'engineering']
```

## PluginMetadata

Plugin metadata for discovery and versioning.

### Class Definition

```python
@dataclass(slots=True, frozen=True)
class PluginMetadata:
    """Metadata for a domain plugin."""

    name: str
    version: str
    description: str
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    min_spreadsheet_dl_version: str = "0.1.0"
```

### Fields

- **name** (str): Unique plugin identifier (lowercase, no spaces) - **REQUIRED**
- **version** (str): Semantic version string (e.g., "1.0.0") - **REQUIRED**
- **description** (str): Human-readable description - **REQUIRED**
- **author** (str): Plugin author/maintainer - Default: ""
- **license** (str): License identifier (SPDX format) - Default: "MIT"
- **homepage** (str): Plugin homepage URL - Default: ""
- **tags** (tuple[str, ...]): Searchable tags - Default: ()
- **min_spreadsheet_dl_version** (str): Minimum SpreadsheetDL version - Default: "0.1.0"

### Validation

Automatically validates on construction:

- `name` must be non-empty, lowercase, no spaces
- `version` must be non-empty

**Raises**: `ValueError` if validation fails

### Example

```python
metadata = PluginMetadata(
    name="finance",
    version="0.1.0",
    description="Financial analysis and reporting tools",
    author="SpreadsheetDL Team",
    license="MIT",
    homepage="https://github.com/lair-click-bats/spreadsheet-dl",
    tags=("finance", "budget", "accounting", "investment"),
    min_spreadsheet_dl_version="0.1.0",
)
```

## PluginDependency

Dependency specification for plugin requirements.

### Class Definition

```python
@dataclass(slots=True, frozen=True)
class PluginDependency:
    """Plugin dependency specification."""

    plugin_name: str
    min_version: str = "0.0.0"
    max_version: str | None = None
    optional: bool = False
```

### Fields

- **plugin_name** (str): Name of required plugin
- **min_version** (str): Minimum version (inclusive) - Default: "0.0.0"
- **max_version** (str | None): Maximum version (exclusive) - Default: None
- **optional** (bool): Whether dependency is optional - Default: False

### Example

```python
dependencies = [
    # Required dependency with minimum version
    PluginDependency("finance", min_version="0.1.0"),

    # Optional dependency
    PluginDependency("charts", min_version="1.0.0", optional=True),

    # Version range
    PluginDependency("data", min_version="2.0.0", max_version="3.0.0"),
]
```

## PluginStatus

Plugin lifecycle status enumeration.

### Enum Definition

```python
class PluginStatus(str, Enum):
    """Plugin lifecycle status."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"
```

### Values

- **UNINITIALIZED**: Plugin created but not initialized
- **INITIALIZING**: Plugin initialization in progress
- **READY**: Plugin initialized and ready to use
- **ERROR**: Plugin initialization or operation failed
- **DISABLED**: Plugin explicitly disabled

### Example

```python
plugin = FinanceDomainPlugin()
assert plugin.status == PluginStatus.UNINITIALIZED

plugin.initialize()
assert plugin.status == PluginStatus.READY
```

## BaseTemplate

Abstract base class for domain-specific spreadsheet templates.

### Class Definition

```python
class BaseTemplate(ABC):
    """Abstract base class for domain-specific templates."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize template with configuration.

        Args:
            **kwargs: Template-specific configuration options
        """
```

### Constructor

**Args**:

- `**kwargs`: Template-specific configuration options

**Standard kwargs** (available on all templates):

- `theme` (str): Theme name - Default: "default"
- `currency` (str): Currency code - Default: "USD"

**Example**:

```python
template = BudgetTemplate(
    theme="corporate",
    currency="EUR",
    fiscal_year=2024,
    departments=["Sales", "Engineering"],
)
```

### Abstract Properties

#### metadata

```python
@property
@abstractmethod
def metadata(self) -> TemplateMetadata:
    """
    Get template metadata.

    Returns:
        TemplateMetadata instance
    """
```

**Required**: Yes

**Returns**: `TemplateMetadata`

**Example**:

```python
@property
def metadata(self) -> TemplateMetadata:
    return TemplateMetadata(
        name="Monthly Budget",
        description="Personal monthly budget tracker",
        category="finance",
        tags=("budget", "personal", "monthly"),
        version="1.0.0",
    )
```

### Abstract Methods

#### generate()

```python
@abstractmethod
def generate(self) -> SpreadsheetBuilder:
    """
    Generate spreadsheet builder instance.

    Creates and configures a SpreadsheetBuilder with all template
    content including sheets, columns, rows, formulas, and styling.

    Returns:
        Configured SpreadsheetBuilder instance
    """
```

**Required**: Yes

**Returns**: `SpreadsheetBuilder` instance

**Example**:

```python
def generate(self) -> SpreadsheetBuilder:
    from spreadsheet_dl.builder import SpreadsheetBuilder

    builder = SpreadsheetBuilder(theme=self._theme)

    builder.workbook_properties(
        title=self.metadata.name,
        author="Finance Team",
    )

    builder.sheet("Budget")
    builder.column("Category", width="150pt")
    builder.column("Amount", width="100pt", type="currency")

    builder.row(style="header_primary")
    builder.cell("Monthly Budget", colspan=2)

    # ... add more content

    return builder
```

### Optional Methods

#### validate()

```python
def validate(self) -> bool:
    """
    Validate template configuration.

    Returns:
        True if configuration is valid
    """
    return True
```

**Required**: No (defaults to True)

**Returns**: `bool`

**Example**:

```python
def validate(self) -> bool:
    # Require fiscal_year configuration
    return self.get_config("fiscal_year") is not None
```

#### customize()

```python
def customize(self, builder: SpreadsheetBuilder) -> SpreadsheetBuilder:
    """
    Apply customizations to generated builder.

    Called after generate() to apply user customizations.

    Args:
        builder: SpreadsheetBuilder instance

    Returns:
        Customized builder (can be same instance)
    """
    return builder
```

**Required**: No (defaults to no-op)

**Args**:

- `builder` (SpreadsheetBuilder): Builder to customize

**Returns**: `SpreadsheetBuilder`

**Example**:

```python
def customize(self, builder: SpreadsheetBuilder) -> SpreadsheetBuilder:
    if self.get_config("add_logo"):
        # Add company logo to first sheet
        pass

    if self.get_config("hide_formulas"):
        # Hide formula cells
        pass

    return builder
```

### Utility Methods

#### get_config()

```python
def get_config(self, key: str, default: Any = None) -> Any:
    """
    Get configuration value.

    Args:
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value
    """
```

**Args**:

- `key` (str): Configuration key
- `default` (Any): Default value - Default: None

**Returns**: Configuration value or default

**Example**:

```python
fiscal_year = self.get_config("fiscal_year", 2024)
departments = self.get_config("departments", ["General"])
```

### Properties

#### theme

```python
@property
def theme(self) -> str:
    """Get template theme name."""
```

**Returns**: `str` - Theme name

#### currency

```python
@property
def currency(self) -> str:
    """Get template currency code."""
```

**Returns**: `str` - Currency code

## TemplateMetadata

Template metadata for discovery and categorization.

### Class Definition

```python
@dataclass(slots=True)
class TemplateMetadata:
    """Metadata for a template."""

    name: str
    description: str = ""
    category: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    version: str = "1.0.0"
    author: str = ""
```

### Fields

- **name** (str): Template name - **REQUIRED**
- **description** (str): Human-readable description - Default: ""
- **category** (str): Template category (e.g., "finance") - Default: ""
- **tags** (tuple[str, ...]): Searchable tags - Default: ()
- **version** (str): Template version - Default: "1.0.0"
- **author** (str): Template author - Default: ""

### Example

```python
metadata = TemplateMetadata(
    name="Enterprise Budget",
    description="Multi-department annual budget with variance analysis",
    category="finance",
    tags=("budget", "enterprise", "annual", "variance"),
    version="2.0.0",
    author="Finance Team",
)
```

## BaseFormula

Abstract base class for domain-specific formula functions.

### Class Definition

```python
class BaseFormula(ABC):
    """Abstract base class for domain-specific formulas."""
```

### Abstract Properties

#### metadata

```python
@property
@abstractmethod
def metadata(self) -> FormulaMetadata:
    """
    Get formula metadata.

    Returns:
        FormulaMetadata instance
    """
```

**Required**: Yes

**Returns**: `FormulaMetadata`

**Example**:

```python
@property
def metadata(self) -> FormulaMetadata:
    return FormulaMetadata(
        name="PMT",
        category="financial",
        description="Calculate loan payment amount",
        arguments=(
            FormulaArgument("rate", "number", description="Interest rate per period"),
            FormulaArgument("nper", "number", description="Number of periods"),
            FormulaArgument("pv", "number", description="Present value (loan amount)"),
            FormulaArgument("fv", "number", required=False, default=0, description="Future value"),
        ),
        return_type="number",
        examples=(
            "=PMT(0.05/12, 360, 200000)",
            "=PMT(A1/12, A2, A3)",
        ),
    )
```

### Abstract Methods

#### build()

```python
@abstractmethod
def build(self, *args: Any, **kwargs: Any) -> str:
    """
    Build ODF formula string.

    Args:
        *args: Positional arguments (formula parameters)
        **kwargs: Keyword arguments (optional parameters)

    Returns:
        ODF formula string (without leading =)

    Raises:
        ValueError: If arguments are invalid
    """
```

**Required**: Yes

**Args**:

- `*args`: Formula arguments
- `**kwargs`: Optional arguments

**Returns**: `str` - ODF formula string (WITHOUT leading "=")

**Raises**: `ValueError` for invalid arguments

**Example**:

```python
def build(self, *args: Any, **kwargs: Any) -> str:
    self.validate_arguments(args)

    rate = args[0]
    nper = args[1]
    pv = args[2]
    fv = args[3] if len(args) > 3 else 0

    # ODF uses semicolons, not commas
    return f"PMT({rate};{nper};{pv};{fv})"
```

### Validation Methods

#### validate_arguments()

```python
def validate_arguments(self, args: tuple[Any, ...]) -> None:
    """
    Validate formula arguments.

    Args:
        args: Arguments to validate

    Raises:
        ValueError: If arguments are invalid
    """
```

**Args**:

- `args` (tuple[Any, ...]): Arguments to validate

**Raises**: `ValueError` for invalid arguments

**Default behavior**: Validates argument count against metadata

**Example** (override for custom validation):

```python
def validate_arguments(self, args: tuple[Any, ...]) -> None:
    # Call parent first
    super().validate_arguments(args)

    # Custom validation
    if len(args) >= 1:
        rate = args[0]
        if isinstance(rate, (int, float)) and rate < 0:
            raise ValueError("Interest rate cannot be negative")
```

## FormulaMetadata

Formula metadata for documentation and discovery.

### Class Definition

```python
@dataclass(slots=True)
class FormulaMetadata:
    """Metadata for a formula function."""

    name: str
    category: str
    description: str
    arguments: tuple[FormulaArgument, ...] = field(default_factory=tuple)
    return_type: str = "number"
    examples: tuple[str, ...] = field(default_factory=tuple)
```

### Fields

- **name** (str): Formula function name (uppercase) - **REQUIRED**
- **category** (str): Formula category - **REQUIRED**
- **description** (str): Human-readable description - **REQUIRED**
- **arguments** (tuple[FormulaArgument, ...]): Argument specifications - Default: ()
- **return_type** (str): Return value type - Default: "number"
- **examples** (tuple[str, ...]): Usage examples - Default: ()

### Example

```python
metadata = FormulaMetadata(
    name="TTEST",
    category="statistical",
    description="Perform Student's t-test on two samples",
    arguments=(
        FormulaArgument("array1", "range", description="First sample"),
        FormulaArgument("array2", "range", description="Second sample"),
        FormulaArgument("tails", "number", required=False, default=2),
        FormulaArgument("type", "number", required=False, default=1),
    ),
    return_type="number",
    examples=(
        "=TTEST(A1:A10, B1:B10)",
        "=TTEST(Sample1, Sample2, 1, 2)",
    ),
)
```

## FormulaArgument

Formula function argument specification.

### Class Definition

```python
@dataclass(slots=True)
class FormulaArgument:
    """Formula function argument specification."""

    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Any = None
```

### Fields

- **name** (str): Argument name - **REQUIRED**
- **type** (str): Expected type - **REQUIRED**
- **required** (bool): Whether argument is required - Default: True
- **description** (str): Argument description - Default: ""
- **default** (Any): Default value if optional - Default: None

### Common Types

- `"number"`: Numeric value
- `"text"`: Text/string value
- `"range"`: Cell range reference
- `"boolean"`: True/false value
- `"date"`: Date value
- `"any"`: Any type

### Example

```python
arguments = (
    FormulaArgument(
        name="rate",
        type="number",
        required=True,
        description="Annual interest rate (e.g., 0.05 for 5%)",
    ),
    FormulaArgument(
        name="nper",
        type="number",
        required=True,
        description="Total number of payment periods",
    ),
    FormulaArgument(
        name="pv",
        type="number",
        required=True,
        description="Present value (loan principal)",
    ),
    FormulaArgument(
        name="fv",
        type="number",
        required=False,
        default=0,
        description="Future value (usually 0 for loans)",
    ),
)
```

## BaseImporter

Abstract base class for domain-specific data importers.

### Class Definition

```python
class BaseImporter(ABC, Generic[T]):
    """
    Abstract base class for domain-specific data importers.

    Type parameter T specifies the imported data type.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize importer with configuration.

        Args:
            **kwargs: Importer-specific configuration
        """
```

### Constructor

**Args**:

- `**kwargs`: Importer-specific configuration

**Example**:

```python
importer = CSVImporter(
    delimiter=",",
    encoding="utf-8",
    skip_rows=0,
    auto_detect_types=True,
)
```

### Abstract Properties

#### metadata

```python
@property
@abstractmethod
def metadata(self) -> ImporterMetadata:
    """
    Get importer metadata.

    Returns:
        ImporterMetadata instance
    """
```

**Required**: Yes

**Returns**: `ImporterMetadata`

**Example**:

```python
@property
def metadata(self) -> ImporterMetadata:
    return ImporterMetadata(
        name="Bank CSV Importer",
        description="Import bank transactions from CSV files",
        supported_formats=("csv", "txt"),
        category="finance",
    )
```

### Abstract Methods

#### validate_source()

```python
@abstractmethod
def validate_source(self, source: Path | str) -> bool:
    """
    Validate data source.

    Args:
        source: Path to data source file

    Returns:
        True if source is valid
    """
```

**Required**: Yes

**Args**:

- `source` (Path | str): Path to data source

**Returns**: `bool` - True if valid

**Example**:

```python
def validate_source(self, source: Path | str) -> bool:
    path = Path(source) if isinstance(source, str) else source

    # Check exists
    if not path.exists():
        return False

    # Check extension
    if path.suffix.lower() not in (".csv", ".txt"):
        return False

    # Check readable
    try:
        with path.open() as f:
            f.read(1)
        return True
    except (OSError, PermissionError):
        return False
```

#### import_data()

```python
@abstractmethod
def import_data(self, source: Path | str) -> ImportResult[T]:
    """
    Import data from source.

    Args:
        source: Path to data source file

    Returns:
        ImportResult with imported data

    Raises:
        ValueError: If source is invalid
        IOError: If source cannot be read
    """
```

**Required**: Yes

**Args**:

- `source` (Path | str): Path to data source

**Returns**: `ImportResult[T]` with imported data

**Raises**:

- `ValueError`: Invalid source
- `IOError`: Cannot read source

**Example**:

```python
def import_data(self, source: Path | str) -> ImportResult[list[dict]]:
    if not self.validate_source(source):
        return ImportResult(
            success=False,
            data=[],
            errors=["Invalid source file"],
        )

    path = Path(source) if isinstance(source, str) else source
    data = []
    errors = []
    warnings = []

    try:
        with path.open() as csvfile:
            reader = csv.DictReader(csvfile)
            for row_num, row in enumerate(reader, start=1):
                self.on_progress(row_num, row_num)
                data.append(self._transform_row(row))
    except Exception as e:
        return ImportResult(
            success=False,
            data=[],
            errors=[str(e)],
        )

    return ImportResult(
        success=True,
        data=data,
        records_imported=len(data),
        errors=errors,
        warnings=warnings,
    )
```

### Optional Methods

#### transform()

```python
def transform(self, data: T) -> T:
    """
    Transform imported data.

    Called after import_data() to apply transformations.

    Args:
        data: Raw imported data

    Returns:
        Transformed data
    """
    return data
```

**Required**: No (defaults to no-op)

**Args**:

- `data` (T): Raw imported data

**Returns**: `T` - Transformed data

**Example**:

```python
def transform(self, data: list[dict]) -> list[dict]:
    # Normalize dates
    for record in data:
        if "date" in record:
            record["date"] = self._parse_date(record["date"])

    # Convert amounts to numbers
    for record in data:
        if "amount" in record:
            record["amount"] = float(record["amount"].replace("$", ""))

    return data
```

#### on_progress()

```python
def on_progress(self, current: int, total: int) -> None:
    """
    Progress callback.

    Args:
        current: Current progress
        total: Total items to process
    """
```

**Required**: No (defaults to callback if set)

**Args**:

- `current` (int): Current item
- `total` (int): Total items

**Example**:

```python
def import_data(self, source: Path | str) -> ImportResult[list[dict]]:
    # ... setup ...

    for row_num, row in enumerate(reader, start=1):
        # Report progress every 100 rows
        if row_num % 100 == 0:
            self.on_progress(row_num, total_rows)

        # ... process row ...

    # Final progress
    self.on_progress(total_rows, total_rows)
```

### Utility Methods

#### set_progress_callback()

```python
def set_progress_callback(
    self,
    callback: Callable[[int, int], None],
) -> None:
    """
    Set progress callback function.

    Args:
        callback: Function(current, total) to call on progress
    """
```

**Args**:

- `callback` (Callable[[int, int], None]): Progress callback

**Example**:

```python
def progress_handler(current: int, total: int) -> None:
    percent = (current / total) * 100
    print(f"Import progress: {percent:.1f}%")

importer.set_progress_callback(progress_handler)
result = importer.import_data("transactions.csv")
```

#### get_config()

```python
def get_config(self, key: str, default: Any = None) -> Any:
    """
    Get configuration value.

    Args:
        key: Configuration key
        default: Default value if not found

    Returns:
        Configuration value
    """
```

**Args**:

- `key` (str): Configuration key
- `default` (Any): Default value - Default: None

**Returns**: Configuration value or default

**Example**:

```python
delimiter = self.get_config("delimiter", ",")
encoding = self.get_config("encoding", "utf-8")
skip_rows = self.get_config("skip_rows", 0)
```

## ImporterMetadata

Importer metadata for discovery and capabilities.

### Class Definition

```python
@dataclass(slots=True)
class ImporterMetadata:
    """Metadata for a data importer."""

    name: str
    description: str
    supported_formats: tuple[str, ...] = field(default_factory=tuple)
    category: str = ""
```

### Fields

- **name** (str): Importer name - **REQUIRED**
- **description** (str): Human-readable description - **REQUIRED**
- **supported_formats** (tuple[str, ...]): File formats (e.g., "csv") - Default: ()
- **category** (str): Importer category - Default: ""

### Example

```python
metadata = ImporterMetadata(
    name="Plaid Transaction Importer",
    description="Import bank transactions via Plaid API",
    supported_formats=("json", "api"),
    category="finance",
)
```

## ImportResult

Result of an import operation.

### Class Definition

```python
@dataclass(slots=True)
class ImportResult(Generic[T]):
    """Result of an import operation."""

    success: bool
    data: T
    records_imported: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
```

### Fields

- **success** (bool): Whether import succeeded - **REQUIRED**
- **data** (T): Imported data (type depends on importer) - **REQUIRED**
- **records_imported** (int): Number of records imported - Default: 0
- **errors** (list[str]): Error messages - Default: []
- **warnings** (list[str]): Warning messages - Default: []
- **metadata** (dict[str, Any]): Additional metadata - Default: {}

### Example

```python
result = ImportResult(
    success=True,
    data=transactions,
    records_imported=142,
    errors=[],
    warnings=["3 records had missing categories"],
    metadata={
        "source_file": "transactions.csv",
        "import_date": "2024-01-03",
        "delimiter": ",",
        "encoding": "utf-8",
    },
)

if result.success:
    print(f"Imported {result.records_imported} records")
    for warning in result.warnings:
        print(f"Warning: {warning}")
else:
    print("Import failed:")
    for error in result.errors:
        print(f"  - {error}")
```

---

**See Also**:

- [Plugin Development Guide](../guides/plugin-development.md)
- [Architecture Overview](../ARCHITECTURE.md)
