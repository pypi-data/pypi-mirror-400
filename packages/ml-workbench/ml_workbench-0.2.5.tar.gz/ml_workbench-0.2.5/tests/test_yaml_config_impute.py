from __future__ import annotations

from pathlib import Path

from ml_workbench.config import YamlConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_YAML = PROJECT_ROOT / "tests" / "data" / "datasets_impute.yaml"


def test_type_imputation_variations() -> None:
    cfg = YamlConfig(DATA_YAML)

    # Explicit formats are preserved
    assert cfg.datasets.explicit_csv.format == "csv"
    assert cfg.datasets.explicit_delta.format == "delta"
    # Types are imputed deterministically
    assert cfg.datasets.explicit_csv.type == "local"
    assert cfg.datasets.explicit_delta.type == "databricks"

    # File extension inference
    assert cfg.datasets.infer_csv.format == "csv"
    assert cfg.datasets.infer_txt.format == "txt"
    assert cfg.datasets.infer_parquet.format == "parquet"
    assert cfg.datasets.infer_json.format == "json"
    # Types
    assert cfg.datasets.infer_csv.type == "local"
    assert cfg.datasets.infer_txt.type == "local"

    # S3 paths still use extension inference
    assert cfg.datasets.s3_parquet.format == "parquet"
    assert cfg.datasets.s3_parquet.type == "s3"

    # Databricks table name heuristic (catalog.schema.table)
    assert cfg.datasets.dbr_table.format == "delta"
    assert cfg.datasets.dbr_table.type == "databricks"
    assert cfg.datasets.dbr_table_interpolated.format == "delta"
    assert cfg.datasets.dbr_table_interpolated.type == "databricks"

    # Unknown extensions remain without format, but type is still imputed
    assert cfg.datasets.unknown_ext.type == "local"
    assert "format" not in cfg.datasets.unknown_ext.to_dict()

    # Combined dataset should be untouched
    assert "type" not in cfg.datasets.combined.to_dict()
    assert "format" not in cfg.datasets.combined.to_dict()
