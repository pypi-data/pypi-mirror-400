#!/usr/bin/env bash
# =============================================================================
# audit_scripts.sh - Comprehensive Script Interface Audit
# =============================================================================
# Analyzes all scripts for consistency, interface patterns, and best practices
# Usage: scripts/audit_scripts.sh [--help]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Analyze all scripts for consistency, interface patterns, and best practices.

OPTIONS:
    -h, --help      Show this help message

EXAMPLES:
    $(basename "$0")              # Run full audit

FEATURES:
    - Checks for Usage lines in scripts
    - Verifies --help flag presence
    - Validates --json output support
    - Confirms --check/--fix patterns
    - Checks for -v/--verbose support
    - Verifies common.sh sourcing
    - Ensures set -euo pipefail usage

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║  Script Interface Audit"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Find all shell scripts
mapfile -t scripts < <(find "${SCRIPT_DIR}" -type f -name "*.sh" ! -name "audit_scripts.sh" | sort)

echo "Found ${#scripts[@]} shell scripts"
echo ""

# Analysis categories
declare -A has_usage
declare -A has_help
declare -A has_json
declare -A has_check_fix
declare -A has_verbose
declare -A sources_common
declare -A has_set_euo

# Analyze each script
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"

    # Check for usage line
    if grep -q "^# Usage:" "${script}"; then
        has_usage["${name}"]=1
    fi

    # Check for --help
    if grep -q -- "--help" "${script}"; then
        has_help["${name}"]=1
    fi

    # Check for --json
    if grep -q -- "--json" "${script}"; then
        has_json["${name}"]=1
    fi

    # Check for --check/--fix
    if grep -q -E -- "--(check|fix|format)" "${script}"; then
        has_check_fix["${name}"]=1
    fi

    # Check for -v/--verbose
    if grep -q -E -- "(-v|--verbose)" "${script}"; then
        has_verbose["${name}"]=1
    fi

    # Check for sourcing common.sh
    if grep -q "source.*common.sh" "${script}"; then
        sources_common["${name}"]=1
    fi

    # Check for set -euo pipefail
    if grep -q "set -euo pipefail" "${script}"; then
        has_set_euo["${name}"]=1
    fi
done

# Report findings
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "INTERFACE CONSISTENCY ANALYSIS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Helper function to check category
count_category() {
    local -n assoc=$1
    local count=0
    for key in "${!assoc[@]}"; do
        ((count++))
    done
    echo "${count}"
}

# Print statistics
echo "Statistics:"
echo "  Usage line:         $(count_category has_usage)/${#scripts[@]}"
echo "  --help flag:        $(count_category has_help)/${#scripts[@]}"
echo "  --json flag:        $(count_category has_json)/${#scripts[@]}"
echo "  --check/--fix:      $(count_category has_check_fix)/${#scripts[@]}"
echo "  -v/--verbose:       $(count_category has_verbose)/${#scripts[@]}"
echo "  Sources common.sh:  $(count_category sources_common)/${#scripts[@]}"
echo "  set -euo pipefail:  $(count_category has_set_euo)/${#scripts[@]}"
echo ""

# Report missing features by category
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "SCRIPTS MISSING STANDARD FEATURES"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

echo "Missing Usage Line:"
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    if [[ -z "${has_usage[${name}]:-}" ]]; then
        echo "  - ${name}"
    fi
done
echo ""

echo "Missing --help:"
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    if [[ -z "${has_help[${name}]:-}" ]]; then
        echo "  - ${name}"
    fi
done
echo ""

echo "Missing --json (for tool scripts):"
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    # Only report tools/* scripts
    if [[ "${name}" == tools/* ]] && [[ -z "${has_json[${name}]:-}" ]]; then
        echo "  - ${name}"
    fi
done
echo ""

echo "Missing -v/--verbose:"
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    if [[ "${name}" == tools/* ]] && [[ -z "${has_verbose[${name}]:-}" ]]; then
        echo "  - ${name}"
    fi
done
echo ""

echo "Not sourcing common.sh (for tool scripts):"
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    if [[ "${name}" == tools/* ]] && [[ -z "${sources_common[${name}]:-}" ]]; then
        echo "  - ${name}"
    fi
done
echo ""

echo "Missing 'set -euo pipefail':"
for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    if [[ -z "${has_set_euo[${name}]:-}" ]]; then
        echo "  - ${name}"
    fi
done
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "TOOL SCRIPT INTERFACE PATTERNS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

echo "Script                      | Usage | Help | JSON | Check/Fix | Verbose | Common |"
echo "----------------------------|-------|------|------|-----------|---------|--------|"

for script in "${scripts[@]}"; do
    name="${script#"${SCRIPT_DIR}"/}"
    # Only show tools/*
    if [[ "${name}" != tools/* ]]; then
        continue
    fi

    printf "%-27s | " "${name#tools/}"
    printf "%-5s | " "${has_usage[${name}]:+✓}"
    printf "%-4s | " "${has_help[${name}]:+✓}"
    printf "%-4s | " "${has_json[${name}]:+✓}"
    printf "%-9s | " "${has_check_fix[${name}]:+✓}"
    printf "%-7s | " "${has_verbose[${name}]:+✓}"
    printf "%-6s |" "${sources_common[${name}]:+✓}"
    echo ""
done

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "AUDIT COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════════"
