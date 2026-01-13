#!/usr/bin/env bash
# =============================================================================
# Shell Script Linting Tool Wrapper
# =============================================================================
# Usage: ./scripts/tools/shellcheck.sh [--json] [-v] [paths...]
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/tools/shellcheck.sh
# =============================================================================

# shellcheck source=../lib/common.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

# Configuration
TOOL_NAME="ShellCheck"
TOOL_CMD="shellcheck"
INSTALL_HINT="apt install shellcheck / brew install shellcheck"

# Defaults
VERBOSE=false
PATHS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --json)
        enable_json
        shift
        ;;
    -v)
        VERBOSE=true
        shift
        ;;
    -h | --help)
        echo "Usage: $0 [OPTIONS] [paths...]"
        echo ""
        echo "Shell script linting with ShellCheck"
        echo ""
        echo "Options:"
        echo "  --json      Output machine-readable JSON"
        echo "  -v          Verbose output"
        echo "  -h, --help  Show this help message"
        exit 0
        ;;
    -*)
        echo "Unknown option: $1" >&2
        exit 2
        ;;
    *)
        PATHS+=("$1")
        shift
        ;;
    esac
done

# Default to current directory
[[ ${#PATHS[@]} -eq 0 ]] && PATHS=(".")

# Main
print_tool "${TOOL_NAME}"

# Check tool installed
if ! require_tool "${TOOL_CMD}" "${INSTALL_HINT}"; then
    json_result "${TOOL_CMD}" "skip" "Tool not installed"
    exit 0
fi

# Find shell scripts
shell_files=()
for path in "${PATHS[@]}"; do
    if [[ -f "${path}" ]]; then
        # Single file
        shell_files+=("${path}")
    elif [[ -d "${path}" ]]; then
        # Directory - find .sh files
        while IFS= read -r -d '' file; do
            shell_files+=("${file}")
        done < <(find "${path}" -type f -name "*.sh" -not -path "*/.git/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -print0 2>/dev/null)
    fi
done

if [[ ${#shell_files[@]} -eq 0 ]]; then
    print_skip "No shell scripts found"
    json_result "${TOOL_CMD}" "skip" "No files found"
    exit 0
fi

# Run shellcheck
if ${VERBOSE}; then
    if shellcheck "${shell_files[@]}"; then
        print_pass "All scripts passed"
        json_result "${TOOL_CMD}" "pass" ""
        exit 0
    else
        print_fail "Issues found"
        json_result "${TOOL_CMD}" "fail" "Linting issues"
        exit 1
    fi
else
    if shellcheck "${shell_files[@]}" &>/dev/null; then
        print_pass "All scripts passed"
        json_result "${TOOL_CMD}" "pass" ""
        exit 0
    else
        print_fail "Issues found"
        print_info "Run with -v for details"
        json_result "${TOOL_CMD}" "fail" "Linting issues"
        exit 1
    fi
fi
