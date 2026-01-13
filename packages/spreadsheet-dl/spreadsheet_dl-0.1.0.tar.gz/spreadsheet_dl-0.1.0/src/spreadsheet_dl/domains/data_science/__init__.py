"""Data Science Domain Plugin for SpreadsheetDL.

    Complete Data Science domain plugin
    PHASE-C: Domain plugin implementations

Provides comprehensive data science-specific functionality including:
- Statistical test formulas (T-test, F-test, Chi-square)
- ML metrics formulas (accuracy, precision, recall, F1)
- Scientific CSV import with type detection
- MLflow experiment import
- Jupyter notebook metadata extraction

Example:
    >>> from spreadsheet_dl.domains.data_science import DataScienceDomainPlugin
    >>> plugin = DataScienceDomainPlugin()
    >>> plugin.initialize()
"""

# Plugin
# Formulas - Data Functions
from spreadsheet_dl.domains.data_science.formulas.data_functions import (
    AverageFormula,
    CorrelationFormula,
    MedianFormula,
    StdevFormula,
    VarianceFormula,
)

# Formulas - ML Metrics
from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
    AccuracyFormula,
    ConfusionMatrixMetricFormula,
    F1ScoreFormula,
    PrecisionFormula,
    RecallFormula,
)

# Formulas - Statistical
from spreadsheet_dl.domains.data_science.formulas.statistical import (
    ChiSquareTestFormula,
    FTestFormula,
    TTestFormula,
    ZTestFormula,
)

# Importers
from spreadsheet_dl.domains.data_science.importers import (
    JupyterMetadataImporter,
    MLflowImporter,
    ScientificCSVImporter,
)
from spreadsheet_dl.domains.data_science.plugin import DataScienceDomainPlugin

# Utils
from spreadsheet_dl.domains.data_science.utils import (
    calculate_confusion_matrix_metrics,
    format_scientific_notation,
    infer_data_type,
    parse_scientific_notation,
)

__all__ = [
    # Formulas - ML Metrics
    "AccuracyFormula",
    # Formulas - Data Functions
    "AverageFormula",
    # Formulas - Statistical
    "ChiSquareTestFormula",
    "ConfusionMatrixMetricFormula",
    "CorrelationFormula",
    # Plugin
    "DataScienceDomainPlugin",
    "F1ScoreFormula",
    "FTestFormula",
    # Importers
    "JupyterMetadataImporter",
    "MLflowImporter",
    "MedianFormula",
    "PrecisionFormula",
    "RecallFormula",
    "ScientificCSVImporter",
    "StdevFormula",
    "TTestFormula",
    "VarianceFormula",
    "ZTestFormula",
    # Utils
    "calculate_confusion_matrix_metrics",
    "format_scientific_notation",
    "infer_data_type",
    "parse_scientific_notation",
]
