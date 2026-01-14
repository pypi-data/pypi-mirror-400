"""CANDY Flat (brute-force) index."""

from .base import CANDYIndex


class CANDYFlatIndex(CANDYIndex):
    """CANDY Flat (brute-force) index.
    
    Brute-force exact nearest neighbor search. Guarantees 100% recall
    but has O(n) search complexity.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
        **kwargs: Additional parameters
    """
    
    def __init__(self, dimension: int, metric: str = "l2", **kwargs):
        super().__init__(
            algorithm="flat",
            dimension=dimension,
            metric=metric,
            **kwargs
        )
