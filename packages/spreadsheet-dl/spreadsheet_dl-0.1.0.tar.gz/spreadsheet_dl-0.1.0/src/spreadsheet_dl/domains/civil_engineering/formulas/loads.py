"""Load calculation formulas for civil engineering.

Load formulas (DEAD_LOAD, LIVE_LOAD, WIND_LOAD, SEISMIC_LOAD)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class DeadLoadFormula(BaseFormula):
    """Dead load formula: DL = rho*V*g.

    Calculates dead load from material density and volume.

        DEAD_LOAD formula

    Example:
        >>> formula = DeadLoadFormula()
        >>> formula.build("2400", "10", "9.81")
        '2400*10*9.81/1000'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="DEAD_LOAD",
            category="civil_engineering",
            description="Calculate dead load: DL = rho*V*g (result in kN)",
            arguments=(
                FormulaArgument(
                    name="rho",
                    type="number",
                    required=True,
                    description="Material density (kg/m³)",
                ),
                FormulaArgument(
                    name="V",
                    type="number",
                    required=True,
                    description="Volume (m³)",
                ),
                FormulaArgument(
                    name="g",
                    type="number",
                    required=False,
                    description="Gravitational acceleration (m/s², default 9.81)",
                    default=9.81,
                ),
            ),
            return_type="number",
            examples=(
                "=DEAD_LOAD(2400; 10; 9.81)  # Concrete volume dead load",
                "=DEAD_LOAD(A2; B2)  # Using default g=9.81",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: rho, V, g (optional, default 9.81)

        Returns:
            ODF formula string: rho*V*g/1000 (converts to kN)
        """
        self.validate_arguments(args)
        rho, V = args[0], args[1]
        g = args[2] if len(args) > 2 else "9.81"
        return f"of:={rho}*{V}*{g}/1000"


@dataclass(slots=True, frozen=True)
class LiveLoadFormula(BaseFormula):
    """Live load formula: LL = q*A.

    Calculates live load from load intensity and area.

        LIVE_LOAD formula

    Example:
        >>> formula = LiveLoadFormula()
        >>> formula.build("5", "50")
        '5*50'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LIVE_LOAD",
            category="civil_engineering",
            description="Calculate live load: LL = q*A",
            arguments=(
                FormulaArgument(
                    name="q",
                    type="number",
                    required=True,
                    description="Live load intensity (kN/m²)",
                ),
                FormulaArgument(
                    name="A",
                    type="number",
                    required=True,
                    description="Tributary area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=LIVE_LOAD(5; 50)  # Residential floor live load",
                "=LIVE_LOAD(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: q, A

        Returns:
            ODF formula string: q*A
        """
        self.validate_arguments(args)
        q, A = args
        return f"of:={q}*{A}"


@dataclass(slots=True, frozen=True)
class WindLoadFormula(BaseFormula):
    """Wind load formula: W = q*G*C_p*A.

    Calculates wind load using design wind pressure and coefficients.

        WIND_LOAD formula

    Example:
        >>> formula = WindLoadFormula()
        >>> formula.build("0.85", "0.85", "0.8", "100")
        '0.85*0.85*0.8*100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="WIND_LOAD",
            category="civil_engineering",
            description="Calculate wind load: W = q*G*C_p*A",
            arguments=(
                FormulaArgument(
                    name="q",
                    type="number",
                    required=True,
                    description="Design wind pressure (kPa)",
                ),
                FormulaArgument(
                    name="G",
                    type="number",
                    required=True,
                    description="Gust factor",
                ),
                FormulaArgument(
                    name="Cp",
                    type="number",
                    required=True,
                    description="Pressure coefficient",
                ),
                FormulaArgument(
                    name="A",
                    type="number",
                    required=True,
                    description="Exposed area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=WIND_LOAD(0.85; 0.85; 0.8; 100)  # Wind load on wall",
                "=WIND_LOAD(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: q, G, Cp, A

        Returns:
            ODF formula string: q*G*Cp*A
        """
        self.validate_arguments(args)
        q, G, Cp, A = args
        return f"of:={q}*{G}*{Cp}*{A}"


@dataclass(slots=True, frozen=True)
class SeismicLoadFormula(BaseFormula):
    """Seismic load formula: F = C_s*W.

    Calculates seismic base shear using seismic coefficient and weight.

        SEISMIC_LOAD formula

    Example:
        >>> formula = SeismicLoadFormula()
        >>> formula.build("0.15", "10000")
        '0.15*10000'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="SEISMIC_LOAD",
            category="civil_engineering",
            description="Calculate seismic load: F = C_s*W",
            arguments=(
                FormulaArgument(
                    name="Cs",
                    type="number",
                    required=True,
                    description="Seismic response coefficient",
                ),
                FormulaArgument(
                    name="W",
                    type="number",
                    required=True,
                    description="Effective seismic weight (kN)",
                ),
            ),
            return_type="number",
            examples=(
                "=SEISMIC_LOAD(0.15; 10000)  # Base shear = 1500 kN",
                "=SEISMIC_LOAD(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: Cs, W

        Returns:
            ODF formula string: Cs*W
        """
        self.validate_arguments(args)
        Cs, W = args
        return f"of:={Cs}*{W}"


__all__ = [
    "DeadLoadFormula",
    "LiveLoadFormula",
    "SeismicLoadFormula",
    "WindLoadFormula",
]
