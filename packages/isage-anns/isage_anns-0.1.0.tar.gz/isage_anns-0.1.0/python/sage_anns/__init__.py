"""SAGE ANNS: Approximate Nearest Neighbor Search algorithms.

This package provides high-performance C++ implementations of ANNS algorithms
with a unified Python interface.
"""

__version__ = "0.1.0"
__author__ = "IntelliStream Team"
__email__ = "shuhao_zhang@hust.edu.cn"

from .factory import create_index, register_algorithm, list_algorithms

__all__ = [
    "create_index",
    "register_algorithm", 
    "list_algorithms",
]
