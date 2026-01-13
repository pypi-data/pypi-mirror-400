"""Tests for Runner and ModelRunner classes."""

import os
from pathlib import Path

import pandas as pd
import pytest
import yaml

from ml_workbench.config import YamlConfig
from ml_workbench.experiment import Experiment
from ml_workbench.runner import ModelRunner, Runner

# Check if sklearn is available
try:
    import sklearn

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

pytestmark = pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="sklearn not installed")


@pytest.fixture(autouse=True)
def fresh_mlflow_db(tmp_path, monkeypatch):
    """Create a fresh mlflow.db for each test."""
    import mlflow

    # Create a temporary directory for this test's MLflow database
    mlflow_db_path = tmp_path / "mlflow.db"

    # Set tracking URI to use SQLite database
    tracking_uri = f"sqlite:///{mlflow_db_path}"
    mlflow.set_tracking_uri(tracking_uri)

    # Also set environment variable to ensure consistency
    monkeypatch.setenv("MLFLOW_TRACKING_URI", tracking_uri)

    yield mlflow_db_path

    # Cleanup: Ensure fresh database for next test
    if mlflow_db_path.exists():
        # Close any open connections
        try:
            mlflow.end_run()
        except Exception:
            pass


@pytest.fixture
def simple_config(tmp_path):
    """Create a simple configuration for testing."""
    # Create a simple CSV dataset
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "category1": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
        "target": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    })

    csv_path = tmp_path / "test_data.csv"
    data.to_csv(csv_path, index=False)

    # Create config
    config_dict = {
        "datasets": {
            "test_dataset": {
                "description": "Test dataset",
                "path": str(csv_path),
                "format": "csv",
                "type": "local",
            }
        },
        "features": {
            "test_features": {
                "description": "Test features",
                "dataset": "test_dataset",
                "numerical": ["feature1", "feature2"],
                "categorical": ["category1"],
            }
        },
        "models": {
            "test_lasso": {
                "description": "Test Lasso model",
                "type": "sklearn.linear_model.Lasso",
                "params": {"alpha": 1.0, "random_state": 42},
            }
        },
        "experiments": {
            "test_experiment": {
                "description": "Test experiment",
                "models": ["test_lasso"],
                "dataset": "test_dataset",
                "target": "target",
                "features": "test_features",
                "metrics": ["r2", "mse"],
            }
        },
    }

    # Write config to YAML file
    config_path = tmp_path / "test_config.yaml"
    with config_path.open("w") as f:
        yaml.dump(config_dict, f)

    return YamlConfig(config_path)


def test_runner_initialization(simple_config):
    """Test Runner can be initialized."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    assert runner.experiment == experiment
    assert runner.verbose is False
    assert runner.model_runners == []


def test_runner_load_dataset(simple_config):
    """Test Runner can load dataset."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    df = runner._load_dataset()

    assert df is not None
    assert len(df) == 10
    assert "target" in df.columns
    assert "feature1" in df.columns


def test_runner_prepare_features(simple_config):
    """Test Runner can prepare and classify features."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    numerical_features, categorical_features = runner._prepare_features()

    assert numerical_features == ["feature1", "feature2"]
    assert categorical_features == ["category1"]
    assert runner.numerical_features == ["feature1", "feature2"]
    assert runner.categorical_features == ["category1"]


def test_runner_split_data(simple_config):
    """Test Runner can split data."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._drop_outliers()  # Must be called before _split_data
    runner._split_data()

    assert runner.X_train is not None
    assert runner.y_train is not None
    # No test split - only training and optionally holdout
    assert len(runner.X_train) == 10


def test_model_runner_initialization(simple_config):
    """Test ModelRunner can be initialized."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    assert model_runner.model_name == "test_lasso"
    assert model_runner.numerical_features == ["feature1", "feature2"]
    assert model_runner.categorical_features == ["category1"]
    assert model_runner.experiment == experiment
    assert model_runner.X_train is not None
    assert model_runner.y_train is not None
    # Pipeline should be None until created
    assert model_runner.full_pipeline is None


def test_model_runner_fit_and_evaluate(simple_config, tmp_path):
    """Test ModelRunner can fit and evaluate a model."""
    import mlflow

    # Add holdout to config for evaluation
    simple_config._data["experiments"]["test_experiment"]["hold_out"] = {
        "fraction": 0.2,
        "random_state": 42,
    }

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow experiment (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        X_holdout=runner.X_holdout,
        y_holdout=runner.y_holdout,
        verbose=False,
    )

    score = model_runner.fit_and_evaluate()

    assert score is not None
    assert isinstance(score, float)
    # Check that metrics were calculated and stored
    assert model_runner.metrics is not None
    assert len(model_runner.metrics) > 0
    assert model_runner.best_pipeline is not None
    assert model_runner.full_pipeline is not None


def test_model_runner_calculate_feature_weights(simple_config, tmp_path):
    """Test ModelRunner can calculate feature weights."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow experiment (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()
    weights = model_runner.calculate_feature_weights()

    assert weights is not None
    assert len(weights) > 0
    assert "feature" in weights.columns
    assert "weight" in weights.columns


def test_runner_full_workflow(simple_config):
    """Test Runner can execute full workflow."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    results = runner.run()

    assert results is not None
    assert "models" in results
    assert "best_model" in results
    assert "best_model_score" in results
    assert "test_lasso" in results["models"]
    assert results["best_model"] == "test_lasso"
    assert isinstance(results["best_model_score"], float)
    assert len(runner.model_runners) == 1
    assert runner.model_runners[0].model_name == "test_lasso"
    # Check that metrics are stored in model_runner
    assert runner.model_runners[0].metrics is not None


def test_runner_with_multiple_models(simple_config):
    """Test Runner with multiple models."""
    # Add another model to config
    simple_config._data["models"]["test_ridge"] = {
        "description": "Test Ridge model",
        "type": "sklearn.linear_model.Ridge",
        "params": {"alpha": 1.0, "random_state": 42},
    }
    simple_config._data["experiments"]["test_experiment"]["models"] = [
        "test_lasso",
        "test_ridge",
    ]

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    results = runner.run()

    assert "models" in results
    assert "best_model" in results
    assert "best_model_score" in results
    assert len(results["models"]) == 2
    assert "test_lasso" in results["models"]
    assert "test_ridge" in results["models"]
    assert results["best_model"] in ["test_lasso", "test_ridge"]
    assert isinstance(results["best_model_score"], float)
    assert len(runner.model_runners) == 2


def test_runner_with_validation_split(simple_config):
    """Test Runner with validation split (validation splits not currently implemented)."""
    # Note: Validation splits are not currently implemented
    # This test verifies that the system works without validation splits

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Validation splits are not currently implemented in split_data()
    assert len(runner.X_train) == 10

    # Check that ModelRunner can be created without validation data
    ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )


def test_runner_with_holdout(simple_config):
    """Test Runner with hold-out set."""
    # Modify experiment to include hold-out
    simple_config._data["experiments"]["test_experiment"]["hold_out"] = {
        "fraction": 0.2,
        "random_state": 42,
    }

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    assert runner.X_holdout is not None
    assert runner.y_holdout is not None
    total_size = len(runner.X_train) + len(runner.X_holdout)
    assert total_size == 10

    # Check that ModelRunner receives holdout data
    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        X_holdout=runner.X_holdout,
        y_holdout=runner.y_holdout,
        verbose=False,
    )

    assert model_runner.X_holdout is not None
    assert model_runner.y_holdout is not None


def test_runner_classification_experiment(tmp_path):
    """Test Runner with classification experiment."""
    import mlflow

    # Create classification dataset
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "target": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    })
    csv_path = tmp_path / "class_data.csv"
    data.to_csv(csv_path, index=False)

    config_dict = {
        "datasets": {
            "class_dataset": {
                "description": "Classification dataset",
                "path": str(csv_path),
                "format": "csv",
                "type": "local",
            }
        },
        "features": {
            "class_features": {
                "description": "Classification features",
                "dataset": "class_dataset",
                "numerical": ["feature1", "feature2"],
            }
        },
        "models": {
            "test_logistic": {
                "description": "Test Logistic Regression",
                "type": "sklearn.linear_model.LogisticRegression",
                "params": {"random_state": 42, "max_iter": 1000},
            }
        },
        "experiments": {
            "class_experiment": {
                "description": "Classification experiment",
                "models": ["test_logistic"],
                "dataset": "class_dataset",
                "target": "target",
                "features": "class_features",
                "type": "classification",
                "metrics": ["accuracy", "f1_score"],
                "hold_out": {"fraction": 0.2, "random_state": 42},
            }
        },
    }

    config_path = tmp_path / "class_config.yaml"
    with config_path.open("w") as f:
        yaml.dump(config_dict, f)

    config = YamlConfig(config_path)
    experiment = Experiment(config, "class_experiment")
    runner = Runner(experiment, verbose=False)

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("class_experiment")

    results = runner.run()

    assert results is not None
    assert "models" in results
    assert "best_model" in results
    assert "best_model_score" in results
    assert "test_logistic" in results["models"]
    assert results["best_model"] == "test_logistic"
    assert isinstance(results["best_model_score"], float)
    # Check that metrics are stored in model_runner
    assert runner.model_runners[0].metrics is not None
    assert len(runner.model_runners[0].metrics) > 0


def test_runner_drop_outliers(simple_config):
    """Test Runner can detect and mark outliers."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()

    # Check that is_outlier column doesn't exist yet
    assert "is_outlier" not in runner.dataset.columns

    # Call _drop_outliers (should create is_outlier column)
    runner._drop_outliers()

    # Check that is_outlier column exists
    assert "is_outlier" in runner.dataset.columns
    assert runner.dataset["is_outlier"].dtype == bool

    # With default threshold (3.0) and small dataset, should have few/no outliers
    outliers_count = runner.dataset["is_outlier"].sum()
    assert outliers_count >= 0  # Should be non-negative


def test_runner_drop_outliers_disabled(simple_config, tmp_path):
    """Test Runner handles disabled outlier detection."""
    # Create config with drop_outliers disabled
    config_dict = {
        "datasets": {
            "test_dataset": {
                "description": "Test dataset",
                "path": str(tmp_path / "test_data.csv"),
                "format": "csv",
                "type": "local",
            }
        },
        "features": {
            "test_features": {
                "description": "Test features",
                "dataset": "test_dataset",
                "numerical": ["feature1", "feature2"],
                "categorical": ["category1"],
            }
        },
        "models": {
            "test_lasso": {
                "description": "Test Lasso model",
                "type": "sklearn.linear_model.Lasso",
                "params": {"alpha": 1.0, "random_state": 42},
            }
        },
        "experiments": {
            "test_experiment": {
                "description": "Test experiment",
                "models": ["test_lasso"],
                "dataset": "test_dataset",
                "target": "target",
                "features": "test_features",
                "drop_outliers": 0.0,  # Disabled
            }
        },
    }

    # Create CSV
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "category1": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
        "target": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    })
    data.to_csv(tmp_path / "test_data.csv", index=False)

    # Write config
    config_path = tmp_path / "test_config.yaml"
    with config_path.open("w") as f:
        yaml.dump(config_dict, f)

    config = YamlConfig(config_path)
    experiment = Experiment(config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._drop_outliers()

    # is_outlier column should exist but all False
    assert "is_outlier" in runner.dataset.columns
    assert runner.dataset["is_outlier"].sum() == 0


def test_runner_with_group_split(tmp_path):
    """Test Runner with group-based split."""
    import mlflow

    # Create dataset with group column
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "group": [1, 1, 1, 2, 2, 2, 3, 3, 3, 3],
        "target": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    })
    csv_path = tmp_path / "group_data.csv"
    data.to_csv(csv_path, index=False)

    config_dict = {
        "datasets": {
            "group_dataset": {
                "description": "Group dataset",
                "path": str(csv_path),
                "format": "csv",
                "type": "local",
            }
        },
        "features": {
            "group_features": {
                "description": "Group features",
                "dataset": "group_dataset",
                "numerical": ["feature1", "feature2"],
            }
        },
        "models": {
            "test_lasso": {
                "description": "Test Lasso",
                "type": "sklearn.linear_model.Lasso",
                "params": {"alpha": 1.0, "random_state": 42},
            }
        },
        "experiments": {
            "group_experiment": {
                "description": "Group experiment",
                "models": ["test_lasso"],
                "dataset": "group_dataset",
                "target": "target",
                "features": "group_features",
                "hold_out": {
                    "fraction": 0.2,
                    "random_state": 42,
                },
                "do_not_split_by": ["group"],
            }
        },
    }

    config_path = tmp_path / "group_config.yaml"
    with config_path.open("w") as f:
        yaml.dump(config_dict, f)

    config = YamlConfig(config_path)
    experiment = Experiment(config, "group_experiment")
    runner = Runner(experiment, verbose=False)

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("group_experiment")

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    assert runner.X_train is not None
    # No test split - only training and optionally holdout


def test_model_runner_plot_feature_weights(simple_config, tmp_path):
    """Test ModelRunner can plot feature weights."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()
    fig = model_runner.plot_feature_weights()

    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_model_runner_plot_feature_weights_no_weights(simple_config, tmp_path):
    """Test ModelRunner plot_feature_weights returns None when no weights available."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    # Don't fit, so no weights available
    fig = model_runner.plot_feature_weights()
    assert fig is None


def test_model_runner_plot_confusion_matrix(simple_config, tmp_path):
    """Test ModelRunner can plot confusion matrix."""
    import mlflow
    import numpy as np

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()

    # Create some predictions for confusion matrix
    y_pred = model_runner.predict(runner.X_train)
    y_true = runner.y_train

    # For regression, confusion matrix doesn't make sense, but test the method
    # Convert to classification-like for testing
    y_true_binary = (y_true > y_true.median()).astype(int)
    y_pred_binary = (y_pred > np.median(y_pred)).astype(int)

    fig = model_runner.plot_confusion_matrix(y_true_binary, y_pred_binary, "test")
    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_model_runner_plot_regression(simple_config, tmp_path):
    """Test ModelRunner can plot regression plots."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()

    y_pred = model_runner.predict(runner.X_train)
    y_true = runner.y_train

    fig = model_runner.plot_regression(y_true, y_pred, "test")
    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_model_runner_plot_distribution(simple_config, tmp_path):
    """Test ModelRunner can plot distribution."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()

    y_pred = model_runner.predict(runner.X_train)
    y_true = runner.y_train

    fig = model_runner.plot_distribution(y_true, y_pred, "test")
    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_model_runner_predict(simple_config, tmp_path):
    """Test ModelRunner can make predictions."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()

    predictions = model_runner.predict(runner.X_train)
    assert predictions is not None
    assert len(predictions) == len(runner.X_train)


def test_model_runner_predict_not_fitted(simple_config):
    """Test ModelRunner predict raises error if not fitted."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    with pytest.raises(RuntimeError, match="not trained"):
        model_runner.predict(runner.X_train)


def test_model_runner_with_tuning_grid_search(simple_config, tmp_path):
    """Test ModelRunner with grid search hyperparameter tuning."""
    import mlflow

    # Add tuning config
    simple_config._data["models"]["test_lasso"]["tuning"] = {
        "method": "grid_search",
        "inner_cv": 3,
        "scoring": "neg_mean_squared_error",
        "param_grid": {
            "alpha": [0.1, 1.0, 10.0]
        }
    }

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    score = model_runner.fit_and_evaluate()

    assert score is not None
    assert model_runner.is_cross_validation is True
    assert model_runner.cv_results_ is not None
    assert model_runner.cv_best_params_ is not None


def test_model_runner_with_tuning_random_search(simple_config, tmp_path):
    """Test ModelRunner with random search hyperparameter tuning."""
    import mlflow

    # Add tuning config
    simple_config._data["models"]["test_lasso"]["tuning"] = {
        "method": "random_search",
        "inner_cv": 3,
        "n_iter": 5,
        "scoring": "neg_mean_squared_error",
        "param_grid": {
            "alpha": [0.1, 1.0, 10.0]
        }
    }

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    score = model_runner.fit_and_evaluate()

    assert score is not None
    assert model_runner.is_cross_validation is True
    assert model_runner.cv_results_ is not None


def test_model_runner_plot_cv_mean_score(simple_config, tmp_path):
    """Test ModelRunner can plot CV mean score."""
    import mlflow

    # Add tuning config
    simple_config._data["models"]["test_lasso"]["tuning"] = {
        "method": "grid_search",
        "inner_cv": 3,
        "scoring": "neg_mean_squared_error",
        "param_grid": {
            "alpha": [0.1, 1.0]
        }
    }

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    model_runner.fit_and_evaluate()

    fig = model_runner.plot_cv_mean_score()
    assert fig is not None
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_model_runner_plot_cv_mean_score_no_cv(simple_config, tmp_path):
    """Test ModelRunner plot_cv_mean_score returns None when no CV results."""
    import mlflow

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()
    runner._split_data()

    # Set up MLflow (fresh_mlflow_db fixture handles database setup)
    import mlflow

    mlflow.set_experiment("test_experiment")

    model_runner = ModelRunner(
        model_name="test_lasso",
        numerical_features=runner.numerical_features,
        categorical_features=runner.categorical_features,
        experiment=experiment,
        X_train=runner.X_train,
        y_train=runner.y_train,
        verbose=False,
    )

    # Don't fit, so no CV results
    fig = model_runner.plot_cv_mean_score()
    assert fig is None


def test_runner_data_save_and_load(simple_config, tmp_path):
    """Test Runner can save and load data."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner.data_preparation()

    # Save data
    filepath = runner.data_save(str(tmp_path / "test_data.parquet"))
    assert filepath == str(tmp_path / "test_data.parquet")
    assert (tmp_path / "test_data.parquet").exists()

    # Create new runner and load data
    runner2 = Runner(experiment, verbose=False)
    runner2.data_load(str(tmp_path / "test_data.parquet"))

    assert runner2.dataset is not None
    assert runner2.X_train is not None
    assert runner2.y_train is not None
    assert len(runner2.X_train) == len(runner.X_train)


def test_runner_data_save_default_filename(simple_config, tmp_path):
    """Test Runner data_save generates default filename."""
    import os
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner.data_preparation()

    from pathlib import Path

    original_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        filepath = runner.data_save()
        assert filepath == "test_experiment_dataset.parquet"
        assert (tmp_path / "test_experiment_dataset.parquet").exists()
    finally:
        os.chdir(original_cwd)


def test_runner_data_load_file_not_found(simple_config):
    """Test Runner data_load raises error for missing file."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    with pytest.raises(FileNotFoundError):
        runner.data_load("nonexistent_file.parquet")


def test_runner_data_load_missing_is_holdout(simple_config, tmp_path):
    """Test Runner data_load raises error if is_holdout column missing."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner.data_preparation()

    # Save dataset without is_holdout column
    df_no_holdout = runner.dataset.drop(columns=["is_holdout"], errors="ignore")
    df_no_holdout.to_parquet(tmp_path / "no_holdout.parquet", index=False)

    runner2 = Runner(experiment, verbose=False)
    with pytest.raises(ValueError, match="is_holdout"):
        runner2.data_load(str(tmp_path / "no_holdout.parquet"))


def test_runner_get_config(simple_config):
    """Test Runner get_config returns config with inferred types."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner.data_preparation()

    config_dict = runner.get_config()

    assert config_dict is not None
    assert "experiments" in config_dict
    assert "test_experiment" in config_dict["experiments"]
    assert "features" in config_dict
    assert "test_features" in config_dict["features"]
    assert "numerical" in config_dict["features"]["test_features"]
    assert "categorical" in config_dict["features"]["test_features"]


def test_runner_get_config_before_preparation(simple_config):
    """Test Runner get_config works even if features not prepared (but won't have inferred types)."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    # Should work but won't have inferred feature types
    config_dict = runner.get_config()
    assert config_dict is not None
    # Features section exists but may not have inferred numerical/categorical
    assert "features" in config_dict


def test_runner_get_best_model(simple_config):
    """Test Runner get_best_model returns best model."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner.run()

    best_model = runner.get_best_model()
    assert best_model is not None
    assert best_model.model_name == "test_lasso"

    best_score = runner.get_best_model_score()
    assert best_score is not None
    assert isinstance(best_score, float)


def test_runner_get_models(simple_config):
    """Test Runner get_models returns list of model runners."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner.run()

    models = runner.get_models()
    assert len(models) == 1
    assert models[0].model_name == "test_lasso"


def test_runner_infer_column_types_with_all(simple_config):
    """Test Runner _infer_column_types handles __all__ keyword."""
    # Create config with __all__ in column list
    simple_config._data["features"]["test_features"]["column"] = ["__all__"]
    del simple_config._data["features"]["test_features"]["numerical"]
    del simple_config._data["features"]["test_features"]["categorical"]

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    numerical, categorical = runner._infer_column_types(runner.dataset)

    # Should infer all columns except target
    assert len(numerical) + len(categorical) > 0
    assert "target" not in numerical
    assert "target" not in categorical


def test_runner_infer_column_types_missing_columns(simple_config):
    """Test Runner _infer_column_types handles missing columns gracefully."""
    # Add non-existent columns to config
    simple_config._data["features"]["test_features"]["numerical"] = ["feature1", "nonexistent"]
    simple_config._data["features"]["test_features"]["categorical"] = ["category1", "missing"]

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    numerical, categorical = runner._infer_column_types(runner.dataset)

    # Should only include existing columns
    assert "feature1" in numerical
    assert "nonexistent" not in numerical
    assert "category1" in categorical
    assert "missing" not in categorical


def test_runner_get_grouping_values_column(simple_config):
    """Test Runner _get_grouping_values from column."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()

    groups = runner._get_grouping_values(runner.dataset, "category1")
    assert groups is not None
    assert len(groups) == len(runner.dataset)


def test_runner_get_grouping_values_index(simple_config):
    """Test Runner _get_grouping_values from index."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner.dataset.index.name = "group_id"

    groups = runner._get_grouping_values(runner.dataset, "group_id")
    assert groups is not None
    assert len(groups) == len(runner.dataset)


def test_runner_get_grouping_values_not_found(simple_config):
    """Test Runner _get_grouping_values raises error if not found."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()

    with pytest.raises(ValueError, match="not found"):
        runner._get_grouping_values(runner.dataset, "nonexistent_column")


def test_runner_prepare_features_target_in_features_error(simple_config):
    """Test Runner _prepare_features raises error if target in features."""
    # Add target to features
    simple_config._data["features"]["test_features"]["numerical"] = ["feature1", "target"]

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()

    with pytest.raises(ValueError, match="Target column"):
        runner._prepare_features()


def test_runner_prepare_features_no_features_error(simple_config):
    """Test Runner _prepare_features raises error if no features."""
    # Remove all features
    simple_config._data["features"]["test_features"] = {
        "description": "Test features",
        "dataset": "test_dataset",
    }

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()

    with pytest.raises(ValueError, match="No features were found"):
        runner._prepare_features()


def test_runner_drop_outliers_no_numeric_columns(simple_config):
    """Test Runner _drop_outliers handles no numeric columns."""
    # Create dataset with only categorical columns
    data = pd.DataFrame({
        "category1": ["A", "B", "A", "B"],
        "category2": ["X", "Y", "X", "Y"],
        "target": ["class1", "class2", "class1", "class2"],
    })

    csv_path = simple_config._data["datasets"]["test_dataset"]["path"]
    data.to_csv(csv_path, index=False)

    simple_config._data["features"]["test_features"] = {
        "description": "Test features",
        "dataset": "test_dataset",
        "categorical": ["category1", "category2"],
    }
    simple_config._data["experiments"]["test_experiment"]["target"] = "target"

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()

    # Should not raise error, just log that no numeric columns found
    runner._drop_outliers()
    assert "is_outlier" in runner.dataset.columns


def test_runner_drop_outliers_constant_column(simple_config):
    """Test Runner _drop_outliers handles constant columns."""
    # Create dataset with constant column
    data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5],
        "feature2": [1, 1, 1, 1, 1],  # Constant column
        "target": [10, 20, 30, 40, 50],
    })

    csv_path = simple_config._data["datasets"]["test_dataset"]["path"]
    data.to_csv(csv_path, index=False)

    simple_config._data["features"]["test_features"]["numerical"] = ["feature1", "feature2"]

    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()

    # Should not raise error, just skip constant column
    runner._drop_outliers()
    assert "is_outlier" in runner.dataset.columns


def test_runner_split_data_target_not_found(simple_config):
    """Test Runner _split_data raises error if target not found."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()

    # Remove target column
    runner.dataset = runner.dataset.drop(columns=["target"])

    with pytest.raises(ValueError, match="Target column"):
        runner._split_data()


def test_runner_convert_column_types(simple_config):
    """Test Runner _convert_column_types converts types correctly."""
    experiment = Experiment(simple_config, "test_experiment")
    runner = Runner(experiment, verbose=False)

    runner._load_dataset()
    runner._prepare_features()

    df = runner._convert_column_types(runner.dataset.copy())

    # Check categorical columns are strings
    for col in runner.categorical_features:
        if col in df.columns:
            assert df[col].dtype == "object" or df[col].dtype.name == "string"

    # Check numerical columns are numeric
    for col in runner.numerical_features:
        if col in df.columns:
            assert pd.api.types.is_numeric_dtype(df[col])
