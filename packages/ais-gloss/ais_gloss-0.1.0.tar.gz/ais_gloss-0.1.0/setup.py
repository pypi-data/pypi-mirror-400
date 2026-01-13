from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
def get_version():
    with open("ais_gloss/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split('"')[1]
    return "0.1.0"

setup(
    name="ais_gloss",
    version=get_version(),
    author="Zhang, Baicheng",
    author_email="zbc@ustc.edu.cn",
    description="AI-Scientist GLOSS Recommendation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zbc0315/ais_gloss",
    project_urls={
        "Bug Tracker": "https://github.com/zbc0315/ais_gloss/issues",
        "Documentation": "https://zbc0315.github.io/ais_gloss/",
        "Source Code": "https://github.com/zbc0315/ais_gloss",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "torch>=1.10.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "bayesian-optimization>=1.2.0",
        "joblib>=1.1.0",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.0.0",
            "mkdocstrings[python]>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ais_gloss=ais_gloss.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
