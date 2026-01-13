from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pandas as pd

from .dataset import Dataset

if TYPE_CHECKING:
    from .config import YamlConfig


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    dataset: str
    numerical: list[str]
    categorical: list[str]
    column: list[str]
    description: str | None = None


class Feature:
    """Represents a feature set (group) defined in a features YAML.

    Expected structure under ``features``:

        features:
          group_name:
            description: "..."           # optional
            dataset: dataset_name         # required
            numerical: [col_a, col_b]     # optional list of columns
            categorical: [col_c, col_d]   # optional list of columns

    Also supports "columns" or "column" forms for auto-inferred types (they are equivalent):

        features:
          feature_name:
            dataset: dataset_name
            columns: [col_a, col_b, col_c]
            # OR
            column: [col_a, col_b, col_c]

    The "columns"/"column" fields are stored as a separate attribute "column" (as a list of column names).
    Their types (numerical/categorical) will be inferred automatically during experiment setup,
    rather than being assigned here.
    """

    def __init__(self, name: str, config: YamlConfig) -> None:
        self.name = name
        self.config = config

        features_section = self._get_features_section(config)
        if name not in features_section:
            raise KeyError(f"Feature '{name}' not found in configuration")  # noqa: TRY003

        spec_raw = features_section[name]
        if not isinstance(spec_raw, Mapping):
            raise TypeError(f"Feature '{name}' specification must be a mapping")  # noqa: TRY003

        dataset_name = spec_raw.get("dataset")
        description = spec_raw.get("description")

        if not isinstance(dataset_name, str) or not dataset_name:
            raise ValueError(  # noqa: TRY003
                f"Feature '{name}' is missing required 'dataset' string field"
            )

        # Accept both grouped (numerical/categorical), columns, and column schema
        numerical_cols: list[str] = []
        categorical_cols: list[str] = []
        column_cols: list[str] = []

        if "numerical" in spec_raw or "categorical" in spec_raw:
            raw_num = spec_raw.get("numerical", [])
            raw_cat = spec_raw.get("categorical", [])
            if not isinstance(raw_num, list) or not all(
                isinstance(x, str) for x in raw_num
            ):
                raise ValueError(  # noqa: TRY003
                    f"Feature '{name}'.numerical must be a list of strings"
                )
            if not isinstance(raw_cat, list) or not all(
                isinstance(x, str) for x in raw_cat
            ):
                raise ValueError(  # noqa: TRY003
                    f"Feature '{name}'.categorical must be a list of strings"
                )
            numerical_cols = list(raw_num)
            categorical_cols = list(raw_cat)
        elif "columns" in spec_raw or "column" in spec_raw:
            # Treat "columns" and "column" as equivalent
            column_names = spec_raw.get("columns") or spec_raw.get("column", [])
            if not isinstance(column_names, list) or not all(
                isinstance(x, str) for x in column_names
            ):
                field_name = "columns" if "columns" in spec_raw else "column"
                raise ValueError(  # noqa: TRY003
                    f"Feature '{name}'.{field_name} must be a list of strings"
                )
            # Store in column_cols for type inference later
            # These will be re-evaluated based on the dataset dtypes
            column_cols = list(column_names)
        else:
            raise ValueError(  # noqa: TRY003
                f"Feature '{name}' must define either 'numerical'/'categorical', 'columns', or 'column'"
            )

        self.spec = FeatureSpec(
            name=name,
            dataset=dataset_name,
            numerical=numerical_cols,
            categorical=categorical_cols,
            column=column_cols,
            description=description if isinstance(description, str) else None,
        )

        # Validate referenced dataset exists
        datasets = config.get_data().get("datasets")
        if not (isinstance(datasets, Mapping) and self.spec.dataset in datasets):
            raise ValueError(  # noqa: TRY003
                f"Feature '{name}' references unknown dataset '{self.spec.dataset}'"
            )

    @staticmethod
    def _get_features_section(config: YamlConfig) -> Mapping[str, Any]:
        features = config.get_data().get("features")
        if not isinstance(features, Mapping):
            raise KeyError("No 'features' section found in configuration")  # noqa: TRY003
        return features

    def get_series(self, column: str, *, index: str | None = None) -> pd.Series:
        """Materialize a single column from this feature set as a pandas Series.

        The ``column`` must be listed under this feature set's numerical,
        categorical, or column lists.
        """
        if (
            column not in self.spec.numerical
            and column not in self.spec.categorical
            and column not in self.spec.column
        ):
            raise KeyError(  # noqa: TRY003
                f"Column '{column}' is not declared in feature set '{self.name}'"
            )

        dataset = Dataset(self.spec.dataset, self.config)
        df = dataset.read_pandas()
        if index is not None and index in df.columns:
            df = df.set_index(index)
        if column not in df.columns:
            raise KeyError(  # noqa: TRY003
                f"Column '{column}' not found in dataset '{self.spec.dataset}'"
            )
        series = df[column].copy()
        series.name = f"{self.name}.{column}"
        return series

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.spec.name,
            "dataset": self.spec.dataset,
            "numerical": list(self.spec.numerical),
            "categorical": list(self.spec.categorical),
            "column": list(self.spec.column),
            "description": self.spec.description,
        }

    def get_columns_by_type(self) -> dict[str, list[str]]:
        return {
            "numerical": list(self.spec.numerical),
            "categorical": list(self.spec.categorical),
            "column": list(self.spec.column),
        }

    @classmethod
    def list_feature_names(cls, config: YamlConfig) -> list[str]:
        features = cls._get_features_section(config)
        return list(features.keys())

    @classmethod
    def load_all(cls, config: YamlConfig) -> dict[str, Feature]:
        names = cls.list_feature_names(config)
        return {name: cls(name, config) for name in names}

    @classmethod
    def to_dataframe(
        cls,
        config: YamlConfig,
        *,
        feature_sets: Iterable[str] | None = None,
        include_types: Sequence[str] | None = None,
        index: str | None = None,
    ) -> pd.DataFrame:
        """Materialize multiple feature sets into a pandas DataFrame.

        Parameters
        ----------
        feature_sets: optional iterable of feature set names to include. If None, all are used.
        include_types: optional list among ["numerical", "categorical", "column"] to filter columns.
        index: optional column name used as index before joining.
        """
        selected_sets = list(feature_sets or cls.list_feature_names(config))
        type_filter = set(include_types or ["numerical", "categorical"])

        series_list: list[pd.Series] = []
        for fs_name in selected_sets:
            fs = cls(fs_name, config)
            columns: list[str] = []
            if "numerical" in type_filter:
                columns.extend(fs.spec.numerical)
            if "categorical" in type_filter:
                columns.extend(fs.spec.categorical)
            if "column" in type_filter:
                columns.extend(fs.spec.column)
            for col in columns:
                series_list.append(fs.get_series(col, index=index))

        if not series_list:
            return pd.DataFrame()

        df = series_list[0].to_frame()
        for s in series_list[1:]:
            df = df.join(s, how="outer")
        return df

    @classmethod
    def verify_config(cls, config: YamlConfig) -> None:
        """Validate that all features are well-formed and reference known datasets.

        Checks
        ------
        - features section exists if referenced and is a mapping
        - each feature has a string "dataset" and the dataset exists in config.datasets
        - either numerical/categorical lists (lists of strings) are present, or a legacy
          single "column" (string) is provided
        - no column appears in both numerical and categorical within the same feature
        - at least one column is declared per feature
        """

        features = config.get_data().get("features")
        if features is None:
            return  # Nothing to verify
        if not isinstance(features, Mapping):
            raise TypeError("'features' section must be a mapping")  # noqa: TRY003

        datasets = config.get_data().get("datasets")
        if not isinstance(datasets, Mapping):
            raise TypeError("No 'datasets' section found while validating features")  # noqa: TRY003

        for feature_name, raw in features.items():
            if not isinstance(raw, Mapping):
                raise TypeError(  # noqa: TRY003
                    f"Feature '{feature_name}' specification must be a mapping"
                )

            dataset_name = raw.get("dataset")
            if not isinstance(dataset_name, str) or not dataset_name:
                raise ValueError(  # noqa: TRY003
                    f"Feature '{feature_name}' is missing required 'dataset' string field"
                )
            if dataset_name not in datasets:
                raise ValueError(  # noqa: TRY003
                    f"Feature '{feature_name}' references unknown dataset '{dataset_name}'"
                )

            has_grouped = ("numerical" in raw) or ("categorical" in raw)
            has_columns_or_column = "columns" in raw or "column" in raw
            declared_columns: list[str] = []
            if has_grouped:
                for key in ("numerical", "categorical"):
                    val = raw.get(key, [])
                    if val is None:
                        val = []
                    if not isinstance(val, list) or not all(
                        isinstance(x, str) for x in val
                    ):
                        raise ValueError(  # noqa: TRY003
                            f"Feature '{feature_name}'.{key} must be a list of strings"
                        )
                num_list = list(raw.get("numerical", []) or [])
                cat_list = list(raw.get("categorical", []) or [])
                # Check duplicates across types
                overlap = set(num_list).intersection(cat_list)
                if overlap:
                    dup = ", ".join(sorted(overlap))
                    raise ValueError(  # noqa: TRY003
                        f"Feature '{feature_name}' declares columns in both numerical and categorical: {dup}"
                    )
                declared_columns.extend(num_list)
                declared_columns.extend(cat_list)
                # '__all__' is only allowed in the 'columns'/'column' form and must be alone
                if "__all__" in num_list or "__all__" in cat_list:
                    raise ValueError(  # noqa: TRY003
                        f"Feature '{feature_name}' cannot use '__all__' inside 'numerical' or 'categorical'; use 'columns: [__all__]' or 'column: [__all__]'"
                    )
            elif has_columns_or_column:
                # Treat "columns" and "column" as equivalent
                column_names = raw.get("columns") or raw.get("column", [])
                field_name = "columns" if "columns" in raw else "column"
                if not isinstance(column_names, list) or not all(
                    isinstance(x, str) for x in column_names
                ):
                    raise ValueError(  # noqa: TRY003
                        f"Feature '{feature_name}'.{field_name} must be a list of strings"
                    )
                # If '__all__' is used, it must be the only entry
                if "__all__" in column_names and len(column_names) != 1:
                    raise ValueError(  # noqa: TRY003
                        f"Feature '{feature_name}' uses '__all__' alongside other columns; '__all__' must be alone"
                    )
                declared_columns.extend(column_names)
            else:
                raise ValueError(  # noqa: TRY003
                    f"Feature '{feature_name}' must define either 'numerical'/'categorical', 'columns', or 'column'"
                )
            if not declared_columns:
                raise ValueError(f"Feature '{feature_name}' declares no columns")  # noqa: TRY003
            # '__all__' is allowed only when it is the single entry in the 'columns' or 'column' list.
            # The grouped form is already rejected above.


__all__ = ["Feature", "FeatureSpec"]
