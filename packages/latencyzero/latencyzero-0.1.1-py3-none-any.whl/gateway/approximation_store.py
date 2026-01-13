"""
Approximation Store - Fast storage for cached results
Uses Redis for production, in-memory dict for development
FIXED VERSION with better error handling
"""

import redis
import json
import time
from typing import Optional, Dict, Any
import os


class ApproximationStore:
    """
    Stores computed results for fast approximation
    
    In production: Uses Redis
    In development: Uses in-memory dict
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        ttl_seconds: int = 3600,  # 1 hour default TTL
        use_redis: bool = False  # Default to memory for easier setup
    ):
        self.ttl_seconds = ttl_seconds
        self.use_redis = use_redis and redis_url is not None
        
        if self.use_redis:
            try:
                redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
                self.redis = redis.from_url(redis_url, decode_responses=False)
                self.redis.ping()  # Test connection
                print(f"✅ Connected to Redis: {redis_url}")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}, using in-memory store")
                self.use_redis = False
                self.memory_store: Dict[str, Dict] = {}
        else:
            print("📦 Using in-memory approximation store")
            self.memory_store: Dict[str, Dict] = {}
        
        # Statistics
        self.stats = {
            'total_stored': 0,
            'total_retrieved': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _make_key(self, function: str, query_hash: str) -> str:
        """Generate Redis/dict key"""
        return f"lz:approx:{function}:{query_hash}"
    
    def get(self, function: str, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve approximation from store"""
        key = self._make_key(function, query_hash)
        
        try:
            if self.use_redis:
                data = self.redis.get(key)
                if data:
                    self.stats['cache_hits'] += 1
                    self.stats['total_retrieved'] += 1
                    
                    # Increment hit count
                    self.redis.hincrby(f"{key}:meta", "hit_count", 1)
                    
                    result = json.loads(data)
                    
                    # Get metadata
                    meta = self.redis.hgetall(f"{key}:meta")
                    if meta:
                        result['hit_count'] = int(meta.get(b'hit_count', 1))
                    
                    return result
                else:
                    self.stats['cache_misses'] += 1
                    return None
            else:
                # In-memory store
                if key in self.memory_store:
                    self.stats['cache_hits'] += 1
                    self.stats['total_retrieved'] += 1
                    
                    data = self.memory_store[key]
                    data['hit_count'] = data.get('hit_count', 0) + 1
                    return data
                else:
                    self.stats['cache_misses'] += 1
                    return None
        
        except Exception as e:
            print(f"❌ Error retrieving from store: {e}")
            self.stats['cache_misses'] += 1
            return None
    
    def put(
        self,
        function: str,
        query_hash: str,
        result: str,
        execution_time: float,
        timestamp: float
    ):
        """Store approximation result"""
        key = self._make_key(function, query_hash)
        
        data = {
            'result': result,
            'execution_time': execution_time,
            'timestamp': timestamp,
            'hit_count': 0
        }
        
        try:
            if self.use_redis:
                # Store main data with TTL
                self.redis.setex(
                    key,
                    self.ttl_seconds,
                    json.dumps(data)
                )
                
                # Store metadata
                self.redis.hset(f"{key}:meta", mapping={
                    'created': timestamp,
                    'hit_count': 0
                })
                self.redis.expire(f"{key}:meta", self.ttl_seconds)
            else:
                # In-memory store - FIXED: just store directly
                self.memory_store[key] = data
            
            self.stats['total_stored'] += 1
            print(f"✅ Stored result for {function[:30]}... (hash: {query_hash[:8]}...)")
        
        except Exception as e:
            print(f"❌ Error storing approximation: {e}")
            import traceback
            traceback.print_exc()
    
    def delete(self, function: str, query_hash: str):
        """Delete approximation from store"""
        key = self._make_key(function, query_hash)
        
        if self.use_redis:
            self.redis.delete(key, f"{key}:meta")
        else:
            self.memory_store.pop(key, None)
    
    def clear(self):
        """Clear all approximations"""
        if self.use_redis:
            # Delete all keys matching pattern
            for key in self.redis.scan_iter("lz:approx:*"):
                self.redis.delete(key)
        else:
            self.memory_store.clear()
        
        print("🗑️  Approximation store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        if self.use_redis:
            try:
                info = self.redis.info('memory')
                memory_used = info.get('used_memory_human', 'unknown')
                total_keys = self.redis.dbsize()
            except:
                memory_used = 'unknown'
                total_keys = 0
        else:
            memory_used = f"{len(self.memory_store)} items"
            total_keys = len(self.memory_store)
        
        hit_rate = 0
        if self.stats['total_retrieved'] > 0:
            hit_rate = self.stats['cache_hits'] / self.stats['total_retrieved']
        
        return {
            'backend': 'redis' if self.use_redis else 'memory',
            'total_stored': self.stats['total_stored'],
            'total_retrieved': self.stats['total_retrieved'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate': hit_rate,
            'total_keys': total_keys,
            'memory_used': memory_used
        }
    
    def close(self):
        """Close connections"""
        if self.use_redis:
            self.redis.close()