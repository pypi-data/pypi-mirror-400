# Claude Context: SpreadsheetDL

Universal spreadsheet definition language with LLM-optimized MCP server

## Project Information

**Repository Type**: Application/Library
**Composition**: base, implementation
**Language**: python

## Configuration Authority

**Single Source of Truth (SSOT)**: All configuration is authoritative in the locations below. When modifying, edit these files directly:

| Resource | Location                | Notes                              |
| -------- | ----------------------- | ---------------------------------- |
| Agents   | `.claude/agents/*.md`   | Agent definitions with frontmatter |
| Commands | `.claude/commands/*.md` | Slash command definitions          |
| Settings | `.claude/settings.json` | Claude Code settings, hooks        |
| Scripts  | `scripts/README.md`     | Script documentation and reference |

This CLAUDE.md file is a high-level overview. For detailed documentation, see the authoritative sources above.

## Philosophy

- Simplest solution that works. Complexity must justify itself.
- Apply 80/20 principle: Focus on core 20% delivering 80% value
- Single source of truth for all configuration
- Hub-and-spoke architecture: All coordination through orchestrator
- Completion reports for all agent work

## Structure

```
.claude/                # Agent and command definitions
.claude/agents/         # Agent markdown files
.claude/commands/       # Command markdown files
.claude/agent-outputs/  # Completion reports (JSON)
.coordination/          # Task state and intermediate files
```

## Commands

```bash
/ai                  # Universal AI routing to specialized agents
/git                 # Smart atomic commits with conventional format
/swarm               # Execute complex tasks with parallel agent coordination
/implement           # Implement tasks from spec with automatic validation
/spec                # Specification workflow utilities
```

## Agent Roster (4 Agents)

| Agent              | Purpose                                                                                                                               | When to Use                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| orchestrator       | Route tasks to specialists or coordinate multi-agent workflows. Central hub for all inter-agent communication via completion reports. | route, coordinate, delegate |
| git_commit_manager | Manage git operations with conventional commits and atomic, well-organized history.                                                   | git, commit, push           |
| spec_implementer   | Implement tasks from task-graph according to requirements. Trace all implementations to requirement IDs.                              | implement, code, build      |
| spec_validator     | Validate implementations against acceptance criteria from validation manifest. Map test results to requirements.                      | test, pytest, validate      |

## Development Tools

**Always use `uv`** - never system Python or pip.

```bash
uv sync                    # Install dependencies
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy .              # Type check
uv run pytest              # Test
uv run python script.py    # Run scripts
```

**Adding dependencies**:

```bash
uv add package             # Add runtime dependency
uv add --dev package       # Add dev dependency
```

## Available Scripts

Quality and maintenance scripts are available in `scripts/`. Use these for code quality workflows:

### Quality Scripts

| Script              | Purpose                                   | When to Use                               |
| ------------------- | ----------------------------------------- | ----------------------------------------- |
| `scripts/check.sh`  | Quick quality check (lint + format check) | Before commits, after significant changes |
| `scripts/lint.sh`   | Run all configured linters                | When checking for issues                  |
| `scripts/format.sh` | Format all code files                     | When formatting is needed                 |
| `scripts/clean.sh`  | Clean build artifacts and caches          | When builds are stale                     |
| `scripts/doctor.sh` | Environment health check                  | When tools seem broken                    |

### Maintenance Scripts

| Script                                        | Purpose                        | When to Use                 |
| --------------------------------------------- | ------------------------------ | --------------------------- |
| `scripts/maintenance/archive_coordination.sh` | Archive old coordination files | Periodically (>30 days old) |

### Tool Wrappers

Individual tool scripts in `scripts/tools/` provide consistent interfaces:

```bash
scripts/tools/<tool>.sh [--check|--json|-v] [paths...]
```

Common options: `--check` (dry-run), `--json` (machine output), `-v` (verbose)

**Python**: `ruff.sh`, `mypy.sh`
**Universal**: `markdownlint.sh`, `prettier.sh`, `shellcheck.sh`, `yamllint.sh`
**Diagrams**: `mermaid.sh`, `plantuml.sh`

## Autonomous Work Mode

Claude works autonomously through the agent roster until tasks are fully complete:

- **Multi-step tasks** are automatically decomposed and coordinated
- **Specialists communicate** via completion reports (never directly)
- **Work continues** until Definition of Done criteria are met
- **Quality validation** occurs before marking complete

### Continuous Operation (CRITICAL)

**DO NOT STOP** until the workflow is fully complete:

1. After spawning agents, **actively monitor** their completion reports
2. When an agent completes, **immediately check** its report and spawn the next agent
3. Continue the **execution loop** until all phases are done
4. Only stop when Definition of Done is met or user explicitly requests stop
5. If blocked, report status and **wait for user input** rather than stopping

**State Management**: Update `active_work.json` at workflow start (`status: "in_progress"`) and end (`status: "complete"`).

### Parallel Workflows

Keywords "comprehensive", "multiple", "various" trigger parallel agent dispatch via `/swarm`.

## Workflow Examples

### Serial: Research → Document → Organize

```bash
/ai research Docker networking and create tutorial
# Routes: knowledge_researcher → technical_writer → note_organizer
```

### Parallel: Comprehensive Analysis

```bash
/swarm comprehensive security analysis with multiple perspectives
# Spawns parallel agents, synthesizes results
```

### Spec-Driven Implementation

```bash
/spec extract requirements.md
/implement phase 1
/git
```

## Context Management

- **Proactive compaction**: At 70% context capacity or workflow breakpoints
- **Preserve**: Architectural decisions, progress, constraints, dependencies
- **Drop**: Verbose tool outputs, exploration paths, resolved debugging

Manual compaction with focus:

```bash
/compact "Focus on: decisions made, implementation progress, remaining tasks"
```

## State Tracking

| File                           | Purpose                                   |
| ------------------------------ | ----------------------------------------- |
| `active_work.json`             | Current task (check before new work)      |
| `.claude/agent-outputs/*.json` | Completion reports (read before handoffs) |
| `.coordination/checkpoints/`   | Long-running task state                   |

**On interruption**: Resume from last checkpoint or completion report.

## Quality Standards

- Code examples must be tested
- All implementations trace to requirements
- Validation tests map to acceptance criteria
- Dependencies verified before implementation

## Versioning Policy

SpreadsheetDL follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (x.0.0) - Breaking changes to public API
- **MINOR** (0.x.0) - New features, backwards compatible
- **PATCH** (0.1.x) - Bug fixes, backwards compatible

**Compatibility Commitment:**

- Public API stability guaranteed within major versions
- Deprecation warnings provided one minor version before removal
- Breaking changes only in major version releases
- Internal APIs (prefixed with `_`) may change in minor versions

## Anti-Patterns

Never:

- Over-engineer solutions
- Create files without reading existing content first
- Skip validation before completion
- Leave intermediate files in project directories
- Direct worker-to-worker communication
- Hardcoded routing tables
- Commit without conventional format

## Coordination

**Intermediate files**: `.coordination/YYYY-MM-DD-description.md`
**Completion reports**: `.claude/agent-outputs/[task-id]-complete.json`
**Final artifacts only**: Project directories (not .coordination/)

## Maintenance

- Archive coordination files >30 days old
- Run validation after significant changes
- Review agent coverage for new domains
