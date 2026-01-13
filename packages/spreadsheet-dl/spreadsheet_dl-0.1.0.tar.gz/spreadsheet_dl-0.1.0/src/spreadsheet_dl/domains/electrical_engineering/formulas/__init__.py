"""Electrical Engineering formulas for SpreadsheetDL.

    Electrical Engineering domain formulas

Provides domain-specific formulas for:
- Power calculations (dissipation, voltage drop, current)
- Impedance calculations (parallel/series resistance, capacitance, inductance)
- Signal analysis (SNR, bandwidth, rise time, propagation delay)
- Digital circuits (logic gates, binary conversions)
- Filter design (cutoff frequencies, Q factor, attenuation)
"""

from spreadsheet_dl.domains.electrical_engineering.formulas.ac_circuits import (
    ComplexImpedance,
    PowerFactor,
    Reactance,
    ResonantFrequency,
    RMSValue,
)
from spreadsheet_dl.domains.electrical_engineering.formulas.digital import (
    BinaryToDecimalFormula,
    DecimalToBinaryFormula,
    LogicNANDFormula,
    LogicNORFormula,
    LogicXORFormula,
)
from spreadsheet_dl.domains.electrical_engineering.formulas.filters import (
    BandPassCenterFormula,
    FilterAttenuationFormula,
    HighPassCutoffFormula,
    LowPassCutoffFormula,
    QFactorFormula,
)
from spreadsheet_dl.domains.electrical_engineering.formulas.impedance import (
    CapacitanceFormula,
    InductanceFormula,
    ParallelResistanceFormula,
    SeriesResistanceFormula,
)
from spreadsheet_dl.domains.electrical_engineering.formulas.power import (
    ComponentThermalResistanceFormula,
    CurrentCalcFormula,
    PowerDissipationFormula,
    VoltageDropFormula,
)
from spreadsheet_dl.domains.electrical_engineering.formulas.signal import (
    BandwidthFormula,
    PropagationDelayFormula,
    RiseTimeFormula,
    SignalToNoiseRatioFormula,
)

__all__ = [
    # Filter formulas
    "BandPassCenterFormula",
    # Signal formulas
    "BandwidthFormula",
    # Digital formulas
    "BinaryToDecimalFormula",
    "CapacitanceFormula",
    "ComplexImpedance",
    "ComponentThermalResistanceFormula",
    "CurrentCalcFormula",
    "DecimalToBinaryFormula",
    "FilterAttenuationFormula",
    "HighPassCutoffFormula",
    "InductanceFormula",
    "LogicNANDFormula",
    "LogicNORFormula",
    "LogicXORFormula",
    "LowPassCutoffFormula",
    # Impedance formulas
    "ParallelResistanceFormula",
    # Power formulas
    "PowerDissipationFormula",
    "PowerFactor",
    "PropagationDelayFormula",
    "QFactorFormula",
    "RMSValue",
    "Reactance",
    "ResonantFrequency",
    "RiseTimeFormula",
    "SeriesResistanceFormula",
    "SignalToNoiseRatioFormula",
    "VoltageDropFormula",
]
