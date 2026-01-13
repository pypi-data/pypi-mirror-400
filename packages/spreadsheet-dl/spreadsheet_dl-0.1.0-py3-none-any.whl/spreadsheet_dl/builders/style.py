"""Fluent StyleBuilder for inline style creation.

Provides a chainable API for building cell styles with
font, alignment, fill, border, and number format configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from spreadsheet_dl.schema.styles import (
    Border,
    BorderEdge,
    Borders,
    BorderStyle,
    CellFill,
    CellStyle,
    Color,
    Font,
    FontWeight,
    NegativeFormat,
    NumberFormat,
    NumberFormatCategory,
    StrikethroughStyle,
    TextAlign,
    UnderlineStyle,
    VerticalAlign,
)


@dataclass
class StyleBuilder:
    r"""Fluent builder for cell styles.

    Examples:
        # Header style
        header_style = StyleBuilder("my_header") \\
            .font(family="Arial", size="12pt", weight="bold", color="#FFFFFF") \\
            .background("#1A3A5C") \\
            .align(horizontal="center", vertical="middle") \\
            .border_bottom("2pt", "solid", "#0F2540") \\
            .build()

        # Currency style
        currency_style = StyleBuilder("currency") \\
            .align(horizontal="right") \\
            .number_format(category="currency", symbol="$", negatives="parentheses") \\
            .build()

        # Warning style with inheritance
        warning_style = StyleBuilder("warning") \\
            .extends(base_style) \\
            .background("#FFEB9C") \\
            .font_color("#9C6500") \\
            .build()
    """

    name: str
    _extends: CellStyle | None = field(default=None)

    # Font
    _font_family: str | None = field(default=None)
    _font_fallback: list[str] = field(default_factory=list)
    _font_size: str | None = field(default=None)
    _font_weight: FontWeight | None = field(default=None)
    _font_color: Color | None = field(default=None)
    _italic: bool = field(default=False)
    _underline: UnderlineStyle = field(default=UnderlineStyle.NONE)
    _strikethrough: StrikethroughStyle = field(default=StrikethroughStyle.NONE)
    _letter_spacing: str | None = field(default=None)

    # Alignment
    _text_align: TextAlign | None = field(default=None)
    _vertical_align: VerticalAlign | None = field(default=None)
    _text_rotation: int = field(default=0)
    _wrap_text: bool = field(default=False)
    _shrink_to_fit: bool = field(default=False)
    _indent: int = field(default=0)

    # Background
    _background_color: Color | None = field(default=None)
    _fill: CellFill | None = field(default=None)

    # Borders
    _border_top: BorderEdge | None = field(default=None)
    _border_bottom: BorderEdge | None = field(default=None)
    _border_left: BorderEdge | None = field(default=None)
    _border_right: BorderEdge | None = field(default=None)

    # Padding
    _padding: str = field(default="2pt")

    # Number format
    _number_format: NumberFormat | str | None = field(default=None)
    _date_format: str | None = field(default=None)

    # Protection
    _locked: bool = field(default=True)
    _hidden: bool = field(default=False)

    # ========================================================================
    # Inheritance
    # ========================================================================

    def extends(self, parent: CellStyle) -> Self:
        """Inherit from parent style.

        Args:
            parent: Parent style to inherit from

        Returns:
            Self for chaining
        """
        self._extends = parent
        return self

    # ========================================================================
    # Font Configuration
    # ========================================================================

    def font(
        self,
        family: str | None = None,
        size: str | None = None,
        weight: str | FontWeight | None = None,
        color: str | Color | None = None,
        italic: bool = False,
        fallback: list[str] | None = None,
    ) -> Self:
        """Configure font properties.

        Args:
            family: Font family name
            size: Font size (e.g., "11pt", "14px")
            weight: Font weight ("normal", "bold", or FontWeight)
            color: Font color
            italic: Whether text is italic
            fallback: Fallback font families

        Returns:
            Self for chaining
        """
        if family:
            self._font_family = family
        if fallback:
            self._font_fallback = fallback
        if size:
            self._font_size = size
        if weight:
            if isinstance(weight, str):
                weight = FontWeight.from_name(weight)
            self._font_weight = weight
        if color:
            self._font_color = color if isinstance(color, Color) else Color(color)
        self._italic = italic
        return self

    def font_family(self, family: str, fallback: list[str] | None = None) -> Self:
        """Set font family."""
        self._font_family = family
        if fallback:
            self._font_fallback = fallback
        return self

    def font_size(self, size: str) -> Self:
        """Set font size."""
        self._font_size = size
        return self

    def font_weight(self, weight: str | FontWeight) -> Self:
        """Set font weight."""
        if isinstance(weight, str):
            weight = FontWeight.from_name(weight)
        self._font_weight = weight
        return self

    def font_color(self, color: str | Color) -> Self:
        """Set font color."""
        self._font_color = color if isinstance(color, Color) else Color(color)
        return self

    def bold(self) -> Self:
        """Make text bold."""
        self._font_weight = FontWeight.BOLD
        return self

    def italic(self) -> Self:
        """Make text italic."""
        self._italic = True
        return self

    def underline(self, style: str | UnderlineStyle = UnderlineStyle.SINGLE) -> Self:
        """Add underline."""
        if isinstance(style, str):
            style = UnderlineStyle(style.lower())
        self._underline = style
        return self

    def strikethrough(
        self, style: str | StrikethroughStyle = StrikethroughStyle.SINGLE
    ) -> Self:
        """Add strikethrough."""
        if isinstance(style, str):
            style = StrikethroughStyle(style.lower())
        self._strikethrough = style
        return self

    def letter_spacing(self, spacing: str) -> Self:
        """Set letter spacing."""
        self._letter_spacing = spacing
        return self

    # ========================================================================
    # Alignment Configuration
    # ========================================================================

    def align(
        self,
        horizontal: str | TextAlign | None = None,
        vertical: str | VerticalAlign | None = None,
    ) -> Self:
        """Configure text alignment.

        Args:
            horizontal: Horizontal alignment ("left", "center", "right", "justify")
            vertical: Vertical alignment ("top", "middle", "bottom")

        Returns:
            Self for chaining
        """
        if horizontal:
            if isinstance(horizontal, str):
                horizontal = TextAlign(horizontal.lower())
            self._text_align = horizontal
        if vertical:
            if isinstance(vertical, str):
                vertical = VerticalAlign(vertical.lower())
            self._vertical_align = vertical
        return self

    def align_left(self) -> Self:
        """Align text left."""
        self._text_align = TextAlign.LEFT
        return self

    def align_center(self) -> Self:
        """Align text center."""
        self._text_align = TextAlign.CENTER
        return self

    def align_right(self) -> Self:
        """Align text right."""
        self._text_align = TextAlign.RIGHT
        return self

    def align_top(self) -> Self:
        """Align text top."""
        self._vertical_align = VerticalAlign.TOP
        return self

    def align_middle(self) -> Self:
        """Align text middle."""
        self._vertical_align = VerticalAlign.MIDDLE
        return self

    def align_bottom(self) -> Self:
        """Align text bottom."""
        self._vertical_align = VerticalAlign.BOTTOM
        return self

    def rotate(self, degrees: int) -> Self:
        """Rotate text (-90 to 90 degrees)."""
        self._text_rotation = max(-90, min(90, degrees))
        return self

    def wrap(self) -> Self:
        """Enable text wrapping."""
        self._wrap_text = True
        return self

    def shrink(self) -> Self:
        """Shrink text to fit cell."""
        self._shrink_to_fit = True
        return self

    def indent_level(self, level: int) -> Self:
        """Set indent level."""
        self._indent = level
        return self

    # ========================================================================
    # Background Configuration
    # ========================================================================

    def background(self, color: str | Color) -> Self:
        """Set background color.

        Args:
            color: Background color

        Returns:
            Self for chaining
        """
        self._background_color = color if isinstance(color, Color) else Color(color)
        return self

    def fill_pattern(self, fill: CellFill) -> Self:
        """Set fill pattern or gradient.

        Args:
            fill: CellFill specification

        Returns:
            Self for chaining
        """
        self._fill = fill
        return self

    # ========================================================================
    # Border Configuration
    # ========================================================================

    def border(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set all borders.

        Args:
            width: Border width
            style: Border style
            color: Border color

        Returns:
            Self for chaining
        """
        if isinstance(style, str):
            style = BorderStyle[style.upper()]
        if isinstance(color, str):
            color = Color(color)

        edge = BorderEdge(style=style, width=width, color=color)
        self._border_top = edge
        self._border_bottom = edge
        self._border_left = edge
        self._border_right = edge
        return self

    def border_top(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set top border."""
        if isinstance(style, str):
            style = BorderStyle[style.upper()]
        if isinstance(color, str):
            color = Color(color)
        self._border_top = BorderEdge(style=style, width=width, color=color)
        return self

    def border_bottom(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set bottom border."""
        if isinstance(style, str):
            style = BorderStyle[style.upper()]
        if isinstance(color, str):
            color = Color(color)
        self._border_bottom = BorderEdge(style=style, width=width, color=color)
        return self

    def border_left(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set left border."""
        if isinstance(style, str):
            style = BorderStyle[style.upper()]
        if isinstance(color, str):
            color = Color(color)
        self._border_left = BorderEdge(style=style, width=width, color=color)
        return self

    def border_right(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set right border."""
        if isinstance(style, str):
            style = BorderStyle[style.upper()]
        if isinstance(color, str):
            color = Color(color)
        self._border_right = BorderEdge(style=style, width=width, color=color)
        return self

    def border_horizontal(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set top and bottom borders."""
        self.border_top(width, style, color)
        self.border_bottom(width, style, color)
        return self

    def border_vertical(
        self,
        width: str = "1pt",
        style: str | BorderStyle = BorderStyle.SOLID,
        color: str | Color = "#000000",
    ) -> Self:
        """Set left and right borders."""
        self.border_left(width, style, color)
        self.border_right(width, style, color)
        return self

    # ========================================================================
    # Padding Configuration
    # ========================================================================

    def padding(self, value: str) -> Self:
        """Set cell padding."""
        self._padding = value
        return self

    # ========================================================================
    # Number Format Configuration
    # ========================================================================

    def number_format(
        self,
        category: str | NumberFormatCategory = NumberFormatCategory.NUMBER,
        decimal_places: int = 2,
        use_thousands: bool = True,
        negatives: str | NegativeFormat = NegativeFormat.MINUS,
        symbol: str = "$",
        custom_code: str | None = None,
    ) -> Self:
        """Configure number format.

        Args:
            category: Format category ("number", "currency", "percentage", etc.)
            decimal_places: Number of decimal places
            use_thousands: Whether to use thousands separator
            negatives: Negative format ("minus", "parentheses", "red")
            symbol: Currency symbol
            custom_code: Custom format code (overrides other settings)

        Returns:
            Self for chaining
        """
        if custom_code:
            self._number_format = NumberFormat(
                category=NumberFormatCategory.CUSTOM,
                custom_code=custom_code,
            )
        else:
            if isinstance(category, str):
                category = NumberFormatCategory(category.lower())
            if isinstance(negatives, str):
                negatives = NegativeFormat(negatives.lower())

            self._number_format = NumberFormat(
                category=category,
                decimal_places=decimal_places,
                use_thousands_separator=use_thousands,
                negative_format=negatives,
                currency_symbol=symbol,
            )
        return self

    def currency(
        self,
        symbol: str = "$",
        decimal_places: int = 2,
        negatives: str | NegativeFormat = NegativeFormat.PARENTHESES,
    ) -> Self:
        """Configure as currency format."""
        return self.number_format(
            category=NumberFormatCategory.CURRENCY,
            decimal_places=decimal_places,
            negatives=negatives,
            symbol=symbol,
        )

    def accounting(
        self,
        symbol: str = "$",
        decimal_places: int = 2,
    ) -> Self:
        """Configure as accounting format."""
        return self.number_format(
            category=NumberFormatCategory.ACCOUNTING,
            decimal_places=decimal_places,
            negatives=NegativeFormat.PARENTHESES,
            symbol=symbol,
        )

    def percentage(self, decimal_places: int = 0) -> Self:
        """Configure as percentage format."""
        return self.number_format(
            category=NumberFormatCategory.PERCENTAGE,
            decimal_places=decimal_places,
        )

    def date_format(self, pattern: str = "YYYY-MM-DD") -> Self:
        """Set date format."""
        self._date_format = pattern
        return self

    # ========================================================================
    # Protection Configuration
    # ========================================================================

    def unlocked(self) -> Self:
        """Allow editing when sheet is protected."""
        self._locked = False
        return self

    def hide_formula(self) -> Self:
        """Hide formula when sheet is protected."""
        self._hidden = True
        return self

    # ========================================================================
    # Build
    # ========================================================================

    def build(self) -> CellStyle:
        """Build the CellStyle object.

        Returns:
            Configured CellStyle
        """
        # Start with parent style or defaults
        if self._extends:
            base_font = self._extends.font
            base_align = self._extends.text_align
            base_valign = self._extends.vertical_align
            base_bg = self._extends.background_color
            base_padding = self._extends.padding
        else:
            base_font = Font()
            base_align = TextAlign.LEFT
            base_valign = VerticalAlign.MIDDLE
            base_bg = None
            base_padding = "2pt"

        # Build font
        font = Font(
            family=self._font_family or base_font.family,
            fallback=self._font_fallback or base_font.fallback.copy(),
            size=self._font_size or base_font.size,
            weight=self._font_weight or base_font.weight,
            color=self._font_color or base_font.color,
            italic=self._italic or base_font.italic,
            underline=self._underline
            if self._underline != UnderlineStyle.NONE
            else base_font.underline,
            strikethrough=self._strikethrough
            if self._strikethrough != StrikethroughStyle.NONE
            else base_font.strikethrough,
            letter_spacing=self._letter_spacing or base_font.letter_spacing,
        )

        # Build borders
        borders = None
        if any(
            [
                self._border_top,
                self._border_bottom,
                self._border_left,
                self._border_right,
            ]
        ):
            borders = Borders(
                top=self._border_top,
                bottom=self._border_bottom,
                left=self._border_left,
                right=self._border_right,
            )

        # Convert BorderEdge to Border for backward compatibility
        border_top = (
            Border(
                width=self._border_top.width,
                style=self._border_top.style,
                color=self._border_top.color,
            )
            if self._border_top
            else None
        )

        border_bottom = (
            Border(
                width=self._border_bottom.width,
                style=self._border_bottom.style,
                color=self._border_bottom.color,
            )
            if self._border_bottom
            else None
        )

        border_left = (
            Border(
                width=self._border_left.width,
                style=self._border_left.style,
                color=self._border_left.color,
            )
            if self._border_left
            else None
        )

        border_right = (
            Border(
                width=self._border_right.width,
                style=self._border_right.style,
                color=self._border_right.color,
            )
            if self._border_right
            else None
        )

        return CellStyle(
            name=self.name,
            font=font,
            text_align=self._text_align or base_align,
            vertical_align=self._vertical_align or base_valign,
            text_rotation=self._text_rotation,
            wrap_text=self._wrap_text,
            shrink_to_fit=self._shrink_to_fit,
            indent=self._indent,
            background_color=self._background_color or base_bg,
            fill=self._fill,
            border_top=border_top,
            border_bottom=border_bottom,
            border_left=border_left,
            border_right=border_right,
            borders=borders,
            padding=self._padding or base_padding,
            number_format=self._number_format,
            date_format=self._date_format,
            locked=self._locked,
            hidden=self._hidden,
        )


# ============================================================================
# Convenience Functions
# ============================================================================


def header_style(
    name: str = "header",
    background: str = "#4472C4",
    font_color: str = "#FFFFFF",
    font_size: str = "11pt",
) -> CellStyle:
    """Create a standard header style."""
    return (
        StyleBuilder(name)
        .font(size=font_size, weight="bold", color=font_color)
        .background(background)
        .align(horizontal="center", vertical="middle")
        .border_bottom("2pt", "solid", background)
        .build()
    )


def currency_style(
    name: str = "currency",
    symbol: str = "$",
    negatives: str = "parentheses",
) -> CellStyle:
    """Create a currency style."""
    return (
        StyleBuilder(name)
        .align_right()
        .currency(symbol=symbol, negatives=negatives)
        .build()
    )


def percentage_style(name: str = "percentage", decimals: int = 0) -> CellStyle:
    """Create a percentage style."""
    return StyleBuilder(name).align_right().percentage(decimal_places=decimals).build()


def total_row_style(
    name: str = "total",
    background: str = "#D9E2F3",
) -> CellStyle:
    """Create a total row style."""
    return (
        StyleBuilder(name)
        .bold()
        .background(background)
        .border_top("2pt", "solid", "#4472C4")
        .build()
    )
