"""SPTAG wrapper (experimental)."""

import warnings
from typing import Optional, Tuple
import numpy as np

from ...base import BaseANNSIndex


class SPTAGIndex(BaseANNSIndex):
    """SPTAG implementation through PyCANDYAlgo.
    
    SPTAG (Space Partition Tree And Graph) is Microsoft's open-source
    ANNS library with tree and graph based algorithms.
    
    Note: This wrapper is experimental. For full SPTAG functionality,
    use PyCANDYAlgo SPTAG bindings directly.
    
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
            "SPTAG wrapper is experimental. Full integration pending. "
            "Use PyCANDYAlgo SPTAG bindings directly for now.",
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
