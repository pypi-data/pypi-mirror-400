from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
import warnings

import pandas as pd

if TYPE_CHECKING:
    from .config import YamlConfig

# Valid experiment types
VALID_EXPERIMENT_TYPES = ["regression", "classification"]


@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    description: str | None
    models: list[str]
    dataset: str
    target: str
    features: str
    do_not_split_by: list[str]
    metrics: list[str]
    hold_out: dict[str, Any]
    drop_outliers: float | None
    type: str | None


class Experiment:
    """Encapsulates an experiment definition from configuration.

    Expected structure under ``experiments``:

        experiments:
          exp_name:
            description: description_text                  # optional
            models: model_name or [model1, model2]         # required (one or many model names)
            dataset: dataset_name                           # required (one dataset name)
            target: target_name                              # required (one target name)
            features: feature_name                          # required (single feature name)
            type: regression or classification              # optional (experiment type)
            do_not_split_by: [col]                           # optional (one or many column names)
            metrics: metric_name or [metric1, metric2]       # optional (one or many metric names)
            hold_out: { ... }                                # optional
            drop_outliers: 3.0 or 0.0 or false               # optional (default: 3.0, disable with 0.0 or false)

        Note: The 'split' component is deprecated and will be ignored if present.
        Use 'hold_out' instead for creating holdout sets.

    If ``type`` is not specified, it will remain None until inference in the Runner,
    where it will be inferred from the target column type:
    - If target is numeric -> type="regression"
    - If target is categorical -> type="classification"
    """

    def __init__(self, config: YamlConfig, name: str | None = None) -> None:
        self.config = config

        experiments = self._get_experiments_section(config)

        # If name is None, use the first experiment in the config
        if name is None:
            if not experiments:
                raise KeyError("No experiments found in configuration")  # noqa: TRY003
            name = next(iter(experiments))

        if name not in experiments:
            raise KeyError(f"Experiment '{name}' not found in configuration")  # noqa: TRY003

        self.name = name
        raw = experiments[name]
        if not isinstance(raw, Mapping):
            raise TypeError(f"Experiment '{name}' specification must be a mapping")  # noqa: TRY003

        description = raw.get("description")
        models = raw.get("models")
        dataset = raw.get("dataset")
        target = raw.get("target")
        features = raw.get("features")

        if isinstance(models, str):
            models_list = [models]
        elif isinstance(models, Sequence):
            models_list = [str(m) for m in list(models)]
        else:
            raise TypeError(  # noqa: TRY003
                f"Experiment '{name}' missing required 'models' (str or list)"
            )

        if not isinstance(dataset, str) or not dataset:
            raise ValueError(f"Experiment '{name}' missing required 'dataset' string")  # noqa: TRY003

        if not isinstance(target, str) or not target:
            raise ValueError(f"Experiment '{name}' missing required 'target' string")  # noqa: TRY003

        if not isinstance(features, str) or not features:
            raise ValueError(f"Experiment '{name}' missing required 'features' string")  # noqa: TRY003

        do_not_split_by = raw.get("do_not_split_by", [])
        if isinstance(do_not_split_by, str):
            do_not_split_by_list = [do_not_split_by]
        elif isinstance(do_not_split_by, Sequence):
            do_not_split_by_list = [str(c) for c in list(do_not_split_by)]
        else:
            do_not_split_by_list = []

        metrics = raw.get("metrics", [])
        if isinstance(metrics, str):
            metrics_list = [metrics]
        elif isinstance(metrics, Sequence):
            metrics_list = [str(m) for m in list(metrics)]
        else:
            metrics_list = []

        # Warn if 'split' is present (deprecated)
        if "split" in raw:
            warnings.warn(
                f"Experiment '{name}' contains deprecated 'split' component. "
                "It will be ignored. Use 'hold_out' instead for creating holdout sets.",
                DeprecationWarning,
                stacklevel=2,
            )

        hold_out = raw.get("hold_out", {})
        hold_out_dict = dict(hold_out) if isinstance(hold_out, Mapping) else {}

        # Parse drop_outliers: default 3.0, disable with 0.0 or false
        drop_outliers_raw = raw.get("drop_outliers", 3.0)
        drop_outliers_value: float | None = None
        if drop_outliers_raw is False or drop_outliers_raw == "false":
            drop_outliers_value = None
        elif isinstance(drop_outliers_raw, int | float):
            drop_outliers_float = float(drop_outliers_raw)
            if drop_outliers_float == 0.0:
                drop_outliers_value = None
            else:
                drop_outliers_value = drop_outliers_float
        elif (
            isinstance(drop_outliers_raw, str) and drop_outliers_raw.lower() == "false"
        ):
            drop_outliers_value = None
        else:
            # Default to 3.0 if invalid type
            drop_outliers_value = 3.0

        experiment_type = raw.get("type")
        experiment_type_str = None
        if isinstance(experiment_type, str):
            # Convert to lowercase and validate
            experiment_type_lower = experiment_type.lower()
            if experiment_type_lower not in VALID_EXPERIMENT_TYPES:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{name}' has invalid type '{experiment_type}'. "
                    f"Valid types are: {', '.join(VALID_EXPERIMENT_TYPES)}"
                )
            experiment_type_str = experiment_type_lower

        self.spec = ExperimentSpec(
            name=name,
            description=description if isinstance(description, str) else None,
            models=models_list,
            dataset=dataset,
            target=target,
            features=features,
            do_not_split_by=do_not_split_by_list,
            metrics=metrics_list,
            hold_out=hold_out_dict,
            drop_outliers=drop_outliers_value,
            type=experiment_type_str,
        )

        # Store inferred type separately (since spec is frozen)
        self._inferred_type: str | None = None

    @staticmethod
    def _get_experiments_section(config: YamlConfig) -> Mapping[str, Any]:
        experiments = config.get_data().get("experiments")
        if not isinstance(experiments, Mapping):
            raise KeyError("No 'experiments' section found in configuration")  # noqa: TRY003
        return experiments

    def infer_type_from_dataset(self, dataset: pd.DataFrame) -> str:
        """Infer experiment type from target column dtype.

        Parameters
        ----------
        dataset : pd.DataFrame
            Dataset containing the target column

        Returns
        -------
        str
            Inferred type: "regression" if target is numeric, "classification" if categorical

        Raises
        ------
        ValueError
            If inferred type is not in VALID_EXPERIMENT_TYPES
        """
        target = self.spec.target
        if target not in dataset.columns:
            raise ValueError(f"Target column '{target}' not found in dataset")  # noqa: TRY003

        target_dtype = dataset[target].dtype
        if pd.api.types.is_numeric_dtype(target_dtype):
            inferred_type = "regression"
        else:
            inferred_type = "classification"

        # Validate inferred type (should always be valid, but check for safety)
        if inferred_type not in VALID_EXPERIMENT_TYPES:
            raise ValueError(  # noqa: TRY003
                f"Inferred type '{inferred_type}' is not in valid types: {', '.join(VALID_EXPERIMENT_TYPES)}"
            )

        self._inferred_type = inferred_type
        return inferred_type

    def get_type(self) -> str | None:
        """Get experiment type, returning configured type or inferred type.

        Returns
        -------
        Optional[str]
            Experiment type: "regression", "classification", or None if not yet inferred
        """
        if self.spec.type is not None:
            return self.spec.type
        return self._inferred_type

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.spec.name,
            "description": self.spec.description,
            "models": list(self.spec.models),
            "dataset": self.spec.dataset,
            "target": self.spec.target,
            "features": self.spec.features,
            "type": self.get_type(),
            "do_not_split_by": list(self.spec.do_not_split_by),
            "metrics": list(self.spec.metrics),
            "hold_out": dict(self.spec.hold_out),
            "drop_outliers": self.spec.drop_outliers,
        }

    @classmethod
    def list_experiment_names(cls, config: YamlConfig) -> list[str]:
        return list(cls._get_experiments_section(config).keys())

    @classmethod
    def verify_config(cls, config: YamlConfig) -> None:
        """Validate experiments reference existing models, datasets, and features.

        Only performs validation if an 'experiments' section exists.
        """
        experiments = config.get_data().get("experiments")
        if experiments is None:
            return
        if not isinstance(experiments, Mapping):
            raise TypeError("'experiments' section must be a mapping")  # noqa: TRY003

        datasets = config.get_data().get("datasets")
        features = config.get_data().get("features")
        models = config.get_data().get("models")

        if not isinstance(datasets, Mapping):
            raise TypeError("No 'datasets' section found while validating experiments")  # noqa: TRY003
        if not isinstance(features, Mapping):
            raise TypeError("No 'features' section found while validating experiments")  # noqa: TRY003
        if not isinstance(models, Mapping):
            raise TypeError("No 'models' section found while validating experiments")  # noqa: TRY003

        for exp_name, raw in experiments.items():
            if not isinstance(raw, Mapping):
                raise TypeError(  # noqa: TRY003
                    f"Experiment '{exp_name}' specification must be a mapping"
                )

            # Dataset must exist
            ds_name = raw.get("dataset")
            if not isinstance(ds_name, str) or not ds_name:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{exp_name}' missing required 'dataset' string"
                )
            if ds_name not in datasets:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{exp_name}' references unknown dataset '{ds_name}'"
                )

            # Target must be provided as a single string
            tgt_field = raw.get("target")
            if not isinstance(tgt_field, str) or not tgt_field:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{exp_name}' missing required 'target' string"
                )

            # Models must exist
            model_field = raw.get("models")
            model_names: list[str]
            if isinstance(model_field, str):
                model_names = [model_field]
            elif isinstance(model_field, Sequence):
                model_names = [str(m) for m in list(model_field)]
            else:
                raise TypeError(  # noqa: TRY003
                    f"Experiment '{exp_name}' missing required 'models' (str or list)"
                )
            missing_models = [m for m in model_names if m not in models]
            if missing_models:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{exp_name}' references unknown models: {', '.join(missing_models)}"
                )

            # Features must exist
            feature_field = raw.get("features")
            if not isinstance(feature_field, str) or not feature_field:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{exp_name}' missing required 'features' string"
                )
            if feature_field not in features:
                raise ValueError(  # noqa: TRY003
                    f"Experiment '{exp_name}' references unknown feature '{feature_field}'"
                )

            # Validate type if specified
            type_field = raw.get("type")
            if isinstance(type_field, str):
                type_lower = type_field.lower()
                if type_lower not in VALID_EXPERIMENT_TYPES:
                    raise ValueError(  # noqa: TRY003
                        f"Experiment '{exp_name}' has invalid type '{type_field}'. "
                        f"Valid types are: {', '.join(VALID_EXPERIMENT_TYPES)}"
                    )


__all__ = ["Experiment", "ExperimentSpec"]
