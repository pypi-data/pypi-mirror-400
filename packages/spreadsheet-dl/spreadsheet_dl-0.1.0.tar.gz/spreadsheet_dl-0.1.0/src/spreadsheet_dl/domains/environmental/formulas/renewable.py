"""Renewable energy formulas.

Renewable energy formulas for solar, wind, and energy analysis
(SOLAR_PANEL_OUTPUT, WIND_TURBINE_POWER, ENERGY_PAYBACK_TIME,
CAPACITY_FACTOR, LEVELIZED_COST_ENERGY, ENERGY_RETURN_INVESTMENT)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class SolarPanelOutputFormula(BaseFormula):
    """Calculate solar panel power output.

        SOLAR_PANEL_OUTPUT formula for PV power generation

    Calculates power output from irradiance, area, and efficiency.

    Example:
        >>> formula = SolarPanelOutputFormula()
        >>> result = formula.build("1000", "1.6", "0.18")
        >>> # Returns: "1000*1.6*0.18"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SOLAR_PANEL_OUTPUT

            Formula metadata
        """
        return FormulaMetadata(
            name="SOLAR_PANEL_OUTPUT",
            category="environmental",
            description="Calculate solar panel power output (watts)",
            arguments=(
                FormulaArgument(
                    "irradiance",
                    "number",
                    required=True,
                    description="Solar irradiance (W/m2)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Panel area (m2)",
                ),
                FormulaArgument(
                    "efficiency",
                    "number",
                    required=True,
                    description="Panel efficiency (0-1)",
                ),
            ),
            return_type="number",
            examples=(
                "=SOLAR_PANEL_OUTPUT(1000;1.6;0.18)",
                "=SOLAR_PANEL_OUTPUT(irradiance;area;efficiency)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SOLAR_PANEL_OUTPUT formula string.

        Args:
            *args: irradiance, area, efficiency
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SOLAR_PANEL_OUTPUT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        irradiance = args[0]
        area = args[1]
        efficiency = args[2]

        # Power = irradiance * area * efficiency
        return f"of:={irradiance}*{area}*{efficiency}"


@dataclass(slots=True, frozen=True)
class WindTurbinePowerFormula(BaseFormula):
    """Calculate wind turbine power output.

        WIND_TURBINE_POWER formula for wind energy capture

    Calculates power from air density, swept area, velocity, and power coefficient.

    Example:
        >>> formula = WindTurbinePowerFormula()
        >>> result = formula.build("1.225", "2827", "12", "0.4")
        >>> # Returns: "0.5*1.225*2827*12^3*0.4"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WIND_TURBINE_POWER

            Formula metadata
        """
        return FormulaMetadata(
            name="WIND_TURBINE_POWER",
            category="environmental",
            description="Calculate wind turbine power output (watts)",
            arguments=(
                FormulaArgument(
                    "air_density",
                    "number",
                    required=True,
                    description="Air density (kg/m3)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Swept area (m2)",
                ),
                FormulaArgument(
                    "velocity",
                    "number",
                    required=True,
                    description="Wind velocity (m/s)",
                ),
                FormulaArgument(
                    "power_coeff",
                    "number",
                    required=True,
                    description="Power coefficient (0-0.593)",
                ),
            ),
            return_type="number",
            examples=(
                "=WIND_TURBINE_POWER(1.225;2827;12;0.4)",
                "=WIND_TURBINE_POWER(density;area;velocity;cp)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WIND_TURBINE_POWER formula string.

        Args:
            *args: air_density, area, velocity, power_coeff
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            WIND_TURBINE_POWER formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        air_density = args[0]
        area = args[1]
        velocity = args[2]
        power_coeff = args[3]

        # Power = 0.5 * density * area * velocity^3 * cp
        return f"of:=0.5*{air_density}*{area}*{velocity}^3*{power_coeff}"


@dataclass(slots=True, frozen=True)
class EnergyPaybackTimeFormula(BaseFormula):
    """Calculate energy payback time.

        ENERGY_PAYBACK_TIME formula for EPBT calculation

    Calculates time to recover energy investment.

    Example:
        >>> formula = EnergyPaybackTimeFormula()
        >>> result = formula.build("50000", "2500")
        >>> # Returns: "50000/2500"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ENERGY_PAYBACK_TIME

            Formula metadata
        """
        return FormulaMetadata(
            name="ENERGY_PAYBACK_TIME",
            category="environmental",
            description="Calculate energy payback time for renewable systems (years)",
            arguments=(
                FormulaArgument(
                    "energy_input",
                    "number",
                    required=True,
                    description="Total energy input for manufacturing (kWh)",
                ),
                FormulaArgument(
                    "annual_output",
                    "number",
                    required=True,
                    description="Annual energy output (kWh/year)",
                ),
            ),
            return_type="number",
            examples=(
                "=ENERGY_PAYBACK_TIME(50000;2500)",
                "=ENERGY_PAYBACK_TIME(input_energy;annual_output)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENERGY_PAYBACK_TIME formula string.

        Args:
            *args: energy_input, annual_output
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ENERGY_PAYBACK_TIME formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        energy_input = args[0]
        annual_output = args[1]

        # EPBT = energy_input / annual_output
        return f"of:={energy_input}/{annual_output}"


@dataclass(slots=True, frozen=True)
class CapacityFactorFormula(BaseFormula):
    """Calculate capacity factor for renewable energy.

        CAPACITY_FACTOR formula for generation efficiency

    Calculates ratio of actual output to maximum possible output.

    Example:
        >>> formula = CapacityFactorFormula()
        >>> result = formula.build("175200", "1000", "8760")
        >>> # Returns: "175200/(1000*8760)"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CAPACITY_FACTOR

            Formula metadata
        """
        return FormulaMetadata(
            name="CAPACITY_FACTOR",
            category="environmental",
            description="Calculate capacity factor for renewable energy (0-1)",
            arguments=(
                FormulaArgument(
                    "actual_output",
                    "number",
                    required=True,
                    description="Actual energy output (kWh)",
                ),
                FormulaArgument(
                    "rated_capacity",
                    "number",
                    required=True,
                    description="Rated capacity (kW)",
                ),
                FormulaArgument(
                    "time_period",
                    "number",
                    required=True,
                    description="Time period (hours)",
                ),
            ),
            return_type="number",
            examples=(
                "=CAPACITY_FACTOR(175200;1000;8760)",
                "=CAPACITY_FACTOR(actual;rated;hours)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CAPACITY_FACTOR formula string.

        Args:
            *args: actual_output, rated_capacity, time_period
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CAPACITY_FACTOR formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual_output = args[0]
        rated_capacity = args[1]
        time_period = args[2]

        # CF = actual_output / (rated_capacity * time_period)
        return f"of:={actual_output}/({rated_capacity}*{time_period})"


@dataclass(slots=True, frozen=True)
class LevelizedCostEnergyFormula(BaseFormula):
    """Calculate levelized cost of energy (LCOE).

        LEVELIZED_COST_ENERGY formula for LCOE calculation

    Calculates lifecycle cost per unit of energy produced (simplified).

    Example:
        >>> formula = LevelizedCostEnergyFormula()
        >>> result = formula.build("1000000", "50000", "100000", "25", "0.05")
        >>> # Returns LCOE calculation with NPV
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for LEVELIZED_COST_ENERGY

            Formula metadata
        """
        return FormulaMetadata(
            name="LEVELIZED_COST_ENERGY",
            category="environmental",
            description="Calculate levelized cost of energy ($/kWh, simplified)",
            arguments=(
                FormulaArgument(
                    "capex",
                    "number",
                    required=True,
                    description="Capital expenditure ($)",
                ),
                FormulaArgument(
                    "opex_annual",
                    "number",
                    required=True,
                    description="Annual operating expenses ($)",
                ),
                FormulaArgument(
                    "energy_annual",
                    "number",
                    required=True,
                    description="Annual energy production (kWh)",
                ),
                FormulaArgument(
                    "lifetime",
                    "number",
                    required=True,
                    description="System lifetime (years)",
                ),
                FormulaArgument(
                    "discount_rate",
                    "number",
                    required=True,
                    description="Discount rate (0-1)",
                ),
            ),
            return_type="number",
            examples=(
                "=LEVELIZED_COST_ENERGY(1000000;50000;100000;25;0.05)",
                "=LEVELIZED_COST_ENERGY(capex;opex;energy;life;rate)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build LEVELIZED_COST_ENERGY formula string.

        Args:
            *args: capex, opex_annual, energy_annual, lifetime, discount_rate
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            LEVELIZED_COST_ENERGY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        capex = args[0]
        opex_annual = args[1]
        energy_annual = args[2]
        lifetime = args[3]
        discount_rate = args[4]

        # Simplified LCOE = (CAPEX + NPV of OPEX) / NPV of Energy
        # Using SEQUENCE for years 1 to lifetime
        # NPV = SUM(cashflow / (1 + r)^t)
        opex_npv = f"SUMPRODUCT({opex_annual}/(1+{discount_rate})^SEQUENCE({lifetime}))"
        energy_npv = (
            f"SUMPRODUCT({energy_annual}/(1+{discount_rate})^SEQUENCE({lifetime}))"
        )

        return f"of:=({capex}+{opex_npv})/({energy_npv})"


@dataclass(slots=True, frozen=True)
class EnergyReturnInvestmentFormula(BaseFormula):
    """Calculate Energy Return on Investment (EROI).

        ENERGY_RETURN_INVESTMENT formula for EROI ratio

    Calculates ratio of energy produced to energy consumed
    over system lifetime.

    Example:
        >>> formula = EnergyReturnInvestmentFormula()
        >>> result = formula.build("500000", "50000")
        >>> # Returns: "500000/50000"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for ENERGY_RETURN_INVESTMENT

            Formula metadata
        """
        return FormulaMetadata(
            name="ENERGY_RETURN_INVESTMENT",
            category="environmental",
            description="Calculate Energy Return on Investment (EROI ratio)",
            arguments=(
                FormulaArgument(
                    "energy_output",
                    "number",
                    required=True,
                    description="Total lifetime energy output (kWh)",
                ),
                FormulaArgument(
                    "energy_input",
                    "number",
                    required=True,
                    description="Total energy input for system (kWh)",
                ),
            ),
            return_type="number",
            examples=(
                "=ENERGY_RETURN_INVESTMENT(500000;50000)",
                "=ENERGY_RETURN_INVESTMENT(output;input)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build ENERGY_RETURN_INVESTMENT formula string.

        Args:
            *args: energy_output, energy_input
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            ENERGY_RETURN_INVESTMENT formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        energy_output = args[0]
        energy_input = args[1]

        # EROI = energy_output / energy_input
        return f"of:={energy_output}/{energy_input}"


@dataclass(slots=True, frozen=True)
class SolarPanelEfficiencyFormula(BaseFormula):
    """Calculate solar panel conversion efficiency.

        SOLAR_PANEL_EFFICIENCY formula for PV efficiency

    Calculates the percentage of solar irradiance converted to electricity.

    Example:
        >>> formula = SolarPanelEfficiencyFormula()
        >>> result = formula.build("300", "1000", "2")
        >>> # Returns: "300/(1000*2)*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for SOLAR_PANEL_EFFICIENCY

            Formula metadata
        """
        return FormulaMetadata(
            name="SOLAR_PANEL_EFFICIENCY",
            category="environmental",
            description="Calculate solar panel conversion efficiency (%)",
            arguments=(
                FormulaArgument(
                    "power_output",
                    "number",
                    required=True,
                    description="Actual power output (W)",
                ),
                FormulaArgument(
                    "irradiance",
                    "number",
                    required=True,
                    description="Solar irradiance (W/m²)",
                ),
                FormulaArgument(
                    "area",
                    "number",
                    required=True,
                    description="Panel area (m²)",
                ),
            ),
            return_type="number",
            examples=(
                "=SOLAR_PANEL_EFFICIENCY(300;1000;2)",
                "=SOLAR_PANEL_EFFICIENCY(power;irradiance;area)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build SOLAR_PANEL_EFFICIENCY formula string.

        Args:
            *args: power_output, irradiance, area
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            SOLAR_PANEL_EFFICIENCY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        power_output = args[0]
        irradiance = args[1]
        area = args[2]

        # Efficiency = Power_out / (Irradiance * Area) * 100
        return f"of:={power_output}/({irradiance}*{area})*100"


@dataclass(slots=True, frozen=True)
class WindCapacityFactorFormula(BaseFormula):
    """Calculate wind turbine capacity factor.

        WIND_CAPACITY_FACTOR formula for turbine utilization

    Calculates the ratio of actual energy output to theoretical maximum.

    Example:
        >>> formula = WindCapacityFactorFormula()
        >>> result = formula.build("8760000", "2000", "8760")
        >>> # Returns: "8760000/(2000*8760)*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for WIND_CAPACITY_FACTOR

            Formula metadata
        """
        return FormulaMetadata(
            name="WIND_CAPACITY_FACTOR",
            category="environmental",
            description="Calculate wind turbine capacity factor (%)",
            arguments=(
                FormulaArgument(
                    "actual_energy",
                    "number",
                    required=True,
                    description="Actual energy produced (kWh)",
                ),
                FormulaArgument(
                    "rated_capacity",
                    "number",
                    required=True,
                    description="Rated capacity (kW)",
                ),
                FormulaArgument(
                    "hours",
                    "number",
                    required=True,
                    description="Time period (hours)",
                ),
            ),
            return_type="number",
            examples=(
                "=WIND_CAPACITY_FACTOR(8760000;2000;8760)",
                "=WIND_CAPACITY_FACTOR(actual;rated;hours)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build WIND_CAPACITY_FACTOR formula string.

        Args:
            *args: actual_energy, rated_capacity, hours
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            WIND_CAPACITY_FACTOR formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        actual_energy = args[0]
        rated_capacity = args[1]
        hours = args[2]

        # Capacity Factor = Actual / (Rated * Hours) * 100
        return f"of:={actual_energy}/({rated_capacity}*{hours})*100"


@dataclass(slots=True, frozen=True)
class BatteryStorageCapacityFormula(BaseFormula):
    """Calculate required battery storage capacity.

        BATTERY_STORAGE_CAPACITY formula for energy storage sizing

    Calculates battery capacity needed for specified autonomy.

    Example:
        >>> formula = BatteryStorageCapacityFormula()
        >>> result = formula.build("50", "3", "0.8")
        >>> # Returns: "(50*3)/0.8"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for BATTERY_STORAGE_CAPACITY

            Formula metadata
        """
        return FormulaMetadata(
            name="BATTERY_STORAGE_CAPACITY",
            category="environmental",
            description="Calculate required battery storage capacity (kWh)",
            arguments=(
                FormulaArgument(
                    "daily_demand",
                    "number",
                    required=True,
                    description="Daily energy demand (kWh/day)",
                ),
                FormulaArgument(
                    "autonomy_days",
                    "number",
                    required=True,
                    description="Days of autonomy required",
                ),
                FormulaArgument(
                    "depth_discharge",
                    "number",
                    required=True,
                    description="Depth of discharge (0-1, e.g., 0.8 for 80%)",
                ),
            ),
            return_type="number",
            examples=(
                "=BATTERY_STORAGE_CAPACITY(50;3;0.8)",
                "=BATTERY_STORAGE_CAPACITY(demand;days;dod)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build BATTERY_STORAGE_CAPACITY formula string.

        Args:
            *args: daily_demand, autonomy_days, depth_discharge
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            BATTERY_STORAGE_CAPACITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        daily_demand = args[0]
        autonomy_days = args[1]
        depth_discharge = args[2]

        # Capacity = (Daily_Demand * Autonomy_Days) / Depth_of_Discharge
        return f"of:=({daily_demand}*{autonomy_days})/{depth_discharge}"


@dataclass(slots=True, frozen=True)
class GridStabilityIndexFormula(BaseFormula):
    """Calculate grid stability with renewable penetration.

        GRID_STABILITY_INDEX formula for renewable integration

    Calculates grid stability metric accounting for renewables and storage.

    Example:
        >>> formula = GridStabilityIndexFormula()
        >>> result = formula.build("500", "1000", "100")
        >>> # Returns: "(500+100)/1000*100"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for GRID_STABILITY_INDEX

            Formula metadata
        """
        return FormulaMetadata(
            name="GRID_STABILITY_INDEX",
            category="environmental",
            description="Calculate grid renewable stability index (%)",
            arguments=(
                FormulaArgument(
                    "renewable_capacity",
                    "number",
                    required=True,
                    description="Renewable generation capacity (MW)",
                ),
                FormulaArgument(
                    "total_capacity",
                    "number",
                    required=True,
                    description="Total grid capacity (MW)",
                ),
                FormulaArgument(
                    "storage_capacity",
                    "number",
                    required=True,
                    description="Energy storage capacity (MW)",
                ),
            ),
            return_type="number",
            examples=(
                "=GRID_STABILITY_INDEX(500;1000;100)",
                "=GRID_STABILITY_INDEX(renewable;total;storage)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build GRID_STABILITY_INDEX formula string.

        Args:
            *args: renewable_capacity, total_capacity, storage_capacity
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            GRID_STABILITY_INDEX formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        renewable_capacity = args[0]
        total_capacity = args[1]
        storage_capacity = args[2]

        # Stability Index = (Renewable + Storage) / Total * 100
        return f"of:=({renewable_capacity}+{storage_capacity})/{total_capacity}*100"


@dataclass(slots=True, frozen=True)
class CarbonIntensityFormula(BaseFormula):
    """Calculate carbon intensity of energy production.

        CARBON_INTENSITY formula for emissions per energy

    Calculates grams of CO2 emitted per kilowatt-hour of energy produced.

    Example:
        >>> formula = CarbonIntensityFormula()
        >>> result = formula.build("500000", "1000000")
        >>> # Returns: "500000/1000000*1000"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for CARBON_INTENSITY

            Formula metadata
        """
        return FormulaMetadata(
            name="CARBON_INTENSITY",
            category="environmental",
            description="Calculate carbon intensity (gCO2/kWh)",
            arguments=(
                FormulaArgument(
                    "co2_emissions",
                    "number",
                    required=True,
                    description="Total CO2 emissions (kg or tonnes)",
                ),
                FormulaArgument(
                    "energy_produced",
                    "number",
                    required=True,
                    description="Total energy produced (kWh)",
                ),
            ),
            return_type="number",
            examples=(
                "=CARBON_INTENSITY(500000;1000000)",
                "=CARBON_INTENSITY(co2;energy)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build CARBON_INTENSITY formula string.

        Args:
            *args: co2_emissions, energy_produced
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            CARBON_INTENSITY formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        co2_emissions = args[0]
        energy_produced = args[1]

        # Carbon Intensity = CO2 / Energy * 1000 (convert kg to g)
        return f"of:={co2_emissions}/{energy_produced}*1000"


__all__ = [
    "BatteryStorageCapacityFormula",
    "CapacityFactorFormula",
    "CarbonIntensityFormula",
    "EnergyPaybackTimeFormula",
    "EnergyReturnInvestmentFormula",
    "GridStabilityIndexFormula",
    "LevelizedCostEnergyFormula",
    "SolarPanelEfficiencyFormula",
    "SolarPanelOutputFormula",
    "WindCapacityFactorFormula",
    "WindTurbinePowerFormula",
]
