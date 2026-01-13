"""
LatencyZero - Adaptive Anticipatory Approximation (A³)
Cut API latency by 50-90% with predictive approximation
"""

from .decorator import a3
from .client import LatencyZeroClient
from .config import configure

__version__ = "0.1.0"
__all__ = ["a3", "LatencyZeroClient", "configure"]
