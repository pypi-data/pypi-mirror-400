"""Tests for CLI experiment tool."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from ml_workbench.cli_experiment import (
    _basic_stats_for_dataset,
    build_arg_parser,
    filter_sections,
    main,
    parse_kv_pairs,
)
from ml_workbench.config import YamlConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tests" / "data"
DATASETS_YAML = DATA_DIR / "datasets_cli.yaml"


def test_parse_kv_pairs_valid() -> None:
    """Test parsing valid key=value pairs."""
    result = parse_kv_pairs(["key1=value1", "key2=value2", "key3=value with spaces"])
    assert result == {"key1": "value1", "key2": "value2", "key3": "value with spaces"}


def test_parse_kv_pairs_with_equals_in_value() -> None:
    """Test parsing pairs where value contains equals sign."""
    result = parse_kv_pairs(["path=/home/user/file.txt", "url=https://example.com?key=value"])
    assert result == {"path": "/home/user/file.txt", "url": "https://example.com?key=value"}


def test_parse_kv_pairs_empty_list() -> None:
    """Test parsing empty list."""
    result = parse_kv_pairs([])
    assert result == {}


def test_parse_kv_pairs_invalid_format() -> None:
    """Test parsing invalid format raises error."""
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        parse_kv_pairs(["invalid_format"])


def test_parse_kv_pairs_no_equals() -> None:
    """Test parsing string without equals sign raises error."""
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        parse_kv_pairs(["noequals"])


def test_filter_sections_valid() -> None:
    """Test filtering sections that exist."""
    data = {
        "datasets": {"ds1": {}},
        "features": {"feat1": {}},
        "models": {"model1": {}},
    }
    result = filter_sections(data, ["datasets", "features"])
    assert result == {
        "datasets": {"ds1": {}},
        "features": {"feat1": {}},
    }
    assert "models" not in result


def test_filter_sections_missing_section(capsys) -> None:
    """Test filtering with missing section prints warning."""
    data = {"datasets": {"ds1": {}}}
    result = filter_sections(data, ["datasets", "nonexistent"])
    assert result == {"datasets": {"ds1": {}}}
    captured = capsys.readouterr()
    assert "Warning: Section 'nonexistent' not found" in captured.err


def test_filter_sections_empty() -> None:
    """Test filtering with empty data."""
    result = filter_sections({}, ["datasets"])
    assert result == {}


def test_basic_stats_for_dataset_success(tmp_path: Path) -> None:
    """Test getting stats for a valid dataset."""
    # Create a simple YAML config
    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  test_ds:
    description: "Test dataset"
    path: "{{base_dir}}test_data.csv"
    format: csv
    type: local
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Create test CSV
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("col1,col2\n1,2\n3,4\n", encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    result = _basic_stats_for_dataset("test_ds", cfg)

    assert result["name"] == "test_ds"
    assert result["description"] == "Test dataset"
    assert result["format"] == "csv"
    assert result["type"] == "local"
    assert result["num_columns"] == 2
    assert result["num_rows"] == 2
    assert "col1" in result["column_names"]
    assert "col2" in result["column_names"]


def test_basic_stats_for_dataset_error(tmp_path: Path) -> None:
    """Test getting stats for dataset that fails to read."""
    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  bad_ds:
    description: "Bad dataset"
    path: "{{base_dir}}nonexistent.csv"
    format: csv
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    result = _basic_stats_for_dataset("bad_ds", cfg)

    assert result["name"] == "bad_ds"
    assert "error" in result
    assert result["num_columns"] is None
    assert result["num_rows"] is None


def test_basic_stats_for_dataset_invalid_dataset(tmp_path: Path) -> None:
    """Test getting stats for non-existent dataset."""
    yaml_content = """
datasets:
  valid_ds: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    result = _basic_stats_for_dataset("nonexistent", cfg)

    assert result["name"] == "nonexistent"
    assert "error" in result
    assert "Failed to create dataset" in result["error"]


def test_build_arg_parser() -> None:
    """Test building argument parser."""
    parser = build_arg_parser()
    assert parser is not None
    assert parser.prog == "cli-experiment"


def test_main_show_config_yaml(tmp_path: Path, capsys) -> None:
    """Test main with --show-config output as YAML."""
    yaml_content = """
datasets:
  ds1:
    description: "Dataset 1"
    path: "/path/to/data.csv"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file), "--show-config"])
    assert exit_code == 0

    captured = capsys.readouterr()
    # Should output YAML
    assert "datasets" in captured.out
    assert "ds1" in captured.out


def test_main_show_config_json(tmp_path: Path, capsys) -> None:
    """Test main with --show-config --json."""
    yaml_content = """
datasets:
  ds1:
    description: "Dataset 1"
    path: "/path/to/data.csv"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file), "--show-config", "--json"])
    assert exit_code == 0

    captured = capsys.readouterr()
    # Should output JSON
    data = json.loads(captured.out)
    assert "datasets" in data
    assert "ds1" in data["datasets"]


def test_main_show_config_with_sections(tmp_path: Path, capsys) -> None:
    """Test main with --show-config --section."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    columns: [col1]
models:
  model1:
    type: builtins.object
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file), "--show-config", "--section", "datasets", "--section", "features"])
    assert exit_code == 0

    captured = capsys.readouterr()
    output = yaml.safe_load(captured.out)
    assert "datasets" in output
    assert "features" in output
    assert "models" not in output


def test_main_show_config_with_variables(tmp_path: Path, capsys) -> None:
    """Test main with --show-config --show-variables."""
    yaml_content = """
defaults:
  base_dir: "{base_dir}/"

datasets:
  ds1:
    path: "{base_dir}data.csv"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([
        str(yaml_file),
        "--show-config",
        "--show-variables",
        "--var", "base_dir=/custom/path"
    ])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "# Resolved Variables:" in captured.err
    assert "base_dir" in captured.err


def test_main_show_datasets(tmp_path: Path, capsys) -> None:
    """Test main with --show-datasets."""
    yaml_content = f"""
defaults:
  base_dir: {DATA_DIR}/

datasets:
  csv_one:
    description: "CSV one"
    path: "{{base_dir}}csv_small_1.csv"
    format: csv
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file), "--show-datasets"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "csv_one" in captured.out
    assert "format:" in captured.out


def test_main_show_datasets_json(tmp_path: Path, capsys) -> None:
    """Test main with --show-datasets --json."""
    yaml_content = f"""
defaults:
  base_dir: {DATA_DIR}/

datasets:
  csv_one:
    description: "CSV one"
    path: "{{base_dir}}csv_small_1.csv"
    format: csv
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file), "--show-datasets", "--json"])
    assert exit_code == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "datasets" in data
    assert len(data["datasets"]) > 0
    assert data["datasets"][0]["name"] == "csv_one"


def test_main_file_not_found(capsys) -> None:
    """Test main with non-existent YAML file."""
    exit_code = main(["nonexistent.yaml"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "YAML file not found" in captured.err


def test_main_no_experiments(tmp_path: Path, capsys) -> None:
    """Test main with YAML file containing no experiments."""
    yaml_content = """
datasets:
  ds1: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file)])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "No experiments found" in captured.err or "experiments" in captured.err.lower()


def test_main_invalid_experiment_name(tmp_path: Path, capsys) -> None:
    """Test main with invalid experiment name."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    columns: [col1]
models:
  model1:
    type: builtins.object
experiments:
  exp1:
    dataset: ds1
    target: target
    features: feat1
    models: model1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file), "--experiments", "nonexistent_exp"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Experiment(s) not found" in captured.err
    assert "nonexistent_exp" in captured.err


def test_main_with_variables(tmp_path: Path) -> None:
    """Test main with variable substitution."""
    yaml_content = """
defaults:
  base_dir: "{base_dir}/"

datasets:
  ds1:
    path: "{base_dir}data.csv"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Just test that it parses variables correctly
    exit_code = main([
        str(yaml_file),
        "--show-config",
        "--var", "base_dir=/custom/path"
    ])
    assert exit_code == 0


def test_main_config_validation_error(tmp_path: Path, capsys) -> None:
    """Test main with invalid configuration."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: nonexistent_dataset  # Invalid reference
    columns: [col1]
models:
  model1:
    type: builtins.object
experiments:
  exp1:
    dataset: ds1
    target: target
    features: feat1
    models: model1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    exit_code = main([str(yaml_file)])
    # Should fail during config validation
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Configuration validation failed" in captured.err or "Error" in captured.err


@patch("ml_workbench.cli_experiment.Runner")
@patch("ml_workbench.cli_experiment.Experiment")
def test_main_run_experiment_success(mock_experiment_class, mock_runner_class, tmp_path: Path, capsys) -> None:
    """Test main running an experiment successfully."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    columns: [col1]
models:
  model1:
    type: builtins.object
experiments:
  exp1:
    dataset: ds1
    target: target
    features: feat1
    models: model1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Mock experiment and runner
    mock_experiment = Mock()
    mock_experiment_class.return_value = mock_experiment

    mock_runner = Mock()
    mock_runner.run.return_value = {"model1": Mock()}
    mock_runner_class.return_value = mock_runner

    mock_experiment_class.list_experiment_names = Mock(return_value=["exp1"])
    mock_experiment_class.verify_config = Mock(return_value=None)

    exit_code = main([str(yaml_file), "--experiments", "exp1"])
    assert exit_code == 0

    mock_runner_class.assert_called_once()
    mock_runner.run.assert_called_once()


@patch("ml_workbench.cli_experiment.Runner")
@patch("ml_workbench.cli_experiment.Experiment")
def test_main_run_experiment_error(mock_experiment_class, mock_runner_class, tmp_path: Path, capsys) -> None:
    """Test main with experiment execution error."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    columns: [col1]
models:
  model1:
    type: builtins.object
experiments:
  exp1:
    dataset: ds1
    target: target
    features: feat1
    models: model1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Mock experiment and runner
    mock_experiment = Mock()
    mock_experiment_class.return_value = mock_experiment

    mock_runner = Mock()
    mock_runner.run.side_effect = Exception("Test error")
    mock_runner_class.return_value = mock_runner

    mock_experiment_class.list_experiment_names = Mock(return_value=["exp1"])
    mock_experiment_class.verify_config = Mock(return_value=None)

    exit_code = main([str(yaml_file), "--experiments", "exp1"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Error running experiment" in captured.err


def test_main_quiet_mode(tmp_path: Path) -> None:
    """Test main with --quiet flag."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    columns: [col1]
models:
  model1:
    type: builtins.object
experiments:
  exp1:
    dataset: ds1
    target: target
    features: feat1
    models: model1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with patch("ml_workbench.cli_experiment.Runner") as mock_runner_class, \
         patch("ml_workbench.cli_experiment.Experiment") as mock_experiment_class:
        mock_experiment = Mock()
        mock_experiment_class.return_value = mock_experiment

        mock_runner = Mock()
        mock_runner.run.return_value = {"model1": Mock()}
        mock_runner_class.return_value = mock_runner

        mock_experiment_class.list_experiment_names = Mock(return_value=["exp1"])
        mock_experiment_class.verify_config = Mock(return_value=None)

        exit_code = main([str(yaml_file), "--quiet", "--experiments", "exp1"])
        assert exit_code == 0

        # Verify runner was called with verbose=False
        mock_runner_class.assert_called_once()
        call_args = mock_runner_class.call_args
        assert call_args[1]["verbose"] is False


def test_main_multiple_experiments(tmp_path: Path) -> None:
    """Test main running multiple experiments."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    columns: [col1]
models:
  model1:
    type: builtins.object
experiments:
  exp1:
    dataset: ds1
    target: target
    features: feat1
    models: model1
  exp2:
    dataset: ds1
    target: target
    features: feat1
    models: model1
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with patch("ml_workbench.cli_experiment.Runner") as mock_runner_class, \
         patch("ml_workbench.cli_experiment.Experiment") as mock_experiment_class:
        mock_experiment = Mock()
        mock_experiment_class.return_value = mock_experiment

        mock_runner = Mock()
        mock_runner.run.return_value = {"model1": Mock()}
        mock_runner_class.return_value = mock_runner

        mock_experiment_class.list_experiment_names = Mock(return_value=["exp1", "exp2"])
        mock_experiment_class.verify_config = Mock(return_value=None)

        exit_code = main([str(yaml_file), "--experiments", "exp1", "--experiments", "exp2"])
        assert exit_code == 0

        # Should be called twice (once per experiment)
        assert mock_runner_class.call_count == 2

