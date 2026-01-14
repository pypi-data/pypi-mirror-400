"""Base classes for ANNS algorithms."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

import numpy as np


class BaseANNSIndex(ABC):
    """Abstract base class for all ANNS index implementations.
    
    This class defines a unified interface for approximate nearest neighbor search
    algorithms. All algorithm implementations should inherit from this class.
    
    Attributes:
        dimension (int): Dimensionality of vectors
        metric (str): Distance metric ('l2', 'cosine', 'inner_product')
        index_params (dict): Algorithm-specific parameters
    """
    
    def __init__(
        self,
        dimension: int,
        metric: str = "l2",
        **kwargs
    ):
        """Initialize the ANNS index.
        
        Args:
            dimension: Vector dimension
            metric: Distance metric ('l2', 'cosine', 'inner_product')
            **kwargs: Algorithm-specific parameters
        """
        self.dimension = dimension
        self.metric = self._normalize_metric(metric)
        self.index_params = kwargs
        self._is_built = False
        self._num_vectors = 0
    
    @staticmethod
    def _normalize_metric(metric: str) -> str:
        """Normalize metric name to standard format."""
        metric = metric.lower().replace("-", "_").replace(" ", "_")
        
        # Map common aliases
        metric_map = {
            "l2": "l2",
            "euclidean": "l2",
            "cosine": "cosine",
            "cos": "cosine",
            "inner_product": "inner_product",
            "ip": "inner_product",
            "dot": "inner_product",
        }
        
        if metric in metric_map:
            return metric_map[metric]
        
        raise ValueError(f"Unknown metric: {metric}. Supported: l2, cosine, inner_product")
    
    @abstractmethod
    def build(self, data: np.ndarray) -> None:
        """Build the index from a dataset.
        
        Args:
            data: Training data of shape (n_samples, dimension)
            
        Raises:
            ValueError: If data shape doesn't match dimension
        """
        pass
    
    @abstractmethod
    def add(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None) -> None:
        """Add vectors to the index (incremental insertion).
        
        Args:
            vectors: Vectors to add, shape (n_samples, dimension)
            ids: Optional IDs for the vectors, shape (n_samples,)
            
        Raises:
            ValueError: If vectors shape doesn't match dimension
        """
        pass
    
    @abstractmethod
    def search(
        self,
        queries: np.ndarray,
        k: int = 10,
        **search_params
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for k nearest neighbors.
        
        Args:
            queries: Query vectors, shape (n_queries, dimension)
            k: Number of neighbors to return
            **search_params: Algorithm-specific search parameters
            
        Returns:
            Tuple of (distances, indices):
                - distances: shape (n_queries, k)
                - indices: shape (n_queries, k)
                
        Raises:
            RuntimeError: If index is not built
            ValueError: If queries shape doesn't match dimension
        """
        pass
    
    def delete(self, ids: np.ndarray) -> None:
        """Delete vectors by their IDs (if supported).
        
        Args:
            ids: IDs of vectors to delete
            
        Raises:
            NotImplementedError: If algorithm doesn't support deletion
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support deletion")
    
    def save(self, path: str) -> None:
        """Save index to disk (if supported).
        
        Args:
            path: File path to save the index
            
        Raises:
            NotImplementedError: If algorithm doesn't support saving
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support saving")
    
    def load(self, path: str) -> None:
        """Load index from disk (if supported).
        
        Args:
            path: File path to load the index from
            
        Raises:
            NotImplementedError: If algorithm doesn't support loading
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support loading")
    
    def _validate_data_shape(self, data: np.ndarray, name: str = "data") -> None:
        """Validate data shape matches index dimension.
        
        Args:
            data: Data array to validate
            name: Name of the data (for error messages)
            
        Raises:
            ValueError: If data shape is invalid
        """
        if data.ndim != 2:
            raise ValueError(f"{name} must be 2D array, got shape {data.shape}")
        
        if data.shape[1] != self.dimension:
            raise ValueError(
                f"{name} dimension mismatch: expected {self.dimension}, "
                f"got {data.shape[1]}"
            )
    
    def _ensure_contiguous_float32(self, data: np.ndarray) -> np.ndarray:
        """Ensure data is contiguous float32 array.
        
        Args:
            data: Input data
            
        Returns:
            Contiguous float32 array
        """
        if data.dtype != np.float32:
            data = data.astype(np.float32)
        
        if not data.flags['C_CONTIGUOUS']:
            data = np.ascontiguousarray(data)
        
        return data
    
    @property
    def is_built(self) -> bool:
        """Check if index is built."""
        return self._is_built
    
    @property
    def num_vectors(self) -> int:
        """Get number of vectors in the index."""
        return self._num_vectors
    
    def __repr__(self) -> str:
        """String representation of the index."""
        status = "built" if self._is_built else "not built"
        return (
            f"{self.__class__.__name__}("
            f"dimension={self.dimension}, "
            f"metric={self.metric}, "
            f"num_vectors={self._num_vectors}, "
            f"status={status})"
        )
