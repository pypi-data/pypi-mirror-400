#!/usr/bin/env bash
# Restore Checkpoint Script
# Loads a checkpoint after compaction to resume a long-running task
#
# Usage:
#   restore_checkpoint.sh <task-id> [--output-format json|text]
#   restore_checkpoint.sh --latest
#
# Output:
#   Prints checkpoint state for Claude to read and resume the task

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CHECKPOINT_DIR="${PROJECT_DIR}/.coordination/checkpoints"
LOG_FILE="${PROJECT_DIR}/.claude/hooks/checkpoints.log"

# ============================================================
# Utility Functions
# ============================================================

log() {
    echo "[$(date -Iseconds)] RESTORE: $*" >>"${LOG_FILE}"
}

get_iso_timestamp() {
    date -Iseconds
}

# Find the most recent checkpoint
find_latest_checkpoint() {
    local latest=""
    local latest_ts=0

    for checkpoint in "${CHECKPOINT_DIR}"/*/; do
        if [[ -d "${checkpoint}" ]] && [[ -f "${checkpoint}/manifest.json" ]]; then
            local ts
            ts=$(jq -r '.created_timestamp // 0' "${checkpoint}/manifest.json" 2>/dev/null || echo 0)
            if [[ "${ts}" -gt "${latest_ts}" ]]; then
                latest_ts=${ts}
                latest=$(basename "${checkpoint}")
            fi
        fi
    done

    echo "${latest}"
}

# ============================================================
# Restore Functions
# ============================================================

restore_json() {
    local task_id="$1"
    local checkpoint_path="${CHECKPOINT_DIR}/${task_id}"

    local manifest state context_summary
    manifest=$(cat "${checkpoint_path}/manifest.json" 2>/dev/null || echo '{}')
    state=$(cat "${checkpoint_path}/state.json" 2>/dev/null || echo '{}')

    # Get first 100 lines of context
    if [[ -f "${checkpoint_path}/context.md" ]]; then
        context_summary=$(head -100 "${checkpoint_path}/context.md" | jq -Rs . 2>/dev/null || echo '""')
    else
        context_summary='""'
    fi

    # List artifacts
    local artifacts='[]'
    if [[ -d "${checkpoint_path}/artifacts" ]]; then
        artifacts=$(find "${checkpoint_path}/artifacts" -type f -exec basename {} \; 2>/dev/null | jq -R . | jq -s . || echo '[]')
    fi

    cat <<EOF
{
    "restored": true,
    "task_id": "${task_id}",
    "restored_at": "$(get_iso_timestamp)",
    "checkpoint_path": "${checkpoint_path}",
    "manifest": ${manifest},
    "state": ${state},
    "context_summary": ${context_summary},
    "artifacts": ${artifacts},
    "instructions": "Use this checkpoint state to resume the task. Check state.next_steps for pending actions."
}
EOF
}

restore_text() {
    local task_id="$1"
    local checkpoint_path="${CHECKPOINT_DIR}/${task_id}"

    cat <<EOF
================================================================================
CHECKPOINT RESTORED: ${task_id}
================================================================================
Restored at: $(get_iso_timestamp)
Checkpoint path: ${checkpoint_path}

--------------------------------------------------------------------------------
MANIFEST
--------------------------------------------------------------------------------
EOF

    if [[ -f "${checkpoint_path}/manifest.json" ]]; then
        jq '.' "${checkpoint_path}/manifest.json" 2>/dev/null || cat "${checkpoint_path}/manifest.json"
    else
        echo "No manifest found"
    fi

    cat <<EOF

--------------------------------------------------------------------------------
STATE
--------------------------------------------------------------------------------
EOF

    if [[ -f "${checkpoint_path}/state.json" ]]; then
        jq '.' "${checkpoint_path}/state.json" 2>/dev/null || cat "${checkpoint_path}/state.json"
    else
        echo "No state found"
    fi

    cat <<EOF

--------------------------------------------------------------------------------
CONTEXT
--------------------------------------------------------------------------------
EOF

    if [[ -f "${checkpoint_path}/context.md" ]]; then
        cat "${checkpoint_path}/context.md"
    else
        echo "No context document found"
    fi

    cat <<EOF

--------------------------------------------------------------------------------
ARTIFACTS
--------------------------------------------------------------------------------
EOF

    if [[ -d "${checkpoint_path}/artifacts" ]]; then
        local artifact_count
        artifact_count=$(find "${checkpoint_path}/artifacts" -type f 2>/dev/null | wc -l)
        echo "Found ${artifact_count} artifact(s):"
        find "${checkpoint_path}/artifacts" -type f -exec ls -lh {} \; 2>/dev/null || true
    else
        echo "No artifacts directory"
    fi

    cat <<EOF

================================================================================
RESUMPTION INSTRUCTIONS
================================================================================
1. Review the STATE section above for current progress
2. Check 'next_steps' for pending actions
3. Review 'key_decisions' for context on choices made
4. Check 'open_questions' for unresolved items
5. Artifacts in: ${checkpoint_path}/artifacts/

To update checkpoint: .claude/hooks/checkpoint_state.sh update ${task_id} <key> <value>
To delete checkpoint: .claude/hooks/checkpoint_state.sh delete ${task_id}
================================================================================
EOF
}

# ============================================================
# Main
# ============================================================

OUTPUT_FORMAT="text"
TASK_ID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
    --latest)
        TASK_ID=$(find_latest_checkpoint)
        if [[ -z "${TASK_ID}" ]]; then
            echo "Error: No checkpoints found" >&2
            exit 1
        fi
        shift
        ;;
    --output-format)
        OUTPUT_FORMAT="${2:-text}"
        shift 2
        ;;
    --json)
        OUTPUT_FORMAT="json"
        shift
        ;;
    --text)
        OUTPUT_FORMAT="text"
        shift
        ;;
    --help | -h)
        cat <<EOF
Restore Checkpoint

Usage:
  restore_checkpoint.sh <task-id> [options]
  restore_checkpoint.sh --latest [options]

Options:
  --latest              Restore the most recent checkpoint
  --output-format FMT   Output format: json or text (default: text)
  --json                Shorthand for --output-format json
  --text                Shorthand for --output-format text
  --help, -h            Show this help

Examples:
  # Restore a specific checkpoint
  restore_checkpoint.sh validation-task

  # Restore the latest checkpoint
  restore_checkpoint.sh --latest

  # Get JSON output for programmatic use
  restore_checkpoint.sh validation-task --json

EOF
        exit 0
        ;;
    -*)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
    *)
        TASK_ID="$1"
        shift
        ;;
    esac
done

# Validate task ID
if [[ -z "${TASK_ID}" ]]; then
    echo "Error: task-id required" >&2
    echo "Usage: restore_checkpoint.sh <task-id>" >&2
    echo "       restore_checkpoint.sh --latest" >&2
    exit 1
fi

CHECKPOINT_PATH="${CHECKPOINT_DIR}/${TASK_ID}"

if [[ ! -d "${CHECKPOINT_PATH}" ]]; then
    echo "Error: Checkpoint '${TASK_ID}' not found" >&2
    echo "Available checkpoints:" >&2
    ls -1 "${CHECKPOINT_DIR}" 2>/dev/null || echo "  (none)" >&2
    exit 1
fi

# Log restoration
log "Restoring checkpoint: ${TASK_ID} (format: ${OUTPUT_FORMAT})"

# Update manifest status
if [[ -f "${CHECKPOINT_PATH}/manifest.json" ]]; then
    tmp_file=$(mktemp)
    if jq --arg ts "$(get_iso_timestamp)" '.status = "restored" | .last_restored = ${ts}' "${CHECKPOINT_PATH}/manifest.json" >"${tmp_file}" 2>/dev/null; then
        mv "${tmp_file}" "${CHECKPOINT_PATH}/manifest.json" || true
    else
        rm -f "${tmp_file}"
    fi
fi

# Output based on format
case "${OUTPUT_FORMAT}" in
json)
    restore_json "${TASK_ID}"
    ;;
text)
    restore_text "${TASK_ID}"
    ;;
*)
    echo "Unknown format: ${OUTPUT_FORMAT}" >&2
    exit 1
    ;;
esac
