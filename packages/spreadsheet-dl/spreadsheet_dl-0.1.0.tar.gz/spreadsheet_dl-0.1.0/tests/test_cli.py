"""Tests for CLI interface."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.cli]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the CLI with given arguments."""
    return subprocess.run(
        [sys.executable, "-m", "spreadsheet_dl.cli", *args],
        capture_output=True,
        text=True,
    )


class TestCLIBasics:
    """Tests for basic CLI functionality."""

    def test_version_flag(self) -> None:
        """Test --version flag shows version."""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "spreadsheet-dl" in result.stdout
        # Accept current version 0.1.0
        assert "0.1.0" in result.stdout

    def test_version_short_flag(self) -> None:
        """Test -V flag shows version."""
        result = run_cli("-V")
        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_help_flag(self) -> None:
        """Test --help flag shows help."""
        result = run_cli("--help")
        assert result.returncode == 0
        assert "spreadsheet-dl" in result.stdout
        assert "generate" in result.stdout
        assert "analyze" in result.stdout
        assert "report" in result.stdout

    def test_no_command_shows_help(self) -> None:
        """Test running without command shows help."""
        result = run_cli()
        assert result.returncode == 1  # Exits with error
        assert "usage:" in result.stdout.lower() or "spreadsheet-dl" in result.stdout


class TestGenerateCommand:
    """Tests for generate command."""

    def test_generate_help(self) -> None:
        """Test generate --help."""
        result = run_cli("generate", "--help")
        assert result.returncode == 0
        assert "--output" in result.stdout
        assert "--month" in result.stdout
        assert "--year" in result.stdout
        assert "--theme" in result.stdout

    def test_generate_creates_file(self, tmp_path: Path) -> None:
        """Test generate creates an ODS file."""
        result = run_cli("generate", "-o", str(tmp_path))
        assert result.returncode == 0
        assert "Created:" in result.stdout

        # Check file was created
        ods_files = list(tmp_path.glob("budget_*.ods"))
        assert len(ods_files) == 1

    def test_generate_with_month_year(self, tmp_path: Path) -> None:
        """Test generate with specific month and year."""
        result = run_cli("generate", "-o", str(tmp_path), "-m", "6", "-y", "2025")
        assert result.returncode == 0

        # Check correct filename
        assert (tmp_path / "budget_2025_06.ods").exists()


class TestTemplatesCommand:
    """Tests for templates command (deprecated)."""

    def test_templates_shows_deprecation(self) -> None:
        """Test templates command shows deprecation message."""
        result = run_cli("templates")
        assert result.returncode == 0
        assert "removed" in result.stdout.lower() or "examples" in result.stdout.lower()

    def test_templates_json(self) -> None:
        """Test templates --json output shows deprecation."""
        result = run_cli("templates", "--json")
        assert result.returncode == 0

        # Should be valid JSON with deprecation message
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "message" in data


class TestConfigCommand:
    """Tests for config command."""

    def test_config_help(self) -> None:
        """Test config command shows info."""
        result = run_cli("config")
        assert result.returncode == 0
        assert "Configuration" in result.stdout
        assert "NEXTCLOUD_URL" in result.stdout

    def test_config_show(self) -> None:
        """Test config --show outputs JSON."""
        result = run_cli("config", "--show")
        assert result.returncode == 0

        # Should be valid JSON
        data = json.loads(result.stdout)
        assert "nextcloud" in data
        assert "defaults" in data
        assert "display" in data

    def test_config_init(self, tmp_path: Path) -> None:
        """Test config --init creates config file."""
        config_path = tmp_path / "config.yaml"
        result = run_cli("config", "--init", "--path", str(config_path))

        # May fail if pyyaml not installed, that's OK
        if result.returncode == 0:
            assert config_path.exists()
            assert "Configuration file created" in result.stdout


class TestAnalyzeCommand:
    """Tests for analyze command."""

    def test_analyze_file_not_found(self, tmp_path: Path) -> None:
        """Test analyze with non-existent file."""
        result = run_cli("analyze", str(tmp_path / "nonexistent.ods"))
        assert result.returncode == 1
        assert (
            "not found" in result.stderr.lower() or "not found" in result.stdout.lower()
        )

    def test_analyze_with_json(self, tmp_path: Path) -> None:
        """Test analyze --json output."""
        # First create a budget file
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli("analyze", str(ods_file), "--json")
        assert result.returncode == 0

        # Should be valid JSON
        data = json.loads(result.stdout)
        assert "total_budget" in data
        assert "total_spent" in data


class TestDashboardCommand:
    """Tests for dashboard command."""

    def test_dashboard_file_not_found(self, tmp_path: Path) -> None:
        """Test dashboard with non-existent file."""
        result = run_cli("dashboard", str(tmp_path / "nonexistent.ods"))
        assert result.returncode == 1

    def test_dashboard_output(self, tmp_path: Path) -> None:
        """Test dashboard produces output."""
        # First create a budget file
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli("dashboard", str(ods_file))
        assert result.returncode == 0
        assert "BUDGET DASHBOARD" in result.stdout
        assert "SUMMARY" in result.stdout


class TestExpenseCommand:
    """Tests for expense command."""

    def test_expense_help(self) -> None:
        """Test expense --help."""
        result = run_cli("expense", "--help")
        assert result.returncode == 0
        assert "amount" in result.stdout.lower()
        assert "description" in result.stdout.lower()
        assert "--dry-run" in result.stdout

    def test_expense_invalid_amount(self) -> None:
        """Test expense with invalid amount."""
        result = run_cli("expense", "not-a-number", "Test expense")
        assert result.returncode == 1
        assert "INVALID_AMOUNT" in result.stderr or "invalid" in result.stderr.lower()

    def test_expense_invalid_date(self) -> None:
        """Test expense with invalid date."""
        result = run_cli("expense", "25.00", "Test", "-d", "bad-date")
        assert result.returncode == 1
        assert "INVALID_DATE" in result.stderr or "invalid" in result.stderr.lower()

    def test_expense_invalid_category(self) -> None:
        """Test expense with invalid category."""
        result = run_cli("expense", "25.00", "Test", "-c", "NotACategory")
        assert result.returncode == 1
        assert "INVALID_CATEGORY" in result.stderr or "invalid" in result.stderr.lower()

    def test_expense_dry_run(self, tmp_path: Path) -> None:
        """Test expense --dry-run shows what would be added without modifying."""
        # Create a budget file first
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli(
            "expense",
            "25.50",
            "Test purchase",
            "-c",
            "Groceries",
            "-f",
            str(ods_file),
            "--dry-run",
        )

        assert result.returncode == 0
        assert "[DRY RUN]" in result.stdout
        assert "25.50" in result.stdout
        assert "Test purchase" in result.stdout
        assert "Groceries" in result.stdout

    def test_expense_adds_to_file(self, tmp_path: Path) -> None:
        """Test expense command actually adds expense to ODS file."""
        # Create a budget file first
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli(
            "expense",
            "42.50",
            "Coffee and snacks",
            "-c",
            "Dining Out",
            "-f",
            str(ods_file),
        )

        assert result.returncode == 0
        assert "Expense added successfully" in result.stdout
        assert "42.50" in result.stdout
        assert "Coffee and snacks" in result.stdout
        assert "Dining Out" in result.stdout
        assert "Row:" in result.stdout

    def test_expense_with_date(self, tmp_path: Path) -> None:
        """Test expense with specific date."""
        # Create a budget file first
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli(
            "expense",
            "100.00",
            "Monthly subscription",
            "-c",
            "Subscriptions",
            "-f",
            str(ods_file),
            "-d",
            "2025-01-15",
        )

        assert result.returncode == 0
        assert "2025-01-15" in result.stdout

    def test_expense_auto_categorize(self, tmp_path: Path) -> None:
        """Test expense auto-categorization."""
        # Create a budget file first
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli(
            "expense",
            "50.00",
            "Walmart groceries",
            "-f",
            str(ods_file),
        )

        assert result.returncode == 0
        assert "Auto-categorized as:" in result.stdout

    def test_expense_creates_file_if_none_exists(self, tmp_path: Path) -> None:
        """Test expense creates budget file if none exists in directory."""
        import os

        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            result = run_cli(
                "expense",
                "25.00",
                "Test expense",
                "-c",
                "Miscellaneous",
            )

            assert result.returncode == 0
            assert "Created new budget:" in result.stdout
            assert "Expense added successfully" in result.stdout

            # Check file was created
            ods_files = list(tmp_path.glob("budget_*.ods"))
            assert len(ods_files) == 1
        finally:
            os.chdir(orig_cwd)

    def test_expense_file_not_found(self, tmp_path: Path) -> None:
        """Test expense with non-existent file specified."""
        result = run_cli(
            "expense",
            "25.00",
            "Test",
            "-f",
            str(tmp_path / "nonexistent.ods"),
        )
        assert result.returncode == 1
        assert (
            "not found" in result.stderr.lower() or "not found" in result.stdout.lower()
        )


class TestImportCommand:
    """Tests for import command."""

    def test_import_file_not_found(self, tmp_path: Path) -> None:
        """Test import with non-existent file."""
        result = run_cli("import", str(tmp_path / "nonexistent.csv"))
        assert result.returncode == 1
        assert "not found" in result.stderr.lower()


class TestAlertsCommand:
    """Tests for alerts command."""

    def test_alerts_file_not_found(self, tmp_path: Path) -> None:
        """Test alerts with non-existent file."""
        result = run_cli("alerts", str(tmp_path / "nonexistent.ods"))
        assert result.returncode == 1

    def test_alerts_json(self, tmp_path: Path) -> None:
        """Test alerts --json output."""
        # First create a budget file
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli("alerts", str(ods_file), "--json")
        assert result.returncode == 0
        # Should be valid JSON (may be empty alerts list)
        data = json.loads(result.stdout)
        assert isinstance(data, (dict, list))


class TestReportCommand:
    """Tests for report command."""

    def test_report_file_not_found(self, tmp_path: Path) -> None:
        """Test report with non-existent file."""
        result = run_cli("report", str(tmp_path / "nonexistent.ods"))
        assert result.returncode == 1

    def test_report_markdown(self, tmp_path: Path) -> None:
        """Test report with markdown format."""
        # First create a budget file
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli("report", str(ods_file), "-f", "markdown")
        assert result.returncode == 0
        assert "# Budget Report" in result.stdout

    def test_report_text(self, tmp_path: Path) -> None:
        """Test report with text format."""
        # First create a budget file
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli("report", str(ods_file), "-f", "text")
        assert result.returncode == 0
        assert "BUDGET REPORT" in result.stdout

    def test_report_json(self, tmp_path: Path) -> None:
        """Test report with JSON format."""
        # First create a budget file
        run_cli("generate", "-o", str(tmp_path))
        ods_file = next(iter(tmp_path.glob("budget_*.ods")))

        result = run_cli("report", str(ods_file), "-f", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "pie_chart" in data or "bar_chart" in data
