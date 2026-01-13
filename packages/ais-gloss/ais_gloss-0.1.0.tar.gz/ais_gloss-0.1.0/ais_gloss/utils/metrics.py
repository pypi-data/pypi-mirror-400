from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
import numpy as np


def calculate_regression_metrics(y_true, y_pred):
    """Calculate regression metrics"""
    metrics = {
        'MSE': mean_squared_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'MAE': mean_absolute_error(y_true, y_pred),
        'R2': r2_score(y_true, y_pred)
    }
    return metrics


def calculate_classification_metrics(y_true, y_pred, y_pred_proba=None, average='weighted'):
    """Calculate classification metrics"""
    metrics = {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, average=average, zero_division=0),
        'Recall': recall_score(y_true, y_pred, average=average, zero_division=0),
        'F1': f1_score(y_true, y_pred, average=average, zero_division=0)
    }

    # Add AUC if probabilities are provided
    if y_pred_proba is not None:
        try:
            if len(np.unique(y_true)) == 2:
                metrics['AUC'] = roc_auc_score(y_true, y_pred_proba[:, 1])
            else:
                metrics['AUC'] = roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average=average)
        except:
            pass

    return metrics
