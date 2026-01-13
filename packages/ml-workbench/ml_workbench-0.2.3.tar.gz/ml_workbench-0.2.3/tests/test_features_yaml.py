"""
Unit tests for loading features.yaml configuration.

Note: features.yaml uses '! include datasets.yaml' directive which is not
standard YAML and not supported by pyyaml. This test creates a simple
test YAML file without the include directive.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ml_workbench.config import YamlConfig
from ml_workbench.feature import Feature

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURES_YAML = PROJECT_ROOT / "tests" / "data" / "features.yaml"


def test_load_features_yaml_structure(tmp_path: Path) -> None:
    """Test loading a features YAML with the expected structure."""
    # Create a simple features YAML without include directive
    yaml_content = """
datasets:
  csv_one: {}
  csv_two: {}

features:
  feature_1:
    description: "Feature 1"
    dataset: csv_one
    columns: [value]
  feature_2:
    description: "Feature 2"
    dataset: csv_two
    columns: [score]
"""
    yaml_file = tmp_path / "features.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Verify the config loaded
    assert cfg is not None

    # Verify features section exists
    assert "features" in cfg._data
    features = cfg._data["features"]
    assert isinstance(features, dict)

    # Verify feature_1 exists and has expected structure
    assert "feature_1" in features
    feature_1 = features["feature_1"]
    assert feature_1["description"] == "Feature 1"
    assert feature_1["dataset"] == "csv_one"
    assert feature_1["columns"] == ["value"]

    # Verify feature_2 exists and has expected structure
    assert "feature_2" in features
    feature_2 = features["feature_2"]
    assert feature_2["description"] == "Feature 2"
    assert feature_2["dataset"] == "csv_two"
    assert feature_2["columns"] == ["score"]


def test_features_yaml_attribute_access(tmp_path: Path) -> None:
    """Test attribute-style access to features configuration."""
    yaml_content = """
datasets:
  csv_one: {}
  csv_two: {}

features:
  feature_1:
    description: "Feature 1"
    dataset: csv_one
    columns: [value]
  feature_2:
    description: "Feature 2"
    dataset: csv_two
    columns: [score]
"""
    yaml_file = tmp_path / "features.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    # Test attribute-style access to features
    assert hasattr(cfg, "features")
    features = cfg.features

    # Test accessing individual features
    assert hasattr(features, "feature_1")
    feature_1 = features.feature_1
    assert feature_1.description == "Feature 1"
    assert feature_1.dataset == "csv_one"
    assert feature_1.columns == ["value"]

    # Test dict-style access
    assert cfg["features"]["feature_2"]["dataset"] == "csv_two"


def test_features_yaml_with_variables(tmp_path: Path) -> None:
    """Test that features YAML works with variable substitution."""
    yaml_content = """
defaults:
  dataset_prefix: test_

datasets:
  prod_csv_one: {}

features:
  feature_1:
    description: "Feature 1"
    dataset: "{dataset_prefix}csv_one"
    columns: [value]
"""
    yaml_file = tmp_path / "features.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file, dataset_prefix="prod_")

    # Variables should be available
    assert "dataset_prefix" in cfg.variables
    assert cfg.variables["dataset_prefix"] == "prod_"

    # Features should still be accessible with interpolated values
    assert "features" in cfg._data
    assert "feature_1" in cfg._data["features"]
    assert cfg.features.feature_1.dataset == "prod_csv_one"


def test_features_yaml_file_exists() -> None:
    """Test that the features.yaml file exists in tests/data."""
    assert FEATURES_YAML.exists(), f"features.yaml not found at {FEATURES_YAML}"
    assert FEATURES_YAML.is_file()
    content = FEATURES_YAML.read_text(encoding="utf-8")
    assert len(content) > 0
    assert "features:" in content


def test_load_actual_features_yaml() -> None:
    """Test loading the features.yaml file with include directive from tests/data."""
    cfg = YamlConfig(FEATURES_YAML)

    # Verify features section exists
    assert "features" in cfg._data
    features = cfg._data["features"]
    assert isinstance(features, dict)

    # Verify features from features.yaml
    assert "feature_1" in features
    assert features["feature_1"]["dataset"] == "csv_one"
    assert features["feature_1"]["columns"] == ["value"]

    assert "feature_2" in features
    assert features["feature_2"]["dataset"] == "csv_two"
    assert features["feature_2"]["columns"] == ["score"]

    # Verify datasets section exists (from included datasets_cli.yaml)
    assert "datasets" in cfg._data
    datasets = cfg._data["datasets"]
    assert isinstance(datasets, dict)

    # Verify some datasets from datasets_cli.yaml are present
    assert "csv_one" in datasets
    assert "combined_dataset" in datasets
    assert "csv_user_id" in datasets


def test_include_directive_with_multiple_files(tmp_path: Path) -> None:
    """Test include directive with multiple files."""
    # Create base file
    base_yaml = tmp_path / "base.yaml"
    base_yaml.write_text(
        """
datasets:
  dataset1:
    path: /path/to/data1
""",
        encoding="utf-8",
    )

    # Create second file
    second_yaml = tmp_path / "second.yaml"
    second_yaml.write_text(
        """
datasets:
  dataset2:
    path: /path/to/data2
""",
        encoding="utf-8",
    )

    # Create main file that includes both
    main_yaml = tmp_path / "main.yaml"
    main_yaml.write_text(
        f"""
include:
  - {base_yaml}
  - {second_yaml}

datasets:
  dataset3:
    path: /path/to/data3
""",
        encoding="utf-8",
    )

    cfg = YamlConfig(main_yaml)

    # All three datasets should be present
    assert "dataset1" in cfg.datasets
    assert "dataset2" in cfg.datasets
    assert "dataset3" in cfg.datasets


def test_include_directive_override(tmp_path: Path) -> None:
    """Test that current file overrides included file."""
    # Create included file
    included_yaml = tmp_path / "included.yaml"
    included_yaml.write_text(
        """
datasets:
  dataset1:
    path: /original/path
    format: csv
""",
        encoding="utf-8",
    )

    # Create main file that overrides
    main_yaml = tmp_path / "main.yaml"
    main_yaml.write_text(
        f"""
include:
  - {included_yaml}

datasets:
  dataset1:
    path: /overridden/path
""",
        encoding="utf-8",
    )

    cfg = YamlConfig(main_yaml)

    # Main file should override the path but keep format
    assert cfg.datasets.dataset1.path == "/overridden/path"
    assert cfg.datasets.dataset1.format == "csv"


def test_include_directive_circular_detection(tmp_path: Path) -> None:
    """Test that circular includes are detected."""
    # Create file A that includes B
    file_a = tmp_path / "a.yaml"
    file_a.write_text(
        f"""
include:
  - {tmp_path / "b.yaml"}

data:
  value: a
""",
        encoding="utf-8",
    )

    # Create file B that includes A (circular)
    file_b = tmp_path / "b.yaml"
    file_b.write_text(
        f"""
include:
  - {file_a}

data:
  value: b
""",
        encoding="utf-8",
    )

    # Should raise ValueError for circular include
    with pytest.raises(ValueError, match="Circular include detected"):
        YamlConfig(file_a)


def test_include_directive_missing_file(tmp_path: Path) -> None:
    """Test that missing included file raises error."""
    main_yaml = tmp_path / "main.yaml"
    main_yaml.write_text(
        """
include:
  - /nonexistent/file.yaml

data:
  value: test
""",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="Included file not found"):
        YamlConfig(main_yaml)


def test_include_directive_not_a_list(tmp_path: Path) -> None:
    """Test that include directive must be a list."""
    main_yaml = tmp_path / "main.yaml"
    main_yaml.write_text(
        """
include: single_file.yaml

data:
  value: test
""",
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="'include' directive must be a list"):
        YamlConfig(main_yaml)


def test_feature_get_series_with_index(tmp_path: Path) -> None:
    """Test Feature.get_series with index parameter."""
    import pandas as pd

    # Create CSV file
    csv_data = pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10, 20, 30],
    })
    csv_path = tmp_path / "data.csv"
    csv_data.to_csv(csv_path, index=False)

    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  ds1:
    path: "{{base_dir}}data.csv"
    format: csv
features:
  feat1:
    dataset: ds1
    numerical: [value]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    feature = Feature("feat1", cfg)
    series = feature.get_series("value", index="id")

    assert series is not None
    assert series.name == "feat1.value"
    assert len(series) == 3


def test_feature_get_series_column_not_declared(tmp_path: Path) -> None:
    """Test Feature.get_series with column not in feature spec."""
    import pandas as pd

    csv_path = tmp_path / "data.csv"
    pd.DataFrame({"col1": [1, 2]}).to_csv(csv_path, index=False)

    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  ds1:
    path: "{{base_dir}}data.csv"
    format: csv
features:
  feat1:
    dataset: ds1
    numerical: [col1]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    feature = Feature("feat1", cfg)
    with pytest.raises(KeyError, match="is not declared in feature set"):
        feature.get_series("undeclared_col")


def test_feature_to_dict(tmp_path: Path) -> None:
    """Test Feature.to_dict method."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    description: "Test feature"
    dataset: ds1
    numerical: [col1, col2]
    categorical: [cat1]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    feature = Feature("feat1", cfg)
    result = feature.to_dict()

    assert result["name"] == "feat1"
    assert result["dataset"] == "ds1"
    assert result["description"] == "Test feature"
    assert result["numerical"] == ["col1", "col2"]
    assert result["categorical"] == ["cat1"]


def test_feature_get_columns_by_type(tmp_path: Path) -> None:
    """Test Feature.get_columns_by_type method."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    numerical: [num1, num2]
    categorical: [cat1]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    feature = Feature("feat1", cfg)
    result = feature.get_columns_by_type()

    assert result["numerical"] == ["num1", "num2"]
    assert result["categorical"] == ["cat1"]


def test_feature_list_feature_names(tmp_path: Path) -> None:
    """Test Feature.list_feature_names class method."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    numerical: [col1]
  feat2:
    dataset: ds1
    categorical: [col2]
  feat3:
    dataset: ds1
    columns: [col3]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    names = Feature.list_feature_names(cfg)
    assert set(names) == {"feat1", "feat2", "feat3"}


def test_feature_load_all(tmp_path: Path) -> None:
    """Test Feature.load_all class method."""
    yaml_content = """
datasets:
  ds1: {}
features:
  feat1:
    dataset: ds1
    numerical: [col1]
  feat2:
    dataset: ds1
    categorical: [col2]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    features = Feature.load_all(cfg)
    assert len(features) == 2
    assert "feat1" in features
    assert "feat2" in features
    assert isinstance(features["feat1"], Feature)
    assert isinstance(features["feat2"], Feature)


def test_feature_to_dataframe(tmp_path: Path) -> None:
    """Test Feature.to_dataframe class method."""
    import pandas as pd

    # Create CSV files
    csv1 = tmp_path / "data1.csv"
    pd.DataFrame({"id": [1, 2], "value": [10, 20]}).to_csv(csv1, index=False)

    csv2 = tmp_path / "data2.csv"
    pd.DataFrame({"id": [1, 2], "score": [100, 200]}).to_csv(csv2, index=False)

    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  ds1:
    path: "{{base_dir}}data1.csv"
    format: csv
  ds2:
    path: "{{base_dir}}data2.csv"
    format: csv
features:
  feat1:
    dataset: ds1
    numerical: [value]
  feat2:
    dataset: ds2
    numerical: [score]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    df = Feature.to_dataframe(cfg, feature_sets=["feat1", "feat2"], index="id")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "feat1.value" in df.columns
    assert "feat2.score" in df.columns


def test_feature_to_dataframe_with_type_filter(tmp_path: Path) -> None:
    """Test Feature.to_dataframe with include_types filter."""
    import pandas as pd

    csv_path = tmp_path / "data.csv"
    pd.DataFrame({
        "id": [1, 2],
        "num_col": [10, 20],
        "cat_col": ["A", "B"],
    }).to_csv(csv_path, index=False)

    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  ds1:
    path: "{{base_dir}}data.csv"
    format: csv
features:
  feat1:
    dataset: ds1
    numerical: [num_col]
    categorical: [cat_col]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    df = Feature.to_dataframe(cfg, include_types=["numerical"])
    assert "feat1.num_col" in df.columns
    assert "feat1.cat_col" not in df.columns


def test_feature_to_dataframe_empty_result(tmp_path: Path) -> None:
    """Test Feature.to_dataframe with empty feature sets."""
    import pandas as pd

    csv_path = tmp_path / "data.csv"
    pd.DataFrame({"col1": [1, 2]}).to_csv(csv_path, index=False)

    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  ds1:
    path: "{{base_dir}}data.csv"
    format: csv
features:
  feat1:
    dataset: ds1
    numerical: [col1]
    categorical: []
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    # Test with include_types that excludes all columns
    df = Feature.to_dataframe(cfg, include_types=["categorical"])
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == 0


def test_feature_get_series_column_not_in_dataset(tmp_path: Path) -> None:
    """Test Feature.get_series with column not in dataset."""
    import pandas as pd

    csv_path = tmp_path / "data.csv"
    pd.DataFrame({"col1": [1, 2]}).to_csv(csv_path, index=False)

    yaml_content = f"""
defaults:
  base_dir: {tmp_path}/

datasets:
  ds1:
    path: "{{base_dir}}data.csv"
    format: csv
features:
  feat1:
    dataset: ds1
    numerical: [col1, missing_col]
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    feature = Feature("feat1", cfg)
    with pytest.raises(KeyError, match="not found in dataset"):
        feature.get_series("missing_col")


def test_feature_list_feature_names_no_features_section(tmp_path: Path) -> None:
    """Test Feature.list_feature_names with no features section."""
    yaml_content = """
datasets:
  ds1: {}
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    with pytest.raises(KeyError, match="No 'features' section found"):
        Feature.list_feature_names(cfg)
