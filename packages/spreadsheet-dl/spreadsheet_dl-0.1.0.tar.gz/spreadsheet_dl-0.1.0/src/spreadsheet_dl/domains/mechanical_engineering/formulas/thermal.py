"""Thermal formulas for mechanical engineering.

Thermal formulas (THERMAL_EXPANSION, THERMAL_STRESS)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class LinearThermalExpansionFormula(BaseFormula):
    """Linear Thermal Expansion formula for mechanical components: DeltaL = alpha * L * DeltaT.

    Calculates linear thermal expansion given coefficient of thermal expansion,
    original length, and temperature change for mechanical engineering applications.

        LINEAR_THERMAL_EXPANSION formula

    Example:
        >>> formula = LinearThermalExpansionFormula()
        >>> formula.build("11.7e-6", "1000", "100")
        'of:=11.7e-6*1000*100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LINEAR_THERMAL_EXPANSION",
            category="mechanical_engineering",
            description="Calculate linear thermal expansion for components: DeltaL = alpha * L * DeltaT",
            arguments=(
                FormulaArgument(
                    name="cte",
                    type="number",
                    required=True,
                    description="Coefficient of thermal expansion (alpha) in 1/°C",
                ),
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Original length (L) in mm",
                ),
                FormulaArgument(
                    name="temp_change",
                    type="number",
                    required=True,
                    description="Temperature change (DeltaT) in °C",
                ),
            ),
            return_type="number",
            examples=(
                "=THERMAL_EXPANSION(11.7E-6; 1000; 100)  # 1.17 mm",
                "=THERMAL_EXPANSION(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: cte, length, temp_change

        Returns:
            ODF formula string: of:=cte*length*temp_change
        """
        self.validate_arguments(args)
        cte, length, temp_change = args
        return f"of:={cte}*{length}*{temp_change}"


@dataclass(slots=True, frozen=True)
class ThermalStressFormula(BaseFormula):
    """Thermal Stress formula: sigma = E * alpha * DeltaT.

    Calculates thermal stress in a constrained member given Young's modulus,
    coefficient of thermal expansion, and temperature change.

        THERMAL_STRESS formula

    Example:
        >>> formula = ThermalStressFormula()
        >>> formula.build("200000", "11.7e-6", "100")
        '200000*11.7e-6*100'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="THERMAL_STRESS",
            category="mechanical_engineering",
            description="Calculate thermal stress in constrained member: sigma = E * alpha * DeltaT",
            arguments=(
                FormulaArgument(
                    name="youngs_modulus",
                    type="number",
                    required=True,
                    description="Young's modulus (E) in MPa",
                ),
                FormulaArgument(
                    name="cte",
                    type="number",
                    required=True,
                    description="Coefficient of thermal expansion (alpha) in 1/°C",
                ),
                FormulaArgument(
                    name="temp_change",
                    type="number",
                    required=True,
                    description="Temperature change (DeltaT) in °C",
                ),
            ),
            return_type="number",
            examples=(
                "=THERMAL_STRESS(200000; 11.7E-6; 100)  # 234 MPa",
                "=THERMAL_STRESS(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: youngs_modulus, cte, temp_change

        Returns:
            ODF formula string: youngs_modulus*cte*temp_change
        """
        self.validate_arguments(args)
        youngs_modulus, cte, temp_change = args
        return f"of:={youngs_modulus}*{cte}*{temp_change}"


@dataclass(slots=True, frozen=True)
class ConvectionCoefficient(BaseFormula):
    """Convection Coefficient formula: h = Nu*k/L.

    Calculates heat transfer coefficient from Nusselt number.

        BATCH2-MECH: ConvectionCoefficient formula

    Example:
        >>> formula = ConvectionCoefficient()
        >>> formula.build("10", "0.6", "0.1")
        'of:=10*0.6/0.1'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="CONVECTION_COEFFICIENT",
            category="mechanical_engineering",
            description="Calculate heat transfer coefficient: h = Nu*k/L",
            arguments=(
                FormulaArgument(
                    name="nusselt",
                    type="number",
                    required=True,
                    description="Nusselt number (dimensionless)",
                ),
                FormulaArgument(
                    name="thermal_conductivity",
                    type="number",
                    required=True,
                    description="Thermal conductivity (W/m·K)",
                ),
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Characteristic length (m)",
                ),
            ),
            return_type="number",
            examples=(
                "=CONVECTION_COEFFICIENT(10; 0.6; 0.1)  # 60 W/m²·K",
                "=CONVECTION_COEFFICIENT(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: nusselt, thermal_conductivity, length

        Returns:
            ODF formula string: of:=nusselt*thermal_conductivity/length
        """
        self.validate_arguments(args)
        nusselt, thermal_conductivity, length = args
        return f"of:={nusselt}*{thermal_conductivity}/{length}"


@dataclass(slots=True, frozen=True)
class RadiationHeatTransfer(BaseFormula):
    """Radiation Heat Transfer formula: Q = epsilon*sigma*A*(T_s^4 - T_surr^4).

    Calculates radiative heat transfer using Stefan-Boltzmann law.

        BATCH2-MECH: RadiationHeatTransfer formula

    Example:
        >>> formula = RadiationHeatTransfer()
        >>> formula.build("0.9", "1.5", "400", "300")
        'of:=0.9*5.67e-8*1.5*(400^4-300^4)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="RADIATION_HEAT_TRANSFER",
            category="mechanical_engineering",
            description="Calculate radiative heat transfer: epsilon*sigma*A*(T_s^4 - T_surr^4)",
            arguments=(
                FormulaArgument(
                    name="emissivity",
                    type="number",
                    required=True,
                    description="Surface emissivity (dimensionless, 0-1)",
                ),
                FormulaArgument(
                    name="area",
                    type="number",
                    required=True,
                    description="Surface area (m²)",
                ),
                FormulaArgument(
                    name="temp_surface",
                    type="number",
                    required=True,
                    description="Surface temperature (K)",
                ),
                FormulaArgument(
                    name="temp_surroundings",
                    type="number",
                    required=True,
                    description="Surroundings temperature (K)",
                ),
            ),
            return_type="number",
            examples=(
                "=RADIATION_HEAT_TRANSFER(0.9; 1.5; 400; 300)  # Heat transfer in W",
                "=RADIATION_HEAT_TRANSFER(A2; B2; C2; D2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: emissivity, area, temp_surface, temp_surroundings

        Returns:
            ODF formula string: of:=emissivity*5.67e-8*area*(temp_surface^4-temp_surroundings^4)
        """
        self.validate_arguments(args)
        emissivity, area, temp_surface, temp_surroundings = args
        return (
            f"of:={emissivity}*5.67e-8*{area}*({temp_surface}^4-{temp_surroundings}^4)"
        )


@dataclass(slots=True, frozen=True)
class ThermalResistance(BaseFormula):
    """Thermal Resistance formula: R = L/(k*A).

    Calculates resistance to heat flow through a material.

        BATCH2-MECH: ThermalResistance formula

    Example:
        >>> formula = ThermalResistance()
        >>> formula.build("0.1", "0.5", "2")
        'of:=0.1/(0.5*2)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="THERMAL_RESISTANCE",
            category="mechanical_engineering",
            description="Calculate thermal resistance: R = L/(k*A)",
            arguments=(
                FormulaArgument(
                    name="thickness",
                    type="number",
                    required=True,
                    description="Material thickness (m)",
                ),
                FormulaArgument(
                    name="thermal_conductivity",
                    type="number",
                    required=True,
                    description="Thermal conductivity (W/m·K)",
                ),
                FormulaArgument(
                    name="area",
                    type="number",
                    required=True,
                    description="Cross-sectional area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=THERMAL_RESISTANCE(0.1; 0.5; 2)  # 0.1 K/W",
                "=THERMAL_RESISTANCE(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: thickness, thermal_conductivity, area

        Returns:
            ODF formula string: of:=thickness/(thermal_conductivity*area)
        """
        self.validate_arguments(args)
        thickness, thermal_conductivity, area = args
        return f"of:={thickness}/({thermal_conductivity}*{area})"


@dataclass(slots=True, frozen=True)
class LogMeanTempDiff(BaseFormula):
    """Log Mean Temperature Difference formula: LMTD = (deltaT1 - deltaT2)/ln(deltaT1/deltaT2).

    Calculates LMTD for heat exchanger design.

        BATCH2-MECH: LogMeanTempDiff formula

    Example:
        >>> formula = LogMeanTempDiff()
        >>> formula.build("50", "30")
        'of:=(50-30)/LN(50/30)'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="LOG_MEAN_TEMP_DIFF",
            category="mechanical_engineering",
            description="Calculate LMTD for heat exchangers: (deltaT1 - deltaT2)/ln(deltaT1/deltaT2)",
            arguments=(
                FormulaArgument(
                    name="delta_t1",
                    type="number",
                    required=True,
                    description="Temperature difference at end 1 (K or °C)",
                ),
                FormulaArgument(
                    name="delta_t2",
                    type="number",
                    required=True,
                    description="Temperature difference at end 2 (K or °C)",
                ),
            ),
            return_type="number",
            examples=(
                "=LOG_MEAN_TEMP_DIFF(50; 30)  # LMTD in K or °C",
                "=LOG_MEAN_TEMP_DIFF(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: delta_t1, delta_t2

        Returns:
            ODF formula string: of:=(delta_t1-delta_t2)/LN(delta_t1/delta_t2)
        """
        self.validate_arguments(args)
        delta_t1, delta_t2 = args
        return f"of:=({delta_t1}-{delta_t2})/LN({delta_t1}/{delta_t2})"


@dataclass(slots=True, frozen=True)
class FinEfficiency(BaseFormula):
    """Fin Efficiency formula: eta = tanh(mL)/(mL).

    Calculates extended surface efficiency for fins.

        BATCH2-MECH: FinEfficiency formula

    Example:
        >>> formula = FinEfficiency()
        >>> formula.build("0.9", "1.5")
        'of:=0.9/1.5'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="FIN_EFFICIENCY",
            category="mechanical_engineering",
            description="Calculate fin efficiency: eta = tanh(mL)/(mL)",
            arguments=(
                FormulaArgument(
                    name="tanh_ml",
                    type="number",
                    required=True,
                    description="Hyperbolic tangent of mL (dimensionless)",
                ),
                FormulaArgument(
                    name="ml",
                    type="number",
                    required=True,
                    description="Product of m and L (dimensionless)",
                ),
            ),
            return_type="number",
            examples=(
                "=FIN_EFFICIENCY(0.9; 1.5)  # Efficiency 0-1",
                "=FIN_EFFICIENCY(A2; B2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: tanh_ml, ml

        Returns:
            ODF formula string: of:=tanh_ml/ml
        """
        self.validate_arguments(args)
        tanh_ml, ml = args
        return f"of:={tanh_ml}/{ml}"


@dataclass(slots=True, frozen=True)
class NusseltNumber(BaseFormula):
    """Nusselt Number formula: Nu = h*L/k.

    Calculates Nusselt number for convection characterization.

        BATCH2-MECH: NusseltNumber formula

    Example:
        >>> formula = NusseltNumber()
        >>> formula.build("50", "0.1", "0.6")
        'of:=50*0.1/0.6'
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata."""
        return FormulaMetadata(
            name="NUSSELT_NUMBER",
            category="mechanical_engineering",
            description="Calculate Nusselt number: Nu = h*L/k",
            arguments=(
                FormulaArgument(
                    name="h_conv",
                    type="number",
                    required=True,
                    description="Convection heat transfer coefficient (W/m²·K)",
                ),
                FormulaArgument(
                    name="length",
                    type="number",
                    required=True,
                    description="Characteristic length (m)",
                ),
                FormulaArgument(
                    name="k_fluid",
                    type="number",
                    required=True,
                    description="Fluid thermal conductivity (W/m·K)",
                ),
            ),
            return_type="number",
            examples=(
                "=NUSSELT_NUMBER(50; 0.1; 0.6)  # Nu = 8.33",
                "=NUSSELT_NUMBER(A2; B2; C2)  # Using cell references",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ODF formula string.

        Args:
            *args: h_conv, length, k_fluid

        Returns:
            ODF formula string: of:=h_conv*length/k_fluid
        """
        self.validate_arguments(args)
        h_conv, length, k_fluid = args
        return f"of:={h_conv}*{length}/{k_fluid}"


__all__ = [
    "ConvectionCoefficient",
    "FinEfficiency",
    "LinearThermalExpansionFormula",
    "LogMeanTempDiff",
    "NusseltNumber",
    "RadiationHeatTransfer",
    "ThermalResistance",
    "ThermalStressFormula",
]
