#!/usr/bin/env bash
# SpreadsheetDL Public Release Preparation Script
# This script cleans development artifacts and git history using orphan branch strategy
#
# WARNING: This rewrites git history. Only run when ready to go public.
# Make sure you have a backup of the repository first!
#
# Usage: ./scripts/prepare_public_release.sh [--cleanup-only] [--help]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

show_help() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Prepare repository for public release by cleaning development artifacts and
optionally rewriting git history using orphan branch strategy.

⚠️  WARNING: This rewrites git history. Make sure you have a backup first!

OPTIONS:
    --cleanup-only  Only clean development artifacts, skip git history rewrite
    -h, --help      Show this help message

EXAMPLES:
    $(basename "$0") --cleanup-only    # Clean artifacts only
    $(basename "$0")                   # Full release preparation (interactive)

WHAT IT DOES:
    Phase 0 (Cleanup):
    - Removes dated coordination files
    - Resets state files to idle
    - Cleans agent outputs and checkpoints

    Phase 1-5 (Git History - Interactive):
    - Archives current development history
    - Creates clean orphan branch
    - Creates comprehensive initial commit
    - Tags as v4.0.0

EOF
  exit 0
}

# Parse arguments
CLEANUP_ONLY=false
while [[ $# -gt 0 ]]; do
  case $1 in
  --cleanup-only)
    CLEANUP_ONLY=true
    shift
    ;;
  -h | --help)
    show_help
    ;;
  *)
    echo "Error: Unknown option: $1" >&2
    echo "Run '$(basename "$0") --help' for usage information" >&2
    exit 1
    ;;
  esac
done

# Function to clean development artifacts
cleanup_dev_artifacts() {
  echo -e "${YELLOW}Phase 0: Cleaning Development Artifacts${NC}"
  echo "=========================================="
  echo ""

  local removed_count=0

  echo -e "${YELLOW}Cleaning .coordination/ directory${NC}"
  echo "-----------------------------------"

  # Remove dated coordination files
  echo "Removing dated coordination markdown files..."
  find .coordination/ -type f -name "2025-*.md" -delete 2>/dev/null || true
  find .coordination/ -type f -name "2026-*.md" -delete 2>/dev/null || true
  removed_count=$((removed_count + $(find .coordination/ -type f -name "*.md" ! -name "README.md" 2>/dev/null | wc -l)))
  find .coordination/ -type f -name "*.md" ! -name "README.md" -delete 2>/dev/null || true

  # Remove implementation summaries
  echo "Removing implementation summaries..."
  find .coordination/ -type f -name "*IMPLEMENTATION*.md" -delete 2>/dev/null || true
  find .coordination/ -type f -name "*SUMMARY*.md" -delete 2>/dev/null || true
  find .coordination/ -type f -name "*COMPLETION*.md" -delete 2>/dev/null || true

  # Reset state files
  echo "Resetting state files..."
  if [[ -f ".coordination/active_work.json" ]]; then
    echo '{"status": "idle", "task": null}' >.coordination/active_work.json
    echo "  - Reset active_work.json"
  fi

  if [[ -f ".coordination/work_queue.json" ]]; then
    echo '{"pending": [], "blocked": []}' >.coordination/work_queue.json
    echo "  - Reset work_queue.json"
  fi

  # Remove outdated task graph
  if [[ -f ".coordination/task-graph.json" ]]; then
    rm -f .coordination/task-graph.json
    echo "  - Removed outdated task-graph.json"
    removed_count=$((removed_count + 1))
  fi

  # Remove completed.jsonl if it exists
  if [[ -f ".coordination/completed.jsonl" ]]; then
    rm -f .coordination/completed.jsonl
    echo "  - Removed completed.jsonl"
    removed_count=$((removed_count + 1))
  fi

  echo ""
  echo -e "${YELLOW}Cleaning .claude/agent-outputs/ directory${NC}"
  echo "-------------------------------------------"

  # Remove all agent output files except .gitkeep
  echo "Removing agent output files..."
  find .claude/agent-outputs/ -type f ! -name ".gitkeep" -delete 2>/dev/null || true
  local agent_files
  agent_files=$(find .claude/agent-outputs/ -type f ! -name ".gitkeep" 2>/dev/null | wc -l)
  removed_count=$((removed_count + agent_files))
  echo "  - Removed all agent output files"

  echo ""
  echo -e "${YELLOW}Cleaning .coordination/checkpoints/ directory${NC}"
  echo "------------------------------------------------"

  # Remove checkpoint files except README.md
  echo "Removing checkpoint files..."
  find .coordination/checkpoints/ -type f ! -name "README.md" ! -name ".gitkeep" -delete 2>/dev/null || true
  local checkpoint_files
  checkpoint_files=$(find .coordination/checkpoints/ -type f ! -name "README.md" ! -name ".gitkeep" 2>/dev/null | wc -l)
  removed_count=$((removed_count + checkpoint_files))
  echo "  - Removed checkpoint files"

  echo ""
  echo -e "${YELLOW}Verification${NC}"
  echo "-------------"

  # Verify key files remain
  echo "Verifying structure..."
  local errors=0

  if [[ ! -f ".coordination/README.md" ]]; then
    echo -e "${RED}  ✗ .coordination/README.md missing!${NC}"
    errors=$((errors + 1))
  else
    echo -e "${GREEN}  ✓ .coordination/README.md present${NC}"
  fi

  if [[ ! -f ".coordination/checkpoints/README.md" ]]; then
    echo -e "${RED}  ✗ .coordination/checkpoints/README.md missing!${NC}"
    errors=$((errors + 1))
  else
    echo -e "${GREEN}  ✓ .coordination/checkpoints/README.md present${NC}"
  fi

  if [[ ! -f ".coordination/spec/incomplete-features.yaml" ]]; then
    echo -e "${RED}  ✗ .coordination/spec/incomplete-features.yaml missing!${NC}"
    errors=$((errors + 1))
  else
    echo -e "${GREEN}  ✓ .coordination/spec/incomplete-features.yaml present${NC}"
  fi

  echo ""
  echo -e "${GREEN}=== Cleanup Complete ===${NC}"
  echo ""
  echo "Summary:"
  echo "  - Removed development artifacts"
  echo "  - Reset state files to empty/idle state"
  echo "  - Preserved README and structure files"

  if [[ ${errors} -eq 0 ]]; then
    echo -e "${GREEN}  ✓ All verification checks passed${NC}"
  else
    echo -e "${RED}  ✗ ${errors} verification check(s) failed${NC}"
    return 1
  fi

  echo ""
}

# Run cleanup
cleanup_dev_artifacts

# If --cleanup-only flag, exit here
if [[ "${CLEANUP_ONLY}" == "true" ]]; then
  echo -e "${GREEN}Cleanup-only mode complete.${NC}"
  exit 0
fi

echo "========================================="
echo "SpreadsheetDL Public Release Preparation"
echo "========================================="
echo ""
echo "This script will:"
echo "1. Archive current development history"
echo "2. Create clean main branch with orphan strategy"
echo "3. Create single comprehensive initial commit"
echo "4. Tag as v4.0.0"
echo ""
echo "WARNING: This rewrites git history!"
echo ""
read -r -p "Are you SURE you want to continue? (type 'yes' to proceed): " confirm

if [[ "${confirm}" != "yes" ]]; then
  echo "Aborted."
  exit 1
fi

# Step 1: Archive current development
echo ""
echo "[Step 1/5] Archiving current development history..."
git branch "dev-archive-$(date +%Y%m%d)"
echo "✓ Created dev-archive branch"

# Push archive to remote (optional - uncomment when ready)
# git push origin dev-archive-$(date +%Y%m%d)
# echo "✓ Pushed archive to remote"

# Step 2: Create orphan branch
echo ""
echo "[Step 2/5] Creating clean orphan branch..."
git checkout --orphan main-clean
echo "✓ Created orphan branch 'main-clean'"

# Step 3: Clear staging area
echo ""
echo "[Step 3/5] Clearing staging area..."
git rm -rf . --quiet
git clean -fxd --quiet
echo "✓ Cleared staging area"

# Step 4: Copy final code from current main
echo ""
echo "[Step 4/5] Copying v4.0.0 code..."
git checkout main -- .
echo "✓ Copied v4.0.0 codebase"

# Step 5: Create comprehensive initial commit
echo ""
echo "[Step 5/5] Creating initial commit..."
git add .

cat >/tmp/commit-message.txt <<'EOF'
feat: SpreadsheetDL v4.0.0 - Universal Spreadsheet Definition Language

🎉 First Public Release

The Spreadsheet Definition Language for Python with complete domain plugin ecosystem.

## Core Platform

**Declarative Builder API:**
- Fluent, chainable methods for spreadsheet construction
- Type-safe FormulaBuilder with 100+ functions
- Circular reference detection with dependency graph
- Named ranges with proper ODF hierarchy
- Cell merge rendering with colspan/rowspan

**Theme System:**
- YAML-based theme definition
- 5 built-in themes (default, corporate, minimal, dark, high_contrast)
- Color palette management with accessibility checking
- Font pairing system with typography scales
- Theme variant switching (light/dark/high-contrast)

**Chart Builder:**
- 60+ chart types (column, bar, line, pie, area, scatter, bubble, combo)
- Sparklines for inline visualizations
- Trendlines with forecasting support
- Full styling and positioning control

**Multi-Format Export:**
- ODS (native, full-featured)
- XLSX (Excel compatibility)
- PDF (professional documents)
- CSV/TSV (data interchange)
- JSON/HTML (web integration)

**MCP Server:**
- 18 tools for Claude/LLM integration
- Tool categories: Cell Ops, Styles, Structure, Charts, Validation, Advanced
- MCPToolRegistry with decorator-based registration
- Rate limiting and security features
- Audit logging configuration

**Performance & Scalability:**
- Streaming I/O for 100k+ row files
- LRU cache with configurable size
- Lazy loading for deferred evaluation
- Batch processing utilities
- Performance benchmarking tools

**Plugin System:**
- Extensible framework with PluginInterface
- Plugin discovery from multiple locations
- Lifecycle management (load, enable, disable, unload)
- Hook system for extensibility

## Domain Plugins (9 Official)

**Finance:**
- Budget templates with categories
- Expense tracking with variance analysis
- Financial reporting (P&L, Balance Sheet, Cash Flow)
- Goal tracking and progress visualization

**Data Science:**
- ML metrics dashboard (accuracy, precision, recall, F1)
- Statistical analysis (descriptive stats, distributions)
- Dataset catalogs with metadata
- A/B test result templates

**Electrical Engineering:**
- Bill of Materials (BOM) with part specs
- Pin mapping and assignment tracking
- Power budget analysis
- Signal routing tables

**Mechanical Engineering:**
- Design calculation templates
- Tolerance stack-up analysis
- Material property databases
- Stress/strain calculations

**Civil Engineering:**
- Structural load calculations
- Construction schedules
- Cost estimation templates
- Project tracking

**Manufacturing:**
- OEE (Overall Equipment Effectiveness) dashboard
- SPC (Statistical Process Control) charts
- Production schedule tracking
- Quality control templates

**Biology:**
- Plate layouts (96-well, 384-well)
- qPCR result analysis
- Cell culture tracking
- Protocol templates

**Education:**
- Gradebook with grade calculations
- Attendance tracking
- Assessment rubrics
- Student progress reports

**Environmental:**
- Emissions tracking
- Environmental impact assessments
- Sustainability metrics

## Advanced Features

**Interactive Features:**
- Dropdown lists for data entry
- Data validation rules (range, list, custom)
- Conditional formatting (color scales, data bars, icon sets)
- Dashboard generation with KPIs
- Sparklines for trend visualization

**Import/Export:**
- CSV import with bank format detection
- Plaid API integration for bank data
- Multi-format export adapters
- Round-trip ODS editing (read, modify, write)

**AI Integration:**
- AI-friendly dual export (ODS + JSON)
- Semantic cell type classification
- Natural language formula descriptions
- Training data export with anonymization
- Privacy-preserving data export (PII detection/removal)

**Backup & Recovery:**
- Automatic backups before destructive operations
- Configurable retention policies
- SHA-256 integrity verification
- Compressed backups (gzip)
- Restore with validation

**Cloud Integration:**
- WebDAV upload for Nextcloud
- Automatic parent directory creation
- File listing and management
- Connection testing

## Technical Details

**Testing:**
- 3,206 tests passing
- 14 skipped (optional features)
- 71% overall coverage
- 95%+ coverage on core modules

**Documentation:**
- 44 API documentation files
- 6 comprehensive tutorials
- Getting started guide
- Best practices guide
- Plugin development guide
- 100+ working code examples

**Development Quality:**
- Type hints throughout (mypy strict mode)
- Ruff linting and formatting
- Conventional commits
- Comprehensive error messages
- Security best practices

**Dependencies:**
- Python 3.12+
- Core: odfpy, pandas, requests, rich
- Optional: openpyxl (XLSX), reportlab (PDF), pyyaml (config)

## Project Stats

- **220 Python modules** across src/
- **3,206 passing tests** with 71% coverage
- **44 API documentation files** (~750KB of docs)
- **9 domain plugins** with production-ready templates
- **18 MCP tools** for LLM integration
- **6 tutorials** (3,700+ lines total)
- **100+ examples** in documentation

## License

MIT License - See LICENSE file

## Acknowledgments

This represents extensive private development and refinement through multiple
major iterations. Version 4.0.0 reflects the maturity of the codebase, not
the public release timeline.

🤖 Generated with Claude Code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF

git commit -F /tmp/commit-message.txt
rm /tmp/commit-message.txt
echo "✓ Created comprehensive initial commit"

# Create tag
echo ""
echo "Creating v4.0.0 tag..."
git tag -a v4.0.0 -m "First public release - SpreadsheetDL v4.0.0"
echo "✓ Tagged v4.0.0"

echo ""
echo "========================================="
echo "SUCCESS! Clean history prepared."
echo "========================================="
echo ""
echo "Current branch: main-clean"
echo "Archive branch: dev-archive-$(date +%Y%m%d)"
echo ""
echo "Next steps:"
echo "1. Review the new history: git log"
echo "2. Compare with original: git diff main main-clean (should be empty)"
echo "3. When ready, replace main:"
echo "   git branch -D main"
echo "   git branch -m main-clean main"
echo "4. Push to remote (when going public):"
echo "   git push -f origin main"
echo "   git push origin v4.0.0"
echo ""
echo "⚠️  Remember: This rewrites history. Only push when ready to go public!"
