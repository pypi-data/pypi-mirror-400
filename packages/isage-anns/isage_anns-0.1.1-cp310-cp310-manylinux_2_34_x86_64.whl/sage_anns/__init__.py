"""SAGE ANNS: Approximate Nearest Neighbor Search algorithms.

This package provides high-performance C++ implementations of ANNS algorithms
with a unified Python interface.
"""

__version__ = "0.1.1"
__author__ = "IntelliStream Team"
__email__ = "shuhao_zhang@hust.edu.cn"

from .base import BaseANNSIndex
from .factory import create_index, register_algorithm, list_algorithms

# Import and auto-register algorithms
def _auto_register_algorithms():
    """Automatically register all available algorithm implementations."""
    
    # Try to register CANDY algorithms
    try:
        from .algorithms.candy import (
            CANDYFlatIndex,
            CANDYNNDescentIndex,
            CANDYLSHAPGIndex,
            CANDYOnlinePQIndex,
            CANDYDPGIndex,
            FAISSIndex,
            FAISSHNSWIndex,
        )
        register_algorithm("candy_flat", CANDYFlatIndex)
        register_algorithm("candy_nndescent", CANDYNNDescentIndex)
        register_algorithm("candy_lshapg", CANDYLSHAPGIndex)
        register_algorithm("candy_onlinepq", CANDYOnlinePQIndex)
        register_algorithm("candy_dpg", CANDYDPGIndex)
        register_algorithm("faiss", FAISSIndex)
        register_algorithm("faiss_hnsw", FAISSHNSWIndex)
    except ImportError:
        pass  # PyCANDYAlgo not built yet
    
    # Try to register VSAG algorithms
    try:
        from .algorithms.vsag_wrapper import VSAGHNSWIndex
        register_algorithm("vsag_hnsw", VSAGHNSWIndex)
    except ImportError:
        pass  # pyvsag not installed
    
    # Try to register GTI algorithm
    try:
        from .algorithms.gti_wrapper import GTIIndex
        register_algorithm("gti", GTIIndex)
    except ImportError:
        pass  # gti_wrapper not built
    
    # Try to register PLSH algorithm
    try:
        from .algorithms.plsh_wrapper import PLSHIndex
        register_algorithm("plsh", PLSHIndex)
    except ImportError:
        pass  # plsh_python not built
    
    # Note: DiskANN and SPTAG are marked as experimental
    # They will be registered when fully implemented


# Auto-register on import
_auto_register_algorithms()

__all__ = [
    "BaseANNSIndex",
    "create_index",
    "register_algorithm",
    "list_algorithms",
]
