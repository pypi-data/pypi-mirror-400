"""Hydrology and water resource formulas.

Civil engineering formulas for hydrology and drainage
(RunoffCoefficient, RationalMethod, ManningEquation, TimeOfConcentration)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class RunoffCoefficient(BaseFormula):
    """Calculate runoff coefficient for drainage design.

        Runoff coefficient based on surface type

    Example:
        >>> formula = RunoffCoefficient()
        >>> result = formula.build("0.35", "5000")
        >>> # Returns: "0.35"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RunoffCoefficient

            Formula metadata
        """
        return FormulaMetadata(
            name="RUNOFF_COEFFICIENT",
            category="hydrology",
            description="Calculate weighted runoff coefficient",
            arguments=(
                FormulaArgument(
                    "coefficient",
                    "number",
                    required=True,
                    description="Runoff coefficient (0-1)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Drainage area (acres or hectares)",
                ),
            ),
            return_type="number",
            examples=(
                "=RUNOFF_COEFFICIENT(0.35;5000)",
                "=RUNOFF_COEFFICIENT(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RunoffCoefficient formula string.

        Args:
            *args: coefficient, area
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RunoffCoefficient formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        coefficient = args[0]
        # area = args[1]  # Used for weighted calculations in practice

        # Return coefficient (can be extended for weighted averages)
        return f"of:={coefficient}"


@dataclass(slots=True, frozen=True)
class RationalMethod(BaseFormula):
    """Calculate peak runoff using rational method.

        Rational method formula Q = CiA

    Example:
        >>> formula = RationalMethod()
        >>> result = formula.build("0.35", "4.5", "100")
        >>> # Returns: "0.35*4.5*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RationalMethod

            Formula metadata
        """
        return FormulaMetadata(
            name="RATIONAL_METHOD",
            category="hydrology",
            description="Calculate peak runoff rate (Q = CiA)",
            arguments=(
                FormulaArgument(
                    "runoff_coefficient",
                    "number",
                    required=True,
                    description="Runoff coefficient C (0-1)",
                ),
                FormulaArgument(
                    "intensity",
                    "number",
                    required=True,
                    description="Rainfall intensity i (in/hr or mm/hr)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Drainage area A (acres or hectares)",
                ),
            ),
            return_type="number",
            examples=(
                "=RATIONAL_METHOD(0.35;4.5;100)",
                "=RATIONAL_METHOD(A1;A2;A3)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RationalMethod formula string.

        Args:
            *args: runoff_coefficient, intensity, area
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RationalMethod formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        runoff_coefficient = args[0]
        intensity = args[1]
        area = args[2]

        # Q = C * i * A
        return f"of:={runoff_coefficient}*{intensity}*{area}"


@dataclass(slots=True, frozen=True)
class ManningEquation(BaseFormula):
    """Calculate flow velocity using Manning's equation.

        Manning's equation for open channel flow

    Example:
        >>> formula = ManningEquation()
        >>> result = formula.build("1.486", "0.013", "5", "0.01")
        >>> # Returns: "(1.486/0.013)*5^(2/3)*0.01^0.5"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ManningEquation

            Formula metadata
        """
        return FormulaMetadata(
            name="MANNING_EQUATION",
            category="hydrology",
            description="Calculate flow velocity in open channels",
            arguments=(
                FormulaArgument(
                    "k",
                    "number",
                    required=True,
                    description="Unit constant (1.486 for US, 1.0 for SI)",
                ),
                FormulaArgument(
                    "n",
                    "number",
                    required=True,
                    description="Manning's roughness coefficient",
                ),
                FormulaArgument(
                    "R",
                    "number",
                    required=True,
                    description="Hydraulic radius (ft or m)",
                ),
                FormulaArgument(
                    "S",
                    "number",
                    required=True,
                    description="Slope of energy grade line (ft/ft or m/m)",
                ),
            ),
            return_type="number",
            examples=(
                "=MANNING_EQUATION(1.486;0.013;5;0.01)",
                "=MANNING_EQUATION(A1;A2;A3;A4)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ManningEquation formula string.

        Args:
            *args: k, n, R, S
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ManningEquation formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        k = args[0]
        n = args[1]
        R = args[2]
        S = args[3]

        # V = (k/n) * R^(2/3) * S^(1/2)
        return f"of:=({k}/{n})*{R}^(2/3)*{S}^0.5"


@dataclass(slots=True, frozen=True)
class TimeOfConcentration(BaseFormula):
    """Calculate time of concentration for watershed.

        Kirpich equation for time of concentration

    Example:
        >>> formula = TimeOfConcentration()
        >>> result = formula.build("5000", "100")
        >>> # Returns: "of:=0.0078*(5000^0.77)/(100^0.385)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for TimeOfConcentration

            Formula metadata
        """
        return FormulaMetadata(
            name="TIME_OF_CONCENTRATION",
            category="hydrology",
            description="Calculate time of concentration using Kirpich equation",
            arguments=(
                FormulaArgument(
                    "length",
                    "number",
                    required=True,
                    description="Flow path length (ft)",
                ),
                FormulaArgument(
                    "elevation_change",
                    "number",
                    required=True,
                    description="Elevation change (ft)",
                ),
            ),
            return_type="number",
            examples=(
                "=TIME_OF_CONCENTRATION(5000;100)",
                "=TIME_OF_CONCENTRATION(A1;A2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build TimeOfConcentration formula string.

        Args:
            *args: length, elevation_change
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            TimeOfConcentration formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        length = args[0]
        elevation_change = args[1]

        # Tc = 0.0078 * L^0.77 / H^0.385 (Kirpich equation, minutes)
        return f"of:=0.0078*({length}^0.77)/({elevation_change}^0.385)"
