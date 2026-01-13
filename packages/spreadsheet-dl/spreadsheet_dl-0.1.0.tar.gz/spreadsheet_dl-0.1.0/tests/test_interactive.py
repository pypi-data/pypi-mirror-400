"""
Tests for interactive ODS features module.

Tests:
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from spreadsheet_dl.interactive import (
    ComparisonOperator,
    ConditionalFormat,
    ConditionalFormatType,
    DashboardGenerator,
    DashboardKPI,
    DashboardSection,
    DropdownList,
    InteractiveOdsBuilder,
    SparklineConfig,
    ValidationRule,
    ValidationRuleType,
)

pytestmark = [pytest.mark.integration, pytest.mark.cli]


class TestValidationRule:
    """Tests for ValidationRule."""

    def test_list_validation(self) -> None:
        """Test list validation rule."""
        rule = ValidationRule(
            rule_type=ValidationRuleType.LIST,
            values=["Option A", "Option B", "Option C"],
            show_dropdown=True,
        )

        content = rule.to_ods_content_validation()

        assert "cell-content-is-in-list" in content["condition"]
        assert content["display_list"] == "true"

    def test_decimal_validation(self) -> None:
        """Test decimal validation rule."""
        rule = ValidationRule(
            rule_type=ValidationRuleType.DECIMAL,
            operator=ComparisonOperator.GREATER_OR_EQUAL,
            value1=0,
            error_message="Amount must be positive",
        )

        content = rule.to_ods_content_validation()

        assert "cell-content()>=0" in content["condition"]
        assert content["error_message"] == "Amount must be positive"

    def test_between_validation(self) -> None:
        """Test between validation rule."""
        rule = ValidationRule(
            rule_type=ValidationRuleType.DECIMAL,
            operator=ComparisonOperator.BETWEEN,
            value1=0,
            value2=100,
        )

        content = rule.to_ods_content_validation()

        assert "is-between" in content["condition"]
        assert "0" in content["condition"]
        assert "100" in content["condition"]

    def test_date_validation(self) -> None:
        """Test date validation rule."""
        rule = ValidationRule(
            rule_type=ValidationRuleType.DATE,
            error_message="Please enter a valid date",
        )

        content = rule.to_ods_content_validation()

        assert "is-date" in content["condition"]

    def test_text_length_validation(self) -> None:
        """Test text length validation."""
        rule = ValidationRule(
            rule_type=ValidationRuleType.TEXT_LENGTH,
            operator=ComparisonOperator.LESS_OR_EQUAL,
            value1=100,
        )

        content = rule.to_ods_content_validation()

        assert "text-length" in content["condition"]


class TestDropdownList:
    """Tests for DropdownList."""

    def test_categories_dropdown(self) -> None:
        """Test categories dropdown factory."""
        dropdown = DropdownList.categories()

        assert dropdown.name == "categories"
        assert len(dropdown.values) > 0
        assert "Groceries" in dropdown.values or any(
            "groceries" in v.lower() for v in dropdown.values
        )

    def test_account_types_dropdown(self) -> None:
        """Test account types dropdown factory."""
        dropdown = DropdownList.account_types()

        assert dropdown.name == "account_types"
        assert len(dropdown.values) > 0

    def test_months_dropdown(self) -> None:
        """Test months dropdown factory."""
        dropdown = DropdownList.months()

        assert dropdown.name == "months"
        assert len(dropdown.values) == 12
        assert "January" in dropdown.values
        assert "December" in dropdown.values

    def test_to_validation_rule(self) -> None:
        """Test conversion to validation rule."""
        dropdown = DropdownList(
            name="test",
            values=["A", "B", "C"],
        )

        rule = dropdown.to_validation_rule()

        assert rule.rule_type == ValidationRuleType.LIST
        assert rule.values == ["A", "B", "C"]
        assert rule.show_dropdown is True


class TestConditionalFormat:
    """Tests for ConditionalFormat."""

    def test_over_budget_warning(self) -> None:
        """Test over budget warning format."""
        fmt = ConditionalFormat.over_budget_warning()

        assert fmt.format_type == ConditionalFormatType.CELL_VALUE
        assert fmt.operator == ComparisonOperator.LESS
        assert fmt.value1 == 0
        assert "background_color" in fmt.style
        assert "font_color" in fmt.style

    def test_under_budget_success(self) -> None:
        """Test under budget success format."""
        fmt = ConditionalFormat.under_budget_success()

        assert fmt.format_type == ConditionalFormatType.CELL_VALUE
        assert fmt.operator == ComparisonOperator.GREATER
        assert fmt.value1 == 0

    def test_percentage_color_scale(self) -> None:
        """Test percentage color scale."""
        fmt = ConditionalFormat.percentage_color_scale()

        assert fmt.format_type == ConditionalFormatType.COLOR_SCALE
        assert "min_color" in fmt.style
        assert "mid_color" in fmt.style
        assert "max_color" in fmt.style

    def test_spending_data_bar(self) -> None:
        """Test spending data bar."""
        fmt = ConditionalFormat.spending_data_bar()

        assert fmt.format_type == ConditionalFormatType.DATA_BAR
        assert "bar_color" in fmt.style

    def test_to_ods_style(self) -> None:
        """Test ODS style conversion."""
        fmt = ConditionalFormat(
            format_type=ConditionalFormatType.CELL_VALUE,
            style={
                "background_color": "#FF0000",
                "font_color": "#FFFFFF",
                "font_weight": "bold",
            },
        )

        ods_style = fmt.to_ods_style()

        assert ods_style.get("fo:background-color") == "#FF0000"
        assert ods_style.get("fo:color") == "#FFFFFF"
        assert ods_style.get("fo:font-weight") == "bold"


class TestDashboardKPI:
    """Tests for DashboardKPI."""

    def test_currency_format(self) -> None:
        """Test currency formatting."""
        kpi = DashboardKPI(
            name="Total Budget",
            value=1500.50,
            unit="$",
        )

        assert kpi.formatted_value == "$1,500.50"

    def test_percentage_format(self) -> None:
        """Test percentage formatting."""
        kpi = DashboardKPI(
            name="Budget Used",
            value=75.5,
            unit="%",
        )

        assert kpi.formatted_value == "75.5%"

    def test_progress_percent(self) -> None:
        """Test progress calculation."""
        kpi = DashboardKPI(
            name="Test",
            value=750,
            target=1000,
        )

        assert kpi.progress_percent == 75.0

    def test_progress_percent_exceeded(self) -> None:
        """Test progress when target exceeded."""
        kpi = DashboardKPI(
            name="Test",
            value=1200,
            target=1000,
        )

        # Should cap at 100
        assert kpi.progress_percent == 100.0

    def test_to_dict(self) -> None:
        """Test KPI serialization."""
        kpi = DashboardKPI(
            name="Total Spent",
            value=1500.00,
            target=2000.00,
            unit="$",
            trend="up",
            status="warning",
        )

        data = kpi.to_dict()

        assert data["name"] == "Total Spent"
        assert data["value"] == 1500.00
        assert data["target"] == 2000.00
        assert data["trend"] == "up"
        assert data["status"] == "warning"
        assert data["progress_percent"] == 75.0


class TestSparklineConfig:
    """Tests for SparklineConfig."""

    def test_to_formula_line_basic(self) -> None:
        """Test basic line sparkline formula."""
        config = SparklineConfig(
            data_range="A1:A10",
            sparkline_type="line",
            color="#2196F3",
        )

        formula = config.to_formula()

        assert formula.startswith("of:=SPARKLINE(")
        assert "A1:A10" in formula
        assert '"type";"line"' in formula
        assert '"color";"#2196F3"' in formula
        assert ";" in formula  # LibreOffice uses semicolons

    def test_to_formula_column(self) -> None:
        """Test column sparkline formula."""
        config = SparklineConfig(
            data_range="B1:B10",
            sparkline_type="column",
            color="#4CAF50",
            negative_color="#F44336",
        )

        formula = config.to_formula()

        assert '"type";"column"' in formula
        assert '"negativecolor";"#F44336"' in formula

    def test_to_formula_stacked(self) -> None:
        """Test stacked sparkline formula."""
        config = SparklineConfig(
            data_range="C1:C10",
            sparkline_type="stacked",
        )

        formula = config.to_formula()

        assert '"type";"stacked"' in formula

    def test_to_formula_with_markers(self) -> None:
        """Test line sparkline with markers."""
        config = SparklineConfig(
            data_range="C1:C10",
            sparkline_type="line",
            show_markers=True,
        )

        formula = config.to_formula()

        assert '"markers";"true"' in formula

    def test_markers_ignored_for_column(self) -> None:
        """Test that markers are ignored for column sparklines."""
        config = SparklineConfig(
            data_range="D1:D10",
            sparkline_type="column",
            show_markers=True,
        )

        formula = config.to_formula()

        # Markers should not appear for column type
        assert '"markers"' not in formula

    def test_to_formula_with_high_low_colors(self) -> None:
        """Test sparkline with high/low point colors."""
        config = SparklineConfig(
            data_range="E1:E10",
            sparkline_type="line",
            high_color="#FF5722",
            low_color="#2196F3",
        )

        formula = config.to_formula()

        assert '"highcolor";"#FF5722"' in formula
        assert '"lowcolor";"#2196F3"' in formula

    def test_to_formula_with_first_last_colors(self) -> None:
        """Test sparkline with first/last point colors."""
        config = SparklineConfig(
            data_range="F1:F10",
            sparkline_type="line",
            first_color="#9C27B0",
            last_color="#FF9800",
        )

        formula = config.to_formula()

        assert '"firstcolor";"#9C27B0"' in formula
        assert '"lastcolor";"#FF9800"' in formula

    def test_to_formula_with_line_width(self) -> None:
        """Test line sparkline with custom width."""
        config = SparklineConfig(
            data_range="G1:G10",
            sparkline_type="line",
            line_width=2.5,
        )

        formula = config.to_formula()

        assert '"linewidth";2.5' in formula

    def test_line_width_default_not_included(self) -> None:
        """Test that default line width is not included in formula."""
        config = SparklineConfig(
            data_range="H1:H10",
            sparkline_type="line",
            line_width=1.0,  # Default value
        )

        formula = config.to_formula()

        assert '"linewidth"' not in formula

    def test_to_formula_with_column_width(self) -> None:
        """Test column sparkline with custom width."""
        config = SparklineConfig(
            data_range="I1:I10",
            sparkline_type="column",
            column_width=0.8,
        )

        formula = config.to_formula()

        assert '"columnwidth";0.8' in formula

    def test_to_formula_with_axis(self) -> None:
        """Test sparkline with axis line."""
        config = SparklineConfig(
            data_range="J1:J10",
            sparkline_type="line",
            axis=True,
        )

        formula = config.to_formula()

        assert '"axis";"true"' in formula

    def test_to_formula_with_min_max(self) -> None:
        """Test sparkline with min/max value scaling."""
        config = SparklineConfig(
            data_range="K1:K10",
            sparkline_type="line",
            min_value=0.0,
            max_value=100.0,
        )

        formula = config.to_formula()

        assert '"min";0.0' in formula
        assert '"max";100.0' in formula

    def test_to_formula_comprehensive(self) -> None:
        """Test sparkline with all options."""
        config = SparklineConfig(
            data_range="L1:L10",
            sparkline_type="line",
            color="#2196F3",
            negative_color="#F44336",
            high_color="#FF5722",
            low_color="#00BCD4",
            first_color="#9C27B0",
            last_color="#FF9800",
            show_markers=True,
            line_width=1.5,
            axis=True,
            min_value=-10.0,
            max_value=10.0,
        )

        formula = config.to_formula()

        # Verify all options are present
        assert '"type";"line"' in formula
        assert '"color";"#2196F3"' in formula
        assert '"negativecolor";"#F44336"' in formula
        assert '"highcolor";"#FF5722"' in formula
        assert '"lowcolor";"#00BCD4"' in formula
        assert '"firstcolor";"#9C27B0"' in formula
        assert '"lastcolor";"#FF9800"' in formula
        assert '"markers";"true"' in formula
        assert '"linewidth";1.5' in formula
        assert '"axis";"true"' in formula
        assert '"min";-10.0' in formula
        assert '"max";10.0' in formula

    def test_invalid_sparkline_type(self) -> None:
        """Test that invalid sparkline type raises error."""
        with pytest.raises(ValueError, match="Invalid sparkline_type"):
            SparklineConfig(data_range="A1:A10", sparkline_type="invalid")

    def test_invalid_line_width(self) -> None:
        """Test that invalid line width raises error."""
        with pytest.raises(ValueError, match="line_width must be > 0"):
            SparklineConfig(data_range="A1:A10", line_width=0.0)

        with pytest.raises(ValueError, match="line_width must be > 0"):
            SparklineConfig(data_range="A1:A10", line_width=-1.0)

    def test_invalid_column_width(self) -> None:
        """Test that invalid column width raises error."""
        with pytest.raises(ValueError, match="column_width must be > 0"):
            SparklineConfig(data_range="A1:A10", column_width=0.0)

    def test_invalid_min_max_values(self) -> None:
        """Test that invalid min/max values raise error."""
        with pytest.raises(ValueError, match=r"min_value.*must be < max_value"):
            SparklineConfig(data_range="A1:A10", min_value=10.0, max_value=5.0)

        with pytest.raises(ValueError, match=r"min_value.*must be < max_value"):
            SparklineConfig(data_range="A1:A10", min_value=5.0, max_value=5.0)

    def test_none_negative_color(self) -> None:
        """Test sparkline with no negative color."""
        config = SparklineConfig(
            data_range="M1:M10",
            sparkline_type="line",
            negative_color=None,
        )

        formula = config.to_formula()

        assert '"negativecolor"' not in formula

    def test_data_range_with_sheet(self) -> None:
        """Test sparkline with sheet-qualified data range."""
        config = SparklineConfig(
            data_range="Sheet1.$A$1:$A$10",
            sparkline_type="line",
        )

        formula = config.to_formula()

        assert "Sheet1.$A$1:$A$10" in formula


class TestInteractiveOdsBuilder:
    """Tests for InteractiveOdsBuilder."""

    @pytest.fixture
    def builder(self) -> InteractiveOdsBuilder:
        """Create a test builder."""
        return InteractiveOdsBuilder()

    def test_add_dropdown(self, builder: InteractiveOdsBuilder) -> None:
        """Test adding dropdown."""
        dropdown = DropdownList.categories()
        builder.add_dropdown("B2:B100", dropdown)

        assert "B2:B100" in builder._dropdowns
        assert builder._dropdowns["B2:B100"][1] == dropdown

    def test_add_validation(self, builder: InteractiveOdsBuilder) -> None:
        """Test adding validation."""
        rule = ValidationRule(
            rule_type=ValidationRuleType.DECIMAL,
            operator=ComparisonOperator.GREATER_OR_EQUAL,
            value1=0,
        )
        builder.add_validation("D2:D100", rule)

        assert "D2:D100" in builder._validations

    def test_add_conditional_format(self, builder: InteractiveOdsBuilder) -> None:
        """Test adding conditional format."""
        fmt = ConditionalFormat.over_budget_warning()
        builder.add_conditional_format("E2:E100", fmt)

        assert len(builder._formats) == 1
        assert builder._formats[0][0] == "E2:E100"

    def test_add_sparkline(self, builder: InteractiveOdsBuilder) -> None:
        """Test adding sparkline."""
        config = SparklineConfig(data_range="A1:A10")
        builder.add_sparkline("F1", config)

        assert "F1" in builder._sparklines

    def test_add_dashboard_section(self, builder: InteractiveOdsBuilder) -> None:
        """Test adding dashboard section."""
        section = DashboardSection(
            title="Test Section",
            kpis=[DashboardKPI(name="Test", value=100)],
        )
        builder.add_dashboard_section(section)

        assert len(builder._dashboard_sections) == 1

    def test_chaining(self, builder: InteractiveOdsBuilder) -> None:
        """Test method chaining."""
        result = builder.add_dropdown(
            "B2:B100", DropdownList.categories()
        ).add_conditional_format("E2:E100", ConditionalFormat.over_budget_warning())

        assert result is builder

    def test_apply_sparkline_to_document(self, builder: InteractiveOdsBuilder) -> None:
        """Test applying sparkline to ODS document."""
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

        # Create a minimal ODS document
        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        doc.spreadsheet.addElement(table)

        # Add some data rows
        for i in range(15):
            row = TableRow()
            for j in range(5):
                cell = TableCell()
                p = P()
                p.addText(str(i * 5 + j))
                cell.addElement(p)
                row.addElement(cell)
            table.addElement(row)

        # Add sparkline to cell F1
        config = SparklineConfig(data_range="A1:A10", sparkline_type="line")
        builder._apply_sparkline(doc, "F1", config)

        # Verify the cell has the formula
        rows = table.getElementsByType(TableRow)
        cells = rows[0].getElementsByType(TableCell)
        target_cell = cells[5]  # F is column 5 (0-indexed)

        formula = target_cell.getAttribute("formula")
        assert formula is not None
        assert "SPARKLINE" in formula
        assert "A1:A10" in formula

    def test_apply_sparkline_creates_cell(self, builder: InteractiveOdsBuilder) -> None:
        """Test that sparkline application creates cell if missing."""
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableCell, TableRow

        # Create minimal document with one row
        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        row = TableRow()
        cell = TableCell()
        row.addElement(cell)
        table.addElement(row)
        doc.spreadsheet.addElement(table)

        # Apply sparkline to cell beyond existing cells
        config = SparklineConfig(data_range="B1:B10")
        builder._apply_sparkline(doc, "E2", config)

        # Verify cell was created
        rows = table.getElementsByType(TableRow)
        assert len(rows) >= 2

    def test_apply_sparkline_with_all_options(
        self, builder: InteractiveOdsBuilder
    ) -> None:
        """Test sparkline with comprehensive options."""
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        doc.spreadsheet.addElement(table)

        # Add row with cell
        row = TableRow()
        cell = TableCell()
        p = P()
        p.addText("Placeholder")
        cell.addElement(p)
        row.addElement(cell)
        table.addElement(row)

        # Create comprehensive sparkline config
        config = SparklineConfig(
            data_range="A1:A10",
            sparkline_type="line",
            color="#2196F3",
            negative_color="#F44336",
            high_color="#FF5722",
            low_color="#00BCD4",
            show_markers=True,
            line_width=2.0,
            axis=True,
        )

        builder._apply_sparkline(doc, "A1", config)

        # Verify formula contains all options
        rows = table.getElementsByType(TableRow)
        cells = rows[0].getElementsByType(TableCell)
        target_cell = cells[0]

        formula = target_cell.getAttribute("formula")
        assert '"type";"line"' in formula
        assert '"color";"#2196F3"' in formula
        assert '"highcolor";"#FF5722"' in formula
        assert '"lowcolor";"#00BCD4"' in formula
        assert '"markers";"true"' in formula

    def test_apply_sparkline_invalid_cell(self, builder: InteractiveOdsBuilder) -> None:
        """Test that invalid cell reference raises error."""
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table

        from spreadsheet_dl.interactive import InteractiveError

        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        doc.spreadsheet.addElement(table)

        config = SparklineConfig(data_range="A1:A10")

        with pytest.raises(InteractiveError, match="Invalid cell reference"):
            builder._apply_sparkline(doc, "INVALID", config)

    def test_apply_multiple_sparklines(self, builder: InteractiveOdsBuilder) -> None:
        """Test applying multiple sparklines to different cells."""
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableCell, TableRow

        doc = OpenDocumentSpreadsheet()
        table = Table(name="Sheet1")
        doc.spreadsheet.addElement(table)

        # Add multiple rows
        for _ in range(5):
            row = TableRow()
            for _ in range(10):
                row.addElement(TableCell())
            table.addElement(row)

        # Add different sparklines
        configs = [
            ("A1", SparklineConfig(data_range="B1:B10", sparkline_type="line")),
            ("A2", SparklineConfig(data_range="B1:B10", sparkline_type="column")),
            ("A3", SparklineConfig(data_range="B1:B10", sparkline_type="stacked")),
        ]

        for cell, config in configs:
            builder._apply_sparkline(doc, cell, config)

        # Verify each sparkline
        rows = table.getElementsByType(TableRow)
        for idx, (_, config) in enumerate(configs):
            cells = rows[idx].getElementsByType(TableCell)
            target_cell = cells[0]
            formula = target_cell.getAttribute("formula")
            assert "SPARKLINE" in formula
            assert f'"type";"{config.sparkline_type}"' in formula


class TestDashboardGenerator:
    """Tests for DashboardGenerator."""

    @pytest.fixture
    def generator(self) -> DashboardGenerator:
        """Create a test generator."""
        return DashboardGenerator()

    def test_create_kpis(self, generator: DashboardGenerator) -> None:
        """Test KPI creation from budget data."""
        mock_summary = MagicMock()
        mock_summary.total_budget = Decimal("2000.00")
        mock_summary.total_spent = Decimal("1500.00")
        mock_summary.total_remaining = Decimal("500.00")
        mock_summary.percent_used = 75.0

        by_category = {"Groceries": Decimal("500"), "Transport": Decimal("300")}

        kpis = generator._create_kpis(mock_summary, by_category)

        assert "total_budget" in kpis
        assert "total_spent" in kpis
        assert "remaining" in kpis
        assert "percent_used" in kpis

        assert kpis["total_budget"].value == 2000.00
        assert kpis["total_spent"].value == 1500.00
        assert kpis["remaining"].value == 500.00
        assert kpis["percent_used"].value == 75.0

    def test_kpi_status_warning(self, generator: DashboardGenerator) -> None:
        """Test KPI warning status."""
        mock_summary = MagicMock()
        mock_summary.total_budget = Decimal("2000.00")
        mock_summary.total_spent = Decimal("1700.00")
        mock_summary.total_remaining = Decimal("300.00")
        mock_summary.percent_used = 85.0

        kpis = generator._create_kpis(mock_summary, {})

        assert kpis["total_spent"].status == "warning"

    def test_kpi_status_critical(self, generator: DashboardGenerator) -> None:
        """Test KPI critical status."""
        mock_summary = MagicMock()
        mock_summary.total_budget = Decimal("2000.00")
        mock_summary.total_spent = Decimal("2200.00")
        mock_summary.total_remaining = Decimal("-200.00")
        mock_summary.percent_used = 110.0

        kpis = generator._create_kpis(mock_summary, {})

        assert kpis["remaining"].status == "critical"
        assert kpis["percent_used"].status == "critical"


class TestDashboardSection:
    """Tests for DashboardSection."""

    def test_default_position(self) -> None:
        """Test default position."""
        section = DashboardSection(title="Test")
        assert section.position == (1, 1)

    def test_default_size(self) -> None:
        """Test default size."""
        section = DashboardSection(title="Test")
        assert section.size == (5, 4)

    def test_with_kpis(self) -> None:
        """Test section with KPIs."""
        kpis = [
            DashboardKPI(name="KPI 1", value=100),
            DashboardKPI(name="KPI 2", value=200),
        ]
        section = DashboardSection(title="Test", kpis=kpis)

        assert len(section.kpis) == 2

    def test_with_chart(self) -> None:
        """Test section with chart."""
        section = DashboardSection(
            title="Chart",
            chart_type="pie",
            data_range="A1:B10",
        )

        assert section.chart_type == "pie"
        assert section.data_range == "A1:B10"


class TestValidationRuleType:
    """Tests for ValidationRuleType enum."""

    def test_all_types_exist(self) -> None:
        """Test all validation types exist."""
        assert ValidationRuleType.WHOLE_NUMBER
        assert ValidationRuleType.DECIMAL
        assert ValidationRuleType.LIST
        assert ValidationRuleType.DATE
        assert ValidationRuleType.TIME
        assert ValidationRuleType.TEXT_LENGTH
        assert ValidationRuleType.CUSTOM


class TestComparisonOperator:
    """Tests for ComparisonOperator enum."""

    def test_all_operators_exist(self) -> None:
        """Test all operators exist."""
        assert ComparisonOperator.EQUAL
        assert ComparisonOperator.NOT_EQUAL
        assert ComparisonOperator.GREATER
        assert ComparisonOperator.GREATER_OR_EQUAL
        assert ComparisonOperator.LESS
        assert ComparisonOperator.LESS_OR_EQUAL
        assert ComparisonOperator.BETWEEN
        assert ComparisonOperator.NOT_BETWEEN


class TestConditionalFormatType:
    """Tests for ConditionalFormatType enum."""

    def test_all_types_exist(self) -> None:
        """Test all format types exist."""
        assert ConditionalFormatType.CELL_VALUE
        assert ConditionalFormatType.FORMULA
        assert ConditionalFormatType.COLOR_SCALE
        assert ConditionalFormatType.DATA_BAR
        assert ConditionalFormatType.ICON_SET
        assert ConditionalFormatType.TOP_N
        assert ConditionalFormatType.ABOVE_AVERAGE
        assert ConditionalFormatType.DUPLICATE
