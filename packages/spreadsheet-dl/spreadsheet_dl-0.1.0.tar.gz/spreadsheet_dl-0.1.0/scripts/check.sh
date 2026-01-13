#!/usr/bin/env bash
# =============================================================================
# check.sh - Quick Quality Check (lint + format --check)
# =============================================================================
# Usage: ./scripts/check.sh [--json] [-v]
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/check.sh
# =============================================================================

# shellcheck source=lib/common.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# Defaults
JSON_ARGS=""
VERBOSE_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --json)
        enable_json
        JSON_ARGS="--json"
        shift
        ;;
    -v)
        VERBOSE_ARGS="-v"
        shift
        ;;
    -h | --help)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Quick quality check: lint + format --check"
        echo ""
        echo "Options:"
        echo "  --json      Output machine-readable JSON"
        echo "  -v          Verbose output"
        echo "  -h, --help  Show this help message"
        exit 0
        ;;
    *)
        echo "Unknown option: $1" >&2
        exit 2
        ;;
    esac
done

print_header "QUALITY CHECK"
echo ""
echo -e "  ${DIM}Repository:${NC} ${REPO_ROOT}"
echo -e "  ${DIM}Timestamp:${NC}  $(date '+%Y-%m-%d %H:%M:%S')"

# Run all tool scripts in check mode
failed=0

run_check() {
    local script="$1"
    local args="${2:-}"

    # Check if script exists
    if [[ ! -f "${SCRIPT_DIR}/tools/${script}" ]]; then
        return 0
    fi

    # shellcheck disable=SC2086
    if ! "${SCRIPT_DIR}/tools/${script}" ${args} ${JSON_ARGS} ${VERBOSE_ARGS}; then
        ((failed++)) || true
    fi
}

# Python
print_header "Python"
run_check "ruff.sh" "--check"
run_check "mypy.sh"

# Shell
print_header "Shell"
run_check "shellcheck.sh"

# Markup & Data
print_header "Markup & Data"
run_check "yamllint.sh"
run_check "jsonc.sh" "--check"
run_check "markdownlint.sh" "--check"
run_check "prettier.sh" "--check"
run_check "xmllint.sh" "--check"

# Diagrams
print_header "Diagrams"
run_check "plantuml.sh" "--check"
run_check "mermaid.sh" "--check"

# Summary
print_header "SUMMARY"
echo ""
if [[ ${failed} -eq 0 ]]; then
    echo -e "  ${GREEN}${BOLD}All checks passed!${NC}"
    exit 0
else
    echo -e "  ${RED}${BOLD}${failed} check(s) failed${NC}"
    echo -e "  ${DIM}Run ./scripts/fix.sh to auto-fix issues${NC}"
    exit 1
fi
