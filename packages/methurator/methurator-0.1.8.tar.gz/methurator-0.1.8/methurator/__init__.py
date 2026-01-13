"""
methsaturator
Package for sequencing saturation analysis of
sequencing methylation data.
"""

__version__ = "0.1.8"

from .plot import plot
from .downsample import downsample

__all__ = [
    "plot",
    "downsample",
    "__version__",
]
