# Claude Code Configuration Templates

This directory documents the Claude Code configuration used in SpreadsheetDL development. The actual configuration lives in `.claude/` at the project root.

## Quick Start

The configuration is ready to use out of the box:

```bash
# Route any task to the appropriate agent
/ai implement the authentication feature

# Smart conventional commits
/git

# Parallel agent coordination
/swarm comprehensive security review
```

## Directory Structure

```
.claude/
├── agents/                     # Agent definitions (4 total)
│   ├── orchestrator.md         # Task routing, workflow coordination
│   ├── git_commit_manager.md   # Conventional commits
│   ├── spec_implementer.md     # Implement from specifications
│   ├── spec_validator.md       # Validate against criteria
│   └── references/             # Supporting documentation
│       └── git-commit-examples.md
├── commands/                   # Slash commands (5 total)
│   ├── ai.md                   # Universal AI routing
│   ├── git.md                  # Git workflow
│   ├── implement.md            # Spec implementation
│   ├── spec.md                 # Specification utilities
│   └── swarm.md                # Parallel execution
├── hooks/                      # Lifecycle automation
│   ├── README.md               # Hook documentation
│   ├── enforce_agent_limit.py  # PreToolUse: Max 2 agents
│   ├── validate_path.py        # PreToolUse: Security validation
│   ├── quality_enforce_strict.py # PostToolUse: Quality gates
│   ├── check_subagent_stop.py  # SubagentStop: Completion check
│   ├── check_stop.py           # Stop: Task completion check
│   ├── cleanup_stale_agents.py # SessionStart: Registry cleanup
│   ├── pre_compact_cleanup.sh  # PreCompact: Archive old files
│   ├── post_compact_recovery.sh # SessionStart: Recovery check
│   ├── session_cleanup.sh      # SessionEnd: Temp file cleanup
│   └── rotate_logs.sh          # SessionStart: Log rotation
├── templates/                  # Schema templates
│   ├── docstring.md            # Docstring format
│   ├── agent_output_rules.md   # Completion report format
│   └── spec/                   # Specification schemas
│       ├── requirements_schema.yaml
│       ├── task_graph_schema.yaml
│       └── validation_manifest_schema.yaml
├── agent-outputs/              # Completion reports
├── checkpoints/                # Task checkpoints
├── summaries/                  # Agent output summaries
├── settings.json               # Claude Code settings
├── orchestration-config.yaml   # Swarm coordination config
├── coding-standards.yaml       # Code quality standards
├── project-metadata.yaml       # Project metadata
├── paths.yaml                  # Centralized path definitions
├── agent-registry.json         # Running agent state
└── README.md                   # Configuration overview
```

## Configuration Files

### settings.json

Core Claude Code configuration including permissions, hooks, and environment:

```json
{
  "model": "sonnet",
  "cleanupPeriodDays": 30,
  "env": {
    "BASH_DEFAULT_TIMEOUT_MS": "60000"
  },
  "permissions": {
    "allow": [
      "Bash(uv:*)",
      "Bash(pytest:*)",
      "Bash(ruff:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)"
    ],
    "deny": [
      "Read(./.git/**)",
      "Read(./.venv/**)",
      "Write(./.claude/settings.json)",
      "Write(**/.env*)",
      "Write(**/*.key)",
      "Bash(pip:*)"
    ],
    "defaultMode": "bypassPermissions"
  },
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "PreCompact": [...],
    "SessionStart": [...],
    "SessionEnd": [...],
    "Stop": [...],
    "SubagentStop": [...]
  }
}
```

### Agent Definition Format

Agent files in `.claude/agents/` use YAML frontmatter + Markdown body:

```markdown
---
name: agent_name
description: 'Brief description of agent purpose'
tools: Read, Write, Edit, Bash, Grep, Glob, Task
model: sonnet
routing_keywords:
  - keyword1
  - keyword2
  - keyword3
---

# Agent Name

Full instructions for the agent...

## Triggers

When this agent should be invoked...

## Process

Step-by-step workflow...

## Anti-patterns

What NOT to do...

## Definition of Done

Completion criteria...

## Completion Report Format

JSON schema for output...
```

### Command Definition Format

Command files in `.claude/commands/` use similar frontmatter:

```markdown
---
name: commandname
description: What the command does
arguments: <required> [optional]
---

# Command Name

Instructions that run when `/commandname` is invoked...

## Usage

\`\`\`bash
/commandname arg1 arg2
\`\`\`

## Examples

...

## See Also

Related commands and agents...
```

## Hook System

Hooks automate quality enforcement and lifecycle management:

| Hook Type    | Purpose                   | Blocking |
| ------------ | ------------------------- | -------- |
| PreToolUse   | Validate before execution | Yes      |
| PostToolUse  | Process after execution   | Yes      |
| PreCompact   | Cleanup before compaction | No       |
| SessionStart | Initialize/recover        | No       |
| SessionEnd   | Cleanup on exit           | No       |
| Stop         | Handle shutdown           | No       |
| SubagentStop | Handle agent completion   | No       |

### Active Hooks

**Security & Validation (PreToolUse)**:

- `validate_path.py` - Block writes to sensitive files (.env, .key, credentials)
- `enforce_agent_limit.py` - Limit parallel agents to 2 max

**Quality Enforcement (PostToolUse)**:

- `quality_enforce_strict.py` - Auto-format and lint all written files

**Context Management**:

- `pre_compact_cleanup.sh` - Archive old coordination files
- `post_compact_recovery.sh` - Verify critical files after compaction
- `cleanup_stale_agents.py` - Mark abandoned agents as failed
- `session_cleanup.sh` - Clean temp files on session end
- `rotate_logs.sh` - Prevent log file growth

**Agent Coordination**:

- `check_stop.py` - Verify task completion before stopping
- `check_subagent_stop.py` - Validate subagent completion reports

### Hook Input/Output Format

Hooks receive JSON on stdin:

```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "content": "..."
  }
}
```

Hooks return JSON on stdout:

```json
{
  "decision": "allow", // or "block"
  "reason": "Optional explanation"
}
```

Exit codes: 0 = allow, non-zero = block (for blocking hooks)

## Orchestration System

### Agent Registry

`.claude/agent-registry.json` tracks running agents:

```json
{
  "version": "2.0.0",
  "agents": {
    "agent-id-123": {
      "status": "running",
      "task_description": "Implementing feature X",
      "launched_at": "2026-01-06T12:00:00Z"
    }
  },
  "metadata": {
    "agents_running": 1,
    "agents_completed": 5,
    "last_cleanup": "2026-01-06T11:00:00Z"
  }
}
```

### Orchestration Config

`.claude/orchestration-config.yaml` controls swarm behavior:

```yaml
swarm:
  max_batch_size: 2
  max_parallel_agents: 2
  poll_interval_seconds: 10
  immediate_retrieval: true

context_management:
  warning_threshold_percent: 60
  critical_threshold_percent: 75
  checkpoint_threshold_percent: 65
```

### Completion Reports

Agents write completion reports to `.claude/agent-outputs/`:

```json
{
  "task_id": "2026-01-06-120000-implement-feature",
  "agent": "spec_implementer",
  "status": "complete",
  "summary": "Implemented authentication feature...",
  "deliverables": ["src/auth.py", "tests/test_auth.py"],
  "next_steps": ["Run validation tests"],
  "completed_at": "2026-01-06T12:30:00Z"
}
```

## Customization

### Adding a New Agent

1. Create `.claude/agents/your_agent.md`
2. Add frontmatter with `name`, `description`, `tools`, `model`, `routing_keywords`
3. Write instructions in markdown body
4. Include: Triggers, Process, Anti-patterns, Definition of Done, Completion Report Format

### Adding a New Command

1. Create `.claude/commands/your_command.md`
2. Add frontmatter with `name`, `description`, `arguments`
3. Write usage instructions and examples

### Adding a New Hook

1. Create hook script in `.claude/hooks/`
2. Make executable: `chmod +x .claude/hooks/your_hook.py`
3. Register in `.claude/settings.json` under appropriate hook type
4. Document in `.claude/hooks/README.md`

### Modifying Permissions

Edit `.claude/settings.json` permissions section:

```json
{
  "permissions": {
    "allow": ["Bash(your-command:*)"],
    "deny": ["Write(**/sensitive-pattern)"]
  }
}
```

## Disabling Features

### Bypass All Hooks

```bash
export CLAUDE_BYPASS_HOOKS=1
```

### Disable Specific Hook

Edit `.claude/settings.json` and remove the hook from its section.

### Disable Quality Enforcement

Remove `quality_enforce_strict.py` from PostToolUse hooks in settings.json.

## Troubleshooting

### Hooks Not Running

```bash
# Check file permissions
chmod +x .claude/hooks/*.sh .claude/hooks/*.py

# Check Python availability
python3 --version

# Check hook logs
cat .claude/hooks/errors.log
```

### Agent Not Found

1. Verify file exists: `ls -la .claude/agents/`
2. Check frontmatter syntax (YAML between `---` markers)
3. Verify `routing_keywords` match your intent
4. Check for syntax errors in YAML frontmatter

### Command Not Working

1. Verify file exists: `ls -la .claude/commands/`
2. Check frontmatter `name` matches command name
3. Try `/help` to see available commands

### Quality Check Failures

```bash
# Check what quality issues exist
uv run ruff check path/to/file.py
uv run mypy path/to/file.py

# Auto-fix issues
uv run ruff check --fix path/to/file.py
uv run ruff format path/to/file.py
```

### Agent Limit Reached

The system enforces max 2 parallel agents. If blocked:

1. Check `.claude/agent-registry.json` for running agents
2. Wait for agents to complete
3. Or manually reset registry if agents are stale

### Context Compaction Issues

If work is lost after compaction:

1. Check `.claude/checkpoints/` for saved state
2. Read `.claude/agent-registry.json` for agent status
3. Look for completion reports in `.claude/agent-outputs/`
4. Check `.claude/summaries/` for agent output summaries

## Best Practices

1. **Keep agents focused** - One agent per domain/capability
2. **Use frontmatter keywords** - Enables dynamic routing
3. **Write completion reports** - Enables agent handoffs
4. **Test hooks locally** - Before committing changes
5. **Monitor context usage** - Checkpoint at 65-70% capacity
6. **Use batch execution** - Max 2 parallel agents
7. **Retrieve outputs immediately** - Don't wait for all agents

## Setup Script

Reset to defaults using the setup script:

```bash
# View current configuration
./scripts/setup_claude_config.sh

# Reset with full hook infrastructure
./scripts/setup_claude_config.sh --full --force
```

## Reference Documentation

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Custom Commands](https://docs.anthropic.com/claude-code/commands)
- [Hooks Documentation](.claude/hooks/README.md)
- [Main Project README](../../README.md)
- [CLAUDE.md](../../CLAUDE.md) - Project-specific instructions
