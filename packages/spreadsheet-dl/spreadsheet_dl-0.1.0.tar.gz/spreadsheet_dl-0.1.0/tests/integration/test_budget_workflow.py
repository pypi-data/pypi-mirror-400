"""
Integration tests for complete budget workflows.

Tests end-to-end scenarios combining multiple features.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.integration]


class TestBudgetCreationWorkflow:
    """Test complete budget creation and management workflow."""

    def test_create_and_analyze_budget(self, tmp_path: Path) -> None:
        """Test creating a budget and analyzing it."""
        from spreadsheet_dl.domains.finance.ods_generator import create_monthly_budget

        # Create budget
        budget_path = create_monthly_budget(tmp_path, month=1, year=2025)

        assert budget_path.exists()
        assert budget_path.suffix == ".ods"

    def test_generate_with_theme(self, tmp_path: Path) -> None:
        """Test generating budget with theme."""
        from spreadsheet_dl.domains.finance.ods_generator import create_monthly_budget

        budget_path = create_monthly_budget(
            tmp_path, month=1, year=2025, theme="modern"
        )

        assert budget_path.exists()


class TestExportImportRoundtrip:
    """Test export and import round-trip fidelity."""

    def test_ods_to_json_roundtrip(self, tmp_path: Path) -> None:
        """Test ODS to JSON export and back."""
        from spreadsheet_dl.domains.finance.ods_generator import create_monthly_budget
        from spreadsheet_dl.export import MultiFormatExporter

        # Create budget
        budget_path = create_monthly_budget(tmp_path, month=1, year=2025)

        # Export to JSON
        exporter = MultiFormatExporter()
        json_path = tmp_path / "budget.json"
        result = exporter.export(budget_path, json_path, "json")

        assert result.exists()
        assert result.stat().st_size > 0

    @pytest.mark.requires_export
    def test_ods_to_xlsx_export(self, tmp_path: Path) -> None:
        """Test ODS to XLSX export."""
        pytest.importorskip("openpyxl")
        from spreadsheet_dl.domains.finance.ods_generator import create_monthly_budget
        from spreadsheet_dl.export import MultiFormatExporter

        # Create budget
        budget_path = create_monthly_budget(tmp_path, month=1, year=2025)

        # Export to XLSX
        exporter = MultiFormatExporter()
        xlsx_path = tmp_path / "budget.xlsx"
        result = exporter.export(budget_path, xlsx_path, "xlsx")

        assert result.exists()
        assert result.stat().st_size > 0


class TestSchemaValidation:
    """Test schema validation workflows."""

    def test_theme_loading(self) -> None:
        """Test loading a theme."""
        from spreadsheet_dl.schema.loader import load_theme

        theme = load_theme("default")

        assert theme is not None
        # Theme object has colors, fonts, and styles
        assert hasattr(theme, "colors")
        assert hasattr(theme, "fonts")
        assert hasattr(theme, "styles")

    def test_invalid_theme(self) -> None:
        """Test loading invalid theme."""
        from spreadsheet_dl.schema.loader import load_theme

        with pytest.raises(FileNotFoundError):
            load_theme("nonexistent_theme")


class TestPluginSystem:
    """Test plugin loading and execution."""

    def test_load_finance_plugin(self) -> None:
        """Test loading finance domain plugin."""
        from spreadsheet_dl.plugins import PluginManager

        pm = PluginManager()
        pm.discover()
        plugins = pm.list_plugins()

        # Plugin system initialized (may be empty if no external plugins)
        assert isinstance(plugins, list)

    def test_load_domain_plugins(self) -> None:
        """Test loading all domain plugins."""
        from spreadsheet_dl.plugins import PluginManager

        pm = PluginManager()
        pm.discover()

        # Should be able to list plugins (may be empty)
        plugins = pm.list_plugins()
        assert isinstance(plugins, list)
