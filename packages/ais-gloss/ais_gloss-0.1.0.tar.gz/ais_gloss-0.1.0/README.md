
# AIS-GLOSS

[![PyPI version](https://badge.fury.io/py/ais_gloss.svg)](https://badge.fury.io/py/ais_gloss)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://zbc0315.github.io/ais_gloss/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

AI-Scientist GLOSS Recommendation System

## 🚀 Features

- **Automated Model Training**: Train and compare multiple ML models automatically
- **GLOSS Algorithm**: Find optimal points using intelligent search
- **Comprehensive Visualization**: Beautiful plots and detailed logging
- **Easy to Use**: Simple API for complex ML tasks
- **Extensible**: Add your own models and metrics

## 📦 Installation

### Using pip

```bash
pip install ais_gloss
```

### Using conda

```bash
conda env create -f environment.yml
conda activate ais_gloss
```

### From source

```bash
git clone https://github.com/zbc0315/ais_gloss.git
cd ais_gloss
pip install -e .
```

## 🎯 Quick Start

### Automated Model Training

```python
from ais_gloss import AutoTrainer

# Initialize trainer
trainer = AutoTrainer(task='regression', metric='R2')

# Load data
trainer.load_data('data.csv', 
                 x_columns=['feature1', 'feature2'],
                 y_columns='target')

# Train all models
trainer.train_all_models()

# Optimize and get best model
trainer.optimize_hyperparameters()
trainer.train_final_model()

# Make predictions
predictions = trainer.predict(X_new)
```

### GLOSS Recommendation

```python
from ais_gloss import GLOSSRecommender

# Define model and comparator
gloss = GLOSSRecommender(
    model_func=your_model,
    y_comparator=lambda y1, y2: y1 > y2
)

# Find optimal points
recommendations = gloss.run_gloss(
    x_ranges={'x1': (0, 10, 0.5), 'x2': (0, 10, 0.5)},
    n_global=5,
    n_local=5,
    visualize=True
)
```

## 📚 Documentation

Full documentation is available at: **https://zbc0315.github.io/ais_gloss/**

- [Installation Guide](https://zbc0315.github.io/ais_gloss/installation/)
- [Quick Start](https://zbc0315.github.io/ais_gloss/quickstart/)
- [Tutorials](https://zbc0315.github.io/ais_gloss/tutorials/regression_tutorial/)
- [API Reference](https://zbc0315.github.io/ais_gloss/api/auto_trainer/)
- [Examples](https://zbc0315.github.io/ais_gloss/examples/basic_usage/)

## 🎓 Examples

Check out the [examples](examples/) directory for complete working examples:

- [Basic Regression](examples/example_auto_trainer.py)
- [Classification](examples/example_classification.py)
- [GLOSS Optimization](examples/example_gloss.py)

## 🛠️ Requirements

- Python >= 3.8
- numpy >= 1.21.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- torch >= 1.10.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/zbc0315/ais_gloss](https://github.com/zbc0315/ais_gloss)

## 🙏 Acknowledgments

- scikit-learn team for the excellent ML library
- PyTorch team for the deep learning framework
- All contributors to this project

## 📊 Citation

If you use AIS-GLOSS in your research, please cite:

XXX

