"""Typography system with font pairing and type hierarchy.

Provides:
- Named font definitions with roles and fallbacks
- Type scale generation with configurable ratios
- Typography hierarchy for consistent text styling
- Professional font pairing presets
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from spreadsheet_dl.schema.styles import Color, Font, FontWeight

# ============================================================================
# Type Scale Ratios
# ============================================================================


class TypeScaleRatio(Enum):
    """Common type scale ratios for typography hierarchy.

    These ratios define the relationship between font sizes
    in a typographic scale.
    """

    # Smaller ratios (subtle progression)
    MINOR_SECOND = 1.067  # 15:16
    MAJOR_SECOND = 1.125  # 8:9

    # Medium ratios (common for text)
    MINOR_THIRD = 1.200  # 5:6 - Most popular
    MAJOR_THIRD = 1.250  # 4:5

    # Larger ratios (more dramatic)
    PERFECT_FOURTH = 1.333  # 3:4
    AUGMENTED_FOURTH = 1.414  # 1:sqrt(2)
    PERFECT_FIFTH = 1.500  # 2:3
    GOLDEN_RATIO = 1.618  # Golden ratio


# ============================================================================
# Font Role Definitions
# ============================================================================


class FontRole(Enum):
    """Font roles for different text purposes."""

    BODY = "body"  # Main body text
    HEADING = "heading"  # Headings and titles
    CODE = "code"  # Code and monospace content
    ACCENT = "accent"  # Special accents
    CAPTION = "caption"  # Captions and small text


@dataclass
class FontDefinition:
    """Complete font definition with role and fallback chain.

    Examples:
        body_font = FontDefinition(
            name="body",
            family="Liberation Sans",
            fallback=["Arial", "Helvetica", "sans-serif"],
            role=FontRole.BODY,
        )
    """

    name: str
    family: str
    fallback: list[str] = field(default_factory=list)
    role: FontRole = FontRole.BODY
    weight: FontWeight = FontWeight.NORMAL
    base_size: str = "10pt"

    def to_font(
        self,
        size: str | None = None,
        weight: FontWeight | None = None,
        color: Color | None = None,
        **kwargs: Any,
    ) -> Font:
        """Create a Font instance from this definition.

        Args:
            size: Override size (default uses base_size)
            weight: Override weight
            color: Override color
            **kwargs: Additional Font parameters

        Returns:
            Font instance
        """
        return Font(
            family=self.family,
            fallback=self.fallback.copy(),
            size=size or self.base_size,
            weight=weight or self.weight,
            color=color or Color("#000000"),
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "family": self.family,
            "fallback": self.fallback,
            "role": self.role.value,
            "weight": self.weight.value,
            "base_size": self.base_size,
        }


# ============================================================================
# Font Pairing System
# ============================================================================


@dataclass
class FontPairing:
    """Collection of font definitions for a complete pairing.

    A font pairing defines fonts for different text roles
    (body, headings, code, etc.) that work well together.

    Examples:
        pairing = FontPairing(
            name="professional",
            description="Professional sans-serif pairing",
            primary=FontDefinition(
                name="primary",
                family="Liberation Sans",
                fallback=["Arial", "sans-serif"],
                role=FontRole.BODY,
            ),
            heading=FontDefinition(
                name="heading",
                family="Liberation Sans",
                fallback=["Arial", "sans-serif"],
                role=FontRole.HEADING,
                weight=FontWeight.BOLD,
            ),
            monospace=FontDefinition(
                name="monospace",
                family="Liberation Mono",
                fallback=["Consolas", "monospace"],
                role=FontRole.CODE,
            ),
        )
    """

    name: str
    description: str = ""

    # Core fonts
    primary: FontDefinition = field(
        default_factory=lambda: FontDefinition(
            name="primary",
            family="Liberation Sans",
            fallback=["Arial", "Helvetica", "sans-serif"],
            role=FontRole.BODY,
        )
    )
    heading: FontDefinition = field(
        default_factory=lambda: FontDefinition(
            name="heading",
            family="Liberation Sans",
            fallback=["Arial", "Helvetica", "sans-serif"],
            role=FontRole.HEADING,
            weight=FontWeight.BOLD,
        )
    )
    monospace: FontDefinition = field(
        default_factory=lambda: FontDefinition(
            name="monospace",
            family="Liberation Mono",
            fallback=["Consolas", "Monaco", "Courier New", "monospace"],
            role=FontRole.CODE,
        )
    )

    # Optional additional fonts
    accent: FontDefinition | None = None
    caption: FontDefinition | None = None

    def get_font(self, role: FontRole) -> FontDefinition:
        """Get font definition by role.

        Args:
            role: Font role

        Returns:
            FontDefinition for the role

        Raises:
            KeyError: If role not defined
        """
        mapping = {
            FontRole.BODY: self.primary,
            FontRole.HEADING: self.heading,
            FontRole.CODE: self.monospace,
            FontRole.ACCENT: self.accent or self.heading,
            FontRole.CAPTION: self.caption or self.primary,
        }
        return mapping[role]

    def get_font_by_name(self, name: str) -> FontDefinition | None:
        """Get font definition by name.

        Args:
            name: Font name

        Returns:
            FontDefinition or None if not found
        """
        fonts = [self.primary, self.heading, self.monospace, self.accent, self.caption]
        for font in fonts:
            if font and font.name == name:
                return font
        return None

    def list_fonts(self) -> list[FontDefinition]:
        """List all defined fonts."""
        fonts = [self.primary, self.heading, self.monospace]
        if self.accent:
            fonts.append(self.accent)
        if self.caption:
            fonts.append(self.caption)
        return fonts

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "primary": self.primary.to_dict(),
            "heading": self.heading.to_dict(),
            "monospace": self.monospace.to_dict(),
        }
        if self.accent:
            result["accent"] = self.accent.to_dict()
        if self.caption:
            result["caption"] = self.caption.to_dict()
        return result


# Pre-built font pairings
FONT_PAIRINGS: dict[str, FontPairing] = {
    "professional": FontPairing(
        name="professional",
        description="Professional sans-serif pairing for business documents",
        primary=FontDefinition(
            name="primary",
            family="Liberation Sans",
            fallback=["Arial", "Helvetica", "sans-serif"],
            role=FontRole.BODY,
            base_size="10pt",
        ),
        heading=FontDefinition(
            name="heading",
            family="Liberation Sans",
            fallback=["Arial", "Helvetica", "sans-serif"],
            role=FontRole.HEADING,
            weight=FontWeight.BOLD,
            base_size="12pt",
        ),
        monospace=FontDefinition(
            name="monospace",
            family="Liberation Mono",
            fallback=["Consolas", "Monaco", "monospace"],
            role=FontRole.CODE,
            base_size="9pt",
        ),
    ),
    "modern": FontPairing(
        name="modern",
        description="Modern clean pairing with strong hierarchy",
        primary=FontDefinition(
            name="primary",
            family="Liberation Sans",
            fallback=["Helvetica Neue", "Arial", "sans-serif"],
            role=FontRole.BODY,
            weight=FontWeight.LIGHT,
            base_size="10pt",
        ),
        heading=FontDefinition(
            name="heading",
            family="Liberation Sans",
            fallback=["Helvetica Neue", "Arial", "sans-serif"],
            role=FontRole.HEADING,
            weight=FontWeight.SEMI_BOLD,
            base_size="14pt",
        ),
        monospace=FontDefinition(
            name="monospace",
            family="Liberation Mono",
            fallback=["SF Mono", "Consolas", "monospace"],
            role=FontRole.CODE,
            base_size="9pt",
        ),
    ),
    "traditional": FontPairing(
        name="traditional",
        description="Traditional serif pairing for formal documents",
        primary=FontDefinition(
            name="primary",
            family="Liberation Serif",
            fallback=["Times New Roman", "Georgia", "serif"],
            role=FontRole.BODY,
            base_size="11pt",
        ),
        heading=FontDefinition(
            name="heading",
            family="Liberation Serif",
            fallback=["Times New Roman", "Georgia", "serif"],
            role=FontRole.HEADING,
            weight=FontWeight.BOLD,
            base_size="14pt",
        ),
        monospace=FontDefinition(
            name="monospace",
            family="Liberation Mono",
            fallback=["Courier New", "monospace"],
            role=FontRole.CODE,
            base_size="10pt",
        ),
    ),
    "minimal": FontPairing(
        name="minimal",
        description="Minimal monospace-focused pairing",
        primary=FontDefinition(
            name="primary",
            family="Liberation Mono",
            fallback=["Consolas", "monospace"],
            role=FontRole.BODY,
            base_size="10pt",
        ),
        heading=FontDefinition(
            name="heading",
            family="Liberation Mono",
            fallback=["Consolas", "monospace"],
            role=FontRole.HEADING,
            weight=FontWeight.BOLD,
            base_size="12pt",
        ),
        monospace=FontDefinition(
            name="monospace",
            family="Liberation Mono",
            fallback=["Consolas", "monospace"],
            role=FontRole.CODE,
            base_size="10pt",
        ),
    ),
}


# ============================================================================
# Typography Hierarchy
# ============================================================================


@dataclass
class TypeSize:
    """A single size in the type scale."""

    name: str
    size: str  # e.g., "10pt"
    line_height: float = 1.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "size": self.size,
            "line_height": self.line_height,
        }


@dataclass
class HeadingStyle:
    """Style definition for a heading level."""

    level: int  # 1-6
    size: str
    weight: FontWeight = FontWeight.BOLD
    line_height: float = 1.25
    letter_spacing: str | None = None
    margin_top: str = "12pt"
    margin_bottom: str = "6pt"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level,
            "size": self.size,
            "weight": self.weight.value,
            "line_height": self.line_height,
            "letter_spacing": self.letter_spacing,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
        }


@dataclass
class Typography:
    """Complete typography hierarchy system.

    Defines consistent text sizes, line heights, and spacing
    for professional document typography.

    Examples:
        typography = Typography.from_scale(
            base_size=10,
            scale=TypeScaleRatio.MINOR_THIRD,
        )

        # Use sizes
        body_size = typography.get_size("base")  # "10pt"
        heading_size = typography.get_size("xl")  # "12pt"

        # Get heading style
        h1 = typography.get_heading(1)  # HeadingStyle with size "20pt"
    """

    # Scale configuration
    scale: TypeScaleRatio = TypeScaleRatio.MINOR_THIRD
    base_size: float = 10.0  # Base size in points
    unit: str = "pt"

    # Named sizes (auto-generated from scale if not provided)
    sizes: dict[str, TypeSize] = field(default_factory=dict)

    # Line heights
    line_height_tight: float = 1.25
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75

    # Heading definitions
    headings: dict[int, HeadingStyle] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Generate sizes and headings if not provided."""
        if not self.sizes:
            self._generate_sizes()
        if not self.headings:
            self._generate_headings()

    def _generate_sizes(self) -> None:
        """Generate type scale sizes."""
        ratio = self.scale.value

        # Calculate sizes relative to base
        sizes_config = [
            ("xs", -2),  # 2 steps down
            ("sm", -1),  # 1 step down
            ("base", 0),  # Base size
            ("lg", 1),  # 1 step up
            ("xl", 2),  # 2 steps up
            ("2xl", 3),  # 3 steps up
            ("3xl", 4),  # 4 steps up
            ("4xl", 5),  # 5 steps up
        ]

        for name, steps in sizes_config:
            size = self.base_size * (ratio**steps)
            # Round to 1 decimal place
            size = round(size, 1)

            # Adjust line height based on size
            if steps < 0 or steps == 0:
                line_height = self.line_height_normal
            elif steps <= 2:
                line_height = self.line_height_tight
            else:
                line_height = 1.2  # Very large text needs tighter leading

            self.sizes[name] = TypeSize(
                name=name,
                size=f"{size}{self.unit}",
                line_height=line_height,
            )

    def _generate_headings(self) -> None:
        """Generate heading styles."""
        # Map heading levels to size names
        heading_map = [
            (1, "3xl", FontWeight.BOLD, "-0.5pt"),
            (2, "2xl", FontWeight.BOLD, "-0.25pt"),
            (3, "xl", FontWeight.BOLD, None),
            (4, "lg", FontWeight.SEMI_BOLD, None),
            (5, "base", FontWeight.SEMI_BOLD, None),
            (6, "sm", FontWeight.SEMI_BOLD, "0.5pt"),
        ]

        for level, size_name, weight, letter_spacing in heading_map:
            type_size = self.sizes.get(size_name)
            if type_size:
                self.headings[level] = HeadingStyle(
                    level=level,
                    size=type_size.size,
                    weight=weight,
                    line_height=self.line_height_tight,
                    letter_spacing=letter_spacing,
                )

    def get_size(self, name: str) -> str:
        """Get size value by name.

        Args:
            name: Size name (xs, sm, base, lg, xl, 2xl, 3xl, 4xl)

        Returns:
            Size string (e.g., "10pt")

        Raises:
            KeyError: If size not found
        """
        if name not in self.sizes:
            raise KeyError(f"Unknown size: {name}")
        return self.sizes[name].size

    def get_type_size(self, name: str) -> TypeSize:
        """Get TypeSize object by name.

        Args:
            name: Size name

        Returns:
            TypeSize object

        Raises:
            KeyError: If size not found
        """
        if name not in self.sizes:
            raise KeyError(f"Unknown size: {name}")
        return self.sizes[name]

    def get_heading(self, level: int) -> HeadingStyle:
        """Get heading style by level.

        Args:
            level: Heading level (1-6)

        Returns:
            HeadingStyle object

        Raises:
            KeyError: If level not defined
        """
        if level not in self.headings:
            raise KeyError(f"Unknown heading level: {level}")
        return self.headings[level]

    def get_line_height(self, style: str = "normal") -> float:
        """Get line height by style name.

        Args:
            style: Line height style (tight, normal, relaxed)

        Returns:
            Line height multiplier
        """
        mapping = {
            "tight": self.line_height_tight,
            "normal": self.line_height_normal,
            "relaxed": self.line_height_relaxed,
        }
        return mapping.get(style, self.line_height_normal)

    @classmethod
    def from_scale(
        cls,
        base_size: float = 10.0,
        scale: TypeScaleRatio = TypeScaleRatio.MINOR_THIRD,
        unit: str = "pt",
    ) -> Typography:
        """Create typography with specified scale.

        Args:
            base_size: Base font size
            scale: Type scale ratio
            unit: Size unit (pt, px, etc.)

        Returns:
            Typography instance
        """
        return cls(base_size=base_size, scale=scale, unit=unit)

    @classmethod
    def professional(cls) -> Typography:
        """Create professional typography preset."""
        return cls.from_scale(
            base_size=10.0,
            scale=TypeScaleRatio.MINOR_THIRD,
        )

    @classmethod
    def compact(cls) -> Typography:
        """Create compact typography for dense tables."""
        return cls.from_scale(
            base_size=9.0,
            scale=TypeScaleRatio.MAJOR_SECOND,
        )

    @classmethod
    def presentation(cls) -> Typography:
        """Create larger typography for presentations."""
        return cls.from_scale(
            base_size=14.0,
            scale=TypeScaleRatio.PERFECT_FOURTH,
        )

    def list_sizes(self) -> list[str]:
        """List all available size names."""
        return list(self.sizes.keys())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scale": self.scale.name,
            "base_size": f"{self.base_size}{self.unit}",
            "sizes": {name: ts.to_dict() for name, ts in self.sizes.items()},
            "line_height": {
                "tight": self.line_height_tight,
                "normal": self.line_height_normal,
                "relaxed": self.line_height_relaxed,
            },
            "headings": {
                f"h{level}": hs.to_dict() for level, hs in self.headings.items()
            },
        }


# Pre-built typography presets
TYPOGRAPHY_PRESETS: dict[str, Typography] = {
    "professional": Typography.professional(),
    "compact": Typography.compact(),
    "presentation": Typography.presentation(),
}


# ============================================================================
# Helper Functions
# ============================================================================


def get_font_pairing(name: str) -> FontPairing:
    """Get a pre-built font pairing by name.

    Args:
        name: Pairing name (professional, modern, traditional, minimal)

    Returns:
        FontPairing instance

    Raises:
        KeyError: If pairing not found
    """
    if name not in FONT_PAIRINGS:
        raise KeyError(
            f"Unknown font pairing: {name}. Available: {list(FONT_PAIRINGS.keys())}"
        )
    return FONT_PAIRINGS[name]


def get_typography(name: str) -> Typography:
    """Get a pre-built typography preset by name.

    Args:
        name: Typography name (professional, compact, presentation)

    Returns:
        Typography instance

    Raises:
        KeyError: If preset not found
    """
    if name not in TYPOGRAPHY_PRESETS:
        raise KeyError(
            f"Unknown typography: {name}. Available: {list(TYPOGRAPHY_PRESETS.keys())}"
        )
    return TYPOGRAPHY_PRESETS[name]


def list_font_pairings() -> list[str]:
    """List available font pairing names."""
    return list(FONT_PAIRINGS.keys())


def list_typography_presets() -> list[str]:
    """List available typography preset names."""
    return list(TYPOGRAPHY_PRESETS.keys())
