"""FAISS index wrappers through PyCANDYAlgo."""

import warnings
from typing import Optional, Tuple
import numpy as np

from ...base import BaseANNSIndex
from .utils import get_pycandy


class FAISSIndex(BaseANNSIndex):
    """FAISS index wrapper through PyCANDYAlgo.
    
    Supports various FAISS index types through factory strings:
    - 'Flat': Brute-force exact search
    - 'IVFx,Flat': Inverted file with x centroids
    - 'HNSWx': HNSW with x connections
    - 'IVFx,PQy': IVF with PQ compression
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'inner_product')
        index_type: FAISS index factory string (default: 'Flat')
        **kwargs: Additional FAISS parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        index_type: str = "Flat",
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self.index_type = index_type
        self._index = None
    
    def build(self, data: np.ndarray) -> None:
        """Build FAISS index."""
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        PyCANDY = get_pycandy()
        
        # Create FAISS index using factory
        if self.metric == "l2":
            self._index = PyCANDY.index_factory_l2(int(self.dimension), self.index_type)
        elif self.metric == "inner_product":
            self._index = PyCANDY.index_factory_ip(int(self.dimension), self.index_type)
        else:
            raise ValueError(f"FAISS only supports l2 and inner_product metrics, got {self.metric}")
        
        # Train and add data
        self._index.train(data)
        self._index.add(data)
        
        self._is_built = True
        self._num_vectors = len(data)
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to FAISS index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before adding vectors")
        
        self._validate_data_shape(vectors, "vectors")
        vectors = self._ensure_contiguous_float32(vectors)
        
        if ids is not None:
            self._index.add_with_ids(vectors, ids.astype(np.int64))
        else:
            self._index.add(vectors)
        
        self._num_vectors += len(vectors)
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search FAISS index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        distances, indices = self._index.search(queries, k)
        
        return distances, indices


class FAISSHNSWIndex(BaseANNSIndex):
    """FAISS HNSW Optimized implementation with Gorder reordering.
    
    This uses the optimized FAISS HNSW implementation from PyCANDYAlgo
    with support for graph reordering for better cache locality.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'inner_product')
        M: HNSW M parameter (default: 32)
        ef_construction: Construction ef parameter (default: 200)
        ef_search: Search ef parameter (default: 64)
        use_gorder: Whether to use Gorder reordering (default: False)
        gorder_window: Gorder window size (default: 5)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        M: int = 32,
        ef_construction: int = 200,
        ef_search: int = 64,
        use_gorder: bool = False,
        gorder_window: int = 5,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self.M = M
        self.ef_construction = ef_construction
        self.ef_search = ef_search
        self.use_gorder = use_gorder
        self.gorder_window = gorder_window
        self._index = None
    
    def build(self, data: np.ndarray) -> None:
        """Build FAISS HNSW Optimized index."""
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        PyCANDY = get_pycandy()
        
        # Map metric
        if self.metric == "l2":
            metric_type = PyCANDY.MetricType.METRIC_L2
        elif self.metric == "inner_product":
            metric_type = PyCANDY.MetricType.METRIC_INNER_PRODUCT
        else:
            raise ValueError(f"FAISS HNSW only supports l2 and inner_product, got {self.metric}")
        
        # Create optimized HNSW index
        self._index = PyCANDY.IndexHNSWFlatOptimized(
            int(self.dimension),
            int(self.M),
            metric_type
        )
        
        # Add data
        self._index.add(len(data), data)
        
        # Apply Gorder reordering if requested
        if self.use_gorder:
            self._index.reorder_gorder(self.gorder_window)
        
        self._is_built = True
        self._num_vectors = len(data)
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to FAISS HNSW index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before adding vectors")
        
        if ids is not None:
            warnings.warn("FAISS HNSW Flat does not support custom IDs, ignoring ids parameter")
        
        self._validate_data_shape(vectors, "vectors")
        vectors = self._ensure_contiguous_float32(vectors)
        
        self._index.add(len(vectors), vectors)
        self._num_vectors += len(vectors)
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        ef: Optional[int] = None,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search FAISS HNSW index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        # Use ef if provided, otherwise use default
        search_ef = ef if ef is not None else self.ef_search
        
        distances, indices = self._index.search(len(queries), queries, k, search_ef)
        
        return distances, indices
