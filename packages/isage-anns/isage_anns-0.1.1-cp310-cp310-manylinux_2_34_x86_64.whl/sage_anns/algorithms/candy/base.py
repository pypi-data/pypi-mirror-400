"""Base CANDY index wrapper."""

from typing import Optional, Tuple, Dict, Any
import numpy as np

from ...base import BaseANNSIndex
from .utils import get_pycandy, get_torch


class CANDYIndex(BaseANNSIndex):
    """Generic CANDY index wrapper supporting multiple algorithms.
    
    Supported algorithms:
    - 'flat': Brute-force flat index
    - 'bucketedFlat': Bucketed flat index
    - 'onlinePQ': Online Product Quantization
    - 'faiss': FAISS integration
    - 'nnDescent': NN-Descent graph index
    - 'DPG': DPG index
    - 'LSHAPG': LSH-APG index
    - 'SPTAG': SPTAG integration (if available)
    
    Args:
        algorithm: Algorithm name from the list above
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
        config: Dictionary of algorithm-specific parameters
        **kwargs: Additional parameters passed as config
    """
    
    def __init__(
        self,
        algorithm: str,
        dimension: int,
        metric: str = "l2",
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self.algorithm = algorithm
        self.config_dict = config or {}
        self.config_dict.update(kwargs)
        
        self._index = None
        self._config = None
    
    def _create_config(self) -> Any:
        """Create ConfigMap from parameters."""
        PyCANDY = get_pycandy()
        cfg = PyCANDY.ConfigMap()
        
        # Set dimension
        cfg.edit("vecDim", int(self.dimension))
        
        # Set metric
        if self.metric == "l2":
            cfg.edit("metric", "L2")
        elif self.metric == "inner_product":
            cfg.edit("metric", "IP")
        elif self.metric == "cosine":
            cfg.edit("metric", "Cosine")
        else:
            cfg.edit("metric", "L2")
        
        # Add all config parameters
        for key, value in self.config_dict.items():
            if isinstance(value, int):
                cfg.edit(key, int(value))
            elif isinstance(value, float):
                cfg.edit(key, float(value))
            elif isinstance(value, str):
                cfg.edit(key, str(value))
        
        return cfg
    
    def build(self, data: np.ndarray) -> None:
        """Build index from data."""
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        PyCANDY = get_pycandy()
        torch = get_torch()
        
        # Create index
        self._index = PyCANDY.createIndex(self.algorithm, self.dimension)
        if self._index is None:
            raise ValueError(
                f"Failed to create index '{self.algorithm}'. "
                f"Available: flat, bucketedFlat, onlinePQ, faiss, nnDescent, DPG, LSHAPG, SPTAG"
            )
        
        # Configure
        self._config = self._create_config()
        self._index.setConfig(self._config)
        
        # Load data
        data_tensor = torch.from_numpy(data)
        self._index.loadInitialTensor(data_tensor)
        
        self._is_built = True
        self._num_vectors = len(data)
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before adding vectors")
        
        self._validate_data_shape(vectors, "vectors")
        vectors = self._ensure_contiguous_float32(vectors)
        
        torch = get_torch()
        vectors_tensor = torch.from_numpy(vectors)
        
        if ids is not None:
            ids_tensor = torch.from_numpy(ids.astype(np.int64))
            self._index.insertTensorWithIds(vectors_tensor, ids_tensor)
        else:
            self._index.insertTensor(vectors_tensor)
        
        self._num_vectors += len(vectors)
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for k nearest neighbors."""
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        # Update search parameters if provided
        if search_params:
            for key, value in search_params.items():
                if isinstance(value, int):
                    self._config.edit(key, int(value))
                elif isinstance(value, float):
                    self._config.edit(key, float(value))
        
        torch = get_torch()
        queries_tensor = torch.from_numpy(queries)
        
        # Search returns (indices, distances) as tensors
        result = self._index.searchTensor(queries_tensor, int(k))
        
        # Convert to numpy
        indices = result[0].numpy().astype(np.int64)
        distances = result[1].numpy().astype(np.float32)
        
        return distances, indices
    
    def delete(self, ids: np.ndarray) -> None:
        """Delete vectors by IDs (if supported by algorithm)."""
        if not self._is_built:
            raise RuntimeError("Index must be built before deleting vectors")
        
        torch = get_torch()
        ids_tensor = torch.from_numpy(ids.astype(np.int64))
        self._index.deleteTensor(ids_tensor)
        self._num_vectors -= len(ids)
