"""Tests for schema module - styles, themes, validation, and loader."""

from __future__ import annotations

import pytest

from spreadsheet_dl.schema.styles import (
    Border,
    BorderStyle,
    CellStyle,
    Color,
    ColorPalette,
    Font,
    FontWeight,
    StyleDefinition,
    TextAlign,
    Theme,
    ThemeSchema,
    VerticalAlign,
)
from spreadsheet_dl.schema.validation import (
    SchemaValidationError,
    validate_border_style,
    validate_color,
    validate_font_weight,
    validate_size,
    validate_style,
    validate_text_align,
    validate_theme,
    validate_vertical_align,
    validate_yaml_data,
)

pytestmark = [pytest.mark.unit, pytest.mark.validation]


class TestColor:
    """Tests for Color class."""

    def test_create_from_hex(self) -> None:
        """Test creating color from hex string."""
        color = Color("#4472C4")
        assert str(color) == "#4472C4"

    def test_create_from_hex_short(self) -> None:
        """Test creating color from short hex string."""
        color = Color("#FFF")
        assert str(color) == "#FFFFFF"

    def test_from_hex_classmethod(self) -> None:
        """Test Color.from_hex classmethod."""
        color = Color.from_hex("4472C4")
        assert str(color) == "#4472C4"

    def test_from_rgb_classmethod(self) -> None:
        """Test Color.from_rgb classmethod."""
        color = Color.from_rgb(68, 114, 196)
        # Color normalizes to uppercase hex
        assert str(color) == "#4472C4"

    def test_to_rgb(self) -> None:
        """Test converting color to RGB tuple."""
        color = Color("#4472C4")
        r, g, b = color.to_rgb()
        assert r == 68
        assert g == 114
        assert b == 196

    def test_invalid_hex_raises(self) -> None:
        """Test invalid hex color raises error."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            Color("#GGGGGG")

    def test_invalid_rgb_raises(self) -> None:
        """Test invalid RGB values raise error."""
        with pytest.raises(ValueError, match="RGB values must be 0-255"):
            Color.from_rgb(256, 0, 0)


class TestColorPalette:
    """Tests for ColorPalette class."""

    def test_default_palette(self) -> None:
        """Test default palette has expected colors."""
        palette = ColorPalette()
        assert str(palette.primary) == "#4472C4"
        assert str(palette.success) == "#70AD47"
        assert str(palette.danger) == "#C00000"

    def test_get_color(self) -> None:
        """Test getting color by name."""
        palette = ColorPalette()
        color = palette.get("primary")
        assert color is not None
        assert str(color) == "#4472C4"

    def test_get_unknown_color_returns_none(self) -> None:
        """Test getting unknown color returns None."""
        palette = ColorPalette()
        assert palette.get("nonexistent") is None

    def test_set_custom_color(self) -> None:
        """Test setting custom color."""
        palette = ColorPalette()
        palette.set("brand", Color("#FF0000"))
        assert str(palette.get("brand")) == "#FF0000"

    def test_to_dict(self) -> None:
        """Test converting palette to dictionary."""
        palette = ColorPalette()
        d = palette.to_dict()
        assert "primary" in d
        assert d["primary"] == "#4472C4"


class TestFont:
    """Tests for Font class."""

    def test_default_font(self) -> None:
        """Test default font values."""
        font = Font()
        assert font.family == "Liberation Sans"
        assert font.size == "10pt"
        assert font.weight == FontWeight.NORMAL

    def test_custom_font(self) -> None:
        """Test creating custom font."""
        font = Font(
            family="Arial",
            size="12pt",
            weight=FontWeight.BOLD,
            color=Color("#FF0000"),
        )
        assert font.family == "Arial"
        assert font.size == "12pt"
        assert font.weight == FontWeight.BOLD

    def test_to_dict(self) -> None:
        """Test converting font to dictionary."""
        font = Font(family="Arial", weight=FontWeight.BOLD)
        d = font.to_dict()
        assert d["family"] == "Arial"
        # FontWeight uses numeric values ("700" for BOLD)
        assert d["weight"] == "700"


class TestBorder:
    """Tests for Border class."""

    def test_default_border(self) -> None:
        """Test default border values."""
        border = Border()
        assert border.width == "1px"
        assert border.style == BorderStyle.SOLID
        assert str(border.color) == "#000000"

    def test_to_odf(self) -> None:
        """Test converting border to ODF string."""
        border = Border(width="2px", style=BorderStyle.DASHED, color=Color("#FF0000"))
        assert border.to_odf() == "2px dashed #FF0000"

    def test_from_string(self) -> None:
        """Test parsing border from string."""
        border = Border.from_string("2px solid #FF0000")
        assert border.width == "2px"
        assert border.style == BorderStyle.SOLID
        assert str(border.color) == "#FF0000"


class TestStyleDefinition:
    """Tests for StyleDefinition class."""

    def test_create_style(self) -> None:
        """Test creating a style definition."""
        style = StyleDefinition(
            name="header",
            font_family="Arial",
            font_weight=FontWeight.BOLD,
        )
        assert style.name == "header"
        assert style.font_family == "Arial"
        assert style.font_weight == FontWeight.BOLD

    def test_style_extends(self) -> None:
        """Test style with extends."""
        style = StyleDefinition(name="sub_header", extends="header")
        assert style.extends == "header"


class TestCellStyle:
    """Tests for CellStyle class."""

    def test_default_cell_style(self) -> None:
        """Test default cell style values."""
        style = CellStyle(name="test")
        assert style.name == "test"
        assert style.text_align == TextAlign.LEFT
        assert style.vertical_align == VerticalAlign.MIDDLE

    def test_with_overrides(self) -> None:
        """Test creating style with overrides."""
        base = CellStyle(name="base", background_color=Color("#FFFFFF"))
        override = base.with_overrides(
            name="derived",
            background_color=Color("#F0F0F0"),
            font_weight=FontWeight.BOLD,
        )
        assert override.name == "derived"
        assert str(override.background_color) == "#F0F0F0"
        assert override.font.weight == FontWeight.BOLD

    def test_to_dict(self) -> None:
        """Test converting cell style to dictionary."""
        style = CellStyle(name="test")
        d = style.to_dict()
        assert d["name"] == "test"
        assert d["text_align"] == "left"


class TestTheme:
    """Tests for Theme class."""

    def test_create_theme(self) -> None:
        """Test creating a theme."""
        theme = Theme(
            meta=ThemeSchema(name="Test Theme", version="1.0.0"),
        )
        assert theme.name == "Test Theme"
        assert theme.version == "1.0.0"

    def test_get_color(self) -> None:
        """Test getting color from theme."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.get_color("primary")
        assert str(color) == "#4472C4"

    def test_get_unknown_color_raises(self) -> None:
        """Test getting unknown color raises error."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        with pytest.raises(KeyError, match="Unknown color"):
            theme.get_color("nonexistent")

    def test_resolve_color_ref(self) -> None:
        """Test resolving color reference."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("{colors.primary}")
        assert str(color) == "#4472C4"

    def test_resolve_literal_color(self) -> None:
        """Test resolving literal color value."""
        theme = Theme(meta=ThemeSchema(name="Test"))
        color = theme.resolve_color_ref("#FF0000")
        assert str(color) == "#FF0000"

    def test_get_style(self) -> None:
        """Test getting resolved style."""
        theme = Theme(
            meta=ThemeSchema(name="Test"),
            base_styles={
                "default": StyleDefinition(
                    name="default",
                    font_family="Arial",
                    font_size="10pt",
                ),
            },
        )
        style = theme.get_style("default")
        assert style.name == "default"
        assert style.font.family == "Arial"

    def test_get_style_with_inheritance(self) -> None:
        """Test getting style with inheritance."""
        theme = Theme(
            meta=ThemeSchema(name="Test"),
            base_styles={
                "default": StyleDefinition(
                    name="default",
                    font_family="Arial",
                    font_size="10pt",
                ),
            },
            styles={
                "header": StyleDefinition(
                    name="header",
                    extends="default",
                    font_weight=FontWeight.BOLD,
                ),
            },
        )
        style = theme.get_style("header")
        assert style.name == "header"
        assert style.font.family == "Arial"  # Inherited
        assert style.font.weight == FontWeight.BOLD  # Overridden

    def test_list_styles(self) -> None:
        """Test listing all styles."""
        theme = Theme(
            meta=ThemeSchema(name="Test"),
            base_styles={"default": StyleDefinition(name="default")},
            styles={"header": StyleDefinition(name="header")},
        )
        styles = theme.list_styles()
        assert "default" in styles
        assert "header" in styles


class TestValidation:
    """Tests for validation functions."""

    def test_validate_color_valid(self) -> None:
        """Test validating valid color."""
        color = validate_color("#4472C4")
        assert str(color) == "#4472C4"

    def test_validate_color_invalid(self) -> None:
        """Test validating invalid color."""
        with pytest.raises(SchemaValidationError, match="hex color"):
            validate_color("invalid")

    def test_validate_size_valid(self) -> None:
        """Test validating valid size."""
        size = validate_size("10pt")
        assert size == "10pt"

    def test_validate_size_invalid(self) -> None:
        """Test validating invalid size."""
        with pytest.raises(SchemaValidationError, match="valid size"):
            validate_size("invalid")

    def test_validate_font_weight_named(self) -> None:
        """Test validating font weight by name."""
        weight = validate_font_weight("bold")
        assert weight == FontWeight.BOLD

    def test_validate_font_weight_numeric(self) -> None:
        """Test validating font weight by numeric value."""
        weight = validate_font_weight("700")
        assert weight == FontWeight.BOLD

    def test_validate_text_align(self) -> None:
        """Test validating text alignment."""
        align = validate_text_align("center")
        assert align == TextAlign.CENTER

    def test_validate_vertical_align(self) -> None:
        """Test validating vertical alignment."""
        align = validate_vertical_align("middle")
        assert align == VerticalAlign.MIDDLE

    def test_validate_border_style(self) -> None:
        """Test validating border style."""
        style = validate_border_style("dashed")
        assert style == BorderStyle.DASHED

    def test_validate_style_missing_name(self) -> None:
        """Test validating style without name."""
        style = StyleDefinition(name="")
        with pytest.raises(SchemaValidationError, match="name is required"):
            validate_style(style)

    def test_validate_theme(self) -> None:
        """Test validating theme."""
        theme = Theme(
            meta=ThemeSchema(name="Test"),
            base_styles={"default": StyleDefinition(name="default")},
        )
        warnings = validate_theme(theme)
        assert warnings == []

    def test_validate_yaml_data_missing_meta(self) -> None:
        """Test validating YAML data without meta."""
        with pytest.raises(SchemaValidationError, match="must have 'meta'"):
            validate_yaml_data({})

    def test_validate_yaml_data_missing_name(self) -> None:
        """Test validating YAML data without name."""
        with pytest.raises(SchemaValidationError, match="must have 'name'"):
            validate_yaml_data({"meta": {}})


class TestSchemaValidationError:
    """Tests for SchemaValidationError."""

    def test_error_message(self) -> None:
        """Test error message formatting."""
        error = SchemaValidationError("Test error", field="test_field", value="bad")
        assert "test_field" in str(error)
        assert "Test error" in str(error)
        assert "bad" in str(error)

    def test_error_without_field(self) -> None:
        """Test error without field."""
        error = SchemaValidationError("Test error")
        assert "Test error" in str(error)
