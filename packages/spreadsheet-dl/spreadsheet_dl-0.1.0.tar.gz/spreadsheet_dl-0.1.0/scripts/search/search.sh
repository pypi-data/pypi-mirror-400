#!/usr/bin/env bash
# =============================================================================
# search.sh - Universal Text and PDF Search Utility
# =============================================================================
# Usage: search.sh [COMMAND] [OPTIONS] <pattern> [path...]
#
# Commands:
#   text        Search text files using ripgrep
#   pdf         Search PDF files using pdfgrep
#   find        Find files by name pattern
#   all         Search both text and PDF files
#
# Run with --help for full usage information.
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/search/search.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "${SCRIPT_DIR}/../lib/common.sh"

# =============================================================================
# Configuration
# =============================================================================

# Defaults
VERBOSE=false
JSON_OUTPUT=false
DRY_RUN=false
CASE_INSENSITIVE=false
CONTEXT_LINES=0
COUNT_ONLY=false
LIST_FILES=false
FIXED_STRINGS=false
WORD_MATCH=false
MAX_COUNT=""
FILE_TYPE=""
INCLUDE_HIDDEN=false
NO_IGNORE=false
RECURSIVE=true
COLOR="auto"

# Tool detection results
HAS_RIPGREP=false
HAS_AG=false
HAS_PDFGREP=false

# =============================================================================
# Help
# =============================================================================

show_usage() {
    cat <<'EOF'
Usage: search.sh [COMMAND] [OPTIONS] <pattern> [path...]

Universal search utility for text and PDF files with consistent CLI interface.
Automatically selects the best available tool (ripgrep > ag > grep).

COMMANDS:
    text        Search text files (ripgrep/ag/grep)
    pdf         Search PDF files (pdfgrep)
    find        Find files by name pattern
    all         Search both text and PDF files

OPTIONS:
    Common:
        -h, --help          Show this help message
        -v, --verbose       Verbose output
        --json              Machine-readable JSON output
        --dry-run           Show what would be done

    Search:
        -i, --ignore-case   Case insensitive search
        -w, --word          Match whole words only
        -F, --fixed-strings Treat pattern as literal string
        -c, --count         Only show count of matches
        -l, --files         Only show filenames with matches
        -C, --context N     Show N lines of context
        -m, --max-count N   Stop after N matches per file

    Filtering:
        -t, --type TYPE     File type filter (e.g., py, js, md)
        --hidden            Include hidden files
        --no-ignore         Don't respect .gitignore

    Output:
        --color MODE        Color output: auto, always, never
        -n, --line-number   Show line numbers (default: on)

EXAMPLES:
    # Search text files
    search.sh text "TODO" ./src
    search.sh text -i "error" --type py .

    # Search PDF files
    search.sh pdf "machine learning" ~/Documents/*.pdf
    search.sh pdf -i "abstract" --context 2 paper.pdf

    # Find files by name
    search.sh find "*.py" ./src
    search.sh find -i "readme*" .

    # Search everything (text + PDF)
    search.sh all "important" ./docs

    # Count matches
    search.sh text -c "function" ./src

    # JSON output for scripting
    search.sh text --json "pattern" ./src

EXIT CODES:
    0   Success (matches found)
    1   No matches found
    2   Error (missing tool, invalid arguments)

TOOL PRIORITY:
    Text search: ripgrep (rg) > The Silver Searcher (ag) > grep
    PDF search:  pdfgrep > grep on pdftotext output (fallback)
EOF
}

# =============================================================================
# Tool Detection
# =============================================================================

detect_tools() {
    if command -v rg &>/dev/null; then
        HAS_RIPGREP=true
    fi
    if command -v ag &>/dev/null; then
        HAS_AG=true
    fi
    if command -v pdfgrep &>/dev/null; then
        HAS_PDFGREP=true
    fi
}

get_text_search_tool() {
    if ${HAS_RIPGREP}; then
        echo "ripgrep"
    elif ${HAS_AG}; then
        echo "ag"
    else
        echo "grep"
    fi
}

# =============================================================================
# Text Search
# =============================================================================

search_text() {
    local pattern="$1"
    shift
    local paths=("$@")

    if [[ ${#paths[@]} -eq 0 ]]; then
        paths=(".")
    fi

    local tool
    tool=$(get_text_search_tool)

    if ${VERBOSE}; then
        print_info "Using ${tool} for text search"
        print_info "Pattern: ${pattern}"
        print_info "Paths: ${paths[*]}"
    fi

    local cmd_args=()

    if ${HAS_RIPGREP}; then
        # ripgrep
        cmd_args=("rg")

        if ${CASE_INSENSITIVE}; then cmd_args+=("-i"); fi
        if ${WORD_MATCH}; then cmd_args+=("-w"); fi
        if ${FIXED_STRINGS}; then cmd_args+=("-F"); fi
        if ${COUNT_ONLY}; then cmd_args+=("-c"); fi
        if ${LIST_FILES}; then cmd_args+=("-l"); fi
        if [[ ${CONTEXT_LINES} -gt 0 ]]; then cmd_args+=("-C" "${CONTEXT_LINES}"); fi
        if [[ -n "${MAX_COUNT}" ]]; then cmd_args+=("-m" "${MAX_COUNT}"); fi
        if [[ -n "${FILE_TYPE}" ]]; then cmd_args+=("-t" "${FILE_TYPE}"); fi
        if ${INCLUDE_HIDDEN}; then cmd_args+=("--hidden"); fi
        if ${NO_IGNORE}; then cmd_args+=("--no-ignore"); fi
        if [[ "${COLOR}" != "auto" ]]; then cmd_args+=("--color=${COLOR}"); fi

        if ${JSON_OUTPUT}; then
            cmd_args+=("--json")
        fi

        cmd_args+=("${pattern}")
        cmd_args+=("${paths[@]}")

    elif ${HAS_AG}; then
        # The Silver Searcher
        cmd_args=("ag")

        if ${CASE_INSENSITIVE}; then cmd_args+=("-i"); fi
        if ${WORD_MATCH}; then cmd_args+=("-w"); fi
        if ${FIXED_STRINGS}; then cmd_args+=("-Q"); fi
        if ${COUNT_ONLY}; then cmd_args+=("-c"); fi
        if ${LIST_FILES}; then cmd_args+=("-l"); fi
        if [[ ${CONTEXT_LINES} -gt 0 ]]; then cmd_args+=("-C" "${CONTEXT_LINES}"); fi
        if [[ -n "${MAX_COUNT}" ]]; then cmd_args+=("-m" "${MAX_COUNT}"); fi
        if ${INCLUDE_HIDDEN}; then cmd_args+=("--hidden"); fi
        if ${NO_IGNORE}; then cmd_args+=("--skip-vcs-ignores"); fi
        if [[ "${COLOR}" == "never" ]]; then cmd_args+=("--nocolor"); fi

        cmd_args+=("${pattern}")
        cmd_args+=("${paths[@]}")

    else
        # GNU grep fallback
        cmd_args=("grep")
        cmd_args+=("-r")
        cmd_args+=("-n")

        if ${CASE_INSENSITIVE}; then cmd_args+=("-i"); fi
        if ${WORD_MATCH}; then cmd_args+=("-w"); fi
        if ${FIXED_STRINGS}; then cmd_args+=("-F"); fi
        if ${COUNT_ONLY}; then cmd_args+=("-c"); fi
        if ${LIST_FILES}; then cmd_args+=("-l"); fi
        if [[ ${CONTEXT_LINES} -gt 0 ]]; then cmd_args+=("-C" "${CONTEXT_LINES}"); fi
        if [[ -n "${MAX_COUNT}" ]]; then cmd_args+=("-m" "${MAX_COUNT}"); fi
        if [[ "${COLOR}" == "always" ]]; then cmd_args+=("--color=always"); fi
        if [[ "${COLOR}" == "never" ]]; then cmd_args+=("--color=never"); fi

        cmd_args+=("${pattern}")
        cmd_args+=("${paths[@]}")
    fi

    if ${DRY_RUN}; then
        echo "[DRY RUN] ${cmd_args[*]}"
        return 0
    fi

    if ${VERBOSE}; then
        print_info "Command: ${cmd_args[*]}"
    fi

    local exit_code=0
    local output
    output=$("${cmd_args[@]}" 2>&1) || exit_code=$?

    if [[ ${exit_code} -eq 0 ]] || [[ ${exit_code} -eq 1 && -z "${output}" ]]; then
        # ripgrep/grep return 1 for no matches
        if [[ -n "${output}" ]]; then
            echo "${output}"
            if ${JSON_OUTPUT} && ! ${HAS_RIPGREP}; then
                # For non-ripgrep, wrap in JSON
                local count
                count=$(echo "${output}" | wc -l)
                json_result "text_search" "pass" "Found ${count} matches"
            fi
            return 0
        else
            if ${JSON_OUTPUT}; then
                json_result "text_search" "pass" "No matches found"
            else
                print_info "No matches found"
            fi
            return 1
        fi
    else
        if ${JSON_OUTPUT}; then
            json_result "text_search" "fail" "Search error"
        else
            print_fail "Search failed: ${output}"
        fi
        return 2
    fi
}

# =============================================================================
# PDF Search
# =============================================================================

search_pdf() {
    local pattern="$1"
    shift
    local paths=("$@")

    if [[ ${#paths[@]} -eq 0 ]]; then
        paths=(".")
    fi

    if ! ${HAS_PDFGREP}; then
        if command -v pdftotext &>/dev/null; then
            # Fallback: use pdftotext + grep
            search_pdf_fallback "${pattern}" "${paths[@]}"
            return $?
        else
            print_fail "pdfgrep not installed"
            print_info "Install with: sudo apt install pdfgrep"
            print_info "Or install poppler-utils for pdftotext fallback"
            return 2
        fi
    fi

    if ${VERBOSE}; then
        print_info "Using pdfgrep for PDF search"
        print_info "Pattern: ${pattern}"
        print_info "Paths: ${paths[*]}"
    fi

    local cmd_args=("pdfgrep")

    if ${CASE_INSENSITIVE}; then cmd_args+=("-i"); fi
    if ${COUNT_ONLY}; then cmd_args+=("-c"); fi
    if ${LIST_FILES}; then cmd_args+=("-l"); fi
    if [[ ${CONTEXT_LINES} -gt 0 ]]; then cmd_args+=("-C" "${CONTEXT_LINES}"); fi
    if [[ -n "${MAX_COUNT}" ]]; then cmd_args+=("--max-count=${MAX_COUNT}"); fi
    if ${RECURSIVE}; then cmd_args+=("-r"); fi

    # Always show page numbers and filenames
    cmd_args+=("-n")
    cmd_args+=("-H")

    if [[ "${COLOR}" == "always" ]]; then cmd_args+=("--color=always"); fi
    if [[ "${COLOR}" == "never" ]]; then cmd_args+=("--color=never"); fi

    cmd_args+=("${pattern}")
    cmd_args+=("${paths[@]}")

    if ${DRY_RUN}; then
        echo "[DRY RUN] ${cmd_args[*]}"
        return 0
    fi

    if ${VERBOSE}; then
        print_info "Command: ${cmd_args[*]}"
    fi

    local exit_code=0
    local output
    output=$("${cmd_args[@]}" 2>&1) || exit_code=$?

    if [[ ${exit_code} -eq 0 ]]; then
        if [[ -n "${output}" ]]; then
            if ${JSON_OUTPUT}; then
                # Parse pdfgrep output into JSON
                local count
                count=$(echo "${output}" | wc -l)
                echo "${output}"
                json_result "pdf_search" "pass" "Found ${count} matches"
            else
                echo "${output}"
            fi
            return 0
        else
            if ${JSON_OUTPUT}; then
                json_result "pdf_search" "pass" "No matches found"
            else
                print_info "No matches found"
            fi
            return 1
        fi
    elif [[ ${exit_code} -eq 1 ]]; then
        # No matches
        if ${JSON_OUTPUT}; then
            json_result "pdf_search" "pass" "No matches found"
        else
            print_info "No matches found"
        fi
        return 1
    else
        if ${JSON_OUTPUT}; then
            json_result "pdf_search" "fail" "Search error"
        else
            print_fail "PDF search failed: ${output}"
        fi
        return 2
    fi
}

search_pdf_fallback() {
    local pattern="$1"
    shift
    local paths=("$@")

    if ${VERBOSE}; then
        print_info "Using pdftotext + grep fallback for PDF search"
    fi

    local found=0
    local grep_opts=("-n")

    if ${CASE_INSENSITIVE}; then grep_opts+=("-i"); fi
    if ${COUNT_ONLY}; then grep_opts+=("-c"); fi
    if [[ ${CONTEXT_LINES} -gt 0 ]]; then grep_opts+=("-C" "${CONTEXT_LINES}"); fi
    if [[ -n "${MAX_COUNT}" ]]; then grep_opts+=("-m" "${MAX_COUNT}"); fi

    # Find all PDF files
    local pdf_files=()
    for path in "${paths[@]}"; do
        if [[ -f "${path}" ]] && [[ "${path,,}" == *.pdf ]]; then
            pdf_files+=("${path}")
        elif [[ -d "${path}" ]]; then
            while IFS= read -r -d '' file; do
                pdf_files+=("${file}")
            done < <(find "${path}" -type f -iname "*.pdf" -print0 2>/dev/null)
        fi
    done

    if [[ ${#pdf_files[@]} -eq 0 ]]; then
        print_info "No PDF files found"
        return 1
    fi

    for pdf in "${pdf_files[@]}"; do
        if ${VERBOSE}; then
            print_info "Searching: ${pdf}"
        fi

        local text
        if text=$(pdftotext -layout "${pdf}" - 2>/dev/null); then
            local result
            if result=$(echo "${text}" | grep "${grep_opts[@]}" "${pattern}" 2>/dev/null); then
                echo "=== ${pdf} ==="
                echo "${result}"
                echo ""
                ((found++))
            fi
        fi
    done

    if [[ ${found} -gt 0 ]]; then
        if ${JSON_OUTPUT}; then
            json_result "pdf_search" "pass" "Found matches in ${found} files"
        fi
        return 0
    else
        if ${JSON_OUTPUT}; then
            json_result "pdf_search" "pass" "No matches found"
        else
            print_info "No matches found"
        fi
        return 1
    fi
}

# =============================================================================
# File Find
# =============================================================================

search_find() {
    local pattern="$1"
    shift
    local paths=("$@")

    if [[ ${#paths[@]} -eq 0 ]]; then
        paths=(".")
    fi

    if ${VERBOSE}; then
        print_info "Finding files matching: ${pattern}"
        print_info "Paths: ${paths[*]}"
    fi

    local find_opts=()
    find_opts+=("-type" "f")

    if ${CASE_INSENSITIVE}; then
        find_opts+=("-iname" "${pattern}")
    else
        find_opts+=("-name" "${pattern}")
    fi

    if ! ${INCLUDE_HIDDEN}; then
        find_opts+=("-not" "-path" "*/.*")
    fi

    if ${DRY_RUN}; then
        echo "[DRY RUN] find ${paths[*]} ${find_opts[*]}"
        return 0
    fi

    local output
    local exit_code=0
    output=$(find "${paths[@]}" "${find_opts[@]}" 2>/dev/null | sort) || exit_code=$?

    if [[ -n "${output}" ]]; then
        if ${COUNT_ONLY}; then
            local count
            count=$(echo "${output}" | wc -l)
            if ${JSON_OUTPUT}; then
                printf '{"command":"find","count":%d}\n' "${count}"
            else
                echo "${count}"
            fi
        else
            echo "${output}"
            if ${JSON_OUTPUT}; then
                local count
                count=$(echo "${output}" | wc -l)
                json_result "find" "pass" "Found ${count} files"
            fi
        fi
        return 0
    else
        if ${JSON_OUTPUT}; then
            json_result "find" "pass" "No files found"
        else
            print_info "No files found matching pattern"
        fi
        return 1
    fi
}

# =============================================================================
# Search All (Text + PDF)
# =============================================================================

search_all() {
    local pattern="$1"
    shift
    local paths=("$@")

    if [[ ${#paths[@]} -eq 0 ]]; then
        paths=(".")
    fi

    if ${VERBOSE}; then
        print_info "Searching all files (text + PDF)"
    fi

    local text_results=0
    local pdf_results=0

    # Search text files
    echo "=== Text Files ==="
    if search_text "${pattern}" "${paths[@]}"; then
        text_results=1
    fi

    echo ""
    echo "=== PDF Files ==="
    if search_pdf "${pattern}" "${paths[@]}"; then
        pdf_results=1
    fi

    if ${JSON_OUTPUT}; then
        printf '{"command":"all","text_found":%s,"pdf_found":%s}\n' \
            "$([[ ${text_results} -eq 1 ]] && echo "true" || echo "false")" \
            "$([[ ${pdf_results} -eq 1 ]] && echo "true" || echo "false")"
    fi

    if [[ ${text_results} -eq 1 ]] || [[ ${pdf_results} -eq 1 ]]; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# Version Info
# =============================================================================

show_version() {
    echo "search.sh - Universal Search Utility"
    echo ""
    echo "Available tools:"

    if ${HAS_RIPGREP}; then
        local version
        version=$(rg --version 2>/dev/null | head -1)
        echo "  ripgrep: ${version}"
    else
        echo "  ripgrep: not installed"
    fi

    if ${HAS_AG}; then
        local version
        version=$(ag --version 2>/dev/null | head -1)
        echo "  ag: ${version}"
    else
        echo "  ag: not installed"
    fi

    if ${HAS_PDFGREP}; then
        local version
        version=$(pdfgrep --version 2>/dev/null | head -1)
        echo "  pdfgrep: ${version}"
    else
        echo "  pdfgrep: not installed"
    fi

    if command -v grep &>/dev/null; then
        local version
        version=$(grep --version 2>/dev/null | head -1)
        echo "  grep: ${version}"
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    # Detect available tools
    detect_tools

    # Check for help first
    if [[ $# -eq 0 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi

    # Get command
    local command="$1"
    shift

    # Handle version command
    if [[ "${command}" == "version" ]] || [[ "${command}" == "--version" ]]; then
        show_version
        exit 0
    fi

    # Parse global options
    local positional=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
        -h | --help)
            show_usage
            exit 0
            ;;
        -v | --verbose)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            enable_json
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -i | --ignore-case)
            CASE_INSENSITIVE=true
            shift
            ;;
        -w | --word)
            WORD_MATCH=true
            shift
            ;;
        -F | --fixed-strings)
            FIXED_STRINGS=true
            shift
            ;;
        -c | --count)
            COUNT_ONLY=true
            shift
            ;;
        -l | --files)
            LIST_FILES=true
            shift
            ;;
        -C | --context)
            CONTEXT_LINES="$2"
            shift 2
            ;;
        -m | --max-count)
            MAX_COUNT="$2"
            shift 2
            ;;
        -t | --type)
            FILE_TYPE="$2"
            shift 2
            ;;
        --hidden)
            INCLUDE_HIDDEN=true
            shift
            ;;
        --no-ignore)
            NO_IGNORE=true
            shift
            ;;
        --color)
            COLOR="$2"
            shift 2
            ;;
        -n | --line-number)
            # Default behavior, ignore
            shift
            ;;
        *)
            positional+=("$1")
            shift
            ;;
        esac
    done

    # Restore positional parameters
    set -- "${positional[@]}"

    # Need at least a pattern for search commands
    if [[ "${command}" != "version" ]] && [[ $# -lt 1 ]]; then
        print_fail "Usage: search.sh ${command} <pattern> [paths...]"
        exit 2
    fi

    case "${command}" in
    text)
        search_text "$@"
        ;;
    pdf)
        search_pdf "$@"
        ;;
    find)
        search_find "$@"
        ;;
    all)
        search_all "$@"
        ;;
    version | --version)
        show_version
        ;;
    *)
        print_fail "Unknown command: ${command}"
        echo "Run 'search.sh --help' for usage."
        exit 2
        ;;
    esac
}

main "$@"
