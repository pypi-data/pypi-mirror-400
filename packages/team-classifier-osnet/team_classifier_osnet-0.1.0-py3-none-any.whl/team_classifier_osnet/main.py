"""
Main module that imports from the compiled .pyc file
"""

import importlib.util
import sys
from pathlib import Path

# Get the directory where this file is located
_package_dir = Path(__file__).parent

# Path to the .pyc file
_pyc_file = _package_dir / "module.pyc"

# Load the .pyc file as a module
if _pyc_file.exists():
    spec = importlib.util.spec_from_file_location("compiled_module", _pyc_file)
    compiled_module = importlib.util.module_from_spec(spec)
    sys.modules["compiled_module"] = compiled_module
    spec.loader.exec_module(compiled_module)
    
    # Import the class from the compiled module
    if hasattr(compiled_module, "TeamClassifier"):
        TeamClassifier = compiled_module.TeamClassifier
    else:
        # If the class name is different, update this line
        # For now, we'll try to get the first class found
        raise ImportError(
            "Could not find 'TeamClassifier' in the compiled module. "
            "Please update main.py with the correct class name."
        )
else:
    raise FileNotFoundError(
        f"Compiled module file not found at {_pyc_file}. "
        "Please ensure module.pyc is in the package directory."
    )

