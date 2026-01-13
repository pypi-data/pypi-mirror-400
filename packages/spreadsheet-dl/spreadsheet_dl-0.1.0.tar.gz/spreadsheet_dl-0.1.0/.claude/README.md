# Claude Code Configuration

This directory contains configuration for [Claude Code](https://docs.anthropic.com/claude-code), Anthropic's AI-powered CLI development assistant.

## Directory Structure

```
.claude/
├── agents/                     # Specialized agent definitions
│   ├── orchestrator.md         # Task routing, workflow coordination
│   ├── git_commit_manager.md   # Conventional commits
│   ├── spec_implementer.md     # Implement from specifications
│   ├── spec_validator.md       # Validate against criteria
│   └── references/             # Supporting documentation
│       └── git-commit-examples.md
├── commands/                   # Custom slash commands
│   ├── ai.md                   # Universal AI routing
│   ├── git.md                  # Git workflow
│   ├── implement.md            # Spec implementation
│   ├── spec.md                 # Specification utilities
│   └── swarm.md                # Parallel execution
├── hooks/                      # Lifecycle automation
│   └── README.md               # Hook documentation
├── templates/                  # Schema and format templates
│   ├── docstring.md            # Docstring format
│   ├── agent_output_rules.md   # Completion report format
│   └── spec/                   # Specification schemas
├── agent-outputs/              # Completion reports
├── checkpoints/                # Task checkpoints
├── summaries/                  # Agent output summaries
├── settings.json               # Claude Code settings
├── orchestration-config.yaml   # Swarm coordination config
├── coding-standards.yaml       # Code quality standards
├── project-metadata.yaml       # Project metadata
├── paths.yaml                  # Centralized path definitions
├── agent-registry.json         # Running agent state
└── README.md                   # This file
```

## Quick Start

If you use Claude Code, these configurations are automatically loaded:

```bash
# Route any task to the right agent
/ai implement the authentication feature

# Smart conventional commits
/git

# Parallel analysis
/swarm comprehensive security review
```

## For Non-Claude Code Users

You can safely ignore this directory. All configurations are optional and won't affect:

- Standard development workflows
- CI/CD pipelines
- Testing or linting
- Building or packaging

## Key Features

### Agents

Specialized AI agents for different tasks:

- **orchestrator** - Routes tasks, coordinates multi-agent workflows
- **git_commit_manager** - Conventional commits, atomic history
- **spec_implementer** - Implements from specifications
- **spec_validator** - Validates against acceptance criteria

### Commands

Custom slash commands for common workflows:

- `/ai` - Universal task routing
- `/git` - Smart commit automation
- `/implement` - Spec-driven implementation
- `/spec` - Specification management
- `/swarm` - Parallel agent coordination

### Hooks

Automated quality gates and lifecycle management:

- Security validation (blocks sensitive file writes)
- Quality enforcement (auto-linting, type checks)
- Agent limit enforcement (max 2 parallel agents)
- Context management (cleanup, checkpointing)

## Configuration Files

| File                        | Purpose                              |
| --------------------------- | ------------------------------------ |
| `settings.json`             | Claude Code behavior and permissions |
| `orchestration-config.yaml` | Agent swarm configuration            |
| `coding-standards.yaml`     | Code quality standards               |
| `project-metadata.yaml`     | Project metadata                     |
| `paths.yaml`                | Centralized path definitions         |
| `agent-registry.json`       | Running agent state tracking         |

## Learn More

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Custom Commands](https://docs.anthropic.com/claude-code/commands)
- [Hooks Documentation](./hooks/README.md)
- [Contrib Documentation](../contrib/claude-config/README.md) - Comprehensive setup guide
