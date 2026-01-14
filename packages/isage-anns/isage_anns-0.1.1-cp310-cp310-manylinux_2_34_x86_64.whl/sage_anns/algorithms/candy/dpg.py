"""CANDY DPG index."""

from .base import CANDYIndex


class CANDYDPGIndex(CANDYIndex):
    """CANDY DPG (Dynamic Proximity Graph) index.
    
    A graph-based index optimized for dynamic workloads with
    frequent insertions and deletions.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
        **kwargs: Additional parameters
    """
    
    def __init__(self, dimension: int, metric: str = "l2", **kwargs):
        super().__init__(
            algorithm="DPG",
            dimension=dimension,
            metric=metric,
            **kwargs
        )
