"""Finance Domain Plugin for SpreadsheetDL.

Provides comprehensive finance-specific functionality including:
- Account management and tracking
- Budget analysis and alerts
- Multi-currency support
- Bank transaction import (CSV and API)
- Expense categorization
- Financial goals and debt payoff
- Recurring expenses and bill reminders
- Financial reporting and analytics

    PHASE0-001: Restructure package for domain plugins
"""

# Account Management
from spreadsheet_dl.domains.finance.accounts import (
    Account,
    AccountManager,
    AccountTransaction,
    AccountType,
    NetWorth,
    Transfer,
    get_default_accounts,
)

# Alerts
from spreadsheet_dl.domains.finance.alerts import (
    Alert,
    AlertConfig,
    AlertMonitor,
    AlertSeverity,
    AlertType,
    check_budget_alerts,
)

# Analytics
from spreadsheet_dl.domains.finance.analytics import (
    AnalyticsDashboard,
    generate_dashboard,
)

# Bank Formats
from spreadsheet_dl.domains.finance.bank_formats import (
    BUILTIN_FORMATS,
    BankFormatDefinition,
    BankFormatRegistry,
    FormatBuilder,
    count_formats,
    detect_format,
    get_format,
    list_formats,
)

# Budget Analyzer
from spreadsheet_dl.domains.finance.budget_analyzer import BudgetAnalyzer

# Categories
from spreadsheet_dl.domains.finance.categories import (
    Category,
    CategoryManager,
    StandardCategory,
    category_from_string,
    get_category_manager,
)

# CSV Import
from spreadsheet_dl.domains.finance.csv_import import (
    CSVImporter,
    TransactionCategorizer,
    import_bank_csv,
)

# Currency
from spreadsheet_dl.domains.finance.currency import (
    CURRENCIES,
    Currency,
    CurrencyCode,
    CurrencyConverter,
    ExchangeRate,
    ExchangeRateProvider,
    MoneyAmount,
    convert,
    format_currency,
    get_currency,
    list_currencies,
    money,
)

# Formulas
from spreadsheet_dl.domains.finance.formulas import (
    CompoundAnnualGrowthRate,
    CompoundInterest,
    DecliningBalanceDepreciation,
    FutureValue,
    InternalRateOfReturn,
    NetPresentValue,
    PaymentFormula,
    PeriodsFormula,
    PortfolioBeta,
    PresentValue,
    RateFormula,
    ReturnOnInvestment,
    SharpeRatio,
    StraightLineDepreciation,
    SUMYearsDigitsDepreciation,
)

# Goals
from spreadsheet_dl.domains.finance.goals import (
    Debt,
    DebtPayoffMethod,
    DebtPayoffPlan,
    GoalCategory,
    GoalManager,
    GoalStatus,
    SavingsGoal,
    compare_payoff_methods,
    create_debt_payoff_plan,
    create_emergency_fund,
)

# ODS Generator
from spreadsheet_dl.domains.finance.ods_generator import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    create_monthly_budget,
)

# Plaid Integration
from spreadsheet_dl.domains.finance.plaid_integration import (
    PlaidAccount,
    PlaidClient,
    PlaidConfig,
    PlaidSyncManager,
    PlaidTransaction,
    SyncResult,
)

# Plugin
from spreadsheet_dl.domains.finance.plugin import FinanceDomainPlugin

# Recurring Expenses
from spreadsheet_dl.domains.finance.recurring import (
    RecurrenceFrequency,
    RecurringExpense,
    RecurringExpenseManager,
)

# Bill Reminders
from spreadsheet_dl.domains.finance.reminders import (
    BillReminder,
    BillReminderManager,
    ReminderFrequency,
    ReminderStatus,
    create_bill_from_template,
)

# Report Generator
from spreadsheet_dl.domains.finance.report_generator import ReportGenerator

__all__ = [
    # Constants
    "BUILTIN_FORMATS",
    "CURRENCIES",
    # Classes - Account Management
    "Account",
    "AccountManager",
    "AccountTransaction",
    "AccountType",
    # Classes - Alerts
    "Alert",
    "AlertConfig",
    "AlertMonitor",
    "AlertSeverity",
    "AlertType",
    # Classes - Analytics
    "AnalyticsDashboard",
    # Classes - Bank Formats
    "BankFormatDefinition",
    "BankFormatRegistry",
    # Classes - Reminders
    "BillReminder",
    "BillReminderManager",
    # Classes - Budget
    "BudgetAllocation",
    "BudgetAnalyzer",
    # Classes - CSV Import
    "CSVImporter",
    # Classes - Categories
    "Category",
    "CategoryManager",
    # Classes - Formulas
    "CompoundAnnualGrowthRate",
    "CompoundInterest",
    # Classes - Currency
    "Currency",
    "CurrencyCode",
    "CurrencyConverter",
    # Classes - Goals
    "Debt",
    "DebtPayoffMethod",
    "DebtPayoffPlan",
    # Classes - Formulas (continued)
    "DecliningBalanceDepreciation",
    "ExchangeRate",
    "ExchangeRateProvider",
    # Classes - ODS Generator
    "ExpenseCategory",
    "ExpenseEntry",
    "FinanceDomainPlugin",
    "FormatBuilder",
    "FutureValue",
    "GoalCategory",
    "GoalManager",
    "GoalStatus",
    "InternalRateOfReturn",
    "MoneyAmount",
    "NetPresentValue",
    "NetWorth",
    "OdsGenerator",
    "PaymentFormula",
    "PeriodsFormula",
    # Classes - Plaid
    "PlaidAccount",
    "PlaidClient",
    "PlaidConfig",
    "PlaidSyncManager",
    "PlaidTransaction",
    "PortfolioBeta",
    "PresentValue",
    "RateFormula",
    # Classes - Recurring
    "RecurrenceFrequency",
    "RecurringExpense",
    "RecurringExpenseManager",
    "ReminderFrequency",
    "ReminderStatus",
    # Classes - Report
    "ReportGenerator",
    "ReturnOnInvestment",
    "SUMYearsDigitsDepreciation",
    "SavingsGoal",
    "SharpeRatio",
    "StandardCategory",
    "StraightLineDepreciation",
    "SyncResult",
    "TransactionCategorizer",
    "Transfer",
    # Functions
    "category_from_string",
    "check_budget_alerts",
    "compare_payoff_methods",
    "convert",
    "count_formats",
    "create_bill_from_template",
    "create_debt_payoff_plan",
    "create_emergency_fund",
    "create_monthly_budget",
    "detect_format",
    "format_currency",
    "generate_dashboard",
    "get_category_manager",
    "get_currency",
    "get_default_accounts",
    "get_format",
    "import_bank_csv",
    "list_currencies",
    "list_formats",
    "money",
]
