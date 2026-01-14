"""
Dataform Dependency Visualizer

Generate interactive SVG diagrams showing table dependencies in Dataform projects.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .visualizer import DependencyVisualizer
from .parser import parse_dependencies_report

__all__ = ["DependencyVisualizer", "parse_dependencies_report"]
