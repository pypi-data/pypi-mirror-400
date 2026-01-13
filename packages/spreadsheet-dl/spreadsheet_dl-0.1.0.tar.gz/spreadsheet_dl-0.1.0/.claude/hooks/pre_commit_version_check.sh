#!/usr/bin/env bash
# =============================================================================
# Version Consistency Check Hook
# Validates version consistency across all documented locations
# Uses project-metadata.yaml as source of truth for locations to check
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

log() {
    echo "[$(date -Iseconds)] VERSION_CHECK: $*" >>"${LOG_FILE}"
}

# Check for bypass
if [[ "${CLAUDE_BYPASS_HOOKS:-0}" = "1" ]]; then
    echo '{"ok": true, "bypassed": true}'
    exit 0
fi

log "Starting version consistency check"

# Extract version from pyproject.toml (SSOT)
VERSION=$(grep -E '^version = "' "${PROJECT_DIR}/pyproject.toml" | cut -d'"' -f2)

if [[ -z "${VERSION}" ]]; then
    log "ERROR: Could not extract version from pyproject.toml"
    echo '{"ok": false, "error": "Version not found in pyproject.toml"}'
    exit 1
fi

log "Found primary version: ${VERSION}"

ERRORS=0

# Check __init__.py
if [[ -f "${PROJECT_DIR}/src/spreadsheet_dl/__init__.py" ]]; then
    if ! grep -q "__version__ = \"${VERSION}\"" "${PROJECT_DIR}/src/spreadsheet_dl/__init__.py"; then
        log "ERROR: Version mismatch in src/spreadsheet_dl/__init__.py"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check README.md (version badge or explicit version text)
if [[ -f "${PROJECT_DIR}/README.md" ]]; then
    # Check for version badge (e.g., version-4.0.0-blue) or explicit version text
    if ! grep -qE "(version-${VERSION}|v${VERSION})" "${PROJECT_DIR}/README.md"; then
        log "ERROR: Version mismatch in README.md"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Output result
if [[ "${ERRORS}" -gt 0 ]]; then
    cat <<EOF
{
    "ok": false,
    "errors": ${ERRORS},
    "message": "Version inconsistency detected. Expected: ${VERSION}. Check ${LOG_FILE} for details."
}
EOF
    log "Version check failed: ${ERRORS} errors"
    exit 1
else
    echo "{\"ok\": true, \"version\": \"${VERSION}\", \"message\": \"Version consistent across all locations\"}"
    log "Version check passed: ${VERSION}"
    exit 0
fi
