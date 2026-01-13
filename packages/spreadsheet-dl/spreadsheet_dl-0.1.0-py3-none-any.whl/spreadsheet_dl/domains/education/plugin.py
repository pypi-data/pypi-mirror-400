"""Education Domain Plugin for SpreadsheetDL.

    Education domain plugin
    PHASE-C: Domain plugin implementations

Provides education-specific functionality including:
- Grade calculation and learning metrics formulas
- LMS data, gradebook export, and assessment results importers
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas
from spreadsheet_dl.domains.education.formulas.assessment import (
    KR20Formula,
    KR21Formula,
    SpearmanBrownFormula,
    StandardErrorMeasurementFormula,
    TrueScoreFormula,
)
from spreadsheet_dl.domains.education.formulas.grades import (
    CurveGradesFormula,
    GradeAverageFormula,
    GradeCurveFormula,
    RubricScoreFormula,
    StandardScoreFormula,
    WeightedGPAFormula,
    WeightedGradeFormula,
)
from spreadsheet_dl.domains.education.formulas.grades import (
    PercentileRankFormula as PercentileRankGradeFormula,
)
from spreadsheet_dl.domains.education.formulas.learning import (
    AttendanceRateFormula,
    BloomTaxonomyLevelFormula,
    CompletionRateFormula,
    ForgettingCurveFormula,
    LearningCurveFormula,
    LearningGainFormula,
    MasteryLearningFormula,
    MasteryLevelFormula,
    ReadabilityScoreFormula,
    SpacedRepetitionFormula,
    TimeOnTaskFormula,
)
from spreadsheet_dl.domains.education.formulas.statistics import (
    CorrelationFormula,
    PercentileRankFormula,
    StandardDeviationFormula,
)

# Import importers
from spreadsheet_dl.domains.education.importers.assessment_results import (
    AssessmentResultsImporter,
)
from spreadsheet_dl.domains.education.importers.gradebook_export import (
    GradebookExportImporter,
)
from spreadsheet_dl.domains.education.importers.lms_data import LMSDataImporter


class EducationDomainPlugin(BaseDomainPlugin):
    """Education domain plugin.

        Complete Education domain plugin
        PHASE-C: Domain plugin implementations

    Provides comprehensive education functionality for SpreadsheetDL
    with formulas and importers tailored for academic and educational workflows.

    Formulas (27 total):
        Grade Calculations (8):
        - GRADE_AVERAGE: Simple grade average
        - WEIGHTED_GRADE: Weighted grade calculation
        - GRADE_CURVE: Grade curve adjustment
        - CURVE_GRADES: Distribution-based curve
        - STANDARD_SCORE: Z-score transformation
        - PERCENTILE_RANK_GRADE: Percentile rank
        - WEIGHTED_GPA: Credit-weighted GPA
        - RUBRIC_SCORE: Criteria-based scoring

        Statistics (3):
        - STANDARD_DEVIATION: Standard deviation of grades
        - PERCENTILE_RANK: Percentile ranking
        - CORRELATION: Correlation coefficient

        Learning Metrics (11):
        - LEARNING_GAIN: Pre/post learning gain
        - MASTERY_LEVEL: Mastery-based grading level
        - ATTENDANCE_RATE: Student attendance rate
        - COMPLETION_RATE: Assignment completion rate
        - BLOOM_TAXONOMY_LEVEL: Bloom's taxonomy categorization
        - READABILITY_SCORE: Text readability (Flesch-Kincaid)
        - LEARNING_CURVE: Performance improvement over time
        - FORGETTING_CURVE: Ebbinghaus retention decay
        - SPACED_REPETITION: Optimal review interval
        - MASTERY_LEARNING: Bloom 2-sigma effect
        - TIME_ON_TASK: Carroll model learning

        Assessment Theory (5):
        - KR20: Kuder-Richardson 20 reliability
        - KR21: Simplified KR20
        - SPEARMAN_BROWN: Test length adjustment
        - STANDARD_ERROR_MEASUREMENT: SEM calculation
        - TRUE_SCORE: Estimated true score

    Importers:
        - LMSDataImporter: Learning Management System data
        - GradebookExportImporter: Gradebook exports (CSV/Excel)
        - AssessmentResultsImporter: Assessment/quiz results

    Example:
        >>> plugin = EducationDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with education plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="education",
            version="0.1.0",
            description=("Education formulas and importers for academic workflows"),
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=("education", "gradebook", "assessment", "curriculum", "learning"),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas and importers.

            Plugin initialization with all components

        Raises:
            Exception: If initialization fails
        """
        # Register grade calculation formulas (8)
        self.register_formula("GRADE_AVERAGE", GradeAverageFormula)
        self.register_formula("WEIGHTED_GRADE", WeightedGradeFormula)
        self.register_formula("GRADE_CURVE", GradeCurveFormula)
        self.register_formula("CURVE_GRADES", CurveGradesFormula)
        self.register_formula("STANDARD_SCORE", StandardScoreFormula)
        self.register_formula("PERCENTILE_RANK_GRADE", PercentileRankGradeFormula)
        self.register_formula("WEIGHTED_GPA", WeightedGPAFormula)
        self.register_formula("RUBRIC_SCORE", RubricScoreFormula)

        # Register statistics formulas (3)
        self.register_formula("STANDARD_DEVIATION", StandardDeviationFormula)
        self.register_formula("PERCENTILE_RANK", PercentileRankFormula)
        self.register_formula("CORRELATION", CorrelationFormula)

        # Register learning metrics formulas (11)
        self.register_formula("LEARNING_GAIN", LearningGainFormula)
        self.register_formula("MASTERY_LEVEL", MasteryLevelFormula)
        self.register_formula("ATTENDANCE_RATE", AttendanceRateFormula)
        self.register_formula("COMPLETION_RATE", CompletionRateFormula)
        self.register_formula("BLOOM_TAXONOMY_LEVEL", BloomTaxonomyLevelFormula)
        self.register_formula("READABILITY_SCORE", ReadabilityScoreFormula)
        self.register_formula("LEARNING_CURVE", LearningCurveFormula)
        self.register_formula("FORGETTING_CURVE", ForgettingCurveFormula)
        self.register_formula("SPACED_REPETITION", SpacedRepetitionFormula)
        self.register_formula("MASTERY_LEARNING", MasteryLearningFormula)
        self.register_formula("TIME_ON_TASK", TimeOnTaskFormula)

        # Register assessment theory formulas (5)
        self.register_formula("KR20", KR20Formula)
        self.register_formula("KR21", KR21Formula)
        self.register_formula("SPEARMAN_BROWN", SpearmanBrownFormula)
        self.register_formula(
            "STANDARD_ERROR_MEASUREMENT", StandardErrorMeasurementFormula
        )
        self.register_formula("TRUE_SCORE", TrueScoreFormula)

        # Register importers (3 total)
        self.register_importer("lms_data", LMSDataImporter)
        self.register_importer("gradebook_export", GradebookExportImporter)
        self.register_importer("assessment_results", AssessmentResultsImporter)

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
        required_formulas = 27  # 8 grades + 3 statistics + 11 learning + 5 assessment
        required_importers = 3

        return (
            len(self._formulas) >= required_formulas
            and len(self._importers) >= required_importers
        )


__all__ = [
    "EducationDomainPlugin",
]
