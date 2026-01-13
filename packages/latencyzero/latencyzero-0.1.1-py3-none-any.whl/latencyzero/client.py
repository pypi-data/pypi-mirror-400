"""
LatencyZero Client - Enhanced with Semantic Support
Communicates with the gateway to check/store approximations
"""

import hashlib
import json
import pickle
import requests
import time
from typing import Any, Dict, Optional, Tuple


class LatencyZeroClient:
    """
    Client for communicating with LatencyZero gateway
    Enhanced with semantic matching support
    """
    
    def __init__(
        self,
        gateway_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: float = 0.1,
        enable_metrics: bool = True
    ):
        self.gateway_url = gateway_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.enable_metrics = enable_metrics
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_latency_cached': 0.0,
            'total_latency_computed': 0.0,
        }
    
    def hash_input(self, args: tuple, kwargs: dict) -> str:
        """
        Generate a deterministic hash of function inputs
        """
        # Serialize inputs
        input_data = {
            'args': args,
            'kwargs': kwargs
        }
        
        # Convert to JSON string (sorted keys for consistency)
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        
        # Hash
        return hashlib.sha256(input_str.encode()).hexdigest()
    
    def _extract_query_text(self, args: tuple, kwargs: dict) -> Optional[str]:
        """
        Extract query text from function arguments for semantic matching
        
        Looks for string arguments that might be queries
        """
        # Try first positional argument if it's a string
        if args and len(args) > 0:
            first_arg = args[0]
            if isinstance(first_arg, str):
                return first_arg
        
        # Try common parameter names
        for key in ['query', 'question', 'prompt', 'text', 'input']:
            if key in kwargs and isinstance(kwargs[key], str):
                return kwargs[key]
        
        # If no string found, try to convert first arg to string
        if args and len(args) > 0:
            try:
                return str(args[0])
            except:
                pass
        
        return None
    
    def check_approximation(
        self,
        function: str,
        input_hash: str,
        tolerance: float,
        args: tuple = None,
        kwargs: dict = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if gateway has a good approximation
        
        Enhanced to send query_input for semantic matching
        """
        try:
            # Build request params
            params = {
                'function': function,
                'hash': input_hash,
                'tolerance': tolerance
            }
            
            # Add query_input for semantic matching
            if args or kwargs:
                query_text = self._extract_query_text(args or (), kwargs or {})
                if query_text:
                    params['query_input'] = query_text
            
            # Add auth header if API key present
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Make request
            response = requests.get(
                f"{self.gateway_url}/api/v1/approximate",
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('available'):
                    # Deserialize result
                    result = self._deserialize(data['result'])
                    
                    return {
                        'result': result,
                        'confidence': data.get('confidence', 1.0),
                        'metadata': data.get('metadata', {}),
                        'semantic_match': data.get('semantic_match', False)
                    }
            
            return None
        
        except requests.Timeout:
            # Timeout is expected - just means we compute exactly
            return None
        
        except Exception as e:
            # On error, return None (will compute exactly)
            if self.enable_metrics:
                print(f"[LatencyZero] Gateway error: {e}")
            return None
    
    def store_result(
        self,
        function: str,
        input_hash: str,
        result: Any,
        execution_time: float,
        args: tuple = None,
        kwargs: dict = None
    ):
        """
        Store computed result in gateway
        
        Enhanced to send query_input for semantic analysis
        """
        try:
            # Serialize result
            serialized = self._serialize(result)
            
            # Build request data
            data = {
                'function': function,
                'hash': input_hash,
                'result': serialized,
                'execution_time': execution_time,
                'timestamp': time.time()
            }
            
            # Add query_input for semantic learning
            if args or kwargs:
                query_text = self._extract_query_text(args or (), kwargs or {})
                if query_text:
                    data['query_input'] = query_text
            
            # Add auth header if API key present
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Make request (fire and forget, don't wait)
            requests.post(
                f"{self.gateway_url}/api/v1/store",
                json=data,
                headers=headers,
                timeout=self.timeout
            )
        
        except Exception as e:
            # Don't fail if storage fails
            if self.enable_metrics:
                print(f"[LatencyZero] Storage error: {e}")
    
    def refine_in_background(
        self,
        function: str,
        func: callable,
        args: tuple,
        kwargs: dict,
        input_hash: str
    ):
        """
        Schedule background refinement (not implemented in client)
        
        This is handled by the gateway's refinement worker
        """
        pass
    
    def record_metrics(self, cache_hit: bool, latency: float):
        """Record performance metrics"""
        if not self.enable_metrics:
            return
        
        self.stats['total_requests'] += 1
        
        if cache_hit:
            self.stats['cache_hits'] += 1
            self.stats['total_latency_cached'] += latency
        else:
            self.stats['cache_misses'] += 1
            self.stats['total_latency_computed'] += latency
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total = self.stats['total_requests']
        hits = self.stats['cache_hits']
        misses = self.stats['cache_misses']
        
        if total == 0:
            hit_rate = 0.0
            avg_cached = 0.0
            avg_computed = 0.0
            improvement = 0.0
        else:
            hit_rate = hits / total
            avg_cached = (self.stats['total_latency_cached'] / hits) if hits > 0 else 0.0
            avg_computed = (self.stats['total_latency_computed'] / misses) if misses > 0 else 0.0
            
            if avg_computed > 0:
                improvement = ((avg_computed - avg_cached) / avg_computed) * 100
            else:
                improvement = 0.0
        
        return {
            'total_requests': total,
            'cache_hits': hits,
            'cache_misses': misses,
            'hit_rate': hit_rate,
            'avg_latency_cached': avg_cached * 1000,  # Convert to ms
            'avg_latency_computed': avg_computed * 1000,
            'latency_improvement': improvement
        }
    
    def _serialize(self, obj: Any) -> str:
        """Serialize object for transmission"""
        try:
            # Try JSON first (faster and more compatible)
            return json.dumps(obj)
        except (TypeError, ValueError):
            # Fall back to pickle
            return pickle.dumps(obj).hex()
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize object from transmission"""
        try:
            # Try JSON first
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            # Fall back to pickle
            return pickle.loads(bytes.fromhex(data))


# Global default client instance
_default_client = None


def get_default_client() -> LatencyZeroClient:
    """Get or create the default client instance"""
    global _default_client
    
    if _default_client is None:
        _default_client = LatencyZeroClient()
    
    return _default_client


def configure(
    gateway_url: str = None,
    api_key: str = None,
    timeout: float = None,
    enable_metrics: bool = None
):
    """
    Configure the default client
    
    Args:
        gateway_url: URL of the LatencyZero gateway
        api_key: API key for authentication
        timeout: Request timeout in seconds
        enable_metrics: Whether to track metrics
    """
    global _default_client
    
    if _default_client is None:
        _default_client = LatencyZeroClient(
            gateway_url=gateway_url or "http://localhost:8080",
            api_key=api_key,
            timeout=timeout or 0.1,
            enable_metrics=enable_metrics if enable_metrics is not None else True
        )
    else:
        # Update existing client
        if gateway_url:
            _default_client.gateway_url = gateway_url.rstrip('/')
        if api_key:
            _default_client.api_key = api_key
        if timeout:
            _default_client.timeout = timeout
        if enable_metrics is not None:
            _default_client.enable_metrics = enable_metrics