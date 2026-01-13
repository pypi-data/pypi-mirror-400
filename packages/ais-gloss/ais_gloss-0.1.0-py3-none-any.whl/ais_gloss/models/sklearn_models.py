from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
    AdaBoostRegressor, AdaBoostClassifier
)
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.neural_network import MLPRegressor, MLPClassifier


def get_regression_models():
    """Get dictionary of regression models"""
    models = {
        'LinearRegression': LinearRegression(),
        'Ridge': Ridge(),
        'Lasso': Lasso(),
        'DecisionTree': DecisionTreeRegressor(random_state=42),
        'RandomForest': RandomForestRegressor(random_state=42, n_estimators=100),
        'GradientBoosting': GradientBoostingRegressor(random_state=42, n_estimators=100),
        'AdaBoost': AdaBoostRegressor(random_state=42, n_estimators=100),
        'SVR': SVR(),
        'KNN': KNeighborsRegressor(),
        'MLP': MLPRegressor(random_state=42, max_iter=1000)
    }
    return models


def get_classification_models():
    """Get dictionary of classification models"""
    models = {
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'DecisionTree': DecisionTreeClassifier(random_state=42),
        'RandomForest': RandomForestClassifier(random_state=42, n_estimators=100),
        'GradientBoosting': GradientBoostingClassifier(random_state=42, n_estimators=100),
        'AdaBoost': AdaBoostClassifier(random_state=42, n_estimators=100),
        'SVC': SVC(probability=True, random_state=42),
        'KNN': KNeighborsClassifier(),
        'MLP': MLPClassifier(random_state=42, max_iter=1000)
    }
    return models


def get_param_grid_regression(model_name):
    """Get parameter grid for regression models"""
    param_grids = {
        'Ridge': {'alpha': [0.1, 1.0, 10.0]},
        'Lasso': {'alpha': [0.1, 1.0, 10.0]},
        'DecisionTree': {'max_depth': [3, 5, 10, None], 'min_samples_split': [2, 5, 10]},
        'RandomForest': {'n_estimators': [50, 100, 200], 'max_depth': [5, 10, None]},
        'GradientBoosting': {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 0.2]},
        'SVR': {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']},
        'KNN': {'n_neighbors': [3, 5, 7, 9]},
        'MLP': {'hidden_layer_sizes': [(50,), (100,), (50, 50)], 'alpha': [0.0001, 0.001, 0.01]}
    }
    return param_grids.get(model_name, {})


def get_param_grid_classification(model_name):
    """Get parameter grid for classification models"""
    param_grids = {
        'LogisticRegression': {'C': [0.1, 1.0, 10.0]},
        'DecisionTree': {'max_depth': [3, 5, 10, None], 'min_samples_split': [2, 5, 10]},
        'RandomForest': {'n_estimators': [50, 100, 200], 'max_depth': [5, 10, None]},
        'GradientBoosting': {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 0.2]},
        'SVC': {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear']},
        'KNN': {'n_neighbors': [3, 5, 7, 9]},
        'MLP': {'hidden_layer_sizes': [(50,), (100,), (50, 50)], 'alpha': [0.0001, 0.001, 0.01]}
    }
    return param_grids.get(model_name, {})
