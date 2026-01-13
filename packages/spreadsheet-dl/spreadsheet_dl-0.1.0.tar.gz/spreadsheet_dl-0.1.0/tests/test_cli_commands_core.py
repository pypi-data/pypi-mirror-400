"""Core CLI commands tests (generate, analyze, report, expense, import, export, backup).

This test suite uses mocks to cover all command paths without requiring
actual file I/O or external dependencies.
"""

from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from spreadsheet_dl._cli import commands
from spreadsheet_dl.exceptions import InvalidCategoryError, OperationCancelledError

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestCmdGenerate:
    """Tests for cmd_generate command."""

    def test_generate_cancelled_by_user(self, tmp_path: Path) -> None:
        """Test generate cancelled by user."""
        output_file = tmp_path / "budget.ods"
        output_file.write_text("existing")

        args = argparse.Namespace(
            output=output_file,
            template=None,
            month=1,
            year=2025,
            theme=None,
            yes=False,
            force=False,
        )

        with patch("spreadsheet_dl._cli.commands.confirm_overwrite") as mock_confirm:
            mock_confirm.return_value = False

            with pytest.raises(OperationCancelledError):
                commands.cmd_generate(args)

    def test_generate_standard_with_directory_output(self, tmp_path: Path) -> None:
        """Test standard generation to directory."""
        args = argparse.Namespace(
            output=tmp_path,
            template=None,
            month=3,
            year=2025,
            theme="minimal",
            yes=True,
            force=False,
        )

        with (
            patch(
                "spreadsheet_dl.domains.finance.ods_generator.create_monthly_budget"
            ) as mock_create,
            patch("spreadsheet_dl.domains.finance.ods_generator.OdsGenerator"),
        ):
            mock_create.return_value = tmp_path / "budget_2025_03.ods"

            result = commands.cmd_generate(args)

            assert result == 0

    def test_generate_standard_with_file_output(self, tmp_path: Path) -> None:
        """Test standard generation to specific file."""
        output_file = tmp_path / "my_budget.ods"
        args = argparse.Namespace(
            output=output_file,
            template=None,
            month=6,
            year=2025,
            theme="dark",
            yes=True,
            force=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.ods_generator.OdsGenerator"
        ) as mock_gen_cls:
            mock_gen = Mock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.create_budget_spreadsheet.return_value = output_file

            result = commands.cmd_generate(args)

            assert result == 0


class TestCmdAnalyze:
    """Tests for cmd_analyze command."""

    def test_analyze_file_not_found(self, tmp_path: Path) -> None:
        """Test analyze with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            category=None,
            start_date=None,
            end_date=None,
            json=False,
        )

        result = commands.cmd_analyze(args)

        assert result == 1

    def test_analyze_by_category(self, tmp_path: Path) -> None:
        """Test analyze filtered by category."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            category="Groceries",
            start_date=None,
            end_date=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer

            # Empty DataFrame
            import pandas as pd

            mock_analyzer.filter_by_category.return_value = pd.DataFrame()

            result = commands.cmd_analyze(args)

            assert result == 0

    def test_analyze_by_category_with_results(self, tmp_path: Path) -> None:
        """Test analyze by category with results."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            category="Groceries",
            start_date=None,
            end_date=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            import pandas as pd

            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer
            mock_analyzer.filter_by_category.return_value = pd.DataFrame(
                {"Amount": [10.0, 20.0, 30.0]}
            )

            result = commands.cmd_analyze(args)

            assert result == 0

    def test_analyze_by_date_range(self, tmp_path: Path) -> None:
        """Test analyze filtered by date range."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            category=None,
            start_date="2025-01-01",
            end_date="2025-01-31",
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            import pandas as pd

            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer
            mock_analyzer.filter_by_date_range.return_value = pd.DataFrame(
                {"Amount": [100.0, 200.0]}
            )

            result = commands.cmd_analyze(args)

            assert result == 0

    def test_analyze_json_output(self, tmp_path: Path) -> None:
        """Test analyze with JSON output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            category=None,
            start_date=None,
            end_date=None,
            json=True,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer
            mock_analyzer.to_dict.return_value = {"total": 100.0}

            result = commands.cmd_analyze(args)

            assert result == 0

    def test_analyze_text_output_with_summary(self, tmp_path: Path) -> None:
        """Test analyze with text summary output."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            category=None,
            start_date=None,
            end_date=None,
            json=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.budget_analyzer.BudgetAnalyzer"
        ) as mock_analyzer_cls:
            from spreadsheet_dl.domains.finance.budget_analyzer import BudgetSummary

            mock_analyzer = Mock()
            mock_analyzer_cls.return_value = mock_analyzer
            mock_analyzer.to_dict.return_value = {}
            mock_summary = BudgetSummary(
                total_budget=Decimal("1000.00"),
                total_spent=Decimal("750.00"),
                total_remaining=Decimal("250.00"),
                categories=[],
                top_categories=[],
                percent_used=75.0,
                alerts=["Warning: Over budget in Dining Out"],
            )
            mock_analyzer.get_summary.return_value = mock_summary

            result = commands.cmd_analyze(args)

            assert result == 0


class TestCmdReport:
    """Tests for cmd_report command."""

    def test_report_file_not_found(self, tmp_path: Path) -> None:
        """Test report with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            output=None,
            format="text",
        )

        result = commands.cmd_report(args)

        assert result == 1

    def test_report_save_to_file(self, tmp_path: Path) -> None:
        """Test report saved to file."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")
        output_file = tmp_path / "report.txt"

        args = argparse.Namespace(
            file=test_file,
            output=output_file,
            format="text",
        )

        with patch(
            "spreadsheet_dl.domains.finance.report_generator.ReportGenerator"
        ) as mock_gen_cls:
            mock_gen = Mock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.save_report.return_value = output_file

            result = commands.cmd_report(args)

            assert result == 0

    def test_report_text_format(self, tmp_path: Path) -> None:
        """Test report in text format."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output=None,
            format="text",
        )

        with patch(
            "spreadsheet_dl.domains.finance.report_generator.ReportGenerator"
        ) as mock_gen_cls:
            mock_gen = Mock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_text_report.return_value = "Text report"

            result = commands.cmd_report(args)

            assert result == 0

    def test_report_markdown_format(self, tmp_path: Path) -> None:
        """Test report in markdown format."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output=None,
            format="markdown",
        )

        with patch(
            "spreadsheet_dl.domains.finance.report_generator.ReportGenerator"
        ) as mock_gen_cls:
            mock_gen = Mock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_markdown_report.return_value = "# Markdown report"

            result = commands.cmd_report(args)

            assert result == 0

    def test_report_json_format(self, tmp_path: Path) -> None:
        """Test report in JSON format."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output=None,
            format="json",
        )

        with patch(
            "spreadsheet_dl.domains.finance.report_generator.ReportGenerator"
        ) as mock_gen_cls:
            mock_gen = Mock()
            mock_gen_cls.return_value = mock_gen
            mock_gen.generate_visualization_data.return_value = {"data": "json"}

            result = commands.cmd_report(args)

            assert result == 0


class TestCmdExpense:
    """Tests for cmd_expense command."""

    def test_expense_with_invalid_category(self, tmp_path: Path) -> None:
        """Test expense with invalid category."""
        args = argparse.Namespace(
            amount="25.00",
            description="Test",
            category="InvalidCategory",
            date=None,
            file=None,
            dry_run=False,
        )

        with pytest.raises(InvalidCategoryError):
            commands.cmd_expense(args)

    def test_expense_auto_categorize(self, tmp_path: Path) -> None:
        """Test expense with auto-categorization."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            amount="50.00",
            description="Kroger grocery shopping",
            category=None,
            date=None,
            file=test_file,
            dry_run=False,
        )

        with patch(
            "spreadsheet_dl.domains.finance.csv_import.TransactionCategorizer"
        ) as mock_cat_cls:
            from spreadsheet_dl.domains.finance.ods_generator import ExpenseCategory

            mock_cat = Mock()
            mock_cat_cls.return_value = mock_cat
            mock_cat.categorize.return_value = ExpenseCategory.GROCERIES

            with patch("spreadsheet_dl.ods_editor.OdsEditor") as mock_editor_cls:
                mock_editor = Mock()
                mock_editor_cls.return_value = mock_editor
                mock_editor.append_expense.return_value = 5

                result = commands.cmd_expense(args)

                assert result == 0

    def test_expense_dry_run(self, tmp_path: Path) -> None:
        """Test expense in dry-run mode."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            amount="100.00",
            description="Test expense",
            category="Groceries",
            date="2025-01-15",
            file=test_file,
            dry_run=True,
        )

        result = commands.cmd_expense(args)

        assert result == 0

    def test_expense_file_not_found(self, tmp_path: Path) -> None:
        """Test expense with non-existent file."""
        args = argparse.Namespace(
            amount="25.00",
            description="Test",
            category="Groceries",
            date=None,
            file=tmp_path / "nonexistent.ods",
            dry_run=False,
        )

        result = commands.cmd_expense(args)

        assert result == 1

    def test_expense_creates_new_file(self, tmp_path: Path) -> None:
        """Test expense creates new file when none exists."""
        args = argparse.Namespace(
            amount="75.00",
            description="Coffee",
            category="Dining Out",
            date=None,
            file=None,
            dry_run=False,
        )

        with patch("spreadsheet_dl._cli.commands.Path.cwd") as mock_cwd:
            mock_cwd.return_value = tmp_path

            with patch(
                "spreadsheet_dl.domains.finance.ods_generator.OdsGenerator"
            ) as mock_gen_cls:
                mock_gen = Mock()
                mock_gen_cls.return_value = mock_gen

                with patch("spreadsheet_dl.ods_editor.OdsEditor") as mock_editor_cls:
                    mock_editor = Mock()
                    mock_editor_cls.return_value = mock_editor
                    mock_editor.append_expense.return_value = 1

                    result = commands.cmd_expense(args)

                    assert result == 0

    def test_expense_error_handling(self, tmp_path: Path) -> None:
        """Test expense error handling."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            amount="50.00",
            description="Test",
            category="Groceries",
            date=None,
            file=test_file,
            dry_run=False,
        )

        with patch("spreadsheet_dl.ods_editor.OdsEditor") as mock_editor_cls:
            mock_editor_cls.side_effect = ValueError("Test error")

            result = commands.cmd_expense(args)

            assert result == 1


class TestCmdImport:
    """Tests for cmd_import command."""

    def test_import_file_not_found(self, tmp_path: Path) -> None:
        """Test import with non-existent CSV."""
        args = argparse.Namespace(
            csv_file=tmp_path / "nonexistent.csv",
            bank="auto",
            output=None,
            preview=False,
            yes=False,
            force=False,
            theme=None,
        )

        result = commands.cmd_import(args)

        assert result == 1

    def test_import_auto_detect(self, tmp_path: Path) -> None:
        """Test import with auto-detect bank format."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")

        args = argparse.Namespace(
            csv_file=csv_file,
            bank="auto",
            output=None,
            preview=False,
            yes=True,
            force=False,
            theme=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.bank_formats.BankFormatRegistry"
        ) as mock_registry_cls:
            mock_registry = Mock()
            mock_registry_cls.return_value = mock_registry
            mock_fmt = Mock()
            mock_fmt.id = "chase_checking"
            mock_registry.detect_format.return_value = mock_fmt

            with patch(
                "spreadsheet_dl.domains.finance.csv_import.import_bank_csv"
            ) as mock_import:
                mock_import.return_value = []

                result = commands.cmd_import(args)

                assert result == 0

    def test_import_no_expenses(self, tmp_path: Path) -> None:
        """Test import with no expenses found."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")

        args = argparse.Namespace(
            csv_file=csv_file,
            bank="chase",
            output=None,
            preview=False,
            yes=False,
            force=False,
            theme=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.csv_import.import_bank_csv"
        ) as mock_import:
            mock_import.return_value = []

            result = commands.cmd_import(args)

            assert result == 0

    def test_import_preview_mode(self, tmp_path: Path) -> None:
        """Test import in preview mode."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")

        args = argparse.Namespace(
            csv_file=csv_file,
            bank="chase",
            output=None,
            preview=True,
            yes=False,
            force=False,
            theme=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.csv_import.import_bank_csv"
        ) as mock_import:
            from spreadsheet_dl.domains.finance.ods_generator import (
                ExpenseCategory,
                ExpenseEntry,
            )

            entries = [
                ExpenseEntry(
                    date=date(2025, 1, 1),
                    category=ExpenseCategory.GROCERIES,
                    description="Store",
                    amount=Decimal("50.00"),
                )
                for _ in range(15)
            ]
            mock_import.return_value = entries

            result = commands.cmd_import(args)

            assert result == 0

    def test_import_create_ods(self, tmp_path: Path) -> None:
        """Test import creates ODS file."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")
        output_file = tmp_path / "imported.ods"

        args = argparse.Namespace(
            csv_file=csv_file,
            bank="chase",
            output=output_file,
            preview=False,
            yes=True,
            force=False,
            theme="minimal",
        )

        with patch(
            "spreadsheet_dl.domains.finance.csv_import.import_bank_csv"
        ) as mock_import:
            from spreadsheet_dl.domains.finance.ods_generator import (
                ExpenseCategory,
                ExpenseEntry,
            )

            entries = [
                ExpenseEntry(
                    date=date(2025, 1, 1),
                    category=ExpenseCategory.GROCERIES,
                    description="Store",
                    amount=Decimal("50.00"),
                )
            ]
            mock_import.return_value = entries

            with patch(
                "spreadsheet_dl.domains.finance.ods_generator.OdsGenerator"
            ) as mock_gen_cls:
                mock_gen = Mock()
                mock_gen_cls.return_value = mock_gen

                result = commands.cmd_import(args)

                assert result == 0

    def test_import_cancelled(self, tmp_path: Path) -> None:
        """Test import cancelled by user."""
        csv_file = tmp_path / "transactions.csv"
        csv_file.write_text("dummy")
        output_file = tmp_path / "imported.ods"
        output_file.write_text("existing")

        args = argparse.Namespace(
            csv_file=csv_file,
            bank="chase",
            output=output_file,
            preview=False,
            yes=False,
            force=False,
            theme=None,
        )

        with patch(
            "spreadsheet_dl.domains.finance.csv_import.import_bank_csv"
        ) as mock_import:
            from spreadsheet_dl.domains.finance.ods_generator import (
                ExpenseCategory,
                ExpenseEntry,
            )

            entries = [
                ExpenseEntry(
                    date=date(2025, 1, 1),
                    category=ExpenseCategory.GROCERIES,
                    description="Store",
                    amount=Decimal("50.00"),
                )
            ]
            mock_import.return_value = entries

            with patch(
                "spreadsheet_dl._cli.commands.confirm_overwrite"
            ) as mock_confirm:
                mock_confirm.return_value = False

                with pytest.raises(OperationCancelledError):
                    commands.cmd_import(args)


class TestCmdExport:
    """Tests for cmd_export command."""

    def test_export_file_not_found(self, tmp_path: Path) -> None:
        """Test export with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            output=None,
            format="xlsx",
            yes=False,
            force=False,
        )

        result = commands.cmd_export(args)

        assert result == 1

    def test_export_to_xlsx(self, tmp_path: Path) -> None:
        """Test export to XLSX format."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output=None,
            format="xlsx",
            yes=True,
            force=False,
        )

        with patch("spreadsheet_dl.export.MultiFormatExporter") as mock_exp_cls:
            mock_exp = Mock()
            mock_exp_cls.return_value = mock_exp
            mock_exp.export.return_value = tmp_path / "budget.xlsx"

            result = commands.cmd_export(args)

            assert result == 0

    def test_export_cancelled(self, tmp_path: Path) -> None:
        """Test export cancelled by user."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")
        output_file = tmp_path / "budget.xlsx"
        output_file.write_text("existing")

        args = argparse.Namespace(
            file=test_file,
            output=output_file,
            format="xlsx",
            yes=False,
            force=False,
        )

        with patch("spreadsheet_dl._cli.commands.confirm_overwrite") as mock_confirm:
            mock_confirm.return_value = False

            with pytest.raises(OperationCancelledError):
                commands.cmd_export(args)


class TestCmdExportDual:
    """Tests for cmd_export_dual command."""

    def test_export_dual_file_not_found(self, tmp_path: Path) -> None:
        """Test dual export with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            output_dir=None,
        )

        result = commands.cmd_export_dual(args)

        assert result == 1

    def test_export_dual_success(self, tmp_path: Path) -> None:
        """Test dual export success."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            output_dir=tmp_path,
        )

        with patch("spreadsheet_dl.ai_export.AIExporter") as mock_exp_cls:
            mock_exp = Mock()
            mock_exp_cls.return_value = mock_exp
            ods_path = tmp_path / "budget.ods"
            json_path = tmp_path / "budget.json"
            mock_exp.export_dual.return_value = (ods_path, json_path)

            result = commands.cmd_export_dual(args)

            assert result == 0


class TestCmdBackup:
    """Tests for cmd_backup command."""

    def test_backup_list(self, tmp_path: Path) -> None:
        """Test backup list command."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            list=True,
            cleanup=False,
            restore=None,
            days=30,
            yes=False,
            force=False,
            dry_run=False,
        )

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.list_backups.return_value = []

            result = commands.cmd_backup(args)

            assert result == 0

    def test_backup_list_with_backups(self, tmp_path: Path) -> None:
        """Test backup list with existing backups."""
        from datetime import datetime

        from spreadsheet_dl.backup import BackupInfo, BackupMetadata, BackupReason

        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        backup_path = tmp_path / "backup.ods"
        backup_path.write_text("backup")

        args = argparse.Namespace(
            file=test_file,
            list=True,
            cleanup=False,
            restore=None,
            days=30,
            yes=False,
            force=False,
            dry_run=False,
        )

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            metadata = BackupMetadata(
                original_path=str(test_file),
                backup_time=datetime.now().isoformat(),
                content_hash="abc123",
                reason=BackupReason.MANUAL.value,
            )
            backup_info = BackupInfo(
                backup_path=backup_path,
                metadata_path=backup_path.with_suffix(".json"),
                metadata=metadata,
                created=datetime.now(),
            )
            mock_mgr.list_backups.return_value = [backup_info]

            result = commands.cmd_backup(args)

            assert result == 0

    def test_backup_cleanup(self, tmp_path: Path) -> None:
        """Test backup cleanup command."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            list=False,
            cleanup=True,
            restore=None,
            days=30,
            yes=True,
            force=False,
            dry_run=False,
        )

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.cleanup_old_backups.return_value = [Path("backup1.ods")]

            result = commands.cmd_backup(args)

            assert result == 0

    def test_backup_cleanup_dry_run(self, tmp_path: Path) -> None:
        """Test backup cleanup in dry-run mode."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            list=False,
            cleanup=True,
            restore=None,
            days=30,
            yes=True,
            force=False,
            dry_run=True,
        )

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.cleanup_old_backups.return_value = [Path("backup1.ods")]

            result = commands.cmd_backup(args)

            assert result == 0

    def test_backup_restore(self, tmp_path: Path) -> None:
        """Test backup restore command."""
        test_file = tmp_path / "budget.ods"
        test_file.write_text("current")
        backup_file = tmp_path / "backup.ods"
        backup_file.write_text("backup")

        args = argparse.Namespace(
            file=test_file,
            list=False,
            cleanup=False,
            restore=backup_file,
            days=30,
            yes=True,
            force=False,
            dry_run=False,
        )

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr
            mock_mgr.restore_backup.return_value = test_file

            result = commands.cmd_backup(args)

            assert result == 0

    def test_backup_restore_file_not_found(self, tmp_path: Path) -> None:
        """Test backup restore with non-existent backup."""
        test_file = tmp_path / "budget.ods"

        args = argparse.Namespace(
            file=test_file,
            list=False,
            cleanup=False,
            restore=tmp_path / "nonexistent.ods",
            days=30,
            yes=False,
            force=False,
            dry_run=False,
        )

        result = commands.cmd_backup(args)

        assert result == 1

    def test_backup_create(self, tmp_path: Path) -> None:
        """Test backup creation."""
        from datetime import datetime

        from spreadsheet_dl.backup import BackupInfo, BackupMetadata, BackupReason

        test_file = tmp_path / "budget.ods"
        test_file.write_text("dummy")

        args = argparse.Namespace(
            file=test_file,
            list=False,
            cleanup=False,
            restore=None,
            days=30,
            yes=False,
            force=False,
            dry_run=False,
        )

        with patch("spreadsheet_dl.backup.BackupManager") as mock_mgr_cls:
            mock_mgr = Mock()
            mock_mgr_cls.return_value = mock_mgr

            metadata = BackupMetadata(
                original_path=str(test_file),
                backup_time=datetime.now().isoformat(),
                content_hash="abc123def456",
                reason=BackupReason.MANUAL.value,
            )
            backup_info = BackupInfo(
                backup_path=tmp_path / "backup.ods",
                metadata_path=tmp_path / "backup.json",
                metadata=metadata,
                created=datetime.now(),
            )
            mock_mgr.create_backup.return_value = backup_info

            result = commands.cmd_backup(args)

            assert result == 0

    def test_backup_create_file_not_found(self, tmp_path: Path) -> None:
        """Test backup creation with non-existent file."""
        args = argparse.Namespace(
            file=tmp_path / "nonexistent.ods",
            list=False,
            cleanup=False,
            restore=None,
            days=30,
            yes=False,
            force=False,
            dry_run=False,
        )

        result = commands.cmd_backup(args)

        assert result == 1
