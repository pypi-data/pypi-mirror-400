"""
Tests for Data Science domain plugin.

    Comprehensive tests for data science domain
    - Template tests (5 templates)
    - Formula tests (14 formulas)
    - Importer tests (3 importers)
    - Integration tests
    - Error handling tests
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spreadsheet_dl.domains.data_science import (
    AccuracyFormula,
    AverageFormula,
    ChiSquareTestFormula,
    ConfusionMatrixMetricFormula,
    CorrelationFormula,
    DataScienceDomainPlugin,
    F1ScoreFormula,
    FTestFormula,
    JupyterMetadataImporter,
    MedianFormula,
    MLflowImporter,
    PrecisionFormula,
    RecallFormula,
    ScientificCSVImporter,
    StdevFormula,
    TTestFormula,
    VarianceFormula,
    ZTestFormula,
    calculate_confusion_matrix_metrics,
    format_scientific_notation,
    infer_data_type,
    parse_scientific_notation,
)

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Plugin Tests
# ============================================================================


class TestDataScienceDomainPlugin:
    """Test DataScienceDomainPlugin."""

    def test_plugin_metadata(self) -> None:
        """Test plugin metadata is correct."""
        plugin = DataScienceDomainPlugin()
        metadata = plugin.metadata

        assert metadata.name == "data_science"
        assert metadata.version == "0.1.0"
        assert "data science" in metadata.description.lower()
        assert "data-science" in metadata.tags

    def test_plugin_initialization(self) -> None:
        """Test plugin initializes correctly."""
        plugin = DataScienceDomainPlugin()
        plugin.initialize()

        # Check formulas registered
        assert len(plugin.list_formulas()) >= 14
        assert "TTEST" in plugin.list_formulas()
        assert "ACCURACY" in plugin.list_formulas()
        assert "DS_AVERAGE" in plugin.list_formulas()

        # Check importers registered
        assert len(plugin.list_importers()) == 3
        assert "scientific_csv" in plugin.list_importers()
        assert "mlflow" in plugin.list_importers()
        assert "jupyter" in plugin.list_importers()

    def test_plugin_validation(self) -> None:
        """Test plugin validates correctly."""
        plugin = DataScienceDomainPlugin()
        plugin.initialize()

        assert plugin.validate() is True

    def test_plugin_cleanup(self) -> None:
        """Test plugin cleanup doesn't error."""
        plugin = DataScienceDomainPlugin()
        plugin.initialize()
        plugin.cleanup()  # Should not raise


# ============================================================================
# Formula Tests - Statistical
# ============================================================================


class TestTTestFormula:
    """Test TTestFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = TTestFormula()
        metadata = formula.metadata

        assert metadata.name == "TTEST"
        assert metadata.category == "statistical"
        assert len(metadata.arguments) == 4

    def test_formula_build_two_args(self) -> None:
        """Test formula building with two args."""
        formula = TTestFormula()
        result = formula.build("A1:A10", "B1:B10")

        assert result == "of:=TTEST(A1:A10;B1:B10;2;1)"

    def test_formula_build_all_args(self) -> None:
        """Test formula building with all args."""
        formula = TTestFormula()
        result = formula.build("A1:A10", "B1:B10", 1, 2)

        assert result == "of:=TTEST(A1:A10;B1:B10;1;2)"

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = TTestFormula()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1:A10")


class TestFTestFormula:
    """Test FTestFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = FTestFormula()
        metadata = formula.metadata

        assert metadata.name == "FTEST"
        assert metadata.category == "statistical"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = FTestFormula()
        result = formula.build("A1:A10", "B1:B10")

        assert result == "of:=FTEST(A1:A10;B1:B10)"


class TestZTestFormula:
    """Test ZTestFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = ZTestFormula()
        metadata = formula.metadata

        assert metadata.name == "ZTEST"

    def test_formula_build_without_sigma(self) -> None:
        """Test formula without sigma."""
        formula = ZTestFormula()
        result = formula.build("A1:A10", 50)

        assert result == "of:=ZTEST(A1:A10;50)"

    def test_formula_build_with_sigma(self) -> None:
        """Test formula with sigma."""
        formula = ZTestFormula()
        result = formula.build("A1:A10", 50, 5)

        assert result == "of:=ZTEST(A1:A10;50;5)"


class TestChiSquareTestFormula:
    """Test ChiSquareTestFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = ChiSquareTestFormula()
        metadata = formula.metadata

        assert metadata.name == "CHISQ_TEST"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = ChiSquareTestFormula()
        result = formula.build("A1:B5", "D1:E5")

        # ODF uses CHITEST
        assert result == "of:=CHITEST(A1:B5;D1:E5)"


# ============================================================================
# Formula Tests - ML Metrics
# ============================================================================


class TestAccuracyFormula:
    """Test AccuracyFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = AccuracyFormula()
        metadata = formula.metadata

        assert metadata.name == "ACCURACY"
        assert metadata.category == "ml_metrics"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = AccuracyFormula()
        result = formula.build(85, 90, 10, 15)

        assert result == "of:=(85+90)/(85+90+10+15)"

    def test_formula_with_cell_refs(self) -> None:
        """Test formula with cell references."""
        formula = AccuracyFormula()
        result = formula.build("A1", "A2", "A3", "A4")

        assert result == "of:=(A1+A2)/(A1+A2+A3+A4)"


class TestPrecisionFormula:
    """Test PrecisionFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = PrecisionFormula()
        metadata = formula.metadata

        assert metadata.name == "PRECISION"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = PrecisionFormula()
        result = formula.build(85, 10)

        assert result == "of:=85/(85+10)"


class TestRecallFormula:
    """Test RecallFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = RecallFormula()
        metadata = formula.metadata

        assert metadata.name == "RECALL"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = RecallFormula()
        result = formula.build(85, 15)

        assert result == "of:=85/(85+15)"


class TestF1ScoreFormula:
    """Test F1ScoreFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = F1ScoreFormula()
        metadata = formula.metadata

        assert metadata.name == "F1SCORE"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = F1ScoreFormula()
        result = formula.build(0.9, 0.85)

        assert result == "of:=2*(0.9*0.85)/(0.9+0.85)"


class TestConfusionMatrixMetricFormula:
    """Test ConfusionMatrixMetricFormula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = ConfusionMatrixMetricFormula()
        metadata = formula.metadata

        assert metadata.name == "CONFUSION_MATRIX_METRIC"

    def test_formula_build_accuracy(self) -> None:
        """Test accuracy extraction."""
        formula = ConfusionMatrixMetricFormula()
        result = formula.build("A1:B2", "accuracy")

        assert "INDEX" in result
        assert "accuracy" in result.lower() or "A1:B2" in result

    def test_formula_build_precision(self) -> None:
        """Test precision extraction."""
        formula = ConfusionMatrixMetricFormula()
        result = formula.build("A1:B2", "precision")

        assert "INDEX" in result

    def test_formula_invalid_metric(self) -> None:
        """Test invalid metric name."""
        formula = ConfusionMatrixMetricFormula()

        with pytest.raises(ValueError, match="Unknown metric"):
            formula.build("A1:B2", "invalid_metric")


# ============================================================================
# Formula Tests - Data Functions
# ============================================================================


class TestDataFunctionFormulas:
    """Test data function formulas."""

    def test_average_formula(self) -> None:
        """Test AverageFormula."""
        formula = AverageFormula()
        result = formula.build("A1:A10")

        assert result == "of:=AVERAGE(A1:A10)"

    def test_median_formula(self) -> None:
        """Test MedianFormula."""
        formula = MedianFormula()
        result = formula.build("A1:A10")

        assert result == "of:=MEDIAN(A1:A10)"

    def test_stdev_formula(self) -> None:
        """Test StdevFormula."""
        formula = StdevFormula()
        result = formula.build("A1:A10")

        assert result == "of:=STDEV(A1:A10)"

    def test_variance_formula(self) -> None:
        """Test VarianceFormula."""
        formula = VarianceFormula()
        result = formula.build("A1:A10")

        assert result == "of:=VAR(A1:A10)"

    def test_correlation_formula(self) -> None:
        """Test CorrelationFormula."""
        formula = CorrelationFormula()
        result = formula.build("A1:A10", "B1:B10")

        assert result == "of:=CORREL(A1:A10;B1:B10)"


# ============================================================================
# Importer Tests
# ============================================================================


class TestScientificCSVImporter:
    """Test ScientificCSVImporter."""

    def test_importer_metadata(self) -> None:
        """Test importer metadata."""
        importer = ScientificCSVImporter()
        metadata = importer.metadata

        assert metadata.name == "Scientific CSV Importer"
        assert "csv" in metadata.supported_formats

    def test_validate_source_valid(self, tmp_path: Path) -> None:
        """Test source validation with valid file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("header1,header2\nvalue1,value2\n")

        importer = ScientificCSVImporter()
        assert importer.validate_source(csv_file) is True

    def test_validate_source_invalid(self) -> None:
        """Test source validation with invalid file."""
        importer = ScientificCSVImporter()
        assert importer.validate_source("/nonexistent/file.csv") is False

    def test_import_csv_basic(self, tmp_path: Path) -> None:
        """Test basic CSV import."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,score\nAlice,25,95.5\nBob,30,87.2\n")

        importer = ScientificCSVImporter()
        result = importer.import_data(csv_file)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
        assert result.data[0]["name"] == "Alice"
        assert result.data[0]["age"] == 25  # Should be int
        assert result.data[0]["score"] == 95.5  # Should be float

    def test_import_csv_scientific_notation(self, tmp_path: Path) -> None:
        """Test CSV import with scientific notation."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("measurement,value\nsmall,1.23e-5\nlarge,4.56E+10\n")

        importer = ScientificCSVImporter()
        result = importer.import_data(csv_file)

        assert result.success is True
        assert isinstance(result.data[0]["value"], float)
        assert abs(result.data[0]["value"] - 1.23e-5) < 1e-10
        assert isinstance(result.data[1]["value"], float)

    def test_import_empty_file(self, tmp_path: Path) -> None:
        """Test import of empty CSV."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        importer = ScientificCSVImporter()
        result = importer.import_data(csv_file)

        assert result.success is False
        assert "Empty CSV file" in result.errors[0]


class TestMLflowImporter:
    """Test MLflowImporter."""

    def test_importer_metadata(self) -> None:
        """Test importer metadata."""
        importer = MLflowImporter()
        metadata = importer.metadata

        assert metadata.name == "MLflow Importer"
        assert "json" in metadata.supported_formats

    def test_validate_source_valid(self, tmp_path: Path) -> None:
        """Test source validation."""
        json_file = tmp_path / "runs.json"
        json_file.write_text("{}")

        importer = MLflowImporter()
        assert importer.validate_source(json_file) is True

    def test_import_single_run(self, tmp_path: Path) -> None:
        """Test import single MLflow run."""
        run_data = {
            "run_id": "abc123",
            "status": "FINISHED",
            "start_time": 1000000,
            "end_time": 1010000,
            "metrics": {"accuracy": 0.92, "loss": 0.15},
            "params": {"lr": "0.001", "batch_size": "32"},
        }

        json_file = tmp_path / "run.json"
        json_file.write_text(json.dumps(run_data))

        importer = MLflowImporter()
        result = importer.import_data(json_file)

        assert result.success is True
        assert result.records_imported == 1
        assert result.data[0]["run_id"] == "abc123"
        assert result.data[0]["metrics"]["accuracy"] == 0.92

    def test_import_multiple_runs(self, tmp_path: Path) -> None:
        """Test import multiple MLflow runs."""
        runs_data = [
            {
                "run_id": "run1",
                "status": "FINISHED",
                "metrics": {"accuracy": 0.9},
                "params": {},
            },
            {
                "run_id": "run2",
                "status": "RUNNING",
                "metrics": {"accuracy": 0.85},
                "params": {},
            },
        ]

        json_file = tmp_path / "runs.json"
        json_file.write_text(json.dumps(runs_data))

        importer = MLflowImporter()
        result = importer.import_data(json_file)

        assert result.success is True
        assert result.records_imported == 2

    def test_import_invalid_json(self, tmp_path: Path) -> None:
        """Test import with invalid JSON."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("not valid json{")

        importer = MLflowImporter()
        result = importer.import_data(json_file)

        assert result.success is False
        assert "Invalid JSON" in result.errors[0]


class TestJupyterMetadataImporter:
    """Test JupyterMetadataImporter."""

    def test_importer_metadata(self) -> None:
        """Test importer metadata."""
        importer = JupyterMetadataImporter()
        metadata = importer.metadata

        assert metadata.name == "Jupyter Metadata Importer"
        assert "ipynb" in metadata.supported_formats

    def test_validate_source_valid(self, tmp_path: Path) -> None:
        """Test source validation."""
        nb_file = tmp_path / "notebook.ipynb"
        nb_file.write_text("{}")

        importer = JupyterMetadataImporter()
        assert importer.validate_source(nb_file) is True

    def test_import_basic_notebook(self, tmp_path: Path) -> None:
        """Test import basic notebook."""
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "name": "python3",
                    "display_name": "Python 3",
                },
                "language_info": {
                    "name": "python",
                },
            },
            "cells": [
                {"cell_type": "code", "execution_count": 1, "outputs": []},
                {"cell_type": "markdown", "source": ["# Header 1\n", "## Header 2"]},
                {"cell_type": "code", "execution_count": 2, "outputs": []},
            ],
        }

        nb_file = tmp_path / "notebook.ipynb"
        nb_file.write_text(json.dumps(notebook))

        importer = JupyterMetadataImporter()
        result = importer.import_data(nb_file)

        assert result.success is True
        assert result.data["cell_count"] == 3
        assert result.data["code_cells"] == 2
        assert result.data["markdown_cells"] == 1
        assert result.data["kernel"] == "Python 3"
        assert len(result.data["headers"]) == 2

    def test_import_empty_notebook(self, tmp_path: Path) -> None:
        """Test import empty notebook."""
        notebook = {
            "nbformat": 4,
            "metadata": {},
            "cells": [],
        }

        nb_file = tmp_path / "empty.ipynb"
        nb_file.write_text(json.dumps(notebook))

        importer = JupyterMetadataImporter()
        result = importer.import_data(nb_file)

        assert result.success is True
        assert result.data["cell_count"] == 0


# ============================================================================
# Utility Tests
# ============================================================================


class TestUtilities:
    """Test utility functions."""

    def test_format_scientific_notation(self) -> None:
        """Test scientific notation formatting."""
        result = format_scientific_notation(0.00012345, 2)
        assert result == "1.23e-04"

    def test_parse_scientific_notation(self) -> None:
        """Test scientific notation parsing."""
        result = parse_scientific_notation("1.23e-04")
        assert abs(result - 0.000123) < 1e-10

    def test_parse_scientific_notation_invalid(self) -> None:
        """Test parsing invalid notation."""
        with pytest.raises(ValueError, match="Invalid scientific notation"):
            parse_scientific_notation("not a number")

    def test_calculate_confusion_matrix_metrics(self) -> None:
        """Test confusion matrix metrics calculation."""
        metrics = calculate_confusion_matrix_metrics(85, 90, 10, 15)

        assert abs(metrics["accuracy"] - 0.875) < 0.001
        assert abs(metrics["precision"] - (85 / 95)) < 0.001
        assert abs(metrics["recall"] - (85 / 100)) < 0.001

    def test_calculate_confusion_matrix_zero_division(self) -> None:
        """Test metrics with zero values."""
        metrics = calculate_confusion_matrix_metrics(0, 0, 0, 0)

        assert metrics["accuracy"] == 0.0
        assert metrics["precision"] == 0.0

    def test_infer_data_type(self) -> None:
        """Test data type inference."""
        assert infer_data_type(123) == "number"
        assert infer_data_type(45.67) == "number"
        assert infer_data_type("hello") == "text"
        assert infer_data_type(True) == "boolean"


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for data science domain."""

    def test_plugin_formula_integration(self) -> None:
        """Test plugin can retrieve and use formulas."""
        plugin = DataScienceDomainPlugin()
        plugin.initialize()

        # Get formula class
        formula_class = plugin.get_formula("TTEST")
        assert formula_class is not None

        # Create formula instance
        formula = formula_class()
        result = formula.build("A1:A10", "B1:B10")

        assert "TTEST" in result

    def test_plugin_importer_integration(self) -> None:
        """Test plugin can retrieve and use importers."""
        plugin = DataScienceDomainPlugin()
        plugin.initialize()

        # Get importer class
        importer_class = plugin.get_importer("scientific_csv")
        assert importer_class is not None

        # Create importer instance
        importer = importer_class()
        metadata = importer.metadata

        assert "CSV" in metadata.name
