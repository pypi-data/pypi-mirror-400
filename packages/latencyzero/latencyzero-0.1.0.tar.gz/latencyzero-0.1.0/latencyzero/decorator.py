"""
A³ Decorator - Enhanced with Semantic Support
"""

import functools
import time
from typing import Callable, Optional
from .client import get_default_client, LatencyZeroClient


def a3(
    tolerance: float = 0.02,
    client: Optional[LatencyZeroClient] = None,
    enable_refinement: bool = True,
    fallback_on_error: bool = True
):
    """
    Adaptive Anticipatory Approximation decorator
    Enhanced with semantic matching support
    
    Wraps expensive functions to provide instant approximate results
    with guaranteed correctness through confidence-based fallback.
    
    Args:
        tolerance: Maximum acceptable error rate (0.02 = 2% error tolerance)
        client: Custom LatencyZeroClient instance (optional)
        enable_refinement: Whether to refine approximations in background
        fallback_on_error: Fall back to exact computation on any error
    
    Example:
        @a3(tolerance=0.15)
        def ask_question(question: str):
            return expensive_llm_call(question)
        
        # First call
        ask_question("What is Python?")  # Slow: 2000ms
        
        # Similar calls now cached via semantic matching!
        ask_question("Explain Python")   # Fast: 10ms ⚡
        ask_question("Python basics")    # Fast: 10ms ⚡
    
    Returns:
        Decorated function that returns instantly when possible
    """
    
    def decorator(func: Callable) -> Callable:
        # Get client instance
        lz_client = client or get_default_client()
        function_name = f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            try:
                # 1. Hash the input
                input_hash = lz_client.hash_input(args, kwargs)
                
                # 2. Check if we have a good approximation
                # ENHANCED: Pass args/kwargs for semantic matching
                approx = lz_client.check_approximation(
                    function_name,
                    input_hash,
                    tolerance,
                    args=args,  # NEW: For semantic matching
                    kwargs=kwargs  # NEW: For semantic matching
                )
                
                if approx:
                    # 3a. Return cached approximate result instantly
                    latency = time.time() - start_time
                    lz_client.record_metrics(cache_hit=True, latency=latency)
                    
                    # Optionally refine in background
                    if enable_refinement:
                        lz_client.refine_in_background(
                            function_name,
                            func,
                            args,
                            kwargs,
                            input_hash
                        )
                    
                    # Add metadata to result if it's a dict
                    result = approx['result']
                    if isinstance(result, dict):
                        result['_latencyzero'] = {
                            'approximated': True,
                            'confidence': approx['confidence'],
                            'latency_ms': latency * 1000,
                            'semantic_match': approx.get('semantic_match', False)
                        }
                    
                    return result
                
                else:
                    # 3b. Fall back to exact computation
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Store for future approximations
                    # ENHANCED: Pass args/kwargs for semantic learning
                    lz_client.store_result(
                        function_name,
                        input_hash,
                        result,
                        execution_time,
                        args=args,  # NEW: For semantic learning
                        kwargs=kwargs  # NEW: For semantic learning
                    )
                    
                    lz_client.record_metrics(cache_hit=False, latency=execution_time)
                    
                    return result
            
            except Exception as e:
                if fallback_on_error:
                    # On any error, compute exactly
                    print(f"[LatencyZero] Error, falling back: {e}")
                    return func(*args, **kwargs)
                else:
                    raise
        
        # Add utility methods to the wrapper
        wrapper._latencyzero_enabled = True
        wrapper._original_func = func
        
        def get_stats():
            """Get statistics for this function"""
            return lz_client.get_stats()
        
        def disable():
            """Temporarily disable A³ for this function"""
            wrapper._latencyzero_enabled = False
        
        def enable():
            """Re-enable A³ for this function"""
            wrapper._latencyzero_enabled = True
        
        wrapper.get_stats = get_stats
        wrapper.disable = disable
        wrapper.enable = enable
        
        return wrapper
    
    return decorator