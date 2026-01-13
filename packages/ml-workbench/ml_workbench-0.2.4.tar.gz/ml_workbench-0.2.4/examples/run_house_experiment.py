#!/usr/bin/env python3
"""Example script demonstrating how to use the Runner class to execute ML experiments.

This script shows how to:
1. Load an experiment configuration from YAML
2. Create an Experiment object
3. Execute the experiment using the Runner
4. Access and display results
"""

from pathlib import Path

import mlflow
from dotenv import load_dotenv

from ml_workbench import Experiment, Runner, YamlConfig

load_dotenv()

# Configure MLflow to use Databricks
mlflow.set_tracking_uri("databricks")


def main():
    """Run the house prices prediction experiment."""
    # Path to the experiment configuration
    config_path = Path(__file__).parent.parent / "examples" / "house_experiment.yaml"

    print("=" * 80)
    print("ML Workbench - House Price Prediction Experiment")
    print(f"MLFlow tracking URI: {mlflow.get_tracking_uri()}")
    print("=" * 80)
    print()

    # Load configuration
    print(f"Loading configuration from: {config_path}")
    config = YamlConfig(config_path)
    print("✓ Configuration loaded successfully")
    print()

    # List available experiments
    experiment_names = Experiment.list_experiment_names(config)
    print(f"Available experiments: {', '.join(experiment_names)}")
    print()

    # Select experiment to run
    experiment_name = (
        "house_prices_prediction_simple"  # or "house_prices_prediction_all"
    )
    print(f"Selected experiment: {experiment_name}")
    print()

    # Create experiment object
    experiment = Experiment(config, experiment_name)
    print(f"Experiment: {experiment.spec.name}")
    print(f"  Description: {experiment.spec.description}")
    print(f"  Dataset: {experiment.spec.dataset}")
    print(f"  Target: {experiment.spec.target}")
    print(f"  Features: {experiment.spec.features}")
    print(f"  Models: {', '.join(experiment.spec.models)}")
    print(f"  Metrics: {', '.join(experiment.spec.metrics)}")
    print()

    # Create and execute runner
    print("Creating Runner...")
    runner = Runner(experiment, verbose=True)
    print()

    # Run the experiment
    print("Executing experiment...")
    print()
    results = runner.run()
    print()

    # Display results summary
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()

    for model_name, model_results in results.items():
        print(f"\nModel: {model_name}")
        print("-" * 40)

        print("Metrics:")
        for metric_name, metric_value in model_results["metrics"].items():
            print(f"  {metric_name}: {metric_value:.6f}")

        print("\nTop 5 Feature Weights:")
        feature_weights = model_results["feature_weights"]
        for idx, row in feature_weights.head(5).iterrows():
            weight_col = feature_weights.columns[1]  # Get the weight column name
            print(f"  {row['feature']}: {row[weight_col]:.6f}")

    print()
    print("=" * 80)
    print("Experiment completed successfully!")
    print("=" * 80)
    print()
    print("MLFlow tracking information has been logged.")
    print("To view results in MLFlow UI, run:")
    print("  mlflow ui")
    print()


if __name__ == "__main__":
    main()
