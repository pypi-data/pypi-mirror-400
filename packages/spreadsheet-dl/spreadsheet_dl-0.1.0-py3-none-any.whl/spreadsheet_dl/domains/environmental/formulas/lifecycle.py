"""Life cycle assessment formulas.

Environmental formulas for lifecycle impact assessment
(GlobalWarmingPotential, AcidificationPotential, EutrophicationPotential)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class GlobalWarmingPotential(BaseFormula):
    """Calculate global warming potential (GWP).

        GWP calculation for climate impact

    Example:
        >>> formula = GlobalWarmingPotential()
        >>> result = formula.build("100", "25")
        >>> # Returns: "100*1+25*25"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GWP

            Formula metadata
        """
        return FormulaMetadata(
            name="GWP",
            category="lifecycle",
            description="Calculate global warming potential (CO2 equivalent)",
            arguments=(
                FormulaArgument(
                    "co2_emissions",
                    "number",
                    required=True,
                    description="CO2 emissions (kg)",
                ),
                FormulaArgument(
                    "ch4_emissions",
                    "number",
                    required=True,
                    description="CH4 emissions (kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=GWP(100;25)",
                "=GWP(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GWP formula string.

        Args:
            *args: co2_emissions, ch4_emissions
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            GWP formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        co2_emissions = args[0]
        ch4_emissions = args[1]

        # GWP = CO2*1 + CH4*25 (GWP100 for methane)
        return f"of:={co2_emissions}*1+{ch4_emissions}*25"


@dataclass(slots=True, frozen=True)
class AcidificationPotential(BaseFormula):
    """Calculate acidification potential.

        AP calculation for acid rain impact

    Example:
        >>> formula = AcidificationPotential()
        >>> result = formula.build("10", "5")
        >>> # Returns: "10*0.7+5*1.88"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for AP

            Formula metadata
        """
        return FormulaMetadata(
            name="ACIDIFICATION_POTENTIAL",
            category="lifecycle",
            description="Calculate acidification potential (SO2 equivalent)",
            arguments=(
                FormulaArgument(
                    "nox_emissions",
                    "number",
                    required=True,
                    description="NOx emissions (kg)",
                ),
                FormulaArgument(
                    "so2_emissions",
                    "number",
                    required=True,
                    description="SO2 emissions (kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=ACIDIFICATION_POTENTIAL(10;5)",
                "=ACIDIFICATION_POTENTIAL(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build AcidificationPotential formula string.

        Args:
            *args: nox_emissions, so2_emissions
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            AcidificationPotential formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        nox_emissions = args[0]
        so2_emissions = args[1]

        # AP = NOx*0.7 + SO2*1.88
        return f"of:={nox_emissions}*0.7+{so2_emissions}*1.88"


@dataclass(slots=True, frozen=True)
class EutrophicationPotential(BaseFormula):
    """Calculate eutrophication potential.

        EP calculation for water nutrient pollution

    Example:
        >>> formula = EutrophicationPotential()
        >>> result = formula.build("5", "3", "2")
        >>> # Returns: "5*0.42+3*0.13+2*3.64"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for EP

            Formula metadata
        """
        return FormulaMetadata(
            name="EUTROPHICATION_POTENTIAL",
            category="lifecycle",
            description="Calculate eutrophication potential (PO4 equivalent)",
            arguments=(
                FormulaArgument(
                    "nox_emissions",
                    "number",
                    required=True,
                    description="NOx emissions (kg)",
                ),
                FormulaArgument(
                    "nh3_emissions",
                    "number",
                    required=True,
                    description="NH3 emissions (kg)",
                ),
                FormulaArgument(
                    "po4_emissions",
                    "number",
                    required=True,
                    description="PO4 emissions (kg)",
                ),
            ),
            return_type="number",
            examples=(
                "=EUTROPHICATION_POTENTIAL(5;3;2)",
                "=EUTROPHICATION_POTENTIAL(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build EutrophicationPotential formula string.

        Args:
            *args: nox_emissions, nh3_emissions, po4_emissions
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            EutrophicationPotential formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        nox_emissions = args[0]
        nh3_emissions = args[1]
        po4_emissions = args[2]

        # EP = NOx*0.42 + NH3*0.13 + PO4*3.64
        return f"of:={nox_emissions}*0.42+{nh3_emissions}*0.13+{po4_emissions}*3.64"
