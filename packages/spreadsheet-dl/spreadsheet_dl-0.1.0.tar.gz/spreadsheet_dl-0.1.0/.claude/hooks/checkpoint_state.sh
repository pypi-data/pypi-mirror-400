#!/usr/bin/env bash
# State Checkpointing Script
# Creates checkpoints for long-running tasks to enable recovery after compaction
#
# Usage:
#   checkpoint_state.sh create <task-id> [description]
#   checkpoint_state.sh list
#   checkpoint_state.sh show <task-id>
#   checkpoint_state.sh delete <task-id>
#
# Checkpoint Format:
#   .coordination/checkpoints/<task-id>/
#     - manifest.json      - Checkpoint metadata
#     - state.json         - Task state (progress, results, next steps)
#     - context.md         - Human-readable context summary
#     - artifacts/         - Referenced files (copied or linked)

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
CHECKPOINT_DIR="${PROJECT_DIR}/.coordination/checkpoints"
LOG_FILE="${PROJECT_DIR}/.claude/hooks/checkpoints.log"

# Ensure directories exist
mkdir -p "${CHECKPOINT_DIR}"
mkdir -p "$(dirname "${LOG_FILE}")"

# ============================================================
# Utility Functions
# ============================================================

log() {
    echo "[$(date -Iseconds)] CHECKPOINT: $*" >>"${LOG_FILE}"
}

get_iso_timestamp() {
    date -Iseconds
}

get_timestamp() {
    date +%s
}

generate_task_id() {
    date +%Y%m%d-%H%M%S
}

# ============================================================
# Commands
# ============================================================

cmd_create() {
    local task_id="${1:-$(generate_task_id)}"
    local description="${2:-Checkpoint created at $(get_iso_timestamp)}"
    local checkpoint_path="${CHECKPOINT_DIR}/${task_id}"

    if [[ -d "${checkpoint_path}" ]]; then
        echo "Error: Checkpoint '${task_id}' already exists" >&2
        echo "Use 'checkpoint_state.sh delete ${task_id}' to remove it first" >&2
        exit 1
    fi

    mkdir -p "${checkpoint_path}/artifacts"

    # Create manifest
    cat >"${checkpoint_path}/manifest.json" <<EOF
{
    "task_id": "${task_id}",
    "created_at": "$(get_iso_timestamp)",
    "created_timestamp": $(get_timestamp),
    "description": "${description}",
    "version": "1.0",
    "status": "active"
}
EOF

    # Create empty state file (to be populated by user/agent)
    cat >"${checkpoint_path}/state.json" <<EOF
{
    "task_id": "${task_id}",
    "phase": "initial",
    "progress": {
        "current_step": 0,
        "total_steps": 0,
        "percentage": 0
    },
    "results": {},
    "next_steps": [],
    "key_decisions": [],
    "open_questions": [],
    "last_updated": "$(get_iso_timestamp)"
}
EOF

    # Create context template
    cat >"${checkpoint_path}/context.md" <<EOF
# Checkpoint: ${task_id}

**Created:** $(get_iso_timestamp)
**Description:** ${description}

## Current State

_Add current task state here_

## Progress

- [ ] Step 1
- [ ] Step 2

## Key Decisions

_Document important decisions made_

## Next Steps

1. _Next action to take_

## Artifacts

_List any important files or outputs_

## Notes

_Additional context for resumption_
EOF

    log "Created checkpoint: ${task_id}"
    echo "Checkpoint created: ${checkpoint_path}"
    echo ""
    echo "Files created:"
    echo "  - manifest.json (checkpoint metadata)"
    echo "  - state.json (task state - edit to save progress)"
    echo "  - context.md (human-readable summary)"
    echo "  - artifacts/ (place important files here)"
    echo ""
    echo "To update state: edit ${checkpoint_path}/state.json"
    echo "To restore: .claude/hooks/restore_checkpoint.sh ${task_id}"
}

cmd_list() {
    echo "Available Checkpoints:"
    echo "======================"

    if [[ ! -d "${CHECKPOINT_DIR}" ]] || [[ -z "$(ls -A "${CHECKPOINT_DIR}" 2>/dev/null)" ]]; then
        echo "No checkpoints found."
        return 0
    fi

    for checkpoint in "${CHECKPOINT_DIR}"/*/; do
        if [[ -d "${checkpoint}" ]]; then
            local task_id
            task_id=$(basename "${checkpoint}")
            local manifest="${checkpoint}/manifest.json"

            if [[ -f "${manifest}" ]]; then
                local created_at description status
                created_at=$(jq -r '.created_at // "unknown"' "${manifest}" 2>/dev/null || echo "unknown")
                description=$(jq -r '.description // "No description"' "${manifest}" 2>/dev/null || echo "No description")
                status=$(jq -r '.status // "unknown"' "${manifest}" 2>/dev/null || echo "unknown")

                printf "%-20s [%s] %s\n" "${task_id}" "${status}" "${created_at}"
                printf "                     %s\n" "${description}"
            else
                printf "%-20s [corrupted] Missing manifest\n" "${task_id}"
            fi
        fi
    done
}

cmd_show() {
    local task_id="$1"
    local checkpoint_path="${CHECKPOINT_DIR}/${task_id}"

    if [[ ! -d "${checkpoint_path}" ]]; then
        echo "Error: Checkpoint '${task_id}' not found" >&2
        exit 1
    fi

    echo "Checkpoint: ${task_id}"
    echo "========================"
    echo ""

    if [[ -f "${checkpoint_path}/manifest.json" ]]; then
        echo "Manifest:"
        jq '.' "${checkpoint_path}/manifest.json" 2>/dev/null || cat "${checkpoint_path}/manifest.json"
        echo ""
    fi

    if [[ -f "${checkpoint_path}/state.json" ]]; then
        echo "State:"
        jq '.' "${checkpoint_path}/state.json" 2>/dev/null || cat "${checkpoint_path}/state.json"
        echo ""
    fi

    if [[ -f "${checkpoint_path}/context.md" ]]; then
        echo "Context Summary:"
        head -50 "${checkpoint_path}/context.md"
        echo ""
    fi

    if [[ -d "${checkpoint_path}/artifacts" ]]; then
        local artifact_count
        artifact_count=$(find "${checkpoint_path}/artifacts" -type f 2>/dev/null | wc -l)
        echo "Artifacts: ${artifact_count} files"
        if [[ "${artifact_count}" -gt 0 ]]; then
            find "${checkpoint_path}/artifacts" -type f -exec ls -lh {} \; 2>/dev/null | head -10
        fi
    fi
}

cmd_delete() {
    local task_id="$1"
    local checkpoint_path="${CHECKPOINT_DIR}/${task_id}"

    if [[ ! -d "${checkpoint_path}" ]]; then
        echo "Error: Checkpoint '${task_id}' not found" >&2
        exit 1
    fi

    # Archive before deleting
    local archive_dir="${CHECKPOINT_DIR}/.archive"
    mkdir -p "${archive_dir}"

    local archive_name="${task_id}-$(date +%Y%m%d%H%M%S)"
    mv "${checkpoint_path}" "${archive_dir}/${archive_name}"

    log "Deleted checkpoint: ${task_id} (archived as ${archive_name})"
    echo "Checkpoint '${task_id}' deleted (archived to .archive/${archive_name})"
}

cmd_update_state() {
    local task_id="$1"
    local key="$2"
    local value="$3"
    local checkpoint_path="${CHECKPOINT_DIR}/${task_id}"
    local state_file="${checkpoint_path}/state.json"

    if [[ ! -f "${state_file}" ]]; then
        echo "Error: State file not found for checkpoint '${task_id}'" >&2
        exit 1
    fi

    # Update the state file
    local tmp_file
    tmp_file=$(mktemp)
    jq --arg key "${key}" --arg value "${value}" '.[${key}] = ${value} | .last_updated = (now | todate)' "${state_file}" >"${tmp_file}" && mv "${tmp_file}" "${state_file}"

    log "Updated state for ${task_id}: ${key}"
    echo "State updated: ${key}"
}

cmd_help() {
    cat <<EOF
Checkpoint State Management

Usage:
  checkpoint_state.sh <command> [arguments]

Commands:
  create <task-id> [description]  Create a new checkpoint
  list                            List all checkpoints
  show <task-id>                  Show checkpoint details
  delete <task-id>                Delete a checkpoint (archives first)
  update <task-id> <key> <value>  Update a state key
  help                            Show this help

Examples:
  # Create a checkpoint for a validation task
  checkpoint_state.sh create validation-task "Validating all WFM files"

  # List all checkpoints
  checkpoint_state.sh list

  # Show details of a checkpoint
  checkpoint_state.sh show validation-task

  # Update progress
  checkpoint_state.sh update validation-task phase "testing"

  # Delete a checkpoint
  checkpoint_state.sh delete validation-task

Checkpoint Structure:
  .coordination/checkpoints/<task-id>/
    manifest.json   - Metadata (created_at, description, status)
    state.json      - Task state (phase, progress, results, next_steps)
    context.md      - Human-readable summary for resumption
    artifacts/      - Important files to preserve

Recovery:
  Use restore_checkpoint.sh to load a checkpoint after compaction:
    .claude/hooks/restore_checkpoint.sh <task-id>

EOF
}

# ============================================================
# Main
# ============================================================

COMMAND="${1:-help}"
shift || true

case "${COMMAND}" in
create)
    cmd_create "$@"
    ;;
list)
    cmd_list
    ;;
show)
    if [[ -z "${1:-}" ]]; then
        echo "Error: task-id required" >&2
        exit 1
    fi
    cmd_show "$1"
    ;;
delete)
    if [[ -z "${1:-}" ]]; then
        echo "Error: task-id required" >&2
        exit 1
    fi
    cmd_delete "$1"
    ;;
update)
    if [[ -z "${1:-}" ]] || [[ -z "${2:-}" ]] || [[ -z "${3:-}" ]]; then
        echo "Error: task-id, key, and value required" >&2
        exit 1
    fi
    cmd_update_state "$1" "$2" "$3"
    ;;
help | --help | -h)
    cmd_help
    ;;
*)
    echo "Unknown command: ${COMMAND}" >&2
    echo "Run 'checkpoint_state.sh help' for usage" >&2
    exit 1
    ;;
esac
