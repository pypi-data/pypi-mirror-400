"""
Configuration for LatencyZero
"""

import os
from typing import Optional
from .client import get_default_client


def configure(
    gateway_url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: Optional[float] = None,
    enable_metrics: bool = True
):
    """
    Configure the global LatencyZero client
    
    Args:
        gateway_url: URL of the A³ Gateway service
        api_key: API key for authentication
        timeout: Timeout for approximation checks (seconds)
        enable_metrics: Whether to collect metrics
    
    Example:
        configure(
            gateway_url="https://api.latencyzero.ai",
            api_key="lz_xxx",
            timeout=0.1
        )
    """
    from .client import LatencyZeroClient, _default_client
    
    # Use environment variables as fallback
    gateway_url = gateway_url or os.getenv('LATENCYZERO_GATEWAY_URL', 'http://localhost:8080')
    api_key = api_key or os.getenv('LATENCYZERO_API_KEY')
    timeout = timeout or float(os.getenv('LATENCYZERO_TIMEOUT', '0.1'))
    
    # Create new client with config
    global _default_client
    if _default_client:
        _default_client.shutdown()
    
    _default_client = LatencyZeroClient(
        gateway_url=gateway_url,
        api_key=api_key,
        timeout=timeout,
        enable_metrics=enable_metrics
    )
