"""
Prediction Engine - Learns patterns and predicts next queries
Uses sliding windows and frequency sketching
"""

import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple
import heapq


class PredictionEngine:
    """
    Predicts upcoming queries based on historical patterns
    
    Uses:
    - Sliding window of recent queries
    - Frequency counting
    - Temporal locality
    - Pattern detection
    """
    
    def __init__(self, window_size: int = 1000, decay_factor: float = 0.95):
        self.window_size = window_size
        self.decay_factor = decay_factor
        
        # Sliding window of recent queries: (function, hash, timestamp)
        self.query_window: deque = deque(maxlen=window_size)
        
        # Frequency counts per function
        self.frequency: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Temporal patterns: query -> next queries
        self.transitions: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'unique_functions': set(),
            'patterns_detected': 0
        }
    
    def record_query(self, function: str, query_hash: str):
        """Record a new query"""
        timestamp = time.time()
        
        # Add to window
        self.query_window.append((function, query_hash, timestamp))
        
        # Update frequency (with decay)
        self._decay_frequencies(function)
        self.frequency[function][query_hash] += 1.0
        
        # Update transitions (what comes after what)
        if len(self.query_window) >= 2:
            prev = self.query_window[-2]
            if prev[0] == function:  # Same function
                self.transitions[(function, prev[1])][query_hash] += 1
        
        # Update stats
        self.stats['total_queries'] += 1
        self.stats['unique_functions'].add(function)
    
    def record_hit(self, function: str, query_hash: str):
        """Record a cache hit (increases confidence)"""
        self.frequency[function][query_hash] *= 1.1  # Boost frequently hit queries
    
    def predict_next(self, function: str, limit: int = 10) -> List[Dict]:
        """
        Predict the next K most likely queries for a function
        
        Returns list of predictions with scores
        """
        predictions = []
        
        # Get frequency-based predictions
        freq_scores = self.frequency.get(function, {})
        
        # Get transition-based predictions
        trans_scores = defaultdict(float)
        if self.query_window:
            last_query = None
            for f, h, t in reversed(self.query_window):
                if f == function:
                    last_query = h
                    break
            
            if last_query:
                transitions = self.transitions.get((function, last_query), {})
                for next_hash, count in transitions.items():
                    trans_scores[next_hash] = count
        
        # Combine scores (weighted)
        combined_scores = {}
        for query_hash in set(list(freq_scores.keys()) + list(trans_scores.keys())):
            freq = freq_scores.get(query_hash, 0)
            trans = trans_scores.get(query_hash, 0)
            
            # Weighted combination (favor transitions for recent patterns)
            combined_scores[query_hash] = (0.6 * freq) + (0.4 * trans)
        
        # Get top K
        top_k = heapq.nlargest(limit, combined_scores.items(), key=lambda x: x[1])
        
        for query_hash, score in top_k:
            predictions.append({
                'hash': query_hash,
                'score': score,
                'frequency': freq_scores.get(query_hash, 0),
                'transition_score': trans_scores.get(query_hash, 0)
            })
        
        return predictions
    
    def should_prewarm(self, function: str, query_hash: str) -> bool:
        """
        Decide if we should pre-warm this query
        
        Pre-warm if:
        - High frequency
        - Strong temporal pattern
        - Recently accessed
        """
        freq = self.frequency.get(function, {}).get(query_hash, 0)
        
        # Check if in recent window
        recent = any(
            f == function and h == query_hash
            for f, h, t in list(self.query_window)[-100:]
        )
        
        # Pre-warm if frequency > threshold OR recent
        return freq > 5.0 or recent
    
    def _decay_frequencies(self, function: str):
        """Apply decay to frequencies to favor recent patterns"""
        for query_hash in self.frequency[function]:
            self.frequency[function][query_hash] *= self.decay_factor
    
    def get_stats(self) -> Dict:
        """Get prediction engine statistics"""
        patterns_count = sum(len(v) for v in self.transitions.values())
        
        return {
            'total_queries': self.stats['total_queries'],
            'unique_functions': len(self.stats['unique_functions']),
            'patterns_detected': patterns_count,
            'window_size': len(self.query_window),
            'functions_tracked': len(self.frequency)
        }
