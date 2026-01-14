"""Wrapper for VSAG (Vector Search Acceleration Gateway) algorithms."""

from typing import Optional, Tuple

import numpy as np

from ..base import BaseANNSIndex


# Lazy import pyvsag to avoid import errors if not installed
_vsag_module = None


def _get_vsag():
    """Lazy load pyvsag module."""
    global _vsag_module
    if _vsag_module is None:
        try:
            import pyvsag
            _vsag_module = pyvsag
        except ImportError as e:
            raise ImportError(
                "pyvsag not found. Please install it first:\n"
                "  cd implementations/vsag && make pyvsag && pip install wheelhouse/pyvsag*.whl\n"
                f"Original error: {e}"
            )
    return _vsag_module


class VSAGHNSWIndex(BaseANNSIndex):
    """VSAG HNSW implementation.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
        M: HNSW M parameter (default: 16)
        ef_construction: Construction ef parameter (default: 200)
        ef_search: Search ef parameter (default: 64)
        **kwargs: Additional VSAG parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        M: int = 16,
        ef_construction: int = 200,
        ef_search: int = 64,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self.M = M
        self.ef_construction = ef_construction
        self.ef_search = ef_search
        self._index = None
    
    def build(self, data: np.ndarray) -> None:
        """Build VSAG HNSW index.
        
        Args:
            data: Training data of shape (n_samples, dimension)
        """
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        pyvsag = _get_vsag()
        
        # Map metric to VSAG format
        vsag_metric = self._map_metric_to_vsag(self.metric)
        
        # Build index parameters (JSON string)
        import json
        build_params = json.dumps({
            "dtype": "float32",
            "metric_type": vsag_metric,
            "dim": self.dimension,
            "hnsw": {
                "max_degree": self.M,
                "ef_construction": self.ef_construction,
            }
        })
        
        # Create index
        self._index = pyvsag.Index("hnsw", build_params)
        
        # Build with data: build(vectors, ids, num_elements, dim)
        ids = np.arange(len(data), dtype=np.int64)
        self._index.build(data, ids, len(data), self.dimension)
        
        self._is_built = True
        self._num_vectors = len(data)
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to VSAG index.
        
        Args:
            vectors: Vectors to add, shape (n_samples, dimension)
            ids: Optional IDs for the vectors
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before adding vectors")
        
        self._validate_data_shape(vectors, "vectors")
        vectors = self._ensure_contiguous_float32(vectors)
        
        # Generate IDs if not provided
        if ids is None:
            ids = np.arange(
                self._num_vectors,
                self._num_vectors + len(vectors),
                dtype=np.int64
            )
        else:
            ids = ids.astype(np.int64)
        
        # Add vectors one by one
        for i in range(len(vectors)):
            self._index.add(vectors[i], ids[i])
        
        self._num_vectors += len(vectors)
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        ef: Optional[int] = None,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search VSAG index for k nearest neighbors.
        
        Args:
            queries: Query vectors, shape (n_queries, dimension)
            k: Number of neighbors to return
            ef: Search ef parameter (if None, uses ef_search from init)
            **search_params: Additional search parameters
            
        Returns:
            Tuple of (distances, indices)
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        # Set search parameters (JSON string)
        import json
        search_ef = ef if ef is not None else self.ef_search
        search_params_str = json.dumps({
            "hnsw": {
                "ef_search": search_ef
            }
        })
        
        n_queries = len(queries)
        all_indices = []
        all_distances = []
        
        # Search each query (VSAG searches one at a time)
        for i in range(n_queries):
            result = self._index.knn_search(
                queries[i],  # Single query vector
                k,
                search_params_str
            )
            
            # result is a tuple: (ids, distances)
            result_ids, result_dists = result
            all_indices.append(result_ids)
            all_distances.append(result_dists)
        
        return np.array(all_distances), np.array(all_indices)
    
    def save(self, path: str) -> None:
        """Save VSAG index to disk.
        
        Args:
            path: File path to save the index
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before saving")
        
        self._index.serialize(path)
    
    def load(self, path: str) -> None:
        """Load VSAG index from disk.
        
        Args:
            path: File path to load the index from
        """
        pyvsag = _get_vsag()
        
        # Map metric to VSAG format
        vsag_metric = self._map_metric_to_vsag(self.metric)
        
        # Create index parameters
        index_params = {
            "dtype": "float32",
            "metric_type": vsag_metric,
            "dim": self.dimension,
        }
        
        self._index = pyvsag.Index("hnsw", index_params)
        self._index.deserialize(path)
        
        self._is_built = True
        # Note: num_vectors would need to be tracked separately or retrieved from index
    
    def _map_metric_to_vsag(self, metric: str) -> str:
        """Map standardized metric name to VSAG metric type."""
        metric_map = {
            "l2": "l2",
            "cosine": "cosine",
            "inner_product": "ip",
        }
        
        if metric not in metric_map:
            raise ValueError(f"Unsupported metric for VSAG: {metric}")
        
        return metric_map[metric]
