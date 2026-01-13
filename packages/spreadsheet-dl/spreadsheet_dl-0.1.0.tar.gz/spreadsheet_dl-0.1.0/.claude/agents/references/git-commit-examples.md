# Conventional Commit Examples and Format Rules

Comprehensive reference for conventional commit format, examples, and patterns used by git_commit_manager.

## Format Specification

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (Required)

| Type        | Description       | When to Use                                                    |
| ----------- | ----------------- | -------------------------------------------------------------- |
| `feat`      | New feature       | Adding new functionality                                       |
| `fix`       | Bug fix           | Fixing a bug or defect                                         |
| `docs`      | Documentation     | Adding or updating documentation (README, guides, API docs)    |
| `content`   | Knowledge content | Adding or updating knowledge base content, notes, articles     |
| `expert`    | Expert system     | Domain expert definitions, knowledge rules, agent capabilities |
| `structure` | Organization      | Reorganizing files, directories, or project structure          |
| `refactor`  | Code refactor     | Restructuring code without changing behavior                   |
| `test`      | Tests             | Adding or updating tests                                       |
| `chore`     | Maintenance       | Build, dependencies, tooling, configuration                    |
| `style`     | Code style        | Formatting, whitespace, linting (no functional change)         |
| `perf`      | Performance       | Performance improvements                                       |
| `ci`        | CI/CD             | Continuous integration and deployment                          |
| `build`     | Build system      | Changes to build process or dependencies                       |
| `revert`    | Revert            | Reverting a previous commit                                    |

### Scope (Optional)

The scope provides additional context about what part of the codebase is affected.

**Common scopes for SpreadsheetDL:**

- Domain plugins: `finance`, `biology`, `data-science`, `manufacturing`, `electrical`, `mechanical`, `civil`, `environmental`, `education`
- Core components: `builder`, `cli`, `mcp`, `schema`, `themes`, `formulas`, `charts`
- Documentation areas: `api`, `guides`, `tutorials`, `examples`
- Infrastructure: `deps`, `ci`, `scripts`, `hooks`

### Subject (Required)

- Use imperative, present tense: "add" not "added" nor "adds"
- Lowercase (no capital first letter)
- No period at the end
- Max 50 characters recommended
- Describe WHAT changed, not WHY (use body for why)

### Body (Optional)

- Use imperative, present tense
- Explain motivation for the change
- Contrast with previous behavior
- Wrap at 72 characters
- Separate from subject with blank line

### Footer (Optional)

- Reference issues: `Fixes #123`, `Closes #456`, `Refs #789`
- Breaking changes: `BREAKING CHANGE: description`
- Co-authors: `Co-Authored-By: Name <email>`

### Breaking Changes

For breaking changes, use either:

1. Add `!` after type/scope: `feat(api)!: remove deprecated endpoints`
2. Add `BREAKING CHANGE:` footer with description

## Examples by Type

### feat (New Feature)

```
feat(finance): add multi-currency support

Implement currency conversion with live exchange rates from ECB.
Budgets can now track expenses in multiple currencies with
automatic conversion to base currency.

Fixes #234
```

```
feat(mcp): add batch spreadsheet generation tool

New tool allows generating multiple spreadsheets from a list
of configurations in a single call.
```

```
feat(charts): support sparkline charts

Add sparkline chart type for inline trend visualization.
Supports line, column, and win/loss sparkline variants.
```

### fix (Bug Fix)

```
fix(builder): prevent formula circular reference crash

Add cycle detection to FormulaBuilder to catch circular
references before export. Prevents crashes when exporting
spreadsheets with invalid formula dependencies.

Fixes #456
```

```
fix(cli): handle missing output directory

Create output directory if it doesn't exist rather than
failing with unclear error message.
```

```
fix(finance): correct IRR calculation for negative cashflows

Previous implementation returned incorrect results when
all cashflows were negative. Now properly handles edge cases.
```

### docs (Documentation)

```
docs(api): add chart builder examples

Include 10 new examples demonstrating chart creation,
customization, and integration with themes.
```

```
docs: update installation instructions for uv

Replace pip-based installation with uv commands to match
current development workflow.
```

```
docs(tutorials): add MCP integration guide

Step-by-step tutorial for integrating SpreadsheetDL MCP
server with Claude Desktop.
```

### content (Knowledge Content)

```
content(health): add sleep optimization protocols

Add comprehensive sleep strategies from Matt Walker research
including chronotype analysis and sleep hygiene practices.
```

```
content(productivity): add deep work principles

Summarize Cal Newport's deep work methodology with
practical implementation strategies.
```

### expert (Expert System)

```
expert(finance): enhance budget analysis rules

Add detection rules for irregular spending patterns and
budget category overruns with alert thresholds.
```

```
expert(biology): add qPCR data validation rules

Implement validation logic for CT values, amplification
efficiency, and replicate consistency.
```

### structure (Organization)

```
structure: reorganize domain plugins

Move all domain plugins to src/spreadsheet_dl/domains/
for consistency. Update imports across codebase.
```

```
structure: split monolithic examples file

Break examples/template_engine_usage.py into separate
example files organized by domain.
```

### refactor (Code Refactor)

```
refactor(builder): extract style logic to separate module

Move all style-related methods from SpreadsheetBuilder
to new StyleBuilder class for better separation of concerns.
```

```
refactor(mcp): simplify tool registration

Replace manual tool registration with decorator-based
approach for cleaner code.
```

### test (Tests)

```
test(finance): add IRR edge case coverage

Add tests for IRR with negative cashflows, zero NPV,
and multiple sign changes.
```

```
test: increase formula builder test coverage to 90%

Add property-based tests using hypothesis for formula
validation and circular reference detection.
```

### chore (Maintenance)

```
chore(deps): update openpyxl to 3.1.2

Update for security patch and Python 3.12 compatibility.
```

```
chore: add pre-commit hooks for ruff

Configure pre-commit to run ruff linting and formatting
before commits.
```

```
chore(ci): add pytest coverage reporting

Configure GitHub Actions to upload coverage reports to
codecov.
```

### style (Code Style)

```
style: apply ruff formatting to all Python files

Run ruff format across codebase for consistent style.
No functional changes.
```

```
style(docs): fix markdown linting issues

Correct line length, heading hierarchy, and list formatting
in all markdown files.
```

### perf (Performance)

```
perf(builder): optimize large spreadsheet export

Reduce memory usage by 60% when exporting 100k+ rows
by switching to streaming write mode.
```

```
perf(formulas): cache compiled formula expressions

Cache formula parsing results to avoid re-parsing identical
formulas. Improves export time by 30% for formula-heavy
spreadsheets.
```

## Multi-File Commit Strategies

### Separate by Domain

When changes span multiple domains, create separate commits:

```bash
# Separate commits for different domains
git add src/spreadsheet_dl/domains/finance/*
git commit -m "feat(finance): add investment tracking formulas"

git add src/spreadsheet_dl/domains/biology/*
git commit -m "feat(biology): add plate layout generator"
```

### Content + Structure Changes

Separate structural changes from content additions:

```bash
# First: structural changes
git add -A
git reset -- knowledge/new-topic.md
git commit -m "structure: reorganize health directory"

# Second: new content
git add knowledge/new-topic.md
git commit -m "content(health): add new topic notes"
```

### Refactor + Fix Pattern

When a refactor enables a bug fix, create separate commits:

```bash
# First: refactor
git add src/spreadsheet_dl/formulas/builder.py
git commit -m "refactor(formulas): extract validation logic"

# Second: fix enabled by refactor
git add src/spreadsheet_dl/formulas/validator.py tests/
git commit -m "fix(formulas): handle empty formula expressions"
```

## Breaking Changes

### Using `!` Suffix

```
feat(api)!: remove deprecated template CLI options

Remove -t/--template flag and 'templates' command.
Use template_engine API directly instead.

BREAKING CHANGE: CLI no longer supports -t flag for
template selection. Templates must now be loaded
programmatically via template_engine module.
```

### Footer Only

```
feat(mcp): change tool naming convention

Rename all MCP tools to use underscores instead of hyphens
for consistency with Python naming.

BREAKING CHANGE: All MCP tool names have changed.
Update any client code that calls tools directly:
  - budget-generate → budget_generate
  - expense-add → expense_add
  - chart-create → chart_create
```

## Atomic Commits

### Good: Single Logical Change

```
fix(finance): correct compound interest calculation

Update compounding period handling in investment formulas.
Previous implementation used annual compounding regardless
of specified period.
```

### Bad: Multiple Unrelated Changes

```
# DON'T DO THIS
fix: various fixes and updates

- Fix compound interest calculation
- Update README badges
- Add new biology plugin
- Refactor CLI parser
```

Instead, split into atomic commits:

```
fix(finance): correct compound interest calculation
docs: update README badges to v4.0.0
feat(biology): add qPCR analysis plugin
refactor(cli): extract argument parser to separate module
```

## Commit Message Quality

### Good Examples

Clear, descriptive, and contextual:

```
feat(charts): add support for dual-axis combination charts

Implement dual Y-axis charts allowing line/column combinations
with different scales. Useful for comparing metrics with
different units (e.g., revenue vs growth rate).
```

```
fix(mcp): handle network timeout in bank import

Add retry logic with exponential backoff for bank API calls.
Prevents import failure due to transient network issues.

Fixes #789
```

### Bad Examples

Vague, unclear, or too brief:

```
# TOO VAGUE
fix: bug fix

# NO CONTEXT
feat: add stuff

# UNCLEAR SCOPE
update: changes

# PAST TENSE (should be imperative)
fixed: added the new feature
```

## Subject Line Best Practices

### Good Subject Lines

- `feat(finance): add investment portfolio tracker`
- `fix(builder): prevent invalid cell reference in formulas`
- `docs(api): document theme customization API`
- `refactor(mcp): simplify tool registration pattern`
- `test(formulas): increase circular reference detection coverage`

### Bad Subject Lines

- `feat: stuff` (too vague)
- `Fix bug` (missing scope, not imperative, capitalized)
- `Added new features for financial tracking` (past tense, too long)
- `Update docs.` (has period, not descriptive enough)
- `WIP: working on thing` (not a finished commit)

## Special Cases

### Reverting Commits

```
revert: feat(charts): add sparkline support

This reverts commit a1b2c3d4.

Reason: Sparkline implementation causes PDF export crashes.
Will re-implement with proper PDF renderer support.
```

### Merge Commits

```
Merge branch 'feature/multi-currency' into main

Implements multi-currency support with ECB exchange rates.

Closes #234
```

### Initial Commits

```
chore: initial commit

Setup project structure with:
- Python package layout
- uv dependency management
- pytest configuration
- ruff linting and formatting
- mypy type checking
```

## Quality Checklist

Before committing, verify:

- [ ] Type is appropriate for the change
- [ ] Scope accurately describes affected area
- [ ] Subject is imperative, lowercase, no period
- [ ] Subject clearly describes WHAT changed
- [ ] Body explains WHY (if non-obvious)
- [ ] Breaking changes are clearly marked
- [ ] Issue references are included (if applicable)
- [ ] Commit is atomic (single logical change)
- [ ] Tests pass
- [ ] Linting passes

## References

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Semantic Versioning](https://semver.org/)
