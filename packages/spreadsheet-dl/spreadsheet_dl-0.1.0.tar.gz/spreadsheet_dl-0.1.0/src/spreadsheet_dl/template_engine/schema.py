"""Template schema definitions for YAML-based spreadsheet templates.

Provides dataclass definitions for template structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VariableType(Enum):
    """Template variable types."""

    STRING = "string"
    NUMBER = "number"
    CURRENCY = "currency"
    DATE = "date"
    BOOLEAN = "boolean"
    LIST = "list"
    FORMULA = "formula"


@dataclass
class TemplateVariable:
    """Template variable definition.

    Variables are placeholders that get replaced with actual values
    during template rendering.

    Examples:
        month_var = TemplateVariable(
            name="month",
            type=VariableType.NUMBER,
            description="Month number (1-12)",
            required=True,
            default=None,
        )

        year_var = TemplateVariable(
            name="year",
            type=VariableType.NUMBER,
            default=2024,
        )
    """

    name: str
    type: VariableType = VariableType.STRING
    description: str = ""
    required: bool = False
    default: Any = None
    validation: str | None = None  # Regex or formula for validation
    choices: list[str] = field(default_factory=list)  # For list/enum types

    def validate_value(self, value: Any) -> bool:
        """Validate a value against this variable's type."""
        if value is None:
            return not self.required

        if self.type == VariableType.NUMBER:
            return isinstance(value, (int, float))
        if self.type == VariableType.BOOLEAN:
            return isinstance(value, bool)
        if self.type == VariableType.LIST:
            return isinstance(value, list)
        if self.type == VariableType.STRING:
            if self.choices and value not in self.choices:
                return False
            return isinstance(value, str)

        return True

    def get_value(self, provided: Any = None) -> Any:
        """Get value, using default if not provided."""
        if provided is not None:
            return provided
        if self.default is not None:
            return self.default
        if self.required:
            raise ValueError(f"Required variable '{self.name}' not provided")
        return None


@dataclass
class ConditionalBlock:
    """Conditional content block.

    Content that is included or excluded based on conditions.

    Examples:
        # Show section only if has_savings is true
        block = ConditionalBlock(
            condition="has_savings == true",
            content=[...],  # Rows to include
        )

        # Conditional formatting
        block = ConditionalBlock(
            condition="amount > 1000",
            style="highlight",
        )
    """

    condition: str  # Expression to evaluate
    content: list[Any] = field(default_factory=list)  # Content if true
    else_content: list[Any] = field(default_factory=list)  # Content if false
    style: str | None = None  # Style to apply if condition is true


@dataclass
class CellTemplate:
    """Template for a single cell.

    Examples:
        # Static value
        cell = CellTemplate(value="Total")

        # Variable reference
        cell = CellTemplate(value="${month_name}")

        # Formula
        cell = CellTemplate(
            formula="=SUM(B2:B{last_row})",
            style="total",
            type="currency",
        )
    """

    value: Any = None
    formula: str | None = None
    style: str | None = None
    type: str | None = None  # "string", "currency", "date", "percentage"
    colspan: int = 1
    rowspan: int = 1
    validation: str | None = None  # Reference to validation rule
    conditional_format: str | None = None  # Reference to conditional format


@dataclass
class RowTemplate:
    """Template for a row.

    Examples:
        # Header row
        header = RowTemplate(
            cells=[
                CellTemplate(value="Date"),
                CellTemplate(value="Description"),
                CellTemplate(value="Amount"),
            ],
            style="header",
        )

        # Data row template (for repeat)
        data = RowTemplate(
            cells=[
                CellTemplate(type="date"),
                CellTemplate(type="string"),
                CellTemplate(type="currency"),
            ],
            repeat=50,  # Repeat 50 times
            style="data",
            alternate_style="data_alt",  # For zebra striping
        )
    """

    cells: list[CellTemplate] = field(default_factory=list)
    style: str | None = None
    height: str | None = None
    repeat: int = 1  # Number of times to repeat this row
    alternate_style: str | None = None  # Alternating row style
    conditional: ConditionalBlock | None = None


@dataclass
class ColumnTemplate:
    """Template for a column definition.

    Examples:
        columns = [
            ColumnTemplate(name="Date", width="2.5cm", type="date"),
            ColumnTemplate(name="Category", width="4cm", validation="category_list"),
            ColumnTemplate(name="Amount", width="3cm", type="currency", style="currency"),
        ]
    """

    name: str
    width: str = "2.5cm"
    type: str = "string"  # "string", "currency", "date", "percentage"
    style: str | None = None  # Default style for this column
    validation: str | None = None  # Reference to validation rule
    conditional_format: str | None = None  # Reference to conditional format
    hidden: bool = False
    frozen: bool = False  # Freeze this column


@dataclass
class ComponentDefinition:
    """Reusable component definition.

    Components are reusable sections that can be included in templates.

    Examples:
        # Header component
        header_component = ComponentDefinition(
            name="budget_header",
            description="Standard budget header with title and date",
            variables=[
                TemplateVariable("title", VariableType.STRING, required=True),
                TemplateVariable("date", VariableType.DATE),
            ],
            rows=[
                RowTemplate(cells=[CellTemplate(value="${title}")], style="title"),
                RowTemplate(cells=[CellTemplate(value="${date}")], style="subtitle"),
            ],
        )
    """

    name: str
    description: str = ""
    variables: list[TemplateVariable] = field(default_factory=list)
    columns: list[ColumnTemplate] = field(default_factory=list)
    rows: list[RowTemplate] = field(default_factory=list)
    styles: dict[str, str] = field(default_factory=dict)  # Local style overrides


@dataclass
class SheetTemplate:
    """Template for a complete sheet.

    Examples:
        sheet = SheetTemplate(
            name="Monthly Budget",
            columns=[
                ColumnTemplate("Category", width="4cm"),
                ColumnTemplate("Budget", width="3cm", type="currency"),
                ColumnTemplate("Actual", width="3cm", type="currency"),
                ColumnTemplate("Remaining", width="3cm", type="currency"),
            ],
            header_row=RowTemplate(style="header"),
            data_rows=RowTemplate(repeat=20, style="data"),
            total_row=RowTemplate(
                cells=[
                    CellTemplate("Total"),
                    CellTemplate(formula="=SUM(B2:B21)"),
                    CellTemplate(formula="=SUM(C2:C21)"),
                    CellTemplate(formula="=SUM(D2:D21)"),
                ],
                style="total",
            ),
            freeze_rows=1,
        )
    """

    name: str
    name_template: str | None = None  # e.g., "${month_name} ${year}"
    columns: list[ColumnTemplate] = field(default_factory=list)

    # Row sections
    header_row: RowTemplate | None = None
    data_rows: RowTemplate | None = None  # Template for data entry rows
    total_row: RowTemplate | None = None
    custom_rows: list[RowTemplate] = field(default_factory=list)

    # Components to include
    components: list[str] = field(default_factory=list)  # Component references

    # Sheet settings
    freeze_rows: int = 0
    freeze_cols: int = 0
    print_area: str | None = None
    protection: dict[str, Any] = field(default_factory=dict)

    # Conditional content
    conditionals: list[ConditionalBlock] = field(default_factory=list)

    # References
    validations: list[str] = field(default_factory=list)  # Validation rule refs
    conditional_formats: list[str] = field(default_factory=list)  # CF rule refs


@dataclass
class SpreadsheetTemplate:
    """Complete spreadsheet template definition.

    Top-level container for a template with all its sheets,
    variables, components, and configuration.

    Examples:
        template = SpreadsheetTemplate(
            name="monthly-budget",
            version="1.0.0",
            description="Monthly budget tracking template",
            theme="corporate",
            variables=[
                TemplateVariable("month", VariableType.NUMBER, required=True),
                TemplateVariable("year", VariableType.NUMBER, required=True),
                TemplateVariable("categories", VariableType.LIST, required=True),
            ],
            sheets=[
                SheetTemplate(name="Budget", ...),
                SheetTemplate(name="Expenses", ...),
                SheetTemplate(name="Summary", ...),
            ],
        )
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    theme: str = "default"

    # Variables
    variables: list[TemplateVariable] = field(default_factory=list)

    # Components (reusable sections)
    components: dict[str, ComponentDefinition] = field(default_factory=dict)

    # Sheets
    sheets: list[SheetTemplate] = field(default_factory=list)

    # Document properties
    properties: dict[str, Any] = field(default_factory=dict)

    # Validations (reusable validation rules)
    validations: dict[str, Any] = field(default_factory=dict)

    # Conditional formats (reusable CF rules)
    conditional_formats: dict[str, Any] = field(default_factory=dict)

    # Custom styles (template-specific styles)
    styles: dict[str, Any] = field(default_factory=dict)

    def get_variable(self, name: str) -> TemplateVariable | None:
        """Get variable by name."""
        for var in self.variables:
            if var.name == name:
                return var
        return None

    def get_component(self, name: str) -> ComponentDefinition | None:
        """Get component by name."""
        return self.components.get(name)

    def validate_variables(self, values: dict[str, Any]) -> list[str]:
        """Validate provided variable values.

        Returns:
            List of validation error messages
        """
        errors = []

        for var in self.variables:
            if var.required and var.name not in values:
                errors.append(f"Required variable '{var.name}' not provided")
            elif var.name in values and not var.validate_value(values[var.name]):
                errors.append(
                    f"Invalid value for variable '{var.name}': "
                    f"expected {var.type.value}"
                )

        return errors

    def get_resolved_variables(self, provided: dict[str, Any]) -> dict[str, Any]:
        """Get all variables with defaults applied.

        Args:
            provided: Provided variable values

        Returns:
            Complete variable dictionary
        """
        result = {}
        for var in self.variables:
            result[var.name] = var.get_value(provided.get(var.name))
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "theme": self.theme,
            "variables": [
                {
                    "name": v.name,
                    "type": v.type.value,
                    "description": v.description,
                    "required": v.required,
                    "default": v.default,
                }
                for v in self.variables
            ],
            "sheets": [s.name for s in self.sheets],
            "properties": self.properties,
        }
