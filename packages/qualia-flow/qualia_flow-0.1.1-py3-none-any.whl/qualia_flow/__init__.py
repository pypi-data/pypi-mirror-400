"""Qualia Flow - MLflow experiment exploration and notebook generation.

This package provides tools for discovering, exploring, and documenting MLflow
experiments through automatically generated Jupyter notebooks.
"""

from qualia_flow.cli import interactive_selection, main
from qualia_flow.explorer import ArtifactExplorer
from qualia_flow.generator import NotebookGenerator

__all__ = [
    "ArtifactExplorer",
    "NotebookGenerator",
    "main",
    "interactive_selection",
]

__version__ = "1.0.0"
