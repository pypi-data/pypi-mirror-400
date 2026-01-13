#!/usr/bin/env bash
# Script to remove requirement identifier references from the repository
# for public release preparation.
#
# Usage: ./scripts/cleanup_requirement_ids.sh [--dry-run] [--help]
#
# Patterns removed:
#   - FR-XXX-NNN (Functional Requirements)
#   - NFR-XXX-NNN (Non-Functional Requirements)
#   - Gap G-NNN (Gap references)
#   - Implements: sections with requirement IDs
#   - Tests FR-XXX references
#   - (FR-XXX) parenthetical references

set -euo pipefail

show_help() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Remove requirement identifier references from the repository for public release.

OPTIONS:
    --dry-run       Preview changes without modifying files
    -h, --help      Show this help message

PATTERNS REMOVED:
    - FR-XXX-NNN (Functional Requirements)
    - NFR-XXX-NNN (Non-Functional Requirements)
    - Gap G-NNN (Gap references)
    - Implements: sections with requirement IDs
    - Tests FR-XXX references
    - (FR-XXX) parenthetical references

EXAMPLES:
    $(basename "$0") --dry-run    # Preview changes
    $(basename "$0")               # Execute cleanup

EOF
  exit 0
}

DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case $1 in
  --dry-run)
    DRY_RUN=true
    echo "=== DRY RUN MODE - No files will be modified ==="
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

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "Repository: ${REPO_ROOT}"
echo ""

# Count occurrences before
echo "=== Counting occurrences before cleanup ==="
BEFORE_COUNT=$(grep -rE 'FR-[A-Z]+-[0-9]+|NFR-[A-Z]+-[0-9]+|Gap G-[0-9]+' --include="*.py" --include="*.md" . 2>/dev/null | wc -l || true)
echo "Found ${BEFORE_COUNT} lines with requirement identifiers"
echo ""

# Function to perform sed replacement
do_sed() {
  local pattern="$1"
  local replacement="$2"
  local description="$3"

  echo "Processing: ${description}"

  if [[ "${DRY_RUN}" == "true" ]]; then
    # Show what would be changed
    grep -rln "${pattern}" --include="*.py" --include="*.md" . 2>/dev/null | head -5 || true
  else
    # Actually perform the replacement
    find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i "s/${pattern}/${replacement}/g" {} + 2>/dev/null || true
  fi
}

echo "=== Removing requirement identifier patterns ==="
echo ""

# Pattern 1: Remove "Implements:" sections with requirement IDs (multi-line)
# This is complex and best handled line by line
echo "Pattern 1: Removing 'Implements:' sections with FR-/NFR- references..."
if [[ "${DRY_RUN}" == "false" ]]; then
  # Remove lines that are just "Implements:" or "Implements FR-..." etc
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*Implements:[[:space:]]*$/d' {} +
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*- FR-[A-Z]*-[0-9]*.*$/d' {} +
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*- NFR-[A-Z]*-[0-9]*.*$/d' {} +
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*FR-[A-Z]*-[0-9]*.*$/d' {} +
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*NFR-[A-Z]*-[0-9]*.*$/d' {} +
  # Remove "Implements: FR-XXX" inline
  find . -type f -name "*.py" -exec sed -i 's/Implements: FR-[A-Z]*-[0-9]*//g' {} +
  find . -type f -name "*.py" -exec sed -i 's/Implements: NFR-[A-Z]*-[0-9]*//g' {} +
fi

# Pattern 2: Remove parenthetical references like (FR-CORE-003)
echo "Pattern 2: Removing parenthetical references (FR-XXX-NNN)..."
if [[ "${DRY_RUN}" == "false" ]]; then
  find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/ *(FR-[A-Z]*-[0-9]*)//g' {} +
  find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/ *(NFR-[A-Z]*-[0-9]*)//g' {} +
fi

# Pattern 3: Remove "Gap G-NN" references
echo "Pattern 3: Removing Gap references..."
if [[ "${DRY_RUN}" == "false" ]]; then
  find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/ *(Gap G-[0-9]*)//g' {} +
  find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/Gap G-[0-9]*//g' {} +
fi

# Pattern 4: Remove "Tests FR-XXX" references
echo "Pattern 4: Removing 'Tests FR-XXX' references..."
if [[ "${DRY_RUN}" == "false" ]]; then
  find . -type f -name "*.py" -exec sed -i 's/Tests FR-[A-Z]*-[0-9]*[,]* *//g' {} +
  find . -type f -name "*.py" -exec sed -i 's/Tests NFR-[A-Z]*-[0-9]*[,]* *//g' {} +
fi

# Pattern 5: Remove standalone FR-XXX-NNN mentions
echo "Pattern 5: Removing standalone FR-XXX-NNN mentions..."
if [[ "${DRY_RUN}" == "false" ]]; then
  find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/FR-[A-Z]*-[0-9]*[,]* *//g' {} +
  find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/NFR-[A-Z]*-[0-9]*[,]* *//g' {} +
fi

# Pattern 6: Clean up empty "Implements:" lines that may remain
echo "Pattern 6: Cleaning up empty Implements lines..."
if [[ "${DRY_RUN}" == "false" ]]; then
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*Implements:[[:space:]]*$/d' {} +
  # Also remove lines with just "Implements:\n    -" patterns
  find . -type f -name "*.py" -exec sed -i '/^[[:space:]]*-[[:space:]]*$/d' {} +
fi

# Pattern 7: Clean up markdown **Implements**: patterns
echo "Pattern 7: Removing markdown Implements patterns..."
if [[ "${DRY_RUN}" == "false" ]]; then
  find . -type f -name "*.md" -exec sed -i 's/\*\*Implements\*\*: *//g' {} +
fi

echo ""
echo "=== Cleanup complete ==="

# Count occurrences after
if [[ "${DRY_RUN}" == "false" ]]; then
  echo ""
  echo "=== Counting occurrences after cleanup ==="
  AFTER_COUNT=$(grep -rE 'FR-[A-Z]+-[0-9]+|NFR-[A-Z]+-[0-9]+|Gap G-[0-9]+' --include="*.py" --include="*.md" . 2>/dev/null | wc -l || true)
  echo "Found ${AFTER_COUNT} lines with requirement identifiers"
  echo ""
  echo "Removed $((BEFORE_COUNT - AFTER_COUNT)) occurrences"
else
  echo ""
  echo "Run without --dry-run to apply changes"
fi
