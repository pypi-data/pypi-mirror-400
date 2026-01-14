"""CANDY Online PQ index."""

from .base import CANDYIndex


class CANDYOnlinePQIndex(CANDYIndex):
    """CANDY Online Product Quantization index.
    
    Online PQ supports dynamic insertion and efficient compression.
    Trades some accuracy for significant memory savings through
    vector quantization.
    
    Args:
        dimension: Vector dimension
        metric: Distance metric ('l2', 'cosine', 'inner_product')
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
