"""Tests for clustering metrics formulas.

Tests for clustering quality metrics
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.data_science.formulas.clustering import (
    CalinskiHarabaszIndex,
    DaviesBouldinIndex,
    SilhouetteScore,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]


class TestSilhouetteScore:
    """Test SilhouetteScore formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = SilhouetteScore()
        metadata = formula.metadata

        assert metadata.name == "SILHOUETTE_SCORE"
        assert metadata.category == "clustering"
        assert len(metadata.arguments) == 2
        assert metadata.return_type == "number"

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = SilhouetteScore()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "STDEV" in result
        assert "AVERAGEIF" in result

    def test_formula_with_named_ranges(self) -> None:
        """Test formula with named ranges."""
        formula = SilhouetteScore()
        result = formula.build("data_points", "cluster_ids")

        assert "data_points" in result
        assert "cluster_ids" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = SilhouetteScore()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1:A100")


class TestDaviesBouldinIndex:
    """Test DaviesBouldinIndex formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = DaviesBouldinIndex()
        metadata = formula.metadata

        assert metadata.name == "DAVIES_BOULDIN_INDEX"
        assert metadata.category == "clustering"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = DaviesBouldinIndex()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "VAR" in result or "SUMPRODUCT" in result

    def test_formula_with_cell_ranges(self) -> None:
        """Test formula with cell ranges."""
        formula = DaviesBouldinIndex()
        result = formula.build("data_range", "labels")

        assert "data_range" in result
        assert "labels" in result


class TestCalinskiHarabaszIndex:
    """Test CalinskiHarabaszIndex formula."""

    def test_formula_metadata(self) -> None:
        """Test formula metadata."""
        formula = CalinskiHarabaszIndex()
        metadata = formula.metadata

        assert metadata.name == "CALINSKI_HARABASZ_INDEX"
        assert metadata.category == "clustering"
        assert len(metadata.arguments) == 2

    def test_formula_build(self) -> None:
        """Test formula building."""
        formula = CalinskiHarabaszIndex()
        result = formula.build("A1:A100", "B1:B100")

        assert result.startswith("of:=")
        assert "VAR" in result
        assert "COUNT" in result

    def test_formula_structure(self) -> None:
        """Test formula has correct structure."""
        formula = CalinskiHarabaszIndex()
        result = formula.build("data", "clusters")

        # Should have ratio structure
        assert "/" in result
        # Should have (n-k)/(k-1) term
        assert "COUNT" in result

    def test_formula_validation_error(self) -> None:
        """Test formula validation fails with insufficient args."""
        formula = CalinskiHarabaszIndex()

        with pytest.raises(ValueError, match="requires at least"):
            formula.build("A1:A100")
