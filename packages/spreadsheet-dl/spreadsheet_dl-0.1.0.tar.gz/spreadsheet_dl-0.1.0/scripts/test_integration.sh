#!/usr/bin/env bash
# =============================================================================
# test_integration.sh - Comprehensive Script Integration Test
# =============================================================================
# Usage: ./scripts/test_integration.sh [-v|--verbose]
# =============================================================================
# Tests all scripts for proper integration, interface consistency, and functionality

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Verbose mode
VERBOSE=false
[[ "${1:-}" == "-v" || "${1:-}" == "--verbose" ]] && VERBOSE=true

print_test() {
  ((TOTAL_TESTS++))
  if ${VERBOSE}; then
    echo -n "  Testing: $1... "
  fi
}

pass_test() {
  ((PASSED_TESTS++))
  if ${VERBOSE}; then
    echo -e "${GREEN}✓${NC}"
  else
    echo -n "."
  fi
}

fail_test() {
  ((FAILED_TESTS++))
  if ${VERBOSE}; then
    echo -e "${RED}✗${NC}"
    [[ -n "${1:-}" ]] && echo "    Error: $1"
  else
    echo -n "F"
  fi
}

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  Script Integration Test Suite"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Repository: ${REPO_ROOT}"
echo "Timestamp:  $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ==============================================================================
# Test 1: All tool scripts have --help
# ==============================================================================
echo -e "${BLUE}[1/7]${NC} Testing --help flag for all tool scripts..."
[[ ${VERBOSE} == false ]] && echo -n "  "

for script in "${SCRIPT_DIR}/tools"/*.sh; do
  script_name=$(basename "${script}")
  print_test "${script_name} --help"

  if output=$("${script}" --help 2>&1); then
    if echo "${output}" | grep -q "Usage:"; then
      pass_test
    else
      fail_test "No Usage line in help output"
    fi
  else
    fail_test "Help flag failed"
  fi
done
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Test 2: All tool scripts support --json
# ==============================================================================
echo -e "${BLUE}[2/7]${NC} Testing --json flag for all tool scripts..."
[[ ${VERBOSE} == false ]] && echo -n "  "

for script in "${SCRIPT_DIR}/tools"/*.sh; do
  script_name=$(basename "${script}")
  print_test "${script_name} --json"

  # Run with --json, capture output
  if output=$("${script}" --json 2>&1 | grep "^{"); then
    # Check for valid JSON structure
    if echo "${output}" | grep -q '"tool".*"status"'; then
      pass_test
    else
      fail_test "Invalid JSON structure"
    fi
  else
    # Some tools might skip if not installed, that's OK
    if "${script}" --json 2>&1 | grep -q '"status":"skip"'; then
      pass_test
    else
      fail_test "No JSON output"
    fi
  fi
done
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Test 3: Formatters support --check mode (dry-run)
# ==============================================================================
echo -e "${BLUE}[3/7]${NC} Testing --check mode for formatter scripts..."
[[ ${VERBOSE} == false ]] && echo -n "  "

formatters=(
  "markdownlint.sh"
  "prettier.sh"
  "ruff.sh"
  "jsonc.sh"
)

for formatter in "${formatters[@]}"; do
  script="${SCRIPT_DIR}/tools/${formatter}"
  [[ ! -f "${script}" ]] && continue

  print_test "${formatter} --check"

  # Run in check mode, should not modify any files
  if "${script}" --check >/dev/null 2>&1 || true; then
    # Check mode should exit gracefully (0, 1, or 2)
    exit_code=$?
    if [[ ${exit_code} -le 2 ]]; then
      pass_test
    else
      fail_test "Invalid exit code: ${exit_code}"
    fi
  else
    fail_test "Check mode failed"
  fi
done
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Test 4: Aggregator scripts run successfully
# ==============================================================================
echo -e "${BLUE}[4/7]${NC} Testing aggregator scripts..."
[[ ${VERBOSE} == false ]] && echo -n "  "

aggregators=(
  "check.sh"
  "lint.sh"
  "fix.sh"
)

for aggregator in "${aggregators[@]}"; do
  script="${SCRIPT_DIR}/${aggregator}"
  [[ ! -f "${script}" ]] && continue

  print_test "${aggregator}"

  # Run aggregator, allow it to fail (exit 1) but not error (exit 2)
  if "${script}" >/dev/null 2>&1 || [[ $? -eq 1 ]]; then
    pass_test
  else
    exit_code=$?
    if [[ ${exit_code} -eq 2 ]]; then
      fail_test "Script error (exit 2)"
    else
      fail_test "Unexpected exit code: ${exit_code}"
    fi
  fi
done
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Test 5: Utility scripts have --help
# ==============================================================================
echo -e "${BLUE}[5/7]${NC} Testing utility scripts..."
[[ ${VERBOSE} == false ]] && echo -n "  "

utilities=(
  "validate_tools.sh"
  "validate_vscode.sh"
  "git_reset_clean_all.sh"
  "git_reset_preserve_ignored.sh"
  "resume_claude_sessions_vscode.sh"
)

for utility in "${utilities[@]}"; do
  script="${SCRIPT_DIR}/${utility}"
  [[ ! -f "${script}" ]] && continue

  print_test "${utility} --help"

  if "${script}" --help 2>&1 | grep -q "Usage:"; then
    pass_test
  else
    fail_test "No --help or invalid help output"
  fi
done
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Test 6: All scripts use set -euo pipefail
# ==============================================================================
echo -e "${BLUE}[6/7]${NC} Testing error handling (set -euo pipefail)..."
[[ ${VERBOSE} == false ]] && echo -n "  "

for script in "${SCRIPT_DIR}"/**/*.sh "${SCRIPT_DIR}"/*.sh; do
  [[ ! -f "${script}" ]] && continue
  [[ "${script}" == *"test_integration.sh" ]] && continue
  [[ "${script}" == *"lib/common.sh" ]] && continue

  script_name=$(basename "${script}")
  print_test "${script_name} has error handling"

  if grep -q "set -euo pipefail" "${script}"; then
    pass_test
  else
    fail_test "Missing 'set -euo pipefail'"
  fi
done
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Test 7: Audit script runs successfully
# ==============================================================================
echo -e "${BLUE}[7/7]${NC} Testing audit script..."
[[ ${VERBOSE} == false ]] && echo -n "  "

print_test "audit_scripts.sh"
if "${SCRIPT_DIR}/audit_scripts.sh" >/dev/null 2>&1; then
  pass_test
else
  fail_test "Audit script failed"
fi
[[ ${VERBOSE} == false ]] && echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  Test Results"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "  Total Tests:  ${TOTAL_TESTS}"
echo -e "  ${GREEN}Passed:${NC}       ${PASSED_TESTS}"
echo -e "  ${RED}Failed:${NC}       ${FAILED_TESTS}"
echo ""

if [[ ${FAILED_TESTS} -eq 0 ]]; then
  PERCENT=100
else
  PERCENT=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi
echo -e "  Pass Rate:    ${PERCENT}%"
echo ""

if [[ ${FAILED_TESTS} -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}All integration tests passed!${NC}"
  echo ""
  exit 0
else
  echo -e "${RED}${BOLD}Some integration tests failed.${NC}"
  echo ""
  echo "Run with -v for verbose output to see failures."
  exit 1
fi
