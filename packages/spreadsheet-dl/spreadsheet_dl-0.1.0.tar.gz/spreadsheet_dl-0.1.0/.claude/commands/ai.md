---
name: ai
description: Universal AI routing to specialized agents
arguments: <task>
---

# AI Task Orchestration

Route any task to the orchestrator for intelligent agent selection and workflow coordination.

## Usage

```bash
/ai <task description>
```

## Examples

```bash
/ai research Docker networking best practices
/ai implement TASK-001 from the task graph
/ai organize the knowledge directory
/ai comprehensive analysis of authentication options
```

## Process

1. Invoke orchestrator agent with full task context
2. Orchestrator parses intent and assesses complexity
3. Orchestrator discovers available agents dynamically
4. Routes to appropriate specialist(s)
5. For multi-step tasks, coordinates workflow via completion reports

## Multi-Agent Triggers

Keywords that trigger multi-agent workflows:

- "comprehensive" - Full coverage requiring multiple specialists
- "multiple" - Explicitly requesting diverse perspectives
- "various" - Different aspects or approaches
- "full" - Complete analysis or implementation
- "research and implement" - Cross-domain workflow

## Notes

- All tasks flow through orchestrator for consistent routing
- Complex tasks automatically decomposed into phases
- Completion reports track progress and enable handoffs

## See Also

- `.claude/agents/orchestrator.md` - Primary agent handling this command
- `/swarm` - For explicitly parallel workflows
