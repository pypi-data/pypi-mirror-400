"""Data Science Domain Plugin for SpreadsheetDL.

    Data Science domain plugin
    PHASE-C: Domain plugin implementations

Provides data science-specific functionality including:
- Statistical testing formulas (T-test, F-test, Chi-square)
- ML metrics formulas (accuracy, precision, recall, F1)
- Scientific CSV and MLflow importers
- Jupyter notebook metadata extraction
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata

# Import formulas
from spreadsheet_dl.domains.data_science.formulas.data_functions import (
    AverageFormula,
    CorrelationFormula,
    MedianFormula,
    StdevFormula,
    VarianceFormula,
)
from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
    AccuracyFormula,
    ConfusionMatrixMetricFormula,
    F1ScoreFormula,
    PrecisionFormula,
    RecallFormula,
)
from spreadsheet_dl.domains.data_science.formulas.statistical import (
    ChiSquareTestFormula,
    FTestFormula,
    TTestFormula,
    ZTestFormula,
)

# Import importers
from spreadsheet_dl.domains.data_science.importers.jupyter import (
    JupyterMetadataImporter,
)
from spreadsheet_dl.domains.data_science.importers.mlflow import MLflowImporter
from spreadsheet_dl.domains.data_science.importers.scientific_csv import (
    ScientificCSVImporter,
)


class DataScienceDomainPlugin(BaseDomainPlugin):
    """Data Science domain plugin.

        Complete Data Science domain plugin
        PHASE-C: Domain plugin implementations

    Provides comprehensive data science functionality for SpreadsheetDL
    with formulas and importers tailored for ML/DS workflows.

    Formulas (14 total):
        Statistical Tests (4):
        - TTEST: T-test for hypothesis testing
        - FTEST: F-test for variance comparison
        - ZTEST: Z-test for large samples
        - CHISQ_TEST: Chi-square test

        ML Metrics (5):
        - ACCURACY: Classification accuracy
        - PRECISION: Precision score
        - RECALL: Recall score
        - F1SCORE: F1 score
        - CONFUSION_MATRIX_METRIC: Confusion matrix metrics

        Data Functions (5):
        - DS_AVERAGE: Average calculation
        - DS_MEDIAN: Median calculation
        - DS_STDEV: Standard deviation
        - DS_VARIANCE: Variance calculation
        - DS_CORRELATION: Correlation coefficient

    Importers:
        - ScientificCSVImporter: Scientific CSV files
        - MLflowImporter: MLflow experiment data
        - JupyterMetadataImporter: Jupyter notebook metadata

    Example:
        >>> plugin = DataScienceDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with data science plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="data_science",
            version="0.1.0",
            description="Data science formulas and importers for ML/DS workflows",
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=("data-science", "machine-learning", "statistics", "analytics"),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

        Registers all formulas and importers.

            Plugin initialization with all components

        Raises:
            Exception: If initialization fails
        """
        # Register statistical formulas
        self.register_formula("TTEST", TTestFormula)
        self.register_formula("FTEST", FTestFormula)
        self.register_formula("ZTEST", ZTestFormula)
        self.register_formula("CHISQ_TEST", ChiSquareTestFormula)

        # Register ML metrics formulas
        self.register_formula("ACCURACY", AccuracyFormula)
        self.register_formula("PRECISION", PrecisionFormula)
        self.register_formula("RECALL", RecallFormula)
        self.register_formula("F1SCORE", F1ScoreFormula)
        self.register_formula("CONFUSION_MATRIX_METRIC", ConfusionMatrixMetricFormula)

        # Register data function formulas
        self.register_formula("DS_AVERAGE", AverageFormula)
        self.register_formula("DS_MEDIAN", MedianFormula)
        self.register_formula("DS_STDEV", StdevFormula)
        self.register_formula("DS_VARIANCE", VarianceFormula)
        self.register_formula("DS_CORRELATION", CorrelationFormula)

        # Register importers (3 total)
        self.register_importer("scientific_csv", ScientificCSVImporter)
        self.register_importer("mlflow", MLflowImporter)
        self.register_importer("jupyter", JupyterMetadataImporter)

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
        required_formulas = 14  # 4 statistical + 5 ML + 5 data functions
        required_importers = 3

        return (
            len(self._formulas) >= required_formulas
            and len(self._importers) >= required_importers
        )


__all__ = [
    "DataScienceDomainPlugin",
]
