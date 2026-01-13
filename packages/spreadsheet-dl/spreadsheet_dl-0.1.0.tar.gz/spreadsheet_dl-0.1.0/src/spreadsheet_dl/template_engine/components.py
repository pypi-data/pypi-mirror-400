"""Pre-built template components for financial spreadsheets.

Provides reusable components for common financial document sections:
- Headers and titles
- Budget tables
- Expense summaries
- Income tracking
- Category totals
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spreadsheet_dl.template_engine.schema import (
    CellTemplate,
    ComponentDefinition,
    RowTemplate,
    TemplateVariable,
    VariableType,
)

# ============================================================================
# Header Components
# ============================================================================


def document_header(
    title_var: str = "title",
    subtitle_var: str = "subtitle",
    date_var: str = "date",
) -> ComponentDefinition:
    """Create a document header component with title, subtitle, and date.

    Args:
        title_var: Variable name for title
        subtitle_var: Variable name for subtitle
        date_var: Variable name for date

    Returns:
        ComponentDefinition for document header

    Examples:
        header = document_header()
        # Use in template with:
        #   components:
        #     document_header: <component>
        #   sheets:
        #     - name: Budget
        #       components: ["document_header:title=Monthly Budget"]
    """
    return ComponentDefinition(
        name="document_header",
        description="Standard document header with title, subtitle, and date",
        variables=[
            TemplateVariable(
                name=title_var,
                type=VariableType.STRING,
                description="Document title",
                default="Untitled Document",
            ),
            TemplateVariable(
                name=subtitle_var,
                type=VariableType.STRING,
                description="Document subtitle",
                default="",
            ),
            TemplateVariable(
                name=date_var,
                type=VariableType.STRING,
                description="Document date",
                default="${current_date}",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(
                        value=f"${{{title_var}}}",
                        style="title",
                        colspan=4,
                    ),
                ],
                style="title_row",
                height="24pt",
            ),
            RowTemplate(
                cells=[
                    CellTemplate(
                        value=f"${{{subtitle_var}}}",
                        style="subtitle",
                        colspan=4,
                    ),
                ],
                style="subtitle_row",
                height="18pt",
            ),
            RowTemplate(
                cells=[
                    CellTemplate(
                        value=f"${{{date_var}}}",
                        style="date",
                        type="date",
                    ),
                ],
                style="date_row",
            ),
            # Empty spacer row
            RowTemplate(cells=[], height="12pt"),
        ],
    )


def month_header() -> ComponentDefinition:
    """Create a month-specific header component.

    Returns:
        ComponentDefinition for month header
    """
    return ComponentDefinition(
        name="month_header",
        description="Header for monthly documents with month and year",
        variables=[
            TemplateVariable(
                name="month",
                type=VariableType.NUMBER,
                description="Month number (1-12)",
                required=True,
            ),
            TemplateVariable(
                name="year",
                type=VariableType.NUMBER,
                description="Year",
                default="${current_year}",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(
                        value="${month_name(month)} ${year}",
                        style="title",
                        colspan=4,
                    ),
                ],
                style="title_row",
                height="24pt",
            ),
            RowTemplate(cells=[], height="12pt"),
        ],
    )


# ============================================================================
# Summary Components
# ============================================================================


def income_summary() -> ComponentDefinition:
    """Create an income summary component.

    Returns:
        ComponentDefinition for income summary
    """
    return ComponentDefinition(
        name="income_summary",
        description="Income summary section with total",
        variables=[
            TemplateVariable(
                name="income_total",
                type=VariableType.CURRENCY,
                description="Total income amount",
                default=0,
            ),
            TemplateVariable(
                name="income_label",
                type=VariableType.STRING,
                default="Total Income",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(
                        value="Income Summary", style="section_header", colspan=2
                    ),
                ],
                style="section_header_row",
            ),
            RowTemplate(
                cells=[
                    CellTemplate(value="${income_label}", style="label"),
                    CellTemplate(
                        value="${income_total}", style="currency_value", type="currency"
                    ),
                ],
            ),
        ],
    )


def expense_summary() -> ComponentDefinition:
    """Create an expense summary component.

    Returns:
        ComponentDefinition for expense summary
    """
    return ComponentDefinition(
        name="expense_summary",
        description="Expense summary section with total",
        variables=[
            TemplateVariable(
                name="expense_total",
                type=VariableType.CURRENCY,
                description="Total expense amount",
                default=0,
            ),
            TemplateVariable(
                name="expense_label",
                type=VariableType.STRING,
                default="Total Expenses",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(
                        value="Expense Summary", style="section_header", colspan=2
                    ),
                ],
                style="section_header_row",
            ),
            RowTemplate(
                cells=[
                    CellTemplate(value="${expense_label}", style="label"),
                    CellTemplate(
                        value="${expense_total}",
                        style="currency_value",
                        type="currency",
                    ),
                ],
            ),
        ],
    )


def balance_row() -> ComponentDefinition:
    """Create a balance row component showing net balance.

    Returns:
        ComponentDefinition for balance row
    """
    return ComponentDefinition(
        name="balance_row",
        description="Row showing income minus expenses balance",
        variables=[
            TemplateVariable(
                name="income_cell",
                type=VariableType.STRING,
                description="Cell reference for income total",
                required=True,
            ),
            TemplateVariable(
                name="expense_cell",
                type=VariableType.STRING,
                description="Cell reference for expense total",
                required=True,
            ),
            TemplateVariable(
                name="label",
                type=VariableType.STRING,
                default="Net Balance",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(value="${label}", style="total_label"),
                    CellTemplate(
                        formula="=${income_cell}-${expense_cell}",
                        style="total_value",
                        type="currency",
                    ),
                ],
                style="total_row",
            ),
        ],
    )


# ============================================================================
# Category Components
# ============================================================================


def category_row() -> ComponentDefinition:
    """Create a category row component for budget/expense tracking.

    Returns:
        ComponentDefinition for category row
    """
    return ComponentDefinition(
        name="category_row",
        description="Single category row with budget and actual amounts",
        variables=[
            TemplateVariable(
                name="category",
                type=VariableType.STRING,
                description="Category name",
                required=True,
            ),
            TemplateVariable(
                name="budget",
                type=VariableType.CURRENCY,
                description="Budgeted amount",
                default=0,
            ),
            TemplateVariable(
                name="actual",
                type=VariableType.CURRENCY,
                description="Actual amount",
                default=0,
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(value="${category}", style="category_name"),
                    CellTemplate(
                        value="${budget}", style="currency_cell", type="currency"
                    ),
                    CellTemplate(
                        value="${actual}", style="currency_cell", type="currency"
                    ),
                    CellTemplate(
                        formula="=${budget}-${actual}",
                        style="variance_cell",
                        type="currency",
                    ),
                ],
            ),
        ],
    )


def category_header() -> ComponentDefinition:
    """Create header row for category tables.

    Returns:
        ComponentDefinition for category table header
    """
    return ComponentDefinition(
        name="category_header",
        description="Header row for budget category tables",
        variables=[
            TemplateVariable(
                name="col1_label",
                type=VariableType.STRING,
                default="Category",
            ),
            TemplateVariable(
                name="col2_label",
                type=VariableType.STRING,
                default="Budget",
            ),
            TemplateVariable(
                name="col3_label",
                type=VariableType.STRING,
                default="Actual",
            ),
            TemplateVariable(
                name="col4_label",
                type=VariableType.STRING,
                default="Remaining",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(value="${col1_label}", style="header_cell"),
                    CellTemplate(value="${col2_label}", style="header_cell"),
                    CellTemplate(value="${col3_label}", style="header_cell"),
                    CellTemplate(value="${col4_label}", style="header_cell"),
                ],
                style="header_row",
            ),
        ],
    )


def category_total() -> ComponentDefinition:
    """Create total row for category tables.

    Returns:
        ComponentDefinition for category total row
    """
    return ComponentDefinition(
        name="category_total",
        description="Total row for budget category tables",
        variables=[
            TemplateVariable(
                name="budget_range",
                type=VariableType.STRING,
                description="Range for budget column SUM",
                required=True,
            ),
            TemplateVariable(
                name="actual_range",
                type=VariableType.STRING,
                description="Range for actual column SUM",
                required=True,
            ),
            TemplateVariable(
                name="remaining_range",
                type=VariableType.STRING,
                description="Range for remaining column SUM",
                required=True,
            ),
            TemplateVariable(
                name="label",
                type=VariableType.STRING,
                default="Total",
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(value="${label}", style="total_label"),
                    CellTemplate(
                        formula="=SUM(${budget_range})",
                        style="total_value",
                        type="currency",
                    ),
                    CellTemplate(
                        formula="=SUM(${actual_range})",
                        style="total_value",
                        type="currency",
                    ),
                    CellTemplate(
                        formula="=SUM(${remaining_range})",
                        style="total_value",
                        type="currency",
                    ),
                ],
                style="total_row",
            ),
        ],
    )


# ============================================================================
# Transaction Components
# ============================================================================


def transaction_header() -> ComponentDefinition:
    """Create header for transaction tables.

    Returns:
        ComponentDefinition for transaction table header
    """
    return ComponentDefinition(
        name="transaction_header",
        description="Header row for transaction/expense entry tables",
        variables=[],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(value="Date", style="header_cell"),
                    CellTemplate(value="Description", style="header_cell"),
                    CellTemplate(value="Category", style="header_cell"),
                    CellTemplate(value="Amount", style="header_cell"),
                ],
                style="header_row",
            ),
        ],
    )


def transaction_entry() -> ComponentDefinition:
    """Create a single transaction entry row.

    Returns:
        ComponentDefinition for transaction entry
    """
    return ComponentDefinition(
        name="transaction_entry",
        description="Single transaction entry row",
        variables=[
            TemplateVariable(
                name="date",
                type=VariableType.DATE,
                description="Transaction date",
            ),
            TemplateVariable(
                name="description",
                type=VariableType.STRING,
                description="Transaction description",
                default="",
            ),
            TemplateVariable(
                name="category",
                type=VariableType.STRING,
                description="Transaction category",
                default="",
            ),
            TemplateVariable(
                name="amount",
                type=VariableType.CURRENCY,
                description="Transaction amount",
                default=0,
            ),
        ],
        rows=[
            RowTemplate(
                cells=[
                    CellTemplate(value="${date}", style="date_cell", type="date"),
                    CellTemplate(value="${description}", style="text_cell"),
                    CellTemplate(value="${category}", style="category_cell"),
                    CellTemplate(
                        value="${amount}", style="currency_cell", type="currency"
                    ),
                ],
            ),
        ],
    )


# ============================================================================
# Component Library
# ============================================================================


@dataclass
class ComponentLibrary:
    """Library of pre-built template components.

    Provides access to common financial spreadsheet components
    that can be included in templates.

    Examples:
        library = ComponentLibrary()

        # Get a specific component
        header = library.get("document_header")

        # Get all components for a template
        components = library.all_components()
    """

    # Built-in components
    _components: dict[str, ComponentDefinition] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize with built-in components."""
        self._register_builtin_components()

    def _register_builtin_components(self) -> None:
        """Register all built-in components."""
        builtins = [
            # Headers
            document_header(),
            month_header(),
            # Summaries
            income_summary(),
            expense_summary(),
            balance_row(),
            # Categories
            category_row(),
            category_header(),
            category_total(),
            # Transactions
            transaction_header(),
            transaction_entry(),
        ]

        for component in builtins:
            self._components[component.name] = component

    def get(self, name: str) -> ComponentDefinition | None:
        """Get a component by name.

        Args:
            name: Component name

        Returns:
            ComponentDefinition or None if not found
        """
        return self._components.get(name)

    def register(self, component: ComponentDefinition) -> None:
        """Register a custom component.

        Args:
            component: Component definition to register
        """
        self._components[component.name] = component

    def list_components(self) -> list[str]:
        """List all available component names.

        Returns:
            List of component names
        """
        return list(self._components.keys())

    def all_components(self) -> dict[str, ComponentDefinition]:
        """Get all components as a dictionary.

        Useful for adding all components to a template.

        Returns:
            Dictionary of component name -> ComponentDefinition
        """
        return self._components.copy()

    def get_by_category(self, category: str) -> list[ComponentDefinition]:
        """Get components by category prefix.

        Args:
            category: Category prefix (e.g., "category", "transaction")

        Returns:
            List of matching components
        """
        return [
            comp for name, comp in self._components.items() if name.startswith(category)
        ]


# Global component library instance
COMPONENT_LIBRARY = ComponentLibrary()


def get_component(name: str) -> ComponentDefinition | None:
    """Get a component from the global library.

    Args:
        name: Component name

    Returns:
        ComponentDefinition or None
    """
    return COMPONENT_LIBRARY.get(name)


def list_components() -> list[str]:
    """List all available components.

    Returns:
        List of component names
    """
    return COMPONENT_LIBRARY.list_components()


def get_all_components() -> dict[str, ComponentDefinition]:
    """Get all components for use in templates.

    Returns:
        Dictionary of all components
    """
    return COMPONENT_LIBRARY.all_components()
