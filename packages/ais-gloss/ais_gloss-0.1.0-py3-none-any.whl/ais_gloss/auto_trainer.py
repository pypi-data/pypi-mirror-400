import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from bayes_opt import BayesianOptimization
import joblib
import os
from tqdm import tqdm

from .models.sklearn_models import (
    get_regression_models, get_classification_models,
    get_param_grid_regression, get_param_grid_classification
)
from .models.pytorch_models import get_pytorch_models
from .utils.logger import ExperimentLogger
from .utils.metrics import calculate_regression_metrics, calculate_classification_metrics
from .visualization import Visualizer


class AutoTrainer:
    """Automated Machine Learning Trainer"""

    def __init__(self, task='regression', metric='R2', n_splits=5,
                 test_size=0.2, use_all_data=False, log_dir='./logs',
                 output_dir='./outputs', random_state=42):
        """
        Initialize AutoTrainer

        Args:
            task: 'regression' or 'classification'
            metric: Metric to optimize ('R2', 'MSE', 'Accuracy', 'F1', etc.)
            n_splits: Number of folds for cross-validation
            test_size: Test set size (if use_all_data=False)
            use_all_data: Whether to use all data for final training
            log_dir: Directory for log files
            output_dir: Directory for outputs
            random_state: Random seed
        """
        self.task = task.lower()
        self.metric = metric
        self.n_splits = n_splits
        self.test_size = test_size
        self.use_all_data = use_all_data
        self.random_state = random_state
        self.output_dir = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.logger = ExperimentLogger(log_dir, f"automl_{task}")
        self.visualizer = Visualizer(output_dir)

        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = None
        self.cv_results = {}

    def load_data(self, csv_path, x_columns, y_columns):
        """
        Load data from CSV file

        Args:
            csv_path: Path to CSV file
            x_columns: List of feature column names
            y_columns: List of target column names (or single column name)
        """
        self.logger.info(f"Loading data from {csv_path}")

        df = pd.read_csv(csv_path)

        if isinstance(x_columns, str):
            x_columns = [x_columns]
        if isinstance(y_columns, str):
            y_columns = [y_columns]

        self.X = df[x_columns].values
        self.y = df[y_columns].values

        if self.y.shape[1] == 1:
            self.y = self.y.ravel()

        self.logger.info(f"Data loaded: X shape {self.X.shape}, y shape {self.y.shape}")

        return self.X, self.y

    def train_all_models(self):
        """Train all models using k-fold cross-validation"""
        self.logger.info(f"Starting {self.n_splits}-fold cross-validation")

        # Get model pool
        if self.task == 'regression':
            sklearn_models = get_regression_models()
            output_dim = 1 if len(self.y.shape) == 1 else self.y.shape[1]
        else:
            sklearn_models = get_classification_models()
            output_dim = len(np.unique(self.y))

        pytorch_models = get_pytorch_models(self.X.shape[1], output_dim, self.task)
        all_models = {**sklearn_models, **pytorch_models}

        # K-Fold cross-validation
        kf = KFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        for model_name, model in tqdm(all_models.items(), desc="Training models"):
            self.logger.info(f"\nTraining {model_name}...")

            fold_metrics = []
            fold_predictions = []
            fold_true_values = []

            for fold, (train_idx, val_idx) in enumerate(kf.split(self.X)):
                X_train, X_val = self.X[train_idx], self.X[val_idx]
                y_train, y_val = self.y[train_idx], self.y[val_idx]

                # Scale features
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_val_scaled = self.scaler.transform(X_val)

                # Train model
                try:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_val_scaled)

                    # Calculate metrics
                    if self.task == 'regression':
                        metrics = calculate_regression_metrics(y_val, y_pred)
                    else:
                        y_pred_proba = model.predict_proba(X_val_scaled) if hasattr(model, 'predict_proba') else None
                        metrics = calculate_classification_metrics(y_val, y_pred, y_pred_proba)

                    fold_metrics.append(metrics)
                    fold_predictions.append(y_pred)
                    fold_true_values.append(y_val)

                except Exception as e:
                    self.logger.error(f"Error training {model_name} on fold {fold}: {str(e)}")
                    continue

            if fold_metrics:
                # Average metrics across folds
                avg_metrics = {k: np.mean([m[k] for m in fold_metrics]) for k in fold_metrics[0].keys()}
                self.cv_results[model_name] = {
                    'metrics': avg_metrics,
                    'fold_metrics': fold_metrics,
                    'predictions': fold_predictions,
                    'true_values': fold_true_values
                }

                self.logger.log_metrics(avg_metrics, prefix=f"{model_name} - ")

                # Visualize predictions
                if self.task == 'regression':
                    self.visualizer.plot_regression_results(
                        np.concatenate(fold_true_values),
                        np.concatenate(fold_predictions),
                        title=f"{model_name} - True vs Predicted",
                        filename=f"{model_name}_predictions.png"
                    )
                else:
                    self.visualizer.plot_confusion_matrix(
                        np.concatenate(fold_true_values),
                        np.concatenate(fold_predictions),
                        title=f"{model_name} - Confusion Matrix",
                        filename=f"{model_name}_confusion.png"
                    )

        # Select best model
        self._select_best_model()

        return self.cv_results

    def _select_best_model(self):
        """Select best model based on metric"""
        self.logger.info(f"\nSelecting best model based on {self.metric}...")

        best_score = -np.inf if self.metric not in ['MSE', 'MAE', 'RMSE'] else np.inf

        for model_name, results in self.cv_results.items():
            score = results['metrics'].get(self.metric, None)

            if score is None:
                continue

            if self.metric in ['MSE', 'MAE', 'RMSE']:
                if score < best_score:
                    best_score = score
                    self.best_model_name = model_name
            else:
                if score > best_score:
                    best_score = score
                    self.best_model_name = model_name

        self.logger.info(f"Best model: {self.best_model_name} with {self.metric}={best_score:.4f}")

    def optimize_hyperparameters(self, method='grid', n_iter=50):
        """
        Optimize hyperparameters of best model

        Args:
            method: 'grid' for GridSearchCV or 'bayes' for Bayesian Optimization
            n_iter: Number of iterations for Bayesian Optimization
        """
        self.logger.info(f"\nOptimizing hyperparameters using {method} search...")

        # Get best model
        if self.task == 'regression':
            models = get_regression_models()
            param_grid = get_param_grid_regression(self.best_model_name)
        else:
            models = get_classification_models()
            param_grid = get_param_grid_classification(self.best_model_name)

        if self.best_model_name not in models or not param_grid:
            self.logger.warning(f"No hyperparameter grid for {self.best_model_name}, skipping optimization")
            return

        model = models[self.best_model_name]

        # Scale data
        X_scaled = self.scaler.fit_transform(self.X)

        if method == 'grid':
            # Grid Search
            scoring = 'neg_mean_squared_error' if self.task == 'regression' else 'accuracy'

            grid_search = GridSearchCV(
                model, param_grid, cv=self.n_splits,
                scoring=scoring, n_jobs=-1, verbose=1
            )
            grid_search.fit(X_scaled, self.y)

            self.best_model = grid_search.best_estimator_
            self.logger.info(f"Best parameters: {grid_search.best_params_}")
            self.logger.info(f"Best score: {grid_search.best_score_:.4f}")

            # Visualize optimization process
            self.visualizer.plot_hyperparameter_optimization(
                grid_search.cv_results_,
                filename=f"{self.best_model_name}_optimization.png"
            )

        else:
            self.logger.warning("Bayesian optimization not fully implemented for all models")
            # For now, use grid search
            self.optimize_hyperparameters(method='grid')

    def train_final_model(self):
        """Train final model on all data or train/test split"""
        self.logger.info("\nTraining final model...")

        if self.best_model is None:
            # If no optimization was done, use best model from CV
            if self.task == 'regression':
                models = get_regression_models()
            else:
                models = get_classification_models()

            self.best_model = models.get(self.best_model_name)

        if self.use_all_data:
            # Train on all data
            X_scaled = self.scaler.fit_transform(self.X)
            self.best_model.fit(X_scaled, self.y)
            self.logger.info("Final model trained on all data")
        else:
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, self.y, test_size=self.test_size, random_state=self.random_state
            )

            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            self.best_model.fit(X_train_scaled, y_train)
            y_pred = self.best_model.predict(X_test_scaled)

            # Evaluate on test set
            if self.task == 'regression':
                test_metrics = calculate_regression_metrics(y_test, y_pred)
                self.visualizer.plot_regression_results(
                    y_test, y_pred,
                    title="Final Model - Test Set Results",
                    filename="final_model_test_results.png"
                )
            else:
                y_pred_proba = self.best_model.predict_proba(X_test_scaled) if hasattr(self.best_model,
                                                                                       'predict_proba') else None
                test_metrics = calculate_classification_metrics(y_test, y_pred, y_pred_proba)
                self.visualizer.plot_confusion_matrix(
                    y_test, y_pred,
                    title="Final Model - Test Set Confusion Matrix",
                    filename="final_model_test_confusion.png"
                )

            self.logger.log_metrics(test_metrics, prefix="Test Set - ")

        # Save model
        model_path = os.path.join(self.output_dir, "best_model.pkl")
        scaler_path = os.path.join(self.output_dir, "scaler.pkl")

        joblib.dump(self.best_model, model_path)
        joblib.dump(self.scaler, scaler_path)

        self.logger.info(f"Model saved to {model_path}")
        self.logger.info(f"Scaler saved to {scaler_path}")

        return self.best_model

    def predict(self, X):
        """Make predictions with trained model"""
        X_scaled = self.scaler.transform(X)
        return self.best_model.predict(X_scaled)

    def get_model_function(self):
        """Return a function that takes X and returns predictions"""

        def model_func(X):
            return self.predict(X)

        return model_func
