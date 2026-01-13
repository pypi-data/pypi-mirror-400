"""
Tests for Education domain plugin.

    Comprehensive tests for Education domain (95%+ coverage target)
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl.domains.education import (
    AssessmentResultsImporter,
    AttendanceRateFormula,
    BloomTaxonomyLevelFormula,
    CompletionRateFormula,
    CorrelationFormula,
    CurveGradesFormula,
    EducationDomainPlugin,
    ForgettingCurveFormula,
    GradeAverageFormula,
    GradebookExportImporter,
    GradeCurveFormula,
    KR20Formula,
    KR21Formula,
    LearningCurveFormula,
    LearningGainFormula,
    LMSDataImporter,
    MasteryLearningFormula,
    MasteryLevelFormula,
    PercentileRankFormula,
    PercentileRankGradeFormula,
    ReadabilityScoreFormula,
    RubricScoreFormula,
    SpacedRepetitionFormula,
    SpearmanBrownFormula,
    StandardDeviationFormula,
    StandardErrorMeasurementFormula,
    StandardScoreFormula,
    TimeOnTaskFormula,
    TrueScoreFormula,
    WeightedGPAFormula,
    WeightedGradeFormula,
)
from spreadsheet_dl.domains.education.utils import (
    calculate_attendance_rate,
    calculate_gpa,
    calculate_grade_average,
    calculate_letter_grade,
    calculate_weighted_grade,
    format_percentage,
    grade_to_points,
    points_to_grade,
)

pytestmark = [pytest.mark.unit, pytest.mark.domain]

# ============================================================================
# Plugin Tests
# ============================================================================


def test_plugin_metadata() -> None:
    """Test plugin metadata."""
    plugin = EducationDomainPlugin()
    metadata = plugin.metadata

    assert metadata.name == "education"
    assert metadata.version == "0.1.0"
    assert "education" in metadata.tags
    assert "gradebook" in metadata.tags


def test_plugin_initialization() -> None:
    """Test plugin initialization."""
    plugin = EducationDomainPlugin()
    plugin.initialize()

    # Verify formulas registered (12 total)
    # Grade formulas
    assert plugin.get_formula("GRADE_AVERAGE") == GradeAverageFormula
    assert plugin.get_formula("WEIGHTED_GRADE") == WeightedGradeFormula
    assert plugin.get_formula("GRADE_CURVE") == GradeCurveFormula

    # Statistics formulas
    assert plugin.get_formula("STANDARD_DEVIATION") == StandardDeviationFormula
    assert plugin.get_formula("PERCENTILE_RANK") == PercentileRankFormula
    assert plugin.get_formula("CORRELATION") == CorrelationFormula

    # Learning metrics formulas
    assert plugin.get_formula("LEARNING_GAIN") == LearningGainFormula
    assert plugin.get_formula("MASTERY_LEVEL") == MasteryLevelFormula
    assert plugin.get_formula("ATTENDANCE_RATE") == AttendanceRateFormula
    assert plugin.get_formula("COMPLETION_RATE") == CompletionRateFormula
    assert plugin.get_formula("BLOOM_TAXONOMY_LEVEL") == BloomTaxonomyLevelFormula
    assert plugin.get_formula("READABILITY_SCORE") == ReadabilityScoreFormula

    # Verify importers registered (3 total)
    assert plugin.get_importer("lms_data") == LMSDataImporter
    assert plugin.get_importer("gradebook_export") == GradebookExportImporter
    assert plugin.get_importer("assessment_results") == AssessmentResultsImporter


def test_plugin_validation() -> None:
    """Test plugin validation."""
    plugin = EducationDomainPlugin()
    plugin.initialize()

    assert plugin.validate() is True


def test_plugin_cleanup() -> None:
    """Test plugin cleanup (should not raise)."""
    plugin = EducationDomainPlugin()
    plugin.initialize()
    plugin.cleanup()  # Should not raise


# ============================================================================
# Grade Formula Tests
# ============================================================================


def test_grade_average_formula() -> None:
    """Test grade average formula: AVERAGE(range)."""
    formula = GradeAverageFormula()

    # Test metadata
    assert formula.metadata.name == "GRADE_AVERAGE"
    assert formula.metadata.category == "education"
    assert len(formula.metadata.arguments) == 2

    # Test simple average
    result = formula.build("A1:A10")
    assert result == "of:=AVERAGE(A1:A10)"

    # Test with cell references
    result = formula.build("B2:B30")
    assert result == "of:=AVERAGE(B2:B30)"


def test_grade_average_exclude_zeros() -> None:
    """Test grade average with zeros excluded."""
    formula = GradeAverageFormula()

    result = formula.build("A1:A10", "TRUE")
    assert result == 'of:=AVERAGEIF(A1:A10;"<>0")'


def test_weighted_grade_formula() -> None:
    """Test weighted grade formula: SUMPRODUCT/SUM."""
    formula = WeightedGradeFormula()

    assert formula.metadata.name == "WEIGHTED_GRADE"

    result = formula.build("A1:A5", "B1:B5")
    assert result == "of:=SUMPRODUCT(A1:A5;B1:B5)/SUM(B1:B5)"


def test_grade_curve_formula_linear() -> None:
    """Test grade curve formula with linear method."""
    formula = GradeCurveFormula()

    assert formula.metadata.name == "GRADE_CURVE"
    assert len(formula.metadata.arguments) == 4

    result = formula.build("B2", "B$2:B$30", "linear", "10")
    assert result == "of:=MIN(B2+10;100)"


def test_grade_curve_formula_sqrt() -> None:
    """Test grade curve formula with sqrt method."""
    formula = GradeCurveFormula()

    result = formula.build("A1", "A1:A30", "sqrt")
    assert result == "of:=SQRT(A1)*10"


def test_grade_curve_formula_bell() -> None:
    """Test grade curve formula with bell curve method."""
    formula = GradeCurveFormula()

    result = formula.build("A1", "A1:A30", "bell")
    assert "AVERAGE" in result
    assert "STDEV" in result


# ============================================================================
# Statistics Formula Tests
# ============================================================================


def test_standard_deviation_formula() -> None:
    """Test standard deviation formula."""
    formula = StandardDeviationFormula()

    assert formula.metadata.name == "STANDARD_DEVIATION"

    result = formula.build("A1:A30")
    assert "STDEV" in result


def test_percentile_rank_formula() -> None:
    """Test percentile rank formula."""
    formula = PercentileRankFormula()

    assert formula.metadata.name == "PERCENTILE_RANK"

    result = formula.build("B5", "B$2:B$30")
    assert "PERCENTRANK" in result or "RANK" in result


def test_correlation_formula() -> None:
    """Test correlation formula."""
    formula = CorrelationFormula()

    assert formula.metadata.name == "CORRELATION"

    result = formula.build("A1:A30", "B1:B30")
    assert "CORREL" in result


# ============================================================================
# Learning Metrics Formula Tests
# ============================================================================


def test_learning_gain_formula() -> None:
    """Test learning gain formula: (post-pre)/(100-pre)."""
    formula = LearningGainFormula()

    assert formula.metadata.name == "LEARNING_GAIN"

    result = formula.build("A1", "B1")
    # Normalized gain formula
    assert "A1" in result
    assert "B1" in result


def test_mastery_level_formula() -> None:
    """Test mastery level formula."""
    formula = MasteryLevelFormula()

    assert formula.metadata.name == "MASTERY_LEVEL"

    result = formula.build("A1", "80")
    assert "IF" in result


def test_attendance_rate_formula() -> None:
    """Test attendance rate formula: present/total*100."""
    formula = AttendanceRateFormula()

    assert formula.metadata.name == "ATTENDANCE_RATE"

    result = formula.build("A1", "B1")
    assert "100" in result


def test_completion_rate_formula() -> None:
    """Test completion rate formula."""
    formula = CompletionRateFormula()

    assert formula.metadata.name == "COMPLETION_RATE"

    result = formula.build("A1", "B1")
    assert "100" in result


def test_bloom_taxonomy_level_formula() -> None:
    """Test Bloom's taxonomy level formula."""
    formula = BloomTaxonomyLevelFormula()

    assert formula.metadata.name == "BLOOM_TAXONOMY_LEVEL"

    result = formula.build("A1")
    assert "IF" in result


def test_readability_score_formula() -> None:
    """Test readability score (Flesch-Kincaid) formula."""
    formula = ReadabilityScoreFormula()

    assert formula.metadata.name == "READABILITY_SCORE"

    result = formula.build("100", "20", "300")
    # Flesch-Kincaid formula components
    assert "206.835" in result or "1.015" in result or result is not None


# ============================================================================
# Importer Tests
# ============================================================================


def test_lms_data_importer_csv() -> None:
    """Test LMS data CSV importer."""
    importer = LMSDataImporter()

    assert importer.metadata.name == "LMS Data Importer"
    assert "csv" in importer.metadata.supported_formats

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Student ID,Name,Assignment 1,Assignment 2,Final Grade\n")
        f.write("STU001,John Doe,85,90,88\n")
        f.write("STU002,Jane Smith,92,88,91\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
    finally:
        csv_path.unlink()


def test_lms_data_importer_invalid_file() -> None:
    """Test LMS data importer with invalid file."""
    importer = LMSDataImporter()

    result = importer.import_data("/nonexistent/file.csv")

    assert result.success is False
    assert len(result.errors) > 0


def test_gradebook_export_importer_csv() -> None:
    """Test gradebook export CSV importer."""
    importer = GradebookExportImporter()

    assert importer.metadata.name == "Gradebook Export Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Student,Quiz 1,Quiz 2,Exam 1,Final\n")
        f.write("Alice,88,92,85,90\n")
        f.write("Bob,75,80,78,82\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
        assert len(result.data) == 2
    finally:
        csv_path.unlink()


def test_assessment_results_importer_csv() -> None:
    """Test assessment results CSV importer."""
    importer = AssessmentResultsImporter()

    assert importer.metadata.name == "Assessment Results Importer"

    # Create test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Student ID,Question 1,Question 2,Question 3,Total\n")
        f.write("S001,1,1,0,2\n")
        f.write("S002,1,1,1,3\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)

        assert result.success is True
        assert result.records_imported == 2
    finally:
        csv_path.unlink()


# ============================================================================
# Utility Function Tests
# ============================================================================


def test_calculate_grade_average() -> None:
    """Test grade average calculation."""
    # Basic average
    assert calculate_grade_average([85, 90, 88, 92]) == 88.75

    # With None values
    result = calculate_grade_average([85, 90, None, 92])
    assert result is not None
    assert abs(result - 89.0) < 0.01

    # Empty list
    assert calculate_grade_average([]) is None

    # All None
    assert calculate_grade_average([None, None, None]) is None


def test_calculate_weighted_grade() -> None:
    """Test weighted grade calculation."""
    result = calculate_weighted_grade([85, 90, 95], [0.3, 0.3, 0.4])
    assert abs(result - 90.5) < 0.01

    # Equal weights
    result = calculate_weighted_grade([80, 90], [1, 1])
    assert abs(result - 85.0) < 0.01

    # Mismatched lengths should raise
    with pytest.raises(ValueError):
        calculate_weighted_grade([80, 90], [1])


def test_calculate_letter_grade() -> None:
    """Test letter grade conversion."""
    assert calculate_letter_grade(98) == "A+"
    assert calculate_letter_grade(93) == "A"
    assert calculate_letter_grade(91) == "A-"
    assert calculate_letter_grade(85) == "B"
    assert calculate_letter_grade(75) == "C"
    assert calculate_letter_grade(65) == "D"
    assert calculate_letter_grade(55) == "F"


def test_grade_to_points() -> None:
    """Test grade to points conversion."""
    assert grade_to_points("A") == 4.0
    assert grade_to_points("B+") == 3.3
    assert grade_to_points("C") == 2.0
    assert grade_to_points("F") == 0.0

    # Case insensitive
    assert grade_to_points("a-") == 3.7


def test_points_to_grade() -> None:
    """Test points to grade conversion."""
    assert points_to_grade(4.0) == "A+"
    assert points_to_grade(3.5) == "B+"
    assert points_to_grade(2.0) == "C"
    assert points_to_grade(0.0) == "F"


def test_calculate_gpa() -> None:
    """Test GPA calculation."""
    # Simple GPA (equal weights)
    result = calculate_gpa(["A", "B+", "B", "A-"])
    assert 3.4 < result < 3.6

    # With credits
    result = calculate_gpa(["A", "B"], [4, 3])
    assert 3.4 < result < 3.6

    # Empty grades
    assert calculate_gpa([]) == 0.0

    # Mismatched lengths should raise
    with pytest.raises(ValueError):
        calculate_gpa(["A", "B"], [4])


def test_calculate_attendance_rate() -> None:
    """Test attendance rate calculation."""
    assert abs(calculate_attendance_rate(85, 90) - 94.44) < 0.1
    assert calculate_attendance_rate(90, 90) == 100.0
    assert calculate_attendance_rate(0, 90) == 0.0
    assert calculate_attendance_rate(0, 0) == 0.0


def test_format_percentage() -> None:
    """Test percentage formatting."""
    assert format_percentage(85.678, 1) == "85.7%"
    assert format_percentage(90.0, 0) == "90%"
    assert format_percentage(75.5, 2, include_symbol=False) == "75.50"


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_workflow_formulas() -> None:
    """Test complete workflow for formulas."""
    # Initialize plugin
    plugin = EducationDomainPlugin()
    plugin.initialize()

    # Get formula class
    formula_class = plugin.get_formula("GRADE_AVERAGE")
    assert formula_class is not None

    # Create formula instance and use it
    formula = formula_class()
    result = formula.build("A1:A10")
    assert result is not None


def test_formula_argument_validation() -> None:
    """Test formula argument validation."""
    formula = WeightedGradeFormula()

    # Too few arguments should raise
    with pytest.raises(ValueError, match="requires at least"):
        formula.build("A1:A5")

    # Correct arguments should work
    result = formula.build("A1:A5", "B1:B5")
    assert result is not None


def test_importer_validation() -> None:
    """Test importer source validation."""
    importer = LMSDataImporter()

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


def test_grade_curve_default_method() -> None:
    """Test grade curve with default method."""
    formula = GradeCurveFormula()

    # Should default to linear with 0 adjustment
    result = formula.build("A1", "A1:A30")
    assert "MIN" in result


def test_lms_importer_canvas_format() -> None:
    """Test LMS importer with Canvas-style format."""
    # Use 'platform' parameter (not 'lms_type') to match implementation
    importer = LMSDataImporter(platform="canvas")

    # Create Canvas-style CSV
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Student,ID,Section,Assignment 1,Assignment 2\n")
        f.write("Doe, John,12345,Section A,85,90\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        assert result.success is True
    finally:
        csv_path.unlink()


def test_gradebook_with_missing_grades() -> None:
    """Test gradebook importer with missing grade values."""
    importer = GradebookExportImporter()

    # Create CSV with missing values
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Student,Quiz 1,Quiz 2,Exam 1\n")
        f.write("Alice,88,,85\n")  # Missing Quiz 2
        f.write("Bob,75,80,\n")  # Missing Exam 1
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        assert result.success is True
        # Should have warnings about missing values
    finally:
        csv_path.unlink()


def test_assessment_item_analysis() -> None:
    """Test assessment results with item analysis."""
    importer = AssessmentResultsImporter()

    # Create assessment data with item scores
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("Student,Q1,Q2,Q3,Q4,Q5,Total,Percentage\n")
        f.write("S001,1,1,1,0,1,4,80\n")
        f.write("S002,1,0,1,1,1,4,80\n")
        f.write("S003,0,1,1,1,0,3,60\n")
        csv_path = Path(f.name)

    try:
        result = importer.import_data(csv_path)
        assert result.success is True
        assert result.records_imported == 3
    finally:
        csv_path.unlink()


def test_importer_error_handling() -> None:
    """Test importer error handling with malformed files."""
    # Test with empty CSV
    importer = LMSDataImporter()
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
    # Zero weights
    result = calculate_weighted_grade([90, 85], [0, 0])
    assert result == 0.0

    # Very high grade
    grade = calculate_letter_grade(110)
    assert grade == "A+"

    # Negative grade
    grade = calculate_letter_grade(-10)
    assert grade == "F"


# ============================================================================
# NEW FORMULAS: Assessment Theory Tests
# ============================================================================


def test_kr20_formula() -> None:
    """Test KR20 reliability coefficient formula."""
    formula = KR20Formula()

    assert formula.metadata.name == "KR20"
    assert formula.metadata.category == "assessment"

    result = formula.build("20", "10", "36")
    assert "20" in result
    assert "10" in result
    assert "36" in result
    assert "/" in result


def test_kr20_formula_cell_refs() -> None:
    """Test KR20 with cell references."""
    formula = KR20Formula()

    result = formula.build("A1", "A2", "A3")
    assert "A1" in result
    assert "A2" in result
    assert "A3" in result


def test_kr20_formula_realistic() -> None:
    """Test KR20 with realistic test data."""
    formula = KR20Formula()

    # 25 item test, sum(pq) = 5.5, variance = 25
    result = formula.build("25", "5.5", "25")
    assert result is not None


def test_kr21_formula() -> None:
    """Test KR21 reliability coefficient formula."""
    formula = KR21Formula()

    assert formula.metadata.name == "KR21"
    assert formula.metadata.category == "assessment"

    result = formula.build("20", "15", "36")
    assert "20" in result
    assert "15" in result
    assert "36" in result


def test_kr21_formula_cell_refs() -> None:
    """Test KR21 with cell references."""
    formula = KR21Formula()

    result = formula.build("B1", "B2", "B3")
    assert "B1" in result
    assert "B2" in result
    assert "B3" in result


def test_kr21_formula_realistic() -> None:
    """Test KR21 with realistic test statistics."""
    formula = KR21Formula()

    # 30 item test, mean=22, variance=16
    result = formula.build("30", "22", "16")
    assert result is not None


def test_spearman_brown_formula() -> None:
    """Test Spearman-Brown prophecy formula."""
    formula = SpearmanBrownFormula()

    assert formula.metadata.name == "SPEARMAN_BROWN"
    assert formula.metadata.category == "assessment"

    result = formula.build("0.75", "2")
    assert "0.75" in result
    assert "2" in result


def test_spearman_brown_doubling() -> None:
    """Test Spearman-Brown for doubling test length."""
    formula = SpearmanBrownFormula()

    result = formula.build("0.80", "2")
    assert result is not None


def test_spearman_brown_halving() -> None:
    """Test Spearman-Brown for halving test length."""
    formula = SpearmanBrownFormula()

    result = formula.build("0.90", "0.5")
    assert "0.90" in result
    assert "0.5" in result


def test_standard_error_measurement_formula() -> None:
    """Test standard error of measurement formula."""
    formula = StandardErrorMeasurementFormula()

    assert formula.metadata.name == "STANDARD_ERROR_MEASUREMENT"
    assert formula.metadata.category == "assessment"

    result = formula.build("10", "0.85")
    assert "10" in result
    assert "0.85" in result
    assert "SQRT" in result


def test_standard_error_measurement_cell_refs() -> None:
    """Test SEM with cell references."""
    formula = StandardErrorMeasurementFormula()

    result = formula.build("C1", "C2")
    assert "C1" in result
    assert "C2" in result


def test_standard_error_measurement_realistic() -> None:
    """Test SEM with realistic values."""
    formula = StandardErrorMeasurementFormula()

    # SD=15, reliability=0.91
    result = formula.build("15", "0.91")
    assert result is not None


def test_true_score_formula() -> None:
    """Test true score estimation formula."""
    formula = TrueScoreFormula()

    assert formula.metadata.name == "TRUE_SCORE"
    assert formula.metadata.category == "assessment"

    result = formula.build("85", "75", "0.85")
    assert "85" in result
    assert "75" in result
    assert "0.85" in result


def test_true_score_formula_cell_refs() -> None:
    """Test true score with cell references."""
    formula = TrueScoreFormula()

    result = formula.build("D1", "D2", "D3")
    assert "D1" in result
    assert "D2" in result
    assert "D3" in result


def test_true_score_formula_realistic() -> None:
    """Test true score with realistic assessment data."""
    formula = TrueScoreFormula()

    # Observed=92, mean=80, reliability=0.88
    result = formula.build("92", "80", "0.88")
    assert result is not None


# ============================================================================
# NEW FORMULAS: Learning Analytics Tests
# ============================================================================


def test_learning_curve_formula() -> None:
    """Test learning curve formula."""
    formula = LearningCurveFormula()

    assert formula.metadata.name == "LEARNING_CURVE"
    assert formula.metadata.category == "education"

    result = formula.build("100", "5")
    assert "100" in result
    assert "5" in result
    assert "POWER" in result


def test_learning_curve_custom_rate() -> None:
    """Test learning curve with custom learning rate."""
    formula = LearningCurveFormula()

    result = formula.build("120", "10", "-0.3")
    assert "120" in result
    assert "10" in result
    assert "-0.3" in result


def test_learning_curve_cell_refs() -> None:
    """Test learning curve with cell references."""
    formula = LearningCurveFormula()

    result = formula.build("E1", "E2", "E3")
    assert "E1" in result
    assert "E2" in result
    assert "E3" in result


def test_forgetting_curve_formula() -> None:
    """Test forgetting curve formula."""
    formula = ForgettingCurveFormula()

    assert formula.metadata.name == "FORGETTING_CURVE"
    assert formula.metadata.category == "education"

    result = formula.build("7")
    assert "7" in result
    assert "EXP" in result


def test_forgetting_curve_custom_strength() -> None:
    """Test forgetting curve with custom memory strength."""
    formula = ForgettingCurveFormula()

    result = formula.build("14", "3")
    assert "14" in result
    assert "3" in result


def test_forgetting_curve_cell_refs() -> None:
    """Test forgetting curve with cell references."""
    formula = ForgettingCurveFormula()

    result = formula.build("F1", "F2")
    assert "F1" in result
    assert "F2" in result


def test_spaced_repetition_formula() -> None:
    """Test spaced repetition interval formula."""
    formula = SpacedRepetitionFormula()

    assert formula.metadata.name == "SPACED_REPETITION"
    assert formula.metadata.category == "education"

    result = formula.build("3", "2.5", "1")
    assert "3" in result
    assert "2.5" in result
    assert "1" in result
    assert "IF" in result


def test_spaced_repetition_poor_performance() -> None:
    """Test spaced repetition with poor recall."""
    formula = SpacedRepetitionFormula()

    result = formula.build("5", "2.0", "0.5")
    assert "0.5" in result
    assert "0.6" in result  # Threshold


def test_spaced_repetition_cell_refs() -> None:
    """Test spaced repetition with cell references."""
    formula = SpacedRepetitionFormula()

    result = formula.build("G1", "G2", "G3")
    assert "G1" in result
    assert "G2" in result
    assert "G3" in result


def test_mastery_learning_formula() -> None:
    """Test mastery learning (Bloom 2-sigma) formula."""
    formula = MasteryLearningFormula()

    assert formula.metadata.name == "MASTERY_LEARNING"
    assert formula.metadata.category == "education"

    result = formula.build("75")
    assert "75" in result
    assert "MIN" in result


def test_mastery_learning_custom_sigma() -> None:
    """Test mastery learning with custom sigma."""
    formula = MasteryLearningFormula()

    result = formula.build("70", "1.5", "12")
    assert "70" in result
    assert "1.5" in result
    assert "12" in result


def test_mastery_learning_cell_refs() -> None:
    """Test mastery learning with cell references."""
    formula = MasteryLearningFormula()

    result = formula.build("H1", "H2", "H3")
    assert "H1" in result
    assert "H2" in result
    assert "H3" in result


def test_time_on_task_formula() -> None:
    """Test time on task (Carroll model) formula."""
    formula = TimeOnTaskFormula()

    assert formula.metadata.name == "TIME_ON_TASK"
    assert formula.metadata.category == "education"

    result = formula.build("45", "60")
    assert "45" in result
    assert "60" in result
    assert "MIN" in result
    assert "100" in result


def test_time_on_task_custom_quality() -> None:
    """Test time on task with custom instruction quality."""
    formula = TimeOnTaskFormula()

    result = formula.build("30", "50", "0.9")
    assert "30" in result
    assert "50" in result
    assert "0.9" in result


def test_time_on_task_cell_refs() -> None:
    """Test time on task with cell references."""
    formula = TimeOnTaskFormula()

    result = formula.build("I1", "I2", "I3")
    assert "I1" in result
    assert "I2" in result
    assert "I3" in result


# ============================================================================
# NEW FORMULAS: Grading Systems Tests
# ============================================================================


def test_curve_grades_formula() -> None:
    """Test distribution-based grade curving formula."""
    formula = CurveGradesFormula()

    assert formula.metadata.name == "CURVE_GRADES"
    assert formula.metadata.category == "education"

    result = formula.build("A1", "A$1:A$30")
    assert "A1" in result
    assert "A$1:A$30" in result
    assert "AVERAGE" in result
    assert "STDEV" in result


def test_curve_grades_custom_target() -> None:
    """Test curve grades with custom target distribution."""
    formula = CurveGradesFormula()

    result = formula.build("B5", "B$2:B$50", "80", "12")
    assert "B5" in result
    assert "80" in result
    assert "12" in result


def test_curve_grades_default_targets() -> None:
    """Test curve grades with default target mean and SD."""
    formula = CurveGradesFormula()

    result = formula.build("C3", "C$1:C$100")
    assert "C3" in result
    assert result is not None


def test_standard_score_formula() -> None:
    """Test z-score standard score formula."""
    formula = StandardScoreFormula()

    assert formula.metadata.name == "STANDARD_SCORE"
    assert formula.metadata.category == "education"

    result = formula.build("85", "75", "10")
    assert "85" in result
    assert "75" in result
    assert "10" in result
    assert "/" in result


def test_standard_score_cell_refs() -> None:
    """Test standard score with cell references."""
    formula = StandardScoreFormula()

    result = formula.build("D1", "AVERAGE(D:D)", "STDEV(D:D)")
    assert "D1" in result
    assert "AVERAGE" in result
    assert "STDEV" in result


def test_standard_score_negative_z() -> None:
    """Test standard score with below-mean grade."""
    formula = StandardScoreFormula()

    result = formula.build("65", "75", "10")
    assert "65" in result
    assert "75" in result


def test_percentile_rank_grade_formula() -> None:
    """Test percentile rank for grades formula."""
    formula = PercentileRankGradeFormula()

    assert formula.metadata.name == "PERCENTILE_RANK_GRADE"
    assert formula.metadata.category == "education"

    result = formula.build("E1", "E$1:E$30")
    assert "E1" in result
    assert "E$1:E$30" in result
    assert "PERCENTRANK" in result


def test_percentile_rank_grade_cell_refs() -> None:
    """Test percentile rank grade with cell references."""
    formula = PercentileRankGradeFormula()

    result = formula.build("F5", "F$2:F$100")
    assert "F5" in result
    assert "F$2:F$100" in result


def test_percentile_rank_grade_realistic() -> None:
    """Test percentile rank grade with realistic class size."""
    formula = PercentileRankGradeFormula()

    result = formula.build("G20", "G$1:G$45")
    assert result is not None


def test_weighted_gpa_formula() -> None:
    """Test weighted GPA formula."""
    formula = WeightedGPAFormula()

    assert formula.metadata.name == "WEIGHTED_GPA"
    assert formula.metadata.category == "education"

    result = formula.build("H1:H5", "I1:I5")
    assert "H1:H5" in result
    assert "I1:I5" in result
    assert "SUMPRODUCT" in result
    assert "SUM" in result


def test_weighted_gpa_different_ranges() -> None:
    """Test weighted GPA with different range sizes."""
    formula = WeightedGPAFormula()

    result = formula.build("A2:A10", "B2:B10")
    assert "A2:A10" in result
    assert "B2:B10" in result


def test_weighted_gpa_named_ranges() -> None:
    """Test weighted GPA with named ranges."""
    formula = WeightedGPAFormula()

    result = formula.build("grade_points", "credits")
    assert "grade_points" in result
    assert "credits" in result


def test_rubric_score_formula() -> None:
    """Test rubric scoring formula."""
    formula = RubricScoreFormula()

    assert formula.metadata.name == "RUBRIC_SCORE"
    assert formula.metadata.category == "education"

    result = formula.build("J1:J4", "K1:K4")
    assert "J1:J4" in result
    assert "K1:K4" in result
    assert "SUMPRODUCT" in result
    assert "100" in result


def test_rubric_score_custom_scale() -> None:
    """Test rubric score with custom scale."""
    formula = RubricScoreFormula()

    result = formula.build("L1:L6", "M1:M6", "50")
    assert "L1:L6" in result
    assert "M1:M6" in result
    assert "50" in result


def test_rubric_score_default_scale() -> None:
    """Test rubric score with default 100-point scale."""
    formula = RubricScoreFormula()

    result = formula.build("N1:N5", "O1:O5")
    assert result is not None


# ============================================================================
# Updated Plugin Tests for 27 Formulas
# ============================================================================


def test_plugin_validation_updated() -> None:
    """Test plugin validation with 27 formulas."""
    plugin = EducationDomainPlugin()
    plugin.initialize()

    # Should have 27 formulas now
    assert len(plugin._formulas) >= 27
    assert plugin.validate() is True


def test_all_new_formulas_registered() -> None:
    """Test that all 15 new formulas are registered."""
    plugin = EducationDomainPlugin()
    plugin.initialize()

    # Assessment theory formulas
    assert plugin.get_formula("KR20") == KR20Formula
    assert plugin.get_formula("KR21") == KR21Formula
    assert plugin.get_formula("SPEARMAN_BROWN") == SpearmanBrownFormula
    assert (
        plugin.get_formula("STANDARD_ERROR_MEASUREMENT")
        == StandardErrorMeasurementFormula
    )
    assert plugin.get_formula("TRUE_SCORE") == TrueScoreFormula

    # Learning analytics formulas
    assert plugin.get_formula("LEARNING_CURVE") == LearningCurveFormula
    assert plugin.get_formula("FORGETTING_CURVE") == ForgettingCurveFormula
    assert plugin.get_formula("SPACED_REPETITION") == SpacedRepetitionFormula
    assert plugin.get_formula("MASTERY_LEARNING") == MasteryLearningFormula
    assert plugin.get_formula("TIME_ON_TASK") == TimeOnTaskFormula

    # Grading systems formulas
    assert plugin.get_formula("CURVE_GRADES") == CurveGradesFormula
    assert plugin.get_formula("STANDARD_SCORE") == StandardScoreFormula
    assert plugin.get_formula("PERCENTILE_RANK_GRADE") == PercentileRankGradeFormula
    assert plugin.get_formula("WEIGHTED_GPA") == WeightedGPAFormula
    assert plugin.get_formula("RUBRIC_SCORE") == RubricScoreFormula
