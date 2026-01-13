"""SpreadsheetDL - The Spreadsheet Definition Language for Python.

A universal spreadsheet definition language with declarative API, multi-format export,
domain-specific functions, and native MCP server for AI integration.

**Key Features:**
- Declarative Builder API (define what, not how)
- Type-Safe Formulas (60+ functions, circular reference detection)
- Theme System (YAML-based, 5 built-in themes)
- Multi-Format Export (ODS, XLSX, PDF from single definition)
- Domain Plugins (finance, science, engineering - with specialized functions)
- MCP Server (native integration with Claude)

**Why SpreadsheetDL?**
- vs openpyxl/xlsxwriter: Declarative, not imperative
- vs pandas: Full spreadsheet model, not just data export
- vs all: Only tool with domain-aware functions and MCP server

v0.1.0 - Universal Spreadsheet Definition Language
===================================================

Core Platform:
- Declarative builder API with fluent, chainable methods
- Type-safe formula builder with circular reference detection
- YAML-based theme system (5 built-in themes)
- Chart builder (60+ chart types)
- Multi-format export (ODS native, XLSX, PDF)
- Advanced formatting (conditional, validation, named ranges, merging)
- Template engine with schema-driven composition
- MCP server with 18 tools for spreadsheet and budget operations
- Streaming I/O for 100k+ rows
- Round-trip editing (read, modify, write ODS)
- Performance optimization with caching and lazy loading

Domain Plugins (specialized functions):
- Finance: NPV, IRR, amortization, budget analysis, bank import
- Data Science: Statistical functions, ML metrics, experiment tracking
- Engineering: Electrical, mechanical, civil - stress, power, beam calculations
- Manufacturing: OEE, quality metrics, inventory functions
- Biology: Dilution, concentration, qPCR calculations
- Education: Grade calculations, attendance tracking
- Environmental: Air/water quality indices, carbon calculations

Legacy Features (from v2.0.0):

Major Features (v0.1.0):
- Universal Spreadsheet Definition Language with declarative DSL
- Multi-format export (ODS, XLSX, CSV, PDF, AI-friendly JSON)
- MCP server integration for LLM workflows
- 9 domain-specific plugins with specialized functions
- Theme system for visual consistency
- Advanced formulas, charts, and conditional formatting
- Security features (encryption, credential management)
- Backup/restore with compression
- Plugin architecture with hot-reload support

For complete feature history and migration guides, see CHANGELOG.md
"""

# Import version from dedicated module for fast CLI startup
# Account Management
# Format Adapters
# =============================================================================
# Modular Packages - Public namespace access
# =============================================================================
# Import packages for users who want to access modular structure
# Example: from spreadsheet_dl import mcp_pkg; config = mcp_pkg.MCPConfig()
from spreadsheet_dl import _builder as builder_pkg  # noqa: F401
from spreadsheet_dl import _cli as cli_pkg  # noqa: F401
from spreadsheet_dl import _mcp as mcp_pkg  # noqa: F401
from spreadsheet_dl._version import __author__, __version__
from spreadsheet_dl.adapters import (
    AdapterOptions,
    AdapterRegistry,
    CsvAdapter,
    ExportFormat,
    FormatAdapter,
    HtmlAdapter,
    ImportFormat,
    JsonAdapter,
    OdsAdapter,
    TsvAdapter,
    export_to,
    import_from,
)

# AI Export
from spreadsheet_dl.ai_export import (
    AIExporter,
    CellRelationship,
    SemanticCell,
    SemanticCellType,
    SemanticSheet,
    SemanticTag,
    export_dual,
    export_for_ai,
)

# AI Training Data Export
from spreadsheet_dl.ai_training import (
    AnonymizationConfig,
    AnonymizationLevel,
    DataAnonymizer,
    PIIDetector,
    TrainingDataExporter,
    TrainingDataset,
    export_training_data,
)

# Backup
from spreadsheet_dl.backup import (
    BackupManager,
    BackupReason,
    auto_backup,
)

# Builder API
from spreadsheet_dl.builder import (
    CellRef,
    CellSpec,
    ColumnSpec,
    FormulaBuilder,
    RangeRef,
    RowSpec,
    SheetRef,
    SheetSpec,
    SpreadsheetBuilder,
    create_spreadsheet,
    formula,
)

# ============================================================================
# v2.0.0 Professional Spreadsheet System (95 new requirements)
# ============================================================================
# Charts
from spreadsheet_dl.charts import (
    AxisConfig,
    AxisType,
    ChartBuilder,
    ChartPosition,
    ChartSize,
    ChartSpec,
    ChartTitle,
    ChartType,
    DataLabelConfig,
    DataLabelPosition,
    DataSeries,
    LegendConfig,
    LegendPosition,
    PlotAreaStyle,
    Sparkline,
    SparklineBuilder,
    SparklineMarkers,
    SparklineType,
    Trendline,
    TrendlineType,
    budget_comparison_chart,
    chart,
    sparkline,
    spending_pie_chart,
    trend_line_chart,
)

# Shell Completions
from spreadsheet_dl.completions import (
    detect_shell,
    generate_bash_completions,
    generate_fish_completions,
    generate_zsh_completions,
    install_completions,
    print_completion_script,
)
from spreadsheet_dl.config import (
    Config,
    get_config,
    init_config_file,
)
from spreadsheet_dl.domains.finance.accounts import (
    Account,
    AccountManager,
    AccountTransaction,
    AccountType,
    NetWorth,
    Transfer,
    get_default_accounts,
)
from spreadsheet_dl.domains.finance.alerts import (
    Alert,
    AlertConfig,
    AlertMonitor,
    AlertSeverity,
    AlertType,
    check_budget_alerts,
)
from spreadsheet_dl.domains.finance.analytics import (
    AnalyticsDashboard,
    generate_dashboard,
)

# Extended Bank Formats
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
from spreadsheet_dl.domains.finance.budget_analyzer import (
    BudgetAnalyzer,
    analyze_budget,
)

# Custom Categories
from spreadsheet_dl.domains.finance.categories import (
    Category,
    CategoryManager,
    StandardCategory,
    category_from_string,
    get_category_manager,
)
from spreadsheet_dl.domains.finance.csv_import import (
    BANK_FORMATS,
    CSVImporter,
    TransactionCategorizer,
    import_bank_csv,
)

# Multi-Currency Support
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

# Goals and Debt Payoff
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
from spreadsheet_dl.domains.finance.ods_generator import (
    BudgetAllocation,
    ExpenseCategory,
    ExpenseEntry,
    OdsGenerator,
    create_monthly_budget,
)

# Plaid Integration
from spreadsheet_dl.domains.finance.plaid_integration import (
    AccessToken,
    LinkStatus,
    LinkToken,
    PlaidAccount,
    PlaidAPIError,
    PlaidAuthError,
    PlaidClient,
    PlaidConfig,
    PlaidConnectionError,
    PlaidEnvironment,
    PlaidError,
    PlaidInstitution,
    PlaidProduct,
    PlaidRateLimitError,
    PlaidSyncError,
    PlaidSyncManager,
    PlaidTransaction,
    SyncResult,
    SyncStatus,
)

# Recurring expenses (Enhanced in Phase 4)
from spreadsheet_dl.domains.finance.recurring import (
    COMMON_RECURRING,
    RecurrenceFrequency,
    RecurringExpense,
    RecurringExpenseManager,
    create_common_recurring,
)

# Bill Reminders
from spreadsheet_dl.domains.finance.reminders import (
    COMMON_BILLS,
    BillReminder,
    BillReminderManager,
    ReminderFrequency,
    ReminderStatus,
    create_bill_from_template,
)
from spreadsheet_dl.domains.finance.report_generator import (
    ReportConfig,
    ReportGenerator,
    generate_monthly_report,
)
from spreadsheet_dl.exceptions import (
    ConfigurationError,
    CSVImportError,
    DecryptionError,
    EncryptionError,
    FileError,
    IntegrityError,
    OdsError,
    OperationCancelledError,
    SpreadsheetDLError,
    TemplateError,
    ValidationError,
    WebDAVError,
)

# Multi-format Export
from spreadsheet_dl.export import (
    ExportOptions,
    MultiFormatExporter,
    export_to_csv,
    export_to_pdf,
    export_to_xlsx,
)
from spreadsheet_dl.interactive import (
    DashboardGenerator as OdsDashboardGenerator,
)

# Interactive ODS Features
from spreadsheet_dl.interactive import (
    DashboardKPI,
    DropdownList,
    InteractiveOdsBuilder,
    ValidationRule,
    add_interactive_features,
    generate_budget_dashboard,
)

# MCP Server
from spreadsheet_dl.mcp_server import (
    MCPConfig,
    MCPServer,
    MCPTool,
    MCPToolResult,
    create_mcp_server,
)

# Notifications
from spreadsheet_dl.notifications import (
    EmailChannel,
    EmailConfig,
    Notification,
    NotificationManager,
    NotificationPriority,
    NotificationTemplates,
    NotificationType,
    NtfyChannel,
    NtfyConfig,
)

# ODS Editor
from spreadsheet_dl.ods_editor import (
    OdsEditor,
    append_expense_to_file,
)

# Performance Optimization
from spreadsheet_dl.performance import (
    BatchProcessor,
    BatchResult,
    Benchmark,
    BenchmarkResult,
    FileCache,
    Lazy,
    LazyProperty,
    LRUCache,
    batch_process,
    cached,
    clear_cache,
    get_cache,
    timed,
)

# Renderer
from spreadsheet_dl.renderer import (
    OdsRenderer,
    render_sheets,
)

# Schema Extensions
from spreadsheet_dl.schema.advanced import (
    AutoFilter,
    CellComment,
    DataTable,
    FilterCriteria,
    HiddenRowsColumns,
    Hyperlink,
    Image,
    NamedRange,
    OutlineGroup,
    OutlineSettings,
    Shape,
)
from spreadsheet_dl.schema.conditional import (
    ConditionalFormat,
    ConditionalRule,
)
from spreadsheet_dl.schema.data_validation import (
    DataValidation,
    ValidationType,
)
from spreadsheet_dl.schema.print_layout import (
    HeaderFooter,
    HeaderFooterContent,
    PageBreak,
    PageMargins,
    PageOrientation,
    PageSetup,
    PageSetupBuilder,
    PageSize,
    PrintPresets,
    PrintQuality,
    PrintScale,
    RepeatConfig,
)
from spreadsheet_dl.schema.typography import (
    FontPairing,
    Typography,
)
from spreadsheet_dl.schema.units import (
    Length,
    LengthUnit,
)

# Security
from spreadsheet_dl.security import (
    CredentialStore,
    EncryptionMetadata,
    FileEncryptor,
    SecurityAuditLog,
    check_password_strength,
    generate_password,
)

# Serialization
from spreadsheet_dl.serialization import (
    DefinitionFormat,
    Serializer,
    SpreadsheetDecoder,
    SpreadsheetEncoder,
    load_definition,
    save_definition,
)

# Streaming I/O
from spreadsheet_dl.streaming import (
    StreamingCell,
    StreamingReader,
    StreamingRow,
    StreamingWriter,
    stream_read,
    stream_write,
)

# Template Engine
from spreadsheet_dl.template_engine import (
    ComponentDefinition,
    TemplateLoader,
    TemplateRenderer,
    TemplateVariable,
)

# Interactive Visualization
from spreadsheet_dl.visualization import (
    CATEGORY_COLORS,
    ChartConfig,
    ChartDataPoint,
    ChartGenerator,
    ChartSeries,
    DashboardGenerator,
    create_budget_dashboard,
    create_spending_pie_chart,
)
from spreadsheet_dl.webdav_upload import (
    NextcloudConfig,
    WebDAVClient,
    upload_budget,
)

__all__ = [  # noqa: RUF022  # Intentionally organized by category, not alphabetically
    # Constants (uppercase first)
    "BANK_FORMATS",
    "BUILTIN_FORMATS",
    "CATEGORY_COLORS",
    "COMMON_BILLS",
    "COMMON_RECURRING",
    "CURRENCIES",
    # Classes (alphabetical)
    "AccessToken",
    "AIExporter",
    "Account",
    "AccountManager",
    "AccountTransaction",
    "AccountType",
    "AdapterOptions",
    "AdapterRegistry",
    "Alert",
    "AlertConfig",
    "AlertMonitor",
    "AlertSeverity",
    "AlertType",
    "AnalyticsDashboard",
    "AnonymizationConfig",
    "AnonymizationLevel",
    "AutoFilter",
    "AxisConfig",
    "AxisType",
    "BackupManager",
    "BackupReason",
    "BankFormatDefinition",
    "BankFormatRegistry",
    "BatchProcessor",
    "BatchResult",
    "Benchmark",
    "BenchmarkResult",
    "BillReminder",
    "BillReminderManager",
    "BudgetAllocation",
    "BudgetAnalyzer",
    "CSVImportError",
    "CSVImporter",
    "Category",
    "CategoryManager",
    "CellComment",
    "CellRef",
    "CellRelationship",
    "CellSpec",
    "ChartBuilder",
    "ChartConfig",
    "ChartDataPoint",
    "ChartGenerator",
    "ChartPosition",
    "ChartSeries",
    "ChartSize",
    "ChartSpec",
    "ChartTitle",
    "ChartType",
    "ColumnSpec",
    "ComponentDefinition",
    "ConditionalFormat",
    "ConditionalRule",
    "Config",
    "ConfigurationError",
    "CredentialStore",
    "CsvAdapter",
    "Currency",
    "CurrencyCode",
    "CurrencyConverter",
    "DashboardGenerator",
    "DashboardKPI",
    "DataAnonymizer",
    "DataLabelConfig",
    "DataLabelPosition",
    "DataSeries",
    "DataTable",
    "DataValidation",
    "Debt",
    "DebtPayoffMethod",
    "DebtPayoffPlan",
    "DecryptionError",
    "DefinitionFormat",
    "DropdownList",
    "EmailChannel",
    "EmailConfig",
    "EncryptionError",
    "EncryptionMetadata",
    "ExchangeRate",
    "ExchangeRateProvider",
    "ExpenseCategory",
    "ExpenseEntry",
    "ExportFormat",
    "ExportOptions",
    "FileCache",
    "FileEncryptor",
    "FileError",
    "FilterCriteria",
    "FontPairing",
    "FormatAdapter",
    "FormatBuilder",
    "FormulaBuilder",
    "GoalCategory",
    "GoalManager",
    "GoalStatus",
    "HeaderFooter",
    "HeaderFooterContent",
    "HiddenRowsColumns",
    "HtmlAdapter",
    "Hyperlink",
    "Image",
    "ImportFormat",
    "IntegrityError",
    "InteractiveOdsBuilder",
    "JsonAdapter",
    "LRUCache",
    "Lazy",
    "LazyProperty",
    "LegendConfig",
    "LegendPosition",
    "Length",
    "LengthUnit",
    "LinkStatus",
    "LinkToken",
    "MCPConfig",
    "MCPServer",
    "MCPTool",
    "MCPToolResult",
    "MoneyAmount",
    "MultiFormatExporter",
    "NamedRange",
    "NetWorth",
    "NextcloudConfig",
    "Notification",
    "NotificationManager",
    "NotificationPriority",
    "NotificationTemplates",
    "NotificationType",
    "NtfyChannel",
    "NtfyConfig",
    "OdsAdapter",
    "OdsDashboardGenerator",
    "OdsEditor",
    "OdsError",
    "OdsGenerator",
    "OdsRenderer",
    "OperationCancelledError",
    "OutlineGroup",
    "OutlineSettings",
    "PIIDetector",
    "PageBreak",
    "PageMargins",
    "PageOrientation",
    "PageSetup",
    "PageSetupBuilder",
    "PageSize",
    "PlaidAccount",
    "PlaidAPIError",
    "PlaidAuthError",
    "PlaidClient",
    "PlaidConfig",
    "PlaidConnectionError",
    "PlaidEnvironment",
    "PlaidError",
    "PlaidInstitution",
    "PlaidProduct",
    "PlaidRateLimitError",
    "PlaidSyncError",
    "PlaidSyncManager",
    "PlaidTransaction",
    "PlotAreaStyle",
    "PrintPresets",
    "PrintQuality",
    "PrintScale",
    "RangeRef",
    "RecurrenceFrequency",
    "RecurringExpense",
    "RecurringExpenseManager",
    "ReminderFrequency",
    "ReminderStatus",
    "RepeatConfig",
    "ReportConfig",
    "ReportGenerator",
    "RowSpec",
    "SavingsGoal",
    "SecurityAuditLog",
    "SemanticCell",
    "SemanticCellType",
    "SemanticSheet",
    "SemanticTag",
    "Serializer",
    "Shape",
    "SheetRef",
    "SheetSpec",
    "Sparkline",
    "SparklineBuilder",
    "SparklineMarkers",
    "SparklineType",
    "SpreadsheetBuilder",
    "SpreadsheetDecoder",
    "SpreadsheetDLError",
    "SpreadsheetEncoder",
    "StandardCategory",
    "StreamingCell",
    "StreamingReader",
    "StreamingRow",
    "StreamingWriter",
    "SyncResult",
    "SyncStatus",
    "TemplateError",
    "TemplateLoader",
    "TemplateRenderer",
    "TemplateVariable",
    "TrainingDataExporter",
    "TrainingDataset",
    "TransactionCategorizer",
    "Transfer",
    "Trendline",
    "TrendlineType",
    "TsvAdapter",
    "Typography",
    "ValidationError",
    "ValidationRule",
    "ValidationType",
    "WebDAVClient",
    "WebDAVError",
    # Dunder attributes
    "__author__",
    "__version__",
    # Functions (alphabetical)
    "add_interactive_features",
    "analyze_budget",
    "append_expense_to_file",
    "auto_backup",
    "batch_process",
    "budget_comparison_chart",
    "cached",
    "category_from_string",
    "chart",
    "check_budget_alerts",
    "check_password_strength",
    "clear_cache",
    "compare_payoff_methods",
    "convert",
    "count_formats",
    "create_bill_from_template",
    "create_budget_dashboard",
    "create_common_recurring",
    "create_debt_payoff_plan",
    "create_emergency_fund",
    "create_mcp_server",
    "create_monthly_budget",
    "create_spending_pie_chart",
    "create_spreadsheet",
    "detect_format",
    "detect_shell",
    "export_dual",
    "export_for_ai",
    "export_to",
    "export_to_csv",
    "export_to_pdf",
    "export_to_xlsx",
    "export_training_data",
    "format_currency",
    "formula",
    "generate_bash_completions",
    "generate_budget_dashboard",
    "generate_dashboard",
    "generate_fish_completions",
    "generate_monthly_report",
    "generate_password",
    "generate_zsh_completions",
    "get_cache",
    "get_category_manager",
    "get_config",
    "get_currency",
    "get_default_accounts",
    "get_format",
    "import_bank_csv",
    "import_from",
    "init_config_file",
    "install_completions",
    "list_currencies",
    "list_formats",
    "load_definition",
    "money",
    "print_completion_script",
    "render_sheets",
    "save_definition",
    "sparkline",
    "spending_pie_chart",
    "stream_read",
    "stream_write",
    "timed",
    "trend_line_chart",
    "upload_budget",
]
