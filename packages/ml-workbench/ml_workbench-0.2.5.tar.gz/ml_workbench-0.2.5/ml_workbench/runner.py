"""Runner for executing ML experiments."""

# ToDo: Add support for estimator specific transformer: https://chatgpt.com/share/e/6923056a-7a44-8012-a36d-d822b913db60

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any
import tempfile
import os

import matplotlib

# matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
import yaml

try:
    import seaborn as sns
except ImportError:
    sns = None
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    GroupShuffleSplit,
    RandomizedSearchCV,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .dataset import Dataset
from .feature import Feature
from .model import Model
from .mlflow_conf import MlflowConf

if TYPE_CHECKING:
    from .experiment import Experiment


class ModelRunner:
    """Handles training, evaluation, and MLflow logging for a specific model.

    Responsibilities:
    - Create model-specific preprocessing pipeline
    - Create model-specific pipeline (preprocessor + model)
    - Train the model
    - Evaluate model performance
    - Calculate feature weights/importances
    - Log results to MLflow

    Parameters
    ----------
    model_name : str
        Name of the model to run
    numerical_features : List[str]
        List of numerical feature column names
    categorical_features : List[str]
        List of categorical feature column names
    experiment : Experiment
        Experiment specification
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    X_holdout : Optional[pd.DataFrame]
        Holdout features (optional)
    y_holdout : Optional[pd.Series]
        Holdout target (optional)
    verbose : bool, optional
        Whether to print progress information, by default True
    """

    def __init__(
        self,
        model_name: str,
        numerical_features: list[str],
        categorical_features: list[str],
        experiment: Experiment,
        X_train: pd.DataFrame,  # noqa: N803
        y_train: pd.Series,
        X_holdout: pd.DataFrame | None = None,  # noqa: N803
        y_holdout: pd.Series | None = None,
        verbose: bool = True,
    ):
        self.model_name = model_name
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.experiment = experiment
        self.config = experiment.config
        self.X_train = X_train
        self.y_train = y_train
        self.X_holdout = X_holdout
        self.y_holdout = y_holdout
        self.verbose = verbose

        # Pipeline and model storage
        self.full_pipeline: Pipeline | None = (
            None  # full pipeline with preprocessor and model
        )
        self.best_pipeline: Pipeline | None = (
            None  # best pipeline after cross-validation
        )
        self.is_cross_validation: bool = False
        # cross validation results on train dataset (used to select the best model)
        self.cv_results_: dict[str, Any] | None = None
        self.cv_best_params_: dict[str, Any] | None = None
        self.cv_best_score_: float | None = None

        # metrics and selection score on holdout and train datasets (used to select the best model)
        self.metrics: dict[str, float] | None = None
        self.selection_score: float | None = (
            None  # the score used to select the best model if multiple metrics are specified
        )

    def _log(self, message: str) -> None:
        """Print message if verbose is enabled."""
        if self.verbose:
            print(f"[ModelRunner:{self.model_name}] {message}") # noqa: T201

    def _build_preprocessing_pipeline(self) -> ColumnTransformer:
        """Build preprocessing pipeline for features.

        Creates separate pipelines for numerical and categorical features:
        - Numerical: integer-to-float conversion + imputation + standardization
        - Categorical: imputation + one-hot encoding

        The integer-to-float conversion ensures MLflow schema compatibility by
        converting integer columns to float64, preventing schema enforcement
        errors when missing values are present at inference time.

        Returns
        -------
        ColumnTransformer
            Preprocessing pipeline
        """
        self._log("Building preprocessing pipeline")

        # Build transformers
        transformers = []

        if self.numerical_features:
            numerical_transformer = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            transformers.append(("num", numerical_transformer, self.numerical_features))

        if self.categorical_features:
            categorical_transformer = Pipeline(
                steps=[
                    (
                        "imputer",
                        SimpleImputer(strategy="constant", fill_value="missing"),
                    ),
                    (
                        "onehot",
                        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    ),
                ]
            )
            transformers.append((
                "cat",
                categorical_transformer,
                self.categorical_features,
            ))

        if not transformers:
            raise ValueError("No features to process")  # noqa: TRY003

        return ColumnTransformer(transformers=transformers, remainder="drop")

    def _create_pipeline(self) -> Pipeline:
        """Create full pipeline with preprocessor and model.

        Returns
        -------
        Pipeline
            Full pipeline with preprocessor and model steps
        """
        # Build preprocessing pipeline if not already built
        preprocessor = self._build_preprocessing_pipeline()

        # Load model configuration
        model_obj = Model(self.model_name, self.config)
        model_instance = model_obj.instantiate()

        # Create full pipeline
        pipeline = Pipeline(
            steps=[("preprocessor", preprocessor), ("model", model_instance)]
        )

        # self.model = model_instance
        self.full_pipeline = pipeline

        return pipeline

    def _calculate_metrics(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray,
        metrics_list: list[str] | None = None,
    ) -> dict[str, float]:
        """Calculate evaluation metrics.

        Parameters
        ----------
        y_true : pd.Series
            True target values
        y_pred : np.ndarray
            Predicted values
        metrics_list : Optional[List[str]]
            List of metric names to calculate. If None, uses experiment metrics. The first metrics will be used to select the best model if multiple specified.

        Returns
        -------
        Dict[str, float]
            Dictionary of metric names to values
        """
        if metrics_list is None:
            metrics_list = self.experiment.spec.metrics or ["r2", "mse"]

        results = {}

        for idx, metric_name in enumerate(metrics_list):
            metric_name_lower = metric_name.lower()
            metric_value = None
            direction_flag = 1

            try:
                if metric_name_lower.startswith("r2"):
                    metric_value = r2_score(y_true, y_pred)
                    results["r2_score"] = metric_value
                    direction_flag = 1  # higher is better
                elif metric_name_lower in ["mse", "mean_squared_error"]:
                    metric_value = mean_squared_error(y_true, y_pred)
                    results["mean_squared_error"] = metric_value
                    direction_flag = -1  # lower is better
                elif metric_name_lower in ["rmse", "root_mean_squared_error"]:
                    metric_value = np.sqrt(mean_squared_error(y_true, y_pred))
                    results["root_mean_squared_error"] = metric_value
                    direction_flag = -1  # lower is better
                elif metric_name_lower in ["mae", "mean_absolute_error"]:
                    metric_value = mean_absolute_error(y_true, y_pred)
                    results["mean_absolute_error"] = metric_value
                    direction_flag = -1  # lower is better
                elif metric_name_lower.startswith("accuracy"):
                    metric_value = accuracy_score(y_true, y_pred)
                    results["accuracy_score"] = metric_value
                    direction_flag = 1  # higher is better
                elif metric_name_lower.startswith("precision"):
                    metric_value = precision_score(y_true, y_pred, average="weighted")
                    results["precision_score"] = metric_value
                    direction_flag = 1  # higher is better
                elif metric_name_lower.startswith("recall"):
                    metric_value = recall_score(y_true, y_pred, average="weighted")
                    results["recall_score"] = metric_value
                    direction_flag = 1  # higher is better
                elif metric_name_lower.startswith("f1"):
                    metric_value = f1_score(y_true, y_pred, average="weighted")
                    results["f1_score"] = metric_value
                    direction_flag = 1  # higher is better
                else:
                    self._log(f"Warning: Unknown metric '{metric_name}'")

                # Always set selection_score from the *first* metric in the list
                if idx == 0 and metric_value is not None:
                    results["selection_score"] = direction_flag * metric_value

            except Exception as e:
                self._log(f"Error calculating metric '{metric_name}': {e}")

        return results

    def calculate_feature_weights(self) -> pd.DataFrame:
        """Calculate feature importances or coefficients.

        Returns
        -------
        pd.DataFrame
            DataFrame with feature names and their weights/importances
        """
        # Get the fitted pipeline from the search
        best_pipeline = self.best_pipeline

        # Find the column transformer and ridge model in the pipeline
        # Assumes the pipeline steps are: ('preprocessor', ...), ('ridge', ...)
        preprocessor = best_pipeline.named_steps["preprocessor"]
        model = best_pipeline.named_steps["model"]

        # Get feature names from preprocessor
        feature_names = preprocessor.get_feature_names_out()
        # Drop prefix before '__' in feature names, if present
        feature_names = [
            name.split("__", 1)[-1] if "__" in name else name for name in feature_names
        ]

        # Extract weights/importances from model
        weights = None
        weight_type = None

        if hasattr(model, "coef_"):
            # Linear models (coefficients)
            weights = model.coef_
            weight_type = "coefficient"
        elif hasattr(model, "feature_importances_"):
            # Tree-based models (feature importances)
            weights = model.feature_importances_
            weight_type = "importance"
        else:
            self._log(
                "Warning: Model does not have coefficients or feature importances"
            )
            return pd.DataFrame()

        # Handle multi-dimensional coefficients (e.g., multi-class classification)
        if len(weights.shape) > 1:
            weights = np.abs(weights).mean(axis=0)

        # Create DataFrame
        df = pd.DataFrame({
            "feature": feature_names[: len(weights)],
            "weight": weights,
            "type": weight_type,
        })
        df = df.sort_values(by="weight", ascending=False, key=abs)

        # self._log("Top 5 features by weight:")
        # for _idx, row in df.head(5).iterrows():
        #     self._log(f"  {row['feature']}: {row['weight']:.6f}")

        return df

    def plot_feature_weights(self) -> matplotlib.figure.Figure | None:
        """
        Plot feature importances or coefficients from the best estimator (tuned search).
        Reuses the calculate_feature_weights method.
        Returns a matplotlib Figure object for notebook display or file export.

        Returns
        -------
        matplotlib.figure.Figure or None
            The figure, or None if no feature weights are available.
        """

        try:
            # Reuse calculate_feature_weights to get DataFrame
            weights_df = self.calculate_feature_weights()
        except Exception as e:
            self._log(f"Error calculating feature weights: {e}")
            return None

        if (
            weights_df is None
            or weights_df.empty
            or "feature" not in weights_df
            or "weight" not in weights_df
        ):
            self._log("No feature weights available to plot.")
            return None

        # Sort features by absolute weight/importance (descending)
        weights_df_sorted = weights_df.reindex(
            weights_df.weight.abs().sort_values(ascending=False).index
        )

        # Plot
        fig, ax = plt.subplots(
            figsize=(10, max(4, min(0.5 * len(weights_df_sorted), 16)))
        )
        ax.barh(
            weights_df_sorted["feature"],
            weights_df_sorted["weight"],
            color="tab:blue",
            alpha=0.85,
        )

        ylabel = (
            "Coefficient"
            if "coefficient" in weights_df_sorted.columns.to_numpy().tolist()
            or "coefficient" in weights_df_sorted.get("type", "")
            else "Importance"
        )
        ax.set_xlabel(ylabel)
        ax.set_title(f"Feature {ylabel}s for Best Estimator ({self.model_name})")
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.5)
        fig.tight_layout()

        return fig

    def plot_cv_mean_score(self, figsize=(10, 10)) -> matplotlib.figure.Figure | None:
        """
        Plot mean test score across CV splits with confidence intervals (std error).
        Returns
        -------
        matplotlib.figure.Figure or None
            The figure, or None if no CV results are available.
        """

        if not self.cv_results_:
            self._log("No cross-validation results found to plot.")
            return None

        cv_results = self.cv_results_
        if "mean_test_score" not in cv_results or "std_test_score" not in cv_results:
            self._log("CV results are missing 'mean_test_score' or 'std_test_score'.")
            return None

        mean_scores = np.array(cv_results["mean_test_score"])
        std_scores = np.array(cv_results["std_test_score"])
        x_labels = [f"{v}" for v in cv_results["params"]]

        # Plot mean test score with confidence intervals
        fig, ax = plt.subplots(figsize=figsize)
        ax.tick_params(axis="x", rotation=90)  # Make x labels vertical
        ax.errorbar(
            x_labels,
            mean_scores,
            yerr=std_scores,
            fmt="o",
            capsize=4,
            label="Mean Test Score ±1 Std",
        )
        ax.set_xlabel("Hyperparameter Combination Index")
        ax.set_ylabel("Mean Test Score")
        ax.set_title(f"Hyperparameter Search Mean Test Score ±1 Std ({self.model_name})")
        ax.legend()
        ax.grid(True)
        fig.tight_layout()

        return fig

    def plot_confusion_matrix(
        self,
        y_true: pd.Series | np.ndarray,
        y_pred: pd.Series | np.ndarray,
        title_prefix: str | None = None,
    ) -> matplotlib.figure.Figure | None:
        """Create confusion matrix plot for classification.

        Parameters
        ----------
        y_true : pd.Series | np.ndarray
            True target values
        y_pred : pd.Series | np.ndarray
            Predicted values
        title_prefix : str, optional
            Prefix to add to plot title (e.g., 'holdout data', 'test data', etc.)
            If None, no prefix is added.

        Returns
        -------
        matplotlib.figure.Figure | None
            Matplotlib figure object with confusion matrix plot, or None if error occurs
        """
        try:
            # Convert to numpy arrays if needed
            y_true = y_true.to_numpy() if isinstance(y_true, pd.Series) else y_true
            y_pred = y_pred.to_numpy() if isinstance(y_pred, pd.Series) else y_pred

            # Get unique class labels
            classes = sorted(set(np.unique(y_true)) | set(np.unique(y_pred)))

            # Calculate confusion matrix with explicit labels
            cm = confusion_matrix(y_true, y_pred, labels=classes)

            # Create plot
            fig, ax = plt.subplots(figsize=(8, 6))

            # Use seaborn if available for better visualization
            if sns is not None:
                sns.heatmap(
                    cm,
                    annot=True,
                    fmt="d",
                    cmap="Blues",
                    ax=ax,
                    cbar_kws={"label": "Count"},
                    xticklabels=classes,
                    yticklabels=classes,
                )
            else:
                # Fallback to matplotlib if seaborn not available
                im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
                ax.figure.colorbar(im, ax=ax)

                # Add text annotations
                thresh = cm.max() / 2.0
                for i in range(cm.shape[0]):
                    for j in range(cm.shape[1]):
                        ax.text(
                            j,
                            i,
                            format(cm[i, j], "d"),
                            ha="center",
                            va="center",
                            color="white" if cm[i, j] > thresh else "black",
                        )

            # Build title suffix
            title_suffix = f" ({title_prefix})" if title_prefix else ""

            ax.set(
                xlabel="Predicted Label",
                ylabel="True Label",
                title=f"Confusion Matrix{title_suffix}",
            )
            ax.set_xticks(np.arange(len(classes)))
            ax.set_yticks(np.arange(len(classes)))
            ax.set_xticklabels(classes)
            ax.set_yticklabels(classes)

            fig.tight_layout()

        except Exception as e:
            self._log(f"Error creating confusion matrix plot: {e}")
            return None
        else:
            return fig

    def plot_regression(
        self,
        y_true: pd.Series | np.ndarray,
        y_pred: pd.Series | np.ndarray,
        title_prefix: str | None = None,
    ) -> matplotlib.figure.Figure | None:
        """Create actual vs predicted and residuals vs predicted plots for regression.

        Parameters
        ----------
        y_true : pd.Series | np.ndarray
            True target values
        y_pred : pd.Series | np.ndarray
            Predicted values
        title_prefix : str, optional
            Prefix to add to plot titles (e.g., 'holdout data', 'test data', etc.)
            If None, no prefix is added.

        Returns
        -------
        matplotlib.figure.Figure | None
            Matplotlib figure object with two subplots, or None if error occurs
        """
        try:
            y_true = y_true.to_numpy() if isinstance(y_true, pd.Series) else y_true
            y_pred = y_pred.to_numpy() if isinstance(y_pred, pd.Series) else y_pred
            # Calculate residuals
            residuals = y_true - y_pred

            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Build title suffix
            title_suffix = f" ({title_prefix})" if title_prefix else ""

            # Plot 1: Actual vs Predicted
            ax1.scatter(y_true, y_pred, alpha=0.6, s=20)

            # Add diagonal line (perfect prediction)
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            ax1.plot(
                [min_val, max_val],
                [min_val, max_val],
                "r--",
                lw=2,
                label="Perfect prediction",
            )

            ax1.set_xlabel("Actual Values")
            ax1.set_ylabel("Predicted Values")
            ax1.set_title(f"Actual vs Predicted{title_suffix}")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot 2: Residuals vs Predicted
            ax2.scatter(y_pred, residuals, alpha=0.6, s=20)

            # Add horizontal line at y=0
            ax2.axhline(y=0, color="r", linestyle="--", lw=2, label="Zero residual")

            ax2.set_xlabel("Predicted Values")
            ax2.set_ylabel("Residuals")
            ax2.set_title(f"Residuals vs Predicted{title_suffix}")
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            fig.tight_layout()

        except Exception as e:
            self._log(f"Error creating regression plots: {e}")
            return None
        else:
            return fig

    def plot_distribution(
        self,
        y_true: pd.Series | np.ndarray,
        y_pred: pd.Series | np.ndarray,
        title_prefix: str | None = None,
    ) -> matplotlib.figure.Figure | None:
        """
        Plot the distribution (KDE) of actual and predicted values.

        Parameters
        ----------
        y_true : pd.Series | np.ndarray
            True target values
        y_pred : pd.Series | np.ndarray
            Predicted values
        title_prefix : str or None
            Optional prefix for the plot title.

        Returns
        -------
        matplotlib.figure.Figure or None
            The figure, or None if an error occurs.
        """
        try:
            y_true = y_true.to_numpy() if isinstance(y_true, pd.Series) else y_true
            y_pred = y_pred.to_numpy() if isinstance(y_pred, pd.Series) else y_pred

            fig, ax = plt.subplots(figsize=(8, 6))
            title_suffix = f" ({title_prefix})" if title_prefix else ""

            # Plot the KDE for true values
            pd.Series(y_true).plot(kind="kde", ax=ax, label="Actual", color="tab:blue")
            # Plot the KDE for predicted values
            pd.Series(y_pred).plot(
                kind="kde", ax=ax, label="Predicted", color="tab:orange"
            )

            ax.set_xlabel("Value")
            ax.set_ylabel("Density")
            ax.set_title(
                f"Distribution (KDE) of Actual and Predicted Values{title_suffix}"
            )
            ax.legend()
            ax.grid(True, alpha=0.3)
            fig.tight_layout()

        except Exception as e:
            self._log(f"Error plotting distributions: {e}")
            return None
        else:
            return fig

    def fit_and_evaluate(self) -> float:
        """Train the model and evaluate it.

        This method encapsulates the full model lifecycle:
        - Creates the pipeline
        - If tuning is configured, performs cross-validation hyperparameter search
        - Fits the model (or best tuned model) on training data
        - Evaluates on holdout sets
        - Calculates feature weights

        Returns
        -------
        float
            R2 score of the model - used to select the best model
        """
        self._log("Starting model training and evaluation")

        # Load model configuration to check for tuning
        model_obj = Model(self.model_name, self.config)
        tuning_config = model_obj.spec.tuning

        # Create initial pipeline (integer-to-float conversion is handled in the pipeline)
        self._create_pipeline()

        # Check if tuning is configured (non-empty dict)
        if tuning_config and len(tuning_config) > 0:
            self._log("Tuning configuration detected - performing cross-validation")
            self.is_cross_validation = True

            # Extract tuning parameters
            method = tuning_config.get("method", "grid_search")
            inner_cv = tuning_config.get("inner_cv", 5)
            scoring = tuning_config.get("scoring", "neg_mean_squared_error")
            param_grid = tuning_config.get("param_grid", {})

            # Build parameter grid with proper prefix for pipeline
            # Parameters need to be prefixed with "model__" since model is a step in the pipeline
            pipeline_param_grid = {}

            # Handle logspace if present as standalone key (overwrites alpha)
            if "logspace" in param_grid:
                logspace_config = param_grid["logspace"]
                start = logspace_config.get("start", -2)
                stop = logspace_config.get("stop", 2)
                num = logspace_config.get("num", 50)
                logspace_values = np.logspace(start, stop, num).tolist()
                # Apply logspace to alpha (most common use case)
                pipeline_param_grid["model__alpha"] = logspace_values
                self._log(
                    f"Using logspace for alpha: {num} values from 10^{start} to 10^{stop}"
                )

            # Process regular parameters
            for param_name, param_values in param_grid.items():
                if (
                    param_name == "logspace"
                ):  # Skip standalone logspace key (already handled)
                    continue

                # Check if this parameter has nested logspace structure
                if isinstance(param_values, dict) and "logspace" in param_values:
                    logspace_config = param_values["logspace"]
                    start = logspace_config.get("start", -2)
                    stop = logspace_config.get("stop", 2)
                    num = logspace_config.get("num", 50)
                    logspace_values = np.logspace(start, stop, num).tolist()
                    pipeline_param_grid[f"model__{param_name}"] = logspace_values
                    self._log(
                        f"Using logspace for {param_name}: {num} values from 10^{start} to 10^{stop}"
                    )
                elif isinstance(param_values, list):
                    # Regular list of values
                    pipeline_param_grid[f"model__{param_name}"] = param_values

            # Choose search method
            if method == "random_search":
                n_iter = tuning_config.get("n_iter", 10)
                search = RandomizedSearchCV(
                    self.full_pipeline,
                    pipeline_param_grid,
                    cv=inner_cv,
                    scoring=scoring,
                    n_iter=n_iter,
                    verbose=1 if self.verbose else 0,
                    n_jobs=-1,
                )
            else:  # Default to grid_search
                search = GridSearchCV(
                    self.full_pipeline,
                    pipeline_param_grid,
                    cv=inner_cv,
                    scoring=scoring,
                    verbose=1 if self.verbose else 0,
                    n_jobs=-1,
                )

            # Perform cross-validation search
            self._log(f"Performing {method} with {inner_cv}-fold CV")
            search.fit(self.X_train, self.y_train)

            # Store CV results for future analysis
            self.cv_results_ = search.cv_results_
            self.cv_best_params_ = search.best_params_
            self.cv_best_score_ = search.best_score_

            # Set best_pipeline as the best tuned pipeline
            self.best_pipeline = search.best_estimator_
            self._log(f"Best parameters: {search.best_params_}")
            self._log(f"Best CV score: {search.best_score_:.6f}")

            # Fit best_pipeline on full training data
            self._log("Fitting best pipeline on full training data")
            self.best_pipeline.fit(self.X_train, self.y_train)

        else:
            # No tuning - standard fit
            self.best_pipeline = self.full_pipeline
            self._log("Training model")
            self.best_pipeline.fit(self.X_train, self.y_train)

        self._log("Model training completed")

        # start evaluation part of the model (if holdout exists)
        metrics = {}
        selection_score = None
        # evaluate on train set
        if self.X_train is not None and self.y_train is not None:
            self._log("Evaluating model on test set")
            y_pred_train = self.best_pipeline.predict(self.X_train)
            train_metrics = self._calculate_metrics(
                self.y_train, y_pred_train, self.experiment.spec.metrics
            )
            for metric, value in train_metrics.items():
                self._log(f"  train_{metric}: {value:.6f}")
            if "selection_score" in train_metrics:
                selection_score = train_metrics["selection_score"]
                self._log(f"Train Selection score: {selection_score:.6f}")
            train_metrics = {f"train_{k}": v for k, v in train_metrics.items()}
            metrics.update(train_metrics)
        # evaluate on holdout set
        if self.X_holdout is not None and self.y_holdout is not None:
            self._log("Evaluating model on holdout set")
            y_pred_holdout = self.best_pipeline.predict(self.X_holdout)
            holdout_metrics = self._calculate_metrics(
                self.y_holdout, y_pred_holdout, self.experiment.spec.metrics
            )
            for metric, value in holdout_metrics.items():
                self._log(f"  holdout_{metric}: {value:.6f}")
            if "selection_score" in holdout_metrics:
                selection_score = holdout_metrics["selection_score"]
                self._log(f"Holdout Selection score: {selection_score:.6f}")
            holdout_metrics = {f"holdout_{k}": v for k, v in holdout_metrics.items()}
            metrics.update(holdout_metrics)

        self.metrics = metrics
        self.selection_score = selection_score
        return self.selection_score

    def predict(self, X):  # noqa: N803
        """
        Make predictions using the best trained pipeline.

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            Input features for prediction.

        Returns
        -------
        np.ndarray
            Predicted outputs.
        """
        if not hasattr(self, "best_pipeline") or self.best_pipeline is None:
            raise RuntimeError("The model pipeline is not trained yet.")  # noqa: TRY003
        return self.best_pipeline.predict(X)

    def mlflow_store(self) -> None:
        """
        Store the model in MLflow.
        Assuming to run with active run
        """
        mlflow.log_param("model_name", self.model_name)
        mlflow.log_param("model_pipeline", str(self.best_pipeline))

        # Get the parameters from the 'model' step of the pipeline and log each as a parameter
        model_params = self.best_pipeline.named_steps['model'].get_params()
        for param_name, param_value in model_params.items():
            mlflow.log_param(f"model__{param_name}", param_value)

        # log metrics
        for k, v in self.metrics.items():
            mlflow.log_metric(k, v)

        # log model with a signature
        # Get a DataFrame containing the first 10 rows of X_train
        sample_df = self.X_train.head(10).copy()
        signature = mlflow.models.infer_signature(sample_df, self.best_pipeline.predict(sample_df))
        mlflow.sklearn.log_model(self.best_pipeline, name="model", signature=signature)

        # create temp directory to create artifacts and load them into MlFlow
        with tempfile.TemporaryDirectory() as temp_dir:
            # log cross validation results
            if self.is_cross_validation and self.cv_results_ is not None:
                mlflow.log_param("cross_validation",True)
                fig = self.plot_cv_mean_score()
                if fig:
                    fig.savefig(os.path.join(temp_dir, "cv_mean_score.png"))
                    mlflow.log_artifact(os.path.join(temp_dir, "cv_mean_score.png"))
            else:
                mlflow.log_param("cross_validation",False)

            # log plot_feature_weights
            weights_df = self.calculate_feature_weights()
            if weights_df is not None and not weights_df.empty:
                weights_df.to_csv(os.path.join(temp_dir, "feature_weights.csv"), index=False)
                mlflow.log_artifact(os.path.join(temp_dir, "feature_weights.csv"))
                fig = self.plot_feature_weights()
                if fig:
                    fig.savefig(os.path.join(temp_dir, "feature_weights.png"))
                    mlflow.log_artifact(os.path.join(temp_dir, "feature_weights.png"))

            # Check if it is regression or classification experiment
            # INSERT_YOUR_CODE
            # Precompute predictions for train and holdout to avoid redundant calls
            y_pred_train = self.predict(self.X_train)
            y_pred_holdout = self.predict(self.X_holdout) if self.X_holdout is not None else None

            task_type = self.experiment.get_type()
            if task_type == "classification":
                # log plot_confusion_matrix
                fig = self.plot_confusion_matrix(self.y_train, y_pred_train, "train")
                if fig:
                    fig.savefig(os.path.join(temp_dir, "train_confusion_matrix.png"))
                    mlflow.log_artifact(os.path.join(temp_dir, "train_confusion_matrix.png"))
                # log plot_confusion_matrix
                if y_pred_holdout is not None:
                    fig = self.plot_confusion_matrix(self.y_holdout, y_pred_holdout, "holdout")
                    if fig:
                        fig.savefig(os.path.join(temp_dir, "holdout_confusion_matrix.png"))
                        mlflow.log_artifact(os.path.join(temp_dir, "holdout_confusion_matrix.png"))
            else:
                # log plot_regression
                fig = self.plot_regression(self.y_train, y_pred_train, "train")
                if fig:
                    fig.savefig(os.path.join(temp_dir, "train_regression.png"))
                    mlflow.log_artifact(os.path.join(temp_dir, "train_regression.png"))

                # log plot_distribution
                fig = self.plot_distribution(self.y_train, y_pred_train, "train")
                if fig:
                    fig.savefig(os.path.join(temp_dir, "train_distribution.png"))
                    mlflow.log_artifact(os.path.join(temp_dir, "train_distribution.png"))

                if y_pred_holdout is not None:
                    # log plot_regression
                    fig = self.plot_regression(self.y_holdout, y_pred_holdout, "holdout")
                    if fig:
                        fig.savefig(os.path.join(temp_dir, "holdout_regression.png"))
                        mlflow.log_artifact(os.path.join(temp_dir, "holdout_regression.png"))

                    # log plot_distribution
                    fig = self.plot_distribution(self.y_holdout, y_pred_holdout, "holdout")
                    if fig:
                        fig.savefig(os.path.join(temp_dir, "holdout_distribution.png"))
                        mlflow.log_artifact(os.path.join(temp_dir, "holdout_distribution.png"))

        plt.close('all')

class Runner:
    """Execute ML experiments with full lifecycle management.

    Responsibilities:
    - Load datasets
    - Build preprocessing pipelines
    - Handle train/validation/test splits
    - Coordinate ModelRunner instances for each model

    Parameters
    ----------
    experiment : Experiment
        Experiment specification to run
    verbose : bool, optional
        Whether to print progress information, by default True
    """

    def __init__(self, experiment: Experiment, verbose: bool = True):
        self.experiment = experiment
        self.verbose = verbose
        self.config = experiment.config

        # Data storage
        self.dataset: pd.DataFrame | None = None
        self.X_train: pd.DataFrame | None = None
        self.y_train: pd.Series | None = None
        self.X_holdout: pd.DataFrame | None = None
        self.y_holdout: pd.Series | None = None

        # Feature tracking
        self.numerical_features: list[str] = []
        self.categorical_features: list[str] = []
        self.all_features: list[str] = []

        # ModelRunner instances
        self.model_runners: list[ModelRunner] = []

        self.best_model: ModelRunner | None = None
        self.best_model_score: str | None = None

    def get_models(self) -> list[ModelRunner]:
        return self.model_runners

    def get_best_model(self) -> ModelRunner | None:
        return self.best_model

    def get_best_model_score(self) -> float:
        return self.best_model_score

    def _log(self, message: str) -> None:
        """Print message if verbose is enabled."""
        if self.verbose:
            print(f"[Runner] {message}")        # noqa: T201

    def _load_dataset(self) -> pd.DataFrame:
        """Load dataset specified in experiment.

        Also infers experiment type from target column if not specified in configuration.

        Returns
        -------
        pd.DataFrame
            Loaded dataset
        """
        self._log(f"Loading dataset: {self.experiment.spec.dataset}")
        dataset = Dataset(self.experiment.spec.dataset, self.config)
        self.dataset = dataset.read_pandas()
        self._log(
            f"Dataset loaded: {len(self.dataset)} rows, {len(self.dataset.columns)} columns"
        )

        # Infer experiment type from target if not specified
        if self.experiment.spec.type is None:
            inferred_type = self.experiment.infer_type_from_dataset(self.dataset)
            self._log(
                f"Inferred experiment type: {inferred_type} (from target column dtype)"
            )
        else:
            self._log(f"Using configured experiment type: {self.experiment.spec.type}")

        return self.dataset

    def _infer_column_types(self, df: pd.DataFrame) -> tuple[list[str], list[str]]:
        """Infer which columns are numerical vs categorical based on dtypes.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to infer from
        columns : List[str]
            Columns to classify

        Returns
        -------
        Tuple[List[str], List[str]]
            Lists of (numerical_features, categorical_features)
        """
        # Fill numerical and categorical list from spec (if available)
        feature_name = getattr(self.experiment.spec, "features", None)
        if feature_name and hasattr(self, "config"):
            try:
                feature = Feature(feature_name, self.config)
                # Add columns from 'numerical' and 'categorical' in spec if present
                numerical = (
                    list(feature.spec.numerical)
                    if hasattr(feature.spec, "numerical") and feature.spec.numerical
                    else []
                )
                categorical = (
                    list(feature.spec.categorical)
                    if hasattr(feature.spec, "categorical") and feature.spec.categorical
                    else []
                )
                column = (
                    list(feature.spec.column)
                    if hasattr(feature.spec, "column") and feature.spec.column
                    else []
                )
            except Exception:
                # Fall back to type inference if Feature cannot be constructed
                numerical = []
                categorical = []
                column = []
        else:
            numerical = []
            categorical = []
            column = []

        # handle a special keywork __all__ in the column list
        if "__all__" in column:
            column = [
                col
                for col in df.columns
                if col not in numerical and col not in categorical
            ]

        # just to be in safe side, remove "target" column"
        target = self.experiment.spec.target
        column = [col for col in column if col != target]
        numerical = [col for col in numerical if col not in column]
        categorical = [col for col in categorical if col not in column]

        # Check that all specified numerical and categorical columns exist in df
        missing_numerical = [col for col in numerical if col not in df.columns]
        missing_categorical = [col for col in categorical if col not in df.columns]
        if missing_numerical:
            self._log(
                f"Warning: The following numerical feature(s) are not in the dataset: {missing_numerical}"
            )
            numerical = [col for col in numerical if col in df.columns]
        if missing_categorical:
            self._log(
                f"Warning: The following categorical feature(s) are not in the dataset: {missing_categorical}"
            )
            categorical = [col for col in categorical if col in df.columns]

        # Process columns from the 'column' parameter (excluding those already specified)
        for col in column:
            if col not in df.columns:
                self._log(f"Warning: Column '{col}' not found in dataset")
                continue
            if col in numerical or col in categorical:
                continue

            dtype = df[col].dtype
            if pd.api.types.is_numeric_dtype(dtype):
                numerical.append(col)
            else:
                categorical.append(col)

        return numerical, categorical

    def _drop_outliers(self) -> None:
        """Detect outliers in numeric features and target, and mark them in the dataset.

        This method:
        - Detects outliers using Z-score method (default threshold: 3.0 standard deviations)
        - Sets 'is_outlier' boolean column in the dataset dataframe
        - Logs the number of records before and after outlier removal
        - Only processes numeric features and target column

        The 'is_outlier' column is always created, even if outlier removal is disabled
        (drop_outliers is None or 0.0). Rows with is_outlier==True will be excluded
        from train/holdout splits in _split_data() and data_load().
        """
        if self.dataset is None:
            raise RuntimeError("Dataset must be loaded before dropping outliers")  # noqa: TRY003

        # Get drop_outliers threshold from experiment config
        threshold = self.experiment.spec.drop_outliers

        # Initialize is_outlier column to False
        self.dataset["is_outlier"] = False

        # If threshold is None or 0.0, outlier detection is disabled
        if threshold is None or threshold == 0.0:
            self._log("Outlier detection disabled (drop_outliers is None or 0.0)")
            return

        self._log(f"Detecting outliers using Z-score threshold: {threshold}")

        # Get numeric columns (features + target)
        target = self.experiment.spec.target
        numeric_columns = []

        # Add numeric features
        if hasattr(self, "numerical_features") and self.numerical_features:
            numeric_columns.extend(self.numerical_features)

        # Add target if it's numeric
        if target in self.dataset.columns and pd.api.types.is_numeric_dtype(
            self.dataset[target].dtype
        ):
            numeric_columns.append(target)

        # Remove duplicates and ensure columns exist
        numeric_columns = list({
            col for col in numeric_columns if col in self.dataset.columns
        })

        if not numeric_columns:
            self._log("No numeric columns found for outlier detection")
            return

        self._log(f"Checking outliers in columns: {numeric_columns}")

        # Record initial number of rows
        initial_count = len(self.dataset)

        # Calculate Z-scores for each numeric column
        outlier_mask = pd.Series(False, index=self.dataset.index)

        for col in numeric_columns:
            # Calculate Z-scores: (value - mean) / std
            col_mean = self.dataset[col].mean()
            col_std = self.dataset[col].std()

            # Skip if std is 0 (constant column) or NaN
            if col_std == 0 or pd.isna(col_std):
                self._log(f"  {col}: skipped (constant or NaN std)")
                continue

            z_scores = np.abs((self.dataset[col] - col_mean) / col_std)
            # Mark as outlier if Z-score exceeds threshold
            col_outliers = z_scores > threshold
            outlier_mask |= col_outliers

            # Log column-specific outlier counts
            col_outlier_count = col_outliers.sum()
            if col_outlier_count > 0:
                self._log(f"  {col}: {col_outlier_count} outliers detected")

        # Set is_outlier column
        self.dataset["is_outlier"] = outlier_mask

        # Count total outliers
        total_outliers = outlier_mask.sum()
        final_count = initial_count - total_outliers

        # Log results
        self._log("Outlier detection complete:")
        self._log(f"  Initial records: {initial_count}")
        self._log(
            f"  Outliers detected: {total_outliers} ({total_outliers / initial_count * 100:.2f}%)"
        )
        self._log(f"  Records after removal: {final_count}")

    def _prepare_features(self) -> tuple[list[str], list[str]]:
        """Prepare and classify features from feature set.

        Collects features from feature specifications and classifies them
        as numerical or categorical. If feature specifications don't include
        types, infers from DataFrame dtypes.

        Returns
        -------
        Tuple[List[str], List[str]]
            Lists of (numerical_features, categorical_features)
        """
        if self.dataset is None:
            raise RuntimeError("Dataset must be loaded before preparing features")  # noqa: TRY003

        self._log("Preparing features")

        # Collect features from feature specifications
        numerical_cols, categorical_cols = self._infer_column_types(self.dataset)

        # If no explicit type specifications, infer from all feature columns
        all_feature_cols = numerical_cols + categorical_cols

        # Remove target column if present
        target = self.experiment.spec.target
        # Check if target accidentally appears in feature columns (should not occur)
        if (
            target in all_feature_cols
            or target in numerical_cols
            or target in categorical_cols
        ):
            raise ValueError(  # noqa: TRY003
                f"Target column '{target}' was included in the feature set"
            )

        if not (numerical_cols or categorical_cols):
            raise ValueError(  # noqa: TRY003
                "No features were found in the feature set. At least one feature must be specified."
            )

        self.numerical_features = numerical_cols
        self.categorical_features = categorical_cols
        self.all_features = numerical_cols + categorical_cols

        # Convert column types: categorical to string, numerical to numeric
        self.dataset = self._convert_column_types(self.dataset)

        self._log(f"Numerical features ({len(numerical_cols)}): {numerical_cols}")
        self._log(f"Categorical features ({len(categorical_cols)}): {categorical_cols}")

        return numerical_cols, categorical_cols

    def _convert_column_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert categorical columns to string and numerical columns to numeric types.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to convert column types for

        Returns
        -------
        pd.DataFrame
            DataFrame with converted column types
        """
        df = df.copy()

        # Convert categorical columns to string
        if self.categorical_features:
            for col in self.categorical_features:
                if col in df.columns:
                    df[col] = df[col].astype(str)

        # Convert numerical columns to numeric (handles mixed types)
        if self.numerical_features:
            for col in self.numerical_features:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def _get_grouping_values(self, df: pd.DataFrame, name: str) -> pd.Series:
        """Get grouping values from column or index.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to extract grouping values from
        name : str
            Name of the column or index to use for grouping

        Returns
        -------
        pd.Series
            Series containing grouping values aligned with df.index

        Raises
        ------
        ValueError
            If the name is not found in columns or index name
        """
        if name in df.columns:
            return df[name]
        if df.index.name is not None and df.index.name == name:
            # Convert index to Series with same index as df for alignment
            return pd.Series(df.index, index=df.index, name=name)
        index_info = (
            f"Index name: {df.index.name}" if df.index.name else "Index has no name"
        )
        raise ValueError(  # noqa: TRY003
            f"Grouping column/index '{name}' not found in dataset. "
            f"Available columns: {list(df.columns)}, "
            f"{index_info}"
        )

    def _split_data(self) -> None:
        """Split data into training and hold-out sets.

        Respects:
        - hold_out configuration for creating a separate hold-out set
        - do_not_split_by for grouped splitting (prevents data leakage)

        Adds a binary column 'is_holdout' to self.dataset indicating hold-out samples.
        """
        if self.dataset is None:
            raise RuntimeError("Dataset must be loaded before splitting")  # noqa: TRY003

        self._log("Splitting data")

        target = self.experiment.spec.target
        if target not in self.dataset.columns:
            raise ValueError(f"Target column '{target}' not found in dataset")  # noqa: TRY003

        df = self.dataset.copy()
        # Initialize hold-out indicator column
        df["is_holdout"] = False

        # Filter out outliers before splitting
        if "is_outlier" in df.columns:
            outlier_mask = df["is_outlier"]
            outliers_count = outlier_mask.sum()
            if outliers_count > 0:
                self._log(
                    f"Excluding {outliers_count} outlier rows from train/holdout splits"
                )
                df = df[~outlier_mask].copy()
            else:
                self._log("No outliers to exclude from splits")
        else:
            # If is_outlier column doesn't exist, create it as False
            df["is_outlier"] = False

        # Separate features and target
        y = df[target]
        X = df[self.all_features]  # noqa: N806

        # Handle hold-out set if specified
        hold_out_config = self.experiment.spec.hold_out
        hold_out_fraction = (
            hold_out_config.get("fraction", 0.0) if hold_out_config else 0.0
        )

        do_not_split_by = self.experiment.spec.do_not_split_by

        if hold_out_fraction > 0:
            self._log(f"Creating hold-out set: {hold_out_fraction:.1%}")
            hold_out_random_state = hold_out_config.get("random_state", 42)

            # Check if we need grouped splitting for hold-out
            if do_not_split_by:
                # Create composite grouping key from multiple columns/index if needed
                # GroupShuffleSplit needs a single array-like, so we combine multiple columns
                if len(do_not_split_by) == 1:
                    groups = self._get_grouping_values(df, do_not_split_by[0])
                else:
                    # Create a composite group identifier from multiple columns/index
                    # Get each grouping value (column or index)
                    group_series = [
                        self._get_grouping_values(df, name) for name in do_not_split_by
                    ]
                    # Combine into DataFrame for easy joining
                    group_df = pd.concat(group_series, axis=1)
                    # Convert to string tuples to create unique group identifiers
                    groups = group_df.apply(
                        lambda row: "_".join(str(val) for val in row), axis=1
                    )
                splitter = GroupShuffleSplit(
                    n_splits=1,
                    test_size=hold_out_fraction,
                    random_state=hold_out_random_state,
                )
                train_idx, holdout_idx = next(splitter.split(X, y, groups=groups))
                # Split data using positional indices
                self.X_train = X.iloc[train_idx].copy()
                self.y_train = y.iloc[train_idx].copy()
                self.X_holdout = X.iloc[holdout_idx].copy()
                self.y_holdout = y.iloc[holdout_idx].copy()
                # Mark hold-out samples using original DataFrame indices
                holdout_original_idx = X.index[holdout_idx]
                df.loc[holdout_original_idx, "is_holdout"] = True
            else:
                # Use train_test_split for non-grouped splitting
                X_train_temp, X_holdout_temp, y_train_temp, y_holdout_temp = (  # noqa: N806
                    train_test_split(
                        X,
                        y,
                        test_size=hold_out_fraction,
                        random_state=hold_out_random_state,
                        shuffle=True,
                    )
                )
                # Assign split data
                self.X_train = X_train_temp.copy()
                self.y_train = y_train_temp.copy()
                self.X_holdout = X_holdout_temp.copy()
                self.y_holdout = y_holdout_temp.copy()
                # Mark hold-out samples in the dataset
                df.loc[X_holdout_temp.index, "is_holdout"] = True

            self._log(f"Hold-out set size: {len(self.X_holdout)}")
        else:
            # No hold-out split, all data is training
            self.X_train = X.copy()
            self.y_train = y.copy()
            self.X_holdout = None
            self.y_holdout = None

        # Update self.dataset with the hold-out indicator (but keep original rows including outliers)
        # Only update is_holdout column, don't filter out outliers from self.dataset
        # Use direct assignment to avoid deprecation warning
        # Initialize is_holdout column to False
        self.dataset["is_holdout"] = False
        # Then update based on df
        for idx in df.index:
            self.dataset.loc[idx, "is_holdout"] = df.loc[idx, "is_holdout"]

        self._log(f"Train set size: {len(self.X_train)}")
        if self.X_holdout is not None:
            self._log(f"Hold-out set size: {len(self.X_holdout)}")

    def data_save(self, filepath: str | None = None) -> str:
        """Save self.dataset to a parquet file.

        Parameters
        ----------
        filepath : str, optional
            Path where to save the parquet file. If None, generates a default
            filename based on experiment name.

        Returns
        -------
        str
            Path to the saved parquet file

        Raises
        ------
        RuntimeError
            If dataset is None (not loaded yet)
        """
        if self.dataset is None:
            raise RuntimeError("Dataset must be loaded before saving")  # noqa: TRY003

        if filepath is None:
            # Generate default filename based on experiment name
            filepath = f"{self.experiment.name}_dataset.parquet"

        self._log(f"Saving dataset to {filepath}")
        self.dataset.to_parquet(filepath, index=False)
        self._log(
            f"Dataset saved successfully: {len(self.dataset)} rows, {len(self.dataset.columns)} columns"
        )

        return filepath

    def data_load(self, filepath: str) -> None:
        """Load dataset from parquet file, prepare features, and split based on is_holdout column.

        This method loads a previously saved dataset (from data_save), prepares features,
        and recreates the train/holdout splits based on the is_holdout column. The result
        is equivalent to calling data_preparation + data_save, then loading the saved file.

        Parameters
        ----------
        filepath : str
            Path to the parquet file to load

        Raises
        ------
        FileNotFoundError
            If the parquet file doesn't exist
        ValueError
            If required columns (target, is_holdout) are missing from the loaded dataset
        """
        self._log(f"Loading dataset from {filepath}")

        # Load dataset from parquet
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Parquet file not found: {filepath}")  # noqa: TRY003

        self.dataset = pd.read_parquet(filepath)
        self._log(
            f"Dataset loaded: {len(self.dataset)} rows, {len(self.dataset.columns)} columns"
        )

        # Verify is_holdout column exists
        if "is_holdout" not in self.dataset.columns:
            raise ValueError(  # noqa: TRY003
                "Dataset must contain 'is_holdout' column. "
                "Please ensure the file was saved using data_save() after data_preparation()."
            )

        # Step 1: Prepare features (classify as numerical/categorical)
        self._prepare_features()

        # Step 2: Split data based on is_holdout column
        target = self.experiment.spec.target
        if target not in self.dataset.columns:
            raise ValueError(f"Target column '{target}' not found in dataset")  # noqa: TRY003

        df = self.dataset.copy()

        # Filter out outliers before splitting
        if "is_outlier" in df.columns:
            outlier_mask = df["is_outlier"]
            outliers_count = outlier_mask.sum()
            if outliers_count > 0:
                self._log(
                    f"Excluding {outliers_count} outlier rows from train/holdout splits"
                )
                df = df[~outlier_mask].copy()
            else:
                self._log("No outliers to exclude from splits")
        else:
            # If is_outlier column doesn't exist, create it as False
            df["is_outlier"] = False

        # Separate features and target
        y = df[target]
        X = df[self.all_features]  # noqa: N806

        # Split based on is_holdout column
        is_holdout = df["is_holdout"]

        # Training set: rows where is_holdout is False
        train_mask = ~is_holdout
        self.X_train = X.loc[train_mask].copy()
        self.y_train = y.loc[train_mask].copy()

        # Holdout set: rows where is_holdout is True
        holdout_mask = is_holdout
        if holdout_mask.any():
            self.X_holdout = X.loc[holdout_mask].copy()
            self.y_holdout = y.loc[holdout_mask].copy()
            self._log(f"Hold-out set size: {len(self.X_holdout)}")
        else:
            self.X_holdout = None
            self.y_holdout = None
            self._log("No hold-out set found in loaded dataset")

        self._log(f"Train set size: {len(self.X_train)}")
        if self.X_holdout is not None:
            self._log(f"Hold-out set size: {len(self.X_holdout)}")

    def data_preparation(self) -> None:
        """Prepare data for the experiment.

        This method performs the initial data preparation steps:
        1. Load dataset
        2. Prepare features (classify as numerical/categorical)
        3. Split data into train/validation/test sets
        """
        self._log("Preparing data for experiment")

        # Step 1: Load dataset
        self._load_dataset()

        # Step 2: Prepare features (classify as numerical/categorical)
        self._prepare_features()

        # Step 3: Drop outliers
        self._drop_outliers()

        # Step 4: Split data
        self._split_data()

    def get_config(self) -> dict[str, Any]:
        """Return dictionary similar to original YAML config with all fields populated.

        Includes inferred feature types (numerical/categorical) and experiment type
        (regression/classification). The returned dictionary has the same structure
        as the original YAML configuration file.

        Returns
        -------
        Dict[str, Any]
            Dictionary with same structure as YAML config, with inferred fields populated.
            Includes:
            - All original config sections (datasets, features, models, experiments, etc.)
            - Inferred experiment type in experiments section
            - Inferred feature types (numerical/categorical) in features section

        Raises
        ------
        RuntimeError
            If features have not been prepared yet (need to call prepare_features() first)
        """
        # Start with a deep copy of the original config
        config_dict = deepcopy(self.config.to_dict())

        # Get experiment name
        exp_name = self.experiment.name

        # Update experiment section with inferred type
        if "experiments" in config_dict and exp_name in config_dict["experiments"]:
            exp_dict = config_dict["experiments"][exp_name]
            if isinstance(exp_dict, dict):
                # Add inferred type if available (either configured or inferred)
                inferred_type = self.experiment.get_type()
                if inferred_type is not None:
                    exp_dict["type"] = inferred_type

        # Update features section with inferred types
        feature_name = self.experiment.spec.features
        if "features" in config_dict and feature_name in config_dict["features"]:
            feature_dict = config_dict["features"][feature_name]
            if isinstance(feature_dict, dict):
                # Check if features have been prepared
                if not hasattr(self, "numerical_features") or not hasattr(
                    self, "categorical_features"
                ):
                    raise RuntimeError(  # noqa: TRY003
                        "Features have not been prepared yet. "
                        "Call prepare_features() or run() first before calling get_config()."
                    )

                # If features have been prepared, update with inferred types
                # Remove 'columns' field if present (replaced by numerical/categorical)
                if "columns" in feature_dict:
                    # Check if it was using __all__ - if so, we've expanded it
                    # Remove columns key as we've inferred types from it
                    feature_dict.pop("columns")
                    # If it was just __all__, we can note that it was inferred
                    # Otherwise, we've inferred types from the columns list

                # Update with inferred types
                feature_dict["numerical"] = self.numerical_features.copy()
                feature_dict["categorical"] = self.categorical_features.copy()

                # Ensure lists are not empty (remove empty lists if both are empty)
                # But keep them if they exist - empty lists are valid

        return config_dict

    def run(self, skip_mlflow: bool = False) -> dict[str, Any]:
        """Execute the complete experiment workflow.

        Parameters
        ----------
        skip_mlflow : bool, optional
            Whether to skip MLflow logging, by default False
            If True, the experiment will be run without logging to MLflow
        Returns
        -------
        Dict[str, Any]
            Results dictionary containing metrics and artifacts for all models
        """
        self._log(f"Starting experiment: {self.experiment.name}")

        # Check if data is already prepared
        if self.X_train is None:
            self.data_preparation()

        # Step 4: Create ModelRunner instances for each model
        if not self.numerical_features and not self.categorical_features:
            raise RuntimeError("No features prepared before creating ModelRunners")  # noqa: TRY003
        if self.X_train is None or self.y_train is None:
            raise RuntimeError("Data must be split before creating ModelRunners")  # noqa: TRY003

        self.model_runners = []
        for model_name in self.experiment.spec.models:
            model_runner = ModelRunner(
                model_name=model_name,
                numerical_features=self.numerical_features,
                categorical_features=self.categorical_features,
                experiment=self.experiment,
                X_train=self.X_train,
                y_train=self.y_train,
                X_holdout=self.X_holdout,
                y_holdout=self.y_holdout,
                verbose=self.verbose,
            )
            self.model_runners.append(model_runner)

        # Step 5: Run each ModelRunner
        results = {}
        results["models"] = {}
        results["best_model"] = None
        results["best_model_score"] = None

        best_model_score = float("-inf")
        for model_runner in self.model_runners:
            self._log(f"\n{'=' * 60}")
            self._log(f"Processing model: {model_runner.model_name}")
            self._log(f"{'=' * 60}")

            model_score = model_runner.fit_and_evaluate()
            self._log(f"Model {model_runner.model_name} score: {model_score:.6f}")
            if model_score > best_model_score:
                best_model_score = model_score
                self.best_model = model_runner
            results["models"][model_runner.model_name] = model_runner.metrics

        self.best_model_score = best_model_score
        results["best_model"] = self.best_model.model_name
        results["best_model_score"] = self.best_model_score

        self._log(f"\n{'=' * 60}")
        self._log("Experiment completed successfully!")
        self._log(f"Best model: {self.best_model.model_name}")
        self._log(f"Best model score: {self.best_model_score:.6f}")
        self._log(f"{'=' * 60}")

        if not skip_mlflow:
            self.mlflow_store()

        return results

    def mlflow_store(self) -> None:
        """
        Store the experiment in MLflow.
        """

        mlflow_config = MlflowConf(self.config)
        if not mlflow_config.is_enabled():
            return

        mlflow_experiment_name = mlflow_config.get_name(self.experiment.name)
        if mlflow_config.get_type() == "databricks":
            mlflow.set_tracking_uri("databricks")
            if not mlflow_experiment_name.startswith("/Shared/"):
                mlflow_experiment_name = f"/Shared/{mlflow_experiment_name}"
            mlflow.set_experiment(mlflow_experiment_name)
        else:
            # Only set tracking URI if not already set (e.g., by test fixtures)
            current_uri = mlflow.get_tracking_uri()
            if current_uri is None or current_uri == "":
                mlflow.set_tracking_uri("sqlite:///mlflow.db")
            mlflow.set_experiment(mlflow_experiment_name)

        # Get experiment description
        experiment_description = self.experiment.spec.description or ""

        with mlflow.start_run(description=experiment_description) as parent_run:
            parent_run_id = parent_run.info.run_id

            models = self.get_models()
            if len(models) > 1:
                # log multiple models as nested run
                for model in models:

                    if self.best_model == model :
                        name = f"BEST-{model.model_name}"
                    else:
                        name = model.model_name 

                    with mlflow.start_run(run_name=name, nested=True) as child_run:
                        model.mlflow_store()
            
            # log the best model as parent run
            self.best_model.mlflow_store()

            # add addtional parameters to the parent run
            mlflow.log_param("experiment_name", self.experiment.name)
            mlflow.log_param("experiment_type", self.experiment.get_type())
            if experiment_description:
                mlflow.log_param("experiment_description", experiment_description)

            # add tags to the parent run
            mlflow.set_tags(mlflow_config.get_tags())

            # store experiment config into temp directory and upload it to mlflow
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = os.path.join(temp_dir, "experiment_config.yaml")
                config_dict = self.get_config()
                with open(config_path, 'w') as f:
                    yaml.dump(config_dict, f, sort_keys=False, default_flow_style=False)
                mlflow.log_artifact(config_path)

__all__ = ["Runner", "ModelRunner"]
