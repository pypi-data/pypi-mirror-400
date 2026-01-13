"""Tests for MlflowConf class."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from ml_workbench.config import YamlConfig
from ml_workbench.mlflow_conf import MlflowConf

if TYPE_CHECKING:
    from pathlib import Path


def test_mlflow_conf_defaults(tmp_path: Path) -> None:
    """Test MlflowConf uses defaults when mlflow section is missing."""
    yaml_content = """
datasets:
  ds: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    mlflow_conf = MlflowConf(cfg)

    assert mlflow_conf.is_enabled() is True
    assert mlflow_conf.get_type() == "local"  # Default when MLFLOW_TRACKING_URI not set
    assert mlflow_conf.get_tags() == {}
    assert mlflow_conf.get_name("test_exp") == "test_exp"


def test_mlflow_conf_with_all_fields(tmp_path: Path) -> None:
    """Test MlflowConf with all fields specified."""
    yaml_content = """
mlflow:
  enabled: false
  type: databricks
  experiment_name_prefix: "/Shared/"
  tags:
    environment: "production"
    data_version: "v2"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    mlflow_conf = MlflowConf(cfg)

    assert mlflow_conf.is_enabled() is False
    assert mlflow_conf.get_type() == "databricks"
    assert mlflow_conf.get_tags() == {"environment": "production", "data_version": "v2"}
    assert mlflow_conf.get_name("test_exp") == "/Shared/test_exp"


def test_mlflow_conf_type_inference_databricks(tmp_path: Path) -> None:
    """Test MlflowConf infers type from MLFLOW_TRACKING_URI."""
    yaml_content = """
mlflow:
  enabled: true
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    with patch.dict(os.environ, {"MLFLOW_TRACKING_URI": "databricks://workspace"}):
        mlflow_conf = MlflowConf(cfg)
        assert mlflow_conf.get_type() == "databricks"


def test_mlflow_conf_type_inference_local(tmp_path: Path) -> None:
    """Test MlflowConf infers local type when MLFLOW_TRACKING_URI doesn't start with databricks."""
    yaml_content = """
mlflow:
  enabled: true
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    with patch.dict(os.environ, {"MLFLOW_TRACKING_URI": "sqlite:///mlflow.db"}, clear=False):
        mlflow_conf = MlflowConf(cfg)
        assert mlflow_conf.get_type() == "local"


def test_mlflow_conf_get_name_with_prefix(tmp_path: Path) -> None:
    """Test get_name combines prefix and experiment name correctly."""
    yaml_content = """
mlflow:
  experiment_name_prefix: "/Shared/"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    mlflow_conf = MlflowConf(cfg)

    assert mlflow_conf.get_name("test_exp") == "/Shared/test_exp"
    assert mlflow_conf.get_name("/test_exp") == "/Shared/test_exp"  # Removes leading /


def test_mlflow_conf_get_name_prefix_without_slash(tmp_path: Path) -> None:
    """Test get_name adds slash if prefix doesn't end with one."""
    yaml_content = """
mlflow:
  experiment_name_prefix: "/Shared"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    mlflow_conf = MlflowConf(cfg)

    assert mlflow_conf.get_name("test_exp") == "/Shared/test_exp"


def test_mlflow_conf_to_dict(tmp_path: Path) -> None:
    """Test to_dict returns correct dictionary representation."""
    yaml_content = """
mlflow:
  enabled: true
  type: local
  experiment_name_prefix: "/Test/"
  tags:
    env: "test"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    mlflow_conf = MlflowConf(cfg)

    result = mlflow_conf.to_dict()
    assert result == {
        "enabled": True,
        "type": "local",
        "experiment_name_prefix": "/Test/",
        "tags": {"env": "test"},
    }


def test_mlflow_conf_enabled_not_boolean(tmp_path: Path) -> None:
    """Test MlflowConf raises TypeError when enabled is not boolean."""
    yaml_content = """
mlflow:
  enabled: "true"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.enabled must be a boolean"):
        YamlConfig(yaml_file)


def test_mlflow_conf_type_not_string(tmp_path: Path) -> None:
    """Test MlflowConf raises TypeError when type is not string."""
    yaml_content = """
mlflow:
  type: 123
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.type must be a string"):
        YamlConfig(yaml_file)


def test_mlflow_conf_type_invalid_value(tmp_path: Path) -> None:
    """Test MlflowConf raises ValueError when type is invalid."""
    yaml_content = """
mlflow:
  type: "invalid"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="mlflow.type must be 'local' or 'databricks'"):
        YamlConfig(yaml_file)


def test_mlflow_conf_type_case_insensitive(tmp_path: Path) -> None:
    """Test MlflowConf accepts case-insensitive type values."""
    yaml_content = """
mlflow:
  type: "DATABRICKS"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    mlflow_conf = MlflowConf(cfg)

    assert mlflow_conf.get_type() == "databricks"


def test_mlflow_conf_prefix_not_string(tmp_path: Path) -> None:
    """Test MlflowConf raises TypeError when prefix is not string."""
    yaml_content = """
mlflow:
  experiment_name_prefix: 123
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.experiment_name_prefix must be a string"):
        YamlConfig(yaml_file)


def test_mlflow_conf_tags_not_mapping(tmp_path: Path) -> None:
    """Test MlflowConf raises TypeError when tags is not a mapping."""
    yaml_content = """
mlflow:
  tags: ["tag1", "tag2"]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.tags must be a mapping"):
        YamlConfig(yaml_file)


def test_mlflow_conf_section_not_mapping(tmp_path: Path) -> None:
    """Test MlflowConf raises TypeError when mlflow section is not a mapping."""
    yaml_content = """
mlflow: "not a dict"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="'mlflow' section must be a mapping"):
        YamlConfig(yaml_file)


def test_mlflow_conf_verify_config_no_section(tmp_path: Path) -> None:
    """Test verify_config passes when mlflow section is missing."""
    yaml_content = """
datasets:
  ds: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    # Should not raise
    MlflowConf.verify_config(cfg)


def test_mlflow_conf_verify_config_invalid_enabled(tmp_path: Path) -> None:
    """Test verify_config raises TypeError for invalid enabled."""
    yaml_content = """
mlflow:
  enabled: "true"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.enabled must be a boolean"):
        YamlConfig(yaml_file)


def test_mlflow_conf_verify_config_invalid_type_string(tmp_path: Path) -> None:
    """Test verify_config raises TypeError for non-string type."""
    yaml_content = """
mlflow:
  type: 123
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.type must be a string"):
        YamlConfig(yaml_file)


def test_mlflow_conf_verify_config_invalid_type_value(tmp_path: Path) -> None:
    """Test verify_config raises ValueError for invalid type value."""
    yaml_content = """
mlflow:
  type: "invalid"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(ValueError, match="mlflow.type must be 'local' or 'databricks'"):
        YamlConfig(yaml_file)


def test_mlflow_conf_verify_config_invalid_prefix(tmp_path: Path) -> None:
    """Test verify_config raises TypeError for invalid prefix."""
    yaml_content = """
mlflow:
  experiment_name_prefix: 123
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.experiment_name_prefix must be a string"):
        YamlConfig(yaml_file)


def test_mlflow_conf_verify_config_invalid_tags(tmp_path: Path) -> None:
    """Test verify_config raises TypeError for invalid tags."""
    yaml_content = """
mlflow:
  tags: ["not", "a", "dict"]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="mlflow.tags must be a mapping"):
        YamlConfig(yaml_file)


def test_mlflow_conf_verify_config_section_not_mapping(tmp_path: Path) -> None:
    """Test verify_config raises TypeError when mlflow section is not a mapping."""
    yaml_content = """
mlflow: "not a dict"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="'mlflow' section must be a mapping"):
        YamlConfig(yaml_file)


def test_mlflow_conf_get_mlflow_section_none(tmp_path: Path) -> None:
    """Test _get_mlflow_section returns empty dict when mlflow section is None."""
    yaml_content = """
datasets:
  ds: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    result = MlflowConf._get_mlflow_section(cfg)
    assert result == {}


def test_mlflow_conf_get_mlflow_section_mapping(tmp_path: Path) -> None:
    """Test _get_mlflow_section returns mlflow section when present."""
    yaml_content = """
mlflow:
  enabled: true
datasets:
  ds: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    result = MlflowConf._get_mlflow_section(cfg)
    assert result == {"enabled": True}


def test_mlflow_conf_get_mlflow_section_not_mapping(tmp_path: Path) -> None:
    """Test _get_mlflow_section raises TypeError when mlflow is not a mapping."""
    yaml_content = """
mlflow: "not a dict"
datasets:
  ds: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(TypeError, match="'mlflow' section must be a mapping"):
        YamlConfig(yaml_file)

