"""Water quality formulas.

Water quality formulas
(WATER_QUALITY_INDEX, BOD_CALCULATION)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class WaterQualityIndexFormula(BaseFormula):
    """Calculate Water Quality Index (WQI).

        WATER_QUALITY_INDEX formula for water quality assessment

    Uses weighted arithmetic index method.

    Example:
        >>> formula = WaterQualityIndexFormula()
        >>> result = formula.build("A1", "B1", "C1")
        >>> # Returns WQI calculation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WATER_QUALITY_INDEX

            Formula metadata
        """
        return FormulaMetadata(
            name="WATER_QUALITY_INDEX",
            category="environmental",
            description="Calculate Water Quality Index from parameters",
            arguments=(
                FormulaArgument(
                    "do_saturation",
                    "number",
                    required=True,
                    description="Dissolved oxygen saturation (%)",
                ),
                FormulaArgument(
                    "bod",
                    "number",
                    required=True,
                    description="Biochemical oxygen demand (mg/L)",
                ),
                FormulaArgument(
                    "ph",
                    "number",
                    required=True,
                    description="pH value (0-14)",
                ),
                FormulaArgument(
                    "turbidity",
                    "number",
                    required=False,
                    description="Turbidity (NTU)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=WATER_QUALITY_INDEX(95;2;7.2)",
                "=WATER_QUALITY_INDEX(do;bod;ph;turbidity)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WATER_QUALITY_INDEX formula string.

        Args:
            *args: do_saturation, bod, ph, [turbidity]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            WATER_QUALITY_INDEX formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        do_sat = args[0]
        bod = args[1]
        ph = args[2]
        turbidity = args[3] if len(args) > 3 else 0

        # Simplified WQI calculation:
        # DO sub-index: 100 at 100% saturation
        # BOD sub-index: 100 at 0, decreasing
        # pH sub-index: 100 at pH 7, decreasing away
        # Each weighted equally for simplicity

        do_index = f"MIN({do_sat};100)"
        bod_index = f"MAX(0;100-{bod}*10)"
        ph_index = f"100-ABS({ph}-7)*15"

        if turbidity and str(turbidity) != "0":
            turb_index = f"MAX(0;100-{turbidity}*2)"
            return f"of:=({do_index}+{bod_index}+{ph_index}+{turb_index})/4"
        else:
            return f"of:=({do_index}+{bod_index}+{ph_index})/3"


@dataclass(slots=True, frozen=True)
class BODCalculationFormula(BaseFormula):
    """Calculate Biochemical Oxygen Demand (BOD).

        BOD_CALCULATION formula for water quality

    Calculates BOD from initial and final DO measurements.

    Example:
        >>> formula = BODCalculationFormula()
        >>> result = formula.build("8.5", "3.2", "300")
        >>> # Returns BOD calculation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BOD_CALCULATION

            Formula metadata
        """
        return FormulaMetadata(
            name="BOD_CALCULATION",
            category="environmental",
            description="Calculate BOD from DO depletion",
            arguments=(
                FormulaArgument(
                    "initial_do",
                    "number",
                    required=True,
                    description="Initial dissolved oxygen (mg/L)",
                ),
                FormulaArgument(
                    "final_do",
                    "number",
                    required=True,
                    description="Final dissolved oxygen after incubation (mg/L)",
                ),
                FormulaArgument(
                    "sample_volume",
                    "number",
                    required=True,
                    description="Sample volume (mL)",
                ),
                FormulaArgument(
                    "bottle_volume",
                    "number",
                    required=False,
                    description="BOD bottle volume (mL, default 300)",
                    default=300,
                ),
            ),
            return_type="number",
            examples=(
                "=BOD_CALCULATION(8.5;3.2;30)",
                "=BOD_CALCULATION(initial;final;sample;300)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BOD_CALCULATION formula string.

        Args:
            *args: initial_do, final_do, sample_volume, [bottle_volume]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            BOD_CALCULATION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        initial_do = args[0]
        final_do = args[1]
        sample_volume = args[2]
        bottle_volume = args[3] if len(args) > 3 else 300

        # BOD = (Initial DO - Final DO) * (Bottle Volume / Sample Volume)
        return f"of:=({initial_do}-{final_do})*({bottle_volume}/{sample_volume})"


__all__ = [
    "BODCalculationFormula",
    "WaterQualityIndexFormula",
]
