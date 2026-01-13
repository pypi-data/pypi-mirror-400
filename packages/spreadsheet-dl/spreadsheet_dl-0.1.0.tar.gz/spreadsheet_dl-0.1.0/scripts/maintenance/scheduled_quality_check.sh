#!/usr/bin/env bash
# =============================================================================
# Scheduled Quality Check - Automated Documentation QA
# =============================================================================
# Comprehensive quality check for documentation repositories.
# Designed for cron jobs or CI pipelines.
#
# Usage: ./scripts/maintenance/scheduled_quality_check.sh [OPTIONS]
#
# Examples:
#   ./scripts/maintenance/scheduled_quality_check.sh              # Full check
#   ./scripts/maintenance/scheduled_quality_check.sh --links      # Links only
#   ./scripts/maintenance/scheduled_quality_check.sh --cron       # Silent for cron
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/maintenance/scheduled_quality_check.sh
# =============================================================================

# shellcheck source=../lib/common.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

# Configuration
REPORT_DIR="${REPO_ROOT}/.coordination/reports"
TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')

# Options
CHECK_LINKS=false
CHECK_LINT=false
CHECK_FULL=true
CRON_MODE=false
VERBOSE=false
REPORT_FILE=""
FAIL_ON_ISSUES=true

# Results
TOTAL_ISSUES=0
LINK_ISSUES=0
LINT_ISSUES=0
FORMAT_ISSUES=0

# =============================================================================
# Help
# =============================================================================

show_script_help() {
    cat <<'EOF'
scheduled_quality_check.sh - Automated documentation quality checking

USAGE:
    scheduled_quality_check.sh [OPTIONS]

DESCRIPTION:
    Runs comprehensive quality checks on documentation repositories.
    Checks links, runs linters, verifies formatting. Designed for
    scheduled execution (cron) or CI pipelines.

OPTIONS:
    --links         Check links only
    --lint          Run linters only
    --format        Check formatting only
    --full          Full check (default): links + lint + format
    --cron          Silent mode for cron jobs (only output on failure)
    --report FILE   Write detailed report to file
    --no-fail       Exit 0 even if issues found (for monitoring)
    -v, --verbose   Show detailed output
    --json          Output machine-readable JSON
    -h, --help      Show this help message

CHECK TYPES:

    Links:
        - Validates internal markdown links
        - Checks for broken file references
        - Verifies anchor links to headers
        - Uses lychee if available, fallback to grep-based check

    Lint:
        - Markdown linting (markdownlint)
        - YAML validation (yamllint)
        - Shell script checking (shellcheck)
        - Python linting (ruff) if applicable

    Format:
        - Prettier formatting check
        - Line ending consistency
        - Trailing whitespace

REPORTS:
    Reports are saved to: .coordination/reports/
    Format: quality_report_YYYY-MM-DD_HHMMSS.md

CRON EXAMPLE:
    # Weekly quality check (Sundays at 2am)
    0 2 * * 0 cd /path/to/repo && ./scripts/maintenance/scheduled_quality_check.sh --cron

    # Monthly full check with report
    0 3 1 * * cd /path/to/repo && ./scripts/maintenance/scheduled_quality_check.sh --report /var/log/quality.md

CI EXAMPLE:
    # GitHub Actions
    - name: Quality Check
      run: ./scripts/maintenance/scheduled_quality_check.sh --json

EXAMPLES:
    # Full quality check
    scheduled_quality_check.sh

    # Links only, verbose
    scheduled_quality_check.sh --links -v

    # For cron (silent unless errors)
    scheduled_quality_check.sh --cron

    # CI with report
    scheduled_quality_check.sh --report report.md --json

EXIT CODES:
    0  All checks passed (or --no-fail specified)
    1  Issues found
    2  Configuration error

SEE ALSO:
    scripts/check.sh - Quick quality check
    scripts/lint.sh - Run all linters
    scripts/tools/check_links.sh - Link validation
EOF
}

# =============================================================================
# Check Functions
# =============================================================================

check_links() {
    local issues=0

    if ! ${CRON_MODE}; then
        print_section "Checking Links"
    fi

    # Use lychee if available
    if has_tool "lychee"; then
        if ${VERBOSE}; then print_info "Using lychee for link checking"; fi

        local lychee_output
        lychee_output=$(lychee --no-progress --format json "**/*.md" 2>/dev/null || true)

        if [[ -n "${lychee_output}" ]]; then
            local fail_count
            fail_count=$(echo "${lychee_output}" | jq -r '.fail_count // 0' 2>/dev/null || echo "0")
            issues=$((issues + fail_count))

            if [[ ${fail_count} -gt 0 ]]; then
                if ! ${CRON_MODE}; then print_fail "${fail_count} broken links found"; fi
                if ${VERBOSE}; then echo "${lychee_output}" | jq -r '.fails[]? | "  - \(.url)"' 2>/dev/null; fi
            else
                if ! ${CRON_MODE}; then print_pass "All links valid"; fi
            fi
        fi
    # Fallback: check internal links with grep
    elif has_files "*.md"; then
        if ${VERBOSE}; then print_info "Using basic link checking (install lychee for better results)"; fi

        # Find markdown links and check if targets exist
        local broken=0
        while IFS= read -r file; do
            # Extract markdown links: [text](path)
            while IFS= read -r link; do
                # Skip external links and anchors
                [[ "${link}" =~ ^http ]] && continue
                [[ "${link}" =~ ^# ]] && continue
                [[ "${link}" =~ ^mailto: ]] && continue

                # Remove anchor from link
                local path="${link%%#*}"
                [[ -z "${path}" ]] && continue

                # Resolve relative to file location
                local file_dir
                file_dir=$(dirname "${file}")
                local target="${file_dir}/${path}"

                if [[ ! -e "${target}" ]]; then
                    ((broken++)) || true
                    if ${VERBOSE}; then print_fail "Broken: ${file} -> ${link}"; fi
                fi
            done < <(grep -oP '\[.*?\]\(\K[^)]+' "${file}" 2>/dev/null || true)
        done < <(find . -name "*.md" -not -path "./.git/*" -not -path "./.venv/*" 2>/dev/null)

        issues=$((issues + broken))
        if [[ ${broken} -gt 0 ]]; then
            if ! ${CRON_MODE}; then print_fail "${broken} broken internal links"; fi
        else
            if ! ${CRON_MODE}; then print_pass "Internal links OK"; fi
        fi
    else
        if ! ${CRON_MODE}; then print_skip "No markdown files found"; fi
    fi

    LINK_ISSUES=${issues}
    return 0
}

check_lint() {
    local issues=0

    if ! ${CRON_MODE}; then
        print_section "Running Linters"
    fi

    # Markdown lint
    if has_tool "markdownlint" && has_files "*.md"; then
        if ${VERBOSE}; then print_info "Running markdownlint..."; fi
        local md_issues=0
        if ! markdownlint "**/*.md" --ignore node_modules --ignore .venv &>/dev/null; then
            md_issues=$(
                set +o pipefail
                markdownlint "**/*.md" --ignore node_modules --ignore .venv 2>&1 | wc -l
            )
            issues=$((issues + md_issues))
            if ! ${CRON_MODE}; then print_fail "markdownlint: ${md_issues} issues"; fi
        else
            if ! ${CRON_MODE}; then print_pass "markdownlint: OK"; fi
        fi
    fi

    # YAML lint
    if has_tool "yamllint" && has_files "*.yaml" || has_files "*.yml"; then
        if ${VERBOSE}; then print_info "Running yamllint..."; fi
        local yaml_issues=0
        if ! yamllint -d relaxed . &>/dev/null 2>&1; then
            yaml_issues=$(
                set +o pipefail
                yamllint -d relaxed . 2>&1 | grep -c "error\|warning"
            )
            issues=$((issues + yaml_issues))
            if ! ${CRON_MODE}; then print_fail "yamllint: ${yaml_issues} issues"; fi
        else
            if ! ${CRON_MODE}; then print_pass "yamllint: OK"; fi
        fi
    fi

    # Shell lint
    if has_tool "shellcheck" && has_files "*.sh"; then
        if ${VERBOSE}; then print_info "Running shellcheck..."; fi
        local shell_issues=0
        local shell_files
        shell_files=$(find . -name "*.sh" -not -path "./.git/*" -not -path "./.venv/*" 2>/dev/null)
        if [[ -n "${shell_files}" ]]; then
            # shellcheck disable=SC2086
            if ! shellcheck ${shell_files} &>/dev/null; then
                shell_issues=$(
                    set +o pipefail
                    shellcheck ${shell_files} 2>&1 | grep -c "^In "
                )
                issues=$((issues + shell_issues))
                if ! ${CRON_MODE}; then print_fail "shellcheck: ${shell_issues} files with issues"; fi
            else
                if ! ${CRON_MODE}; then print_pass "shellcheck: OK"; fi
            fi
        fi
    fi

    # Python lint (if applicable)
    if has_tool "ruff" && has_files "*.py"; then
        if ${VERBOSE}; then print_info "Running ruff..."; fi
        local py_issues=0
        if ! ruff check . --quiet &>/dev/null 2>&1; then
            py_issues=$(
                set +o pipefail
                ruff check . 2>&1 | wc -l
            )
            issues=$((issues + py_issues))
            if ! ${CRON_MODE}; then print_fail "ruff: ${py_issues} issues"; fi
        else
            if ! ${CRON_MODE}; then print_pass "ruff: OK"; fi
        fi
    fi

    LINT_ISSUES=${issues}
    return 0
}

check_format() {
    local issues=0

    if ! ${CRON_MODE}; then
        print_section "Checking Formatting"
    fi

    # Prettier check
    if has_tool "prettier" || has_tool "npx"; then
        if ${VERBOSE}; then print_info "Running prettier..."; fi
        local prettier_cmd="prettier"
        has_tool "prettier" || prettier_cmd="npx prettier"

        if ! ${prettier_cmd} --check "**/*.{md,yaml,yml,json}" --ignore-path .gitignore &>/dev/null 2>&1; then
            local fmt_issues
            fmt_issues=$(
                set +o pipefail
                ${prettier_cmd} --check "**/*.{md,yaml,yml,json}" --ignore-path .gitignore 2>&1 | grep -c "\[warn\]"
            )
            issues=$((issues + fmt_issues))
            if ! ${CRON_MODE}; then print_fail "prettier: ${fmt_issues} files need formatting"; fi
        else
            if ! ${CRON_MODE}; then print_pass "prettier: OK"; fi
        fi
    fi

    # Trailing whitespace check
    if ${VERBOSE}; then print_info "Checking trailing whitespace..."; fi
    local ws_files=0
    while IFS= read -r file; do
        if grep -q '[[:space:]]$' "${file}" 2>/dev/null; then
            ((ws_files++)) || true
            if ${VERBOSE}; then print_info "  Trailing whitespace: ${file}"; fi
        fi
    done < <(find . \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "*.py" \) \
        -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" 2>/dev/null)

    if [[ ${ws_files} -gt 0 ]]; then
        issues=$((issues + ws_files))
        if ! ${CRON_MODE}; then print_fail "Trailing whitespace: ${ws_files} files"; fi
    else
        if ! ${CRON_MODE}; then print_pass "Trailing whitespace: OK"; fi
    fi

    FORMAT_ISSUES=${issues}
    return 0
}

# =============================================================================
# Report Generation
# =============================================================================

generate_report() {
    local output_file="$1"

    mkdir -p "$(dirname "${output_file}")"

    cat >"${output_file}" <<EOF
# Quality Check Report

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')
**Repository**: ${REPO_ROOT}

## Summary

| Check Type | Issues |
|------------|--------|
| Links | ${LINK_ISSUES} |
| Linting | ${LINT_ISSUES} |
| Formatting | ${FORMAT_ISSUES} |
| **Total** | **${TOTAL_ISSUES}** |

## Status

$(if [[ ${TOTAL_ISSUES} -eq 0 ]]; then echo "All checks passed."; else echo "Issues found - review and fix."; fi)

## Recommendations

EOF

    {
        if [[ ${LINK_ISSUES} -gt 0 ]]; then
            echo "- Fix broken links: Run \`lychee **/*.md\` for details"
        fi
        if [[ ${LINT_ISSUES} -gt 0 ]]; then
            echo "- Fix lint issues: Run \`./scripts/lint.sh -v\`"
        fi
        if [[ ${FORMAT_ISSUES} -gt 0 ]]; then
            echo "- Fix formatting: Run \`./scripts/format.sh\`"
        fi
        if [[ ${TOTAL_ISSUES} -eq 0 ]]; then
            echo "- No action required"
        fi

        echo ""
        echo "---"
    } >>"${output_file}"
    echo "*Report generated by scheduled_quality_check.sh*" >>"${output_file}"

    if ! ${CRON_MODE}; then print_pass "Report saved: ${output_file}"; fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
        -h | --help)
            show_script_help
            exit 0
            ;;
        --links)
            CHECK_LINKS=true
            CHECK_FULL=false
            shift
            ;;
        --lint)
            CHECK_LINT=true
            CHECK_FULL=false
            shift
            ;;
        --format)
            CHECK_FULL=false
            shift
            ;;
        --full)
            CHECK_FULL=true
            shift
            ;;
        --cron)
            CRON_MODE=true
            shift
            ;;
        --report)
            REPORT_FILE="$2"
            shift 2
            ;;
        --no-fail)
            FAIL_ON_ISSUES=false
            shift
            ;;
        -v | --verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            enable_json
            shift
            ;;
        -*)
            echo "Unknown option: $1" >&2
            echo "Use -h for help" >&2
            exit 2
            ;;
        *)
            echo "Unexpected argument: $1" >&2
            exit 2
            ;;
        esac
    done

    # Header
    if ! ${CRON_MODE}; then
        print_header "SCHEDULED QUALITY CHECK"
        echo ""
        print_info "Repository: ${REPO_ROOT}"
        print_info "Timestamp:  $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
    fi

    # Run checks
    if ${CHECK_FULL} || ${CHECK_LINKS}; then
        check_links
    fi

    if ${CHECK_FULL} || ${CHECK_LINT}; then
        check_lint
    fi

    if ${CHECK_FULL}; then
        check_format
    fi

    # Calculate total
    TOTAL_ISSUES=$((LINK_ISSUES + LINT_ISSUES + FORMAT_ISSUES))

    # Generate report if requested
    if [[ -n "${REPORT_FILE}" ]]; then
        generate_report "${REPORT_FILE}"
    fi

    # Save to default location if not cron mode
    if ! ${CRON_MODE} && [[ -z "${REPORT_FILE}" ]]; then
        mkdir -p "${REPORT_DIR}"
        generate_report "${REPORT_DIR}/quality_report_${TIMESTAMP}.md"
    fi

    # Summary
    if ! ${CRON_MODE}; then
        print_header "SUMMARY"
        echo ""
        printf "  %-20s %d\n" "Link issues:" "${LINK_ISSUES}"
        printf "  %-20s %d\n" "Lint issues:" "${LINT_ISSUES}"
        printf "  %-20s %d\n" "Format issues:" "${FORMAT_ISSUES}"
        echo "  ────────────────────────"
        printf "  ${BOLD}%-20s %d${NC}\n" "Total issues:" "${TOTAL_ISSUES}"
        echo ""
    fi

    # JSON output
    if is_json_mode; then
        printf '{"total_issues":%d,"link_issues":%d,"lint_issues":%d,"format_issues":%d,"timestamp":"%s"}\n' \
            "${TOTAL_ISSUES}" "${LINK_ISSUES}" "${LINT_ISSUES}" "${FORMAT_ISSUES}" "$(date -Iseconds)"
    fi

    # Exit status
    if [[ ${TOTAL_ISSUES} -gt 0 ]]; then
        if ! ${CRON_MODE}; then
            print_fail "Quality check found ${TOTAL_ISSUES} issue(s)"
            print_info "Run ./scripts/fix.sh to auto-fix"
        fi
        if ${FAIL_ON_ISSUES}; then
            exit 1
        fi
    else
        if ! ${CRON_MODE}; then print_pass "All quality checks passed!"; fi
    fi

    exit 0
}

main "$@"
