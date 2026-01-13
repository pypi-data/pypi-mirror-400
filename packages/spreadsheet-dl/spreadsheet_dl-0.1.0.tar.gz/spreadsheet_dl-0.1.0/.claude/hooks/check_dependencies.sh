#!/usr/bin/env bash
# =============================================================================
# Hook Dependencies Checker
# Validates that all required dependencies for hook execution are available
# Run this FIRST before any other hooks to ensure environment is ready
#
# Version: 1.0.0
# Created: 2025-12-25
# =============================================================================

set -euo pipefail

# Resolve to absolute path from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-${REPO_ROOT}}"
LOG_FILE="${PROJECT_DIR}/.claude/hooks/hook.log"

# Ensure log directory exists
mkdir -p "$(dirname "${LOG_FILE}")"

log() {
    echo "[$(date -Iseconds)] CHECK_DEPS: $*" >>"${LOG_FILE}"
}

log_error() {
    echo "[$(date -Iseconds)] CHECK_DEPS_ERROR: $*" >>"${LOG_FILE}"
    echo "ERROR: $*" >&2
}

# =============================================================================
# Dependency Definitions
# =============================================================================

# Required shell commands
REQUIRED_SHELL_COMMANDS=(
    "bash"
    "find"
    "grep"
    "cut"
    "wc"
    "date"
    "stat"
    "mkdir"
    "mv"
    "rm"
    "gzip"
    "du"
)

# Optional shell commands (warn if missing, don't fail)
OPTIONAL_SHELL_COMMANDS=(
    "jq"
    "numfmt"
    "md5sum"
)

# Required Python modules (checked via uv or python3)
REQUIRED_PYTHON_MODULES=(
    "json"
    "pathlib"
    "hashlib"
    "re"
    "sys"
    "os"
)

# Optional Python modules (warn if missing)
OPTIONAL_PYTHON_MODULES=(
    "yaml"
)

# =============================================================================
# Check Functions
# =============================================================================

check_shell_command() {
    local cmd="$1"
    local required="${2:-true}"

    if command -v "${cmd}" &>/dev/null; then
        return 0
    else
        if [[ "${required}" = "true" ]]; then
            log_error "Required command '${cmd}' not found"
            return 1
        else
            log "Optional command '${cmd}' not found - some features may be limited"
            return 0
        fi
    fi
}

check_python_module() {
    local module="$1"
    local required="${2:-true}"

    # Try uv first, fall back to python3
    if command -v uv &>/dev/null; then
        if uv run python3 -c "import ${module}" 2>/dev/null; then
            return 0
        fi
    elif python3 -c "import ${module}" 2>/dev/null; then
        return 0
    fi

    if [[ "${required}" = "true" ]]; then
        log_error "Required Python module '${module}' not available"
        return 1
    else
        log "Optional Python module '${module}' not available - install with: uv add ${module}"
        return 0
    fi
}

check_python_available() {
    if command -v uv &>/dev/null; then
        if uv run python3 --version &>/dev/null; then
            return 0
        fi
    elif command -v python3 &>/dev/null; then
        return 0
    fi

    log_error "Python 3 not available. Install Python or uv."
    return 1
}

# =============================================================================
# Main Validation
# =============================================================================

ERRORS=0
WARNINGS=0

log "Starting dependency check..."

# Check Python availability first
if ! check_python_available; then
    ERRORS=$((ERRORS + 1))
fi

# Check required shell commands
for cmd in "${REQUIRED_SHELL_COMMANDS[@]}"; do
    if ! check_shell_command "${cmd}" "true"; then
        ERRORS=$((ERRORS + 1))
    fi
done

# Check optional shell commands
for cmd in "${OPTIONAL_SHELL_COMMANDS[@]}"; do
    if ! check_shell_command "${cmd}" "false"; then
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check required Python modules
for module in "${REQUIRED_PYTHON_MODULES[@]}"; do
    if ! check_python_module "${module}" "true"; then
        ERRORS=$((ERRORS + 1))
    fi
done

# Check optional Python modules
for module in "${OPTIONAL_PYTHON_MODULES[@]}"; do
    if ! check_python_module "${module}" "false"; then
        WARNINGS=$((WARNINGS + 1))
    fi
done

# =============================================================================
# Output Results
# =============================================================================

log "Dependency check complete: ${ERRORS} errors, ${WARNINGS} warnings"

if [[ "${ERRORS}" -gt 0 ]]; then
    cat <<EOF
{
    "ok": false,
    "errors": ${ERRORS},
    "warnings": ${WARNINGS},
    "message": "Missing required dependencies. Check ${LOG_FILE} for details."
}
EOF
    exit 1
fi

if [[ "${WARNINGS}" -gt 0 ]]; then
    cat <<EOF
{
    "ok": true,
    "errors": 0,
    "warnings": ${WARNINGS},
    "message": "All required dependencies available. ${WARNINGS} optional dependencies missing."
}
EOF
else
    echo '{"ok": true, "errors": 0, "warnings": 0, "message": "All dependencies satisfied"}'
fi

exit 0
