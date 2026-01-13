"""Domain Plugin Base Classes for SpreadsheetDL v4.0.0.

    PHASE0-002: Create domain plugin base classes

Provides abstract base classes for domain plugin architecture enabling
9+ domain plugins (Finance, Data Science, Engineering, etc.) to extend
core functionality with domain-specific templates, formulas, and importers.

Architecture:
    - BaseDomainPlugin: Core plugin interface with registration
    - BaseTemplate: Domain-specific spreadsheet templates
    - BaseFormula: Domain-specific formula extensions
    - BaseImporter: Domain-specific data importers

Design Principles:
    - Abstract base classes using ABC
    - Clear separation of concerns
    - Extensibility for future domains
    - Type-safe interfaces
    - Comprehensive error handling

Example:
    See the individual domain plugin implementations in the domains/ directory
    for complete examples of how to create domain plugins.

    Basic structure::

        class FinanceDomainPlugin(BaseDomainPlugin):
            @property
            def metadata(self):
                return PluginMetadata(name="finance", version="1.0.0", ...)

            def initialize(self) -> None:
                self.register_template("budget", BudgetTemplate)

            def cleanup(self) -> None:
                pass
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from spreadsheet_dl.builder import FormulaBuilder, SpreadsheetBuilder


# ============================================================================
# Type Variables
# ============================================================================

T = TypeVar("T")
TemplateT = TypeVar("TemplateT", bound="BaseTemplate")
FormulaT = TypeVar("FormulaT", bound="BaseFormula")
ImporterT = TypeVar("ImporterT", bound="BaseImporter[Any]")


# ============================================================================
# Plugin Metadata
# ============================================================================


@dataclass(slots=True, frozen=True)
class PluginMetadata:
    """Metadata for a domain plugin.

        PHASE0-002: BaseDomainPlugin metadata requirements

    Attributes:
        name: Unique plugin identifier (lowercase, no spaces)
        version: Semantic version string (e.g., "1.0.0")
        description: Human-readable plugin description
        author: Plugin author/maintainer
        license: License identifier (SPDX format)
        homepage: Plugin homepage URL
        tags: Searchable tags for plugin discovery
        min_spreadsheet_dl_version: Minimum SpreadsheetDL version required
    """

    name: str
    version: str
    description: str
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    min_spreadsheet_dl_version: str = "4.0.0"

    def __post_init__(self) -> None:
        """Validate metadata after initialization."""
        if not self.name:
            msg = "Plugin name cannot be empty"
            raise ValueError(msg)
        if " " in self.name or not self.name.islower():
            msg = f"Plugin name must be lowercase without spaces: {self.name}"
            raise ValueError(msg)
        if not self.version:
            msg = "Plugin version cannot be empty"
            raise ValueError(msg)


@dataclass(slots=True, frozen=True)
class PluginDependency:
    """Plugin dependency specification.

    Attributes:
        plugin_name: Name of required plugin
        min_version: Minimum version (inclusive)
        max_version: Maximum version (exclusive)
        optional: Whether dependency is optional
    """

    plugin_name: str
    min_version: str = "0.0.0"
    max_version: str | None = None
    optional: bool = False


# ============================================================================
# Plugin Status
# ============================================================================


class PluginStatus(str, Enum):
    """Plugin lifecycle status."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"


# ============================================================================
# Base Domain Plugin
# ============================================================================


class BaseDomainPlugin(ABC):
    """Abstract base class for domain plugins.

        PHASE0-002: BaseDomainPlugin abstract class

    Provides core plugin interface with:
    - Plugin metadata and lifecycle management
    - Template, formula, and importer registration
    - Dependency declaration and validation
    - Plugin discovery and initialization hooks

    Subclasses must implement:
    - metadata property: Return PluginMetadata instance
    - initialize() method: Setup plugin resources
    - cleanup() method: Teardown and cleanup

    Optional overrides:
    - dependencies property: Declare plugin dependencies
    - validate() method: Validate plugin configuration

    Example:
        >>> class DataSciencePlugin(BaseDomainPlugin):
        ...     @property
        ...     def metadata(self) -> PluginMetadata:
        ...         return PluginMetadata(
        ...             name="data_science",
        ...             version="1.0.0",
        ...             description="Data science templates and tools",
        ...             author="SpreadsheetDL Team",
        ...         )
        ...
        ...     def initialize(self) -> None:
        ...         self.register_template("experiment_log", ExperimentLogTemplate)
        ...         self.register_formula("TTEST", TTestFormula)
        ...
        ...     def cleanup(self) -> None:
        ...         pass  # No cleanup needed
    """

    # Class-level registry for all plugins
    _registry: ClassVar[dict[str, type[BaseDomainPlugin]]] = {}

    def __init__(self) -> None:
        """Initialize plugin instance."""
        self._status: PluginStatus = PluginStatus.UNINITIALIZED
        self._templates: dict[str, type[BaseTemplate]] = {}
        self._formulas: dict[str, type[BaseFormula]] = {}
        self._importers: dict[str, type[BaseImporter[Any]]] = {}
        self._initialized_at: datetime | None = None
        self._error_message: str | None = None

    # ========================================================================
    # Abstract Properties (MUST implement)
    # ========================================================================

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata instance with name, version, description, etc.

        Example:
            >>> @property  # doctest: +SKIP
            >>> def metadata(self) -> PluginMetadata:
            ...     return PluginMetadata(
            ...         name="finance",
            ...         version="4.0.0",
            ...         description="Financial analysis and reporting",
            ...     )
        """
        ...

    # ========================================================================
    # Abstract Methods (MUST implement)
    # ========================================================================

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin resources.

        Called once when plugin is loaded. Use this to:
        - Register templates via register_template()
        - Register formulas via register_formula()
        - Register importers via register_importer()
        - Setup any plugin-specific resources

        Raises:
            Exception: On initialization failure

        Example:
            >>> def initialize(self) -> None:
            ...     self.register_template("budget", BudgetTemplate)
            ...     self.register_template("invoice", InvoiceTemplate)
            ...     self.register_formula("PMT", PMTFormula)
            ...     self.register_importer("csv", CSVImporter)
        """
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources.

        Called when plugin is unloaded or application exits.
        Use this to release resources, close connections, etc.

        Example:
            >>> def cleanup(self) -> None:
            ...     if self._database:
            ...         self._database.close()
        """
        ...

    # ========================================================================
    # Optional Overrides
    # ========================================================================

    @property
    def dependencies(self) -> Sequence[PluginDependency]:
        """Declare plugin dependencies.

        Returns:
            Sequence of PluginDependency instances

        Example:
            >>> @property  # doctest: +SKIP
            >>> def dependencies(self) -> Sequence[PluginDependency]:
            ...     return [
            ...         PluginDependency("finance", min_version="4.0.0"),
            ...         PluginDependency("charts", optional=True),
            ...     ]
        """
        return []

    def validate(self) -> bool:
        """Validate plugin configuration.

        Called after initialize() to verify plugin is properly configured.

        Returns:
            True if valid, False otherwise

        Example:
            >>> def validate(self) -> bool:
            ...     return len(self._templates) > 0
        """
        return True

    # ========================================================================
    # Template Registry
    # ========================================================================

    def register_template(
        self,
        name: str,
        template_class: type[BaseTemplate],
    ) -> None:
        """Register a template class.

        Args:
            name: Unique template identifier within this plugin
            template_class: Template class (must extend BaseTemplate)

        Raises:
            ValueError: If name already registered or invalid class

        Example:
            >>> self.register_template("budget", BudgetTemplate)  # doctest: +SKIP
        """
        if not name:
            msg = "Template name cannot be empty"
            raise ValueError(msg)
        if name in self._templates:
            msg = f"Template '{name}' already registered"
            raise ValueError(msg)
        if not issubclass(template_class, BaseTemplate):
            msg = f"Template class must extend BaseTemplate: {template_class}"
            raise ValueError(msg)

        self._templates[name] = template_class

    def get_template(self, name: str) -> type[BaseTemplate] | None:
        """Get registered template class by name.

        Args:
            name: Template identifier

        Returns:
            Template class or None if not found
        """
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        """List all registered template names.

        Returns:
            List of template identifiers
        """
        return list(self._templates.keys())

    # ========================================================================
    # Formula Registry
    # ========================================================================

    def register_formula(
        self,
        name: str,
        formula_class: type[BaseFormula],
    ) -> None:
        """Register a formula class.

        Args:
            name: Formula function name (uppercase, e.g., "PMT")
            formula_class: Formula class (must extend BaseFormula)

        Raises:
            ValueError: If name already registered or invalid class

        Example:
            >>> self.register_formula("PMT", PMTFormula)  # doctest: +SKIP
        """
        if not name:
            msg = "Formula name cannot be empty"
            raise ValueError(msg)
        if not name.isupper():
            msg = f"Formula name must be uppercase: {name}"
            raise ValueError(msg)
        if name in self._formulas:
            msg = f"Formula '{name}' already registered"
            raise ValueError(msg)
        if not issubclass(formula_class, BaseFormula):
            msg = f"Formula class must extend BaseFormula: {formula_class}"
            raise ValueError(msg)

        self._formulas[name] = formula_class

    def get_formula(self, name: str) -> type[BaseFormula] | None:
        """Get registered formula class by name.

        Args:
            name: Formula function name

        Returns:
            Formula class or None if not found
        """
        return self._formulas.get(name.upper())

    def list_formulas(self) -> list[str]:
        """List all registered formula names.

        Returns:
            List of formula function names
        """
        return list(self._formulas.keys())

    # ========================================================================
    # Importer Registry
    # ========================================================================

    def register_importer(
        self,
        name: str,
        importer_class: type[BaseImporter[Any]],
    ) -> None:
        """Register an importer class.

        Args:
            name: Unique importer identifier
            importer_class: Importer class (must extend BaseImporter)

        Raises:
            ValueError: If name already registered or invalid class

        Example:
            >>> self.register_importer("csv", CSVImporter)  # doctest: +SKIP
        """
        if not name:
            msg = "Importer name cannot be empty"
            raise ValueError(msg)
        if name in self._importers:
            msg = f"Importer '{name}' already registered"
            raise ValueError(msg)
        if not issubclass(importer_class, BaseImporter):
            msg = f"Importer class must extend BaseImporter: {importer_class}"
            raise ValueError(msg)

        self._importers[name] = importer_class

    def get_importer(self, name: str) -> type[BaseImporter[Any]] | None:
        """Get registered importer class by name.

        Args:
            name: Importer identifier

        Returns:
            Importer class or None if not found
        """
        return self._importers.get(name)

    def list_importers(self) -> list[str]:
        """List all registered importer names.

        Returns:
            List of importer identifiers
        """
        return list(self._importers.keys())

    # ========================================================================
    # Lifecycle Management
    # ========================================================================

    @property
    def status(self) -> PluginStatus:
        """Get current plugin status."""
        return self._status

    @property
    def is_ready(self) -> bool:
        """Check if plugin is initialized and ready."""
        return self._status == PluginStatus.READY

    @property
    def error_message(self) -> str | None:
        """Get error message if status is ERROR."""
        return self._error_message

    def _set_status(
        self,
        status: PluginStatus,
        error_message: str | None = None,
    ) -> None:
        """Set plugin status (internal use only)."""
        self._status = status
        self._error_message = error_message
        if status == PluginStatus.READY:
            self._initialized_at = datetime.now()

    # ========================================================================
    # Plugin Registry (Class Methods)
    # ========================================================================

    @classmethod
    def register_plugin(cls, plugin_class: type[BaseDomainPlugin]) -> None:
        """Register a plugin class globally.

        Args:
            plugin_class: Plugin class to register

        Raises:
            ValueError: If plugin name already registered

        Example:
            >>> BaseDomainPlugin.register_plugin(FinancePlugin)  # doctest: +SKIP
        """
        instance = plugin_class()
        name = instance.metadata.name

        if name in cls._registry:
            msg = f"Plugin '{name}' already registered"
            raise ValueError(msg)

        cls._registry[name] = plugin_class

    @classmethod
    def get_plugin_class(cls, name: str) -> type[BaseDomainPlugin] | None:
        """Get registered plugin class by name.

        Args:
            name: Plugin identifier

        Returns:
            Plugin class or None if not found
        """
        return cls._registry.get(name)

    @classmethod
    def list_plugins(cls) -> list[str]:
        """List all registered plugin names.

        Returns:
            List of plugin identifiers
        """
        return list(cls._registry.keys())


# ============================================================================
# Base Template
# ============================================================================


@dataclass(slots=True)
class TemplateMetadata:
    """Metadata for a template.

    Attributes:
        name: Template name
        description: Human-readable description
        category: Template category (e.g., "finance", "science")
        tags: Searchable tags
        version: Template version
        author: Template author
    """

    name: str
    description: str = ""
    category: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    version: str = "1.0.0"
    author: str = ""


class BaseTemplate(ABC):
    """Abstract base class for domain-specific templates.

        PHASE0-002: BaseTemplate class for domain templates

    Provides common spreadsheet template functionality:
    - Template metadata and configuration
    - Builder generation and customization
    - Style and theme integration
    - Validation hooks
    - Export format support

    Subclasses must implement:
    - metadata property: Return TemplateMetadata
    - generate() method: Create SpreadsheetBuilder instance

    Optional overrides:
    - validate() method: Validate template configuration
    - customize() method: Apply customizations to builder

    Example:
        >>> class BudgetTemplate(BaseTemplate):
        ...     @property
        ...     def metadata(self) -> TemplateMetadata:
        ...         return TemplateMetadata(
        ...             name="Monthly Budget",
        ...             description="Personal monthly budget tracker",
        ...             category="finance",
        ...         )
        ...
        ...     def generate(self) -> SpreadsheetBuilder:
        ...         from spreadsheet_dl.builder import SpreadsheetBuilder
        ...         builder = SpreadsheetBuilder(theme="corporate")
        ...         builder.sheet("Budget")
        ...         # ... add columns, rows, formulas
        ...         return builder
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize template with configuration.

        Args:
            **kwargs: Template-specific configuration options
        """
        self._config: dict[str, Any] = kwargs
        self._theme: str = kwargs.get("theme", "default")
        self._currency: str = kwargs.get("currency", "USD")

    # ========================================================================
    # Abstract Properties and Methods
    # ========================================================================

    @property
    @abstractmethod
    def metadata(self) -> TemplateMetadata:
        """Get template metadata.

        Returns:
            TemplateMetadata instance

        Example:
            >>> @property  # doctest: +SKIP
            >>> def metadata(self) -> TemplateMetadata:
            ...     return TemplateMetadata(
            ...         name="Invoice",
            ...         description="Professional invoice template",
            ...         category="finance",
            ...         tags=("invoice", "billing"),
            ...     )
        """
        ...

    @abstractmethod
    def generate(self) -> SpreadsheetBuilder:
        """Generate spreadsheet builder instance.

        Creates and configures a SpreadsheetBuilder with all template
        content including sheets, columns, rows, formulas, and styling.

        Returns:
            Configured SpreadsheetBuilder instance

        Example:
            >>> def generate(self) -> SpreadsheetBuilder:
            ...     from spreadsheet_dl.builder import SpreadsheetBuilder
            ...     builder = SpreadsheetBuilder(theme=self._theme)
            ...     builder.workbook_properties(title=self.metadata.name)
            ...     builder.sheet("Main")
            ...     # ... configure template
            ...     return builder
        """
        ...

    # ========================================================================
    # Optional Overrides
    # ========================================================================

    def validate(self) -> bool:
        """Validate template configuration.

        Returns:
            True if configuration is valid

        Example:
            >>> def validate(self) -> bool:
            ...     return self._config.get("year") is not None
        """
        return True

    def customize(self, builder: SpreadsheetBuilder) -> SpreadsheetBuilder:
        """Apply customizations to generated builder.

        Called after generate() to apply user customizations.

        Args:
            builder: SpreadsheetBuilder instance

        Returns:
            Customized builder (can be same instance)

        Example:
            >>> def customize(self, builder: SpreadsheetBuilder) -> SpreadsheetBuilder:
            ...     if self._config.get("add_logo"):
            ...         # Add company logo
            ...         pass
            ...     return builder
        """
        return builder

    # ========================================================================
    # Template Utilities
    # ========================================================================

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    @property
    def theme(self) -> str:
        """Get template theme name."""
        return self._theme

    @property
    def currency(self) -> str:
        """Get template currency code."""
        return self._currency


# ============================================================================
# Base Formula
# ============================================================================


@dataclass(slots=True)
class FormulaArgument:
    """Formula function argument specification.

    Attributes:
        name: Argument name
        type: Expected type (e.g., "number", "text", "range")
        required: Whether argument is required
        description: Argument description
        default: Default value if optional
    """

    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Any = None

    @property
    def optional(self) -> bool:
        """Return True if argument is optional (inverse of required).

        Returns:
            True if optional, False if required
        """
        return not self.required


@dataclass(slots=True)
class FormulaMetadata:
    """Metadata for a formula function.

    Attributes:
        name: Formula function name (uppercase)
        category: Formula category (e.g., "financial", "statistical")
        description: Human-readable description
        arguments: Argument specifications
        return_type: Return value type
        examples: Usage examples
    """

    name: str
    category: str
    description: str
    arguments: tuple[FormulaArgument, ...] = field(default_factory=tuple)
    return_type: str = "number"
    examples: tuple[str, ...] = field(default_factory=tuple)


class BaseFormula(ABC):
    """Abstract base class for domain-specific formulas.

        PHASE0-002: BaseFormula class for domain formula extensions

    Provides formula extension interface:
    - Formula metadata and type information
    - Argument validation and type checking
    - Integration with FormulaBuilder
    - Documentation generation support

    Subclasses must implement:
    - metadata property: Return FormulaMetadata
    - build() method: Generate ODF formula string

    Optional overrides:
    - validate_arguments() method: Custom argument validation

    Example:
        >>> class PMTFormula(BaseFormula):
        ...     @property
        ...     def metadata(self) -> FormulaMetadata:
        ...         return FormulaMetadata(
        ...             name="PMT",
        ...             category="financial",
        ...             description="Calculate loan payment",
        ...             arguments=(
        ...                 FormulaArgument("rate", "number", description="Interest rate"),
        ...                 FormulaArgument("nper", "number", description="Number of periods"),
        ...                 FormulaArgument("pv", "number", description="Present value"),
        ...             ),
        ...             examples=("=PMT(0.05/12, 360, 200000)",),
        ...         )
        ...
        ...     def build(self, *args: Any) -> str:
        ...         rate, nper, pv = args
        ...         return f"PMT({rate};{nper};{pv})"
    """

    # ========================================================================
    # Abstract Properties and Methods
    # ========================================================================

    @property
    @abstractmethod
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata instance

        Example:
            >>> @property  # doctest: +SKIP
            >>> def metadata(self) -> FormulaMetadata:
            ...     return FormulaMetadata(
            ...         name="TTEST",
            ...         category="statistical",
            ...         description="Perform t-test",
            ...         arguments=(
            ...             FormulaArgument("array1", "range"),
            ...             FormulaArgument("array2", "range"),
            ...             FormulaArgument("tails", "number", default=2),
            ...             FormulaArgument("type", "number", default=1),
            ...         ),
            ...     )
        """
        ...

    @abstractmethod
    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: Positional arguments (formula parameters)
            **kwargs: Keyword arguments (optional parameters)

        Returns:
            ODF formula string (without leading =)

        Raises:
            ValueError: If arguments are invalid

        Example:
            >>> def build(self, *args: Any) -> str:
            ...     self.validate_arguments(args)
            ...     array1, array2 = args[:2]
            ...     tails = args[2] if len(args) > 2 else 2
            ...     type_ = args[3] if len(args) > 3 else 1
            ...     return f"TTEST({array1};{array2};{tails};{type_})"
        """
        ...

    # ========================================================================
    # Validation
    # ========================================================================

    def validate_arguments(self, args: tuple[Any, ...]) -> None:
        """Validate formula arguments.

        Args:
            args: Arguments to validate

        Raises:
            ValueError: If arguments are invalid

        Example:
            >>> def validate_arguments(self, args: tuple[Any, ...]) -> None:
            ...     required = sum(1 for arg in self.metadata.arguments if arg.required)
            ...     if len(args) < required:
            ...         raise ValueError(f"Expected at least {required} arguments")
        """
        # Count required arguments
        required_count = sum(1 for arg in self.metadata.arguments if arg.required)
        total_count = len(self.metadata.arguments)

        if len(args) < required_count:
            msg = (
                f"{self.metadata.name} requires at least {required_count} arguments, "
                f"got {len(args)}"
            )
            raise ValueError(msg)

        if len(args) > total_count:
            msg = (
                f"{self.metadata.name} accepts at most {total_count} arguments, "
                f"got {len(args)}"
            )
            raise ValueError(msg)

    # ========================================================================
    # Integration with FormulaBuilder
    # ========================================================================

    def register_with_builder(self, builder: FormulaBuilder) -> None:  # noqa: B027
        """Register this formula with a FormulaBuilder instance.

        Optional method for subclasses to implement custom registration logic.

        Args:
            builder: FormulaBuilder instance

        Example:
            >>> formula = PMTFormula()  # doctest: +SKIP
            >>> formula.register_with_builder(formula_builder)  # Default implementation: no-op  # doctest: +SKIP
        """
        # Subclasses can override to implement custom registration logic
        pass


# ============================================================================
# Base Importer
# ============================================================================


@dataclass(slots=True)
class ImporterMetadata:
    """Metadata for a data importer.

    Attributes:
        name: Importer name
        description: Human-readable description
        supported_formats: File formats supported (e.g., "csv", "xlsx")
        category: Importer category
    """

    name: str
    description: str
    supported_formats: tuple[str, ...] = field(default_factory=tuple)
    category: str = ""


@dataclass(slots=True)
class ImportResult[T]:
    """Result of an import operation.

    Attributes:
        success: Whether import succeeded
        data: Imported data (type depends on importer)
        records_imported: Number of records imported
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional metadata about import
    """

    success: bool
    data: T
    records_imported: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseImporter[T](ABC):
    """Abstract base class for domain-specific data importers.

        PHASE0-002: BaseImporter class for domain data importers

    Provides data import interface:
    - Data source specification and validation
    - Import validation and type mapping
    - Error handling and reporting
    - Progress reporting support

    Subclasses must implement:
    - metadata property: Return ImporterMetadata
    - import_data() method: Perform data import
    - validate_source() method: Validate data source

    Optional overrides:
    - transform() method: Transform imported data
    - on_progress() method: Progress callback

    Exception Handling Pattern:
        Importer implementations use broad `except Exception` clauses to ensure
        robust error handling. Importers must never crash the application -
        instead they should return ImportResult(success=False) with error details.
        This allows graceful degradation and clear error reporting to users.

    Example:
        >>> class BankCSVImporter(BaseImporter[list[dict]]):
        ...     @property
        ...     def metadata(self) -> ImporterMetadata:
        ...         return ImporterMetadata(
        ...             name="Bank CSV Importer",
        ...             description="Import bank transactions from CSV",
        ...             supported_formats=("csv",),
        ...             category="finance",
        ...         )
        ...
        ...     def validate_source(self, source: Path) -> bool:
        ...         return source.exists() and source.suffix == ".csv"
        ...
        ...     def import_data(self, source: Path) -> ImportResult[list[dict]]:
        ...         try:
        ...             # Read CSV and parse transactions
        ...             transactions = []
        ...             # ... parsing logic
        ...             return ImportResult(
        ...                 success=True,
        ...                 data=transactions,
        ...                 records_imported=len(transactions),
        ...             )
        ...         except Exception as e:
        ...             return ImportResult(
        ...                 success=False,
        ...                 data=[],
        ...                 errors=[f"Import failed: {e}"],
        ...             )
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer with configuration.

        Args:
            **kwargs: Importer-specific configuration
        """
        self._config: dict[str, Any] = kwargs
        self._progress_callback: Callable[[int, int], None] | None = None

    # ========================================================================
    # Abstract Properties and Methods
    # ========================================================================

    @property
    @abstractmethod
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata instance

        Example:
            >>> @property  # doctest: +SKIP
            >>> def metadata(self) -> ImporterMetadata:
            ...     return ImporterMetadata(
            ...         name="CSV Transaction Importer",
            ...         description="Import transactions from CSV files",
            ...         supported_formats=("csv", "txt"),
            ...     )
        """
        ...

    @abstractmethod
    def validate_source(self, source: Path | str) -> bool:
        """Validate data source.

        Args:
            source: Path to data source file

        Returns:
            True if source is valid

        Example:
            >>> def validate_source(self, source: Path | str) -> bool:
            ...     path = Path(source) if isinstance(source, str) else source
            ...     return path.exists() and path.suffix in (".csv", ".txt")
        """
        ...

    @abstractmethod
    def import_data(self, source: Path | str) -> ImportResult[T]:
        """Import data from source.

        Args:
            source: Path to data source file

        Returns:
            ImportResult with imported data

        Raises:
            ValueError: If source is invalid
            IOError: If source cannot be read

        Example:
            >>> def import_data(self, source: Path | str) -> ImportResult[list[dict]]:
            ...     if not self.validate_source(source):
            ...         return ImportResult(
            ...             success=False,
            ...             data=[],
            ...             errors=["Invalid source file"],
            ...         )
            ...     # ... import logic
            ...     return ImportResult(
            ...         success=True,
            ...         data=records,
            ...         records_imported=len(records),
            ...     )
        """
        ...

    # ========================================================================
    # Optional Overrides
    # ========================================================================

    def transform(self, data: T) -> T:
        """Transform imported data.

        Called after import_data() to apply transformations.

        Args:
            data: Raw imported data

        Returns:
            Transformed data

        Example:
            >>> def transform(self, data: list[dict]) -> list[dict]:
            ...     # Normalize dates, amounts, etc.
            ...     return [self._normalize_record(r) for r in data]
        """
        return data

    def on_progress(self, current: int, total: int) -> None:
        """Progress callback.

        Args:
            current: Current progress
            total: Total items to process

        Example:
            >>> def on_progress(self, current: int, total: int) -> None:
            ...     print(f"Progress: {current}/{total}")
        """
        if self._progress_callback:
            self._progress_callback(current, total)

    # ========================================================================
    # Utilities
    # ========================================================================

    def set_progress_callback(
        self,
        callback: Callable[[int, int], None],
    ) -> None:
        """Set progress callback function.

        Args:
            callback: Function(current, total) to call on progress
        """
        self._progress_callback = callback

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # Plugin Infrastructure
    "BaseDomainPlugin",
    # Formula System
    "BaseFormula",
    # Importer System
    "BaseImporter",
    # Template System
    "BaseTemplate",
    "FormulaArgument",
    "FormulaMetadata",
    "ImportResult",
    "ImporterMetadata",
    "PluginDependency",
    "PluginMetadata",
    "PluginStatus",
    "TemplateMetadata",
]
