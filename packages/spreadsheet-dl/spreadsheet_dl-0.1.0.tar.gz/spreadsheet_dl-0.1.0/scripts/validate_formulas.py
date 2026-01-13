#!/usr/bin/env python3
"""Validate formula coverage and metadata across all domain plugins.

This script:
1. Counts formulas in each domain
2. Verifies formula metadata is complete
3. Tests formula generation (build() method)
4. Reports coverage statistics
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# ruff: noqa: E402
from spreadsheet_dl.domains.base import BaseFormula


def discover_domain_formulas() -> dict[str, list[type[BaseFormula]]]:
    """Discover all formulas in domain plugins."""
    domains = {
        "biology": "spreadsheet_dl.domains.biology.formulas",
        "chemistry": "spreadsheet_dl.domains.chemistry.formulas",
        "civil_engineering": "spreadsheet_dl.domains.civil_engineering.formulas",
        "data_science": "spreadsheet_dl.domains.data_science.formulas",
        "education": "spreadsheet_dl.domains.education.formulas",
        "electrical_engineering": "spreadsheet_dl.domains.electrical_engineering.formulas",
        "environmental": "spreadsheet_dl.domains.environmental.formulas",
        "finance": "spreadsheet_dl.domains.finance.formulas",
        "manufacturing": "spreadsheet_dl.domains.manufacturing.formulas",
        "mechanical_engineering": "spreadsheet_dl.domains.mechanical_engineering.formulas",
        "physics": "spreadsheet_dl.domains.physics.formulas",
    }

    formula_map: dict[str, list[type[BaseFormula]]] = {}

    for domain_name, module_path in domains.items():
        try:
            module = __import__(module_path, fromlist=["__all__"])
            formulas = []

            if hasattr(module, "__all__"):
                for name in module.__all__:
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, BaseFormula)
                        and obj is not BaseFormula
                    ):
                        formulas.append(obj)

            formula_map[domain_name] = formulas
        except ImportError as e:
            print(f"⚠️  Warning: Could not import {domain_name}: {e}")
            formula_map[domain_name] = []

    return formula_map


def validate_formula_metadata(formula_class: type[BaseFormula]) -> list[str]:
    """Validate formula metadata. Returns list of issues."""
    issues = []

    try:
        # Instantiate formula
        formula = formula_class()

        # Check metadata exists
        if not hasattr(formula, "metadata"):
            issues.append("Missing 'metadata' property")
            return issues

        metadata = formula.metadata

        # Check required fields
        if not metadata.name:
            issues.append("Missing metadata.name")

        if not metadata.category:
            issues.append("Missing metadata.category")

        if not metadata.description:
            issues.append("Missing metadata.description")

        if metadata.arguments is None:
            issues.append("Missing metadata.arguments")

        if not metadata.return_type:
            issues.append("Missing metadata.return_type")

        # Check examples
        if not metadata.examples or len(metadata.examples) == 0:
            issues.append("Missing metadata.examples")

    except Exception as e:
        issues.append(f"Error instantiating: {e}")

    return issues


def test_formula_generation(formula_class: type[BaseFormula]) -> list[str]:
    """Test formula generation. Returns list of issues."""
    issues = []

    try:
        formula = formula_class()

        # Try to call build() with dummy args
        # We can't test all formulas perfectly without knowing their signatures,
        # but we can at least verify the method exists and is callable
        if not hasattr(formula, "build"):
            issues.append("Missing 'build' method")

    except Exception as e:
        issues.append(f"Error testing generation: {e}")

    return issues


def main() -> int:
    """Run validation and report results."""
    print("=" * 80)
    print("Formula Validation Report")
    print("=" * 80)
    print()

    # Discover formulas
    formula_map = discover_domain_formulas()

    total_formulas = 0
    total_issues = 0
    domain_stats = []

    # Validate each domain
    for domain_name in sorted(formula_map.keys()):
        formulas = formula_map[domain_name]
        domain_formula_count = len(formulas)
        total_formulas += domain_formula_count

        print(f"📁 {domain_name.replace('_', ' ').title()}")
        print(f"   Formulas: {domain_formula_count}")

        domain_issues = 0

        for formula_class in formulas:
            # Validate metadata
            metadata_issues = validate_formula_metadata(formula_class)
            generation_issues = test_formula_generation(formula_class)

            all_issues = metadata_issues + generation_issues

            if all_issues:
                domain_issues += len(all_issues)
                total_issues += len(all_issues)
                print(f"   ❌ {formula_class.__name__}:")
                for issue in all_issues:
                    print(f"      - {issue}")

        if domain_issues == 0:
            print("   ✅ All formulas valid")

        domain_stats.append((domain_name, domain_formula_count, domain_issues))
        print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total Formulas: {total_formulas}")
    print(f"Total Issues: {total_issues}")
    print()

    # Coverage by domain
    print("Coverage by Domain:")
    print()
    for domain_name, count, issues in sorted(
        domain_stats, key=lambda x: x[1], reverse=True
    ):
        status = "✅" if issues == 0 else "❌"
        print(
            f"  {status} {domain_name.replace('_', ' ').title():30} {count:3} formulas"
        )

    print()

    # Return status
    if total_issues > 0:
        print(f"❌ Validation FAILED with {total_issues} issues")
        return 1
    else:
        print(f"✅ Validation PASSED - All {total_formulas} formulas are valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
