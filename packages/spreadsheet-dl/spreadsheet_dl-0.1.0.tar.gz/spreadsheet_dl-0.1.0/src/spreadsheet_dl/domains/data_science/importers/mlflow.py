"""MLflow experiment data importer.

MLflowImporter for data science domain
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spreadsheet_dl.domains.base import BaseImporter, ImporterMetadata, ImportResult


class MLflowImporter(BaseImporter[list[dict[str, Any]]]):
    """MLflow experiment data importer.

        MLflowImporter for ML experiment tracking

    Features:
    - Parse MLflow JSON exports
    - Extract run ID, metrics, parameters, artifacts
    - Map to ExperimentLogTemplate format
    - Handle nested metric dictionaries
    - Optional: Direct API connection (future enhancement)

    Supported formats:
    - MLflow JSON export files
    - MLflow runs export

    Example:
        >>> importer = MLflowImporter()
        >>> importer.metadata is not None
        True
        >>> result = importer.import_data("mlflow_runs.json")  # doctest: +SKIP
        >>> if result.success:  # doctest: +SKIP
        ...     for run in result.data:
        ...         print(f"Run {run['run_id']}: {run['metrics']}")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize importer."""
        super().__init__(**kwargs)

    @property
    def metadata(self) -> ImporterMetadata:
        """Get importer metadata.

        Returns:
            ImporterMetadata for MLflow importer

            Importer metadata
        """
        return ImporterMetadata(
            name="MLflow Importer",
            description="Import ML experiment data from MLflow JSON exports",
            supported_formats=("json",),
            category="data_science",
        )

    def validate_source(self, source: Path | str) -> bool:
        """Validate MLflow JSON source file.

        Args:
            source: Path to JSON file

        Returns:
            True if source is valid JSON file

            Source validation
        """
        path = Path(source) if isinstance(source, str) else source
        return path.exists() and path.is_file() and path.suffix.lower() == ".json"

    def import_data(self, source: Path | str) -> ImportResult[list[dict[str, Any]]]:
        """Import experiment data from MLflow JSON file.

        Args:
            source: Path to MLflow JSON file

        Returns:
            ImportResult with experiment data

            MLflow data import

        Expected JSON format:
            [
                {
                    "run_id": "abc123",
                    "experiment_id": "1",
                    "status": "FINISHED",
                    "start_time": 1234567890,
                    "end_time": 1234567900,
                    "metrics": {"accuracy": 0.92, "loss": 0.15},
                    "params": {"lr": 0.001, "batch_size": 32},
                    "tags": {...},
                    "artifact_uri": "..."
                }
            ]

        Raises:
            ValueError: If source is invalid
            IOError: If file cannot be read
        """
        if not self.validate_source(source):
            return ImportResult(
                success=False,
                data=[],
                errors=["Invalid JSON file or file does not exist"],
            )

        path = Path(source) if isinstance(source, str) else source

        try:
            # Read JSON file
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both single run and list of runs
            if isinstance(data, dict):
                runs = [data]
            elif isinstance(data, list):
                runs = data
            else:
                return ImportResult(
                    success=False,
                    data=[],
                    errors=["Invalid MLflow JSON format: expected dict or list"],
                )

            # Parse runs
            experiments = []
            warnings = []

            for idx, run in enumerate(runs):
                try:
                    experiment = self._parse_run(run)
                    experiments.append(experiment)
                    self.on_progress(idx + 1, len(runs))
                except Exception as e:
                    warnings.append(f"Error parsing run {idx}: {e!s}")

            return ImportResult(
                success=True,
                data=experiments,
                records_imported=len(experiments),
                warnings=warnings,
                metadata={
                    "total_runs": len(runs),
                    "successful_imports": len(experiments),
                },
            )

        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Invalid JSON format: {e!s}"],
            )
        except Exception as e:
            return ImportResult(
                success=False,
                data=[],
                errors=[f"Error reading MLflow data: {e!s}"],
            )

    def _parse_run(self, run: dict[str, Any]) -> dict[str, Any]:
        """Parse individual MLflow run.

        Args:
            run: MLflow run dictionary

        Returns:
            Parsed experiment data for ExperimentLogTemplate

            MLflow run parsing
        """
        # Extract core fields
        run_id = run.get("run_id", run.get("info", {}).get("run_id", "unknown"))
        status = run.get("status", run.get("info", {}).get("status", "unknown"))

        # Extract timestamps
        start_time = run.get("start_time", run.get("info", {}).get("start_time"))
        end_time = run.get("end_time", run.get("info", {}).get("end_time"))

        # Calculate duration
        duration = None
        if start_time and end_time:
            # MLflow timestamps are in milliseconds
            duration = (end_time - start_time) / 1000.0

        # Extract metrics
        metrics = run.get("metrics", run.get("data", {}).get("metrics", {}))
        if isinstance(metrics, dict):
            # Flatten metrics if they contain history
            flat_metrics = {
                k: v[-1] if isinstance(v, list) and len(v) > 0 else v
                for k, v in metrics.items()
            }
        else:
            flat_metrics = {}

        # Extract parameters
        params = run.get("params", run.get("data", {}).get("params", {}))

        # Extract tags
        tags = run.get("tags", run.get("data", {}).get("tags", {}))

        # Build experiment record
        experiment = {
            "run_id": run_id,
            "status": status,
            "duration": duration,
            "metrics": flat_metrics,
            "params": params,
            "tags": tags,
            "artifact_uri": run.get(
                "artifact_uri", run.get("info", {}).get("artifact_uri")
            ),
        }

        # Add individual metric fields for common metrics
        for metric_name in (
            "accuracy",
            "loss",
            "val_accuracy",
            "val_loss",
            "f1",
            "precision",
            "recall",
        ):
            if metric_name in flat_metrics:
                experiment[metric_name] = flat_metrics[metric_name]

        # Add individual param fields for common hyperparameters
        for param_name in ("learning_rate", "lr", "batch_size", "epochs"):
            if param_name in params:
                try:
                    # Try to convert to number
                    value = float(params[param_name])
                    experiment[param_name] = value
                except (ValueError, TypeError):
                    experiment[param_name] = params[param_name]

        return experiment


__all__ = ["MLflowImporter"]
