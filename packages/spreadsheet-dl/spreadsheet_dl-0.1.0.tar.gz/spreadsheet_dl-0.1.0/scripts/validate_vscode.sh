#!/usr/bin/env bash
# =============================================================================
# validate_vscode.sh - VS Code Configuration Validation with Schema Checking
# =============================================================================
# Usage: ./scripts/validate_vscode.sh [-h|--help] [-v|--verbose] [--skip-schema]
# =============================================================================
# Validates .vscode/ configuration files:
#   1. JSONC syntax validation (Python-based comment stripping)
#   2. JSON Schema validation (check-jsonschema against VS Code schema)
#   3. Extension cross-reference (installed vs recommended)
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/validate_vscode.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common library if available (for consistent output formatting)
if [[ -f "${SCRIPT_DIR}/lib/common.sh" ]]; then
    source "${SCRIPT_DIR}/lib/common.sh"
else
    # Fallback colors if common.sh not available
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    DIM='\033[2m'
    NC='\033[0m'
fi

# Configuration
VERBOSE=false
SKIP_SCHEMA=false

# VS Code settings schema URL (official Microsoft schema)
VSCODE_SETTINGS_SCHEMA="https://raw.githubusercontent.com/wraith13/vscode-schemas/master/en/latest/schemas/settings/machine.json"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        echo "Usage: $0 [-h|--help] [-v|--verbose] [--skip-schema]"
        echo ""
        echo "VS Code configuration validation"
        echo ""
        echo "Validates .vscode/ configuration files for correctness:"
        echo "  1. JSONC syntax (validates JSON with comments)"
        echo "  2. JSON Schema (validates against VS Code settings schema)"
        echo "  3. Extensions (cross-references installed vs recommended)"
        echo ""
        echo "Options:"
        echo "  -h, --help     Show this help message"
        echo "  -v, --verbose  Show detailed output including validation errors"
        echo "  --skip-schema  Skip JSON schema validation"
        echo ""
        echo "Schema Validation:"
        echo "  Requires check-jsonschema tool. Install with:"
        echo "    uv pip install check-jsonschema"
        echo "  Or: pip install check-jsonschema"
        echo ""
        echo "What Schema Validation Catches:"
        echo "  - Unknown/misspelled setting keys"
        echo "  - Invalid value types (string vs boolean, etc.)"
        echo "  - Deprecated settings"
        echo "  - Missing required fields"
        echo ""
        echo "Exit Codes:"
        echo "  0  All validations passed"
        echo "  1  Validation errors found"
        echo "  2  Script/argument error"
        exit 0
        ;;
    -v | --verbose)
        VERBOSE=true
        shift
        ;;
    --skip-schema)
        SKIP_SCHEMA=true
        shift
        ;;
    *)
        echo "Unknown option: $1" >&2
        echo "Try '$0 --help' for usage information" >&2
        exit 2
        ;;
    esac
done

# Find workspace root dynamically
if WORKSPACE_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
    :
else
    WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

VSCODE_DIR="${WORKSPACE_ROOT}/.vscode"

echo -e "${BLUE}VS Code Configuration Validation${NC}"
echo -e "   Workspace: ${WORKSPACE_ROOT}"
echo ""

ERRORS=0
WARNINGS=0

# ============================================================================
# 1. Check .vscode directory exists
# ============================================================================
if [[ ! -d "${VSCODE_DIR}" ]]; then
    echo -e "${RED}x .vscode/ directory not found${NC}"
    exit 1
fi

# ============================================================================
# 2. Validate JSONC files (basic syntax check using Python's json module)
# ============================================================================
echo -e "${BLUE}[1/3]${NC} Validating JSONC syntax..."

validate_jsonc() {
    local file="$1"
    local filename
    filename=$(basename "${file}")

    if [[ ! -f "${file}" ]]; then
        echo -e "   ${YELLOW}o${NC} ${filename} (not present)"
        return 0
    fi

    # Use Python to validate (strips JSONC comments properly)
    if python3 -c "
import json, re, sys

def strip_jsonc_comments(content):
    # Remove single-line comments (but preserve URLs)
    lines = []
    for line in content.split('\n'):
        if '//' in line:
            idx = line.find('//')
            while idx != -1:
                # Check if part of URL (http://, https://)
                if idx > 0 and line[idx-1] == ':':
                    idx = line.find('//', idx + 2)
                else:
                    line = line[:idx]
                    break
        lines.append(line)
    content = '\n'.join(lines)
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    return content

try:
    content = open('${file}').read()
    clean = strip_jsonc_comments(content)
    json.loads(clean)
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
        echo -e "   ${GREEN}+${NC} ${filename}"
        return 0
    else
        echo -e "   ${RED}x${NC} ${filename} (invalid JSONC)"
        return 1
    fi
}

# Validate each config file
for file in settings.json extensions.json tasks.json launch.json; do
    if ! validate_jsonc "${VSCODE_DIR}/${file}"; then
        ((ERRORS++))
    fi
done
echo ""

# ============================================================================
# 3. JSON Schema Validation (settings.json against VS Code schema)
# ============================================================================
echo -e "${BLUE}[2/3]${NC} Validating settings.json against schema..."

validate_schema() {
    local file="$1"
    local filename
    filename=$(basename "${file}")

    if [[ ! -f "${file}" ]]; then
        echo -e "   ${YELLOW}o${NC} ${filename} (not present - skipping schema validation)"
        return 0
    fi

    # Check if check-jsonschema is installed
    if ! command -v check-jsonschema &>/dev/null; then
        echo -e "   ${YELLOW}!${NC} check-jsonschema not installed"
        echo -e "   ${DIM}   Install: uv pip install check-jsonschema${NC}"
        echo -e "   ${DIM}   Skipping schema validation${NC}"
        ((WARNINGS++))
        return 0
    fi

    # Create a temp file with comments stripped (check-jsonschema needs pure JSON)
    local temp_file
    temp_file=$(mktemp)
    trap 'rm -f "${temp_file}"' EXIT

    # Strip JSONC comments using Python
    if ! python3 -c "
import json, re, sys

def strip_jsonc_comments(content):
    lines = []
    for line in content.split('\n'):
        if '//' in line:
            idx = line.find('//')
            while idx != -1:
                if idx > 0 and line[idx-1] == ':':
                    idx = line.find('//', idx + 2)
                else:
                    line = line[:idx]
                    break
        lines.append(line)
    content = '\n'.join(lines)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    return content

try:
    with open('${file}', 'r') as f:
        content = f.read()
    clean = strip_jsonc_comments(content)
    data = json.loads(clean)
    with open('${temp_file}', 'w') as f:
        json.dump(data, f)
    sys.exit(0)
except Exception as e:
    print(f'Error preprocessing: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1; then
        echo -e "   ${RED}x${NC} Failed to preprocess ${filename} for schema validation"
        return 1
    fi

    # Run schema validation
    # Note: We use a community-maintained schema that's more lenient than the strict VS Code schema
    # This helps avoid false positives from extension-contributed settings
    if ${VERBOSE}; then
        if check-jsonschema --schemafile "${VSCODE_SETTINGS_SCHEMA}" "${temp_file}" 2>&1; then
            echo -e "   ${GREEN}+${NC} ${filename} (schema valid)"
            return 0
        else
            echo -e "   ${RED}x${NC} ${filename} (schema validation failed)"
            return 1
        fi
    else
        local output
        if output=$(check-jsonschema --schemafile "${VSCODE_SETTINGS_SCHEMA}" "${temp_file}" 2>&1); then
            echo -e "   ${GREEN}+${NC} ${filename} (schema valid)"
            return 0
        else
            echo -e "   ${RED}x${NC} ${filename} (schema validation failed)"
            echo -e "   ${DIM}   Run with -v for details${NC}"
            return 1
        fi
    fi
}

if [[ "${SKIP_SCHEMA}" = true ]]; then
    echo -e "   ${YELLOW}o${NC} Schema validation skipped (--skip-schema)"
else
    if ! validate_schema "${VSCODE_DIR}/settings.json"; then
        ((ERRORS++))
    fi
fi
echo ""

# ============================================================================
# 4. Check extensions (using our smart script)
# ============================================================================
echo -e "${BLUE}[3/3]${NC} Checking extensions..."

if [[ -f "${SCRIPT_DIR}/check_vscode_extensions.py" ]]; then
    if python3 "${SCRIPT_DIR}/check_vscode_extensions.py"; then
        echo ""
    else
        ((ERRORS++))
        echo ""
    fi
else
    echo -e "   ${YELLOW}!${NC} Extension checker not found (skipping)"
    echo ""
fi

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}------------------------------------------------------------------------${NC}"
if [[ ${ERRORS} -eq 0 ]] && [[ ${WARNINGS} -eq 0 ]]; then
    echo -e "${GREEN}All VS Code validations passed${NC}"
    exit 0
elif [[ ${ERRORS} -eq 0 ]]; then
    echo -e "${YELLOW}Passed with ${WARNINGS} warning(s)${NC}"
    echo -e "${DIM}Install missing tools for full validation${NC}"
    exit 0
else
    echo -e "${RED}Found ${ERRORS} validation error(s)${NC}"
    exit 1
fi
