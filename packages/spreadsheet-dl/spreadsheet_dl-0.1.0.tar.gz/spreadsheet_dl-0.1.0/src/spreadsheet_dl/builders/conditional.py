"""Fluent ConditionalFormatBuilder for conditional formatting rules.

Provides a chainable API for building conditional formatting rules
including cell value rules, color scales, data bars, and icon sets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Self

from spreadsheet_dl.schema.conditional import (
    ColorScale,
    ColorScalePoint,
    ColorScaleType,
    ConditionalFormat,
    ConditionalRule,
    ConditionalRuleType,
    DataBar,
    IconSet,
    IconSetThreshold,
    IconSetType,
    RuleOperator,
    ValueType,
)
from spreadsheet_dl.schema.styles import CellStyle, Color


@dataclass
class ColorScaleBuilder:
    """Builder for color scales."""

    _type: ColorScaleType = field(default=ColorScaleType.THREE_COLOR)
    _points: list[ColorScalePoint] = field(default_factory=list)

    def min_color(
        self,
        color: Color | str,
        value_type: ValueType = ValueType.MIN,
        value: float | None = None,
    ) -> Self:
        """Set minimum color."""
        if isinstance(color, str):
            color = Color(color)
        self._points.insert(0, ColorScalePoint(value_type, value, color))
        return self

    def mid_color(
        self,
        color: Color | str,
        value_type: ValueType = ValueType.PERCENTILE,
        value: float = 50,
    ) -> Self:
        """Set midpoint color."""
        if isinstance(color, str):
            color = Color(color)
        self._points.insert(1, ColorScalePoint(value_type, value, color))
        return self

    def max_color(
        self,
        color: Color | str,
        value_type: ValueType = ValueType.MAX,
        value: float | None = None,
    ) -> Self:
        """Set maximum color."""
        if isinstance(color, str):
            color = Color(color)
        self._points.append(ColorScalePoint(value_type, value, color))
        return self

    def build(self) -> ColorScale:
        """Build the color scale."""
        # Determine type based on number of points
        if len(self._points) == 2:
            self._type = ColorScaleType.TWO_COLOR
        else:
            self._type = ColorScaleType.THREE_COLOR
        return ColorScale(type=self._type, points=tuple(self._points))


@dataclass
class DataBarBuilder:
    """Builder for data bars."""

    _fill_color: Color | str | None = field(default=None)
    _negative_color: Color | str | None = field(default=None)
    _border_color: Color | str | None = field(default=None)
    _min_type: ValueType = field(default=ValueType.AUTOMATIC)
    _max_type: ValueType = field(default=ValueType.AUTOMATIC)
    _min_value: float | None = field(default=None)
    _max_value: float | None = field(default=None)
    _show_value: bool = field(default=True)
    _gradient: bool = field(default=False)
    _axis_position: str = field(default="automatic")
    _direction: str = field(default="context")

    def fill(self, color: Color | str) -> Self:
        """Set fill color."""
        self._fill_color = color if isinstance(color, Color) else Color(color)
        return self

    def negative(self, color: Color | str) -> Self:
        """Set negative value color."""
        self._negative_color = color if isinstance(color, Color) else Color(color)
        return self

    def border(self, color: Color | str) -> Self:
        """Set border color."""
        self._border_color = color if isinstance(color, Color) else Color(color)
        return self

    def min_value(self, value: float, value_type: ValueType = ValueType.NUMBER) -> Self:
        """Set minimum value."""
        self._min_type = value_type
        self._min_value = value
        return self

    def max_value(self, value: float, value_type: ValueType = ValueType.NUMBER) -> Self:
        """Set maximum value."""
        self._max_type = value_type
        self._max_value = value
        return self

    def hide_value(self) -> Self:
        """Hide cell value, show only bar."""
        self._show_value = False
        return self

    def gradient(self, enable: bool = True) -> Self:
        """Enable gradient fill."""
        self._gradient = enable
        return self

    def axis_midpoint(self) -> Self:
        """Show axis at midpoint."""
        self._axis_position = "midpoint"
        return self

    def no_axis(self) -> Self:
        """Hide axis."""
        self._axis_position = "none"
        return self

    def left_to_right(self) -> Self:
        """Force left-to-right direction."""
        self._direction = "leftToRight"
        return self

    def right_to_left(self) -> Self:
        """Force right-to-left direction."""
        self._direction = "rightToLeft"
        return self

    def build(self) -> DataBar:
        """Build the data bar."""
        return DataBar(
            fill_color=self._fill_color,
            negative_color=self._negative_color,
            border_color=self._border_color,
            min_type=self._min_type,
            max_type=self._max_type,
            min_value=self._min_value,
            max_value=self._max_value,
            show_value=self._show_value,
            gradient_fill=self._gradient,
            axis_position=self._axis_position,
            direction=self._direction,
        )


@dataclass
class IconSetBuilder:
    """Builder for icon sets."""

    _icon_set: IconSetType = field(default=IconSetType.THREE_ARROWS)
    _thresholds: list[IconSetThreshold] = field(default_factory=list)
    _show_value: bool = field(default=True)
    _reverse: bool = field(default=False)

    def arrows_3(self) -> Self:
        """Use 3 arrows icon set."""
        self._icon_set = IconSetType.THREE_ARROWS
        return self

    def traffic_lights_3(self) -> Self:
        """Use 3 traffic lights icon set."""
        self._icon_set = IconSetType.THREE_TRAFFIC_LIGHTS_1
        return self

    def symbols_3(self) -> Self:
        """Use 3 symbols icon set."""
        self._icon_set = IconSetType.THREE_SYMBOLS
        return self

    def arrows_4(self) -> Self:
        """Use 4 arrows icon set."""
        self._icon_set = IconSetType.FOUR_ARROWS
        return self

    def ratings_5(self) -> Self:
        """Use 5 ratings icon set."""
        self._icon_set = IconSetType.FIVE_RATINGS
        return self

    def quarters_5(self) -> Self:
        """Use 5 quarters icon set."""
        self._icon_set = IconSetType.FIVE_QUARTERS
        return self

    def icon_set(self, set_type: IconSetType) -> Self:
        """Set icon set type."""
        self._icon_set = set_type
        return self

    def threshold(
        self,
        value: float,
        icon_index: int,
        value_type: ValueType = ValueType.PERCENT,
        gte: bool = True,
    ) -> Self:
        """Add a threshold."""
        self._thresholds.append(
            IconSetThreshold(
                value_type=value_type,
                value=value,
                icon_index=icon_index,
                gte=gte,
            )
        )
        return self

    def hide_value(self) -> Self:
        """Hide cell value, show only icons."""
        self._show_value = False
        return self

    def reverse(self) -> Self:
        """Reverse icon order."""
        self._reverse = True
        return self

    def build(self) -> IconSet:
        """Build the icon set."""
        return IconSet(
            icon_set=self._icon_set,
            thresholds=tuple(self._thresholds),
            show_value=self._show_value,
            reverse=self._reverse,
        )


@dataclass
class ValueRuleBuilder:
    """Builder for cell value rules (chained from ConditionalFormatBuilder)."""

    _parent: ConditionalFormatBuilder
    _operator: RuleOperator | None = field(default=None)
    _value: Any = field(default=None)
    _value2: Any = field(default=None)

    def less_than(self, value: Any) -> ValueRuleBuilder:
        """Value less than."""
        self._operator = RuleOperator.LESS_THAN
        self._value = value
        return self

    def less_than_or_equal(self, value: Any) -> ValueRuleBuilder:
        """Value less than or equal."""
        self._operator = RuleOperator.LESS_THAN_OR_EQUAL
        self._value = value
        return self

    def greater_than(self, value: Any) -> ValueRuleBuilder:
        """Value greater than."""
        self._operator = RuleOperator.GREATER_THAN
        self._value = value
        return self

    def greater_than_or_equal(self, value: Any) -> ValueRuleBuilder:
        """Value greater than or equal."""
        self._operator = RuleOperator.GREATER_THAN_OR_EQUAL
        self._value = value
        return self

    def equal_to(self, value: Any) -> ValueRuleBuilder:
        """Value equal to."""
        self._operator = RuleOperator.EQUAL
        self._value = value
        return self

    def not_equal_to(self, value: Any) -> ValueRuleBuilder:
        """Value not equal to."""
        self._operator = RuleOperator.NOT_EQUAL
        self._value = value
        return self

    def between(self, min_value: Any, max_value: Any) -> ValueRuleBuilder:
        """Value between min and max."""
        self._operator = RuleOperator.BETWEEN
        self._value = min_value
        self._value2 = max_value
        return self

    def less_than_formula(self, formula: str) -> ValueRuleBuilder:
        """Value less than formula result."""
        self._operator = RuleOperator.LESS_THAN
        self._value = formula
        return self

    def style(self, style: CellStyle | str) -> ConditionalFormatBuilder:
        """Apply style and return to parent builder."""
        rule = ConditionalRule(
            type=ConditionalRuleType.CELL_VALUE,
            operator=self._operator,
            value=self._value,
            value2=self._value2,
            style=style,
            priority=len(self._parent._rules) + 1,
        )
        self._parent._rules.append(rule)
        return self._parent


@dataclass
class ConditionalFormatBuilder:
    r"""Fluent builder for conditional formatting.

    Examples:
        # Budget status formatting
        budget_format = ConditionalFormatBuilder() \\
            .range("D2:D100") \\
            .when_value().less_than(0).style("danger") \\
            .when_value().less_than_formula("B2*0.1").style("warning") \\
            .otherwise().style("success") \\
            .build()

        # Color scale
        heat_map = ConditionalFormatBuilder() \\
            .range("E2:E100") \\
            .color_scale() \\
                .min_color("#63BE7B") \\
                .mid_color("#FFEB84", percentile=50) \\
                .max_color("#F8696B") \\
            .build()

        # Data bar
        expense_bars = ConditionalFormatBuilder() \\
            .range("C2:C100") \\
            .data_bar() \\
                .fill("#638EC6") \\
                .gradient() \\
            .build()

        # Icon set
        trend_icons = ConditionalFormatBuilder() \\
            .range("F2:F100") \\
            .icon_set() \\
                .arrows_3() \\
                .hide_value() \\
            .build()
    """

    _range: str = field(default="A1")
    _rules: list[ConditionalRule] = field(default_factory=list)

    # Nested builders
    _color_scale_builder: ColorScaleBuilder | None = field(default=None)
    _data_bar_builder: DataBarBuilder | None = field(default=None)
    _icon_set_builder: IconSetBuilder | None = field(default=None)

    def range(self, range_ref: str) -> Self:
        """Set the range for this conditional format."""
        self._range = range_ref
        return self

    # ========================================================================
    # Cell Value Rules
    # ========================================================================

    def when_value(self) -> ValueRuleBuilder:
        """Start a cell value rule."""
        return ValueRuleBuilder(_parent=self)

    def when_formula(self, formula: str, style: CellStyle | str) -> Self:
        """Add formula-based rule."""
        rule = ConditionalRule(
            type=ConditionalRuleType.FORMULA,
            formula=formula,
            style=style,
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    def otherwise(self) -> ValueRuleBuilder:
        """Add catch-all rule (uses formula that always matches)."""
        builder = ValueRuleBuilder(_parent=self)
        builder._operator = RuleOperator.NOT_EQUAL
        builder._value = "NEVER_MATCH_THIS_VALUE"
        return builder

    # ========================================================================
    # Color Scale
    # ========================================================================

    def color_scale(self) -> ColorScaleBuilder:
        """Start building a color scale."""
        self._color_scale_builder = ColorScaleBuilder()
        return self._color_scale_builder

    def red_yellow_green(self) -> Self:
        """Apply standard red-yellow-green color scale."""
        rule = ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.red_yellow_green(),
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    def green_yellow_red(self) -> Self:
        """Apply inverted green-yellow-red color scale."""
        rule = ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.green_yellow_red(),
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    def white_to_blue(self) -> Self:
        """Apply white to blue color scale."""
        rule = ConditionalRule(
            type=ConditionalRuleType.COLOR_SCALE,
            color_scale=ColorScale.white_to_blue(),
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    # ========================================================================
    # Data Bar
    # ========================================================================

    def data_bar(self) -> DataBarBuilder:
        """Start building a data bar."""
        self._data_bar_builder = DataBarBuilder()
        return self._data_bar_builder

    def default_data_bar(self) -> Self:
        """Apply default blue data bar."""
        rule = ConditionalRule(
            type=ConditionalRuleType.DATA_BAR,
            data_bar=DataBar.default(),
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    # ========================================================================
    # Icon Set
    # ========================================================================

    def icon_set(self) -> IconSetBuilder:
        """Start building an icon set."""
        self._icon_set_builder = IconSetBuilder()
        return self._icon_set_builder

    def three_arrows(self) -> Self:
        """Apply three arrows icon set."""
        rule = ConditionalRule(
            type=ConditionalRuleType.ICON_SET,
            icon_set=IconSet.three_arrows(),
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    def three_traffic_lights(self) -> Self:
        """Apply three traffic lights icon set."""
        rule = ConditionalRule(
            type=ConditionalRuleType.ICON_SET,
            icon_set=IconSet.three_traffic_lights(),
            priority=len(self._rules) + 1,
        )
        self._rules.append(rule)
        return self

    # ========================================================================
    # Top/Bottom Rules
    # ========================================================================

    def top(self, n: int, style: CellStyle | str, percent: bool = False) -> Self:
        """Add top N rule."""
        rule = ConditionalRule.top_n(
            n, style, percent=percent, priority=len(self._rules) + 1
        )
        self._rules.append(rule)
        return self

    def bottom(self, n: int, style: CellStyle | str, percent: bool = False) -> Self:
        """Add bottom N rule."""
        rule = ConditionalRule.bottom_n(
            n, style, percent=percent, priority=len(self._rules) + 1
        )
        self._rules.append(rule)
        return self

    # ========================================================================
    # Average Rules
    # ========================================================================

    def above_average(self, style: CellStyle | str) -> Self:
        """Add above average rule."""
        rule = ConditionalRule.above_average(style, priority=len(self._rules) + 1)
        self._rules.append(rule)
        return self

    def below_average(self, style: CellStyle | str) -> Self:
        """Add below average rule."""
        rule = ConditionalRule.below_average(style, priority=len(self._rules) + 1)
        self._rules.append(rule)
        return self

    # ========================================================================
    # Text Rules
    # ========================================================================

    def contains_text(self, text: str, style: CellStyle | str) -> Self:
        """Add text contains rule."""
        rule = ConditionalRule.contains_text(text, style, priority=len(self._rules) + 1)
        self._rules.append(rule)
        return self

    # ========================================================================
    # Duplicate/Unique Rules
    # ========================================================================

    def duplicates(self, style: CellStyle | str) -> Self:
        """Highlight duplicate values."""
        rule = ConditionalRule.duplicate(style, priority=len(self._rules) + 1)
        self._rules.append(rule)
        return self

    # ========================================================================
    # Build
    # ========================================================================

    def build(self) -> ConditionalFormat:
        """Build the ConditionalFormat object."""
        # Finalize nested builders if they exist
        if self._color_scale_builder:
            rule = ConditionalRule(
                type=ConditionalRuleType.COLOR_SCALE,
                color_scale=self._color_scale_builder.build(),
                priority=len(self._rules) + 1,
            )
            self._rules.append(rule)

        if self._data_bar_builder:
            rule = ConditionalRule(
                type=ConditionalRuleType.DATA_BAR,
                data_bar=self._data_bar_builder.build(),
                priority=len(self._rules) + 1,
            )
            self._rules.append(rule)

        if self._icon_set_builder:
            rule = ConditionalRule(
                type=ConditionalRuleType.ICON_SET,
                icon_set=self._icon_set_builder.build(),
                priority=len(self._rules) + 1,
            )
            self._rules.append(rule)

        return ConditionalFormat(range=self._range, rules=self._rules)


# ============================================================================
# Convenience Functions
# ============================================================================


def budget_variance_format(
    range_ref: str,
    danger_style: str = "danger",
    warning_style: str = "warning",
    success_style: str = "success",
) -> ConditionalFormat:
    """Create budget variance conditional format.

    Highlights:
    - Negative values (over budget) in red
    - Low remaining (<10% of budget) in yellow
    - Healthy remaining (>=10%) in green
    """
    return (
        ConditionalFormatBuilder()
        .range(range_ref)
        .when_value()
        .less_than(0)
        .style(danger_style)
        .when_formula("AND(D2>=0, D2<B2*0.1)", warning_style)
        .when_value()
        .greater_than_or_equal(0)
        .style(success_style)
        .build()
    )


def percent_scale_format(range_ref: str) -> ConditionalFormat:
    """Create percentage color scale (green at 0%, red at 100%)."""
    return ConditionalFormatBuilder().range(range_ref).green_yellow_red().build()


def expense_bar_format(range_ref: str) -> ConditionalFormat:
    """Create expense data bar format."""
    return ConditionalFormatBuilder().range(range_ref).default_data_bar().build()
