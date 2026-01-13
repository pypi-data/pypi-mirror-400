from __future__ import annotations

from typing import TYPE_CHECKING
import warnings

import pytest

from ml_workbench.config import YamlConfig
from ml_workbench.experiment import Experiment

if TYPE_CHECKING:
    from pathlib import Path


def _base_yaml() -> str:
    return """
datasets:
  ds: {}

features:
  feat:
    dataset: ds
    columns: [value]

models:
  m:
    type: builtins.object
"""


def test_experiment_basic_parsing_and_lists(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    description: "Demo"
    models: m
    dataset: ds
    target: y
    features: feat
    split: { test_size: 0.2 }
    hold_out: { fraction: 0.0 }
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    names = Experiment.list_experiment_names(cfg)
    assert names == ["exp1"]

    exp = Experiment(cfg, "exp1")
    d = exp.to_dict()
    assert d["name"] == "exp1"
    assert d["description"] == "Demo"
    assert d["models"] == ["m"]
    assert d["dataset"] == "ds"
    assert d["target"] == "y"
    assert d["features"] == "feat"
    assert d["type"] is None  # Type not specified, should be None
    # split is deprecated and should not be in output
    assert "split" not in d
    assert d["hold_out"]["fraction"] == 0.0


def test_experiment_multiple_lists(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y1
    features: feat
    do_not_split_by: [participant_uuid]
    metrics: [r2, mae]
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")
    d = exp.to_dict()
    assert d["target"] == "y1"
    assert d["features"] == "feat"
    assert d["do_not_split_by"] == ["participant_uuid"]
    assert d["metrics"] == ["r2", "mae"]


def test_experiment_unknown_dataset_raises(tmp_path: Path) -> None:
    yaml_content = """
datasets: { ds: {} }
features: { feat: { dataset: ds, columns: [value] } }
models: { m: { type: builtins.object } }
experiments:
  exp1:
    models: [m]
    dataset: unknown_ds
    target: y
    features: feat
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="unknown dataset"):
        YamlConfig(yaml_file)


def test_experiment_unknown_model_raises(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [missing]
    dataset: ds
    target: y
    features: feat
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="unknown models"):
        YamlConfig(yaml_file)


def test_experiment_unknown_feature_raises(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: missing
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="unknown feature"):
        YamlConfig(yaml_file)


def test_experiment_missing_dataset_raises(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    target: y
    features: feat
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="missing required 'dataset'"):
        YamlConfig(yaml_file)


def test_experiment_missing_features_raises(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="missing required 'features'"):
        YamlConfig(yaml_file)


def test_experiment_missing_target_raises(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    features: feat
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="missing required 'target'"):
        YamlConfig(yaml_file)


def test_experiment_target_list_raises(tmp_path: Path) -> None:
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    features: feat
    target: [y1, y2]
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="missing required 'target'"):
        YamlConfig(yaml_file)


def test_experiment_type_optional(tmp_path: Path) -> None:
    """Test that type field is optional and can be specified."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    type: regression
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")
    d = exp.to_dict()
    assert d["type"] == "regression"
    assert exp.spec.type == "regression"
    assert exp.get_type() == "regression"


def test_experiment_type_lowercase_conversion(tmp_path: Path) -> None:
    """Test that type field is converted to lowercase."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    type: REGRESSION
  exp2:
    models: [m]
    dataset: ds
    target: y
    features: feat
    type: Classification
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    exp1 = Experiment(cfg, "exp1")
    assert exp1.spec.type == "regression"

    exp2 = Experiment(cfg, "exp2")
    assert exp2.spec.type == "classification"


def test_experiment_type_invalid_raises(tmp_path: Path) -> None:
    """Test that invalid type raises ValueError during config validation."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    type: invalid_type
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # ValueError is raised during YamlConfig initialization via verify_config
    with pytest.raises(ValueError, match="invalid type"):
        YamlConfig(yaml_file)


def test_experiment_type_inference(tmp_path: Path) -> None:
    """Test that type can be inferred from target column dtype."""
    import pandas as pd

    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")

    # Test regression inference (numeric target)
    df_numeric = pd.DataFrame({"y": [1, 2, 3, 4, 5], "value": [10, 20, 30, 40, 50]})
    inferred_type = exp.infer_type_from_dataset(df_numeric)
    assert inferred_type == "regression"
    assert exp.get_type() == "regression"

    # Test classification inference (categorical target)
    df_categorical = pd.DataFrame({
        "y": ["A", "B", "C", "A", "B"],
        "value": [10, 20, 30, 40, 50],
    })
    inferred_type = exp.infer_type_from_dataset(df_categorical)
    assert inferred_type == "classification"
    assert exp.get_type() == "classification"


def test_experiment_split_deprecated_warning(tmp_path: Path) -> None:
    """Test that a warning is issued when 'split' component is present."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    split: { test_size: 0.2, validation_size: 0.1 }
    hold_out: { fraction: 0.2 }
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Check that a DeprecationWarning is issued
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        exp = Experiment(cfg, "exp1")

        # Verify warning was issued
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated 'split' component" in str(w[0].message)
        assert "exp1" in str(w[0].message)

    # Verify split is not in the output
    d = exp.to_dict()
    assert "split" not in d
    # Verify hold_out is still present
    assert "hold_out" in d
    assert d["hold_out"]["fraction"] == 0.2


def test_experiment_split_ignored(tmp_path: Path) -> None:
    """Test that 'split' component is ignored even if present."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    split: { test_size: 0.2 }
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress warning for this test
        exp = Experiment(cfg, "exp1")

    # Verify experiment can be created successfully
    assert exp.name == "exp1"
    d = exp.to_dict()
    assert "split" not in d
    # Verify hold_out defaults to empty dict
    assert d["hold_out"] == {}


def test_experiment_name_optional_first_experiment(tmp_path: Path) -> None:
    """Test that if name is None, the first experiment is selected."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  first_exp:
    models: [m]
    dataset: ds
    target: y
    features: feat
  second_exp:
    models: [m]
    dataset: ds
    target: y
    features: feat
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Create experiment without specifying name - should pick first
    exp = Experiment(cfg)
    assert exp.name == "first_exp"
    d = exp.to_dict()
    assert d["name"] == "first_exp"


def test_experiment_name_optional_no_experiments_raises(tmp_path: Path) -> None:
    """Test that if name is None and no experiments exist, raises KeyError."""
    yaml_content = _base_yaml()  # No experiments section
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Should raise KeyError when no experiments section exists
    with pytest.raises(KeyError, match="No 'experiments' section found"):
        Experiment(cfg)


def test_experiment_drop_outliers_default(tmp_path: Path) -> None:
    """Test that drop_outliers defaults to 3.0 when omitted."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")

    assert exp.spec.drop_outliers == 3.0
    d = exp.to_dict()
    assert d["drop_outliers"] == 3.0


def test_experiment_drop_outliers_explicit(tmp_path: Path) -> None:
    """Test that drop_outliers can be set to a custom value."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    drop_outliers: 2.5
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")

    assert exp.spec.drop_outliers == 2.5
    d = exp.to_dict()
    assert d["drop_outliers"] == 2.5


def test_experiment_drop_outliers_disable_zero(tmp_path: Path) -> None:
    """Test that drop_outliers can be disabled with 0.0."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    drop_outliers: 0.0
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")

    assert exp.spec.drop_outliers is None
    d = exp.to_dict()
    assert d["drop_outliers"] is None


def test_experiment_drop_outliers_disable_false(tmp_path: Path) -> None:
    """Test that drop_outliers can be disabled with false."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    drop_outliers: false
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")

    assert exp.spec.drop_outliers is None
    d = exp.to_dict()
    assert d["drop_outliers"] is None


def test_experiment_drop_outliers_disable_string_false(tmp_path: Path) -> None:
    """Test that drop_outliers can be disabled with string 'false'."""
    yaml_content = (
        _base_yaml()
        + """
experiments:
  exp1:
    models: [m]
    dataset: ds
    target: y
    features: feat
    drop_outliers: "false"
"""
    )
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    exp = Experiment(cfg, "exp1")

    assert exp.spec.drop_outliers is None
    d = exp.to_dict()
    assert d["drop_outliers"] is None
