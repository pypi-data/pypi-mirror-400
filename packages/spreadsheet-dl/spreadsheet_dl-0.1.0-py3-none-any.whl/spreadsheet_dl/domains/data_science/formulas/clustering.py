"""Clustering quality metrics formulas.

Clustering metrics formulas for unsupervised learning
(Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class SilhouetteScore(BaseFormula):
    """Calculate silhouette score for clustering quality.

        Silhouette score formula for cluster quality measurement

    Example:
        >>> formula = SilhouetteScore()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns silhouette score formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SilhouetteScore

            Formula metadata for silhouette score
        """
        return FormulaMetadata(
            name="SILHOUETTE_SCORE",
            category="clustering",
            description="Calculate silhouette score for cluster quality (-1 to 1)",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of data points",
                ),
                FormulaArgument(
                    "cluster_labels",
                    "range",
                    required=True,
                    description="Range of cluster assignments",
                ),
            ),
            return_type="number",
            examples=(
                "=SILHOUETTE_SCORE(A1:A100;B1:B100)",
                "=SILHOUETTE_SCORE(data_points;cluster_ids)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SilhouetteScore formula string.

        Args:
            *args: data_range, cluster_labels
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Silhouette score formula building (simplified approximation)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        cluster_labels = args[1]

        # Silhouette score is complex - this is a simplified approximation
        # Full calculation requires pairwise distances within and between clusters
        # Using variance-based approximation: (b-a)/max(a,b)
        # where a = intra-cluster distance, b = inter-cluster distance
        return (
            f"of:=(STDEV({data_range})-"
            f"AVERAGEIF({cluster_labels};{cluster_labels};{data_range}))"
            f"/STDEV({data_range})"
        )


@dataclass(slots=True, frozen=True)
class DaviesBouldinIndex(BaseFormula):
    """Calculate Davies-Bouldin Index for clustering quality.

        Davies-Bouldin Index formula for cluster separation measure

    Example:
        >>> formula = DaviesBouldinIndex()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns Davies-Bouldin Index formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DaviesBouldinIndex

            Formula metadata for Davies-Bouldin Index
        """
        return FormulaMetadata(
            name="DAVIES_BOULDIN_INDEX",
            category="clustering",
            description="Calculate Davies-Bouldin Index (lower is better)",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of data points",
                ),
                FormulaArgument(
                    "cluster_labels",
                    "range",
                    required=True,
                    description="Range of cluster assignments",
                ),
            ),
            return_type="number",
            examples=(
                "=DAVIES_BOULDIN_INDEX(A1:A100;B1:B100)",
                "=DAVIES_BOULDIN_INDEX(data_points;cluster_ids)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DaviesBouldinIndex formula string.

        Args:
            *args: data_range, cluster_labels
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Davies-Bouldin Index formula building (simplified)

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        cluster_labels = args[1]

        # Davies-Bouldin Index is complex - simplified approximation
        # DB = 1/k * SUM(max(R_ij)) where R_ij = (S_i + S_j)/M_ij
        # S_i = avg distance within cluster, M_ij = distance between centroids
        # Using variance ratio as approximation
        num_clusters = f"COUNT(UNIQUE({cluster_labels}))"
        within_var = f"SUMPRODUCT((COUNTIF({cluster_labels};{cluster_labels})-1)*VAR({data_range}))"
        between_var = f"VAR({data_range})*COUNT({data_range})"
        return f"of:={within_var}/{between_var}/{num_clusters}"


@dataclass(slots=True, frozen=True)
class CalinskiHarabaszIndex(BaseFormula):
    """Calculate Calinski-Harabasz Index (Variance Ratio Criterion).

        Calinski-Harabasz Index formula for cluster quality

    Example:
        >>> formula = CalinskiHarabaszIndex()
        >>> result = formula.build("A1:A100", "B1:B100")
        >>> # Returns Calinski-Harabasz Index formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CalinskiHarabaszIndex

            Formula metadata for Calinski-Harabasz Index
        """
        return FormulaMetadata(
            name="CALINSKI_HARABASZ_INDEX",
            category="clustering",
            description="Calculate Calinski-Harabasz Index (higher is better)",
            arguments=(
                FormulaArgument(
                    "data_range",
                    "range",
                    required=True,
                    description="Range of data points",
                ),
                FormulaArgument(
                    "cluster_labels",
                    "range",
                    required=True,
                    description="Range of cluster assignments",
                ),
            ),
            return_type="number",
            examples=(
                "=CALINSKI_HARABASZ_INDEX(A1:A100;B1:B100)",
                "=CALINSKI_HARABASZ_INDEX(data_points;cluster_ids)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CalinskiHarabaszIndex formula string.

        Args:
            *args: data_range, cluster_labels
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            Calinski-Harabasz Index formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        data_range = args[0]
        cluster_labels = args[1]

        # Calinski-Harabasz = (Between-cluster dispersion / Within-cluster dispersion)
        #                      * ((n-k)/(k-1))
        # where n = number of points, k = number of clusters
        n = f"COUNT({data_range})"
        k = f"COUNT(UNIQUE({cluster_labels}))"
        between_ss = f"VAR({data_range})*{n}"
        within_ss = f"SUMPRODUCT((COUNTIF({cluster_labels};{cluster_labels})-1)*VAR({data_range}))"

        return f"of:=({between_ss}/{within_ss})*(({n}-{k})/({k}-1))"


__all__ = [
    "CalinskiHarabaszIndex",
    "DaviesBouldinIndex",
    "SilhouetteScore",
]
