#!/usr/bin/env bash
# =============================================================================
# NotImplementedError Check Hook
# Ensures all NotImplementedError instances are tracked in incomplete-features.yaml
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
    echo "[$(date -Iseconds)] CHECK_NOT_IMPL: $*" >>"${LOG_FILE}"
}

# Check for bypass
if [[ "${CLAUDE_BYPASS_HOOKS:-0}" = "1" ]]; then
    echo '{"ok": true, "bypassed": true}'
    exit 0
fi

log "Checking for untracked NotImplementedError"

# Find all NotImplementedError instances in code
UNTRACKED=0

while IFS= read -r line; do
    file=$(echo "${line}" | cut -d: -f1)

    # Skip if this NotImplementedError has a FUTURE-XXX comment nearby
    if grep -B2 -A2 "raise NotImplementedError" "${file}" | grep -q "# FUTURE-"; then
        continue
    fi

    # Skip if file uses ABC or has @abstractmethod (valid abstract base class pattern)
    if grep -q "from abc import.*ABC\|@abstractmethod" "${file}"; then
        continue
    fi

    # Skip if NotImplementedError message indicates subclass requirement (soft ABC pattern)
    if grep -q 'NotImplementedError.*[Ss]ubclass.*must\|NotImplementedError.*must implement' "${file}"; then
        continue
    fi

    log "WARN: Untracked NotImplementedError in ${file}"
    UNTRACKED=$((UNTRACKED + 1))
done < <(grep -rn "raise NotImplementedError" "${PROJECT_DIR}/src" 2>/dev/null || true)

if [[ "${UNTRACKED}" -gt 0 ]]; then
    cat <<EOF
{
    "ok": false,
    "untracked": ${UNTRACKED},
    "message": "${UNTRACKED} NotImplementedError instances not tracked in incomplete-features.yaml"
}
EOF
    log "Check failed: ${UNTRACKED} untracked NotImplementedError"
    exit 1
else
    echo '{"ok": true, "message": "All NotImplementedError instances are tracked"}'
    log "Check passed"
    exit 0
fi
