# Team Classifier OSNet

A Python package for team classification using OSNet.

## Installation

```bash
pip install team-classifier-osnet
```

## Usage

```python
from team_classifier_osnet import TeamClassifier

# Use TeamClassifier here
instance = TeamClassifier()
```

## Setup Instructions

1. Place your `.pyc` file in the `team_classifier_osnet/` directory and name it `module.pyc`
2. Update `team_classifier_osnet/main.py` to replace `TeamClassifier` with the actual class name from your `.pyc` file
3. Update `team_classifier_osnet/__init__.py` to export the correct class name
4. Update `pyproject.toml` with your package information (name, author, etc.)

## Building and Publishing

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (test first with testpypi)
twine upload dist/*
```

## License

MIT

