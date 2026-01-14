"""Utility functions for CANDY wrappers."""

# Lazy import modules to avoid import errors if not built
_pycandy_module = None
_torch_module = None


def get_pycandy():
    """Lazy load PyCANDYAlgo module."""
    global _pycandy_module
    if _pycandy_module is None:
        try:
            import PyCANDYAlgo
            _pycandy_module = PyCANDYAlgo
        except ImportError as e:
            raise ImportError(
                "PyCANDYAlgo not found. Please build it first:\n"
                "  cd implementations/build && cmake .. && make -j$(nproc)\n"
                f"Original error: {e}"
            )
    return _pycandy_module


def get_torch():
    """Lazy load torch module."""
    global _torch_module
    if _torch_module is None:
        try:
            import torch
            _torch_module = torch
        except ImportError as e:
            raise ImportError(
                "PyTorch not found. CANDY algorithms require PyTorch.\n"
                "Install with: pip install torch\n"
                f"Original error: {e}"
            )
    return _torch_module
