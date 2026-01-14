"""Factory for creating ANNS index instances."""

from typing import Any, Dict, Optional

# Algorithm registry
_ALGORITHM_REGISTRY: Dict[str, type] = {}


def register_algorithm(name: str, cls: type) -> None:
    """Register an ANNS algorithm implementation.
    
    Args:
        name: Algorithm name (e.g., "faiss_hnsw")
        cls: Algorithm class implementing the ANNS interface
    """
    _ALGORITHM_REGISTRY[name] = cls


def list_algorithms() -> list[str]:
    """List all registered ANNS algorithms.
    
    Returns:
        List of algorithm names
    """
    return list(_ALGORITHM_REGISTRY.keys())


def create_index(algorithm: str, **kwargs: Any) -> Any:
    """Create an ANNS index instance.
    
    Args:
        algorithm: Algorithm name (e.g., "faiss_hnsw", "diskann")
        **kwargs: Algorithm-specific parameters
        
    Returns:
        ANNS index instance
        
    Raises:
        ValueError: If algorithm is not registered
    """
    if algorithm not in _ALGORITHM_REGISTRY:
        available = ", ".join(_ALGORITHM_REGISTRY.keys())
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. "
            f"Available algorithms: {available}"
        )
    
    cls = _ALGORITHM_REGISTRY[algorithm]
    return cls(**kwargs)
