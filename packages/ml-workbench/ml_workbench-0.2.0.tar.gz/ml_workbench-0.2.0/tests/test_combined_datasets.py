"""
Unit tests for combined datasets functionality.

Tests both local file-based combined datasets and Databricks combined datasets.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ml_workbench.config import YamlConfig
from ml_workbench.dataset import Dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_COMBINED_YAML = PROJECT_ROOT / "tests" / "data" / "datasets_combined.yaml"


# ============================================================================
# Local Combined Datasets Tests
# ============================================================================


def test_local_combined_dataset_basic() -> None:
    """Test basic local combined dataset functionality."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    ds = Dataset("local_combined_dataset", cfg)

    # Verify it's recognized as combined
    assert ds.is_combined is True
    assert ds.path is None  # Combined datasets don't have a path

    # Read the combined dataset
    df = ds.read_pandas()

    # Verify the result
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

    # Should have columns from all three datasets
    assert "id" in df.columns
    assert "value" in df.columns  # from csv_one
    assert "user_id" in df.columns  # from csv_user_id
    assert "score" in df.columns  # from csv_two
    assert "flag" in df.columns  # from csv_two


def test_local_combined_dataset_merge_logic() -> None:
    """Test that local combined dataset merges correctly."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    ds = Dataset("local_combined_dataset", cfg)
    df = ds.read_pandas()

    # csv_one has 3 rows (id: 1, 2, 3)
    # csv_user_id has 10 rows (id: 1-10, user_id: u1-u10)
    # csv_two has 2 rows (user_id: u1, u2)
    # With left joins, we should have 3 rows (from csv_one)
    assert len(df) == 3

    # Check that the first row has data from all sources
    first_row = df[df["id"] == 1].iloc[0]
    assert first_row["value"] == 10  # from csv_one
    assert first_row["user_id"] == "u1"  # from csv_user_id
    assert first_row["score"] == 0.5  # from csv_two
    # flag is read as boolean True, not string "true"
    assert first_row["flag"] is True  # from csv_two

    # Check that row with id=3 has user_id_tmp but no user_id and score/flag (left join)
    third_row = df[df["id"] == 3].iloc[0]
    assert third_row["value"] == 30
    assert third_row["user_id_tmp"] == "u3"
    assert pd.isna(third_row["user_id"])
    assert pd.isna(third_row["score"])  # No match in csv_two
    assert pd.isna(third_row["flag"])  # No match in csv_two


def test_local_combined_dataset_statistics() -> None:
    """Test statistics methods on local combined datasets."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    ds = Dataset("local_combined_dataset", cfg)

    # Test get_statistics
    stats = ds.get_statistics()
    assert stats["num_rows"] == 3
    assert stats["num_columns"] == 6  # id, value, user_id_tmp, user_id, score, flag
    assert len(stats["column_names"]) == 6
    assert "id" in stats["column_names"]
    assert "value" in stats["column_names"]
    assert "user_id_tmp" in stats["column_names"]
    assert "user_id" in stats["column_names"]
    assert "score" in stats["column_names"]
    assert "flag" in stats["column_names"]

    # Test get_columns
    columns = ds.get_columns()
    assert len(columns) == 6
    assert "id" in columns

    # Test get_rows
    rows = ds.get_rows()
    assert rows == 3

    # Test get_head
    head = ds.get_head(2)
    assert isinstance(head, pd.DataFrame)
    assert len(head) == 2


def test_local_combined_dataset_caching() -> None:
    """Test that local combined dataset results are cached."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    ds = Dataset("local_combined_dataset", cfg)

    # First read
    df1 = ds.read_pandas()

    # Second read should return the same object (cached)
    df2 = ds.read_pandas()

    assert df1 is df2


def test_local_combined_dataset_individual_components() -> None:
    """Test that individual datasets in the merge can be read separately."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    # Read individual datasets
    csv_one = Dataset("csv_one", cfg)
    df_one = csv_one.read_pandas()
    assert len(df_one) == 3
    assert list(df_one.columns) == ["id", "value"]

    csv_user_id = Dataset("csv_user_id", cfg)
    df_user_id = csv_user_id.read_pandas()
    assert len(df_user_id) == 10
    assert list(df_user_id.columns) == ["id", "user_id_tmp"]

    csv_two = Dataset("csv_two", cfg)
    df_two = csv_two.read_pandas()
    assert len(df_two) == 2
    assert list(df_two.columns) == ["user_id", "score", "flag"]


# ============================================================================
# Databricks Combined Datasets Tests
# ============================================================================


@patch("pyspark.sql.SparkSession")
def test_databricks_combined_dataset_left_join(mock_spark_class: MagicMock) -> None:
    """Test Databricks combined dataset with left join."""
    # Create mock Spark session and DataFrames
    mock_spark = MagicMock()
    mock_spark_class.builder.getOrCreate.return_value = mock_spark

    # Mock data for test_users (3 rows)
    users_data = pd.DataFrame({
        "participant_uuid": ["uuid1", "uuid2", "uuid3"],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
    })

    # Mock data for test_users_metadata (2 rows, missing uuid3)
    metadata_data = pd.DataFrame({
        "participant_uuid": ["uuid1", "uuid2"],
        "height": [165, 180],
        "weight": [60, 75],
    })

    # Mock Spark DataFrame
    mock_users_df = MagicMock()
    mock_users_df.toPandas.return_value = users_data

    mock_metadata_df = MagicMock()
    mock_metadata_df.toPandas.return_value = metadata_data

    # Configure mock to return appropriate DataFrames
    def mock_table(table_name: str) -> MagicMock:
        if "users" in table_name and "metadata" not in table_name:
            return mock_users_df
        if "metadata" in table_name:
            return mock_metadata_df
        raise ValueError(f"Unknown table: {table_name}")

    mock_spark.table.side_effect = mock_table

    # Test the combined dataset
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")
    ds = Dataset("databricks_combined_left_join", cfg)

    assert ds.is_combined is True
    # Note: Combined datasets don't have their own type, it's determined by component datasets

    df = ds.read_pandas()

    # Verify the result
    assert isinstance(df, pd.DataFrame)
    # Left join should preserve all 3 rows from test_users
    assert len(df) == 3

    # Should have columns from both datasets
    assert "participant_uuid" in df.columns
    assert "name" in df.columns
    assert "age" in df.columns
    assert "height" in df.columns
    assert "weight" in df.columns

    # Check that uuid3 has NaN for metadata columns (left join)
    uuid3_row = df[df["participant_uuid"] == "uuid3"].iloc[0]
    assert uuid3_row["name"] == "Charlie"
    assert pd.isna(uuid3_row["height"])
    assert pd.isna(uuid3_row["weight"])


@patch("pyspark.sql.SparkSession")
def test_databricks_combined_dataset_inner_join(mock_spark_class: MagicMock) -> None:
    """Test Databricks combined dataset with inner join."""
    # Create mock Spark session and DataFrames
    mock_spark = MagicMock()
    mock_spark_class.builder.getOrCreate.return_value = mock_spark

    # Mock data for test_users (3 rows)
    users_data = pd.DataFrame({
        "participant_uuid": ["uuid1", "uuid2", "uuid3"],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
    })

    # Mock data for test_users_metadata (2 rows, missing uuid3)
    metadata_data = pd.DataFrame({
        "participant_uuid": ["uuid1", "uuid2"],
        "height": [165, 180],
        "weight": [60, 75],
    })

    # Mock Spark DataFrame
    mock_users_df = MagicMock()
    mock_users_df.toPandas.return_value = users_data

    mock_metadata_df = MagicMock()
    mock_metadata_df.toPandas.return_value = metadata_data

    # Configure mock to return appropriate DataFrames
    def mock_table(table_name: str) -> MagicMock:
        if "users" in table_name and "metadata" not in table_name:
            return mock_users_df
        if "metadata" in table_name:
            return mock_metadata_df
        raise ValueError(f"Unknown table: {table_name}")

    mock_spark.table.side_effect = mock_table

    # Test the combined dataset
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")
    ds = Dataset("databricks_combined_inner_join", cfg)

    assert ds.is_combined is True
    # Note: Combined datasets don't have their own type, it's determined by component datasets

    df = ds.read_pandas()

    # Verify the result
    assert isinstance(df, pd.DataFrame)
    # Inner join should only have 2 rows (matching records)
    assert len(df) == 2

    # Should have columns from both datasets
    assert "participant_uuid" in df.columns
    assert "name" in df.columns
    assert "age" in df.columns
    assert "height" in df.columns
    assert "weight" in df.columns

    # All rows should have complete data (no NaN)
    assert not df["height"].isna().any()
    assert not df["weight"].isna().any()

    # uuid3 should not be in the result
    assert "uuid3" not in df["participant_uuid"].values


@patch("pyspark.sql.SparkSession")
def test_databricks_combined_dataset_statistics(mock_spark_class: MagicMock) -> None:
    """Test statistics methods on Databricks combined datasets."""
    # Create mock Spark session and DataFrames
    mock_spark = MagicMock()
    mock_spark_class.builder.getOrCreate.return_value = mock_spark

    # Mock data
    users_data = pd.DataFrame({
        "participant_uuid": ["uuid1", "uuid2"],
        "name": ["Alice", "Bob"],
    })

    metadata_data = pd.DataFrame({
        "participant_uuid": ["uuid1", "uuid2"],
        "height": [165, 180],
    })

    mock_users_df = MagicMock()
    mock_users_df.toPandas.return_value = users_data

    mock_metadata_df = MagicMock()
    mock_metadata_df.toPandas.return_value = metadata_data

    def mock_table(table_name: str) -> MagicMock:
        if "users" in table_name and "metadata" not in table_name:
            return mock_users_df
        if "metadata" in table_name:
            return mock_metadata_df
        raise ValueError(f"Unknown table: {table_name}")

    mock_spark.table.side_effect = mock_table

    # Test the combined dataset
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")
    ds = Dataset("databricks_combined_inner_join", cfg)

    # Test get_statistics
    stats = ds.get_statistics()
    assert stats["num_rows"] == 2
    assert stats["num_columns"] == 3  # participant_uuid, name, height
    assert len(stats["column_names"]) == 3

    # Test get_columns
    columns = ds.get_columns()
    assert len(columns) == 3
    assert "participant_uuid" in columns
    assert "name" in columns
    assert "height" in columns

    # Test get_rows
    rows = ds.get_rows()
    assert rows == 2


@patch("pyspark.sql.SparkSession")
def test_databricks_combined_dataset_caching(mock_spark_class: MagicMock) -> None:
    """Test that Databricks combined dataset results are cached."""
    # Create mock Spark session and DataFrames
    mock_spark = MagicMock()
    mock_spark_class.builder.getOrCreate.return_value = mock_spark

    users_data = pd.DataFrame({"participant_uuid": ["uuid1"], "name": ["Alice"]})

    metadata_data = pd.DataFrame({"participant_uuid": ["uuid1"], "height": [165]})

    mock_users_df = MagicMock()
    mock_users_df.toPandas.return_value = users_data

    mock_metadata_df = MagicMock()
    mock_metadata_df.toPandas.return_value = metadata_data

    def mock_table(table_name: str) -> MagicMock:
        if "users" in table_name and "metadata" not in table_name:
            return mock_users_df
        if "metadata" in table_name:
            return mock_metadata_df
        raise ValueError(f"Unknown table: {table_name}")

    mock_spark.table.side_effect = mock_table

    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")
    ds = Dataset("databricks_combined_inner_join", cfg)

    # First read
    df1 = ds.read_pandas()

    # Second read should return the same object (cached)
    df2 = ds.read_pandas()

    assert df1 is df2

    # Verify that Spark table was only called once per dataset (not twice)
    # This confirms caching is working
    assert mock_spark.table.call_count == 2  # Once for each dataset in the merge


# ============================================================================
# Mixed Type Tests
# ============================================================================


def test_combined_dataset_type_detection() -> None:
    """Test that component datasets have correct types."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    # Test individual local datasets
    csv_one = Dataset("csv_one", cfg)
    assert csv_one.type == "local"

    # Test individual Databricks datasets
    test_users = Dataset("test_users", cfg)
    assert test_users.type == "databricks"

    test_metadata = Dataset("test_users_metadata", cfg)
    assert test_metadata.type == "databricks"


def test_combined_dataset_description() -> None:
    """Test that combined datasets preserve their descriptions."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    local_ds = Dataset("local_combined_dataset", cfg)
    assert local_ds.description == "Combined datasets"

    db_ds = Dataset("databricks_combined_left_join", cfg)
    assert (
        db_ds.description == "Composite dataset from multiple datasets using left join"
    )


def test_combined_dataset_repr() -> None:
    """Test string representation of combined datasets."""
    cfg = YamlConfig(DATASETS_COMBINED_YAML, base_dir="tests/data/")

    local_ds = Dataset("local_combined_dataset", cfg)
    repr_str = repr(local_ds)
    assert "local_combined_dataset" in repr_str
    assert "combined" in repr_str.lower()

    db_ds = Dataset("databricks_combined_inner_join", cfg)
    repr_str = repr(db_ds)
    assert "databricks_combined_inner_join" in repr_str
    assert "combined" in repr_str.lower()


# ============================================================================
# Error Cases
# ============================================================================


def test_combined_dataset_missing_component() -> None:
    """Test error when a component dataset is missing."""
    # Create a YAML with a combined dataset referencing a non-existent dataset
    yaml_content = """
datasets:
  csv_one:
    path: "tests/data/csv_small_1.csv"
    format: csv
  bad_combined:
    merge_specs:
      csv_one:
        left_on: id
      nonexistent_dataset:
        right_on: id
        left_on: id
"""

    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    try:
        with pytest.raises(ValueError):
            YamlConfig(yaml_path)
    finally:
        Path(yaml_path).unlink()


def test_combined_dataset_empty_merge_specs() -> None:
    """Test error when merge_specs is empty."""
    yaml_content = """
datasets:
  empty_combined:
    merge_specs: {}
"""

    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    try:
        cfg = YamlConfig(yaml_path)
        ds = Dataset("empty_combined", cfg)

        with pytest.raises(ValueError, match="no merge_specs"):
            ds.read_pandas()
    finally:
        Path(yaml_path).unlink()
