"""
Stale-on-Error: Resilience Layer
Serve cached results when upstream fails

This turns LatencyZero into a reliability enhancement, not just speed
"""

import time
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass


class FailureMode(Enum):
    """Types of upstream failures"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"


@dataclass
class StaleResult:
    """Cached result that's being served during outage"""
    result: Any
    cached_at: float
    age_seconds: float
    confidence: float
    stale: bool = True
    failure_reason: Optional[str] = None


class ResilienceConfig:
    """Configuration for resilience behavior"""
    
    def __init__(
        self,
        max_stale_age: float = 3600,  # Serve stale up to 1 hour
        min_confidence_for_stale: float = 0.70,  # Only serve high-confidence stale results
        circuit_breaker_threshold: int = 5,  # Trip after 5 failures
        circuit_breaker_timeout: float = 60,  # Try again after 60s
        enable_degraded_mode: bool = True,
        alert_on_stale_serving: bool = True
    ):
        self.max_stale_age = max_stale_age
        self.min_confidence_for_stale = min_confidence_for_stale
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.enable_degraded_mode = enable_degraded_mode
        self.alert_on_stale_serving = alert_on_stale_serving


class CircuitBreaker:
    """
    Circuit breaker for upstream services
    
    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, don't even try
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"⚠️  Circuit breaker OPEN ({self.failure_count} failures)")
    
    def should_attempt(self) -> bool:
        """Should we attempt to call upstream?"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if timeout expired
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                print("🔄 Circuit breaker HALF_OPEN (testing)")
                return True
            return False
        
        # HALF_OPEN: allow one test call
        return True


class StaleOnErrorLayer:
    """
    Resilience layer that serves stale results on upstream failures
    
    This is THE differentiator - competitors don't have this!
    
    Use cases:
    - API goes down → Serve last known good result
    - Rate limit hit → Serve cached data
    - Slow response → Serve approximate result instantly
    - Partial outage → Gracefully degrade
    """
    
    def __init__(self, config: Optional[ResilienceConfig] = None):
        self.config = config or ResilienceConfig()
        
        # Circuit breakers per function
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Failure tracking
        self.failure_history: Dict[str, list] = {}
        
        # Stale serving stats
        self.stats = {
            'total_requests': 0,
            'upstream_failures': 0,
            'stale_served': 0,
            'stale_rejected': 0,
            'circuit_breaker_opens': 0
        }
    
    def execute_with_resilience(
        self,
        function_name: str,
        upstream_call: Callable,
        get_cached: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with resilience guarantees
        
        Flow:
        1. Try upstream call
        2. If fails, check if we can serve stale
        3. If stale available and fresh enough → serve it
        4. If stale too old or low confidence → raise error
        5. Update circuit breaker
        """
        self.stats['total_requests'] += 1
        
        # Get circuit breaker
        if function_name not in self.circuit_breakers:
            self.circuit_breakers[function_name] = CircuitBreaker(
                self.config.circuit_breaker_threshold,
                self.config.circuit_breaker_timeout
            )
        
        breaker = self.circuit_breakers[function_name]
        
        # Check circuit breaker
        if not breaker.should_attempt():
            print(f"⚠️  Circuit OPEN, serving stale immediately")
            return self._serve_stale(function_name, get_cached, FailureMode.RATE_LIMIT)
        
        # Try upstream call
        try:
            result = upstream_call(*args, **kwargs)
            
            # Success!
            breaker.record_success()
            return result
        
        except Exception as e:
            # Upstream failed
            self.stats['upstream_failures'] += 1
            
            failure_mode = self._classify_failure(e)
            
            # Record failure
            self._record_failure(function_name, failure_mode)
            breaker.record_failure()
            
            # Try to serve stale
            if self.config.enable_degraded_mode:
                return self._serve_stale(function_name, get_cached, failure_mode)
            else:
                raise
    
    def _serve_stale(
        self,
        function_name: str,
        get_cached: Callable,
        failure_mode: FailureMode
    ) -> StaleResult:
        """
        Serve stale cached result
        
        Only if:
        1. Cache exists
        2. Not too old
        3. High enough confidence
        """
        # Try to get cached result
        cached = get_cached()
        
        if not cached:
            self.stats['stale_rejected'] += 1
            raise Exception(f"Upstream failed and no cache available: {failure_mode.value}")
        
        # Check age
        age = time.time() - cached['timestamp']
        
        if age > self.config.max_stale_age:
            self.stats['stale_rejected'] += 1
            raise Exception(
                f"Upstream failed and cache too stale "
                f"({age/60:.1f} min > {self.config.max_stale_age/60:.1f} min max)"
            )
        
        # Check confidence
        confidence = cached.get('confidence', 0.0)
        
        if confidence < self.config.min_confidence_for_stale:
            self.stats['stale_rejected'] += 1
            raise Exception(
                f"Upstream failed and cache confidence too low "
                f"({confidence:.2f} < {self.config.min_confidence_for_stale:.2f} required)"
            )
        
        # Serve stale!
        self.stats['stale_served'] += 1
        
        if self.config.alert_on_stale_serving:
            print(f"""
⚠️  SERVING STALE RESULT
   Function: {function_name}
   Reason: {failure_mode.value}
   Age: {age/60:.1f} minutes
   Confidence: {confidence*100:.1f}%
   
   Upstream is down, serving last known good result.
            """)
        
        return StaleResult(
            result=cached['result'],
            cached_at=cached['timestamp'],
            age_seconds=age,
            confidence=confidence,
            stale=True,
            failure_reason=failure_mode.value
        )
    
    def _classify_failure(self, error: Exception) -> FailureMode:
        """Classify what type of failure occurred"""
        error_str = str(error).lower()
        
        if "timeout" in error_str or "timed out" in error_str:
            return FailureMode.TIMEOUT
        elif "connection" in error_str or "unreachable" in error_str:
            return FailureMode.CONNECTION_ERROR
        elif "rate limit" in error_str or "429" in error_str:
            return FailureMode.RATE_LIMIT
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            return FailureMode.SERVER_ERROR
        else:
            return FailureMode.UNKNOWN
    
    def _record_failure(self, function_name: str, failure_mode: FailureMode):
        """Record failure for tracking"""
        if function_name not in self.failure_history:
            self.failure_history[function_name] = []
        
        self.failure_history[function_name].append({
            'mode': failure_mode.value,
            'timestamp': time.time()
        })
        
        # Keep last 100 failures
        if len(self.failure_history[function_name]) > 100:
            self.failure_history[function_name].pop(0)
    
    def get_failure_report(self) -> Dict:
        """Generate failure report for monitoring"""
        report = {
            'total_requests': self.stats['total_requests'],
            'upstream_failures': self.stats['upstream_failures'],
            'failure_rate': 0,
            'stale_served': self.stats['stale_served'],
            'stale_success_rate': 0,
            'circuit_breakers': {}
        }
        
        if self.stats['total_requests'] > 0:
            report['failure_rate'] = (
                self.stats['upstream_failures'] / self.stats['total_requests']
            )
        
        if self.stats['upstream_failures'] > 0:
            report['stale_success_rate'] = (
                self.stats['stale_served'] / self.stats['upstream_failures']
            )
        
        # Circuit breaker states
        for func, breaker in self.circuit_breakers.items():
            report['circuit_breakers'][func] = {
                'state': breaker.state,
                'failures': breaker.failure_count
            }
        
        return report
    
    def get_resilience_metrics(self) -> Dict:
        """Get resilience metrics for dashboard"""
        total_failures = self.stats['upstream_failures']
        
        if total_failures == 0:
            return {
                'uptime_effective': 100.0,
                'stale_serving_rate': 0.0,
                'resilience_score': 100.0
            }
        
        # Calculate effective uptime (including stale serving)
        effective_success = (
            self.stats['total_requests'] - 
            self.stats['upstream_failures'] + 
            self.stats['stale_served']
        )
        
        effective_uptime = (effective_success / self.stats['total_requests']) * 100
        
        stale_serving_rate = (self.stats['stale_served'] / total_failures) * 100
        
        # Resilience score: How often do we successfully handle failures?
        resilience_score = stale_serving_rate
        
        return {
            'uptime_effective': effective_uptime,
            'uptime_upstream': ((self.stats['total_requests'] - total_failures) / self.stats['total_requests']) * 100,
            'stale_serving_rate': stale_serving_rate,
            'resilience_score': resilience_score,
            'total_requests': self.stats['total_requests'],
            'upstream_failures': total_failures,
            'stale_served': self.stats['stale_served']
        }


# Example usage
if __name__ == "__main__":
    config = ResilienceConfig(
        max_stale_age=300,  # 5 minutes
        min_confidence_for_stale=0.80,
        circuit_breaker_threshold=3
    )
    
    resilience = StaleOnErrorLayer(config)
    
    # Simulate failures
    print("Simulating upstream failures with stale serving...\n")
    
    def failing_upstream():
        """Upstream that fails"""
        raise ConnectionError("Service unavailable")
    
    def get_cached():
        """Return cached result"""
        return {
            'result': {'answer': 'cached response'},
            'timestamp': time.time() - 60,  # 1 minute old
            'confidence': 0.95
        }
    
    try:
        # First few calls will fail
        for i in range(5):
            try:
                result = resilience.execute_with_resilience(
                    "api_call",
                    failing_upstream,
                    get_cached
                )
                
                if isinstance(result, StaleResult):
                    print(f"✅ Call {i+1}: Served stale (age: {result.age_seconds:.0f}s)\n")
                else:
                    print(f"✅ Call {i+1}: Fresh result\n")
            
            except Exception as e:
                print(f"❌ Call {i+1}: Failed - {e}\n")
    
    finally:
        # Show metrics
        metrics = resilience.get_resilience_metrics()
        print("\n" + "="*70)
        print("RESILIENCE METRICS")
        print("="*70)
        print(f"Upstream uptime: {metrics['uptime_upstream']:.1f}%")
        print(f"Effective uptime (with stale): {metrics['uptime_effective']:.1f}%")
        print(f"Resilience score: {metrics['resilience_score']:.1f}%")
        print(f"\nTotal requests: {metrics['total_requests']}")
        print(f"Upstream failures: {metrics['upstream_failures']}")
        print(f"Stale served: {metrics['stale_served']}")
        
        print("\n💡 Resilience Impact:")
        print(f"   Without stale-on-error: {metrics['uptime_upstream']:.1f}% uptime")
        print(f"   With stale-on-error: {metrics['uptime_effective']:.1f}% uptime")
        print(f"   Improvement: +{metrics['uptime_effective'] - metrics['uptime_upstream']:.1f}%")