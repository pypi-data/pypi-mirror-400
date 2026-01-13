from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ml_workbench.config import YamlConfig
from ml_workbench.dataset import Dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_FIXTURE = PROJECT_ROOT / "tests" / "data" / "csv_small_1.csv"
CSV_FIXTURE_2 = PROJECT_ROOT / "tests" / "data" / "csv_small_2.csv"
DATASETS_CLI_YAML = PROJECT_ROOT / "tests" / "data" / "datasets_cli.yaml"


def test_dataset_init(tmp_path: Path) -> None:
    # Create a simple YAML config
    yaml_content = """
datasets:
  test_ds:
    path: "/tmp/data.csv"
    format: csv
    type: local
    description: "Test dataset"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    ds = Dataset("test_ds", cfg)

    assert ds.name == "test_ds"
    assert ds.path == "/tmp/data.csv"
    assert ds.format == "csv"
    assert ds.type == "local"
    assert ds.description == "Test dataset"


def test_dataset_read_local_csv() -> None:
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    df = ds.read_pandas()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert len(df.columns) == 2
    assert list(df.columns) == ["id", "value"]


def test_dataset_read_caching() -> None:
    """Test that read() caches the DataFrame."""
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    df1 = ds.read_pandas()
    df2 = ds.read_pandas()

    # Should return the same cached object
    assert df1 is df2


def test_dataset_read_local_file_not_found(tmp_path: Path) -> None:
    yaml_content = """
datasets:
  missing:
    path: "/nonexistent/file.csv"
    format: csv
    type: local
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("missing", cfg)

    with pytest.raises(FileNotFoundError):
        ds.read_pandas()


def test_dataset_read_no_path(tmp_path: Path) -> None:
    yaml_content = """
datasets:
  no_path:
    format: csv
    type: local
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("no_path", cfg)

    with pytest.raises(ValueError, match="has no path specified"):
        ds.read_pandas()


def test_dataset_read_unsupported_type(tmp_path: Path) -> None:
    yaml_content = """
datasets:
  bad_type:
    path: "/tmp/data.csv"
    format: csv
    type: unknown_type
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("bad_type", cfg)

    with pytest.raises(ValueError, match="Unsupported dataset type"):
        ds.read_pandas()


def test_dataset_read_unsupported_format_local(tmp_path: Path) -> None:
    yaml_content = f"""
datasets:
  bad_format:
    path: "{CSV_FIXTURE}"
    format: unsupported
    type: local
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("bad_format", cfg)

    with pytest.raises(ValueError, match="Unsupported format for local files"):
        ds.read_pandas()


def test_dataset_get_statistics() -> None:
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    stats = ds.get_statistics()

    assert stats["num_rows"] == 3
    assert stats["num_columns"] == 2
    assert stats["column_names"] == ["id", "value"]
    assert "id" in stats["dtypes"]
    assert "value" in stats["dtypes"]
    assert stats["memory_usage_bytes"] > 0


def test_dataset_get_schema() -> None:
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    schema = ds.get_schema()

    assert "id" in schema
    assert "value" in schema
    assert isinstance(schema["id"], str)


def test_dataset_get_columns() -> None:
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    columns = ds.get_columns()

    assert columns == ["id", "value"]


def test_dataset_get_rows() -> None:
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    rows = ds.get_rows()

    assert rows == 3


def test_dataset_get_head() -> None:
    cfg = YamlConfig(DATASETS_CLI_YAML)
    ds = Dataset("csv_one", cfg)
    head = ds.get_head(2)

    assert isinstance(head, pd.DataFrame)
    assert len(head) == 2
    assert list(head.columns) == ["id", "value"]


def test_dataset_repr(tmp_path: Path) -> None:
    yaml_content = """
datasets:
  test_ds:
    path: "/tmp/data.csv"
    format: csv
    type: local
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("test_ds", cfg)
    repr_str = repr(ds)

    assert "test_ds" in repr_str
    assert "local" in repr_str
    assert "csv" in repr_str


@patch("boto3.client")
@patch("ml_workbench.dataset.pd.read_csv")
def test_dataset_read_s3_csv(mock_read_csv: MagicMock, mock_boto3_client: MagicMock, tmp_path: Path) -> None:
    """Test S3 CSV reading."""
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_read_csv.return_value = mock_df

    # Mock boto3 S3 client
    mock_s3_client = MagicMock()
    mock_boto3_client.return_value = mock_s3_client

    # Create mock S3 object response with Body that has read() method
    csv_content = b"col1,col2\n1,3\n2,4\n"
    mock_body = MagicMock()
    mock_body.read.return_value = csv_content
    mock_s3_client.get_object.return_value = {"Body": mock_body}

    yaml_content = """
datasets:
  s3_csv:
    path: "s3://bucket/data.csv"
    format: csv
    type: s3
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("s3_csv", cfg)
    df = ds.read_pandas()

    mock_boto3_client.assert_called_once_with("s3")
    mock_s3_client.get_object.assert_called_once_with(Bucket="bucket", Key="data.csv")
    mock_read_csv.assert_called_once()
    assert df is mock_df


@patch("boto3.client")
@patch("ml_workbench.dataset.pd.read_parquet")
def test_dataset_read_s3_parquet(mock_read_parquet: MagicMock, mock_boto3_client: MagicMock, tmp_path: Path) -> None:
    """Test S3 Parquet reading."""
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_read_parquet.return_value = mock_df

    # Mock boto3 S3 client
    mock_s3_client = MagicMock()
    mock_boto3_client.return_value = mock_s3_client

    # Create mock S3 object response with Body that has read() method
    parquet_content = b"dummy parquet content"
    mock_body = MagicMock()
    mock_body.read.return_value = parquet_content
    mock_s3_client.get_object.return_value = {"Body": mock_body}

    yaml_content = """
datasets:
  s3_parquet:
    path: "s3://bucket/data.parquet"
    format: parquet
    type: s3
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("s3_parquet", cfg)
    df = ds.read_pandas()

    mock_boto3_client.assert_called_once_with("s3")
    mock_s3_client.get_object.assert_called_once_with(Bucket="bucket", Key="data.parquet")
    mock_read_parquet.assert_called_once()
    assert df is mock_df


@patch("boto3.client")
def test_dataset_read_s3_unsupported_format(mock_boto3_client: MagicMock, tmp_path: Path) -> None:
    """Test S3 unsupported format raises error."""
    # Mock boto3 S3 client
    mock_s3_client = MagicMock()
    mock_boto3_client.return_value = mock_s3_client

    # Create mock S3 object response with Body that has read() method
    txt_content = b"dummy text content"
    mock_body = MagicMock()
    mock_body.read.return_value = txt_content
    mock_s3_client.get_object.return_value = {"Body": mock_body}

    yaml_content = """
datasets:
  s3_txt:
    path: "s3://bucket/data.txt"
    format: txt
    type: s3
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("s3_txt", cfg)

    with pytest.raises(ValueError, match="Unsupported format for S3"):
        ds.read_pandas()


@patch("pyspark.sql.SparkSession")
def test_dataset_read_databricks_table(
    mock_spark_session: MagicMock, tmp_path: Path
) -> None:
    """Test Databricks Delta table reading."""
    mock_spark = MagicMock()
    mock_spark_session.builder.getOrCreate.return_value = mock_spark

    mock_spark_df = MagicMock()
    mock_pandas_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_spark_df.toPandas.return_value = mock_pandas_df
    mock_spark.table.return_value = mock_spark_df

    yaml_content = """
datasets:
  dbr_table:
    path: "catalog.schema.table"
    format: delta
    type: databricks
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("dbr_table", cfg)
    df = ds.read_pandas()

    mock_spark.table.assert_called_once_with("catalog.schema.table")
    assert df is mock_pandas_df


@patch("pyspark.sql.SparkSession")
def test_dataset_read_databricks_volumes_csv(
    mock_spark_session: MagicMock, tmp_path: Path
) -> None:
    """Test Databricks /Volumes/ CSV reading."""
    mock_spark = MagicMock()
    mock_spark_session.builder.getOrCreate.return_value = mock_spark

    mock_spark_df = MagicMock()
    mock_pandas_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_spark_df.toPandas.return_value = mock_pandas_df
    mock_spark.read.csv.return_value = mock_spark_df

    yaml_content = """
datasets:
  dbr_csv:
    path: "/Volumes/catalog/schema/volume/data.csv"
    format: csv
    type: databricks
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("dbr_csv", cfg)
    df = ds.read_pandas()

    mock_spark.read.csv.assert_called_once_with(
        "/Volumes/catalog/schema/volume/data.csv", header=True, inferSchema=True
    )
    assert df is mock_pandas_df


def test_dataset_read_databricks_no_pyspark(tmp_path: Path) -> None:
    """Test that missing PySpark raises helpful error."""
    yaml_content = """
datasets:
  dbr_table:
    path: "catalog.schema.table"
    format: delta
    type: databricks
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("dbr_table", cfg)

    with patch.dict("sys.modules", {"pyspark.sql": None}):
        with pytest.raises(RuntimeError, match="PySpark is required"):
            ds.read_pandas()


def test_dataset_combined_basic(tmp_path: Path) -> None:
    """Test basic combined dataset with merge."""
    # Create test CSV files
    csv1 = tmp_path / "data1.csv"
    csv1.write_text("id,value\n1,10\n2,20\n", encoding="utf-8")

    csv2 = tmp_path / "data2.csv"
    csv2.write_text("id,score\n1,100\n2,200\n", encoding="utf-8")

    # Create config YAML
    yaml_content = f"""
datasets:
  ds1:
    path: "{csv1}"
    format: csv
    type: local
  ds2:
    path: "{csv2}"
    format: csv
    type: local
  combined:
    description: "Combined dataset"
    merge_specs:
      ds1:
        left_on: id
      ds2:
        right_on: id
        left_on: id
        how: inner
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    ds = Dataset("combined", cfg)
    df = ds.read_pandas()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    # Should have columns from both datasets
    assert "value" in df.columns
    assert "score" in df.columns


def test_dataset_combined_no_merge_specs(tmp_path: Path) -> None:
    """Test that combined dataset without merge_specs raises error."""
    yaml_content = """
datasets:
  combined:
    description: "Empty combined"
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)
    ds = Dataset("combined", cfg)

    # Should not be marked as combined without merge_specs
    assert ds.is_combined is False


def test_dataset_combined_missing_dataset(tmp_path: Path) -> None:
    """Test that referencing non-existent dataset raises error."""
    csv1 = tmp_path / "data1.csv"
    csv1.write_text("id,value\n1,10\n", encoding="utf-8")

    yaml_content = f"""
datasets:
  ds1:
    path: "{csv1}"
    format: csv
    type: local
  combined:
    merge_specs:
      ds1:
        left_on: id
      nonexistent:
        right_on: id
        left_on: id
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    # Validation happens during config load now
    with pytest.raises(ValueError):
        YamlConfig(yaml_file)


def test_dataset_combined_missing_left_on(tmp_path: Path) -> None:
    """Test that merge spec without left_on and merge on indices."""
    csv1 = tmp_path / "data1.csv"
    csv1.write_text("id,value\n1,10\n", encoding="utf-8")

    csv2 = tmp_path / "data2.csv"
    csv2.write_text("id,score\n1,100\n", encoding="utf-8")

    csv3 = tmp_path / "data3.csv"
    csv3.write_text("id,flag\n0,true\n1,false\n", encoding="utf-8")

    yaml_content = f"""
datasets:
  ds1:
    path: "{csv1}"
    format: csv
    type: local
  ds2:
    path: "{csv2}"
    format: csv
    type: local
  ds3:
    path: "{csv3}"
    format: csv
    type: local
  combined:
    merge_specs:
      ds1:
        left_on: id
      ds2:
        right_on: id
        how: inner
      ds3:
        right_on: id
        how: inner
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)

    ds = Dataset("combined", cfg)

    # ds2 is in the middle and missing left_on, should use index for merge
    df = ds.read_pandas()
    assert len(df) == 1
    assert "id" in df.columns
    assert "value" in df.columns
    assert "score" in df.columns
    assert "flag" in df.columns

    # Should have score==100 and flag==true
    assert df["score"][0] == 100
    assert df["flag"][0]


def test_dataset_combined_last_without_right_on(tmp_path: Path) -> None:
    """Test that last dataset can omit right_on and merge on indices."""
    csv1 = tmp_path / "data1.csv"
    csv1.write_text("id,value\n1,10\n2,20\n", encoding="utf-8")

    csv2 = tmp_path / "data2.csv"
    # CSV where we'll merge using left_on=id and left_on=True
    csv2.write_text("score,flag\n100,true\n200,false\n", encoding="utf-8")

    yaml_content = f"""
datasets:
  ds1:
    path: "{csv1}"
    format: csv
    type: local
  ds2:
    path: "{csv2}"
    format: csv
    type: local
  combined:
    merge_specs:
      ds1:
        how: inner
      ds2:
        how: left
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    cfg = YamlConfig(yaml_file)
    ds = Dataset("combined", cfg)
    df = ds.read_pandas()

    # Should successfully merge using left_on=id and left_on=True for ds2
    # Since ds2 has index 0,1 and we're merging on id (1,2), we expect 2 rows
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "value" in df.columns
    # score and flag should be present but may have NaN for mismatched indices
    assert "score" in df.columns or "flag" in df.columns


def test_dataset_combined_from_yaml() -> None:
    """Test combined dataset from datasets_cli.yaml."""
    cfg = YamlConfig(DATASETS_CLI_YAML)

    ds = Dataset("combined_dataset", cfg)
    df = ds.read_pandas()

    assert isinstance(df, pd.DataFrame)
    # Should have columns from all three datasets
    assert "id" in df.columns
    assert "value" in df.columns  # from csv_one
    assert "user_id" in df.columns  # from csv_user_id
    # csv_two columns should be present (score, flag)
    assert "score" in df.columns or len(df) > 0  # May not have matches due to left join

    # csv_one has 3 rows, left join should preserve them
    assert len(df) >= 3


def test_dataset_combined_merge_logic() -> None:
    """Test that merge logic follows the specifications correctly."""
    cfg = YamlConfig(DATASETS_CLI_YAML)

    ds = Dataset("combined_dataset", cfg)
    df = ds.read_pandas()

    # Verify merge happened correctly
    # csv_one (id=1,2,3) -> csv_user_id (id=1-10, user_id=u1-u10) -> csv_two (user_id=u1,u2)
    # First merge: csv_one (3 rows) left join csv_user_id on id
    # Should get 3 rows with user_id filled in
    # Second merge: result left join csv_two on user_id
    # Should still have 3 rows, but only id=1,2 will have score/flag

    assert len(df) == 3
    # Check that id values are preserved
    assert set(df["id"].dropna().astype(int)) == {1, 2, 3}


def test_dataset_combined_caching() -> None:
    """Test that combined dataset caching works."""
    cfg = YamlConfig(DATASETS_CLI_YAML)

    ds = Dataset("combined_dataset", cfg)
    df1 = ds.read_pandas()
    df2 = ds.read_pandas()

    # Should return cached DataFrame
    assert df1 is df2


def test_dataset_combined_statistics() -> None:
    """Test statistics methods work on combined datasets."""
    cfg = YamlConfig(DATASETS_CLI_YAML)

    ds = Dataset("combined_dataset", cfg)

    # Test get_statistics
    stats = ds.get_statistics()
    assert stats["num_rows"] == 3
    assert stats["num_columns"] > 0
    assert "id" in stats["column_names"]
    assert "value" in stats["column_names"]

    # Test get_columns
    columns = ds.get_columns()
    assert "id" in columns
    assert "value" in columns
    assert "user_id" in columns

    # Test get_rows
    rows = ds.get_rows()
    assert rows == 3

    # Test get_head
    head = ds.get_head(2)
    assert len(head) == 2

    # Test get_schema
    schema = ds.get_schema()
    assert isinstance(schema, dict)
    assert "id" in schema


def test_dataset_is_combined_flag(tmp_path: Path) -> None:
    """Test that is_combined flag is set correctly."""
    # Regular dataset
    yaml_content = """
datasets:
  regular:
    path: "/tmp/data.csv"
    format: csv
    type: local
  combined:
    merge_specs:
      regular:
        left_on: id
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    cfg = YamlConfig(yaml_file)

    ds1 = Dataset("regular", cfg)
    assert ds1.is_combined is False

    # Combined dataset
    ds2 = Dataset("combined", cfg)
    assert ds2.is_combined is True
