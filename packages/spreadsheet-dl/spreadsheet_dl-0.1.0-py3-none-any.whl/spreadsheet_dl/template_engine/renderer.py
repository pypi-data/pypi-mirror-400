"""Template renderer for converting templates to spreadsheets.

Renders SpreadsheetTemplate objects with variable values
into actual spreadsheet content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from spreadsheet_dl.template_engine.schema import (
        CellTemplate,
        ConditionalBlock,
        RowTemplate,
        SheetTemplate,
        SpreadsheetTemplate,
    )


# Built-in variable functions
def month_name(month: int) -> str:
    """Get month name from number (1-12)."""
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    if 1 <= month <= 12:
        return months[month - 1]
    return str(month)


def month_abbrev(month: int) -> str:
    """Get abbreviated month name from number (1-12)."""
    abbrevs = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    if 1 <= month <= 12:
        return abbrevs[month - 1]
    return str(month)


def format_date(d: date | datetime, pattern: str = "%Y-%m-%d") -> str:
    """Format a date with given pattern."""
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime(pattern)


def format_currency(value: float | int, symbol: str = "$", decimals: int = 2) -> str:
    """Format a number as currency."""
    return f"{symbol}{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a number as percentage."""
    return f"{value * 100:.{decimals}f}%"


# Built-in functions registry
BUILTIN_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "month_name": month_name,
    "month_abbrev": month_abbrev,
    "format_date": format_date,
    "format_currency": format_currency,
    "format_percentage": format_percentage,
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "len": len,
    "sum": sum,
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
}


@dataclass
class RenderedCell:
    """A rendered cell ready for output.

    Contains the final values after variable substitution
    and conditional evaluation.
    """

    value: Any = None
    formula: str | None = None
    style: str | None = None
    type: str | None = None
    colspan: int = 1
    rowspan: int = 1


@dataclass
class RenderedRow:
    """A rendered row ready for output."""

    cells: list[RenderedCell] = field(default_factory=list)
    style: str | None = None
    height: str | None = None


@dataclass
class RenderedSheet:
    """A rendered sheet ready for output."""

    name: str
    columns: list[dict[str, Any]] = field(default_factory=list)
    rows: list[RenderedRow] = field(default_factory=list)
    freeze_rows: int = 0
    freeze_cols: int = 0
    protection: dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderedSpreadsheet:
    """A fully rendered spreadsheet ready for output."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    sheets: list[RenderedSheet] = field(default_factory=list)
    styles: dict[str, Any] = field(default_factory=dict)
    properties: dict[str, Any] = field(default_factory=dict)


class ExpressionEvaluator:
    """Evaluate expressions in template strings.

    Supports:
    - Simple variables: ${var_name}
    - Nested access: ${parent.child}
    - Function calls: ${month_name(month)}
    - Filters: ${value|default:0}
    - Arithmetic: ${a + b}
    """

    # Pattern for ${...} expressions
    EXPR_PATTERN = re.compile(r"\$\{([^}]+)\}")

    def __init__(
        self,
        variables: dict[str, Any],
        functions: dict[str, Callable[..., Any]] | None = None,
    ) -> None:
        """Initialize evaluator.

        Args:
            variables: Variable values for substitution
            functions: Custom functions (merged with built-ins)
        """
        self._variables = variables
        self._functions = {**BUILTIN_FUNCTIONS}
        if functions:
            self._functions.update(functions)

    def with_variables(self, additional: dict[str, Any]) -> ExpressionEvaluator:
        """Create new evaluator with additional variables merged.

        Args:
            additional: Additional variables to add

        Returns:
            New ExpressionEvaluator with merged variables
        """
        merged = {**self._variables, **additional}
        return ExpressionEvaluator(merged, self._functions)

    def evaluate(self, text: str | Any) -> Any:
        """Evaluate a template string.

        Args:
            text: Template string with ${...} expressions

        Returns:
            Evaluated result
        """
        if not isinstance(text, str):
            return text

        # Check if the entire string is a single expression
        if text.startswith("${") and text.endswith("}"):
            inner = text[2:-1]
            if "${" not in inner:
                return self._evaluate_expression(inner)

        # Replace all expressions in the string
        def replace_expr(match: re.Match[str]) -> str:
            result = self._evaluate_expression(match.group(1))
            return str(result) if result is not None else ""

        return self.EXPR_PATTERN.sub(replace_expr, text)

    def _evaluate_expression(self, expr: str) -> Any:
        """Evaluate a single expression.

        Args:
            expr: Expression without ${} wrapper

        Returns:
            Evaluated value
        """
        expr = expr.strip()

        # Handle filters: value|filter:arg
        if "|" in expr:
            return self._apply_filter(expr)

        # Handle function calls: func(args)
        if "(" in expr and expr.endswith(")"):
            return self._call_function(expr)

        # Handle arithmetic expressions
        if any(
            op in expr
            for op in [" + ", " - ", " * ", " / ", " > ", " < ", " == ", " != "]
        ):
            return self._evaluate_arithmetic(expr)

        # Simple variable lookup
        return self._get_variable(expr)

    def _get_variable(self, name: str) -> Any:
        """Get a variable value, supporting nested access.

        Args:
            name: Variable name (supports dot notation)

        Returns:
            Variable value or None
        """
        # Handle nested access
        parts = name.split(".")
        value: Any = self._variables

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

            if value is None:
                return None

        return value

    def _apply_filter(self, expr: str) -> Any:
        """Apply a filter to a value.

        Supports:
        - default:value - Use default if None
        - upper - Uppercase string
        - lower - Lowercase string
        - round:n - Round to n decimals

        Args:
            expr: Expression with filter

        Returns:
            Filtered value
        """
        parts = expr.split("|", 1)
        value = self._evaluate_expression(parts[0])
        filter_expr = parts[1].strip()

        # Parse filter name and argument
        if ":" in filter_expr:
            filter_name, filter_arg = filter_expr.split(":", 1)
            filter_arg = filter_arg.strip()
        else:
            filter_name = filter_expr
            filter_arg = None

        filter_name = filter_name.strip()

        # Apply filter
        if filter_name == "default":
            if value is None:
                # Try to evaluate filter_arg as expression first
                if filter_arg:
                    try:
                        result = self._evaluate_expression(filter_arg)
                        # If result is None (variable not found), use filter_arg as literal
                        if result is not None:
                            return result
                        # Use filter_arg as literal value
                        return filter_arg
                    except (ValueError, TypeError, KeyError, AttributeError):
                        return filter_arg
                return ""
            return value

        if filter_name == "upper" and isinstance(value, str):
            return value.upper()

        if filter_name == "lower" and isinstance(value, str):
            return value.lower()

        if filter_name == "title" and isinstance(value, str):
            return value.title()

        if filter_name == "round" and isinstance(value, (int, float)):
            decimals = int(filter_arg) if filter_arg else 0
            return round(value, decimals)

        if filter_name == "currency" and isinstance(value, (int, float)):
            symbol = filter_arg or "$"
            return format_currency(value, symbol)

        if filter_name == "percentage" and isinstance(value, (int, float)):
            decimals = int(filter_arg) if filter_arg else 1
            return format_percentage(value, decimals)

        return value

    def _call_function(self, expr: str) -> Any:
        """Call a template function.

        Args:
            expr: Function call expression

        Returns:
            Function result
        """
        # Parse function name and arguments
        paren_idx = expr.index("(")
        func_name = expr[:paren_idx].strip()
        args_str = expr[paren_idx + 1 : -1]

        if func_name not in self._functions:
            # Unknown function, return as-is
            return f"${{{expr}}}"

        func = self._functions[func_name]

        # Parse arguments
        args: list[Any] = []
        if args_str.strip():
            for arg in self._split_args(args_str):
                arg = arg.strip()
                # Try to evaluate as expression or variable
                if (arg.startswith('"') and arg.endswith('"')) or (
                    arg.startswith("'") and arg.endswith("'")
                ):
                    args.append(arg[1:-1])
                else:
                    # Try as variable or literal
                    var_value = self._get_variable(arg)
                    if var_value is not None:
                        args.append(var_value)
                    else:
                        # Try as literal
                        try:
                            args.append(int(arg))
                        except ValueError:
                            try:
                                args.append(float(arg))
                            except ValueError:
                                args.append(arg)

        try:
            return func(*args)
        except (TypeError, ValueError, KeyError, AttributeError):
            return None

    def _split_args(self, args_str: str) -> list[str]:
        """Split function arguments, respecting nested parens and quotes."""
        args = []
        current = ""
        depth = 0
        in_string = False
        string_char = ""

        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current += char
            elif char == string_char and in_string:
                in_string = False
                current += char
            elif char == "(" and not in_string:
                depth += 1
                current += char
            elif char == ")" and not in_string:
                depth -= 1
                current += char
            elif char == "," and depth == 0 and not in_string:
                args.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def _evaluate_arithmetic(self, expr: str) -> Any:
        """Evaluate simple arithmetic expressions.

        Args:
            expr: Arithmetic expression

        Returns:
            Result
        """
        # Replace variable references with values
        tokens = expr.split()
        resolved: list[str] = []

        for token in tokens:
            if token in (
                "+",
                "-",
                "*",
                "/",
                ">",
                "<",
                "==",
                "!=",
                ">=",
                "<=",
                "and",
                "or",
            ):
                resolved.append(token)
            else:
                value = self._get_variable(token)
                if value is not None:
                    resolved.append(repr(value))
                else:
                    # Try as literal
                    resolved.append(token)

        # Safe evaluation
        try:
            # Only allow safe operations
            expr_str = " ".join(resolved)
            # Use a restricted eval
            return eval(expr_str, {"__builtins__": {}}, {})
        except (ValueError, TypeError, SyntaxError, NameError, ZeroDivisionError):
            return None


class ConditionalEvaluator:
    """Evaluate conditional blocks in templates.

    Evaluates if/else conditions and returns appropriate content.
    """

    def __init__(self, evaluator: ExpressionEvaluator) -> None:
        """Initialize with expression evaluator.

        Args:
            evaluator: Expression evaluator for condition parsing
        """
        self._evaluator = evaluator

    def evaluate(self, condition: str) -> bool:
        """Evaluate a condition string.

        Args:
            condition: Condition expression

        Returns:
            Boolean result
        """
        # Handle special keywords
        condition = condition.strip()

        if condition.lower() == "true":
            return True
        if condition.lower() == "false":
            return False

        # Evaluate as expression
        result = self._evaluator._evaluate_expression(condition)

        # Convert to boolean
        return bool(result)

    def select_content(self, block: ConditionalBlock) -> list[Any]:
        """Select content based on condition.

        Args:
            block: Conditional block

        Returns:
            Selected content list
        """
        if self.evaluate(block.condition):
            return block.content
        return block.else_content


class TemplateRenderer:
    """Render templates to spreadsheet content.

    Examples:
        renderer = TemplateRenderer()
        result = renderer.render(template, {
            "month": 12,
            "year": 2024,
            "categories": ["Housing", "Utilities"],
        })
    """

    def __init__(
        self,
        custom_functions: dict[str, Callable[..., Any]] | None = None,
    ) -> None:
        """Initialize renderer.

        Args:
            custom_functions: Additional template functions
        """
        self._custom_functions = custom_functions or {}
        self._components: dict[str, Any] = {}

    def render(
        self,
        template: SpreadsheetTemplate,
        variables: dict[str, Any],
    ) -> RenderedSpreadsheet:
        """Render a template with variable values.

        Args:
            template: Template to render
            variables: Variable values

        Returns:
            Rendered spreadsheet

        Raises:
            ValueError: If required variables are missing
        """
        # Validate variables
        errors = template.validate_variables(variables)
        if errors:
            raise ValueError(f"Variable validation failed: {'; '.join(errors)}")

        # Get resolved variables with defaults
        resolved_vars = template.get_resolved_variables(variables)

        # Add built-in variables
        resolved_vars.update(self._get_builtin_variables())

        # Store template components for use during rendering
        self._components = template.components

        # Create evaluators
        expr_evaluator = ExpressionEvaluator(resolved_vars, self._custom_functions)
        cond_evaluator = ConditionalEvaluator(expr_evaluator)

        # Render sheets
        rendered_sheets: list[RenderedSheet] = []
        for sheet in template.sheets:
            rendered_sheet = self._render_sheet(
                sheet, template, expr_evaluator, cond_evaluator
            )
            rendered_sheets.append(rendered_sheet)

        return RenderedSpreadsheet(
            name=template.name,
            version=template.version,
            description=template.description,
            sheets=rendered_sheets,
            styles=template.styles,
            properties=template.properties,
        )

    def _get_builtin_variables(self) -> dict[str, Any]:
        """Get built-in template variables."""
        now = datetime.now()
        today = now.date()

        return {
            "current_date": today,
            "current_datetime": now,
            "current_year": today.year,
            "current_month": today.month,
            "current_month_name": month_name(today.month),
            "current_day": today.day,
        }

    def _render_sheet(
        self,
        sheet: SheetTemplate,
        template: SpreadsheetTemplate,
        expr_eval: ExpressionEvaluator,
        cond_eval: ConditionalEvaluator,
    ) -> RenderedSheet:
        """Render a single sheet template."""
        # Evaluate sheet name
        sheet_name = sheet.name
        if sheet.name_template:
            sheet_name = str(expr_eval.evaluate(sheet.name_template))

        # Render columns
        rendered_columns: list[dict[str, Any]] = []
        for col in sheet.columns:
            rendered_columns.append(
                {
                    "name": str(expr_eval.evaluate(col.name)),
                    "width": col.width,
                    "type": col.type,
                    "style": col.style,
                    "hidden": col.hidden,
                }
            )

        # Render rows
        rendered_rows: list[RenderedRow] = []

        # Render components first
        for component_ref in sheet.components:
            component_rows = self._render_component(
                component_ref, template, expr_eval, cond_eval
            )
            rendered_rows.extend(component_rows)

        # Header row
        if sheet.header_row:
            header_rows = self._render_row(sheet.header_row, expr_eval, cond_eval)
            rendered_rows.extend(header_rows)

        # Data rows (may repeat)
        if sheet.data_rows:
            data_rows = self._render_row(sheet.data_rows, expr_eval, cond_eval)
            rendered_rows.extend(data_rows)

        # Custom rows
        for row in sheet.custom_rows:
            custom_rows = self._render_row(row, expr_eval, cond_eval)
            rendered_rows.extend(custom_rows)

        # Total row
        if sheet.total_row:
            total_rows = self._render_row(sheet.total_row, expr_eval, cond_eval)
            rendered_rows.extend(total_rows)

        return RenderedSheet(
            name=sheet_name,
            columns=rendered_columns,
            rows=rendered_rows,
            freeze_rows=sheet.freeze_rows,
            freeze_cols=sheet.freeze_cols,
            protection=sheet.protection,
        )

    def _render_component(
        self,
        component_ref: str,
        template: SpreadsheetTemplate,
        expr_eval: ExpressionEvaluator,
        cond_eval: ConditionalEvaluator,
    ) -> list[RenderedRow]:
        """Render a component reference.

        Args:
            component_ref: Component name or name with variables (e.g., "header" or "header:title=Budget")
            template: Parent template containing component definitions
            expr_eval: Expression evaluator
            cond_eval: Conditional evaluator

        Returns:
            List of rendered rows from the component
        """
        # Parse component reference for inline variable assignments
        if ":" in component_ref:
            component_name, var_str = component_ref.split(":", 1)
            # Parse variable assignments like "var1=val1,var2=val2"
            inline_vars: dict[str, Any] = {}
            for assignment in var_str.split(","):
                if "=" in assignment:
                    key, value = assignment.split("=", 1)
                    inline_vars[key.strip()] = expr_eval.evaluate(value.strip())
        else:
            component_name = component_ref
            inline_vars = {}

        # Look up component definition
        component = template.components.get(component_name)
        if component is None:
            # Component not found, skip silently
            return []

        # Resolve component variables with defaults
        component_vars: dict[str, Any] = {}
        for var in component.variables:
            if var.name in inline_vars:
                component_vars[var.name] = inline_vars[var.name]
            elif var.default is not None:
                component_vars[var.name] = var.default
            elif var.required:
                raise ValueError(
                    f"Required component variable '{var.name}' not provided for component '{component_name}'"
                )

        # Create evaluator with component variables merged
        comp_expr_eval = expr_eval.with_variables(component_vars)
        comp_cond_eval = ConditionalEvaluator(comp_expr_eval)

        # Render component rows
        rendered_rows: list[RenderedRow] = []
        for row in component.rows:
            rows = self._render_row(row, comp_expr_eval, comp_cond_eval)
            rendered_rows.extend(rows)

        return rendered_rows

    def _render_row(
        self,
        row: RowTemplate,
        expr_eval: ExpressionEvaluator,
        cond_eval: ConditionalEvaluator,
    ) -> list[RenderedRow]:
        """Render a row template.

        May return multiple rows if repeat > 1 or conditional content.
        """
        rows: list[RenderedRow] = []

        # Check conditional
        if row.conditional:
            content = cond_eval.select_content(row.conditional)
            if not content:
                return rows

        # Repeat row
        repeat_count = row.repeat if row.repeat > 0 else 1

        for i in range(repeat_count):
            # Render cells
            rendered_cells: list[RenderedCell] = []
            for cell in row.cells:
                rendered_cell = self._render_cell(cell, expr_eval)
                rendered_cells.append(rendered_cell)

            # Determine style (alternate for even rows)
            style = row.style
            if i % 2 == 1 and row.alternate_style:
                style = row.alternate_style

            rows.append(
                RenderedRow(
                    cells=rendered_cells,
                    style=style,
                    height=row.height,
                )
            )

        return rows

    def _render_cell(
        self,
        cell: CellTemplate,
        expr_eval: ExpressionEvaluator,
    ) -> RenderedCell:
        """Render a single cell template."""
        # Evaluate value
        value = cell.value
        if value is not None:
            value = expr_eval.evaluate(value)

        # Evaluate formula
        formula = cell.formula
        if formula is not None:
            formula = str(expr_eval.evaluate(formula))

        return RenderedCell(
            value=value,
            formula=formula,
            style=cell.style,
            type=cell.type,
            colspan=cell.colspan,
            rowspan=cell.rowspan,
        )


def render_template(
    template: SpreadsheetTemplate,
    variables: dict[str, Any],
    custom_functions: dict[str, Callable[..., Any]] | None = None,
) -> RenderedSpreadsheet:
    """Render a template with variable values.

    Convenience function for simple usage.

    Args:
        template: Template to render
        variables: Variable values
        custom_functions: Optional custom functions

    Returns:
        Rendered spreadsheet

    Examples:
        result = render_template(template, {"month": 12, "year": 2024})
    """
    renderer = TemplateRenderer(custom_functions)
    return renderer.render(template, variables)
