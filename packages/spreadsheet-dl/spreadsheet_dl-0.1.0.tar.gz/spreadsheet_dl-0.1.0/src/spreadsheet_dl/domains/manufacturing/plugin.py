"""Manufacturing Domain Plugin for SpreadsheetDL.

    Manufacturing domain plugin
    PHASE-C: Domain plugin implementations

Provides manufacturing-specific functionality including:
- Production, quality, and inventory metrics formulas
- MES, ERP, and sensor data importers
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas
from spreadsheet_dl.domains.manufacturing.formulas.inventory import (
    EOQFormula,
    InventoryTurnoverFormula,
    ReorderPointFormula,
    SafetyStockFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.lean import (
    CycleTimeFormula as LeanCycleTimeFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.lean import (
    FlowEfficiencyFormula,
    KanbanCalculationFormula,
    LeadTimeFormula,
    LittlesLawFormula,
    ProcessCycleEfficiencyFormula,
    SingleMinuteExchangeFormula,
    TotalProductiveMaintenanceFormula,
    ValueStreamEfficiencyFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.lean import (
    TaktTimeFormula as LeanTaktTimeFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.production import (
    CapacityUtilizationFormula,
    CycleTimeFormula,
    TaktTimeFormula,
    ThroughputFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.quality import (
    ControlLimitsFormula,
    DefectRateFormula,
    FirstPassYieldFormula,
    ProcessCapabilityFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.six_sigma import (
    ControlLimitFormula,
    DPMOFormula,
    GaugeRnRFormula,
    ProcessCapabilityIndexFormula,
    ProcessPerformanceIndexFormula,
    ProcessSigmaFormula,
    SigmaLevelFormula,
    YieldCalculationFormula,
    ZScoreQualityFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.six_sigma import (
    DefectRateFormula as SixSigmaDefectRateFormula,
)
from spreadsheet_dl.domains.manufacturing.formulas.supply_chain import (
    ABCAnalysisFormula,
    BullwhipEffectFormula,
    CashConversionCycleFormula,
    NewsvendorModelFormula,
    ServiceLevelFormula,
)

# Import importers
from spreadsheet_dl.domains.manufacturing.importers.erp_data import ERPDataImporter
from spreadsheet_dl.domains.manufacturing.importers.mes_data import MESDataImporter
from spreadsheet_dl.domains.manufacturing.importers.sensor_data import (
    SensorDataImporter,
)


class ManufacturingDomainPlugin(BaseDomainPlugin):
    """Manufacturing domain plugin.

        Complete Manufacturing domain plugin
        PHASE-C: Domain plugin implementations

    Provides comprehensive manufacturing functionality for SpreadsheetDL
    with formulas and importers tailored for production planning,
    quality control, inventory management, lean manufacturing, Six Sigma,
    and supply chain optimization.

    Formulas (37 total):
        Production Metrics (4):
        - CYCLE_TIME: Production cycle time
        - TAKT_TIME: Takt time calculation
        - THROUGHPUT: Production throughput
        - CAPACITY_UTILIZATION: Capacity utilization rate

        Quality Metrics (4):
        - DEFECT_RATE: Defect rate calculation
        - FIRST_PASS_YIELD: First pass yield
        - PROCESS_CAPABILITY: Process capability index
        - CONTROL_LIMITS: SPC control limits

        Inventory Metrics (4):
        - EOQ: Economic order quantity
        - REORDER_POINT: Reorder point
        - SAFETY_STOCK: Safety stock level
        - INVENTORY_TURNOVER: Inventory turnover ratio

        Lean Manufacturing (10):
        - VALUE_STREAM_EFFICIENCY: Value stream efficiency
        - LEAN_LEAD_TIME: Lead time calculation
        - PROCESS_CYCLE_EFFICIENCY: Process cycle efficiency
        - LEAN_TAKT_TIME: Lean takt time
        - LEAN_CYCLE_TIME: Lean cycle time
        - TPM_AVAILABILITY: TPM availability
        - SMED_CHANGEOVER: SMED changeover time
        - KANBAN_QUANTITY: Kanban calculation
        - LITTLES_LAW: Little's Law (WIP)
        - FLOW_EFFICIENCY: Flow efficiency

        Six Sigma Quality (10):
        - DPMO: Defects per million opportunities
        - SIGMA_LEVEL: Sigma level from DPMO
        - CPK: Process capability index
        - PPK: Process performance index
        - RTY: Rolled throughput yield
        - SIX_SIGMA_DEFECT_RATE: Six Sigma defect rate
        - PROCESS_SIGMA: Process sigma calculation
        - CONTROL_LIMIT: Control limits with Z-score
        - Z_SCORE: Z-score for quality
        - GAUGE_RNR: Gauge R&R

        Supply Chain (5):
        - BULLWHIP_EFFECT: Bullwhip effect ratio
        - NEWSVENDOR_QUANTITY: Newsvendor model
        - ABC_SCORE: ABC analysis score
        - SERVICE_LEVEL: Service level / fill rate
        - CASH_CONVERSION_CYCLE: Cash conversion cycle

    Importers:
        - MESDataImporter: Manufacturing Execution System data
        - ERPDataImporter: Enterprise Resource Planning data
        - SensorDataImporter: IoT sensor data

    Example:
        >>> plugin = ManufacturingDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with manufacturing plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="manufacturing",
            version="0.1.0",
            description="Manufacturing formulas and importers for production planning and quality control",
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=("manufacturing", "production", "quality-control", "inventory", "oee"),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas and importers.

            Plugin initialization with all components

        Raises:
            Exception: If initialization fails
        """
        # Register production metrics formulas (4)
        self.register_formula("CYCLE_TIME", CycleTimeFormula)
        self.register_formula("TAKT_TIME", TaktTimeFormula)
        self.register_formula("THROUGHPUT", ThroughputFormula)
        self.register_formula("CAPACITY_UTILIZATION", CapacityUtilizationFormula)

        # Register quality metrics formulas (4)
        self.register_formula("DEFECT_RATE", DefectRateFormula)
        self.register_formula("FIRST_PASS_YIELD", FirstPassYieldFormula)
        self.register_formula("PROCESS_CAPABILITY", ProcessCapabilityFormula)
        self.register_formula("CONTROL_LIMITS", ControlLimitsFormula)

        # Register inventory metrics formulas (4)
        self.register_formula("EOQ", EOQFormula)
        self.register_formula("REORDER_POINT", ReorderPointFormula)
        self.register_formula("SAFETY_STOCK", SafetyStockFormula)
        self.register_formula("INVENTORY_TURNOVER", InventoryTurnoverFormula)

        # Register lean manufacturing formulas (10)
        self.register_formula("VALUE_STREAM_EFFICIENCY", ValueStreamEfficiencyFormula)
        self.register_formula("LEAN_LEAD_TIME", LeadTimeFormula)
        self.register_formula("PROCESS_CYCLE_EFFICIENCY", ProcessCycleEfficiencyFormula)
        self.register_formula("LEAN_TAKT_TIME", LeanTaktTimeFormula)
        self.register_formula("LEAN_CYCLE_TIME", LeanCycleTimeFormula)
        self.register_formula("TPM_AVAILABILITY", TotalProductiveMaintenanceFormula)
        self.register_formula("SMED_CHANGEOVER", SingleMinuteExchangeFormula)
        self.register_formula("KANBAN_QUANTITY", KanbanCalculationFormula)
        self.register_formula("LITTLES_LAW", LittlesLawFormula)
        self.register_formula("FLOW_EFFICIENCY", FlowEfficiencyFormula)

        # Register Six Sigma formulas (10)
        self.register_formula("DPMO", DPMOFormula)
        self.register_formula("SIGMA_LEVEL", SigmaLevelFormula)
        self.register_formula("CPK", ProcessCapabilityIndexFormula)
        self.register_formula("PPK", ProcessPerformanceIndexFormula)
        self.register_formula("RTY", YieldCalculationFormula)
        self.register_formula("SIX_SIGMA_DEFECT_RATE", SixSigmaDefectRateFormula)
        self.register_formula("PROCESS_SIGMA", ProcessSigmaFormula)
        self.register_formula("CONTROL_LIMIT", ControlLimitFormula)
        self.register_formula("Z_SCORE", ZScoreQualityFormula)
        self.register_formula("GAUGE_RNR", GaugeRnRFormula)

        # Register supply chain formulas (5)
        self.register_formula("BULLWHIP_EFFECT", BullwhipEffectFormula)
        self.register_formula("NEWSVENDOR_QUANTITY", NewsvendorModelFormula)
        self.register_formula("ABC_SCORE", ABCAnalysisFormula)
        self.register_formula("SERVICE_LEVEL", ServiceLevelFormula)
        self.register_formula("CASH_CONVERSION_CYCLE", CashConversionCycleFormula)

        # Register importers (3 total)
        self.register_importer("mes_data", MESDataImporter)
        self.register_importer("erp_data", ERPDataImporter)
        self.register_importer("sensor_data", SensorDataImporter)

    def cleanup(self) -> None:
        """Cleanup plugin resources.

        No resources need explicit cleanup for this plugin.

            Plugin cleanup method
        """
        pass

    def validate(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if plugin has required formulas and importers registered

            Plugin validation
        """
        required_formulas = 37  # 4 production + 4 quality + 4 inventory + 10 lean + 10 six_sigma + 5 supply_chain
        required_importers = 3

        return (
            len(self._formulas) >= required_formulas
            and len(self._importers) >= required_importers
        )


__all__ = [
    "ManufacturingDomainPlugin",
]
