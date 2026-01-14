"""CANDY LSH-APG index."""

from .base import CANDYIndex


class CANDYLSHAPGIndex(CANDYIndex):
    """CANDY LSH-APG (Locality-Sensitive Hashing with Approximate Proximity Graph) index.
    
    Combines LSH for fast candidate generation with graph refinement.
    Good for high-dimensional sparse data.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
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
