# 02_formulas - Calculations and Analysis

Master budget analysis and reporting with formulas and data processing.

## Prerequisites

- **Completed**: [01_basics](../01_basics/) - Fundamental spreadsheet creation
- **Skills needed**: Basic Python, understanding of pandas DataFrames (helpful)
- **Time**: 45-60 minutes

## Learning Objectives

By completing these examples, you'll learn how to:

1. **Analyze budgets** - Extract insights from budget data using pandas
2. **Generate reports** - Create text, markdown, and JSON reports
3. **Filter data** - Query expenses by date ranges and categories
4. **Calculate metrics** - Compute totals, percentages, and breakdowns
5. **Export analysis** - Save reports in multiple formats
6. **Build workflows** - Create realistic multi-step budget processes

## Examples in This Section

### 01_analyze_budget.py

**What it does**: Analyze budget data with pandas and extract insights

**Concepts covered**:

- BudgetAnalyzer class usage
- Summary statistics (total budget, spent, remaining)
- Category breakdown analysis
- Date range filtering
- Direct pandas DataFrame operations
- JSON export of analysis

**Run it**:

```bash
uv run python examples/02_formulas/01_analyze_budget.py
```

**Expected output**: Console output showing budget analysis

**Key code**:

```python
from spreadsheet_dl.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer(budget_path)
summary = analyzer.get_summary()
print(f"Total Budget: ${summary.total_budget:,.2f}")
print(f"Total Spent: ${summary.total_spent:,.2f}")
```

---

### 02_generate_reports.py

**What it does**: Generate budget reports in multiple formats

**Concepts covered**:

- ReportGenerator class
- Text report generation
- Markdown report formatting
- JSON data export
- Custom report configuration (ReportConfig)
- Visualization data preparation
- Convenience functions

**Run it**:

```bash
uv run python examples/02_formulas/02_generate_reports.py
```

**Expected output**:

- `output/reports/budget_report.txt`
- `output/reports/budget_report.md`
- `output/reports/budget_report.json`

**Key code**:

```python
from spreadsheet_dl.report_generator import ReportGenerator, ReportConfig

generator = ReportGenerator(ods_path)
report = generator.generate_text_report()
generator.save_report(output_path, format="markdown")
```

---

### 03_custom_reports.py

**What it does**: Create custom analysis reports tailored to specific needs

**Concepts covered**:

- Custom analysis workflows
- Combining BudgetAnalyzer and ReportGenerator
- Category spending breakdown
- Alert generation for overspending
- Multi-format output
- Report customization

**Run it**:

```bash
uv run python examples/02_formulas/03_custom_reports.py
```

**Expected output**:

- `output/report.txt`
- `output/report.md`
- `output/report.json`
- Console output with custom analysis

**Key code**:

```python
analyzer = BudgetAnalyzer(budget_file)
generator = ReportGenerator(budget_file)

# Custom analysis
by_category = analyzer.get_category_breakdown()
for category, amount in sorted(by_category.items()):
    print(f"{category}: ${amount:,.2f}")
```

---

### 04_realistic_workflow.py

**What it does**: Demonstrates a complete real-world budget workflow

**Concepts covered**:

- Building comprehensive monthly budgets
- Multiple expense categories
- Week-by-week expense tracking
- Holiday and seasonal expenses
- Complete budget allocation setup
- Summary statistics calculation
- Top spending analysis

**Run it**:

```bash
uv run python examples/02_formulas/04_realistic_workflow.py
```

**Expected output**: `output/december_2025_family_budget.ods` with detailed summary

**Demonstrates**:

- 19 expense entries across December 2025
- 16 budget categories (housing, utilities, groceries, etc.)
- Real-world amounts and descriptions
- Category spending analysis
- Budget vs. actual comparison

## Key Concepts

### BudgetAnalyzer

Analyze budget data with pandas integration:

```python
from spreadsheet_dl.budget_analyzer import BudgetAnalyzer

analyzer = BudgetAnalyzer("path/to/budget.ods")

# Get summary
summary = analyzer.get_summary()
# -> total_budget, total_spent, total_remaining, percent_used, alerts

# Category breakdown
breakdown = analyzer.get_category_breakdown()
# -> {"Groceries": Decimal("752.45"), "Transportation": ...}

# Filter by date
week1 = analyzer.filter_by_date_range(
    date(2025, 1, 1),
    date(2025, 1, 7)
)
# -> pandas DataFrame

# Access raw data
expenses_df = analyzer.expenses  # pandas DataFrame
budget_df = analyzer.budget      # pandas DataFrame
```

### ReportGenerator

Generate formatted reports:

```python
from spreadsheet_dl.report_generator import (
    ReportGenerator,
    ReportConfig
)

generator = ReportGenerator("path/to/budget.ods")

# Text report
text = generator.generate_text_report()

# Markdown report
markdown = generator.generate_markdown_report()

# Save to file
generator.save_report(Path("report.md"), format="markdown")
generator.save_report(Path("report.json"), format="json")

# Custom config
config = ReportConfig(
    include_category_breakdown=True,
    include_trends=False,
    include_alerts=True
)
generator = ReportGenerator(ods_path, config=config)
```

### Convenience Functions

Quick analysis without classes:

```python
from spreadsheet_dl.budget_analyzer import analyze_budget
from spreadsheet_dl.report_generator import generate_monthly_report

# Analyze and get dict
data = analyze_budget("budget.ods")

# Generate report
report_str = generate_monthly_report("budget.ods", format="text")
# or save to directory
report_path = generate_monthly_report(
    "budget.ods",
    output_dir=Path("reports")
)
```

## Estimated Time

- **Quick review**: 15 minutes (read code, understand concepts)
- **Run all examples**: 20 minutes
- **Hands-on practice**: 45-60 minutes (modify, create custom analysis)

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pandas'`
**Solution**: Pandas is a core dependency. Reinstall SpreadsheetDL:

```bash
uv add spreadsheet-dl
```

**Issue**: `FileNotFoundError: Budget file not found`
**Solution**: Run 01_basics examples first to create sample budget files, or provide your own ODS file

**Issue**: Empty DataFrames or zero totals
**Solution**: Ensure the budget file has the correct sheet structure (Expenses and Budget sheets)

**Issue**: Date filtering returns no results
**Solution**: Check date ranges match actual expense dates in your budget file

## Tips and Best Practices

1. **Always check file existence** before analysis:

   ```python
   if not budget_path.exists():
       print(f"File not found: {budget_path}")
       return
   ```

2. **Use Decimal for currency** to avoid floating-point errors:

   ```python
   from decimal import Decimal
   total = sum(Decimal(str(amount)) for amount in amounts)
   ```

3. **Handle empty DataFrames** gracefully:

   ```python
   if not expenses_df.empty:
       # Process data
   else:
       print("No expense data found")
   ```

4. **Combine analysis methods** for richer insights:

   ```python
   summary = analyzer.get_summary()
   breakdown = analyzer.get_category_breakdown()
   # Correlate the two for detailed analysis
   ```

## Next Steps

Ready for visualization? Move on to:

**[03_charts](../03_charts/)** - Learn how to create charts and visual representations of your budget data

## Additional Resources

- [BudgetAnalyzer API Reference](../../docs/api/_builder/core.md)
- [ReportGenerator API Reference](../../docs/api/_builder/core.md)
- [Pandas Documentation](https://pandas.pydata.org/docs/) - For advanced DataFrame operations
- [SpreadsheetDL Formulas Guide](../../docs/guides/formulas.md)

## Questions?

- Review the API documentation
- Check example source code for detailed comments
- Open an issue on GitHub for bugs or feature requests
