"""Comprehensive tests for schema/styles.py - targeting 90%+ coverage.

- Color class testing (creation, manipulation, WCAG)
- Font class testing (all properties and methods)
- Border classes testing (BorderEdge, Border, Borders)
- Fill classes testing (PatternFill, GradientFill, CellFill)
- NumberFormat testing (all categories and formats)
- Style classes testing (StyleDefinition, CellStyle)
- Theme class testing (variants, inheritance, composition)
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.schema.styles import (
    Border,
    BorderEdge,
    Borders,
    BorderStyle,
    CellFill,
    CellStyle,
    Color,
    ColorPalette,
    Font,
    FontWeight,
    GradientFill,
    GradientStop,
    GradientType,
    NegativeFormat,
    NumberFormat,
    NumberFormatCategory,
    PatternFill,
    PatternType,
    StyleDefinition,
    TextAlign,
    Theme,
    ThemeSchema,
    ThemeVariant,
    UnderlineStyle,
    VerticalAlign,
)

pytestmark = [pytest.mark.unit, pytest.mark.validation]


# ============================================================================
# Color Tests
# ============================================================================


class TestColor:
    """Comprehensive tests for Color class."""

    def test_color_from_hex_3char(self) -> None:
        """Test 3-character hex color normalization."""
        c = Color("#ABC")
        assert c.value == "#AABBCC"

    def test_color_from_hex_4char(self) -> None:
        """Test 4-character hex color with alpha normalization."""
        c = Color("#ABCD")
        assert c.value == "#AABBCCDD"

    def test_color_from_hex_6char(self) -> None:
        """Test 6-character hex color."""
        c = Color("#AABBCC")
        assert c.value == "#AABBCC"

    def test_color_from_hex_8char(self) -> None:
        """Test 8-character hex color with alpha."""
        c = Color("#AABBCCDD")
        assert c.value == "#AABBCCDD"

    def test_color_invalid_hex_raises(self) -> None:
        """Test invalid hex color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            Color("#GGGGGG")

    def test_color_from_hex_classmethod(self) -> None:
        """Test Color.from_hex() classmethod."""
        c1 = Color.from_hex("#ABC")
        assert c1.value == "#AABBCC"
        c2 = Color.from_hex("ABC")
        assert c2.value == "#AABBCC"

    def test_color_from_rgb(self) -> None:
        """Test Color.from_rgb() creation."""
        c = Color.from_rgb(255, 128, 64)
        assert c.to_rgb() == (255, 128, 64)

    def test_color_from_rgb_with_alpha(self) -> None:
        """Test Color.from_rgb() with alpha."""
        c = Color.from_rgb(255, 128, 64, 128)
        r, g, b, a = c.to_rgba()
        assert (r, g, b, a) == (255, 128, 64, 128)

    def test_color_from_rgb_invalid_raises(self) -> None:
        """Test invalid RGB values raise ValueError."""
        with pytest.raises(ValueError, match="RGB values must be 0-255"):
            Color.from_rgb(256, 0, 0)
        with pytest.raises(ValueError, match="RGB values must be 0-255"):
            Color.from_rgb(0, -1, 0)
        with pytest.raises(ValueError, match="Alpha must be 0-255"):
            Color.from_rgb(128, 128, 128, 300)

    def test_color_from_hsl(self) -> None:
        """Test Color.from_hsl() creation."""
        c = Color.from_hsl(120, 50, 50)  # Green
        hue, saturation, lightness = c.to_hsl()
        assert abs(hue - 120) < 5  # Allow small tolerance
        assert abs(saturation - 50) < 5
        assert abs(lightness - 50) < 5

    def test_color_from_hsl_with_alpha(self) -> None:
        """Test Color.from_hsl() with alpha."""
        c = Color.from_hsl(240, 100, 50, 50)  # Blue with 50% alpha
        assert 0 <= c.alpha <= 1

    def test_color_from_name_valid(self) -> None:
        """Test Color.from_name() with valid names."""
        red = Color.from_name("red")
        assert red.value == "#FF0000"
        blue = Color.from_name("blue")
        assert blue.value == "#0000FF"
        steelblue = Color.from_name("steelblue")
        assert steelblue.value == "#4682B4"

    def test_color_from_name_case_insensitive(self) -> None:
        """Test Color.from_name() is case-insensitive."""
        c1 = Color.from_name("RED")
        c2 = Color.from_name("red")
        c3 = Color.from_name("Red")
        assert c1.value == c2.value == c3.value

    def test_color_from_name_invalid_raises(self) -> None:
        """Test invalid color name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown color name"):
            Color.from_name("notacolor")

    def test_color_to_rgb(self) -> None:
        """Test Color.to_rgb() conversion."""
        c = Color("#FF8040")
        assert c.to_rgb() == (255, 128, 64)

    def test_color_to_rgba(self) -> None:
        """Test Color.to_rgba() conversion."""
        c1 = Color("#FF8040")
        assert c1.to_rgba() == (255, 128, 64, 255)
        c2 = Color("#FF804080")
        assert c2.to_rgba() == (255, 128, 64, 128)

    def test_color_to_hsl(self) -> None:
        """Test Color.to_hsl() conversion."""
        c = Color.from_rgb(255, 0, 0)  # Red
        hue, saturation, _lightness = c.to_hsl()
        assert abs(hue - 0) < 5
        assert saturation > 90

    def test_color_alpha_property(self) -> None:
        """Test Color.alpha property."""
        c1 = Color("#FF0000")
        assert c1.alpha == 1.0
        c2 = Color("#FF000080")
        assert abs(c2.alpha - 0.5) < 0.01

    def test_color_with_alpha(self) -> None:
        """Test Color.with_alpha() method."""
        c = Color("#FF0000")
        c_alpha = c.with_alpha(0.5)
        assert abs(c_alpha.alpha - 0.5) < 0.01

    def test_color_lighten(self) -> None:
        """Test Color.lighten() method."""
        c = Color("#808080")
        lighter = c.lighten(0.5)
        assert lighter.to_hsl()[2] > c.to_hsl()[2]

    def test_color_darken(self) -> None:
        """Test Color.darken() method."""
        c = Color("#808080")
        darker = c.darken(0.5)
        assert darker.to_hsl()[2] < c.to_hsl()[2]

    def test_color_saturate(self) -> None:
        """Test Color.saturate() method."""
        c = Color.from_hsl(120, 30, 50)
        saturated = c.saturate(0.5)
        assert saturated.to_hsl()[1] > c.to_hsl()[1]

    def test_color_desaturate(self) -> None:
        """Test Color.desaturate() method."""
        c = Color.from_hsl(120, 80, 50)
        desaturated = c.desaturate(0.5)
        assert desaturated.to_hsl()[1] < c.to_hsl()[1]

    def test_color_invert(self) -> None:
        """Test Color.invert() method."""
        c = Color("#FF0000")
        inverted = c.invert()
        assert inverted.to_rgb() == (0, 255, 255)

    def test_color_grayscale(self) -> None:
        """Test Color.grayscale() method."""
        c = Color("#FF8040")
        gray = c.grayscale()
        r, g, b = gray.to_rgb()
        assert r == g == b

    def test_color_luminance(self) -> None:
        """Test Color.luminance() calculation."""
        white = Color("#FFFFFF")
        black = Color("#000000")
        assert white.luminance() > 0.9
        assert black.luminance() < 0.1

    def test_color_contrast_ratio(self) -> None:
        """Test Color.contrast_ratio() calculation."""
        white = Color("#FFFFFF")
        black = Color("#000000")
        ratio = white.contrast_ratio(black)
        assert ratio == 21.0

    def test_color_is_wcag_aa(self) -> None:
        """Test Color.is_wcag_aa() check."""
        white = Color("#FFFFFF")
        black = Color("#000000")
        assert black.is_wcag_aa(white, large_text=False)
        assert black.is_wcag_aa(white, large_text=True)

    def test_color_is_wcag_aaa(self) -> None:
        """Test Color.is_wcag_aaa() check."""
        white = Color("#FFFFFF")
        black = Color("#000000")
        assert black.is_wcag_aaa(white, large_text=False)
        assert black.is_wcag_aaa(white, large_text=True)

    def test_color_str(self) -> None:
        """Test Color.__str__() method."""
        c = Color("#AABBCC")
        assert str(c) == "#AABBCC"

    def test_color_equality(self) -> None:
        """Test Color.__eq__() method."""
        c1 = Color("#AABBCC")
        c2 = Color("#aabbcc")
        c3 = Color("#DDEEFF")
        assert c1 == c2
        assert c1 != c3

    def test_color_hash(self) -> None:
        """Test Color.__hash__() method."""
        c1 = Color("#AABBCC")
        c2 = Color("#aabbcc")
        assert hash(c1) == hash(c2)


# ============================================================================
# ColorPalette Tests
# ============================================================================


class TestColorPalette:
    """Tests for ColorPalette class."""

    def test_palette_defaults(self) -> None:
        """Test ColorPalette default values."""
        palette = ColorPalette()
        assert palette.primary.value == "#4472C4"
        assert palette.success.value == "#70AD47"

    def test_palette_get_standard_color(self) -> None:
        """Test getting standard colors from palette."""
        palette = ColorPalette()
        primary = palette.get("primary")
        assert primary is not None
        assert primary.value == "#4472C4"

    def test_palette_get_with_hyphens(self) -> None:
        """Test getting colors with hyphens (normalized to underscores)."""
        palette = ColorPalette()
        color = palette.get("primary-light")
        assert color is not None
        assert color == palette.primary_light

    def test_palette_get_custom_color(self) -> None:
        """Test getting custom colors."""
        palette = ColorPalette()
        palette.set("brand", Color("#123456"))
        brand = palette.get("brand")
        assert brand is not None
        assert brand.value == "#123456"

    def test_palette_get_nonexistent(self) -> None:
        """Test getting non-existent color returns None."""
        palette = ColorPalette()
        result = palette.get("nonexistent")
        assert result is None

    def test_palette_set_custom_color(self) -> None:
        """Test setting custom colors."""
        palette = ColorPalette()
        custom = Color("#ABCDEF")
        palette.set("my_color", custom)
        assert palette.custom["my_color"] == custom

    def test_palette_generate_scale(self) -> None:
        """Test generating color scale."""
        palette = ColorPalette()
        base = Color("#4472C4")
        scale = palette.generate_scale(base, "blue")
        assert len(scale) == 5
        assert "blue_100" in scale
        assert "blue_500" in scale
        assert "blue_900" in scale

    def test_palette_to_dict(self) -> None:
        """Test ColorPalette.to_dict() conversion."""
        palette = ColorPalette()
        palette.set("custom", Color("#123456"))
        result = palette.to_dict()
        assert "primary" in result
        assert "custom" in result
        assert result["custom"] == "#123456"


# ============================================================================
# FontWeight Tests
# ============================================================================


class TestFontWeight:
    """Tests for FontWeight enum."""

    def test_fontweight_from_name_valid(self) -> None:
        """Test FontWeight.from_name() with valid names."""
        assert FontWeight.from_name("bold") == FontWeight.BOLD
        assert FontWeight.from_name("normal") == FontWeight.NORMAL
        assert FontWeight.from_name("light") == FontWeight.LIGHT

    def test_fontweight_from_name_aliases(self) -> None:
        """Test FontWeight.from_name() with aliases."""
        assert FontWeight.from_name("regular") == FontWeight.NORMAL
        assert FontWeight.from_name("semibold") == FontWeight.SEMI_BOLD
        assert FontWeight.from_name("heavy") == FontWeight.BLACK

    def test_fontweight_from_name_case_insensitive(self) -> None:
        """Test FontWeight.from_name() is case-insensitive."""
        assert FontWeight.from_name("BOLD") == FontWeight.BOLD
        assert FontWeight.from_name("Bold") == FontWeight.BOLD

    def test_fontweight_from_name_with_separators(self) -> None:
        """Test FontWeight.from_name() handles separators."""
        assert FontWeight.from_name("semi-bold") == FontWeight.SEMI_BOLD
        assert FontWeight.from_name("semi_bold") == FontWeight.SEMI_BOLD

    def test_fontweight_from_name_unknown(self) -> None:
        """Test FontWeight.from_name() with unknown name returns NORMAL."""
        assert FontWeight.from_name("unknown") == FontWeight.NORMAL

    def test_fontweight_is_bold_property(self) -> None:
        """Test FontWeight.is_bold property."""
        assert FontWeight.BOLD.is_bold
        assert FontWeight.SEMI_BOLD.is_bold
        assert FontWeight.EXTRA_BOLD.is_bold
        assert not FontWeight.NORMAL.is_bold
        assert not FontWeight.LIGHT.is_bold


# ============================================================================
# Font Tests
# ============================================================================


class TestFont:
    """Tests for Font class."""

    def test_font_defaults(self) -> None:
        """Test Font default values."""
        font = Font()
        assert font.family == "Liberation Sans"
        assert font.size == "10pt"
        assert font.weight == FontWeight.NORMAL
        assert not font.italic

    def test_font_with_size(self) -> None:
        """Test Font.with_size() method."""
        font = Font()
        larger = font.with_size("14pt")
        assert larger.size == "14pt"
        assert larger.family == font.family
        assert larger.weight == font.weight

    def test_font_with_weight(self) -> None:
        """Test Font.with_weight() method."""
        font = Font()
        bold = font.with_weight(FontWeight.BOLD)
        assert bold.weight == FontWeight.BOLD
        assert bold.family == font.family
        assert bold.size == font.size

    def test_font_is_bold_property(self) -> None:
        """Test Font.is_bold property."""
        normal = Font()
        bold = Font(weight=FontWeight.BOLD)
        assert not normal.is_bold
        assert bold.is_bold

    def test_font_family_string(self) -> None:
        """Test Font.font_family_string property."""
        font = Font(family="Arial", fallback=["Helvetica", "sans-serif"])
        assert font.font_family_string == "Arial, Helvetica, sans-serif"

    def test_font_family_string_with_spaces(self) -> None:
        """Test Font.font_family_string with spaces in names."""
        font = Font(family="Times New Roman", fallback=["Times", "serif"])
        assert '"Times New Roman"' in font.font_family_string

    def test_font_to_dict(self) -> None:
        """Test Font.to_dict() conversion."""
        font = Font(
            family="Arial",
            size="12pt",
            weight=FontWeight.BOLD,
            color=Color("#FF0000"),
            italic=True,
            underline=UnderlineStyle.SINGLE,
        )
        result = font.to_dict()
        assert result["family"] == "Arial"
        assert result["size"] == "12pt"
        assert result["weight"] == "700"
        assert result["italic"] is True
        assert result["underline"] == "single"

    def test_font_to_dict_minimal(self) -> None:
        """Test Font.to_dict() with minimal attributes."""
        font = Font()
        result = font.to_dict()
        assert "underline" not in result  # Should be omitted for NONE
        assert "strikethrough" not in result


# ============================================================================
# Border Tests
# ============================================================================


class TestBorderEdge:
    """Tests for BorderEdge class."""

    def test_borderedge_defaults(self) -> None:
        """Test BorderEdge default values."""
        edge = BorderEdge()
        assert edge.style == BorderStyle.NONE
        assert edge.width == "1pt"

    def test_borderedge_to_odf(self) -> None:
        """Test BorderEdge.to_odf() conversion."""
        edge = BorderEdge(style=BorderStyle.SOLID, width="2pt", color=Color("#FF0000"))
        assert edge.to_odf() == "2pt solid #FF0000"

    def test_borderedge_to_odf_none(self) -> None:
        """Test BorderEdge.to_odf() with NONE style."""
        edge = BorderEdge(style=BorderStyle.NONE)
        assert edge.to_odf() == "none"

    def test_borderedge_str(self) -> None:
        """Test BorderEdge.__str__() method."""
        edge = BorderEdge(style=BorderStyle.DASHED, width="1pt", color=Color("#000000"))
        assert str(edge) == "1pt dashed #000000"

    def test_borderedge_parse_valid(self) -> None:
        """Test BorderEdge.parse() with valid string."""
        edge = BorderEdge.parse("2pt SOLID #FF0000")
        assert edge.width == "2pt"
        assert edge.style == BorderStyle.SOLID
        assert edge.color.value == "#FF0000"

    def test_borderedge_parse_none(self) -> None:
        """Test BorderEdge.parse() with 'none'."""
        edge = BorderEdge.parse("none")
        assert edge.style == BorderStyle.NONE

    def test_borderedge_parse_minimal(self) -> None:
        """Test BorderEdge.parse() with minimal string."""
        edge = BorderEdge.parse("1pt solid")
        assert edge.width == "1pt"
        assert edge.style == BorderStyle.SOLID
        assert edge.color.value == "#000000"

    def test_borderedge_parse_invalid_raises(self) -> None:
        """Test BorderEdge.parse() with invalid string."""
        with pytest.raises(ValueError, match="Invalid border string"):
            BorderEdge.parse("invalid")


class TestBorder:
    """Tests for Border class (backward compatible)."""

    def test_border_defaults(self) -> None:
        """Test Border default values."""
        border = Border()
        assert border.width == "1px"
        assert border.style == BorderStyle.SOLID

    def test_border_to_odf(self) -> None:
        """Test Border.to_odf() conversion."""
        border = Border(width="2px", style=BorderStyle.DASHED, color=Color("#0000FF"))
        assert border.to_odf() == "2px dashed #0000FF"

    def test_border_from_string(self) -> None:
        """Test Border.from_string() parsing."""
        border = Border.from_string("3px DOTTED #00FF00")
        assert border.width == "3px"
        assert border.style == BorderStyle.DOTTED
        assert border.color.value == "#00FF00"

    def test_border_to_edge(self) -> None:
        """Test Border.to_edge() conversion."""
        border = Border(width="2pt", style=BorderStyle.THICK, color=Color("#FF0000"))
        edge = border.to_edge()
        assert edge.width == "2pt"
        assert edge.style == BorderStyle.THICK
        assert edge.color.value == "#FF0000"


class TestBorders:
    """Tests for Borders class."""

    def test_borders_defaults(self) -> None:
        """Test Borders default values."""
        borders = Borders()
        assert borders.top is None
        assert borders.bottom is None

    def test_borders_none(self) -> None:
        """Test Borders.none() factory."""
        borders = Borders.none()
        assert borders.top is None
        assert borders.bottom is None
        assert borders.left is None
        assert borders.right is None

    def test_borders_all(self) -> None:
        """Test Borders.all() factory."""
        borders = Borders.all(BorderStyle.THICK, "2pt", Color("#FF0000"))
        assert borders.top is not None
        assert borders.bottom is not None
        assert borders.left is not None
        assert borders.right is not None
        assert borders.top.width == "2pt"

    def test_borders_box(self) -> None:
        """Test Borders.box() factory (alias for all)."""
        borders = Borders.box(BorderStyle.MEDIUM)
        assert borders.top is not None
        assert borders.bottom is not None

    def test_borders_horizontal(self) -> None:
        """Test Borders.horizontal() factory."""
        borders = Borders.horizontal(BorderStyle.THIN, "1pt")
        assert borders.top is not None
        assert borders.bottom is not None
        assert borders.left is None
        assert borders.right is None

    def test_borders_vertical(self) -> None:
        """Test Borders.vertical() factory."""
        borders = Borders.vertical(BorderStyle.THIN, "1pt")
        assert borders.left is not None
        assert borders.right is not None
        assert borders.top is None
        assert borders.bottom is None

    def test_borders_bottom_only(self) -> None:
        """Test Borders.bottom_only() factory."""
        borders = Borders.bottom_only(BorderStyle.DOUBLE, "2pt", Color("#0000FF"))
        assert borders.bottom is not None
        assert borders.top is None
        assert borders.bottom.style == BorderStyle.DOUBLE

    def test_borders_top_only(self) -> None:
        """Test Borders.top_only() factory."""
        borders = Borders.top_only(BorderStyle.THICK, "3pt")
        assert borders.top is not None
        assert borders.bottom is None
        assert borders.top.style == BorderStyle.THICK

    def test_borders_to_dict(self) -> None:
        """Test Borders.to_dict() conversion."""
        borders = Borders.all(BorderStyle.THIN, "1pt", Color("#000000"))
        result = borders.to_dict()
        assert "top" in result
        assert "bottom" in result
        assert "left" in result
        assert "right" in result


# ============================================================================
# Fill Tests
# ============================================================================


class TestPatternFill:
    """Tests for PatternFill class."""

    def test_patternfill_defaults(self) -> None:
        """Test PatternFill default values."""
        fill = PatternFill()
        assert fill.pattern_type == PatternType.SOLID
        assert fill.foreground_color.value == "#000000"
        assert fill.background_color.value == "#FFFFFF"


class TestGradientFill:
    """Tests for GradientFill class."""

    def test_gradientfill_defaults(self) -> None:
        """Test GradientFill default values."""
        fill = GradientFill()
        assert fill.type == GradientType.LINEAR
        assert fill.angle == 0.0
        assert fill.center_x == 0.5
        assert fill.center_y == 0.5

    def test_gradientfill_with_stops(self) -> None:
        """Test GradientFill with stops."""
        stops = (
            GradientStop(0.0, Color("#FFFFFF")),
            GradientStop(1.0, Color("#000000")),
        )
        fill = GradientFill(type=GradientType.RADIAL, stops=stops)
        assert len(fill.stops) == 2
        assert fill.stops[0].position == 0.0


class TestCellFill:
    """Tests for CellFill class."""

    def test_cellfill_defaults(self) -> None:
        """Test CellFill default values."""
        fill = CellFill()
        assert fill.solid_color is None
        assert fill.pattern is None
        assert fill.gradient is None
        assert fill.opacity == 1.0

    def test_cellfill_solid(self) -> None:
        """Test CellFill.solid() factory."""
        color = Color("#FF0000")
        fill = CellFill.solid(color)
        assert fill.solid_color == color

    def test_cellfill_from_color_object(self) -> None:
        """Test CellFill.from_color() with Color object."""
        color = Color("#00FF00")
        fill = CellFill.from_color(color)
        assert fill.solid_color == color

    def test_cellfill_from_color_string(self) -> None:
        """Test CellFill.from_color() with string."""
        fill = CellFill.from_color("#0000FF")
        assert fill.solid_color is not None
        assert fill.solid_color.value == "#0000FF"

    def test_cellfill_to_color_solid(self) -> None:
        """Test CellFill.to_color() with solid fill."""
        fill = CellFill.solid(Color("#FF0000"))
        color = fill.to_color()
        assert color is not None
        assert color.value == "#FF0000"

    def test_cellfill_to_color_pattern(self) -> None:
        """Test CellFill.to_color() with pattern fill."""
        pattern = PatternFill(
            pattern_type=PatternType.LIGHT_GRID, foreground_color=Color("#00FF00")
        )
        fill = CellFill(pattern=pattern)
        color = fill.to_color()
        assert color is not None
        assert color.value == "#00FF00"

    def test_cellfill_to_color_gradient(self) -> None:
        """Test CellFill.to_color() with gradient fill."""
        stops = (
            GradientStop(0.0, Color("#FFFFFF")),
            GradientStop(1.0, Color("#000000")),
        )
        gradient = GradientFill(stops=stops)
        fill = CellFill(gradient=gradient)
        color = fill.to_color()
        assert color is not None
        assert color.value == "#FFFFFF"

    def test_cellfill_to_color_empty(self) -> None:
        """Test CellFill.to_color() with no fill returns None."""
        fill = CellFill()
        assert fill.to_color() is None


# ============================================================================
# NumberFormat Tests
# ============================================================================


class TestNumberFormat:
    """Tests for NumberFormat class."""

    def test_numberformat_defaults(self) -> None:
        """Test NumberFormat default values."""
        fmt = NumberFormat()
        assert fmt.category == NumberFormatCategory.GENERAL
        assert fmt.decimal_places == 2
        assert fmt.use_thousands_separator is True

    def test_numberformat_general(self) -> None:
        """Test GENERAL format code."""
        fmt = NumberFormat(category=NumberFormatCategory.GENERAL)
        assert fmt.to_format_code() == "General"

    def test_numberformat_text(self) -> None:
        """Test TEXT format code."""
        fmt = NumberFormat(category=NumberFormatCategory.TEXT)
        assert fmt.to_format_code() == "@"

    def test_numberformat_percentage(self) -> None:
        """Test PERCENTAGE format code."""
        fmt = NumberFormat(category=NumberFormatCategory.PERCENTAGE, decimal_places=1)
        assert fmt.to_format_code() == "0.0%"

    def test_numberformat_percentage_no_decimals(self) -> None:
        """Test PERCENTAGE format with no decimals."""
        fmt = NumberFormat(category=NumberFormatCategory.PERCENTAGE, decimal_places=0)
        assert fmt.to_format_code() == "0%"

    def test_numberformat_scientific(self) -> None:
        """Test SCIENTIFIC format code."""
        fmt = NumberFormat(category=NumberFormatCategory.SCIENTIFIC, decimal_places=2)
        assert fmt.to_format_code() == "0.00E+00"

    def test_numberformat_scientific_no_decimals(self) -> None:
        """Test SCIENTIFIC format with no decimals."""
        fmt = NumberFormat(category=NumberFormatCategory.SCIENTIFIC, decimal_places=0)
        assert fmt.to_format_code() == "0E+00"

    def test_numberformat_number_with_thousands(self) -> None:
        """Test NUMBER format with thousands separator."""
        fmt = NumberFormat(
            category=NumberFormatCategory.NUMBER,
            decimal_places=2,
            use_thousands_separator=True,
        )
        code = fmt.to_format_code()
        assert "#,##0.00" in code

    def test_numberformat_number_negative_minus(self) -> None:
        """Test NUMBER format with minus negative format."""
        fmt = NumberFormat(
            category=NumberFormatCategory.NUMBER, negative_format=NegativeFormat.MINUS
        )
        code = fmt.to_format_code()
        assert code.startswith("#,##0.00;-")

    def test_numberformat_number_negative_parentheses(self) -> None:
        """Test NUMBER format with parentheses negative format."""
        fmt = NumberFormat(
            category=NumberFormatCategory.NUMBER,
            negative_format=NegativeFormat.PARENTHESES,
        )
        code = fmt.to_format_code()
        assert "(#,##0.00)" in code

    def test_numberformat_number_negative_red(self) -> None:
        """Test NUMBER format with red negative format."""
        fmt = NumberFormat(
            category=NumberFormatCategory.NUMBER, negative_format=NegativeFormat.RED
        )
        code = fmt.to_format_code()
        assert "[Red]" in code

    def test_numberformat_number_negative_red_parentheses(self) -> None:
        """Test NUMBER format with red parentheses negative format."""
        fmt = NumberFormat(
            category=NumberFormatCategory.NUMBER,
            negative_format=NegativeFormat.RED_PARENTHESES,
        )
        code = fmt.to_format_code()
        assert "[Red](" in code

    def test_numberformat_currency_before(self) -> None:
        """Test CURRENCY format with symbol before."""
        fmt = NumberFormat(
            category=NumberFormatCategory.CURRENCY,
            currency_symbol="$",
            currency_position="before",
            decimal_places=2,
        )
        code = fmt.to_format_code()
        assert code.startswith("$#,##0.00")

    def test_numberformat_currency_after(self) -> None:
        """Test CURRENCY format with symbol after."""
        fmt = NumberFormat(
            category=NumberFormatCategory.CURRENCY,
            currency_symbol="€",
            currency_position="after",
            decimal_places=2,
        )
        code = fmt.to_format_code()
        assert "€" in code
        assert code.startswith("#,##0.00")

    def test_numberformat_currency_with_spacing(self) -> None:
        """Test CURRENCY format with spacing."""
        fmt = NumberFormat(
            category=NumberFormatCategory.CURRENCY,
            currency_symbol="$",
            currency_spacing=True,
        )
        code = fmt.to_format_code()
        assert "$ " in code

    def test_numberformat_accounting(self) -> None:
        """Test ACCOUNTING format."""
        fmt = NumberFormat(category=NumberFormatCategory.ACCOUNTING)
        code = fmt.to_format_code()
        assert "$" in code

    def test_numberformat_date(self) -> None:
        """Test DATE format."""
        fmt = NumberFormat(
            category=NumberFormatCategory.DATE, date_pattern="YYYY-MM-DD"
        )
        code = fmt.to_format_code()
        assert "yyyy-mm-dd" in code.lower()

    def test_numberformat_time(self) -> None:
        """Test TIME format."""
        fmt = NumberFormat(category=NumberFormatCategory.TIME, time_pattern="HH:MM:SS")
        code = fmt.to_format_code()
        assert "hh:mm:ss" in code.lower()

    def test_numberformat_time_12hour(self) -> None:
        """Test TIME format with 12-hour."""
        fmt = NumberFormat(
            category=NumberFormatCategory.TIME,
            time_pattern="HH:MM:SS",
            use_12_hour=True,
        )
        code = fmt.to_format_code()
        assert "AM/PM" in code

    def test_numberformat_datetime(self) -> None:
        """Test DATETIME format."""
        fmt = NumberFormat(category=NumberFormatCategory.DATETIME)
        code = fmt.to_format_code()
        assert "yyyy" in code.lower()
        assert "hh" in code.lower()

    def test_numberformat_fraction(self) -> None:
        """Test FRACTION format."""
        fmt = NumberFormat(category=NumberFormatCategory.FRACTION)
        assert fmt.to_format_code() == "# ?/?"

    def test_numberformat_custom_code(self) -> None:
        """Test custom format code."""
        fmt = NumberFormat(custom_code="0.000")
        assert fmt.to_format_code() == "0.000"


# ============================================================================
# Style Tests
# ============================================================================


class TestStyleDefinition:
    """Tests for StyleDefinition class."""

    def test_styledef_defaults(self) -> None:
        """Test StyleDefinition default values."""
        style = StyleDefinition(name="test")
        assert style.name == "test"
        assert style.extends is None
        assert style.includes == []

    def test_styledef_with_inheritance(self) -> None:
        """Test StyleDefinition with inheritance."""
        style = StyleDefinition(name="child", extends="parent")
        assert style.extends == "parent"

    def test_styledef_with_traits(self) -> None:
        """Test StyleDefinition with trait composition."""
        style = StyleDefinition(name="styled", includes=["bold", "centered"])
        assert len(style.includes) == 2


class TestCellStyle:
    """Tests for CellStyle class."""

    def test_cellstyle_defaults(self) -> None:
        """Test CellStyle default values."""
        style = CellStyle(name="default")
        assert style.name == "default"
        assert style.text_align == TextAlign.LEFT
        assert style.vertical_align == VerticalAlign.MIDDLE
        assert style.wrap_text is False

    def test_cellstyle_get_effective_borders_from_borders(self) -> None:
        """Test get_effective_borders() with Borders object."""
        borders = Borders.all(BorderStyle.THIN)
        style = CellStyle(name="test", borders=borders)
        effective = style.get_effective_borders()
        assert effective.top is not None

    def test_cellstyle_get_effective_borders_from_individual(self) -> None:
        """Test get_effective_borders() with individual borders."""
        style = CellStyle(
            name="test",
            border_top=Border(style=BorderStyle.THICK),
            border_bottom=Border(style=BorderStyle.THIN),
        )
        effective = style.get_effective_borders()
        assert effective.top is not None
        assert effective.bottom is not None

    def test_cellstyle_get_effective_fill_from_fill(self) -> None:
        """Test get_effective_fill() with CellFill."""
        fill = CellFill.solid(Color("#FF0000"))
        style = CellStyle(name="test", fill=fill)
        effective = style.get_effective_fill()
        assert effective is not None
        assert effective.solid_color is not None

    def test_cellstyle_get_effective_fill_from_background_color(self) -> None:
        """Test get_effective_fill() with background_color."""
        style = CellStyle(name="test", background_color=Color("#00FF00"))
        effective = style.get_effective_fill()
        assert effective is not None
        assert effective.solid_color is not None

    def test_cellstyle_get_effective_fill_none(self) -> None:
        """Test get_effective_fill() with no fill."""
        style = CellStyle(name="test")
        assert style.get_effective_fill() is None

    def test_cellstyle_with_overrides(self) -> None:
        """Test CellStyle.with_overrides() method."""
        base = CellStyle(name="base", font=Font(size="10pt"))
        modified = base.with_overrides(font_size="14pt", text_align=TextAlign.CENTER)
        assert modified.font.size == "14pt"
        assert modified.text_align == TextAlign.CENTER
        assert base.font.size == "10pt"  # Original unchanged

    def test_cellstyle_merge_with(self) -> None:
        """Test CellStyle.merge_with() method."""
        parent = CellStyle(
            name="parent", font=Font(size="12pt", weight=FontWeight.BOLD)
        )
        child = CellStyle(name="child", font=Font(size="14pt"))
        merged = child.merge_with(parent)
        assert merged.name == "child"

    def test_cellstyle_to_dict(self) -> None:
        """Test CellStyle.to_dict() conversion."""
        style = CellStyle(
            name="test",
            font=Font(size="12pt"),
            text_align=TextAlign.CENTER,
            background_color=Color("#FF0000"),
        )
        result = style.to_dict()
        assert result["name"] == "test"
        assert result["text_align"] == "center"
        assert result["background_color"] == "#FF0000"


# ============================================================================
# Theme Tests
# ============================================================================


class TestThemeSchema:
    """Tests for ThemeSchema class."""

    def test_themeschema_defaults(self) -> None:
        """Test ThemeSchema default values."""
        schema = ThemeSchema(name="Test Theme")
        assert schema.name == "Test Theme"
        assert schema.version == "1.0.0"
        assert schema.extends is None


class TestThemeVariant:
    """Tests for ThemeVariant class."""

    def test_themevariant_defaults(self) -> None:
        """Test ThemeVariant default values."""
        variant = ThemeVariant(name="dark")
        assert variant.name == "dark"
        assert variant.description == ""
        assert len(variant.colors) == 0

    def test_themevariant_with_colors(self) -> None:
        """Test ThemeVariant with custom colors."""
        variant = ThemeVariant(
            name="dark",
            colors={"primary": Color("#6B8DD6"), "background": Color("#1A1A1A")},
        )
        assert len(variant.colors) == 2


class TestTheme:
    """Tests for Theme class."""

    def test_theme_defaults(self) -> None:
        """Test Theme default values."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        assert theme.name == "Test"
        assert theme.version == "1.0.0"
        assert len(theme.styles) == 0

    def test_theme_properties(self) -> None:
        """Test Theme property accessors."""
        meta = ThemeSchema(name="MyTheme", version="2.0.0", description="A test theme")
        theme = Theme(meta=meta)
        assert theme.name == "MyTheme"
        assert theme.version == "2.0.0"
        assert theme.description == "A test theme"

    def test_theme_get_color_base(self) -> None:
        """Test Theme.get_color() from base palette."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        primary = theme.get_color("primary")
        assert primary.value == "#4472C4"

    def test_theme_get_color_variant(self) -> None:
        """Test Theme.get_color() from variant."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        variant = ThemeVariant(name="dark", colors={"primary": Color("#6B8DD6")})
        theme.variants["dark"] = variant
        theme.set_variant("dark")
        primary = theme.get_color("primary")
        assert primary.value == "#6B8DD6"

    def test_theme_get_color_not_found(self) -> None:
        """Test Theme.get_color() raises for unknown color."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        with pytest.raises(KeyError, match="Unknown color"):
            theme.get_color("nonexistent")

    def test_theme_set_variant(self) -> None:
        """Test Theme.set_variant() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        variant = ThemeVariant(name="dark")
        theme.variants["dark"] = variant
        theme.set_variant("dark")
        assert theme.active_variant == "dark"

    def test_theme_set_variant_invalid(self) -> None:
        """Test Theme.set_variant() raises for unknown variant."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        with pytest.raises(KeyError, match="Unknown variant"):
            theme.set_variant("nonexistent")

    def test_theme_set_variant_none(self) -> None:
        """Test Theme.set_variant(None) resets to base."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        variant = ThemeVariant(name="dark")
        theme.variants["dark"] = variant
        theme.set_variant("dark")
        theme.set_variant(None)
        assert theme.active_variant is None

    def test_theme_get_variant(self) -> None:
        """Test Theme.get_variant() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        variant = ThemeVariant(name="dark")
        theme.variants["dark"] = variant
        retrieved = theme.get_variant("dark")
        assert retrieved.name == "dark"

    def test_theme_get_variant_not_found(self) -> None:
        """Test Theme.get_variant() raises for unknown variant."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        with pytest.raises(KeyError, match="Unknown variant"):
            theme.get_variant("nonexistent")

    def test_theme_list_variants(self) -> None:
        """Test Theme.list_variants() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        theme.variants["dark"] = ThemeVariant(name="dark")
        theme.variants["light"] = ThemeVariant(name="light")
        variants = theme.list_variants()
        assert len(variants) == 2
        assert "dark" in variants
        assert "light" in variants

    def test_theme_resolve_color_ref_simple(self) -> None:
        """Test Theme.resolve_color_ref() with simple reference."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("{colors.primary}")
        assert color.value == "#4472C4"

    def test_theme_resolve_color_ref_with_modifier(self) -> None:
        """Test Theme.resolve_color_ref() with color modifier."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("{colors.primary|lighten:0.2}")
        # Should be lighter than base
        assert color != theme.colors.primary

    def test_theme_resolve_color_ref_darken(self) -> None:
        """Test Theme.resolve_color_ref() with darken modifier."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("{colors.primary|darken:0.3}")
        base = theme.colors.primary
        assert color.to_hsl()[2] < base.to_hsl()[2]

    def test_theme_resolve_color_ref_saturate(self) -> None:
        """Test Theme.resolve_color_ref() with saturate modifier."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("{colors.primary|saturate:0.2}")
        base = theme.colors.primary
        # Saturation should be higher
        assert color != base

    def test_theme_resolve_color_ref_desaturate(self) -> None:
        """Test Theme.resolve_color_ref() with desaturate modifier."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("{colors.primary|desaturate:0.5}")
        base = theme.colors.primary
        assert color != base

    def test_theme_resolve_color_ref_literal(self) -> None:
        """Test Theme.resolve_color_ref() with literal color."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("#FF0000")
        assert color.value == "#FF0000"

    def test_theme_get_font(self) -> None:
        """Test Theme.get_font() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        font = Font(family="Arial", size="12pt")
        theme.fonts["heading"] = font
        retrieved = theme.get_font("heading")
        assert retrieved.family == "Arial"

    def test_theme_get_font_not_found(self) -> None:
        """Test Theme.get_font() raises for unknown font."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        with pytest.raises(KeyError, match="Unknown font"):
            theme.get_font("nonexistent")

    def test_theme_get_style(self) -> None:
        """Test Theme.get_style() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        style_def = StyleDefinition(name="header", font_size="14pt")
        theme.styles["header"] = style_def
        style = theme.get_style("header")
        assert style.name == "header"

    def test_theme_get_style_not_found(self) -> None:
        """Test Theme.get_style() raises for unknown style."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        with pytest.raises(KeyError, match="Unknown style"):
            theme.get_style("nonexistent")

    def test_theme_get_style_with_inheritance(self) -> None:
        """Test Theme.get_style() with inheritance chain."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        parent = StyleDefinition(name="base", font_size="10pt")
        child = StyleDefinition(
            name="header", extends="base", font_weight=FontWeight.BOLD
        )
        theme.styles["base"] = parent
        theme.styles["header"] = child
        style = theme.get_style("header")
        assert style.font.size == "10pt"
        assert style.font.weight == FontWeight.BOLD

    def test_theme_get_style_with_traits(self) -> None:
        """Test Theme.get_style() with trait composition."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        # Create a base style with attributes
        base = StyleDefinition(name="base", font_size="12pt")
        bold_trait = StyleDefinition(name="bold", font_weight=FontWeight.BOLD)
        centered_trait = StyleDefinition(name="centered", text_align=TextAlign.CENTER)
        # Create styled that extends base and includes traits
        styled = StyleDefinition(
            name="styled", extends="base", includes=["bold", "centered"]
        )
        theme.styles["base"] = base
        theme.traits["bold"] = bold_trait
        theme.traits["centered"] = centered_trait
        theme.styles["styled"] = styled
        style = theme.get_style("styled")
        # Verify that trait attributes are applied
        assert style.text_align == TextAlign.CENTER
        # Font size from base should be present
        assert style.font.size == "12pt"

    def test_theme_get_style_circular_inheritance(self) -> None:
        """Test Theme.get_style() detects circular inheritance."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        style1 = StyleDefinition(name="style1", extends="style2")
        style2 = StyleDefinition(name="style2", extends="style1")
        theme.styles["style1"] = style1
        theme.styles["style2"] = style2
        with pytest.raises(ValueError, match="Circular inheritance"):
            theme.get_style("style1")

    def test_theme_get_style_caching(self) -> None:
        """Test Theme.get_style() caches resolved styles."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        style_def = StyleDefinition(name="cached")
        theme.styles["cached"] = style_def
        style1 = theme.get_style("cached")
        style2 = theme.get_style("cached")
        assert style1 is style2

    def test_theme_clear_cache(self) -> None:
        """Test Theme.clear_cache() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        style_def = StyleDefinition(name="test")
        theme.styles["test"] = style_def
        style1 = theme.get_style("test")
        theme.clear_cache()
        style2 = theme.get_style("test")
        assert style1 is not style2

    def test_theme_list_styles(self) -> None:
        """Test Theme.list_styles() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        theme.styles["style1"] = StyleDefinition(name="style1")
        theme.base_styles["base1"] = StyleDefinition(name="base1")
        styles = theme.list_styles()
        assert len(styles) == 2
        assert "style1" in styles
        assert "base1" in styles

    def test_theme_list_traits(self) -> None:
        """Test Theme.list_traits() method."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        theme.traits["bold"] = StyleDefinition(name="bold")
        theme.traits["italic"] = StyleDefinition(name="italic")
        traits = theme.list_traits()
        assert len(traits) == 2
        assert "bold" in traits

    def test_theme_to_dict(self) -> None:
        """Test Theme.to_dict() conversion."""
        theme = Theme(meta=ThemeSchema(name="Test", version="1.0.0"))
        result = theme.to_dict()
        assert result["meta"]["name"] == "Test"
        assert result["meta"]["version"] == "1.0.0"
        assert "colors" in result
        assert "fonts" in result
