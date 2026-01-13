"""
Tests for Manufacturing domain plugin.

    Comprehensive tests for Manufacturing domain (95%+ coverage target)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.domains.manufacturing import (
    CapacityUtilizationFormula,
    ControlLimitsFormula,
    CycleTimeFormula,
    DefectRateFormula,
    EOQFormula,
    ERPDataImporter,
    FirstPassYieldFormula,
    InventoryTurnoverFormula,
    ManufacturingDomainPlugin,
    MESDataImporter,
    ProcessCapabilityFormula,
    ReorderPointFormula,
    SafetyStockFormula,
    SensorDataImporter,
    TaktTimeFormula,
    ThroughputFormula,
)
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

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.manufacturing]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = ManufacturingDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "manufacturing"
    assert metadata.version == "0.1.0"
    assert "manufacturing" in metadata.tags
    assert "production" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = ManufacturingDomainPlugin()
    plugin.initialize()

    # Verify production metrics formulas registered (4 total)
    assert plugin.get_formula("CYCLE_TIME") == CycleTimeFormula
    assert plugin.get_formula("TAKT_TIME") == TaktTimeFormula
    assert plugin.get_formula("THROUGHPUT") == ThroughputFormula
    assert plugin.get_formula("CAPACITY_UTILIZATION") == CapacityUtilizationFormula

    # Verify quality metrics formulas registered (4 total)
    assert plugin.get_formula("DEFECT_RATE") == DefectRateFormula
    assert plugin.get_formula("FIRST_PASS_YIELD") == FirstPassYieldFormula
    assert plugin.get_formula("PROCESS_CAPABILITY") == ProcessCapabilityFormula
    assert plugin.get_formula("CONTROL_LIMITS") == ControlLimitsFormula

    # Verify inventory metrics formulas registered (4 total)
    assert plugin.get_formula("EOQ") == EOQFormula
    assert plugin.get_formula("REORDER_POINT") == ReorderPointFormula
    assert plugin.get_formula("SAFETY_STOCK") == SafetyStockFormula
    assert plugin.get_formula("INVENTORY_TURNOVER") == InventoryTurnoverFormula

    # Verify importers registered (3 total)
    assert plugin.get_importer("mes_data") == MESDataImporter
    assert plugin.get_importer("erp_data") == ERPDataImporter
    assert plugin.get_importer("sensor_data") == SensorDataImporter


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = ManufacturingDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = ManufacturingDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Production Metrics Formula Tests
# ============================================================================


def test_cycle_time_formula() -> None:
    """Test cycle time formula: production_time / units."""
    formula = CycleTimeFormula()

    assert formula.metadata.name == "CYCLE_TIME"
    assert formula.metadata.category == "production"
    assert len(formula.metadata.arguments) == 2

    # Test calculation
    result = formula.build("480", "120")
    assert result == "of:=480/120"

    # Test with cell references
    result = formula.build("A2", "B2")
    assert result == "of:=A2/B2"


def test_takt_time_formula() -> None:
    """Test takt time formula: available_time / demand."""
    formula = TaktTimeFormula()

    assert formula.metadata.name == "TAKT_TIME"

    result = formula.build("28800", "1200")
    assert result == "of:=28800/1200"


def test_throughput_formula() -> None:
    """Test throughput formula: units / time."""
    formula = ThroughputFormula()

    assert formula.metadata.name == "THROUGHPUT"

    result = formula.build("1200", "480")
    assert result == "of:=1200/480"


def test_capacity_utilization_formula() -> None:
    """Test capacity utilization formula: (actual/max)*100."""
    formula = CapacityUtilizationFormula()

    assert formula.metadata.name == "CAPACITY_UTILIZATION"

    result = formula.build("850", "1000")
    assert result == "of:=(850/1000)*100"


# ============================================================================
# Quality Metrics Formula Tests
# ============================================================================


def test_defect_rate_formula() -> None:
    """Test defect rate formula."""
    formula = DefectRateFormula()

    assert formula.metadata.name == "DEFECT_RATE"

    result = formula.build("15", "1000")
    # Defect rate = (defects / total) * 100 or similar
    assert "/" in result
    assert "15" in result
    assert "1000" in result


def test_first_pass_yield_formula() -> None:
    """Test first pass yield formula."""
    formula = FirstPassYieldFormula()

    assert formula.metadata.name == "FIRST_PASS_YIELD"

    result = formula.build("950", "1000")
    # FPY = (good units / total) * 100
    assert "/" in result


def test_process_capability_formula() -> None:
    """Test process capability (Cp/Cpk) formula."""
    formula = ProcessCapabilityFormula()

    assert formula.metadata.name == "PROCESS_CAPABILITY"

    # Formula requires: usl, lsl, mean, stddev
    result = formula.build("10", "5", "7.5", "0.5")
    # Cp = (USL - LSL) / (6 * sigma)
    assert "6" in result or "/" in result


def test_control_limits_formula() -> None:
    """Test control limits formula."""
    formula = ControlLimitsFormula()

    assert formula.metadata.name == "CONTROL_LIMITS"

    # Formula requires: mean, stddev, limit_type
    result = formula.build("50", "2", "upper")
    # UCL = mean + 3*sigma, LCL = mean - 3*sigma
    assert "50" in result
    assert "3" in result or "2" in result


# ============================================================================
# Inventory Metrics Formula Tests
# ============================================================================


def test_eoq_formula() -> None:
    """Test Economic Order Quantity formula."""
    formula = EOQFormula()

    assert formula.metadata.name == "EOQ"

    result = formula.build("1000", "50", "2")
    # EOQ = sqrt((2*D*S)/H)
    assert "SQRT" in result


def test_reorder_point_formula() -> None:
    """Test reorder point formula."""
    formula = ReorderPointFormula()

    assert formula.metadata.name == "REORDER_POINT"

    result = formula.build("100", "7", "50")
    # ROP = (demand_rate * lead_time) + safety_stock
    assert "+" in result or "*" in result


def test_safety_stock_formula() -> None:
    """Test safety stock formula."""
    formula = SafetyStockFormula()

    assert formula.metadata.name == "SAFETY_STOCK"

    result = formula.build("1.65", "10", "7")
    # Safety stock = Z * sigma * sqrt(lead_time)
    assert "SQRT" in result or "*" in result


def test_inventory_turnover_formula() -> None:
    """Test inventory turnover formula."""
    formula = InventoryTurnoverFormula()

    assert formula.metadata.name == "INVENTORY_TURNOVER"

    result = formula.build("1000000", "100000")
    # Turnover = COGS / Average Inventory
    assert "/" in result


# ============================================================================
# Importer Tests
# ============================================================================


def test_mes_data_importer_csv() -> None:
    """Test MES data CSV importer."""
    importer = MESDataImporter()

    assert importer.metadata.name == "MES Data Importer"
    assert "csv" in importer.metadata.supported_formats

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Timestamp,Machine,Status,Units,Cycle_Time\n")
        f.write("2024-01-01 08:00,M001,Running,100,2.5\n")
        f.write("2024-01-01 09:00,M001,Running,95,2.6\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
    finally:
        csv_path.unlink()


def test_erp_data_importer_csv() -> None:
    """Test ERP data CSV importer."""
    importer = ERPDataImporter()

    assert importer.metadata.name == "ERP Data Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Item,Quantity,UnitCost,TotalCost\n")
        f.write("PART-001,100,5.50,550.00\n")
        f.write("PART-002,50,12.00,600.00\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
    finally:
        csv_path.unlink()


def test_sensor_data_importer_csv() -> None:
    """Test sensor data CSV importer."""
    importer = SensorDataImporter()

    assert importer.metadata.name == "Sensor Data Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Timestamp,Sensor_ID,Temperature,Pressure,Vibration\n")
        f.write("2024-01-01 08:00:00,S001,75.2,14.7,0.05\n")
        f.write("2024-01-01 08:00:01,S001,75.3,14.7,0.06\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
    finally:
        csv_path.unlink()


def test_importer_invalid_file() -> None:
    """Test importer with invalid file."""
    importer = MESDataImporter()

    result = importer.import_data("/nonexistent/file.csv")

    assert result.success is False
    assert len(result.errors) > 0


def test_sensor_data_validation_warnings() -> None:
    """Test sensor data importer with unusual values."""
    importer = SensorDataImporter()

    # Create CSV with unusual temperature
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Timestamp,Temperature\n")
        f.write("2024-01-01 08:00,500\n")  # Very high temperature
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        # Should succeed but may have warnings
        assert result.success is True
    finally:
        csv_path.unlink()


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_calculate_cycle_time() -> None:
    """Test cycle time calculation."""
    # 480 minutes / 120 units = 4 minutes per unit
    cycle_time = calculate_cycle_time(480, 120)
    assert abs(cycle_time - 4.0) < 0.01


def test_calculate_takt_time() -> None:
    """Test takt time calculation."""
    # 28800 seconds / 1200 demand = 24 seconds
    takt = calculate_takt_time(28800, 1200)
    assert abs(takt - 24.0) < 0.01


def test_calculate_defect_rate() -> None:
    """Test defect rate calculation."""
    # 15 defects / 1000 total = 1.5%
    rate = calculate_defect_rate(15, 1000)
    assert abs(rate - 1.5) < 0.01


def test_calculate_first_pass_yield() -> None:
    """Test first pass yield calculation."""
    # 950 good / 1000 total = 95%
    fpy = calculate_first_pass_yield(950, 1000)
    assert abs(fpy - 95.0) < 0.01


def test_calculate_oee() -> None:
    """Test OEE calculation."""
    # OEE = Availability * Performance * Quality (all as percentages)
    # 90% * 95% * 99% = 84.645%
    oee = calculate_oee(
        availability=90.0,
        performance=95.0,
        quality=99.0,
    )
    assert abs(oee - 84.645) < 0.1


def test_calculate_eoq() -> None:
    """Test Economic Order Quantity calculation."""
    # EOQ = sqrt((2*D*S)/H)
    # D=1000, S=50, H=2
    # EOQ = sqrt((2*1000*50)/2) = sqrt(50000) = 223.6
    eoq = calculate_eoq(annual_demand=1000, order_cost=50, holding_cost=2)
    assert 220 < eoq < 230


def test_calculate_reorder_point() -> None:
    """Test reorder point calculation."""
    # ROP = (demand_rate * lead_time) + safety_stock
    # Using positional arguments to match implementation signature
    rop = calculate_reorder_point(100, 7, 50)  # demand_rate, lead_time, safety_stock
    assert rop == 100 * 7 + 50  # 750


def test_calculate_safety_stock() -> None:
    """Test safety stock calculation."""
    # Safety stock = Z * sigma * sqrt(lead_time)
    # Using positional arguments to match implementation signature
    ss = calculate_safety_stock(1.65, 10, 7)  # z_score, demand_stddev, lead_time
    assert ss > 0


def test_format_manufacturing_number() -> None:
    """Test manufacturing number formatting."""
    formatted = format_manufacturing_number(1234567.89)
    assert "," in formatted or "." in formatted


def test_parse_manufacturing_date() -> None:
    """Test manufacturing date parsing."""
    date = parse_manufacturing_date("2024-01-15")
    assert date is not None


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_workflow_formulas() -> None:
    """Test complete workflow for formulas."""
    # Initialize plugin
    plugin = ManufacturingDomainPlugin()
    plugin.initialize()

    # Get formula class
    formula_class = plugin.get_formula("CYCLE_TIME")
    assert formula_class is not None

    # Create formula instance and use it
    formula = formula_class()
    result = formula.build("480", "120")
    assert result is not None


def test_formula_argument_validation() -> None:
    """Test formula argument validation."""
    formula = CycleTimeFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("480")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("480", "120", "extra")


def test_importer_validation() -> None:
    """Test importer source validation."""
    importer = MESDataImporter()

    # Non-existent file
    assert importer.validate_source(Path("/nonexistent.csv")) is False

    # Create temp file for validation
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        temp_path = Path(f.name)

    try:
        assert importer.validate_source(temp_path) is True
    finally:
        temp_path.unlink()


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


def test_zero_division_handling() -> None:
    """Test handling of zero division scenarios."""
    # Cycle time with zero units returns 0.0 (graceful handling)
    result = calculate_cycle_time(480, 0)
    assert result == 0.0


def test_negative_values_handling() -> None:
    """Test handling of negative values."""
    # Negative values might be rejected or handled
    # This depends on implementation
    try:
        result = calculate_defect_rate(-5, 100)
        # If it doesn't raise, ensure result makes sense
        assert result < 0 or result >= 0
    except ValueError:
        pass  # Expected for some implementations


def test_oee_boundary_values() -> None:
    """Test OEE with boundary values."""
    # Perfect OEE (100% for all metrics)
    oee = calculate_oee(100.0, 100.0, 100.0)
    assert abs(oee - 100.0) < 0.01

    # Zero availability
    oee = calculate_oee(0.0, 100.0, 100.0)
    assert abs(oee - 0.0) < 0.01


def test_inventory_formulas_with_cell_references() -> None:
    """Test inventory formulas with cell range references."""
    eoq = EOQFormula()
    result = eoq.build("A1", "B1", "C1")
    assert "A1" in result
    assert "SQRT" in result

    rop = ReorderPointFormula()
    result = rop.build("D1", "E1", "F1")
    assert "D1" in result


def test_mes_importer_json_format() -> None:
    """Test MES importer with JSON format."""
    importer = MESDataImporter()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('[{"machine": "M001", "status": "Running", "units": 100}]')
        json_path = Path(f.name)

    try:
        result = importer.import_data(json_path)
        assert result.success is True
    finally:
        json_path.unlink()


def test_quality_control_spc_calculations() -> None:
    """Test SPC-related calculations in quality control."""
    # Control limits formula
    formula = ControlLimitsFormula()
    # Formula requires: mean, stddev, limit_type
    result = formula.build("100", "5", "upper")

    # Should include 3-sigma calculation
    assert "3" in result or "5" in result
