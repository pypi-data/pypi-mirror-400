"""Shell Completions Module.

Provides tab completion scripts for Bash, Zsh, and Fish shells.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Command structure for completions
COMMAND_STRUCTURE: dict[str, dict[str, Any]] = {
    "generate": {
        "description": "Generate a new budget spreadsheet",
        "options": {
            "--month": {"type": "int", "description": "Month number (1-12)"},
            "--year": {"type": "int", "description": "Year"},
            "--output": {"type": "file", "description": "Output file path"},
            "--template": {
                "type": "choice",
                "choices": [
                    "50_30_20",
                    "family",
                    "minimalist",
                    "zero_based",
                    "fire",
                    "high_income",
                ],
                "description": "Budget template",
            },
            "--theme": {
                "type": "choice",
                "choices": ["default", "corporate", "minimal", "dark", "high_contrast"],
                "description": "Visual theme",
            },
            "--income": {"type": "float", "description": "Monthly income"},
        },
    },
    "expense": {
        "description": "Add a quick expense entry",
        "options": {
            "--file": {"type": "file", "description": "ODS file to update"},
            "--date": {"type": "date", "description": "Expense date (YYYY-MM-DD)"},
            "--category": {
                "type": "choice",
                "choices": [
                    "housing",
                    "utilities",
                    "groceries",
                    "transportation",
                    "healthcare",
                    "insurance",
                    "entertainment",
                    "dining_out",
                    "clothing",
                    "personal_care",
                    "education",
                    "savings",
                    "debt_payment",
                    "gifts",
                    "subscriptions",
                    "miscellaneous",
                ],
                "description": "Expense category",
            },
            "--amount": {"type": "float", "description": "Amount"},
            "--description": {"type": "string", "description": "Description"},
            "--dry-run": {"type": "flag", "description": "Preview without saving"},
        },
    },
    "analyze": {
        "description": "Analyze budget spending",
        "options": {
            "--file": {"type": "file", "description": "ODS file to analyze"},
            "--format": {
                "type": "choice",
                "choices": ["text", "json", "markdown"],
                "description": "Output format",
            },
        },
    },
    "report": {
        "description": "Generate spending report",
        "options": {
            "--file": {"type": "file", "description": "ODS file"},
            "--format": {
                "type": "choice",
                "choices": ["text", "markdown", "json"],
                "description": "Report format",
            },
            "--output": {"type": "file", "description": "Output file"},
        },
    },
    "import": {
        "description": "Import bank transactions",
        "options": {
            "--bank": {
                "type": "choice",
                "choices": [
                    "chase",
                    "chase_credit",
                    "bank_of_america",
                    "wells_fargo",
                    "capital_one",
                    "discover",
                    "amex",
                    "usaa",
                    "generic",
                ],
                "description": "Bank format",
            },
            "--output": {"type": "file", "description": "Output ODS file"},
            "--append": {"type": "file", "description": "Append to existing file"},
            "--categorize": {"type": "flag", "description": "Auto-categorize"},
        },
    },
    "upload": {
        "description": "Upload to Nextcloud",
        "options": {
            "--remote-path": {"type": "string", "description": "Remote directory"},
        },
    },
    "templates": {
        "description": "List available budget templates",
        "options": {
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "themes": {
        "description": "List available themes",
        "options": {
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "config": {
        "description": "Manage configuration",
        "subcommands": {
            "show": {"description": "Show current configuration"},
            "init": {"description": "Initialize configuration file"},
            "set": {"description": "Set a configuration value"},
            "get": {"description": "Get a configuration value"},
        },
        "options": {
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "alerts": {
        "description": "Check budget alerts",
        "options": {
            "--file": {"type": "file", "description": "ODS file"},
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "dashboard": {
        "description": "Generate analytics dashboard",
        "options": {
            "--file": {"type": "file", "description": "ODS file"},
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "recurring": {
        "description": "Manage recurring expenses",
        "subcommands": {
            "list": {"description": "List recurring expenses"},
            "add": {"description": "Add recurring expense"},
            "remove": {"description": "Remove recurring expense"},
            "generate": {"description": "Generate expenses for period"},
        },
        "options": {
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "account": {
        "description": "Manage accounts",
        "subcommands": {
            "add": {"description": "Add an account"},
            "list": {"description": "List accounts"},
            "balance": {"description": "Show account balance"},
            "transfer": {"description": "Transfer between accounts"},
            "net-worth": {"description": "Calculate net worth"},
        },
        "options": {
            "--type": {
                "type": "choice",
                "choices": [
                    "checking",
                    "savings",
                    "credit_card",
                    "investment",
                    "loan",
                    "cash",
                    "other",
                ],
                "description": "Account type",
            },
            "--json": {"type": "flag", "description": "Output as JSON"},
        },
    },
    "visualize": {
        "description": "Generate interactive charts",
        "subcommands": {
            "pie": {"description": "Generate pie chart"},
            "bar": {"description": "Generate bar chart"},
            "dashboard": {"description": "Generate full dashboard"},
        },
        "options": {
            "--output": {"type": "file", "description": "Output HTML file"},
            "--theme": {
                "type": "choice",
                "choices": ["light", "dark"],
                "description": "Chart theme",
            },
        },
    },
    "banks": {
        "description": "List supported bank formats",
        "options": {
            "--list": {"type": "flag", "description": "List all formats"},
            "--search": {"type": "string", "description": "Search formats"},
            "--detect": {"type": "file", "description": "Detect format from CSV"},
        },
    },
    "currency": {
        "description": "Currency conversion",
        "subcommands": {
            "convert": {"description": "Convert amount between currencies"},
            "list": {"description": "List supported currencies"},
            "rates": {"description": "Show exchange rates"},
        },
        "options": {
            "--from": {"type": "string", "description": "Source currency code"},
            "--to": {"type": "string", "description": "Target currency code"},
        },
    },
    "goal": {
        "description": "Manage savings goals",
        "subcommands": {
            "add": {"description": "Add a savings goal"},
            "list": {"description": "List goals"},
            "progress": {"description": "Show goal progress"},
            "contribute": {"description": "Add contribution to goal"},
        },
        "options": {
            "--category": {
                "type": "choice",
                "choices": [
                    "savings",
                    "emergency_fund",
                    "vacation",
                    "home_down_payment",
                    "car_purchase",
                    "education",
                    "retirement",
                ],
                "description": "Goal category",
            },
        },
    },
    "debt": {
        "description": "Manage debt payoff",
        "subcommands": {
            "add": {"description": "Add a debt"},
            "list": {"description": "List debts"},
            "plan": {"description": "Show payoff plan"},
            "payment": {"description": "Record debt payment"},
            "compare": {"description": "Compare payoff methods"},
        },
        "options": {
            "--method": {
                "type": "choice",
                "choices": ["snowball", "avalanche"],
                "description": "Payoff method",
            },
        },
    },
    "bills": {
        "description": "Manage bill reminders",
        "subcommands": {
            "add": {"description": "Add a bill reminder"},
            "list": {"description": "List bills"},
            "upcoming": {"description": "Show upcoming bills"},
            "overdue": {"description": "Show overdue bills"},
            "pay": {"description": "Mark bill as paid"},
            "export-calendar": {"description": "Export to ICS calendar"},
        },
        "options": {
            "--days": {"type": "int", "description": "Days ahead to show"},
        },
    },
    "notify": {
        "description": "Send notifications",
        "subcommands": {
            "test": {"description": "Send test notification"},
            "config": {"description": "Configure notifications"},
            "history": {"description": "Show notification history"},
        },
        "options": {
            "--channel": {
                "type": "choice",
                "choices": ["email", "ntfy"],
                "description": "Notification channel",
            },
        },
    },
    "completions": {
        "description": "Generate shell completions",
        "subcommands": {
            "bash": {"description": "Generate Bash completions"},
            "zsh": {"description": "Generate Zsh completions"},
            "fish": {"description": "Generate Fish completions"},
            "install": {"description": "Install completions"},
        },
    },
}


def generate_bash_completions() -> str:
    """Generate Bash completion script."""
    commands = list(COMMAND_STRUCTURE.keys())
    commands_str = " ".join(commands)

    script = f'''# spreadsheet-dl bash completion
# Generated by spreadsheet-dl completions bash

_spreadsheet_dl_completions()
{{
    local cur prev words cword
    _init_completion || return

    local commands="{commands_str}"

    # Complete commands at position 1
    if [[ $cword -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return
    fi

    local cmd="${{words[1]}}"

    case "$cmd" in
'''

    for cmd, info in COMMAND_STRUCTURE.items():
        options = []
        if "options" in info:
            options.extend(info["options"].keys())
        if "subcommands" in info:
            options.extend(info["subcommands"].keys())

        options_str = " ".join(options)

        script += f'''        {cmd})
            if [[ $cword -eq 2 ]]; then
                COMPREPLY=($(compgen -W "{options_str}" -- "$cur"))
            else
                _spreadsheet_dl_complete_option "$cmd" "$prev" "$cur"
            fi
            ;;
'''

    script += """        *)
            COMPREPLY=()
            ;;
    esac
}

_spreadsheet_dl_complete_option()
{
    local cmd="$1" prev="$2" cur="$3"

    case "$prev" in
        --file|--output|--append|--detect)
            _filedir '@(ods|csv|xlsx|json)'
            ;;
        --template)
            COMPREPLY=($(compgen -W "50_30_20 family minimalist zero_based fire high_income" -- "$cur"))
            ;;
        --theme)
            COMPREPLY=($(compgen -W "default corporate minimal dark high_contrast" -- "$cur"))
            ;;
        --format)
            COMPREPLY=($(compgen -W "text json markdown" -- "$cur"))
            ;;
        --bank)
            COMPREPLY=($(compgen -W "chase chase_credit bank_of_america wells_fargo capital_one discover amex usaa generic" -- "$cur"))
            ;;
        --category)
            COMPREPLY=($(compgen -W "housing utilities groceries transportation healthcare insurance entertainment dining_out clothing personal_care education savings debt_payment gifts subscriptions miscellaneous" -- "$cur"))
            ;;
        --type)
            COMPREPLY=($(compgen -W "checking savings credit_card investment loan cash other" -- "$cur"))
            ;;
        --method)
            COMPREPLY=($(compgen -W "snowball avalanche" -- "$cur"))
            ;;
        --channel)
            COMPREPLY=($(compgen -W "email ntfy" -- "$cur"))
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -F _spreadsheet_dl_completions spreadsheet-dl
"""

    return script


def generate_zsh_completions() -> str:
    """Generate Zsh completion script."""
    script = """#compdef spreadsheet-dl
# spreadsheet-dl zsh completion
# Generated by spreadsheet-dl completions zsh

_spreadsheet_dl() {
    local -a commands
    commands=(
"""

    for cmd, info in COMMAND_STRUCTURE.items():
        desc = info.get("description", cmd)
        script += f"""        '{cmd}:{desc}'\n"""

    script += """    )

    _arguments -C \\
        '1:command:->command' \\
        '*::arg:->args'

    case "$state" in
        command)
            _describe 'command' commands
            ;;
        args)
            case "$words[1]" in
"""

    for cmd in COMMAND_STRUCTURE:
        script += f"""                {cmd})
                    _spreadsheet_dl_{cmd.replace("-", "_")}
                    ;;
"""

    script += """            esac
            ;;
    esac
}

"""

    # Generate per-command functions
    for cmd, info in COMMAND_STRUCTURE.items():
        func_name = cmd.replace("-", "_")
        script += f"""_spreadsheet_dl_{func_name}() {{
    local -a options subcommands
"""

        if "subcommands" in info:
            script += "    subcommands=(\n"
            for sub, sub_info in info["subcommands"].items():
                desc = sub_info.get("description", sub)
                script += f"        '{sub}:{desc}'\n"
            script += "    )\n"

        if "options" in info:
            script += "    options=(\n"
            for opt, opt_info in info["options"].items():
                desc = opt_info.get("description", opt)
                opt_type = opt_info.get("type", "string")
                if opt_type == "flag":
                    script += f"        '{opt}[{desc}]'\n"
                elif opt_type == "file":
                    script += f"        '{opt}[{desc}]:file:_files'\n"
                elif opt_type == "choice":
                    choices = " ".join(opt_info.get("choices", []))
                    script += f"        '{opt}[{desc}]:choice:({choices})'\n"
                else:
                    script += f"        '{opt}[{desc}]:{opt_type}:'\n"
            script += "    )\n"

        if "subcommands" in info:
            script += """    _arguments -C \\
        '1:subcommand:->subcommand' \\
        '*:option:->option'

    case "$state" in
        subcommand)
            _describe 'subcommand' subcommands
            ;;
        option)
            _arguments $options
            ;;
    esac
"""
        else:
            script += "    _arguments $options\n"

        script += "}\n\n"

    script += "_spreadsheet_dl\n"

    return script


def generate_fish_completions() -> str:
    """Generate Fish completion script."""
    script = """# spreadsheet-dl fish completion
# Generated by spreadsheet-dl completions fish

# Disable file completions by default
complete -c spreadsheet-dl -f

# Main commands
"""

    for cmd, info in COMMAND_STRUCTURE.items():
        desc = info.get("description", cmd)
        script += f"complete -c spreadsheet-dl -n '__fish_use_subcommand' -a '{cmd}' -d '{desc}'\n"

    script += "\n# Subcommands and options\n"

    for cmd, info in COMMAND_STRUCTURE.items():
        # Subcommands
        if "subcommands" in info:
            for sub, sub_info in info["subcommands"].items():
                desc = sub_info.get("description", sub)
                script += f"complete -c spreadsheet-dl -n '__fish_seen_subcommand_from {cmd}' -a '{sub}' -d '{desc}'\n"

        # Options
        if "options" in info:
            for opt, opt_info in info["options"].items():
                desc = opt_info.get("description", opt)
                opt_name = opt.lstrip("-")
                opt_type = opt_info.get("type", "string")

                if opt_type == "flag":
                    script += f"complete -c spreadsheet-dl -n '__fish_seen_subcommand_from {cmd}' -l '{opt_name}' -d '{desc}'\n"
                elif opt_type == "file":
                    script += f"complete -c spreadsheet-dl -n '__fish_seen_subcommand_from {cmd}' -l '{opt_name}' -d '{desc}' -r -F\n"
                elif opt_type == "choice":
                    choices = opt_info.get("choices", [])
                    for choice in choices:
                        script += f"complete -c spreadsheet-dl -n '__fish_seen_subcommand_from {cmd}; and __fish_prev_arg_in --{opt_name}' -a '{choice}'\n"
                    script += f"complete -c spreadsheet-dl -n '__fish_seen_subcommand_from {cmd}' -l '{opt_name}' -d '{desc}' -r\n"
                else:
                    script += f"complete -c spreadsheet-dl -n '__fish_seen_subcommand_from {cmd}' -l '{opt_name}' -d '{desc}' -r\n"

    return script


def install_completions(shell: str | None = None) -> dict[str, Any]:
    """Install shell completions.

    Args:
        shell: Shell type (bash, zsh, fish). Auto-detects if None.

    Returns:
        Dict with installation status and path.
    """
    if shell is None:
        shell = detect_shell()

    result: dict[str, Any] = {
        "shell": shell,
        "success": False,
        "path": None,
        "message": "",
    }

    if shell == "bash":
        path = _install_bash_completions()
    elif shell == "zsh":
        path = _install_zsh_completions()
    elif shell == "fish":
        path = _install_fish_completions()
    else:
        result["message"] = f"Unsupported shell: {shell}"
        return result

    if path:
        result["success"] = True
        result["path"] = str(path)
        result["message"] = f"Completions installed to {path}"
    else:
        result["message"] = f"Failed to install {shell} completions"

    return result


def detect_shell() -> str:
    """Detect current shell."""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh"
    elif "fish" in shell:
        return "fish"
    elif "bash" in shell:
        return "bash"

    # Try to detect from parent process
    try:
        ppid = os.getppid()
        with open(f"/proc/{ppid}/comm") as f:
            comm = f.read().strip()
            if "zsh" in comm:
                return "zsh"
            elif "fish" in comm:
                return "fish"
            elif "bash" in comm:
                return "bash"
    except OSError:
        pass

    return "bash"  # Default to bash


def _install_bash_completions() -> Path | None:
    """Install Bash completions."""
    script = generate_bash_completions()

    # Try system-wide first
    system_paths = [
        Path("/etc/bash_completion.d/spreadsheet-dl"),
        Path("/usr/share/bash-completion/completions/spreadsheet-dl"),
    ]

    # User-local paths
    user_paths = [
        Path.home() / ".local/share/bash-completion/completions/spreadsheet-dl",
        Path.home() / ".bash_completion.d/spreadsheet-dl",
    ]

    # Try each path
    for path in system_paths + user_paths:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(script)
            return path
        except PermissionError:
            continue
        except OSError:
            continue

    return None


def _install_zsh_completions() -> Path | None:
    """Install Zsh completions."""
    script = generate_zsh_completions()

    # Check fpath directories
    fpath_dirs = [
        Path.home() / ".zsh/completions",
        Path.home() / ".local/share/zsh/site-functions",
        Path("/usr/local/share/zsh/site-functions"),
    ]

    for path in fpath_dirs:
        completion_file = path / "_spreadsheet-dl"
        try:
            path.mkdir(parents=True, exist_ok=True)
            completion_file.write_text(script)
            return completion_file
        except PermissionError:
            continue
        except OSError:
            continue

    return None


def _install_fish_completions() -> Path | None:
    """Install Fish completions."""
    script = generate_fish_completions()

    # Fish completion paths
    paths = [
        Path.home() / ".config/fish/completions/spreadsheet-dl.fish",
        Path("/usr/share/fish/vendor_completions.d/spreadsheet-dl.fish"),
    ]

    for path in paths:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(script)
            return path
        except PermissionError:
            continue
        except OSError:
            continue

    return None


def print_completion_script(shell: str) -> str:
    """Print completion script for manual installation.

    Args:
        shell: Shell type (bash, zsh, fish).

    Returns:
        Completion script content.
    """
    if shell == "bash":
        return generate_bash_completions()
    elif shell == "zsh":
        return generate_zsh_completions()
    elif shell == "fish":
        return generate_fish_completions()
    else:
        raise ValueError(f"Unsupported shell: {shell}")


def get_installation_instructions(shell: str) -> str:
    """Get manual installation instructions.

    Args:
        shell: Shell type.

    Returns:
        Installation instructions.
    """
    instructions = {
        "bash": """
Bash Completion Installation
============================

Option 1: Add to .bashrc (recommended)
    spreadsheet-dl completions bash >> ~/.bash_completion
    source ~/.bashrc

Option 2: System-wide (requires sudo)
    sudo spreadsheet-dl completions bash > /etc/bash_completion.d/spreadsheet-dl

Option 3: User-local
    mkdir -p ~/.local/share/bash-completion/completions
    spreadsheet-dl completions bash > ~/.local/share/bash-completion/completions/spreadsheet-dl
""",
        "zsh": """
Zsh Completion Installation
===========================

Option 1: Add to .zshrc (recommended)
    mkdir -p ~/.zsh/completions
    spreadsheet-dl completions zsh > ~/.zsh/completions/_spreadsheet-dl

    Add to .zshrc:
    fpath=(~/.zsh/completions $fpath)
    autoload -Uz compinit && compinit

Option 2: Oh My Zsh
    spreadsheet-dl completions zsh > ~/.oh-my-zsh/completions/_spreadsheet-dl
    omz reload
""",
        "fish": """
Fish Completion Installation
============================

Option 1: User-local (recommended)
    mkdir -p ~/.config/fish/completions
    spreadsheet-dl completions fish > ~/.config/fish/completions/spreadsheet-dl.fish

Option 2: System-wide (requires sudo)
    sudo spreadsheet-dl completions fish > /usr/share/fish/vendor_completions.d/spreadsheet-dl.fish
""",
    }
    return instructions.get(shell, f"Unknown shell: {shell}")
