"""
Tests for AI export module.

Tests the AIExporter class and related functionality for
creating AI-friendly JSON exports from ODS files.
"""

from __future__ import annotations

import json
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from spreadsheet_dl.ai_export import (
    AIExporter,
    AIExportMetadata,
    ConsistencyError,
    DualExportError,
    ExportError,
    SemanticCell,
    SemanticCellType,
    SemanticSheet,
    export_dual,
    export_for_ai,
)
from spreadsheet_dl.exceptions import FileError

# Check if odfpy is available
try:
    import odf  # noqa: F401

    HAS_ODFPY = True
except ImportError:
    HAS_ODFPY = False

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_ods(temp_dir: Path) -> Path:
    """Create a sample ODS file for testing."""
    # Create a minimal ODS file using odfpy
    try:
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

        doc = OpenDocumentSpreadsheet()

        # Create a budget sheet
        table = Table(name="Budget")

        # Header row
        header_row = TableRow()
        for header in ["Category", "Budget", "Spent", "Remaining"]:
            cell = TableCell()
            cell.addElement(P(text=header))
            header_row.addElement(cell)
        table.addElement(header_row)

        # Data rows
        data = [
            ("Housing", 1500.00, 1450.00, 50.00),
            ("Food", 500.00, 520.00, -20.00),
            ("Transport", 300.00, 250.00, 50.00),
        ]

        for cat, budget, spent, remaining in data:
            row = TableRow()

            # Category cell
            cat_cell = TableCell()
            cat_cell.addElement(P(text=cat))
            row.addElement(cat_cell)

            # Budget cell
            budget_cell = TableCell(valuetype="currency", value=str(budget))
            budget_cell.addElement(P(text=f"${budget:.2f}"))
            row.addElement(budget_cell)

            # Spent cell
            spent_cell = TableCell(valuetype="currency", value=str(spent))
            spent_cell.addElement(P(text=f"${spent:.2f}"))
            row.addElement(spent_cell)

            # Remaining cell
            remaining_cell = TableCell(valuetype="currency", value=str(remaining))
            remaining_cell.addElement(P(text=f"${remaining:.2f}"))
            row.addElement(remaining_cell)

            table.addElement(row)

        doc.spreadsheet.addElement(table)

        ods_path = temp_dir / "sample_budget.ods"
        doc.save(str(ods_path))

        return ods_path

    except ImportError:
        pytest.skip("odfpy not installed")


class TestSemanticCellType:
    """Tests for SemanticCellType enum."""

    def test_all_types_have_values(self) -> None:
        """Test all semantic types have string values."""
        for cell_type in SemanticCellType:
            assert isinstance(cell_type.value, str)
            assert len(cell_type.value) > 0

    def test_financial_types_exist(self) -> None:
        """Test that all financial semantic types exist."""
        financial_types = [
            SemanticCellType.BUDGET_AMOUNT,
            SemanticCellType.EXPENSE_AMOUNT,
            SemanticCellType.INCOME_AMOUNT,
            SemanticCellType.BALANCE,
            SemanticCellType.TOTAL,
            SemanticCellType.VARIANCE,
        ]
        for t in financial_types:
            assert t is not None


class TestSemanticCell:
    """Tests for SemanticCell class."""

    def test_to_dict_basic(self) -> None:
        """Test basic serialization."""
        cell = SemanticCell(
            row=1,
            column=1,
            column_letter="A",
            value="Test",
            display_value="Test",
            semantic_type=SemanticCellType.TEXT,
        )

        result = cell.to_dict()

        assert result["ref"] == "A1"
        assert result["value"] == "Test"
        assert result["display"] == "Test"
        assert result["type"] == "text"

    def test_to_dict_with_formula(self) -> None:
        """Test serialization with formula."""
        cell = SemanticCell(
            row=5,
            column=2,
            column_letter="B",
            value=Decimal("100.50"),
            display_value="$100.50",
            semantic_type=SemanticCellType.SUM_FORMULA,
            formula="=SUM(B2:B4)",
            formula_description="Calculates the total of B2 to B4",
        )

        result = cell.to_dict()

        assert result["formula"] == "=SUM(B2:B4)"
        assert result["formula_meaning"] == "Calculates the total of B2 to B4"

    def test_to_dict_decimal_serialization(self) -> None:
        """Test that Decimal values are serialized as float."""
        cell = SemanticCell(
            row=1,
            column=1,
            column_letter="A",
            value=Decimal("123.45"),
            display_value="$123.45",
            semantic_type=SemanticCellType.CURRENCY,
        )

        result = cell.to_dict()
        assert result["value"] == 123.45
        assert isinstance(result["value"], float)

    def test_to_dict_date_serialization(self) -> None:
        """Test that date values are serialized as ISO string."""
        cell = SemanticCell(
            row=1,
            column=1,
            column_letter="A",
            value=date(2024, 12, 28),
            display_value="2024-12-28",
            semantic_type=SemanticCellType.DATE,
        )

        result = cell.to_dict()
        assert result["value"] == "2024-12-28"


class TestSemanticSheet:
    """Tests for SemanticSheet class."""

    def test_to_dict(self) -> None:
        """Test sheet serialization."""
        sheet = SemanticSheet(
            name="Budget",
            purpose="Monthly budget tracking",
            rows=10,
            columns=5,
        )

        result = sheet.to_dict()

        assert result["name"] == "Budget"
        assert result["purpose"] == "Monthly budget tracking"
        assert result["dimensions"]["rows"] == 10
        assert result["dimensions"]["columns"] == 5


class TestAIExportMetadata:
    """Tests for AIExportMetadata class."""

    def test_to_dict(self) -> None:
        """Test metadata serialization."""
        metadata = AIExportMetadata(
            source_file="/path/to/budget.ods",
            business_context={"domain": "personal_finance"},
        )

        result = metadata.to_dict()

        assert result["source_file"] == "/path/to/budget.ods"
        assert result["format"] == "spreadsheet-dl-ai-export"
        assert result["business_context"]["domain"] == "personal_finance"
        assert "export_time" in result


class TestAIExporter:
    """Tests for AIExporter class."""

    def test_init_defaults(self) -> None:
        """Test default initialization."""
        exporter = AIExporter()

        assert exporter.include_empty_cells is False
        assert exporter.include_formulas is True
        assert exporter.include_context is True

    def test_init_custom(self) -> None:
        """Test custom initialization."""
        exporter = AIExporter(
            include_empty_cells=True,
            include_formulas=False,
            include_context=False,
        )

        assert exporter.include_empty_cells is True
        assert exporter.include_formulas is False
        assert exporter.include_context is False

    def test_get_column_letter(self) -> None:
        """Test column number to letter conversion."""
        exporter = AIExporter()

        assert exporter._get_column_letter(1) == "A"
        assert exporter._get_column_letter(2) == "B"
        assert exporter._get_column_letter(26) == "Z"
        assert exporter._get_column_letter(27) == "AA"
        assert exporter._get_column_letter(28) == "AB"

    def test_infer_sheet_purpose(self) -> None:
        """Test sheet purpose inference."""
        exporter = AIExporter()

        assert "budget" in exporter._infer_sheet_purpose("Monthly Budget").lower()
        assert "expense" in exporter._infer_sheet_purpose("Expenses").lower()
        assert "income" in exporter._infer_sheet_purpose("Income Sources").lower()

    def test_describe_formula_sum(self) -> None:
        """Test formula description for SUM."""
        exporter = AIExporter()

        desc = exporter._describe_formula("=SUM([.B2:.B10])")
        assert "total" in desc.lower() or "sum" in desc.lower()

    def test_describe_formula_average(self) -> None:
        """Test formula description for AVERAGE."""
        exporter = AIExporter()

        desc = exporter._describe_formula("=AVERAGE([.C2:.C5])")
        assert "average" in desc.lower()

    def test_export_to_json_file_not_found(self, temp_dir: Path) -> None:
        """Test export with non-existent file."""
        exporter = AIExporter()

        with pytest.raises(FileError):
            exporter.export_to_json(temp_dir / "nonexistent.ods")

    @pytest.mark.skipif(
        not HAS_ODFPY,
        reason="odfpy required for full ODS testing",
    )
    def test_export_to_json_with_file(self, sample_ods: Path, temp_dir: Path) -> None:
        """Test export to JSON with actual ODS file."""
        exporter = AIExporter()
        output_path = temp_dir / "export.json"

        result = exporter.export_to_json(sample_ods, output_path)

        # Verify result structure
        assert "metadata" in result
        assert "sheets" in result
        assert "ai_instructions" in result

        # Verify file was written
        assert output_path.exists()
        with open(output_path) as f:
            loaded = json.load(f)
        assert loaded["metadata"]["source_file"] == str(sample_ods)

    @pytest.mark.skipif(
        not HAS_ODFPY,
        reason="odfpy required for full ODS testing",
    )
    def test_export_dual(self, sample_ods: Path, temp_dir: Path) -> None:
        """Test dual export functionality."""
        exporter = AIExporter()

        ods_output, json_output = exporter.export_dual(sample_ods, temp_dir)

        assert ods_output.exists()
        assert json_output.exists()
        assert ods_output.suffix == ".ods"
        assert json_output.suffix == ".json"

    def test_generate_ai_instructions(self) -> None:
        """Test AI instructions generation."""
        exporter = AIExporter()
        sheets = [SemanticSheet(name="Budget", purpose="Budget tracking")]

        instructions = exporter._generate_ai_instructions(sheets)

        assert "purpose" in instructions
        assert "semantic_types" in instructions
        assert "analysis_suggestions" in instructions

    def test_infer_business_context(self) -> None:
        """Test business context inference."""
        exporter = AIExporter()
        sheets = [
            SemanticSheet(name="Budget", purpose="Budget"),
            SemanticSheet(name="Expenses", purpose="Expenses"),
        ]

        context = exporter._infer_business_context(sheets)

        assert context["domain"] == "personal_finance"
        assert context["sheets_count"] == 2
        assert context["has_budget"] is True


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_export_for_ai_not_found(self, temp_dir: Path) -> None:
        """Test export_for_ai with non-existent file."""
        with pytest.raises(FileError):
            export_for_ai(temp_dir / "nonexistent.ods")

    def test_export_dual_not_found(self, temp_dir: Path) -> None:
        """Test export_dual with non-existent file."""
        with pytest.raises(FileError):
            export_dual(temp_dir / "nonexistent.ods")


class TestExportExceptions:
    """Tests for export exceptions."""

    def test_export_error_base(self) -> None:
        """Test ExportError base class."""
        error = ExportError("Test error")
        assert "FT-EXP-1200" in error.error_code

    def test_dual_export_error(self) -> None:
        """Test DualExportError."""
        error = DualExportError("Export failed")
        assert "FT-EXP-1201" in error.error_code

    def test_consistency_error(self) -> None:
        """Test ConsistencyError."""
        issues = ["Sheet count mismatch", "Missing column"]
        error = ConsistencyError(issues)

        assert "FT-EXP-1202" in error.error_code
        assert error.issues == issues
