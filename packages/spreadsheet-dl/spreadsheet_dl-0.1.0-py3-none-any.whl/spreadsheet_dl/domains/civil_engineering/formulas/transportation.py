"""Transportation engineering formulas for civil engineering.

CIVIL-TRANSPORTATION: Transportation and traffic flow formulas
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class StoppingDistance(BaseFormula):
    """Stopping distance formula: d = v*t_r + v²/(2*g*(f+G)).

    Calculates total stopping sight distance including reaction time.

        CIVIL-TRANSPORTATION-001: Stopping sight distance calculation

    Example:
        >>> formula = StoppingDistance()
        >>> formula.build("25", "2.5", "0.35", "0.03")
        'of:=25*2.5+(25^2)/(2*9.81*(0.35+0.03))'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="STOPPING_DISTANCE",
            category="civil_engineering",
            description="Calculate stopping distance: d = v*t_r + v²/(2*g*(f+G))",
            arguments=(
                FormulaArgument(
                    name="velocity",
                    type="number",
                    required=True,
                    description="Vehicle velocity (m/s)",
                ),
                FormulaArgument(
                    name="reaction_time",
                    type="number",
                    required=True,
                    description="Driver reaction time (s)",
                ),
                FormulaArgument(
                    name="friction_coeff",
                    type="number",
                    required=True,
                    description="Coefficient of friction (dimensionless)",
                ),
                FormulaArgument(
                    name="grade",
                    type="number",
                    required=True,
                    description="Roadway grade (decimal, + for uphill)",
                ),
            ),
            return_type="number",
            examples=(
                "=STOPPING_DISTANCE(25; 2.5; 0.35; 0.03)  # Stopping sight distance",
                "=STOPPING_DISTANCE(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: velocity, reaction_time, friction_coeff, grade

        Returns:
            ODF formula string: of:=velocity*reaction_time+(velocity^2)/(2*9.81*(friction_coeff+grade))
        """
        self.validate_arguments(args)
        velocity, reaction_time, friction_coeff, grade = args
        return f"of:={velocity}*{reaction_time}+({velocity}^2)/(2*9.81*({friction_coeff}+{grade}))"


@dataclass(slots=True, frozen=True)
class TrafficFlow(BaseFormula):
    """Traffic flow formula: q = k*v.

    Fundamental traffic flow equation relating flow, density, and speed.

        CIVIL-TRANSPORTATION-002: Fundamental traffic flow equation

    Example:
        >>> formula = TrafficFlow()
        >>> formula.build("50", "80")
        'of:=50*80'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="TRAFFIC_FLOW",
            category="civil_engineering",
            description="Calculate traffic flow: q = k*v",
            arguments=(
                FormulaArgument(
                    name="density",
                    type="number",
                    required=True,
                    description="Traffic density (vehicles/km)",
                ),
                FormulaArgument(
                    name="speed",
                    type="number",
                    required=True,
                    description="Average speed (km/h)",
                ),
            ),
            return_type="number",
            examples=(
                "=TRAFFIC_FLOW(50; 80)  # Flow = 4000 vehicles/hour",
                "=TRAFFIC_FLOW(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: density, speed

        Returns:
            ODF formula string: of:=density*speed
        """
        self.validate_arguments(args)
        density, speed = args
        return f"of:={density}*{speed}"


__all__ = [
    "StoppingDistance",
    "TrafficFlow",
]
