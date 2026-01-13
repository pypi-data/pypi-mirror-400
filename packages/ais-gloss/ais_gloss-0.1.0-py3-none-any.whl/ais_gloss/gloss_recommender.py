import numpy as np
import pandas as pd
from itertools import product
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from tqdm import tqdm

from .utils.logger import ExperimentLogger
from .visualization import Visualizer


class GLOSSRecommender:
    """GLOSS Recommendation Algorithm"""

    def __init__(self, model_func=None, y_comparator=None,
                 log_dir='./logs', output_dir='./outputs'):
        """
        Initialize GLOSS Recommender

        Args:
            model_func: Function that takes X and returns y predictions
            y_comparator: Function that takes (y1, y2) and returns True if y1 is better than y2
            log_dir: Directory for log files
            output_dir: Directory for outputs
        """
        self.model_func = model_func
        self.y_comparator = y_comparator

        self.logger = ExperimentLogger(log_dir, "gloss_recommender")
        self.visualizer = Visualizer(output_dir)

        self.X_grid = None
        self.y_pred = None
        self.recommendations = {}

    def set_model(self, model_func):
        """Set the prediction model"""
        self.model_func = model_func

    def set_comparator(self, y_comparator):
        """Set the y comparator function"""
        self.y_comparator = y_comparator

    def generate_grid(self, x_ranges):
        """
        Generate grid of input values

        Args:
            x_ranges: Dictionary or list of tuples
                     Format: {'x1': (min, max, step), 'x2': [val1, val2, val3], ...}
                     or [(min, max, step), [val1, val2], ...]
        """
        self.logger.info("Generating input grid...")

        grid_values = []

        if isinstance(x_ranges, dict):
            for key, value in x_ranges.items():
                if isinstance(value, tuple) and len(value) == 3:
                    # (min, max, step)
                    grid_values.append(np.arange(value[0], value[1] + value[2], value[2]))
                else:
                    # List of values
                    grid_values.append(np.array(value))
        else:
            for value in x_ranges:
                if isinstance(value, tuple) and len(value) == 3:
                    grid_values.append(np.arange(value[0], value[1] + value[2], value[2]))
                else:
                    grid_values.append(np.array(value))

        # Generate all combinations
        grid_combinations = list(product(*grid_values))
        self.X_grid = np.array(grid_combinations)

        self.logger.info(f"Generated grid with {len(self.X_grid)} points")

        return self.X_grid

    def predict_grid(self):
        """Predict y values for all grid points"""
        if self.model_func is None:
            raise ValueError("Model function not set. Use set_model() or provide during initialization.")

        self.logger.info("Predicting y values for grid points...")

        self.y_pred = []
        for x in tqdm(self.X_grid, desc="Predicting"):
            y = self.model_func(x.reshape(1, -1))
            self.y_pred.append(y)

        self.y_pred = np.array(self.y_pred).squeeze()

        self.logger.info(f"Predictions completed. y shape: {self.y_pred.shape}")

        return self.y_pred

    def find_global_optima(self, n_global=5):
        """
        Find global optima points

        Args:
            n_global: Number of global optima to return
        """
        if self.y_comparator is None:
            raise ValueError("Y comparator not set. Use set_comparator() or provide during initialization.")

        self.logger.info(f"Finding top {n_global} global optima...")

        # Sort points by y value using comparator
        sorted_indices = self._sort_by_comparator()

        global_indices = sorted_indices[:n_global]
        self.recommendations['global'] = {
            'indices': global_indices,
            'X': self.X_grid[global_indices],
            'y': self.y_pred[global_indices]
        }

        self.logger.info(f"Found {len(global_indices)} global optima")

        return self.recommendations['global']

    def find_local_optima(self, n_local=5, radius=None):
        """
        Find local optima points

        Args:
            n_local: Number of local optima to return
            radius: Radius for local neighborhood (if None, auto-calculated)
        """
        self.logger.info(f"Finding {n_local} local optima...")

        if radius is None:
            # Auto-calculate radius based on grid spacing
            distances = []
            for i in range(min(100, len(self.X_grid))):
                for j in range(i + 1, min(100, len(self.X_grid))):
                    distances.append(np.linalg.norm(self.X_grid[i] - self.X_grid[j]))
            radius = np.median(distances) * 2

        local_optima_indices = []

        for i in range(len(self.X_grid)):
            # Find neighbors
            distances = np.linalg.norm(self.X_grid - self.X_grid[i], axis=1)
            neighbors = np.where((distances < radius) & (distances > 0))[0]

            if len(neighbors) == 0:
                continue

            # Check if this point is better than all neighbors
            is_local_optimum = True
            for neighbor in neighbors:
                if not self._compare_points(i, neighbor):
                    is_local_optimum = False
                    break

            if is_local_optimum:
                local_optima_indices.append(i)

        # Remove global optima from local optima
        if 'global' in self.recommendations:
            global_set = set(self.recommendations['global']['indices'])
            local_optima_indices = [i for i in local_optima_indices if i not in global_set]

        # Select top n_local
        if len(local_optima_indices) > n_local:
            local_optima_indices = sorted(local_optima_indices,
                                          key=lambda i: self.y_pred[i],
                                          reverse=True)[:n_local]

        self.recommendations['local'] = {
            'indices': local_optima_indices,
            'X': self.X_grid[local_optima_indices],
            'y': self.y_pred[local_optima_indices]
        }

        self.logger.info(f"Found {len(local_optima_indices)} local optima")

        return self.recommendations['local']

    def find_unexplored_regions(self, n_unexplored=5, historical_data=None):
        """
        Find points in unexplored regions

        Args:
            n_unexplored: Number of unexplored points to return
            historical_data: Historical X data (numpy array)
        """
        if historical_data is None or len(historical_data) == 0:
            self.logger.warning("No historical data provided, cannot find unexplored regions")
            return None

        self.logger.info(f"Finding {n_unexplored} unexplored region points...")

        # Calculate distances to nearest historical point
        distances_to_history = []
        for x in self.X_grid:
            min_dist = np.min(np.linalg.norm(historical_data - x, axis=1))
            distances_to_history.append(min_dist)

        distances_to_history = np.array(distances_to_history)

        # Select points farthest from historical data
        unexplored_indices = np.argsort(distances_to_history)[-n_unexplored:]

        self.recommendations['unexplored'] = {
            'indices': unexplored_indices,
            'X': self.X_grid[unexplored_indices],
            'y': self.y_pred[unexplored_indices],
            'distances': distances_to_history[unexplored_indices]
        }

        self.logger.info(f"Found {len(unexplored_indices)} unexplored region points")

        return self.recommendations['unexplored']

    def visualize_landscape(self, dim_reduction='pca', y_index=None):
        """
        Visualize the prediction landscape

        Args:
            dim_reduction: 'pca' or 'tsne'
            y_index: If y is multi-dimensional, specify which dimension to visualize
        """
        self.logger.info(f"Visualizing landscape using {dim_reduction}...")

        # Reduce X to 2D
        if self.X_grid.shape[1] > 2:
            if dim_reduction == 'pca':
                reducer = PCA(n_components=2)
            else:
                reducer = TSNE(n_components=2, random_state=42)

            X_2d = reducer.fit_transform(self.X_grid)
        else:
            X_2d = self.X_grid

        # Handle multi-dimensional y
        if len(self.y_pred.shape) > 1 and self.y_pred.shape[1] > 1:
            if y_index is None:
                # Visualize each dimension
                for i in range(self.y_pred.shape[1]):
                    self.visualizer.plot_landscape(
                        X_2d, self.y_pred[:, i], self.recommendations,
                        title=f"Prediction Landscape - y[{i}]",
                        filename=f"landscape_y{i}.png"
                    )
            else:
                y_values = self.y_pred[:, y_index]
                self.visualizer.plot_landscape(
                    X_2d, y_values, self.recommendations,
                    title=f"Prediction Landscape - y[{y_index}]",
                    filename=f"landscape_y{y_index}.png"
                )
        else:
            y_values = self.y_pred.ravel()
            self.visualizer.plot_landscape(
                X_2d, y_values, self.recommendations,
                title="Prediction Landscape",
                filename="landscape.png"
            )

        self.logger.info("Landscape visualization completed")

    def run_gloss(self, x_ranges, n_global=5, n_local=5, n_unexplored=0,
                  historical_data=None, visualize=True):
        """
        Run complete GLOSS recommendation pipeline

        Args:
            x_ranges: Input ranges for grid generation
            n_global: Number of global optima
            n_local: Number of local optima
            n_unexplored: Number of unexplored region points
            historical_data: Historical X data
            visualize: Whether to create visualizations
        """
        # Generate grid
        self.generate_grid(x_ranges)

        # Predict
        self.predict_grid()

        # Find recommendations
        self.find_global_optima(n_global)
        self.find_local_optima(n_local)

        if n_unexplored > 0 and historical_data is not None:
            self.find_unexplored_regions(n_unexplored, historical_data)

        # Visualize
        if visualize:
            self.visualize_landscape()

        return self.recommendations

    def _sort_by_comparator(self):
        """Sort indices by y values using comparator"""
        indices = list(range(len(self.y_pred)))

        # Bubble sort using comparator (simple but works)
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                if not self._compare_points(indices[i], indices[j]):
                    indices[i], indices[j] = indices[j], indices[i]

        return np.array(indices)

    def _compare_points(self, i, j):
        """Compare two points using y comparator"""
        y1 = self.y_pred[i]
        y2 = self.y_pred[j]
        return self.y_comparator(y1, y2)
