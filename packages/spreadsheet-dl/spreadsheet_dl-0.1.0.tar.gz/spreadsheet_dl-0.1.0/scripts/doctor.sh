#!/usr/bin/env bash
# =============================================================================
# doctor.sh - Environment Health Check
# =============================================================================
# Usage: ./scripts/doctor.sh [--json]
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/doctor.sh
# =============================================================================

# shellcheck source=lib/common.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --json)
    enable_json
    shift
    ;;
  -h | --help)
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Check development environment setup"
    echo ""
    echo "Options:"
    echo "  --json      Output machine-readable JSON"
    echo "  -h, --help  Show this help message"
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    exit 2
    ;;
  esac
done

print_header "ENVIRONMENT DOCTOR"
echo ""
echo -e "  ${DIM}Repository:${NC} ${REPO_ROOT}"
echo -e "  ${DIM}Timestamp:${NC}  $(date '+%Y-%m-%d %H:%M:%S')"

# Tool categories (used via nameref in check_tools)
# shellcheck disable=SC2034
declare -A CORE_TOOLS=(
  ["git"]="Version control"
  ["bash"]="Shell interpreter"
)

# shellcheck disable=SC2034
declare -A PYTHON_TOOLS=(
  ["python3"]="Python interpreter"
  ["uv"]="Python package manager"
  ["ruff"]="Python linter/formatter"
  ["mypy"]="Python type checker"
  ["check-jsonschema"]="JSON schema validator"
)

# shellcheck disable=SC2034
declare -A JS_TOOLS=(
  ["node"]="Node.js runtime"
  ["npm"]="Node package manager"
  ["npx"]="Node package runner"
  ["prettier"]="Code formatter"
  ["markdownlint"]="Markdown linter"
)

# shellcheck disable=SC2034
declare -A SHELL_TOOLS=(
  ["shellcheck"]="Shell linter"
  ["shfmt"]="Shell formatter"
)

# shellcheck disable=SC2034
declare -A YAML_TOOLS=(
  ["yamllint"]="YAML linter"
)

# shellcheck disable=SC2034
declare -A XML_TOOLS=(
  ["xmllint"]="XML validator"
  ["jq"]="JSON processor"
)

# shellcheck disable=SC2034
declare -A DIAGRAM_TOOLS=(
  ["mmdc"]="Mermaid CLI"
  ["plantuml"]="PlantUML"
)

check_tools() {
  local category="$1"
  shift
  local -n tools=$1

  print_header "${category}"
  for tool in "${!tools[@]}"; do
    local desc="${tools[${tool}]}"
    if has_tool "${tool}"; then
      local version=""
      case "${tool}" in
      python3) version=$(${tool} --version 2>&1 | head -1) ;;
      node) version=$(${tool} --version 2>&1) ;;
      git) version=$(${tool} --version 2>&1 | head -1) ;;
      uv) version=$(${tool} --version 2>&1 | head -1) ;;
      ruff) version=$(${tool} --version 2>&1 | head -1) ;;
      shfmt) version=$(${tool} --version 2>&1 | head -1) ;;
      jq) version=$(${tool} --version 2>&1) ;;
      check-jsonschema) version=$(${tool} --version 2>&1 | head -1) ;;
      *) version="installed" ;;
      esac
      print_pass "${tool} - ${desc} ${DIM}(${version})${NC}"
      json_result "${tool}" "pass" "${version}"
    else
      print_skip "${tool} - ${desc} (not installed)"
      json_result "${tool}" "skip" "Not installed"
    fi
  done
}

# Check each category
check_tools "Core Tools" CORE_TOOLS
check_tools "Python Tools" PYTHON_TOOLS
check_tools "JavaScript Tools" JS_TOOLS
check_tools "Shell Tools" SHELL_TOOLS
check_tools "YAML Tools" YAML_TOOLS
check_tools "XML/JSON Tools" XML_TOOLS
check_tools "Diagram Tools" DIAGRAM_TOOLS

# Check config files
print_header "Configuration Files"

configs=(
  "pyproject.toml:Python project config"
  ".editorconfig:Editor settings"
  ".gitattributes:Git attributes"
  ".shellcheckrc:ShellCheck config"
  ".yamllint.yaml:YAML lint config"
  ".markdownlint.yaml:Markdown lint config"
  ".prettierrc.yaml:Prettier config"
)

for config in "${configs[@]}"; do
  name="${config%%:*}"
  desc="${config#*:}"
  if [[ -f "${REPO_ROOT}/${name}" ]]; then
    print_pass "${name} - ${desc}"
    json_result "${name}" "pass" ""
  else
    print_skip "${name} - ${desc} (not found)"
    json_result "${name}" "skip" "Not found"
  fi
done

# Summary
print_header "RECOMMENDATIONS"
echo ""

# Essential tools
if ! has_tool "shfmt"; then
  echo -e "  ${YELLOW}[CRITICAL]${NC} Install shfmt: ${DIM}go install mvdan.cc/sh/v3/cmd/shfmt@latest${NC}"
fi
if ! has_tool "shellcheck"; then
  echo -e "  ${YELLOW}[CRITICAL]${NC} Install shellcheck: ${DIM}apt install shellcheck${NC}"
fi
if ! has_tool "uv"; then
  echo -e "  ${YELLOW}[CRITICAL]${NC} Install uv: ${DIM}curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
fi
if ! has_tool "ruff"; then
  echo -e "  ${YELLOW}[CRITICAL]${NC} Install ruff: ${DIM}uv tool install ruff${NC}"
fi

# Recommended tools
if ! has_tool "check-jsonschema"; then
  echo -e "  ${YELLOW}▸${NC} Install check-jsonschema: ${DIM}uv pip install check-jsonschema${NC}"
fi
if ! has_tool "markdownlint"; then
  echo -e "  ${YELLOW}▸${NC} Install markdownlint: ${DIM}npm install -g markdownlint-cli${NC}"
fi
if ! has_tool "prettier"; then
  echo -e "  ${YELLOW}▸${NC} Install prettier: ${DIM}npm install -g prettier${NC}"
fi
if ! has_tool "xmllint"; then
  echo -e "  ${YELLOW}▸${NC} Install xmllint: ${DIM}apt install libxml2-utils${NC}"
fi
if ! has_tool "jq"; then
  echo -e "  ${YELLOW}▸${NC} Install jq: ${DIM}apt install jq${NC}"
fi

echo ""
echo -e "  ${DIM}Run ./scripts/setup.sh for automated setup${NC}"
echo -e "  ${DIM}Run ./scripts/setup/install_tools.sh for tool installation${NC}"
