"""
Tests for custom category management module.

Tests:
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from spreadsheet_dl import (
    Category,
    CategoryManager,
    StandardCategory,
    category_from_string,
    get_category_manager,
)

pytestmark = [pytest.mark.unit, pytest.mark.finance]


class TestCategory:
    """Tests for Category dataclass."""

    def test_create_category(self) -> None:
        """Test creating a category."""
        cat = Category(name="Pet Care", color="#795548", description="Pet expenses")
        assert cat.name == "Pet Care"
        assert cat.color == "#795548"
        assert cat.is_custom is True
        assert cat.is_hidden is False

    def test_category_validation(self) -> None:
        """Test category name validation."""
        # Valid names
        Category(name="Food")
        Category(name="Dining Out")
        Category(name="Home & Garden")
        Category(name="Category-Name")
        Category(name="Category 123")

        # Invalid names
        with pytest.raises(ValueError, match="cannot be empty"):
            Category(name="")

        with pytest.raises(ValueError, match="Invalid category name"):
            Category(name="Invalid@Name")

        with pytest.raises(ValueError, match="Invalid category name"):
            Category(name="Has/Slash")

    def test_category_name_length(self) -> None:
        """Test category name length validation."""
        # Max length should work
        Category(name="A" * 50)

        # Too long should fail
        with pytest.raises(ValueError, match="too long"):
            Category(name="A" * 51)

    def test_category_to_dict(self) -> None:
        """Test category serialization."""
        cat = Category(
            name="Custom",
            color="#FF0000",
            icon="shopping",
            description="Custom category",
            parent="Shopping",
            aliases=["custom1", "custom2"],
            budget_default=500.0,
        )
        data = cat.to_dict()
        assert data["name"] == "Custom"
        assert data["color"] == "#FF0000"
        assert data["aliases"] == ["custom1", "custom2"]
        assert data["budget_default"] == 500.0

    def test_category_from_dict(self) -> None:
        """Test category deserialization."""
        data = {
            "name": "Custom",
            "color": "#FF0000",
            "icon": "icon",
            "aliases": ["alias1"],
            "budget_default": 100.0,
        }
        cat = Category.from_dict(data)
        assert cat.name == "Custom"
        assert cat.color == "#FF0000"
        assert cat.aliases == ["alias1"]

    def test_category_matches(self) -> None:
        """Test category matching."""
        cat = Category(name="Dining Out", aliases=["Restaurant", "Food Out"])

        assert cat.matches("dining")
        assert cat.matches("Dining Out")
        assert cat.matches("restaurant")
        assert cat.matches("Food")
        assert not cat.matches("Groceries")


class TestCategoryManager:
    """Tests for CategoryManager."""

    def test_init_with_standard_categories(self) -> None:
        """Test manager initializes with standard categories."""
        manager = CategoryManager(auto_load=False)

        # Check all standard categories exist
        for std_cat in StandardCategory:
            cat = manager.get_category(std_cat.value)
            assert cat is not None
            assert cat.is_custom is False

    def test_list_categories(self) -> None:
        """Test listing categories."""
        manager = CategoryManager(auto_load=False)
        categories = manager.list_categories()

        assert len(categories) == 16  # Standard categories
        assert all(not c.is_custom for c in categories)

    def test_add_custom_category(self) -> None:
        """Test adding custom category."""
        manager = CategoryManager(auto_load=False)

        cat = manager.add_category(
            Category(name="Pet Care", color="#795548", description="Pet expenses")
        )

        assert cat.name == "Pet Care"
        assert cat.is_custom is True

        # Should be in list
        categories = manager.list_categories()
        assert any(c.name == "Pet Care" for c in categories)

    def test_add_duplicate_category(self) -> None:
        """Test adding duplicate category fails."""
        manager = CategoryManager(auto_load=False)

        # Can't add category with same name as standard
        with pytest.raises(ValueError, match="already exists"):
            manager.add_category(Category(name="Housing"))

        # Can't add duplicate custom
        manager.add_category(Category(name="Pet Care"))
        with pytest.raises(ValueError, match="already exists"):
            manager.add_category(Category(name="Pet Care"))

    def test_update_category(self) -> None:
        """Test updating category."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Custom"))

        # Update custom category
        cat = manager.update_category(
            "Custom", color="#FF0000", description="Updated", budget_default=1000.0
        )

        assert cat.color == "#FF0000"
        assert cat.description == "Updated"
        assert cat.budget_default == 1000.0

    def test_update_standard_category(self) -> None:
        """Test updating standard category (limited)."""
        manager = CategoryManager(auto_load=False)

        # Can update some properties
        cat = manager.update_category("Housing", color="#000000", is_hidden=True)
        assert cat.color == "#000000"
        assert cat.is_hidden is True

        # Cannot rename
        with pytest.raises(ValueError, match="Cannot rename"):
            manager.update_category("Housing", new_name="Home")

    def test_rename_category(self) -> None:
        """Test renaming custom category."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Old Name"))

        cat = manager.update_category("Old Name", new_name="New Name")
        assert cat.name == "New Name"
        assert manager.get_category("Old Name") is None
        assert manager.get_category("New Name") is not None

    def test_delete_category(self) -> None:
        """Test deleting category."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="ToDelete"))

        # Delete custom category
        result = manager.delete_category("ToDelete")
        assert result is True
        assert manager.get_category("ToDelete") is None

        # Cannot delete standard
        with pytest.raises(ValueError, match="Cannot delete built-in"):
            manager.delete_category("Housing")

    def test_delete_nonexistent(self) -> None:
        """Test deleting nonexistent category."""
        manager = CategoryManager(auto_load=False)
        result = manager.delete_category("Nonexistent")
        assert result is False

    def test_search_categories(self) -> None:
        """Test searching categories."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Pet Care", aliases=["Pets", "Animals"]))

        # Search by name
        results = manager.search_categories("pet")
        assert len(results) == 1
        assert results[0].name == "Pet Care"

        # Search by alias
        results = manager.search_categories("animals")
        assert len(results) == 1
        assert results[0].name == "Pet Care"

    def test_suggest_category(self) -> None:
        """Test category suggestion."""
        manager = CategoryManager(auto_load=False)

        # Test various descriptions
        housing = manager.suggest_category("rent payment")
        assert housing is not None
        assert housing.name == "Housing"

        utilities = manager.suggest_category("electric bill")
        assert utilities is not None
        assert utilities.name == "Utilities"

        groceries = manager.suggest_category("kroger grocery")
        assert groceries is not None
        assert groceries.name == "Groceries"

        transportation = manager.suggest_category("uber ride")
        assert transportation is not None
        assert transportation.name == "Transportation"

        entertainment = manager.suggest_category("netflix subscription")
        assert entertainment is not None
        assert entertainment.name == "Entertainment"

        # Unknown should return Miscellaneous
        misc = manager.suggest_category("random stuff")
        assert misc is not None
        assert misc.name == "Miscellaneous"

    def test_hidden_categories(self) -> None:
        """Test hidden categories behavior."""
        manager = CategoryManager(auto_load=False)
        manager.update_category("Gifts", is_hidden=True)

        # Not in default list
        categories = manager.list_categories()
        assert not any(c.name == "Gifts" for c in categories)

        # In list with include_hidden
        categories = manager.list_categories(include_hidden=True)
        assert any(c.name == "Gifts" for c in categories)

    def test_custom_only_filter(self) -> None:
        """Test custom-only category filter."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Custom1"))
        manager.add_category(Category(name="Custom2"))

        categories = manager.list_categories(custom_only=True)
        assert len(categories) == 2
        assert all(c.is_custom for c in categories)

    def test_category_tree(self) -> None:
        """Test category tree organization."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Parent"))
        manager.add_category(Category(name="Child1", parent="Parent"))
        manager.add_category(Category(name="Child2", parent="Parent"))

        tree = manager.get_category_tree()
        assert "Parent" in tree
        assert len(tree["Parent"]) == 2

    def test_save_and_load_yaml(self) -> None:
        """Test saving and loading from YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "categories.yaml"

            # Create and save
            manager = CategoryManager(config_path=path, auto_load=False)
            manager.add_category(
                Category(name="Pet Care", color="#795548", budget_default=200.0)
            )
            manager.update_category("Housing", color="#000000")
            manager.save()

            # Load in new manager
            manager2 = CategoryManager(config_path=path, auto_load=True)

            # Check custom category
            cat = manager2.get_category("Pet Care")
            assert cat is not None
            assert cat.color == "#795548"
            assert cat.budget_default == 200.0

            # Check override
            housing = manager2.get_category("Housing")
            assert housing is not None
            assert housing.color == "#000000"

    def test_save_and_load_json(self) -> None:
        """Test saving and loading from JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "categories.json"

            manager = CategoryManager(config_path=path, auto_load=False)
            manager.add_category(Category(name="Custom"))
            manager.save()

            manager2 = CategoryManager(config_path=path, auto_load=True)
            assert manager2.get_category("Custom") is not None

    def test_export_to_list(self) -> None:
        """Test exporting category names."""
        manager = CategoryManager(auto_load=False)
        names = manager.export_to_list()

        assert len(names) == 16
        assert "Housing" in names
        assert "Utilities" in names

    def test_iteration(self) -> None:
        """Test iterating over categories."""
        manager = CategoryManager(auto_load=False)
        categories = list(manager)
        assert len(categories) == 16

    def test_contains(self) -> None:
        """Test membership check."""
        manager = CategoryManager(auto_load=False)
        assert "Housing" in manager
        assert "Nonexistent" not in manager

    def test_len(self) -> None:
        """Test length."""
        manager = CategoryManager(auto_load=False)
        assert len(manager) == 16

        manager.add_category(Category(name="Custom"))
        assert len(manager) == 17


class TestGlobalManager:
    """Tests for global category manager."""

    def test_get_category_manager(self) -> None:
        """Test getting global manager."""
        manager = get_category_manager()
        assert isinstance(manager, CategoryManager)

    def test_category_from_string(self) -> None:
        """Test convenience function."""
        cat = category_from_string("Housing")
        assert cat is not None
        assert cat.name == "Housing"

        cat = category_from_string("nonexistent")
        assert cat is None


class TestAliasConflicts:
    """Tests for alias conflict handling."""

    def test_alias_conflict_on_add(self) -> None:
        """Test alias conflict when adding category."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Custom1"))

        # Alias conflicts with existing category
        with pytest.raises(ValueError, match="conflicts"):
            manager.add_category(Category(name="Custom2", aliases=["Custom1"]))

    def test_alias_conflict_on_update(self) -> None:
        """Test alias conflict when updating category."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Custom1"))
        manager.add_category(Category(name="Custom2"))

        with pytest.raises(ValueError, match="conflicts"):
            manager.update_category("Custom2", aliases=["Custom1"])


class TestSubCategories:
    """Tests for sub-category functionality."""

    def test_delete_with_subcategories(self) -> None:
        """Test deleting category with sub-categories."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Parent"))
        manager.add_category(Category(name="Child", parent="Parent"))

        # Should fail without force
        with pytest.raises(ValueError, match="sub-categories"):
            manager.delete_category("Parent")

        # Should work with force
        manager.delete_category("Parent", force=True)
        assert manager.get_category("Parent") is None

        # Child should have parent removed
        child = manager.get_category("Child")
        assert child is not None
        assert child.parent is None

    def test_filter_by_parent(self) -> None:
        """Test filtering categories by parent."""
        manager = CategoryManager(auto_load=False)
        manager.add_category(Category(name="Parent"))
        manager.add_category(Category(name="Child1", parent="Parent"))
        manager.add_category(Category(name="Child2", parent="Parent"))
        manager.add_category(Category(name="Other"))

        children = manager.list_categories(parent="Parent")
        assert len(children) == 2
        assert all(c.parent == "Parent" for c in children)


class TestEdgeCases:
    """Tests for edge cases."""

    def test_case_insensitive_lookup(self) -> None:
        """Test case-insensitive category lookup."""
        manager = CategoryManager(auto_load=False)

        # Should find regardless of case
        assert manager.get_category("housing") is not None
        assert manager.get_category("HOUSING") is not None
        assert manager.get_category("Housing") is not None

    def test_load_missing_file(self) -> None:
        """Test loading from missing file."""
        manager = CategoryManager(
            config_path="/nonexistent/path/categories.yaml", auto_load=False
        )
        # Should not raise, just skip loading
        manager.load()
        assert len(manager) == 16  # Only standard categories

    def test_load_invalid_yaml(self) -> None:
        """Test loading from invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.yaml"
            path.write_text("invalid: [yaml: content")

            manager = CategoryManager(config_path=path, auto_load=False)
            with pytest.raises(OSError, match="Failed to load"):
                manager.load()
