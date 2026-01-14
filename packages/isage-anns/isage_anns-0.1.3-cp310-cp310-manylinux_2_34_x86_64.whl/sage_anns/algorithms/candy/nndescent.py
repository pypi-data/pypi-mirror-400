"""CANDY NN-Descent graph-based index."""

from .base import CANDYIndex


class CANDYNNDescentIndex(CANDYIndex):
    """CANDY NN-Descent graph-based index.
    
    NN-Descent builds a k-NN graph incrementally and efficiently.
    It's particularly good for high-dimensional data and provides
    a good balance between build time and search quality.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
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
