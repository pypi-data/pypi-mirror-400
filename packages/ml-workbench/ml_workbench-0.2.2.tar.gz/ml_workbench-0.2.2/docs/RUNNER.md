# Runner Class Documentation

## Overview

The `Runner` class is the execution engine for ML experiments in the ML Workbench. It orchestrates the complete machine learning workflow from data loading to model training and evaluation, with built-in MLFlow experiment tracking.

## Features

### Core Capabilities

1. **Dataset Management**
   - Loads datasets from various sources (local files, S3, Databricks)
   - Supports combined datasets with merge specifications
   - Automatic type inference for features

2. **Data Preprocessing**
   - Automatic pipeline creation for numerical and categorical features
   - Numerical: imputation + standardization
   - Categorical: imputation + one-hot encoding
   - Type inference when specifications are not provided

3. **Data Splitting**
   - Training and holdout splits
   - Grouped splitting to prevent data leakage (`do_not_split_by`)
   - Hold-out sets for final validation

4. **Model Training**
   - Supports any scikit-learn compatible model
   - Full pipeline integration (preprocessing + model)
   - Configurable hyperparameters from YAML

5. **Model Evaluation**
   - Multiple metrics: r2, mse, rmse, mae, accuracy, precision, recall, f1
   - Holdout set evaluation
   - Per-model performance tracking

6. **Feature Analysis**
   - Extracts feature importances (tree-based models)
   - Extracts coefficients (linear models)
   - Ranks features by importance/magnitude

7. **Experiment Tracking**
   - Full MLFlow integration
   - Logs parameters, metrics, and artifacts
   - Tracks data split sizes
   - Saves trained models
   - Records feature weights

## Quick Start

### 1. Create an Experiment Configuration (YAML)

```yaml
# my_experiment.yaml
datasets:
  my_data:
    path: "data/my_data.csv"
    format: csv
    type: local

features:
  my_features:
    dataset: my_data
    numerical: [age, income]
    categorical: [gender, region]

models:
  my_model:
    type: "sklearn.linear_model.LassoCV"
    params:
      random_state: 42
      max_iter: 10000

experiments:
  my_experiment:
    dataset: my_data
    target: target_column
    features: [my_features]
    models: [my_model]
    metrics: [r2, mse]
    hold_out:
      fraction: 0.3
      random_state: 42
```

### 2. Run Your Experiment

```python
from ml_workbench import YamlConfig, Experiment, Runner

# Load configuration
config = YamlConfig("my_experiment.yaml")

# Create experiment (name is optional - uses first experiment if not specified)
experiment = Experiment(config, "my_experiment")
# or simply:
# experiment = Experiment(config)  # Uses first experiment

# Run experiment
runner = Runner(experiment, verbose=True)
results = runner.run()

# View results
print(f"Best model : {results['best_model']}")
print(f"Best model score : {results['best_model_score']}")
for model_name, model_results in results.items():
    print(f"\nModel: {model_name}")
    print(f"R² Score: {model_results['metrics']['r2']:.4f}")
    print(f"MSE: {model_results['metrics']['mse']:.4f}")
    print("\nTop 5 Features:")
    print(model_results['feature_weights'].head())
```

### 3. View in MLFlow

```bash
mlflow ui
# Open http://localhost:5000 in your browser
```

## Usage

### Basic Example

```python
from ml_workbench import YamlConfig, Experiment, Runner

# Load configuration
config = YamlConfig("experiments/my_experiment.yaml")

# Create experiment
experiment = Experiment(config, "my_experiment_name")

# Create and run
runner = Runner(experiment, verbose=True)
results = runner.run()

# Access results
print(f"Best model : {results['best_model']}")
print(f"Best model score : {results['best_model_score']}")

for model_name, metrics in results['models'].items():
    print(f"\nModel: {model_name}")
    for k, v in metrics.items():
        if k.startswith("train_") or k.startswith("holdout_") or k in ["r2", "mse", "mae", "rmse"]:
            print(f"{k}: {v:.4f}")

### Step-by-Step Execution

For more control, you can execute each step individually:

```python
# Initialize runner
runner = Runner(experiment, verbose=True)

# Prepare data (loads dataset, prepares features, and splits data)
runner.data_preparation()
print(f"Loaded {len(runner.dataset)} rows")
print(f"Numerical features: {runner.numerical_features}")
print(f"Categorical features: {runner.categorical_features}")
print(f"Train: {len(runner.X_train)}")
if runner.X_holdout is not None:
    print(f"Holdout: {len(runner.X_holdout)}")

# Run the complete experiment
results = runner.run()

# Access results
print(f"Best model : {results['best_model']}")
print(f"Best model score : {results['best_model_score']}")

for model_name, metrics in results['models'].items():
    print(f"\nModel: {model_name}")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

```

## Configuration Syntax

### Experiment YAML Structure

```yaml
experiments:
  my_experiment:
    description: "Experiment description"
    models: [model1, model2]        # One or more models
    dataset: my_dataset              # Dataset name
    target: target_column            # Target variable
    features: feature_set1          # Single feature set or list
    metrics: [r2, mse, mae]         # Evaluation metrics
    do_not_split_by: [group_id]     # Optional: grouped splitting
    drop_outliers:  3.0             # Optional: outlier removal before splitting
    hold_out:                        # Optional: hold-out set
      fraction: 0.3
      random_state: 42
```

### Data Splitting Options

#### Basic Split (No Holdout)

By default, all data is used for training:

```python
runner.data_preparation()
# All data is in runner.X_train
```

#### With Hold-Out Set

```yaml
hold_out:
  fraction: 0.3           # 30% held out entirely
  random_state: 42
```

This results in:
- Hold-out: 30% of total data (for final validation)
- Training: 70% of total data

#### Grouped Splitting (Prevent Data Leakage)

```yaml
do_not_split_by: [participant_id]
hold_out:
  fraction: 0.3
  random_state: 42
```

Ensures all samples from the same participant stay in the same split (either training or holdout).

### Feature Handling

#### Explicit Type Specification

```yaml
features:
  my_features:
    dataset: my_dataset
    numerical: [age, income, score]
    categorical: [gender, region, category]
```

#### Automatic Type Inference

```yaml
features:
  my_features:
    dataset: my_dataset
    columns: [age, gender, income, region]
    # Types inferred from DataFrame dtypes
```

#### All Columns

```yaml
features:
  all_features:
    dataset: my_dataset
    columns: [__all__]
    # Uses all columns except target
```

### Model Configuration

```yaml
models:
  my_model:
    type: "sklearn.linear_model.LassoCV"  # Full import path
    params:
      random_state: 42
      max_iter: 10000
```

## Common Use Cases

### Basic Regression

```yaml
experiments:
  my_regression:
    dataset: sales_data
    target: sales
    features: [all_features]
    models: [linear_model]
    metrics: [r2, mse, mae]
```

### Classification

```yaml
experiments:
  my_classification:
    dataset: user_data
    target: churned
    features: [user_features]
    models: [random_forest]
    metrics: [accuracy, f1, precision, recall]
```

### Time Series (Grouped Splitting)

```yaml
experiments:
  time_series_exp:
    dataset: sensor_data
    target: reading
    features: [sensor_features]
    models: [gradient_boosting]
    metrics: [r2, mae]
    do_not_split_by: [device_id]  # Keep all data from same device together
```

### Multiple Models

```yaml
experiments:
  model_comparison:
    dataset: my_data
    target: outcome
    features: [all_features]
    models: [lasso, ridge, elasticnet, random_forest]  # Compare multiple models
    metrics: [r2, mse]
```

### Hold-Out Set Configuration

```yaml
experiments:
  with_holdout:
    # ... other config ...
    hold_out:
      fraction: 0.3        # Set aside 30% for final validation
      random_state: 42
```

## Metrics

### Regression Metrics

- **r2**: R² (coefficient of determination)
- **mse**: Mean Squared Error
- **rmse**: Root Mean Squared Error
- **mae**: Mean Absolute Error

### Classification Metrics

- **accuracy**: Classification accuracy
- **precision**: Precision (weighted average for multi-class)
- **recall**: Recall (weighted average for multi-class)
- **f1**: F1 Score (weighted average for multi-class)

### Configuration

```yaml
experiments:
  my_experiment:
    # ... other config ...
    metrics: [r2, mse, mae]  # Multiple metrics
    # or
    metrics: r2              # Single metric
```

## MLFlow Integration

### Automatic Logging

The Runner automatically logs to MLFlow (if installed):

1. **Parameters**
   - Model name and type
   - Dataset name
   - Target variable
   - Feature sets
   - Split configuration
   - Model hyperparameters

2. **Metrics**
   - All configured evaluation metrics
   - Data split sizes (train/holdout)

3. **Artifacts**
   - Trained model (full pipeline)
   - Feature weights CSV
   - Additional model artifacts

### Viewing Results

```bash
# Start MLFlow UI
mlflow ui

# Access at http://localhost:5000
```

### Custom MLFlow Configuration

Set MLFlow environment variables before running:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_EXPERIMENT_NAME=my_experiment
```

### Databricks MLFlow

When running on Databricks, MLFlow is automatically configured:

```python
# No additional configuration needed
runner = Runner(experiment)
results = runner.run()
# Results automatically logged to Databricks MLFlow
```

## Advanced Usage

### Accessing Trained Models

```python
results = runner.run()

# Get the best model runner
best_model_runner = runner.get_best_model()

# Or get a specific model runner
model_runners = runner.get_models()
my_model_runner = next(mr for mr in model_runners if mr.model_name == 'my_model')

# Make predictions using ModelRunner
predictions = my_model_runner.predict(new_data)

# Access the trained pipeline
best_pipeline = best_model_runner.best_pipeline

# Access underlying model
underlying_model = best_pipeline.named_steps['model']
```

### Accessing Metrics

```python
results = runner.run()

# Access metrics for all models
for model_name, metrics in results['models'].items():
    print(f"{model_name}:")
    print(f"  Train R²: {metrics.get('train_r2_score', 'N/A')}")
    print(f"  Holdout R²: {metrics.get('holdout_r2_score', 'N/A')}")

# Access best model information
print(f"Best model: {results['best_model']}")
print(f"Best model score: {results['best_model_score']}")
```

### Custom Evaluation

```python
runner.data_preparation()  # Prepare data first
results = runner.run()  # Run the experiment

# Get model runner for custom evaluation
model_runner = runner.get_best_model()

# Custom evaluation on holdout set
from sklearn.metrics import mean_absolute_percentage_error

if runner.X_holdout is not None:
    y_pred = model_runner.predict(runner.X_holdout)
    mape = mean_absolute_percentage_error(runner.y_holdout, y_pred)
    print(f"MAPE: {mape:.4f}")
```

### Feature Analysis

```python
results = runner.run()

# Get feature weights for the best model
best_model_runner = runner.get_best_model()
feature_weights = best_model_runner._calculate_feature_weights()
print(feature_weights.head(10))

# Plot feature weights
fig = best_model_runner.plot_feature_weights()
if fig:
    fig.savefig('feature_weights.png')
```

### Visualization

```python
results = runner.run()
model_runner = runner.get_best_model()

# For regression: plot actual vs predicted and residuals
if runner.y_holdout is not None:
    y_pred = model_runner.predict(runner.X_holdout)
    fig = model_runner.plot_regression(runner.y_holdout, y_pred, title_prefix='holdout')
    if fig:
        fig.savefig('regression_plots.png')

# For classification: plot confusion matrix
if runner.y_holdout is not None:
    y_pred = model_runner.predict(runner.X_holdout)
    fig = model_runner.plot_confusion_matrix(runner.y_holdout, y_pred, title_prefix='holdout')
    if fig:
        fig.savefig('confusion_matrix.png')

# Plot cross-validation results (if tuning was performed)
if model_runner.is_cross_validation:
    fig = model_runner.plot_cv_mean_score()
    if fig:
        fig.savefig('cv_results.png')
```

### Saving and Loading Prepared Data

```python
# Save prepared dataset
runner.data_preparation()
filepath = runner.data_save('my_experiment_data.parquet')

# Later, load the saved dataset
runner2 = Runner(experiment)
runner2.data_load('my_experiment_data.parquet')
results = runner2.run()  # Continue with training
```

## API Reference

### Runner Class

#### Runner.__init__(experiment, verbose=True)

Initialize Runner with an Experiment object.

**Parameters:**
- `experiment` (Experiment): Experiment specification
- `verbose` (bool, optional): Whether to print progress information. Defaults to True.

#### Runner.data_preparation() -> None

Prepare data for the experiment. This method performs:
1. Load dataset
2. Prepare features (classify as numerical/categorical)
3. Drop outliers (if `drop_outliers` is configured)
4. Split data into train/holdout sets

This is the recommended way to prepare data. The individual steps (`_load_dataset`, `_prepare_features`, `_drop_outliers`, `_split_data`) are private methods and should not be called directly.

#### Runner.data_save(filepath=None) -> str

Save the prepared dataset to a parquet file.

**Parameters:**
- `filepath` (str, optional): Path where to save the parquet file. If None, generates a default filename based on experiment name.

**Returns:**
- `str`: Path to the saved parquet file

**Raises:**
- `RuntimeError`: If dataset is None (not loaded yet)

#### Runner.data_load(filepath) -> None

Load dataset from parquet file, prepare features, and split based on `is_holdout` column.

This method loads a previously saved dataset (from `data_save()`), prepares features, and recreates the train/holdout splits based on the `is_holdout` column.

**Parameters:**
- `filepath` (str): Path to the parquet file to load

**Raises:**
- `FileNotFoundError`: If the parquet file doesn't exist
- `ValueError`: If required columns (target, is_holdout) are missing from the loaded dataset

#### Runner.get_config() -> dict[str, Any]

Return dictionary similar to original YAML config with all fields populated.

Includes inferred feature types (numerical/categorical) and experiment type (regression/classification). The returned dictionary has the same structure as the original YAML configuration file.

**Returns:**
- `dict[str, Any]`: Dictionary with same structure as YAML config, with inferred fields populated. Includes:
  - All original config sections (datasets, features, models, experiments, etc.)
  - Inferred experiment type in experiments section
  - Inferred feature types (numerical/categorical) in features section

**Raises:**
- `RuntimeError`: If features have not been prepared yet (need to call `data_preparation()` or `run()` first)

#### Runner.get_models() -> list[ModelRunner]

Get list of ModelRunner instances for all models in the experiment.

**Returns:**
- `list[ModelRunner]`: List of ModelRunner instances

#### Runner.get_best_model() -> ModelRunner | None

Get the best performing model runner based on selection score.

**Returns:**
- `ModelRunner | None`: Best model runner, or None if no models have been trained yet

#### Runner.get_best_model_score() -> float

Get the selection score of the best model.

**Returns:**
- `float`: Selection score of the best model

#### Runner.run() -> dict[str, Any]

Execute complete experiment workflow.

**Returns:**
- `dict[str, Any]`: Results dictionary containing:
  - `models` (dict): Dictionary mapping model names to their metrics dictionaries. Each metrics dictionary contains:
    - `train_*` metrics: Metrics evaluated on training set (e.g., `train_r2_score`, `train_mean_squared_error`)
    - `holdout_*` metrics: Metrics evaluated on holdout set (e.g., `holdout_r2_score`, `holdout_mean_squared_error`)
    - `selection_score`: Score used to select the best model (based on first metric in metrics list)
  - `best_model` (str): Name of the best performing model
  - `best_model_score` (float): Selection score of the best model

**Note:** The selection score is based on the first metric in the experiment's metrics list. Higher scores are better for metrics like R², while lower scores are better for metrics like MSE (the score is negated for minimization metrics).

### ModelRunner Class

The `ModelRunner` class handles training, evaluation, and analysis for individual models. Instances are created automatically by `Runner.run()`.

#### ModelRunner.fit_and_evaluate() -> float

Train the model and evaluate it. This method:
- Creates the preprocessing and model pipeline
- Performs cross-validation hyperparameter search if tuning is configured
- Fits the model (or best tuned model) on training data
- Evaluates on training and holdout sets
- Calculates feature weights

**Returns:**
- `float`: Selection score of the model (used to select the best model)

#### ModelRunner.predict(X) -> np.ndarray

Make predictions using the best trained pipeline.

**Parameters:**
- `X` (pd.DataFrame | np.ndarray): Input features for prediction

**Returns:**
- `np.ndarray`: Predicted outputs

**Raises:**
- `RuntimeError`: If the model pipeline is not trained yet

#### ModelRunner._calculate_feature_weights() -> pd.DataFrame

Calculate feature importances or coefficients from the trained model.

**Returns:**
- `pd.DataFrame`: DataFrame with columns:
  - `feature`: Feature names
  - `weight`: Feature weights/importances/coefficients
  - `type`: Type of weight ("coefficient" for linear models, "importance" for tree-based models)

#### ModelRunner.plot_feature_weights() -> matplotlib.figure.Figure | None

Plot feature importances or coefficients from the best estimator.

**Returns:**
- `matplotlib.figure.Figure | None`: The figure object, or None if no feature weights are available

#### ModelRunner.plot_cv_mean_score(figsize=(10, 10)) -> matplotlib.figure.Figure | None

Plot mean test score across CV splits with confidence intervals (std error).

**Parameters:**
- `figsize` (tuple, optional): Figure size. Defaults to (10, 10).

**Returns:**
- `matplotlib.figure.Figure | None`: The figure object, or None if no CV results are available

#### ModelRunner.plot_confusion_matrix(y_true, y_pred, title_prefix=None) -> matplotlib.figure.Figure | None

Create confusion matrix plot for classification.

**Parameters:**
- `y_true` (pd.Series | np.ndarray): True target values
- `y_pred` (pd.Series | np.ndarray): Predicted values
- `title_prefix` (str, optional): Prefix to add to plot title (e.g., 'holdout data', 'test data')

**Returns:**
- `matplotlib.figure.Figure | None`: Matplotlib figure object with confusion matrix plot, or None if error occurs

#### ModelRunner.plot_regression(y_true, y_pred, title_prefix=None) -> matplotlib.figure.Figure | None

Create actual vs predicted and residuals vs predicted plots for regression.

**Parameters:**
- `y_true` (pd.Series | np.ndarray): True target values
- `y_pred` (pd.Series | np.ndarray): Predicted values
- `title_prefix` (str, optional): Prefix to add to plot titles

**Returns:**
- `matplotlib.figure.Figure | None`: Matplotlib figure object with two subplots, or None if error occurs

#### ModelRunner.plot_distribution(y_true, y_pred, title_prefix=None) -> matplotlib.figure.Figure | None

Plot the distribution (KDE) of actual and predicted values.

**Parameters:**
- `y_true` (pd.Series | np.ndarray): True target values
- `y_pred` (pd.Series | np.ndarray): Predicted values
- `title_prefix` (str, optional): Optional prefix for the plot title

**Returns:**
- `matplotlib.figure.Figure | None`: The figure object, or None if an error occurs

## Examples

### Working Example

A complete working example is provided with the house prices dataset:

```bash
# Run the house prices example
uv run python examples/run_house_experiment.py

# This will:
# 1. Load the house prices dataset (1460 rows, 81 columns)
# 2. Build preprocessing pipeline (20 features total)
# 3. Split data (train/validation/test)
# 4. Train a Lasso regression model
# 5. Evaluate on test set (R² ~0.80)
# 6. Extract feature weights
# 7. Log everything to MLFlow
```

### Example Output

```
[Runner] Starting experiment: my_experiment
[Runner] Loading dataset: my_data
[Runner] Dataset loaded: 1000 rows, 15 columns
[Runner] Building preprocessing pipeline
[Runner] Numerical features (2): ['age', 'income']
[Runner] Categorical features (2): ['gender', 'region']
[Runner] Splitting data
[Runner] Train set size: 720
[Runner] Holdout set size: 280
[Runner] Training model: my_model
[Runner] Model training completed: my_model
[Runner] Evaluating model on test set
[Runner]   r2: 0.842156
[Runner]   mse: 123.456789
[Runner] Calculating feature weights
[Runner] Top 5 features by coefficient:
[Runner]   income: 12.345678
[Runner]   age: 5.678901
[Runner] Logging to MLFlow
[Runner] MLFlow run completed: abc123...
[Runner] Experiment completed successfully!
```

## Best Practices

### 1. Always Set Random State

```yaml
hold_out:
  fraction: 0.3
  random_state: 42  # For reproducibility
```

### 2. Use Grouped Splitting When Needed

```yaml
# For time series or grouped data
do_not_split_by: [participant_id, session_id]
```

### 3. Validate Hold-Out Sets Separately

```python
results = runner.run()

# Access holdout metrics from results
for model_name, metrics in results['models'].items():
    if 'holdout_r2_score' in metrics:
        print(f"{model_name} Hold-out R²: {metrics['holdout_r2_score']:.4f}")

# Or use the best model runner for custom evaluation
if runner.X_holdout is not None:
    best_model_runner = runner.get_best_model()
    holdout_pred = best_model_runner.predict(runner.X_holdout)
    from sklearn.metrics import r2_score
    holdout_score = r2_score(runner.y_holdout, holdout_pred)
    print(f"Best model Hold-out R²: {holdout_score:.4f}")
```

### 4. Track Multiple Metrics

```yaml
metrics: [r2, mse, mae, rmse]  # Get comprehensive evaluation
```

### 5. Document Experiments

```yaml
experiments:
  my_experiment:
    description: >
      Detailed description of what this experiment tests,
      why it's important, and what we expect to learn.
```

## Troubleshooting

### MLFlow Not Logging

Check if MLFlow is installed:
```bash
uv add mlflow
# or
pip install mlflow
```

Verify MLFlow tracking URI:
```python
import mlflow
print(mlflow.get_tracking_uri())
```

### Feature Type Inference Issues

Explicitly specify feature types:
```yaml
features:
  my_features:
    numerical: [col1, col2]
    categorical: [col3, col4]
    # Don't rely on automatic inference
```

### Common Errors

1. **Missing Target Column**
```python
ValueError: Target column 'target_name' not found in dataset
```
**Solution**: Verify target column name in dataset

2. **No Features Specified**
```python
ValueError: No features to process
```
**Solution**: Add feature specifications in YAML

3. **Model Import Error**
```python
ImportError: No module named 'sklearn.linear_model'
```
**Solution**: Verify model type in YAML configuration (must be full import path)

4. **Insufficient Data**
```python
ValueError: Not enough samples for split
```
**Solution**: Reduce hold_out fraction or ensure sufficient data

### Graceful Degradation

- If MLFlow is not installed, Runner logs a warning and continues
- If a metric is unknown, Runner logs a warning and skips it
- If feature weights cannot be extracted, returns empty DataFrame

## Supported Models

Any scikit-learn compatible model:
- Linear models (Lasso, Ridge, ElasticNet)
- Tree models (RandomForest, GradientBoosting)
- SVM models
- Neural networks (MLPRegressor, MLPClassifier)
- And many more!

## Performance

Tested performance on house prices dataset:
- **Dataset**: 1,460 rows × 81 columns
- **Features**: 10 numerical + 10 categorical
- **Runtime**: ~2 seconds (training + evaluation)
- **With MLFlow**: ~5 seconds (includes logging)

### Performance Considerations

- Preprocessing is done once and cached in the pipeline
- Multiple models reuse the same preprocessed data splits
- Feature transformations are parallelized when possible

When running on Databricks:
- Use Delta format for datasets
- Enable caching for intermediate results
- Use distributed computing for large-scale experiments

## Future Enhancements

Planned improvements:
- [ ] Support for custom preprocessing functions
- [X] Hyperparameter tuning integration
- [X] Cross-validation support
- [ ] Ensemble model support
- [ ] Automated feature selection
- [ ] Model comparison reports
- [ ] Prediction interval estimates
- [ ] SHAP value integration
