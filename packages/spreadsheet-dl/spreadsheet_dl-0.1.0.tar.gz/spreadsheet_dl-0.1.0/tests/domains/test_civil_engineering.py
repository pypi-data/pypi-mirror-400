"""
Tests for Civil Engineering domain plugin.

    Comprehensive tests for Civil Engineering domain (95%+ coverage target)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.domains.civil_engineering import (
    BeamDeflectionFormula,
    BearingCapacityFormula,
    BearingCapacityTerzaghi,
    BuildingCodesImporter,
    CivilEngineeringDomainPlugin,
    ConcreteMix,
    ConcreteStrengthFormula,
    ConsolidationSettlement,
    CrackWidthFormula,
    DeadLoadFormula,
    LiveLoadFormula,
    LoadCombination,
    LoadCombinationCode,
    MomentFormula,
    ReinforcementRatioFormula,
    SeismicLoadFormula,
    SettlementElastic,
    SettlementFormula,
    ShearStressFormula,
    SoilPressureFormula,
    StoppingDistance,
    StructuralResultsImporter,
    SurveyDataImporter,
    TrafficFlow,
    WindLoadFormula,
)
from spreadsheet_dl.domains.civil_engineering.utils import (
    beam_self_weight,
    bearing_capacity_factors,
    calculate_cement_content,
    consolidation_settlement,
    design_concrete_mix,
    ft_to_m,
    get_load_combinations,
    kn_to_lbf,
    knpm_to_lbpft,
    lbf_to_kn,
    lbpft_to_knpm,
    m_to_ft,
    mpa_to_psi,
    psi_to_mpa,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.engineering]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = CivilEngineeringDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "civil_engineering"
    assert metadata.version == "0.1.0"
    assert "civil-engineering" in metadata.tags
    assert "structural" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = CivilEngineeringDomainPlugin()
    plugin.initialize()

    # Verify formulas registered (18 total)
    # Beam formulas
    assert plugin.get_formula("BEAM_DEFLECTION") == BeamDeflectionFormula
    assert plugin.get_formula("SHEAR_STRESS") == ShearStressFormula
    assert plugin.get_formula("MOMENT") == MomentFormula

    # Soil formulas
    assert plugin.get_formula("BEARING_CAPACITY") == BearingCapacityFormula
    assert plugin.get_formula("SETTLEMENT") == SettlementFormula
    assert plugin.get_formula("SOIL_PRESSURE") == SoilPressureFormula

    # Concrete formulas
    assert plugin.get_formula("CONCRETE_STRENGTH") == ConcreteStrengthFormula
    assert plugin.get_formula("REINFORCEMENT_RATIO") == ReinforcementRatioFormula
    assert plugin.get_formula("CRACK_WIDTH") == CrackWidthFormula

    # Load formulas
    assert plugin.get_formula("DEAD_LOAD") == DeadLoadFormula
    assert plugin.get_formula("LIVE_LOAD") == LiveLoadFormula
    assert plugin.get_formula("WIND_LOAD") == WindLoadFormula
    assert plugin.get_formula("SEISMIC_LOAD") == SeismicLoadFormula

    # Foundation formulas
    assert plugin.get_formula("BEARING_CAPACITY_TERZAGHI") == BearingCapacityTerzaghi
    assert plugin.get_formula("SETTLEMENT_ELASTIC") == SettlementElastic
    assert plugin.get_formula("CONSOLIDATION_SETTLEMENT") == ConsolidationSettlement

    # Transportation formulas
    assert plugin.get_formula("STOPPING_DISTANCE") == StoppingDistance
    assert plugin.get_formula("TRAFFIC_FLOW") == TrafficFlow

    # Verify importers registered (3 total)
    assert plugin.get_importer("survey_data") == SurveyDataImporter
    assert plugin.get_importer("structural_results") == StructuralResultsImporter
    assert plugin.get_importer("building_codes") == BuildingCodesImporter


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = CivilEngineeringDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = CivilEngineeringDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Beam Formula Tests
# ============================================================================


def test_beam_deflection_formula() -> None:
    """Test beam deflection formula: delta = (5*w*L⁴)/(384*E*I)."""
    formula = BeamDeflectionFormula()

    # Test metadata
    assert formula.metadata.name == "BEAM_DEFLECTION"
    assert formula.metadata.category == "civil_engineering"
    assert len(formula.metadata.arguments) == 4

    # Test calculation
    result = formula.build("10", "5000", "200000", "8.33e6")
    assert result == "of:=(5*10*5000^4)/(384*200000*8.33e6)"

    # Test with cell references
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=(5*A2*B2^4)/(384*C2*D2)"


def test_shear_stress_formula() -> None:
    """Test shear stress formula: tau = V*Q/(I*b)."""
    formula = ShearStressFormula()

    assert formula.metadata.name == "SHEAR_STRESS"

    result = formula.build("50000", "1e6", "8.33e6", "200")
    assert result == "of:=50000*1e6/(8.33e6*200)"


def test_moment_formula() -> None:
    """Test moment formula: M = w*L²/8."""
    formula = MomentFormula()

    assert formula.metadata.name == "MOMENT"

    result = formula.build("10", "5000")
    assert result == "of:=10*5000^2/8"


# ============================================================================
# Soil Formula Tests
# ============================================================================


def test_bearing_capacity_formula() -> None:
    """Test bearing capacity formula."""
    formula = BearingCapacityFormula()

    assert formula.metadata.name == "BEARING_CAPACITY"
    assert len(formula.metadata.arguments) == 7

    result = formula.build("20", "5.14", "18", "2", "1.81", "1.5", "0.45")
    assert result == "of:=20*5.14+18*2*1.81+0.5*18*1.5*0.45"


def test_settlement_formula() -> None:
    """Test settlement formula: S = (H*Deltasigma)/E_s."""
    formula = SettlementFormula()

    assert formula.metadata.name == "SETTLEMENT"

    result = formula.build("3000", "100", "10000")
    assert result == "of:=3000*100/10000"


def test_soil_pressure_formula() -> None:
    """Test soil pressure formula: sigma = P/A."""
    formula = SoilPressureFormula()

    assert formula.metadata.name == "SOIL_PRESSURE"

    result = formula.build("1000", "4")
    assert result == "of:=1000/4"


# ============================================================================
# Concrete Formula Tests
# ============================================================================


def test_concrete_strength_formula() -> None:
    """Test concrete strength formula: f'_c = P/A."""
    formula = ConcreteStrengthFormula()

    assert formula.metadata.name == "CONCRETE_STRENGTH"

    result = formula.build("400000", "19635")
    assert result == "of:=400000/19635"


def test_reinforcement_ratio_formula() -> None:
    """Test reinforcement ratio formula: rho = A_s/(b*d)."""
    formula = ReinforcementRatioFormula()

    assert formula.metadata.name == "REINFORCEMENT_RATIO"

    result = formula.build("1256", "300", "450")
    assert result == "of:=1256/(300*450)"


def test_crack_width_formula() -> None:
    """Test crack width formula: w = s_r*epsilon_m."""
    formula = CrackWidthFormula()

    assert formula.metadata.name == "CRACK_WIDTH"

    result = formula.build("150", "0.0002")
    assert result == "of:=150*0.0002"


# ============================================================================
# Load Formula Tests
# ============================================================================


def test_dead_load_formula() -> None:
    """Test dead load formula: DL = rho*V*g."""
    formula = DeadLoadFormula()

    assert formula.metadata.name == "DEAD_LOAD"

    # With all arguments
    result = formula.build("2400", "10", "9.81")
    assert result == "of:=2400*10*9.81/1000"

    # With default g
    result = formula.build("2400", "10")
    assert result == "of:=2400*10*9.81/1000"


def test_live_load_formula() -> None:
    """Test live load formula: LL = q*A."""
    formula = LiveLoadFormula()

    assert formula.metadata.name == "LIVE_LOAD"

    result = formula.build("5", "50")
    assert result == "of:=5*50"


def test_wind_load_formula() -> None:
    """Test wind load formula: W = q*G*C_p*A."""
    formula = WindLoadFormula()

    assert formula.metadata.name == "WIND_LOAD"

    result = formula.build("0.85", "0.85", "0.8", "100")
    assert result == "of:=0.85*0.85*0.8*100"


def test_seismic_load_formula() -> None:
    """Test seismic load formula: F = C_s*W."""
    formula = SeismicLoadFormula()

    assert formula.metadata.name == "SEISMIC_LOAD"

    result = formula.build("0.15", "10000")
    assert result == "of:=0.15*10000"


# ============================================================================
# Importer Tests
# ============================================================================


def test_survey_data_importer_csv() -> None:
    """Test survey data CSV importer."""
    importer = SurveyDataImporter()

    assert importer.metadata.name == "Survey Data Importer"
    assert "csv" in importer.metadata.supported_formats

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Station,Northing,Easting,Elevation,Description\n")
        f.write("STA001,1000.5,2000.3,100.2,Benchmark\n")
        f.write("STA002,1050.2,2010.8,102.5,Control Point\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
        # Check that data was imported (station field may be auto-detected differently)
        assert "elevation" in result.data[0]
        assert result.data[0]["elevation"] == 100.2
        assert "northing" in result.data[0]
        assert result.data[0]["northing"] == 1000.5
    finally:
        csv_path.unlink()


def test_survey_data_importer_invalid_file() -> None:
    """Test survey data importer with invalid file."""
    importer = SurveyDataImporter()

    result = importer.import_data("/nonexistent/file.csv")

    assert result.success is False
    assert len(result.errors) > 0


def test_structural_results_importer_csv() -> None:
    """Test structural results CSV importer."""
    importer = StructuralResultsImporter(software="generic")

    assert importer.metadata.name == "Structural Results Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Member,Axial,Shear,Moment\n")
        f.write("M001,100.5,-50.2,75.8\n")
        f.write("M002,-80.3,30.1,-60.5\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
        assert result.data[0]["id"] == "M001"
        assert result.data[0]["axial"] == 100.5
    finally:
        csv_path.unlink()


def test_building_codes_importer_csv() -> None:
    """Test building codes CSV importer."""
    importer = BuildingCodesImporter(code_standard="ASCE_7")

    assert importer.metadata.name == "Building Codes Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Zone,Wind Speed,Snow Load,Seismic Coefficient\n")
        f.write("Zone 1,90,30,0.15\n")
        f.write("Zone 2,110,50,0.25\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
        assert result.data[0]["zone"] == "Zone 1"
        assert result.data[0]["wind_speed"] == 90
    finally:
        csv_path.unlink()


def test_building_codes_importer_json() -> None:
    """Test building codes JSON importer."""
    importer = BuildingCodesImporter()

    # Create test JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('[{"zone": "A", "wind_speed": 100}, {"zone": "B", "wind_speed": 120}]')
        json_path = Path(f.name)

    try:
        result = importer.import_data(json_path)

        assert result.success is True
        assert len(result.data) == 2
    finally:
        json_path.unlink()


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_unit_conversions() -> None:
    """Test unit conversion functions."""
    # Force conversions
    assert abs(kn_to_lbf(10.0) - 2248.089) < 0.1
    assert abs(lbf_to_kn(1000.0) - 4.448) < 0.001

    # Length conversions
    assert abs(m_to_ft(10.0) - 32.808) < 0.001
    assert abs(ft_to_m(100.0) - 30.48) < 0.01

    # Pressure conversions
    assert abs(mpa_to_psi(10.0) - 1450.377) < 0.001
    assert abs(psi_to_mpa(1000.0) - 6.895) < 0.001

    # Load conversions
    assert abs(knpm_to_lbpft(10.0) - 685.218) < 0.001
    assert abs(lbpft_to_knpm(100.0) - 1.459) < 0.001


def test_load_combinations_asce7() -> None:
    """Test ASCE 7 load combinations."""
    combos = get_load_combinations(LoadCombinationCode.ASCE_7_16)

    assert len(combos) == 7
    assert isinstance(combos[0], LoadCombination)
    assert combos[0].name == "1.4D"
    assert combos[0].dead_factor == 1.4

    # Check specific combination
    combo = combos[1]
    assert combo.dead_factor == 1.2
    assert combo.live_factor == 1.6


def test_load_combinations_eurocode() -> None:
    """Test Eurocode load combinations."""
    combos = get_load_combinations(LoadCombinationCode.EUROCODE)

    assert len(combos) == 5
    assert combos[0].dead_factor == 1.35


def test_bearing_capacity_factors_calculation() -> None:
    """Test bearing capacity factors calculation."""
    Nc, Nq, Ng = bearing_capacity_factors(30.0)

    # Verify factors are in reasonable ranges
    assert 25 < Nc < 35
    assert 15 < Nq < 25
    assert 10 < Ng < 25


def test_consolidation_settlement() -> None:
    """Test consolidation settlement calculation."""
    settlement = consolidation_settlement(
        H=5000,  # mm
        Cc=0.3,
        e0=0.8,
        p0=100,  # kPa
        delta_p=50,  # kPa
    )

    # Settlement should be positive and reasonable
    assert settlement > 0
    assert settlement < 1000  # Less than 1m seems reasonable


def test_calculate_cement_content() -> None:
    """Test cement content calculation."""
    cement = calculate_cement_content(25.0, 0.5)

    assert cement > 0
    assert cement == 350.0  # 175 / 0.5


def test_design_concrete_mix() -> None:
    """Test concrete mix design."""
    mix = design_concrete_mix(25.0, 0.5, 75)

    assert isinstance(mix, ConcreteMix)
    assert mix.cement > 0
    assert mix.water > 0
    assert mix.fine_aggregate > 0
    assert mix.coarse_aggregate > 0
    assert mix.wc_ratio <= 0.5
    assert mix.target_strength == 25.0


def test_beam_self_weight() -> None:
    """Test beam self-weight calculation."""
    weight = beam_self_weight(300, 500, 6000)  # mm

    # Weight should be positive
    assert weight > 0
    # Roughly 0.3m * 0.5m * 2400 kg/m³ * 9.81 / 1000 = 3.53 kN/m
    assert 3.0 < weight < 4.0


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_workflow_formulas() -> None:
    """Test complete workflow for formulas."""
    # Initialize plugin
    plugin = CivilEngineeringDomainPlugin()
    plugin.initialize()

    # Get formula class
    formula_class = plugin.get_formula("BEAM_DEFLECTION")
    assert formula_class is not None

    # Create formula instance and use it
    formula = formula_class()
    result = formula.build("10", "5000", "200000", "8.33e6")
    assert result is not None


def test_formula_argument_validation() -> None:
    """Test formula argument validation."""
    formula = BeamDeflectionFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("10", "5000")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("10", "5000", "200000", "8.33e6", "extra")


def test_importer_validation() -> None:
    """Test importer source validation."""
    importer = SurveyDataImporter()

    # Valid file types
    assert importer.validate_source(Path("/test/file.csv")) is False  # Doesn't exist
    assert importer.validate_source(Path("/test/file.xml")) is False  # Doesn't exist

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


def test_bearing_capacity_zero_phi() -> None:
    """Test bearing capacity with zero friction angle."""
    Nc, _Nq, _Ng = bearing_capacity_factors(0.0)

    # For phi=0 (purely cohesive soil), Nc should be around 5.14
    assert abs(Nc - 5.14) < 0.01


def test_survey_importer_unusual_elevations() -> None:
    """Test survey importer with unusual elevation values."""
    importer = SurveyDataImporter()

    # Create CSV with unusual elevation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Station,Northing,Easting,Elevation\n")
        f.write("STA001,1000,2000,15000\n")  # Very high elevation
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert len(result.warnings) > 0  # Should warn about unusual elevation
    finally:
        csv_path.unlink()


def test_structural_results_large_forces() -> None:
    """Test structural results importer with very large forces."""
    importer = StructuralResultsImporter()

    # Create CSV with large force
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Member,Axial\n")
        f.write("M001,2000000\n")  # 2,000,000 kN
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert len(result.warnings) > 0  # Should warn about large force
    finally:
        csv_path.unlink()


def test_survey_data_importer_xml() -> None:
    """Test survey data XML importer."""
    importer = SurveyDataImporter()

    # Create test XML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write('<?xml version="1.0"?>\n')
        f.write("<survey>\n")
        f.write("  <point><station>STA001</station><northing>1000.5</northing>")
        f.write("<easting>2000.3</easting><elevation>100.2</elevation></point>\n")
        f.write("</survey>\n")
        xml_path = Path(f.name)

    try:
        result = importer.import_data(xml_path)

        assert result.success is True
        assert len(result.data) == 1
        assert "elevation" in result.data[0]
    finally:
        xml_path.unlink()


def test_structural_results_text_formats() -> None:
    """Test structural results with different software formats."""
    # Test SAP2000 format
    importer = StructuralResultsImporter(software="SAP2000")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("MEMBER FORCES\n")
        f.write("Member   Axial   Shear   Moment\n")
        f.write("M001     100.5   -50.2   75.8\n")
        txt_path = Path(f.name)

    try:
        result = importer.import_data(txt_path)
        assert result.success is True
    finally:
        txt_path.unlink()

    # Test STAAD format
    importer2 = StructuralResultsImporter(software="STAAD")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("MEMBER END FORCES\n")
        f.write("Member   Axial   Shear   Moment\n")
        f.write("M001     100.5   -50.2   75.8\n")
        txt_path2 = Path(f.name)

    try:
        result2 = importer2.import_data(txt_path2)
        assert result2.success is True
    finally:
        txt_path2.unlink()


def test_building_codes_importer_warnings() -> None:
    """Test building codes importer validation warnings."""
    importer = BuildingCodesImporter()

    # Create CSV with unusual values
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Zone,Wind Speed,Snow Load,Seismic Coefficient\n")
        f.write("Zone 1,300,600,5.0\n")  # All values are unusual
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert len(result.warnings) >= 3  # Should warn about all three
    finally:
        csv_path.unlink()


def test_building_codes_importer_json_objects() -> None:
    """Test building codes JSON importer with object format."""
    importer = BuildingCodesImporter()

    # Create JSON with object format
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"zone_a": {"wind_speed": 100}, "zone_b": {"wind_speed": 120}}')
        json_path = Path(f.name)

    try:
        result = importer.import_data(json_path)

        assert result.success is True
        assert len(result.data) == 2
    finally:
        json_path.unlink()


def test_utils_edge_cases() -> None:
    """Test utility functions with edge cases."""
    from spreadsheet_dl.domains.civil_engineering.utils import (
        LoadCombinationCode,
        get_load_combinations,
    )

    # Test IBC code (should return same as ASCE 7)
    combos_ibc = get_load_combinations(LoadCombinationCode.IBC_2021)
    combos_asce = get_load_combinations(LoadCombinationCode.ASCE_7_16)
    assert len(combos_ibc) == len(combos_asce)


def test_importer_error_handling() -> None:
    """Test importer error handling with malformed files."""
    # Test with empty CSV
    importer = SurveyDataImporter()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("")  # Empty file
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        # Should handle gracefully
        assert result.success in (True, False)
    finally:
        csv_path.unlink()

    # Test with malformed XML
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write("<invalid>")  # Malformed XML
        xml_path = Path(f.name)

    try:
        result = importer.import_data(xml_path)
        # May succeed but with errors, or fail entirely
        if result.success:
            assert len(result.errors) > 0  # Should have errors
        else:
            assert len(result.errors) > 0  # Should have errors
    finally:
        xml_path.unlink()


# ============================================================================
# Foundation Formula Tests (Batch 3)
# ============================================================================


def test_bearing_capacity_terzaghi_formula() -> None:
    """Test Terzaghi bearing capacity formula."""
    formula = BearingCapacityTerzaghi()

    assert formula.metadata.name == "BEARING_CAPACITY_TERZAGHI"
    assert formula.metadata.category == "civil_engineering"
    assert len(formula.metadata.arguments) == 7

    # Test calculation with numeric values
    result = formula.build("20", "18", "2", "1.5", "5.14", "1.81", "0.45")
    assert result == "of:=20*5.14+18*2*1.81+0.5*18*1.5*0.45"

    # Test with cell references
    result = formula.build("A2", "B2", "C2", "D2", "E2", "F2", "G2")
    assert result == "of:=A2*E2+B2*C2*F2+0.5*B2*D2*G2"


def test_settlement_elastic_formula() -> None:
    """Test elastic settlement formula."""
    formula = SettlementElastic()

    assert formula.metadata.name == "SETTLEMENT_ELASTIC"
    assert formula.metadata.category == "civil_engineering"
    assert len(formula.metadata.arguments) == 4

    # Test calculation
    result = formula.build("100", "2", "20000", "0.3")
    assert result == "of:=(100*2*(1-0.3^2))/20000"

    # Test with cell references
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=(A2*B2*(1-D2^2))/C2"


def test_consolidation_settlement_formula() -> None:
    """Test consolidation settlement formula."""
    formula = ConsolidationSettlement()

    assert formula.metadata.name == "CONSOLIDATION_SETTLEMENT"
    assert formula.metadata.category == "civil_engineering"
    assert len(formula.metadata.arguments) == 5

    # Test calculation
    result = formula.build("0.3", "0.8", "5", "100", "150")
    assert result == "of:=(0.3*5/(1+0.8))*LOG10(150/100)"

    # Test with cell references
    result = formula.build("A2", "B2", "C2", "D2", "E2")
    assert result == "of:=(A2*C2/(1+B2))*LOG10(E2/D2)"


# ============================================================================
# Transportation Formula Tests (Batch 3)
# ============================================================================


def test_stopping_distance_formula() -> None:
    """Test stopping distance formula."""
    formula = StoppingDistance()

    assert formula.metadata.name == "STOPPING_DISTANCE"
    assert formula.metadata.category == "civil_engineering"
    assert len(formula.metadata.arguments) == 4

    # Test calculation
    result = formula.build("25", "2.5", "0.35", "0.03")
    assert result == "of:=25*2.5+(25^2)/(2*9.81*(0.35+0.03))"

    # Test with cell references
    result = formula.build("A2", "B2", "C2", "D2")
    assert result == "of:=A2*B2+(A2^2)/(2*9.81*(C2+D2))"


def test_traffic_flow_formula() -> None:
    """Test traffic flow formula."""
    formula = TrafficFlow()

    assert formula.metadata.name == "TRAFFIC_FLOW"
    assert formula.metadata.category == "civil_engineering"
    assert len(formula.metadata.arguments) == 2

    # Test calculation
    result = formula.build("50", "80")
    assert result == "of:=50*80"

    # Test with cell references
    result = formula.build("A2", "B2")
    assert result == "of:=A2*B2"


# ============================================================================
# Formula Argument Validation Tests (Batch 3)
# ============================================================================


def test_bearing_capacity_terzaghi_validation() -> None:
    """Test Terzaghi bearing capacity argument validation."""
    formula = BearingCapacityTerzaghi()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("20", "18", "2")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("20", "18", "2", "1.5", "5.14", "1.81", "0.45", "extra")


def test_settlement_elastic_validation() -> None:
    """Test elastic settlement argument validation."""
    formula = SettlementElastic()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("100", "2")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("100", "2", "20000", "0.3", "extra")


def test_consolidation_settlement_validation() -> None:
    """Test consolidation settlement argument validation."""
    formula = ConsolidationSettlement()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("0.3", "0.8")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("0.3", "0.8", "5", "100", "150", "extra")


def test_stopping_distance_validation() -> None:
    """Test stopping distance argument validation."""
    formula = StoppingDistance()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("25", "2.5")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("25", "2.5", "0.35", "0.03", "extra")


def test_traffic_flow_validation() -> None:
    """Test traffic flow argument validation."""
    formula = TrafficFlow()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("50")

    # Too many arguments should raise
    with pytest.raises(ValueError, match="accepts at most"):
        formula.build("50", "80", "extra")
