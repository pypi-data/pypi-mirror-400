# SpreadsheetDL

[![MCP](https://img.shields.io/badge/MCP-native%20server-purple.svg)](docs/MCP_INTEGRATION.md)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/lair-click-bats/spreadsheet-dl/releases)
[![Status](https://img.shields.io/badge/status-beta-orange.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-4702%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)](tests/)
[![Property Tests](https://img.shields.io/badge/property--based%20tests-103+-blue.svg)](docs/testing-philosophy.md)
[![Validated](https://img.shields.io/badge/scientifically%20validated-NIST%7CCODATA-informational.svg)](docs/scientific-validation.md)

**The Universal Spreadsheet Definition Language**

Define spreadsheets declaratively in Python or YAML, export to ODS/XLSX/PDF. Built for AI integration with native MCP server. 11 domain plugins with 317+ specialized formulas.

---

## Overview

SpreadsheetDL is a declarative spreadsheet definition language that lets you define structure, formulas, and styling once—then export to any format.

**Key Features:**

- 🤖 **[MCP-Native](docs/MCP_INTEGRATION.md)** - Built-in Model Context Protocol server for AI assistants
- 📝 **Declarative API** - Define what you want, not how to build it (10 lines vs 100)
- 🌍 **Multi-Format** - Single definition → ODS, XLSX, PDF
- 🔧 **[Domain Plugins](docs/api/domain-plugins.md)** - 11 specialized domains (physics, engineering, finance, data science, etc.)
- ⚡ **Type-Safe Formulas** - FormulaBuilder with circular reference detection
- 🎨 **[Theme System](docs/user-guide.md#themes)** - Professional styling without cell-by-cell code
- 🔒 **[Security Hardening](SECURITY.md)** - XXE protection, ZIP bomb detection, path traversal prevention

**vs openpyxl/xlsxwriter:**

- MCP-native (AI integration from day one)
- Declarative (not imperative cell-by-cell)
- Multi-format (not Excel-only)
- Domain-aware (317+ specialized formulas)

---

## Quick Start

### Installation

**PyPI Package (Ready - Publishing in Progress):**

Package is built and ready for publication. Once credentials are configured, install with:

```bash
uv pip install spreadsheet-dl                    # Basic installation
uv pip install spreadsheet-dl[security]          # With security enhancements (recommended)
uv pip install spreadsheet-dl[all]               # All features and domains
```

**Install from Source (Current):**

```bash
git clone https://github.com/lair-click-bats/spreadsheet-dl.git
cd spreadsheet-dl
uv sync
```

See [Installation Guide](docs/installation.md) for detailed options.

### Quick Example

```python
from spreadsheet_dl import create_spreadsheet, formula

# Define spreadsheet declaratively
builder = create_spreadsheet(theme="corporate")
builder.sheet("Q1 Budget") \
    .column("Category", width="5cm") \
    .column("Amount", width="4cm", type="currency") \
    .column("% of Total", width="4cm", type="percent") \
    .header_row() \
    .row().cell("Rent").cell(1500).cell(formula=formula().divide("B2", "B5")) \
    .row().cell("Utilities").cell(300).cell(formula=formula().divide("B3", "B5")) \
    .row().cell("Total").cell(formula=formula().sum("B2:B3"))

# Export to any format
builder.save("budget.ods")        # Native ODS
builder.export("budget.xlsx")     # Excel
builder.export("budget.pdf")      # PDF
```

**Result**: Professional spreadsheet with formulas, styling, and formatting—in 10 lines instead of 100.

### Next Steps

**For Users:**

- 📖 [Getting Started Guide](docs/getting-started.md) - Your first spreadsheet in 5 minutes
- 🎓 [Tutorials](docs/tutorials/) - Step-by-step learning path
- 📚 [User Guide](docs/user-guide.md) - Complete documentation
- 🔧 [CLI Reference](docs/cli.md) - Command-line usage

**For Developers:**

- 🧪 [Test Suite Guide](tests/README.md) - Running and writing tests with markers
- 🤝 [Contributing Guide](CONTRIBUTING.md) - Development setup and workflow

---

## Why SpreadsheetDL?

### Declarative Paradigm

SpreadsheetDL brings declarative design to spreadsheets—the same paradigm shift that transformed other domains:

| Domain             | Imperative          | Declarative       |
| ------------------ | ------------------- | ----------------- |
| **Data**           | Cursors, loops      | SQL               |
| **Infrastructure** | Manual provisioning | Terraform         |
| **UI**             | DOM manipulation    | React             |
| **Spreadsheets**   | openpyxl            | **SpreadsheetDL** |

**Code Comparison:**

```python
# openpyxl (imperative - 15+ lines)
ws['A1'] = 'Category'
ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
ws['A1'].fill = PatternFill(start_color='366092', fill_type='solid')
ws['A1'].alignment = Alignment(horizontal='center')
ws.column_dimensions['A'].width = 20
# ... repeat for every cell ...

# SpreadsheetDL (declarative - 3 lines)
builder.sheet("Budget") \
    .column("Category", width="5cm") \
    .header_row()  # Theme handles all styling
```

### MCP-Native Integration

The **only** spreadsheet library with native [Model Context Protocol](docs/MCP_INTEGRATION.md) support:

```
You: "Create a Q1 budget spreadsheet with corporate theme"
Claude (via MCP): *generates professional ODS with formulas and formatting*

You: "Add a chart showing spending by category"
Claude (via MCP): *adds chart with proper data references*
```

Built for AI integration from day one—not retrofitted.

### Format Freedom

One definition, any output:

- **ODS** - Native format, open standard (LibreOffice, Collabora)
- **XLSX** - Microsoft Excel compatibility
- **PDF** - Distribution and reporting

Never be locked into a proprietary format.

### Domain Expertise

11 specialized domains with 317+ formulas: [Physics](docs/api/domains/physics/), [Data Science](docs/api/domains/data_science/), [Engineering](docs/api/domains/electrical_engineering/) (electrical, mechanical, civil), [Chemistry](docs/api/domains/chemistry/), [Biology](docs/api/domains/biology/), [Manufacturing](docs/api/domains/manufacturing/), [Finance](docs/api/domains/finance/), [Education](docs/api/domains/education/).

Domain expertise you don't have to recreate for every project. See [Domain Plugins Documentation](docs/api/domain-plugins.md).

---

## Documentation

### User Guides

- **[Getting Started](docs/getting-started.md)** - Installation and first spreadsheet
- **[User Guide](docs/user-guide.md)** - Complete feature documentation
- **[CLI Reference](docs/cli.md)** - Command-line interface
- **[Best Practices](docs/guides/best-practices.md)** - Tips and patterns

### Tutorials

Learn step-by-step:

1. [Create Your First Spreadsheet](docs/tutorials/01-create-budget.md)
2. [Working with Data](docs/tutorials/02-track-expenses.md)
3. [Domain Plugins](docs/tutorials/03-import-bank-data.md)
4. [Generate Reports](docs/tutorials/04-create-reports.md)
5. [MCP Integration](docs/tutorials/05-use-mcp-tools.md)
6. [Custom Themes](docs/tutorials/06-customize-themes.md)

### Technical Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and structure
- **[API Reference](docs/api/)** - Complete Python API documentation
- **[MCP Integration](docs/MCP_INTEGRATION.md)** - Model Context Protocol setup
- **[Domain Plugins](docs/api/domain-plugins.md)** - Specialized domain APIs
- **[Error Codes](docs/error-codes.md)** - Error handling reference

### Examples

Working code in [`examples/`](examples/):

- Basic API usage, data import, report generation
- Chart creation, theming, domain-specific examples
- MCP integration from Python

---

## Built-in Themes

| Theme           | Description        | Style                          |
| --------------- | ------------------ | ------------------------------ |
| `default`       | Clean professional | Blue headers, green/red status |
| `corporate`     | Business-focused   | Navy blue, brown accents       |
| `minimal`       | Distraction-free   | Gray headers, subtle borders   |
| `dark`          | Dark mode          | Dark backgrounds, light text   |
| `high_contrast` | Accessibility      | Bold colors, large fonts       |

Create custom themes with YAML. See [Theme Creation Guide](docs/guides/theme-creation.md).

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, testing requirements, and commit message format.

For consistent messaging and terminology, see [BRANDING.md](BRANDING.md).

**Optional:** This repo includes [Claude Code configuration](.claude/README.md) for AI-assisted development.

---

## Security

SpreadsheetDL v0.1.0 includes comprehensive security hardening. See [SECURITY.md](SECURITY.md) for complete documentation.

**Recommended installation (once published to PyPI):**

```bash
uv pip install spreadsheet-dl[security]  # Includes defusedxml + cryptography
```

**Current (from source):**

```bash
uv sync  # Already includes security dependencies
```

---

## License

MIT License - See [LICENSE](LICENSE) file.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Recent releases:**

- **v0.1.0** (2026-01-06) - Initial public beta: Feature-complete, seeking community feedback

---

## Links

- **Documentation**: [docs/](docs/)
- **GitHub**: [github.com/lair-click-bats/spreadsheet-dl](https://github.com/lair-click-bats/spreadsheet-dl)
- **Issues**: [github.com/lair-click-bats/spreadsheet-dl/issues](https://github.com/lair-click-bats/spreadsheet-dl/issues)
- **PyPI**: [pypi.org/project/spreadsheet-dl](https://pypi.org/project/spreadsheet-dl)
