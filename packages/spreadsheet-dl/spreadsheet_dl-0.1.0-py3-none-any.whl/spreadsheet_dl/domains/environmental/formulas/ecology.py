"""Ecology and biodiversity formulas.

Ecology formulas
(SHANNON_DIVERSITY, SIMPSON_INDEX, SPECIES_RICHNESS)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class EcosystemShannonDiversityFormula(BaseFormula):
    """Calculate Shannon Diversity Index.

        SHANNON_DIVERSITY formula for biodiversity assessment

    H' = -SUM(pi * ln(pi)) where pi is proportion of species i.

    Example:
        >>> formula = EcosystemShannonDiversityFormula()  # doctest: +SKIP
        >>> result = formula.build("A1:A10", "B1:B10")  # doctest: +SKIP
        >>> # Returns Shannon index formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SHANNON_DIVERSITY

            Formula metadata
        """
        return FormulaMetadata(
            name="ECOSYSTEM_SHANNON_DIVERSITY",
            category="environmental",
            description="Calculate Shannon Diversity Index (H')",
            arguments=(
                FormulaArgument(
                    "counts_range",
                    "range",
                    required=True,
                    description="Range of species counts",
                ),
            ),
            return_type="number",
            examples=(
                "=SHANNON_DIVERSITY(B2:B20)",
                "=SHANNON_DIVERSITY(species_counts)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SHANNON_DIVERSITY formula string.

        Args:
            *args: counts_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SHANNON_DIVERSITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        counts_range = args[0]

        # Shannon index: H' = -SUM(pi * ln(pi))
        # Using array formula approach
        # pi = count_i / total
        return (
            f"of:=-SUMPRODUCT("
            f"IF({counts_range}>0;"
            f"({counts_range}/SUM({counts_range}))*LN({counts_range}/SUM({counts_range}));"
            f"0))"
        )


@dataclass(slots=True, frozen=True)
class EcosystemSimpsonIndexFormula(BaseFormula):
    """Calculate Simpson's Diversity Index.

        SIMPSON_INDEX formula for biodiversity assessment

    D = 1 - SUM(pi^2) where pi is proportion of species i.

    Example:
        >>> formula = EcosystemSimpsonIndexFormula()
        >>> result = formula.build("A1:A10")
        >>> # Returns Simpson index formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SIMPSON_INDEX

            Formula metadata
        """
        return FormulaMetadata(
            name="ECOSYSTEM_SIMPSON_INDEX",
            category="environmental",
            description="Calculate Simpson's Diversity Index (1-D)",
            arguments=(
                FormulaArgument(
                    "counts_range",
                    "range",
                    required=True,
                    description="Range of species counts",
                ),
            ),
            return_type="number",
            examples=(
                "=SIMPSON_INDEX(B2:B20)",
                "=SIMPSON_INDEX(species_counts)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SIMPSON_INDEX formula string.

        Args:
            *args: counts_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SIMPSON_INDEX formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        counts_range = args[0]

        # Simpson index: D = SUM(pi^2), return 1-D for diversity
        # pi = count_i / total
        return (
            f"of:=1-SUMPRODUCT("
            f"({counts_range}/SUM({counts_range}))*"
            f"({counts_range}/SUM({counts_range})))"
        )


@dataclass(slots=True, frozen=True)
class EcosystemSpeciesRichnessFormula(BaseFormula):
    """Calculate Species Richness.

        SPECIES_RICHNESS formula for biodiversity assessment

    Simple count of distinct species with non-zero abundance.

    Example:
        >>> formula = EcosystemSpeciesRichnessFormula()
        >>> result = formula.build("A1:A10")
        >>> # Returns species richness count formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SPECIES_RICHNESS

            Formula metadata
        """
        return FormulaMetadata(
            name="ECOSYSTEM_SPECIES_RICHNESS",
            category="environmental",
            description="Count species with non-zero abundance",
            arguments=(
                FormulaArgument(
                    "counts_range",
                    "range",
                    required=True,
                    description="Range of species counts",
                ),
            ),
            return_type="number",
            examples=(
                "=SPECIES_RICHNESS(B2:B20)",
                "=SPECIES_RICHNESS(species_counts)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SPECIES_RICHNESS formula string.

        Args:
            *args: counts_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SPECIES_RICHNESS formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        counts_range = args[0]

        # Count cells with value > 0
        return f'of:=COUNTIF({counts_range};">0")'


__all__ = [
    "EcosystemShannonDiversityFormula",
    "EcosystemSimpsonIndexFormula",
    "EcosystemSpeciesRichnessFormula",
]
