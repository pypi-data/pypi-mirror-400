#!/usr/bin/env bash
# =============================================================================
# validate_tools.sh - Validation dashboard for workspace template configs
# =============================================================================
# Usage: ./scripts/validate_tools.sh [-h|--help]
# =============================================================================
# Run all linters/formatters on test files and report results

set -euo pipefail

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  -h | --help)
    echo "Usage: $0 [-h|--help]"
    echo ""
    echo "Validation dashboard for workspace template configurations"
    echo ""
    echo "Runs all configured linters and formatters on test files to"
    echo "validate that tool configurations are working correctly."
    echo ""
    echo "Options:"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "Test files location: examples/validation-tests/"
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    echo "Try '$0 --help' for usage information" >&2
    exit 2
    ;;
  esac
  shift
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEST_DIR="${REPO_ROOT}/examples/validation-tests"

# Results tracking
PASSED=0
FAILED=0
SKIPPED=0

print_header() {
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_section() {
  echo ""
  echo -e "${YELLOW}▶ $1${NC}"
}

print_config() {
  echo -e "  Config: ${BLUE}$1${NC}"
}

check_tool() {
  local tool=$1
  if command -v "${tool}" &>/dev/null; then
    return 0
  else
    return 1
  fi
}

run_check() {
  local name=$1
  local config=$2
  local cmd=$3

  print_section "${name}"
  print_config "${config}"

  if eval "${cmd}" &>/dev/null; then
    echo -e "  Result: ${GREEN}✓ PASS${NC}"
    ((PASSED++))
    return 0
  else
    echo -e "  Result: ${RED}✗ FAIL${NC}"
    ((FAILED++))
    # Show actual output
    eval "${cmd}" 2>&1 | head -5 | sed 's/^/  /'
    return 1
  fi
}

skip_check() {
  local name=$1
  local reason=$2

  print_section "${name}"
  echo -e "  Result: ${YELLOW}○ SKIPPED${NC} (${reason})"
  ((SKIPPED++))
}

# ==============================================================================
# MAIN
# ==============================================================================

print_header "WORKSPACE TEMPLATE - TOOL VALIDATION DASHBOARD"
echo ""
echo "Repository: ${REPO_ROOT}"
echo "Test Files: ${TEST_DIR}"
echo "Timestamp:  $(date '+%Y-%m-%d %H:%M:%S')"

# ==============================================================================
# PYTHON
# ==============================================================================

print_header "PYTHON (ruff + mypy)"

if check_tool "uv"; then
  run_check "Ruff Linting" "pyproject.toml [tool.ruff.lint]" \
    "cd '${REPO_ROOT}' && uv run ruff check '${TEST_DIR}/test_python.py'"

  run_check "Ruff Formatting" "pyproject.toml [tool.ruff.format]" \
    "cd '${REPO_ROOT}' && uv run ruff format --check '${TEST_DIR}/test_python.py'"

  run_check "Mypy Type Checking" "pyproject.toml [tool.mypy]" \
    "cd '${REPO_ROOT}' && uv run mypy '${TEST_DIR}/test_python.py'"
else
  skip_check "Python Tools" "uv not installed"
fi

# ==============================================================================
# SHELL
# ==============================================================================

print_header "SHELL (shellcheck)"

if check_tool "shellcheck"; then
  run_check "ShellCheck Linting" ".shellcheckrc" \
    "cd '${REPO_ROOT}' && shellcheck '${TEST_DIR}/test_script.sh'"
else
  skip_check "ShellCheck" "shellcheck not installed"
fi

# ==============================================================================
# YAML
# ==============================================================================

print_header "YAML (yamllint)"

if check_tool "yamllint"; then
  run_check "YAML Linting" ".yamllint.yaml" \
    "cd '${REPO_ROOT}' && yamllint '${TEST_DIR}/test_config.yaml'"
else
  skip_check "YAML Linting" "yamllint not installed"
fi

# ==============================================================================
# JSON/JSONC
# ==============================================================================

print_header "JSON/JSONC (jsonc.sh)"

if check_tool "jq" || check_tool "python3"; then
  run_check "JSON Validation" "scripts/tools/jsonc.sh" \
    "cd '${REPO_ROOT}' && '${SCRIPT_DIR}/tools/jsonc.sh' --check '${TEST_DIR}/test_config.json'"

  # Test JSONC support with VS Code settings if they exist
  if [[ -f "${REPO_ROOT}/.vscode/settings.json" ]]; then
    run_check "JSONC Validation (VS Code)" "scripts/tools/jsonc.sh" \
      "cd '${REPO_ROOT}' && '${SCRIPT_DIR}/tools/jsonc.sh' --check '${REPO_ROOT}/.vscode/settings.json'"
  fi
else
  skip_check "JSON Validation" "jq or python3 not installed"
fi

# ==============================================================================
# MARKDOWN
# ==============================================================================

print_header "MARKDOWN (markdownlint)"

if check_tool "markdownlint"; then
  run_check "Markdown Linting" ".markdownlint.yaml" \
    "cd '${REPO_ROOT}' && markdownlint '${TEST_DIR}/test_markdown.md'"
else
  skip_check "Markdown Linting" "markdownlint not installed"
fi

# ==============================================================================
# PRETTIER (JSON, YAML, Markdown)
# ==============================================================================

print_header "PRETTIER (json, yaml)"

if check_tool "npx"; then
  run_check "JSON Formatting" ".prettierrc.yaml" \
    "cd '${REPO_ROOT}' && npx prettier --check '${TEST_DIR}/test_config.json'"

  run_check "YAML Formatting" ".prettierrc.yaml" \
    "cd '${REPO_ROOT}' && npx prettier --check '${TEST_DIR}/test_config.yaml'"
else
  skip_check "Prettier" "npx not installed"
fi

# ==============================================================================
# VS CODE
# ==============================================================================

print_header "VS CODE (vscode_extensions.sh)"

if check_tool "code"; then
  run_check "VS Code Extensions" "scripts/tools/vscode_extensions.sh" \
    "cd '${REPO_ROOT}' && '${SCRIPT_DIR}/tools/vscode_extensions.sh' --check"
else
  skip_check "VS Code Extensions" "VS Code CLI not installed"
fi

# ==============================================================================
# SUMMARY
# ==============================================================================

print_header "VALIDATION SUMMARY"
echo ""
echo -e "  ${GREEN}Passed:${NC}  ${PASSED}"
echo -e "  ${RED}Failed:${NC}  ${FAILED}"
echo -e "  ${YELLOW}Skipped:${NC} ${SKIPPED}"
echo ""

TOTAL=$((PASSED + FAILED))
if [[ ${TOTAL} -gt 0 ]]; then
  PERCENT=$((PASSED * 100 / TOTAL))
  echo -e "  Pass Rate: ${PERCENT}%"
fi

echo ""
if [[ ${FAILED} -eq 0 ]]; then
  echo -e "${GREEN}All validation checks passed!${NC}"
  exit 0
else
  echo -e "${RED}Some validation checks failed.${NC}"
  exit 1
fi
