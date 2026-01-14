"""Data science environment template configuration."""

from devcon.models import (
    CommonConfiguration,
    ContainerType,
    EnvironmentTemplate,
)

# Data science package list
DATA_SCIENCE_PACKAGES = {
    "pip": [
        "jupyter",
        "jupyterlab",
        "marimo",
        "pandas",
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "plotly",
        "mlflow",
        "dvc",
        "great-expectations",
    ],
    "apt": [
        "build-essential",
        "libhdf5-dev",
        "graphviz",
    ],
}

# VS Code extensions for data science
DATA_SCIENCE_EXTENSIONS = [
    "ms-python.python",
    "ms-toolsai.jupyter",
    "marimo-team.vscode-marimo",
    "Anthropic.claude-code",
]

# Default settings for data science environment
DATA_SCIENCE_DEFAULTS = {
    "python_version": "3.11",
}

# Data science template instance
DATA_SCIENCE_TEMPLATE = EnvironmentTemplate(
    container_type=ContainerType.DATA_SCIENCE,
    base_image="mcr.microsoft.com/devcontainers/python:3.11",
    additional_packages=DATA_SCIENCE_PACKAGES,
    vscode_extensions=DATA_SCIENCE_EXTENSIONS,
    dockerfile_template="data-science/Dockerfile.j2",
    devcontainer_template="data-science/devcontainer.json.j2",
    default_settings=DATA_SCIENCE_DEFAULTS,
    common_config=CommonConfiguration(),
)
