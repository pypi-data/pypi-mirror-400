"""
Tests for template engine module.

Tests:
"""

import pytest

from spreadsheet_dl.template_engine import (
    CellTemplate,
    ColumnTemplate,
    ConditionalBlock,
    ConditionalEvaluator,
    ExpressionEvaluator,
    RenderedSpreadsheet,
    RowTemplate,
    SheetTemplate,
    SpreadsheetTemplate,
    TemplateVariable,
    VariableType,
    load_template_from_yaml,
    render_template,
)

pytestmark = [pytest.mark.unit, pytest.mark.templates]

# ============================================================================
# Schema Tests
# ============================================================================


class TestTemplateVariable:
    """Tests for TemplateVariable class."""

    def test_string_variable(self) -> None:
        """Test string variable creation."""
        var = TemplateVariable(name="title", type=VariableType.STRING)
        assert var.name == "title"
        assert var.type == VariableType.STRING
        assert not var.required

    def test_required_variable(self) -> None:
        """Test required variable validation."""
        var = TemplateVariable(
            name="month",
            type=VariableType.NUMBER,
            required=True,
        )
        assert var.required
        assert var.validate_value(12)
        assert not var.validate_value(None)

    def test_variable_with_default(self) -> None:
        """Test variable with default value."""
        var = TemplateVariable(
            name="year",
            type=VariableType.NUMBER,
            default=2024,
        )
        assert var.get_value() == 2024
        assert var.get_value(2025) == 2025

    def test_variable_choices(self) -> None:
        """Test variable with choices."""
        var = TemplateVariable(
            name="category",
            type=VariableType.STRING,
            choices=["Housing", "Utilities", "Groceries"],
        )
        assert var.validate_value("Housing")
        assert not var.validate_value("Unknown")


class TestCellTemplate:
    """Tests for CellTemplate class."""

    def test_simple_value(self) -> None:
        """Test cell with simple value."""
        cell = CellTemplate(value="Total")
        assert cell.value == "Total"
        assert cell.formula is None

    def test_formula_cell(self) -> None:
        """Test cell with formula."""
        cell = CellTemplate(
            formula="=SUM(B2:B${last_row})",
            style="total",
            type="currency",
        )
        assert cell.formula == "=SUM(B2:B${last_row})"
        assert cell.style == "total"
        assert cell.type == "currency"

    def test_cell_with_span(self) -> None:
        """Test cell with colspan and rowspan."""
        cell = CellTemplate(value="Title", colspan=3, rowspan=2)
        assert cell.colspan == 3
        assert cell.rowspan == 2


class TestRowTemplate:
    """Tests for RowTemplate class."""

    def test_simple_row(self) -> None:
        """Test simple row with cells."""
        row = RowTemplate(
            cells=[
                CellTemplate(value="Name"),
                CellTemplate(value="Amount"),
            ],
            style="header",
        )
        assert len(row.cells) == 2
        assert row.style == "header"

    def test_repeating_row(self) -> None:
        """Test row with repeat count."""
        row = RowTemplate(
            cells=[CellTemplate()],
            repeat=50,
            style="data",
            alternate_style="data_alt",
        )
        assert row.repeat == 50
        assert row.alternate_style == "data_alt"


class TestSheetTemplate:
    """Tests for SheetTemplate class."""

    def test_simple_sheet(self) -> None:
        """Test simple sheet template."""
        sheet = SheetTemplate(
            name="Budget",
            columns=[
                ColumnTemplate(name="Category", width="4cm"),
                ColumnTemplate(name="Amount", width="3cm", type="currency"),
            ],
            freeze_rows=1,
        )
        assert sheet.name == "Budget"
        assert len(sheet.columns) == 2
        assert sheet.freeze_rows == 1

    def test_sheet_with_name_template(self) -> None:
        """Test sheet with dynamic name template."""
        sheet = SheetTemplate(
            name="Budget",
            name_template="${month_name(month)} ${year}",
        )
        assert sheet.name_template == "${month_name(month)} ${year}"


class TestSpreadsheetTemplate:
    """Tests for SpreadsheetTemplate class."""

    def test_complete_template(self) -> None:
        """Test complete template definition."""
        template = SpreadsheetTemplate(
            name="monthly-budget",
            version="1.0.0",
            description="Monthly budget tracking",
            variables=[
                TemplateVariable("month", VariableType.NUMBER, required=True),
                TemplateVariable("year", VariableType.NUMBER, default=2024),
            ],
            sheets=[
                SheetTemplate(name="Budget"),
            ],
        )
        assert template.name == "monthly-budget"
        assert len(template.variables) == 2
        assert len(template.sheets) == 1

    def test_validate_variables(self) -> None:
        """Test variable validation."""
        template = SpreadsheetTemplate(
            name="test",
            variables=[
                TemplateVariable("month", VariableType.NUMBER, required=True),
            ],
        )
        errors = template.validate_variables({})
        assert len(errors) == 1
        assert "month" in errors[0]

        errors = template.validate_variables({"month": 12})
        assert len(errors) == 0

    def test_get_resolved_variables(self) -> None:
        """Test resolving variables with defaults."""
        template = SpreadsheetTemplate(
            name="test",
            variables=[
                TemplateVariable("year", VariableType.NUMBER, default=2024),
            ],
        )
        resolved = template.get_resolved_variables({})
        assert resolved["year"] == 2024


# ============================================================================
# Expression Evaluator Tests
# ============================================================================


class TestExpressionEvaluator:
    """Tests for ExpressionEvaluator class."""

    def test_simple_variable(self) -> None:
        """Test simple variable substitution."""
        evaluator = ExpressionEvaluator({"name": "John"})
        result = evaluator.evaluate("${name}")
        assert result == "John"

    def test_nested_variable(self) -> None:
        """Test nested variable access."""
        evaluator = ExpressionEvaluator({"user": {"name": "John", "age": 30}})
        result = evaluator.evaluate("${user.name}")
        assert result == "John"

    def test_string_interpolation(self) -> None:
        """Test variable interpolation in strings."""
        evaluator = ExpressionEvaluator({"month": "December", "year": 2024})
        result = evaluator.evaluate("Budget for ${month} ${year}")
        assert result == "Budget for December 2024"

    def test_function_call(self) -> None:
        """Test function call in expression."""
        evaluator = ExpressionEvaluator({"month": 12})
        result = evaluator.evaluate("${month_name(month)}")
        assert result == "December"

    def test_filter_default(self) -> None:
        """Test default filter."""
        evaluator = ExpressionEvaluator({"value": None})
        result = evaluator.evaluate("${value|default:0}")
        assert result == "0"

        evaluator = ExpressionEvaluator({"value": 42})
        result = evaluator.evaluate("${value|default:0}")
        assert result == 42

    def test_filter_upper(self) -> None:
        """Test upper filter."""
        evaluator = ExpressionEvaluator({"text": "hello"})
        result = evaluator.evaluate("${text|upper}")
        assert result == "HELLO"

    def test_filter_round(self) -> None:
        """Test round filter."""
        evaluator = ExpressionEvaluator({"value": 3.14159})
        result = evaluator.evaluate("${value|round:2}")
        assert result == 3.14

    def test_arithmetic(self) -> None:
        """Test arithmetic expressions."""
        evaluator = ExpressionEvaluator({"a": 10, "b": 5})
        result = evaluator.evaluate("${a + b}")
        assert result == 15

    def test_builtin_functions(self) -> None:
        """Test built-in functions."""
        evaluator = ExpressionEvaluator({"items": [1, 2, 3, 4, 5]})
        assert evaluator.evaluate("${sum(items)}") == 15
        assert evaluator.evaluate("${len(items)}") == 5
        assert evaluator.evaluate("${max(items)}") == 5


class TestBuiltinFunctions:
    """Tests for built-in template functions."""

    def test_month_name(self) -> None:
        """Test month_name function."""
        evaluator = ExpressionEvaluator({"month": 1})
        assert evaluator.evaluate("${month_name(month)}") == "January"

        evaluator = ExpressionEvaluator({"month": 12})
        assert evaluator.evaluate("${month_name(month)}") == "December"

    def test_month_abbrev(self) -> None:
        """Test month_abbrev function."""
        evaluator = ExpressionEvaluator({"month": 1})
        assert evaluator.evaluate("${month_abbrev(month)}") == "Jan"


# ============================================================================
# Conditional Evaluator Tests
# ============================================================================


class TestConditionalEvaluator:
    """Tests for ConditionalEvaluator class."""

    def test_true_condition(self) -> None:
        """Test evaluating true condition."""
        expr_eval = ExpressionEvaluator({})
        cond_eval = ConditionalEvaluator(expr_eval)
        assert cond_eval.evaluate("true") is True

    def test_false_condition(self) -> None:
        """Test evaluating false condition."""
        expr_eval = ExpressionEvaluator({})
        cond_eval = ConditionalEvaluator(expr_eval)
        assert cond_eval.evaluate("false") is False

    def test_variable_condition(self) -> None:
        """Test evaluating variable as condition."""
        expr_eval = ExpressionEvaluator({"show_summary": True})
        cond_eval = ConditionalEvaluator(expr_eval)
        assert cond_eval.evaluate("show_summary") is True

    def test_select_content(self) -> None:
        """Test selecting content based on condition."""
        expr_eval = ExpressionEvaluator({"include_totals": True})
        cond_eval = ConditionalEvaluator(expr_eval)

        block = ConditionalBlock(
            condition="include_totals",
            content=["total_row"],
            else_content=["no_totals"],
        )

        result = cond_eval.select_content(block)
        assert result == ["total_row"]

    def test_select_else_content(self) -> None:
        """Test selecting else content."""
        expr_eval = ExpressionEvaluator({"include_totals": False})
        cond_eval = ConditionalEvaluator(expr_eval)

        block = ConditionalBlock(
            condition="include_totals",
            content=["total_row"],
            else_content=["no_totals"],
        )

        result = cond_eval.select_content(block)
        assert result == ["no_totals"]


# ============================================================================
# Template Renderer Tests
# ============================================================================


class TestTemplateRenderer:
    """Tests for TemplateRenderer class."""

    def test_render_simple_template(self) -> None:
        """Test rendering a simple template."""
        template = SpreadsheetTemplate(
            name="test",
            variables=[
                TemplateVariable("title", VariableType.STRING, default="Budget"),
            ],
            sheets=[
                SheetTemplate(
                    name="Sheet1",
                    columns=[
                        ColumnTemplate(name="Category"),
                    ],
                    header_row=RowTemplate(
                        cells=[CellTemplate(value="${title}")],
                        style="header",
                    ),
                ),
            ],
        )

        result = render_template(template, {})
        assert isinstance(result, RenderedSpreadsheet)
        assert len(result.sheets) == 1
        assert result.sheets[0].rows[0].cells[0].value == "Budget"

    def test_render_with_variables(self) -> None:
        """Test rendering with variable substitution."""
        template = SpreadsheetTemplate(
            name="test",
            variables=[
                TemplateVariable("month", VariableType.NUMBER, required=True),
                TemplateVariable("year", VariableType.NUMBER, default=2024),
            ],
            sheets=[
                SheetTemplate(
                    name="Budget",
                    name_template="${month_name(month)} ${year}",
                ),
            ],
        )

        result = render_template(template, {"month": 12})
        assert result.sheets[0].name == "December 2024"

    def test_render_repeating_rows(self) -> None:
        """Test rendering rows with repeat."""
        template = SpreadsheetTemplate(
            name="test",
            sheets=[
                SheetTemplate(
                    name="Sheet1",
                    data_rows=RowTemplate(
                        cells=[CellTemplate()],
                        repeat=5,
                        style="data",
                        alternate_style="data_alt",
                    ),
                ),
            ],
        )

        result = render_template(template, {})
        assert len(result.sheets[0].rows) == 5
        # Check alternating styles
        assert result.sheets[0].rows[0].style == "data"
        assert result.sheets[0].rows[1].style == "data_alt"

    def test_render_builtin_variables(self) -> None:
        """Test that built-in variables are available."""
        template = SpreadsheetTemplate(
            name="test",
            sheets=[
                SheetTemplate(
                    name="Sheet1",
                    header_row=RowTemplate(
                        cells=[CellTemplate(value="${current_year}")],
                    ),
                ),
            ],
        )

        result = render_template(template, {})
        # Should have current year
        from datetime import date

        assert result.sheets[0].rows[0].cells[0].value == date.today().year


# ============================================================================
# Template Loader Tests
# ============================================================================


class TestTemplateLoader:
    """Tests for TemplateLoader class."""

    def test_load_from_string(self) -> None:
        """Test loading template from YAML string."""
        yaml_content = """
meta:
  name: "Test Template"
  version: "1.0.0"
  description: "A test template"

variables:
  - name: month
    type: number
    required: true

sheets:
  - name: Budget
    columns:
      - name: Category
        width: "4cm"
      - name: Amount
        width: "3cm"
        type: currency
"""
        template = load_template_from_yaml(yaml_content)
        assert template.name == "Test Template"
        assert template.version == "1.0.0"
        assert len(template.variables) == 1
        assert template.variables[0].name == "month"
        assert len(template.sheets) == 1
        assert len(template.sheets[0].columns) == 2

    def test_load_with_components(self) -> None:
        """Test loading template with component definitions."""
        yaml_content = """
meta:
  name: "Test"

components:
  header_block:
    description: "Standard header"
    rows:
      - cells:
          - value: "Header"
            style: header

sheets:
  - name: Main
    components:
      - header_block
"""
        template = load_template_from_yaml(yaml_content)
        assert "header_block" in template.components
        assert template.components["header_block"].description == "Standard header"
