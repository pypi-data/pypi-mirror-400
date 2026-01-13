#!/usr/bin/env bash
# Generate dynamic test statistics
# Usage: scripts/test_stats.sh [--json] [--help]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Generate comprehensive test statistics using pytest markers.

OPTIONS:
    --json          Output results in JSON format
    -h, --help      Show this help message

EXAMPLES:
    $(basename "$0")              # Human-readable output
    $(basename "$0") --json       # JSON output for automation

EOF
    exit 0
}

# Check for flags
JSON_OUTPUT=false
while [[ $# -gt 0 ]]; do
    case $1 in
    --json)
        JSON_OUTPUT=true
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

# Helper function to extract test count from pytest output
get_test_count() {
    local marker="$1"
    local output

    if [[ -z "${marker}" ]]; then
        # Total tests (no marker filter)
        output=$(uv run pytest --collect-only -q 2>/dev/null | tail -1)
    else
        # Specific marker filter
        output=$(uv run pytest --collect-only -m "${marker}" -q 2>/dev/null | tail -1)
    fi

    # Extract first number from output like "3206 tests collected" or "2873/3279 tests"
    echo "${output}" | grep -oE '[0-9]+' | head -1 || echo "0"
}

# Collect statistics
total=$(get_test_count "")
unit=$(get_test_count "unit")
integration=$(get_test_count "integration")
finance=$(get_test_count "finance")
science=$(get_test_count "science")
engineering=$(get_test_count "engineering")
manufacturing=$(get_test_count "manufacturing")
domain=$(get_test_count "domain")
mcp=$(get_test_count "mcp")
cli=$(get_test_count "cli")
builder=$(get_test_count "builder")
validation=$(get_test_count "validation")
rendering=$(get_test_count "rendering")
templates=$(get_test_count "templates")
visualization=$(get_test_count "visualization")
slow=$(get_test_count "slow")
benchmark=$(get_test_count "benchmark")

# Calculate percentages
if [[ ${total} -gt 0 ]]; then
    unit_pct=$(awk "BEGIN {printf \"%.1f\", (${unit} / ${total}) * 100}")
    integration_pct=$(awk "BEGIN {printf \"%.1f\", (${integration} / ${total}) * 100}")
else
    unit_pct="0.0"
    integration_pct="0.0"
fi

# Output in requested format
if [[ "${JSON_OUTPUT}" == true ]]; then
    # JSON output for machine consumption
    cat <<EOF
{
  "total": ${total},
  "by_level": {
    "unit": ${unit},
    "integration": ${integration}
  },
  "by_domain": {
    "finance": ${finance},
    "science": ${science},
    "engineering": ${engineering},
    "manufacturing": ${manufacturing},
    "domain": ${domain}
  },
  "by_feature": {
    "mcp": ${mcp},
    "cli": ${cli},
    "builder": ${builder},
    "validation": ${validation},
    "rendering": ${rendering},
    "templates": ${templates},
    "visualization": ${visualization}
  },
  "by_performance": {
    "slow": ${slow},
    "benchmark": ${benchmark}
  },
  "percentages": {
    "unit": ${unit_pct},
    "integration": ${integration_pct}
  }
}
EOF
else
    # Human-readable output
    cat <<EOF
=== SpreadsheetDL Test Statistics ===

Test Levels:
  Total:        ${total} tests
  Unit:         ${unit} tests (${unit_pct}%)
  Integration:  ${integration} tests (${integration_pct}%)

Domains:
  Finance:      ${finance} tests
  Science:      ${science} tests
  Engineering:  ${engineering} tests
  Manufacturing: ${manufacturing} tests
  Domain:       ${domain} tests

Features:
  MCP:          ${mcp} tests
  CLI:          ${cli} tests
  Builder:      ${builder} tests
  Validation:   ${validation} tests
  Rendering:    ${rendering} tests
  Templates:    ${templates} tests
  Visualization: ${visualization} tests

Performance:
  Slow:         ${slow} tests
  Benchmark:    ${benchmark} tests

Generated: $(date '+%Y-%m-%d %H:%M:%S')
EOF
fi
