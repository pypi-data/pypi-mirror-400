# ML Workbench Examples

This directory contains example scripts demonstrating how to use the ML Workbench.

## Available Examples

### run_house_experiment.py

Demonstrates the complete workflow for running ML experiments:

- Loading experiment configurations from YAML
- Creating and executing experiments with the Runner class
- Accessing and displaying results
- MLFlow integration for experiment tracking

**Usage:**

```bash
# Make sure you're in the project root
cd /path/to/ml_workbench

# Run with uv
uv run python examples/run_house_experiment.py

# Or activate the virtual environment and run directly
source .venv/bin/activate
python examples/run_house_experiment.py
```

**Prerequisites:**

The house prices dataset must be present at `experiments/house_prices.csv`. You can download it from sklearn:

```python
from sklearn.datasets import fetch_openml
import pandas as pd

house_prices = fetch_openml(name='house_prices', as_frame=True)
df = house_prices.frame
df.to_csv('experiments/house_prices.csv', index=False)
```

## Runner Class Overview

The `Runner` class orchestrates the complete ML experiment workflow:

1. **Load Dataset** - Reads data from configured sources (local files, S3, Databricks)
2. **Build Pipeline** - Creates preprocessing pipelines for numerical and categorical features
3. **Split Data** - Handles train/validation/test splits with support for grouped splitting
4. **Train Model** - Trains the specified model(s) with configured hyperparameters
5. **Evaluate** - Calculates metrics on the test set
6. **Feature Weights** - Extracts feature importances or coefficients
7. **MLFlow Logging** - Tracks all experiments, parameters, metrics, and artifacts

### Basic Usage

```python
from ml_workbench import YamlConfig, Experiment, Runner

# Load configuration
config = YamlConfig("path/to/config.yaml")

# Create experiment
experiment = Experiment("experiment_name", config)

# Run experiment
runner = Runner(experiment, verbose=True)
results = runner.run()

# Access results
for model_name, model_results in results.items():
    print(f"Model: {model_name}")
    print(f"Metrics: {model_results['metrics']}")
    print(f"Feature weights: {model_results['feature_weights']}")
```

### Advanced Features

#### Custom Data Splits

The Runner respects all split configurations from your YAML:

```yaml
split:
  test_size: 0.2
  validation_size: 0.1
  random_state: 42
```

#### Grouped Splitting (Prevent Data Leakage)

Use `do_not_split_by` to keep related samples together:

```yaml
do_not_split_by: [participant_uuid]
```

#### Hold-Out Sets

Create separate hold-out sets for final validation:

```yaml
hold_out:
  fraction: 0.3
  random_state: 42
```

#### MLFlow Integration

Results are automatically logged to MLFlow including:
- Model parameters
- Training/validation/test metrics
- Data split sizes
- Feature weights/importances
- Trained model artifacts

View results with:
```bash
mlflow ui
```

## Configuration Files

Experiment configurations are defined in YAML files with the following structure:

```yaml
datasets:
  my_dataset:
    path: "path/to/data.csv"
    format: csv
    type: local

features:
  my_features:
    dataset: my_dataset
    numerical: [col1, col2]
    categorical: [col3, col4]

models:
  my_model:
    type: "sklearn.linear_model.Lasso"
    params:
      alpha: 1.0
      random_state: 42

experiments:
  my_experiment:
    dataset: my_dataset
    target: target_column
    features: [my_features]
    models: [my_model]
    metrics: [r2, mse]
    split:
      test_size: 0.2
      validation_size: 0.1
      random_state: 42
```

See `experiments/house_experiment.yaml` for a complete example.

