"""
Module for working with datasets.

Dataset class is responsible to read dataset in accordance with it type and format.
It also provides basic statistics about the dataset.

For combined datasets, it is responsible to read the datasets and merge them in accordance with the merge specification.

Dataset class is initialized with a dataset name and a dataset specification.
Primitive dataset specification is a dictionary with the following keys:
- name: str
- description: str
- path: str
- format: str
- type: str

Combined dataset specification is a dictionary with the following keys:
- name: str
- description: str
- merge_specs: dict
  - dataset_name: dict
    - right_on: str
    - left_on: str
    - how: str

Dataset class has the following methods:
- read: read the dataset in accordance with it type and format
- get_statistics: get basic statistics about the dataset
- get_schema: get the schema of the dataset
- get_columns: get the columns of the dataset
- get_rows: get the rows of the dataset
- get_head: get the head of the dataset
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

# Constants
DELTA_TABLE_PARTS_COUNT = 2  # catalog.schema.table format has 2 dots

if TYPE_CHECKING:
    from .config import YamlConfig


def _is_databricks_table_name(path: str) -> bool:
    """Return True if ``path`` looks like a Databricks table identifier.

    Heuristic: exactly two dots separating catalog.schema.table and no path separators
    or URL schemes. This keeps the check permissive and practical.
    """

    if "/" in path or "\\" in path:
        return False
    # Exclude common URL schemes
    if "://" in path:
        return False
    if path.count(".") != DELTA_TABLE_PARTS_COUNT:
        return False
    parts = path.split(".")
    return all(part.strip() for part in parts)


def _infer_dataset_format_from_path(path: str) -> str | None:
    """Infer dataset type from a path-like string.

    - If the value looks like a Databricks table name (catalog.schema.table), return "delta".
    - Otherwise infer by file extension (case-insensitive): csv, txt, parquet, json.
    - Returns None if no inference is possible.
    """

    if _is_databricks_table_name(path):
        return "delta"

    # Extract filename segment and extension without being confused by schemes
    last_segment = path.rsplit("/", 1)[-1]
    if "." not in last_segment:
        return None
    ext = last_segment.rsplit(".", 1)[-1].lower()
    if ext in {"csv", "txt", "parquet", "json"}:
        return ext
    return None


class Dataset:
    """Dataset abstraction for reading data from various sources.

    Supports:
    - Local files (CSV, TXT, Parquet, JSON)
    - S3 paths (CSV, Parquet, JSON)
    - Databricks Delta tables and /Volumes/ paths
    - Combined datasets via merge specifications

    Always returns pandas DataFrame regardless of source.
    """

    def __init__(self, name: str, config: YamlConfig) -> None:
        """Initialize a Dataset.

        Parameters
        ----------
        name : str
            Dataset name
        config : YamlConfig
            Configuration object containing dataset specifications
        """
        self.name = name
        self.config = config

        # Get dataset spec from config
        spec = config.get_dataset_config(name)

        self.path = spec.get("path")
        self.format = spec.get("format")
        self.type = spec.get("type", "local")
        self.description = spec.get("description")
        self.is_combined = "merge_specs" in spec
        self._merge_specs = spec.get("merge_specs") if self.is_combined else None
        self._df: pd.DataFrame | None = None

    def read_pandas(self) -> pd.DataFrame:
        """Read the dataset and return a pandas DataFrame.

        For combined datasets, reads all participating datasets and merges them
        according to merge specifications.

        Returns
        -------
        pd.DataFrame
            The loaded dataset

        Raises
        ------
        ValueError
            If path or format is missing or unsupported, or if config is missing
            for combined datasets
        RuntimeError
            If reading fails
        """
        if self._df is not None:
            return self._df

        # Handle combined datasets
        if self.is_combined:
            self._df = self._read_combined()
            return self._df

        # Handle primitive datasets
        if not self.path:
            raise ValueError(f"Dataset '{self.name}' has no path specified")  # noqa: TRY003

        if self.type == "databricks":
            self._df = self._read_databricks()
        elif self.type == "s3":
            self._df = self._read_s3()
        elif self.type == "local":
            self._df = self._read_local()
        else:
            raise ValueError(f"Unsupported dataset type: {self.type}")  # noqa: TRY003

        return self._df

    def _read_combined(self) -> pd.DataFrame:
        """Read and merge multiple datasets according to merge specifications.

        Returns
        -------
        pd.DataFrame
            Merged dataset

        Raises
        ------
        ValueError
            If merge specs are invalid
        """
        if not self._merge_specs:
            raise ValueError(f"Combined dataset '{self.name}' has no merge_specs")  # noqa: TRY003

        # Start with None; first dataset becomes the base
        result_df: pd.DataFrame | None = None

        # Convert to list to track position
        merge_items = list(self._merge_specs.items())

        # Iterate through merge specs in order
        for idx, (dataset_name, merge_spec) in enumerate(merge_items):
            # Get the dataset configuration
            try:
                self.config.get_dataset_config(dataset_name)
            except KeyError as exc:
                raise ValueError(  # noqa: TRY003
                    f"Dataset '{dataset_name}' referenced in merge_specs not found"
                ) from exc

            # Create and read the dataset
            ds = Dataset(dataset_name, self.config)
            df = ds.read_pandas()

            # First dataset becomes the base (no merge needed)
            if result_df is None:
                result_df = df
                continue

            # Merge with the accumulated result
            # right_on comes from current dataset's merge_spec
            # left_on and how come from previous dataset's merge_spec
            prev_dataset_name, prev_merge_spec = merge_items[idx - 1]
            right_on = merge_spec.get("right_on")
            left_on = prev_merge_spec.get("left_on")
            how = prev_merge_spec.get("how", "inner")

            # Perform the merge
            if right_on and left_on:
                # Merge on specified columns
                result_df = result_df.merge(
                    df,
                    left_on=left_on,
                    right_on=right_on,
                    how=how,
                )
            elif left_on:
                # Merge on index (right) and column (left)
                result_df = result_df.merge(
                    df,
                    right_index=True,
                    left_on=left_on,
                    how=how,
                )
            elif right_on:
                # Last dataset: merge on column (right) and index (left)
                result_df = result_df.merge(
                    df,
                    right_on=right_on,
                    left_index=True,
                    how=how,
                )
            else:
                # Both use index
                result_df = result_df.merge(
                    df,
                    right_index=True,
                    left_index=True,
                    how=how,
                )

        if result_df is None:
            raise ValueError(f"Combined dataset '{self.name}' produced no data")  # noqa: TRY003

        return result_df

    def _read_databricks(self) -> pd.DataFrame:
        """Read from Databricks (Delta tables or /Volumes/ paths)."""
        try:
            from pyspark.sql import (  # noqa: PLC0415
                SparkSession,  # type: ignore[import-not-found]  # noqa: PLC0415
            )

            spark = SparkSession.builder.getOrCreate()

            # Check if it's a table name (catalog.schema.table)
            if self.path.count(".") == DELTA_TABLE_PARTS_COUNT and "/" not in self.path:  # type: ignore[union-attr]
                # Delta table
                spark_df = spark.table(self.path)
            else:
                # File path under /Volumes/ or similar
                fmt = self.format or "delta"
                if fmt == "delta":
                    spark_df = spark.read.format("delta").load(self.path)
                elif fmt == "parquet":
                    spark_df = spark.read.parquet(self.path)
                elif fmt == "csv":
                    spark_df = spark.read.csv(self.path, header=True, inferSchema=True)
                elif fmt == "json":
                    spark_df = spark.read.json(self.path)
                elif fmt == "txt":
                    spark_df = spark.read.text(self.path)
                else:
                    raise ValueError(f"Unsupported format for Databricks: {fmt}")  # noqa: TRY003

            return spark_df.toPandas()
        except ImportError as exc:
            raise RuntimeError(  # noqa: TRY003
                "PySpark is required for Databricks datasets. "
                "Install with: pip install pyspark or databricks-connect"
            ) from exc

    def _read_s3(self) -> pd.DataFrame:
        """Read from S3 paths by fetching into an IO object via boto3."""
        import io  # noqa: PLC0415
        import re  # noqa: PLC0415

        import boto3  # noqa: PLC0415

        fmt = (self.format or "").lower()

        # Extract bucket and key from the S3 path
        # supports s3://bucket-name/key/to/object
        match = re.match(r"s3://([^/]+)/(.+)", self.path)
        if not match:
            raise ValueError(f"Invalid S3 path: {self.path}")  # noqa: TRY003
        bucket, key = match.groups()

        s3 = boto3.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        file_obj = io.BytesIO(obj["Body"].read())

        if fmt == "csv":
            return pd.read_csv(file_obj)
        if fmt == "parquet":
            return pd.read_parquet(file_obj)
        if fmt == "json":
            return pd.read_json(file_obj)
        raise ValueError(f"Unsupported format for S3: {fmt}")  # noqa: TRY003

    def _read_local(self) -> pd.DataFrame:
        """Read from local filesystem."""
        path = Path(self.path)  # type: ignore[arg-type]

        if not path.exists():
            raise FileNotFoundError(f"Local file not found: {path}")  # noqa: TRY003

        fmt = (self.format or "").lower()

        if fmt == "csv":
            return pd.read_csv(path)
        if fmt == "txt":
            # TXT files often are CSV-like with different delimiters
            return pd.read_csv(path, sep="\t")
        if fmt == "parquet":
            return pd.read_parquet(path)
        if fmt == "json":
            return pd.read_json(path)
        raise ValueError(f"Unsupported format for local files: {fmt}")  # noqa: TRY003

    def get_statistics(self) -> dict[str, Any]:
        """Get basic statistics about the dataset.

        Returns
        -------
        Dict[str, Any]
            Statistics including num_rows, num_columns, column_names, dtypes
        """
        df = self.read_pandas()
        return {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        }

    def get_schema(self) -> dict[str, str]:
        """Get the schema (column names and types).

        Returns
        -------
        Dict[str, str]
            Mapping of column name to dtype string
        """
        df = self.read_pandas()
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

    def get_columns(self) -> list[str]:
        """Get column names.

        Returns
        -------
        list[str]
            List of column names
        """
        df = self.read_pandas()
        return list(df.columns)

    def get_rows(self) -> int:
        """Get number of rows.

        Returns
        -------
        int
            Number of rows
        """
        df = self.read_pandas()
        return len(df)

    def get_head(self, n: int = 5) -> pd.DataFrame:
        """Get first n rows.

        Parameters
        ----------
        n : int, default 5
            Number of rows to return

        Returns
        -------
        pd.DataFrame
            First n rows
        """
        df = self.read_pandas()
        return df.head(n)

    def __repr__(self) -> str:
        return f"Dataset(name={self.name!r}, type={self.type}, format={self.format}, path={self.path!r})"

    @classmethod
    def _impute_dataset_types(cls, config: YamlConfig) -> None:
        """Impute dataset format and source type for entries in ``datasets``.

        - "format": csv, txt, parquet, json, delta (inferred from path or table name)
        - "type": databricks, s3, local (inferred from path and/or format)

        Datasets that represent composite/merged inputs (e.g. have ``merge_specs``)
        are left unchanged.
        """

        datasets = config.get_data().get("datasets")
        if not isinstance(datasets, dict):
            return

        for _dataset_name, dataset_spec in datasets.items():
            if not isinstance(dataset_spec, dict):
                continue

            # Skip combined datasets defined via merge specs
            if "merge_specs" in dataset_spec:
                continue

            dataset_path = dataset_spec.get("path")
            if not isinstance(dataset_path, str):
                continue

            # 1) Impute format if missing
            has_format = "format" in dataset_spec and dataset_spec.get(
                "format"
            ) not in (None, "")
            if not has_format:
                inferred_fmt = _infer_dataset_format_from_path(dataset_path)
                if inferred_fmt:
                    dataset_spec["format"] = inferred_fmt

            # 2) Impute source type if missing
            has_type = "type" in dataset_spec and dataset_spec.get("type") not in (
                None,
                "",
            )
            if not has_type:
                fmt = str(dataset_spec.get("format") or "").lower()
                if _is_databricks_table_name(dataset_path) or dataset_path.startswith(
                    "/Volumes/"
                ):
                    src_type = "databricks"
                elif dataset_path.startswith("s3://"):
                    src_type = "s3"
                elif fmt == "delta":
                    src_type = "databricks"
                else:
                    src_type = "local"
                dataset_spec["type"] = src_type

    @classmethod
    def verify_config(cls, config: YamlConfig) -> None:
        """Verify dataset configuration integrity.

        Steps:
        1. Impute dataset formats and types where missing.
        2. Validate that combined datasets reference only datasets defined in this config.

        Raises
        ------
        ValueError
            If a combined dataset references a dataset not present in the configuration.
        """

        # Step 1: impute
        cls._impute_dataset_types(config)

        # Step 2: validate combined dataset references
        datasets = config.get_data().get("datasets")
        if not isinstance(datasets, dict):
            return

        for combined_name, combined_spec in datasets.items():
            if not isinstance(combined_spec, dict):
                continue
            merge_specs = combined_spec.get("merge_specs")
            if not isinstance(merge_specs, dict):
                continue

            for referenced_name in merge_specs:
                if referenced_name not in datasets:
                    raise ValueError(  # noqa: TRY003
                        f"Combined dataset '{combined_name}' references unknown dataset '{referenced_name}'"
                    )
