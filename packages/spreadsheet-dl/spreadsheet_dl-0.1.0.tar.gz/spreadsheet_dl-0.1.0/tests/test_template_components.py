"""Comprehensive tests for template_engine/components.py - targeting 100% coverage.


Tests all pre-built template components for financial spreadsheets.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.template_engine.components import (
    COMPONENT_LIBRARY,
    ComponentLibrary,
    balance_row,
    category_header,
    category_row,
    category_total,
    document_header,
    expense_summary,
    get_all_components,
    get_component,
    income_summary,
    list_components,
    month_header,
    transaction_entry,
    transaction_header,
)
from spreadsheet_dl.template_engine.schema import (
    ComponentDefinition,
    VariableType,
)

pytestmark = [pytest.mark.unit, pytest.mark.templates]


# ============================================================================
# Header Components Tests
# ============================================================================


class TestDocumentHeader:
    """Tests for document_header component."""

    def test_document_header_default(self) -> None:
        """Test document_header with default variable names."""
        comp = document_header()
        assert comp.name == "document_header"
        assert (
            comp.description
            == "Standard document header with title, subtitle, and date"
        )
        assert len(comp.variables) == 3
        assert len(comp.rows) == 4  # Title, subtitle, date, spacer

    def test_document_header_variables(self) -> None:
        """Test document_header has correct variables."""
        comp = document_header()
        var_names = [v.name for v in comp.variables]
        assert "title" in var_names
        assert "subtitle" in var_names
        assert "date" in var_names

    def test_document_header_custom_var_names(self) -> None:
        """Test document_header with custom variable names."""
        comp = document_header(
            title_var="my_title", subtitle_var="my_sub", date_var="my_date"
        )
        var_names = [v.name for v in comp.variables]
        assert "my_title" in var_names
        assert "my_sub" in var_names
        assert "my_date" in var_names

    def test_document_header_row_structure(self) -> None:
        """Test document_header row structure."""
        comp = document_header()
        # First row: title
        assert len(comp.rows[0].cells) == 1
        assert comp.rows[0].cells[0].value == "${title}"
        assert comp.rows[0].cells[0].style == "title"
        assert comp.rows[0].cells[0].colspan == 4
        # Second row: subtitle
        assert len(comp.rows[1].cells) == 1
        assert comp.rows[1].cells[0].value == "${subtitle}"
        # Third row: date
        assert len(comp.rows[2].cells) == 1
        assert comp.rows[2].cells[0].value == "${date}"
        assert comp.rows[2].cells[0].type == "date"
        # Fourth row: spacer
        assert len(comp.rows[3].cells) == 0

    def test_document_header_defaults(self) -> None:
        """Test document_header variable defaults."""
        comp = document_header()
        title_var = next(v for v in comp.variables if v.name == "title")
        assert title_var.default == "Untitled Document"
        date_var = next(v for v in comp.variables if v.name == "date")
        assert date_var.default == "${current_date}"


class TestMonthHeader:
    """Tests for month_header component."""

    def test_month_header_structure(self) -> None:
        """Test month_header structure."""
        comp = month_header()
        assert comp.name == "month_header"
        assert len(comp.variables) == 2
        assert len(comp.rows) == 2  # Month/year, spacer

    def test_month_header_variables(self) -> None:
        """Test month_header variables."""
        comp = month_header()
        var_names = {v.name: v for v in comp.variables}
        assert "month" in var_names
        assert "year" in var_names
        assert var_names["month"].type == VariableType.NUMBER
        assert var_names["month"].required is True
        assert var_names["year"].default == "${current_year}"

    def test_month_header_template(self) -> None:
        """Test month_header template syntax."""
        comp = month_header()
        cell = comp.rows[0].cells[0]
        assert "${month_name(month)}" in cell.value
        assert "${year}" in cell.value


# ============================================================================
# Summary Components Tests
# ============================================================================


class TestIncomeSummary:
    """Tests for income_summary component."""

    def test_income_summary_structure(self) -> None:
        """Test income_summary structure."""
        comp = income_summary()
        assert comp.name == "income_summary"
        assert len(comp.variables) == 2
        assert len(comp.rows) == 2  # Header, total

    def test_income_summary_variables(self) -> None:
        """Test income_summary variables."""
        comp = income_summary()
        var_names = {v.name: v for v in comp.variables}
        assert "income_total" in var_names
        assert "income_label" in var_names
        assert var_names["income_total"].type == VariableType.CURRENCY
        assert var_names["income_total"].default == 0
        assert var_names["income_label"].default == "Total Income"

    def test_income_summary_rows(self) -> None:
        """Test income_summary row structure."""
        comp = income_summary()
        # Header row
        assert comp.rows[0].cells[0].value == "Income Summary"
        assert comp.rows[0].cells[0].style == "section_header"
        # Total row
        assert comp.rows[1].cells[0].value == "${income_label}"
        assert comp.rows[1].cells[1].value == "${income_total}"
        assert comp.rows[1].cells[1].type == "currency"


class TestExpenseSummary:
    """Tests for expense_summary component."""

    def test_expense_summary_structure(self) -> None:
        """Test expense_summary structure."""
        comp = expense_summary()
        assert comp.name == "expense_summary"
        assert len(comp.variables) == 2
        assert len(comp.rows) == 2

    def test_expense_summary_variables(self) -> None:
        """Test expense_summary variables."""
        comp = expense_summary()
        var_names = {v.name: v for v in comp.variables}
        assert "expense_total" in var_names
        assert "expense_label" in var_names
        assert var_names["expense_total"].type == VariableType.CURRENCY
        assert var_names["expense_label"].default == "Total Expenses"

    def test_expense_summary_rows(self) -> None:
        """Test expense_summary row structure."""
        comp = expense_summary()
        assert comp.rows[0].cells[0].value == "Expense Summary"
        assert comp.rows[1].cells[0].value == "${expense_label}"
        assert comp.rows[1].cells[1].value == "${expense_total}"
        assert comp.rows[1].cells[1].type == "currency"


class TestBalanceRow:
    """Tests for balance_row component."""

    def test_balance_row_structure(self) -> None:
        """Test balance_row structure."""
        comp = balance_row()
        assert comp.name == "balance_row"
        assert len(comp.variables) == 3
        assert len(comp.rows) == 1

    def test_balance_row_variables(self) -> None:
        """Test balance_row variables."""
        comp = balance_row()
        var_names = {v.name: v for v in comp.variables}
        assert "income_cell" in var_names
        assert "expense_cell" in var_names
        assert "label" in var_names
        assert var_names["income_cell"].required is True
        assert var_names["expense_cell"].required is True
        assert var_names["label"].default == "Net Balance"

    def test_balance_row_formula(self) -> None:
        """Test balance_row formula generation."""
        comp = balance_row()
        formula_cell = comp.rows[0].cells[1]
        assert formula_cell.formula == "=${income_cell}-${expense_cell}"
        assert formula_cell.type == "currency"
        assert formula_cell.style == "total_value"


# ============================================================================
# Category Components Tests
# ============================================================================


class TestCategoryRow:
    """Tests for category_row component."""

    def test_category_row_structure(self) -> None:
        """Test category_row structure."""
        comp = category_row()
        assert comp.name == "category_row"
        assert len(comp.variables) == 3
        assert len(comp.rows) == 1
        assert len(comp.rows[0].cells) == 4  # Category, budget, actual, variance

    def test_category_row_variables(self) -> None:
        """Test category_row variables."""
        comp = category_row()
        var_names = {v.name: v for v in comp.variables}
        assert "category" in var_names
        assert "budget" in var_names
        assert "actual" in var_names
        assert var_names["category"].required is True
        assert var_names["budget"].type == VariableType.CURRENCY
        assert var_names["actual"].type == VariableType.CURRENCY

    def test_category_row_formula(self) -> None:
        """Test category_row variance formula."""
        comp = category_row()
        variance_cell = comp.rows[0].cells[3]
        assert variance_cell.formula == "=${budget}-${actual}"
        assert variance_cell.style == "variance_cell"


class TestCategoryHeader:
    """Tests for category_header component."""

    def test_category_header_structure(self) -> None:
        """Test category_header structure."""
        comp = category_header()
        assert comp.name == "category_header"
        assert len(comp.variables) == 4
        assert len(comp.rows) == 1
        assert len(comp.rows[0].cells) == 4

    def test_category_header_defaults(self) -> None:
        """Test category_header default labels."""
        comp = category_header()
        var_defaults = {v.name: v.default for v in comp.variables}
        assert var_defaults["col1_label"] == "Category"
        assert var_defaults["col2_label"] == "Budget"
        assert var_defaults["col3_label"] == "Actual"
        assert var_defaults["col4_label"] == "Remaining"

    def test_category_header_cells(self) -> None:
        """Test category_header cell values."""
        comp = category_header()
        cells = comp.rows[0].cells
        assert cells[0].value == "${col1_label}"
        assert cells[1].value == "${col2_label}"
        assert cells[2].value == "${col3_label}"
        assert cells[3].value == "${col4_label}"
        assert all(cell.style == "header_cell" for cell in cells)


class TestCategoryTotal:
    """Tests for category_total component."""

    def test_category_total_structure(self) -> None:
        """Test category_total structure."""
        comp = category_total()
        assert comp.name == "category_total"
        assert len(comp.variables) == 4
        assert len(comp.rows) == 1
        assert len(comp.rows[0].cells) == 4

    def test_category_total_variables(self) -> None:
        """Test category_total variables."""
        comp = category_total()
        var_names = {v.name: v for v in comp.variables}
        assert "budget_range" in var_names
        assert "actual_range" in var_names
        assert "remaining_range" in var_names
        assert "label" in var_names
        assert var_names["budget_range"].required is True
        assert var_names["actual_range"].required is True
        assert var_names["remaining_range"].required is True
        assert var_names["label"].default == "Total"

    def test_category_total_formulas(self) -> None:
        """Test category_total SUM formulas."""
        comp = category_total()
        cells = comp.rows[0].cells
        assert cells[0].value == "${label}"
        assert cells[1].formula == "=SUM(${budget_range})"
        assert cells[2].formula == "=SUM(${actual_range})"
        assert cells[3].formula == "=SUM(${remaining_range})"
        assert all(cells[i].type == "currency" for i in [1, 2, 3])


# ============================================================================
# Transaction Components Tests
# ============================================================================


class TestTransactionHeader:
    """Tests for transaction_header component."""

    def test_transaction_header_structure(self) -> None:
        """Test transaction_header structure."""
        comp = transaction_header()
        assert comp.name == "transaction_header"
        assert len(comp.variables) == 0  # No variables
        assert len(comp.rows) == 1
        assert len(comp.rows[0].cells) == 4

    def test_transaction_header_labels(self) -> None:
        """Test transaction_header fixed labels."""
        comp = transaction_header()
        cells = comp.rows[0].cells
        assert cells[0].value == "Date"
        assert cells[1].value == "Description"
        assert cells[2].value == "Category"
        assert cells[3].value == "Amount"
        assert all(cell.style == "header_cell" for cell in cells)


class TestTransactionEntry:
    """Tests for transaction_entry component."""

    def test_transaction_entry_structure(self) -> None:
        """Test transaction_entry structure."""
        comp = transaction_entry()
        assert comp.name == "transaction_entry"
        assert len(comp.variables) == 4
        assert len(comp.rows) == 1
        assert len(comp.rows[0].cells) == 4

    def test_transaction_entry_variables(self) -> None:
        """Test transaction_entry variables."""
        comp = transaction_entry()
        var_names = {v.name: v for v in comp.variables}
        assert "date" in var_names
        assert "description" in var_names
        assert "category" in var_names
        assert "amount" in var_names
        assert var_names["date"].type == VariableType.DATE
        assert var_names["amount"].type == VariableType.CURRENCY
        assert var_names["amount"].default == 0

    def test_transaction_entry_cells(self) -> None:
        """Test transaction_entry cell configuration."""
        comp = transaction_entry()
        cells = comp.rows[0].cells
        assert cells[0].value == "${date}"
        assert cells[0].type == "date"
        assert cells[1].value == "${description}"
        assert cells[2].value == "${category}"
        assert cells[3].value == "${amount}"
        assert cells[3].type == "currency"


# ============================================================================
# ComponentLibrary Tests
# ============================================================================


class TestComponentLibrary:
    """Tests for ComponentLibrary class."""

    def test_library_initialization(self) -> None:
        """Test ComponentLibrary initializes with built-in components."""
        library = ComponentLibrary()
        components = library.list_components()
        assert len(components) > 0
        assert "document_header" in components
        assert "category_row" in components

    def test_library_get_component(self) -> None:
        """Test getting component by name."""
        library = ComponentLibrary()
        comp = library.get("document_header")
        assert comp is not None
        assert comp.name == "document_header"

    def test_library_get_nonexistent(self) -> None:
        """Test getting non-existent component returns None."""
        library = ComponentLibrary()
        comp = library.get("nonexistent_component")
        assert comp is None

    def test_library_register_custom(self) -> None:
        """Test registering custom component."""
        library = ComponentLibrary()
        custom = ComponentDefinition(
            name="custom_comp",
            description="Custom component",
            variables=[],
            rows=[],
        )
        library.register(custom)
        retrieved = library.get("custom_comp")
        assert retrieved is not None
        assert retrieved.name == "custom_comp"

    def test_library_list_components(self) -> None:
        """Test listing all components."""
        library = ComponentLibrary()
        names = library.list_components()
        assert isinstance(names, list)
        assert "document_header" in names
        assert "month_header" in names
        assert "income_summary" in names
        assert "expense_summary" in names
        assert "balance_row" in names
        assert "category_row" in names
        assert "category_header" in names
        assert "category_total" in names
        assert "transaction_header" in names
        assert "transaction_entry" in names

    def test_library_all_components(self) -> None:
        """Test getting all components dictionary."""
        library = ComponentLibrary()
        all_comps = library.all_components()
        assert isinstance(all_comps, dict)
        assert "document_header" in all_comps
        assert isinstance(all_comps["document_header"], ComponentDefinition)

    def test_library_all_components_copy(self) -> None:
        """Test all_components returns a copy."""
        library = ComponentLibrary()
        all_comps = library.all_components()
        all_comps["test"] = ComponentDefinition(
            name="test", description="test", variables=[], rows=[]
        )
        # Original library should not be modified
        assert library.get("test") is None

    def test_library_get_by_category(self) -> None:
        """Test getting components by category prefix."""
        library = ComponentLibrary()
        category_comps = library.get_by_category("category")
        assert len(category_comps) == 3  # category_row, category_header, category_total
        names = [c.name for c in category_comps]
        assert "category_row" in names
        assert "category_header" in names
        assert "category_total" in names

    def test_library_get_by_category_transaction(self) -> None:
        """Test getting transaction components."""
        library = ComponentLibrary()
        trans_comps = library.get_by_category("transaction")
        assert len(trans_comps) == 2  # transaction_header, transaction_entry
        names = [c.name for c in trans_comps]
        assert "transaction_header" in names
        assert "transaction_entry" in names

    def test_library_get_by_category_empty(self) -> None:
        """Test getting components with non-matching prefix."""
        library = ComponentLibrary()
        result = library.get_by_category("nonexistent")
        assert result == []


# ============================================================================
# Global Functions Tests
# ============================================================================


class TestGlobalFunctions:
    """Tests for global module-level functions."""

    def test_get_component_function(self) -> None:
        """Test get_component() module function."""
        comp = get_component("document_header")
        assert comp is not None
        assert comp.name == "document_header"

    def test_get_component_nonexistent(self) -> None:
        """Test get_component() with non-existent component."""
        comp = get_component("nonexistent")
        assert comp is None

    def test_list_components_function(self) -> None:
        """Test list_components() module function."""
        names = list_components()
        assert isinstance(names, list)
        assert len(names) >= 10  # At least 10 built-in components
        assert "document_header" in names

    def test_get_all_components_function(self) -> None:
        """Test get_all_components() module function."""
        all_comps = get_all_components()
        assert isinstance(all_comps, dict)
        assert "document_header" in all_comps
        assert "transaction_entry" in all_comps

    def test_global_library_instance(self) -> None:
        """Test COMPONENT_LIBRARY global instance."""
        assert COMPONENT_LIBRARY is not None
        assert isinstance(COMPONENT_LIBRARY, ComponentLibrary)
        # Should have built-in components
        assert len(COMPONENT_LIBRARY.list_components()) >= 10


# ============================================================================
# Integration Tests
# ============================================================================


class TestComponentIntegration:
    """Integration tests for component combinations."""

    def test_all_builtin_components_valid(self) -> None:
        """Test all built-in components are valid ComponentDefinitions."""
        all_comps = get_all_components()
        for name, comp in all_comps.items():
            assert isinstance(comp, ComponentDefinition)
            assert comp.name == name
            assert comp.description != ""
            assert isinstance(comp.variables, list)
            assert isinstance(comp.rows, list)

    def test_components_have_unique_names(self) -> None:
        """Test all components have unique names."""
        names = list_components()
        assert len(names) == len(set(names))

    def test_required_variables_marked(self) -> None:
        """Test required variables are properly marked."""
        # Balance row requires cell references
        balance = balance_row()
        required_vars = [v for v in balance.variables if v.required]
        assert len(required_vars) == 2
        var_names = [v.name for v in required_vars]
        assert "income_cell" in var_names
        assert "expense_cell" in var_names

    def test_currency_variables_typed(self) -> None:
        """Test currency variables are properly typed."""
        income = income_summary()
        income_var = next(v for v in income.variables if v.name == "income_total")
        assert income_var.type == VariableType.CURRENCY

    def test_date_variables_typed(self) -> None:
        """Test date variables are properly typed."""
        trans = transaction_entry()
        date_var = next(v for v in trans.variables if v.name == "date")
        assert date_var.type == VariableType.DATE
