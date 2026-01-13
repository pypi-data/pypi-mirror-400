# Agent Output Rules Template

Template for file-based output patterns used by orchestrator agent coordination.

## Purpose

This template defines the standard structure and rules for agent completion reports. All agents must follow this pattern when writing their output to `.claude/agent-outputs/`.

## Output File Pattern

```
.claude/agent-outputs/[task-id]-complete.json
```

**Naming Convention:**

- `task-id`: Unique identifier for the task (typically timestamp-based: YYYY-MM-DD-HHMMSS-description)
- `-complete`: Suffix indicating task completion
- `.json`: JSON format for machine-readable output

**Examples:**

- `.claude/agent-outputs/2026-01-06-160000-comprehensive-audit-complete.json`
- `.claude/agent-outputs/2026-01-05-143000-implement-feature-complete.json`
- `.claude/agent-outputs/2026-01-04-092000-test-validation-complete.json`

## Output Structure

### Required Fields

```json
{
  "task_id": "string",
  "agent": "string",
  "status": "string",
  "timestamp": "string",
  "summary": "string",
  "details": {},
  "deliverables": [],
  "next_steps": []
}
```

### Field Definitions

| Field          | Type   | Description                                            | Required |
| -------------- | ------ | ------------------------------------------------------ | -------- |
| `task_id`      | string | Unique task identifier matching filename               | Yes      |
| `agent`        | string | Agent name that produced this output                   | Yes      |
| `status`       | string | Completion status: "complete", "blocked", "partial"    | Yes      |
| `timestamp`    | string | ISO 8601 timestamp of completion                       | Yes      |
| `summary`      | string | Brief summary of work performed (2-3 sentences)        | Yes      |
| `details`      | object | Detailed findings, results, or analysis                | Yes      |
| `deliverables` | array  | List of files created/modified or artifacts produced   | No       |
| `next_steps`   | array  | Recommended follow-up actions                          | No       |
| `blockers`     | array  | Issues preventing completion (if status != "complete") | No       |

## Status Values

| Status     | Description              | When to Use                                    |
| ---------- | ------------------------ | ---------------------------------------------- |
| `complete` | Task fully completed     | All work done, all deliverables ready          |
| `partial`  | Task partially completed | Some work done, but more required              |
| `blocked`  | Task blocked             | Cannot proceed due to external dependency      |
| `failed`   | Task failed              | Attempted but could not complete due to errors |

## Examples

### Complete Task Output

```json
{
  "task_id": "2026-01-06-160000-comprehensive-audit",
  "agent": "orchestrator",
  "status": "complete",
  "timestamp": "2026-01-06T16:30:00Z",
  "summary": "Completed comprehensive audit of SpreadsheetDL project covering all documentation, code, configuration, and scripts. Found 2 HIGH, 8 MEDIUM, and 12 LOW priority issues.",
  "details": {
    "files_audited": 323,
    "documentation_files": 97,
    "python_files": 170,
    "config_files": 15,
    "scripts": 41,
    "issues_found": {
      "high": 2,
      "medium": 8,
      "low": 12
    },
    "critical_findings": [
      "Missing referenced file: .claude/agents/references/git-commit-examples.md",
      "Missing referenced file: .claude/templates/agent_output_rules.md"
    ],
    "recommendations": [
      "Create missing referenced files",
      "Update documentation to reflect template system removal",
      "Sync version references across all files"
    ]
  },
  "deliverables": [
    ".claude/agent-outputs/2026-01-06-160000-comprehensive-audit-complete.json",
    ".coordination/2026-01-06-audit-detailed-findings.md"
  ],
  "next_steps": [
    "Fix HIGH priority issues (2 missing files)",
    "Address MEDIUM priority documentation updates",
    "Review LOW priority improvements"
  ]
}
```

### Blocked Task Output

```json
{
  "task_id": "2026-01-06-170000-implement-feature",
  "agent": "spec_implementer",
  "status": "blocked",
  "timestamp": "2026-01-06T17:15:00Z",
  "summary": "Implementation of authentication feature blocked pending API specification. Cannot proceed without endpoint definitions and authentication flow.",
  "details": {
    "work_completed": [
      "Analyzed existing authentication patterns",
      "Reviewed security best practices",
      "Identified required dependencies"
    ],
    "work_remaining": [
      "Implement authentication endpoints",
      "Add JWT token handling",
      "Create authentication middleware"
    ]
  },
  "blockers": [
    "API specification not finalized",
    "Authentication flow not defined by stakeholder",
    "OAuth provider selection pending"
  ],
  "next_steps": [
    "Wait for API specification from architect",
    "Clarify authentication requirements with user",
    "Resume implementation once blockers resolved"
  ]
}
```

### Partial Task Output

```json
{
  "task_id": "2026-01-06-180000-test-suite",
  "agent": "spec_validator",
  "status": "partial",
  "timestamp": "2026-01-06T18:45:00Z",
  "summary": "Completed unit tests for core modules. Integration tests pending due to database setup issues. 45 of 60 planned tests implemented.",
  "details": {
    "tests_implemented": 45,
    "tests_planned": 60,
    "coverage": "73%",
    "passing": 43,
    "failing": 2,
    "modules_covered": [
      "src/spreadsheet_dl/builder.py",
      "src/spreadsheet_dl/formulas/",
      "src/spreadsheet_dl/themes/"
    ],
    "modules_pending": [
      "src/spreadsheet_dl/_mcp/",
      "src/spreadsheet_dl/domains/"
    ]
  },
  "deliverables": [
    "tests/unit/test_builder.py",
    "tests/unit/test_formulas.py",
    "tests/unit/test_themes.py"
  ],
  "next_steps": [
    "Fix 2 failing tests in test_builder.py",
    "Setup test database for integration tests",
    "Implement remaining 15 integration tests"
  ]
}
```

## Usage in Orchestrator

The orchestrator agent uses these completion reports to:

1. **Track Progress**: Monitor status of delegated tasks
2. **Coordinate Workflows**: Determine next agent to spawn based on completion status
3. **Handle Handoffs**: Pass deliverables and context between agents
4. **Detect Blockers**: Identify when tasks are stuck and require intervention
5. **Synthesize Results**: Combine outputs from multiple parallel agents

### Orchestrator Reading Pattern

```python
# Pseudocode for orchestrator reading completion reports
import json

def read_completion_report(task_id):
    path = f".claude/agent-outputs/{task_id}-complete.json"
    with open(path) as f:
        return json.load(f)

def coordinate_next_step(report):
    if report["status"] == "complete":
        return spawn_next_agent(report["next_steps"])
    elif report["status"] == "blocked":
        return escalate_to_user(report["blockers"])
    elif report["status"] == "partial":
        return resume_or_spawn_helper(report)
```

## Best Practices

### DO:

- Write completion reports immediately after finishing work
- Use descriptive task IDs that indicate the work performed
- Include specific, actionable next steps
- Provide detailed findings in the `details` object
- List all deliverables (files created/modified)
- Be honest about status (use "partial" or "blocked" when appropriate)

### DON'T:

- Leave tasks without completion reports
- Use vague or generic summaries
- Omit critical information from details
- Write reports before work is actually done
- Skip the report for "small" tasks
- Change report schema without updating this template

## Validation

Completion reports should be validated against this schema before writing:

```python
# JSON Schema for validation
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["task_id", "agent", "status", "timestamp", "summary", "details"],
  "properties": {
    "task_id": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}-.+$"},
    "agent": {"type": "string"},
    "status": {"type": "string", "enum": ["complete", "partial", "blocked", "failed"]},
    "timestamp": {"type": "string", "format": "date-time"},
    "summary": {"type": "string", "minLength": 10},
    "details": {"type": "object"},
    "deliverables": {"type": "array", "items": {"type": "string"}},
    "next_steps": {"type": "array", "items": {"type": "string"}},
    "blockers": {"type": "array", "items": {"type": "string"}}
  }
}
```

## Maintenance

This template should be updated when:

- New required fields are added to completion reports
- Status values are changed or expanded
- Output file naming convention changes
- Validation schema is modified

**Template Version**: 1.0.0
**Last Updated**: 2026-01-06
**Owner**: orchestrator agent
