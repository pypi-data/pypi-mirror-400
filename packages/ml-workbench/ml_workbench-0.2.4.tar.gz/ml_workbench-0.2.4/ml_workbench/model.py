from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .config import YamlConfig


@dataclass(frozen=True)
class ModelSpec:
    name: str
    type: str
    description: str | None
    params: dict[str, Any]
    tuning: dict[str, Any]


class Model:
    """Encapsulates a model definition from the configuration.

    Expected YAML structure:

        models:
          my_model:
            description: "..."           # optional
            type: "package.module.Class"  # required
            params: { ... }                # optional, free-form dict
            tuning: { ... }                # optional, free-form dict

    Notes
    -----
    - The ``params`` and ``tuning`` sections are model-specific and are stored as given.
    - Use ``instantiate()`` to create the model class instance with provided params.
    """

    def __init__(self, name: str, config: YamlConfig) -> None:
        self.name = name
        self.config = config

        models_section = self._get_models_section(config)
        if name not in models_section:
            raise KeyError(f"Model '{name}' not found in configuration")  # noqa: TRY003

        raw = models_section[name]
        if not isinstance(raw, Mapping):
            raise TypeError(f"Model '{name}' specification must be a mapping")  # noqa: TRY003

        model_type = raw.get("type")
        if not isinstance(model_type, str) or not model_type:
            raise ValueError(f"Model '{name}' is missing required 'type' string field")  # noqa: TRY003

        description = raw.get("description")
        params = raw.get("params", {})
        tuning = raw.get("tuning", {})

        if not isinstance(params, Mapping):
            raise TypeError(f"Model '{name}'.params must be a mapping if provided")  # noqa: TRY003
        if not isinstance(tuning, Mapping):
            raise TypeError(f"Model '{name}'.tuning must be a mapping if provided")  # noqa: TRY003

        self.spec = ModelSpec(
            name=name,
            type=model_type,
            description=description if isinstance(description, str) else None,
            params=dict(params),
            tuning=dict(tuning),
        )

    @staticmethod
    def _get_models_section(config: YamlConfig) -> Mapping[str, Any]:
        models = config.get_data().get("models")
        if not isinstance(models, Mapping):
            raise KeyError("No 'models' section found in configuration")  # noqa: TRY003
        return models

    @staticmethod
    def _import_string(path: str) -> tuple[object, str]:
        """Import a dotted path like 'package.module.Class'.

        Returns the imported module object and the class name.
        """
        if "." not in path:
            raise ValueError(  # noqa: TRY003
                f"Invalid model type path '{path}'. Expected 'package.module.Class'"
            )
        module_path, class_name = path.rsplit(".", 1)
        module = import_module(module_path)
        return module, class_name

    def instantiate(self, **overrides: Any) -> Any:
        """Instantiate the model class using configured params.

        Parameters
        ----------
        overrides: Any
            Optional overrides for parameters when constructing the model.
        """
        module, cls_name = self._import_string(self.spec.type)
        cls = getattr(module, cls_name)
        init_kwargs = {**self.spec.params, **overrides}
        return cls(**init_kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.spec.name,
            "type": self.spec.type,
            "description": self.spec.description,
            "params": dict(self.spec.params),
            "tuning": dict(self.spec.tuning),
        }

    @classmethod
    def list_model_names(cls, config: YamlConfig) -> list[str]:
        models = cls._get_models_section(config)
        return list(models.keys())

    @classmethod
    def verify_config(cls, config: YamlConfig) -> None:
        """Validate that all models are well-formed.

        Checks
        ------
        - models section exists and is a mapping
        - each model has a non-empty string 'type'
        - params and tuning, if present, are mappings
        """
        models = config.get_data().get("models")
        if models is None:
            return
        if not isinstance(models, Mapping):
            raise TypeError("'models' section must be a mapping")  # noqa: TRY003

        for model_name, raw in models.items():
            if not isinstance(raw, Mapping):
                raise TypeError(  # noqa: TRY003
                    f"Model '{model_name}' specification must be a mapping"
                )
            model_type = raw.get("type")
            if not isinstance(model_type, str) or not model_type:
                raise ValueError(  # noqa: TRY003
                    f"Model '{model_name}' is missing required 'type' string field"
                )
            params = raw.get("params", {})
            tuning = raw.get("tuning", {})
            if not isinstance(params, Mapping):
                raise TypeError(  # noqa: TRY003
                    f"Model '{model_name}'.params must be a mapping if provided"
                )
            if not isinstance(tuning, Mapping):
                raise TypeError(  # noqa: TRY003
                    f"Model '{model_name}'.tuning must be a mapping if provided"
                )


__all__ = ["Model", "ModelSpec"]
