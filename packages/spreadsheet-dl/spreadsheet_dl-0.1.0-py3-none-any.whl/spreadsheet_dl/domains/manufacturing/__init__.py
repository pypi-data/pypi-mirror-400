"""Manufacturing Domain Plugin for SpreadsheetDL.

    Complete Manufacturing domain plugin
    PHASE-C: Domain plugin implementations

Provides comprehensive manufacturing-specific functionality including:
- Production metrics formulas (cycle time, takt time, throughput, capacity)
- Quality metrics formulas (defect rate, FPY, Cp/Cpk, control limits)
- Inventory formulas (EOQ, reorder point, safety stock, turnover)
- MES, ERP, and sensor data importers

Example:
    >>> from spreadsheet_dl.domains.manufacturing import ManufacturingDomainPlugin
    >>> plugin = ManufacturingDomainPlugin()
    >>> plugin.initialize()
"""

# Plugin
# Formulas - Inventory
from spreadsheet_dl.domains.manufacturing.formulas.inventory import (
    EOQFormula,
    InventoryTurnoverFormula,
    ReorderPointFormula,
    SafetyStockFormula,
)

# Formulas - Production
from spreadsheet_dl.domains.manufacturing.formulas.production import (
    CapacityUtilizationFormula,
    CycleTimeFormula,
    TaktTimeFormula,
    ThroughputFormula,
)

# Formulas - Quality
from spreadsheet_dl.domains.manufacturing.formulas.quality import (
    ControlLimitsFormula,
    DefectRateFormula,
    FirstPassYieldFormula,
    ProcessCapabilityFormula,
)

# Importers
from spreadsheet_dl.domains.manufacturing.importers import (
    ERPDataImporter,
    MESDataImporter,
    SensorDataImporter,
)
from spreadsheet_dl.domains.manufacturing.plugin import ManufacturingDomainPlugin

# Utils
from spreadsheet_dl.domains.manufacturing.utils import (
    calculate_cycle_time,
    calculate_defect_rate,
    calculate_eoq,
    calculate_first_pass_yield,
    calculate_oee,
    calculate_reorder_point,
    calculate_safety_stock,
    calculate_takt_time,
    format_manufacturing_number,
    parse_manufacturing_date,
)

__all__ = [
    # Formulas - Production
    "CapacityUtilizationFormula",
    # Formulas - Quality
    "ControlLimitsFormula",
    "CycleTimeFormula",
    "DefectRateFormula",
    # Formulas - Inventory
    "EOQFormula",
    # Importers
    "ERPDataImporter",
    "FirstPassYieldFormula",
    "InventoryTurnoverFormula",
    "MESDataImporter",
    # Plugin
    "ManufacturingDomainPlugin",
    "ProcessCapabilityFormula",
    "ReorderPointFormula",
    "SafetyStockFormula",
    "SensorDataImporter",
    "TaktTimeFormula",
    "ThroughputFormula",
    # Utils
    "calculate_cycle_time",
    "calculate_defect_rate",
    "calculate_eoq",
    "calculate_first_pass_yield",
    "calculate_oee",
    "calculate_reorder_point",
    "calculate_safety_stock",
    "calculate_takt_time",
    "format_manufacturing_number",
    "parse_manufacturing_date",
]
