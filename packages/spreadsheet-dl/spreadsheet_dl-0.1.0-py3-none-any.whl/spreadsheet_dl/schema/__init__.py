"""Schema package - Declarative style and theme definitions.

This package provides:
- Style dataclasses for type-safe style definitions
- Length value objects for consistent dimension handling
- YAML theme loader with validation
- Style inheritance and color resolution
- Number and currency formatting
- Cell fill patterns and gradients
- Font pairing and typography hierarchy
- Print layout configuration
"""

from spreadsheet_dl.schema.loader import ThemeLoader
from spreadsheet_dl.schema.print_layout import (
    # Headers and footers
    HeaderFooter,
    HeaderFooterContent,
    HeaderFooterSection,
    PageBreak,
    PageMargins,
    PageOrientation,
    # Page setup
    PageSetup,
    PageSetupBuilder,
    PageSize,
    # Print area
    PrintArea,
    # Presets
    PrintPresets,
    PrintQuality,
    PrintScale,
    RepeatConfig,
)
from spreadsheet_dl.schema.styles import (
    CSS_NAMED_COLORS,
    # Borders
    Border,
    BorderEdge,
    Borders,
    BorderStyle,
    # Cell fill
    CellFill,
    # Core styles
    CellStyle,
    # Colors
    Color,
    ColorPalette,
    # Fonts
    Font,
    FontWeight,
    GradientFill,
    GradientStop,
    GradientType,
    # Number formats
    NegativeFormat,
    NumberFormat,
    NumberFormatCategory,
    PatternFill,
    PatternType,
    StrikethroughStyle,
    # Styles
    StyleDefinition,
    # Alignment
    TextAlign,
    # Theme
    Theme,
    ThemeSchema,
    UnderlineStyle,
    VerticalAlign,
)
from spreadsheet_dl.schema.typography import (
    FONT_PAIRINGS,
    TYPOGRAPHY_PRESETS,
    # Font pairing
    FontDefinition,
    FontPairing,
    FontRole,
    # Typography hierarchy
    HeadingStyle,
    TypeScaleRatio,
    TypeSize,
    Typography,
    get_font_pairing,
    get_typography,
    list_font_pairings,
    list_typography_presets,
)
from spreadsheet_dl.schema.units import (
    Length,
    LengthUnit,
    cm,
    inches,
    mm,
    parse_length,
    pt,
)
from spreadsheet_dl.schema.validation import (
    SchemaValidationError,
    validate_color,
    validate_style,
    validate_theme,
)

__all__ = [
    "CSS_NAMED_COLORS",
    "FONT_PAIRINGS",
    "TYPOGRAPHY_PRESETS",
    # Borders
    "Border",
    "BorderEdge",
    "BorderStyle",
    "Borders",
    # Cell Fill
    "CellFill",
    # Cell Style
    "CellStyle",
    # Colors
    "Color",
    "ColorPalette",
    # Fonts
    "Font",
    # Font Pairing
    "FontDefinition",
    "FontPairing",
    "FontRole",
    "FontWeight",
    "GradientFill",
    "GradientStop",
    "GradientType",
    # Headers and Footers
    "HeaderFooter",
    "HeaderFooterContent",
    "HeaderFooterSection",
    # Typography Hierarchy
    "HeadingStyle",
    # Length
    "Length",
    "LengthUnit",
    "NegativeFormat",
    # Number Format
    "NumberFormat",
    "NumberFormatCategory",
    "PageBreak",
    "PageMargins",
    "PageOrientation",
    # Page Setup
    "PageSetup",
    "PageSetupBuilder",
    "PageSize",
    "PatternFill",
    "PatternType",
    # Print Area
    "PrintArea",
    # Print Presets
    "PrintPresets",
    "PrintQuality",
    "PrintScale",
    "RepeatConfig",
    # Validation
    "SchemaValidationError",
    "StrikethroughStyle",
    "StyleDefinition",
    # Alignment
    "TextAlign",
    # Theme (*)
    "Theme",
    # Loader
    "ThemeLoader",
    "ThemeSchema",
    "TypeScaleRatio",
    "TypeSize",
    "Typography",
    "UnderlineStyle",
    "VerticalAlign",
    "cm",
    "get_font_pairing",
    "get_typography",
    "inches",
    "list_font_pairings",
    "list_typography_presets",
    "mm",
    "parse_length",
    "pt",
    "validate_color",
    "validate_style",
    "validate_theme",
]
