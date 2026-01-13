"""
Comprehensive tests for conditional formatting implementation.

Tests all implemented conditional formatting features with focus on:
- Cell value comparisons (>, <, =, between, etc.)
- Text-based conditions (contains, begins with, ends with)
- Style application
- Multiple rules with priority
- Edge cases and error handling
"""

from __future__ import annotations

import pytest
from odf.opendocument import OpenDocumentSpreadsheet

from spreadsheet_dl.interactive import InteractiveOdsBuilder
from spreadsheet_dl.schema.conditional import (
    ColorScale,
    ConditionalFormat,
    ConditionalRule,
    ConditionalRuleType,
    DataBar,
    IconSet,
    RuleOperator,
)
from spreadsheet_dl.schema.styles import CellStyle, Color


class TestConditionalFormattingBasics:
    """Test basic conditional formatting functionality."""

    def test_simple_less_than_rule(self) -> None:
        """Test basic less than comparison."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=0,
            style="danger",
        )

        fmt = ConditionalFormat(range="A1:A5", rules=[rule])

        assert fmt.range == "A1:A5"
        assert len(fmt.rules) == 1
        assert fmt.rules[0].operator == RuleOperator.LESS_THAN
        assert fmt.rules[0].value == 0

    def test_greater_than_rule(self) -> None:
        """Test greater than comparison."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN,
            value=100,
            style="success",
        )

        assert rule.operator == RuleOperator.GREATER_THAN
        assert rule.value == 100
        assert rule.style == "success"

    def test_equal_rule(self) -> None:
        """Test equality comparison."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.EQUAL,
            value=50,
            style="warning",
        )

        assert rule.operator == RuleOperator.EQUAL
        assert rule.value == 50

    def test_not_equal_rule(self) -> None:
        """Test not equal comparison."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.NOT_EQUAL,
            value=0,
            style="info",
        )

        assert rule.operator == RuleOperator.NOT_EQUAL
        assert rule.value == 0

    def test_between_rule(self) -> None:
        """Test between comparison."""
        rule = ConditionalRule.between(
            min_value=0,
            max_value=100,
            style="normal",
        )

        assert rule.operator == RuleOperator.BETWEEN
        assert rule.value == 0
        assert rule.value2 == 100

    def test_greater_than_or_equal_rule(self) -> None:
        """Test >= comparison."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN_OR_EQUAL,
            value=0,
            style="success",
        )

        assert rule.operator == RuleOperator.GREATER_THAN_OR_EQUAL
        assert rule.value == 0

    def test_less_than_or_equal_rule(self) -> None:
        """Test <= comparison."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN_OR_EQUAL,
            value=100,
            style="warning",
        )

        assert rule.operator == RuleOperator.LESS_THAN_OR_EQUAL
        assert rule.value == 100


class TestTextConditions:
    """Test text-based conditional rules."""

    def test_contains_text_rule(self) -> None:
        """Test contains text condition."""
        rule = ConditionalRule.contains_text(
            text="Error",
            style="danger",
        )

        assert rule.type == ConditionalRuleType.TEXT
        assert rule.operator == RuleOperator.CONTAINS_TEXT
        assert rule.text == "Error"

    def test_begins_with_condition(self) -> None:
        """Test begins with text condition."""
        rule = ConditionalRule(
            type=ConditionalRuleType.TEXT,
            operator=RuleOperator.BEGINS_WITH,
            text="WARN",
            style="warning",
        )

        assert rule.operator == RuleOperator.BEGINS_WITH
        assert rule.text == "WARN"

    def test_ends_with_condition(self) -> None:
        """Test ends with text condition."""
        rule = ConditionalRule(
            type=ConditionalRuleType.TEXT,
            operator=RuleOperator.ENDS_WITH,
            text=".pdf",
            style="info",
        )

        assert rule.operator == RuleOperator.ENDS_WITH
        assert rule.text == ".pdf"

    def test_not_contains_text(self) -> None:
        """Test not contains text condition."""
        rule = ConditionalRule(
            type=ConditionalRuleType.TEXT,
            operator=RuleOperator.NOT_CONTAINS_TEXT,
            text="deprecated",
            style="success",
        )

        assert rule.operator == RuleOperator.NOT_CONTAINS_TEXT


class TestMultipleRules:
    """Test conditional formats with multiple rules."""

    def test_multiple_rules_with_priority(self) -> None:
        """Test multiple rules applied in priority order."""
        fmt = ConditionalFormat(
            range="D2:D100",
            rules=[
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN, 0, "danger", priority=1
                ),
                ConditionalRule.cell_value(
                    RuleOperator.LESS_THAN, 100, "warning", priority=2
                ),
                ConditionalRule.cell_value(
                    RuleOperator.GREATER_THAN_OR_EQUAL, 100, "success", priority=3
                ),
            ],
        )

        assert len(fmt.rules) == 3
        assert fmt.rules[0].priority == 1
        assert fmt.rules[1].priority == 2
        assert fmt.rules[2].priority == 3

    def test_stop_if_true_flag(self) -> None:
        """Test stop_if_true behavior."""
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=0,
            style="danger",
        )
        rule.stop_if_true = True

        assert rule.stop_if_true is True

    def test_add_rule_method(self) -> None:
        """Test adding rules dynamically."""
        fmt = ConditionalFormat(range="A1:A10")
        assert len(fmt.rules) == 0

        fmt.add_rule(ConditionalRule.cell_value(RuleOperator.LESS_THAN, 0, "danger"))
        assert len(fmt.rules) == 1

        fmt.add_rule(
            ConditionalRule.cell_value(RuleOperator.GREATER_THAN, 100, "success")
        )
        assert len(fmt.rules) == 2


class TestColorScales:
    """Test color scale conditional formatting."""

    def test_two_color_scale(self) -> None:
        """Test two-color gradient scale."""
        scale = ColorScale.two_color(
            min_color=Color("#FF0000"),
            max_color=Color("#00FF00"),
        )

        assert scale.type.value == "twoColor"
        assert len(scale.points) == 2

    def test_three_color_scale(self) -> None:
        """Test three-color gradient scale."""
        scale = ColorScale.three_color(
            min_color=Color("#F8696B"),
            mid_color=Color("#FFEB84"),
            max_color=Color("#63BE7B"),
        )

        assert scale.type.value == "threeColor"
        assert len(scale.points) == 3

    def test_red_yellow_green_preset(self) -> None:
        """Test red-yellow-green preset."""
        scale = ColorScale.red_yellow_green()

        assert scale.type.value == "threeColor"
        assert len(scale.points) == 3

    def test_green_yellow_red_preset(self) -> None:
        """Test inverted green-yellow-red preset."""
        scale = ColorScale.green_yellow_red()

        assert scale.type.value == "threeColor"

    def test_white_to_blue_preset(self) -> None:
        """Test white to blue two-color scale."""
        scale = ColorScale.white_to_blue()

        assert scale.type.value == "twoColor"
        assert len(scale.points) == 2

    def test_color_scale_in_rule(self) -> None:
        """Test color scale as part of conditional rule."""
        rule = ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.red_yellow_green(),
        )

        assert rule.type == ConditionalRuleType.COLOR_SCALE
        assert rule.color_scale is not None


class TestDataBars:
    """Test data bar conditional formatting."""

    def test_default_data_bar(self) -> None:
        """Test default data bar creation."""
        bar = DataBar.default()

        assert bar.fill_color is not None
        assert bar.show_value is True

    def test_budget_variance_data_bar(self) -> None:
        """Test budget variance data bar preset."""
        bar = DataBar.budget_variance()

        assert bar.fill_color is not None
        assert bar.negative_color is not None
        assert bar.axis_position == "midpoint"

    def test_custom_data_bar(self) -> None:
        """Test custom data bar configuration."""
        bar = DataBar(
            fill_color=Color("#4472C4"),
            negative_color=Color("#C00000"),
            show_value=False,
            gradient_fill=True,
        )

        assert bar.show_value is False
        assert bar.gradient_fill is True

    def test_data_bar_in_rule(self) -> None:
        """Test data bar as part of conditional rule."""
        rule = ConditionalRule(
            type=ConditionalRuleType.DATA_BAR,
            data_bar=DataBar.default(),
        )

        assert rule.type == ConditionalRuleType.DATA_BAR
        assert rule.data_bar is not None


class TestIconSets:
    """Test icon set conditional formatting."""

    def test_three_arrows_preset(self) -> None:
        """Test three arrows icon set."""
        icons = IconSet.three_arrows()

        assert icons.icon_set.value == "3Arrows"
        assert len(icons.thresholds) == 2

    def test_three_traffic_lights_preset(self) -> None:
        """Test three traffic lights icon set."""
        icons = IconSet.three_traffic_lights()

        assert icons.icon_set.value == "3TrafficLights1"

    def test_five_ratings_preset(self) -> None:
        """Test five ratings (stars) icon set."""
        icons = IconSet.five_ratings()

        assert icons.icon_set.value == "5Ratings"
        assert len(icons.thresholds) == 4

    def test_icon_set_with_reversed_order(self) -> None:
        """Test reversed icon order."""
        icons = IconSet.three_arrows(reverse=True)

        assert icons.reverse is True

    def test_icon_set_hide_value(self) -> None:
        """Test hiding cell values with icons."""
        icons = IconSet(
            icon_set=IconSet.three_arrows().icon_set,
            show_value=False,
        )

        assert icons.show_value is False


class TestCellRangeParsing:
    """Test cell range parsing utilities."""

    def test_parse_simple_range(self) -> None:
        """Test parsing simple range like A1:B10."""
        builder = InteractiveOdsBuilder()
        start, end = builder._parse_range("A1:B10")

        assert start == "A1"
        assert end == "B10"

    def test_parse_single_cell(self) -> None:
        """Test parsing single cell as range."""
        builder = InteractiveOdsBuilder()
        start, end = builder._parse_range("A1")

        assert start == "A1"
        assert end == "A1"

    def test_cell_to_coords_simple(self) -> None:
        """Test converting A1 notation to coordinates."""
        builder = InteractiveOdsBuilder()
        col, row = builder._cell_to_coords("A1")

        assert col == 0
        assert row == 0

    def test_cell_to_coords_b5(self) -> None:
        """Test converting B5 to coordinates."""
        builder = InteractiveOdsBuilder()
        col, row = builder._cell_to_coords("B5")

        assert col == 1
        assert row == 4

    def test_cell_to_coords_z10(self) -> None:
        """Test converting Z10 to coordinates."""
        builder = InteractiveOdsBuilder()
        col, row = builder._cell_to_coords("Z10")

        assert col == 25
        assert row == 9

    def test_cell_to_coords_aa1(self) -> None:
        """Test converting AA1 to coordinates."""
        builder = InteractiveOdsBuilder()
        col, row = builder._cell_to_coords("AA1")

        assert col == 26
        assert row == 0

    def test_invalid_range_format(self) -> None:
        """Test handling invalid range format."""
        builder = InteractiveOdsBuilder()

        with pytest.raises(ValueError, match="Invalid cell range format"):
            builder._parse_range("A1:B2:C3")

    def test_invalid_cell_reference(self) -> None:
        """Test handling invalid cell reference."""
        builder = InteractiveOdsBuilder()

        with pytest.raises(ValueError, match="Invalid cell reference"):
            builder._cell_to_coords("123")


class TestRuleEvaluation:
    """Test conditional rule evaluation logic."""

    def test_evaluate_less_than_true(self) -> None:
        """Test evaluating less than condition (true case)."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=10,
            style="danger",
        )

        result = builder._evaluate_cell_value_rule(5, rule)
        assert result is True

    def test_evaluate_less_than_false(self) -> None:
        """Test evaluating less than condition (false case)."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=10,
            style="danger",
        )

        result = builder._evaluate_cell_value_rule(15, rule)
        assert result is False

    def test_evaluate_greater_than_true(self) -> None:
        """Test evaluating greater than condition."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN,
            value=100,
            style="success",
        )

        result = builder._evaluate_cell_value_rule(150, rule)
        assert result is True

    def test_evaluate_equal_true(self) -> None:
        """Test evaluating equality condition."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.EQUAL,
            value=42,
            style="info",
        )

        result = builder._evaluate_cell_value_rule(42, rule)
        assert result is True

    def test_evaluate_between_true(self) -> None:
        """Test evaluating between condition (in range)."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.between(
            min_value=0,
            max_value=100,
            style="normal",
        )

        result = builder._evaluate_cell_value_rule(50, rule)
        assert result is True

    def test_evaluate_between_false(self) -> None:
        """Test evaluating between condition (out of range)."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.between(
            min_value=0,
            max_value=100,
            style="normal",
        )

        result = builder._evaluate_cell_value_rule(150, rule)
        assert result is False

    def test_evaluate_contains_text_true(self) -> None:
        """Test evaluating contains text condition."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.contains_text(
            text="Error",
            style="danger",
        )

        result = builder._evaluate_text_rule("Error: Something failed", rule)
        assert result is True

    def test_evaluate_contains_text_false(self) -> None:
        """Test evaluating contains text condition (not found)."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.contains_text(
            text="Error",
            style="danger",
        )

        result = builder._evaluate_text_rule("Success", rule)
        assert result is False

    def test_evaluate_begins_with_true(self) -> None:
        """Test evaluating begins with condition."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule(
            type=ConditionalRuleType.TEXT,
            operator=RuleOperator.BEGINS_WITH,
            text="WARN",
            style="warning",
        )

        result = builder._evaluate_text_rule("WARNING: Check this", rule)
        assert result is True

    def test_evaluate_ends_with_true(self) -> None:
        """Test evaluating ends with condition."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule(
            type=ConditionalRuleType.TEXT,
            operator=RuleOperator.ENDS_WITH,
            text=".pdf",
            style="info",
        )

        result = builder._evaluate_text_rule("document.pdf", rule)
        assert result is True

    def test_evaluate_with_string_to_number_conversion(self) -> None:
        """Test evaluation with automatic string to number conversion."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN,
            value="100",
            style="success",
        )

        # String value should be converted to number for comparison
        result = builder._evaluate_cell_value_rule("150", rule)
        assert result is True

    def test_evaluate_with_none_value(self) -> None:
        """Test evaluation with None value."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.LESS_THAN,
            value=10,
            style="danger",
        )

        result = builder._evaluate_cell_value_rule(None, rule)
        assert result is False


class TestStyleApplication:
    """Test style application from conditional rules."""

    def test_named_style_danger(self) -> None:
        """Test applying danger style."""
        # Create a minimal ODS document
        doc = OpenDocumentSpreadsheet()
        builder = InteractiveOdsBuilder()

        style = builder._get_or_create_named_style(doc, "danger")

        assert style is not None
        assert style.getAttribute("name") == "danger"

    def test_named_style_warning(self) -> None:
        """Test applying warning style."""
        doc = OpenDocumentSpreadsheet()
        builder = InteractiveOdsBuilder()

        style = builder._get_or_create_named_style(doc, "warning")

        assert style is not None
        assert style.getAttribute("name") == "warning"

    def test_named_style_success(self) -> None:
        """Test applying success style."""
        doc = OpenDocumentSpreadsheet()
        builder = InteractiveOdsBuilder()

        style = builder._get_or_create_named_style(doc, "success")

        assert style is not None
        assert style.getAttribute("name") == "success"

    def test_custom_cell_style_conversion(self) -> None:
        """Test converting CellStyle to ODF style."""
        from spreadsheet_dl.schema.styles import Font, FontWeight

        doc = OpenDocumentSpreadsheet()
        builder = InteractiveOdsBuilder()

        cell_style = CellStyle(
            name="custom",
            background_color=Color("#FF0000"),
            font=Font(color=Color("#FFFFFF"), weight=FontWeight.BOLD),
        )

        odf_style = builder._convert_cell_style_to_odf(doc, cell_style)

        assert odf_style is not None
        assert odf_style.getAttribute("name") == "custom"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_rules_list(self) -> None:
        """Test conditional format with no rules."""
        fmt = ConditionalFormat(range="A1:A10")

        assert len(fmt.rules) == 0

    def test_none_style_in_rule(self) -> None:
        """Test rule with None style."""
        rule = ConditionalRule(
            type=ConditionalRuleType.CELL_VALUE,
            operator=RuleOperator.LESS_THAN,
            value=0,
            style=None,
        )

        assert rule.style is None

    def test_invalid_operator_returns_false(self) -> None:
        """Test that invalid operator returns False."""
        builder = InteractiveOdsBuilder()

        # Create rule with value but no valid comparison
        result = builder._evaluate_cell_value_rule(
            10, type("Rule", (), {"operator": None, "value": 5})()
        )

        assert result is False

    def test_type_mismatch_in_comparison(self) -> None:
        """Test handling type mismatches gracefully."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.cell_value(
            operator=RuleOperator.GREATER_THAN,
            value=100,
            style="success",
        )

        # Should handle comparison between incompatible types
        result = builder._evaluate_cell_value_rule("not_a_number", rule)
        # May be True or False depending on conversion, but shouldn't crash
        assert isinstance(result, bool)

    def test_formula_rule_not_supported(self) -> None:
        """Test that formula rules return False (not supported)."""
        builder = InteractiveOdsBuilder()
        rule = ConditionalRule.from_formula(
            formula="A1>B1",
            style="warning",
        )

        # Formula rules not supported in static evaluation
        result = builder._evaluate_rule(None, rule)
        assert result is False


class TestIntegration:
    """Integration tests for end-to-end conditional formatting."""

    def test_to_dict_conversion(self) -> None:
        """Test converting ConditionalFormat to dictionary."""
        fmt = ConditionalFormat(
            range="A1:A10",
            rules=[
                ConditionalRule.cell_value(RuleOperator.LESS_THAN, 0, "danger"),
            ],
        )

        data = fmt.to_dict()

        assert data["range"] == "A1:A10"
        assert len(data["rules"]) == 1
        assert data["rules"][0]["type"] == "cellValue"
        assert data["rules"][0]["operator"] == "lessThan"
        assert data["rules"][0]["value"] == 0

    def test_rule_to_dict_with_color_scale(self) -> None:
        """Test converting color scale rule to dict."""
        rule = ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.red_yellow_green(),
        )

        data = rule.to_dict()

        assert data["type"] == "colorScale"
        assert "colorScale" in data
        assert data["colorScale"]["type"] == "threeColor"

    def test_rule_to_dict_with_data_bar(self) -> None:
        """Test converting data bar rule to dict."""
        rule = ConditionalRule(
            type=ConditionalRuleType.DATA_BAR,
            data_bar=DataBar.default(),
        )

        data = rule.to_dict()

        assert data["type"] == "dataBar"
        assert "dataBar" in data

    def test_rule_to_dict_with_icon_set(self) -> None:
        """Test converting icon set rule to dict."""
        rule = ConditionalRule(
            type=ConditionalRuleType.ICON_SET,
            icon_set=IconSet.three_arrows(),
        )

        data = rule.to_dict()

        assert data["type"] == "iconSet"
        assert "iconSet" in data
