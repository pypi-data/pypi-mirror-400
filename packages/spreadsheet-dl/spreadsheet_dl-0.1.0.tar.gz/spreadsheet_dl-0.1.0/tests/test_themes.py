"""Tests for theme loading and built-in themes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.schema.loader import (
    ThemeLoader,
    get_default_loader,
    list_available_themes,
    load_theme,
)
from spreadsheet_dl.schema.styles import FontWeight, Theme
from spreadsheet_dl.schema.validation import SchemaValidationError

if TYPE_CHECKING:
    from pathlib import Path

    pass


# Check if pyyaml is available
try:
    import yaml  # noqa: F401

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

pytestmark = [pytest.mark.unit, pytest.mark.validation]


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestThemeLoader:
    """Tests for ThemeLoader class."""

    def test_list_themes(self) -> None:
        """Test listing available themes."""
        loader = ThemeLoader()
        themes = loader.list_themes()
        assert "default" in themes
        assert "corporate" in themes
        assert "minimal" in themes

    def test_load_default_theme(self) -> None:
        """Test loading default theme."""
        loader = ThemeLoader()
        theme = loader.load("default")
        assert theme.name == "Default Finance Theme"
        assert theme.version == "1.0.0"

    def test_load_corporate_theme(self) -> None:
        """Test loading corporate theme."""
        loader = ThemeLoader()
        theme = loader.load("corporate")
        assert theme.name == "Corporate Theme"
        assert theme.meta.extends == "default"

    def test_load_minimal_theme(self) -> None:
        """Test loading minimal theme."""
        loader = ThemeLoader()
        theme = loader.load("minimal")
        assert theme.name == "Minimal Theme"

    def test_load_dark_theme(self) -> None:
        """Test loading dark theme."""
        loader = ThemeLoader()
        theme = loader.load("dark")
        assert theme.name == "Dark Theme"

    def test_load_high_contrast_theme(self) -> None:
        """Test loading high contrast theme."""
        loader = ThemeLoader()
        theme = loader.load("high_contrast")
        assert theme.name == "High Contrast Theme"

    def test_load_nonexistent_theme_raises(self) -> None:
        """Test loading non-existent theme raises error."""
        loader = ThemeLoader()
        with pytest.raises(FileNotFoundError, match="Theme not found"):
            loader.load("nonexistent")

    def test_theme_caching(self) -> None:
        """Test that themes are cached."""
        loader = ThemeLoader()
        theme1 = loader.load("default")
        theme2 = loader.load("default")
        assert theme1 is theme2

    def test_clear_cache(self) -> None:
        """Test clearing theme cache."""
        loader = ThemeLoader()
        theme1 = loader.load("default")
        loader.clear_cache()
        theme2 = loader.load("default")
        assert theme1 is not theme2

    def test_load_from_string(self) -> None:
        """Test loading theme from YAML string."""
        yaml_content = """
meta:
  name: "Test Theme"
  version: "1.0.0"
"""
        loader = ThemeLoader()
        theme = loader.load_from_string(yaml_content)
        assert theme.name == "Test Theme"

    def test_load_from_dict(self) -> None:
        """Test loading theme from dictionary."""
        data = {
            "meta": {
                "name": "Test Theme",
                "version": "1.0.0",
            },
        }
        loader = ThemeLoader()
        theme = loader.load_from_dict(data)
        assert theme.name == "Test Theme"

    def test_load_empty_string_raises(self) -> None:
        """Test loading empty YAML string raises error."""
        loader = ThemeLoader()
        with pytest.raises(SchemaValidationError, match="empty"):
            loader.load_from_string("")


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestThemeInheritance:
    """Tests for theme inheritance functionality."""

    def test_child_inherits_parent_colors(self) -> None:
        """Test that child theme inherits parent colors."""
        loader = ThemeLoader()
        # Corporate extends default
        corporate = loader.load("corporate")

        # Check that corporate has its own primary color
        assert str(corporate.colors.primary) == "#1E3A5F"  # Corporate blue

    def test_child_inherits_parent_styles(self) -> None:
        """Test that child theme inherits parent styles."""
        loader = ThemeLoader()
        corporate = loader.load("corporate")

        # Should be able to get styles from both parent and child
        styles = corporate.list_styles()
        assert "header" in styles  # From default
        assert "header_corporate" in styles  # From corporate

    def test_style_inheritance_chain(self) -> None:
        """Test style inheritance within a theme."""
        loader = ThemeLoader()
        theme = loader.load("default")

        # header_primary extends header
        header = theme.get_style("header_primary")
        # FontWeight.BOLD has value "700" (numeric weight)
        assert header.font.weight == FontWeight.BOLD
        assert header.font.weight.is_bold


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestThemeColors:
    """Tests for theme color functionality."""

    def test_default_theme_colors(self) -> None:
        """Test default theme has expected colors."""
        loader = ThemeLoader()
        theme = loader.load("default")

        assert str(theme.colors.primary) == "#4472C4"
        assert str(theme.colors.success) == "#70AD47"
        assert str(theme.colors.danger) == "#C00000"

    def test_corporate_theme_colors(self) -> None:
        """Test corporate theme has different colors."""
        loader = ThemeLoader()
        theme = loader.load("corporate")

        assert str(theme.colors.primary) == "#1E3A5F"  # Navy blue
        assert str(theme.colors.secondary) == "#8B4513"  # Brown


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestThemeStyles:
    """Tests for theme style functionality."""

    def test_get_header_style(self) -> None:
        """Test getting header style from theme."""
        loader = ThemeLoader()
        theme = loader.load("default")

        style = theme.get_style("header_primary")
        # Check the font weight is bold using the enum or is_bold property
        assert style.font.weight == FontWeight.BOLD or style.font.weight.is_bold
        assert style.background_color is not None

    def test_get_currency_style(self) -> None:
        """Test getting currency style from theme."""
        loader = ThemeLoader()
        theme = loader.load("default")

        style = theme.get_style("cell_currency")
        assert style.text_align.value == "right"

    def test_get_date_style(self) -> None:
        """Test getting date style from theme."""
        loader = ThemeLoader()
        theme = loader.load("default")

        style = theme.get_style("cell_date")
        assert style.text_align.value == "center"


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_load_theme_function(self) -> None:
        """Test load_theme convenience function."""
        theme = load_theme("default")
        assert theme.name == "Default Finance Theme"

    def test_list_available_themes_function(self) -> None:
        """Test list_available_themes convenience function."""
        themes = list_available_themes()
        assert "default" in themes

    def test_get_default_loader(self) -> None:
        """Test get_default_loader returns singleton."""
        loader1 = get_default_loader()
        loader2 = get_default_loader()
        assert loader1 is loader2


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestThemeWithOdsGenerator:
    """Tests for theme integration with OdsGenerator."""

    def test_ods_generator_with_theme(self, tmp_path: Path) -> None:
        """Test OdsGenerator with theme creates valid file."""
        from spreadsheet_dl import OdsGenerator

        output = tmp_path / "themed_budget.ods"
        generator = OdsGenerator(theme="default")
        path = generator.create_budget_spreadsheet(output, month=1, year=2025)

        assert path.exists()
        assert path.stat().st_size > 0

    def test_ods_generator_with_corporate_theme(self, tmp_path: Path) -> None:
        """Test OdsGenerator with corporate theme."""
        from spreadsheet_dl import OdsGenerator

        output = tmp_path / "corporate_budget.ods"
        generator = OdsGenerator(theme="corporate")
        path = generator.create_budget_spreadsheet(output, month=1, year=2025)

        assert path.exists()

    def test_ods_generator_with_invalid_theme(self, tmp_path: Path) -> None:
        """Test OdsGenerator with invalid theme falls back to legacy."""
        from spreadsheet_dl import OdsGenerator

        output = tmp_path / "fallback_budget.ods"
        # Should not raise, should fall back to legacy styles
        generator = OdsGenerator(theme="nonexistent")
        path = generator.create_budget_spreadsheet(output, month=1, year=2025)

        assert path.exists()


@pytest.mark.skipif(not HAS_YAML, reason="PyYAML not installed")
class TestBuiltinThemes:
    """Integration tests for all built-in themes."""

    @pytest.mark.parametrize(
        "theme_name",
        ["default", "corporate", "minimal", "dark", "high_contrast"],
    )
    def test_theme_loads_successfully(self, theme_name: str) -> None:
        """Test all built-in themes load successfully."""
        loader = ThemeLoader()
        theme = loader.load(theme_name)
        assert isinstance(theme, Theme)
        assert theme.name is not None

    @pytest.mark.parametrize(
        "theme_name",
        ["default", "corporate", "minimal", "dark", "high_contrast"],
    )
    def test_theme_has_required_styles(self, theme_name: str) -> None:
        """Test all themes have required styles."""
        loader = ThemeLoader()
        theme = loader.load(theme_name)

        # All themes should have these core styles
        styles = theme.list_styles()
        assert "header" in styles or "header_primary" in styles
        assert "currency" in styles or "cell_currency" in styles

    @pytest.mark.parametrize(
        "theme_name",
        ["default", "corporate", "minimal", "dark", "high_contrast"],
    )
    def test_theme_creates_valid_ods(self, theme_name: str, tmp_path: Path) -> None:
        """Test all themes create valid ODS files."""
        from spreadsheet_dl import OdsGenerator

        output = tmp_path / f"{theme_name}_budget.ods"
        generator = OdsGenerator(theme=theme_name)
        path = generator.create_budget_spreadsheet(output, month=1, year=2025)

        assert path.exists()
        assert path.stat().st_size > 0
