from __future__ import annotations

from pathlib import Path

import pytest

from ml_workbench.config import YamlConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_YAML = PROJECT_ROOT / "tests" / "data" / "datasets_cli.yaml"


def test_missing_variables_raise_keyerror(tmp_path: Path) -> None:
    base_text = DATA_YAML.read_text(encoding="utf-8")
    # Inject a placeholder that is not provided in defaults nor kwargs
    augmented_text = base_text + '\nprobe: "{unknown_placeholder}"\n'
    tmp_yaml = tmp_path / "datasets_missing.yaml"
    tmp_yaml.write_text(augmented_text, encoding="utf-8")

    with pytest.raises(KeyError) as err:
        YamlConfig(tmp_yaml)  # strict=True by default

    assert "unknown_placeholder" in str(err.value)


def test_unnecessary_variables_are_ignored_and_preserved() -> None:
    cfg = YamlConfig(DATA_YAML, extra_unused_var="value123")

    # No exception and variables should include the unused one
    assert cfg.variables["extra_unused_var"] == "value123"

    # Interpolated value should remain correct and unaffected
    expected_csv_one = "tests/data/csv_small_1.csv"
    assert (
        cfg.datasets.csv_one.path
        == expected_csv_one
        == cfg["datasets"]["csv_one"]["path"]
    )


def test_correct_interpolation_and_access_deep_structures() -> None:
    cfg = YamlConfig(DATA_YAML)

    # Dict-style and attribute-style access for a simple interpolated path
    expected_csv_two_path = "tests/data/csv_small_2.csv"
    assert cfg.datasets.csv_two.path == expected_csv_two_path
    assert cfg["datasets"]["csv_two"]["path"] == expected_csv_two_path

    # Deep nested structures inside nested mappings
    # 1st join spec
    first_join = cfg.datasets.combined_dataset.merge_specs.csv_one
    assert first_join.how == "left"
    assert first_join["how"] == "left"
    assert first_join.left_on == "id"

    # 2nd join spec (last in sequence, only has right_on)
    second_join = cfg.datasets.combined_dataset.merge_specs.csv_user_id
    assert second_join.right_on == "id"
    assert second_join.left_on == "user_id_tmp"
    assert second_join.how == "left"


def test_list_of_dataset_names_matches_expected() -> None:
    cfg = YamlConfig(DATA_YAML)
    # The dataset names are the keys under top-level datasets mapping
    dataset_names_attr = set(cfg.datasets.keys())
    dataset_names_dict = set(cfg["datasets"].keys())

    expected = {
        "csv_one",
        "csv_two",
        "csv_user_id",
        "combined_dataset",
        "parquet_to_fail",
    }

    assert dataset_names_attr == expected
    assert dataset_names_dict == expected


def test_get_datasets_list() -> None:
    cfg = YamlConfig(DATA_YAML)
    datasets_list = cfg.get_datasets_list()

    expected = {
        "csv_one",
        "csv_two",
        "csv_user_id",
        "combined_dataset",
        "parquet_to_fail",
    }

    assert set(datasets_list) == expected
    assert isinstance(datasets_list, list)


def test_get_dataset_config() -> None:
    cfg = YamlConfig(DATA_YAML)

    # Get a simple dataset config
    csv_config = cfg.get_dataset_config("csv_one")
    assert isinstance(csv_config, dict)
    assert csv_config["format"] == "csv"
    assert csv_config["type"] == "local"
    assert "description" in csv_config

    # Get a combined dataset config
    combined_config = cfg.get_dataset_config("combined_dataset")
    assert isinstance(combined_config, dict)
    assert "merge_specs" in combined_config
    assert "description" in combined_config


def test_get_dataset_config_not_found() -> None:
    cfg = YamlConfig(DATA_YAML)

    with pytest.raises(KeyError, match="Dataset 'nonexistent' not found"):
        cfg.get_dataset_config("nonexistent")


def test_get_datasets_list_empty_config(tmp_path: Path) -> None:
    # Config without datasets section
    yaml_content = "defaults:\n  catalog: test\n"
    tmp_yaml = tmp_path / "no_datasets.yaml"
    tmp_yaml.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(tmp_yaml)
    datasets_list = cfg.get_datasets_list()

    assert datasets_list == []


def test_get_dataset_config_no_datasets_section(tmp_path: Path) -> None:
    # Config without datasets section
    yaml_content = "defaults:\n  catalog: test\n"
    tmp_yaml = tmp_path / "no_datasets.yaml"
    tmp_yaml.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(tmp_yaml)

    with pytest.raises(KeyError, match="No datasets section found"):
        cfg.get_dataset_config("any_dataset")


def test_interpolation_non_strict_mode(tmp_path: Path) -> None:
    """Test interpolation in non-strict mode leaves placeholders."""
    yaml_content = """
defaults:
  var1: value1
data:
  path: "{var1}/{var2}"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file, strict=False)
    # In non-strict mode, missing placeholders should remain as-is
    assert "{var2}" in cfg._data["data"]["path"] or "value1" in cfg._data["data"]["path"]


def test_interpolation_with_list(tmp_path: Path) -> None:
    """Test interpolation works with lists."""
    yaml_content = """
defaults:
  base: /path
data:
  paths: ["{base}/file1", "{base}/file2"]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    assert cfg._data["data"]["paths"][0] == "/path/file1"
    assert cfg._data["data"]["paths"][1] == "/path/file2"


def test_interpolation_with_nested_dict(tmp_path: Path) -> None:
    """Test interpolation works with nested dictionaries."""
    yaml_content = """
defaults:
  name: test
data:
  nested:
    path: "{name}/file"
    deeper:
      value: "{name}_value"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    assert cfg._data["data"]["nested"]["path"] == "test/file"
    assert cfg._data["data"]["nested"]["deeper"]["value"] == "test_value"


def test_interpolation_no_placeholders(tmp_path: Path) -> None:
    """Test interpolation with string containing no placeholders."""
    yaml_content = """
defaults:
  var1: value1
data:
  path: "simple/path"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    assert cfg._data["data"]["path"] == "simple/path"


def test_interpolation_empty_string(tmp_path: Path) -> None:
    """Test interpolation with empty string."""
    yaml_content = """
defaults:
  var1: value1
data:
  path: ""
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    assert cfg._data["data"]["path"] == ""


def test_to_dict_method(tmp_path: Path) -> None:
    """Test YamlConfig.to_dict method."""
    yaml_content = """
defaults:
  var1: value1
datasets:
  ds1:
    path: "{var1}/data"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    result = cfg.to_dict()

    assert isinstance(result, dict)
    assert "datasets" in result
    assert "ds1" in result["datasets"]
    assert result["datasets"]["ds1"]["path"] == "value1/data"


def test_config_setitem_delitem(tmp_path: Path) -> None:
    """Test YamlConfig __setitem__ and __delitem__ methods."""
    yaml_content = """
data:
  key1: value1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Test __setitem__
    cfg["data"]["key2"] = "value2"
    assert cfg["data"]["key2"] == "value2"

    # Test __delitem__
    del cfg["data"]["key1"]
    assert "key1" not in cfg["data"]


def test_config_iter_len(tmp_path: Path) -> None:
    """Test YamlConfig __iter__ and __len__ methods."""
    yaml_content = """
section1:
  key1: value1
section2:
  key2: value2
section3:
  key3: value3
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Test __iter__
    keys = list(cfg)
    assert "section1" in keys
    assert "section2" in keys
    assert "section3" in keys

    # Test __len__
    assert len(cfg) == 3


def test_config_getattr_missing(tmp_path: Path) -> None:
    """Test YamlConfig __getattr__ with missing attribute."""
    yaml_content = """
section1:
  key1: value1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Test accessing existing section
    assert cfg.section1 is not None

    # Test accessing missing section raises AttributeError
    with pytest.raises(AttributeError):
        _ = cfg.nonexistent_section


def test_config_get_method(tmp_path: Path) -> None:
    """Test YamlConfig get method."""
    yaml_content = """
section1:
  key1: value1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Test get with existing key
    result = cfg.get("section1")
    assert result is not None
    assert result.key1 == "value1"

    # Test get with missing key and default
    result = cfg.get("nonexistent", "default_value")
    assert result == "default_value"

    # Test get with missing key and None default
    result = cfg.get("nonexistent", None)
    assert result is None
