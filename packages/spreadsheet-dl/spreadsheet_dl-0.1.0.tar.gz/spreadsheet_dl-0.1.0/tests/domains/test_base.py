"""
Tests for domain plugin base classes.

    PHASE0-002: Tests for BaseDomainPlugin, BaseTemplate, BaseFormula, BaseImporter
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from spreadsheet_dl.builder import SpreadsheetBuilder
from spreadsheet_dl.domains.base import (
    BaseDomainPlugin,
    BaseFormula,
    BaseImporter,
    BaseTemplate,
    FormulaArgument,
    FormulaMetadata,
    ImporterMetadata,
    ImportResult,
    PluginDependency,
    PluginMetadata,
    PluginStatus,
    TemplateMetadata,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain]

# ============================================================================
# Test Plugin Implementation
# ============================================================================


class SamplePlugin(BaseDomainPlugin):
    """Sample plugin implementation for tests."""

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin for unit tests",
            author="Test Author",
        )

    def initialize(self) -> None:
        """Initialize test plugin."""
        self.register_template("test_template", SampleTemplate)
        self.register_formula("TESTFUNC", SampleFormula)
        self.register_importer("test_importer", SampleImporter)

    def cleanup(self) -> None:
        """Cleanup test plugin."""
        pass


class SamplePluginWithDeps(BaseDomainPlugin):
    """Sample plugin with dependencies for tests."""

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="test_plugin_deps",
            version="1.0.0",
            description="Test plugin with dependencies",
        )

    @property
    def dependencies(self) -> list[PluginDependency]:
        """Declare dependencies."""
        return [
            PluginDependency("test_plugin", min_version="1.0.0"),
            PluginDependency("optional_plugin", optional=True),
        ]

    def initialize(self) -> None:
        """Initialize plugin."""
        pass

    def cleanup(self) -> None:
        """Cleanup plugin."""
        pass


# ============================================================================
# Test Template Implementation
# ============================================================================


class SampleTemplate(BaseTemplate):
    """Test template implementation."""

    @property
    def metadata(self) -> TemplateMetadata:
        """Get template metadata."""
        return TemplateMetadata(
            name="Test Template",
            description="A test template",
            category="test",
            tags=("test", "example"),
        )

    def generate(self) -> SpreadsheetBuilder:
        """Generate spreadsheet."""
        builder = SpreadsheetBuilder(theme=self.theme)
        builder.sheet("Test")
        builder.column("Name", width="100pt")
        builder.column("Value", width="80pt", type="number")
        return builder


# ============================================================================
# Test Formula Implementation
# ============================================================================


class SampleFormula(BaseFormula):
    """Test formula implementation."""

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="TESTFUNC",
            category="test",
            description="Test formula function",
            arguments=(
                FormulaArgument("arg1", "number", required=True),
                FormulaArgument("arg2", "number", required=True),
                FormulaArgument("arg3", "number", required=False, default=0),
            ),
            examples=("=TESTFUNC(1, 2)", "=TESTFUNC(1, 2, 3)"),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build formula string."""
        self.validate_arguments(args)
        if len(args) == 2:
            return f"TESTFUNC({args[0]};{args[1]})"
        return f"TESTFUNC({args[0]};{args[1]};{args[2]})"


# ============================================================================
# Test Importer Implementation
# ============================================================================


class SampleImporter(BaseImporter[list[dict[str, Any]]]):
    """Test importer implementation."""

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata."""
        return ImporterMetadata(
            name="Test Importer",
            description="Test data importer",
            supported_formats=("csv", "txt"),
            category="test",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate source file."""
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.suffix in (".csv", ".txt")

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import data from source."""
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid source file"],
            )

        # Simulate import
        data = [
            {"id": 1, "name": "Record 1"},
            {"id": 2, "name": "Record 2"},
        ]

        return ImportResult(
            success=True,
            data=data,
            records_imported=len(data),
        )


# ============================================================================
# Plugin Metadata Tests
# ============================================================================


def test_plugin_metadata_creation() -> None:
    """Test creating plugin metadata."""
    metadata = PluginMetadata(
        name="test",
        version="1.0.0",
        description="Test plugin",
        author="Test Author",
    )
    assert metadata.name == "test"
    assert metadata.version == "1.0.0"
    assert metadata.description == "Test plugin"
    assert metadata.author == "Test Author"


def test_plugin_metadata_validation_empty_name() -> None:
    """Test metadata validation fails with empty name."""
    with pytest.raises(ValueError, match="name cannot be empty"):
        PluginMetadata(name="", version="1.0.0", description="Test")


def test_plugin_metadata_validation_invalid_name() -> None:
    """Test metadata validation fails with invalid name."""
    with pytest.raises(ValueError, match="must be lowercase"):
        PluginMetadata(name="Test Plugin", version="1.0.0", description="Test")


def test_plugin_metadata_validation_empty_version() -> None:
    """Test metadata validation fails with empty version."""
    with pytest.raises(ValueError, match="version cannot be empty"):
        PluginMetadata(name="test", version="", description="Test")


# ============================================================================
# BaseDomainPlugin Tests
# ============================================================================


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = SamplePlugin()
    assert plugin.status == PluginStatus.UNINITIALIZED
    assert not plugin.is_ready


def test_plugin_initialize() -> None:
    """Test plugin initialize method."""
    plugin = SamplePlugin()
    plugin.initialize()

    # Check registrations
    assert "test_template" in plugin.list_templates()
    assert "TESTFUNC" in plugin.list_formulas()
    assert "test_importer" in plugin.list_importers()


def test_plugin_template_registration() -> None:
    """Test template registration."""
    plugin = SamplePlugin()
    plugin.register_template("custom", SampleTemplate)

    assert "custom" in plugin.list_templates()
    assert plugin.get_template("custom") == SampleTemplate
    assert plugin.get_template("nonexistent") is None


def test_plugin_template_registration_duplicate() -> None:
    """Test duplicate template registration fails."""
    plugin = SamplePlugin()
    plugin.register_template("test", SampleTemplate)

    with pytest.raises(ValueError, match="already registered"):
        plugin.register_template("test", SampleTemplate)


def test_plugin_formula_registration() -> None:
    """Test formula registration."""
    plugin = SamplePlugin()
    plugin.register_formula("CUSTOM", SampleFormula)

    assert "CUSTOM" in plugin.list_formulas()
    assert plugin.get_formula("CUSTOM") == SampleFormula
    assert plugin.get_formula("custom") == SampleFormula  # Case insensitive get
    assert plugin.get_formula("NONEXISTENT") is None


def test_plugin_formula_registration_uppercase_required() -> None:
    """Test formula names must be uppercase."""
    plugin = SamplePlugin()

    with pytest.raises(ValueError, match="must be uppercase"):
        plugin.register_formula("lowercase", SampleFormula)


def test_plugin_importer_registration() -> None:
    """Test importer registration."""
    plugin = SamplePlugin()
    plugin.register_importer("custom", SampleImporter)

    assert "custom" in plugin.list_importers()
    assert plugin.get_importer("custom") == SampleImporter
    assert plugin.get_importer("nonexistent") is None


def test_plugin_dependencies() -> None:
    """Test plugin dependencies."""
    plugin = SamplePluginWithDeps()
    deps = plugin.dependencies

    assert len(deps) == 2
    assert deps[0].plugin_name == "test_plugin"
    assert deps[0].min_version == "1.0.0"
    assert not deps[0].optional
    assert deps[1].optional


def test_plugin_global_registration() -> None:
    """Test global plugin registration."""
    # Clear registry first
    BaseDomainPlugin._registry.clear()

    BaseDomainPlugin.register_plugin(SamplePlugin)

    assert "test_plugin" in BaseDomainPlugin.list_plugins()
    assert BaseDomainPlugin.get_plugin_class("test_plugin") == SamplePlugin


def test_plugin_global_registration_duplicate() -> None:
    """Test duplicate global registration fails."""
    # Clear registry first
    BaseDomainPlugin._registry.clear()

    BaseDomainPlugin.register_plugin(SamplePlugin)

    with pytest.raises(ValueError, match="already registered"):
        BaseDomainPlugin.register_plugin(SamplePlugin)


# ============================================================================
# BaseTemplate Tests
# ============================================================================


def test_template_metadata() -> None:
    """Test template metadata."""
    template = SampleTemplate()
    metadata = template.metadata

    assert metadata.name == "Test Template"
    assert metadata.description == "A test template"
    assert metadata.category == "test"
    assert "test" in metadata.tags


def test_template_generate() -> None:
    """Test template generation."""
    template = SampleTemplate(theme="corporate")
    builder = template.generate()

    assert isinstance(builder, SpreadsheetBuilder)
    assert template.theme == "corporate"


def test_template_config() -> None:
    """Test template configuration."""
    template = SampleTemplate(
        theme="minimal",
        currency="EUR",
        custom_option="value",
    )

    assert template.theme == "minimal"
    assert template.currency == "EUR"
    assert template.get_config("custom_option") == "value"
    assert template.get_config("nonexistent", "default") == "default"


def test_template_validation() -> None:
    """Test template validation."""
    template = SampleTemplate()
    assert template.validate()


def test_template_customization() -> None:
    """Test template customization."""
    template = SampleTemplate()
    builder = template.generate()
    customized = template.customize(builder)

    assert customized is builder


# ============================================================================
# BaseFormula Tests
# ============================================================================


def test_formula_metadata() -> None:
    """Test formula metadata."""
    formula = SampleFormula()
    metadata = formula.metadata

    assert metadata.name == "TESTFUNC"
    assert metadata.category == "test"
    assert len(metadata.arguments) == 3
    assert metadata.arguments[0].name == "arg1"
    assert metadata.arguments[0].required
    assert metadata.arguments[2].required is False


def test_formula_build() -> None:
    """Test formula building."""
    formula = SampleFormula()

    # With required args only
    result = formula.build(1, 2)
    assert result == "TESTFUNC(1;2)"

    # With optional arg
    result = formula.build(1, 2, 3)
    assert result == "TESTFUNC(1;2;3)"


def test_formula_validation_too_few_args() -> None:
    """Test formula validation with too few arguments."""
    formula = SampleFormula()

    with pytest.raises(ValueError, match="requires at least 2 arguments"):
        formula.validate_arguments((1,))


def test_formula_validation_too_many_args() -> None:
    """Test formula validation with too many arguments."""
    formula = SampleFormula()

    with pytest.raises(ValueError, match="accepts at most 3 arguments"):
        formula.validate_arguments((1, 2, 3, 4))


def test_formula_argument_metadata() -> None:
    """Test formula argument metadata."""
    arg = FormulaArgument(
        name="test_arg",
        type="number",
        required=True,
        description="Test argument",
        default=10,
    )

    assert arg.name == "test_arg"
    assert arg.type == "number"
    assert arg.required
    assert arg.description == "Test argument"
    assert arg.default == 10


# ============================================================================
# BaseImporter Tests
# ============================================================================


def test_importer_metadata() -> None:
    """Test importer metadata."""
    importer = SampleImporter()
    metadata = importer.metadata

    assert metadata.name == "Test Importer"
    assert metadata.description == "Test data importer"
    assert "csv" in metadata.supported_formats
    assert metadata.category == "test"


def test_importer_validate_source(tmp_path: Path) -> None:
    """Test importer source validation."""
    importer = SampleImporter()

    # Create test file
    test_file = tmp_path / "test.csv"
    test_file.write_text("id,name\n1,Test\n")

    assert importer.validate_source(test_file)
    assert not importer.validate_source(tmp_path / "nonexistent.csv")

    # Wrong extension
    wrong_file = tmp_path / "test.xlsx"
    wrong_file.write_text("test")
    assert not importer.validate_source(wrong_file)


def test_importer_import_data(tmp_path: Path) -> None:
    """Test data import."""
    importer = SampleImporter()

    # Create test file
    test_file = tmp_path / "test.csv"
    test_file.write_text("id,name\n1,Test\n")

    result = importer.import_data(test_file)

    assert result.success
    assert result.records_imported == 2
    assert len(result.data) == 2
    assert result.data[0]["id"] == 1
    assert len(result.errors) == 0


def test_importer_import_invalid_source() -> None:
    """Test import with invalid source."""
    importer = SampleImporter()

    result = importer.import_data(Path("/nonexistent/file.csv"))

    assert not result.success
    assert len(result.errors) > 0
    assert "Invalid source file" in result.errors[0]


def test_importer_config() -> None:
    """Test importer configuration."""
    importer = SampleImporter(
        delimiter=",",
        encoding="utf-8",
    )

    assert importer.get_config("delimiter") == ","
    assert importer.get_config("encoding") == "utf-8"
    assert importer.get_config("nonexistent", "default") == "default"


def test_importer_progress_callback() -> None:
    """Test importer progress callback."""
    importer = SampleImporter()

    progress_calls = []

    def callback(current: int, total: int) -> None:
        progress_calls.append((current, total))

    importer.set_progress_callback(callback)
    importer.on_progress(5, 10)

    assert len(progress_calls) == 1
    assert progress_calls[0] == (5, 10)


def test_import_result_creation() -> None:
    """Test import result creation."""
    result = ImportResult(
        success=True,
        data={"key": "value"},
        records_imported=10,
        errors=["error1"],
        warnings=["warning1"],
        metadata={"source": "test.csv"},
    )

    assert result.success
    assert result.data == {"key": "value"}
    assert result.records_imported == 10
    assert "error1" in result.errors
    assert "warning1" in result.warnings
    assert result.metadata["source"] == "test.csv"


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_plugin_lifecycle() -> None:
    """Test complete plugin lifecycle."""
    # Clear registry
    BaseDomainPlugin._registry.clear()

    # Register plugin
    BaseDomainPlugin.register_plugin(SamplePlugin)

    # Get plugin class
    plugin_class = BaseDomainPlugin.get_plugin_class("test_plugin")
    assert plugin_class is not None

    # Instantiate
    plugin = plugin_class()
    assert plugin.status == PluginStatus.UNINITIALIZED

    # Initialize
    plugin.initialize()

    # Verify registrations
    assert len(plugin.list_templates()) > 0
    assert len(plugin.list_formulas()) > 0
    assert len(plugin.list_importers()) > 0

    # Get and use template
    template_class = plugin.get_template("test_template")
    assert template_class is not None
    template = template_class(theme="minimal")
    builder = template.generate()
    assert isinstance(builder, SpreadsheetBuilder)

    # Get and use formula
    formula_class = plugin.get_formula("TESTFUNC")
    assert formula_class is not None
    formula = formula_class()
    formula_str = formula.build(1, 2)
    assert "TESTFUNC" in formula_str

    # Cleanup
    plugin.cleanup()


def test_template_metadata_creation() -> None:
    """Test template metadata creation."""
    metadata = TemplateMetadata(
        name="Budget",
        description="Monthly budget template",
        category="finance",
        tags=("budget", "finance", "monthly"),
        version="2.0.0",
        author="Test",
    )

    assert metadata.name == "Budget"
    assert metadata.category == "finance"
    assert len(metadata.tags) == 3
    assert metadata.version == "2.0.0"
