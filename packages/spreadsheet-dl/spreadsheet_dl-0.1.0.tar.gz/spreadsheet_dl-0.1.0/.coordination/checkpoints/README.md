# Checkpoints Directory

This directory stores state checkpoints for long-running tasks to enable recovery after context compaction.

## Purpose

When Claude's context approaches capacity, it may need to compact (summarize) the conversation history. Checkpoints preserve critical task state that can be restored after compaction.

## Structure

Each checkpoint is stored in its own subdirectory:

```
.coordination/checkpoints/
  <task-id>/
    manifest.json   - Checkpoint metadata (created_at, description, status)
    state.json      - Task state (phase, progress, results, next_steps)
    context.md      - Human-readable summary for resumption
    artifacts/      - Important files to preserve
```

## Usage

### Creating a Checkpoint

```bash
# Create before compaction or at milestone
.claude/hooks/checkpoint_state.sh create <task-id> "Description"

# Example
.claude/hooks/checkpoint_state.sh create validation-run "Validating WFM files"
```

### Listing Checkpoints

```bash
.claude/hooks/checkpoint_state.sh list
```

### Restoring After Compaction

```bash
# Restore specific checkpoint
.claude/hooks/restore_checkpoint.sh <task-id>

# Restore most recent
.claude/hooks/restore_checkpoint.sh --latest
```

### Updating Progress

Edit `state.json` directly or use:

```bash
.claude/hooks/checkpoint_state.sh update <task-id> phase "testing"
```

### Deleting Checkpoints

```bash
.claude/hooks/checkpoint_state.sh delete <task-id>
```

Deleted checkpoints are archived to `.archive/` subdirectory.

## State File Format

```json
{
  "task_id": "validation-run",
  "phase": "testing",
  "progress": {
    "current_step": 50,
    "total_steps": 100,
    "percentage": 50
  },
  "results": {
    "files_processed": 50,
    "errors_found": 3
  },
  "next_steps": [
    "Continue processing remaining files",
    "Generate final report"
  ],
  "key_decisions": ["Using strict validation mode", "Skipping corrupted files"],
  "open_questions": ["Should we retry failed files?"],
  "last_updated": "2025-12-24T10:00:00Z"
}
```

## Best Practices

1. **Create checkpoints proactively** - Before context reaches 70%
2. **Update state regularly** - After each significant milestone
3. **Document decisions** - In `key_decisions` field
4. **List next steps** - Clear resumption instructions
5. **Keep artifacts minimal** - Only essential files
6. **Write clear context.md** - Human-readable summary

## Retention Policy

- Checkpoints are cleaned up after 7 days by pre_compact_cleanup.sh
- Deleted checkpoints are archived for 30 days
- Use `--days` flag with archive script to customize

## Integration with Compaction

The pre_compact_cleanup.sh hook:

1. Archives checkpoints older than 7 days
2. Preserves active checkpoints during compaction
3. Logs checkpoint status to compaction.log

The post_compact_recovery.sh hook:

1. Verifies checkpoint directory exists
2. Reports number of available checkpoints
3. Suggests restoration commands if needed
