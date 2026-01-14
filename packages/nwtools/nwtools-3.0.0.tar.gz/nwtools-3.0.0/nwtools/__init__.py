"""
nwtools - A Python package for negatively optimizing system performance.

This package provides various methods to degrade system performance
for testing, demonstration, and educational purposes.
"""

__version__ = "1.0.0"
__author__ = "ruin321"
__license__ = "MIT"

from .core import NegativeOptimizer, IntensityLevel, OptimizationConfig
from .cli import main
from .utils import get_system_info, print_system_info, load_config, save_config
from .tui import NWToolsTUI, main as tui_main
from .simple_tui import SimpleTUI, simple_tui_main
from .stable_tui import StableTUI, stable_tui_main

__all__ = [
    "NegativeOptimizer", 
    "IntensityLevel", 
    "OptimizationConfig",
    "main",
    "get_system_info",
    "print_system_info",
    "load_config",
    "save_config",
    "NWToolsTUI",
    "tui_main",
    "SimpleTUI",
    "simple_tui_main",
    "StableTUI",
    "stable_tui_main"
]