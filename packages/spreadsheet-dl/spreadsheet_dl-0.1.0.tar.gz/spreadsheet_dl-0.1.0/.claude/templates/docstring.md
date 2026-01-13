# Docstring Template for SpreadsheetDL

This document defines the standard docstring format for all SpreadsheetDL code.
All public APIs must follow this Google-style docstring format.

## Module Docstring Template

```python
"""
Brief one-line description of the module.

Extended description explaining the module's purpose, key functionality,
and how it fits into the overall architecture.

Key Classes:
    - ClassName: Brief description
    - AnotherClass: Brief description

Key Functions:
    - function_name: Brief description

Examples:
    Basic usage example::

        >>> from spreadsheet_dl.module import ClassName
        >>> obj = ClassName()
        >>> result = obj.method()

.. versionadded:: 4.0.0
"""
```

## Class Docstring Template

```python
class ClassName:
    """
    Brief one-line description of the class.

    Extended description explaining what this class does,
    when to use it, and any important behavior.

    Attributes:
        attr1: Description of first attribute.
        attr2: Description of second attribute.

    Examples:
        >>> obj = ClassName(param1="value")
        >>> obj.method()
        'expected result'

    See Also:
        :class:`RelatedClass`: For related functionality.

    Note:
        Any important notes about usage.

    .. versionadded:: 4.0.0
    """
```

## Method/Function Docstring Template

```python
def method_name(self, param1: str, param2: int = 0) -> ReturnType:
    """
    Brief one-line description of what this method does.

    Extended description if needed. Can span multiple lines
    and provide additional context.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter. Defaults to 0.

    Returns:
        Description of return value and its type.
        For complex returns, describe the structure.

    Raises:
        ValueError: When param1 is empty or invalid.
        TypeError: When param2 is not an integer.
        SpreadsheetDLError: When operation fails.

    Examples:
        Basic usage:

        >>> obj = ClassName()
        >>> obj.method_name("value", 10)
        ExpectedResult(...)

        With error handling:

        >>> try:
        ...     obj.method_name("")
        ... except ValueError as e:
        ...     print(e)
        'param1 cannot be empty'

    Note:
        Optional additional notes about behavior or edge cases.

    Warning:
        Any warnings about side effects or deprecation.

    See Also:
        :meth:`related_method`: For related functionality.

    .. versionadded:: 4.0.0
    """
```

## Property Docstring Template

```python
@property
def property_name(self) -> ReturnType:
    """
    Brief description of what this property represents.

    Returns:
        Description of the returned value.

    Examples:
        >>> obj = ClassName()
        >>> obj.property_name
        'expected value'
    """
```

## Required Sections by Context

### Minimum Required (all public APIs)

- Brief one-line description
- Args (if parameters exist)
- Returns (if not None)

### Recommended (for complex functionality)

- Extended description
- Raises
- Examples

### Optional (for comprehensive documentation)

- Note
- Warning
- See Also
- Version annotations

## Style Guidelines

1. **First line**: Always a brief, imperative description ending with a period.
2. **Blank line**: Always separate the brief description from extended content.
3. **Args format**: `param_name: Description.` (no type hints in docstring, they're in signature)
4. **Returns format**: Describe the value, not just the type.
5. **Raises format**: `ExceptionType: When this exception is raised.`
6. **Examples**: Use `>>>` doctest format for testable examples.
7. **Line length**: Keep lines under 88 characters.
8. **Consistency**: Use the same terminology throughout the codebase.

## Domain-Specific Notes

For domain plugins (Biology, Manufacturing, Engineering, etc.):

1. Include domain-specific terminology definitions
2. Add mathematical formulas in LaTeX notation where applicable
3. Reference relevant standards or specifications
4. Include units of measurement where applicable

Example for a domain formula:

```python
def shannon_diversity(counts: list[int]) -> float:
    """
    Calculate Shannon diversity index (H').

    The Shannon diversity index measures species diversity in a community.
    Higher values indicate greater diversity.

    Formula:
        H' = -sum(p_i * ln(p_i))

        where p_i is the proportion of individuals belonging to species i.

    Args:
        counts: List of individual counts per species.

    Returns:
        Shannon diversity index value (H').
        Values typically range from 0 to ~4.5.

    Raises:
        ValueError: If counts contains negative values.
        ValueError: If all counts are zero.

    Examples:
        >>> shannon_diversity([10, 10, 10, 10])  # Equal distribution
        1.386...
        >>> shannon_diversity([40, 0, 0, 0])  # Single species
        0.0

    References:
        Shannon, C.E. (1948). A Mathematical Theory of Communication.
    """
```

## Validation

All docstrings are validated by:

1. **ruff D rules**: Google-style compliance
2. **interrogate**: Coverage checking (80% minimum)
3. **pytest --doctest-modules**: Example validation
4. **mkdocstrings**: Rendering verification
