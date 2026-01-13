"""Data Science Formulas for SpreadsheetDL.

    Data Science domain formulas

Provides statistical and ML formula extensions:
- Statistical formulas: TTEST, FTEST, ZTEST, CHISQ_TEST
- ML metrics: ACCURACY, PRECISION, RECALL, F1SCORE, CONFUSION_MATRIX_METRIC, ROC_AUC, LOG_LOSS, COHEN_KAPPA, MCC
- Data functions: DS_AVERAGE, DS_MEDIAN, DS_STDEV, DS_VARIANCE, DS_CORRELATION
- Time series: MOVING_AVERAGE, EXPONENTIAL_SMOOTHING, ACF, PACF, SEASONALITY
- Clustering: SILHOUETTE_SCORE, DAVIES_BOULDIN_INDEX, CALINSKI_HARABASZ_INDEX
- Feature engineering: MIN_MAX_NORMALIZE, Z_SCORE_STANDARDIZE, LOG_TRANSFORM
"""

# Clustering formulas
from spreadsheet_dl.domains.data_science.formulas.clustering import (
    CalinskiHarabaszIndex,
    DaviesBouldinIndex,
    SilhouetteScore,
)

# Statistical formulas
# Data function formulas
from spreadsheet_dl.domains.data_science.formulas.data_functions import (
    AverageFormula,
    CorrelationFormula,
    MedianFormula,
    StdevFormula,
    VarianceFormula,
)

# Feature engineering formulas
from spreadsheet_dl.domains.data_science.formulas.feature_engineering import (
    LogTransform,
    MinMaxNormalize,
    ZScoreStandardize,
)

# ML metrics formulas
from spreadsheet_dl.domains.data_science.formulas.ml_metrics import (
    ROC_AUC,
    AccuracyFormula,
    CohenKappa,
    ConfusionMatrixMetricFormula,
    F1ScoreFormula,
    LogLoss,
    MatthewsCorrCoef,
    PrecisionFormula,
    RecallFormula,
)

# Regression metrics formulas
from spreadsheet_dl.domains.data_science.formulas.regression import (
    MeanAbsoluteError,
    MeanAbsolutePercentageError,
    MeanSquaredError,
    RootMeanSquaredError,
    RSquared,
)
from spreadsheet_dl.domains.data_science.formulas.statistical import (
    ChiSquareTestFormula,
    FTestFormula,
    TTestFormula,
    ZTestFormula,
)

# Time series formulas
from spreadsheet_dl.domains.data_science.formulas.time_series import (
    AutoCorrelation,
    ExponentialSmoothing,
    MovingAverage,
    PartialAutoCorrelation,
    Seasonality,
)

__all__ = [
    "ROC_AUC",
    "AccuracyFormula",
    "AutoCorrelation",
    "AverageFormula",
    "CalinskiHarabaszIndex",
    "ChiSquareTestFormula",
    "CohenKappa",
    "ConfusionMatrixMetricFormula",
    "CorrelationFormula",
    "DaviesBouldinIndex",
    "ExponentialSmoothing",
    "F1ScoreFormula",
    "FTestFormula",
    "LogLoss",
    "LogTransform",
    "MatthewsCorrCoef",
    "MeanAbsoluteError",
    "MeanAbsolutePercentageError",
    "MeanSquaredError",
    "MedianFormula",
    "MinMaxNormalize",
    "MovingAverage",
    "PartialAutoCorrelation",
    "PrecisionFormula",
    "RSquared",
    "RecallFormula",
    "RootMeanSquaredError",
    "Seasonality",
    "SilhouetteScore",
    "StdevFormula",
    "TTestFormula",
    "VarianceFormula",
    "ZScoreStandardize",
    "ZTestFormula",
]
