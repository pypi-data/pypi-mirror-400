"""Cell biology and growth formulas.

Biology formulas for cell culture and population growth
(CellDensity, ViabilityPercent, DoublingTime, SpecificGrowthRate)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class CellDensity(BaseFormula):
    """Calculate cell density (cells per volume).

        Cell density calculation

    Example:
        >>> formula = CellDensity()
        >>> result = formula.build("1000000", "0.001")
        >>> # Returns: "1000000/0.001"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CellDensity

            Formula metadata
        """
        return FormulaMetadata(
            name="CELL_DENSITY",
            category="cell_biology",
            description="Calculate cell density (cells/mL)",
            arguments=(
                FormulaArgument(
                    "cell_count",
                    "number",
                    required=True,
                    description="Total cell count",
                ),
                FormulaArgument(
                    "volume",
                    "number",
                    required=True,
                    description="Volume (mL)",
                ),
            ),
            return_type="number",
            examples=(
                "=CELL_DENSITY(1000000;0.001)",
                "=CELL_DENSITY(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CellDensity formula string.

        Args:
            *args: cell_count, volume
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CellDensity formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        cell_count = args[0]
        volume = args[1]

        # Density = Cells / Volume
        return f"of:={cell_count}/{volume}"


@dataclass(slots=True, frozen=True)
class ViabilityPercent(BaseFormula):
    """Calculate cell viability percentage.

        Viability calculation from live/dead cell counts

    Example:
        >>> formula = ViabilityPercent()
        >>> result = formula.build("900", "1000")
        >>> # Returns: "900/1000*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ViabilityPercent

            Formula metadata
        """
        return FormulaMetadata(
            name="VIABILITY_PERCENT",
            category="cell_biology",
            description="Calculate cell viability percentage",
            arguments=(
                FormulaArgument(
                    "live_cells",
                    "number",
                    required=True,
                    description="Number of live cells",
                ),
                FormulaArgument(
                    "total_cells",
                    "number",
                    required=True,
                    description="Total number of cells",
                ),
            ),
            return_type="number",
            examples=(
                "=VIABILITY_PERCENT(900;1000)",
                "=VIABILITY_PERCENT(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ViabilityPercent formula string.

        Args:
            *args: live_cells, total_cells
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ViabilityPercent formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        live_cells = args[0]
        total_cells = args[1]

        # Viability % = (Live / Total) * 100
        return f"of:={live_cells}/{total_cells}*100"


@dataclass(slots=True, frozen=True)
class DoublingTime(BaseFormula):
    """Calculate population doubling time.

        Doubling time calculation from growth rate

    Example:
        >>> formula = DoublingTime()
        >>> result = formula.build("0.693")
        >>> # Returns: "of:=LN(2)/0.693"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for DoublingTime

            Formula metadata
        """
        return FormulaMetadata(
            name="DOUBLING_TIME",
            category="cell_biology",
            description="Calculate population doubling time",
            arguments=(
                FormulaArgument(
                    "growth_rate",
                    "number",
                    required=True,
                    description="Specific growth rate μ (1/hr)",
                ),
            ),
            return_type="number",
            examples=(
                "=DOUBLING_TIME(0.693)",
                "=DOUBLING_TIME(A1)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build DoublingTime formula string.

        Args:
            *args: growth_rate
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            DoublingTime formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        growth_rate = args[0]

        # td = ln(2) / μ
        return f"of:=LN(2)/{growth_rate}"


@dataclass(slots=True, frozen=True)
class SpecificGrowthRate(BaseFormula):
    """Calculate specific growth rate from cell densities.

        Exponential growth rate calculation

    Example:
        >>> formula = SpecificGrowthRate()
        >>> result = formula.build("1000000", "100000", "5")
        >>> # Returns: "of:=(LN(1000000)-LN(100000))/5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SpecificGrowthRate

            Formula metadata
        """
        return FormulaMetadata(
            name="SPECIFIC_GROWTH_RATE",
            category="cell_biology",
            description="Calculate specific growth rate (μ)",
            arguments=(
                FormulaArgument(
                    "final_density",
                    "number",
                    required=True,
                    description="Final cell density",
                ),
                FormulaArgument(
                    "initial_density",
                    "number",
                    required=True,
                    description="Initial cell density",
                ),
                FormulaArgument(
                    "time",
                    "number",
                    required=True,
                    description="Time interval (hours)",
                ),
            ),
            return_type="number",
            examples=(
                "=SPECIFIC_GROWTH_RATE(1000000;100000;5)",
                "=SPECIFIC_GROWTH_RATE(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SpecificGrowthRate formula string.

        Args:
            *args: final_density, initial_density, time
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SpecificGrowthRate formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        final_density = args[0]
        initial_density = args[1]
        time = args[2]

        # μ = (ln(X) - ln(X₀)) / t
        return f"of:=(LN({final_density})-LN({initial_density}))/{time}"
