"""Carbon and sustainability formulas.

Carbon and sustainability formulas
(CARBON_EQUIVALENT, ECOLOGICAL_FOOTPRINT, SUSTAINABILITY_SCORE,
ENVIRONMENTAL_IMPACT_SCORE)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class CarbonEquivalentFormula(BaseFormula):
    """Calculate CO2 equivalent from various emissions.

        CARBON_EQUIVALENT formula for emissions

    Converts various greenhouse gases to CO2 equivalent using GWP.

    Example:
        >>> formula = CarbonEquivalentFormula()
        >>> result = formula.build("1000", "co2")
        >>> # Returns CO2e calculation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CARBON_EQUIVALENT

            Formula metadata
        """
        return FormulaMetadata(
            name="CARBON_EQUIVALENT",
            category="environmental",
            description="Convert emissions to CO2 equivalent (CO2e)",
            arguments=(
                FormulaArgument(
                    "amount",
                    "number",
                    required=True,
                    description="Emission amount (kg or tonnes)",
                ),
                FormulaArgument(
                    "gas_type",
                    "text",
                    required=False,
                    description="Gas type: co2, ch4, n2o, hfc, pfc, sf6",
                    default="co2",
                ),
            ),
            return_type="number",
            examples=(
                "=CARBON_EQUIVALENT(1000;co2)",
                "=CARBON_EQUIVALENT(50;ch4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CARBON_EQUIVALENT formula string.

        Args:
            *args: amount, [gas_type]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CARBON_EQUIVALENT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        amount = args[0]
        gas_type = str(args[1]).lower() if len(args) > 1 else "co2"

        # Global Warming Potentials (100-year, AR5)
        # CO2 = 1, CH4 = 28, N2O = 265, HFCs ~1430, PFCs ~6630, SF6 = 23500
        gwp_map = {
            "co2": 1,
            "ch4": 28,
            "n2o": 265,
            "hfc": 1430,
            "pfc": 6630,
            "sf6": 23500,
        }

        gwp = gwp_map.get(gas_type, 1)

        return f"of:={amount}*{gwp}"


@dataclass(slots=True, frozen=True)
class EcologicalFootprintFormula(BaseFormula):
    """Calculate ecological footprint.

        ECOLOGICAL_FOOTPRINT formula for sustainability

    Estimates ecological footprint in global hectares.

    Example:
        >>> formula = EcologicalFootprintFormula()
        >>> result = formula.build("5000", "2000", "1000")
        >>> # Returns footprint calculation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ECOLOGICAL_FOOTPRINT

            Formula metadata
        """
        return FormulaMetadata(
            name="ECOLOGICAL_FOOTPRINT",
            category="environmental",
            description="Calculate ecological footprint (global hectares)",
            arguments=(
                FormulaArgument(
                    "carbon_footprint",
                    "number",
                    required=True,
                    description="Annual CO2 emissions (kg)",
                ),
                FormulaArgument(
                    "food_consumption",
                    "number",
                    required=False,
                    description="Food consumption factor",
                    default=0,
                ),
                FormulaArgument(
                    "housing_area",
                    "number",
                    required=False,
                    description="Housing area (m2)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=ECOLOGICAL_FOOTPRINT(5000)",
                "=ECOLOGICAL_FOOTPRINT(carbon;food;housing)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ECOLOGICAL_FOOTPRINT formula string.

        Args:
            *args: carbon_footprint, [food_consumption], [housing_area]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ECOLOGICAL_FOOTPRINT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        carbon_footprint = args[0]
        food = args[1] if len(args) > 1 else 0
        housing = args[2] if len(args) > 2 else 0

        # Simplified calculation:
        # Carbon: 1 tonne CO2 = ~0.27 gha (using world average sequestration)
        # Food: varies significantly, use placeholder factor
        # Housing: ~0.0001 gha per m2

        carbon_gha = f"({carbon_footprint}/1000)*0.27"

        if food and str(food) != "0" and housing and str(housing) != "0":
            return f"of:={carbon_gha}+{food}*0.8+{housing}*0.0001"
        elif food and str(food) != "0":
            return f"of:={carbon_gha}+{food}*0.8"
        elif housing and str(housing) != "0":
            return f"of:={carbon_gha}+{housing}*0.0001"
        else:
            return f"of:={carbon_gha}"


@dataclass(slots=True, frozen=True)
class SustainabilityScoreFormula(BaseFormula):
    """Calculate sustainability score.

        SUSTAINABILITY_SCORE formula for ESG metrics

    Calculates normalized sustainability score (0-100).

    Example:
        >>> formula = SustainabilityScoreFormula()
        >>> result = formula.build("75", "80", "85")
        >>> # Returns sustainability score formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SUSTAINABILITY_SCORE

            Formula metadata
        """
        return FormulaMetadata(
            name="SUSTAINABILITY_SCORE",
            category="environmental",
            description="Calculate weighted sustainability score (0-100)",
            arguments=(
                FormulaArgument(
                    "environmental_score",
                    "number",
                    required=True,
                    description="Environmental component score (0-100)",
                ),
                FormulaArgument(
                    "social_score",
                    "number",
                    required=False,
                    description="Social component score (0-100)",
                    default=None,
                ),
                FormulaArgument(
                    "governance_score",
                    "number",
                    required=False,
                    description="Governance component score (0-100)",
                    default=None,
                ),
            ),
            return_type="number",
            examples=(
                "=SUSTAINABILITY_SCORE(75)",
                "=SUSTAINABILITY_SCORE(env;social;gov)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SUSTAINABILITY_SCORE formula string.

        Args:
            *args: environmental_score, [social_score], [governance_score]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SUSTAINABILITY_SCORE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        env_score = args[0]
        social_score = args[1] if len(args) > 1 else None
        gov_score = args[2] if len(args) > 2 else None

        # ESG weighting: E=40%, S=30%, G=30%
        if (
            social_score
            and str(social_score) not in ("", "None")
            and gov_score
            and str(gov_score) not in ("", "None")
        ):
            return f"of:={env_score}*0.4+{social_score}*0.3+{gov_score}*0.3"
        elif social_score and str(social_score) not in ("", "None"):
            return f"of:={env_score}*0.6+{social_score}*0.4"
        else:
            return f"of:={env_score}"


@dataclass(slots=True, frozen=True)
class EnvironmentalImpactScoreFormula(BaseFormula):
    """Calculate environmental impact score.

        ENVIRONMENTAL_IMPACT_SCORE formula for EIA

    Calculates normalized environmental impact score.

    Example:
        >>> formula = EnvironmentalImpactScoreFormula()
        >>> result = formula.build("3", "4", "2", "3")
        >>> # Returns impact score formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ENVIRONMENTAL_IMPACT_SCORE

            Formula metadata
        """
        return FormulaMetadata(
            name="ENVIRONMENTAL_IMPACT_SCORE",
            category="environmental",
            description="Calculate environmental impact score for EIA",
            arguments=(
                FormulaArgument(
                    "magnitude",
                    "number",
                    required=True,
                    description="Impact magnitude (1-5 scale)",
                ),
                FormulaArgument(
                    "duration",
                    "number",
                    required=True,
                    description="Impact duration (1-5 scale)",
                ),
                FormulaArgument(
                    "reversibility",
                    "number",
                    required=True,
                    description="Reversibility (1=reversible, 5=permanent)",
                ),
                FormulaArgument(
                    "probability",
                    "number",
                    required=False,
                    description="Probability of occurrence (0-1)",
                    default=1,
                ),
            ),
            return_type="number",
            examples=(
                "=ENVIRONMENTAL_IMPACT_SCORE(3;4;2)",
                "=ENVIRONMENTAL_IMPACT_SCORE(mag;dur;rev;prob)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENVIRONMENTAL_IMPACT_SCORE formula string.

        Args:
            *args: magnitude, duration, reversibility, [probability]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ENVIRONMENTAL_IMPACT_SCORE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        magnitude = args[0]
        duration = args[1]
        reversibility = args[2]
        probability = args[3] if len(args) > 3 else 1

        # Impact = Magnitude * Duration * Reversibility * Probability
        # Normalized to 0-100 scale (max raw = 5*5*5*1 = 125, so divide by 1.25)
        return f"of:=({magnitude}*{duration}*{reversibility}*{probability})/1.25"


__all__ = [
    "CarbonEquivalentFormula",
    "EcologicalFootprintFormula",
    "EnvironmentalImpactScoreFormula",
    "SustainabilityScoreFormula",
]
