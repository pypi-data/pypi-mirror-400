"""Wrapper for GTI (Graph-based Tree Index) algorithm."""

from typing import Optional, Tuple

import numpy as np

from ..base import BaseANNSIndex


# Lazy import gti_wrapper to avoid import errors if not built
_gti_module = None


def _get_gti():
    """Lazy load gti_wrapper module."""
    global _gti_module
    if _gti_module is None:
        try:
            import gti_wrapper
            _gti_module = gti_wrapper
        except ImportError as e:
            raise ImportError(
                "gti_wrapper not found. Please build it first:\n"
                "  cd implementations/gti/GTI && mkdir -p build && cd build\n"
                "  cmake .. && make gti_wrapper\n"
                f"Original error: {e}"
            )
    return _gti_module


class GTIIndex(BaseANNSIndex):
    """GTI (Graph-based Tree Index) implementation.
    
    GTI is a graph-based index that combines tree structure with graph navigation
    for efficient insertions and deletions with logarithmic complexity.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric (only 'l2' supported)
        capacity_up_i: Capacity parameter for insertion (default: 100)
        capacity_up_l: Capacity parameter for leaves (default: 100)
        m: Number of connections in graph (default: 16)
        L: Search beam width (default: 100)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        capacity_up_i: int = 50,
        capacity_up_l: int = 50,
        m: int = 16,
        L: int = 100,
        max_pts: int = 1000000,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        
        if self.metric != "l2":
            raise ValueError("GTI only supports L2 (Euclidean) distance")
        
        self.capacity_up_i = capacity_up_i
        self.capacity_up_l = capacity_up_l
        self.m = m
        self.L = L
        self.max_pts = max_pts
        self._index = None
        self._next_id = 0
    
    def build(self, data: np.ndarray) -> None:
        """Build GTI index from data.
        
        Args:
            data: Training data of shape (n_samples, dimension)
        """
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        gti_wrapper = _get_gti()
        
        # Create index
        self._index = gti_wrapper.GTIWrapper()
        
        # Setup - uses positional args: max_pts, ndim, capacity_up_i, capacity_up_l, m
        self._index.setup(
            self.max_pts,
            self.dimension,
            self.capacity_up_i,
            self.capacity_up_l,
            self.m
        )
        
        # Generate IDs for initial data
        n_samples = len(data)
        ids = np.arange(n_samples, dtype=np.int32)
        
        # Build index - uses positional args: data, ids, capacity_up_i, capacity_up_l, m
        self._index.build(
            data,
            ids,
            self.capacity_up_i,
            self.capacity_up_l,
            self.m
        )
        
        self._is_built = True
        self._num_vectors = n_samples
        self._next_id = n_samples
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to GTI index.
        
        Args:
            vectors: Vectors to add, shape (n_samples, dimension)
            ids: Optional IDs for the vectors (if None, auto-generated)
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before adding vectors")
        
        self._validate_data_shape(vectors, "vectors")
        vectors = self._ensure_contiguous_float32(vectors)
        
        n_samples = len(vectors)
        
        # Generate IDs if not provided
        if ids is None:
            ids = np.arange(
                self._next_id,
                self._next_id + n_samples,
                dtype=np.int32
            )
            self._next_id += n_samples
        else:
            ids = ids.astype(np.int32)
            # Update next_id to avoid conflicts
            self._next_id = max(self._next_id, np.max(ids) + 1)
        
        # Insert into index
        self._index.insert(vectors, ids)
        self._num_vectors += n_samples
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        L: Optional[int] = None,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search GTI index for k nearest neighbors.
        
        Args:
            queries: Query vectors, shape (n_queries, dimension)
            k: Number of neighbors to return
            L: Search beam width (if None, uses L from init)
            **search_params: Additional search parameters
            
        Returns:
            Tuple of (distances, indices)
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        # Use provided L or default
        search_L = L if L is not None else self.L
        
        # Query returns (indices, distances)
        indices, distances = self._index.query(queries, k, search_L)
        
        return distances, indices
    
    def delete(self, ids: np.ndarray) -> None:
        """Delete vectors by their IDs.
        
        Args:
            ids: IDs of vectors to delete
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before deleting vectors")
        
        ids = ids.astype(np.int32)
        self._index.remove(ids)
        
        # Note: We don't decrement _num_vectors as deleted vectors 
        # may still occupy space until compaction
