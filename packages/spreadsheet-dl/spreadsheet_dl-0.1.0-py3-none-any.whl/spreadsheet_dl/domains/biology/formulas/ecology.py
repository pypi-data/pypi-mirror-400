"""Ecology and population biology formulas.

Ecology formulas
(SHANNON_DIVERSITY, SIMPSON_INDEX, SPECIES_RICHNESS, POPULATION_GROWTH)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class ShannonDiversityFormula(BaseFormula):
    """Calculate Shannon diversity index.

        SHANNON_DIVERSITY formula for biodiversity analysis

    Example:
        >>> formula = ShannonDiversityFormula()
        >>> result = formula.build("A1:A10")
        >>> # Returns: formula for Shannon H'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SHANNON_DIVERSITY

            Formula metadata
        """
        return FormulaMetadata(
            name="SHANNON_DIVERSITY",
            category="ecology",
            description="Calculate Shannon diversity index (H')",
            arguments=(
                FormulaArgument(
                    "abundance_range",
                    "range",
                    required=True,
                    description="Range of species abundances",
                ),
            ),
            return_type="number",
            examples=(
                "=SHANNON_DIVERSITY(A1:A10)",
                "=SHANNON_DIVERSITY(abundance_column)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SHANNON_DIVERSITY formula string.

        Args:
            *args: abundance_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SHANNON_DIVERSITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        abundance_range = args[0]

        # Shannon H' = -SUM(pi * ln(pi)) where pi = ni/N
        # Simplified for spreadsheet using IF to avoid ln(0)

        pi_formula = f"{abundance_range}/SUM({abundance_range})"
        return f"of:=SUMPRODUCT(IF({abundance_range}=0;0;-({pi_formula})*LN({pi_formula})))"


@dataclass(slots=True, frozen=True)
class SimpsonIndexFormula(BaseFormula):
    """Calculate Simpson's diversity index.

        SIMPSON_INDEX formula for biodiversity analysis

    Example:
        >>> formula = SimpsonIndexFormula()
        >>> result = formula.build("A1:A10")
        >>> # Returns: formula for Simpson's D
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SIMPSON_INDEX

            Formula metadata
        """
        return FormulaMetadata(
            name="SIMPSON_INDEX",
            category="ecology",
            description="Calculate Simpson's diversity index (D)",
            arguments=(
                FormulaArgument(
                    "abundance_range",
                    "range",
                    required=True,
                    description="Range of species abundances",
                ),
                FormulaArgument(
                    "inverse",
                    "number",
                    required=False,
                    description="Return inverse (1/D) if 1, else return D",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=SIMPSON_INDEX(A1:A10)",
                "=SIMPSON_INDEX(A1:A10;1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SIMPSON_INDEX formula string.

        Args:
            *args: abundance_range, [inverse]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SIMPSON_INDEX formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        abundance_range = args[0]
        inverse = args[1] if len(args) > 1 else 0

        # Simpson's D = SUM(pi^2) where pi = ni/N
        # Simpson's diversity index = 1 - D (default)
        # Or inverse D = 1/D (Simpson's reciprocal index)
        # Simplified: SUMPRODUCT((range/SUM(range))^2)

        d_formula = f"SUMPRODUCT(({abundance_range}/SUM({abundance_range}))^2)"

        if inverse and str(inverse) != "0":
            # Return 1/D (Simpson's reciprocal index)
            return f"of:=1/({d_formula})"
        else:
            # Return 1-D (Simpson's diversity index, default)
            return f"of:=1-{d_formula}"


@dataclass(slots=True, frozen=True)
class SpeciesRichnessFormula(BaseFormula):
    """Calculate species richness (number of species).

        SPECIES_RICHNESS formula for biodiversity analysis

    Example:
        >>> formula = SpeciesRichnessFormula()
        >>> result = formula.build("A1:A10")
        >>> # Returns: "COUNTIF(A1:A10;">0")"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SPECIES_RICHNESS

            Formula metadata
        """
        return FormulaMetadata(
            name="SPECIES_RICHNESS",
            category="ecology",
            description="Calculate species richness (number of unique species present)",
            arguments=(
                FormulaArgument(
                    "abundance_range",
                    "range",
                    required=True,
                    description="Range of species abundances",
                ),
            ),
            return_type="number",
            examples=(
                "=SPECIES_RICHNESS(A1:A10)",
                "=SPECIES_RICHNESS(abundance_column)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SPECIES_RICHNESS formula string.

        Args:
            *args: abundance_range
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SPECIES_RICHNESS formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        abundance_range = args[0]

        # Count non-zero values (species present)
        return f'of:=COUNTIF({abundance_range};">0")'


@dataclass(slots=True, frozen=True)
class PopulationGrowthFormula(BaseFormula):
    """Calculate population growth rate.

        POPULATION_GROWTH formula for population dynamics

    Example:
        >>> formula = PopulationGrowthFormula()
        >>> result = formula.build("A1", "0.05", "1")
        >>> # Returns: "A1*EXP(0.05*1)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for POPULATION_GROWTH

            Formula metadata
        """
        return FormulaMetadata(
            name="POPULATION_GROWTH",
            category="ecology",
            description=(
                "Calculate population size using exponential or logistic growth"
            ),
            arguments=(
                FormulaArgument(
                    "n0",
                    "number",
                    required=True,
                    description="Initial population size",
                ),
                FormulaArgument(
                    "r",
                    "number",
                    required=True,
                    description="Growth rate",
                ),
                FormulaArgument(
                    "t",
                    "number",
                    required=True,
                    description="Time period",
                ),
                FormulaArgument(
                    "k",
                    "number",
                    required=False,
                    description="Carrying capacity (for logistic growth)",
                    default=None,
                ),
            ),
            return_type="number",
            examples=(
                "=POPULATION_GROWTH(100;0.05;10)",
                "=POPULATION_GROWTH(100;0.05;10;1000)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build POPULATION_GROWTH formula string.

        Args:
            *args: n0, r, t, [k]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            POPULATION_GROWTH formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        n0 = args[0]
        r = args[1]
        t = args[2]
        k = args[3] if len(args) > 3 else None

        if k is not None:
            # Logistic growth: N(t) = K / (1 + ((K-N0)/N0) * e^(-rt))
            return f"of:={k}/(1+(({k}-{n0})/{n0})*EXP(-{r}*{t}))"
        else:
            # Exponential growth: N(t) = N0 * e^(rt)
            return f"of:={n0}*EXP({r}*{t})"


__all__ = [
    "PopulationGrowthFormula",
    "ShannonDiversityFormula",
    "SimpsonIndexFormula",
    "SpeciesRichnessFormula",
]
