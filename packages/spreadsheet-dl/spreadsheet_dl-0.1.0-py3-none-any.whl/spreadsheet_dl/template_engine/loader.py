"""Template loader for YAML-based spreadsheet templates.

Loads templates from YAML files and converts them to
SpreadsheetTemplate objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spreadsheet_dl.template_engine.schema import (
    CellTemplate,
    ColumnTemplate,
    ComponentDefinition,
    ConditionalBlock,
    RowTemplate,
    SheetTemplate,
    SpreadsheetTemplate,
    TemplateVariable,
    VariableType,
)


class TemplateLoader:
    """Loader for YAML-based spreadsheet templates.

    Examples:
        loader = TemplateLoader()
        template = loader.load("monthly-budget")
        template = loader.load_from_file("custom-template.yaml")
    """

    # Default template directory
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "yaml"

    def __init__(self, template_dir: Path | str | None = None) -> None:
        """Initialize loader.

        Args:
            template_dir: Directory containing template files
        """
        self._template_dir = (
            Path(template_dir) if template_dir else self.DEFAULT_TEMPLATE_DIR
        )
        self._cache: dict[str, SpreadsheetTemplate] = {}

    def load(self, name: str) -> SpreadsheetTemplate:
        """Load template by name from template directory.

        Args:
            name: Template name (without .yaml extension)

        Returns:
            SpreadsheetTemplate object

        Raises:
            FileNotFoundError: If template not found
        """
        if name in self._cache:
            return self._cache[name]

        # Look for template file
        template_file = self._template_dir / f"{name}.yaml"
        if not template_file.exists():
            template_file = self._template_dir / f"{name}.yml"

        if not template_file.exists():
            raise FileNotFoundError(
                f"Template '{name}' not found in {self._template_dir}"
            )

        template = self.load_from_file(template_file)
        self._cache[name] = template
        return template

    def load_from_file(self, path: Path | str) -> SpreadsheetTemplate:
        """Load template from a specific file.

        Args:
            path: Path to template YAML file

        Returns:
            SpreadsheetTemplate object
        """
        path = Path(path)

        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required for template loading. "
                "Install with: pip install spreadsheet-dl[config]"
            ) from exc

        with open(path) as f:
            data = yaml.safe_load(f)

        return self._parse_template(data)

    def load_from_string(self, yaml_content: str) -> SpreadsheetTemplate:
        """Load template from YAML string.

        Args:
            yaml_content: YAML content as string

        Returns:
            SpreadsheetTemplate object
        """
        try:
            import yaml
        except ImportError as exc:
            raise ImportError("PyYAML is required for template loading") from exc

        data = yaml.safe_load(yaml_content)
        return self._parse_template(data)

    def list_templates(self) -> list[dict[str, str]]:
        """List available templates in template directory.

        Returns:
            List of template info dictionaries
        """
        templates: list[dict[str, Any]] = []

        if not self._template_dir.exists():
            return templates

        for path in self._template_dir.glob("*.yaml"):
            try:
                template = self.load_from_file(path)
                templates.append(
                    {
                        "name": template.name,
                        "file": path.name,
                        "version": template.version,
                        "description": template.description,
                    }
                )
            except (OSError, ValueError, KeyError, TypeError, ImportError):
                # Skip invalid templates
                pass

        for path in self._template_dir.glob("*.yml"):
            try:
                template = self.load_from_file(path)
                templates.append(
                    {
                        "name": template.name,
                        "file": path.name,
                        "version": template.version,
                        "description": template.description,
                    }
                )
            except (OSError, ValueError, KeyError, TypeError, ImportError):
                pass

        return templates

    def _parse_template(self, data: dict[str, Any]) -> SpreadsheetTemplate:
        """Parse template dictionary into SpreadsheetTemplate."""
        # Parse meta
        meta = data.get("meta", data)

        # Parse variables
        variables = self._parse_variables(data.get("variables", []))

        # Parse components
        components = self._parse_components(data.get("components", {}))

        # Parse sheets
        sheets = self._parse_sheets(data.get("sheets", []))

        # Parse validations
        validations = data.get("validations", {})

        # Parse conditional formats
        conditional_formats = data.get("conditional_formats", {})

        # Parse styles
        styles = data.get("styles", {})

        return SpreadsheetTemplate(
            name=meta.get("name", "Untitled"),
            version=meta.get("version", "1.0.0"),
            description=meta.get("description", ""),
            author=meta.get("author", ""),
            theme=meta.get("theme", "default"),
            variables=variables,
            components=components,
            sheets=sheets,
            properties=data.get("properties", {}),
            validations=validations,
            conditional_formats=conditional_formats,
            styles=styles,
        )

    def _parse_variables(
        self, var_list: list[dict[str, Any]]
    ) -> list[TemplateVariable]:
        """Parse variable definitions."""
        variables = []

        for var_data in var_list:
            var_type = VariableType.STRING
            if "type" in var_data:
                try:
                    var_type = VariableType(var_data["type"])
                except ValueError:
                    var_type = VariableType.STRING

            variables.append(
                TemplateVariable(
                    name=var_data.get("name", ""),
                    type=var_type,
                    description=var_data.get("description", ""),
                    required=var_data.get("required", False),
                    default=var_data.get("default"),
                    validation=var_data.get("validation"),
                    choices=var_data.get("choices", []),
                )
            )

        return variables

    def _parse_components(
        self, comp_dict: dict[str, Any]
    ) -> dict[str, ComponentDefinition]:
        """Parse component definitions."""
        components = {}

        for name, comp_data in comp_dict.items():
            components[name] = ComponentDefinition(
                name=name,
                description=comp_data.get("description", ""),
                variables=self._parse_variables(comp_data.get("variables", [])),
                columns=self._parse_columns(comp_data.get("columns", [])),
                rows=self._parse_rows(comp_data.get("rows", [])),
                styles=comp_data.get("styles", {}),
            )

        return components

    def _parse_sheets(self, sheet_list: list[dict[str, Any]]) -> list[SheetTemplate]:
        """Parse sheet definitions."""
        sheets = []

        for sheet_data in sheet_list:
            # Parse columns
            columns = self._parse_columns(sheet_data.get("columns", []))

            # Parse row sections
            header_row = None
            if "header" in sheet_data:
                header_row = self._parse_row(sheet_data["header"])

            data_rows = None
            if "data_rows" in sheet_data:
                data_rows = self._parse_row(sheet_data["data_rows"])

            total_row = None
            if "total" in sheet_data:
                total_row = self._parse_row(sheet_data["total"])

            custom_rows = self._parse_rows(sheet_data.get("rows", []))

            # Parse conditionals
            conditionals = self._parse_conditionals(sheet_data.get("conditionals", []))

            sheets.append(
                SheetTemplate(
                    name=sheet_data.get("name", "Sheet"),
                    name_template=sheet_data.get("name_template"),
                    columns=columns,
                    header_row=header_row,
                    data_rows=data_rows,
                    total_row=total_row,
                    custom_rows=custom_rows,
                    components=sheet_data.get("components", []),
                    freeze_rows=sheet_data.get("freeze_rows", 0),
                    freeze_cols=sheet_data.get("freeze_cols", 0),
                    print_area=sheet_data.get("print_area"),
                    protection=sheet_data.get("protection", {}),
                    conditionals=conditionals,
                    validations=sheet_data.get("validations", []),
                    conditional_formats=sheet_data.get("conditional_formats", []),
                )
            )

        return sheets

    def _parse_columns(self, col_list: list[dict[str, Any]]) -> list[ColumnTemplate]:
        """Parse column definitions."""
        columns = []

        for col_data in col_list:
            if isinstance(col_data, str):
                # Simple column name
                columns.append(ColumnTemplate(name=col_data))
            else:
                columns.append(
                    ColumnTemplate(
                        name=col_data.get("name", ""),
                        width=col_data.get("width", "2.5cm"),
                        type=col_data.get("type", "string"),
                        style=col_data.get("style"),
                        validation=col_data.get("validation"),
                        conditional_format=col_data.get("conditional_format"),
                        hidden=col_data.get("hidden", False),
                        frozen=col_data.get("frozen", False),
                    )
                )

        return columns

    def _parse_rows(self, row_list: list[dict[str, Any]]) -> list[RowTemplate]:
        """Parse row definitions."""
        return [self._parse_row(row_data) for row_data in row_list]

    def _parse_row(self, row_data: dict[str, Any]) -> RowTemplate:
        """Parse a single row definition."""
        cells = self._parse_cells(row_data.get("cells", []))

        conditional = None
        if "if" in row_data:
            conditional = ConditionalBlock(
                condition=row_data["if"],
                content=row_data.get("then", []),
                else_content=row_data.get("else", []),
            )

        return RowTemplate(
            cells=cells,
            style=row_data.get("style"),
            height=row_data.get("height"),
            repeat=row_data.get("repeat", 1),
            alternate_style=row_data.get("alternate_style"),
            conditional=conditional,
        )

    def _parse_cells(self, cell_list: list[Any]) -> list[CellTemplate]:
        """Parse cell definitions."""
        cells = []

        for cell_data in cell_list:
            if cell_data is None:
                cells.append(CellTemplate())
            elif isinstance(cell_data, (str, int, float)):
                # Simple value
                cells.append(CellTemplate(value=cell_data))
            else:
                cells.append(
                    CellTemplate(
                        value=cell_data.get("value"),
                        formula=cell_data.get("formula"),
                        style=cell_data.get("style"),
                        type=cell_data.get("type"),
                        colspan=cell_data.get("colspan", 1),
                        rowspan=cell_data.get("rowspan", 1),
                        validation=cell_data.get("validation"),
                        conditional_format=cell_data.get("conditional_format"),
                    )
                )

        return cells

    def _parse_conditionals(
        self, cond_list: list[dict[str, Any]]
    ) -> list[ConditionalBlock]:
        """Parse conditional block definitions."""
        conditionals = []

        for cond_data in cond_list:
            conditionals.append(
                ConditionalBlock(
                    condition=cond_data.get("if", "true"),
                    content=cond_data.get("then", []),
                    else_content=cond_data.get("else", []),
                    style=cond_data.get("style"),
                )
            )

        return conditionals


def load_template(
    name: str, template_dir: Path | str | None = None
) -> SpreadsheetTemplate:
    """Load template by name.

    Args:
        name: Template name
        template_dir: Optional custom template directory

    Returns:
        SpreadsheetTemplate object
    """
    loader = TemplateLoader(template_dir)
    return loader.load(name)


def load_template_from_yaml(yaml_content: str) -> SpreadsheetTemplate:
    """Load template from YAML string.

    Args:
        yaml_content: YAML content

    Returns:
        SpreadsheetTemplate object
    """
    loader = TemplateLoader()
    return loader.load_from_string(yaml_content)
