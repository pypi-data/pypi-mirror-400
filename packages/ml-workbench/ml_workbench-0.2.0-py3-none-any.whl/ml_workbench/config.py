from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from copy import deepcopy
from pathlib import Path
from string import Formatter
from typing import Any, Union

import yaml

YamlPrimitive = Union[str, int, float, bool, None]              # noqa: UP007
YamlValue = Union[YamlPrimitive, "YamlDict", "YamlList"]       # noqa: UP007
YamlDict = dict[str, YamlValue]
YamlList = list[YamlValue]


def _extract_field_names(template: str) -> list[str]:
    """Return field names used in a ``str.format``-style template string.

    Example: "{catalog}.{schema}.table" -> ["catalog", "schema"]
    """

    field_names: list[str] = []
    for _literal_text, field_name, _format_spec, _conversion in Formatter().parse(
        template
    ):
        if field_name:  # skip None and empty
            field_names.append(field_name)
    return field_names


def _interpolate_string(
    value: str, variables: Mapping[str, Any], *, strict: bool
) -> str:
    """Interpolate placeholders in a string using ``variables``.

    - If ``strict`` is True (default), raise a KeyError if any placeholder is missing.
    - If ``strict`` is False, leave unknown placeholders as-is.
    """

    if "{" not in value or "}" not in value:
        return value

    placeholders = _extract_field_names(value)
    if not placeholders:
        return value

    missing = [name for name in placeholders if name not in variables]
    if missing and strict:
        raise KeyError(  # noqa: TRY003
            f"Missing values for placeholders {missing} while formatting: {value!r}"
        )

    class _DefaultDict(dict):
        def __missing__(self, key: str) -> str:  # type: ignore[override]
            return "{" + key + "}"

    mapping: Mapping[str, Any]
    mapping = variables if strict else _DefaultDict(variables)  # type: ignore[arg-type]
    return value.format_map(mapping)  # type: ignore[arg-type]


def _interpolate_value(
    value: YamlValue, variables: Mapping[str, Any], *, strict: bool
) -> YamlValue:
    if isinstance(value, str):
        return _interpolate_string(value, variables, strict=strict)
    if isinstance(value, dict):
        return {
            k: _interpolate_value(v, variables, strict=strict) for k, v in value.items()
        }
    if isinstance(value, list):
        return [_interpolate_value(v, variables, strict=strict) for v in value]
    return value


def _wrap(value: YamlValue) -> Any:
    if isinstance(value, dict):
        return _ConfigNode(value)
    if isinstance(value, list):
        return [_wrap(v) for v in value]
    return value


def _unwrap(value: Any) -> YamlValue:
    if isinstance(value, _ConfigNode):
        return {k: _unwrap(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_unwrap(v) for v in value]
    return value


## moved to dataset.py: _is_databricks_table_name, _infer_dataset_format_from_path


class _ConfigNode(MutableMapping[str, Any]):
    """Lightweight mapping that supports both dict- and attribute-style access.

    This is used for nested configuration sections.
    """

    def __init__(self, data: YamlDict) -> None:
        self._data: YamlDict = data

    # Mapping interface
    def __getitem__(self, key: str) -> Any:
        return _wrap(self._data[key])

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = _unwrap(value)

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __iter__(self) -> Iterable[str]:
        return iter(self._data)

    def __len__(self) -> int:  # noqa: D401 - trivial
        return len(self._data)

    # Attribute-style access
    def __getattr__(self, name: str) -> Any:
        try:
            return _wrap(self._data[name])
        except KeyError as exc:
            raise AttributeError(name) from exc  # noqa: TRY003

    def get(self, key: str, default: Any | None = None) -> Any:
        if key in self._data:
            return _wrap(self._data[key])
        return default

    def to_dict(self) -> YamlDict:
        return deepcopy(self._data)

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"_ConfigNode({self._data!r})"


class YamlConfig(_ConfigNode):
    """Configuration loaded from a YAML file with placeholder interpolation.

    Placeholders use Python's ``str.format`` style, e.g. "{catalog}".
    Values for placeholders are assembled as:
    1) ``defaults`` key from the YAML file (if present), then
    2) Keyword arguments provided to the constructor, which override defaults.

    Parameters
    ----------
    yaml_path:
        Path to the YAML file.
    strict:
        If True (default), raise when placeholders are missing. If False, leave
        unknown placeholders unchanged.
    **variables:
        Additional key/value pairs to use for placeholder interpolation.
    """

    def __init__(
        self, yaml_path: str | Path, *, strict: bool = True, **variables: Any
    ) -> None:
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")  # noqa: TRY003

        # Load YAML with recursive include processing
        loaded = self._load_with_includes(path, set())

        if not isinstance(loaded, dict):
            raise TypeError("Top-level YAML structure must be a mapping (dict)")  # noqa: TRY003

        defaults_section: Mapping[str, Any] = (
            loaded.get("defaults", {})
            if isinstance(loaded.get("defaults", {}), dict)
            else {}
        )

        # Merge defaults with user-supplied variables (kwargs override defaults)
        variables_merged: dict[str, Any] = {**defaults_section, **variables}

        # Interpolate placeholders across the entire loaded YAML structure
        interpolated: YamlDict = _interpolate_value(
            loaded, variables_merged, strict=strict
        )  # type: ignore[assignment]

        super().__init__(interpolated)
        self.path: Path = path
        self.variables: dict[str, Any] = variables_merged
        self.strict: bool = strict

        # Post-process datasets to impute missing information
        # Delayed import to avoid circular dependency
        from .dataset import Dataset  # noqa: PLC0415

        Dataset.verify_config(self)

        from .feature import Feature  # noqa: PLC0415

        Feature.verify_config(self)

        from .model import Model  # noqa: PLC0415

        Model.verify_config(self)

        from .experiment import Experiment  # noqa: PLC0415

        Experiment.verify_config(self)

        from .mlflow_conf import MlflowConf  # noqa: PLC0415

        MlflowConf.verify_config(self)

    def _load_with_includes(
        self, yaml_path: Path, visited: set[Path]
    ) -> dict[str, Any]:
        """
        Load a YAML file and recursively process any 'include' directives.

        The 'include' field should be a list of file paths (relative to the current file
        or absolute). Included files are merged into the current file, with the current
        file's values taking precedence.

        Parameters
        ----------
        yaml_path : Path
            Path to the YAML file to load
        visited : set[Path]
            Set of already visited paths to prevent circular includes

        Returns
        -------
        Dict[str, Any]
            Merged dictionary from all included files and the current file

        Raises
        ------
        ValueError
            If a circular include is detected
        """
        # Resolve to absolute path to detect circular includes
        abs_path = yaml_path.resolve()

        if abs_path in visited:
            raise ValueError(f"Circular include detected: {abs_path}")  # noqa: TRY003

        visited.add(abs_path)

        # Load the current file
        with abs_path.open("r", encoding="utf-8") as f:
            current_data: Any = yaml.safe_load(f) or {}

        if not isinstance(current_data, dict):
            return current_data

        # Check for 'include' directive
        include_list = current_data.pop("include", None)

        if include_list is None:
            return current_data

        # Ensure include is a list
        if not isinstance(include_list, list):
            raise TypeError(  # noqa: TRY003
                f"'include' directive must be a list, got {type(include_list).__name__}"
            )

        # Start with an empty result
        result: dict[str, Any] = {}

        # Process each included file
        for include_path_str in include_list:
            if not isinstance(include_path_str, str):
                raise TypeError(  # noqa: TRY003
                    f"Include path must be a string, got {type(include_path_str).__name__}"
                )

            # Resolve include path
            include_path = Path(include_path_str)
            if not include_path.is_absolute():
                # Try relative to current file's directory first
                relative_to_current = abs_path.parent / include_path
                if relative_to_current.exists():
                    include_path = relative_to_current
                else:
                    # Try relative to project root (parent of current file's parent)
                    # This handles cases like "snippets/datasets.yaml" from "snippets/features.yaml"
                    project_root = abs_path.parent.parent
                    relative_to_root = project_root / include_path
                    if relative_to_root.exists():
                        include_path = relative_to_root
                    else:
                        # Neither worked, raise error with both attempted paths
                        raise FileNotFoundError(  # noqa: TRY003
                            f"Included file not found: {include_path_str}\n"
                            f"  Tried: {relative_to_current}\n"
                            f"  Tried: {relative_to_root}"
                        )

            if not include_path.exists():
                raise FileNotFoundError(f"Included file not found: {include_path}")  # noqa: TRY003

            # Recursively load the included file
            included_data = self._load_with_includes(include_path, visited.copy())

            # Merge included data into result (deep merge)
            result = self._deep_merge(result, included_data)

        # Merge current file's data on top (current file takes precedence)
        return self._deep_merge(result, current_data)

    def _deep_merge(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Deep merge two dictionaries, with override taking precedence.

        Parameters
        ----------
        base : Dict[str, Any]
            Base dictionary
        override : Dict[str, Any]
            Override dictionary (takes precedence)

        Returns
        -------
        Dict[str, Any]
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override takes precedence
                result[key] = value

        return result

    @classmethod
    def from_file(
        cls, yaml_path: str | Path, *, strict: bool = True, **variables: Any
    ) -> YamlConfig:
        return cls(yaml_path, strict=strict, **variables)

    def to_dict(self) -> YamlDict:
        return deepcopy(self._data)

    def get_data(self) -> YamlDict:
        """Get the raw configuration data dictionary.

        Returns
        -------
        YamlDict
            The raw configuration data dictionary
        """
        return self._data

    def reload(self, *, strict: bool | None = None, **variables: Any) -> None:
        """Reload the YAML file, optionally overriding variables and strictness.

        Useful if the file or variables have changed.
        """

        new_strict = self.strict if strict is None else strict
        updated_vars = {**self.variables, **variables}
        refreshed = type(self).from_file(self.path, strict=new_strict, **updated_vars)
        # Replace internal state
        self._data = refreshed.get_data()
        self.variables = refreshed.variables
        self.strict = refreshed.strict

    def get_datasets_list(self) -> list[str]:
        """Return list of dataset names defined in the configuration.

        Returns
        -------
        List[str]
            List of dataset names, or empty list if no datasets section exists
        """
        datasets = self._data.get("datasets")
        if not isinstance(datasets, dict):
            return []
        return list(datasets.keys())

    def get_dataset_config(self, name: str) -> YamlDict:
        """Return configuration dictionary for a specific dataset.

        Parameters
        ----------
        name : str
            Dataset name

        Returns
        -------
        YamlDict
            Dataset configuration as a plain dictionary

        Raises
        ------
        KeyError
            If dataset with given name does not exist
        """
        datasets = self._data.get("datasets")
        if not isinstance(datasets, dict):
            raise KeyError("No datasets section found in configuration")  # noqa: TRY003

        if name not in datasets:
            raise KeyError(f"Dataset '{name}' not found in configuration")  # noqa: TRY003

        dataset_spec = datasets[name]
        if isinstance(dataset_spec, dict):
            return deepcopy(dataset_spec)

        raise TypeError(f"Dataset '{name}' configuration is not a valid mapping")  # noqa: TRY003

    # Internal utilities


__all__ = ["YamlConfig"]
