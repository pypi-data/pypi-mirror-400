"""
Advanced Prediction Engine with ML & Semantic Understanding
Makes LatencyZero truly intelligent and defensible
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
import time
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Install: pip install sentence-transformers")

try:
    from sklearn.cluster import DBSCAN
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  scikit-learn not installed. Install: pip install scikit-learn")


class AdvancedPredictionEngine:
    """
    ML-powered prediction with semantic understanding
    
    Features:
    1. Semantic similarity (embeddings)
    2. Clustering of related queries
    3. Interpolation for similar inputs
    4. Pattern learning across semantically similar queries
    
    This is the MOAT - hard to replicate
    """
    
    def __init__(
        self,
        use_embeddings: bool = True,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.85,
        window_size: int = 1000
    ):
        self.window_size = window_size
        self.similarity_threshold = similarity_threshold
        
        # Original heuristic tracking
        self.query_window: deque = deque(maxlen=window_size)
        self.frequency: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # 🔥 NEW: Semantic understanding
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE and SKLEARN_AVAILABLE
        
        if self.use_embeddings:
            print(f"✅ Loading semantic model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            
            # Store embeddings for each query
            self.query_embeddings: Dict[Tuple[str, str], np.ndarray] = {}
            
            # Cluster queries by semantic similarity
            self.query_clusters: Dict[str, List[List[str]]] = defaultdict(list)
            
            # Track which queries are semantically similar
            self.similar_queries: Dict[str, Dict[str, List[Tuple[str, float]]]] = defaultdict(
                lambda: defaultdict(list)
            )
        else:
            print("⚠️  Running without embeddings (heuristic mode)")
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'semantic_predictions': 0,
            'heuristic_predictions': 0,
            'interpolations': 0
        }
    
    def record_query(self, function: str, query_input: any, query_hash: str):
        """
        Record query with semantic analysis
        
        This is where the magic happens:
        1. Generate embedding
        2. Find similar past queries
        3. Build semantic clusters
        4. Enable interpolation
        """
        timestamp = time.time()
        
        # Basic tracking (same as before)
        self.query_window.append((function, query_hash, timestamp))
        self.frequency[function][query_hash] += 1.0
        self.stats['total_queries'] += 1
        
        # 🔥 NEW: Semantic analysis
        if self.use_embeddings:
            try:
                # Convert query to embedding
                embedding = self._get_embedding(function, query_input, query_hash)
                
                # Find semantically similar past queries
                similar = self._find_similar_queries(function, query_hash, embedding)
                
                # Store similarity relationships
                if similar:
                    self.similar_queries[function][query_hash] = similar
                    self.stats['semantic_predictions'] += 1
                
                # Update clusters periodically
                if len(self.query_embeddings) % 50 == 0:
                    self._update_clusters(function)
            
            except Exception as e:
                print(f"⚠️  Semantic analysis failed: {e}")
        else:
            self.stats['heuristic_predictions'] += 1
    
    def predict_next(
        self,
        function: str,
        current_input: any = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Predict next queries using both:
        1. Heuristic patterns (frequency, transitions)
        2. Semantic similarity (embeddings)
        
        Returns predictions sorted by confidence
        """
        predictions = []
        
        # Method 1: Heuristic predictions (original)
        heuristic_scores = self._get_heuristic_predictions(function)
        
        # Method 2: Semantic predictions (NEW)
        semantic_scores = {}
        if self.use_embeddings and current_input:
            semantic_scores = self._get_semantic_predictions(function, current_input)
        
        # Combine both methods (weighted)
        combined_scores = {}
        
        for query_hash in set(list(heuristic_scores.keys()) + list(semantic_scores.keys())):
            heuristic = heuristic_scores.get(query_hash, 0)
            semantic = semantic_scores.get(query_hash, 0)
            
            # Weight: 40% heuristic, 60% semantic (semantic is more powerful)
            combined_scores[query_hash] = (0.4 * heuristic) + (0.6 * semantic)
        
        # Sort by score
        sorted_predictions = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        for query_hash, score in sorted_predictions:
            predictions.append({
                'hash': query_hash,
                'score': score,
                'heuristic_score': heuristic_scores.get(query_hash, 0),
                'semantic_score': semantic_scores.get(query_hash, 0),
                'method': 'semantic' if semantic_scores.get(query_hash, 0) > 0 else 'heuristic'
            })
        
        return predictions
    
    def can_interpolate(
        self,
        function: str,
        query_input: any,
        query_hash: str
    ) -> Optional[List[Tuple[str, float]]]:
        """
        Check if we can interpolate from similar queries
        
        This enables approximation even for NEW queries
        that we've never seen before!
        
        Returns: List of (similar_hash, similarity_score) tuples
        """
        if not self.use_embeddings:
            return None
        
        try:
            # Get embedding for new query
            embedding = self._get_embedding(function, query_input, query_hash)
            
            # Find similar queries
            similar = self._find_similar_queries(
                function,
                query_hash,
                embedding,
                min_similarity=self.similarity_threshold
            )
            
            if similar and len(similar) >= 2:
                self.stats['interpolations'] += 1
                return similar
            
            return None
        
        except Exception as e:
            print(f"⚠️  Interpolation check failed: {e}")
            return None
    
    def _get_embedding(
        self,
        function: str,
        query_input: any,
        query_hash: str
    ) -> np.ndarray:
        """Generate embedding for query input"""
        
        # Check cache first
        cache_key = (function, query_hash)
        if cache_key in self.query_embeddings:
            return self.query_embeddings[cache_key]
        
        # Convert input to string for embedding
        if isinstance(query_input, str):
            text = query_input
        elif isinstance(query_input, dict):
            text = str(query_input)
        elif isinstance(query_input, (list, tuple)):
            text = ' '.join(str(x) for x in query_input)
        else:
            text = str(query_input)
        
        # Generate embedding
        embedding = self.embedding_model.encode([text])[0]
        
        # Cache it
        self.query_embeddings[cache_key] = embedding
        
        return embedding
    
    def _find_similar_queries(
        self,
        function: str,
        query_hash: str,
        embedding: np.ndarray,
        min_similarity: float = 0.80
    ) -> List[Tuple[str, float]]:
        """Find semantically similar past queries"""
        
        similar = []
        
        # Compare with all past queries for this function
        for (past_func, past_hash), past_embedding in self.query_embeddings.items():
            if past_func != function or past_hash == query_hash:
                continue
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                embedding.reshape(1, -1),
                past_embedding.reshape(1, -1)
            )[0][0]
            
            if similarity >= min_similarity:
                similar.append((past_hash, float(similarity)))
        
        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)
        
        return similar[:10]  # Top 10 most similar
    
    def _update_clusters(self, function: str):
        """
        Update semantic clusters using DBSCAN
        
        Groups queries into semantic clusters for better prediction
        """
        # Get all embeddings for this function
        embeddings = []
        hashes = []
        
        for (func, hash_val), emb in self.query_embeddings.items():
            if func == function:
                embeddings.append(emb)
                hashes.append(hash_val)
        
        if len(embeddings) < 10:
            return  # Need at least 10 queries
        
        # Cluster using DBSCAN
        embeddings_array = np.array(embeddings)
        
        clustering = DBSCAN(
            eps=0.3,  # Distance threshold
            min_samples=2,
            metric='cosine'
        ).fit(embeddings_array)
        
        # Organize into clusters
        clusters = defaultdict(list)
        for hash_val, label in zip(hashes, clustering.labels_):
            if label != -1:  # -1 is noise
                clusters[label].append(hash_val)
        
        self.query_clusters[function] = list(clusters.values())
    
    def _get_heuristic_predictions(self, function: str) -> Dict[str, float]:
        """Original heuristic prediction (frequency-based)"""
        return dict(self.frequency.get(function, {}))
    
    def _get_semantic_predictions(
        self,
        function: str,
        current_input: any
    ) -> Dict[str, float]:
        """
        Semantic predictions based on similarity
        
        "What queries are semantically similar to current input?"
        """
        try:
            # Get embedding for current input
            temp_hash = hashlib.sha256(str(current_input).encode()).hexdigest()
            embedding = self._get_embedding(function, current_input, temp_hash)
            
            # Find similar queries
            similar = self._find_similar_queries(
                function,
                temp_hash,
                embedding,
                min_similarity=0.70  # Lower threshold for predictions
            )
            
            # Convert to scores
            scores = {}
            for query_hash, similarity in similar:
                scores[query_hash] = similarity
            
            return scores
        
        except Exception as e:
            print(f"⚠️  Semantic predictions failed: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """Get prediction engine statistics"""
        total_predictions = (
            self.stats['semantic_predictions'] +
            self.stats['heuristic_predictions']
        )
        
        if total_predictions > 0:
            semantic_pct = (self.stats['semantic_predictions'] / total_predictions) * 100
        else:
            semantic_pct = 0
        
        return {
            'total_queries': self.stats['total_queries'],
            'semantic_predictions': self.stats['semantic_predictions'],
            'heuristic_predictions': self.stats['heuristic_predictions'],
            'semantic_percentage': semantic_pct,
            'interpolations': self.stats['interpolations'],
            'embeddings_enabled': self.use_embeddings,
            'total_embeddings': len(self.query_embeddings),
            'total_clusters': sum(len(c) for c in self.query_clusters.values())
        }


# Example usage
if __name__ == "__main__":
    engine = AdvancedPredictionEngine()
    
    # Simulate queries
    queries = [
        ("What is Python?", "hash1"),
        ("Explain Python programming", "hash2"),
        ("What is JavaScript?", "hash3"),
        ("Tell me about Python", "hash4"),
    ]
    
    for query, hash_val in queries:
        engine.record_query("ask_question", query, hash_val)
    
    # Predict next queries
    predictions = engine.predict_next("ask_question", "Python basics")
    
    print("\nPredictions for 'Python basics':")
    for pred in predictions:
        print(f"  {pred['hash'][:8]}: {pred['score']:.3f} ({pred['method']})")
    
    # Check interpolation
    similar = engine.can_interpolate("ask_question", "Python tutorial", "hash_new")
    if similar:
        print(f"\n✅ Can interpolate from {len(similar)} similar queries")