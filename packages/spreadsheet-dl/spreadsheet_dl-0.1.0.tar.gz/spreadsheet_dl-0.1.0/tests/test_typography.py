"""
Tests for typography module.

Tests:
"""

import pytest

from spreadsheet_dl.schema import (
    FontDefinition,
    FontPairing,
    FontRole,
    # Typography
    HeadingStyle,
    TypeScaleRatio,
    TypeSize,
    Typography,
    get_font_pairing,
    get_typography,
    list_font_pairings,
    list_typography_presets,
)
from spreadsheet_dl.schema.styles import Font, FontWeight

pytestmark = [pytest.mark.unit, pytest.mark.rendering]

# ============================================================================
# Font Definition Tests
# ============================================================================


class TestFontDefinition:
    """Tests for FontDefinition class."""

    def test_basic_definition(self) -> None:
        """Test basic font definition creation."""
        font_def = FontDefinition(
            name="body",
            family="Liberation Sans",
            fallback=["Arial", "sans-serif"],
            role=FontRole.BODY,
        )
        assert font_def.name == "body"
        assert font_def.family == "Liberation Sans"
        assert font_def.fallback == ["Arial", "sans-serif"]
        assert font_def.role == FontRole.BODY

    def test_to_font(self) -> None:
        """Test converting definition to Font instance."""
        font_def = FontDefinition(
            name="heading",
            family="Liberation Sans",
            role=FontRole.HEADING,
            weight=FontWeight.BOLD,
            base_size="12pt",
        )
        font = font_def.to_font()
        assert isinstance(font, Font)
        assert font.family == "Liberation Sans"
        assert font.weight == FontWeight.BOLD
        assert font.size == "12pt"

    def test_to_font_with_overrides(self) -> None:
        """Test converting with overrides."""
        font_def = FontDefinition(
            name="body",
            family="Liberation Sans",
            base_size="10pt",
        )
        font = font_def.to_font(size="14pt", weight=FontWeight.BOLD)
        assert font.size == "14pt"
        assert font.weight == FontWeight.BOLD

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        font_def = FontDefinition(
            name="body",
            family="Liberation Sans",
            role=FontRole.BODY,
        )
        data = font_def.to_dict()
        assert data["name"] == "body"
        assert data["family"] == "Liberation Sans"
        assert data["role"] == "body"


# ============================================================================
# Font Pairing Tests
# ============================================================================


class TestFontPairing:
    """Tests for FontPairing class."""

    def test_default_pairing(self) -> None:
        """Test default font pairing."""
        pairing = FontPairing(name="default")
        assert pairing.primary is not None
        assert pairing.heading is not None
        assert pairing.monospace is not None

    def test_get_font_by_role(self) -> None:
        """Test getting font by role."""
        pairing = FontPairing(name="test")
        body = pairing.get_font(FontRole.BODY)
        assert body == pairing.primary

        heading = pairing.get_font(FontRole.HEADING)
        assert heading == pairing.heading

        code = pairing.get_font(FontRole.CODE)
        assert code == pairing.monospace

    def test_get_font_by_name(self) -> None:
        """Test getting font by name."""
        pairing = FontPairing(name="test")
        font = pairing.get_font_by_name("primary")
        assert font == pairing.primary

    def test_list_fonts(self) -> None:
        """Test listing all fonts."""
        pairing = FontPairing(name="test")
        fonts = pairing.list_fonts()
        assert len(fonts) >= 3  # primary, heading, monospace

    def test_to_dict(self) -> None:
        """Test serialization."""
        pairing = FontPairing(
            name="test",
            description="Test pairing",
        )
        data = pairing.to_dict()
        assert data["name"] == "test"
        assert data["description"] == "Test pairing"
        assert "primary" in data
        assert "heading" in data
        assert "monospace" in data


class TestFontPairingPresets:
    """Tests for pre-built font pairings."""

    def test_professional_pairing(self) -> None:
        """Test professional font pairing."""
        pairing = get_font_pairing("professional")
        assert pairing.name == "professional"
        assert pairing.primary.family == "Liberation Sans"

    def test_modern_pairing(self) -> None:
        """Test modern font pairing."""
        pairing = get_font_pairing("modern")
        assert pairing.name == "modern"

    def test_traditional_pairing(self) -> None:
        """Test traditional font pairing."""
        pairing = get_font_pairing("traditional")
        assert pairing.name == "traditional"
        assert "Serif" in pairing.primary.family

    def test_minimal_pairing(self) -> None:
        """Test minimal font pairing."""
        pairing = get_font_pairing("minimal")
        assert pairing.name == "minimal"
        # Minimal uses monospace for everything
        assert "Mono" in pairing.primary.family

    def test_list_pairings(self) -> None:
        """Test listing available pairings."""
        pairings = list_font_pairings()
        assert "professional" in pairings
        assert "modern" in pairings
        assert "traditional" in pairings
        assert "minimal" in pairings

    def test_unknown_pairing_raises(self) -> None:
        """Test that unknown pairing raises KeyError."""
        with pytest.raises(KeyError):
            get_font_pairing("nonexistent")


# ============================================================================
# Type Scale Tests
# ============================================================================


class TestTypeScaleRatio:
    """Tests for TypeScaleRatio enum."""

    def test_minor_third(self) -> None:
        """Test minor third ratio."""
        assert TypeScaleRatio.MINOR_THIRD.value == 1.2

    def test_golden_ratio(self) -> None:
        """Test golden ratio."""
        assert TypeScaleRatio.GOLDEN_RATIO.value == 1.618


class TestTypeSize:
    """Tests for TypeSize class."""

    def test_type_size(self) -> None:
        """Test TypeSize creation."""
        size = TypeSize(name="base", size="10pt", line_height=1.5)
        assert size.name == "base"
        assert size.size == "10pt"
        assert size.line_height == 1.5

    def test_to_dict(self) -> None:
        """Test serialization."""
        size = TypeSize(name="lg", size="12pt")
        data = size.to_dict()
        assert data["name"] == "lg"
        assert data["size"] == "12pt"


class TestHeadingStyle:
    """Tests for HeadingStyle class."""

    def test_heading_style(self) -> None:
        """Test HeadingStyle creation."""
        h1 = HeadingStyle(
            level=1,
            size="20pt",
            weight=FontWeight.BOLD,
            line_height=1.25,
        )
        assert h1.level == 1
        assert h1.size == "20pt"
        assert h1.weight == FontWeight.BOLD

    def test_to_dict(self) -> None:
        """Test serialization."""
        h1 = HeadingStyle(level=1, size="20pt")
        data = h1.to_dict()
        assert data["level"] == 1
        assert data["size"] == "20pt"


# ============================================================================
# Typography Tests
# ============================================================================


class TestTypography:
    """Tests for Typography class."""

    def test_default_typography(self) -> None:
        """Test default typography creation."""
        typo = Typography()
        assert typo.base_size == 10.0
        assert typo.scale == TypeScaleRatio.MINOR_THIRD
        assert len(typo.sizes) > 0
        assert len(typo.headings) > 0

    def test_custom_scale(self) -> None:
        """Test typography with custom scale."""
        typo = Typography.from_scale(
            base_size=12.0,
            scale=TypeScaleRatio.PERFECT_FOURTH,
        )
        assert typo.base_size == 12.0
        assert typo.scale == TypeScaleRatio.PERFECT_FOURTH

    def test_get_size(self) -> None:
        """Test getting size by name."""
        typo = Typography()
        base = typo.get_size("base")
        assert "pt" in base

        lg = typo.get_size("lg")
        assert "pt" in lg

    def test_get_type_size(self) -> None:
        """Test getting TypeSize object."""
        typo = Typography()
        ts = typo.get_type_size("base")
        assert isinstance(ts, TypeSize)
        assert ts.name == "base"

    def test_get_heading(self) -> None:
        """Test getting heading style."""
        typo = Typography()
        h1 = typo.get_heading(1)
        assert isinstance(h1, HeadingStyle)
        assert h1.level == 1

    def test_get_line_height(self) -> None:
        """Test getting line height."""
        typo = Typography()
        assert typo.get_line_height("tight") == typo.line_height_tight
        assert typo.get_line_height("normal") == typo.line_height_normal
        assert typo.get_line_height("relaxed") == typo.line_height_relaxed

    def test_list_sizes(self) -> None:
        """Test listing available sizes."""
        typo = Typography()
        sizes = typo.list_sizes()
        assert "xs" in sizes
        assert "base" in sizes
        assert "3xl" in sizes

    def test_scale_progression(self) -> None:
        """Test that sizes follow the scale."""
        typo = Typography.from_scale(base_size=10.0, scale=TypeScaleRatio.MINOR_THIRD)

        # Extract numeric values
        base_val = float(typo.get_size("base").replace("pt", ""))
        lg_val = float(typo.get_size("lg").replace("pt", ""))

        # lg should be larger than base by the ratio
        ratio = lg_val / base_val
        assert abs(ratio - 1.2) < 0.1  # Minor third is 1.2

    def test_to_dict(self) -> None:
        """Test serialization."""
        typo = Typography()
        data = typo.to_dict()
        assert "scale" in data
        assert "base_size" in data
        assert "sizes" in data
        assert "headings" in data


class TestTypographyPresets:
    """Tests for typography presets."""

    def test_professional_preset(self) -> None:
        """Test professional typography preset."""
        typo = get_typography("professional")
        assert typo.base_size == 10.0

    def test_compact_preset(self) -> None:
        """Test compact typography preset."""
        typo = get_typography("compact")
        assert typo.base_size == 9.0

    def test_presentation_preset(self) -> None:
        """Test presentation typography preset."""
        typo = get_typography("presentation")
        assert typo.base_size == 14.0

    def test_list_presets(self) -> None:
        """Test listing available presets."""
        presets = list_typography_presets()
        assert "professional" in presets
        assert "compact" in presets
        assert "presentation" in presets

    def test_unknown_preset_raises(self) -> None:
        """Test that unknown preset raises KeyError."""
        with pytest.raises(KeyError):
            get_typography("nonexistent")


class TestTypographyIntegration:
    """Integration tests for typography system."""

    def test_typography_with_font_pairing(self) -> None:
        """Test using typography with font pairing."""
        pairing = get_font_pairing("professional")
        typo = get_typography("professional")

        # Create a heading font from pairing with typography size
        heading_def = pairing.heading
        h1_style = typo.get_heading(1)

        # Should be able to create a font with the heading size
        font = heading_def.to_font(size=h1_style.size)
        assert font.size == h1_style.size
        assert font.family == heading_def.family

    def test_complete_hierarchy(self) -> None:
        """Test complete typography hierarchy."""
        typo = Typography.professional()

        # Check all heading levels exist
        for level in range(1, 7):
            heading = typo.get_heading(level)
            assert heading.level == level
            assert heading.size is not None

        # Check size progression makes sense (h1 > h6)
        h1_size = float(typo.get_heading(1).size.replace("pt", ""))
        h6_size = float(typo.get_heading(6).size.replace("pt", ""))
        assert h1_size > h6_size
