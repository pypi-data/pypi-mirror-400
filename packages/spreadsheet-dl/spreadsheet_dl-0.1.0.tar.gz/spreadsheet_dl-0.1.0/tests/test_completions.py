"""
Tests for Shell Completions Module.

: Shell Completions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from spreadsheet_dl.completions import (
    COMMAND_STRUCTURE,
    detect_shell,
    generate_bash_completions,
    generate_fish_completions,
    generate_zsh_completions,
    get_installation_instructions,
    install_completions,
    print_completion_script,
)

pytestmark = [pytest.mark.unit, pytest.mark.mcp]


class TestCommandStructure:
    """Tests for command structure definition."""

    def test_structure_not_empty(self) -> None:
        """Test command structure is defined."""
        assert len(COMMAND_STRUCTURE) > 0

    def test_required_commands_defined(self) -> None:
        """Test required commands are present."""
        required = ["generate", "expense", "analyze", "report", "import", "upload"]
        for cmd in required:
            assert cmd in COMMAND_STRUCTURE, f"Missing command: {cmd}"

    def test_commands_have_descriptions(self) -> None:
        """Test all commands have descriptions."""
        for cmd, info in COMMAND_STRUCTURE.items():
            assert "description" in info, f"Missing description for {cmd}"

    def test_options_have_types(self) -> None:
        """Test options have type definitions."""
        for cmd, info in COMMAND_STRUCTURE.items():
            if "options" in info:
                for opt, opt_info in info["options"].items():
                    assert "type" in opt_info, f"Missing type for {cmd} {opt}"


class TestBashCompletions:
    """Tests for Bash completion generation."""

    def test_generate_bash_script(self) -> None:
        """Test Bash script generation."""
        script = generate_bash_completions()

        # Check basic structure
        assert "_spreadsheet_dl_completions()" in script
        assert "complete -F _spreadsheet_dl_completions spreadsheet-dl" in script

    def test_bash_includes_commands(self) -> None:
        """Test Bash script includes all commands."""
        script = generate_bash_completions()

        for cmd in COMMAND_STRUCTURE:
            assert cmd in script

    def test_bash_includes_options(self) -> None:
        """Test Bash script includes common options."""
        script = generate_bash_completions()

        assert "--file" in script
        assert "--output" in script
        assert "--template" in script
        assert "--theme" in script

    def test_bash_file_completion(self) -> None:
        """Test Bash script handles file completions."""
        script = generate_bash_completions()

        # Should use _filedir for file options
        assert "_filedir" in script

    def test_bash_choice_completion(self) -> None:
        """Test Bash script handles choice options."""
        script = generate_bash_completions()

        # Should include template choices
        assert "50_30_20" in script
        assert "family" in script


class TestZshCompletions:
    """Tests for Zsh completion generation."""

    def test_generate_zsh_script(self) -> None:
        """Test Zsh script generation."""
        script = generate_zsh_completions()

        # Check basic structure
        assert "#compdef spreadsheet-dl" in script
        assert "_spreadsheet_dl()" in script

    def test_zsh_includes_commands(self) -> None:
        """Test Zsh script includes all commands."""
        script = generate_zsh_completions()

        for cmd in COMMAND_STRUCTURE:
            assert cmd in script

    def test_zsh_command_descriptions(self) -> None:
        """Test Zsh script includes command descriptions."""
        script = generate_zsh_completions()

        # Should have command:description format
        assert "generate:" in script
        assert "expense:" in script

    def test_zsh_per_command_functions(self) -> None:
        """Test Zsh generates per-command completion functions."""
        script = generate_zsh_completions()

        # Should have _spreadsheet_dl_<cmd> functions
        assert "_spreadsheet_dl_generate()" in script
        assert "_spreadsheet_dl_expense()" in script

    def test_zsh_option_descriptions(self) -> None:
        """Test Zsh script includes option descriptions."""
        script = generate_zsh_completions()

        # Options should have descriptions
        assert "--file[" in script
        assert "--template[" in script


class TestFishCompletions:
    """Tests for Fish completion generation."""

    def test_generate_fish_script(self) -> None:
        """Test Fish script generation."""
        script = generate_fish_completions()

        # Check basic structure
        assert "complete -c spreadsheet-dl" in script

    def test_fish_includes_commands(self) -> None:
        """Test Fish script includes all commands."""
        script = generate_fish_completions()

        for cmd in COMMAND_STRUCTURE:
            assert f"-a '{cmd}'" in script

    def test_fish_command_descriptions(self) -> None:
        """Test Fish script includes command descriptions."""
        script = generate_fish_completions()

        # Should have -d 'description' format
        assert "-d 'Generate a new budget spreadsheet'" in script

    def test_fish_subcommand_completions(self) -> None:
        """Test Fish script handles subcommands."""
        script = generate_fish_completions()

        # Should have conditional completions for subcommands
        assert "__fish_seen_subcommand_from" in script


class TestShellDetection:
    """Tests for shell detection."""

    @patch.dict("os.environ", {"SHELL": "/bin/bash"})
    def test_detect_bash(self) -> None:
        """Test detecting Bash shell."""
        assert detect_shell() == "bash"

    @patch.dict("os.environ", {"SHELL": "/usr/bin/zsh"})
    def test_detect_zsh(self) -> None:
        """Test detecting Zsh shell."""
        assert detect_shell() == "zsh"

    @patch.dict("os.environ", {"SHELL": "/usr/bin/fish"})
    def test_detect_fish(self) -> None:
        """Test detecting Fish shell."""
        assert detect_shell() == "fish"

    @patch.dict("os.environ", {"SHELL": ""})
    def test_default_to_bash(self) -> None:
        """Test defaulting to Bash when unknown."""
        # Mock the /proc check to fail
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert detect_shell() == "bash"


class TestInstallCompletions:
    """Tests for completion installation."""

    def test_install_returns_result(self) -> None:
        """Test install returns result dict."""
        result = install_completions("bash")

        assert "shell" in result
        assert "success" in result
        assert "message" in result

    def test_unsupported_shell(self) -> None:
        """Test error for unsupported shell."""
        result = install_completions("unsupported")

        assert result["success"] is False
        assert "Unsupported" in result["message"]

    @patch("spreadsheet_dl.completions._install_bash_completions")
    def test_install_calls_correct_function(self, mock_install: Any) -> None:
        """Test install calls correct shell function."""
        mock_install.return_value = Path("/test/path")

        result = install_completions("bash")

        mock_install.assert_called_once()
        assert result["success"] is True


class TestPrintCompletionScript:
    """Tests for script printing."""

    def test_print_bash(self) -> None:
        """Test printing Bash script."""
        script = print_completion_script("bash")
        assert "_spreadsheet_dl_completions" in script

    def test_print_zsh(self) -> None:
        """Test printing Zsh script."""
        script = print_completion_script("zsh")
        assert "#compdef" in script

    def test_print_fish(self) -> None:
        """Test printing Fish script."""
        script = print_completion_script("fish")
        assert "complete -c spreadsheet-dl" in script

    def test_print_unsupported(self) -> None:
        """Test error for unsupported shell."""
        with pytest.raises(ValueError, match="Unsupported shell"):
            print_completion_script("unsupported")


class TestInstallationInstructions:
    """Tests for installation instructions."""

    def test_bash_instructions(self) -> None:
        """Test Bash installation instructions."""
        instructions = get_installation_instructions("bash")

        assert "Bash" in instructions
        assert ".bashrc" in instructions
        assert "bash_completion" in instructions

    def test_zsh_instructions(self) -> None:
        """Test Zsh installation instructions."""
        instructions = get_installation_instructions("zsh")

        assert "Zsh" in instructions
        assert ".zshrc" in instructions
        assert "fpath" in instructions

    def test_fish_instructions(self) -> None:
        """Test Fish installation instructions."""
        instructions = get_installation_instructions("fish")

        assert "Fish" in instructions
        assert ".config/fish/completions" in instructions

    def test_unknown_shell_instructions(self) -> None:
        """Test unknown shell instructions."""
        instructions = get_installation_instructions("unknown")
        assert "Unknown shell" in instructions
