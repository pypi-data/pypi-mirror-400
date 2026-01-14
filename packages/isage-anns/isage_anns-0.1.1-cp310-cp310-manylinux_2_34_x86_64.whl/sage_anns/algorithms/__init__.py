"""Algorithm implementations for SAGE ANNS."""

# CANDY algorithms (from PyCANDYAlgo)
try:
    from .candy import (
        CANDYIndex,
        CANDYFlatIndex,
        CANDYNNDescentIndex,
        CANDYLSHAPGIndex,
        CANDYOnlinePQIndex,
        CANDYDPGIndex,
        FAISSIndex,
        FAISSHNSWIndex,
        DiskANNIndex,
        SPTAGIndex,
    )
    __all__ = [
        "CANDYIndex",
        "CANDYFlatIndex",
        "CANDYNNDescentIndex",
        "CANDYLSHAPGIndex",
        "CANDYOnlinePQIndex",
        "CANDYDPGIndex",
        "FAISSIndex",
        "FAISSHNSWIndex",
        "DiskANNIndex",
        "SPTAGIndex",
    ]
except ImportError:
    __all__ = []

# Try to import VSAG if available
try:
    from .vsag_wrapper import VSAGHNSWIndex
    __all__.append("VSAGHNSWIndex")
except ImportError:
    pass

# Try to import GTI if available
try:
    from .gti_wrapper import GTIIndex
    __all__.append("GTIIndex")
except ImportError:
    pass

# Try to import PLSH if available
try:
    from .plsh_wrapper import PLSHIndex
    __all__.append("PLSHIndex")
except ImportError:
    pass
