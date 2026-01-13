---
name: implement
description: Implement tasks from spec with automatic validation
arguments: <task-id|phase|next>
---

# Implement Command

Implement tasks from the specification task graph with automatic validation.

## Usage

```bash
/implement TASK-001        # Implement specific task
/implement phase 1         # Implement all tasks in phase 1
/implement next            # Implement next unblocked task
/implement tier 1          # Implement all tier 1 tasks
```

## Process

1. Load task from task-graph.yaml
2. Verify dependencies are complete
3. Invoke spec_implementer agent
4. After implementation, invoke spec_validator
5. If validation passes, mark task complete
6. If validation fails, report issues (retry up to 3x)

## Workflow

```
Load Task -> Check Dependencies -> Gather Context
                |
        spec_implementer
                |
        spec_validator
                |
    +-------+-------+
    |               |
  Pass            Fail
    |               |
Mark Complete   Retry (max 3x)
```

## Arguments

| Argument | Description          |
| -------- | -------------------- |
| TASK-XXX | Specific task ID     |
| phase N  | All tasks in phase N |
| next     | Next unblocked task  |
| tier N   | All tier N tasks     |

## Output

- Implemented deliverables
- Validation results
- Updated task status
- Completion reports for impl and validation

## See Also

- `.claude/agents/spec_implementer.md` - Implementation agent
- `.claude/agents/spec_validator.md` - Validation agent
- `/spec` - Specification workflow utilities
