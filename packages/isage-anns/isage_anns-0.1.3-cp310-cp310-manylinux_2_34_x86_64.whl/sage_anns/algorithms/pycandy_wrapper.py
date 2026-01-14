"""Wrappers for PyCANDYAlgo algorithms.

PyCANDYAlgo provides multiple algorithm implementations through AbstractIndex:
- flat: Flat brute-force search
- bucketedFlat: Bucketed flat index
- onlinePQ: Online Product Quantization
- faiss: FAISS integration (various index types)
- nnDescent: NN-Descent graph-based index
- DPG: DPG index
- LSHAPG: LSH-APG index
- SPTAG: SPTAG integration (if enabled)

All algorithms are accessed through the unified AbstractIndex interface.
"""

import warnings
from typing import Optional, Tuple, Dict, Any

import numpy as np

from ..base import BaseANNSIndex


# Lazy import PyCANDYAlgo to avoid import errors if not built
_pycandy_module = None
_torch_module = None


def _get_pycandy():
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


def _get_torch():
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
        PyCANDY = _get_pycandy()
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
        
        PyCANDY = _get_pycandy()
        torch = _get_torch()
        
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
        
        torch = _get_torch()
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
        
        torch = _get_torch()
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
        
        torch = _get_torch()
        ids_tensor = torch.from_numpy(ids.astype(np.int64))
        self._index.deleteTensor(ids_tensor)
        self._num_vectors -= len(ids)


class CANDYFlatIndex(CANDYIndex):
    """CANDY Flat (brute-force) index.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric
        **kwargs: Additional parameters
    """
    
    def __init__(self, dimension: int, metric: str = "l2", **kwargs):
        super().__init__(
            algorithm="flat",
            dimension=dimension,
            metric=metric,
            **kwargs
        )


class CANDYNNDescentIndex(CANDYIndex):
    """CANDY NN-Descent graph-based index.
    
    NN-Descent builds a k-NN graph incrementally and efficiently.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric
        k: Number of neighbors in the graph (default: 50)
        iterations: Number of iterations (default: 10)
        sample_rate: Sampling rate (default: 0.5)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        k: int = 50,
        iterations: int = 10,
        sample_rate: float = 0.5,
        **kwargs
    ):
        config = {
            "k": k,
            "iterations": iterations,
            "sampleRate": sample_rate,
        }
        config.update(kwargs)
        super().__init__(
            algorithm="nnDescent",
            dimension=dimension,
            metric=metric,
            config=config
        )


class CANDYLSHAPGIndex(CANDYIndex):
    """CANDY LSH-APG (Locality-Sensitive Hashing with Approximate Proximity Graph) index.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric
        num_tables: Number of hash tables (default: 10)
        hash_width: Hash function width (default: 4)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        num_tables: int = 10,
        hash_width: int = 4,
        **kwargs
    ):
        config = {
            "numTables": num_tables,
            "hashWidth": hash_width,
        }
        config.update(kwargs)
        super().__init__(
            algorithm="LSHAPG",
            dimension=dimension,
            metric=metric,
            config=config
        )


class CANDYOnlinePQIndex(CANDYIndex):
    """CANDY Online Product Quantization index.
    
    Online PQ supports dynamic insertion and efficient compression.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric
        num_subvectors: Number of subvectors (default: 8)
        num_clusters: Number of clusters per subvector (default: 256)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        num_subvectors: int = 8,
        num_clusters: int = 256,
        **kwargs
    ):
        config = {
            "nSubvectors": num_subvectors,
            "nClusters": num_clusters,
        }
        config.update(kwargs)
        super().__init__(
            algorithm="onlinePQ",
            dimension=dimension,
            metric=metric,
            config=config
        )


class CANDYDPGIndex(CANDYIndex):
    """CANDY DPG (Dynamic Proximity Graph) index.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric
        **kwargs: Additional parameters
    """
    
    def __init__(self, dimension: int, metric: str = "l2", **kwargs):
        super().__init__(
            algorithm="DPG",
            dimension=dimension,
            metric=metric,
            **kwargs
        )
    """CANDY HNSW implementation.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
        M: HNSW parameter - number of connections per layer (default: 16)
        ef_construction: HNSW parameter - size of dynamic candidate list (default: 200)
        ef_search: HNSW parameter - search parameter (default: 50)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        M: int = 16,
        ef_construction: int = 200,
        ef_search: int = 50,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self.M = M
        self.ef_construction = ef_construction
        self.ef_search = ef_search
        self._index = None
        self._config = None
    
    def build(self, data: np.ndarray) -> None:
        """Build index from data."""
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        PyCANDY = _get_pycandy()
        
        # Create index
        self._index = PyCANDY.createIndex("HNSWNaive", self.dimension)
        
        # Configure
        self._config = PyCANDY.newConfigMap()
        self._config.edit("vecDim", int(self.dimension))
        self._config.edit("M", int(self.M))
        self._config.edit("efConstruction", int(self.ef_construction))
        
        # Set metric
        if self.metric == "l2":
            self._config.edit("metric", "L2")
        elif self.metric == "inner_product":
            self._config.edit("metric", "IP")
        else:
            self._config.edit("metric", "L2")
        
        self._index.setConfig(self._config)
        
        # Load data
        import torch
        data_tensor = torch.from_numpy(data)
        self._index.loadInitialTensor(data_tensor, self._config)
        
        self._is_built = True
        self._num_vectors = len(data)
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before adding vectors")
        
        self._validate_data_shape(vectors, "vectors")
        vectors = self._ensure_contiguous_float32(vectors)
        
        import torch
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
        ef: Optional[int] = None,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for k nearest neighbors.
        
        Args:
            queries: Query vectors
            k: Number of neighbors
            ef: Search parameter (if None, uses ef_search from init)
            **search_params: Additional search parameters
        """
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        # Update ef if provided
        if ef is not None:
            self._config.edit("ef", int(ef))
        else:
            self._config.edit("ef", int(self.ef_search))
        
        import torch
        queries_tensor = torch.from_numpy(queries)
        
        # Search returns (indices, distances) as tensors
        result = self._index.searchTensor(queries_tensor, int(k))
        
        # Convert to numpy
        indices = result[0].numpy()
        distances = result[1].numpy()
        
        return distances, indices


class FAISSHNSWIndex(BaseANNSIndex):
    """FAISS HNSW implementation through PyCANDYAlgo.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'inner_product')
        M: HNSW M parameter (default: 32)
        ef_construction: Construction ef parameter (default: 200)
        ef_search: Search ef parameter (default: 64)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        M: int = 32,
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
        """Build FAISS HNSW index."""
        self._validate_data_shape(data, "data")
        data = self._ensure_contiguous_float32(data)
        
        PyCANDY = _get_pycandy()
        
        # Create FAISS index using factory
        index_desc = f"HNSW{self.M}"
        
        if self.metric == "l2":
            self._index = PyCANDY.index_factory_l2(int(self.dimension), index_desc)
        elif self.metric == "inner_product":
            self._index = PyCANDY.index_factory_ip(int(self.dimension), index_desc)
        else:
            raise ValueError(f"FAISS HNSW only supports l2 and inner_product metrics")
        
        # Set parameters
        self._index.hnsw.efConstruction = self.ef_construction
        self._index.hnsw.efSearch = self.ef_search
        
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
        ef: Optional[int] = None,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search FAISS index."""
        if not self._is_built:
            raise RuntimeError("Index must be built before searching")
        
        self._validate_data_shape(queries, "queries")
        queries = self._ensure_contiguous_float32(queries)
        
        # Update ef if provided
        if ef is not None:
            self._index.hnsw.efSearch = ef
        
        distances, indices = self._index.search(queries, k)
        
        return distances, indices


class DiskANNIndex(BaseANNSIndex):
    """DiskANN implementation through PyCANDYAlgo.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'inner_product')
        R: Graph degree (default: 64)
        L: Build complexity (default: 100)
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        R: int = 64,
        L: int = 100,
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self.R = R
        self.L = L
        self._index = None
        
        warnings.warn(
            "DiskANN wrapper is experimental. Full integration pending.",
            UserWarning
        )
    
    def build(self, data: np.ndarray) -> None:
        """Build DiskANN index."""
        raise NotImplementedError(
            "DiskANN build not yet fully integrated. "
            "Use PyCANDYAlgo.diskannpy directly for now."
        )
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors."""
        raise NotImplementedError("DiskANN add not yet implemented")
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search DiskANN index."""
        raise NotImplementedError("DiskANN search not yet implemented")


class SPTAGIndex(BaseANNSIndex):
    """SPTAG implementation through PyCANDYAlgo.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric
        **kwargs: Additional parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        **kwargs
    ):
        super().__init__(dimension, metric, **kwargs)
        self._index = None
        
        warnings.warn(
            "SPTAG wrapper is experimental. Full integration pending.",
            UserWarning
        )
    
    def build(self, data: np.ndarray) -> None:
        """Build SPTAG index."""
        raise NotImplementedError(
            "SPTAG build not yet fully integrated. "
            "Use PyCANDYAlgo SPTAG bindings directly for now."
        )
    
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors."""
        raise NotImplementedError("SPTAG add not yet implemented")
    
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search SPTAG index."""
        raise NotImplementedError("SPTAG search not yet implemented")
