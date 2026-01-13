#!/usr/bin/env python3
"""
Template Engine Examples - Main Runner

Runs all template engine examples in sequence to demonstrate the complete
functionality of the SpreadsheetDL template engine.

Usage:
    python run_all.py              # Run all examples
    python run_all.py --example N  # Run specific example number (1-8)
"""

import sys


def main() -> None:
    """Run all template engine examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print(
        "║" + "  Template Engine Usage Examples - SpreadsheetDL v4.0".center(68) + "║"
    )
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        # Import all example functions - use absolute imports to avoid issues
        import importlib.util
        from pathlib import Path

        # Get the directory containing this file
        template_dir = Path(__file__).parent

        # Import each example module
        modules = {}
        for i in range(1, 9):
            module_name = f"{i:02d}_*.py"
            module_files = list(template_dir.glob(module_name))
            if module_files:
                module_path = module_files[0]
                spec = importlib.util.spec_from_file_location(
                    f"example_{i}", module_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    modules[i] = module

        # Get the example functions
        example_basic_template_loading = modules[1].example_basic_template_loading
        example_variable_substitution = modules[2].example_variable_substitution
        example_conditional_rendering = modules[3].example_conditional_rendering
        example_component_composition = modules[4].example_component_composition
        example_complete_template = modules[5].example_complete_template
        example_builtin_functions = modules[6].example_builtin_functions
        example_custom_template = modules[7].example_custom_template
        example_error_handling = modules[8].example_error_handling

        # Run all examples in sequence
        example_basic_template_loading()
        example_variable_substitution()
        example_conditional_rendering()
        example_component_composition()
        example_complete_template()
        example_builtin_functions()
        example_custom_template()
        example_error_handling()

        print("=" * 70)
        print("All Template Engine Examples Completed Successfully!")
        print("=" * 70)
        print()
        print("Key Features Demonstrated:")
        print("  • YAML-based template definition")
        print("  • Variable substitution with ${...} syntax")
        print("  • Built-in functions for dates, strings, math, formatting")
        print("  • Conditional rendering with if/else blocks")
        print("  • Reusable components for DRY templates")
        print("  • Template validation and error handling")
        print("  • Programmatic template creation")
        print()
        print("Template Engine Benefits:")
        print("  • Reusable spreadsheet templates")
        print("  • No code duplication")
        print("  • Type-safe variable system")
        print("  • Easy maintenance and updates")
        print("  • Version control friendly (YAML)")
        print()
        print("Common Use Cases:")
        print("  • Monthly budget templates")
        print("  • Invoice generators")
        print("  • Report templates")
        print("  • Data entry forms")
        print("  • Financial statements")
        print()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
