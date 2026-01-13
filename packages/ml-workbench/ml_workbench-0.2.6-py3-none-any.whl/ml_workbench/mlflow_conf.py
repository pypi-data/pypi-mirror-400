from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .config import YamlConfig


@dataclass(frozen=True)
class MlflowSpec:
    enabled: bool
    type: str  # Always "local" or "databricks", inferred from MLFLOW_TRACKING_URI if not specified
    experiment_name_prefix: str
    tags: dict[str, Any]


class MlflowConf:
    """Encapsulates MLflow configuration from the YAML config.

    Expected YAML structure:

        mlflow:
          enabled: true                    # optional, defaults to True
          type: "local"                   # optional, "local" or "databricks", inferred from MLFLOW_TRACKING_URI if not specified
          experiment_name_prefix: "/Shared/"  # optional, defaults to ""
          tags:                            # optional, defaults to {}
            environment: "development"
            data_version: "v1"

    If the `mlflow` section is not present in the config, default values are used:
    - enabled: True
    - type: inferred from MLFLOW_TRACKING_URI env var (if starts with "databricks" -> "databricks", else "local")
    - experiment_name_prefix: ""
    - tags: {}
    """

    def __init__(self, config: YamlConfig) -> None:
        self.config = config

        mlflow_section = self._get_mlflow_section(config)

        # Extract values with defaults
        enabled = mlflow_section.get("enabled", True)
        if not isinstance(enabled, bool):
            raise TypeError("mlflow.enabled must be a boolean")  # noqa: TRY003

        mlflow_type = mlflow_section.get("type")
        if mlflow_type is not None and not isinstance(mlflow_type, str):
            raise TypeError("mlflow.type must be a string or None")  # noqa: TRY003
        # Validate type if provided
        if mlflow_type is not None:
            mlflow_type_lower = mlflow_type.lower()
            if mlflow_type_lower not in ("local", "databricks"):
                raise ValueError(  # noqa: TRY003
                    f"mlflow.type must be 'local' or 'databricks', got '{mlflow_type}'"
                )
            mlflow_type = mlflow_type_lower
        else:
            # If type not specified, infer from MLFLOW_TRACKING_URI environment variable
            tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "")
            if tracking_uri.startswith("databricks"):
                mlflow_type = "databricks"
            else:
                mlflow_type = "local"

        experiment_name_prefix = mlflow_section.get("experiment_name_prefix", "")
        if not isinstance(experiment_name_prefix, str):
            raise TypeError("mlflow.experiment_name_prefix must be a string")  # noqa: TRY003

        tags = mlflow_section.get("tags", {})
        if not isinstance(tags, Mapping):
            raise TypeError("mlflow.tags must be a mapping")  # noqa: TRY003

        self.spec = MlflowSpec(
            enabled=enabled,
            type=mlflow_type,
            experiment_name_prefix=experiment_name_prefix,
            tags=dict(tags),
        )

    @staticmethod
    def _get_mlflow_section(config: YamlConfig) -> Mapping[str, Any]:
        """Get mlflow section from config, returning empty dict if not present."""
        mlflow = config.get_data().get("mlflow")
        if mlflow is None:
            return {}
        if not isinstance(mlflow, Mapping):
            raise TypeError("'mlflow' section must be a mapping")  # noqa: TRY003
        return mlflow

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary representation of MLflow configuration."""
        return {
            "enabled": self.spec.enabled,
            "type": self.spec.type,
            "experiment_name_prefix": self.spec.experiment_name_prefix,
            "tags": dict(self.spec.tags),
        }

    def is_enabled(self) -> bool:
        """Check if MLflow tracking is enabled.

        Returns
        -------
        bool
            True if MLflow tracking is enabled, False otherwise
        """
        return self.spec.enabled

    def get_type(self) -> str:
        """Get the MLflow tracking type.

        Returns
        -------
        str
            The tracking type: "local" or "databricks"
        """
        return self.spec.type

    def get_tags(self) -> dict[str, Any]:
        """Get all tags.

        Returns
        -------
        dict[str, Any]
            All tags
        """
        return self.spec.tags

    def get_name(self, experiment_name: str) -> str:
        """Get the full experiment name by combining experiment name prefix with experiment name.

        Parameters
        ----------
        experiment_name : str
            The experiment name

        Returns
        -------
        str
            The full experiment name (prefix + experiment_name)
        """
        prefix = self.spec.experiment_name_prefix
        # Ensure prefix ends with / if it's not empty and doesn't already end with /
        if prefix and not prefix.endswith("/"):
            prefix = prefix + "/"
        # Remove leading / from experiment_name if prefix already has it
        if prefix.startswith("/") and experiment_name.startswith("/"):
            experiment_name = experiment_name.lstrip("/")
        return prefix + experiment_name

    @classmethod
    def verify_config(cls, config: YamlConfig) -> None:
        """Validate that mlflow section is well-formed if present.

        Checks
        ------
        - mlflow section, if present, is a mapping
        - enabled is a boolean (if provided)
        - type is "local" or "databricks" (if provided)
        - experiment_name_prefix is a string (if provided)
        - tags is a mapping (if provided)

        Notes
        -----
        If mlflow section is not present, validation passes (defaults will be used).
        """
        mlflow = config.get_data().get("mlflow")
        if mlflow is None:
            return  # Section not present, defaults will be used

        if not isinstance(mlflow, Mapping):
            raise TypeError("'mlflow' section must be a mapping")  # noqa: TRY003

        # Validate enabled if present
        enabled = mlflow.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            raise TypeError("mlflow.enabled must be a boolean")  # noqa: TRY003

        # Validate type if present
        mlflow_type = mlflow.get("type")
        if mlflow_type is not None:
            if not isinstance(mlflow_type, str):
                raise TypeError("mlflow.type must be a string")  # noqa: TRY003
            mlflow_type_lower = mlflow_type.lower()
            if mlflow_type_lower not in ("local", "databricks"):
                raise ValueError(  # noqa: TRY003
                    f"mlflow.type must be 'local' or 'databricks', got '{mlflow_type}'"
                )

        # Validate experiment_name_prefix if present
        experiment_name_prefix = mlflow.get("experiment_name_prefix")
        if experiment_name_prefix is not None and not isinstance(
            experiment_name_prefix, str
        ):
            raise TypeError("mlflow.experiment_name_prefix must be a string")  # noqa: TRY003

        # Validate tags if present
        tags = mlflow.get("tags")
        if tags is not None and not isinstance(tags, Mapping):
            raise TypeError("mlflow.tags must be a mapping")  # noqa: TRY003


__all__ = ["MlflowConf", "MlflowSpec"]
