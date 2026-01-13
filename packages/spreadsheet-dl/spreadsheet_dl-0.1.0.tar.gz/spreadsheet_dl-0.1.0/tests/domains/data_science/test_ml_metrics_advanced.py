"""Tests for advanced ML metrics formulas.

Tests for ROC_AUC, LogLoss, CohenKappa, MatthewsCorrCoef
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
    ROC_AUC,
    CohenKappa,
    LogLoss,
    MatthewsCorrCoef,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


class TestROC_AUC:
    """Test ROC_AUC formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = ROC_AUC()
        metadata = formula.metadata

        assert metadata.name == "ROC_AUC"
        assert metadata.category == "ml_metrics"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = ROC_AUC()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "CORREL" in result
        assert "A1:A100" in result
        assert "B1:B100" in result

    def test_formula_with_named_ranges(self) -> None:
        """Test formula with named ranges."""
        formula = ROC_AUC()
        result = formula.build("true_labels", "predicted_probs")

        assert result.startswith("of:=")
        assert "true_labels" in result
        assert "predicted_probs" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = ROC_AUC()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1:A100")


class TestLogLoss:
    """Test LogLoss formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = LogLoss()
        metadata = formula.metadata

        assert metadata.name == "LOG_LOSS"
        assert metadata.category == "ml_metrics"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = LogLoss()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "SUMPRODUCT" in result
        assert "LN" in result
        assert "COUNT" in result

    def test_formula_includes_both_terms(self) -> None:
        """Test formula includes both positive and negative class terms."""
        formula = LogLoss()
        result = formula.build("A1:A100", "B1:B100")

        # Should have both y*ln(p) and (1-y)*ln(1-p)
        assert result.count("LN") == 2
        assert "1-" in result


class TestCohenKappa:
    """Test CohenKappa formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = CohenKappa()
        metadata = formula.metadata

        assert metadata.name == "COHEN_KAPPA"
        assert metadata.category == "ml_metrics"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = CohenKappa()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "SUMPRODUCT" in result
        assert "COUNT" in result

    def test_formula_with_cell_ranges(self) -> None:
        """Test formula with cell ranges."""
        formula = CohenKappa()
        result = formula.build("rater1", "rater2")

        assert "rater1" in result
        assert "rater2" in result


class TestMatthewsCorrCoef:
    """Test MatthewsCorrCoef formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = MatthewsCorrCoef()
        metadata = formula.metadata

        assert metadata.name == "MCC"
        assert metadata.category == "ml_metrics"
        assert len(metadata.arguments) == 4

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = MatthewsCorrCoef()
        result = formula.build(85, 90, 10, 15)

        assert result.startswith("of:=")
        assert "SQRT" in result
        assert "85" in result
        assert "90" in result
        assert "10" in result
        assert "15" in result

    def test_formula_with_cell_refs(self) -> None:
        """Test formula with cell references."""
        formula = MatthewsCorrCoef()
        result = formula.build("A1", "A2", "A3", "A4")

        assert result.startswith("of:=")
        assert "A1" in result
        assert "A2" in result
        assert "A3" in result
        assert "A4" in result

    def test_formula_structure(self) -> None:
        """Test formula has correct structure."""
        formula = MatthewsCorrCoef()
        result = formula.build("TP", "TN", "FP", "FN")

        # Should have numerator (TP*TN - FP*FN)
        assert "TP*TN" in result or "TP)*(TN" in result
        assert "FP*FN" in result or "FP)*(FN" in result
        # Should have denominator with SQRT
        assert "SQRT" in result
        assert result.count("+") >= 3  # At least 3 additions in denominator

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = MatthewsCorrCoef()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build(85, 90, 10)
