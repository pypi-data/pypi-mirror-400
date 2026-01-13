"""Air quality formulas.

Air quality formulas
(AQI_CALCULATION, EMISSION_RATE, POLLUTION_INDEX)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spreadsheet_dl.domains.base import BaseFormula, FormulaArgument, FormulaMetadata


@dataclass(slots=True, frozen=True)
class AQICalculationFormula(BaseFormula):
    """Calculate Air Quality Index from pollutant concentration.

        AQI_CALCULATION formula for air quality

    Uses EPA AQI calculation methodology.

    Example:
        >>> formula = AQICalculationFormula()
        >>> result = formula.build("A1", "pm25")
        >>> # Returns AQI calculation formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for AQI_CALCULATION

            Formula metadata
        """
        return FormulaMetadata(
            name="AQI_CALCULATION",
            category="environmental",
            description="Calculate Air Quality Index from pollutant concentration",
            arguments=(
                FormulaArgument(
                    "concentration",
                    "number",
                    required=True,
                    description="Pollutant concentration (ug/m3 or ppb)",
                ),
                FormulaArgument(
                    "pollutant",
                    "text",
                    required=False,
                    description="Pollutant type: pm25, pm10, o3, no2, so2, co",
                    default="pm25",
                ),
            ),
            return_type="number",
            examples=(
                "=AQI_CALCULATION(35.5;pm25)",
                "=AQI_CALCULATION(concentration;pollutant_type)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build AQI_CALCULATION formula string.

        Args:
            *args: concentration, [pollutant]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            AQI_CALCULATION formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        concentration = args[0]
        # pollutant = str(args[1]).lower() if len(args) > 1 else "pm25"

        # Simplified AQI calculation for PM2.5:
        # AQI = ((IHi - ILo) / (BPHi - BPLo)) * (Cp - BPLo) + ILo
        # Using PM2.5 breakpoints for simplicity
        # This is a simplified linear interpolation
        return (
            f"of:=IF({concentration}<=12;{concentration}*4.166;"
            f"IF({concentration}<=35.4;50+({concentration}-12)*2.132;"
            f"IF({concentration}<=55.4;100+({concentration}-35.4)*2.5;"
            f"IF({concentration}<=150.4;150+({concentration}-55.4)*0.526;"
            f"IF({concentration}<=250.4;200+({concentration}-150.4)*0.5;"
            f"IF({concentration}<=350.4;300+({concentration}-250.4)*1;"
            f"400+({concentration}-350.4)*1))))))"
        )


@dataclass(slots=True, frozen=True)
class EmissionRateFormula(BaseFormula):
    """Calculate pollutant emission rate.

        EMISSION_RATE formula for emissions calculations

    Calculates mass emission rate from flow and concentration.

    Example:
        >>> formula = EmissionRateFormula()
        >>> result = formula.build("1000", "50")
        >>> # Returns: "1000*50/1000000"
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for EMISSION_RATE

            Formula metadata
        """
        return FormulaMetadata(
            name="EMISSION_RATE",
            category="environmental",
            description="Calculate pollutant emission rate (kg/hr)",
            arguments=(
                FormulaArgument(
                    "flow_rate",
                    "number",
                    required=True,
                    description="Flow rate (m3/hr)",
                ),
                FormulaArgument(
                    "concentration",
                    "number",
                    required=True,
                    description="Pollutant concentration (mg/m3)",
                ),
                FormulaArgument(
                    "efficiency",
                    "number",
                    required=False,
                    description="Control efficiency (0-1, optional)",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=EMISSION_RATE(1000;50)",
                "=EMISSION_RATE(flow;conc;0.95)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build EMISSION_RATE formula string.

        Args:
            *args: flow_rate, concentration, [efficiency]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            EMISSION_RATE formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        flow_rate = args[0]
        concentration = args[1]
        efficiency = args[2] if len(args) > 2 else 0

        # Emission rate = flow * concentration * (1 - efficiency) / 1000000
        # Convert mg/hr to kg/hr
        if efficiency and str(efficiency) != "0":
            return f"of:={flow_rate}*{concentration}*(1-{efficiency})/1000000"
        else:
            return f"of:={flow_rate}*{concentration}/1000000"


@dataclass(slots=True, frozen=True)
class PollutionIndexFormula(BaseFormula):
    """Calculate combined pollution index.

        POLLUTION_INDEX formula for multi-pollutant assessment

    Calculates a normalized pollution severity index.

    Example:
        >>> formula = PollutionIndexFormula()
        >>> result = formula.build("A1", "B1", "C1")
        >>> # Returns pollution index formula
    """

    @property
    def metadata(self) -> FormulaMetadata:
        """Get formula metadata.

        Returns:
            FormulaMetadata for POLLUTION_INDEX

            Formula metadata
        """
        return FormulaMetadata(
            name="POLLUTION_INDEX",
            category="environmental",
            description="Calculate combined pollution index from multiple pollutants",
            arguments=(
                FormulaArgument(
                    "pm25_aqi",
                    "number",
                    required=True,
                    description="PM2.5 AQI value",
                ),
                FormulaArgument(
                    "o3_aqi",
                    "number",
                    required=False,
                    description="Ozone AQI value",
                    default=0,
                ),
                FormulaArgument(
                    "no2_aqi",
                    "number",
                    required=False,
                    description="NO2 AQI value",
                    default=0,
                ),
            ),
            return_type="number",
            examples=(
                "=POLLUTION_INDEX(75)",
                "=POLLUTION_INDEX(pm25_aqi;o3_aqi;no2_aqi)",
            ),
        )

    def build(self, *args: Any, **kwargs: Any) -> str:
        """Build POLLUTION_INDEX formula string.

        Args:
            *args: pm25_aqi, [o3_aqi], [no2_aqi]
            **kwargs: Keyword arguments (optional)

        Returns:
            ODF formula string

            POLLUTION_INDEX formula building

        Raises:
            ValueError: If arguments are invalid
        """
        self.validate_arguments(args)

        pm25_aqi = args[0]
        o3_aqi = args[1] if len(args) > 1 else 0
        no2_aqi = args[2] if len(args) > 2 else 0

        # Combined index uses maximum pollutant (EPA method)
        # Plus weighted contribution from others
        if o3_aqi and no2_aqi and str(o3_aqi) != "0" and str(no2_aqi) != "0":
            return f"of:=MAX({pm25_aqi};{o3_aqi};{no2_aqi})+0.1*(({pm25_aqi}+{o3_aqi}+{no2_aqi})/3)"
        elif o3_aqi and str(o3_aqi) != "0":
            return f"of:=MAX({pm25_aqi};{o3_aqi})+0.1*(({pm25_aqi}+{o3_aqi})/2)"
        else:
            return f"of:={pm25_aqi}"


__all__ = [
    "AQICalculationFormula",
    "EmissionRateFormula",
    "PollutionIndexFormula",
]
