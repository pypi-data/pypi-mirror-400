"""
Tests for the builders module.

Implements tests for:
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.builders.conditional import (
    ColorScaleBuilder,
    ConditionalFormatBuilder,
    DataBarBuilder,
    IconSetBuilder,
    budget_variance_format,
    expense_bar_format,
    percent_scale_format,
)
from spreadsheet_dl.builders.style import (
    StyleBuilder,
    currency_style,
    header_style,
    percentage_style,
    total_row_style,
)
from spreadsheet_dl.builders.validation import (
    DataValidationBuilder,
    category_validation,
    date_validation,
    list_validation,
    number_validation,
    positive_number_validation,
)
from spreadsheet_dl.schema.conditional import (
    ColorScaleType,
    ConditionalRuleType,
    IconSetType,
    RuleOperator,
    ValueType,
)
from spreadsheet_dl.schema.data_validation import (
    ErrorAlertStyle,
    ValidationOperator,
    ValidationType,
)
from spreadsheet_dl.schema.styles import (
    BorderStyle,
    FontWeight,
    NumberFormat,
    NumberFormatCategory,
    TextAlign,
    VerticalAlign,
)

pytestmark = [pytest.mark.unit, pytest.mark.builder]

# ============================================================================
# DataValidationBuilder Tests
# ============================================================================


class TestDataValidationBuilder:
    """Tests for DataValidationBuilder."""

    def test_list_validation(self) -> None:
        """Test list validation builder."""
        validation = (
            DataValidationBuilder().list(["A", "B", "C"]).show_dropdown().build()
        )
        assert validation.type == ValidationType.LIST
        assert validation.list_items == ["A", "B", "C"]
        assert validation.show_dropdown is True

    def test_list_from_range(self) -> None:
        """Test list validation from range."""
        validation = DataValidationBuilder().list_from_range("Categories!A:A").build()
        assert validation.type == ValidationType.LIST
        assert validation.list_source == "Categories!A:A"

    def test_decimal_greater_than(self) -> None:
        """Test decimal greater than validation."""
        validation = DataValidationBuilder().decimal().greater_than(0).build()
        assert validation.type == ValidationType.DECIMAL
        assert validation.operator == ValidationOperator.GREATER_THAN
        assert validation.value1 == 0

    def test_decimal_between(self) -> None:
        """Test decimal between validation."""
        validation = DataValidationBuilder().decimal().between(0, 100).build()
        assert validation.operator == ValidationOperator.BETWEEN
        assert validation.value1 == 0
        assert validation.value2 == 100

    def test_whole_number_less_than(self) -> None:
        """Test whole number less than validation."""
        validation = DataValidationBuilder().whole_number().less_than(1000).build()
        assert validation.type == ValidationType.WHOLE_NUMBER
        assert validation.operator == ValidationOperator.LESS_THAN
        assert validation.value1 == 1000

    def test_date_validation(self) -> None:
        """Test date validation builder."""
        from datetime import date

        validation = (
            DataValidationBuilder()
            .date()
            .between(date(2024, 1, 1), date(2024, 12, 31))
            .build()
        )
        assert validation.type == ValidationType.DATE
        assert validation.operator == ValidationOperator.BETWEEN
        assert validation.value1 == "2024-01-01"
        assert validation.value2 == "2024-12-31"

    def test_text_length_validation(self) -> None:
        """Test text length validation."""
        validation = (
            DataValidationBuilder().text_length().less_than_or_equal(100).build()
        )
        assert validation.type == ValidationType.TEXT_LENGTH
        assert validation.operator == ValidationOperator.LESS_THAN_OR_EQUAL
        assert validation.value1 == 100

    def test_custom_formula_validation(self) -> None:
        """Test custom formula validation."""
        validation = DataValidationBuilder().custom("=A1<=SUM(B:B)").build()
        assert validation.type == ValidationType.CUSTOM
        assert validation.formula == "=A1<=SUM(B:B)"

    def test_input_message(self) -> None:
        """Test input message configuration."""
        validation = (
            DataValidationBuilder()
            .decimal()
            .greater_than(0)
            .input_message("Amount", "Enter positive amount")
            .build()
        )
        assert validation.input_message is not None
        assert validation.input_message.title == "Amount"
        assert validation.input_message.body == "Enter positive amount"

    def test_stop_alert(self) -> None:
        """Test stop error alert."""
        validation = (
            DataValidationBuilder()
            .decimal()
            .greater_than(0)
            .stop_alert("Invalid", "Enter positive number")
            .build()
        )
        assert validation.error_alert is not None
        assert validation.error_alert.style == ErrorAlertStyle.STOP
        assert validation.error_alert.title == "Invalid"

    def test_warning_alert(self) -> None:
        """Test warning error alert."""
        validation = (
            DataValidationBuilder()
            .decimal()
            .greater_than(0)
            .warning_alert("Unusual", "Value seems high")
            .build()
        )
        assert validation.error_alert is not None
        assert validation.error_alert.style == ErrorAlertStyle.WARNING

    def test_allow_blank_default(self) -> None:
        """Test allow_blank defaults to True."""
        validation = DataValidationBuilder().decimal().greater_than(0).build()
        assert validation.allow_blank is True

    def test_allow_blank_disabled(self) -> None:
        """Test disabling allow_blank."""
        validation = (
            DataValidationBuilder().decimal().greater_than(0).allow_blank(False).build()
        )
        assert validation.allow_blank is False

    def test_operators(self) -> None:
        """Test all comparison operators."""
        # Equal
        v = DataValidationBuilder().decimal().equal_to(100).build()
        assert v.operator == ValidationOperator.EQUAL

        # Not equal
        v = DataValidationBuilder().decimal().not_equal_to(0).build()
        assert v.operator == ValidationOperator.NOT_EQUAL

        # Less than or equal
        v = DataValidationBuilder().decimal().less_than_or_equal(100).build()
        assert v.operator == ValidationOperator.LESS_THAN_OR_EQUAL

        # Greater than or equal
        v = DataValidationBuilder().decimal().greater_than_or_equal(0).build()
        assert v.operator == ValidationOperator.GREATER_THAN_OR_EQUAL

        # Not between
        v = DataValidationBuilder().decimal().not_between(0, 100).build()
        assert v.operator == ValidationOperator.NOT_BETWEEN


class TestValidationConvenienceFunctions:
    """Tests for validation convenience functions."""

    def test_list_validation_function(self) -> None:
        """Test list_validation convenience function."""
        builder = list_validation(["A", "B", "C"])
        validation = builder.build()
        assert validation.type == ValidationType.LIST
        assert validation.list_items == ["A", "B", "C"]

    def test_number_validation_function(self) -> None:
        """Test number_validation convenience function."""
        builder = number_validation()
        validation = builder.greater_than(0).build()
        assert validation.type == ValidationType.DECIMAL

    def test_date_validation_function(self) -> None:
        """Test date_validation convenience function."""
        builder = date_validation()
        validation = builder.greater_than("2024-01-01").build()
        assert validation.type == ValidationType.DATE

    def test_positive_number_validation(self) -> None:
        """Test positive_number_validation preset."""
        validation = positive_number_validation()
        assert validation.type == ValidationType.DECIMAL
        assert validation.operator == ValidationOperator.GREATER_THAN
        assert validation.error_alert is not None

    def test_positive_number_validation_with_zero(self) -> None:
        """Test positive_number_validation allowing zero."""
        validation = positive_number_validation(allow_zero=True)
        assert validation.operator == ValidationOperator.GREATER_THAN_OR_EQUAL

    def test_category_validation(self) -> None:
        """Test category_validation preset."""
        categories = ["Housing", "Food", "Transport"]
        validation = category_validation(categories)
        assert validation.type == ValidationType.LIST
        assert validation.list_items == categories
        assert validation.show_dropdown is True


# ============================================================================
# ConditionalFormatBuilder Tests
# ============================================================================


class TestConditionalFormatBuilder:
    """Tests for ConditionalFormatBuilder."""

    def test_range_setting(self) -> None:
        """Test setting range."""
        fmt = ConditionalFormatBuilder().range("D2:D100").red_yellow_green().build()
        assert fmt.range == "D2:D100"

    def test_cell_value_rule_less_than(self) -> None:
        """Test cell value less than rule."""
        fmt = (
            ConditionalFormatBuilder()
            .range("D2:D100")
            .when_value()
            .less_than(0)
            .style("danger")
            .build()
        )
        assert len(fmt.rules) == 1
        assert fmt.rules[0].type == ConditionalRuleType.CELL_VALUE
        assert fmt.rules[0].operator == RuleOperator.LESS_THAN
        assert fmt.rules[0].value == 0
        assert fmt.rules[0].style == "danger"

    def test_cell_value_rule_between(self) -> None:
        """Test cell value between rule."""
        fmt = (
            ConditionalFormatBuilder()
            .range("D2:D100")
            .when_value()
            .between(0, 100)
            .style("normal")
            .build()
        )
        assert fmt.rules[0].operator == RuleOperator.BETWEEN
        assert fmt.rules[0].value == 0
        assert fmt.rules[0].value2 == 100

    def test_formula_rule(self) -> None:
        """Test formula-based rule."""
        fmt = (
            ConditionalFormatBuilder()
            .range("D2:D100")
            .when_formula("AND(D2>=0, D2<B2*0.1)", "warning")
            .build()
        )
        assert fmt.rules[0].type == ConditionalRuleType.FORMULA
        assert fmt.rules[0].formula == "AND(D2>=0, D2<B2*0.1)"

    def test_multiple_rules(self) -> None:
        """Test multiple rules with priority."""
        fmt = (
            ConditionalFormatBuilder()
            .range("D2:D100")
            .when_value()
            .less_than(0)
            .style("danger")
            .when_value()
            .greater_than_or_equal(0)
            .style("success")
            .build()
        )
        assert len(fmt.rules) == 2
        assert fmt.rules[0].priority == 1
        assert fmt.rules[1].priority == 2

    def test_color_scale_preset(self) -> None:
        """Test color scale preset."""
        fmt = ConditionalFormatBuilder().range("E2:E100").red_yellow_green().build()
        assert len(fmt.rules) == 1
        assert fmt.rules[0].type == ConditionalRuleType.COLOR_SCALE
        assert fmt.rules[0].color_scale is not None

    def test_color_scale_builder(self) -> None:
        """Test custom color scale builder."""
        builder = ConditionalFormatBuilder().range("E2:E100")
        color_scale = builder.color_scale()
        color_scale.min_color("#FF0000").mid_color("#FFFF00").max_color("#00FF00")
        fmt = builder.build()

        assert len(fmt.rules) == 1
        assert fmt.rules[0].color_scale is not None
        assert fmt.rules[0].color_scale.type == ColorScaleType.THREE_COLOR

    def test_data_bar_default(self) -> None:
        """Test default data bar."""
        fmt = ConditionalFormatBuilder().range("C2:C100").default_data_bar().build()
        assert fmt.rules[0].type == ConditionalRuleType.DATA_BAR
        assert fmt.rules[0].data_bar is not None

    def test_data_bar_builder(self) -> None:
        """Test custom data bar builder."""
        builder = ConditionalFormatBuilder().range("C2:C100")
        data_bar = builder.data_bar()
        data_bar.fill("#638EC6").gradient().hide_value()
        fmt = builder.build()

        assert fmt.rules[0].data_bar is not None
        assert fmt.rules[0].data_bar.gradient_fill is True
        assert fmt.rules[0].data_bar.show_value is False

    def test_icon_set_preset(self) -> None:
        """Test icon set preset."""
        fmt = ConditionalFormatBuilder().range("F2:F100").three_arrows().build()
        assert fmt.rules[0].type == ConditionalRuleType.ICON_SET
        assert fmt.rules[0].icon_set is not None

    def test_icon_set_builder(self) -> None:
        """Test custom icon set builder."""
        builder = ConditionalFormatBuilder().range("F2:F100")
        icons = builder.icon_set()
        icons.traffic_lights_3().hide_value()
        fmt = builder.build()

        assert fmt.rules[0].icon_set is not None
        assert fmt.rules[0].icon_set.icon_set == IconSetType.THREE_TRAFFIC_LIGHTS_1
        assert fmt.rules[0].icon_set.show_value is False

    def test_top_rule(self) -> None:
        """Test top N rule."""
        fmt = ConditionalFormatBuilder().range("C2:C100").top(10, "highlight").build()
        assert fmt.rules[0].type == ConditionalRuleType.TOP_BOTTOM
        assert fmt.rules[0].rank == 10
        assert fmt.rules[0].bottom is False

    def test_bottom_percent_rule(self) -> None:
        """Test bottom percent rule."""
        fmt = (
            ConditionalFormatBuilder()
            .range("C2:C100")
            .bottom(10, "low", percent=True)
            .build()
        )
        assert fmt.rules[0].rank == 10
        assert fmt.rules[0].percent is True
        assert fmt.rules[0].bottom is True

    def test_above_average_rule(self) -> None:
        """Test above average rule."""
        fmt = ConditionalFormatBuilder().range("C2:C100").above_average("high").build()
        assert fmt.rules[0].type == ConditionalRuleType.ABOVE_BELOW_AVERAGE

    def test_contains_text_rule(self) -> None:
        """Test contains text rule."""
        fmt = (
            ConditionalFormatBuilder()
            .range("A2:A100")
            .contains_text("Error", "error_style")
            .build()
        )
        assert fmt.rules[0].type == ConditionalRuleType.TEXT
        assert fmt.rules[0].text == "Error"

    def test_duplicates_rule(self) -> None:
        """Test duplicate values rule."""
        fmt = (
            ConditionalFormatBuilder()
            .range("B2:B100")
            .duplicates("duplicate_style")
            .build()
        )
        assert fmt.rules[0].type == ConditionalRuleType.DUPLICATE_UNIQUE


class TestConditionalConvenienceFunctions:
    """Tests for conditional formatting convenience functions."""

    def test_budget_variance_format(self) -> None:
        """Test budget variance format preset."""
        fmt = budget_variance_format("D2:D100")
        assert fmt.range == "D2:D100"
        assert len(fmt.rules) >= 2  # At least danger and warning rules

    def test_percent_scale_format(self) -> None:
        """Test percent scale format preset."""
        fmt = percent_scale_format("E2:E100")
        assert fmt.range == "E2:E100"
        assert fmt.rules[0].type == ConditionalRuleType.COLOR_SCALE

    def test_expense_bar_format(self) -> None:
        """Test expense bar format preset."""
        fmt = expense_bar_format("C2:C100")
        assert fmt.range == "C2:C100"
        assert fmt.rules[0].type == ConditionalRuleType.DATA_BAR


class TestColorScaleBuilder:
    """Tests for ColorScaleBuilder."""

    def test_two_color_scale(self) -> None:
        """Test two color scale."""
        scale = ColorScaleBuilder().min_color("#FF0000").max_color("#00FF00").build()
        assert scale.type == ColorScaleType.TWO_COLOR
        assert len(scale.points) == 2

    def test_three_color_scale(self) -> None:
        """Test three color scale."""
        scale = (
            ColorScaleBuilder()
            .min_color("#FF0000")
            .mid_color("#FFFF00")
            .max_color("#00FF00")
            .build()
        )
        assert scale.type == ColorScaleType.THREE_COLOR
        assert len(scale.points) == 3

    def test_custom_value_types(self) -> None:
        """Test custom value types."""
        scale = (
            ColorScaleBuilder()
            .min_color("#FF0000", ValueType.NUMBER, 0)
            .max_color("#00FF00", ValueType.NUMBER, 100)
            .build()
        )
        assert scale.points[0].value_type == ValueType.NUMBER
        assert scale.points[0].value == 0


class TestDataBarBuilder:
    """Tests for DataBarBuilder."""

    def test_fill_color(self) -> None:
        """Test fill color."""
        bar = DataBarBuilder().fill("#638EC6").build()
        assert str(bar.fill_color) == "#638EC6"

    def test_negative_color(self) -> None:
        """Test negative color."""
        bar = DataBarBuilder().negative("#C00000").build()
        assert str(bar.negative_color) == "#C00000"

    def test_gradient(self) -> None:
        """Test gradient fill."""
        bar = DataBarBuilder().gradient().build()
        assert bar.gradient_fill is True

    def test_min_max_values(self) -> None:
        """Test min/max values."""
        bar = DataBarBuilder().min_value(0).max_value(100).build()
        assert bar.min_type == ValueType.NUMBER
        assert bar.min_value == 0
        assert bar.max_value == 100

    def test_axis_position(self) -> None:
        """Test axis position."""
        bar = DataBarBuilder().axis_midpoint().build()
        assert bar.axis_position == "midpoint"

        bar = DataBarBuilder().no_axis().build()
        assert bar.axis_position == "none"

    def test_direction(self) -> None:
        """Test direction."""
        bar = DataBarBuilder().left_to_right().build()
        assert bar.direction == "leftToRight"

        bar = DataBarBuilder().right_to_left().build()
        assert bar.direction == "rightToLeft"


class TestIconSetBuilder:
    """Tests for IconSetBuilder."""

    def test_icon_set_types(self) -> None:
        """Test different icon set types."""
        icons = IconSetBuilder().arrows_3().build()
        assert icons.icon_set == IconSetType.THREE_ARROWS

        icons = IconSetBuilder().traffic_lights_3().build()
        assert icons.icon_set == IconSetType.THREE_TRAFFIC_LIGHTS_1

        icons = IconSetBuilder().ratings_5().build()
        assert icons.icon_set == IconSetType.FIVE_RATINGS

    def test_hide_value(self) -> None:
        """Test hide value option."""
        icons = IconSetBuilder().arrows_3().hide_value().build()
        assert icons.show_value is False

    def test_reverse(self) -> None:
        """Test reverse option."""
        icons = IconSetBuilder().arrows_3().reverse().build()
        assert icons.reverse is True

    def test_custom_thresholds(self) -> None:
        """Test custom thresholds."""
        icons = IconSetBuilder().arrows_3().threshold(70, 0).threshold(30, 1).build()
        assert len(icons.thresholds) == 2
        assert icons.thresholds[0].value == 70
        assert icons.thresholds[1].value == 30


# ============================================================================
# StyleBuilder Tests
# ============================================================================


class TestStyleBuilder:
    """Tests for StyleBuilder."""

    def test_basic_style(self) -> None:
        """Test basic style creation."""
        style = StyleBuilder("test").build()
        assert style.name == "test"

    def test_font_configuration(self) -> None:
        """Test font configuration."""
        style = (
            StyleBuilder("test")
            .font(family="Arial", size="12pt", weight="bold", color="#FF0000")
            .build()
        )
        assert style.font.family == "Arial"
        assert style.font.size == "12pt"
        assert style.font.weight == FontWeight.BOLD
        assert str(style.font.color) == "#FF0000"

    def test_individual_font_methods(self) -> None:
        """Test individual font methods."""
        style = (
            StyleBuilder("test")
            .font_family("Arial")
            .font_size("11pt")
            .font_color("#000000")
            .bold()
            .italic()
            .build()
        )
        assert style.font.family == "Arial"
        assert style.font.size == "11pt"
        assert style.font.weight == FontWeight.BOLD
        assert style.font.italic is True

    def test_underline(self) -> None:
        """Test underline."""
        style = StyleBuilder("test").underline().build()
        assert style.font.underline.value == "single"

    def test_strikethrough(self) -> None:
        """Test strikethrough."""
        style = StyleBuilder("test").strikethrough().build()
        assert style.font.strikethrough.value == "single"

    def test_alignment(self) -> None:
        """Test alignment configuration."""
        style = (
            StyleBuilder("test").align(horizontal="center", vertical="middle").build()
        )
        assert style.text_align == TextAlign.CENTER
        assert style.vertical_align == VerticalAlign.MIDDLE

    def test_alignment_shortcuts(self) -> None:
        """Test alignment shortcut methods."""
        style = StyleBuilder("test").align_right().align_top().build()
        assert style.text_align == TextAlign.RIGHT
        assert style.vertical_align == VerticalAlign.TOP

    def test_background(self) -> None:
        """Test background color."""
        style = StyleBuilder("test").background("#FF0000").build()
        assert str(style.background_color) == "#FF0000"

    def test_borders(self) -> None:
        """Test border configuration."""
        style = StyleBuilder("test").border("2pt", "solid", "#000000").build()
        assert style.border_top is not None
        assert style.border_bottom is not None
        assert style.border_left is not None
        assert style.border_right is not None
        assert style.border_top.width == "2pt"
        assert style.border_top.style == BorderStyle.SOLID

    def test_individual_borders(self) -> None:
        """Test individual border methods."""
        style = (
            StyleBuilder("test")
            .border_top("2pt", "solid", "#FF0000")
            .border_bottom("1pt", "dashed", "#0000FF")
            .build()
        )
        assert style.border_top is not None
        assert style.border_bottom is not None
        assert style.border_left is None
        assert style.border_top.width == "2pt"
        assert style.border_bottom.style == BorderStyle.DASHED

    def test_number_format(self) -> None:
        """Test number format configuration."""
        style = (
            StyleBuilder("test")
            .number_format(
                category="number",
                decimal_places=2,
                use_thousands=True,
            )
            .build()
        )
        assert style.number_format is not None
        assert isinstance(style.number_format, NumberFormat)
        assert style.number_format.category == NumberFormatCategory.NUMBER
        assert style.number_format.decimal_places == 2

    def test_currency_format(self) -> None:
        """Test currency format shortcut."""
        style = (
            StyleBuilder("test").currency(symbol="$", negatives="parentheses").build()
        )
        assert style.number_format is not None
        assert isinstance(style.number_format, NumberFormat)
        assert style.number_format.category == NumberFormatCategory.CURRENCY
        assert style.number_format.currency_symbol == "$"

    def test_percentage_format(self) -> None:
        """Test percentage format shortcut."""
        style = StyleBuilder("test").percentage(decimal_places=1).build()
        assert style.number_format is not None
        assert isinstance(style.number_format, NumberFormat)
        assert style.number_format.category == NumberFormatCategory.PERCENTAGE
        assert style.number_format.decimal_places == 1

    def test_text_wrap(self) -> None:
        """Test text wrapping."""
        style = StyleBuilder("test").wrap().build()
        assert style.wrap_text is True

    def test_shrink_to_fit(self) -> None:
        """Test shrink to fit."""
        style = StyleBuilder("test").shrink().build()
        assert style.shrink_to_fit is True

    def test_text_rotation(self) -> None:
        """Test text rotation."""
        style = StyleBuilder("test").rotate(45).build()
        assert style.text_rotation == 45

    def test_indent(self) -> None:
        """Test indent."""
        style = StyleBuilder("test").indent_level(2).build()
        assert style.indent == 2

    def test_protection(self) -> None:
        """Test cell protection."""
        style = StyleBuilder("test").unlocked().hide_formula().build()
        assert style.locked is False
        assert style.hidden is True

    def test_inheritance(self) -> None:
        """Test style inheritance."""
        base = StyleBuilder("base").font_family("Arial").font_size("12pt").build()
        derived = StyleBuilder("derived").extends(base).bold().build()

        assert derived.font.family == "Arial"
        assert derived.font.weight == FontWeight.BOLD


class TestStyleConvenienceFunctions:
    """Tests for style convenience functions."""

    def test_header_style(self) -> None:
        """Test header_style preset."""
        style = header_style()
        assert style.name == "header"
        assert style.font.weight == FontWeight.BOLD
        assert style.background_color is not None
        assert style.text_align == TextAlign.CENTER

    def test_header_style_custom(self) -> None:
        """Test header_style with custom options."""
        style = header_style(
            name="my_header",
            background="#1A3A5C",
            font_color="#FFFFFF",
        )
        assert style.name == "my_header"
        assert str(style.background_color) == "#1A3A5C"

    def test_currency_style(self) -> None:
        """Test currency_style preset."""
        style = currency_style()
        assert style.name == "currency"
        assert style.text_align == TextAlign.RIGHT
        assert style.number_format is not None
        assert isinstance(style.number_format, NumberFormat)
        assert style.number_format.category == NumberFormatCategory.CURRENCY

    def test_percentage_style(self) -> None:
        """Test percentage_style preset."""
        style = percentage_style()
        assert style.name == "percentage"
        assert style.number_format is not None
        assert isinstance(style.number_format, NumberFormat)
        assert style.number_format.category == NumberFormatCategory.PERCENTAGE

    def test_total_row_style(self) -> None:
        """Test total_row_style preset."""
        style = total_row_style()
        assert style.name == "total"
        assert style.font.weight == FontWeight.BOLD
        assert style.border_top is not None
