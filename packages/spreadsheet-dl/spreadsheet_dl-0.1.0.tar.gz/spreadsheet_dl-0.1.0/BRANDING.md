# SpreadsheetDL Brand Guidelines

**Version:** 1.1
**Last Updated:** 2026-01-06
**Purpose:** Contributor guidelines for consistent naming and terminology

---

## Name & Capitalization

### Official Name

**SpreadsheetDL** (one word, capital S, capital D, capital L)

### Package & Import Names

```python
# PyPI package name (lowercase, hyphenated)
uv pip install spreadsheet-dl

# Python import (lowercase, underscored)
import spreadsheet_dl
from spreadsheet_dl import create_spreadsheet

# CLI command (lowercase, hyphenated)
spreadsheet-dl generate
```

### Usage Rules

✅ **CORRECT:**

- SpreadsheetDL is a universal spreadsheet definition language
- The SpreadsheetDL project
- Using SpreadsheetDL for science
- Install `uv pip install spreadsheet-dl` (in code blocks)
- Import `spreadsheet_dl` (in code)

❌ **INCORRECT:**

- spreadsheetdl (no capitals)
- Spreadsheet-DL (hyphen in prose)
- spreadsheet-DL (mixed case)
- Spreadsheet DL (two words)
- SDL (conflicts with Simple DirectMedia Layer)

### Context-Specific Forms

| Context            | Form           | Example                           |
| ------------------ | -------------- | --------------------------------- |
| **Marketing copy** | SpreadsheetDL  | "SpreadsheetDL is the..."         |
| **Documentation**  | SpreadsheetDL  | "Using SpreadsheetDL, you can..." |
| **Package names**  | spreadsheet-dl | `uv pip install spreadsheet-dl`   |
| **Python imports** | spreadsheet_dl | `import spreadsheet_dl`           |
| **CLI commands**   | spreadsheet-dl | `spreadsheet-dl generate`         |
| **File names**     | spreadsheet-dl | `spreadsheet-dl-guide.md`         |
| **URLs**           | spreadsheet-dl | `github.com/.../spreadsheet-dl`   |

---

## Tagline

**The Universal Spreadsheet Definition Language**

Use this tagline consistently in documentation headers and project descriptions.

---

## Preferred Terminology

| Use This            | Not This                           |
| ------------------- | ---------------------------------- |
| SpreadsheetDL       | Spreadsheet DL, spreadsheetdl, SDL |
| definition language | DSL, description language          |
| declarative         | high-level, abstract               |
| domain plugin       | domain package, extension          |
| Builder API         | fluent API, builder pattern        |
| formula builder     | formula generator                  |
| theme               | style, stylesheet, skin            |
| MCP server          | MCP integration, MCP support       |
| export to ODS       | save as ODS, generate ODS          |

---

## Technical Terms

**First use:** Define it
**Subsequent:** Use directly
**Avoid:** Excessive jargon without context

Examples:

- **Good**: "SpreadsheetDL is a definition language that lets you declare spreadsheet structure..."
- **Bad**: "SpreadsheetDL leverages a domain-driven architecture paradigm to facilitate..."

---

## Domain-Specific Language

Use standard terminology for each domain:

- **Finance**: budget, invoice, P&L, financial statement
- **Science**: experiment log, dataset catalog, analysis
- **Engineering**: BOM, pin map, design calculation, tolerance
- **Manufacturing**: OEE, SPC, lean metrics, six sigma
- **Education**: gradebook, rubric, assessment analytics

---

## Tone Guidelines

### Documentation

- **Style**: Clear, precise, example-rich
- **Focus**: Explain "why" not just "how"
- **Examples**: Every concept has code example
- **Assumption**: Reader is competent Python developer

### Community (GitHub, Issues)

- **Style**: Welcoming, collaborative, patient
- **Focus**: Help, don't judge
- **Celebrate**: Contributions, milestones

### Announcements

- **Style**: Excited but not hyperbolic
- **Focus**: User value, not our effort
- **Examples**: Concrete metrics over vague claims
- **Voice**: Understated confidence

---

## Code Examples

### Formatting

- Use proper indentation (4 spaces)
- Include imports at top
- Add comments for clarity
- Show output when helpful

### Good Example

```python
from spreadsheet_dl import create_spreadsheet

# Create spreadsheet with corporate theme
builder = create_spreadsheet(theme="corporate")
builder.sheet("Budget").header_row()
builder.save("budget.ods")
```

### Bad Example

```python
# Missing imports, unclear purpose
builder.sheet("Budget")
```

---

## File Naming

### Documentation

- `README.md` (not readme.md)
- `BRANDING.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `LICENSE` (no extension)

### Code

- `spreadsheet_dl/` (directory)
- `builder.py` (not Builder.py)
- `test_builder.py` (test files)

### Examples

- `example-budget.py` (hyphenated)
- `tutorial-1-basic-api.md`

---

## Version Naming

Format: `MAJOR.MINOR.PATCH[-PRERELEASE]`

Examples:

- `4.0.0` (stable release)
- `4.0.0-alpha.1` (alpha prerelease)
- `4.1.0` (minor feature release)
- `4.0.1` (bugfix patch)

**No code names** - use version numbers only

---

## Legal

### Copyright Notice

```
Copyright (c) 2024-2026 lair-click-bats
Licensed under the MIT License
```

### Disclaimer

> SpreadsheetDL provides tools for creating spreadsheets with formulas. Users are responsible for validating calculations for their specific use case.

---

## Updates

This document is reviewed:

- **Major releases**: Update examples, version numbers
- **Quarterly**: Ensure consistency with actual usage
- **On feedback**: Incorporate community suggestions

**Owner**: Project maintainer
**Contributors**: Open to community input via GitHub issues

---

**Document Version:** 1.1
**Status:** Official - All project materials should follow these guidelines
