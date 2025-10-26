"""
Query caching for LLM responses
"""

import hashlib
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass

logger = structlog.get_logger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached response"""
    response: str
    metadata: Dict[str, Any]
    timestamp: datetime
    access_count: int = 1
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp

class QueryCache:
    """Intelligent caching system for LLM queries"""
    
    def __init__(self, max_size: int = 1000, default_ttl_hours: int = 24):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    def _generate_cache_key(self, prompt: str, provider: str, model: str, **kwargs) -> str:
        """Generate a cache key from query parameters"""
        # Create a dictionary of all relevant parameters
        cache_data = {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        # Create deterministic JSON representation
        cache_json = json.dumps(cache_data, sort_keys=True)
        
        # Generate hash
        return hashlib.sha256(cache_json.encode()).hexdigest()
    
    def get(self, prompt: str, provider: str, model: str, **kwargs) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get cached response if available"""
        self.stats["total_requests"] += 1
        
        cache_key = self._generate_cache_key(prompt, provider, model, **kwargs)
        
        if cache_key not in self.cache:
            self.stats["misses"] += 1
            logger.debug("Cache miss", key=cache_key[:8])
            return None
        
        entry = self.cache[cache_key]
        
        # Check if entry is expired
        if datetime.utcnow() - entry.timestamp > self.default_ttl:
            del self.cache[cache_key]
            self.stats["misses"] += 1
            logger.debug("Cache expired", key=cache_key[:8])
            return None
        
        # Update access metadata
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        
        self.stats["hits"] += 1
        logger.debug("Cache hit", key=cache_key[:8], access_count=entry.access_count)
        
        return entry.response, entry.metadata
    
    def set(self, prompt: str, provider: str, model: str, response: str, metadata: Dict[str, Any] = None, **kwargs) -> str:
        """Cache a response"""
        cache_key = self._generate_cache_key(prompt, provider, model, **kwargs)
        
        # Check if we need to evict entries
        if len(self.cache) >= self.max_size:
            self._evict_least_recently_used()
        
        # Create cache entry
        entry = CacheEntry(
            response=response,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )
        
        self.cache[cache_key] = entry
        logger.debug("Cached response", key=cache_key[:8], size=len(response))
        
        return cache_key
    
    def _evict_least_recently_used(self):
        """Evict the least recently used entry"""
        if not self.cache:
            return
        
        # Find entry with oldest last_accessed time
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]
        self.stats["evictions"] += 1
        logger.debug("Evicted LRU entry", key=lru_key[:8])
    
    def clear(self):
        """Clear all cached entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info("Cache cleared", entries_removed=count)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.stats["hits"] / max(self.stats["total_requests"], 1)
        
        return {
            "hit_rate": hit_rate,
            "total_entries": len(self.cache),
            "max_size": self.max_size,
            **self.stats
        }
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if now - entry.timestamp > self.default_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info("Cleaned up expired entries", count=len(expired_keys))

class SmartQueryCache(QueryCache):
    """Enhanced cache with similarity matching and content-aware caching"""
    
    def __init__(self, max_size: int = 1000, default_ttl_hours: int = 24, similarity_threshold: float = 0.8):
        super().__init__(max_size, default_ttl_hours)
        self.similarity_threshold = similarity_threshold
    
    def _normalize_prompt(self, prompt: str) -> str:
        """Normalize prompt for better matching"""
        # Remove extra whitespace
        normalized = " ".join(prompt.split())
        
        # Convert to lowercase for case-insensitive matching
        normalized = normalized.lower()
        
        # Remove common stop words that don't affect medical meaning
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"
        }
        
        words = normalized.split()
        filtered_words = [word for word in words if word not in stop_words]
        
        return " ".join(filtered_words)
    
    def _calculate_similarity(self, prompt1: str, prompt2: str) -> float:
        """Calculate similarity between two prompts"""
        norm1 = self._normalize_prompt(prompt1)
        norm2 = self._normalize_prompt(prompt2)
        
        # Simple Jaccard similarity
        set1 = set(norm1.split())
        set2 = set(norm2.split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_similar(
        self, 
        prompt: str, 
        provider: str, 
        model: str, 
        similarity_threshold: Optional[float] = None,
        **kwargs
    ) -> Optional[Tuple[str, Dict[str, Any], float]]:
        """Get similar cached response based on content similarity"""
        similarity_threshold = similarity_threshold or self.similarity_threshold
        
        best_match = None
        best_similarity = 0.0
        
        for cache_key, entry in self.cache.items():
            # Parse the cache key to extract original prompt
            try:
                # This is a simplified approach - in practice, you might want to store
                # the original prompt separately
                cache_metadata = json.loads(hashlib.sha256(cache_key.encode()).hexdigest()[:16])
                cached_prompt = entry.metadata.get("original_prompt", "")
                
                similarity = self._calculate_similarity(prompt, cached_prompt)
                
                if similarity >= similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = (entry.response, entry.metadata, similarity)
                    
            except Exception:
                continue
        
        if best_match:
            self.stats["hits"] += 1
            logger.debug("Similar cache hit", similarity=best_similarity)
        else:
            self.stats["misses"] += 1
        
        return best_match

# Global cache instance
_global_cache: Optional[QueryCache] = None

def get_query_cache() -> QueryCache:
    """Get or create the global query cache"""
    global _global_cache
    
    if _global_cache is None:
        _global_cache = SmartQueryCache()
    
    return _global_cache

def cache_query_response(
    prompt: str, 
    provider: str, 
    model: str, 
    response: str, 
    metadata: Dict[str, Any] = None,
    **kwargs
) -> str:
    """Cache a query response"""
    cache = get_query_cache()
    return cache.set(prompt, provider, model, response, metadata, **kwargs)

def get_cached_response(
    prompt: str, 
    provider: str, 
    model: str, 
    **kwargs
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Get cached response if available"""
    cache = get_query_cache()
    return cache.get(prompt, provider, model, **kwargs)

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    cache = get_query_cache()
    return cache.get_stats()

def clear_cache():
    """Clear all cached responses"""
    cache = get_query_cache()
    cache.clear()