"""Education Domain Plugin for SpreadsheetDL.

    Education domain plugin
    PHASE-C: Domain plugin implementations

Provides education-specific functionality including:
- Grade calculation formulas (average, weighted, curve)
- Statistical analysis formulas (standard deviation, percentile)
- Learning metrics (mastery level, learning gain, completion rate)
- LMS data, gradebook export, and assessment results importers

Example:
    >>> from spreadsheet_dl.domains.education import EducationDomainPlugin
    >>> plugin = EducationDomainPlugin()
    >>> plugin.initialize()
"""

# Plugin
# Formulas - Import all from formulas package
from spreadsheet_dl.domains.education.formulas import (
    AttendanceRateFormula,
    Bloom2SigmaFormula,
    BloomTaxonomyLevelFormula,
    CompletionRateFormula,
    CorrelationFormula,
    CronbachAlpha,
    CurveGradesFormula,
    ForgettingCurveFormula,
    GradeAverageFormula,
    GradeCurveFormula,
    ItemDifficulty,
    ItemDiscrimination,
    KR20Formula,
    KR21Formula,
    LearningCurveFormula,
    LearningGainFormula,
    MasteryLearningFormula,
    MasteryLevelFormula,
    PassFailThresholdFormula,
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

# Importers
from spreadsheet_dl.domains.education.importers import (
    AssessmentResultsImporter,
    GradebookExportImporter,
    LMSDataImporter,
)
from spreadsheet_dl.domains.education.plugin import EducationDomainPlugin

# Utils
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

__all__ = [
    "AssessmentResultsImporter",
    "AttendanceRateFormula",
    "Bloom2SigmaFormula",
    "BloomTaxonomyLevelFormula",
    "CompletionRateFormula",
    "CorrelationFormula",
    "CronbachAlpha",
    "CurveGradesFormula",
    "EducationDomainPlugin",
    "ForgettingCurveFormula",
    "GradeAverageFormula",
    "GradeCurveFormula",
    "GradebookExportImporter",
    "ItemDifficulty",
    "ItemDiscrimination",
    "KR20Formula",
    "KR21Formula",
    "LMSDataImporter",
    "LearningCurveFormula",
    "LearningGainFormula",
    "MasteryLearningFormula",
    "MasteryLevelFormula",
    "PassFailThresholdFormula",
    "PercentileRankFormula",
    "PercentileRankGradeFormula",
    "ReadabilityScoreFormula",
    "RubricScoreFormula",
    "SpacedRepetitionFormula",
    "SpearmanBrownFormula",
    "StandardDeviationFormula",
    "StandardErrorMeasurementFormula",
    "StandardScoreFormula",
    "TimeOnTaskFormula",
    "TrueScoreFormula",
    "WeightedGPAFormula",
    "WeightedGradeFormula",
    "calculate_attendance_rate",
    "calculate_gpa",
    "calculate_grade_average",
    "calculate_letter_grade",
    "calculate_weighted_grade",
    "format_percentage",
    "grade_to_points",
    "points_to_grade",
]
