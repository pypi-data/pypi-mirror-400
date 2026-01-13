# Categories API Reference

Custom category management for expense tracking.

## Overview

The categories module provides dynamic category management including:

- Built-in standard categories (16 defaults)
- Custom category creation, editing, and deletion
- Category persistence via YAML/JSON configuration
- Category validation and suggestions
- MCP tool integration

## Classes

### Category

Represents a budget/expense category.

```python
from spreadsheet_dl.categories import Category

# Create a custom category
category = Category(
    name="Pet Care",
    color="#795548",
    icon="pet",
    description="Pet food, vet visits, supplies",
    parent=None,
    budget_default=200.0
)

# Serialize to dictionary
data = category.to_dict()

# Create from dictionary
restored = Category.from_dict(data)

# Check if matches search query
matches = category.matches("pet")  # True
```

#### Constructor

```python
Category(
    name: str,
    color: str = "#6B7280",
    icon: str = "",
    description: str = "",
    parent: str | None = None,
    is_custom: bool = True,
    is_hidden: bool = False,
    aliases: list[str] = [],
    budget_default: float = 0.0
)
```

**Parameters:**

- `name`: Category name (letters, numbers, spaces, hyphens, ampersands; max 50 chars)
- `color`: Hex color code for UI display
- `icon`: Optional emoji or icon name
- `description`: Category description
- `parent`: Parent category name for sub-categories
- `is_custom`: False for built-in categories
- `is_hidden`: Hidden categories don't appear in dropdowns
- `aliases`: Alternative names for the category
- `budget_default`: Default monthly budget amount

#### Methods

| Method            | Returns    | Description                            |
| ----------------- | ---------- | -------------------------------------- |
| `to_dict()`       | `dict`     | Serialize to dictionary                |
| `from_dict(data)` | `Category` | Create from dictionary (classmethod)   |
| `matches(query)`  | `bool`     | Check if category matches search query |

---

### CategoryManager

Manages expense categories including custom ones.

```python
from spreadsheet_dl.categories import CategoryManager, Category

# Initialize manager
manager = CategoryManager()

# List all categories
for cat in manager.list_categories():
    print(f"{cat.name}: {cat.color}")

# Add custom category
manager.add_category(Category(
    name="Pet Care",
    color="#795548",
    description="Pet-related expenses"
))

# Update category
manager.update_category("Pet Care", color="#8B4513", new_name="Pets")

# Search categories
results = manager.search_categories("food")

# Get category suggestion
suggested = manager.suggest_category("Kroger grocery shopping")
# Returns: Groceries category

# Save to file
manager.save()
```

#### Constructor

```python
CategoryManager(
    config_path: Path | str | None = None,
    auto_load: bool = True
)
```

**Parameters:**

- `config_path`: Path to categories config file (default: `~/.config/spreadsheet-dl/categories.yaml`)
- `auto_load`: Whether to load categories from file on init

#### Methods

##### `list_categories()`

List all categories with optional filtering.

```python
categories = manager.list_categories(
    include_hidden: bool = False,
    custom_only: bool = False,
    parent: str | None = None
)
```

##### `get_category()`

Get a category by name or alias.

```python
cat = manager.get_category("Groceries")
cat = manager.get_category("food")  # Works with aliases
```

##### `add_category()`

Add a new custom category.

```python
category = manager.add_category(Category(
    name="Childcare",
    color="#FF6B6B",
    description="Daycare, babysitter, activities"
))
```

**Raises:**

- `ValueError`: If category name already exists or alias conflicts

##### `update_category()`

Update an existing category.

```python
updated = manager.update_category(
    name: str,
    color: str | None = None,
    icon: str | None = None,
    description: str | None = None,
    aliases: list[str] | None = None,
    is_hidden: bool | None = None,
    budget_default: float | None = None,
    new_name: str | None = None  # Custom categories only
)
```

##### `delete_category()`

Delete a custom category.

```python
deleted = manager.delete_category(
    name: str,
    force: bool = False  # Delete even with sub-categories
)
```

**Raises:**

- `ValueError`: If trying to delete built-in category

##### `search_categories()`

Search categories by name or alias.

```python
results = manager.search_categories(
    query: str,
    limit: int = 10
)
```

##### `suggest_category()`

Suggest a category based on expense description.

```python
category = manager.suggest_category("Netflix subscription")
# Returns: Subscriptions
```

Uses keyword matching for common expense patterns.

##### `get_category_tree()`

Get categories organized as a tree by parent.

```python
tree = manager.get_category_tree()
# {
#     None: [root categories],
#     "Transportation": [sub-categories],
# }
```

##### `load()` / `save()`

Load/save categories from/to configuration file.

```python
manager.load(path: Path | str | None = None)
path = manager.save(path: Path | str | None = None)
```

##### `export_to_list()`

Export category names as a simple list (for dropdowns).

```python
names = manager.export_to_list()
# ["Clothing", "Debt Payment", "Dining Out", ...]
```

---

### StandardCategory

Enum of built-in standard categories.

```python
from spreadsheet_dl.categories import StandardCategory

# 16 standard categories
StandardCategory.HOUSING
StandardCategory.UTILITIES
StandardCategory.GROCERIES
StandardCategory.TRANSPORTATION
StandardCategory.HEALTHCARE
StandardCategory.INSURANCE
StandardCategory.ENTERTAINMENT
StandardCategory.DINING_OUT
StandardCategory.CLOTHING
StandardCategory.PERSONAL
StandardCategory.EDUCATION
StandardCategory.SAVINGS
StandardCategory.DEBT_PAYMENT
StandardCategory.GIFTS
StandardCategory.SUBSCRIPTIONS
StandardCategory.MISCELLANEOUS
```

---

## Module Functions

### `get_category_manager()`

Get the global category manager instance.

```python
from spreadsheet_dl.categories import get_category_manager

manager = get_category_manager(reload: bool = False)
```

### `category_from_string()`

Get a category by name string.

```python
from spreadsheet_dl.categories import category_from_string

cat = category_from_string("Groceries")
```

---

## Constants

### `CATEGORY_COLORS`

Default colors for standard categories.

```python
from spreadsheet_dl.categories import CATEGORY_COLORS

CATEGORY_COLORS = {
    "Housing": "#2c3e50",
    "Utilities": "#3498db",
    "Groceries": "#27ae60",
    # ... etc
}
```

---

## Configuration File Format

Categories are persisted in YAML format:

```yaml
version: '1.0'
custom_categories:
  - name: Pet Care
    color: '#795548'
    icon: pet
    description: Pet food, vet visits, supplies
    parent: null
    is_custom: true
    is_hidden: false
    aliases:
      - pets
      - animals
    budget_default: 200.0

category_overrides:
  Housing:
    color: '#1a1a2e'
    aliases:
      - rent
      - mortgage
```

---

## Complete Example

```python
from spreadsheet_dl.categories import CategoryManager, Category

# Initialize with custom config
manager = CategoryManager("./my_categories.yaml")

# Add custom categories with hierarchy
manager.add_category(Category(
    name="Transportation",
    color="#e67e22",
    is_custom=False  # Modify built-in
))

manager.add_category(Category(
    name="Gas",
    parent="Transportation",
    color="#f39c12"
))

manager.add_category(Category(
    name="Car Insurance",
    parent="Transportation",
    color="#d35400"
))

# Use suggestions
description = "Shell gas station"
category = manager.suggest_category(description)
print(f"Suggested: {category.name}")  # Transportation

# Hide unused categories
manager.update_category("Education", is_hidden=True)

# List visible custom categories
for cat in manager.list_categories(custom_only=True):
    print(f"- {cat.name} ({cat.color})")

# Save configuration
manager.save()
```
