#!/usr/bin/env bash
# =============================================================================
# pdf_tools.sh - PDF Operations Utility
# =============================================================================
# Usage: pdf_tools.sh [COMMAND] [OPTIONS] <input> [output]
#
# Commands:
#   extract     Extract text from PDF
#   info        Get PDF metadata
#   ocr         OCR scanned PDF (create searchable PDF)
#   pages       Get page count
#   batch       Batch operations
#
# Run with --help for full usage information.
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/search/pdf_tools.sh
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
LAYOUT_MODE="layout"
PAGE_FIRST=""
PAGE_LAST=""
OUTPUT_FILE=""
LANGUAGE="eng"
FORCE_OCR=false
DESKEW=false
CLEAN=false

# Tool detection
HAS_PDFTOTEXT=false
HAS_PDFINFO=false
HAS_TESSERACT=false
HAS_OCRMYPDF=false
HAS_EXIFTOOL=false

# =============================================================================
# Help
# =============================================================================

show_usage() {
    cat <<'EOF'
Usage: pdf_tools.sh [COMMAND] [OPTIONS] <input> [output]

PDF operations utility for text extraction, metadata, and OCR.

COMMANDS:
    extract     Extract text from PDF
    info        Get PDF metadata
    ocr         OCR scanned PDF (create searchable PDF)
    pages       Get page count
    batch       Batch operations on multiple PDFs

OPTIONS:
    Common:
        -h, --help          Show this help message
        -v, --verbose       Verbose output
        --json              Machine-readable JSON output
        --dry-run           Show what would be done

    Extract:
        --layout            Maintain physical layout (default)
        --raw               Keep strings in content stream order
        --table             Table-oriented layout
        -f, --first N       First page to extract
        -l, --last N        Last page to extract
        -o, --output FILE   Output file (default: stdout)
        --no-page-breaks    Don't insert page break characters

    OCR:
        --lang LANG         OCR language (default: eng)
                            Multiple: --lang eng+fra+deu
        --force-ocr         OCR all pages (even with text)
        --skip-text         Skip pages that already have text
        --deskew            Deskew pages before OCR
        --clean             Clean pages (remove noise)
        --rotate            Auto-rotate pages

EXAMPLES:
    # Extract text from PDF
    pdf_tools.sh extract document.pdf
    pdf_tools.sh extract --layout -o output.txt document.pdf

    # Extract specific pages
    pdf_tools.sh extract -f 1 -l 10 document.pdf

    # Get PDF info
    pdf_tools.sh info document.pdf
    pdf_tools.sh info --json document.pdf

    # Get page count only
    pdf_tools.sh pages document.pdf

    # OCR a scanned PDF (creates searchable PDF)
    pdf_tools.sh ocr scanned.pdf searchable.pdf
    pdf_tools.sh ocr --lang eng+spa --deskew scanned.pdf output.pdf

    # Batch extract text
    pdf_tools.sh batch extract --output-dir ./text/ *.pdf

EXIT CODES:
    0   Success
    1   Failure (processing error)
    2   Error (missing tool, invalid arguments)

REQUIRED TOOLS:
    extract/info: poppler-utils (pdftotext, pdfinfo)
    ocr:          ocrmypdf (recommended) or tesseract

INSTALLATION:
    Debian/Ubuntu:
        sudo apt install poppler-utils
        sudo apt install ocrmypdf
        sudo apt install tesseract-ocr tesseract-ocr-eng

    macOS:
        brew install poppler
        brew install ocrmypdf
        brew install tesseract
EOF
}

# =============================================================================
# Tool Detection
# =============================================================================

detect_tools() {
    if command -v pdftotext &>/dev/null; then
        HAS_PDFTOTEXT=true
    fi
    if command -v pdfinfo &>/dev/null; then
        HAS_PDFINFO=true
    fi
    if command -v tesseract &>/dev/null; then
        HAS_TESSERACT=true
    fi
    if command -v ocrmypdf &>/dev/null; then
        HAS_OCRMYPDF=true
    fi
    if command -v exiftool &>/dev/null; then
        HAS_EXIFTOOL=true
    fi
}

check_pdf_exists() {
    local input="$1"

    if [[ ! -f "${input}" ]]; then
        print_fail "File not found: ${input}"
        return 1
    fi

    # Check if it's actually a PDF (magic bytes)
    local magic
    magic=$(head -c 4 "${input}" 2>/dev/null)
    if [[ "${magic}" != "%PDF" ]]; then
        print_fail "Not a valid PDF file: ${input}"
        return 1
    fi

    return 0
}

# =============================================================================
# Extract Text
# =============================================================================

extract_text() {
    local input="$1"

    if ! check_pdf_exists "${input}"; then
        return 1
    fi

    if ! ${HAS_PDFTOTEXT}; then
        print_fail "pdftotext not installed (part of poppler-utils)"
        print_info "Install with: sudo apt install poppler-utils"
        return 2
    fi

    if ${VERBOSE}; then
        print_info "Extracting text from: ${input}"
        print_info "Layout mode: ${LAYOUT_MODE}"
    fi

    local cmd_args=("pdftotext")

    # Layout options
    case "${LAYOUT_MODE}" in
    layout)
        cmd_args+=("-layout")
        ;;
    raw)
        cmd_args+=("-raw")
        ;;
    table)
        cmd_args+=("-table")
        ;;
    simple)
        # No layout flag
        ;;
    esac

    # Page range
    if [[ -n "${PAGE_FIRST}" ]]; then
        cmd_args+=("-f" "${PAGE_FIRST}")
    fi
    if [[ -n "${PAGE_LAST}" ]]; then
        cmd_args+=("-l" "${PAGE_LAST}")
    fi

    # Input file
    cmd_args+=("${input}")

    # Output: file or stdout
    if [[ -n "${OUTPUT_FILE}" ]]; then
        cmd_args+=("${OUTPUT_FILE}")
    else
        cmd_args+=("-") # stdout
    fi

    if ${DRY_RUN}; then
        echo "[DRY RUN] ${cmd_args[*]}"
        return 0
    fi

    if ${VERBOSE}; then
        print_info "Command: ${cmd_args[*]}"
    fi

    local exit_code=0
    if [[ -n "${OUTPUT_FILE}" ]]; then
        if "${cmd_args[@]}" 2>/dev/null; then
            if ${JSON_OUTPUT}; then
                local size
                size=$(stat -c%s "${OUTPUT_FILE}" 2>/dev/null || stat -f%z "${OUTPUT_FILE}" 2>/dev/null)
                printf '{"command":"extract","status":"pass","output":"%s","size":%d}\n' "${OUTPUT_FILE}" "${size}"
            else
                print_pass "Extracted to: ${OUTPUT_FILE}"
            fi
        else
            if ${JSON_OUTPUT}; then
                json_result "extract" "fail" "Extraction failed"
            else
                print_fail "Extraction failed"
            fi
            return 1
        fi
    else
        # Output to stdout
        "${cmd_args[@]}" || exit_code=$?
        if [[ ${exit_code} -ne 0 ]]; then
            return 1
        fi
    fi
}

# =============================================================================
# PDF Info
# =============================================================================

get_info() {
    local input="$1"

    if ! check_pdf_exists "${input}"; then
        return 1
    fi

    if ! ${HAS_PDFINFO}; then
        print_fail "pdfinfo not installed (part of poppler-utils)"
        print_info "Install with: sudo apt install poppler-utils"
        return 2
    fi

    if ${VERBOSE}; then
        print_info "Getting info for: ${input}"
    fi

    if ${DRY_RUN}; then
        echo "[DRY RUN] pdfinfo ${input}"
        return 0
    fi

    local info
    info=$(pdfinfo "${input}" 2>/dev/null) || {
        print_fail "Failed to read PDF info"
        return 1
    }

    if ${JSON_OUTPUT}; then
        # Parse pdfinfo output into JSON
        local title author subject keywords creator producer
        local created modified pages page_size pdf_version encrypted

        title=$(echo "${info}" | grep "^Title:" | sed 's/^Title:[[:space:]]*//' || echo "")
        author=$(echo "${info}" | grep "^Author:" | sed 's/^Author:[[:space:]]*//' || echo "")
        subject=$(echo "${info}" | grep "^Subject:" | sed 's/^Subject:[[:space:]]*//' || echo "")
        keywords=$(echo "${info}" | grep "^Keywords:" | sed 's/^Keywords:[[:space:]]*//' || echo "")
        creator=$(echo "${info}" | grep "^Creator:" | sed 's/^Creator:[[:space:]]*//' || echo "")
        producer=$(echo "${info}" | grep "^Producer:" | sed 's/^Producer:[[:space:]]*//' || echo "")
        created=$(echo "${info}" | grep "^CreationDate:" | sed 's/^CreationDate:[[:space:]]*//' || echo "")
        modified=$(echo "${info}" | grep "^ModDate:" | sed 's/^ModDate:[[:space:]]*//' || echo "")
        pages=$(echo "${info}" | grep "^Pages:" | sed 's/^Pages:[[:space:]]*//' || echo "0")
        page_size=$(echo "${info}" | grep "^Page size:" | sed 's/^Page size:[[:space:]]*//' || echo "")
        pdf_version=$(echo "${info}" | grep "^PDF version:" | sed 's/^PDF version:[[:space:]]*//' || echo "")
        encrypted=$(echo "${info}" | grep "^Encrypted:" | sed 's/^Encrypted:[[:space:]]*//' || echo "no")

        # Get file size
        local file_size
        file_size=$(stat -c%s "${input}" 2>/dev/null || stat -f%z "${input}" 2>/dev/null)

        printf '{"file":"%s","title":"%s","author":"%s","subject":"%s","keywords":"%s","creator":"%s","producer":"%s","created":"%s","modified":"%s","pages":%s,"page_size":"%s","pdf_version":"%s","encrypted":"%s","size_bytes":%d}\n' \
            "${input}" "${title}" "${author}" "${subject}" "${keywords}" "${creator}" "${producer}" "${created}" "${modified}" "${pages}" "${page_size}" "${pdf_version}" "${encrypted}" "${file_size}"
    else
        echo "File:        ${input}"
        echo "${info}"

        # Add file size
        local file_size
        file_size=$(stat -c%s "${input}" 2>/dev/null || stat -f%z "${input}" 2>/dev/null)
        echo "File size:   $(numfmt --to=iec-i --suffix=B "${file_size}" 2>/dev/null || echo "${file_size} bytes")"
    fi
}

# =============================================================================
# Page Count
# =============================================================================

get_pages() {
    local input="$1"

    if ! check_pdf_exists "${input}"; then
        return 1
    fi

    if ! ${HAS_PDFINFO}; then
        print_fail "pdfinfo not installed"
        return 2
    fi

    local pages
    pages=$(pdfinfo "${input}" 2>/dev/null | grep "^Pages:" | awk '{print $2}')

    if [[ -z "${pages}" ]]; then
        print_fail "Could not determine page count"
        return 1
    fi

    if ${JSON_OUTPUT}; then
        printf '{"file":"%s","pages":%s}\n' "${input}" "${pages}"
    else
        echo "${pages}"
    fi
}

# =============================================================================
# OCR
# =============================================================================

do_ocr() {
    local input="$1"
    local output="${2:-}"

    if ! check_pdf_exists "${input}"; then
        return 1
    fi

    # Default output name
    if [[ -z "${output}" ]]; then
        local base="${input%.pdf}"
        output="${base}_ocr.pdf"
    fi

    if ${HAS_OCRMYPDF}; then
        ocr_with_ocrmypdf "${input}" "${output}"
    elif ${HAS_TESSERACT}; then
        ocr_with_tesseract "${input}" "${output}"
    else
        print_fail "No OCR tool available"
        print_info "Install ocrmypdf: sudo apt install ocrmypdf"
        print_info "Or tesseract: sudo apt install tesseract-ocr"
        return 2
    fi
}

ocr_with_ocrmypdf() {
    local input="$1"
    local output="$2"

    if ${VERBOSE}; then
        print_info "Using ocrmypdf for OCR"
        print_info "Input: ${input}"
        print_info "Output: ${output}"
        print_info "Language: ${LANGUAGE}"
    fi

    local cmd_args=("ocrmypdf")

    # Language
    cmd_args+=("-l" "${LANGUAGE}")

    # Options
    if ${FORCE_OCR}; then
        cmd_args+=("--force-ocr")
    else
        cmd_args+=("--skip-text")
    fi

    if ${DESKEW}; then
        cmd_args+=("--deskew")
    fi

    if ${CLEAN}; then
        cmd_args+=("--clean")
    fi

    # Output type (PDF/A for archival)
    cmd_args+=("--output-type" "pdfa")

    # Input/output
    cmd_args+=("${input}" "${output}")

    if ${DRY_RUN}; then
        echo "[DRY RUN] ${cmd_args[*]}"
        return 0
    fi

    if ${VERBOSE}; then
        print_info "Command: ${cmd_args[*]}"
    fi

    if "${cmd_args[@]}"; then
        if ${JSON_OUTPUT}; then
            local size
            size=$(stat -c%s "${output}" 2>/dev/null || stat -f%z "${output}" 2>/dev/null)
            printf '{"command":"ocr","status":"pass","input":"%s","output":"%s","size":%d}\n' "${input}" "${output}" "${size}"
        else
            print_pass "OCR complete: ${output}"
        fi
    else
        if ${JSON_OUTPUT}; then
            json_result "ocr" "fail" "OCR failed"
        else
            print_fail "OCR failed"
        fi
        return 1
    fi
}

ocr_with_tesseract() {
    local input="$1"
    local output="$2"

    if ${VERBOSE}; then
        print_info "Using tesseract for OCR (basic mode)"
        print_info "Note: For better results, install ocrmypdf"
    fi

    # This is a basic implementation - extract images and OCR them
    # For production use, ocrmypdf is strongly recommended

    # Check for pdftoppm (to convert PDF to images)
    if ! command -v pdftoppm &>/dev/null; then
        print_fail "pdftoppm required for tesseract OCR"
        print_info "Install with: sudo apt install poppler-utils"
        return 2
    fi

    local temp_dir
    temp_dir=$(mktemp -d)

    if ${VERBOSE}; then
        print_info "Converting PDF to images..."
    fi

    # Convert PDF pages to images
    pdftoppm -png "${input}" "${temp_dir}/page" || {
        rm -rf "${temp_dir}"
        print_fail "Failed to convert PDF to images"
        return 1
    }

    # OCR each page
    local text_files=()
    for img in "${temp_dir}"/page-*.png; do
        if [[ -f "${img}" ]]; then
            local base="${img%.png}"
            if tesseract "${img}" "${base}" -l "${LANGUAGE}" 2>/dev/null; then
                text_files+=("${base}.txt")
            fi
        fi
    done

    # Combine text files
    if [[ ${#text_files[@]} -gt 0 ]]; then
        cat "${text_files[@]}" >"${output%.pdf}.txt"
        if ${JSON_OUTPUT}; then
            json_result "ocr" "pass" "Text extracted to ${output%.pdf}.txt"
        else
            print_pass "Text extracted to: ${output%.pdf}.txt"
            print_info "Note: For searchable PDF output, install ocrmypdf"
        fi
    else
        print_fail "OCR produced no output"
        rm -rf "${temp_dir}"
        return 1
    fi

    rm -rf "${temp_dir}"
}

# =============================================================================
# Batch Operations
# =============================================================================

batch_process() {
    local command="$1"
    shift

    local files=()
    local output_dir=""

    # Parse batch options
    while [[ $# -gt 0 ]]; do
        case "$1" in
        --output-dir)
            output_dir="$2"
            shift 2
            ;;
        -*)
            shift
            ;;
        *)
            files+=("$1")
            shift
            ;;
        esac
    done

    if [[ ${#files[@]} -eq 0 ]]; then
        print_fail "No input files specified"
        return 1
    fi

    if [[ -n "${output_dir}" ]]; then
        mkdir -p "${output_dir}"
    fi

    local processed=0
    local failed=0

    for file in "${files[@]}"; do
        if [[ ! -f "${file}" ]]; then
            print_skip "File not found: ${file}"
            continue
        fi

        local basename
        basename=$(basename "${file}" .pdf)

        case "${command}" in
        extract)
            local output="${output_dir:-.}/${basename}.txt"
            OUTPUT_FILE="${output}"
            if extract_text "${file}"; then
                ((processed++))
            else
                ((failed++))
            fi
            OUTPUT_FILE=""
            ;;
        info)
            if get_info "${file}"; then
                ((processed++))
            else
                ((failed++))
            fi
            echo ""
            ;;
        ocr)
            local output="${output_dir:-.}/${basename}_ocr.pdf"
            if do_ocr "${file}" "${output}"; then
                ((processed++))
            else
                ((failed++))
            fi
            ;;
        *)
            print_fail "Unknown batch command: ${command}"
            return 2
            ;;
        esac
    done

    echo ""
    if ${JSON_OUTPUT}; then
        printf '{"command":"batch","subcommand":"%s","processed":%d,"failed":%d}\n' "${command}" "${processed}" "${failed}"
    else
        print_info "Processed: ${processed}, Failed: ${failed}"
    fi

    [[ ${failed} -eq 0 ]]
}

# =============================================================================
# Version Info
# =============================================================================

show_version() {
    echo "pdf_tools.sh - PDF Operations Utility"
    echo ""
    echo "Available tools:"

    if ${HAS_PDFTOTEXT}; then
        local version
        version=$(pdftotext -v 2>&1 | head -1 || echo "unknown")
        echo "  pdftotext: ${version}"
    else
        echo "  pdftotext: not installed"
    fi

    if ${HAS_PDFINFO}; then
        local version
        version=$(pdfinfo -v 2>&1 | head -1 || echo "unknown")
        echo "  pdfinfo: ${version}"
    else
        echo "  pdfinfo: not installed"
    fi

    if ${HAS_OCRMYPDF}; then
        local version
        version=$(ocrmypdf --version 2>/dev/null | head -1 || echo "unknown")
        echo "  ocrmypdf: ${version}"
    else
        echo "  ocrmypdf: not installed"
    fi

    if ${HAS_TESSERACT}; then
        local version
        version=$(tesseract --version 2>&1 | head -1 || echo "unknown")
        echo "  tesseract: ${version}"
    else
        echo "  tesseract: not installed"
    fi

    if ${HAS_EXIFTOOL}; then
        local version
        version=$(exiftool -ver 2>/dev/null || echo "unknown")
        echo "  exiftool: ${version}"
    else
        echo "  exiftool: not installed"
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

    # Handle version
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
        --layout)
            LAYOUT_MODE="layout"
            shift
            ;;
        --raw)
            LAYOUT_MODE="raw"
            shift
            ;;
        --table)
            LAYOUT_MODE="table"
            shift
            ;;
        -f | --first)
            PAGE_FIRST="$2"
            shift 2
            ;;
        -l | --last)
            PAGE_LAST="$2"
            shift 2
            ;;
        -o | --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --lang)
            LANGUAGE="$2"
            shift 2
            ;;
        --force-ocr)
            FORCE_OCR=true
            shift
            ;;
        --skip-text)
            FORCE_OCR=false
            shift
            ;;
        --deskew)
            DESKEW=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            positional+=("$1")
            shift
            ;;
        esac
    done

    # Restore positional
    set -- "${positional[@]}"

    case "${command}" in
    extract)
        if [[ $# -lt 1 ]]; then
            print_fail "Usage: pdf_tools.sh extract <input.pdf>"
            exit 2
        fi
        extract_text "$1"
        ;;
    info)
        if [[ $# -lt 1 ]]; then
            print_fail "Usage: pdf_tools.sh info <input.pdf>"
            exit 2
        fi
        get_info "$1"
        ;;
    pages)
        if [[ $# -lt 1 ]]; then
            print_fail "Usage: pdf_tools.sh pages <input.pdf>"
            exit 2
        fi
        get_pages "$1"
        ;;
    ocr)
        if [[ $# -lt 1 ]]; then
            print_fail "Usage: pdf_tools.sh ocr <input.pdf> [output.pdf]"
            exit 2
        fi
        do_ocr "$1" "${2:-}"
        ;;
    batch)
        if [[ $# -lt 2 ]]; then
            print_fail "Usage: pdf_tools.sh batch <command> [options] <files...>"
            exit 2
        fi
        batch_process "$@"
        ;;
    version | --version)
        show_version
        ;;
    *)
        print_fail "Unknown command: ${command}"
        echo "Run 'pdf_tools.sh --help' for usage."
        exit 2
        ;;
    esac
}

main "$@"
