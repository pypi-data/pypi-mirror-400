"""Theme loader from YAML files.

Loads and parses theme definitions from YAML files,
handling inheritance and color reference resolution.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

from spreadsheet_dl.schema.styles import (
    Border,
    BorderStyle,
    CellFill,
    Color,
    ColorPalette,
    Font,
    FontWeight,
    GradientFill,
    GradientStop,
    GradientType,
    PatternFill,
    PatternType,
    StrikethroughStyle,
    StyleDefinition,
    TextAlign,
    Theme,
    ThemeSchema,
    ThemeVariant,
    UnderlineStyle,
    VerticalAlign,
)
from spreadsheet_dl.schema.validation import (
    SchemaValidationError,
    validate_yaml_data,
)

# Try to import yaml, with fallback for when it's not installed
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ThemeLoader:
    """Load themes from YAML files.

    Handles:
    - YAML parsing with validation
    - Theme inheritance (extends)
    - Color reference resolution
    - Style inheritance resolution
    - Theme caching
    """

    # Default theme directory (relative to this file)
    DEFAULT_THEME_DIR = Path(__file__).parent.parent / "themes"

    def __init__(self, theme_dir: Path | str | None = None) -> None:
        """Initialize theme loader.

        Args:
            theme_dir: Directory containing theme YAML files.
                      Defaults to package themes/ directory.
        """
        if theme_dir is None:
            self.theme_dir = self.DEFAULT_THEME_DIR
        else:
            self.theme_dir = Path(theme_dir)

        self._cache: dict[str, Theme] = {}

    def load(self, name: str) -> Theme:
        """Load theme by name.

        Args:
            name: Theme name (filename without .yaml extension)

        Returns:
            Loaded Theme

        Raises:
            FileNotFoundError: If theme file not found
            SchemaValidationError: If theme is invalid
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for theme loading. "
                "Install with: pip install 'spreadsheet-dl[config]'"
            )

        # Check cache
        if name in self._cache:
            return self._cache[name]

        # Find theme file
        theme_path = self.theme_dir / f"{name}.yaml"
        if not theme_path.exists():
            # Try .yml extension
            theme_path = self.theme_dir / f"{name}.yml"
            if not theme_path.exists():
                raise FileNotFoundError(
                    f"Theme not found: {name} (looked in {self.theme_dir})"
                )

        # Load and parse
        with open(theme_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise SchemaValidationError(f"Theme file is empty: {theme_path}")

        # Validate raw data
        validate_yaml_data(data)

        # Parse theme
        theme = self._parse_theme(data)

        # Handle inheritance from parent theme
        if theme.meta.extends:
            parent = self.load(theme.meta.extends)
            theme = self._merge_themes(parent, theme)

        # Cache and return
        self._cache[name] = theme
        return theme

    def load_from_string(self, yaml_content: str) -> Theme:
        """Load theme from YAML string.

        Args:
            yaml_content: YAML content as string

        Returns:
            Loaded Theme
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for theme loading")

        data = yaml.safe_load(yaml_content)
        if data is None:
            raise SchemaValidationError("Theme content is empty")

        validate_yaml_data(data)
        return self._parse_theme(data)

    def load_from_dict(self, data: dict[str, Any]) -> Theme:
        """Load theme from dictionary.

        Useful for programmatic theme creation.

        Args:
            data: Theme data as dictionary

        Returns:
            Loaded Theme
        """
        validate_yaml_data(data)
        return self._parse_theme(data)

    def list_themes(self) -> list[str]:
        """List available theme names.

        Returns:
            List of theme names
        """
        if not self.theme_dir.exists():
            return []

        themes = []
        for path in self.theme_dir.glob("*.yaml"):
            themes.append(path.stem)
        for path in self.theme_dir.glob("*.yml"):
            if path.stem not in themes:
                themes.append(path.stem)

        return sorted(themes)

    def clear_cache(self) -> None:
        """Clear the theme cache."""
        self._cache.clear()

    def _parse_theme(self, data: dict[str, Any]) -> Theme:
        """Parse theme from YAML data.

        Args:
            data: Raw YAML data

        Returns:
            Parsed Theme
        """
        # Parse metadata
        meta_data = data.get("meta", {})
        meta = ThemeSchema(
            name=meta_data.get("name", "Unnamed"),
            version=meta_data.get("version", "1.0.0"),
            description=meta_data.get("description", ""),
            author=meta_data.get("author", ""),
            extends=meta_data.get("extends"),
        )

        # Parse colors
        colors = self._parse_colors(data.get("colors", {}))

        # Parse fonts
        fonts = self._parse_fonts(data.get("fonts", {}))

        # Parse base styles
        base_styles = self._parse_styles(
            data.get("base_styles", {}),
            colors,
            fonts,
        )

        # Parse semantic styles
        styles = self._parse_styles(
            data.get("styles", {}),
            colors,
            fonts,
        )

        # Parse conditional formats
        conditional_formats = data.get("conditional_formats", {})

        # Parse variants
        variants = self._parse_variants(data.get("variants", {}))

        return Theme(
            meta=meta,
            colors=colors,
            fonts=fonts,
            base_styles=base_styles,
            styles=styles,
            conditional_formats=conditional_formats,
            variants=variants,
        )

    def _parse_colors(self, data: dict[str, str]) -> ColorPalette:
        """Parse color palette from YAML data.

        Args:
            data: Colors dictionary from YAML

        Returns:
            ColorPalette
        """
        palette = ColorPalette()

        # Standard color mappings
        standard_colors = {
            "primary": "primary",
            "primary_light": "primary_light",
            "primary_dark": "primary_dark",
            "secondary": "secondary",
            "success": "success",
            "success_bg": "success_bg",
            "warning": "warning",
            "warning_bg": "warning_bg",
            "danger": "danger",
            "danger_bg": "danger_bg",
            "neutral_100": "neutral_100",
            "neutral_200": "neutral_200",
            "neutral_300": "neutral_300",
            "neutral_800": "neutral_800",
            "neutral_900": "neutral_900",
        }

        for name, value in data.items():
            color = Color(value)
            if name in standard_colors:
                setattr(palette, standard_colors[name], color)
            else:
                palette.set(name, color)

        return palette

    def _parse_fonts(self, data: dict[str, Any]) -> dict[str, Font]:
        """Parse font definitions from YAML data.

        Args:
            data: Fonts dictionary from YAML

        Returns:
            Dictionary of Font objects
        """
        fonts: dict[str, Font] = {}

        for name, font_data in data.items():
            if isinstance(font_data, dict):
                fonts[name] = Font(
                    family=font_data.get("family", "Liberation Sans"),
                    fallback=font_data.get("fallback", "Arial, sans-serif"),
                    size=font_data.get("size", "10pt"),
                )
            else:
                # Simple case: just font family name
                fonts[name] = Font(family=str(font_data))

        return fonts

    def _parse_variants(self, data: dict[str, Any]) -> dict[str, ThemeVariant]:
        """Parse theme variants from YAML data.

        Implements Theme variants missing

        Args:
            data: Variants dictionary from YAML

        Returns:
            Dictionary of ThemeVariant objects
        """
        variants: dict[str, ThemeVariant] = {}

        for name, variant_data in data.items():
            if not isinstance(variant_data, dict):
                continue

            description = variant_data.get("description", "")

            # Parse variant colors
            variant_colors: dict[str, Color] = {}
            colors_data = variant_data.get("colors", {})
            for color_name, color_value in colors_data.items():
                if isinstance(color_value, str):
                    variant_colors[color_name] = Color(color_value)

            variants[name] = ThemeVariant(
                name=name,
                description=description,
                colors=variant_colors,
            )

        return variants

    def _parse_styles(
        self,
        data: dict[str, Any],
        colors: ColorPalette,
        fonts: dict[str, Font],
    ) -> dict[str, StyleDefinition]:
        """Parse style definitions from YAML data.

        Args:
            data: Styles dictionary from YAML
            colors: Color palette for reference resolution
            fonts: Font definitions for reference resolution

        Returns:
            Dictionary of StyleDefinition objects
        """
        styles: dict[str, StyleDefinition] = {}

        for name, style_data in data.items():
            if not isinstance(style_data, dict):
                continue

            style = StyleDefinition(name=name)

            # Handle extends
            if "extends" in style_data:
                style.extends = style_data["extends"]

            # Typography
            if "font_family" in style_data:
                ref = style_data["font_family"]
                if ref.startswith("{fonts."):
                    font_name = ref[7:-1]  # Extract from {fonts.name}
                    if font_name in fonts:
                        style.font_family = fonts[font_name].family
                else:
                    style.font_family = ref

            if "font_size" in style_data:
                style.font_size = style_data["font_size"]

            if "font_weight" in style_data:
                weight_str = style_data["font_weight"]
                try:
                    # Try numeric value first (e.g., "700")
                    style.font_weight = FontWeight(weight_str)
                except ValueError:
                    # Fall back to name lookup (e.g., "bold")
                    style.font_weight = FontWeight.from_name(weight_str)

            if "color" in style_data:
                style.font_color = self._resolve_color(style_data["color"], colors)

            if "italic" in style_data:
                style.italic = bool(style_data["italic"])

            if "underline" in style_data:
                # Parse as UnderlineStyle enum
                underline_val = style_data["underline"]
                if isinstance(underline_val, bool):
                    # Backward compatibility: bool -> enum
                    style.underline = (
                        UnderlineStyle.SINGLE if underline_val else UnderlineStyle.NONE
                    )
                elif isinstance(underline_val, str):
                    with contextlib.suppress(ValueError):
                        style.underline = UnderlineStyle(underline_val)

            if "strikethrough" in style_data:
                # Parse strikethrough
                strikethrough_val = style_data["strikethrough"]
                if isinstance(strikethrough_val, bool):
                    # Backward compatibility: bool -> enum
                    style.strikethrough = (
                        StrikethroughStyle.SINGLE
                        if strikethrough_val
                        else StrikethroughStyle.NONE
                    )
                elif isinstance(strikethrough_val, str):
                    with contextlib.suppress(ValueError):
                        style.strikethrough = StrikethroughStyle(strikethrough_val)

            if "letter_spacing" in style_data:
                # Parse letter_spacing
                style.letter_spacing = style_data["letter_spacing"]

            if "text_align" in style_data:
                with contextlib.suppress(ValueError):
                    style.text_align = TextAlign(style_data["text_align"])

            if "vertical_align" in style_data:
                with contextlib.suppress(ValueError):
                    style.vertical_align = VerticalAlign(style_data["vertical_align"])

            # Alignment properties
            if "text_rotation" in style_data:
                style.text_rotation = int(style_data["text_rotation"])

            if "wrap_text" in style_data:
                style.wrap_text = bool(style_data["wrap_text"])

            if "shrink_to_fit" in style_data:
                style.shrink_to_fit = bool(style_data["shrink_to_fit"])

            if "indent" in style_data:
                style.indent = int(style_data["indent"])

            # Background
            if "background_color" in style_data:
                style.background_color = self._resolve_color(
                    style_data["background_color"], colors
                )

            # Fill (pattern or gradient)
            if "fill" in style_data:
                fill_data = style_data["fill"]
                if isinstance(fill_data, dict):
                    if "pattern_type" in fill_data:
                        # Pattern fill
                        pattern_fill = self._parse_pattern_fill(fill_data, colors)
                        style.fill = CellFill(pattern=pattern_fill)
                    elif "type" in fill_data and fill_data["type"] in (
                        "linear",
                        "radial",
                    ):
                        # Gradient fill
                        gradient_fill = self._parse_gradient_fill(fill_data, colors)
                        style.fill = CellFill(gradient=gradient_fill)
                    elif "solid_color" in fill_data:
                        # Solid fill
                        color = self._resolve_color(fill_data["solid_color"], colors)
                        style.fill = CellFill(solid_color=color)

            # Borders
            for border_name in [
                "border_top",
                "border_bottom",
                "border_left",
                "border_right",
            ]:
                if border_name in style_data:
                    border = self._parse_border(style_data[border_name], colors)
                    setattr(style, border_name, border)

            # Spacing
            if "padding" in style_data:
                style.padding = style_data["padding"]

            # Number/date formatting
            if "number_format" in style_data:
                style.number_format = style_data["number_format"]

            if "date_format" in style_data:
                style.date_format = style_data["date_format"]

            styles[name] = style

        return styles

    def _resolve_color(self, value: str, colors: ColorPalette) -> Color:
        """Resolve color value or reference.

        Args:
            value: Color value or reference like "{colors.primary}"
            colors: Color palette for resolution

        Returns:
            Resolved Color
        """
        if value.startswith("{colors."):
            color_name = value[8:-1]  # Extract from {colors.name}
            resolved = colors.get(color_name)
            if resolved:
                return resolved
        return Color(value)

    def _parse_border(
        self, value: str | dict[str, Any], colors: ColorPalette
    ) -> Border:
        """Parse border from string or dict.

        Args:
            value: Border specification
            colors: Color palette for color resolution

        Returns:
            Border object
        """
        if isinstance(value, str):
            # Parse "1px solid {colors.primary}" format
            parts = value.split()
            width = parts[0] if len(parts) > 0 else "1px"

            style = BorderStyle.SOLID
            if len(parts) > 1:
                with contextlib.suppress(ValueError):
                    style = BorderStyle(parts[1])

            color = Color("#000000")
            if len(parts) > 2:
                color = self._resolve_color(parts[2], colors)

            return Border(width=width, style=style, color=color)

        elif isinstance(value, dict):
            return Border(
                width=value.get("width", "1px"),
                style=BorderStyle(value.get("style", "solid")),
                color=self._resolve_color(value.get("color", "#000000"), colors),
            )

        return Border()

    def _parse_pattern_fill(
        self, value: dict[str, Any], colors: ColorPalette
    ) -> PatternFill:
        """Parse pattern fill from YAML data.

        Implements PatternFill not parsed from YAML

        Args:
            value: Pattern fill specification dict
            colors: Color palette for color resolution

        Returns:
            PatternFill object
        """
        pattern_type_str = value.get("pattern_type", "solid")
        try:
            pattern_type = PatternType(pattern_type_str)
        except ValueError:
            pattern_type = PatternType.SOLID

        foreground = self._resolve_color(
            value.get("foreground_color", "#000000"), colors
        )
        background = self._resolve_color(
            value.get("background_color", "#FFFFFF"), colors
        )

        return PatternFill(
            pattern_type=pattern_type,
            foreground_color=foreground,
            background_color=background,
        )

    def _parse_gradient_fill(
        self, value: dict[str, Any], colors: ColorPalette
    ) -> GradientFill:
        """Parse gradient fill from YAML data.

        Implements GradientFill not parsed from YAML

        Args:
            value: Gradient fill specification dict
            colors: Color palette for color resolution

        Returns:
            GradientFill object
        """
        gradient_type_str = value.get("type", "linear")
        try:
            gradient_type = GradientType(gradient_type_str)
        except ValueError:
            gradient_type = GradientType.LINEAR

        angle = float(value.get("angle", 0.0))
        center_x = float(value.get("center_x", 0.5))
        center_y = float(value.get("center_y", 0.5))

        # Parse gradient stops
        stops_data = value.get("stops", [])
        stops: list[GradientStop] = []
        for stop_data in stops_data:
            if isinstance(stop_data, dict):
                position = float(stop_data.get("position", 0.0))
                color = self._resolve_color(stop_data.get("color", "#FFFFFF"), colors)
                stops.append(GradientStop(position=position, color=color))

        return GradientFill(
            type=gradient_type,
            angle=angle,
            center_x=center_x,
            center_y=center_y,
            stops=tuple(stops),
        )

    def _merge_themes(self, parent: Theme, child: Theme) -> Theme:
        """Merge child theme over parent (inheritance).

        Child values override parent values.

        Args:
            parent: Parent theme
            child: Child theme

        Returns:
            Merged theme
        """
        # Merge colors
        merged_colors = ColorPalette()
        for attr in [
            "primary",
            "primary_light",
            "primary_dark",
            "secondary",
            "success",
            "success_bg",
            "warning",
            "warning_bg",
            "danger",
            "danger_bg",
            "neutral_100",
            "neutral_200",
            "neutral_300",
            "neutral_800",
            "neutral_900",
        ]:
            parent_color = getattr(parent.colors, attr)
            child_color = getattr(child.colors, attr)
            # Use child if different from default
            default_palette = ColorPalette()
            if str(child_color) != str(getattr(default_palette, attr)):
                setattr(merged_colors, attr, child_color)
            else:
                setattr(merged_colors, attr, parent_color)

        # Merge custom colors
        merged_colors.custom = {**parent.colors.custom, **child.colors.custom}

        # Merge fonts
        merged_fonts = {**parent.fonts, **child.fonts}

        # Merge styles
        merged_base_styles = {**parent.base_styles, **child.base_styles}
        merged_styles = {**parent.styles, **child.styles}

        # Merge conditional formats
        merged_cond = {**parent.conditional_formats, **child.conditional_formats}

        return Theme(
            meta=child.meta,
            colors=merged_colors,
            fonts=merged_fonts,
            base_styles=merged_base_styles,
            styles=merged_styles,
            conditional_formats=merged_cond,
        )


# Default loader instance
_default_loader: ThemeLoader | None = None


def get_default_loader() -> ThemeLoader:
    """Get or create the default theme loader."""
    global _default_loader
    if _default_loader is None:
        _default_loader = ThemeLoader()
    return _default_loader


def load_theme(name: str) -> Theme:
    """Convenience function to load a theme.

    Args:
        name: Theme name

    Returns:
        Loaded Theme
    """
    return get_default_loader().load(name)


def list_available_themes() -> list[str]:
    """List available themes.

    Returns:
        List of theme names
    """
    return get_default_loader().list_themes()
