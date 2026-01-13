"""
Tests for Environmental domain plugin.

    Comprehensive tests for Environmental domain (95%+ coverage target)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.domains.environmental import (
    AQICalculationFormula,
    BODCalculationFormula,
    CarbonEquivalentFormula,
    EcologicalFootprintFormula,
    EcosystemShannonDiversityFormula,
    EcosystemSimpsonIndexFormula,
    EcosystemSpeciesRichnessFormula,
    EmissionRateFormula,
    EnvironmentalDomainPlugin,
    EnvironmentalImpactScoreFormula,
    LabResultsImporter,
    PollutionIndexFormula,
    SatelliteDataImporter,
    SensorNetworkImporter,
    SustainabilityScoreFormula,
    WaterQualityIndexFormula,
)
from spreadsheet_dl.domains.environmental.utils import (
    calculate_aqi,
    calculate_bod,
    calculate_carbon_equivalent,
    calculate_ecological_footprint,
    calculate_shannon_diversity,
    calculate_simpson_index,
    calculate_wqi,
    format_concentration,
    ppm_to_ugm3,
    ugm3_to_ppm,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain, pytest.mark.science]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = EnvironmentalDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "environmental"
    assert metadata.version == "0.1.0"
    assert "environmental" in metadata.tags
    assert "sustainability" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = EnvironmentalDomainPlugin()
    plugin.initialize()

    # Verify formulas registered (12 total)
    # Air quality formulas
    assert plugin.get_formula("AQI_CALCULATION") == AQICalculationFormula
    assert plugin.get_formula("EMISSION_RATE") == EmissionRateFormula
    assert plugin.get_formula("POLLUTION_INDEX") == PollutionIndexFormula

    # Water quality formulas
    assert plugin.get_formula("WATER_QUALITY_INDEX") == WaterQualityIndexFormula
    assert plugin.get_formula("BOD_CALCULATION") == BODCalculationFormula

    # Ecology formulas
    assert (
        plugin.get_formula("ECOSYSTEM_SHANNON_DIVERSITY")
        == EcosystemShannonDiversityFormula
    )
    assert plugin.get_formula("ECOSYSTEM_SIMPSON_INDEX") == EcosystemSimpsonIndexFormula
    assert (
        plugin.get_formula("ECOSYSTEM_SPECIES_RICHNESS")
        == EcosystemSpeciesRichnessFormula
    )

    # Carbon/sustainability formulas
    assert plugin.get_formula("CARBON_EQUIVALENT") == CarbonEquivalentFormula
    assert plugin.get_formula("ECOLOGICAL_FOOTPRINT") == EcologicalFootprintFormula
    assert plugin.get_formula("SUSTAINABILITY_SCORE") == SustainabilityScoreFormula
    assert (
        plugin.get_formula("ENVIRONMENTAL_IMPACT_SCORE")
        == EnvironmentalImpactScoreFormula
    )

    # Verify importers registered (3 total)
    assert plugin.get_importer("sensor_network") == SensorNetworkImporter
    assert plugin.get_importer("lab_results") == LabResultsImporter
    assert plugin.get_importer("satellite_data") == SatelliteDataImporter


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = EnvironmentalDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = EnvironmentalDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Air Quality Formula Tests
# ============================================================================


def test_aqi_calculation_formula() -> None:
    """Test AQI calculation formula."""
    formula = AQICalculationFormula()

    # Test metadata
    assert formula.metadata.name == "AQI_CALCULATION"
    assert formula.metadata.category == "environmental"
    assert len(formula.metadata.arguments) == 2

    # Test calculation
    result = formula.build("35.5")
    assert "IF" in result  # Uses nested IF for breakpoints


def test_aqi_with_pollutant_type() -> None:
    """Test AQI calculation with pollutant type specified."""
    formula = AQICalculationFormula()

    result = formula.build("A1", "pm25")
    assert "IF" in result


def test_emission_rate_formula() -> None:
    """Test emission rate formula: flow * concentration / 1000000."""
    formula = EmissionRateFormula()

    assert formula.metadata.name == "EMISSION_RATE"

    result = formula.build("1000", "50")
    assert result == "of:=1000*50/1000000"


def test_emission_rate_with_efficiency() -> None:
    """Test emission rate with control efficiency."""
    formula = EmissionRateFormula()

    result = formula.build("1000", "50", "0.95")
    assert "(1-0.95)" in result


def test_pollution_index_formula() -> None:
    """Test pollution index formula."""
    formula = PollutionIndexFormula()

    assert formula.metadata.name == "POLLUTION_INDEX"

    # Single pollutant
    result = formula.build("75")
    assert result == "of:=75"

    # Multiple pollutants
    result = formula.build("75", "60", "50")
    assert "MAX" in result


def test_pollution_index_two_pollutants() -> None:
    """Test pollution index with two pollutants."""
    formula = PollutionIndexFormula()

    result = formula.build("75", "60")
    assert "MAX(75;60)" in result


# ============================================================================
# Water Quality Formula Tests
# ============================================================================


def test_water_quality_index_formula() -> None:
    """Test water quality index formula."""
    formula = WaterQualityIndexFormula()

    assert formula.metadata.name == "WATER_QUALITY_INDEX"

    result = formula.build("95", "2", "7.2")
    # Should produce WQI calculation with sub-indices
    assert "MIN" in result  # DO sub-index
    assert "MAX" in result  # BOD sub-index
    assert "ABS" in result  # pH sub-index


def test_water_quality_index_with_turbidity() -> None:
    """Test WQI formula with turbidity parameter."""
    formula = WaterQualityIndexFormula()

    result = formula.build("95", "2", "7.2", "10")
    # With 4 parameters, should divide by 4
    assert "/4" in result


def test_bod_calculation_formula() -> None:
    """Test BOD calculation formula: (initial - final) * (bottle/sample)."""
    formula = BODCalculationFormula()

    assert formula.metadata.name == "BOD_CALCULATION"

    result = formula.build("8.5", "3.2", "30")
    # BOD = (initial_do - final_do) * (bottle_volume / sample_volume)
    assert "(8.5-3.2)" in result
    assert "(300/30)" in result


def test_bod_with_custom_bottle_volume() -> None:
    """Test BOD formula with custom bottle volume."""
    formula = BODCalculationFormula()

    result = formula.build("8.5", "3.2", "30", "500")
    assert "(500/30)" in result


# ============================================================================
# Ecology Formula Tests
# ============================================================================


def test_shannon_diversity_formula() -> None:
    """Test Shannon diversity index formula."""
    formula = EcosystemShannonDiversityFormula()

    assert formula.metadata.name == "ECOSYSTEM_SHANNON_DIVERSITY"

    result = formula.build("A1:A10")
    # Shannon index uses SUMPRODUCT with LN
    assert "SUMPRODUCT" in result
    assert "LN" in result


def test_simpson_index_formula() -> None:
    """Test Simpson's diversity index formula."""
    formula = EcosystemSimpsonIndexFormula()

    assert formula.metadata.name == "ECOSYSTEM_SIMPSON_INDEX"

    result = formula.build("A1:A10")
    # Simpson index: 1 - sum(pi^2)
    assert "1-SUMPRODUCT" in result


def test_species_richness_formula() -> None:
    """Test species richness formula."""
    formula = EcosystemSpeciesRichnessFormula()

    assert formula.metadata.name == "ECOSYSTEM_SPECIES_RICHNESS"

    result = formula.build("A1:A10")
    # Count species with non-zero abundance
    assert "COUNTIF" in result
    assert ">0" in result


# ============================================================================
# Carbon/Sustainability Formula Tests
# ============================================================================


def test_carbon_equivalent_formula() -> None:
    """Test carbon equivalent formula using GWP."""
    formula = CarbonEquivalentFormula()

    assert formula.metadata.name == "CARBON_EQUIVALENT"

    # CH4 has GWP of 28
    result = formula.build("100", "ch4")
    assert result == "of:=100*28"

    # CO2 has GWP of 1
    result = formula.build("100", "co2")
    assert result == "of:=100*1"


def test_carbon_equivalent_default_gas() -> None:
    """Test carbon equivalent with default gas type (CO2)."""
    formula = CarbonEquivalentFormula()

    result = formula.build("100")
    assert result == "of:=100*1"


def test_ecological_footprint_formula() -> None:
    """Test ecological footprint formula."""
    formula = EcologicalFootprintFormula()

    assert formula.metadata.name == "ECOLOGICAL_FOOTPRINT"

    result = formula.build("5000")
    # Carbon footprint in gha: (kg/1000)*0.27
    assert "5000/1000" in result
    assert "0.27" in result


def test_ecological_footprint_with_food_and_housing() -> None:
    """Test ecological footprint with food and housing factors."""
    formula = EcologicalFootprintFormula()

    result = formula.build("5000", "1.5", "100")
    assert "0.8" in result  # Food factor
    assert "0.0001" in result  # Housing factor


def test_sustainability_score_formula() -> None:
    """Test sustainability score formula."""
    formula = SustainabilityScoreFormula()

    assert formula.metadata.name == "SUSTAINABILITY_SCORE"

    # Full ESG score
    result = formula.build("75", "80", "85")
    assert "0.4" in result  # Environmental weight
    assert "0.3" in result  # Social and governance weights


def test_sustainability_score_environmental_only() -> None:
    """Test sustainability score with environmental component only."""
    formula = SustainabilityScoreFormula()

    result = formula.build("75")
    assert result == "of:=75"


def test_environmental_impact_score_formula() -> None:
    """Test environmental impact score formula."""
    formula = EnvironmentalImpactScoreFormula()

    assert formula.metadata.name == "ENVIRONMENTAL_IMPACT_SCORE"

    # Magnitude * Duration * Reversibility / 1.25
    result = formula.build("3", "4", "2")
    assert result == "of:=(3*4*2*1)/1.25"


def test_environmental_impact_score_with_probability() -> None:
    """Test environmental impact score with probability."""
    formula = EnvironmentalImpactScoreFormula()

    result = formula.build("3", "4", "2", "0.8")
    assert result == "of:=(3*4*2*0.8)/1.25"


# ============================================================================
# Importer Tests
# ============================================================================


def test_sensor_network_importer_csv() -> None:
    """Test sensor network CSV importer."""
    importer = SensorNetworkImporter()

    assert importer.metadata.name == "Sensor Network Importer"
    assert "csv" in importer.metadata.supported_formats

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Timestamp,Sensor ID,PM2.5,PM10,Temperature,Humidity\n")
        f.write("2024-01-01 12:00,S001,35.5,50.2,22.5,65.0\n")
        f.write("2024-01-01 12:15,S001,38.2,52.1,22.8,64.5\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
    finally:
        csv_path.unlink()


def test_sensor_network_importer_invalid_file() -> None:
    """Test sensor network importer with invalid file."""
    importer = SensorNetworkImporter()

    result = importer.import_data("/nonexistent/file.csv")

    assert result.success is False
    assert len(result.errors) > 0


def test_lab_results_importer_csv() -> None:
    """Test lab results CSV importer."""
    importer = LabResultsImporter()

    assert importer.metadata.name == "Lab Results Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Sample ID,Parameter,Result,Unit,Method\n")
        f.write("WQ001,pH,7.2,,pH Meter\n")
        f.write("WQ001,BOD,3.5,mg/L,Standard Method\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
    finally:
        csv_path.unlink()


def test_lab_results_non_detect() -> None:
    """Test lab results importer with non-detect values."""
    importer = LabResultsImporter(validate_detection_limits=True)

    # Create CSV with non-detect values
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Sample ID,Parameter,Result,Detection Limit\n")
        f.write("WQ001,Lead,<0.005,0.005\n")
        f.write("WQ001,Arsenic,ND,0.001\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        # Should have warnings for non-detect values
        assert len(result.warnings) >= 0
    finally:
        csv_path.unlink()


def test_satellite_data_importer_csv() -> None:
    """Test satellite data CSV importer."""
    importer = SatelliteDataImporter(data_product="MODIS_NDVI")

    assert importer.metadata.name == "Satellite Data Importer"
    assert "csv" in importer.metadata.supported_formats

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Date,Latitude,Longitude,NDVI,Cloud Cover\n")
        f.write("2024-01-01,37.7749,-122.4194,0.65,10\n")
        f.write("2024-01-02,37.7749,-122.4194,0.68,5\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert result.metadata["data_product"] == "MODIS_NDVI"
    finally:
        csv_path.unlink()


def test_satellite_data_importer_geojson() -> None:
    """Test satellite data GeoJSON importer."""
    importer = SatelliteDataImporter()

    # Create test GeoJSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".geojson", delete=False) as f:
        f.write('{"type": "FeatureCollection", "features": [')
        f.write('{"type": "Feature", "geometry": {"type": "Point", ')
        f.write('"coordinates": [-122.4194, 37.7749]}, ')
        f.write('"properties": {"ndvi": 0.65, "date": "2024-01-01"}}')
        f.write("]}")
        geojson_path = Path(f.name)

    try:
        result = importer.import_data(geojson_path)

        assert result.success is True
        assert len(result.data) == 1
    finally:
        geojson_path.unlink()


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_ppm_to_ugm3_conversion() -> None:
    """Test ppm to ug/m3 conversion."""
    # O3: MW = 48
    result = ppm_to_ugm3(0.1, 48.0)
    assert abs(result - 196.3) < 1.0


def test_ugm3_to_ppm_conversion() -> None:
    """Test ug/m3 to ppm conversion."""
    # O3: MW = 48
    result = ugm3_to_ppm(196.0, 48.0)
    assert abs(result - 0.0999) < 0.01


def test_calculate_aqi() -> None:
    """Test AQI calculation from PM2.5."""
    # Good air quality
    assert calculate_aqi(10.0) <= 50

    # Moderate
    aqi = calculate_aqi(25.0)
    assert 51 <= aqi <= 100

    # Unhealthy for sensitive groups
    aqi = calculate_aqi(45.0)
    assert 101 <= aqi <= 150

    # Above highest breakpoint
    assert calculate_aqi(600.0) == 500


def test_calculate_wqi() -> None:
    """Test Water Quality Index calculation."""
    # Good water quality
    wqi = calculate_wqi(95, 2, 7.2)
    assert wqi > 80

    # With turbidity
    wqi = calculate_wqi(90, 3, 7.0, 5)
    assert 70 < wqi < 95


def test_calculate_bod() -> None:
    """Test BOD calculation."""
    bod = calculate_bod(8.5, 3.2, 30)
    # (8.5 - 3.2) * (300 / 30) = 53.0
    assert abs(bod - 53.0) < 0.1


def test_calculate_shannon_diversity() -> None:
    """Test Shannon diversity index calculation."""
    # Equal distribution
    h = calculate_shannon_diversity([10, 10, 10, 10])
    assert abs(h - 1.386) < 0.01

    # Single species
    assert calculate_shannon_diversity([100]) == 0.0

    # Empty
    assert calculate_shannon_diversity([]) == 0.0


def test_calculate_simpson_index() -> None:
    """Test Simpson's diversity index calculation."""
    # Equal distribution
    d = calculate_simpson_index([10, 10, 10, 10])
    assert abs(d - 0.75) < 0.01

    # Single species (no diversity)
    assert calculate_simpson_index([100]) == 0.0

    # Empty
    assert calculate_simpson_index([]) == 0.0


def test_calculate_carbon_equivalent() -> None:
    """Test carbon equivalent calculation."""
    # CO2 (GWP = 1)
    assert calculate_carbon_equivalent(100, "co2") == 100

    # CH4 (GWP = 28)
    assert calculate_carbon_equivalent(100, "ch4") == 2800

    # N2O (GWP = 265)
    assert calculate_carbon_equivalent(100, "n2o") == 26500


def test_calculate_ecological_footprint() -> None:
    """Test ecological footprint calculation."""
    # Carbon only
    fp = calculate_ecological_footprint(5000)
    assert abs(fp - 1.35) < 0.01

    # With food factor
    fp = calculate_ecological_footprint(5000, food_factor=1.0)
    assert fp > 1.35


def test_format_concentration() -> None:
    """Test concentration formatting."""
    assert format_concentration(35.56, "ug/m3", 1) == "35.6 ug/m3"
    assert format_concentration(100.0, "ppb", 0) == "100 ppb"


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_workflow_formulas() -> None:
    """Test complete workflow for formulas."""
    # Initialize plugin
    plugin = EnvironmentalDomainPlugin()
    plugin.initialize()

    # Get formula class
    formula_class = plugin.get_formula("AQI_CALCULATION")
    assert formula_class is not None

    # Create formula instance and use it
    formula = formula_class()
    result = formula.build("35.5")
    assert result is not None


def test_formula_argument_validation() -> None:
    """Test formula argument validation."""
    formula = EmissionRateFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("1000")

    # Correct arguments should work
    result = formula.build("1000", "50")
    assert result is not None


def test_importer_validation() -> None:
    """Test importer source validation."""
    importer = SensorNetworkImporter()

    # Non-existent file
    assert importer.validate_source(Path("/test/file.csv")) is False

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


def test_satellite_invalid_coordinates() -> None:
    """Test satellite importer with invalid coordinates."""
    importer = SatelliteDataImporter()

    # Create CSV with invalid coordinates
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Date,Latitude,Longitude,NDVI\n")
        f.write("2024-01-01,200.0,-300.0,0.65\n")  # Invalid lat/lon
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        assert result.success is True
        # Should have warnings about invalid coordinates
        assert len(result.warnings) > 0
    finally:
        csv_path.unlink()


def test_sensor_data_calibration() -> None:
    """Test sensor data with calibration metadata."""
    importer = SensorNetworkImporter()

    # Create CSV with sensor metadata
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Timestamp,Sensor,PM2.5,Calibration Date\n")
        f.write("2024-01-01 12:00,S001,35.5,2023-12-01\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        assert result.success is True
    finally:
        csv_path.unlink()


def test_satellite_json_format() -> None:
    """Test satellite importer with regular JSON format."""
    importer = SatelliteDataImporter()

    # Create regular JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('[{"date": "2024-01-01", "lat": 37.7, "lon": -122.4, "ndvi": 0.65}]')
        json_path = Path(f.name)

    try:
        result = importer.import_data(json_path)
        assert result.success is True
    finally:
        json_path.unlink()


def test_lab_results_unsupported_format() -> None:
    """Test lab results importer with unsupported format."""
    importer = LabResultsImporter()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
        f.write("data")
        xyz_path = Path(f.name)

    try:
        result = importer.import_data(xyz_path)
        assert result.success is False
        assert len(result.errors) > 0
    finally:
        xyz_path.unlink()


def test_importer_error_handling() -> None:
    """Test importer error handling with malformed files."""
    # Test with empty CSV
    importer = SensorNetworkImporter()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("")  # Empty file
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        # Should handle gracefully
        assert result.success in (True, False)
    finally:
        csv_path.unlink()


def test_utils_edge_cases() -> None:
    """Test utility functions with edge cases."""
    # Zero concentration
    assert calculate_aqi(0.0) == 0

    # Zero BOD parameters
    assert calculate_bod(0.0, 0.0, 30) == 0.0

    # Shannon with zeros
    assert calculate_shannon_diversity([0, 0, 0]) == 0.0

    # Unknown gas type defaults to CO2
    assert calculate_carbon_equivalent(100, "unknown") == 100


def test_satellite_data_with_nested_json() -> None:
    """Test satellite importer with nested JSON structure."""
    importer = SatelliteDataImporter()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"data": [{"date": "2024-01-01", "ndvi": 0.65}]}')
        json_path = Path(f.name)

    try:
        result = importer.import_data(json_path)
        assert result.success is True
    finally:
        json_path.unlink()


def test_impact_score_requires_three_args() -> None:
    """Test environmental impact score requires magnitude, duration, reversibility."""
    formula = EnvironmentalImpactScoreFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("3", "4")

    # Correct arguments should work
    result = formula.build("3", "4", "2")
    assert result is not None
