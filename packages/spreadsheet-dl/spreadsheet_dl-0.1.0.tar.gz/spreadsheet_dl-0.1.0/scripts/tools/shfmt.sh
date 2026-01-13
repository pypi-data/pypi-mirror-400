#!/usr/bin/env bash
# =============================================================================
# shfmt.sh - Shell Script Formatting with shfmt
# =============================================================================
# Usage: ./scripts/tools/shfmt.sh [--check|--fix] [--json] [-v] [paths...]
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/tools/shfmt.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

# Configuration
TOOL_NAME="shfmt"
TOOL_CMD="shfmt"
INSTALL_HINT="go install mvdan.cc/sh/v3/cmd/shfmt@latest"

# shfmt options matching .editorconfig:
# -i 4   : 4-space indentation (matches [*.{sh,bash}] indent_size = 4)
# -bn    : Binary ops like && and | may start a line
# -ci    : Indent switch cases
# -sr    : Redirect operators will be followed by a space
SHFMT_OPTS="-i 4 -bn -ci -sr"

# Defaults
MODE="check"
VERBOSE=false
PATHS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --check)
        MODE="check"
        shift
        ;;
    --fix)
        MODE="fix"
        shift
        ;;
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
        echo "Shell script formatting with shfmt"
        echo ""
        echo "Options:"
        echo "  --check     Check formatting only (default)"
        echo "  --fix       Fix formatting in place"
        echo "  --json      Output machine-readable JSON"
        echo "  -v          Verbose output"
        echo "  -h, --help  Show this help message"
        echo ""
        echo "Formatting options:"
        echo "  -i 4   4-space indentation (matches .editorconfig)"
        echo "  -bn    Binary ops may start a line"
        echo "  -ci    Indent switch cases"
        echo "  -sr    Space after redirect operators"
        echo ""
        echo "Example:"
        echo "  $0 --check scripts/"
        echo "  $0 --fix scripts/ base/hooks/"
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
print_tool "${TOOL_NAME} (${MODE})"

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
        done < <(find "${path}" -type f -name "*.sh" \
            -not -path "*/.git/*" \
            -not -path "*/.venv/*" \
            -not -path "*/node_modules/*" \
            -print0 2>/dev/null)
    fi
done

if [[ ${#shell_files[@]} -eq 0 ]]; then
    print_skip "No shell scripts found"
    json_result "${TOOL_CMD}" "skip" "No files found"
    exit 0
fi

file_count=${#shell_files[@]}
${VERBOSE} && print_info "Found ${file_count} shell script(s)"

# Run shfmt
case ${MODE} in
check)
    # Use -d (diff) flag to check without modifying
    # shellcheck disable=SC2086
    if ${VERBOSE}; then
        if shfmt ${SHFMT_OPTS} -d "${shell_files[@]}"; then
            print_pass "All ${file_count} scripts formatted correctly"
            json_result "${TOOL_CMD}" "pass" ""
            exit 0
        else
            print_fail "Formatting issues found"
            json_result "${TOOL_CMD}" "fail" "Formatting issues"
            exit 1
        fi
    else
        # shellcheck disable=SC2086
        if shfmt ${SHFMT_OPTS} -d "${shell_files[@]}" &>/dev/null; then
            print_pass "All ${file_count} scripts formatted correctly"
            json_result "${TOOL_CMD}" "pass" ""
            exit 0
        else
            print_fail "Formatting issues found"
            print_info "Run with --fix to format"
            json_result "${TOOL_CMD}" "fail" "Formatting issues"
            exit 1
        fi
    fi
    ;;
fix)
    # Use -w (write) flag to format in place
    # shellcheck disable=SC2086
    if ${VERBOSE}; then
        if shfmt ${SHFMT_OPTS} -w "${shell_files[@]}"; then
            print_pass "Formatted ${file_count} scripts"
            json_result "${TOOL_CMD}" "pass" "Formatted"
            exit 0
        else
            print_fail "Formatting failed"
            json_result "${TOOL_CMD}" "fail" "Format error"
            exit 1
        fi
    else
        # shellcheck disable=SC2086
        if shfmt ${SHFMT_OPTS} -w "${shell_files[@]}" 2>/dev/null; then
            print_pass "Formatted ${file_count} scripts"
            json_result "${TOOL_CMD}" "pass" "Formatted"
            exit 0
        else
            print_fail "Formatting failed"
            json_result "${TOOL_CMD}" "fail" "Format error"
            exit 1
        fi
    fi
    ;;
esac
