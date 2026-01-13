#!/usr/bin/env bash
# Context usage monitoring hook
# Monitors token usage and triggers warnings at configurable thresholds
# Logs context growth rate and suggests cleanup actions
#
# Usage: Called periodically or before operations to check context health
# Can be invoked manually: .claude/hooks/check_context_usage.sh [--report]

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
HOOKS_DIR="${PROJECT_DIR}/.claude/hooks"
LOG_FILE="${HOOKS_DIR}/context_metrics.log"
STATE_FILE="${HOOKS_DIR}/.context_state.json"

# Thresholds (percentage of max context)
WARN_THRESHOLD_60=60
WARN_THRESHOLD_70=70
WARN_THRESHOLD_80=80
CRITICAL_THRESHOLD=90

# Estimated max context tokens (Claude's context window)
MAX_CONTEXT_TOKENS=200000

# Ensure directories exist
mkdir -p "${HOOKS_DIR}"

# ============================================================
# Utility Functions
# ============================================================

log() {
    echo "[$(date -Iseconds)] CONTEXT_MONITOR: $*" >>"${LOG_FILE}"
}

get_timestamp() {
    date +%s
}

get_iso_timestamp() {
    date -Iseconds
}

# Estimate context usage based on project file sizes and recent activity
# This is a heuristic since we can't directly query Claude's context
estimate_context_usage() {
    local total_estimate=0

    # Factor 1: Recent agent outputs (high weight - directly in context)
    if [[ -d "${PROJECT_DIR}/.claude/agent-outputs" ]]; then
        local agent_size
        agent_size=$(find "${PROJECT_DIR}/.claude/agent-outputs" -maxdepth 1 -name "*.json" -type f -mmin -60 -exec du -cb {} + 2>/dev/null | tail -1 | cut -f1 || echo 0)
        # Estimate ~4 chars per token
        total_estimate=$((total_estimate + agent_size / 4))
    fi

    # Factor 2: Coordination files (medium weight)
    if [[ -d "${PROJECT_DIR}/.coordination" ]]; then
        local coord_size
        coord_size=$(find "${PROJECT_DIR}/.coordination" -maxdepth 2 -type f \( -name "*.md" -o -name "*.json" -o -name "*.yaml" \) -mmin -120 -exec du -cb {} + 2>/dev/null | tail -1 | cut -f1 || echo 0)
        total_estimate=$((total_estimate + coord_size / 4))
    fi

    # Factor 3: Recent tool outputs (check log sizes)
    if [[ -f "${HOOKS_DIR}/compaction.log" ]]; then
        local log_size
        log_size=$(stat -c%s "${HOOKS_DIR}/compaction.log" 2>/dev/null || echo 0)
        total_estimate=$((total_estimate + log_size / 4))
    fi

    # Factor 4: Base overhead (CLAUDE.md, agents, commands)
    local base_overhead=5000 # ~5K tokens baseline
    total_estimate=$((total_estimate + base_overhead))

    echo "${total_estimate}"
}

# Calculate percentage
calc_percentage() {
    local current="$1"
    local max="$2"
    echo $((current * 100 / max))
}

# Load previous state for growth rate calculation
load_state() {
    if [[ -f "${STATE_FILE}" ]]; then
        cat "${STATE_FILE}"
    else
        echo '{"last_check": 0, "last_estimate": 0, "samples": []}'
    fi
}

# Save current state
save_state() {
    local estimate="$1"
    local timestamp
    timestamp=$(get_timestamp)

    # Load existing samples
    local prev_state
    prev_state=$(load_state)

    # Keep last 10 samples for growth rate calculation
    local samples
    samples=$(echo "${prev_state}" | jq -c '.samples // []' 2>/dev/null || echo '[]')
    samples=$(echo "${samples}" | jq -c ". + [{\"ts\": ${timestamp}, \"est\": ${estimate}}] | .[-10:]" 2>/dev/null || echo '[]')

    cat >"${STATE_FILE}" <<EOF
{
    "last_check": ${timestamp},
    "last_estimate": ${estimate},
    "samples": ${samples}
}
EOF
}

# Calculate growth rate (tokens per minute)
calc_growth_rate() {
    local current_estimate="$1"
    local state
    state=$(load_state)

    local samples
    samples=$(echo "${state}" | jq -c '.samples // []' 2>/dev/null || echo '[]')
    local sample_count
    sample_count=$(echo "${samples}" | jq 'length' 2>/dev/null || echo 0)

    if [[ "${sample_count}" -lt 2 ]]; then
        echo "0"
        return
    fi

    # Get first and last samples
    local first_ts first_est last_ts last_est
    first_ts=$(echo "${samples}" | jq '.[0].ts' 2>/dev/null || echo 0)
    first_est=$(echo "${samples}" | jq '.[0].est' 2>/dev/null || echo 0)
    last_ts=$(echo "${samples}" | jq '.[-1].ts' 2>/dev/null || echo 0)
    last_est=$(echo "${samples}" | jq '.[-1].est' 2>/dev/null || echo 0)

    local time_diff=$((last_ts - first_ts))
    local token_diff=$((last_est - first_est))

    if [[ "${time_diff}" -gt 0 ]]; then
        # Tokens per minute
        echo $((token_diff * 60 / time_diff))
    else
        echo "0"
    fi
}

# Generate cleanup suggestions based on current state
generate_suggestions() {
    local percentage="$1"
    local suggestions=()

    if [[ "${percentage}" -ge "${CRITICAL_THRESHOLD}" ]]; then
        suggestions+=("CRITICAL: Compact immediately or end session")
        suggestions+=("Run: .claude/hooks/pre_compact_cleanup.sh")
        suggestions+=("Consider creating checkpoint before compact")
    elif [[ "${percentage}" -ge "${WARN_THRESHOLD_80}" ]]; then
        suggestions+=("HIGH: Consider compacting soon")
        suggestions+=("Archive old agent outputs: find .claude/agent-outputs -mtime +1 -delete")
        suggestions+=("Clean checkpoints: rm -rf .coordination/checkpoints/*/")
    elif [[ "${percentage}" -ge "${WARN_THRESHOLD_70}" ]]; then
        suggestions+=("MEDIUM: Monitor context growth")
        suggestions+=("Avoid loading large files into context")
        suggestions+=("Use file references instead of embedding content")
    elif [[ "${percentage}" -ge "${WARN_THRESHOLD_60}" ]]; then
        suggestions+=("LOW: Context usage moderate")
        suggestions+=("Consider summarizing completed work")
    fi

    # Output as JSON array
    printf '%s\n' "${suggestions[@]}" | jq -R . | jq -s .
}

# Get warning level
get_warning_level() {
    local percentage="$1"

    if [[ "${percentage}" -ge "${CRITICAL_THRESHOLD}" ]]; then
        echo "critical"
    elif [[ "${percentage}" -ge "${WARN_THRESHOLD_80}" ]]; then
        echo "high"
    elif [[ "${percentage}" -ge "${WARN_THRESHOLD_70}" ]]; then
        echo "medium"
    elif [[ "${percentage}" -ge "${WARN_THRESHOLD_60}" ]]; then
        echo "low"
    else
        echo "ok"
    fi
}

# ============================================================
# Main Logic
# ============================================================

# Parse arguments
REPORT_MODE=false
if [[ "${1:-}" = "--report" ]] || [[ "${1:-}" = "-r" ]]; then
    REPORT_MODE=true
fi

# Estimate current usage
CURRENT_ESTIMATE=$(estimate_context_usage)
PERCENTAGE=$(calc_percentage "${CURRENT_ESTIMATE}" "${MAX_CONTEXT_TOKENS}")
GROWTH_RATE=$(calc_growth_rate "${CURRENT_ESTIMATE}")
WARNING_LEVEL=$(get_warning_level "${PERCENTAGE}")
SUGGESTIONS=$(generate_suggestions "${PERCENTAGE}")

# Save state for trend analysis
save_state "${CURRENT_ESTIMATE}"

# Log the check
log "Usage: ${PERCENTAGE}% (~${CURRENT_ESTIMATE} tokens), Growth: ${GROWTH_RATE} tokens/min, Level: ${WARNING_LEVEL}"

# Calculate time until critical (if growing)
TIME_UNTIL_CRITICAL="unknown"
if [[ "${GROWTH_RATE}" -gt 0 ]]; then
    tokens_remaining=$((MAX_CONTEXT_TOKENS * CRITICAL_THRESHOLD / 100 - CURRENT_ESTIMATE))
    if [[ "${tokens_remaining}" -gt 0 ]]; then
        TIME_UNTIL_CRITICAL="$((tokens_remaining / GROWTH_RATE)) minutes"
    else
        TIME_UNTIL_CRITICAL="now"
    fi
fi

# Generate output
if [[ "${REPORT_MODE}" = true ]]; then
    # Detailed report for manual inspection
    cat <<EOF
Context Usage Report
====================
Timestamp: $(get_iso_timestamp)

Estimated Usage: ${CURRENT_ESTIMATE} tokens (${PERCENTAGE}% of ${MAX_CONTEXT_TOKENS})
Growth Rate: ${GROWTH_RATE} tokens/minute
Warning Level: ${WARNING_LEVEL}
Time Until Critical: ${TIME_UNTIL_CRITICAL}

Thresholds:
  - Low Warning: ${WARN_THRESHOLD_60}%
  - Medium Warning: ${WARN_THRESHOLD_70}%
  - High Warning: ${WARN_THRESHOLD_80}%
  - Critical: ${CRITICAL_THRESHOLD}%

Suggestions:
$(echo "${SUGGESTIONS}" | jq -r '.[]' 2>/dev/null | sed 's/^/  - /')

Recent Metrics:
$(tail -5 "${LOG_FILE}" 2>/dev/null | sed 's/^/  /')
EOF
else
    # JSON output for programmatic use
    cat <<EOF
{
    "ok": $([[ "${WARNING_LEVEL}" = "ok" ]] || [[ "${WARNING_LEVEL}" = "low" ]] && echo "true" || echo "false"),
    "warning_level": "${WARNING_LEVEL}",
    "estimated_tokens": ${CURRENT_ESTIMATE},
    "max_tokens": ${MAX_CONTEXT_TOKENS},
    "percentage": ${PERCENTAGE},
    "growth_rate_per_min": ${GROWTH_RATE},
    "time_until_critical": "${TIME_UNTIL_CRITICAL}",
    "suggestions": ${SUGGESTIONS},
    "timestamp": "$(get_iso_timestamp)"
}
EOF
fi

# Exit with appropriate code based on warning level
case "${WARNING_LEVEL}" in
"critical")
    exit 2
    ;;
"high")
    exit 1
    ;;
*)
    exit 0
    ;;
esac
