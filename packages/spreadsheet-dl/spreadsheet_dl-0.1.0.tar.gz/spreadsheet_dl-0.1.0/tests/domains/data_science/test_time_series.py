"""Tests for time series formulas.

Comprehensive tests for time series analysis formulas
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.data_science.formulas.time_series import (
    AutoCorrelation,
    ExponentialSmoothing,
    MovingAverage,
    PartialAutoCorrelation,
    Seasonality,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


class TestMovingAverage:
    """Test MovingAverage formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = MovingAverage()
        metadata = formula.metadata

        assert metadata.name == "MOVING_AVERAGE"
        assert metadata.category == "time_series"
        assert len(metadata.arguments) == 3
        assert metadata.return_type == "number"

    def test_formula_build_simple(self) -> None:
        """Test simple moving average."""
        formula = MovingAverage()
        result = formula.build("A1:A100", 7)

        assert result.startswith("of:=")
        assert "AVERAGE" in result
        assert "OFFSET" in result
        assert "7" in result

    def test_formula_build_exponential(self) -> None:
        """Test exponential moving average."""
        formula = MovingAverage()
        result = formula.build("A1:A100", 30, "exponential")

        assert result.startswith("of:=")
        assert "OFFSET" in result
        assert "30" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = MovingAverage()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1:A100")


class TestExponentialSmoothing:
    """Test ExponentialSmoothing formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = ExponentialSmoothing()
        metadata = formula.metadata

        assert metadata.name == "EXPONENTIAL_SMOOTHING"
        assert metadata.category == "time_series"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = ExponentialSmoothing()
        result = formula.build("A1:A100", 0.3)

        assert result.startswith("of:=")
        assert "0.3" in result
        assert "OFFSET" in result

    def test_formula_with_cell_alpha(self) -> None:
        """Test formula with cell reference for alpha."""
        formula = ExponentialSmoothing()
        result = formula.build("A1:A100", "B1")

        assert result.startswith("of:=")
        assert "B1" in result


class TestAutoCorrelation:
    """Test AutoCorrelation formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = AutoCorrelation()
        metadata = formula.metadata

        assert metadata.name == "ACF"
        assert metadata.category == "time_series"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = AutoCorrelation()
        result = formula.build("A1:A100", 5)

        assert result.startswith("of:=")
        assert "CORREL" in result
        assert "OFFSET" in result
        assert "5" in result

    def test_formula_build_lag_12(self) -> None:
        """Test formula with lag 12."""
        formula = AutoCorrelation()
        result = formula.build("A1:A100", 12)

        assert result.startswith("of:=")
        assert "12" in result


class TestPartialAutoCorrelation:
    """Test PartialAutoCorrelation formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = PartialAutoCorrelation()
        metadata = formula.metadata

        assert metadata.name == "PACF"
        assert metadata.category == "time_series"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = PartialAutoCorrelation()
        result = formula.build("A1:A100", 5)

        assert result.startswith("of:=")
        assert "CORREL" in result
        assert "5" in result


class TestSeasonality:
    """Test Seasonality formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = Seasonality()
        metadata = formula.metadata

        assert metadata.name == "SEASONALITY"
        assert metadata.category == "time_series"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = Seasonality()
        result = formula.build("A1:A100", 12)

        assert result.startswith("of:=")
        assert "AVERAGEIF" in result
        assert "12" in result

    def test_formula_build_quarterly(self) -> None:
        """Test formula with quarterly period."""
        formula = Seasonality()
        result = formula.build("A1:A100", 4)

        assert result.startswith("of:=")
        assert "4" in result
