#!/usr/bin/env bash
# Initialize agent registry for context compaction mitigation
# Version: 1.0.0 (2025-12-24)

set -euo pipefail

REGISTRY_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/agent-registry.json"
BACKUP_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/agent-registry.backup.json"
SUMMARIES_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/summaries"
CHECKPOINTS_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/checkpoints"

# Create directories if they don't exist
mkdir -p "$(dirname "${REGISTRY_FILE}")"
mkdir -p "${SUMMARIES_DIR}"
mkdir -p "${CHECKPOINTS_DIR}"

# Backup existing registry if present
if [[ -f "${REGISTRY_FILE}" ]]; then
    cp "${REGISTRY_FILE}" "${BACKUP_FILE}"
    echo "Backed up existing registry to ${BACKUP_FILE}"
fi

# Initialize empty registry with metadata
cat >"${REGISTRY_FILE}" <<EOF
{
  "version": "1.0.0",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "agents": {},
  "metadata": {
    "total_agents_launched": 0,
    "agents_running": 0,
    "agents_completed": 0,
    "agents_failed": 0,
    "last_cleanup": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  }
}
EOF

echo "Initialized agent registry at ${REGISTRY_FILE}"
echo "Summaries directory: ${SUMMARIES_DIR}"
echo "Checkpoints directory: ${CHECKPOINTS_DIR}"
