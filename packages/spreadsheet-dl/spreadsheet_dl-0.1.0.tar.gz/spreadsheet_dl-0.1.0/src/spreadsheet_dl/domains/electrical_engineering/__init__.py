"""Electrical Engineering Domain Plugin for SpreadsheetDL.

    Electrical Engineering domain plugin
    PHASE-C: Domain plugin implementations

Provides comprehensive electrical engineering functionality including:
- Power, impedance, and signal calculation formulas
- Digital circuits and filter design formulas
- KiCad, Eagle, and generic component importers

Example:
    >>> from spreadsheet_dl.domains.electrical_engineering import (
    ...     ElectricalEngineeringDomainPlugin,
    ...     PowerDissipationFormula,
    ... )
    >>>
    >>> plugin = ElectricalEngineeringDomainPlugin()
    >>> plugin.initialize()
"""

# Plugin
# Formulas - Digital
from spreadsheet_dl.domains.electrical_engineering.formulas.digital import (
    BinaryToDecimalFormula,
    DecimalToBinaryFormula,
    LogicNANDFormula,
    LogicNORFormula,
    LogicXORFormula,
)

# Formulas - Filters
from spreadsheet_dl.domains.electrical_engineering.formulas.filters import (
    BandPassCenterFormula,
    FilterAttenuationFormula,
    HighPassCutoffFormula,
    LowPassCutoffFormula,
    QFactorFormula,
)

# Formulas - Impedance
from spreadsheet_dl.domains.electrical_engineering.formulas.impedance import (
    CapacitanceFormula,
    InductanceFormula,
    ParallelResistanceFormula,
    SeriesResistanceFormula,
)

# Formulas - Power
from spreadsheet_dl.domains.electrical_engineering.formulas.power import (
    ComponentThermalResistanceFormula,
    CurrentCalcFormula,
    PowerDissipationFormula,
    VoltageDropFormula,
)

# Formulas - Signal
from spreadsheet_dl.domains.electrical_engineering.formulas.signal import (
    BandwidthFormula,
    PropagationDelayFormula,
    RiseTimeFormula,
    SignalToNoiseRatioFormula,
)

# Importers
from spreadsheet_dl.domains.electrical_engineering.importers.component_csv import (
    GenericComponentCSVImporter,
)
from spreadsheet_dl.domains.electrical_engineering.importers.eagle_bom import (
    EagleBOMImporter,
)
from spreadsheet_dl.domains.electrical_engineering.importers.kicad_bom import (
    KiCadBOMImporter,
    KiCadComponent,
)
from spreadsheet_dl.domains.electrical_engineering.plugin import (
    ElectricalEngineeringDomainPlugin,
)

__all__ = [
    # Formulas - Filters
    "BandPassCenterFormula",
    # Formulas - Signal
    "BandwidthFormula",
    # Formulas - Digital
    "BinaryToDecimalFormula",
    # Formulas - Impedance
    "CapacitanceFormula",
    "ComponentThermalResistanceFormula",
    # Formulas - Power
    "CurrentCalcFormula",
    "DecimalToBinaryFormula",
    # Importers
    "EagleBOMImporter",
    # Plugin
    "ElectricalEngineeringDomainPlugin",
    "FilterAttenuationFormula",
    "GenericComponentCSVImporter",
    "HighPassCutoffFormula",
    "InductanceFormula",
    "KiCadBOMImporter",
    "KiCadComponent",
    "LogicNANDFormula",
    "LogicNORFormula",
    "LogicXORFormula",
    "LowPassCutoffFormula",
    "ParallelResistanceFormula",
    "PowerDissipationFormula",
    "PropagationDelayFormula",
    "QFactorFormula",
    "RiseTimeFormula",
    "SeriesResistanceFormula",
    "SignalToNoiseRatioFormula",
    "VoltageDropFormula",
]
