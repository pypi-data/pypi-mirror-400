"""
Confidence Evaluator - DEMO VERSION (Ultra Permissive)
This version is optimized to show cache hits in demos
"""

import time
import math
from typing import Dict, Any


class ConfidenceEvaluator:
    """
    Evaluates confidence in approximations
    DEMO VERSION - Very permissive for showcasing cache hits
    """
    
    def __init__(self):
        # Track accuracy per function
        self.accuracy_history: Dict[str, list] = {}
        
        # DEMO CONFIGURATION - Very permissive
        self.max_age_seconds = 3600  # 1 hour
        self.min_hit_count = 0  # No minimum hits required
        
        # Statistics
        self.stats = {
            'total_evaluations': 0,
            'high_confidence': 0,
            'low_confidence': 0,
            'rejected_too_old': 0,
            'rejected_low_hits': 0
        }
    
    def evaluate(
        self,
        function: str,
        hash: str,
        stored_data: Dict[str, Any],
        tolerance: float
    ) -> float:
        """
        Evaluate confidence in approximation
        
        Returns confidence score between 0 and 1
        For DEMO: Returns high confidence for recent cache entries
        """
        self.stats['total_evaluations'] += 1
        
        # Factor 1: Age (fresher = better)
        age_seconds = time.time() - stored_data['timestamp']
        age_confidence = self._calculate_age_confidence(age_seconds)
        
        # Factor 2: Hit count
        hit_count = stored_data.get('hit_count', 0)
        hit_confidence = self._calculate_hit_confidence(hit_count)
        
        # Factor 3: Historical accuracy
        historical_confidence = self._get_historical_confidence(function)
        
        # Factor 4: Execution time variance
        variance_confidence = self._calculate_variance_confidence(
            function,
            stored_data['execution_time']
        )
        
        # DEMO: More permissive weighting
        # Give more weight to age (fresh entries get high scores)
        weights = {
            'age': 0.5,      # Was 0.3, now 0.5 (favor fresh)
            'hits': 0.1,     # Was 0.25, now 0.1 (don't penalize new)
            'history': 0.2,  # Was 0.25
            'variance': 0.2  # Was 0.2
        }
        
        confidence = (
            weights['age'] * age_confidence +
            weights['hits'] * hit_confidence +
            weights['history'] * historical_confidence +
            weights['variance'] * variance_confidence
        )
        
        # Track statistics
        if confidence >= 0.8:
            self.stats['high_confidence'] += 1
        else:
            self.stats['low_confidence'] += 1
        
        # Apply hard limits
        if age_seconds > self.max_age_seconds:
            self.stats['rejected_too_old'] += 1
            return 0.0
        
        # DEMO: Don't penalize low hit counts
        # Just use the confidence as-is
        
        return min(confidence, 1.0)
    
    def _calculate_age_confidence(self, age_seconds: float) -> float:
        """
        DEMO: Very generous age confidence
        Fresh results (< 5 min) get near-perfect scores
        """
        if age_seconds < 60:
            return 1.0  # < 1 minute = perfect
        elif age_seconds < 300:
            return 0.95  # < 5 minutes = excellent
        elif age_seconds < 600:
            return 0.90  # < 10 minutes = great
        elif age_seconds < 1800:
            return 0.85  # < 30 minutes = good
        elif age_seconds < self.max_age_seconds:
            # Gentle exponential decay
            decay_rate = 0.0003
            return max(0.7, math.exp(-decay_rate * age_seconds))
        else:
            return 0.0
    
    def _calculate_hit_confidence(self, hit_count: int) -> float:
        """
        DEMO: Start with high confidence even for new entries
        """
        if hit_count == 0:
            return 0.85  # NEW: Start high for demo
        elif hit_count < 5:
            return 0.90 + (hit_count * 0.01)
        elif hit_count < 20:
            return 0.95 + (hit_count * 0.002)
        else:
            return 1.0
    
    def _get_historical_confidence(self, function: str) -> float:
        """
        DEMO: Start with optimistic default
        """
        if function not in self.accuracy_history:
            return 0.90  # NEW: Optimistic default for demo
        
        history = self.accuracy_history[function]
        if not history:
            return 0.90
        
        # Calculate average accuracy
        avg_accuracy = sum(history) / len(history)
        return avg_accuracy
    
    def _calculate_variance_confidence(
        self,
        function: str,
        execution_time: float
    ) -> float:
        """
        DEMO: Assume medium-high confidence
        """
        return 0.90  # Optimistic default
    
    def record_accuracy(self, function: str, accuracy: float):
        """
        Record accuracy after refinement
        """
        if function not in self.accuracy_history:
            self.accuracy_history[function] = []
        
        # Keep last 100 accuracy measurements
        history = self.accuracy_history[function]
        history.append(accuracy)
        if len(history) > 100:
            history.pop(0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get evaluator statistics"""
        total = self.stats['total_evaluations']
        if total == 0:
            high_pct = 0
            low_pct = 0
        else:
            high_pct = (self.stats['high_confidence'] / total) * 100
            low_pct = (self.stats['low_confidence'] / total) * 100
        
        return {
            'total_evaluations': total,
            'high_confidence_rate': high_pct,
            'low_confidence_rate': low_pct,
            'rejected_too_old': self.stats['rejected_too_old'],
            'rejected_low_hits': self.stats['rejected_low_hits'],
            'functions_tracked': len(self.accuracy_history)
        }