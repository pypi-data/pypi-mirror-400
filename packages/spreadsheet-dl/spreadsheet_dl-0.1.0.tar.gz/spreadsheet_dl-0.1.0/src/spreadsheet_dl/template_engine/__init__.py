"""Enhanced template engine for professional spreadsheet generation.

Provides a YAML-based template system with:
- Variable substitution
- Conditional content
- Reusable components
- Sheet templates with styling
"""

from spreadsheet_dl.template_engine.loader import (
    TemplateLoader,
    load_template,
    load_template_from_yaml,
)
from spreadsheet_dl.template_engine.renderer import (
    ConditionalEvaluator,
    ExpressionEvaluator,
    RenderedCell,
    RenderedRow,
    RenderedSheet,
    RenderedSpreadsheet,
    TemplateRenderer,
    render_template,
)
from spreadsheet_dl.template_engine.schema import (
    CellTemplate,
    ColumnTemplate,
    ComponentDefinition,
    ConditionalBlock,
    RowTemplate,
    SheetTemplate,
    SpreadsheetTemplate,
    TemplateVariable,
    VariableType,
)

__all__ = [
    "CellTemplate",
    "ColumnTemplate",
    "ComponentDefinition",
    "ConditionalBlock",
    "ConditionalEvaluator",
    "ExpressionEvaluator",
    "RenderedCell",
    "RenderedRow",
    "RenderedSheet",
    "RenderedSpreadsheet",
    "RowTemplate",
    "SheetTemplate",
    # Schema
    "SpreadsheetTemplate",
    # Loader
    "TemplateLoader",
    # Renderer
    "TemplateRenderer",
    "TemplateVariable",
    "VariableType",
    "load_template",
    "load_template_from_yaml",
    "render_template",
]
