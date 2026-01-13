#!/usr/bin/env bash
# =============================================================================
# fix.sh - Quick Fix (format + lint --fix)
# =============================================================================
# Usage: ./scripts/fix.sh [--json] [-v]
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/fix.sh
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
    echo "Quick fix: format + lint --fix"
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

print_header "AUTO-FIX"
echo ""
echo -e "  ${DIM}Repository:${NC} ${REPO_ROOT}"
echo -e "  ${DIM}Timestamp:${NC}  $(date '+%Y-%m-%d %H:%M:%S')"

fixed=0
failed=0

run_fix() {
  local script="$1"
  local args="${2:---fix}"

  # Check if script exists
  if [[ ! -f "${SCRIPT_DIR}/tools/${script}" ]]; then
    return 0
  fi

  # shellcheck disable=SC2086
  if "${SCRIPT_DIR}/tools/${script}" ${args} ${JSON_ARGS} ${VERBOSE_ARGS}; then
    ((fixed++)) || true
  else
    ((failed++)) || true
  fi
}

# Python - format first, then fix lint issues
print_header "Python"
run_fix "ruff.sh" "--format"
run_fix "ruff.sh" "--fix"

# Shell - format with shfmt
print_header "Shell"
if has_tool shfmt; then
  echo -e "  ${CYAN}▸${NC} ${BOLD}shfmt (format)${NC}"
  # Find all shell script directories
  shell_dirs=()
  [[ -d "${REPO_ROOT}/scripts" ]] && shell_dirs+=("${REPO_ROOT}/scripts")
  [[ -d "${REPO_ROOT}/base/hooks" ]] && shell_dirs+=("${REPO_ROOT}/base/hooks")
  [[ -d "${REPO_ROOT}/.claude/hooks" ]] && shell_dirs+=("${REPO_ROOT}/.claude/hooks")

  if [[ ${#shell_dirs[@]} -gt 0 ]]; then
    shell_files=()
    for dir in "${shell_dirs[@]}"; do
      while IFS= read -r -d '' file; do
        shell_files+=("${file}")
      done < <(find "${dir}" -type f -name "*.sh" -not -path "*/.git/*" -not -path "*/.venv/*" -print0 2>/dev/null)
    done

    if [[ ${#shell_files[@]} -gt 0 ]]; then
      if shfmt -i 4 -w "${shell_files[@]}" 2>/dev/null; then
        print_pass "Shell scripts formatted"
        ((fixed++)) || true
      else
        print_fail "shfmt formatting failed"
        ((failed++)) || true
      fi
    else
      print_skip "No shell scripts found"
    fi
  else
    print_skip "No shell script directories found"
  fi
else
  print_skip "shfmt not installed (go install mvdan.cc/sh/v3/cmd/shfmt@latest)"
fi

# Markup/Data - formatting (YAML, JSON, Markdown)
print_header "Markup & Data"
run_fix "markdownlint.sh" "--fix"
run_fix "prettier.sh" "--fix"

# Summary
print_header "SUMMARY"
echo ""
echo -e "  ${GREEN}Fixed:${NC}  ${fixed} tool(s)"
echo -e "  ${RED}Failed:${NC} ${failed} tool(s)"
echo ""

if [[ ${failed} -eq 0 ]]; then
  echo -e "  ${GREEN}${BOLD}All auto-fixes applied!${NC}"
  echo -e "  ${DIM}Run ./scripts/check.sh to verify${NC}"
  exit 0
else
  echo -e "  ${YELLOW}${BOLD}Some fixes could not be applied${NC}"
  echo -e "  ${DIM}Review issues manually${NC}"
  exit 1
fi
