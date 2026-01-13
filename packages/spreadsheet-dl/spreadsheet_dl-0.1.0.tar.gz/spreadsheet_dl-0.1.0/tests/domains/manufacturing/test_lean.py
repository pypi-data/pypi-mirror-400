"""
Tests for Lean Manufacturing formulas.

    Comprehensive tests for Lean formulas (10 formulas, 30+ tests)
"""

from __future__ import annotations

import pytest

from spreadsheet_dl.domains.manufacturing.formulas.lean import (
    CycleTimeFormula,
    FlowEfficiencyFormula,
    KanbanCalculationFormula,
    LeadTimeFormula,
    LittlesLawFormula,
    ProcessCycleEfficiencyFormula,
    SingleMinuteExchangeFormula,
    TaktTimeFormula,
    TotalProductiveMaintenanceFormula,
    ValueStreamEfficiencyFormula,
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.domain,
    pytest.mark.manufacturing,
    pytest.mark.lean,
]


# ============================================================================
# Value Stream Efficiency Tests
# ============================================================================


def test_value_stream_efficiency_metadata() -> None:
    """Test VALUE_STREAM_EFFICIENCY metadata."""
    formula = ValueStreamEfficiencyFormula()
    assert formula.metadata.name == "VALUE_STREAM_EFFICIENCY"
    assert formula.metadata.category == "lean"
    assert len(formula.metadata.arguments) == 2


def test_value_stream_efficiency_build() -> None:
    """Test VALUE_STREAM_EFFICIENCY formula building."""
    formula = ValueStreamEfficiencyFormula()
    result = formula.build("120", "600")
    assert result == "of:=(120/600)*100"


def test_value_stream_efficiency_with_cells() -> None:
    """Test VALUE_STREAM_EFFICIENCY with cell references."""
    formula = ValueStreamEfficiencyFormula()
    result = formula.build("A1", "B1")
    assert result == "of:=(A1/B1)*100"


# ============================================================================
# Lead Time Tests
# ============================================================================


def test_lead_time_metadata() -> None:
    """Test LEAD_TIME metadata."""
    formula = LeadTimeFormula()
    assert formula.metadata.name == "LEAD_TIME"
    assert formula.metadata.category == "lean"


def test_lead_time_build() -> None:
    """Test LEAD_TIME formula building."""
    formula = LeadTimeFormula()
    result = formula.build("B1", "A1")
    assert result == "of:=B1-A1"


def test_lead_time_calculation() -> None:
    """Test LEAD_TIME with date values."""
    formula = LeadTimeFormula()
    result = formula.build("45", "38")
    assert result == "of:=45-38"


# ============================================================================
# Process Cycle Efficiency Tests
# ============================================================================


def test_process_cycle_efficiency_metadata() -> None:
    """Test PROCESS_CYCLE_EFFICIENCY metadata."""
    formula = ProcessCycleEfficiencyFormula()
    assert formula.metadata.name == "PROCESS_CYCLE_EFFICIENCY"
    assert formula.metadata.category == "lean"


def test_process_cycle_efficiency_build() -> None:
    """Test PROCESS_CYCLE_EFFICIENCY formula building."""
    formula = ProcessCycleEfficiencyFormula()
    result = formula.build("120", "720")
    assert result == "of:=(120/720)*100"


def test_process_cycle_efficiency_with_cells() -> None:
    """Test PROCESS_CYCLE_EFFICIENCY with cells."""
    formula = ProcessCycleEfficiencyFormula()
    result = formula.build("C1", "D1")
    assert result == "of:=(C1/D1)*100"


# ============================================================================
# Takt Time Tests
# ============================================================================


def test_takt_time_metadata() -> None:
    """Test TAKT_TIME metadata."""
    formula = TaktTimeFormula()
    assert formula.metadata.name == "TAKT_TIME"
    assert formula.metadata.category == "lean"


def test_takt_time_build() -> None:
    """Test TAKT_TIME formula building."""
    formula = TaktTimeFormula()
    result = formula.build("28800", "1200")
    assert result == "of:=28800/1200"


def test_takt_time_with_cells() -> None:
    """Test TAKT_TIME with cell references."""
    formula = TaktTimeFormula()
    result = formula.build("E1", "F1")
    assert result == "of:=E1/F1"


# ============================================================================
# Cycle Time Tests
# ============================================================================


def test_cycle_time_metadata() -> None:
    """Test CYCLE_TIME metadata."""
    formula = CycleTimeFormula()
    assert formula.metadata.name == "CYCLE_TIME"
    assert formula.metadata.category == "lean"


def test_cycle_time_build() -> None:
    """Test CYCLE_TIME formula building."""
    formula = CycleTimeFormula()
    result = formula.build("480", "120")
    assert result == "of:=480/120"


def test_cycle_time_edge_case() -> None:
    """Test CYCLE_TIME with small numbers."""
    formula = CycleTimeFormula()
    result = formula.build("1", "1")
    assert result == "of:=1/1"


# ============================================================================
# TPM Availability Tests
# ============================================================================


def test_tpm_availability_metadata() -> None:
    """Test TPM_AVAILABILITY metadata."""
    formula = TotalProductiveMaintenanceFormula()
    assert formula.metadata.name == "TPM_AVAILABILITY"
    assert formula.metadata.category == "lean"


def test_tpm_availability_build() -> None:
    """Test TPM_AVAILABILITY formula building."""
    formula = TotalProductiveMaintenanceFormula()
    result = formula.build("420", "480")
    assert result == "of:=(420/480)*100"


def test_tpm_availability_perfect() -> None:
    """Test TPM_AVAILABILITY with 100% availability."""
    formula = TotalProductiveMaintenanceFormula()
    result = formula.build("480", "480")
    assert result == "of:=(480/480)*100"


# ============================================================================
# SMED Changeover Tests
# ============================================================================


def test_smed_changeover_metadata() -> None:
    """Test SMED_CHANGEOVER metadata."""
    formula = SingleMinuteExchangeFormula()
    assert formula.metadata.name == "SMED_CHANGEOVER"
    assert formula.metadata.category == "lean"


def test_smed_changeover_build() -> None:
    """Test SMED_CHANGEOVER formula building."""
    formula = SingleMinuteExchangeFormula()
    result = formula.build("125", "110")
    assert result == "of:=125-110"


def test_smed_changeover_with_cells() -> None:
    """Test SMED_CHANGEOVER with cell references."""
    formula = SingleMinuteExchangeFormula()
    result = formula.build("G1", "H1")
    assert result == "of:=G1-H1"


# ============================================================================
# Kanban Quantity Tests
# ============================================================================


def test_kanban_quantity_metadata() -> None:
    """Test KANBAN_QUANTITY metadata."""
    formula = KanbanCalculationFormula()
    assert formula.metadata.name == "KANBAN_QUANTITY"
    assert formula.metadata.category == "lean"
    assert len(formula.metadata.arguments) == 3


def test_kanban_quantity_build() -> None:
    """Test KANBAN_QUANTITY formula building."""
    formula = KanbanCalculationFormula()
    result = formula.build("100", "5", "0.2")
    assert result == "of:=((100*5)*(1+0.2))"


def test_kanban_quantity_no_safety() -> None:
    """Test KANBAN_QUANTITY with zero safety factor."""
    formula = KanbanCalculationFormula()
    result = formula.build("100", "5", "0")
    assert result == "of:=((100*5)*(1+0))"


# ============================================================================
# Little's Law Tests
# ============================================================================


def test_littles_law_metadata() -> None:
    """Test LITTLES_LAW metadata."""
    formula = LittlesLawFormula()
    assert formula.metadata.name == "LITTLES_LAW"
    assert formula.metadata.category == "lean"


def test_littles_law_build() -> None:
    """Test LITTLES_LAW formula building."""
    formula = LittlesLawFormula()
    result = formula.build("10", "5")
    assert result == "of:=10*5"


def test_littles_law_with_cells() -> None:
    """Test LITTLES_LAW with cell references."""
    formula = LittlesLawFormula()
    result = formula.build("I1", "J1")
    assert result == "of:=I1*J1"


# ============================================================================
# Flow Efficiency Tests
# ============================================================================


def test_flow_efficiency_metadata() -> None:
    """Test FLOW_EFFICIENCY metadata."""
    formula = FlowEfficiencyFormula()
    assert formula.metadata.name == "FLOW_EFFICIENCY"
    assert formula.metadata.category == "lean"


def test_flow_efficiency_build() -> None:
    """Test FLOW_EFFICIENCY formula building."""
    formula = FlowEfficiencyFormula()
    result = formula.build("60", "480")
    assert result == "of:=(60/480)*100"


def test_flow_efficiency_high() -> None:
    """Test FLOW_EFFICIENCY with high efficiency."""
    formula = FlowEfficiencyFormula()
    result = formula.build("400", "480")
    assert result == "of:=(400/480)*100"


# ============================================================================
# Argument Validation Tests
# ============================================================================


def test_value_stream_efficiency_too_few_args() -> None:
    """Test VALUE_STREAM_EFFICIENCY with too few arguments."""
    formula = ValueStreamEfficiencyFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("120")


def test_kanban_quantity_too_few_args() -> None:
    """Test KANBAN_QUANTITY with too few arguments."""
    formula = KanbanCalculationFormula()
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("100", "5")


def test_lead_time_too_many_args() -> None:
    """Test LEAD_TIME with too many arguments."""
    formula = LeadTimeFormula()
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("45", "38", "extra")
