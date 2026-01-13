"""ODS Spreadsheet Generator for family budget tracking.

Creates ODS files with formulas, formatting, and structure compatible
with Collabora Office and mobile editing via Nextcloud.

Supports both legacy hardcoded styles and theme-based styling through
the declarative DSL system.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TableCellProperties, TextProperties
from odf.table import Table, TableCell, TableColumn, TableRow
from odf.text import P

if TYPE_CHECKING:
    from collections.abc import Sequence

    from spreadsheet_dl.schema.styles import CellStyle, Theme


class ExpenseCategory(Enum):
    """Standard expense categories for budget tracking."""

    HOUSING = "Housing"
    UTILITIES = "Utilities"
    GROCERIES = "Groceries"
    TRANSPORTATION = "Transportation"
    HEALTHCARE = "Healthcare"
    INSURANCE = "Insurance"
    ENTERTAINMENT = "Entertainment"
    DINING_OUT = "Dining Out"
    CLOTHING = "Clothing"
    PERSONAL = "Personal Care"
    EDUCATION = "Education"
    SAVINGS = "Savings"
    DEBT_PAYMENT = "Debt Payment"
    GIFTS = "Gifts"
    SUBSCRIPTIONS = "Subscriptions"
    MISCELLANEOUS = "Miscellaneous"


@dataclass
class ExpenseEntry:
    """Single expense entry."""

    date: date
    category: ExpenseCategory
    description: str
    amount: Decimal
    notes: str = ""


@dataclass
class BudgetAllocation:
    """Budget allocation for a category."""

    category: ExpenseCategory
    monthly_budget: Decimal
    notes: str = ""


class OdsGenerator:
    """Generate ODS spreadsheets for family budget tracking.

    Creates formatted spreadsheets with:
    - Expense tracking sheets
    - Budget allocation sheets
    - Summary sheets with formulas
    - Conditional formatting for over-budget alerts

    Compatible with Collabora Office and mobile editing.

    Supports optional theme-based styling through the declarative DSL:

    ```python
    # Legacy (hardcoded styles)
    generator = OdsGenerator()

    # Theme-based styling
    generator = OdsGenerator(theme="corporate")
    generator = OdsGenerator(theme="minimal")
    ```
    """

    def __init__(
        self,
        theme: str | Theme | None = None,
        theme_dir: Path | str | None = None,
    ) -> None:
        """Initialize the ODS generator.

        Args:
            theme: Theme name (e.g., "default", "corporate") or Theme object.
                   If None, uses legacy hardcoded styles.
            theme_dir: Directory containing theme YAML files.
        """
        self._doc: OpenDocumentSpreadsheet | None = None
        self._styles: dict[str, Style] = {}
        self._theme: Theme | None = None
        self._theme_name: str | None = None
        self._theme_dir = Path(theme_dir) if theme_dir else None
        self._style_counter = 0

        if theme is not None:
            if isinstance(theme, str):
                self._theme_name = theme
            else:
                self._theme = theme

    def _get_theme(self) -> Theme | None:
        """Load theme if specified by name."""
        if self._theme is None and self._theme_name is not None:
            try:
                from spreadsheet_dl.schema.loader import ThemeLoader

                loader = ThemeLoader(self._theme_dir)
                self._theme = loader.load(self._theme_name)
            except ImportError:
                # YAML not available, fall back to hardcoded styles
                pass
            except FileNotFoundError:
                # Theme not found, fall back to hardcoded styles
                pass
        return self._theme

    def create_budget_spreadsheet(
        self,
        output_path: Path | str,
        *,
        month: int | None = None,
        year: int | None = None,
        budget_allocations: Sequence[BudgetAllocation] | None = None,
        expenses: Sequence[ExpenseEntry] | None = None,
    ) -> Path:
        """Create a complete budget tracking spreadsheet.

        Args:
            output_path: Path to save the ODS file.
            month: Month number (1-12). Defaults to current month.
            year: Year. Defaults to current year.
            budget_allocations: List of budget allocations per category.
            expenses: List of expense entries to pre-populate.

        Returns:
            Path to the created ODS file.
        """
        output_path = Path(output_path)
        today = date.today()
        month = month or today.month
        year = year or today.year

        self._doc = OpenDocumentSpreadsheet()
        self._create_styles()

        # Create sheets
        self._create_expense_sheet(expenses or [])
        self._create_budget_sheet(budget_allocations or self._default_allocations())
        self._create_summary_sheet(month, year)

        # Save document
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._doc.save(str(output_path))
        return output_path

    def create_expense_template(
        self,
        output_path: Path | str,
        *,
        categories: Sequence[ExpenseCategory] | None = None,
    ) -> Path:
        """Create a blank expense tracking template.

        Args:
            output_path: Path to save the ODS file.
            categories: Categories to include. Defaults to all.

        Returns:
            Path to the created ODS file.
        """
        output_path = Path(output_path)
        categories = categories or list(ExpenseCategory)

        self._doc = OpenDocumentSpreadsheet()
        self._create_styles()

        # Create single expense sheet
        self._create_expense_sheet([])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._doc.save(str(output_path))
        return output_path

    def _create_styles(self) -> None:
        """Create cell styles for the spreadsheet."""
        if self._doc is None:
            return

        # Try to use theme-based styles
        theme = self._get_theme()
        if theme:
            self._create_theme_styles(theme)
        else:
            self._create_legacy_styles()

    def _create_legacy_styles(self) -> None:
        """Create legacy hardcoded cell styles."""
        if self._doc is None:
            return

        # Header style
        header_style = Style(name="HeaderCell", family="table-cell")
        header_style.addElement(
            TableCellProperties(backgroundcolor="#4472C4", padding="2pt")
        )
        header_style.addElement(TextProperties(fontweight="bold", color="#FFFFFF"))
        self._doc.automaticstyles.addElement(header_style)
        self._styles["header"] = header_style

        # Currency style
        currency_style = Style(name="CurrencyCell", family="table-cell")
        currency_style.addElement(TableCellProperties(padding="2pt"))
        self._doc.automaticstyles.addElement(currency_style)
        self._styles["currency"] = currency_style

        # Date style
        date_style = Style(name="DateCell", family="table-cell")
        date_style.addElement(TableCellProperties(padding="2pt"))
        self._doc.automaticstyles.addElement(date_style)
        self._styles["date"] = date_style

        # Warning style (over budget)
        warning_style = Style(name="WarningCell", family="table-cell")
        warning_style.addElement(
            TableCellProperties(backgroundcolor="#FFC7CE", padding="2pt")
        )
        warning_style.addElement(TextProperties(color="#9C0006"))
        self._doc.automaticstyles.addElement(warning_style)
        self._styles["warning"] = warning_style

        # Good style (under budget)
        good_style = Style(name="GoodCell", family="table-cell")
        good_style.addElement(
            TableCellProperties(backgroundcolor="#C6EFCE", padding="2pt")
        )
        good_style.addElement(TextProperties(color="#006100"))
        self._doc.automaticstyles.addElement(good_style)
        self._styles["good"] = good_style

    def _create_theme_styles(self, theme: Theme) -> None:
        """Create styles from theme definitions."""
        if self._doc is None:
            return

        # Create styles for all theme-defined styles
        for style_name in theme.list_styles():
            try:
                cell_style = theme.get_style(style_name)
                odf_style = self._cell_style_to_odf(style_name, cell_style)
                self._doc.automaticstyles.addElement(odf_style)
                self._styles[style_name] = odf_style
            except (KeyError, ValueError, AttributeError):
                # Skip styles that fail to resolve
                pass

        # Map semantic names to theme styles for backward compatibility
        style_mappings = {
            "header": ["header_primary", "header"],
            "currency": ["cell_currency", "currency"],
            "date": ["cell_date", "date"],
            "warning": ["cell_warning", "cell_danger", "warning"],
            "good": ["cell_success", "good"],
        }

        for internal_name, candidates in style_mappings.items():
            if internal_name not in self._styles:
                for candidate in candidates:
                    if candidate in self._styles:
                        self._styles[internal_name] = self._styles[candidate]
                        break

        # Ensure minimum required styles exist (fallback to legacy)
        if "header" not in self._styles:
            self._create_legacy_styles()

    def _cell_style_to_odf(self, name: str, cell_style: CellStyle) -> Style:
        """Convert CellStyle to ODF Style."""
        self._style_counter += 1
        style = Style(name=f"Theme_{name}_{self._style_counter}", family="table-cell")

        # Cell properties
        cell_props: dict[str, Any] = {}

        if cell_style.background_color:
            cell_props["backgroundcolor"] = str(cell_style.background_color)

        if cell_style.padding:
            cell_props["padding"] = cell_style.padding

        # Borders
        if cell_style.border_top:
            cell_props["bordertop"] = cell_style.border_top.to_odf()
        if cell_style.border_bottom:
            cell_props["borderbottom"] = cell_style.border_bottom.to_odf()
        if cell_style.border_left:
            cell_props["borderleft"] = cell_style.border_left.to_odf()
        if cell_style.border_right:
            cell_props["borderright"] = cell_style.border_right.to_odf()

        if cell_props:
            style.addElement(TableCellProperties(**cell_props))

        # Text properties
        text_props: dict[str, Any] = {}

        if cell_style.font.family:
            text_props["fontfamily"] = cell_style.font.family

        if cell_style.font.size:
            text_props["fontsize"] = cell_style.font.size

        if cell_style.font.weight.value == "bold":
            text_props["fontweight"] = "bold"

        if cell_style.font.color:
            text_props["color"] = str(cell_style.font.color)

        if cell_style.font.italic:
            text_props["fontstyle"] = "italic"

        if text_props:
            style.addElement(TextProperties(**text_props))

        return style

    def _create_expense_sheet(self, expenses: Sequence[ExpenseEntry]) -> None:
        """Create the expense tracking sheet."""
        if self._doc is None:
            return

        table = Table(name="Expense Log")

        # Column widths
        for _ in range(5):
            table.addElement(TableColumn())

        # Header row
        headers = ["Date", "Category", "Description", "Amount", "Notes"]
        header_row = TableRow()
        for header in headers:
            cell = TableCell(stylename=self._styles["header"])
            cell.addElement(P(text=header))
            header_row.addElement(cell)
        table.addElement(header_row)

        # Data rows
        for expense in expenses:
            row = TableRow()

            # Date
            date_cell = TableCell(
                valuetype="date",
                datevalue=expense.date.isoformat(),
                stylename=self._styles.get("date"),
            )
            date_cell.addElement(P(text=expense.date.strftime("%Y-%m-%d")))
            row.addElement(date_cell)

            # Category
            cat_cell = TableCell(valuetype="string")
            cat_cell.addElement(P(text=expense.category.value))
            row.addElement(cat_cell)

            # Description
            desc_cell = TableCell(valuetype="string")
            desc_cell.addElement(P(text=expense.description))
            row.addElement(desc_cell)

            # Amount
            amount_cell = TableCell(
                valuetype="currency",
                value=str(expense.amount),
                stylename=self._styles.get("currency"),
            )
            amount_cell.addElement(P(text=f"${expense.amount:.2f}"))
            row.addElement(amount_cell)

            # Notes
            notes_cell = TableCell(valuetype="string")
            notes_cell.addElement(P(text=expense.notes))
            row.addElement(notes_cell)

            table.addElement(row)

        # Add empty rows for data entry (mobile-friendly)
        for _ in range(50):
            row = TableRow()
            for _ in range(5):
                row.addElement(TableCell())
            table.addElement(row)

        self._doc.spreadsheet.addElement(table)

    def _create_budget_sheet(self, allocations: Sequence[BudgetAllocation]) -> None:
        """Create the budget allocation sheet."""
        if self._doc is None:
            return

        table = Table(name="Budget")

        # Column widths
        for _ in range(3):
            table.addElement(TableColumn())

        # Header row
        headers = ["Category", "Monthly Budget", "Notes"]
        header_row = TableRow()
        for header in headers:
            cell = TableCell(stylename=self._styles["header"])
            cell.addElement(P(text=header))
            header_row.addElement(cell)
        table.addElement(header_row)

        # Data rows
        for allocation in allocations:
            row = TableRow()

            # Category
            cat_cell = TableCell(valuetype="string")
            cat_cell.addElement(P(text=allocation.category.value))
            row.addElement(cat_cell)

            # Budget amount
            budget_cell = TableCell(
                valuetype="currency",
                value=str(allocation.monthly_budget),
                stylename=self._styles.get("currency"),
            )
            budget_cell.addElement(P(text=f"${allocation.monthly_budget:.2f}"))
            row.addElement(budget_cell)

            # Notes
            notes_cell = TableCell(valuetype="string")
            notes_cell.addElement(P(text=allocation.notes))
            row.addElement(notes_cell)

            table.addElement(row)

        # Total row
        total_row = TableRow()
        total_label = TableCell(stylename=self._styles["header"])
        total_label.addElement(P(text="TOTAL"))
        total_row.addElement(total_label)

        # SUM formula
        row_count = len(allocations) + 1  # +1 for header
        total_cell = TableCell(
            valuetype="currency",
            formula=f"of:=SUM([.B2:.B{row_count}])",
            stylename=self._styles["header"],
        )
        total_cell.addElement(P(text=""))
        total_row.addElement(total_cell)
        total_row.addElement(TableCell())

        table.addElement(total_row)
        self._doc.spreadsheet.addElement(table)

    def _create_summary_sheet(self, month: int, year: int) -> None:
        """Create the summary sheet with formulas."""
        if self._doc is None:
            return

        month_name = datetime(year, month, 1).strftime("%B %Y")
        table = Table(name=f"Summary - {month_name}")

        # Column widths
        for _ in range(4):
            table.addElement(TableColumn())

        # Header row
        headers = ["Category", "Budget", "Actual", "Remaining"]
        header_row = TableRow()
        for header in headers:
            cell = TableCell(stylename=self._styles["header"])
            cell.addElement(P(text=header))
            header_row.addElement(cell)
        table.addElement(header_row)

        # Category rows with SUMIF formulas
        for i, category in enumerate(ExpenseCategory, start=2):
            row = TableRow()

            # Category name
            cat_cell = TableCell(valuetype="string")
            cat_cell.addElement(P(text=category.value))
            row.addElement(cat_cell)

            # Budget (lookup from Budget sheet)
            budget_cell = TableCell(
                valuetype="currency",
                formula=f"of:=VLOOKUP([.A{i}];[Budget.$A:$B];2;0)",
                stylename=self._styles.get("currency"),
            )
            budget_cell.addElement(P(text=""))
            row.addElement(budget_cell)

            # Actual (SUMIF from Expense Log)
            actual_cell = TableCell(
                valuetype="currency",
                formula=f"of:=SUMIF(['Expense Log'.$B:$B];[.A{i}];['Expense Log'.$D:$D])",
                stylename=self._styles.get("currency"),
            )
            actual_cell.addElement(P(text=""))
            row.addElement(actual_cell)

            # Remaining (Budget - Actual)
            remaining_cell = TableCell(
                valuetype="currency",
                formula=f"of:=[.B{i}]-[.C{i}]",
                stylename=self._styles.get("currency"),
            )
            remaining_cell.addElement(P(text=""))
            row.addElement(remaining_cell)

            table.addElement(row)

        # Total row
        total_row = TableRow()
        total_label = TableCell(stylename=self._styles["header"])
        total_label.addElement(P(text="TOTAL"))
        total_row.addElement(total_label)

        row_end = len(ExpenseCategory) + 1
        for col in ["B", "C", "D"]:
            total_cell = TableCell(
                valuetype="currency",
                formula=f"of:=SUM([.{col}2:.{col}{row_end}])",
                stylename=self._styles["header"],
            )
            total_cell.addElement(P(text=""))
            total_row.addElement(total_cell)

        table.addElement(total_row)
        self._doc.spreadsheet.addElement(table)

    def _default_allocations(self) -> list[BudgetAllocation]:
        """Return default budget allocations."""
        return [
            BudgetAllocation(ExpenseCategory.HOUSING, Decimal("1500")),
            BudgetAllocation(ExpenseCategory.UTILITIES, Decimal("200")),
            BudgetAllocation(ExpenseCategory.GROCERIES, Decimal("600")),
            BudgetAllocation(ExpenseCategory.TRANSPORTATION, Decimal("400")),
            BudgetAllocation(ExpenseCategory.HEALTHCARE, Decimal("200")),
            BudgetAllocation(ExpenseCategory.INSURANCE, Decimal("300")),
            BudgetAllocation(ExpenseCategory.ENTERTAINMENT, Decimal("150")),
            BudgetAllocation(ExpenseCategory.DINING_OUT, Decimal("200")),
            BudgetAllocation(ExpenseCategory.CLOTHING, Decimal("100")),
            BudgetAllocation(ExpenseCategory.PERSONAL, Decimal("75")),
            BudgetAllocation(ExpenseCategory.EDUCATION, Decimal("50")),
            BudgetAllocation(ExpenseCategory.SAVINGS, Decimal("500")),
            BudgetAllocation(ExpenseCategory.DEBT_PAYMENT, Decimal("300")),
            BudgetAllocation(ExpenseCategory.GIFTS, Decimal("50")),
            BudgetAllocation(ExpenseCategory.SUBSCRIPTIONS, Decimal("100")),
            BudgetAllocation(ExpenseCategory.MISCELLANEOUS, Decimal("100")),
        ]


def create_monthly_budget(
    output_dir: Path | str,
    *,
    month: int | None = None,
    year: int | None = None,
    theme: str | None = None,
) -> Path:
    """Convenience function to create a monthly budget spreadsheet.

    Args:
        output_dir: Directory to save the file.
        month: Month number (1-12). Defaults to current.
        year: Year. Defaults to current.
        theme: Optional theme name (e.g., "default", "corporate").

    Returns:
        Path to the created file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    today = date.today()
    month = month or today.month
    year = year or today.year

    filename = f"budget_{year}_{month:02d}.ods"
    output_path = output_dir / filename

    generator = OdsGenerator(theme=theme)
    return generator.create_budget_spreadsheet(output_path, month=month, year=year)
