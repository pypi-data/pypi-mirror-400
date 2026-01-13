"""
Formal Error Bounds & SLA Guarantees
Enterprise-grade accuracy tracking with guarantees
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time


class ErrorBoundType(Enum):
    """Types of error bounds we can provide"""
    ABSOLUTE = "absolute"      # |approximation - exact| <= ε
    RELATIVE = "relative"      # |approx - exact| / |exact| <= ε  
    PERCENTILE = "percentile"  # 95% of errors <= ε
    PROBABILISTIC = "probabilistic"  # P(error <= ε) >= 0.95


@dataclass
class ErrorBound:
    """
    Formal error bound for an approximation
    
    This is what enterprises need for SLAs
    """
    bound_type: ErrorBoundType
    max_error: float
    confidence_level: float  # 0.95 = 95% confidence
    sample_size: int
    historical_accuracy: float
    worst_case_error: Optional[float] = None
    
    def __str__(self):
        if self.bound_type == ErrorBoundType.ABSOLUTE:
            return f"Error ≤ {self.max_error:.4f} with {self.confidence_level*100:.1f}% confidence"
        elif self.bound_type == ErrorBoundType.RELATIVE:
            return f"Relative error ≤ {self.max_error*100:.1f}% with {self.confidence_level*100:.1f}% confidence"
        elif self.bound_type == ErrorBoundType.PERCENTILE:
            return f"P95 error ≤ {self.max_error:.4f}"
        else:
            return f"P(error ≤ {self.max_error:.4f}) ≥ {self.confidence_level*100:.1f}%"


@dataclass
class AccuracyMetrics:
    """Historical accuracy metrics for a function"""
    total_measurements: int
    mean_error: float
    std_error: float
    p50_error: float  # Median
    p95_error: float  # 95th percentile
    p99_error: float  # 99th percentile
    max_error: float  # Worst case observed
    last_updated: float


class FormalErrorBounds:
    """
    Provides formal error bounds and SLA guarantees
    
    This is the enterprise moat:
    - Track actual errors over time
    - Compute statistical bounds
    - Provide SLA guarantees
    - Alert when bounds are violated
    """
    
    def __init__(self):
        # Historical errors per function
        self.error_history: Dict[str, List[float]] = {}
        
        # Accuracy metrics per function
        self.metrics: Dict[str, AccuracyMetrics] = {}
        
        # SLA violations
        self.sla_violations: List[Dict] = []
        
        # Configuration
        self.max_history_size = 1000
        self.min_samples_for_bounds = 30
    
    def record_error(
        self,
        function: str,
        approximation: any,
        exact: any,
        timestamp: float = None
    ):
        """
        Record the error between approximation and exact result
        
        This builds up historical data for bounds
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate error
        error = self._calculate_error(approximation, exact)
        
        # Store in history
        if function not in self.error_history:
            self.error_history[function] = []
        
        self.error_history[function].append(error)
        
        # Limit history size
        if len(self.error_history[function]) > self.max_history_size:
            self.error_history[function].pop(0)
        
        # Update metrics
        self._update_metrics(function)
    
    def get_error_bound(
        self,
        function: str,
        bound_type: ErrorBoundType = ErrorBoundType.PERCENTILE,
        confidence_level: float = 0.95
    ) -> Optional[ErrorBound]:
        """
        Get formal error bound for a function
        
        This is what you put in the SLA!
        """
        if function not in self.error_history:
            return None
        
        errors = np.array(self.error_history[function])
        
        if len(errors) < self.min_samples_for_bounds:
            return None  # Not enough data
        
        if bound_type == ErrorBoundType.ABSOLUTE:
            # Use confidence interval
            mean = np.mean(errors)
            std = np.std(errors)
            
            # z-score for confidence level
            from scipy import stats
            z = stats.norm.ppf((1 + confidence_level) / 2)
            
            max_error = mean + z * std / np.sqrt(len(errors))
            
            return ErrorBound(
                bound_type=bound_type,
                max_error=max_error,
                confidence_level=confidence_level,
                sample_size=len(errors),
                historical_accuracy=1 - mean,
                worst_case_error=np.max(errors)
            )
        
        elif bound_type == ErrorBoundType.PERCENTILE:
            # Use percentile directly
            percentile = int(confidence_level * 100)
            max_error = np.percentile(errors, percentile)
            
            return ErrorBound(
                bound_type=bound_type,
                max_error=max_error,
                confidence_level=confidence_level,
                sample_size=len(errors),
                historical_accuracy=1 - np.mean(errors),
                worst_case_error=np.max(errors)
            )
        
        elif bound_type == ErrorBoundType.PROBABILISTIC:
            # Empirical probability
            threshold = np.percentile(errors, confidence_level * 100)
            prob = np.mean(errors <= threshold)
            
            return ErrorBound(
                bound_type=bound_type,
                max_error=threshold,
                confidence_level=prob,
                sample_size=len(errors),
                historical_accuracy=1 - np.mean(errors),
                worst_case_error=np.max(errors)
            )
    
    def get_sla_compliance(
        self,
        function: str,
        sla_max_error: float,
        sla_confidence: float = 0.95
    ) -> Dict:
        """
        Check if function meets SLA requirements
        
        Returns compliance report
        """
        if function not in self.error_history:
            return {
                'compliant': None,
                'reason': 'No data available'
            }
        
        errors = np.array(self.error_history[function])
        
        # Check compliance
        violations = np.sum(errors > sla_max_error)
        compliance_rate = 1 - (violations / len(errors))
        
        compliant = compliance_rate >= sla_confidence
        
        return {
            'compliant': compliant,
            'sla_max_error': sla_max_error,
            'sla_confidence': sla_confidence,
            'actual_compliance_rate': compliance_rate,
            'violations': int(violations),
            'total_samples': len(errors),
            'mean_error': float(np.mean(errors)),
            'p95_error': float(np.percentile(errors, 95)),
            'worst_error': float(np.max(errors))
        }
    
    def get_accuracy_guarantee(
        self,
        function: str,
        tolerance: float
    ) -> Optional[Dict]:
        """
        Get accuracy guarantee based on historical data
        
        Returns: What accuracy can we GUARANTEE with this tolerance?
        """
        if function not in self.metrics:
            return None
        
        metrics = self.metrics[function]
        
        # Calculate probability of meeting tolerance
        errors = np.array(self.error_history[function])
        meets_tolerance = np.sum(errors <= tolerance)
        probability = meets_tolerance / len(errors)
        
        return {
            'tolerance': tolerance,
            'guaranteed_accuracy': probability,
            'sample_size': len(errors),
            'mean_error': metrics.mean_error,
            'p95_error': metrics.p95_error,
            'worst_case': metrics.max_error,
            'recommendation': self._get_tolerance_recommendation(errors, tolerance)
        }
    
    def check_sla_violation(
        self,
        function: str,
        error: float,
        sla_threshold: float
    ) -> bool:
        """
        Check if this error violates SLA
        
        Log violations for reporting
        """
        if error > sla_threshold:
            self.sla_violations.append({
                'function': function,
                'error': error,
                'threshold': sla_threshold,
                'timestamp': time.time(),
                'severity': 'critical' if error > sla_threshold * 2 else 'warning'
            })
            return True
        
        return False
    
    def _calculate_error(self, approximation: any, exact: any) -> float:
        """
        Calculate error between approximation and exact result
        
        Handles different data types intelligently
        """
        # Numeric values
        if isinstance(approximation, (int, float)) and isinstance(exact, (int, float)):
            if exact == 0:
                return abs(approximation - exact)
            else:
                # Relative error
                return abs(approximation - exact) / abs(exact)
        
        # Strings (edit distance)
        elif isinstance(approximation, str) and isinstance(exact, str):
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, approximation, exact).ratio()
            return 1 - similarity  # Convert similarity to error
        
        # Lists/arrays
        elif isinstance(approximation, (list, np.ndarray)) and isinstance(exact, (list, np.ndarray)):
            approx_arr = np.array(approximation)
            exact_arr = np.array(exact)
            
            if exact_arr.size == 0:
                return 0.0
            
            # Normalized L2 distance
            return np.linalg.norm(approx_arr - exact_arr) / np.linalg.norm(exact_arr)
        
        # Dictionaries
        elif isinstance(approximation, dict) and isinstance(exact, dict):
            # Average error across numeric values
            errors = []
            for key in set(approximation.keys()) & set(exact.keys()):
                if isinstance(approximation[key], (int, float)) and isinstance(exact[key], (int, float)):
                    if exact[key] != 0:
                        errors.append(abs(approximation[key] - exact[key]) / abs(exact[key]))
                    else:
                        errors.append(abs(approximation[key] - exact[key]))
            
            return np.mean(errors) if errors else 0.0
        
        # Default: exact match
        else:
            return 0.0 if approximation == exact else 1.0
    
    def _update_metrics(self, function: str):
        """Update accuracy metrics for function"""
        errors = np.array(self.error_history[function])
        
        self.metrics[function] = AccuracyMetrics(
            total_measurements=len(errors),
            mean_error=float(np.mean(errors)),
            std_error=float(np.std(errors)),
            p50_error=float(np.percentile(errors, 50)),
            p95_error=float(np.percentile(errors, 95)),
            p99_error=float(np.percentile(errors, 99)),
            max_error=float(np.max(errors)),
            last_updated=time.time()
        )
    
    def _get_tolerance_recommendation(
        self,
        errors: np.ndarray,
        current_tolerance: float
    ) -> str:
        """Recommend tolerance adjustment based on error distribution"""
        p95 = np.percentile(errors, 95)
        
        if p95 < current_tolerance * 0.5:
            return f"Consider lowering tolerance to {p95:.4f} for stricter accuracy"
        elif p95 > current_tolerance:
            return f"Consider raising tolerance to {p95:.4f} to improve cache hit rate"
        else:
            return "Current tolerance is appropriate"
    
    def get_sla_report(self) -> Dict:
        """Generate SLA compliance report"""
        report = {
            'total_functions': len(self.metrics),
            'functions': {},
            'violations': {
                'total': len(self.sla_violations),
                'critical': sum(1 for v in self.sla_violations if v['severity'] == 'critical'),
                'warning': sum(1 for v in self.sla_violations if v['severity'] == 'warning'),
                'recent': self.sla_violations[-10:]  # Last 10 violations
            }
        }
        
        for function, metrics in self.metrics.items():
            report['functions'][function] = {
                'samples': metrics.total_measurements,
                'mean_error': f"{metrics.mean_error*100:.2f}%",
                'p95_error': f"{metrics.p95_error*100:.2f}%",
                'p99_error': f"{metrics.p99_error*100:.2f}%",
                'worst_case': f"{metrics.max_error*100:.2f}%"
            }
        
        return report


# Example usage
if __name__ == "__main__":
    error_bounds = FormalErrorBounds()
    
    # Simulate measurements
    print("Simulating error measurements...\n")
    
    for i in range(100):
        # Exact result
        exact = 100.0
        
        # Approximation with some error
        approx = exact + np.random.normal(0, 2.0)
        
        error_bounds.record_error("api_call", approx, exact)
    
    # Get error bound
    bound = error_bounds.get_error_bound("api_call")
    if bound:
        print(f"✅ Error Bound: {bound}\n")
    
    # Check SLA compliance
    sla = error_bounds.get_sla_compliance("api_call", sla_max_error=0.05)
    print(f"📊 SLA Compliance:")
    print(f"   Required: Error ≤ 5% for 95% of requests")
    print(f"   Actual: {sla['actual_compliance_rate']*100:.1f}% compliance")
    print(f"   Status: {'✅ COMPLIANT' if sla['compliant'] else '❌ NON-COMPLIANT'}\n")
    
    # Get accuracy guarantee
    guarantee = error_bounds.get_accuracy_guarantee("api_call", tolerance=0.05)
    if guarantee:
        print(f"🎯 Accuracy Guarantee (5% tolerance):")
        print(f"   Guaranteed accuracy: {guarantee['guaranteed_accuracy']*100:.1f}%")
        print(f"   P95 error: {guarantee['p95_error']*100:.2f}%")
        print(f"   Worst case: {guarantee['worst_case']*100:.2f}%")