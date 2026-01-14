"""Wrapper for PLSH (Parallel Locality-Sensitive Hashing) algorithm."""

from typing import Optional, Tuple

import numpy as np

from ..base import BaseANNSIndex


# Lazy import plsh_python to avoid import errors if not built
_plsh_module = None


def _get_plsh():
    """Lazy load plsh_python module."""
    global _plsh_module
    if _plsh_module is None:
        try:
            import plsh_python
            _plsh_module = plsh_python
        except ImportError as e:
            raise ImportError(
                "plsh_python not found. Please build it first:\n"
                "  cd implementations/plsh && mkdir -p build && cd build\n"
                "  cmake .. && make\n"
                f"Original error: {e}"
            )
    return _plsh_module


class PLSHIndex(BaseANNSIndex):
    """PLSH (Parallel Locality-Sensitive Hashing) implementation.
    
    PLSH is designed for high-dimensional sparse vectors using LSH for
    efficient approximate nearest neighbor search with parallel processing.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric (only 'l2' supported)
        k: Number of hash functions per table (default: 10)
        m: Number of hash tables (default: 10)
        num_threads: Number of parallel threads (default: 4)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        k: int = 10,
        m: int = 10,
        num_threads: int = 4,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        
        if self.metric != "l2":
            raise ValueError("PLSH only supports L2 (Euclidean) distance")
        
        self.k = k
        self.m = m
        self.num_threads = num_threads
        self._index = None
        self._next_id = 0
    
    def build(self, data: np.ndarray) -> None:
        """Build PLSH index from data.
        
        Args:
            data: Training data of shape (n_samples, dimension)
        """
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        plsh_python = _get_plsh()
        
        # Create index
        self._index = plsh_python.Index(
            dimensions=self.dimension,
            k=self.k,
            m=self.m,
            num_threads=self.num_threads
        )
        
        # Generate IDs
        n_samples = len(data)
        ids = list(range(n_samples))
        
        # Build index
        self._index.build(data, n_samples, ids)
        
        self._is_built = True
        self._num_vectors = n_samples
        self._next_id = n_samples
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to PLSH index.
        
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
            ids_list = list(range(self._next_id, self._next_id + n_samples))
            self._next_id += n_samples
        else:
            ids_list = ids.astype(np.int32).tolist()
            # Update next_id to avoid conflicts
            self._next_id = max(self._next_id, max(ids_list) + 1)
        
        # Insert into index
        self._index.insert(vectors, ids_list)
        self._num_vectors += n_samples
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search PLSH index for k nearest neighbors.
        
        Args:
            queries: Query vectors, shape (n_queries, dimension)
            k: Number of neighbors to return
            **search_params: Additional search parameters
            
        Returns:
            Tuple of (distances, indices)
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        n_queries = len(queries)
        all_indices = []
        all_distances = []
        
        # Search each query individually
        for i in range(n_queries):
            query_vec = queries[i]
            
            # query_topk returns (ids, distances)
            ids, dists = self._index.query_topk(query_vec, k)
            
            # Convert to numpy arrays
            ids_array = np.array(ids, dtype=np.int64)
            dists_array = np.array(dists, dtype=np.float32)
            
            # Pad if necessary
            if len(ids_array) < k:
                pad_len = k - len(ids_array)
                ids_array = np.pad(ids_array, (0, pad_len), constant_values=-1)
                dists_array = np.pad(dists_array, (0, pad_len), constant_values=np.inf)
            elif len(ids_array) > k:
                ids_array = ids_array[:k]
                dists_array = dists_array[:k]
            
            all_indices.append(ids_array)
            all_distances.append(dists_array)
        
        return np.array(all_distances), np.array(all_indices)
    
    def merge_delta_to_static(self) -> None:
        """Merge incremental insertions to static index for better performance."""
        if not self._is_built:
            raise RuntimeError("Index must be built before merging")
        
        self._index.merge_delta_to_static()
