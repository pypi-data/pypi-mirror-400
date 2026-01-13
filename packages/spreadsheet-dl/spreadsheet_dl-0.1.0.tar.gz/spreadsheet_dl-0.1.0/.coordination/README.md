# Coordination Directory

This directory manages agent coordination, task state, and workflow orchestration.

## Structure

```
.coordination/
├── work_queue.json      # Pending tasks (FIFO queue)
├── active_work.json     # Currently executing task
├── completed.jsonl      # Append-only completion log (event sourcing)
├── checkpoints/         # Long-running task state snapshots
├── handoffs/            # Pending agent handoff queue
├── locks/               # TTL-based coordination locks
├── projects/            # Project-specific coordination state
├── archive/             # Archived files (>30 days old)
└── README.md            # This file
```

## File Formats

### work_queue.json

```json
{
  "tasks": [
    {
      "id": "YYYY-MM-DD-HHMMSS-description",
      "type": "research|implementation|validation",
      "priority": 1,
      "agent": "target-agent",
      "context": {},
      "created_at": "ISO-8601"
    }
  ]
}
```

### active_work.json

```json
{
  "task_id": "YYYY-MM-DD-HHMMSS-description",
  "agent": "agent-name",
  "status": "in_progress",
  "started_at": "ISO-8601",
  "last_update": "ISO-8601",
  "context": {}
}
```

### completed.jsonl (append-only)

Each line is a JSON completion report:

```json
{
  "task_id": "...",
  "agent": "...",
  "status": "complete",
  "artifacts": [],
  "completed_at": "ISO-8601"
}
```

## Checkpoints

For long-running tasks, state is preserved in `checkpoints/[task-id]/`:

```
checkpoints/[task-id]/
├── metadata.json    # Task info, phase number
├── state.json       # Agent state snapshot
├── context.json     # Accumulated context
└── artifacts.json   # References to outputs
```

## Handoffs

Pending agent handoffs are queued in `handoffs/`:

```json
{
  "from_agent": "knowledge_researcher",
  "to_agent": "technical_writer",
  "task_id": "...",
  "handoff_context": {
    "summary": "...",
    "key_findings": [],
    "open_questions": []
  },
  "created_at": "ISO-8601"
}
```

## Locks

TTL-based coordination locks in `locks/`:

```json
{
  "holder": "agent-name",
  "resource": "resource-id",
  "acquired_at": "ISO-8601",
  "expires_at": "ISO-8601",
  "pid": 12345
}
```

## Retention Policy

- **Coordination files**: Archived after 30 days
- **Completed tasks**: Retained in `completed.jsonl` indefinitely
- **Checkpoints**: Cleaned up 7 days after task completion
- **Locks**: Expired locks cleaned up by `session_cleanup.sh`

## Best Practices

1. **Never modify `completed.jsonl`** - It's an append-only event log
2. **Always use locks** for concurrent resource access
3. **Include `handoff_context`** in completion reports for reliable handoffs
4. **Checkpoint at phase boundaries** for long-running tasks (not step-by-step)
5. **Clean up locks** when task completes or fails
