import logging
import os
from datetime import datetime


class ExperimentLogger:
    """Logger for tracking experiments and results"""

    def __init__(self, log_dir="./logs", experiment_name=None):
        """
        Initialize logger

        Args:
            log_dir: Directory to save log files
            experiment_name: Name of the experiment
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        if experiment_name is None:
            experiment_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.experiment_name = experiment_name
        self.log_file = os.path.join(log_dir, f"{experiment_name}.log")

        # Setup logger
        self.logger = logging.getLogger(experiment_name)
        self.logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def log_metrics(self, metrics_dict, prefix=""):
        """Log metrics dictionary"""
        for key, value in metrics_dict.items():
            self.logger.info(f"{prefix}{key}: {value}")
