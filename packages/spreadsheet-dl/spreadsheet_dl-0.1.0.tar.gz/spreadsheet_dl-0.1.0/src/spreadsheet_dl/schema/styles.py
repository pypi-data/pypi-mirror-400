"""Style schema definitions with comprehensive dataclass validation.

Provides type-safe style definitions for themes including:
- Color with hex/RGB/HSL support and manipulation
- Font specifications with full typography control
- Border definitions with per-side control
- Cell fill with solid, pattern, and gradient support
- Number formats with locale support
- Complete cell styles with inheritance
- Theme with color palette and style registry
"""

from __future__ import annotations

import colorsys
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ============================================================================
# Enumerations
# ============================================================================


class FontWeight(Enum):
    """Font weight options."""

    THIN = "100"
    EXTRA_LIGHT = "200"
    LIGHT = "300"
    NORMAL = "400"
    MEDIUM = "500"
    SEMI_BOLD = "600"
    BOLD = "700"
    EXTRA_BOLD = "800"
    BLACK = "900"

    # Aliases for backward compatibility
    @classmethod
    def from_name(cls, name: str) -> FontWeight:
        """Get weight from common name."""
        mapping = {
            "thin": cls.THIN,
            "extralight": cls.EXTRA_LIGHT,
            "light": cls.LIGHT,
            "normal": cls.NORMAL,
            "regular": cls.NORMAL,
            "medium": cls.MEDIUM,
            "semibold": cls.SEMI_BOLD,
            "bold": cls.BOLD,
            "extrabold": cls.EXTRA_BOLD,
            "black": cls.BLACK,
            "heavy": cls.BLACK,
        }
        return mapping.get(name.lower().replace("-", "").replace("_", ""), cls.NORMAL)

    @property
    def is_bold(self) -> bool:
        """Check if this is a bold weight."""
        return int(self.value) >= 600


class TextAlign(Enum):
    """Horizontal text alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"
    DISTRIBUTED = "distributed"
    FILL = "fill"


class VerticalAlign(Enum):
    """Vertical text alignment options."""

    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"
    JUSTIFY = "justify"
    DISTRIBUTED = "distributed"


class BorderStyle(Enum):
    """Border style options."""

    NONE = "none"
    THIN = "thin"
    MEDIUM = "medium"
    THICK = "thick"
    DOUBLE = "double"
    DOTTED = "dotted"
    DASHED = "dashed"
    HAIR = "hair"
    # Aliases
    SOLID = "solid"


class UnderlineStyle(Enum):
    """Underline style options."""

    NONE = "none"
    SINGLE = "single"
    DOUBLE = "double"
    DOTTED = "dotted"
    DASHED = "dashed"
    WAVE = "wave"
    ACCOUNTING = "accounting"  # Double accounting underline


class StrikethroughStyle(Enum):
    """Strikethrough style options."""

    NONE = "none"
    SINGLE = "single"
    DOUBLE = "double"


class PatternType(Enum):
    """Pattern fill types."""

    NONE = "none"
    SOLID = "solid"
    GRAY_125 = "gray125"
    GRAY_0625 = "gray0625"
    DARK_GRAY = "darkGray"
    MEDIUM_GRAY = "mediumGray"
    LIGHT_GRAY = "lightGray"
    DARK_HORIZONTAL = "darkHorizontal"
    DARK_VERTICAL = "darkVertical"
    DARK_DOWN = "darkDown"
    DARK_UP = "darkUp"
    DARK_GRID = "darkGrid"
    DARK_TRELLIS = "darkTrellis"
    LIGHT_HORIZONTAL = "lightHorizontal"
    LIGHT_VERTICAL = "lightVertical"
    LIGHT_DOWN = "lightDown"
    LIGHT_UP = "lightUp"
    LIGHT_GRID = "lightGrid"
    LIGHT_TRELLIS = "lightTrellis"


class GradientType(Enum):
    """Gradient types."""

    LINEAR = "linear"
    RADIAL = "radial"


class NumberFormatCategory(Enum):
    """Number format categories."""

    GENERAL = "general"
    NUMBER = "number"
    CURRENCY = "currency"
    ACCOUNTING = "accounting"
    PERCENTAGE = "percentage"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    SCIENTIFIC = "scientific"
    FRACTION = "fraction"
    TEXT = "text"
    CUSTOM = "custom"


class NegativeFormat(Enum):
    """Negative number display formats."""

    MINUS = "minus"  # -123.45
    PARENTHESES = "parentheses"  # (123.45)
    RED = "red"  # 123.45 in red
    RED_PARENTHESES = "red_parentheses"  # (123.45) in red


# ============================================================================
# Color Class
# ============================================================================


# Regex for hex color validation
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3,4}){1,2}$")

# CSS named colors
CSS_NAMED_COLORS: dict[str, str] = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#008000",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "silver": "#C0C0C0",
    "gray": "#808080",
    "grey": "#808080",
    "maroon": "#800000",
    "olive": "#808000",
    "navy": "#000080",
    "purple": "#800080",
    "teal": "#008080",
    "orange": "#FFA500",
    "steelblue": "#4682B4",
    "lightblue": "#ADD8E6",
    "darkblue": "#00008B",
    "lightgreen": "#90EE90",
    "darkgreen": "#006400",
    "lightgray": "#D3D3D3",
    "darkgray": "#A9A9A9",
    "coral": "#FF7F50",
    "salmon": "#FA8072",
    "gold": "#FFD700",
    "crimson": "#DC143C",
    "indigo": "#4B0082",
    "violet": "#EE82EE",
    "aqua": "#00FFFF",
    "lime": "#00FF00",
    "fuchsia": "#FF00FF",
    "transparent": "#00000000",
}


@dataclass(frozen=True)
class Color:
    """Color specification supporting hex, RGB, HSL values and manipulation.

    Implements Missing frozen=True on value objects

    Examples:
        # Multiple creation methods
        c1 = Color("#4472C4")
        c2 = Color.from_rgb(68, 114, 196)
        c3 = Color.from_hsl(217, 49, 52)
        c4 = Color.from_name("steelblue")

        # Manipulation
        lighter = c1.lighten(0.2)  # 20% lighter
        darker = c1.darken(0.15)   # 15% darker
        muted = c1.desaturate(0.3)  # 30% less saturated

        # Color schemes
        comp = c1.complementary()      # 180 degrees on color wheel
        ana1, ana2 = c1.analogous()    # +/-30 degrees
        tri1, tri2 = c1.triadic()      # 120 degrees apart
        sp1, sp2 = c1.split_complementary()  # 150/210 degrees

        # Accessibility
        ratio = c1.contrast_ratio(Color("#FFFFFF"))
        assert c1.is_wcag_aa(Color("#FFFFFF"))  # True if ratio >= 4.5
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and normalize color value."""
        if self.value.startswith("#"):
            if not HEX_COLOR_PATTERN.match(self.value):
                raise ValueError(f"Invalid hex color: {self.value}")
            # Normalize to 6 or 8 character hex (use object.__setattr__ for frozen dataclass)
            val = self.value[1:]
            normalized: str
            if len(val) == 3:
                normalized = f"#{val[0] * 2}{val[1] * 2}{val[2] * 2}"
            elif len(val) == 4:
                normalized = f"#{val[0] * 2}{val[1] * 2}{val[2] * 2}{val[3] * 2}"
            else:
                normalized = f"#{val.upper()}"
            object.__setattr__(self, "value", normalized)

    @classmethod
    def from_hex(cls, hex_code: str) -> Color:
        """Create color from hex code."""
        if not hex_code.startswith("#"):
            hex_code = f"#{hex_code}"
        return cls(hex_code)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, a: int | None = None) -> Color:
        """Create color from RGB values (0-255).

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            a: Optional alpha component (0-255)

        Returns:
            Color instance
        """
        if not all(0 <= x <= 255 for x in (r, g, b)):
            raise ValueError(f"RGB values must be 0-255: ({r}, {g}, {b})")
        if a is not None:
            if not 0 <= a <= 255:
                raise ValueError(f"Alpha must be 0-255: {a}")
            return cls(f"#{r:02X}{g:02X}{b:02X}{a:02X}")
        return cls(f"#{r:02X}{g:02X}{b:02X}")

    @classmethod
    def from_hsl(
        cls, hue: float, saturation: float, lightness: float, a: float | None = None
    ) -> Color:
        """Create color from HSL values.

        Args:
            hue: Hue (0-360)
            saturation: Saturation (0-100)
            lightness: Lightness (0-100)
            a: Optional alpha (0-100)

        Returns:
            Color instance
        """
        # Normalize values
        h_norm = hue / 360.0
        s_norm = saturation / 100.0
        l_norm = lightness / 100.0

        r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)

        if a is not None:
            alpha = int(a * 255 / 100)
            return cls.from_rgb(int(r * 255), int(g * 255), int(b * 255), alpha)
        return cls.from_rgb(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def from_name(cls, name: str) -> Color:
        """Create color from CSS color name.

        Args:
            name: CSS color name (e.g., "steelblue", "red")

        Returns:
            Color instance

        Raises:
            ValueError: If color name not recognized
        """
        name_lower = name.lower().strip()
        if name_lower in CSS_NAMED_COLORS:
            return cls(CSS_NAMED_COLORS[name_lower])
        raise ValueError(
            f"Unknown color name: {name}. Valid names: {', '.join(CSS_NAMED_COLORS.keys())}"
        )

    def to_rgb(self) -> tuple[int, int, int]:
        """Convert to RGB tuple."""
        hex_val = self.value.lstrip("#")[:6]  # Ignore alpha
        return (
            int(hex_val[0:2], 16),
            int(hex_val[2:4], 16),
            int(hex_val[4:6], 16),
        )

    def to_rgba(self) -> tuple[int, int, int, int]:
        """Convert to RGBA tuple."""
        hex_val = self.value.lstrip("#")
        r = int(hex_val[0:2], 16)
        g = int(hex_val[2:4], 16)
        b = int(hex_val[4:6], 16)
        a = int(hex_val[6:8], 16) if len(hex_val) >= 8 else 255
        return (r, g, b, a)

    def to_hsl(self) -> tuple[float, float, float]:
        """Convert to HSL tuple (h: 0-360, s: 0-100, l: 0-100)."""
        r, g, b = self.to_rgb()
        hue, lightness, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        return (hue * 360, saturation * 100, lightness * 100)

    @property
    def alpha(self) -> float:
        """Get alpha value (0.0-1.0)."""
        hex_val = self.value.lstrip("#")
        if len(hex_val) >= 8:
            return int(hex_val[6:8], 16) / 255
        return 1.0

    def with_alpha(self, alpha: float) -> Color:
        """Create new color with specified alpha.

        Args:
            alpha: Alpha value (0.0-1.0)

        Returns:
            New Color with alpha
        """
        r, g, b = self.to_rgb()
        a = int(max(0, min(1, alpha)) * 255)
        return Color.from_rgb(r, g, b, a)

    def lighten(self, amount: float) -> Color:
        """Create lighter color.

        Args:
            amount: Amount to lighten (0.0-1.0)

        Returns:
            Lighter color
        """
        hue, saturation, lightness = self.to_hsl()
        new_lightness = min(100, lightness + (100 - lightness) * amount)
        return Color.from_hsl(hue, saturation, new_lightness)

    def darken(self, amount: float) -> Color:
        """Create darker color.

        Args:
            amount: Amount to darken (0.0-1.0)

        Returns:
            Darker color
        """
        hue, saturation, lightness = self.to_hsl()
        new_lightness = max(0, lightness * (1 - amount))
        return Color.from_hsl(hue, saturation, new_lightness)

    def saturate(self, amount: float) -> Color:
        """Increase saturation.

        Args:
            amount: Amount to saturate (0.0-1.0)

        Returns:
            More saturated color
        """
        hue, saturation, lightness = self.to_hsl()
        new_saturation = min(100, saturation + (100 - saturation) * amount)
        return Color.from_hsl(hue, new_saturation, lightness)

    def desaturate(self, amount: float) -> Color:
        """Decrease saturation.

        Args:
            amount: Amount to desaturate (0.0-1.0)

        Returns:
            Less saturated color
        """
        hue, saturation, lightness = self.to_hsl()
        new_saturation = max(0, saturation * (1 - amount))
        return Color.from_hsl(hue, new_saturation, lightness)

    def invert(self) -> Color:
        """Return inverted color."""
        r, g, b = self.to_rgb()
        return Color.from_rgb(255 - r, 255 - g, 255 - b)

    def grayscale(self) -> Color:
        """Convert to grayscale."""
        r, g, b = self.to_rgb()
        # Use luminance-based conversion
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        return Color.from_rgb(gray, gray, gray)

    def luminance(self) -> float:
        """Calculate relative luminance per WCAG 2.0.

        Returns:
            Relative luminance (0.0-1.0)
        """
        r, g, b = self.to_rgb()

        def _channel_luminance(c: int) -> float:
            c_srgb = c / 255
            if c_srgb <= 0.03928:
                return c_srgb / 12.92
            return math.pow((c_srgb + 0.055) / 1.055, 2.4)

        return (
            0.2126 * _channel_luminance(r)
            + 0.7152 * _channel_luminance(g)
            + 0.0722 * _channel_luminance(b)
        )

    def contrast_ratio(self, other: Color) -> float:
        """Calculate contrast ratio between two colors per WCAG 2.0.

        Args:
            other: Color to compare against

        Returns:
            Contrast ratio (1.0-21.0)
        """
        lum1 = self.luminance()
        lum2 = other.luminance()
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)

    def is_wcag_aa(self, background: Color, large_text: bool = False) -> bool:
        """Check if color passes WCAG AA contrast requirements.

        Args:
            background: Background color
            large_text: True if text is 18pt+ or 14pt+ bold

        Returns:
            True if passes WCAG AA
        """
        ratio = self.contrast_ratio(background)
        required = 3.0 if large_text else 4.5
        return ratio >= required

    def is_wcag_aaa(self, background: Color, large_text: bool = False) -> bool:
        """Check if color passes WCAG AAA contrast requirements.

        Args:
            background: Background color
            large_text: True if text is 18pt+ or 14pt+ bold

        Returns:
            True if passes WCAG AAA
        """
        ratio = self.contrast_ratio(background)
        required = 4.5 if large_text else 7.0
        return ratio >= required

    def rotate_hue(self, degrees: float) -> Color:
        """Rotate the hue by a specified number of degrees.

        Args:
            degrees: Degrees to rotate (positive = clockwise)

        Returns:
            New Color with rotated hue
        """
        hue, saturation, lightness = self.to_hsl()
        new_hue = (hue + degrees) % 360
        return Color.from_hsl(new_hue, saturation, lightness)

    def analogous(self) -> tuple[Color, Color]:
        """Generate analogous colors (+/- 30 degrees on color wheel).

        Analogous colors are adjacent on the color wheel and create
        harmonious, cohesive color schemes.

        Returns:
            Tuple of (color at -30 degrees, color at +30 degrees)

        Examples:
            >>> blue = Color("#0000FF")
            >>> ana1, ana2 = blue.analogous()
            >>> # ana1 is blue-violet, ana2 is blue-green
        """
        return (self.rotate_hue(-30), self.rotate_hue(30))

    def complementary(self) -> Color:
        """Generate complementary color (180 degrees on color wheel).

        Complementary colors are opposite on the color wheel and create
        high-contrast, vibrant combinations.

        Returns:
            Complementary color

        Examples:
            >>> blue = Color("#0000FF")
            >>> comp = blue.complementary()
            >>> # comp is yellow/orange
        """
        return self.rotate_hue(180)

    def triadic(self) -> tuple[Color, Color]:
        """Generate triadic colors (120 degrees apart).

        Triadic colors are evenly spaced around the color wheel,
        creating balanced, vibrant color schemes.

        Returns:
            Tuple of (color at +120 degrees, color at +240 degrees)

        Examples:
            >>> red = Color("#FF0000")
            >>> tri1, tri2 = red.triadic()
            >>> # tri1 is green, tri2 is blue
        """
        return (self.rotate_hue(120), self.rotate_hue(240))

    def split_complementary(self) -> tuple[Color, Color]:
        """Generate split complementary colors (150 and 210 degrees).

        Split complementary uses colors adjacent to the complement,
        providing high contrast with less tension than complementary.

        Returns:
            Tuple of (color at +150 degrees, color at +210 degrees)

        Examples:
            >>> blue = Color("#0000FF")
            >>> sp1, sp2 = blue.split_complementary()
            >>> # sp1 and sp2 are yellow-orange variants
        """
        return (self.rotate_hue(150), self.rotate_hue(210))

    def tetradic(self) -> tuple[Color, Color, Color]:
        """Generate tetradic (rectangular) colors (90, 180, 270 degrees).

        Tetradic colors form a rectangle on the color wheel,
        offering rich variety while maintaining balance.

        Returns:
            Tuple of three colors at 90, 180, and 270 degrees

        Examples:
            >>> red = Color("#FF0000")
            >>> t1, t2, t3 = red.tetradic()
            >>> # Returns yellow-green, cyan, and blue-violet
        """
        return (self.rotate_hue(90), self.rotate_hue(180), self.rotate_hue(270))

    def square(self) -> tuple[Color, Color, Color]:
        """Generate square colors (90 degrees apart).

        Square colors are evenly spaced at 90-degree intervals,
        creating bold, dynamic color schemes.

        Returns:
            Tuple of three colors at 90, 180, and 270 degrees

        Note:
            Same as tetradic() - both produce colors at 90-degree intervals.
        """
        return self.tetradic()

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if isinstance(other, Color):
            return self.value.upper() == other.value.upper()
        return False

    def __hash__(self) -> int:
        """Return hash value."""
        return hash(self.value.upper())


# ============================================================================
# Color Palette
# ============================================================================


@dataclass
class ColorPalette:
    """Named color palette for themes with auto-generated tints and shades.

    Provides semantic color naming for consistent theming.

    Note: Not frozen to allow dynamic color updates via set() method.
    """

    # Primary colors
    primary: Color = field(default_factory=lambda: Color("#4472C4"))
    primary_light: Color = field(default_factory=lambda: Color("#6B8DD6"))
    primary_dark: Color = field(default_factory=lambda: Color("#2F4A82"))

    secondary: Color = field(default_factory=lambda: Color("#ED7D31"))

    # Semantic colors
    success: Color = field(default_factory=lambda: Color("#70AD47"))
    success_bg: Color = field(default_factory=lambda: Color("#C6EFCE"))

    warning: Color = field(default_factory=lambda: Color("#FFC000"))
    warning_bg: Color = field(default_factory=lambda: Color("#FFEB9C"))

    danger: Color = field(default_factory=lambda: Color("#C00000"))
    danger_bg: Color = field(default_factory=lambda: Color("#FFC7CE"))

    info: Color = field(default_factory=lambda: Color("#0070C0"))
    info_bg: Color = field(default_factory=lambda: Color("#DEEAF6"))

    # Neutral scale
    neutral_50: Color = field(default_factory=lambda: Color("#FAFAFA"))
    neutral_100: Color = field(default_factory=lambda: Color("#F5F5F5"))
    neutral_200: Color = field(default_factory=lambda: Color("#E0E0E0"))
    neutral_300: Color = field(default_factory=lambda: Color("#BDBDBD"))
    neutral_400: Color = field(default_factory=lambda: Color("#9E9E9E"))
    neutral_500: Color = field(default_factory=lambda: Color("#757575"))
    neutral_600: Color = field(default_factory=lambda: Color("#616161"))
    neutral_700: Color = field(default_factory=lambda: Color("#424242"))
    neutral_800: Color = field(default_factory=lambda: Color("#333333"))
    neutral_900: Color = field(default_factory=lambda: Color("#000000"))

    # Border color
    border: Color = field(default_factory=lambda: Color("#DEE2E6"))

    # Additional custom colors
    custom: dict[str, Color] = field(default_factory=dict)

    def get(self, name: str) -> Color | None:
        """Get color by name."""
        # Check standard attributes first
        name_normalized = name.replace("-", "_")
        if hasattr(self, name_normalized) and name_normalized != "custom":
            value = getattr(self, name_normalized)
            if isinstance(value, Color):
                return value
        # Check custom colors
        return self.custom.get(name)

    def set(self, name: str, color: Color) -> None:
        """Set a custom color."""
        self.custom[name] = color

    def generate_scale(self, base_color: Color, name: str) -> dict[str, Color]:
        """Generate a 5-step tint/shade scale from a base color.

        Args:
            base_color: Base color for the scale
            name: Name prefix for the scale

        Returns:
            Dictionary with {name}_100 through {name}_900 colors
        """
        return {
            f"{name}_100": base_color.lighten(0.8),
            f"{name}_300": base_color.lighten(0.4),
            f"{name}_500": base_color,
            f"{name}_700": base_color.darken(0.3),
            f"{name}_900": base_color.darken(0.5),
        }

    def to_dict(self) -> dict[str, str]:
        """Convert palette to dictionary."""
        result: dict[str, str] = {}
        for attr in dir(self):
            if attr.startswith("_") or attr in (
                "custom",
                "get",
                "set",
                "generate_scale",
                "to_dict",
            ):
                continue
            value = getattr(self, attr)
            if isinstance(value, Color):
                result[attr] = str(value)
        for name, color in self.custom.items():
            result[name] = str(color)
        return result


# ============================================================================
# Font Classes
# ============================================================================


@dataclass(frozen=True)
class Font:
    """Comprehensive font specification with full typographic control.

    Implements Missing frozen=True on value objects

    Examples:
        font = Font(
            family="Liberation Sans",
            fallback=["Arial", "Helvetica", "sans-serif"],
            size="11pt",
            weight=FontWeight.BOLD,
            italic=True,
            underline=UnderlineStyle.SINGLE,
            color=Color("#1A3A5C"),
        )
    """

    family: str = "Liberation Sans"
    fallback: list[str] = field(default_factory=lambda: ["Arial", "sans-serif"])
    size: str = "10pt"
    weight: FontWeight = FontWeight.NORMAL
    color: Color = field(default_factory=lambda: Color("#000000"))

    # Style
    italic: bool = False
    oblique: bool = False

    # Decoration
    underline: UnderlineStyle = UnderlineStyle.NONE
    underline_color: Color | None = None
    strikethrough: StrikethroughStyle = StrikethroughStyle.NONE
    strikethrough_color: Color | None = None

    # Effects
    superscript: bool = False
    subscript: bool = False
    shadow: bool = False
    outline: bool = False

    # Spacing
    letter_spacing: str | None = None  # e.g., "0.5pt", "1px"
    kerning: bool = True

    # Highlight/background
    highlight: Color | None = None

    def with_size(self, size: str) -> Font:
        """Create font with different size."""
        return Font(
            family=self.family,
            fallback=self.fallback.copy(),
            size=size,
            weight=self.weight,
            color=self.color,
            italic=self.italic,
            oblique=self.oblique,
            underline=self.underline,
            underline_color=self.underline_color,
            strikethrough=self.strikethrough,
            strikethrough_color=self.strikethrough_color,
            superscript=self.superscript,
            subscript=self.subscript,
            shadow=self.shadow,
            outline=self.outline,
            letter_spacing=self.letter_spacing,
            kerning=self.kerning,
            highlight=self.highlight,
        )

    def with_weight(self, weight: FontWeight) -> Font:
        """Create font with different weight."""
        return Font(
            family=self.family,
            fallback=self.fallback.copy(),
            size=self.size,
            weight=weight,
            color=self.color,
            italic=self.italic,
            oblique=self.oblique,
            underline=self.underline,
            underline_color=self.underline_color,
            strikethrough=self.strikethrough,
            strikethrough_color=self.strikethrough_color,
            superscript=self.superscript,
            subscript=self.subscript,
            shadow=self.shadow,
            outline=self.outline,
            letter_spacing=self.letter_spacing,
            kerning=self.kerning,
            highlight=self.highlight,
        )

    @property
    def is_bold(self) -> bool:
        """Check if font is bold."""
        return self.weight.is_bold

    @property
    def font_family_string(self) -> str:
        """Get full font family string with fallbacks."""
        families = [self.family, *self.fallback]
        return ", ".join(f'"{f}"' if " " in f else f for f in families)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "family": self.family,
            "fallback": self.fallback,
            "size": self.size,
            "weight": self.weight.value,
            "color": str(self.color),
            "italic": self.italic,
        }
        if self.underline != UnderlineStyle.NONE:
            result["underline"] = self.underline.value
        if self.strikethrough != StrikethroughStyle.NONE:
            result["strikethrough"] = self.strikethrough.value
        if self.letter_spacing:
            result["letter_spacing"] = self.letter_spacing
        return result


# ============================================================================
# Border Classes
# ============================================================================


@dataclass(frozen=True)
class BorderEdge:
    """Single border edge specification.

    Implements Missing frozen=True on value objects
    """

    style: BorderStyle = BorderStyle.NONE
    width: str = "1pt"
    color: Color = field(default_factory=lambda: Color("#000000"))

    def to_odf(self) -> str:
        """Convert to ODF border attribute string."""
        if self.style == BorderStyle.NONE:
            return "none"
        return f"{self.width} {self.style.value} {self.color.value}"

    def __str__(self) -> str:
        """Return string representation."""
        return self.to_odf()

    @classmethod
    def parse(cls, s: str) -> BorderEdge:
        """Parse from string like '1pt solid #000000'."""
        if s.lower().strip() == "none":
            return cls(style=BorderStyle.NONE)

        parts = s.strip().split()
        if len(parts) < 2:
            raise ValueError(f"Invalid border string: {s}")

        width = parts[0]
        style_str = parts[1].upper()

        try:
            style = BorderStyle[style_str]
        except KeyError:
            style = BorderStyle.SOLID

        color = Color(parts[2]) if len(parts) > 2 else Color("#000000")
        return cls(style=style, width=width, color=color)


# Keep Border for backward compatibility
@dataclass(frozen=True)
class Border:
    """Border specification (backward compatible).

    Implements Missing frozen=True on value objects

    Examples:
        Border()  # 1px solid black
        Border(width="2px", style=BorderStyle.DASHED, color=Color("#FF0000"))
    """

    width: str = "1px"
    style: BorderStyle = BorderStyle.SOLID
    color: Color = field(default_factory=lambda: Color("#000000"))

    def to_odf(self) -> str:
        """Convert to ODF border attribute string."""
        if self.style == BorderStyle.NONE:
            return "none"
        return f"{self.width} {self.style.value} {self.color.value}"

    def __str__(self) -> str:
        """Return string representation."""
        return self.to_odf()

    @classmethod
    def from_string(cls, border_str: str) -> Border:
        """Parse border from string like '1px solid #000000'."""
        parts = border_str.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid border string: {border_str}")

        width = parts[0]
        style_str = parts[1].upper()

        try:
            style = BorderStyle[style_str]
        except KeyError:
            style = BorderStyle.SOLID

        color = Color(parts[2]) if len(parts) > 2 else Color("#000000")
        return cls(width=width, style=style, color=color)

    def to_edge(self) -> BorderEdge:
        """Convert to BorderEdge."""
        return BorderEdge(style=self.style, width=self.width, color=self.color)


@dataclass
class Borders:
    """Complete borders specification with per-side control.

    Note: Not frozen as it's a container object, not a value object.

    Examples:
        # Per-side control
        borders = Borders(
            top=BorderEdge(BorderStyle.THICK, "2pt", Color("#1A3A5C")),
            bottom=BorderEdge(BorderStyle.THICK, "2pt", Color("#1A3A5C")),
        )

        # Factory methods
        box = Borders.all(BorderStyle.MEDIUM, "1pt", Color("#000000"))
        underline = Borders.bottom_only(BorderStyle.DOUBLE, "1pt")
    """

    top: BorderEdge | None = None
    bottom: BorderEdge | None = None
    left: BorderEdge | None = None
    right: BorderEdge | None = None
    diagonal_up: BorderEdge | None = None  # Diagonal from bottom-left to top-right
    diagonal_down: BorderEdge | None = None  # Diagonal from top-left to bottom-right

    @classmethod
    def none(cls) -> Borders:
        """Create borders with no sides."""
        return cls()

    @classmethod
    def all(
        cls,
        style: BorderStyle = BorderStyle.THIN,
        width: str = "1pt",
        color: Color | None = None,
    ) -> Borders:
        """Create borders with all sides the same."""
        if color is None:
            color = Color("#000000")
        edge = BorderEdge(style=style, width=width, color=color)
        return cls(top=edge, bottom=edge, left=edge, right=edge)

    @classmethod
    def box(
        cls,
        style: BorderStyle = BorderStyle.THIN,
        width: str = "1pt",
        color: Color | None = None,
    ) -> Borders:
        """Alias for all()."""
        return cls.all(style, width, color)

    @classmethod
    def horizontal(
        cls,
        style: BorderStyle = BorderStyle.THIN,
        width: str = "1pt",
        color: Color | None = None,
    ) -> Borders:
        """Create borders with top and bottom only."""
        if color is None:
            color = Color("#000000")
        edge = BorderEdge(style=style, width=width, color=color)
        return cls(top=edge, bottom=edge)

    @classmethod
    def vertical(
        cls,
        style: BorderStyle = BorderStyle.THIN,
        width: str = "1pt",
        color: Color | None = None,
    ) -> Borders:
        """Create borders with left and right only."""
        if color is None:
            color = Color("#000000")
        edge = BorderEdge(style=style, width=width, color=color)
        return cls(left=edge, right=edge)

    @classmethod
    def bottom_only(
        cls,
        style: BorderStyle = BorderStyle.THIN,
        width: str = "1pt",
        color: Color | None = None,
    ) -> Borders:
        """Create borders with bottom only."""
        if color is None:
            color = Color("#000000")
        return cls(bottom=BorderEdge(style=style, width=width, color=color))

    @classmethod
    def top_only(
        cls,
        style: BorderStyle = BorderStyle.THIN,
        width: str = "1pt",
        color: Color | None = None,
    ) -> Borders:
        """Create borders with top only."""
        if color is None:
            color = Color("#000000")
        return cls(top=BorderEdge(style=style, width=width, color=color))

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        result: dict[str, str] = {}
        if self.top:
            result["top"] = self.top.to_odf()
        if self.bottom:
            result["bottom"] = self.bottom.to_odf()
        if self.left:
            result["left"] = self.left.to_odf()
        if self.right:
            result["right"] = self.right.to_odf()
        return result


# ============================================================================
# Cell Fill Classes
# ============================================================================


@dataclass(frozen=True)
class GradientStop:
    """A color stop in a gradient.

    Implements Missing frozen=True on value objects
    """

    position: float  # 0.0 to 1.0
    color: Color


@dataclass(frozen=True)
class PatternFill:
    """Pattern fill specification.

    Implements Missing frozen=True on value objects
    """

    pattern_type: PatternType = PatternType.SOLID
    foreground_color: Color = field(default_factory=lambda: Color("#000000"))
    background_color: Color = field(default_factory=lambda: Color("#FFFFFF"))


@dataclass(frozen=True)
class GradientFill:
    """Gradient fill specification.

    Implements Missing frozen=True on value objects
    """

    type: GradientType = GradientType.LINEAR
    angle: float = 0.0  # For linear gradients (degrees)
    center_x: float = 0.5  # For radial gradients
    center_y: float = 0.5  # For radial gradients
    stops: tuple[GradientStop, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CellFill:
    """Cell background fill specification.

    Implements Missing frozen=True on value objects

    Supports solid colors, patterns, and gradients.

    Examples:
        # Solid fill
        solid = CellFill(solid_color=Color("#E8F4FD"))

        # Pattern fill
        striped = CellFill(pattern=PatternFill(
            pattern_type=PatternType.LIGHT_HORIZONTAL,
            foreground_color=Color("#4472C4"),
            background_color=Color("#FFFFFF"),
        ))

        # Gradient fill
        gradient = CellFill(gradient=GradientFill(
            type=GradientType.LINEAR,
            angle=90,
            stops=[
                GradientStop(0.0, Color("#FFFFFF")),
                GradientStop(1.0, Color("#4472C4")),
            ],
        ))
    """

    solid_color: Color | None = None
    pattern: PatternFill | None = None
    gradient: GradientFill | None = None
    opacity: float = 1.0  # 0.0 to 1.0

    @classmethod
    def solid(cls, color: Color) -> CellFill:
        """Create solid color fill."""
        return cls(solid_color=color)

    @classmethod
    def from_color(cls, color: Color | str) -> CellFill:
        """Create solid fill from color or hex string."""
        if isinstance(color, str):
            color = Color(color)
        return cls(solid_color=color)

    def to_color(self) -> Color | None:
        """Get the primary color of this fill."""
        if self.solid_color:
            return self.solid_color
        if self.pattern:
            return self.pattern.foreground_color
        if self.gradient and self.gradient.stops:
            return self.gradient.stops[0].color
        return None


# ============================================================================
# Number Format
# ============================================================================


@dataclass(frozen=True)
class NumberFormat:
    """Number format specification with ODF format code generation.

    Implements Missing frozen=True on value objects

    Examples:
        # Currency with accounting format
        accounting = NumberFormat(
            category=NumberFormatCategory.CURRENCY,
            currency_symbol="$",
            currency_position="before",
            decimal_places=2,
            use_thousands_separator=True,
            negative_format=NegativeFormat.PARENTHESES,
        )
        print(accounting.to_format_code())  # "$#,##0.00;($#,##0.00)"

        # Percentage
        pct = NumberFormat(category=NumberFormatCategory.PERCENTAGE, decimal_places=1)
        print(pct.to_format_code())  # "0.0%"

        # Date
        date_fmt = NumberFormat(
            category=NumberFormatCategory.DATE,
            date_pattern="MMMM DD, YYYY"
        )
    """

    category: NumberFormatCategory = NumberFormatCategory.GENERAL

    # Number options
    decimal_places: int = 2
    use_thousands_separator: bool = True
    min_integer_digits: int = 1

    # Negative number handling
    negative_format: NegativeFormat = NegativeFormat.MINUS

    # Currency options
    currency_symbol: str = "$"
    currency_position: str = "before"  # "before" or "after"
    currency_spacing: bool = False  # Space between symbol and number

    # Date/time patterns
    date_pattern: str = "YYYY-MM-DD"
    time_pattern: str = "HH:MM:SS"
    use_12_hour: bool = False

    # Custom format code
    custom_code: str | None = None

    # Locale
    locale: str | None = None

    def to_format_code(self) -> str:
        """Generate ODF format code string.

        Returns:
            ODF-compatible format code
        """
        if self.custom_code:
            return self.custom_code

        if self.category == NumberFormatCategory.GENERAL:
            return "General"

        if self.category == NumberFormatCategory.TEXT:
            return "@"

        if self.category == NumberFormatCategory.PERCENTAGE:
            decimals = "0" * self.decimal_places if self.decimal_places > 0 else ""
            if decimals:
                return f"0.{decimals}%"
            return "0%"

        if self.category == NumberFormatCategory.SCIENTIFIC:
            decimals = "0" * self.decimal_places if self.decimal_places > 0 else ""
            if decimals:
                return f"0.{decimals}E+00"
            return "0E+00"

        if self.category == NumberFormatCategory.NUMBER:
            return self._build_number_format()

        if self.category in (
            NumberFormatCategory.CURRENCY,
            NumberFormatCategory.ACCOUNTING,
        ):
            return self._build_currency_format()

        if self.category == NumberFormatCategory.DATE:
            return self._convert_date_pattern()

        if self.category == NumberFormatCategory.TIME:
            return self._convert_time_pattern()

        if self.category == NumberFormatCategory.DATETIME:
            return f"{self._convert_date_pattern()} {self._convert_time_pattern()}"

        if self.category == NumberFormatCategory.FRACTION:
            return "# ?/?"

        return "General"

    def _build_number_format(self) -> str:
        """Build format code for number category."""
        # Integer part
        if self.use_thousands_separator:
            integer = "#,##0"
        else:
            integer = "0" * self.min_integer_digits

        # Decimal part
        decimal = "." + "0" * self.decimal_places if self.decimal_places > 0 else ""

        positive = integer + decimal

        # Negative format
        if self.negative_format == NegativeFormat.MINUS:
            negative = f"-{positive}"
        elif self.negative_format == NegativeFormat.PARENTHESES:
            negative = f"({positive})"
        elif self.negative_format == NegativeFormat.RED:
            negative = f"[Red]{positive}"
        else:  # RED_PARENTHESES
            negative = f"[Red]({positive})"

        return f"{positive};{negative}"

    def _build_currency_format(self) -> str:
        """Build format code for currency/accounting category."""
        spacing = " " if self.currency_spacing else ""

        # Integer part
        if self.use_thousands_separator:
            integer = "#,##0"
        else:
            integer = "0" * self.min_integer_digits

        # Decimal part
        decimal = "." + "0" * self.decimal_places if self.decimal_places > 0 else ""

        number = integer + decimal

        # Add currency symbol
        if self.currency_position == "before":
            positive = f"{self.currency_symbol}{spacing}{number}"
        else:
            positive = f"{number}{spacing}{self.currency_symbol}"

        # Negative format
        if self.negative_format == NegativeFormat.MINUS:
            if self.currency_position == "before":
                negative = f"-{self.currency_symbol}{spacing}{number}"
            else:
                negative = f"-{number}{spacing}{self.currency_symbol}"
        elif self.negative_format == NegativeFormat.PARENTHESES:
            if self.currency_position == "before":
                negative = f"({self.currency_symbol}{spacing}{number})"
            else:
                negative = f"({number}{spacing}{self.currency_symbol})"
        elif self.negative_format == NegativeFormat.RED:
            negative = f"[Red]{positive}"
        else:  # RED_PARENTHESES
            if self.currency_position == "before":
                negative = f"[Red]({self.currency_symbol}{spacing}{number})"
            else:
                negative = f"[Red]({number}{spacing}{self.currency_symbol})"

        return f"{positive};{negative}"

    def _convert_date_pattern(self) -> str:
        """Convert date pattern to ODF format."""
        # Convert common patterns
        pattern = self.date_pattern
        pattern = pattern.replace("YYYY", "yyyy")
        pattern = pattern.replace("YY", "yy")
        pattern = pattern.replace("MMMM", "mmmm")
        pattern = pattern.replace("MMM", "mmm")
        pattern = pattern.replace("MM", "mm")
        pattern = pattern.replace("DD", "dd")
        pattern = pattern.replace("D", "d")
        return pattern

    def _convert_time_pattern(self) -> str:
        """Convert time pattern to ODF format."""
        pattern = self.time_pattern
        if self.use_12_hour:
            pattern = pattern.replace("HH", "hh")
            pattern = pattern.replace("H", "h")
            pattern += " AM/PM"
        else:
            pattern = pattern.replace("HH", "hh")
            pattern = pattern.replace("H", "h")
        pattern = pattern.replace("MM", "mm")
        pattern = pattern.replace("SS", "ss")
        return pattern


# ============================================================================
# Style Definition ()
# ============================================================================


@dataclass
class StyleDefinition:
    """Base style definition that can be extended and composed.

    Note: Not frozen as it's a mutable configuration object used during theme loading.

    Used as building blocks for CellStyle. Supports inheritance
    via 'extends' and composition via 'includes'.
    """

    name: str
    extends: str | None = None
    includes: list[str] = field(default_factory=list)  # Trait mixins

    # Typography
    font_family: str | None = None
    font_size: str | None = None
    font_weight: FontWeight | None = None
    font_color: Color | None = None
    italic: bool | None = None
    underline: UnderlineStyle | None = None
    strikethrough: StrikethroughStyle | None = None
    letter_spacing: str | None = None

    # Alignment
    text_align: TextAlign | None = None
    vertical_align: VerticalAlign | None = None
    text_rotation: int | None = None  # -90 to 90 degrees
    wrap_text: bool | None = None
    shrink_to_fit: bool | None = None
    indent: int | None = None

    # Background
    background_color: Color | None = None
    fill: CellFill | None = None

    # Borders
    border_top: Border | None = None
    border_bottom: Border | None = None
    border_left: Border | None = None
    border_right: Border | None = None
    borders: Borders | None = None

    # Spacing
    padding: str | None = None

    # Formatting
    number_format: NumberFormat | str | None = None
    date_format: str | None = None

    # Protection
    locked: bool | None = None
    hidden: bool | None = None  # Hide formula


@dataclass
class CellStyle:
    """Complete cell style definition with all properties resolved.

    Note: Not frozen as it needs to support with_overrides() and merge_with() operations.

    This is the final style used for rendering, with inheritance
    already applied.
    """

    name: str

    # Typography
    font: Font = field(default_factory=Font)
    text_align: TextAlign = TextAlign.LEFT
    vertical_align: VerticalAlign = VerticalAlign.MIDDLE
    text_rotation: int = 0
    wrap_text: bool = False
    shrink_to_fit: bool = False
    indent: int = 0

    # Background
    background_color: Color | None = None
    fill: CellFill | None = None

    # Borders (individual for backward compatibility)
    border_top: Border | None = None
    border_bottom: Border | None = None
    border_left: Border | None = None
    border_right: Border | None = None

    # Or complete borders
    borders: Borders | None = None

    # Spacing
    padding: str = "2pt"

    # Formatting
    number_format: NumberFormat | str | None = None
    date_format: str | None = None

    # Protection
    locked: bool = True
    hidden: bool = False

    def get_effective_borders(self) -> Borders:
        """Get borders, preferring the Borders object if set."""
        if self.borders:
            return self.borders
        return Borders(
            top=self.border_top.to_edge() if self.border_top else None,
            bottom=self.border_bottom.to_edge() if self.border_bottom else None,
            left=self.border_left.to_edge() if self.border_left else None,
            right=self.border_right.to_edge() if self.border_right else None,
        )

    def get_effective_fill(self) -> CellFill | None:
        """Get fill, creating from background_color if needed."""
        if self.fill:
            return self.fill
        if self.background_color:
            return CellFill.solid(self.background_color)
        return None

    def with_overrides(self, **kwargs: Any) -> CellStyle:
        """Create new style with overridden values.

        Args:
            **kwargs: Style properties to override

        Returns:
            New CellStyle with overrides applied
        """
        # Extract font-related overrides
        font_family = kwargs.get("font_family", self.font.family)
        font_size = kwargs.get("font_size", self.font.size)
        font_weight = kwargs.get("font_weight", self.font.weight)
        font_color = kwargs.get("font_color", self.font.color)
        italic = kwargs.get("italic", self.font.italic)
        underline = kwargs.get("underline", self.font.underline)

        # Create new font with overrides (Font is frozen)
        new_font = Font(
            family=font_family,
            fallback=self.font.fallback,  # Tuples are immutable, no need to copy
            size=font_size,
            weight=font_weight,
            color=font_color,
            italic=italic,
            underline=underline,
            strikethrough=self.font.strikethrough,
            letter_spacing=self.font.letter_spacing,
        )

        # Create result with all values
        result = CellStyle(
            name=kwargs.get("name", f"{self.name}_override"),
            font=new_font,
            text_align=kwargs.get("text_align", self.text_align),
            vertical_align=kwargs.get("vertical_align", self.vertical_align),
            text_rotation=kwargs.get("text_rotation", self.text_rotation),
            wrap_text=kwargs.get("wrap_text", self.wrap_text),
            shrink_to_fit=kwargs.get("shrink_to_fit", self.shrink_to_fit),
            indent=kwargs.get("indent", self.indent),
            background_color=kwargs.get("background_color", self.background_color),
            fill=kwargs.get("fill", self.fill),
            border_top=kwargs.get("border_top", self.border_top),
            border_bottom=kwargs.get("border_bottom", self.border_bottom),
            border_left=kwargs.get("border_left", self.border_left),
            border_right=kwargs.get("border_right", self.border_right),
            borders=kwargs.get("borders", self.borders),
            padding=kwargs.get("padding", self.padding),
            number_format=kwargs.get("number_format", self.number_format),
            date_format=kwargs.get("date_format", self.date_format),
            locked=kwargs.get("locked", self.locked),
            hidden=kwargs.get("hidden", self.hidden),
        )

        return result

    def merge_with(self, parent: CellStyle) -> CellStyle:
        """Merge this style with a parent, with self taking precedence.

        Args:
            parent: Parent style to merge from

        Returns:
            New merged CellStyle
        """
        return CellStyle(
            name=self.name,
            font=self.font if self.font.family != "Liberation Sans" else parent.font,
            text_align=(
                self.text_align
                if self.text_align != TextAlign.LEFT
                else parent.text_align
            ),
            vertical_align=(
                self.vertical_align
                if self.vertical_align != VerticalAlign.MIDDLE
                else parent.vertical_align
            ),
            text_rotation=(
                self.text_rotation if self.text_rotation != 0 else parent.text_rotation
            ),
            wrap_text=self.wrap_text if self.wrap_text else parent.wrap_text,
            shrink_to_fit=(
                self.shrink_to_fit if self.shrink_to_fit else parent.shrink_to_fit
            ),
            indent=self.indent if self.indent != 0 else parent.indent,
            background_color=self.background_color or parent.background_color,
            fill=self.fill or parent.fill,
            border_top=self.border_top or parent.border_top,
            border_bottom=self.border_bottom or parent.border_bottom,
            border_left=self.border_left or parent.border_left,
            border_right=self.border_right or parent.border_right,
            borders=self.borders or parent.borders,
            padding=self.padding if self.padding != "2pt" else parent.padding,
            number_format=self.number_format or parent.number_format,
            date_format=self.date_format or parent.date_format,
            locked=self.locked,
            hidden=self.hidden,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {
            "name": self.name,
            "font": self.font.to_dict(),
            "text_align": self.text_align.value,
            "vertical_align": self.vertical_align.value,
        }

        if self.text_rotation:
            result["text_rotation"] = self.text_rotation
        if self.wrap_text:
            result["wrap_text"] = self.wrap_text
        if self.shrink_to_fit:
            result["shrink_to_fit"] = self.shrink_to_fit
        if self.indent:
            result["indent"] = self.indent

        if self.background_color:
            result["background_color"] = str(self.background_color)

        if self.border_top:
            result["border_top"] = str(self.border_top)
        if self.border_bottom:
            result["border_bottom"] = str(self.border_bottom)
        if self.border_left:
            result["border_left"] = str(self.border_left)
        if self.border_right:
            result["border_right"] = str(self.border_right)

        result["padding"] = self.padding

        if self.number_format:
            if isinstance(self.number_format, NumberFormat):
                result["number_format"] = self.number_format.to_format_code()
            else:
                result["number_format"] = self.number_format
        if self.date_format:
            result["date_format"] = self.date_format

        if not self.locked:
            result["locked"] = self.locked
        if self.hidden:
            result["hidden"] = self.hidden

        return result


# ============================================================================
# Theme Classes (*)
# ============================================================================


@dataclass(frozen=True)
class ThemeSchema:
    """Theme metadata schema.

    Implements Missing frozen=True on value objects

    Contains theme identification and inheritance information.
    """

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    extends: str | None = None


@dataclass
class ThemeVariant:
    """Theme variant configuration for alternate color schemes.

    Implements Theme variants missing

    Allows defining alternate color palettes (dark mode, high contrast, etc.)
    that can be switched at runtime while keeping the same style definitions.

    Examples:
        # Define dark mode variant
        dark = ThemeVariant(
            name="dark",
            colors={
                "primary": Color("#6B8DD6"),
                "neutral_900": Color("#FFFFFF"),  # Inverted
                "neutral_100": Color("#1A1A1A"),  # Inverted
            }
        )
    """

    name: str
    description: str = ""
    colors: dict[str, Color] = field(default_factory=dict)


@dataclass
class Theme:
    """Complete theme definition.

    A theme contains:
    - Metadata (name, version, etc.)
    - Color palette
    - Font definitions
    - Style definitions with inheritance
    - Traits for composition
    - Conditional formatting rules
    """

    meta: ThemeSchema
    colors: ColorPalette = field(default_factory=ColorPalette)
    fonts: dict[str, Font] = field(default_factory=dict)
    traits: dict[str, StyleDefinition] = field(
        default_factory=dict
    )  # Reusable partial styles
    base_styles: dict[str, StyleDefinition] = field(default_factory=dict)
    styles: dict[str, StyleDefinition] = field(default_factory=dict)
    conditional_formats: dict[str, Any] = field(default_factory=dict)
    variants: dict[str, ThemeVariant] = field(default_factory=dict)

    # Active variant (None for base theme)
    _active_variant: str | None = field(default=None, repr=False)

    # Cache for resolved styles
    _resolved_cache: dict[str, CellStyle] = field(default_factory=dict, repr=False)

    @property
    def name(self) -> str:
        """Theme name."""
        return self.meta.name

    @property
    def version(self) -> str:
        """Theme version."""
        return self.meta.version

    @property
    def description(self) -> str:
        """Theme description."""
        return self.meta.description

    @property
    def active_variant(self) -> str | None:
        """Get active variant name."""
        return self._active_variant

    def set_variant(self, variant_name: str | None) -> None:
        """Switch to a different theme variant.

        Implements Theme variants missing

        Args:
            variant_name: Variant name (e.g., "dark", "high_contrast") or None for base theme

        Raises:
            KeyError: If variant not found
        """
        if variant_name is not None and variant_name not in self.variants:
            raise KeyError(f"Unknown variant: {variant_name}")

        self._active_variant = variant_name
        # Clear cache when variant changes
        self.clear_cache()

    def get_variant(self, variant_name: str) -> ThemeVariant:
        """Get a theme variant by name.

        Args:
            variant_name: Variant name

        Returns:
            ThemeVariant

        Raises:
            KeyError: If variant not found
        """
        if variant_name not in self.variants:
            raise KeyError(f"Unknown variant: {variant_name}")
        return self.variants[variant_name]

    def list_variants(self) -> list[str]:
        """List available variant names."""
        return list(self.variants.keys())

    def get_color(self, name: str) -> Color:
        """Get color by name, with variant override support.

        Args:
            name: Color name from palette

        Returns:
            Color instance (from active variant if available, otherwise base palette)

        Raises:
            KeyError: If color not found
        """
        # Check active variant first
        if self._active_variant is not None:
            variant = self.variants.get(self._active_variant)
            if variant and name in variant.colors:
                return variant.colors[name]

        # Fall back to base palette
        color = self.colors.get(name)
        if color is None:
            raise KeyError(f"Unknown color: {name}")
        return color

    def resolve_color_ref(self, ref: str) -> Color:
        """Resolve color reference like "{colors.primary}".

        Args:
            ref: Color reference string

        Returns:
            Resolved Color
        """
        if ref.startswith("{") and ref.endswith("}"):
            path = ref[1:-1].split(".")
            if path[0] == "colors" and len(path) > 1:
                # Check for modifiers like lighten, darken
                color_spec = path[1]
                if "|" in color_spec:
                    color_name, modifier = color_spec.split("|", 1)
                    base_color = self.get_color(color_name)
                    return self._apply_color_modifier(base_color, modifier)
                return self.get_color(path[1])
        # Treat as literal color value
        return Color(ref)

    def _apply_color_modifier(self, color: Color, modifier: str) -> Color:
        """Apply a color modifier like 'lighten:0.2'."""
        if ":" not in modifier:
            return color

        func, value = modifier.split(":", 1)
        amount = float(value)

        if func == "lighten":
            return color.lighten(amount)
        elif func == "darken":
            return color.darken(amount)
        elif func == "saturate":
            return color.saturate(amount)
        elif func == "desaturate":
            return color.desaturate(amount)

        return color

    def get_font(self, name: str) -> Font:
        """Get font by name."""
        if name in self.fonts:
            return self.fonts[name]
        raise KeyError(f"Unknown font: {name}")

    def get_style(self, name: str) -> CellStyle:
        """Get fully resolved style by name.

        Handles inheritance and composition by resolving parent styles
        and included traits first.

        Args:
            name: Style name

        Returns:
            Fully resolved CellStyle

        Raises:
            KeyError: If style not found
        """
        # Check cache first
        if name in self._resolved_cache:
            return self._resolved_cache[name]

        # Find style definition
        style_def = self.styles.get(name) or self.base_styles.get(name)
        if style_def is None:
            raise KeyError(f"Unknown style: {name}")

        # Resolve inheritance chain
        resolved = self._resolve_style(style_def, set())
        self._resolved_cache[name] = resolved
        return resolved

    def _resolve_style(
        self,
        style_def: StyleDefinition,
        visited: set[str],
    ) -> CellStyle:
        """Recursively resolve style with inheritance and composition.

        Args:
            style_def: Style definition to resolve
            visited: Set of visited style names (for cycle detection)

        Returns:
            Resolved CellStyle
        """
        if style_def.name in visited:
            raise ValueError(
                f"Circular inheritance detected for style: {style_def.name}"
            )
        visited.add(style_def.name)

        # Start with default or parent style
        if style_def.extends:
            parent_def = self.styles.get(style_def.extends) or self.base_styles.get(
                style_def.extends
            )
            if parent_def is None:
                raise KeyError(f"Parent style not found: {style_def.extends}")
            parent = self._resolve_style(parent_def, visited.copy())
        else:
            parent = CellStyle(name=style_def.name)

        # Apply included traits (in order)
        for trait_name in style_def.includes:
            trait_def = self.traits.get(trait_name)
            if trait_def:
                trait_style = self._resolve_style(trait_def, visited.copy())
                parent = trait_style.merge_with(parent)

        # Apply overrides from this style
        font = Font(
            family=style_def.font_family or parent.font.family,
            fallback=parent.font.fallback.copy(),
            size=style_def.font_size or parent.font.size,
            weight=style_def.font_weight or parent.font.weight,
            color=style_def.font_color or parent.font.color,
            italic=(
                style_def.italic if style_def.italic is not None else parent.font.italic
            ),
            underline=(
                style_def.underline
                if style_def.underline is not None
                else parent.font.underline
            ),
            strikethrough=(
                style_def.strikethrough
                if style_def.strikethrough is not None
                else parent.font.strikethrough
            ),
            letter_spacing=style_def.letter_spacing or parent.font.letter_spacing,
        )

        return CellStyle(
            name=style_def.name,
            font=font,
            text_align=style_def.text_align or parent.text_align,
            vertical_align=style_def.vertical_align or parent.vertical_align,
            text_rotation=(
                style_def.text_rotation
                if style_def.text_rotation is not None
                else parent.text_rotation
            ),
            wrap_text=(
                style_def.wrap_text
                if style_def.wrap_text is not None
                else parent.wrap_text
            ),
            shrink_to_fit=(
                style_def.shrink_to_fit
                if style_def.shrink_to_fit is not None
                else parent.shrink_to_fit
            ),
            indent=(
                style_def.indent if style_def.indent is not None else parent.indent
            ),
            background_color=style_def.background_color or parent.background_color,
            fill=style_def.fill or parent.fill,
            border_top=style_def.border_top or parent.border_top,
            border_bottom=style_def.border_bottom or parent.border_bottom,
            border_left=style_def.border_left or parent.border_left,
            border_right=style_def.border_right or parent.border_right,
            borders=style_def.borders or parent.borders,
            padding=style_def.padding or parent.padding,
            number_format=style_def.number_format or parent.number_format,
            date_format=style_def.date_format or parent.date_format,
            locked=style_def.locked if style_def.locked is not None else parent.locked,
            hidden=style_def.hidden if style_def.hidden is not None else parent.hidden,
        )

    def list_styles(self) -> list[str]:
        """List all available style names."""
        return list(set(self.base_styles.keys()) | set(self.styles.keys()))

    def list_traits(self) -> list[str]:
        """List all available trait names."""
        return list(self.traits.keys())

    def clear_cache(self) -> None:
        """Clear the resolved style cache."""
        self._resolved_cache.clear()

    def to_dict(self) -> dict[str, Any]:
        """Convert theme to dictionary for serialization."""
        return {
            "meta": {
                "name": self.meta.name,
                "version": self.meta.version,
                "description": self.meta.description,
                "author": self.meta.author,
                "extends": self.meta.extends,
            },
            "colors": self.colors.to_dict(),
            "fonts": {name: font.to_dict() for name, font in self.fonts.items()},
            "traits": {
                name: {"name": s.name, "extends": s.extends}
                for name, s in self.traits.items()
            },
            "base_styles": {
                name: {"name": s.name, "extends": s.extends}
                for name, s in self.base_styles.items()
            },
            "styles": {
                name: {"name": s.name, "extends": s.extends}
                for name, s in self.styles.items()
            },
        }
