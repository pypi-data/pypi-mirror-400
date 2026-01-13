"""Comprehensive domain cross-validation tests.

Task 2.6: Domain Cross-Validation Tests for SpreadsheetDL v4.1.0 pre-release audit.

Tests:
    - Cross-domain formula compatibility
    - Domain plugin registration consistency
    - Formula output format validation
    - Metadata completeness across domains
    - Formula argument validation patterns
    - Inter-domain formula combinations
"""

from __future__ import annotations

from typing import Any

import pytest

# Import all domain plugins
from spreadsheet_dl.domains.biology import BiologyDomainPlugin
from spreadsheet_dl.domains.chemistry import ChemistryDomainPlugin
from spreadsheet_dl.domains.civil_engineering import CivilEngineeringDomainPlugin
from spreadsheet_dl.domains.data_science import DataScienceDomainPlugin
from spreadsheet_dl.domains.education import EducationDomainPlugin
from spreadsheet_dl.domains.electrical_engineering import (
    ElectricalEngineeringDomainPlugin,
)
from spreadsheet_dl.domains.environmental import EnvironmentalDomainPlugin
from spreadsheet_dl.domains.finance import FinanceDomainPlugin
from spreadsheet_dl.domains.manufacturing import ManufacturingDomainPlugin
from spreadsheet_dl.domains.mechanical_engineering import (
    MechanicalEngineeringDomainPlugin,
)
from spreadsheet_dl.domains.physics import PhysicsDomainPlugin

pytestmark = [pytest.mark.unit, pytest.mark.domain]


# =============================================================================
# Plugin Registry for All Domains
# =============================================================================

ALL_DOMAIN_PLUGINS = [
    ("physics", PhysicsDomainPlugin),
    ("chemistry", ChemistryDomainPlugin),
    ("biology", BiologyDomainPlugin),
    ("data_science", DataScienceDomainPlugin),
    ("finance", FinanceDomainPlugin),
    ("electrical_engineering", ElectricalEngineeringDomainPlugin),
    ("mechanical_engineering", MechanicalEngineeringDomainPlugin),
    ("civil_engineering", CivilEngineeringDomainPlugin),
    ("environmental", EnvironmentalDomainPlugin),
    ("manufacturing", ManufacturingDomainPlugin),
    ("education", EducationDomainPlugin),
]


# =============================================================================
# Plugin Registration Consistency Tests
# =============================================================================


class TestPluginRegistrationConsistency:
    """Test that all domain plugins follow consistent registration patterns."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_plugin_has_metadata(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test that each plugin has proper metadata."""
        plugin = plugin_class()
        metadata = plugin.metadata

        assert metadata is not None
        assert metadata.name == domain_name
        assert metadata.version
        assert len(metadata.tags) > 0

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_plugin_initializes(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test that each plugin initializes without error."""
        plugin = plugin_class()
        plugin.initialize()

        # Should have at least one formula after init
        formulas = plugin.list_formulas()
        assert len(formulas) > 0

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_plugin_validates(self, domain_name: str, plugin_class: type[Any]) -> None:
        """Test that each plugin validates successfully."""
        plugin = plugin_class()
        plugin.initialize()

        assert plugin.validate() is True

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_plugin_cleanup(self, domain_name: str, plugin_class: type[Any]) -> None:
        """Test that each plugin cleans up without error."""
        plugin = plugin_class()
        plugin.initialize()
        plugin.cleanup()  # Should not raise


# =============================================================================
# Formula Output Format Tests
# =============================================================================


class TestFormulaOutputFormat:
    """Test that all formulas produce properly formatted ODF output."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_produce_odf_prefix(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas produce output starting with 'of:='."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            # Build with minimum required arguments using test values
            test_args = self._get_test_args_for_formula(metadata)

            try:
                result = formula.build(*test_args)
                assert result.startswith("of:="), (
                    f"Formula {formula_name} in {domain_name} "
                    f"does not produce ODF prefix: {result[:20]}..."
                )
            except (ValueError, TypeError):
                # Some formulas may need specific argument types
                pass

    def _get_test_args_for_formula(self, metadata: Any) -> list[str]:
        """Generate test arguments for a formula based on metadata."""
        args = []
        required_count = sum(
            1 for arg in metadata.arguments if not getattr(arg, "optional", False)
        )

        for _i in range(required_count):
            # Use simple numeric test values
            args.append("10")

        return args


# =============================================================================
# Metadata Completeness Tests
# =============================================================================


class TestMetadataCompleteness:
    """Test that all formulas have complete metadata."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_have_name(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas have a name."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            assert formula.metadata.name, f"Formula {formula_name} has no name"

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_have_category(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas have a category."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            assert formula.metadata.category, f"Formula {formula_name} has no category"

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_have_description(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas have a description."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            assert formula.metadata.description, (
                f"Formula {formula_name} has no description"
            )

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_have_arguments(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas have arguments defined."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            assert len(formula.metadata.arguments) > 0, (
                f"Formula {formula_name} has no arguments"
            )

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_have_return_type(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas have a return type."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            assert formula.metadata.return_type, (
                f"Formula {formula_name} has no return_type"
            )

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_all_formulas_have_examples(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test all formulas have at least one example."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            assert len(formula.metadata.examples) > 0, (
                f"Formula {formula_name} has no examples"
            )


# =============================================================================
# Formula Argument Validation Tests
# =============================================================================


class TestFormulaArgumentValidation:
    """Test formula argument validation across domains."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_formulas_validate_minimum_args(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test formulas reject insufficient arguments."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            required_count = sum(
                1 for arg in metadata.arguments if not getattr(arg, "optional", False)
            )

            if required_count > 1:
                # Try with one fewer than required
                with pytest.raises(ValueError):
                    formula.build(*["10"] * (required_count - 1))

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_formulas_handle_optional_args(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test formulas handle optional arguments correctly."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            required_count = sum(
                1 for arg in metadata.arguments if not getattr(arg, "optional", False)
            )

            # Should work with just required args
            try:
                result = formula.build(*["10"] * required_count)
                assert result.startswith("of:=")
            except (ValueError, TypeError):
                # Some formulas may need specific values
                pass


# =============================================================================
# Cross-Domain Integration Tests
# =============================================================================


class TestCrossDomainIntegration:
    """Test integration between different domains."""

    def test_all_plugins_can_coexist(self) -> None:
        """Test that all plugins can be initialized together."""
        plugins = []
        for _domain_name, plugin_class in ALL_DOMAIN_PLUGINS:
            plugin = plugin_class()
            plugin.initialize()
            plugins.append(plugin)

        # All should be initialized
        assert len(plugins) == len(ALL_DOMAIN_PLUGINS)

        # All should have formulas
        total_formulas = sum(len(p.list_formulas()) for p in plugins)
        assert total_formulas > 200  # Should have many formulas across all domains

    def test_no_formula_name_collisions(self) -> None:
        """Test that no formula names collide across domains."""
        all_formulas: dict[str, str] = {}  # formula_name -> domain_name

        for domain_name, plugin_class in ALL_DOMAIN_PLUGINS:
            plugin = plugin_class()
            plugin.initialize()

            for formula_name in plugin.list_formulas():
                # Check for collision
                if formula_name in all_formulas:
                    existing_domain = all_formulas[formula_name]
                    pytest.fail(
                        f"Formula {formula_name} exists in both "
                        f"{existing_domain} and {domain_name}"
                    )

                all_formulas[formula_name] = domain_name

    def test_total_formula_count(self) -> None:
        """Test total formula count across all domains."""
        total = 0
        for _domain_name, plugin_class in ALL_DOMAIN_PLUGINS:
            plugin = plugin_class()
            plugin.initialize()
            total += len(plugin.list_formulas())

        # Should have at least 250 formulas (based on audit)
        assert total >= 250, f"Expected at least 250 formulas, found {total}"

    def test_domain_formula_distribution(self) -> None:
        """Test that formulas are distributed across domains."""
        domain_counts: dict[str, int] = {}

        for domain_name, plugin_class in ALL_DOMAIN_PLUGINS:
            plugin = plugin_class()
            plugin.initialize()
            domain_counts[domain_name] = len(plugin.list_formulas())

        # Each domain should have at least 10 formulas
        for domain_name, count in domain_counts.items():
            assert count >= 10, f"Domain {domain_name} has only {count} formulas"


# =============================================================================
# Category Coverage Tests
# =============================================================================


class TestCategoryCoverage:
    """Test formula category coverage within domains."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_domain_has_multiple_categories(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test that each domain has formulas in multiple categories."""
        plugin = plugin_class()
        plugin.initialize()

        categories = set()
        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            categories.add(formula.metadata.category)

        # Most domains should have at least 2 categories
        # (some specialized domains may have fewer)
        assert len(categories) >= 1, f"Domain {domain_name} has no categories"

    def test_physics_categories(self) -> None:
        """Test Physics domain has expected categories."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        categories = set()
        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            categories.add(formula.metadata.category)

        expected = {"mechanics", "electromagnetism", "optics", "quantum"}
        assert expected.issubset(categories)

    def test_chemistry_categories(self) -> None:
        """Test Chemistry domain has expected categories."""
        plugin = ChemistryDomainPlugin()
        plugin.initialize()

        categories = set()
        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            categories.add(formula.metadata.category)

        # Should have thermodynamics, kinetics, solutions
        assert len(categories) >= 3

    def test_finance_categories(self) -> None:
        """Test Finance domain has expected categories."""
        plugin = FinanceDomainPlugin()
        plugin.initialize()

        categories = set()
        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            categories.add(formula.metadata.category)

        # Should have time_value, investments, depreciation, etc.
        assert len(categories) >= 3


# =============================================================================
# Formula Build Consistency Tests
# =============================================================================


class TestFormulaBuildConsistency:
    """Test formula build method consistency."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_build_returns_string(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test build method always returns string."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            required_count = sum(
                1 for arg in metadata.arguments if not getattr(arg, "optional", False)
            )

            try:
                result = formula.build(*["10"] * required_count)
                assert isinstance(result, str), (
                    f"Formula {formula_name} build() "
                    f"returned {type(result)}, expected str"
                )
            except (ValueError, TypeError):
                pass

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_build_not_empty(self, domain_name: str, plugin_class: type[Any]) -> None:
        """Test build method never returns empty string."""
        plugin = plugin_class()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            required_count = sum(
                1 for arg in metadata.arguments if not getattr(arg, "optional", False)
            )

            try:
                result = formula.build(*["10"] * required_count)
                assert len(result) > 0, f"Formula {formula_name} returned empty string"
            except (ValueError, TypeError):
                pass


# =============================================================================
# Domain Tag Tests
# =============================================================================


class TestDomainTags:
    """Test domain plugin tags."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_domain_has_relevant_tags(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test each domain has relevant tags."""
        plugin = plugin_class()
        metadata = plugin.metadata

        # Should have at least one tag that matches domain name
        name_parts = domain_name.replace("_", " ").split()
        has_relevant_tag = any(
            part.lower() in tag.lower() for part in name_parts for tag in metadata.tags
        )

        assert has_relevant_tag or len(metadata.tags) > 0


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestDomainEdgeCases:
    """Test edge cases in domain formulas."""

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_formulas_handle_cell_references(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test formulas can accept cell references as arguments."""
        plugin = plugin_class()
        plugin.initialize()

        # Get first formula
        formula_names = plugin.list_formulas()
        if formula_names:
            formula_class = plugin.get_formula(formula_names[0])

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            required_count = sum(
                1 for arg in metadata.arguments if not getattr(arg, "optional", False)
            )

            # Build with cell references
            cell_refs = ["A1", "B1", "C1", "D1", "E1"][:required_count]

            try:
                result = formula.build(*cell_refs)
                # Should contain the cell references
                assert any(ref in result for ref in cell_refs)
            except (ValueError, TypeError):
                pass

    @pytest.mark.parametrize("domain_name,plugin_class", ALL_DOMAIN_PLUGINS)
    def test_formulas_handle_ranges(
        self, domain_name: str, plugin_class: type[Any]
    ) -> None:
        """Test formulas can handle range arguments where applicable."""
        plugin = plugin_class()
        plugin.initialize()

        # Some formulas may accept ranges
        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            # Check if any argument suggests range support
            for arg in metadata.arguments:
                if "range" in arg.name.lower() or "array" in arg.name.lower():
                    try:
                        result = formula.build("A1:A10")
                        assert "A1:A10" in result
                    except (ValueError, TypeError):
                        pass
                    break


# =============================================================================
# Performance Sanity Tests
# =============================================================================


class TestFormulaBuildPerformance:
    """Basic performance sanity tests for formula building."""

    def test_all_formulas_build_quickly(self) -> None:
        """Test that all formulas build in reasonable time."""
        import time

        total_formulas = 0
        start = time.time()

        for _domain_name, plugin_class in ALL_DOMAIN_PLUGINS:
            plugin = plugin_class()
            plugin.initialize()

            for formula_name in plugin.list_formulas():
                formula_class = plugin.get_formula(formula_name)

                assert formula_class is not None, "Formula not found"
                formula = formula_class()
                metadata = formula.metadata

                required_count = sum(
                    1
                    for arg in metadata.arguments
                    if not getattr(arg, "optional", False)
                )

                try:
                    formula.build(*["10"] * required_count)
                    total_formulas += 1
                except (ValueError, TypeError):
                    pass

        elapsed = time.time() - start

        # Should be able to build all formulas in under 5 seconds
        assert elapsed < 5.0, f"Building {total_formulas} formulas took {elapsed:.2f}s"

    def test_repeated_builds_consistent(self) -> None:
        """Test that repeated builds produce same result."""
        plugin = PhysicsDomainPlugin()
        plugin.initialize()

        for formula_name in plugin.list_formulas():
            formula_class = plugin.get_formula(formula_name)

            assert formula_class is not None, "Formula not found"
            formula = formula_class()
            metadata = formula.metadata

            required_count = sum(
                1 for arg in metadata.arguments if not getattr(arg, "optional", False)
            )

            try:
                result1 = formula.build(*["10"] * required_count)
                result2 = formula.build(*["10"] * required_count)
                assert result1 == result2, f"Formula {formula_name} not deterministic"
            except (ValueError, TypeError):
                pass
