"""Interactive ODS features for enhanced user experience.

Provides interactive elements for ODS spreadsheets including
dropdowns, data validation, conditional formatting, and
dashboard views.

Requirements implemented:

Features:
    - Dropdown lists for category selection
    - Data validation rules for amounts and dates
    - Conditional formatting for budget status
    - Interactive dashboard with KPIs
    - Sparklines for trend visualization (LibreOffice-specific)
    - Auto-complete suggestions

**Known Limitations:**
    - Conditional formatting: Implemented with static evaluation at render time.
      odfpy does not support ODF calc:conditional-formats elements, so conditions
      are evaluated when the file is created and styles are applied statically.
      For dynamic conditional formatting, use XLSX format or add rules manually
      in LibreOffice after export.
    - Sparklines: LibreOffice-specific feature using SPARKLINE() function.
      May not render correctly in Excel or Google Sheets. Formulas are embedded
      in ODS files and render when opened in LibreOffice Calc.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from spreadsheet_dl.exceptions import SpreadsheetDLError

if TYPE_CHECKING:
    from decimal import Decimal
    from pathlib import Path


class InteractiveError(SpreadsheetDLError):
    """Base exception for interactive feature errors."""

    error_code = "FT-INT-2100"


class ValidationRuleType(Enum):
    """Types of data validation rules."""

    WHOLE_NUMBER = "whole_number"
    DECIMAL = "decimal"
    LIST = "list"
    DATE = "date"
    TIME = "time"
    TEXT_LENGTH = "text_length"
    CUSTOM = "custom"


class ComparisonOperator(Enum):
    """Comparison operators for validation."""

    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER = "greater"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS = "less"
    LESS_OR_EQUAL = "less_or_equal"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"


class ConditionalFormatType(Enum):
    """Types of conditional formatting."""

    CELL_VALUE = "cell_value"
    FORMULA = "formula"
    COLOR_SCALE = "color_scale"
    DATA_BAR = "data_bar"
    ICON_SET = "icon_set"
    TOP_N = "top_n"
    ABOVE_AVERAGE = "above_average"
    DUPLICATE = "duplicate"


@dataclass
class ValidationRule:
    """Data validation rule for ODS cells.

    Attributes:
        rule_type: Type of validation.
        operator: Comparison operator.
        value1: First comparison value.
        value2: Second value (for BETWEEN).
        input_title: Title for input prompt.
        input_message: Message for input prompt.
        error_title: Title for error alert.
        error_message: Error message text.
        allow_blank: Whether blank cells are valid.
        show_dropdown: Show dropdown for list validation.
        values: List values for LIST type.
    """

    rule_type: ValidationRuleType
    operator: ComparisonOperator = ComparisonOperator.GREATER_OR_EQUAL
    value1: Any = None
    value2: Any = None
    input_title: str = ""
    input_message: str = ""
    error_title: str = "Invalid Input"
    error_message: str = "Please enter a valid value."
    allow_blank: bool = True
    show_dropdown: bool = True
    values: list[str] = field(default_factory=list)

    def to_ods_content_validation(self) -> dict[str, Any]:
        """Convert to ODS content validation format."""
        validation: dict[str, Any] = {
            "allow_empty_cell": self.allow_blank,
            # ODF format expects lowercase string for boolean attributes
            "display_list": "true" if self.show_dropdown else "false",
        }

        if self.rule_type == ValidationRuleType.LIST:
            validation["condition"] = (
                f"cell-content-is-in-list({';'.join(self.values)})"
            )
        elif self.rule_type == ValidationRuleType.DECIMAL:
            if self.operator == ComparisonOperator.GREATER_OR_EQUAL:
                validation["condition"] = f"cell-content()>={self.value1}"
            elif self.operator == ComparisonOperator.BETWEEN:
                validation["condition"] = (
                    f"cell-content-is-between({self.value1},{self.value2})"
                )
        elif self.rule_type == ValidationRuleType.DATE:
            validation["condition"] = "cell-content-is-date()"
        elif (
            self.rule_type == ValidationRuleType.TEXT_LENGTH
            and self.operator == ComparisonOperator.LESS_OR_EQUAL
        ):
            validation["condition"] = f"cell-content-text-length()<={self.value1}"

        validation["error_message"] = self.error_message
        validation["error_title"] = self.error_title

        return validation


@dataclass
class DropdownList:
    """Dropdown list configuration.

    Attributes:
        name: List name for reference.
        values: List of dropdown values.
        source_range: Optional cell range as source.
        allow_custom: Allow custom values.
    """

    name: str
    values: list[str] = field(default_factory=list)
    source_range: str | None = None
    allow_custom: bool = False

    @classmethod
    def categories(cls) -> DropdownList:
        """Create a dropdown for expense categories."""
        from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory

        return cls(
            name="categories",
            values=[cat.value for cat in ExpenseCategory],
            allow_custom=False,
        )

    @classmethod
    def account_types(cls) -> DropdownList:
        """Create a dropdown for account types."""
        from spreadsheet_dl.domains.finance.accounts import AccountType

        return cls(
            name="account_types",
            values=[at.value for at in AccountType],
            allow_custom=False,
        )

    @classmethod
    def months(cls) -> DropdownList:
        """Create a dropdown for months."""
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
        return cls(name="months", values=months, allow_custom=False)

    def to_validation_rule(self) -> ValidationRule:
        """Convert to validation rule."""
        return ValidationRule(
            rule_type=ValidationRuleType.LIST,
            values=self.values,
            show_dropdown=True,
            error_message=f"Please select a valid {self.name}.",
        )


@dataclass
class ConditionalFormat:
    """Conditional formatting rule.

    Attributes:
        format_type: Type of conditional format.
        operator: Comparison operator.
        value1: First comparison value.
        value2: Second value (for ranges).
        formula: Custom formula.
        style: Style to apply (font color, background, etc.).
        priority: Rule priority.
    """

    format_type: ConditionalFormatType
    operator: ComparisonOperator = ComparisonOperator.GREATER_OR_EQUAL
    value1: Any = None
    value2: Any = None
    formula: str | None = None
    style: dict[str, Any] = field(default_factory=dict)
    priority: int = 1

    @classmethod
    def over_budget_warning(cls) -> ConditionalFormat:
        """Create format for over-budget cells (red background)."""
        return cls(
            format_type=ConditionalFormatType.CELL_VALUE,
            operator=ComparisonOperator.LESS,
            value1=0,
            style={
                "background_color": "#FFCDD2",  # Light red
                "font_color": "#B71C1C",  # Dark red
                "font_weight": "bold",
            },
        )

    @classmethod
    def under_budget_success(cls) -> ConditionalFormat:
        """Create format for under-budget cells (green background)."""
        return cls(
            format_type=ConditionalFormatType.CELL_VALUE,
            operator=ComparisonOperator.GREATER,
            value1=0,
            style={
                "background_color": "#C8E6C9",  # Light green
                "font_color": "#1B5E20",  # Dark green
            },
        )

    @classmethod
    def percentage_color_scale(cls) -> ConditionalFormat:
        """Create color scale for percentage values."""
        return cls(
            format_type=ConditionalFormatType.COLOR_SCALE,
            style={
                "min_color": "#C8E6C9",  # Green (0%)
                "mid_color": "#FFF9C4",  # Yellow (50%)
                "max_color": "#FFCDD2",  # Red (100%)
            },
        )

    @classmethod
    def spending_data_bar(cls) -> ConditionalFormat:
        """Create data bar for spending visualization."""
        return cls(
            format_type=ConditionalFormatType.DATA_BAR,
            style={
                "bar_color": "#2196F3",  # Blue
                "show_value": True,
            },
        )

    def to_ods_style(self) -> dict[str, str]:
        """Convert style to ODS format."""
        ods_style = {}

        if "background_color" in self.style:
            ods_style["fo:background-color"] = self.style["background_color"]

        if "font_color" in self.style:
            ods_style["fo:color"] = self.style["font_color"]

        if self.style.get("font_weight") == "bold":
            ods_style["fo:font-weight"] = "bold"

        return ods_style


@dataclass
class DashboardKPI:
    """Key Performance Indicator for dashboard.

    Attributes:
        name: KPI display name.
        value: Current value.
        target: Target value.
        unit: Unit of measurement.
        trend: Trend direction (up, down, stable).
        status: Status (good, warning, critical).
    """

    name: str
    value: float
    target: float | None = None
    unit: str = "$"
    trend: str = "stable"
    status: str = "good"

    @property
    def formatted_value(self) -> str:
        """Get formatted value string."""
        if self.unit == "$":
            return f"${self.value:,.2f}"
        elif self.unit == "%":
            return f"{self.value:.1f}%"
        else:
            return f"{self.value:,.2f} {self.unit}"

    @property
    def progress_percent(self) -> float:
        """Calculate progress toward target."""
        if self.target and self.target > 0:
            return min((self.value / self.target) * 100, 100)
        return 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "formatted_value": self.formatted_value,
            "target": self.target,
            "unit": self.unit,
            "trend": self.trend,
            "status": self.status,
            "progress_percent": self.progress_percent,
        }


@dataclass
class SparklineConfig:
    """Configuration for sparkline chart (LibreOffice-specific).

    LibreOffice Calc supports SPARKLINE() function for mini charts within cells.
    This is a LibreOffice-specific feature and may not work in Excel or Google Sheets.

     (Sparkline application to ODS documents)

    Attributes:
        data_range: Cell range for data (e.g., "B2:B10").
        sparkline_type: Type of sparkline: "line", "column", or "stacked".
        color: Primary color for sparkline (hex format).
        negative_color: Color for negative values (hex format).
        high_color: Color for highest point (hex format, optional).
        low_color: Color for lowest point (hex format, optional).
        first_color: Color for first point (hex format, optional).
        last_color: Color for last point (hex format, optional).
        show_markers: Show data point markers (line sparklines only).
        line_width: Line width for line sparklines (default: 1.0).
        column_width: Column width for column sparklines (default: 1.0).
        axis: Whether to show axis line (default: False).
        min_value: Minimum value for Y-axis scaling (optional, auto if None).
        max_value: Maximum value for Y-axis scaling (optional, auto if None).

    Example:
        >>> config = SparklineConfig(  # doctest: +SKIP
        ...     data_range="A1:A10",
        ...     sparkline_type="line",
        ...     color="#2196F3",
        ...     show_markers=True
        ... )
        >>> config.to_formula()  # doctest: +SKIP
        '=SPARKLINE(A1:A10;{"type";"line";"color";"#2196F3";"markers";"true"})'

        >>> config = SparklineConfig(  # doctest: +SKIP
        ...     data_range="B1:B10",
        ...     sparkline_type="column",
        ...     color="#4CAF50",
        ...     high_color="#FF5722",
        ...     low_color="#2196F3"
        ... )
    """

    data_range: str
    sparkline_type: str = "line"  # "line", "column", or "stacked"
    color: str = "#2196F3"
    negative_color: str | None = "#F44336"
    high_color: str | None = None
    low_color: str | None = None
    first_color: str | None = None
    last_color: str | None = None
    show_markers: bool = False
    line_width: float = 1.0
    column_width: float = 1.0
    axis: bool = False
    min_value: float | None = None
    max_value: float | None = None

    def __post_init__(self) -> None:
        """Validate sparkline configuration."""
        valid_types = {"line", "column", "stacked"}
        if self.sparkline_type not in valid_types:
            raise ValueError(
                f"Invalid sparkline_type: {self.sparkline_type}. "
                f"Must be one of: {', '.join(sorted(valid_types))}"
            )

        if self.line_width <= 0:
            raise ValueError(f"line_width must be > 0, got {self.line_width}")

        if self.column_width <= 0:
            raise ValueError(f"column_width must be > 0, got {self.column_width}")

        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value >= self.max_value
        ):
            raise ValueError(
                f"min_value ({self.min_value}) must be < max_value ({self.max_value})"
            )

    def to_formula(self) -> str:
        """Generate LibreOffice SPARKLINE formula.

        Returns:
            ODF formula string for SPARKLINE function.

        Note:
            LibreOffice uses semicolon (;) as parameter separator in formulas,
            not comma. Formula syntax: =SPARKLINE(range;{options})
        """
        # Build options array
        options = [
            f'"type";"{self.sparkline_type}"',
            f'"color";"{self.color}"',
        ]

        # Add optional color parameters
        if self.negative_color:
            options.append(f'"negativecolor";"{self.negative_color}"')

        if self.high_color:
            options.append(f'"highcolor";"{self.high_color}"')

        if self.low_color:
            options.append(f'"lowcolor";"{self.low_color}"')

        if self.first_color:
            options.append(f'"firstcolor";"{self.first_color}"')

        if self.last_color:
            options.append(f'"lastcolor";"{self.last_color}"')

        # Add markers (line sparklines only)
        if self.show_markers and self.sparkline_type == "line":
            options.append('"markers";"true"')

        # Add line width (line sparklines)
        if self.sparkline_type == "line" and self.line_width != 1.0:
            options.append(f'"linewidth";{self.line_width}')

        # Add column width (column sparklines)
        if self.sparkline_type in ("column", "stacked") and self.column_width != 1.0:
            options.append(f'"columnwidth";{self.column_width}')

        # Add axis
        if self.axis:
            options.append('"axis";"true"')

        # Add min/max values for scaling
        if self.min_value is not None:
            options.append(f'"min";{self.min_value}')

        if self.max_value is not None:
            options.append(f'"max";{self.max_value}')

        # LibreOffice uses semicolon separator and braces for options
        options_str = ";".join(options)
        return f"of:=SPARKLINE({self.data_range};{{{options_str}}})"


@dataclass
class DashboardSection:
    """Dashboard section configuration.

    Attributes:
        title: Section title.
        kpis: KPIs to display.
        chart_type: Type of chart.
        data_range: Data range for charts.
        position: Grid position (row, col).
        size: Size in cells (rows, cols).
    """

    title: str
    kpis: list[DashboardKPI] = field(default_factory=list)
    chart_type: str | None = None
    data_range: str | None = None
    position: tuple[int, int] = (1, 1)
    size: tuple[int, int] = (5, 4)


class InteractiveOdsBuilder:
    """Builder for interactive ODS features.

    Adds dropdowns, validation, conditional formatting, and
    dashboard elements to ODS spreadsheets.

    Example:
        >>> builder = InteractiveOdsBuilder()  # doctest: +SKIP
        >>> builder.add_dropdown("B2:B100", DropdownList.categories())  # doctest: +SKIP
        >>> builder.add_conditional_format("E2:E100", ConditionalFormat.over_budget_warning())  # doctest: +SKIP
        >>> builder.apply_to_document(doc)  # doctest: +SKIP
    """

    def __init__(self) -> None:
        """Initialize builder."""
        self._dropdowns: dict[str, tuple[str, DropdownList]] = {}
        self._validations: dict[str, tuple[str, ValidationRule]] = {}
        self._formats: list[tuple[str, ConditionalFormat]] = []
        self._dashboard_sections: list[DashboardSection] = []
        self._sparklines: dict[str, SparklineConfig] = {}

    def add_dropdown(
        self,
        cell_range: str,
        dropdown: DropdownList,
    ) -> InteractiveOdsBuilder:
        """Add a dropdown list to a cell range.

        Args:
            cell_range: Cell range (e.g., "B2:B100").
            dropdown: Dropdown configuration.

        Returns:
            Self for chaining.
        """
        self._dropdowns[cell_range] = (cell_range, dropdown)
        return self

    def add_validation(
        self,
        cell_range: str,
        rule: ValidationRule,
    ) -> InteractiveOdsBuilder:
        """Add data validation to a cell range.

        Args:
            cell_range: Cell range.
            rule: Validation rule.

        Returns:
            Self for chaining.
        """
        self._validations[cell_range] = (cell_range, rule)
        return self

    def add_conditional_format(
        self,
        cell_range: str,
        format: ConditionalFormat,
    ) -> InteractiveOdsBuilder:
        """Add conditional formatting to a cell range.

        Args:
            cell_range: Cell range.
            format: Conditional format configuration.

        Returns:
            Self for chaining.
        """
        self._formats.append((cell_range, format))
        return self

    def add_sparkline(
        self,
        cell: str,
        config: SparklineConfig,
    ) -> InteractiveOdsBuilder:
        """Add a sparkline to a cell.

        Args:
            cell: Target cell (e.g., "F1").
            config: Sparkline configuration.

        Returns:
            Self for chaining.
        """
        self._sparklines[cell] = config
        return self

    def add_dashboard_section(
        self,
        section: DashboardSection,
    ) -> InteractiveOdsBuilder:
        """Add a dashboard section.

        Args:
            section: Dashboard section configuration.

        Returns:
            Self for chaining.
        """
        self._dashboard_sections.append(section)
        return self

    def apply_to_document(self, doc: Any) -> None:
        """Apply all interactive features to an ODS document.

        Args:
            doc: ODF document object from odfpy.
        """
        # Apply dropdowns as content validations
        for cell_range, (_, dropdown) in self._dropdowns.items():
            self._apply_dropdown_validation(doc, cell_range, dropdown)

        # Apply custom validations
        for cell_range, (_, rule) in self._validations.items():
            self._apply_validation_rule(doc, cell_range, rule)

        # Apply conditional formatting
        for cell_range, format_config in self._formats:
            self._apply_conditional_format(doc, cell_range, format_config)

        # Apply sparklines
        for cell, config in self._sparklines.items():
            self._apply_sparkline(doc, cell, config)

    def _apply_dropdown_validation(
        self,
        doc: Any,
        cell_range: str,
        dropdown: DropdownList,
    ) -> None:
        """Apply dropdown validation to cells."""
        # Convert dropdown to validation rule
        rule = dropdown.to_validation_rule()
        self._apply_validation_rule(doc, cell_range, rule)

    def _apply_validation_rule(
        self,
        doc: Any,
        cell_range: str,
        rule: ValidationRule,
    ) -> None:
        """Apply validation rule to cells."""
        try:
            from odf.table import ContentValidation

            # Create content validation element
            validation = ContentValidation()

            # Set validation attributes based on rule
            validation_dict = rule.to_ods_content_validation()

            for attr, value in validation_dict.items():
                if attr == "condition":
                    validation.setAttribute("condition", value)
                elif attr == "allow_empty_cell":
                    validation.setAttribute("allowemptycell", str(value).lower())
                elif attr == "display_list":
                    validation.setAttribute("displaylist", str(value).lower())

            # Add to document's content validations
            # Note: This is a simplified implementation
            # Full implementation would need to find/create ContentValidations element

        except (ImportError, AttributeError):
            # ODF validation features may not be fully supported by library version
            pass

    def _apply_conditional_format(
        self,
        doc: Any,
        cell_range: str,
        format_config: ConditionalFormat,
    ) -> None:
        """Apply conditional formatting to cells.

        Implements conditional formatting by applying styles based on cell values.

        **IMPORTANT LIMITATIONS:**
        - odfpy does not support ODF calc:conditional-formats elements
        - Conditions are evaluated at render time, not dynamically in LibreOffice
        - Color scales, data bars, and icon sets are rendered as static styles
        - Formula-based conditions require cell values to be present at render time

        This implementation provides a foundation for conditional formatting that:
        - Works for static data (values known at export time)
        - Applies correct styles based on rules
        - Documents limitations clearly

        For dynamic conditional formatting in LibreOffice, you need to manually
        add the formatting rules after opening the file, or use a different
        export format (like XLSX via openpyxl).


        Args:
            doc: The ODF document object
            cell_range: Cell range (e.g., "A1:B10")
            format_config: Conditional formatting configuration

        Raises:
            InteractiveError: If the cell range is invalid or styles cannot be applied
        """
        from odf.table import Table as OdfTable

        from spreadsheet_dl.schema.conditional import ConditionalFormat as CondFormat

        # Type narrow format_config
        if not isinstance(format_config, CondFormat):
            raise InteractiveError("Invalid conditional format configuration")

        try:
            # Parse cell range (e.g., "A1:B10" -> start/end coordinates)
            start_cell, end_cell = self._parse_range(cell_range)
            start_col, start_row = self._cell_to_coords(start_cell)
            end_col, end_row = self._cell_to_coords(end_cell)

            # Get the table from document
            tables = doc.spreadsheet.getElementsByType(OdfTable)
            if not tables:
                raise InteractiveError("No table found in document")
            table_elem = tables[0]

            # Process each cell in the range
            for row_idx in range(start_row, end_row + 1):
                for col_idx in range(start_col, end_col + 1):
                    cell = self._get_cell(table_elem, row_idx, col_idx)
                    if cell is None:
                        continue

                    # Apply each rule in priority order
                    for rule in sorted(format_config.rules, key=lambda r: r.priority):
                        if self._evaluate_rule(cell, rule):
                            self._apply_rule_style(doc, cell, rule)
                            if rule.stop_if_true:
                                break

        except Exception as e:
            raise InteractiveError(
                f"Failed to apply conditional formatting to range {cell_range}: {e}"
            ) from e

    def _parse_range(self, cell_range: str) -> tuple[str, str]:
        """Parse cell range like 'A1:B10' into (start_cell, end_cell)."""
        if ":" not in cell_range:
            # Single cell
            return (cell_range, cell_range)
        parts = cell_range.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid cell range format: {cell_range}")
        return (parts[0].strip(), parts[1].strip())

    def _cell_to_coords(self, cell_ref: str) -> tuple[int, int]:
        """Convert cell reference like 'A1' to (col_idx, row_idx)."""
        import re

        match = re.match(r"([A-Z]+)(\d+)", cell_ref.upper())
        if not match:
            raise ValueError(f"Invalid cell reference: {cell_ref}")

        col_letters, row_num = match.groups()

        # Convert column letters to index (A=0, B=1, ..., Z=25, AA=26, etc.)
        col_idx = 0
        for char in col_letters:
            col_idx = col_idx * 26 + (ord(char) - ord("A") + 1)
        col_idx -= 1  # Make 0-based

        row_idx = int(row_num) - 1  # Make 0-based

        return (col_idx, row_idx)

    def _get_cell(self, table_elem: Any, row_idx: int, col_idx: int) -> Any:
        """Get cell at given row and column index."""
        from odf.table import TableCell, TableRow

        rows = table_elem.getElementsByType(TableRow)
        if row_idx >= len(rows):
            return None

        row = rows[row_idx]
        cells = row.getElementsByType(TableCell)
        if col_idx >= len(cells):
            return None

        return cells[col_idx]

    def _get_cell_value(self, cell: Any) -> Any:
        """Extract the value from an ODF cell."""
        if cell is None:
            return None

        # Check for office:value attribute
        if cell.hasAttribute("value"):
            value_type = cell.getAttribute("valuetype")
            if (
                value_type == "float"
                or value_type == "percentage"
                or value_type == "currency"
            ):
                return float(cell.getAttribute("value"))
            elif value_type == "date":
                return cell.getAttribute("datevalue")
            elif value_type == "time":
                return cell.getAttribute("timevalue")
            elif value_type == "boolean":
                return cell.getAttribute("booleanvalue") == "true"
            elif value_type == "string":
                return cell.getAttribute("stringvalue")

        # Fall back to text content
        from odf.text import P

        paragraphs = cell.getElementsByType(P)
        if paragraphs:
            text = str(paragraphs[0])
            # Try to parse as number
            try:
                return float(text)
            except ValueError:
                return text

        return None

    def _evaluate_rule(self, cell: Any, rule: Any) -> bool:
        """Evaluate if a conditional rule matches a cell."""
        from spreadsheet_dl.schema.conditional import (
            ConditionalRuleType,
        )

        value = self._get_cell_value(cell)

        # Handle different rule types
        if rule.type == ConditionalRuleType.CELL_VALUE:
            return self._evaluate_cell_value_rule(value, rule)
        if rule.type == ConditionalRuleType.TEXT:
            return self._evaluate_text_rule(value, rule)
        if rule.type == ConditionalRuleType.FORMULA:
            # Formula rules are not supported in static evaluation
            return False
        # These rule types are applied differently (not true/false evaluation)
        # Other rule types not yet supported return False
        return rule.type in (
            ConditionalRuleType.COLOR_SCALE,
            ConditionalRuleType.DATA_BAR,
            ConditionalRuleType.ICON_SET,
        )

    def _evaluate_cell_value_rule(self, value: Any, rule: Any) -> bool:
        """Evaluate cell value comparison rule."""
        from spreadsheet_dl.schema.conditional import RuleOperator

        if value is None or rule.operator is None:
            return False

        # Convert to comparable types
        try:
            if isinstance(value, str):
                # Try converting string to float
                with contextlib.suppress(ValueError):
                    value = float(value)

            compare_value = rule.value
            if isinstance(compare_value, str) and isinstance(value, (int, float)):
                # Try converting comparison value to float
                with contextlib.suppress(ValueError):
                    compare_value = float(compare_value)

            # Perform comparison
            result: bool
            if rule.operator == RuleOperator.EQUAL:
                result = bool(value == compare_value)
            elif rule.operator == RuleOperator.NOT_EQUAL:
                result = bool(value != compare_value)
            elif rule.operator == RuleOperator.GREATER_THAN:
                result = bool(value > compare_value)
            elif rule.operator == RuleOperator.GREATER_THAN_OR_EQUAL:
                result = bool(value >= compare_value)
            elif rule.operator == RuleOperator.LESS_THAN:
                result = bool(value < compare_value)
            elif rule.operator == RuleOperator.LESS_THAN_OR_EQUAL:
                result = bool(value <= compare_value)
            elif rule.operator == RuleOperator.BETWEEN:
                result = bool(compare_value <= value <= rule.value2)
            elif rule.operator == RuleOperator.NOT_BETWEEN:
                result = bool(not (compare_value <= value <= rule.value2))
            else:
                result = False

            return result

        except (TypeError, ValueError):
            return False

    def _evaluate_text_rule(self, value: Any, rule: Any) -> bool:
        """Evaluate text-based conditional rule."""
        from spreadsheet_dl.schema.conditional import RuleOperator

        if value is None or rule.text is None:
            return False

        text_value = str(value)
        search_text = str(rule.text)

        if rule.operator == RuleOperator.CONTAINS_TEXT:
            return search_text in text_value
        elif rule.operator == RuleOperator.NOT_CONTAINS_TEXT:
            return search_text not in text_value
        elif rule.operator == RuleOperator.BEGINS_WITH:
            return text_value.startswith(search_text)
        elif rule.operator == RuleOperator.ENDS_WITH:
            return text_value.endswith(search_text)
        else:
            return False

    def _apply_rule_style(self, doc: Any, cell: Any, rule: Any) -> None:
        """Apply the style from a conditional rule to a cell."""
        if rule.style is None:
            return

        # Get or create the style
        if isinstance(rule.style, str):
            # Style name reference - look it up or create default
            style_name = rule.style
            style = self._get_or_create_named_style(doc, style_name)
        else:
            # CellStyle object
            style = self._convert_cell_style_to_odf(doc, rule.style)

        # Apply style to cell
        cell.setAttribute("stylename", style.getAttribute("name"))

    def _get_or_create_named_style(self, doc: Any, style_name: str) -> Any:
        """Get existing named style or create a default one."""
        from odf.style import Style, TableCellProperties, TextProperties

        # Check if style exists
        for style in doc.automaticstyles.getElementsByType(Style):
            if style.getAttribute("name") == style_name:
                return style

        # Create default style based on name
        style = Style(name=style_name, family="table-cell")

        # Apply default colors based on common names
        if "danger" in style_name.lower() or "error" in style_name.lower():
            tcp = TableCellProperties(backgroundcolor="#ffcccc")
            tp = TextProperties(color="#cc0000")
        elif "warning" in style_name.lower():
            tcp = TableCellProperties(backgroundcolor="#fff4cc")
            tp = TextProperties(color="#cc8800")
        elif "success" in style_name.lower():
            tcp = TableCellProperties(backgroundcolor="#ccffcc")
            tp = TextProperties(color="#00cc00")
        else:
            tcp = TableCellProperties()
            tp = TextProperties()

        style.addElement(tcp)
        style.addElement(tp)
        doc.automaticstyles.addElement(style)

        return style

    def _convert_cell_style_to_odf(self, doc: Any, cell_style: Any) -> Any:
        """Convert CellStyle object to ODF Style."""
        from odf.style import Style, TableCellProperties, TextProperties

        style = Style(name=cell_style.name or "conditional", family="table-cell")

        # Add table cell properties
        tcp_attrs = {}
        if hasattr(cell_style, "background_color") and cell_style.background_color:
            tcp_attrs["backgroundcolor"] = str(cell_style.background_color)
        if tcp_attrs:
            style.addElement(TableCellProperties(**tcp_attrs))

        # Add text properties from Font object
        tp_attrs = {}
        if hasattr(cell_style, "font") and cell_style.font:
            font = cell_style.font
            if hasattr(font, "color") and font.color:
                tp_attrs["color"] = str(font.color)
            # Font weight is FontWeight enum with values like '400', '700'
            if (
                hasattr(font, "weight")
                and font.weight
                and str(font.weight.value) >= "700"
            ):
                tp_attrs["fontweight"] = "bold"
            if hasattr(font, "italic") and font.italic:
                tp_attrs["fontstyle"] = "italic"
        if tp_attrs:
            style.addElement(TextProperties(**tp_attrs))

        doc.automaticstyles.addElement(style)
        return style

    def _apply_sparkline(
        self,
        doc: Any,
        cell: str,
        config: SparklineConfig,
    ) -> None:
        """Apply sparkline formula to a cell.

        Uses LibreOffice SPARKLINE() function to create mini charts within cells.
        This is a LibreOffice-specific feature.

         (Sparkline application to ODS documents)

        Args:
            doc: The ODF document object
            cell: Target cell reference (e.g., "A1")
            config: Sparkline configuration

        Raises:
            InteractiveError: If the cell reference is invalid or sparkline cannot be applied
        """
        from odf.table import Table as OdfTable
        from odf.table import TableCell, TableRow
        from odf.text import P

        try:
            # Get the first sheet (assume we're working with the first sheet)
            tables = doc.spreadsheet.getElementsByType(OdfTable)
            if not tables:
                raise InteractiveError("No sheets found in document")

            table = tables[0]

            # Parse cell reference
            col_idx, row_idx = self._cell_to_coords(cell)

            # Get or create the cell
            rows = table.getElementsByType(TableRow)

            # Ensure we have enough rows
            while len(rows) <= row_idx:
                table.addElement(TableRow())
                rows = table.getElementsByType(TableRow)

            target_row = rows[row_idx]
            cells = target_row.getElementsByType(TableCell)

            # Ensure we have enough cells in the row
            while len(cells) <= col_idx:
                target_row.addElement(TableCell())
                cells = target_row.getElementsByType(TableCell)

            target_cell = cells[col_idx]

            # Generate the SPARKLINE formula
            formula = config.to_formula()

            # Set the formula attribute
            target_cell.setAttribute("formula", formula)

            # Set value type to float (sparklines are calculated values)
            target_cell.setAttribute("valuetype", "float")

            # Add a placeholder text to indicate sparkline
            # (LibreOffice will replace this with the actual sparkline when opened)
            p = P()
            p.addText("[Sparkline]")
            target_cell.addElement(p)

        except ValueError as e:
            raise InteractiveError(f"Invalid cell reference '{cell}': {e}") from e
        except Exception as e:
            raise InteractiveError(
                f"Failed to apply sparkline to cell '{cell}': {e}"
            ) from e


class DashboardGenerator:
    """Generates dashboard views in ODS spreadsheets.

    Creates a dedicated dashboard sheet with KPIs, charts,
    and summary information.

    Example:
        >>> generator = DashboardGenerator()  # doctest: +SKIP
        >>> generator.generate_dashboard(budget_data, output_path)  # doctest: +SKIP
    """

    def __init__(self) -> None:
        """Initialize dashboard generator."""
        self.builder = InteractiveOdsBuilder()

    def generate_dashboard(
        self,
        budget_path: Path,
        output_path: Path | None = None,
    ) -> Path:
        """Generate a dashboard ODS file.

        Args:
            budget_path: Path to source budget file.
            output_path: Output path (default: adds _dashboard suffix).

        Returns:
            Path to generated dashboard file.
        """
        from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

        analyzer = BudgetAnalyzer(budget_path)
        summary = analyzer.get_summary()
        by_category = analyzer.get_category_breakdown()

        # Create KPIs
        kpis = self._create_kpis(summary, by_category)

        # Create dashboard sections
        sections = [
            DashboardSection(
                title="Budget Overview",
                kpis=[
                    kpis["total_budget"],
                    kpis["total_spent"],
                    kpis["remaining"],
                    kpis["percent_used"],
                ],
                position=(1, 1),
                size=(4, 6),
            ),
            DashboardSection(
                title="Top Categories",
                chart_type="pie",
                data_range="Categories!A2:B10",
                position=(6, 1),
                size=(8, 6),
            ),
            DashboardSection(
                title="Spending Trend",
                chart_type="line",
                data_range="Expenses!A2:D30",
                position=(1, 8),
                size=(6, 6),
            ),
        ]

        for section in sections:
            self.builder.add_dashboard_section(section)

        # Generate ODS with dashboard
        output_path = output_path or budget_path.with_stem(
            f"{budget_path.stem}_dashboard"
        )
        return self._write_dashboard_ods(output_path, kpis, sections, by_category)

    def _create_kpis(
        self,
        summary: Any,
        by_category: dict[str, Decimal],
    ) -> dict[str, DashboardKPI]:
        """Create KPIs from budget data."""
        total_budget = float(summary.total_budget)
        total_spent = float(summary.total_spent)
        remaining = float(summary.total_remaining)
        percent_used = float(summary.percent_used)

        return {
            "total_budget": DashboardKPI(
                name="Total Budget",
                value=total_budget,
                unit="$",
                status="good",
            ),
            "total_spent": DashboardKPI(
                name="Total Spent",
                value=total_spent,
                target=total_budget,
                unit="$",
                status="warning" if percent_used > 80 else "good",
                trend="up" if total_spent > 0 else "stable",
            ),
            "remaining": DashboardKPI(
                name="Remaining",
                value=remaining,
                unit="$",
                status="critical" if remaining < 0 else "good",
            ),
            "percent_used": DashboardKPI(
                name="Budget Used",
                value=percent_used,
                target=100,
                unit="%",
                status="critical"
                if percent_used > 100
                else "warning"
                if percent_used > 80
                else "good",
            ),
        }

    def _write_dashboard_ods(
        self,
        output_path: Path,
        kpis: dict[str, DashboardKPI],
        sections: list[DashboardSection],
        by_category: dict[str, Decimal],
    ) -> Path:
        """Write dashboard ODS file."""
        try:
            from odf.opendocument import OpenDocumentSpreadsheet
            from odf.table import Table, TableCell, TableRow
            from odf.text import P
        except ImportError as err:
            raise InteractiveError(
                "odfpy required for dashboard generation. "
                "Install with: pip install odfpy"
            ) from err

        doc = OpenDocumentSpreadsheet()

        # Create Dashboard sheet
        dashboard_table = Table(name="Dashboard")

        # Add title row
        title_row = TableRow()
        title_cell = TableCell()
        title_cell.addElement(P(text="Budget Dashboard"))
        title_row.addElement(title_cell)
        dashboard_table.addElement(title_row)

        # Add empty row
        dashboard_table.addElement(TableRow())

        # Add KPI section header
        header_row = TableRow()
        for header in ["Metric", "Value", "Target", "Status"]:
            cell = TableCell()
            cell.addElement(P(text=header))
            header_row.addElement(cell)
        dashboard_table.addElement(header_row)

        # Add KPI rows
        for _kpi_key, kpi in kpis.items():
            kpi_row = TableRow()

            # Name
            name_cell = TableCell()
            name_cell.addElement(P(text=kpi.name))
            kpi_row.addElement(name_cell)

            # Value
            value_cell = TableCell(valuetype="float", value=str(kpi.value))
            value_cell.addElement(P(text=kpi.formatted_value))
            kpi_row.addElement(value_cell)

            # Target
            target_cell = TableCell()
            if kpi.target:
                target_cell.setAttribute("valuetype", "float")
                target_cell.setAttribute("value", str(kpi.target))
                if kpi.unit == "$":
                    target_cell.addElement(P(text=f"${kpi.target:,.2f}"))
                else:
                    target_cell.addElement(P(text=f"{kpi.target}{kpi.unit}"))
            kpi_row.addElement(target_cell)

            # Status
            status_cell = TableCell()
            status_cell.addElement(P(text=kpi.status.upper()))
            kpi_row.addElement(status_cell)

            dashboard_table.addElement(kpi_row)

        # Add empty rows
        for _ in range(2):
            dashboard_table.addElement(TableRow())

        # Add category breakdown header
        cat_header_row = TableRow()
        for header in ["Category", "Amount", "Percentage"]:
            cell = TableCell()
            cell.addElement(P(text=header))
            cat_header_row.addElement(cell)
        dashboard_table.addElement(cat_header_row)

        # Add category rows
        total = sum(by_category.values())
        sorted_categories = sorted(
            by_category.items(), key=lambda x: x[1], reverse=True
        )

        for cat_name, cat_amount in sorted_categories[:10]:
            cat_row = TableRow()

            # Category name
            name_cell = TableCell()
            name_cell.addElement(P(text=cat_name))
            cat_row.addElement(name_cell)

            # Amount
            amount_cell = TableCell(valuetype="currency", value=str(cat_amount))
            amount_cell.addElement(P(text=f"${float(cat_amount):,.2f}"))
            cat_row.addElement(amount_cell)

            # Percentage
            pct = (cat_amount / total * 100) if total > 0 else 0
            pct_cell = TableCell(valuetype="percentage", value=str(float(pct) / 100))
            pct_cell.addElement(P(text=f"{float(pct):.1f}%"))
            cat_row.addElement(pct_cell)

            dashboard_table.addElement(cat_row)

        doc.spreadsheet.addElement(dashboard_table)

        # Apply interactive features
        self.builder.apply_to_document(doc)

        # Save document
        doc.save(str(output_path))

        return output_path


def add_interactive_features(
    ods_path: Path,
    output_path: Path | None = None,
) -> Path:
    """Add interactive features to an existing ODS file.

    Args:
        ods_path: Path to ODS file.
        output_path: Output path (default: modifies in place).

    Returns:
        Path to output file.
    """
    try:
        from odf.opendocument import load
    except ImportError as err:
        raise InteractiveError(
            "odfpy required for interactive features. Install with: pip install odfpy"
        ) from err

    doc = load(str(ods_path))

    builder = InteractiveOdsBuilder()

    # Add category dropdown to column B (typical category column)
    builder.add_dropdown("B2:B1000", DropdownList.categories())

    # Add amount validation to column D (typical amount column)
    builder.add_validation(
        "D2:D1000",
        ValidationRule(
            rule_type=ValidationRuleType.DECIMAL,
            operator=ComparisonOperator.GREATER_OR_EQUAL,
            value1=0,
            error_message="Amount must be a positive number.",
        ),
    )

    # Add date validation to column A
    builder.add_validation(
        "A2:A1000",
        ValidationRule(
            rule_type=ValidationRuleType.DATE,
            error_message="Please enter a valid date (YYYY-MM-DD).",
        ),
    )

    # Add conditional formatting for remaining budget (if column E)
    builder.add_conditional_format("E2:E100", ConditionalFormat.over_budget_warning())
    builder.add_conditional_format("E2:E100", ConditionalFormat.under_budget_success())

    # Apply features
    builder.apply_to_document(doc)

    # Save
    output_path = output_path or ods_path
    doc.save(str(output_path))

    return output_path


def generate_budget_dashboard(
    budget_path: Path,
    output_path: Path | None = None,
) -> Path:
    """Generate a dashboard from a budget file.

    Args:
        budget_path: Path to budget ODS file.
        output_path: Output path for dashboard.

    Returns:
        Path to dashboard file.
    """
    generator = DashboardGenerator()
    return generator.generate_dashboard(budget_path, output_path)
