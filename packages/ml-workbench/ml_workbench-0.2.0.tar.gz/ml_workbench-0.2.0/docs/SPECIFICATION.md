# ML Workbench YAML Configuration Specification

## Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Include Directive](#include-directive)
4. [Defaults Section](#defaults-section)
5. [Datasets Section](#datasets-section)
6. [Features Section](#features-section)
7. [Models Section](#models-section)
8. [Experiments Section](#experiments-section)
9. [MLflow Section](#mlflow-section)
10. [Complete Example](#complete-example)
11. [Validation Rules](#validation-rules)

---

## Overview

The ML Workbench uses YAML configuration files to define machine learning experiments in a declarative way. The configuration consists of several main sections:

- **`defaults`**: Variable definitions for placeholder interpolation
- **`datasets`**: Data source definitions (files, tables, or combined datasets)
- **`features`**: Feature set definitions with column type specifications
- **`models`**: Model definitions with hyperparameters and tuning configurations
- **`experiments`**: Complete experiment specifications that combine datasets, features, and models
- **`mlflow`**: MLflow experiment tracking configuration (optional)

---

## File Structure

### Basic Structure

```yaml
# Optional: include other YAML files
include:
  - path/to/file1.yaml
  - path/to/file2.yaml

# Optional: default values for variable interpolation
defaults:
  key1: value1
  key2: value2

# Required sections (at least one of these should be defined)
datasets:
  # dataset definitions

features:
  # feature definitions

models:
  # model definitions

experiments:
  # experiment definitions

# Optional: MLflow experiment tracking configuration
mlflow:
  # MLflow configuration
```

---

## Include Directive

The `include` directive allows you to split configuration across multiple files and compose them together.

### Syntax

```yaml
include:
  - snippets/datasets.yaml
  - snippets/features.yaml
  - snippets/models.yaml
```

### Rules

- **Format**: List of file paths (strings)
- **Path resolution**: 
  - Relative paths are resolved relative to the current file's directory
  - If not found, attempts resolution relative to the project root
  - Absolute paths are used as-is
- **Merging**: Included files are merged recursively (deep merge)
  - Current file's values take precedence over included files
  - Sections (e.g., `datasets`, `features`) are merged at the key level
- **Circular includes**: Detected and prevented (raises error)

### Example

```yaml
# experiments/my_experiment.yaml
include:
  - snippets/datasets.yaml
  - snippets/features.yaml

experiments:
  my_exp:
    dataset: house_prices  # Defined in snippets/datasets.yaml
    features: house_prices  # Defined in snippets/features.yaml
    # ... rest of config
```

---

## Defaults Section

The `defaults` section defines variables that can be used for placeholder interpolation throughout the configuration.

### Syntax

```yaml
defaults:
  s3_path: s3://your-bucket/your-path
  third_party_path: /Volumes/third_party/cgm/
  catalog: pheno
  schema: ml
  path: experiments
```

### Usage

Variables are referenced using Python `str.format()` style placeholders: `{variable_name}`

```yaml
defaults:
  catalog: pheno
  schema: ml

datasets:
  my_dataset:
    path: "{catalog}.{schema}.my_table"  # Becomes: pheno.ml.my_table
```

### Override

- Variables can be overridden programmatically when loading the config
- Command-line arguments override file defaults
- Strict mode (default): raises error if placeholder has no value
- Non-strict mode: leaves undefined placeholders unchanged

---

## Datasets Section

The `datasets` section defines data sources that can be used in features and experiments.

### Dataset Types

There are two main types of datasets:

1. **Primitive datasets**: Single data source (file, table, S3)
2. **Combined datasets**: Merge multiple datasets together

### Primitive Dataset Specification

```yaml
datasets:
  dataset_name:
    description: "Optional description"  # Optional
    path: "path/to/data"                  # Required
    format: "csv|txt|parquet|json|delta"  # Optional (auto-inferred)
    type: "local|s3|databricks"           # Optional (auto-inferred)
```

#### Fields

- **`description`** (optional): Human-readable description
- **`path`** (required): Location of the data
  - Local file: relative or absolute path (e.g., `../data/file.csv`)
  - Databricks table: `catalog.schema.table` (three-part name)
  - Databricks volume: `/Volumes/catalog/schema/volume/file.csv`
  - S3: `s3://bucket/path/to/file.parquet`
- **`format`** (optional): File format
  - Valid values: `csv`, `txt`, `parquet`, `json`, `delta`
  - Auto-inferred from file extension or path pattern if not specified
  - Case-insensitive (e.g., `CSV`, `csv`, `Csv` are all valid)
- **`type`** (optional): Source type
  - Valid values: `local`, `s3`, `databricks`
  - Auto-inferred based on path pattern:
    - Path starts with `/Volumes/` → `databricks`
    - Path matches `catalog.schema.table` → `databricks`
    - Path starts with `s3://` → `s3`
    - Format is `delta` → `databricks`
    - Otherwise → `local`

#### Examples

```yaml
datasets:
  # Databricks Delta table (auto-inferred type and format)
  pheno_cgm:
    description: "CGM timeseries dataset"
    path: "pheno.ml.cgm_v2_timeseries"
    format: "delta"
    type: "databricks"

  # CSV file in Databricks volumes (auto-inferred type)
  chase2025_cgm:
    description: "CGM dataset from Chase2025"
    path: "/Volumes/third_party/cgm/Chase2005/tblCDataCGMS.csv"
    format: "csv"

  # S3 parquet file (auto-inferred format and type)
  s3_cgm:
    description: "CGM dataset from S3"
    path: "s3://datasets-development/samsung_health/cgm.parquet"

  # Local CSV file with variable interpolation
  local_file:
    description: "Local CSV file"
    path: "{path}/house_prices.csv"
    format: "csv"
    type: "local"

  # TXT file with tab delimiter
  aleppo2017:
    description: "CGM dataset from Aleppo2017"
    path: "{third_party_path}Aleppo2017/HDeviceCGM.txt"
    format: "txt"
```

### Combined Dataset Specification

Combined datasets merge multiple primitive datasets using join operations.

```yaml
datasets:
  combined_dataset_name:
    description: "Optional description"
    merge_specs:
      first_dataset_name:
        left_on: column_name_or_list    # Optional
        how: "inner|left|right|outer"   # Optional (default: inner)
      second_dataset_name:
        right_on: column_name_or_list   # Optional
```

#### Fields

- **`merge_specs`**: Dictionary of datasets to merge (in order)
  - **Keys**: Names of datasets to merge (must be defined in `datasets` section)
  - **Values**: Merge specification dictionaries

#### Merge Specification Fields

- **`left_on`**: Column name(s) from the accumulated result (left side)
  - Can be a string (single column) or list (multiple columns)
  - Optional: if omitted, uses index
  - For intermediate datasets: specifies columns to use for the **next** merge
- **`right_on`**: Column name(s) from the current dataset (right side)
  - Can be a string (single column) or list (multiple columns)
  - Optional: if omitted, uses index
  - Specifies columns from the current dataset to merge with the accumulated result
- **`how`**: Join type (optional, default: `"inner"`)
  - Valid values: `"inner"`, `"left"`, `"right"`, `"outer"`, `"cross"`
  - For intermediate datasets: applies to the **next** merge

#### Merge Logic

1. The first dataset in `merge_specs` becomes the base (no merge needed)
2. For each subsequent dataset:
   - Use `left_on` from the **previous** dataset's merge spec (or index if not specified)
   - Use `right_on` from the **current** dataset's merge spec (or index if not specified)
   - Use `how` from the **previous** dataset's merge spec (defaults to `"inner"` if not specified)
3. Intermediate datasets can specify both `left_on` and `right_on`:
   - `right_on`: used for merging with the accumulated result from previous datasets
   - `left_on`: used for the next merge with subsequent datasets
4. If only `left_on` specified: merge on column (left) and index (right)
5. If only `right_on` specified: merge on index (left) and column (right)
6. If neither specified: merge on index (both sides)
7. Multiple datasets (3+) can be merged sequentially using this pattern

#### Examples

```yaml
datasets:
  # Simple datasets
  test_users:
    path: "pheno.test.users"
  
  test_users_metadata:
    path: "pheno.test.user_metadata"

  # Combined with inner join
  test_users_combined_inner:
    description: "Users with metadata (inner join)"
    merge_specs:
      test_users:
        left_on: participant_uuid
        how: inner
      test_users_metadata:
        right_on: participant_uuid

  # Combined with left join (keeps all users, even without metadata)
  test_users_combined_left:
    description: "All users with optional metadata"
    merge_specs:
      test_users:
        left_on: participant_uuid
        how: left
      test_users_metadata:
        right_on: participant_uuid

  # Complex merge with multiple columns
  cgm_combined:
    description: "CGM timeseries with metadata"
    merge_specs:
      pheno_cgm_timeseries:
        left_on: [pia_uuid, participant_uuid]
        how: inner
      pheno_metadata:
        right_on: [pia_uuid, participant_uuid]

  # Merging three or more datasets
  combined_iglu_hba1c:
    description: "Combined dataset with baseline, features, and target"
    merge_specs:
      baseline_az:
        left_on: participant_id
        how: inner
      az_databricks_iglu_features:
        right_on: participant_id      # Merge with baseline_az
        left_on: participant_id       # Prepare for next merge
        how: inner
      az_target_hba1c_within_6_months:
        right_on: participant_id      # Merge with accumulated result
```

---

## Features Section

The `features` section defines groups of features (columns) that can be used in experiments.

### Feature Group Specification

```yaml
features:
  feature_group_name:
    description: "Optional description"  # Optional
    dataset: "dataset_name"               # Required
    # Choose one of the following approaches:
    
    # Approach 1: Explicit type specification
    numerical: [col1, col2, ...]          # Optional list
    categorical: [col3, col4, ...]        # Optional list
    
    # Approach 2: Auto-inferred types
    columns: [col1, col2, col3, ...]      # Optional list
    
    # Approach 3: All columns (excluding target)
    columns: [__all__]                    # Special keyword
```

#### Fields

- **`description`** (optional): Human-readable description
- **`dataset`** (required): Name of dataset (must exist in `datasets` section)
- **Column specification** (required, choose one approach):

##### Approach 1: Explicit Type Specification

```yaml
features:
  handgrip:
    description: "Handgrip strength measurements"
    dataset: "handgrip_dataset"
    numerical:
      - hand_grip_strength_left
      - hand_grip_strength_right
    categorical:
      - hand_grip_strength_left_type
      - hand_grip_strength_right_type
```

- **`numerical`**: List of numerical column names (float, int)
- **`categorical`**: List of categorical column names (string, bool)
- Column types are used explicitly as specified
- A column cannot appear in both lists (raises validation error)

##### Approach 2: Auto-Inferred Types

```yaml
features:
  handgrip_auto:
    description: "Same features, auto-inferred types"
    dataset: "handgrip_dataset"
    columns:
      - hand_grip_strength_left
      - hand_grip_strength_right
      - hand_grip_strength_left_type
      - hand_grip_strength_right_type
```

- **`columns`**: List of column names
- Types are inferred from DataFrame dtypes:
  - Numerical: `int64`, `float64`, etc.
  - Categorical: `object`, `string`, `bool`, `category`

##### Approach 3: All Columns

```yaml
features:
  all_features:
    description: "Use all columns except target"
    dataset: "my_dataset"
    columns:
      - __all__
```

- **`__all__`**: Special keyword meaning "all columns in the dataset"
- Target column is automatically excluded during experiment execution
- Types are auto-inferred from DataFrame dtypes

#### Examples

```yaml
features:
  # Explicit typing
  cgm_features:
    description: "CGM and demographic features"
    dataset: "cgm_combined_dataset"
    numerical:
      - cgm_timeseries
      - age
      - zip_code
    categorical:
      - sex
      - cgm_source

  # Auto-inferred typing
  house_prices:
    description: "House features with auto-inferred types"
    dataset: "house_prices"
    columns:
      - YrSold
      - YearRemodAdd
      - BsmtUnfSF
      - MasVnrArea
      - HeatingQC
      - Street
      - GarageType

  # All columns
  house_prices_all:
    description: "All house features"
    dataset: "house_prices"
    columns:
      - __all__
```

---

## Models Section

The `models` section defines machine learning models with their hyperparameters and tuning configurations.

### Model Specification

```yaml
models:
  model_name:
    description: "Optional description"        # Optional
    type: "package.module.ClassName"          # Required
    params:                                    # Optional
      param1: value1
      param2: value2
    tuning:                                    # Optional
      method: "grid_search|random_search"     # Optional
      # ... tuning parameters
```

#### Fields

- **`description`** (optional): Human-readable description
- **`type`** (required): Fully qualified Python class name
  - Format: `"package.module.ClassName"`
  - Must be importable at runtime
  - Example: `"sklearn.linear_model.Lasso"`
- **`params`** (optional): Model initialization parameters
  - Free-form dictionary
  - Keys and values passed to model constructor
  - Values can be any valid YAML types
- **`tuning`** (optional): Hyperparameter tuning configuration
  - Free-form dictionary
  - Implementation-specific structure
  - Typically used for cross-validation and grid/random search

#### Tuning Configuration (Common Pattern)

```yaml
tuning:
  method: "grid_search"           # or "random_search"
  inner_cv: 3                     # Inner cross-validation folds
  outer_cv: 3                     # Outer cross-validation folds
  scoring: "neg_mean_squared_error"  # Scoring metric
  param_grid:                     # Parameters to search
    alpha: [0.1, 1.0, 10.0]
    l1_ratio: [0.3, 0.5, 0.7]
  n_iter: 30                      # For random_search only
```

##### Tuning Fields

- **`method`**: Search strategy
  - `"grid_search"`: Exhaustive search over all parameter combinations
  - `"random_search"`: Random sampling of parameter combinations
- **`inner_cv`**: Number of folds for inner cross-validation (hyperparameter tuning)
- **`outer_cv`**: Number of folds for outer cross-validation (model evaluation)
- **`scoring`**: Scoring metric for optimization
  - Examples: `"neg_mean_squared_error"`, `"r2"`, `"accuracy"`, `"f1"`
- **`param_grid`**: Parameters to search over
  - Dictionary where keys are parameter names
  - Values are lists of values to try (grid search) or distributions (random search)
  - Special `logspace` format for logarithmic parameter ranges
- **`n_iter`**: Number of iterations for random search

#### Special Parameter Grid Formats

##### Logspace Range

```yaml
param_grid:
  alpha: [0.1, 1.0, 10.0]  # Will be overwritten
  logspace:
    start: -2              # 10^-2 = 0.01
    stop: 2                # 10^2 = 100
    num: 50                # 50 values logarithmically spaced
```

Generates: `[0.01, 0.0126, 0.0158, ..., 79.4, 100]`

#### Examples

```yaml
models:
  # Linear regression with L1 regularization
  lasso:
    description: "Linear regression with L1 regularization"
    type: "sklearn.linear_model.Lasso"
    params:
      alpha: 1.0
      random_state: 42
      max_iter: 100000
      tol: 0.0001
      selection: "cyclic"
    tuning:
      method: "random_search"
      inner_cv: 3
      outer_cv: 3
      scoring: "neg_mean_squared_error"
      param_grid:
        alpha:
          logspace:
            start: -2
            stop: 2
            num: 50
      n_iter: 30

  # ElasticNet with grid search
  elasticnet:
    description: "Linear regression with L1 and L2 regularization"
    type: "sklearn.linear_model.ElasticNet"
    params:
      alpha: 1.0
      l1_ratio: 0.5
      random_state: 42
      max_iter: 1000000
      tol: 0.0001
      selection: "cyclic"
    tuning:
      method: "grid_search"
      inner_cv: 3
      outer_cv: 3
      scoring: "neg_mean_squared_error"
      param_grid:
        alpha: [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 75.0, 100.0]
        l1_ratio: [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]

  # Random forest (no tuning)
  random_forest:
    description: "Random forest regressor"
    type: "sklearn.ensemble.RandomForestRegressor"
    params:
      n_estimators: 100
      max_depth: 10
      random_state: 42
      n_jobs: -1
```

---

## Experiments Section

The `experiments` section brings together datasets, features, and models to define complete machine learning experiments.

### Experiment Specification

```yaml
experiments:
  experiment_name:
    description: "Optional description"               # Optional
    models: model_name or [model1, model2]           # Required
    dataset: dataset_name                             # Required
    target: target_column_name                        # Required
    features: feature_name                            # Required
    do_not_split_by: [column_name]                   # Optional
    drop_outliers: 3.0 or 0.0 or false               # Optional (default: 3.0)
    metrics: metric_name or [metric1, metric2]       # Optional
    hold_out:                                         # Optional
      fraction: 0.3
      random_state: 42
      stratify: false
```

#### Fields

- **`description`** (optional): Human-readable description of the experiment

- **`models`** (required): Model(s) to use
  - Single model: `"model_name"`
  - Multiple models: `["model1", "model2", "model3"]`
  - All model names must exist in `models` section

- **`dataset`** (required): Dataset to use
  - Single dataset name (string)
  - Must exist in `datasets` section

- **`target`** (required): Target column name to predict
  - Single column name (string)
  - Must exist in the specified dataset

- **`features`** (required): Feature set to use
  - Single feature set name (string)
  - Must exist in `features` section

- **`do_not_split_by`** (optional): Column(s) to keep together during splitting
  - Single column: `"participant_uuid"`
  - Multiple columns: `["participant_uuid", "session_id"]`
  - Default: `[]` (no grouping)
  - Used to prevent data leakage (e.g., keep all data for a participant in same split)

- **`drop_outliers`** (optional): Outlier detection and removal threshold
  - Number (float): Z-score threshold for outlier detection (e.g., `3.0` means 3 standard deviations)
  - `0.0` or `false`: Disable outlier detection
  - Default: `3.0` (outliers beyond 3 standard deviations are marked)
  - Outliers are detected using Z-score method on numeric features and target
  - Rows marked as outliers are excluded from train/holdout splits

- **`metrics`** (optional): Evaluation metric(s)
  - Single metric: `"r2"`
  - Multiple metrics: `["r2", "mse", "mae"]`
  - Default: `[]` (implementation-defined default metrics)
  - Common metrics: `"r2"`, `"mse"`, `"mae"`, `"rmse"`, `"accuracy"`, `"f1"`, `"precision"`, `"recall"`
  - First metric in list is used to select the best model if multiple models are specified

- **`hold_out`** (optional): Hold-out set configuration
  - Dictionary with hold-out parameters
  - Default: no hold-out set

#### Hold-Out Configuration

```yaml
hold_out:
  fraction: 0.3           # Fraction to hold out (0.0-1.0)
  random_state: 42        # Random seed
  stratify: false         # Whether to stratify by target
```

- **`fraction`**: Fraction of data to hold out entirely
  - Set to `0.0` to disable hold-out
  - Hold-out data is excluded before train/validation/test split
- **`random_state`**: Random seed for reproducibility
- **`stratify`**: Whether to preserve target distribution in hold-out split
  - `true`: Stratified split (for classification)
  - `false`: Random split (default, for regression)

#### Examples

```yaml
experiments:
  # Simple experiment with single model and feature set
  house_price_prediction:
    description: "Predict house prices using Lasso"
    models: lasso
    dataset: house_prices
    target: SalePrice
    features: house_prices_all
    drop_outliers: 3.0
    metrics: r2
    hold_out:
      fraction: 0.2
      random_state: 42
      stratify: false

  # Multiple models comparison
  cgm_prediction:
    description: "Predict HbA1c from CGM data"
    models: [lasso, elasticnet, random_forest]
    dataset: cgm_combined_dataset
    target: hba1c
    features: cgm_features
    do_not_split_by: [participant_uuid]
    drop_outliers: 3.0  # Detect outliers beyond 3 standard deviations
    metrics: [r2, mse, mae]
    hold_out:
      fraction: 0.3
      random_state: 42
      stratify: false

  # Single feature set
  comprehensive_experiment:
    description: "Using a single feature set"
    models: elasticnet
    dataset: combined_dataset
    target: outcome
    features: combined_features
    drop_outliers: 3.0
    metrics: r2
    hold_out:
      fraction: 0.25
      random_state: 123
      stratify: false
```

---

## MLflow Section

The `mlflow` section configures MLflow experiment tracking for logging experiment runs, metrics, and artifacts.

### MLflow Specification

```yaml
mlflow:
  enabled: true                    # Optional (default: true)
  type: "local"                    # Optional: "local" or "databricks"
  experiment_name_prefix: "/Shared/"  # Optional (default: "")
  tags:                            # Optional (default: {})
    environment: "development"
    data_version: "v1"
```

#### Fields

- **`enabled`** (optional): Whether MLflow tracking is enabled
  - `true`: Enable MLflow tracking (default)
  - `false`: Disable MLflow tracking
  - Default: `true`

- **`type`** (optional): MLflow tracking backend type
  - `"local"`: Use local file-based tracking (default if not specified and MLFLOW_TRACKING_URI doesn't start with "databricks")
  - `"databricks"`: Use Databricks MLflow tracking
  - If not specified, inferred from `MLFLOW_TRACKING_URI` environment variable:
    - If `MLFLOW_TRACKING_URI` starts with "databricks" → `"databricks"`
    - Otherwise → `"local"`
  - Case-insensitive

- **`experiment_name_prefix`** (optional): Prefix for experiment names
  - String that will be prepended to experiment names
  - Default: `""` (no prefix)
  - Example: If prefix is `"/Shared/"` and experiment name is `"my_experiment"`, the full name becomes `"/Shared/my_experiment"`

- **`tags`** (optional): Dictionary of tags to apply to all experiment runs
  - Free-form key-value pairs
  - Default: `{}` (no tags)
  - Tags are logged with each experiment run

#### Default Behavior

If the `mlflow` section is not present in the configuration:
- `enabled`: `true`
- `type`: Inferred from `MLFLOW_TRACKING_URI` environment variable (or `"local"` if not set)
- `experiment_name_prefix`: `""`
- `tags`: `{}`

#### Examples

```yaml
# Minimal MLflow configuration (uses defaults)
mlflow:
  enabled: true

# Local MLflow tracking with tags
mlflow:
  enabled: true
  type: local
  experiment_name_prefix: "/MyProject/"
  tags:
    environment: "development"
    data_version: "v2.1"
    team: "ml-team"

# Databricks MLflow tracking
mlflow:
  enabled: true
  type: databricks
  experiment_name_prefix: "/Shared/"
  tags:
    environment: "production"
    data_version: "v3.0"

# Disable MLflow tracking
mlflow:
  enabled: false
```

#### Notes

- MLflow configuration is global and applies to all experiments in the configuration file
- Experiment names are constructed as: `{experiment_name_prefix}{experiment_name}`
- Tags are applied to all runs within experiments that use MLflow tracking
- If `enabled: false`, no MLflow logging occurs regardless of other settings

---

## Complete Example

Here's a complete configuration file demonstrating all features:

```yaml
# Include shared configurations
include:
  - snippets/datasets.yaml
  - snippets/features.yaml
  - snippets/models.yaml

# Default values for variable interpolation
defaults:
  path: "experiments"
  catalog: "pheno"
  schema: "ml"

# Dataset definitions
datasets:
  # Local CSV file
  house_prices:
    description: "House pricing prediction dataset"
    path: "{path}/house_prices.csv"
    format: CSV
    type: local

  # Databricks table
  cgm_timeseries:
    description: "CGM timeseries dataset"
    path: "{catalog}.{schema}.cgm_v2_timeseries"
    format: delta

  # Combined dataset
  cgm_combined:
    description: "CGM with metadata"
    merge_specs:
      cgm_timeseries:
        left_on: [pia_uuid, participant_uuid]
        how: inner
      cgm_metadata:
        right_on: [pia_uuid, participant_uuid]

# Feature definitions
features:
  # Explicit type specification
  house_features:
    description: "House features with explicit types"
    dataset: house_prices
    numerical:
      - YrSold
      - YearRemodAdd
      - BsmtUnfSF
    categorical:
      - HeatingQC
      - Street
      - Heating

  # Auto-inferred types
  house_features_auto:
    description: "House features with auto-inferred types"
    dataset: house_prices
    columns:
      - YrSold
      - YearRemodAdd
      - BsmtUnfSF
      - HeatingQC
      - Street

  # All columns
  all_house_features:
    description: "All house features"
    dataset: house_prices
    columns:
      - __all__

# Model definitions
models:
  lasso:
    description: "Linear regression with L1 regularization"
    type: "sklearn.linear_model.Lasso"
    params:
      alpha: 1.0
      random_state: 42
      max_iter: 100000
    tuning:
      method: "random_search"
      inner_cv: 3
      outer_cv: 3
      scoring: "neg_mean_squared_error"
      param_grid:
        alpha:
          logspace:
            start: -2
            stop: 2
            num: 50
      n_iter: 30

  elasticnet:
    description: "Linear regression with L1 and L2 regularization"
    type: "sklearn.linear_model.ElasticNet"
    params:
      alpha: 1.0
      l1_ratio: 0.5
      random_state: 42
    tuning:
      method: "grid_search"
      inner_cv: 3
      outer_cv: 3
      scoring: "neg_mean_squared_error"
      param_grid:
        alpha: [0.1, 0.5, 1.0, 5.0, 10.0]
        l1_ratio: [0.1, 0.5, 0.9]

# MLflow configuration
mlflow:
  enabled: true
  type: local
  experiment_name_prefix: "/MyProject/"
  tags:
    environment: "development"
    data_version: "v1.0"

# Experiment definitions
experiments:
  house_price_prediction:
    description: "Predict house prices"
    models: [lasso, elasticnet]
    dataset: house_prices
    target: SalePrice
    features: all_house_features
    drop_outliers: 3.0
    metrics: [r2, mse]
    hold_out:
      fraction: 0.2
      random_state: 42
      stratify: false

  cgm_hba1c_prediction:
    description: "Predict HbA1c from CGM data"
    models: lasso
    dataset: cgm_combined
    target: hba1c
    features: cgm_features
    do_not_split_by: [participant_uuid]
    drop_outliers: 3.0
    metrics: r2
    hold_out:
      fraction: 0.3
      random_state: 42
      stratify: false
```

---

## Validation Rules

The configuration is validated when loaded. Here are the key validation rules:

### Global Rules

1. **Top-level structure**: Must be a dictionary (mapping)
2. **Include paths**: Must be valid file paths (prevents circular includes)
3. **Variable interpolation**: All placeholders must have values (in strict mode)

### Datasets

1. **Primitive datasets**:
   - Must have `path` field
   - `format` and `type` are auto-inferred if missing
   - `type` must be one of: `local`, `s3`, `databricks`
   - `format` must be one of: `csv`, `txt`, `parquet`, `json`, `delta`

2. **Combined datasets**:
   - Must have `merge_specs` field
   - All referenced datasets must exist in `datasets` section
   - `how` must be one of: `inner`, `left`, `right`, `outer`, `cross`

3. **Cannot be both**: Dataset cannot have both `path` and `merge_specs`

### Features

1. **Required fields**: Must have `dataset` field
2. **Dataset reference**: Referenced dataset must exist in `datasets` section
3. **Column specification**: Must use one of:
   - `numerical` and/or `categorical` lists
   - `columns` list
   - Legacy `column` single string
4. **No overlap**: Column cannot appear in both `numerical` and `categorical`
5. **Not empty**: Must declare at least one column

### Models

1. **Required fields**: Must have `type` field
2. **Type format**: Must be a string in format `"package.module.ClassName"`
3. **Type validation**: Must be importable at runtime (checked when instantiating)
4. **Params**: If provided, must be a dictionary
5. **Tuning**: If provided, must be a dictionary

### Experiments

1. **Required fields**: Must have `models`, `dataset`, `target`, `features`
2. **Model references**: All referenced models must exist in `models` section
3. **Dataset reference**: Referenced dataset must exist in `datasets` section
4. **Feature references**: All referenced features must exist in `features` section
5. **Target**: Must be a string (single column name)
6. **Hold_out**: If provided, must be a dictionary
7. **Drop_outliers**: If provided, must be a number (float), `0.0`, or `false`

### MLflow

1. **Section**: If present, must be a mapping (dictionary)
2. **Enabled**: If provided, must be a boolean
3. **Type**: If provided, must be `"local"` or `"databricks"` (case-insensitive)
4. **Experiment_name_prefix**: If provided, must be a string
5. **Tags**: If provided, must be a mapping (dictionary)

### Cross-Section Validation

1. **Feature dataset consistency**: Features can reference any dataset (not just experiment dataset)
2. **Feature column existence**: Column existence in dataset is validated at runtime (when reading data)
3. **Target exclusion**: Target column is automatically excluded when using `__all__` features

---

## Implementation Notes

### Data Loading

- All data is loaded as pandas DataFrames (even Databricks tables are converted)
- Combined datasets are merged in-memory
- Large datasets may require significant memory

### Type Inference

- Numerical: `int64`, `int32`, `float64`, `float32`, etc.
- Categorical: `object`, `string`, `bool`, `category`
- Custom dtypes are treated based on their underlying type

### Path Resolution

- Relative paths in `path` fields are resolved relative to the current working directory
- Relative paths in `include` are resolved relative to the YAML file location
- `{variable}` placeholders are expanded before path resolution

### Model Instantiation

- Models are instantiated lazily (only when needed)
- `params` are passed as `**kwargs` to the model constructor
- `tuning` configuration is used by the experiment runner (not passed to model)

### Experiment Execution

- Experiments are not auto-executed (configuration only)
- Use the ML Workbench CLI or API to run experiments
- Results are saved separately from configuration

---

## Best Practices

1. **Organize with includes**: Split large configurations into logical files (datasets, features, models)
2. **Use descriptive names**: Make dataset, feature, and model names self-documenting
3. **Document with descriptions**: Add `description` fields to clarify intent
4. **Version control**: Track configuration files in version control
5. **Variable interpolation**: Use `defaults` for paths that change between environments
6. **Test configurations**: Validate configurations load correctly before running experiments
7. **Group features logically**: Create feature sets that make sense together
8. **Specify random_state**: Always set `random_state` for reproducibility
9. **Use do_not_split_by**: Prevent data leakage with proper grouping (e.g., by participant)
10. **Start simple**: Begin with single models and feature sets, then expand

---

## Error Messages

Common errors and their meanings:

- **"Circular include detected"**: Include chain loops back to an already-included file
- **"Missing values for placeholders"**: Variable used in `{placeholder}` but not defined in `defaults` or arguments
- **"Dataset 'X' not found"**: Referenced dataset doesn't exist in `datasets` section
- **"Feature 'X' references unknown dataset 'Y'"**: Feature references non-existent dataset
- **"Experiment 'X' references unknown model 'Y'"**: Experiment references non-existent model
- **"Column 'X' is not declared in feature set 'Y'"**: Attempting to use undeclared column
- **"Feature 'X' declares columns in both numerical and categorical"**: Overlap between type lists
- **"Model 'X' is missing required 'type' string field"**: Model missing required type field
- **"Unsupported dataset type"**: Dataset type not in: `local`, `s3`, `databricks`
- **"Unsupported format"**: Dataset format not supported for given type
- **"mlflow.enabled must be a boolean"**: MLflow enabled field must be true or false
- **"mlflow.type must be 'local' or 'databricks'"**: Invalid MLflow type specified
- **"mlflow.experiment_name_prefix must be a string"**: Invalid prefix type
- **"mlflow.tags must be a mapping"**: Tags must be a dictionary

---

*This specification is based on ML Workbench v1.0*

