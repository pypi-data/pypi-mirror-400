#!/usr/bin/env bash
# =============================================================================
# archive_coordination.sh - Coordination File Archival Tool
# =============================================================================
# Archives old coordination files and agent outputs to keep working directories
# clean. Moves files older than a configurable threshold to archive subdirectories
# with manifest generation for audit trails.
#
# Usage: ./scripts/maintenance/archive_coordination.sh [OPTIONS]
#
# Examples:
#   ./scripts/maintenance/archive_coordination.sh              # Archive files >30 days
#   ./scripts/maintenance/archive_coordination.sh --dry-run    # Preview what would happen
#   ./scripts/maintenance/archive_coordination.sh --days 14    # Custom threshold
#   ./scripts/maintenance/archive_coordination.sh --cron       # Silent for scheduled runs
#
# Cron Example:
#   # Weekly archive (Sundays at 3am)
#   0 3 * * 0 cd /path/to/repo && ./scripts/maintenance/archive_coordination.sh --cron
# =============================================================================
#
# NOTE: VS Code shellcheck extension may show SC2154 false positives for
# variables sourced from lib/common.sh. These are extension bugs, not code
# issues. CLI shellcheck validates correctly:
#   cd /path/to/workspace_template && shellcheck scripts/maintenance/archive_coordination.sh
# =============================================================================

# shellcheck source=../lib/common.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/common.sh"

# Configuration
DEFAULT_DAYS=30
COORDINATION_DIR="${REPO_ROOT}/.coordination"
AGENT_OUTPUTS_DIR="${REPO_ROOT}/.claude/agent-outputs"
TIMESTAMP=$(date '+%Y-%m-%d_%H%M%S')

# Options
DAYS=${DEFAULT_DAYS}
DRY_RUN=false
CRON_MODE=false
VERBOSE=false

# Results
ARCHIVED_COUNT=0
SKIPPED_COUNT=0
TOTAL_SIZE=0
declare -a ARCHIVED_FILES=()

# =============================================================================
# Help
# =============================================================================

show_script_help() {
    cat <<'EOF'
archive_coordination.sh - Coordination file archival tool

USAGE:
    archive_coordination.sh [OPTIONS]

DESCRIPTION:
    Archives coordination files and agent outputs that are older than a
    specified threshold. Files are moved to archive subdirectories with
    a manifest documenting what was archived.

    This helps keep working directories clean while preserving historical
    data for audit and reference purposes.

DIRECTORIES MANAGED:
    .coordination/          - Task coordination files, work queues
    .claude/agent-outputs/  - Agent completion reports

OPTIONS:
    --days N        Archive files older than N days (default: 30)
    --dry-run, -n   Preview what would be archived without making changes
    --cron          Silent mode for cron jobs (only output on errors)
    --json          Output machine-readable JSON
    -v, --verbose   Show detailed output for each file
    -h, --help      Show this help message

ARCHIVE STRUCTURE:
    .coordination/
    └── archive/
        └── YYYY-MM-DD_HHMMSS/
            ├── manifest.json      # List of archived files with metadata
            └── [archived files]   # Moved coordination files

    .claude/agent-outputs/
    └── archive/
        └── YYYY-MM-DD_HHMMSS/
            ├── manifest.json
            └── [archived files]

MANIFEST FORMAT:
    {
        "archived_at": "2024-01-15T10:30:00Z",
        "threshold_days": 30,
        "files": [
            {
                "name": "2024-01-01-task.md",
                "original_path": ".coordination/2024-01-01-task.md",
                "size_bytes": 1234,
                "modified_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total_files": 5,
        "total_size_bytes": 12345
    }

CRON EXAMPLES:
    # Weekly archive (Sundays at 3am)
    0 3 * * 0 cd /path/to/repo && ./scripts/maintenance/archive_coordination.sh --cron

    # Monthly archive with 14-day threshold
    0 4 1 * * cd /path/to/repo && ./scripts/maintenance/archive_coordination.sh --cron --days 14

    # Daily dry-run report to email
    0 6 * * * cd /path/to/repo && ./scripts/maintenance/archive_coordination.sh --dry-run | mail -s "Archive Report" admin@example.com

EXAMPLES:
    # Preview what would be archived
    archive_coordination.sh --dry-run

    # Archive files older than 14 days
    archive_coordination.sh --days 14

    # Verbose output showing each file
    archive_coordination.sh -v

    # Silent cron mode
    archive_coordination.sh --cron

    # JSON output for automation
    archive_coordination.sh --json

EXIT CODES:
    0  Archival completed successfully (or nothing to archive)
    1  Errors during archival
    2  Configuration error

SEE ALSO:
    scripts/maintenance/scheduled_quality_check.sh - Automated quality checks
    scripts/clean.sh - Clean build artifacts
EOF
}

# =============================================================================
# Utility Functions
# =============================================================================

# Get file age in days
get_file_age_days() {
    local file="$1"
    local now
    local file_mtime
    local age_seconds

    now=$(date +%s)
    file_mtime=$(stat -c %Y "${file}" 2>/dev/null || stat -f %m "${file}" 2>/dev/null)
    age_seconds=$((now - file_mtime))
    echo $((age_seconds / 86400))
}

# Get file modification time in ISO format
get_file_mtime_iso() {
    local file="$1"
    stat -c %y "${file}" 2>/dev/null | cut -d. -f1 | tr ' ' 'T' ||
        date -r "${file}" '+%Y-%m-%dT%H:%M:%S' 2>/dev/null ||
        echo "unknown"
}

# Get file size in bytes
get_file_size() {
    local file="$1"
    stat -c %s "${file}" 2>/dev/null || stat -f %z "${file}" 2>/dev/null || echo 0
}

# Create archive directory
create_archive_dir() {
    local base_dir="$1"
    local archive_dir="${base_dir}/archive/${TIMESTAMP}"

    if ! ${DRY_RUN}; then
        mkdir -p "${archive_dir}"
    fi
    echo "${archive_dir}"
}

# Generate manifest JSON
generate_manifest() {
    local archive_dir="$1"
    local manifest_file="${archive_dir}/manifest.json"
    local files_json=""
    local i=0

    for entry in "${ARCHIVED_FILES[@]}"; do
        # Parse entry: name|original_path|size|mtime
        IFS='|' read -r name original size mtime <<<"${entry}"

        if [[ ${i} -gt 0 ]]; then
            files_json+=","
        fi
        files_json+="
        {
            \"name\": \"${name}\",
            \"original_path\": \"${original}\",
            \"size_bytes\": ${size},
            \"modified_at\": \"${mtime}\"
        }"
        ((i++)) || true
    done

    if ! ${DRY_RUN}; then
        cat >"${manifest_file}" <<EOF
{
    "archived_at": "$(date -Iseconds)",
    "threshold_days": ${DAYS},
    "files": [${files_json}
    ],
    "total_files": ${ARCHIVED_COUNT},
    "total_size_bytes": ${TOTAL_SIZE}
}
EOF
    fi

    if ${VERBOSE} && ! ${CRON_MODE}; then
        print_pass "Created manifest: ${manifest_file}"
    fi
}

# =============================================================================
# Archive Functions
# =============================================================================

archive_directory() {
    local source_dir="$1"
    local dir_name="$2"
    local archived_from_dir=0
    local archive_dir=""

    if [[ ! -d "${source_dir}" ]]; then
        if ! ${CRON_MODE}; then
            print_skip "${dir_name}: Directory not found"
        fi
        return 0
    fi

    if ! ${CRON_MODE}; then
        print_section "Archiving ${dir_name}"
    fi

    # Find old files
    local old_files=()
    while IFS= read -r -d '' file; do
        # Skip archive directory itself
        [[ "${file}" == *"/archive/"* ]] && continue

        local age
        age=$(get_file_age_days "${file}")
        if [[ ${age} -ge ${DAYS} ]]; then
            old_files+=("${file}")
        fi
    done < <(find "${source_dir}" -maxdepth 1 -type f -print0 2>/dev/null)

    if [[ ${#old_files[@]} -eq 0 ]]; then
        if ! ${CRON_MODE}; then
            print_info "No files older than ${DAYS} days"
        fi
        return 0
    fi

    # Create archive directory
    archive_dir=$(create_archive_dir "${source_dir}")

    if ${VERBOSE} && ! ${CRON_MODE}; then
        print_info "Archive destination: ${archive_dir}"
    fi

    # Archive each file
    for file in "${old_files[@]}"; do
        local filename
        local size
        local mtime
        local age

        filename=$(basename "${file}")
        size=$(get_file_size "${file}")
        mtime=$(get_file_mtime_iso "${file}")
        age=$(get_file_age_days "${file}")

        if ${DRY_RUN}; then
            if ! ${CRON_MODE}; then
                print_info "Would archive: ${filename} (${age}d old, ${size} bytes)"
            fi
        else
            if mv "${file}" "${archive_dir}/"; then
                if ${VERBOSE} && ! ${CRON_MODE}; then
                    print_pass "Archived: ${filename}"
                fi
            else
                if ! ${CRON_MODE}; then
                    print_fail "Failed to archive: ${filename}"
                fi
                continue
            fi
        fi

        # Track for manifest
        ARCHIVED_FILES+=("${filename}|${source_dir}/${filename}|${size}|${mtime}")
        ((ARCHIVED_COUNT++)) || true
        ((TOTAL_SIZE += size)) || true
        ((archived_from_dir++)) || true
    done

    # Generate manifest if files were archived
    if [[ ${archived_from_dir} -gt 0 ]] && [[ ${#ARCHIVED_FILES[@]} -gt 0 ]]; then
        if ! ${DRY_RUN}; then
            generate_manifest "${archive_dir}"
        fi
    fi

    if ! ${CRON_MODE}; then
        if ${DRY_RUN}; then
            print_info "Would archive ${archived_from_dir} file(s) from ${dir_name}"
        else
            print_pass "Archived ${archived_from_dir} file(s) from ${dir_name}"
        fi
    fi
}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
    -h | --help)
        show_script_help
        exit 0
        ;;
    --days)
        if [[ -z "${2:-}" ]] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
            echo "Error: --days requires a positive integer" >&2
            exit 2
        fi
        DAYS="$2"
        shift 2
        ;;
    --dry-run | -n)
        DRY_RUN=true
        shift
        ;;
    --cron)
        CRON_MODE=true
        shift
        ;;
    -v | --verbose)
        VERBOSE=true
        shift
        ;;
    --json)
        enable_json
        shift
        ;;
    -*)
        echo "Unknown option: $1" >&2
        echo "Use -h for help" >&2
        exit 2
        ;;
    *)
        echo "Unexpected argument: $1" >&2
        exit 2
        ;;
    esac
done

# =============================================================================
# Main
# =============================================================================

main() {
    # Header
    if ! ${CRON_MODE}; then
        print_header "COORDINATION FILE ARCHIVAL"
        echo ""
        print_info "Repository: ${REPO_ROOT}"
        print_info "Threshold:  ${DAYS} days"
        print_info "Timestamp:  $(date '+%Y-%m-%d %H:%M:%S')"
        if ${DRY_RUN}; then
            echo ""
            echo -e "  ${YELLOW}DRY RUN MODE - No changes will be made${NC}"
        fi
        echo ""
    fi

    # Reset tracking for each run
    ARCHIVED_COUNT=0
    SKIPPED_COUNT=0
    TOTAL_SIZE=0
    ARCHIVED_FILES=()

    # Archive coordination files
    archive_directory "${COORDINATION_DIR}" ".coordination"

    # Reset file list for second directory
    ARCHIVED_FILES=()

    # Archive agent outputs
    archive_directory "${AGENT_OUTPUTS_DIR}" ".claude/agent-outputs"

    # Summary
    if ! ${CRON_MODE}; then
        print_header "SUMMARY"
        echo ""
        printf "  %-25s %d\n" "Files archived:" "${ARCHIVED_COUNT}"
        printf "  %-25s %s\n" "Total size:" "$(numfmt --to=iec ${TOTAL_SIZE} 2>/dev/null || echo "${TOTAL_SIZE} bytes")"
        printf "  %-25s %d days\n" "Age threshold:" "${DAYS}"
        echo ""

        if ${DRY_RUN}; then
            print_info "Dry run complete - no files were moved"
        elif [[ ${ARCHIVED_COUNT} -eq 0 ]]; then
            print_pass "No files needed archiving"
        else
            print_pass "Archival complete"
        fi
    fi

    # JSON output
    if is_json_mode; then
        printf '{"archived_count":%d,"total_size_bytes":%d,"threshold_days":%d,"dry_run":%s,"timestamp":"%s"}\n' \
            "${ARCHIVED_COUNT}" "${TOTAL_SIZE}" "${DAYS}" "${DRY_RUN}" "$(date -Iseconds)"
    fi

    exit 0
}

main "$@"
