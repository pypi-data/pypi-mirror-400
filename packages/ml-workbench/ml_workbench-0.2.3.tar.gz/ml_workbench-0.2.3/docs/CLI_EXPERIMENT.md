# CLI Experiment - Command Line Interface for Running Experiments

## Overview

The `cli-experiment` command provides a command-line interface for running YAML-defined ML experiments. It allows you to execute one or more experiments from a configuration file without writing Python code.

## Installation

The CLI command is automatically available after installing the package:

```bash
# Install the package
uv sync

# Verify installation
cli-experiment --help
```

## Basic Usage

### Run All Experiments

By default, the CLI runs all experiments defined in the YAML file:

```bash
cli-experiment experiment.yaml
```

### Run Specific Experiment(s)

Use the `--experiments` flag to run one or more specific experiments:

```bash
# Run a single experiment
cli-experiment experiment.yaml --experiments house_prices_prediction_simple

# Run multiple experiments
cli-experiment experiment.yaml --experiments exp1 exp2 exp3
```

### Variable Substitution

Use the `--var` flag to provide variable values for interpolation in the YAML file:

```bash
# Single variable
cli-experiment experiment.yaml --var path=/data/datasets

# Multiple variables
cli-experiment experiment.yaml --var path=/data --var env=production --var catalog=prod
```

### Quiet Mode

Suppress verbose output from the Runner:

```bash
cli-experiment experiment.yaml --quiet
```

## Inspection Modes

The CLI provides inspection options that allow you to view configuration and dataset information **without running experiments**.

### Inspect Configuration

View the processed configuration:

```bash
# Show full configuration
cli-experiment experiment.yaml --show-config

# Show as JSON
cli-experiment experiment.yaml --show-config --json

# Show specific sections
cli-experiment experiment.yaml --show-config --section experiments --section datasets

# Show resolved variables
cli-experiment experiment.yaml --show-config --show-variables
```

### Inspect Datasets

View dataset statistics:

```bash
# Show dataset statistics
cli-experiment experiment.yaml --show-datasets

# Show as JSON
cli-experiment experiment.yaml --show-datasets --json
```

**Note:** When using `--show-config` or `--show-datasets`, experiments are **not run**. These are inspection-only modes.

## Command Syntax

```
cli-experiment YAML_FILE [OPTIONS]
```

### Required Arguments

- `YAML_FILE` - Path to the YAML configuration file containing experiment definitions

### Optional Arguments

**Experiment Execution:**
- `--experiments EXPERIMENT [EXPERIMENT ...]` - Name(s) of experiment(s) to run. Can be specified multiple times. If not specified, all experiments in the YAML will be run. Ignored if `--show-config` or `--show-datasets` is used.
- `--var KEY=VALUE` - Variable for interpolation in the YAML file. Can be specified multiple times.
- `--quiet` - Suppress verbose output from Runner

**Inspection Options (mutually exclusive with running experiments):**
- `--show-config` - Show processed configuration. When used, experiments are not run.
- `--show-datasets` - Show dataset statistics. When used, experiments are not run.
- `--json` - Output as JSON instead of YAML/text (used with `--show-config` or `--show-datasets`)
- `--section SECTION` - Output only specific section(s) when using `--show-config` (can be specified multiple times)
- `--show-variables` - Show resolved variables when using `--show-config`

- `--help` - Show help message and exit

## Examples

### Example 1: Run All Experiments

```bash
cli-experiment examples/house_experiment.yaml
```

This will run both `house_prices_prediction_simple` and `house_prices_prediction_all` experiments.

### Example 2: Run Single Experiment

```bash
cli-experiment examples/house_experiment.yaml --experiments house_prices_prediction_simple
```

This runs only the `house_prices_prediction_simple` experiment.

### Example 3: Run Multiple Experiments

```bash
cli-experiment examples/house_experiment.yaml \
  --experiments house_prices_prediction_simple \
  --experiments house_prices_prediction_all
```

Or more concisely:

```bash
cli-experiment examples/house_experiment.yaml \
  --experiments house_prices_prediction_simple house_prices_prediction_all
```

### Example 4: With Variable Substitution

```yaml
# experiment.yaml
defaults:
  data_path: "{base_path}/data"

datasets:
  my_data:
    path: "{data_path}/dataset.csv"
    format: CSV
    type: local
```

```bash
cli-experiment experiment.yaml --var base_path=/home/user/project
```

### Example 5: Combined Options

```bash
cli-experiment experiment.yaml \
  --experiments exp1 exp2 \
  --var path=/data \
  --var env=production \
  --quiet
```

### Example 6: Inspect Configuration

```bash
# View full processed configuration
cli-experiment experiment.yaml --show-config

# View only experiments section
cli-experiment experiment.yaml --show-config --section experiments

# View as JSON with resolved variables
cli-experiment experiment.yaml --show-config --json --show-variables
```

### Example 7: Inspect Datasets

```bash
# View dataset statistics
cli-experiment experiment.yaml --show-datasets

# View as JSON
cli-experiment experiment.yaml --show-datasets --json
```

## YAML Configuration Format

The YAML file must contain an `experiments` section with experiment definitions. Each experiment should reference datasets, features, and models defined in the same file.

### Minimal Example

```yaml
datasets:
  my_data:
    path: "data.csv"
    format: CSV
    type: local

features:
  my_features:
    dataset: my_data
    numerical: [col1, col2]
    categorical: [col3]

models:
  my_model:
    type: "sklearn.linear_model.LassoCV"
    params:
      random_state: 42

experiments:
  my_experiment:
    description: "My first experiment"
    dataset: my_data
    target: target_column
    features: my_features
    models: [my_model]
    metrics: [r2, mse]
    hold_out:
      fraction: 0.3  
      random_state: 42
```

See `docs/SPECIFICATION.md` for complete YAML configuration documentation.

## Error Handling

### Missing YAML File

```bash
$ cli-experiment nonexistent.yaml
Error: YAML file not found: nonexistent.yaml
```

### No Experiments Found

```bash
$ cli-experiment empty.yaml
Error: No experiments found in configuration file
```

### Invalid Experiment Name

```bash
$ cli-experiment experiment.yaml --experiments invalid_exp
Error: Experiment(s) not found: invalid_exp
Available experiments: exp1, exp2, exp3
```

### Configuration Validation Errors

The CLI validates the configuration before running experiments:

```bash
$ cli-experiment invalid_config.yaml
Error: Configuration validation failed: Experiment 'exp1' references unknown dataset 'missing_dataset'
```

### Invalid Variable Format

```bash
$ cli-experiment experiment.yaml --var invalid_format
Error: Invalid variable format 'invalid_format', expected key=value
```

## Exit Codes

- `0` - Success (all experiments completed successfully)
- `1` - Error (file not found, validation error, or experiment execution error)
- `130` - Interrupted by user (Ctrl+C)

## Integration with MLFlow

The CLI automatically logs experiment results to MLFlow if available. To view results:

```bash
# Start MLFlow UI
mlflow ui

# Open http://localhost:5000 in your browser
```

## Comparison with Python API

The CLI provides the same functionality as the Python API but is more convenient for command-line usage:

### Python API

```python
from ml_workbench import YamlConfig, Experiment, Runner

config = YamlConfig("experiment.yaml")
experiment = Experiment("my_experiment", config)
runner = Runner(experiment, verbose=True)
results = runner.run()
```

### CLI Equivalent

```bash
cli-experiment experiment.yaml --experiments my_experiment
```

## Best Practices

1. **Use descriptive experiment names** - Makes it easier to identify experiments in MLFlow
2. **Validate YAML before running** - Use `--show-config` to inspect your YAML file first
3. **Use variables for paths** - Makes configurations portable across environments
4. **Run experiments individually first** - Test single experiments before running all
5. **Check MLFlow UI** - Review logged results after execution

## Troubleshooting

### Command Not Found

If `cli-experiment` is not found, ensure the package is installed:

```bash
uv sync
```

### Import Errors

If you see import errors, check that all dependencies are installed:

```bash
uv sync --all-groups
```

### MLFlow Not Logging

MLFlow logging is optional. If you want MLFlow support:

```bash
uv add mlflow
```

### Verbose Output Too Noisy

Use `--quiet` flag to suppress Runner output:

```bash
cli-experiment experiment.yaml --quiet
```

## See Also

- `docs/RUNNER.md` - Detailed Runner documentation
- `docs/SPECIFICATION.md` - Complete YAML specification
- `examples/run_house_experiment.py` - Python API example
- `examples/house_experiment.yaml` - Example experiment configuration

