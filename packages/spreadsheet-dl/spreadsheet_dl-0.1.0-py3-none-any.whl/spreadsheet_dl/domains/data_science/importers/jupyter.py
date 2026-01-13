"""Jupyter notebook metadata importer.

JupyterMetadataImporter for data science domain
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class JupyterMetadataImporter(BaseImporter[dict[str, Any]]):
    """Jupyter notebook metadata extractor.

        JupyterMetadataImporter for notebook analysis

    Features:
    - Read .ipynb files
    - Extract cell count and types
    - Extract kernel information
    - Calculate execution times
    - Extract markdown headers
    - Create summary metadata dict

    Example:
        >>> importer = JupyterMetadataImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("analysis.ipynb")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     metadata = result.data
        ...     print(f"Cells: {metadata['cell_count']}")
        ...     print(f"Kernel: {metadata['kernel']}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for Jupyter importer

            Importer metadata
        """
        return ImporterMetadata(
            name="Jupyter Metadata Importer",
            description="Extract metadata and statistics from Jupyter notebooks",
            supported_formats=("ipynb",),
            category="data_science",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate Jupyter notebook source file.

        Args:
            source: Path to .ipynb file

        Returns:
            True if source is valid notebook file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.is_file() and path.suffix.lower() == ".ipynb"

    def import_data(self, source: Path | str) -> ImportResult[dict[str, Any]]:
        """Import metadata from Jupyter notebook.

        Args:
            source: Path to .ipynb file

        Returns:
            ImportResult with notebook metadata

            Jupyter metadata extraction

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data={},
                errors=["Invalid .ipynb file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            # Read notebook file
            with path.open("r", encoding="utf-8") as f:
                notebook = json.load(f)

            # Extract metadata
            metadata = self._extract_metadata(notebook, path)

            return ImportResult(
                success=True,
                data=metadata,
                records_imported=1,
                metadata={
                    "notebook_file": str(path.name),
                    "notebook_format": notebook.get("nbformat", "unknown"),
                },
            )

        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                data={},
                errors=[f"Invalid JSON format: {e!s}"],
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data={},
                errors=[f"Error reading notebook: {e!s}"],
            )

    def _extract_metadata(self, notebook: dict[str, Any], path: Path) -> dict[str, Any]:
        """Extract metadata from notebook JSON.

        Args:
            notebook: Parsed notebook JSON
            path: Path to notebook file

        Returns:
            Dictionary with notebook metadata

            Metadata extraction logic
        """
        # Get cells
        cells = notebook.get("cells", [])

        # Count cells by type
        code_cells = [c for c in cells if c.get("cell_type") == "code"]
        markdown_cells = [c for c in cells if c.get("cell_type") == "markdown"]
        raw_cells = [c for c in cells if c.get("cell_type") == "raw"]

        # Extract kernel info
        kernel_spec = notebook.get("metadata", {}).get("kernelspec", {})
        kernel_name = kernel_spec.get("name", "unknown")
        kernel_display_name = kernel_spec.get("display_name", kernel_name)

        # Calculate execution times
        total_execution_time = 0.0
        executed_cells = 0

        for cell in code_cells:
            # Check for execution count (indicates cell was executed)
            if cell.get("execution_count"):
                executed_cells += 1

                # Try to get execution time from metadata
                cell_metadata = cell.get("metadata", {})
                execution = cell_metadata.get("execution", {})

                # Some notebooks store timing info
                if (
                    "iopub.execute_input" in execution
                    and "iopub.status.idle" in execution
                ):
                    try:
                        start_str = execution["iopub.execute_input"]
                        end_str = execution["iopub.status.idle"]
                        # Parse ISO format timestamps
                        start_time = datetime.fromisoformat(
                            start_str.replace("Z", "+00:00")
                        )
                        end_time = datetime.fromisoformat(
                            end_str.replace("Z", "+00:00")
                        )
                        total_execution_time += (end_time - start_time).total_seconds()
                    except (KeyError, ValueError, AttributeError):
                        pass

        # Extract markdown headers
        headers = []
        for cell in markdown_cells:
            source = cell.get("source", [])
            if isinstance(source, list):
                source = "".join(source)

            # Find markdown headers (lines starting with #)
            for line in source.split("\n"):
                if line.strip().startswith("#"):
                    headers.append(line.strip())

        # Extract output types
        output_types = set()
        for cell in code_cells:
            outputs = cell.get("outputs", [])
            for output in outputs:
                output_type = output.get("output_type")
                if output_type:
                    output_types.add(output_type)

        # Build metadata dictionary
        metadata = {
            "notebook_name": path.name,
            "notebook_path": str(path.absolute()),
            "cell_count": len(cells),
            "code_cells": len(code_cells),
            "markdown_cells": len(markdown_cells),
            "raw_cells": len(raw_cells),
            "kernel": kernel_display_name,
            "kernel_name": kernel_name,
            "executed_cells": executed_cells,
            "execution_time": total_execution_time,
            "headers": headers,
            "header_count": len(headers),
            "output_types": list(output_types),
            "nbformat": notebook.get("nbformat"),
            "nbformat_minor": notebook.get("nbformat_minor"),
            "language": notebook.get("metadata", {})
            .get("language_info", {})
            .get("name", "unknown"),
        }

        return metadata


__all__ = ["JupyterMetadataImporter"]
