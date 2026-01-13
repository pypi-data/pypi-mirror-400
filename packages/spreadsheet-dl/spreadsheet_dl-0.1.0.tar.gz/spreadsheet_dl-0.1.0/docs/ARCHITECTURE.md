# Architecture Overview

## Version 0.1.0 - Universal Spreadsheet Definition Language

This document describes the architecture of SpreadsheetDL v0.1.0, a universal
spreadsheet definition language with LLM-optimized MCP server, multi-format support,
and professional-grade formatting capabilities.

**What's New in v0.1.0 (Initial Public Release):**

This release includes all features developed during internal iterations (v4.x series):

- **Property-Based Testing**: 103+ new tests with Hypothesis for mathematical correctness
- **Scientific Validation**: Tests against NIST CODATA 2018 reference values
- **Universal Format**: SpreadsheetDL spec works across ODS, XLSX, CSV, PDF
- **MCP Server**: Extensive tools for AI-driven spreadsheet manipulation
- **Domain Plugins**: 11 scientific/engineering domains with comprehensive formula libraries
- **Theme Variants**: Light, dark, and high-contrast themes
- **Streaming I/O**: Handle 100k+ row files efficiently
- **Round-Trip**: Import and export with 95%+ fidelity preservation
- **Format Adapters**: Pluggable export to multiple formats
- **Security Hardening**: Formula sanitization, rate limiting, audit logging

**Development History:**

The following sections document features developed during internal iterations (v0.1.0, v0.1.0) prior to public release.

**Features from v0.1.0 (Internal):**

- Property-Based Testing with Hypothesis
- Scientific Validation against NIST CODATA 2018
- ODF formula prefix consistency fixes

**Features from v0.1.0 (Internal):**

- **Universal Format**: SpreadsheetDL spec works across ODS, XLSX, CSV, PDF
- **MCP Server**: Extensive tools for AI-driven spreadsheet manipulation
- **Domain Plugins**: 11 scientific/engineering domains with comprehensive formula libraries
- **Theme Variants**: Light, dark, and high-contrast themes
- **Streaming I/O**: Handle 100k+ row files efficiently
- **Round-Trip**: Import and export with 95%+ fidelity preservation
- **Format Adapters**: Pluggable export to multiple formats
- **Security Hardening**: Formula sanitization, rate limiting, audit logging

---

## Architecture Diagrams

### High-Level System Architecture

```mermaid
flowchart TB
    subgraph "User Interfaces"
        CLI[CLI Application<br/>typer-based]
        MCP[MCP Server<br/>AI Integration]
        API[Python API<br/>Direct Import]
    end

    subgraph "Core Engine"
        Builder[SpreadsheetBuilder<br/>Fluent API]
        Templates[Template Engine<br/>YAML Processing]
        Formulas[Formula Engine<br/>ODF Formulas]
    end

    subgraph "Domain Plugins"
        Physics[Physics<br/>25 formulas]
        Chemistry[Chemistry<br/>20 formulas]
        Biology[Biology<br/>17 formulas]
        DataSci[Data Science<br/>20 formulas]
        Finance[Finance<br/>15 formulas]
        EE[Electrical Eng<br/>15 formulas]
        ME[Mechanical Eng<br/>16 formulas]
        CE[Civil Eng<br/>12 formulas]
        Env[Environmental<br/>15 formulas]
        Mfg[Manufacturing<br/>12 formulas]
        Edu[Education<br/>27 formulas]
    end

    subgraph "Renderers"
        ODS[ODS Renderer<br/>odfpy]
        XLSX[XLSX Renderer<br/>openpyxl]
        Stream[Streaming Writer<br/>Large Files]
    end

    subgraph "Export Formats"
        ODSFile[.ods Files]
        XLSXFile[.xlsx Files]
        CSVFile[.csv Files]
        JSONFile[.json Files]
        PDFFile[.pdf Reports]
        HTMLFile[.html Dashboards]
    end

    CLI --> Builder
    MCP --> Builder
    API --> Builder

    Builder --> Templates
    Builder --> Formulas
    Templates --> Formulas

    Physics --> Formulas
    Chemistry --> Formulas
    Biology --> Formulas
    DataSci --> Formulas
    Finance --> Formulas
    EE --> Formulas
    ME --> Formulas
    CE --> Formulas
    Env --> Formulas
    Mfg --> Formulas
    Edu --> Formulas

    Formulas --> ODS
    Formulas --> XLSX
    Formulas --> Stream

    ODS --> ODSFile
    XLSX --> XLSXFile
    Stream --> ODSFile
    Stream --> XLSXFile

    ODS --> CSVFile
    ODS --> JSONFile
    ODS --> PDFFile
    ODS --> HTMLFile
```

### MCP Server Architecture

```mermaid
flowchart LR
    subgraph "AI Clients"
        Claude[Claude Desktop]
        Other[Other MCP Clients]
    end

    subgraph "MCP Server"
        Server[MCPServer<br/>stdio transport]
        Registry[Tool Registry<br/>Decorator-based]
        Config[MCPConfig<br/>Settings]

        subgraph "Tool Categories"
            Spreadsheet[Spreadsheet Tools<br/>create, open, save]
            Cell[Cell Operations<br/>get, set, clear, copy]
            Sheet[Sheet Management<br/>create, delete, rename]
            Formula[Formula Tools<br/>evaluate, list, apply]
            Chart[Chart Tools<br/>create, configure]
            Style[Style Tools<br/>apply, create themes]
            Data[Data Tools<br/>validate, filter, sort]
            Export[Export Tools<br/>multi-format]
        end

        subgraph "Security Layer"
            RateLimit[Rate Limiter<br/>Per-tool limits]
            Sanitizer[Formula Sanitizer<br/>Injection prevention]
            Audit[Audit Logger<br/>Operation tracking]
        end
    end

    subgraph "Backend"
        Builder2[SpreadsheetBuilder]
        Renderer2[Renderers]
        Plugins[Domain Plugins]
    end

    Claude --> Server
    Other --> Server

    Server --> Registry
    Server --> Config

    Registry --> Spreadsheet
    Registry --> Cell
    Registry --> Sheet
    Registry --> Formula
    Registry --> Chart
    Registry --> Style
    Registry --> Data
    Registry --> Export

    Spreadsheet --> RateLimit
    Cell --> RateLimit
    Sheet --> RateLimit
    Formula --> Sanitizer

    RateLimit --> Audit
    Sanitizer --> Audit

    Audit --> Builder2
    Builder2 --> Renderer2
    Renderer2 --> Plugins
```

### Domain Plugin Architecture

```mermaid
flowchart TB
    subgraph "Plugin Interface"
        Base[DomainPlugin<br/>Abstract Base Class]
        BaseFormula[FormulaBase<br/>Formula Interface]
    end

    subgraph "Plugin Implementation"
        Plugin[Concrete Plugin<br/>e.g., PhysicsPlugin]

        subgraph "Formula Categories"
            Cat1[Category 1<br/>e.g., Mechanics]
            Cat2[Category 2<br/>e.g., Thermodynamics]
            Cat3[Category 3<br/>e.g., Electromagnetism]
        end

        subgraph "Importers"
            Imp1[Domain Importer 1<br/>e.g., Lab Data]
            Imp2[Domain Importer 2<br/>e.g., Sensor Data]
        end

        Utils[Domain Utilities<br/>Helper Functions]
    end

    subgraph "Registration"
        Registry2[Formula Registry<br/>Name -> Formula Map]
        Metadata[Formula Metadata<br/>Description, Args, Units]
    end

    Base --> Plugin
    BaseFormula --> Cat1
    BaseFormula --> Cat2
    BaseFormula --> Cat3

    Plugin --> Cat1
    Plugin --> Cat2
    Plugin --> Cat3
    Plugin --> Imp1
    Plugin --> Imp2
    Plugin --> Utils

    Cat1 --> Registry2
    Cat2 --> Registry2
    Cat3 --> Registry2

    Registry2 --> Metadata
```

### Data Flow Architecture

```mermaid
flowchart TB
    subgraph "Input Sources"
        YAML[YAML Templates]
        CSV[CSV Files]
        Bank[Bank APIs<br/>Plaid]
        Manual[Manual Entry<br/>CLI/API]
        Import[Domain Importers<br/>Lab/Sensor Data]
    end

    subgraph "Processing Pipeline"
        Parse[Parser<br/>Template/Data]
        Validate[Validator<br/>Schema/Rules]
        Transform[Transformer<br/>Apply Formulas]
        Build[Builder<br/>Construct Spec]
    end

    subgraph "Specification Layer"
        WorkbookSpec[WorkbookSpec<br/>Complete Model]
        SheetSpec[SheetSpec<br/>Sheet Definition]
        CellSpec[CellSpec<br/>Cell Data/Style]
        ChartSpec[ChartSpec<br/>Visualization]
    end

    subgraph "Rendering Layer"
        ODSRender[ODS Renderer<br/>OpenDocument]
        XLSXRender[XLSX Renderer<br/>Excel Format]
        StreamRender[Streaming Renderer<br/>Large Files]
    end

    subgraph "Output Targets"
        LocalFS[Local Filesystem]
        Cloud[Cloud Storage<br/>Nextcloud/WebDAV]
        AIExport[AI Export<br/>Semantic JSON]
    end

    YAML --> Parse
    CSV --> Parse
    Bank --> Parse
    Manual --> Parse
    Import --> Parse

    Parse --> Validate
    Validate --> Transform
    Transform --> Build

    Build --> WorkbookSpec
    WorkbookSpec --> SheetSpec
    SheetSpec --> CellSpec
    SheetSpec --> ChartSpec

    WorkbookSpec --> ODSRender
    WorkbookSpec --> XLSXRender
    WorkbookSpec --> StreamRender

    ODSRender --> LocalFS
    XLSXRender --> LocalFS
    StreamRender --> LocalFS

    LocalFS --> Cloud
    LocalFS --> AIExport
```

### Builder Pattern Architecture

```mermaid
flowchart LR
    subgraph "Fluent Builder API"
        SB[SpreadsheetBuilder<br/>Entry Point]

        subgraph "Configuration Methods"
            Theme[.with_theme]
            Meta[.with_metadata]
            Config2[.with_config]
        end

        subgraph "Content Methods"
            AddSheet[.add_sheet]
            AddRow[.add_row]
            AddCell[.add_cell]
            AddFormula[.add_formula]
            AddChart[.add_chart]
        end

        subgraph "Style Methods"
            Style2[.with_style]
            Cond[.with_conditional]
            Valid[.with_validation]
        end

        Build2[.build]
    end

    subgraph "Output"
        Spec[WorkbookSpec]
        ODS2[.to_ods]
        XLSX2[.to_xlsx]
        Multi[.to_format]
    end

    SB --> Theme
    SB --> Meta
    SB --> Config2

    Theme --> AddSheet
    Meta --> AddSheet
    Config2 --> AddSheet

    AddSheet --> AddRow
    AddRow --> AddCell
    AddCell --> AddFormula
    AddCell --> AddChart

    AddFormula --> Style2
    AddChart --> Style2
    Style2 --> Cond
    Cond --> Valid

    Valid --> Build2
    Build2 --> Spec

    Spec --> ODS2
    Spec --> XLSX2
    Spec --> Multi
```

### Security Architecture

```mermaid
flowchart TB
    subgraph "Security Boundaries"
        Input[User Input<br/>Formulas, Data]

        subgraph "Input Validation"
            Sanitize[Formula Sanitizer<br/>Injection Prevention]
            PathCheck[Path Validator<br/>Traversal Prevention]
            SizeCheck[Size Limiter<br/>DoS Prevention]
        end

        subgraph "Access Control"
            RateLimit2[Rate Limiter<br/>Request Throttling]
            FileAccess[File Access Control<br/>Allowed Paths]
            PluginVerify[Plugin Verification<br/>Signature Check]
        end

        subgraph "Data Protection"
            Encrypt[AES-256-GCM<br/>Encryption at Rest]
            Creds[Credential Store<br/>Secure Storage]
            Mask[Data Masking<br/>PII Protection]
        end

        subgraph "Audit Trail"
            Logger[Audit Logger<br/>All Operations]
            Rotate[Log Rotation<br/>Automatic Cleanup]
        end
    end

    Input --> Sanitize
    Input --> PathCheck
    Input --> SizeCheck

    Sanitize --> RateLimit2
    PathCheck --> FileAccess
    SizeCheck --> PluginVerify

    RateLimit2 --> Encrypt
    FileAccess --> Creds
    PluginVerify --> Mask

    Encrypt --> Logger
    Creds --> Logger
    Mask --> Logger
    Logger --> Rotate
```

---

## Project Structure

```
spreadsheet-dl/
├── docs/                         # Documentation
├── examples/                     # Usage examples
│   ├── 01_basics/
│   ├── 02_formulas/
│   ├── 03_charts/
│   ├── 04_advanced/
│   └── template_engine/
├── src/
│   └── spreadsheet_dl/          # Main package (250+ symbols)
│       ├── _builder/             # Builder internals
│       │   ├── __init__.py
│       │   ├── core.py
│       │   ├── models.py
│       │   └── references.py
│       ├── _cli/                 # CLI implementation
│       │   ├── __init__.py
│       │   ├── app.py
│       │   ├── commands.py
│       │   └── utils.py
│       ├── _mcp/                 # MCP server implementation (77+ tools)
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── exceptions.py
│       │   ├── handlers.py
│       │   ├── models.py
│       │   └── registry.py
│       ├── domains/              # Domain plugins (11 domains)
│       │   ├── biology/
│       │   ├── chemistry/
│       │   ├── civil_engineering/
│       │   ├── data_science/
│       │   ├── education/
│       │   ├── electrical_engineering/
│       │   ├── environmental/
│       │   ├── finance/
│       │   ├── manufacturing/
│       │   ├── mechanical_engineering/
│       │   ├── physics/
│       │   ├── __init__.py
│       │   └── base.py
│       ├── schema/               # Schema extensions
│       │   ├── advanced.py
│       │   ├── conditional.py
│       │   ├── data_validation.py
│       │   ├── print_layout.py
│       │   ├── typography.py
│       │   └── units.py
│       ├── themes/               # Built-in themes
│       ├── __init__.py
│       ├── ai_export.py
│       ├── ai_training.py
│       ├── budget_analyzer.py
│       ├── builder.py
│       ├── charts.py
│       ├── cli.py
│       ├── export.py
│       ├── interactive.py
│       ├── mcp_server.py
│       ├── plaid_integration.py
│       ├── renderer.py
│       ├── report_generator.py
│       ├── security.py
│       ├── streaming.py
│       ├── template_engine.py
│       ├── visualization.py
│       └── xlsx_renderer.py
├── templates/                    # YAML theme templates
└── tests/                        # Test suite (3,200+ tests)
    ├── benchmarks/
    ├── domains/
    ├── integration/
    ├── mcp/
    ├── security/
    ├── unit/
    └── xlsx/
```

---

## Core Components

### 1. SpreadsheetBuilder (Fluent API)

The primary API for creating spreadsheets programmatically.

```python
from spreadsheet_dl import SpreadsheetBuilder

workbook = (
    SpreadsheetBuilder()
    .with_theme("professional")
    .add_sheet("Summary")
        .add_header_row(["Category", "Budget", "Actual", "Variance"])
        .add_data_row(["Marketing", 50000, 48500, "=B2-C2"])
        .add_data_row(["Engineering", 120000, 115000, "=B3-C3"])
        .with_conditional_format("D2:D10", "negative_red")
    .add_sheet("Details")
        .from_dataframe(df)
    .build()
)

workbook.save("budget.ods")
```

### 2. Domain Plugin System

Extensible formula system with 11 scientific/engineering domains.

**Plugin Interface:**

```python
from spreadsheet_dl.domains.base import DomainPlugin, FormulaBase

class PhysicsDomainPlugin(DomainPlugin):
    name = "physics"
    version = "1.0.0"

    def initialize(self):
        self.register_formula("KINETIC_ENERGY", KineticEnergyFormula())
        self.register_formula("VELOCITY", VelocityFormula())

class KineticEnergyFormula(FormulaBase):
    name = "KINETIC_ENERGY"
    description = "Calculate kinetic energy: KE = 0.5 * m * v^2"
    arguments = ["mass", "velocity"]
    units = {"mass": "kg", "velocity": "m/s", "result": "J"}

    def build(self, mass: str, velocity: str) -> str:
        return f"of:=0.5*{mass}*POWER({velocity},2)"
```

### 3. Renderer System

Multi-format rendering with consistent output.

```python
from spreadsheet_dl import WorkbookSpec, OdsRenderer, XlsxRenderer

# Render to ODS
ods_renderer = OdsRenderer()
ods_renderer.render(workbook_spec, "output.ods")

# Render to XLSX
xlsx_renderer = XlsxRenderer()
xlsx_renderer.render(workbook_spec, "output.xlsx")

# Streaming for large files
from spreadsheet_dl import StreamingWriter

with StreamingWriter("large.ods", chunk_size=1000) as writer:
    writer.start_sheet("Data", columns=["A", "B", "C"])
    for row in data_generator():
        writer.write_row(row)
    writer.end_sheet()
```

### 4. MCP Server Integration

Native Model Context Protocol server for AI integration.

**Configuration (Claude Desktop):**

```json
{
  "mcpServers": {
    "spreadsheet-dl": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "spreadsheet-dl-mcp"],
      "env": {
        "FINANCE_DATA_DIR": "~/Documents/Finance"
      }
    }
  }
}
```

**Tool Categories (50+ tools):**

| Category    | Tools | Purpose                                |
| ----------- | ----- | -------------------------------------- |
| Spreadsheet | 6     | Create, open, save, properties         |
| Cell        | 8     | Get, set, clear, copy, move, format    |
| Sheet       | 6     | Create, delete, rename, list, copy     |
| Formula     | 5     | Evaluate, apply, list, domain formulas |
| Chart       | 4     | Create, configure, add series          |
| Style       | 5     | Apply, create, list themes             |
| Data        | 8     | Validate, filter, sort, import         |
| Export      | 5     | Multi-format, PDF, HTML                |
| Query       | 3     | Natural language queries               |

### 5. Template Engine

YAML-based declarative spreadsheet creation.

```yaml
# templates/budget.yaml
name: monthly_budget
version: '1.0'
variables:
  month: 'January'
  year: 2026

sheets:
  - name: '{{month}} {{year}}'
    columns:
      - name: Category
        type: text
        width: 20
      - name: Budget
        type: currency
        format: '$#,##0.00'
      - name: Actual
        type: currency
      - name: Variance
        type: formula
        formula: '=B{row}-C{row}'

    rows:
      - ['Marketing', 50000, 48500]
      - ['Engineering', 120000, 115000]
      - ['Operations', 30000, 32000]

    conditional:
      - range: 'D:D'
        rule: less_than_zero
        style: negative_red
```

### 6. Chart Builder

Comprehensive charting with multiple chart types.

```python
from spreadsheet_dl import ChartBuilder, ChartType

chart = (
    ChartBuilder()
    .set_type(ChartType.COLUMN)
    .set_title("Monthly Budget vs Actual")
    .add_series("Budget", "B2:B10", "A2:A10")
    .add_series("Actual", "C2:C10", "A2:A10")
    .set_legend_position("bottom")
    .set_axis_title("x", "Category")
    .set_axis_title("y", "Amount ($)")
    .build()
)
```

### 7. Security Module

Data protection and secure operations.

**Features:**

- AES-256-GCM encryption at rest
- PBKDF2-SHA256 key derivation (600K iterations)
- Formula sanitization (injection prevention)
- Rate limiting per tool
- Audit trail logging
- Secure credential storage

```python
from spreadsheet_dl import FileEncryptor, CredentialStore

# Encrypt sensitive files
encryptor = FileEncryptor()
encryptor.encrypt_file("sensitive.ods", password="secure123")

# Secure credential storage
creds = CredentialStore()
creds.store("api_key", "secret_value")
```

---

## Technology Stack

### Core Dependencies

| Library  | Purpose            | Version |
| -------- | ------------------ | ------- |
| odfpy    | ODS file creation  | ^1.4.1  |
| openpyxl | XLSX file creation | ^3.1.0  |
| pandas   | Data analysis      | ^2.0.0  |
| pyyaml   | Configuration      | ^6.0    |
| typer    | CLI framework      | ^0.9.0  |
| rich     | Terminal output    | ^13.0.0 |

### Optional Dependencies

| Library      | Purpose             | Install Extra |
| ------------ | ------------------- | ------------- |
| reportlab    | PDF export          | `[pdf]`       |
| plaid-python | Bank integration    | `[plaid]`     |
| cryptography | Enhanced encryption | `[security]`  |

---

## Performance Characteristics

### File Size Limits

| Operation          | Recommended  | Maximum         |
| ------------------ | ------------ | --------------- |
| Standard rendering | <10,000 rows | 50,000 rows     |
| Streaming write    | Any size     | Limited by disk |
| MCP operations     | <5,000 cells | 10,000 cells    |
| Chart data points  | <1,000       | 10,000          |

### Memory Usage

- Standard: ~50 bytes/cell
- Streaming: ~1KB buffer (configurable)
- Large file mode: Chunk-based, constant memory

### Benchmarks

| Operation          | Time (1000 rows) | Time (10000 rows) |
| ------------------ | ---------------- | ----------------- |
| Create ODS         | ~100ms           | ~800ms            |
| Create XLSX        | ~150ms           | ~1.2s             |
| Streaming write    | ~50ms            | ~400ms            |
| Formula evaluation | ~5ms             | ~50ms             |

---

## Extension Points

### Custom Domain Plugin

```python
from spreadsheet_dl.domains.base import DomainPlugin

class AstronomyPlugin(DomainPlugin):
    name = "astronomy"
    version = "1.0.0"

    def initialize(self):
        self.register_formula("PARSEC_TO_LY", ParsecToLightYearFormula())
        self.register_importer("fits", FITSImporter())
```

### Custom Renderer

```python
from spreadsheet_dl.renderer import BaseRenderer

class CustomRenderer(BaseRenderer):
    def render(self, spec: WorkbookSpec, output_path: str):
        # Custom rendering logic
        pass
```

### Custom MCP Tool

```python
from spreadsheet_dl._mcp import MCPToolRegistry

@MCPToolRegistry.register("custom_analysis")
def custom_analysis_tool(file_path: str, options: dict) -> dict:
    """Custom analysis tool for MCP."""
    # Implementation
    return {"result": "analysis complete"}
```

---

## Related Documentation

- [API Reference](./api/index.md)
- [Formula Reference](./reference/formula-reference.md)
- [MCP Tools Reference](./reference/mcp-tools-reference.md)
- [Examples Index](./reference/examples-index.md)
- [Plugin Development](./guides/plugin-development.md)
- [Security Guide](../SECURITY.md)
- [CLI Reference](./cli.md)
- [Modular Structure](./architecture/modular-structure.md)
