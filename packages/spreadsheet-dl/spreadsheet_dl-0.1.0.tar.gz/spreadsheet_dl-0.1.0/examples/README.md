# SpreadsheetDL Examples - Learning Path

Welcome to the SpreadsheetDL examples! This directory contains a structured learning path from basic concepts to advanced integrations.

## Learning Path Structure

The examples are organized into progressive levels:

```
examples/
├── 01_basics/                  ← Start here
├── 02_formulas/                ← Add calculations
├── 03_charts/                  ← Visualize data
├── 04_advanced/                ← Extend with plugins
├── 05_domain_plugins/          ← Domain-specific examples
├── 06_security_and_export/     ← Security & format export
└── template_engine/            ← Advanced templates
```

### Prerequisites

- Python 3.12 or higher
- SpreadsheetDL installed (`uv add spreadsheet-dl` or `uv pip install spreadsheet-dl`)
- Basic familiarity with Python

### Estimated Time

- **Total learning path**: 3-4 hours
- **Quick start** (basics only): 30-45 minutes
- **Core skills** (basics + formulas): 1.5-2 hours
- **Full mastery** (all levels): 3-4 hours

## 01_basics - Getting Started

**Start here if you're new to SpreadsheetDL**

Learn the fundamentals:

- Create your first budget spreadsheet
- Customize budget categories and allocations
- Import data from CSV files
- Use progress indicators for long operations

**Time**: 30-45 minutes
**Next**: [02_formulas](./02_formulas/)

## 02_formulas - Calculations and Analysis

**Prerequisites**: Complete 01_basics

Add intelligence to your spreadsheets:

- Analyze budget data with pandas
- Generate text, markdown, and JSON reports
- Create custom analysis workflows
- Build realistic multi-category budgets

**Time**: 45-60 minutes
**Next**: [03_charts](./03_charts/)

## 03_charts - Data Visualization

**Prerequisites**: Complete 02_formulas

Make your data visual:

- Create basic charts (pie, bar, line)
- Use advanced chart builder features
- Customize colors and styles
- Add sparklines for compact visualizations

**Time**: 45 minutes
**Next**: [04_advanced](./04_advanced/)

## 04_advanced - Integration and Extension

**Prerequisites**: Complete 03_charts

Extend SpreadsheetDL:

- Build custom domain plugins
- Integrate with MCP (Model Context Protocol)
- Create MCP servers for LLM integration
- Extend functionality for your specific needs

**Time**: 60 minutes
**Next**: [05_domain_plugins](./05_domain_plugins/)

## 05_domain_plugins - Specialized Functions

**Prerequisites**: Complete 01_basics

Leverage domain-specific plugins:

- Finance domain (budgets, analysis)
- Data science functions
- Engineering calculations
- Life sciences formulas

**Time**: 30 minutes
**Next**: [06_security_and_export](./06_security_and_export/)

## 06_security_and_export - Security & Export

**Prerequisites**: Complete 01_basics

Secure and share your spreadsheets:

- Export to XLSX (Excel format)
- Password strength validation
- File encryption/decryption
- Automated backups with integrity checks

**Time**: 30 minutes

## Running Examples

Each example is a standalone Python script. Run any example with:

```bash
uv run python examples/01_basics/01_hello_budget.py
```

Or using system Python:

```bash
python examples/01_basics/01_hello_budget.py
```

## Output Files

Examples create output files in the `output/` directory:

```
output/
├── *.ods           # OpenDocument Spreadsheets
├── *.xlsx          # Excel files (if xlsxwriter installed)
├── *.pdf           # PDF exports (if reportlab installed)
├── reports/        # Generated reports
└── ...
```

## Template Engine Usage

The `template_engine/` directory contains advanced examples for template-based workflows. These are separate from the main learning path and demonstrate template engine capabilities.

## Additional Resources

- **Documentation**: https://lair-click-bats.github.io/spreadsheet-dl/
- **GitHub**: https://github.com/lair-click-bats/spreadsheet-dl
- **Issues**: Report bugs or request features at https://github.com/lair-click-bats/spreadsheet-dl/issues

## Philosophy

SpreadsheetDL provides **universal tools, not templates**. You get composable building blocks (formulas, styles, formats) that work for ANY use case, rather than rigid pre-built templates.

This approach gives you maximum flexibility to create exactly what you need.

## Next Steps

1. Start with [01_basics](./01_basics/) if you're new
2. Jump to specific topics if you have experience
3. Check [template_engine](./template_engine/) for advanced patterns
4. Read the [documentation](https://lair-click-bats.github.io/spreadsheet-dl/) for API reference

Happy building!
