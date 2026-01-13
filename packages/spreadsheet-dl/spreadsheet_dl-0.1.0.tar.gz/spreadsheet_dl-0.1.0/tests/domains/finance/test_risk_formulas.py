"""Tests for risk management formulas.

Test suite for risk analysis formulas including VaR, CVaR, volatility,
alpha, tracking error, information ratio, and downside deviation.
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.finance.formulas.risk import (
    AlphaRatio,
    ConditionalVaR,
    DownsideDeviation,
    InformationRatio,
    PortfolioVolatility,
    TrackingError,
    ValueAtRisk,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.finance]


class TestValueAtRisk:
    """Test ValueAtRisk formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = ValueAtRisk()
        metadata = formula.metadata

        assert metadata.name == "VAR"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = ValueAtRisk()
        result = formula.build("A1:A100", "0.95")

        assert result.startswith("of:=")
        assert "PERCENTILE" in result
        assert "A1:A100" in result
        assert "0.95" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = ValueAtRisk()
        result = formula.build("B1:B252", "C1")

        assert result.startswith("of:=")
        assert "B1:B252" in result
        assert "C1" in result

    def test_validation_missing_args(self) -> None:
        """Test validation with missing arguments."""
        formula = ValueAtRisk()
        with pytest.raises(ValueError, match="requires at least 2 arguments"):
            formula.build("A1:A100")


class TestConditionalVaR:
    """Test ConditionalVaR formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = ConditionalVaR()
        metadata = formula.metadata

        assert metadata.name == "CVAR"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 2

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = ConditionalVaR()
        result = formula.build("A1:A100", "0.95")

        assert result.startswith("of:=")
        assert "AVERAGEIF" in result
        assert "PERCENTILE" in result
        assert "A1:A100" in result


class TestPortfolioVolatility:
    """Test PortfolioVolatility formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = PortfolioVolatility()
        metadata = formula.metadata

        assert metadata.name == "PORTFOLIO_VOLATILITY"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 1

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = PortfolioVolatility()
        result = formula.build("A1:A100")

        assert result.startswith("of:=")
        assert "STDEV" in result
        assert "A1:A100" in result


class TestAlphaRatio:
    """Test AlphaRatio formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = AlphaRatio()
        metadata = formula.metadata

        assert metadata.name == "ALPHA_RATIO"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 4

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = AlphaRatio()
        result = formula.build("0.12", "0.03", "1.2", "0.10")

        assert result.startswith("of:=")
        assert "0.12" in result
        assert "0.03" in result
        assert "1.2" in result
        assert "0.10" in result

    def test_build_with_cell_references(self) -> None:
        """Test formula with cell references."""
        formula = AlphaRatio()
        result = formula.build("A1", "B1", "C1", "D1")

        assert result.startswith("of:=")
        assert "A1" in result
        assert "B1" in result
        assert "C1" in result
        assert "D1" in result


class TestTrackingError:
    """Test TrackingError formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = TrackingError()
        metadata = formula.metadata

        assert metadata.name == "TRACKING_ERROR"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 2

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = TrackingError()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "STDEV" in result
        assert "A1:A100" in result
        assert "B1:B100" in result


class TestInformationRatio:
    """Test InformationRatio formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = InformationRatio()
        metadata = formula.metadata

        assert metadata.name == "INFORMATION_RATIO"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 2

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = InformationRatio()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "AVERAGE" in result
        assert "STDEV" in result
        assert "A1:A100" in result
        assert "B1:B100" in result


class TestDownsideDeviation:
    """Test DownsideDeviation formula."""

    def test_metadata(self) -> None:
        """Test formula metadata."""
        formula = DownsideDeviation()
        metadata = formula.metadata

        assert metadata.name == "DOWNSIDE_DEVIATION"
        assert metadata.category == "risk"
        assert len(metadata.arguments) == 2
        assert metadata.arguments[1].default == 0

    def test_build_basic(self) -> None:
        """Test basic formula building."""
        formula = DownsideDeviation()
        result = formula.build("A1:A100", "0")

        assert result.startswith("of:=")
        assert "SQRT" in result
        assert "SUMPRODUCT" in result
        assert "COUNTIF" in result
        assert "A1:A100" in result

    def test_build_with_custom_target(self) -> None:
        """Test formula with custom target."""
        formula = DownsideDeviation()
        result = formula.build("B1:B252", "0.02")

        assert result.startswith("of:=")
        assert "B1:B252" in result
        assert "0.02" in result

    def test_build_default_target(self) -> None:
        """Test formula with default target."""
        formula = DownsideDeviation()
        result = formula.build("A1:A100")

        assert result.startswith("of:=")
        assert "A1:A100" in result


class TestRiskFormulasIntegration:
    """Integration tests for risk formulas."""

    def test_all_formulas_have_metadata(self) -> None:
        """Test all risk formulas have valid metadata."""
        formulas = [
            ValueAtRisk(),
            ConditionalVaR(),
            PortfolioVolatility(),
            AlphaRatio(),
            TrackingError(),
            InformationRatio(),
            DownsideDeviation(),
        ]

        for formula in formulas:
            metadata = formula.metadata
            assert metadata.name
            assert metadata.category == "risk"
            assert metadata.description
            assert len(metadata.arguments) > 0
            assert len(metadata.examples) > 0

    def test_all_formulas_build_valid_strings(self) -> None:
        """Test all risk formulas build valid ODF strings."""
        test_cases = [
            (ValueAtRisk(), ["A1:A100", "0.95"]),
            (ConditionalVaR(), ["A1:A100", "0.95"]),
            (PortfolioVolatility(), ["A1:A100"]),
            (AlphaRatio(), ["0.12", "0.03", "1.2", "0.10"]),
            (TrackingError(), ["A1:A100", "B1:B100"]),
            (InformationRatio(), ["A1:A100", "B1:B100"]),
            (DownsideDeviation(), ["A1:A100", "0"]),
        ]

        for formula, args in test_cases:
            result = formula.build(*args)
            assert result.startswith("of:=")
            assert len(result) > 5
