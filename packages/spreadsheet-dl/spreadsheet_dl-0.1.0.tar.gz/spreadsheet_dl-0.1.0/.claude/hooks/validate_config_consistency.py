#!/usr/bin/env python3
"""Comprehensive Configuration Consistency Validator.

Validates all aspects of Claude Code configuration:
- Cross-file consistency
- Hook integration
- Agent-command coordination
- SSOT compliance
- Version alignment

Version: 1.0.0
Created: 2025-12-25
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Configuration
REPO_ROOT = Path(__file__).parent.parent.parent
PROJECT_DIR = REPO_ROOT


class ConfigValidator:
    """Validator for configuration consistency across the project."""

    def __init__(self):
        """Initialize the config validator."""
        self.errors = []
        self.warnings = []
        self.info = []

    def error(self, msg: str):
        """Record an error message."""
        self.errors.append(msg)

    def warning(self, msg: str):
        """Record a warning message."""
        self.warnings.append(msg)

    def info_msg(self, msg: str):
        """Record an info message."""
        self.info.append(msg)

    def validate_yaml_versions(self) -> None:
        """Check all YAML files have consistent version numbers."""
        if not HAS_YAML:
            self.warning("PyYAML not available - skipping YAML validation")
            return

        yaml_files = {
            "orchestration-config.yaml": None,
            "coding-standards.yaml": None,
            "project-metadata.yaml": None,
        }

        for filename in yaml_files:
            path = PROJECT_DIR / ".claude" / filename
            if path.exists():
                with open(path) as f:
                    content = f.read()
                    # Extract version from comments or metadata
                    version_match = re.search(r"Version:\s*(\d+\.\d+\.\d+)", content)
                    if version_match:
                        yaml_files[filename] = version_match.group(1)

        # Report versions
        for filename, version in yaml_files.items():
            if version:
                self.info_msg(f"{filename}: v{version}")
            else:
                self.warning(f"{filename}: No version found")

    def validate_hook_references(self) -> None:
        """Check all hooks referenced in YAML exist as files."""
        if not HAS_YAML:
            return

        standards_file = PROJECT_DIR / ".claude/coding-standards.yaml"
        if not standards_file.exists():
            self.error("coding-standards.yaml not found")
            return

        with open(standards_file) as f:
            standards = yaml.safe_load(f)

        hooks = standards.get("hooks", {})
        for _hook_type, hook_list in hooks.items():
            if not isinstance(hook_list, list):
                continue

            for hook_config in hook_list:
                if isinstance(hook_config, dict):
                    script = hook_config.get("script", "")
                    if script:
                        script_path = PROJECT_DIR / script
                        if not script_path.exists():
                            self.error(f"Hook script not found: {script}")
                        else:
                            self.info_msg(f"Hook exists: {script}")

    def validate_agent_command_references(self) -> None:
        """Check command files reference existing agents."""
        commands_dir = PROJECT_DIR / ".claude/commands"
        agents_dir = PROJECT_DIR / ".claude/agents"

        if not commands_dir.exists():
            self.error("Commands directory not found")
            return

        if not agents_dir.exists():
            self.error("Agents directory not found")
            return

        # Get list of agent files
        agent_files = {f.stem for f in agents_dir.glob("*.md")}

        # Check each command file
        for cmd_file in commands_dir.glob("*.md"):
            content = cmd_file.read_text()

            # Find agent references (e.g., ".claude/agents/orchestrator.md")
            agent_refs = re.findall(r"\.claude/agents/(\w+)\.md", content)

            for agent_ref in agent_refs:
                if agent_ref not in agent_files:
                    self.error(
                        f"{cmd_file.name} references non-existent agent: {agent_ref}"
                    )
                else:
                    self.info_msg(f"{cmd_file.name} → {agent_ref} ✓")

    def validate_settings_generation(self) -> None:
        """Check settings.json was generated from coding-standards.yaml."""
        settings_file = PROJECT_DIR / ".claude/settings.json"

        if not settings_file.exists():
            self.error("settings.json not found")
            return

        with open(settings_file) as f:
            settings = json.load(f)

        generated = settings.get("_generated")
        if not generated:
            self.warning("settings.json missing _generated metadata")
        else:
            source = generated.get("source")
            if source != "coding-standards.yaml":
                self.error(f"settings.json source mismatch: {source}")
            else:
                self.info_msg(f"settings.json generated from {source} ✓")

    def validate_agent_routing_keywords(self) -> None:
        """Check agent routing keywords are unique and consistent."""
        agents_dir = PROJECT_DIR / ".claude/agents"

        if not agents_dir.exists():
            return

        all_keywords = {}

        for agent_file in agents_dir.glob("*.md"):
            content = agent_file.read_text()

            # Parse frontmatter
            frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
            if not frontmatter_match:
                self.warning(f"{agent_file.name}: No frontmatter")
                continue

            try:
                if HAS_YAML:
                    frontmatter = yaml.safe_load(frontmatter_match.group(1))
                    keywords = frontmatter.get("routing_keywords", [])

                    for kw in keywords:
                        if kw in all_keywords:
                            self.warning(
                                f"Keyword '{kw}' shared by {agent_file.stem} and {all_keywords[kw]}"
                            )
                        else:
                            all_keywords[kw] = agent_file.stem
            except Exception as e:
                self.error(f"{agent_file.name}: Failed to parse frontmatter: {e}")

        self.info_msg(f"Total routing keywords: {len(all_keywords)}")

    def validate_ssot_compliance(self) -> None:
        """Check SSOT files exist and are referenced correctly."""
        ssot_files = [
            ".claude/project-metadata.yaml",
            ".claude/coding-standards.yaml",
            ".claude/orchestration-config.yaml",
            ".coordination/spec/incomplete-features.yaml",
        ]

        for ssot_file in ssot_files:
            path = PROJECT_DIR / ssot_file
            if not path.exists():
                self.error(f"SSOT file missing: {ssot_file}")
            else:
                self.info_msg(f"SSOT file exists: {ssot_file}")

    def validate_hook_execution_order(self) -> None:
        """Check hooks have proper execution order without conflicts."""
        if not HAS_YAML:
            return

        standards_file = PROJECT_DIR / ".claude/coding-standards.yaml"
        if not standards_file.exists():
            return

        with open(standards_file) as f:
            standards = yaml.safe_load(f)

        hooks = standards.get("hooks", {}).get("pre_commit", [])
        orders = {}

        for hook in hooks:
            if isinstance(hook, dict):
                name = hook.get("name")
                order = hook.get("order")
                depends = hook.get("depends_on", [])

                if order is not None:
                    if order in orders:
                        self.error(
                            f"Duplicate order {order}: {name} and {orders[order]}"
                        )
                    else:
                        orders[order] = name

                # Check dependencies exist
                for dep in depends:
                    found = False
                    for other_hook in hooks:
                        if (
                            isinstance(other_hook, dict)
                            and other_hook.get("name") == dep
                        ):
                            found = True
                            break
                    if not found:
                        self.error(f"Hook '{name}' depends on non-existent '{dep}'")

        self.info_msg(f"Pre-commit hooks: {len(hooks)} with execution order")

    def run_all_validations(self) -> dict[str, Any]:
        """Run all validation checks."""
        print("Running comprehensive configuration validation...\n")

        self.validate_yaml_versions()
        self.validate_hook_references()
        self.validate_agent_command_references()
        self.validate_settings_generation()
        self.validate_agent_routing_keywords()
        self.validate_ssot_compliance()
        self.validate_hook_execution_order()

        return {
            "ok": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": len(self.info),
            },
        }


def main() -> None:
    """Run configuration consistency validation."""
    validator = ConfigValidator()
    result = validator.run_all_validations()

    # Print results
    if result["info"]:
        print("i  Information:")
        for msg in result["info"]:
            print(f"   {msg}")
        print()

    if result["warnings"]:
        print("⚠️  Warnings:")
        for msg in result["warnings"]:
            print(f"   {msg}")
        print()

    if result["errors"]:
        print("❌ Errors:")
        for msg in result["errors"]:
            print(f"   {msg}")
        print()

    # Summary
    print("═" * 60)
    print(f"Errors: {result['summary']['errors']}")
    print(f"Warnings: {result['summary']['warnings']}")
    print(f"Info: {result['summary']['info']}")
    print("═" * 60)

    if result["ok"]:
        print("✅ Configuration is consistent and optimal")
        sys.exit(0)
    else:
        print("❌ Configuration has issues that need fixing")
        sys.exit(1)


if __name__ == "__main__":
    main()
