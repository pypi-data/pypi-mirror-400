"""Climate modeling formulas.

Climate modeling formulas for radiative forcing, climate sensitivity,
sea level rise, and ice sheet melting
(RADIATIVE_FORCING, CLIMATE_SENSITIVITY, SEA_LEVEL_RISE, ICE_SHEET_MELTING)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class RadiativeForcingFormula(BaseFormula):
    """Calculate radiative forcing from CO2 concentration.

        RADIATIVE_FORCING formula for climate forcing calculation

    Calculates radiative forcing (W/m^2) from atmospheric CO2 concentration
    using the simplified logarithmic relationship.

    Example:
        >>> formula = RadiativeForcingFormula()
        >>> result = formula.build("400", "280")
        >>> # Returns: "5.35*LN(400/280)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for RADIATIVE_FORCING

            Formula metadata
        """
        return FormulaMetadata(
            name="RADIATIVE_FORCING",
            category="environmental",
            description="Calculate radiative forcing from CO2 (W/m^2)",
            arguments=(
                FormulaArgument(
                    "co2_current",
                    "number",
                    required=True,
                    description="Current CO2 concentration (ppm)",
                ),
                FormulaArgument(
                    "co2_reference",
                    "number",
                    required=False,
                    description="Reference CO2 concentration (ppm, default 280)",
                    default=280,
                ),
            ),
            return_type="number",
            examples=(
                "=RADIATIVE_FORCING(400;280)",
                "=RADIATIVE_FORCING(co2_current;co2_pre_industrial)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build RADIATIVE_FORCING formula string.

        Args:
            *args: co2_current, [co2_reference]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            RADIATIVE_FORCING formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        co2_current = args[0]
        co2_reference = args[1] if len(args) > 1 else 280

        # Radiative forcing: RF = 5.35 * ln(C/C0)
        # Where C is current CO2 and C0 is reference (pre-industrial)
        return f"of:=5.35*LN({co2_current}/{co2_reference})"


@dataclass(slots=True, frozen=True)
class ClimateSensitivityFormula(BaseFormula):
    """Calculate temperature response to CO2 doubling.

        CLIMATE_SENSITIVITY formula for equilibrium climate sensitivity

    Calculates expected temperature change from radiative forcing
    using climate sensitivity parameter.

    Example:
        >>> formula = ClimateSensitivityFormula()
        >>> result = formula.build("3.7", "0.8")
        >>> # Returns: "3.7/0.8"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CLIMATE_SENSITIVITY

            Formula metadata
        """
        return FormulaMetadata(
            name="CLIMATE_SENSITIVITY",
            category="environmental",
            description="Calculate temperature response to CO2 doubling (degrees C)",
            arguments=(
                FormulaArgument(
                    "radiative_forcing",
                    "number",
                    required=True,
                    description="Radiative forcing (W/m^2)",
                ),
                FormulaArgument(
                    "climate_feedback",
                    "number",
                    required=False,
                    description="Climate feedback parameter (W/m^2/K, default 0.8)",
                    default=0.8,
                ),
            ),
            return_type="number",
            examples=(
                "=CLIMATE_SENSITIVITY(3.7;0.8)",
                "=CLIMATE_SENSITIVITY(forcing;feedback)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CLIMATE_SENSITIVITY formula string.

        Args:
            *args: radiative_forcing, [climate_feedback]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CLIMATE_SENSITIVITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        radiative_forcing = args[0]
        climate_feedback = args[1] if len(args) > 1 else 0.8

        # Climate sensitivity: ΔT = ΔF / λ
        # Where ΔF is radiative forcing and λ is climate feedback parameter
        return f"of:={radiative_forcing}/{climate_feedback}"


@dataclass(slots=True, frozen=True)
class SeaLevelRiseFormula(BaseFormula):
    """Calculate sea level rise from thermal expansion.

        SEA_LEVEL_RISE formula for thermal expansion calculation

    Calculates sea level rise from ocean thermal expansion
    based on temperature increase and expansion coefficient.

    Example:
        >>> formula = SeaLevelRiseFormula()
        >>> result = formula.build("1.5", "3700", "0.000214")
        >>> # Returns: "1.5*3700*0.000214"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SEA_LEVEL_RISE

            Formula metadata
        """
        return FormulaMetadata(
            name="SEA_LEVEL_RISE",
            category="environmental",
            description="Calculate sea level rise from thermal expansion (meters)",
            arguments=(
                FormulaArgument(
                    "temp_change",
                    "number",
                    required=True,
                    description="Ocean temperature change (degrees C)",
                ),
                FormulaArgument(
                    "ocean_depth",
                    "number",
                    required=False,
                    description="Mean ocean depth (meters, default 3700)",
                    default=3700,
                ),
                FormulaArgument(
                    "expansion_coeff",
                    "number",
                    required=False,
                    description="Thermal expansion coefficient (1/K, default 0.000214)",
                    default=0.000214,
                ),
            ),
            return_type="number",
            examples=(
                "=SEA_LEVEL_RISE(1.5;3700;0.000214)",
                "=SEA_LEVEL_RISE(temp_change;depth;alpha)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SEA_LEVEL_RISE formula string.

        Args:
            *args: temp_change, [ocean_depth], [expansion_coeff]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SEA_LEVEL_RISE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        temp_change = args[0]
        ocean_depth = args[1] if len(args) > 1 else 3700
        expansion_coeff = args[2] if len(args) > 2 else 0.000214

        # Sea level rise from thermal expansion: ΔH = alpha * H * ΔT
        # Where alpha is expansion coefficient, H is ocean depth, ΔT is temp change
        return f"of:={temp_change}*{ocean_depth}*{expansion_coeff}"


@dataclass(slots=True, frozen=True)
class IceSheetMeltingFormula(BaseFormula):
    """Calculate ice sheet mass balance.

        ICE_SHEET_MELTING formula for mass balance equation

    Calculates net ice mass change from accumulation and ablation rates.

    Example:
        >>> formula = IceSheetMeltingFormula()
        >>> result = formula.build("250", "180", "15000000")
        >>> # Returns: "(250-180)*15000000/1000"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ICE_SHEET_MELTING

            Formula metadata
        """
        return FormulaMetadata(
            name="ICE_SHEET_MELTING",
            category="environmental",
            description="Calculate ice sheet mass balance (Gt/year)",
            arguments=(
                FormulaArgument(
                    "accumulation",
                    "number",
                    required=True,
                    description="Snow accumulation rate (Gt/year)",
                ),
                FormulaArgument(
                    "ablation",
                    "number",
                    required=True,
                    description="Ice ablation rate (Gt/year)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=False,
                    description="Ice sheet area (km^2, for density calc)",
                    default=None,
                ),
            ),
            return_type="number",
            examples=(
                "=ICE_SHEET_MELTING(250;180)",
                "=ICE_SHEET_MELTING(accumulation;ablation;area)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ICE_SHEET_MELTING formula string.

        Args:
            *args: accumulation, ablation, [area]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ICE_SHEET_MELTING formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        accumulation = args[0]
        ablation = args[1]
        area = args[2] if len(args) > 2 else None

        # Mass balance: MB = Accumulation - Ablation
        if area and str(area) not in ("", "None"):
            # If area provided, calculate mass balance per unit area
            # then multiply by area (convert km^2 to proper units)
            return f"of:=({accumulation}-{ablation})*{area}/1000"
        else:
            # Simple mass balance
            return f"of:={accumulation}-{ablation}"


@dataclass(slots=True, frozen=True)
class CarbonBudgetFormula(BaseFormula):
    """Calculate remaining carbon budget for temperature target.

        CARBON_BUDGET formula for remaining emissions budget

    Calculates remaining carbon emissions (GtCO2) allowed to stay within
    a specific temperature target, based on Transient Climate Response
    to Cumulative CO2 Emissions (TCRE).

    Example:
        >>> formula = CarbonBudgetFormula()
        >>> result = formula.build("1.5", "1.1", "0.45")
        >>> # Returns: "(1.5-1.1)/0.45" (remaining budget in GtCO2)
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CARBON_BUDGET

            Formula metadata
        """
        return FormulaMetadata(
            name="CARBON_BUDGET",
            category="environmental",
            description="Calculate remaining carbon budget for temperature target (GtCO2)",
            arguments=(
                FormulaArgument(
                    "temp_target",
                    "number",
                    required=True,
                    description="Target temperature limit (degrees C above pre-industrial)",
                ),
                FormulaArgument(
                    "temp_current",
                    "number",
                    required=True,
                    description="Current temperature (degrees C above pre-industrial)",
                ),
                FormulaArgument(
                    "tcre",
                    "number",
                    required=False,
                    description="TCRE - degrees C per 1000 GtCO2 (default 0.45)",
                    default=0.45,
                ),
            ),
            return_type="number",
            examples=(
                "=CARBON_BUDGET(1.5;1.1;0.45)",
                "=CARBON_BUDGET(target;current;tcre)",
                "=CARBON_BUDGET(2.0;1.2)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CARBON_BUDGET formula string.

        Args:
            *args: temp_target, temp_current, [tcre]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CARBON_BUDGET formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        target = args[0]
        current = args[1]
        tcre = args[2] if len(args) > 2 else 0.45

        # Remaining budget (GtCO2) = (Target - Current) / TCRE * 1000
        # TCRE is in degrees per 1000 GtCO2, so multiply by 1000
        return f"of:=({target}-{current})/{tcre}*1000"


__all__ = [
    "CarbonBudgetFormula",
    "ClimateSensitivityFormula",
    "IceSheetMeltingFormula",
    "RadiativeForcingFormula",
    "SeaLevelRiseFormula",
]
