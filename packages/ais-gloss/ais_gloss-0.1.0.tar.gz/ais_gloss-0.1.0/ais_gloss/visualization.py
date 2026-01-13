import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix
import os


class Visualizer:
    """Visualization utilities"""

    def __init__(self, output_dir='./outputs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)

    def plot_regression_results(self, y_true, y_pred, title="True vs Predicted", filename=None):
        """Plot regression results"""
        fig, ax = plt.subplots(figsize=(8, 8))

        ax.scatter(y_true, y_pred, alpha=0.5)

        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

        ax.set_xlabel('True Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title(title)
        ax.legend()

        plt.tight_layout()

        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')

        plt.close()

    def plot_confusion_matrix(self, y_true, y_pred, title="Confusion Matrix", filename=None):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)

        ax.set_xlabel('Predicted Label')
        ax.set_ylabel('True Label')
        ax.set_title(title)

        plt.tight_layout()

        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')

        plt.close()

    def plot_hyperparameter_optimization(self, cv_results, filename=None):
        """Plot hyperparameter optimization results"""
        params = cv_results['params']
        scores = cv_results['mean_test_score']

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(range(len(scores)), scores, 'o-')
        ax.set_xlabel('Configuration Index')
        ax.set_ylabel('Score')
        ax.set_title('Hyperparameter Optimization Progress')
        ax.grid(True)

        plt.tight_layout()

        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')

        plt.close()

    def plot_landscape(self, X_2d, y_values, recommendations, title="Prediction Landscape", filename=None):
        """Plot 2D landscape with recommendations"""
        fig, ax = plt.subplots(figsize=(12, 10))

        # Create heatmap
        scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=y_values,
                             cmap='viridis', alpha=0.6, s=50)
        plt.colorbar(scatter, ax=ax, label='Predicted y')

        # Plot recommendations
        if 'global' in recommendations:
            global_X = X_2d[recommendations['global']['indices']]
            ax.scatter(global_X[:, 0], global_X[:, 1],
                       c='red', marker='*', s=500,
                       edgecolors='black', linewidths=2,
                       label='Global Optima', zorder=5)

        if 'local' in recommendations:
            local_X = X_2d[recommendations['local']['indices']]
            ax.scatter(local_X[:, 0], local_X[:, 1],
                       c='orange', marker='s', s=300,
                       edgecolors='black', linewidths=2,
                       label='Local Optima', zorder=5)

        if 'unexplored' in recommendations:
            unexplored_X = X_2d[recommendations['unexplored']['indices']]
            ax.scatter(unexplored_X[:, 0], unexplored_X[:, 1],
                       c='cyan', marker='^', s=300,
                       edgecolors='black', linewidths=2,
                       label='Unexplored Regions', zorder=5)

        ax.set_xlabel('Dimension 1')
        ax.set_ylabel('Dimension 2')
        ax.set_title(title)
        ax.legend()

        plt.tight_layout()

        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')

        plt.close()
