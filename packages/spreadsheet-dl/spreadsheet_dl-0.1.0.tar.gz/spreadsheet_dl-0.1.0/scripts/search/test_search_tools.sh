#!/usr/bin/env bash
# =============================================================================
# test_search_tools.sh - Comprehensive Test Suite for Search/PDF Scripts
# =============================================================================
# Tests search.sh and pdf_tools.sh for correct functionality and CLI compliance.
#
# Usage: ./scripts/search/test_search_tools.sh [--verbose] [--keep-temp]
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Options
VERBOSE=false
KEEP_TEMP=false

# Test directory
TEST_DIR=""

# =============================================================================
# Helper Functions
# =============================================================================

log_test() {
    echo -e "${BLUE}[TEST]${NC} $*"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $*"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $*"
    ((TESTS_FAILED++))
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $*"
    ((TESTS_SKIPPED++))
}

log_info() {
    if ${VERBOSE}; then
        echo -e "  ${BLUE}[INFO]${NC} $*"
    fi
}

# =============================================================================
# Setup and Teardown
# =============================================================================

setup_test_env() {
    echo ""
    echo "=========================================="
    echo "  Search Tools Test Suite"
    echo "=========================================="
    echo ""

    # Create temporary directory
    TEST_DIR=$(mktemp -d)
    log_info "Test directory: ${TEST_DIR}"

    # Check for required tools
    echo -e "${BLUE}Checking dependencies...${NC}"

    if command -v rg &>/dev/null; then
        echo -e "${GREEN}  ripgrep: OK${NC}"
    else
        echo -e "${YELLOW}  ripgrep: not installed (will use fallback)${NC}"
    fi

    if command -v ag &>/dev/null; then
        echo -e "${GREEN}  ag (silver_searcher): OK${NC}"
    else
        echo -e "${YELLOW}  ag: not installed${NC}"
    fi

    if command -v pdfgrep &>/dev/null; then
        echo -e "${GREEN}  pdfgrep: OK${NC}"
    else
        echo -e "${YELLOW}  pdfgrep: not installed - PDF search tests will be limited${NC}"
    fi

    if command -v pdftotext &>/dev/null; then
        echo -e "${GREEN}  pdftotext (poppler): OK${NC}"
    else
        echo -e "${YELLOW}  pdftotext: not installed - PDF extraction tests will be skipped${NC}"
    fi

    if command -v pdfinfo &>/dev/null; then
        echo -e "${GREEN}  pdfinfo (poppler): OK${NC}"
    else
        echo -e "${YELLOW}  pdfinfo: not installed${NC}"
    fi

    if command -v ocrmypdf &>/dev/null; then
        echo -e "${GREEN}  ocrmypdf: OK${NC}"
    else
        echo -e "${YELLOW}  ocrmypdf: not installed - OCR tests will be skipped${NC}"
    fi

    if command -v tesseract &>/dev/null; then
        echo -e "${GREEN}  tesseract: OK${NC}"
    else
        echo -e "${YELLOW}  tesseract: not installed${NC}"
    fi

    echo ""

    # Create test files
    create_test_files
}

create_test_files() {
    # Create test text files
    mkdir -p "${TEST_DIR}/src" "${TEST_DIR}/docs"

    # Python file
    cat >"${TEST_DIR}/src/example.py" <<'EOF'
#!/usr/bin/env python3
"""Example Python script for testing search."""

def hello_world():
    """Print hello world."""
    print("Hello, World!")

def search_test():
    """Test function with TODO comment."""
    # TODO: Implement this function
    pass

if __name__ == "__main__":
    hello_world()
EOF

    # JavaScript file
    cat >"${TEST_DIR}/src/example.js" <<'EOF'
// Example JavaScript file for testing

function helloWorld() {
    console.log("Hello, World!");
}

// TODO: Add more functions
function searchTest() {
    // Implementation pending
    return null;
}

module.exports = { helloWorld, searchTest };
EOF

    # Markdown file
    cat >"${TEST_DIR}/docs/README.md" <<'EOF'
# Test Documentation

This is a test README file for search testing.

## Features

- Text search with ripgrep
- PDF search with pdfgrep
- File finding

## TODO

- Add more examples
- Improve documentation
EOF

    # Hidden file
    cat >"${TEST_DIR}/.hidden_file" <<'EOF'
This is a hidden file for testing --hidden flag.
TODO: Hidden TODO
EOF

    # Create a simple test PDF if pdftotext is available
    # (We'll create a text file that mimics what pdftotext would output)
    cat >"${TEST_DIR}/docs/sample.txt" <<'EOF'
Sample PDF Content

This is sample text content that would be in a PDF file.
It contains searchable text for testing purposes.

Page 1 of 1

Keywords: test, sample, search, document
EOF

    # Create .gitignore
    cat >"${TEST_DIR}/.gitignore" <<'EOF'
*.tmp
ignored_dir/
EOF

    mkdir -p "${TEST_DIR}/ignored_dir"
    echo "This should be ignored" >"${TEST_DIR}/ignored_dir/ignored.txt"
    echo "Temporary file" >"${TEST_DIR}/temp.tmp"

    log_info "Created test files"
}

cleanup_test_env() {
    if [[ -n "${TEST_DIR}" ]] && [[ -d "${TEST_DIR}" ]]; then
        if ${KEEP_TEMP}; then
            echo ""
            echo -e "${BLUE}Test files preserved at: ${TEST_DIR}${NC}"
        else
            rm -rf "${TEST_DIR}"
            log_info "Cleaned up test directory"
        fi
    fi
}

# =============================================================================
# Search.sh Tests
# =============================================================================

test_search_help() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Help flag (--help)"

    if [[ ! -x "${script}" ]]; then
        log_fail "Script not executable: ${script}"
        return 1
    fi

    if "${script}" --help &>/dev/null; then
        log_pass "search.sh help works"
    else
        log_fail "search.sh help failed"
        return 1
    fi
}

test_search_no_args() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: No arguments shows help"

    if "${script}" &>/dev/null; then
        log_pass "search.sh shows help with no args"
    else
        log_fail "search.sh failed with no args"
        return 1
    fi
}

test_search_version() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Version command"

    local output
    if output=$("${script}" version 2>&1); then
        if echo "${output}" | grep -q "ripgrep\|grep\|ag"; then
            log_pass "search.sh version works"
        else
            log_fail "search.sh version output unexpected"
            return 1
        fi
    else
        log_fail "search.sh version failed"
        return 1
    fi
}

test_search_text_basic() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Basic text search"

    local output
    if output=$("${script}" text "hello" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -qi "hello"; then
            log_pass "Basic text search works"
        else
            log_fail "Text search found no matches"
            return 1
        fi
    else
        log_fail "Text search failed"
        return 1
    fi
}

test_search_text_case_insensitive() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Case insensitive text search (-i)"

    local output
    if output=$("${script}" text -i "HELLO" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -qi "hello"; then
            log_pass "Case insensitive search works"
        else
            log_fail "Case insensitive search found no matches"
            return 1
        fi
    else
        log_fail "Case insensitive search failed"
        return 1
    fi
}

test_search_text_count() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Count matches (-c)"

    local output
    if output=$("${script}" text -c "TODO" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -qE '[0-9]+'; then
            log_pass "Count option works"
        else
            log_fail "Count option produced no numbers"
            return 1
        fi
    else
        log_fail "Count search failed"
        return 1
    fi
}

test_search_text_list_files() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: List files only (-l)"

    local output
    if output=$("${script}" text -l "TODO" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -qE '\.(py|js|md)'; then
            log_pass "List files option works"
        else
            log_info "Output: ${output}"
            log_fail "List files option produced unexpected output"
            return 1
        fi
    else
        log_fail "List files search failed"
        return 1
    fi
}

test_search_text_type_filter() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: File type filter (-t py)"

    # Only test if ripgrep is available (type filter is rg-specific)
    if ! command -v rg &>/dev/null; then
        log_skip "Type filter requires ripgrep"
        return 0
    fi

    local output
    if output=$("${script}" text -t py "def" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -q "example.py"; then
            log_pass "Type filter works"
        else
            log_fail "Type filter found no Python files"
            return 1
        fi
    else
        log_fail "Type filter search failed"
        return 1
    fi
}

test_search_text_dry_run() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Dry run mode"

    local output
    if output=$("${script}" text --dry-run "pattern" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -qi "dry.run"; then
            log_pass "Dry run mode works"
        else
            log_fail "Dry run output unexpected"
            return 1
        fi
    else
        log_fail "Dry run failed"
        return 1
    fi
}

test_search_text_json() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: JSON output mode"

    # JSON mode behavior depends on whether ripgrep is available
    local output
    if output=$("${script}" text --json "hello" "${TEST_DIR}" 2>&1); then
        # Either ripgrep JSON or our wrapper JSON
        if echo "${output}" | grep -qE '\{|\[|"'; then
            log_pass "JSON output mode works"
        else
            log_info "Output: ${output}"
            log_fail "JSON output not valid"
            return 1
        fi
    else
        log_fail "JSON mode failed"
        return 1
    fi
}

test_search_find_basic() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Find files by name"

    local output
    if output=$("${script}" find "*.py" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -q "example.py"; then
            log_pass "Find files works"
        else
            log_fail "Find didn't locate Python file"
            return 1
        fi
    else
        log_fail "Find command failed"
        return 1
    fi
}

test_search_find_case_insensitive() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Find files case insensitive"

    local output
    if output=$("${script}" find -i "README*" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -qi "readme"; then
            log_pass "Find case insensitive works"
        else
            log_fail "Find didn't locate README"
            return 1
        fi
    else
        log_fail "Find case insensitive failed"
        return 1
    fi
}

test_search_hidden() {
    local script="${SCRIPT_DIR}/search.sh"
    ((TESTS_RUN++))
    log_test "search.sh: Include hidden files (--hidden)"

    local output
    if output=$("${script}" text --hidden "Hidden TODO" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -q "hidden"; then
            log_pass "Hidden files search works"
        else
            log_fail "Hidden file not found"
            return 1
        fi
    else
        log_fail "Hidden files search failed"
        return 1
    fi
}

# =============================================================================
# PDF Tools Tests
# =============================================================================

test_pdf_help() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: Help flag (--help)"

    if [[ ! -x "${script}" ]]; then
        log_fail "Script not executable: ${script}"
        return 1
    fi

    if "${script}" --help &>/dev/null; then
        log_pass "pdf_tools.sh help works"
    else
        log_fail "pdf_tools.sh help failed"
        return 1
    fi
}

test_pdf_no_args() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: No arguments shows help"

    if "${script}" &>/dev/null; then
        log_pass "pdf_tools.sh shows help with no args"
    else
        log_fail "pdf_tools.sh failed with no args"
        return 1
    fi
}

test_pdf_version() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: Version command"

    local output
    if output=$("${script}" version 2>&1); then
        if echo "${output}" | grep -qE "pdftotext|pdfinfo|tesseract|ocrmypdf"; then
            log_pass "pdf_tools.sh version works"
        else
            log_fail "pdf_tools.sh version output unexpected"
            return 1
        fi
    else
        log_fail "pdf_tools.sh version failed"
        return 1
    fi
}

test_pdf_missing_file() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: Missing file error"

    local output
    if output=$("${script}" info "/nonexistent/file.pdf" 2>&1); then
        log_fail "Should fail on missing file"
        return 1
    else
        if echo "${output}" | grep -qi "not found"; then
            log_pass "Missing file error handled correctly"
        else
            log_fail "Missing file error message unexpected"
            return 1
        fi
    fi
}

test_pdf_invalid_file() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: Invalid PDF file error"

    # Use a text file as invalid PDF
    local output
    if output=$("${script}" info "${TEST_DIR}/src/example.py" 2>&1); then
        log_fail "Should fail on non-PDF file"
        return 1
    else
        if echo "${output}" | grep -qi "not.*valid\|not.*pdf"; then
            log_pass "Invalid PDF error handled correctly"
        else
            log_info "Output: ${output}"
            log_fail "Invalid PDF error message unexpected"
            return 1
        fi
    fi
}

test_pdf_dry_run() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: Dry run mode"

    # Create a minimal valid-looking PDF header
    echo -e "%PDF-1.4\n%%EOF" >"${TEST_DIR}/minimal.pdf"

    local output
    if output=$("${script}" extract --dry-run "${TEST_DIR}/minimal.pdf" 2>&1); then
        if echo "${output}" | grep -qi "dry.run"; then
            log_pass "pdf_tools.sh dry run works"
        else
            log_fail "Dry run output unexpected"
            return 1
        fi
    else
        log_fail "Dry run failed"
        return 1
    fi
}

test_pdf_extract_with_real_pdf() {
    local script="${SCRIPT_DIR}/pdf_tools.sh"
    ((TESTS_RUN++))
    log_test "pdf_tools.sh: Extract from real PDF"

    if ! command -v pdftotext &>/dev/null; then
        log_skip "pdftotext not installed"
        return 0
    fi

    # We need a real PDF to test this properly
    # For now, skip if no real PDF exists
    log_skip "No test PDF available (would need to create one)"
}

# =============================================================================
# ShellCheck Validation
# =============================================================================

test_shellcheck() {
    echo ""
    echo -e "${BLUE}Testing: ShellCheck Compliance${NC}"
    echo "----------------------------------------"

    if ! command -v shellcheck &>/dev/null; then
        log_skip "ShellCheck not installed"
        return 0
    fi

    local scripts=(
        "${SCRIPT_DIR}/search.sh"
        "${SCRIPT_DIR}/pdf_tools.sh"
    )

    for script in "${scripts[@]}"; do
        ((TESTS_RUN++))
        local name
        name=$(basename "${script}")
        log_test "ShellCheck: ${name}"

        if [[ ! -f "${script}" ]]; then
            log_skip "Script not found: ${name}"
            continue
        fi

        if shellcheck "${script}" 2>/dev/null; then
            log_pass "${name} passes ShellCheck"
        else
            log_fail "${name} has ShellCheck issues"
        fi
    done
}

# =============================================================================
# Exit Code Tests
# =============================================================================

test_exit_codes() {
    echo ""
    echo -e "${BLUE}Testing: Exit Codes${NC}"
    echo "----------------------------------------"

    local script="${SCRIPT_DIR}/search.sh"

    # Test exit code 0 (matches found)
    ((TESTS_RUN++))
    log_test "Exit code 0 when matches found"
    if "${script}" text "hello" "${TEST_DIR}" &>/dev/null; then
        log_pass "Exit 0 on matches"
    else
        log_fail "Expected exit 0 on matches"
    fi

    # Test exit code 1 (no matches)
    ((TESTS_RUN++))
    log_test "Exit code 1 when no matches found"
    if "${script}" text "nonexistent_pattern_xyz123" "${TEST_DIR}" &>/dev/null; then
        log_fail "Expected exit 1 on no matches"
    else
        local code=$?
        if [[ ${code} -eq 1 ]]; then
            log_pass "Exit 1 on no matches"
        else
            log_fail "Expected exit 1, got ${code}"
        fi
    fi

    # Test exit code 2 (error)
    ((TESTS_RUN++))
    log_test "Exit code 2 on invalid command"
    if "${script}" invalid_command pattern 2>/dev/null; then
        log_fail "Expected exit 2 on invalid command"
    else
        local code=$?
        if [[ ${code} -eq 2 ]]; then
            log_pass "Exit 2 on invalid command"
        else
            log_fail "Expected exit 2, got ${code}"
        fi
    fi
}

# =============================================================================
# Integration Tests
# =============================================================================

test_integration() {
    echo ""
    echo -e "${BLUE}Testing: Integration${NC}"
    echo "----------------------------------------"

    local search_script="${SCRIPT_DIR}/search.sh"
    local pdf_script="${SCRIPT_DIR}/pdf_tools.sh"

    # Test search.sh all command
    ((TESTS_RUN++))
    log_test "search.sh: Combined text+PDF search (all)"

    local output
    if output=$("${search_script}" all "hello" "${TEST_DIR}" 2>&1); then
        if echo "${output}" | grep -q "Text Files"; then
            log_pass "Combined search works"
        else
            log_fail "Combined search output unexpected"
            return 1
        fi
    else
        # Might return 1 if no PDF matches
        if echo "${output}" | grep -q "Text Files"; then
            log_pass "Combined search works (no PDFs)"
        else
            log_fail "Combined search failed"
            return 1
        fi
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
        -v | --verbose)
            VERBOSE=true
            shift
            ;;
        --keep-temp)
            KEEP_TEMP=true
            shift
            ;;
        -h | --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Test suite for search and PDF tools scripts."
            echo ""
            echo "Options:"
            echo "  -v, --verbose    Verbose output"
            echo "  --keep-temp      Keep temporary test files"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
        esac
    done

    # Setup
    setup_test_env

    # Trap for cleanup
    trap cleanup_test_env EXIT

    # Make scripts executable
    chmod +x "${SCRIPT_DIR}/search.sh" 2>/dev/null || true
    chmod +x "${SCRIPT_DIR}/pdf_tools.sh" 2>/dev/null || true

    # Run search.sh tests
    echo ""
    echo -e "${BLUE}Testing: search.sh${NC}"
    echo "----------------------------------------"
    test_search_help
    test_search_no_args
    test_search_version
    test_search_text_basic
    test_search_text_case_insensitive
    test_search_text_count
    test_search_text_list_files
    test_search_text_type_filter
    test_search_text_dry_run
    test_search_text_json
    test_search_find_basic
    test_search_find_case_insensitive
    test_search_hidden

    # Run pdf_tools.sh tests
    echo ""
    echo -e "${BLUE}Testing: pdf_tools.sh${NC}"
    echo "----------------------------------------"
    test_pdf_help
    test_pdf_no_args
    test_pdf_version
    test_pdf_missing_file
    test_pdf_invalid_file
    test_pdf_dry_run
    test_pdf_extract_with_real_pdf

    # Run common tests
    test_shellcheck
    test_exit_codes
    test_integration

    # Summary
    echo ""
    echo "=========================================="
    echo "  Test Summary"
    echo "=========================================="
    echo ""
    echo "Tests run:    ${TESTS_RUN}"
    echo -e "${GREEN}Tests passed: ${TESTS_PASSED}${NC}"
    if [[ ${TESTS_FAILED} -gt 0 ]]; then
        echo -e "${RED}Tests failed: ${TESTS_FAILED}${NC}"
    else
        echo "Tests failed: ${TESTS_FAILED}"
    fi
    if [[ ${TESTS_SKIPPED} -gt 0 ]]; then
        echo -e "${YELLOW}Tests skipped: ${TESTS_SKIPPED}${NC}"
    else
        echo "Tests skipped: ${TESTS_SKIPPED}"
    fi
    echo ""

    if [[ ${TESTS_FAILED} -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

main "$@"
