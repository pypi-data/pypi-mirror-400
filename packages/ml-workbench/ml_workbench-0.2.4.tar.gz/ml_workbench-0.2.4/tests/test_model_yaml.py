from __future__ import annotations

import sys
import types
from typing import TYPE_CHECKING

import pytest

from ml_workbench.config import YamlConfig
from ml_workbench.model import Model

if TYPE_CHECKING:
    from pathlib import Path


def test_model_list_and_basic_fields(tmp_path: Path) -> None:
    yaml_content = """
models:
  m1:
    type: package.module.Class
    description: "Test model 1"
    params:
      alpha: 1.0
    tuning:
      method: grid_search
  m2:
    type: another.module.Class
    params: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    names = set(Model.list_model_names(cfg))
    assert names == {"m1", "m2"}

    m1 = Model("m1", cfg)
    d = m1.to_dict()
    assert d["name"] == "m1"
    assert d["type"] == "package.module.Class"
    assert d["description"] == "Test model 1"
    assert d["params"]["alpha"] == 1.0
    assert d["tuning"]["method"] == "grid_search"


def test_model_instantiate_with_params(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Create a temporary module with a Dummy model class
    module_name = "temp_dummy_model"
    module = types.ModuleType(module_name)

    class Dummy:
        def __init__(self, a: int, b: int = 0, **kwargs):
            self.a = a
            self.b = b
            self.kw = kwargs

    module.Dummy = Dummy
    sys.modules[module_name] = module

    yaml_content = f"""
models:
  dummy:
    type: "{module_name}.Dummy"
    params:
      a: 5
      b: 7
      extra: true
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    model = Model("dummy", cfg)
    inst = model.instantiate()

    assert isinstance(inst, Dummy)
    assert inst.a == 5
    assert inst.b == 7
    assert inst.kw == {"extra": True}


def test_model_verify_invalid_params_type(tmp_path: Path) -> None:
    yaml_content = """
models:
  bad:
    type: x.y.Z
    params: [1, 2, 3]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="params must be a mapping"):
        YamlConfig(yaml_file)


def test_model_verify_missing_type(tmp_path: Path) -> None:
    yaml_content = """
models:
  bad:
    params: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="missing required 'type'"):
        YamlConfig(yaml_file)
