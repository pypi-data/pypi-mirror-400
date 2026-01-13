#!/usr/bin/env bash
# Log rotation for errors.log
#
# Prevents errors.log from growing too large by:
# - Keeping last 50 lines in current log
# - Archiving older entries with timestamp
# - Maintaining historical debugging data
#
# Runs as preMessageSent hook to ensure log is always readable

set -euo pipefail

# CLAUDE_PROJECT_DIR is set by the environment when called as a hook
LOG_FILE="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/errors.log"
ARCHIVE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/errors.archive"
MAX_SIZE_KB=100 # Rotate at 100KB
KEEP_LINES=100  # Keep last N lines in current log (covers ~7-10 file errors)

# Create archive directory if it doesn't exist
mkdir -p "${ARCHIVE_DIR}"

# Check if log file exists and needs rotation
if [[ -f "${LOG_FILE}" ]]; then
  SIZE=$(du -k "${LOG_FILE}" 2>/dev/null | cut -f1 || echo "0")

  if [[ "${SIZE}" -gt "${MAX_SIZE_KB}" ]]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    ARCHIVE_FILE="${ARCHIVE_DIR}/errors-${TIMESTAMP}.log"

    # Keep last N lines, archive the rest
    if [[ "$(wc -l <"${LOG_FILE}")" -gt "${KEEP_LINES}" ]]; then
      # Archive everything except last N lines
      head -n -${KEEP_LINES} "${LOG_FILE}" >"${ARCHIVE_FILE}"

      # Keep only last N lines in current log
      tail -${KEEP_LINES} "${LOG_FILE}" >"${LOG_FILE}.tmp"
      mv "${LOG_FILE}.tmp" "${LOG_FILE}"

      # Add rotation marker
      echo "=== Log rotated at ${TIMESTAMP} (archived $(wc -l <"${ARCHIVE_FILE}") lines) ===" >>"${LOG_FILE}"
    fi
  fi
fi

# Cleanup old archives (keep last 10)
find "${ARCHIVE_DIR}" -name "errors-*.log" -type f | sort -r | tail -n +11 | xargs -r rm -f

exit 0
