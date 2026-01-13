"""Tests for CLI theme support."""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    pass


pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCliThemeCommand:
    """Tests for CLI themes command."""

    def test_themes_command(self) -> None:
        """Test themes command lists themes."""
        result = subprocess.run(
            [sys.executable, "-m", "spreadsheet_dl.cli", "themes"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Available Visual Themes" in result.stdout
        assert "default" in result.stdout
        assert "corporate" in result.stdout
        assert "minimal" in result.stdout

    def test_themes_command_json(self) -> None:
        """Test themes command with JSON output."""
        result = subprocess.run(
            [sys.executable, "-m", "spreadsheet_dl.cli", "themes", "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert '"name": "default"' in result.stdout


class TestCliGenerateWithTheme:
    """Tests for generate command with theme flag."""

    def test_generate_with_default_theme(self, tmp_path: Path) -> None:
        """Test generate with default theme."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "spreadsheet_dl.cli",
                "generate",
                "-o",
                str(tmp_path),
                "--theme",
                "default",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Using theme: default" in result.stdout
        assert "Created:" in result.stdout

        # Verify file was created
        ods_files = list(tmp_path.glob("*.ods"))
        assert len(ods_files) == 1

    def test_generate_with_corporate_theme(self, tmp_path: Path) -> None:
        """Test generate with corporate theme."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "spreadsheet_dl.cli",
                "generate",
                "-o",
                str(tmp_path),
                "--theme",
                "corporate",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Using theme: corporate" in result.stdout

    def test_generate_without_theme(self, tmp_path: Path) -> None:
        """Test generate without theme uses legacy styles."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "spreadsheet_dl.cli",
                "generate",
                "-o",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Using theme:" not in result.stdout  # No theme message
        assert "Created:" in result.stdout


class TestCliVersionOutput:
    """Tests for CLI version output."""

    def test_version_shows_current(self) -> None:
        """Test version command shows current version (0.1.0)."""
        result = subprocess.run(
            [sys.executable, "-m", "spreadsheet_dl.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout


class TestCliHelpText:
    """Tests for CLI help text."""

    def test_help_includes_theme_option(self) -> None:
        """Test help includes --theme option."""
        result = subprocess.run(
            [sys.executable, "-m", "spreadsheet_dl.cli", "generate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--theme" in result.stdout

    def test_help_includes_themes_command(self) -> None:
        """Test main help includes themes command."""
        result = subprocess.run(
            [sys.executable, "-m", "spreadsheet_dl.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "themes" in result.stdout

    def test_examples_include_theme(self) -> None:
        """Test examples include theme usage."""
        result = subprocess.run(
            [sys.executable, "-m", "spreadsheet_dl.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--theme corporate" in result.stdout
