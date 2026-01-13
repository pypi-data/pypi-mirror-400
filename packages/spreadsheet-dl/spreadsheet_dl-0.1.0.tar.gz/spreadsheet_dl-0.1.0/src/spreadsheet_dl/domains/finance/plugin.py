"""Finance Domain Plugin for SpreadsheetDL.

    Finance domain plugin
    PHASE-C: Domain plugin implementations

Provides finance-specific functionality including:
- Budget analysis and tracking
- Multi-currency support
- Bank transaction import
- Financial calculations
"""

from __future__ import annotations

from spreadsheet_dl.domains.base import BaseDomainPlugin, PluginMetadata


class FinanceDomainPlugin(BaseDomainPlugin):
    """Finance domain plugin.

        Complete Finance domain plugin
        PHASE-C: Domain plugin implementations

    Provides comprehensive finance functionality for SpreadsheetDL
    with budget analysis, currency conversion, and bank import capabilities.

    Example:
        >>> plugin = FinanceDomainPlugin()
        >>> plugin.initialize()
        >>> formulas = plugin.list_formulas()
    """

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata.

        Returns:
            PluginMetadata with finance plugin information

            Plugin metadata requirements
        """
        return PluginMetadata(
            name="finance",
            version="0.1.0",
            description="Finance functions for budgeting and financial analysis",
            author="SpreadsheetDL Team",
            license="MIT",
            homepage="https://github.com/lair-click-bats/spreadsheet-dl",
            tags=(
                "finance",
                "budget",
                "accounting",
                "currency",
            ),
            min_spreadsheet_dl_version="0.1.0",
        )

    def initialize(self) -> None:
        """Initialize plugin resources.

            Plugin initialization with all components

        Raises:
            Exception: If initialization fails
        """
        # Register all finance formulas
        from spreadsheet_dl.domains.finance.formulas import (
            AlphaRatio,
            BlackScholesCall,
            BlackScholesPut,
            BondPrice,
            CompoundAnnualGrowthRate,
            CompoundInterest,
            ConditionalVaR,
            Convexity,
            DecliningBalanceDepreciation,
            DownsideDeviation,
            FutureValue,
            ImpliedVolatility,
            InformationRatio,
            InternalRateOfReturn,
            MacDuration,
            ModifiedDuration,
            NetPresentValue,
            OptionDelta,
            OptionGamma,
            OptionRho,
            OptionTheta,
            OptionVega,
            PaymentFormula,
            PeriodsFormula,
            PortfolioBeta,
            PortfolioVolatility,
            PresentValue,
            RateFormula,
            ReturnOnInvestment,
            SharpeRatio,
            StraightLineDepreciation,
            SUMYearsDigitsDepreciation,
            TrackingError,
            ValueAtRisk,
            YieldToMaturity,
        )

        # Register Time Value of Money formulas (7)
        self.register_formula("PV", PresentValue)
        self.register_formula("FV", FutureValue)
        self.register_formula("NPV", NetPresentValue)
        self.register_formula("IRR", InternalRateOfReturn)
        self.register_formula("PMT", PaymentFormula)
        self.register_formula("RATE", RateFormula)
        self.register_formula("NPER", PeriodsFormula)

        # Register Investments formulas (5)
        self.register_formula("ROI", ReturnOnInvestment)
        self.register_formula("CAGR", CompoundAnnualGrowthRate)
        self.register_formula("COMPOUND_INTEREST", CompoundInterest)
        self.register_formula("SHARPE_RATIO", SharpeRatio)
        self.register_formula("PORTFOLIO_BETA", PortfolioBeta)

        # Register Depreciation formulas (3)
        self.register_formula("SLN", StraightLineDepreciation)
        self.register_formula("DDB", DecliningBalanceDepreciation)
        self.register_formula("SYD", SUMYearsDigitsDepreciation)

        # Register Risk Management formulas (7)
        self.register_formula("VAR", ValueAtRisk)
        self.register_formula("CVAR", ConditionalVaR)
        self.register_formula("PORTFOLIO_VOLATILITY", PortfolioVolatility)
        self.register_formula("ALPHA", AlphaRatio)
        self.register_formula("TRACKING_ERROR", TrackingError)
        self.register_formula("INFORMATION_RATIO", InformationRatio)
        self.register_formula("DOWNSIDE_DEVIATION", DownsideDeviation)

        # Register Options Pricing formulas (8)
        self.register_formula("BS_CALL", BlackScholesCall)
        self.register_formula("BS_PUT", BlackScholesPut)
        self.register_formula("IMPLIED_VOL", ImpliedVolatility)
        self.register_formula("OPTION_DELTA", OptionDelta)
        self.register_formula("OPTION_GAMMA", OptionGamma)
        self.register_formula("OPTION_THETA", OptionTheta)
        self.register_formula("OPTION_VEGA", OptionVega)
        self.register_formula("OPTION_RHO", OptionRho)

        # Register Bond Analytics formulas (5)
        self.register_formula("BOND_PRICE", BondPrice)
        self.register_formula("YTM", YieldToMaturity)
        self.register_formula("DURATION", MacDuration)
        self.register_formula("MDURATION", ModifiedDuration)
        self.register_formula("CONVEXITY", Convexity)

    def cleanup(self) -> None:
        """Cleanup plugin resources.

        No resources need explicit cleanup for this plugin.

            Plugin cleanup method
        """
        pass

    def validate(self) -> bool:
        """Validate plugin configuration.

        Returns:
            True if plugin is valid

            Plugin validation
        """
        # Validate that all 35 formulas are registered
        formulas = self.list_formulas()
        expected_count = 35
        if len(formulas) != expected_count:
            msg = f"Expected {expected_count} formulas, found {len(formulas)}"
            raise ValueError(msg)
        return True


__all__ = [
    "FinanceDomainPlugin",
]
