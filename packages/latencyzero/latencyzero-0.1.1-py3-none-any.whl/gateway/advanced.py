from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Any
import time
from sklearn.neighbors import NearestNeighbors
import json

# Advanced Prediction Engine for Semantic Matching
class AdvancedPredictionEngine:
    def __init__(self, use_embeddings: bool = True, similarity_threshold: float = 0.85, numeric_dist_threshold: float = 0.05):
        self.use_embeddings = use_embeddings
        self.similarity_threshold = similarity_threshold
        self.numeric_dist_threshold = numeric_dist_threshold
        self.model = None
        self.query_store: Dict[str, List[Tuple[str, str, np.ndarray]]] = {}  # function: list of (query_input, hash, embedding)
        self.numeric_store: Dict[str, List[Tuple[np.ndarray, str]]] = {}  # function: list of (vector, hash)
        self.stats = {
            'total_queries': 0,
            'semantic_matches': 0,
            'numeric_matches': 0,
            'average_similarity': 0.0
        }
        if use_embeddings:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Loaded embedding model for semantic prediction")

    def record_query(self, function: str, query_input: str, hash: str):
        if not self.use_embeddings or not query_input:
            return
        embedding = self.model.encode(query_input)
        if function not in self.query_store:
            self.query_store[function] = []
        self.query_store[function].append((query_input, hash, embedding))
        self.stats['total_queries'] += 1

    def record_numeric(self, function: str, vector: np.ndarray, hash: str):
        if function not in self.numeric_store:
            self.numeric_store[function] = []
        self.numeric_store[function].append((vector, hash))
        self.stats['total_queries'] += 1

    def can_interpolate(self, function: str, query_input: str, hash: str, input_data: str = None) -> List[Tuple[str, float]]:
        if query_input:
            if not self.use_embeddings or function not in self.query_store:
                return []
            embedding = self.model.encode(query_input)
            similars = []
            for _, stored_hash, stored_emb in self.query_store[function]:
                if stored_hash == hash:
                    continue
                sim = cosine_similarity([embedding], [stored_emb])[0][0]
                if sim >= self.similarity_threshold:
                    similars.append((stored_hash, sim))
            similars.sort(key=lambda x: x[1], reverse=True)
            if similars:
                self.stats['semantic_matches'] += 1
                self.stats['average_similarity'] = (self.stats['average_similarity'] * (self.stats['semantic_matches'] - 1) + similars[0][1]) / self.stats['semantic_matches']
            return similars
        else:
            vector = self._extract_vector(input_data)
            if vector is None or function not in self.numeric_store or len(self.numeric_store[function]) == 0:
                return []
            points = np.array([v for v, h in self.numeric_store[function]])
            nn = NearestNeighbors(n_neighbors=1)
            nn.fit(points)
            dists, indices = nn.kneighbors([vector])
            dist = dists[0][0]
            norm_dist = dist / np.linalg.norm(vector) if np.linalg.norm(vector) > 0 else dist
            if norm_dist < self.numeric_dist_threshold:
                similar_hash = self.numeric_store[function][indices[0][0]][1]
                sim = 1 - norm_dist / self.numeric_dist_threshold
                self.stats['numeric_matches'] += 1
                return [(similar_hash, sim)]
            return []

    def _extract_vector(self, input_data: str) -> Optional[np.ndarray]:
        if not input_data:
            return None
        try:
            data = json.loads(input_data)
            vec = []
            for a in data.get('args', []):
                if isinstance(a, (int, float)):
                    vec.append(float(a))
            for v in data.get('kwargs', {}).values():
                if isinstance(v, (int, float)):
                    vec.append(float(v))
            if vec:
                return np.array(vec)
            return None
        except:
            return None

    def get_stats(self) -> Dict[str, Any]:
        return self.stats

# Use the enhanced FormalErrorBounds from the provided code
# (Paste the entire FormalErrorBounds class here as provided in the query)

# Resilience Layer (Stale-on-Error)
class ResilienceConfig:
    def __init__(self, max_stale_age: int = 3600, min_confidence_for_stale: float = 0.80, circuit_breaker_threshold: int = 5):
        self.max_stale_age = max_stale_age
        self.min_confidence_for_stale = min_confidence_for_stale
        self.circuit_breaker_threshold = circuit_breaker_threshold

class StaleOnErrorLayer:
    def __init__(self, config: ResilienceConfig):
        self.config = config
        self.failures: Dict[str, int] = {}  # function: consecutive failures
        self.circuit_open: Dict[str, float] = {}  # function: time when opened

    def get_resilience_metrics(self) -> Dict[str, Any]:
        return {
            'failures': self.failures,
            'open_circuits': {k: time.time() - v for k, v in self.circuit_open.items()}
        }