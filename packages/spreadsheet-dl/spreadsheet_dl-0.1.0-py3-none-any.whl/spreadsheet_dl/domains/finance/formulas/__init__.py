"""Financial formulas for time value of money, investments, and analysis."""

from __future__ import annotations

from spreadsheet_dl.domains.finance.formulas.bonds import (
    BondPrice,
    Convexity,
    MacDuration,
    ModifiedDuration,
    YieldToMaturity,
)
from spreadsheet_dl.domains.finance.formulas.depreciation import (
    DecliningBalanceDepreciation,
    StraightLineDepreciation,
    SUMYearsDigitsDepreciation,
)
from spreadsheet_dl.domains.finance.formulas.investments import (
    CompoundAnnualGrowthRate,
    CompoundInterest,
    PortfolioBeta,
    ReturnOnInvestment,
    SharpeRatio,
)
from spreadsheet_dl.domains.finance.formulas.options import (
    BlackScholesCall,
    BlackScholesPut,
    ImpliedVolatility,
    OptionDelta,
    OptionGamma,
    OptionRho,
    OptionTheta,
    OptionVega,
)
from spreadsheet_dl.domains.finance.formulas.risk import (
    AlphaRatio,
    ConditionalVaR,
    DownsideDeviation,
    InformationRatio,
    PortfolioVolatility,
    TrackingError,
    ValueAtRisk,
)
from spreadsheet_dl.domains.finance.formulas.time_value import (
    FutureValue,
    InternalRateOfReturn,
    NetPresentValue,
    PaymentFormula,
    PeriodsFormula,
    PresentValue,
    RateFormula,
)

__all__ = [
    "AlphaRatio",
    "BlackScholesCall",
    "BlackScholesPut",
    "BondPrice",
    "CompoundAnnualGrowthRate",
    "CompoundInterest",
    "ConditionalVaR",
    "Convexity",
    "DecliningBalanceDepreciation",
    "DownsideDeviation",
    "FutureValue",
    "ImpliedVolatility",
    "InformationRatio",
    "InternalRateOfReturn",
    "MacDuration",
    "ModifiedDuration",
    "NetPresentValue",
    "OptionDelta",
    "OptionGamma",
    "OptionRho",
    "OptionTheta",
    "OptionVega",
    "PaymentFormula",
    "PeriodsFormula",
    "PortfolioBeta",
    "PortfolioVolatility",
    "PresentValue",
    "RateFormula",
    "ReturnOnInvestment",
    "SUMYearsDigitsDepreciation",
    "SharpeRatio",
    "StraightLineDepreciation",
    "TrackingError",
    "ValueAtRisk",
    "YieldToMaturity",
]
