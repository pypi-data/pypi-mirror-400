"""Domain Plugins for SpreadsheetDL.

Domain-specific functionality organized as plugins.

    PHASE0-001: Restructure package for domain plugins
    PHASE0-002: Create domain plugin base classes
"""

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

__all__ = [
    # Base Classes
    "BaseDomainPlugin",
    "BaseFormula",
    "BaseImporter",
    "BaseTemplate",
    "FormulaArgument",
    "FormulaMetadata",
    "ImportResult",
    "ImporterMetadata",
    "PluginDependency",
    # Metadata Classes
    "PluginMetadata",
    "PluginStatus",
    "TemplateMetadata",
    # Domain Subpackages (9 domains)
    "biology",
    "civil_engineering",
    "data_science",
    "education",
    "electrical_engineering",
    "environmental",
    "finance",
    "manufacturing",
    "mechanical_engineering",
]
