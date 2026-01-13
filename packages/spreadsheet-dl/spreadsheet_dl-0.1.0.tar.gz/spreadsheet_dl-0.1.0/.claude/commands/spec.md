---
name: spec
description: Specification workflow utilities
arguments: <action> [args]
---

# Spec Command

Specification workflow utilities for managing requirements and tasks.

## Usage

```bash
/spec extract <source>     # Extract requirements from narrative
/spec validate             # Validate requirement completeness
/spec decompose            # Create task graph from requirements
/spec criteria             # Generate validation criteria
/spec coverage             # Check implementation coverage
/spec context TASK-XXX     # Bundle context for task
```

## Actions

| Action    | Input              | Output                   |
| --------- | ------------------ | ------------------------ |
| extract   | Narrative markdown | requirements.yaml        |
| validate  | requirements.yaml  | Validation report        |
| decompose | requirements.yaml  | task-graph.yaml          |
| criteria  | requirements.yaml  | validation-manifest.yaml |
| coverage  | All + completions  | Coverage report          |
| context   | Task ID            | Context bundle           |

## Workflow

```
Narrative (L1)
     | extract
Requirements (L2)
     | validate
Validated Requirements
     | decompose
Task Graph (L3)
     | criteria
Validation Manifest (L4)
     | coverage
Coverage Report
```

## Output Locations

- Requirements: `.coordination/spec/{project}/requirements.yaml`
- Task Graph: `.coordination/spec/{project}/task-graph.yaml`
- Validation: `.coordination/spec/{project}/validation-manifest.yaml`
- Coverage: `.coordination/spec/{project}/coverage-report.md`

## See Also

- `/implement` - Implement tasks from task graph
- `.claude/templates/spec/` - Schema files
