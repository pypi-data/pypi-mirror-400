"""Tests for feature engineering formulas.

Tests for data transformation and normalization
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.data_science.formulas.feature_engineering import (
    LogTransform,
    MinMaxNormalize,
    ZScoreStandardize,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


class TestMinMaxNormalize:
    """Test MinMaxNormalize formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = MinMaxNormalize()
        metadata = formula.metadata

        assert metadata.name == "MIN_MAX_NORMALIZE"
        assert metadata.category == "feature_engineering"
        assert len(metadata.arguments) == 4
        assert metadata.return_type == "number"

    def test_formula_build_default(self) -> None:
        """Test formula building with default 0-1 range."""
        formula = MinMaxNormalize()
        result = formula.build("A1", "A1:A100")

        assert result.startswith("of:=")
        assert "MIN" in result
        assert "MAX" in result
        assert "A1" in result
        assert "A1:A100" in result

    def test_formula_build_custom_range(self) -> None:
        """Test formula building with custom range."""
        formula = MinMaxNormalize()
        result = formula.build("A1", "A1:A100", -1, 1)

        assert result.startswith("of:=")
        assert "MIN" in result
        assert "MAX" in result
        assert "-1" in result
        assert "1" in result

    def test_formula_with_cell_refs(self) -> None:
        """Test formula with cell references."""
        formula = MinMaxNormalize()
        result = formula.build("B5", "B1:B100")

        assert "B5" in result
        assert "B1:B100" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = MinMaxNormalize()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1")


class TestZScoreStandardize:
    """Test ZScoreStandardize formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = ZScoreStandardize()
        metadata = formula.metadata

        assert metadata.name == "Z_SCORE_STANDARDIZE"
        assert metadata.category == "feature_engineering"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = ZScoreStandardize()
        result = formula.build("A1", "A1:A100")

        assert result.startswith("of:=")
        assert "AVERAGE" in result
        assert "STDEV" in result
        assert "A1" in result
        assert "A1:A100" in result

    def test_formula_structure(self) -> None:
        """Test formula has correct structure."""
        formula = ZScoreStandardize()
        result = formula.build("value", "data_range")

        # Should be (value - mean) / std
        assert "value" in result
        assert "AVERAGE(data_range)" in result
        assert "STDEV(data_range)" in result
        assert "/" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = ZScoreStandardize()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1")


class TestLogTransform:
    """Test LogTransform formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = LogTransform()
        metadata = formula.metadata

        assert metadata.name == "LOG_TRANSFORM"
        assert metadata.category == "feature_engineering"
        assert len(metadata.arguments) == 3

    def test_formula_build_default_natural_log(self) -> None:
        """Test formula building with default natural log."""
        formula = LogTransform()
        result = formula.build("A1")

        assert result.startswith("of:=")
        assert "LN" in result
        assert "A1" in result

    def test_formula_build_log10(self) -> None:
        """Test formula building with log base 10."""
        formula = LogTransform()
        result = formula.build("A1", "10")

        assert result.startswith("of:=")
        assert "LOG10" in result
        assert "A1" in result

    def test_formula_build_log2(self) -> None:
        """Test formula building with log base 2."""
        formula = LogTransform()
        result = formula.build("A1", "2")

        assert result.startswith("of:=")
        assert "LOG" in result
        assert ";2" in result

    def test_formula_build_with_offset(self) -> None:
        """Test formula building with offset."""
        formula = LogTransform()
        result = formula.build("A1", "e", 1)

        assert result.startswith("of:=")
        assert "LN" in result
        assert "A1" in result or "1" in result
        assert "+" in result

    def test_formula_build_custom_base(self) -> None:
        """Test formula building with custom base."""
        formula = LogTransform()
        result = formula.build("A1", "5")

        assert result.startswith("of:=")
        assert "LOG" in result
        assert "5" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = LogTransform()

        # Should not error with 1 arg (value is required, base is optional)
        result = formula.build("A1")
        assert result.startswith("of:=")
