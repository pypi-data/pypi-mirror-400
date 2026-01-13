"""Custom Category Management Module.

Provides dynamic category management for expense tracking:
- Built-in standard categories
- Custom category creation, editing, and deletion
- Category persistence via configuration
- Category validation and suggestions
- MCP tool integration

"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

# Try to import yaml for persistence
try:
    import yaml

    HAS_YAML = True
except ImportError:
    # Optional dependency - set to None when unavailable (type checker doesn't handle conditional imports)
    yaml = None  # type: ignore[assignment]
    HAS_YAML = False


class StandardCategory(Enum):
    """Standard expense categories (built-in).

    These are the 16 default categories that cannot be deleted,
    but can be hidden or renamed via aliases.
    """

    HOUSING = "Housing"
    UTILITIES = "Utilities"
    GROCERIES = "Groceries"
    TRANSPORTATION = "Transportation"
    HEALTHCARE = "Healthcare"
    INSURANCE = "Insurance"
    ENTERTAINMENT = "Entertainment"
    DINING_OUT = "Dining Out"
    CLOTHING = "Clothing"
    PERSONAL = "Personal Care"
    EDUCATION = "Education"
    SAVINGS = "Savings"
    DEBT_PAYMENT = "Debt Payment"
    GIFTS = "Gifts"
    SUBSCRIPTIONS = "Subscriptions"
    MISCELLANEOUS = "Miscellaneous"


@dataclass
class Category:
    """Represents a budget/expense category.

    Supports both standard (built-in) and custom categories
    with optional color coding, icon, and parent category.
    """

    name: str
    color: str = "#6B7280"  # Default gray
    icon: str = ""  # Optional emoji or icon name
    description: str = ""
    parent: str | None = None  # For sub-categories
    is_custom: bool = True  # False for built-in categories
    is_hidden: bool = False  # Hidden categories don't appear in dropdowns
    aliases: list[str] = field(default_factory=list)  # Alternative names
    budget_default: float = 0.0  # Default monthly budget

    def __post_init__(self) -> None:
        """Validate category on creation."""
        if not self.name:
            raise ValueError("Category name cannot be empty")
        if not re.match(r"^[a-zA-Z0-9\s\-&]+$", self.name):
            raise ValueError(
                f"Invalid category name '{self.name}': "
                "use only letters, numbers, spaces, hyphens, and ampersands"
            )
        if len(self.name) > 50:
            raise ValueError("Category name too long: max 50 characters")

    def to_dict(self) -> dict[str, Any]:
        """Convert category to dictionary for serialization."""
        return {
            "name": self.name,
            "color": self.color,
            "icon": self.icon,
            "description": self.description,
            "parent": self.parent,
            "is_custom": self.is_custom,
            "is_hidden": self.is_hidden,
            "aliases": self.aliases,
            "budget_default": self.budget_default,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Category:
        """Create category from dictionary."""
        return cls(
            name=data["name"],
            color=data.get("color", "#6B7280"),
            icon=data.get("icon", ""),
            description=data.get("description", ""),
            parent=data.get("parent"),
            is_custom=data.get("is_custom", True),
            is_hidden=data.get("is_hidden", False),
            aliases=data.get("aliases", []),
            budget_default=data.get("budget_default", 0.0),
        )

    def matches(self, query: str) -> bool:
        """Check if this category matches a search query."""
        query_lower = query.lower()
        if query_lower in self.name.lower():
            return True
        return any(query_lower in alias.lower() for alias in self.aliases)


# Default colors for categories
CATEGORY_COLORS = {
    "Housing": "#2c3e50",
    "Utilities": "#3498db",
    "Groceries": "#27ae60",
    "Transportation": "#e67e22",
    "Healthcare": "#e74c3c",
    "Insurance": "#9b59b6",
    "Entertainment": "#f39c12",
    "Dining Out": "#1abc9c",
    "Clothing": "#d35400",
    "Personal Care": "#c0392b",
    "Education": "#2980b9",
    "Savings": "#16a085",
    "Debt Payment": "#8e44ad",
    "Gifts": "#f1c40f",
    "Subscriptions": "#34495e",
    "Miscellaneous": "#7f8c8d",
}


class CategoryManager:
    """Manages expense categories including custom ones.

    Provides CRUD operations for categories with persistence
    to YAML/JSON files and integration with MCP tools.

    Example:
        ```python
        manager = CategoryManager()

        # List all categories
        for cat in manager.list_categories():
            print(f"{cat.name}: {cat.color}")

        # Add custom category
        manager.add_category(Category(
            name="Pet Care",
            color="#795548",
            icon="pet",
            description="Pet food, vet visits, supplies"
        ))

        # Save to file
        manager.save()
        ```
    """

    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "spreadsheet-dl" / "categories.yaml"

    def __init__(
        self,
        config_path: Path | str | None = None,
        auto_load: bool = True,
    ) -> None:
        """Initialize category manager.

        Args:
            config_path: Path to categories config file.
            auto_load: Whether to load categories from file on init.
        """
        self._config_path = (
            Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        )
        self._categories: dict[str, Category] = {}
        self._initialize_standard_categories()

        if auto_load and self._config_path.exists():
            self.load()

    def _initialize_standard_categories(self) -> None:
        """Initialize built-in standard categories."""
        for std_cat in StandardCategory:
            self._categories[std_cat.value] = Category(
                name=std_cat.value,
                color=CATEGORY_COLORS.get(std_cat.value, "#6B7280"),
                is_custom=False,
            )

    def list_categories(
        self,
        include_hidden: bool = False,
        custom_only: bool = False,
        parent: str | None = None,
    ) -> list[Category]:
        """List all categories with optional filtering.

        Args:
            include_hidden: Include hidden categories.
            custom_only: Only return custom categories.
            parent: Filter by parent category.

        Returns:
            List of matching categories.
        """
        categories = []
        for cat in self._categories.values():
            if not include_hidden and cat.is_hidden:
                continue
            if custom_only and not cat.is_custom:
                continue
            if parent is not None and cat.parent != parent:
                continue
            categories.append(cat)
        return sorted(categories, key=lambda c: (c.is_custom, c.name))

    def get_category(self, name: str) -> Category | None:
        """Get a category by name or alias.

        Args:
            name: Category name or alias.

        Returns:
            Category if found, None otherwise.
        """
        # Direct lookup
        if name in self._categories:
            return self._categories[name]

        # Search by alias
        name_lower = name.lower()
        for cat in self._categories.values():
            if cat.name.lower() == name_lower:
                return cat
            for alias in cat.aliases:
                if alias.lower() == name_lower:
                    return cat

        return None

    def category_exists(self, name: str) -> bool:
        """Check if a category exists."""
        return self.get_category(name) is not None

    def add_category(self, category: Category) -> Category:
        """Add a new custom category.

        Args:
            category: Category to add.

        Returns:
            The added category.

        Raises:
            ValueError: If category name already exists.
        """
        if self.category_exists(category.name):
            raise ValueError(f"Category '{category.name}' already exists")

        # Check aliases don't conflict
        for alias in category.aliases:
            if self.category_exists(alias):
                raise ValueError(f"Alias '{alias}' conflicts with existing category")

        category.is_custom = True
        self._categories[category.name] = category
        return category

    def update_category(
        self,
        name: str,
        color: str | None = None,
        icon: str | None = None,
        description: str | None = None,
        aliases: list[str] | None = None,
        is_hidden: bool | None = None,
        budget_default: float | None = None,
        new_name: str | None = None,
    ) -> Category:
        """Update an existing category.

        Args:
            name: Current category name.
            color: New color (optional).
            icon: New icon (optional).
            description: New description (optional).
            aliases: New aliases (optional).
            is_hidden: New hidden state (optional).
            budget_default: New default budget (optional).
            new_name: Rename category (optional, custom only).

        Returns:
            Updated category.

        Raises:
            KeyError: If category not found.
            ValueError: If trying to rename built-in category.
        """
        cat = self.get_category(name)
        if cat is None:
            raise KeyError(f"Category '{name}' not found")

        if new_name and not cat.is_custom:
            raise ValueError("Cannot rename built-in categories")

        if new_name and new_name != cat.name:
            if self.category_exists(new_name):
                raise ValueError(f"Category '{new_name}' already exists")
            # Remove old entry and add with new name
            del self._categories[cat.name]
            cat.name = new_name
            self._categories[new_name] = cat

        if color is not None:
            cat.color = color
        if icon is not None:
            cat.icon = icon
        if description is not None:
            cat.description = description
        if aliases is not None:
            # Validate aliases don't conflict
            for alias in aliases:
                existing = self.get_category(alias)
                if existing and existing.name != cat.name:
                    raise ValueError(
                        f"Alias '{alias}' conflicts with '{existing.name}'"
                    )
            cat.aliases = aliases
        if is_hidden is not None:
            cat.is_hidden = is_hidden
        if budget_default is not None:
            cat.budget_default = budget_default

        return cat

    def delete_category(self, name: str, force: bool = False) -> bool:
        """Delete a category.

        Args:
            name: Category name to delete.
            force: Force delete even if has sub-categories.

        Returns:
            True if deleted, False if category not found.

        Raises:
            ValueError: If trying to delete built-in category.
            ValueError: If category has sub-categories and force=False.
        """
        cat = self.get_category(name)
        if cat is None:
            return False

        if not cat.is_custom:
            raise ValueError(
                f"Cannot delete built-in category '{name}'. "
                "Use update_category(is_hidden=True) to hide it instead."
            )

        # Check for sub-categories
        children = [c for c in self._categories.values() if c.parent == name]
        if children and not force:
            raise ValueError(
                f"Category '{name}' has {len(children)} sub-categories. "
                "Use force=True to delete anyway."
            )

        # Update children to remove parent reference
        for child in children:
            child.parent = None

        del self._categories[name]
        return True

    def search_categories(self, query: str, limit: int = 10) -> list[Category]:
        """Search categories by name or alias.

        Args:
            query: Search query.
            limit: Maximum results to return.

        Returns:
            List of matching categories.
        """
        matches = []
        for cat in self._categories.values():
            if cat.is_hidden:
                continue
            if cat.matches(query):
                matches.append(cat)
            if len(matches) >= limit:
                break
        return matches

    def suggest_category(self, description: str) -> Category | None:
        """Suggest a category based on expense description.

        Uses keyword matching to suggest appropriate category.

        Args:
            description: Expense description.

        Returns:
            Suggested category or None.
        """
        desc_lower = description.lower()

        # Keywords to category mapping
        keywords = {
            "Housing": ["rent", "mortgage", "property", "hoa", "home"],
            "Utilities": ["electric", "gas", "water", "internet", "phone", "utility"],
            "Groceries": [
                "grocery",
                "supermarket",
                "food",
                "kroger",
                "walmart",
                "costco",
            ],
            "Transportation": [
                "gas",
                "fuel",
                "uber",
                "lyft",
                "transit",
                "parking",
                "car",
            ],
            "Healthcare": [
                "doctor",
                "medical",
                "pharmacy",
                "hospital",
                "dental",
                "vision",
            ],
            "Insurance": ["insurance", "premium", "coverage"],
            "Entertainment": ["movie", "netflix", "spotify", "game", "concert", "show"],
            "Dining Out": [
                "restaurant",
                "cafe",
                "coffee",
                "pizza",
                "takeout",
                "doordash",
            ],
            "Clothing": ["clothing", "clothes", "shoes", "apparel", "fashion"],
            "Personal Care": ["haircut", "salon", "spa", "gym", "fitness"],
            "Education": ["tuition", "course", "book", "school", "training"],
            "Savings": ["savings", "investment", "401k", "ira", "deposit"],
            "Debt Payment": ["loan", "credit card", "debt", "payment"],
            "Gifts": ["gift", "present", "donation", "charity"],
            "Subscriptions": ["subscription", "membership", "monthly", "annual"],
        }

        for cat_name, cat_keywords in keywords.items():
            for keyword in cat_keywords:
                if keyword in desc_lower:
                    return self.get_category(cat_name)

        return self.get_category("Miscellaneous")

    def get_category_tree(self) -> dict[str | None, list[Category]]:
        """Get categories organized as a tree by parent.

        Returns:
            Dictionary mapping parent names to child categories.
            None key contains root categories.
        """
        tree: dict[str | None, list[Category]] = {None: []}
        for cat in self._categories.values():
            if cat.is_hidden:
                continue
            parent = cat.parent
            if parent not in tree:
                tree[parent] = []
            tree[parent].append(cat)

        # Sort each list
        for key in tree:
            tree[key] = sorted(tree[key], key=lambda c: c.name)

        return tree

    def load(self, path: Path | str | None = None) -> None:
        """Load categories from configuration file.

        Args:
            path: Optional path override.
        """
        load_path = Path(path) if path else self._config_path
        if not load_path.exists():
            return

        try:
            if load_path.suffix in (".yaml", ".yml") and HAS_YAML and yaml is not None:
                with open(load_path) as f:
                    data = yaml.safe_load(f)
            else:
                with open(load_path) as f:
                    data = json.load(f)

            if not isinstance(data, dict):
                return

            # Load custom categories
            for cat_data in data.get("custom_categories", []):
                try:
                    cat = Category.from_dict(cat_data)
                    cat.is_custom = True
                    self._categories[cat.name] = cat
                except (KeyError, ValueError):
                    continue  # Skip invalid categories

            # Load overrides for standard categories
            for name, overrides in data.get("category_overrides", {}).items():
                if name in self._categories:
                    cat = self._categories[name]
                    if "color" in overrides:
                        cat.color = overrides["color"]
                    if "icon" in overrides:
                        cat.icon = overrides["icon"]
                    if "aliases" in overrides:
                        cat.aliases = overrides["aliases"]
                    if "is_hidden" in overrides:
                        cat.is_hidden = overrides["is_hidden"]
                    if "budget_default" in overrides:
                        cat.budget_default = overrides["budget_default"]

        except (OSError, json.JSONDecodeError, Exception) as e:
            # Catch YAML parsing errors and other exceptions
            raise OSError(f"Failed to load categories from {load_path}: {e}") from e

    def save(self, path: Path | str | None = None) -> Path:
        """Save categories to configuration file.

        Args:
            path: Optional path override.

        Returns:
            Path where categories were saved.
        """
        save_path = Path(path) if path else self._config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "version": "1.0",
            "custom_categories": [],
            "category_overrides": {},
        }

        # Save custom categories
        for cat in self._categories.values():
            if cat.is_custom:
                data["custom_categories"].append(cat.to_dict())
            else:
                # Save overrides for standard categories
                overrides: dict[str, Any] = {}
                std_color = CATEGORY_COLORS.get(cat.name, "#6B7280")
                if cat.color != std_color:
                    overrides["color"] = cat.color
                if cat.icon:
                    overrides["icon"] = cat.icon
                if cat.aliases:
                    overrides["aliases"] = cat.aliases
                if cat.is_hidden:
                    overrides["is_hidden"] = cat.is_hidden
                if cat.budget_default:
                    overrides["budget_default"] = cat.budget_default

                if overrides:
                    data["category_overrides"][cat.name] = overrides

        try:
            if save_path.suffix in (".yaml", ".yml") and HAS_YAML and yaml is not None:
                with open(save_path, "w") as f:
                    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                with open(save_path, "w") as f:
                    json.dump(data, f, indent=2)
        except OSError as e:
            raise OSError(f"Failed to save categories to {save_path}: {e}") from e

        return save_path

    def export_to_list(self) -> list[str]:
        """Export category names as a simple list.

        Useful for dropdowns and validation lists.

        Returns:
            List of visible category names.
        """
        return [cat.name for cat in self.list_categories()]

    def __iter__(self) -> Iterator[Category]:
        """Iterate over visible categories."""
        return iter(self.list_categories())

    def __len__(self) -> int:
        """Return number of visible categories."""
        return len(self.list_categories())

    def __contains__(self, name: str) -> bool:
        """Check if category exists."""
        return self.category_exists(name)


# Global category manager instance (lazy-loaded)
_category_manager: CategoryManager | None = None


def get_category_manager(reload: bool = False) -> CategoryManager:
    """Get the global category manager instance.

    Args:
        reload: Force reload from configuration.

    Returns:
        Global CategoryManager instance.
    """
    global _category_manager
    if _category_manager is None or reload:
        _category_manager = CategoryManager()
    return _category_manager


def category_from_string(name: str) -> Category | None:
    """Get a category by name string.

    Convenience function for CLI and MCP tools.

    Args:
        name: Category name or alias.

    Returns:
        Category if found, None otherwise.
    """
    return get_category_manager().get_category(name)
