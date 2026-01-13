"""
LLM Response Caching for Scalability.

Caches identical queries to avoid redundant API calls.
Especially useful for:
- Repeated sub-queries during recursion
- Common document patterns
- Retry scenarios
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional, Callable
from functools import wraps
from threading import Lock


@dataclass
class CacheEntry:
    """Single cache entry."""
    response: str
    created_at: float
    hits: int = 0
    tokens_saved: int = 0


class LLMCache:
    """
    Thread-safe LRU cache for LLM responses.
    
    Features:
    - Content-based hashing (same query = same cache key)
    - TTL expiration
    - LRU eviction
    - Hit rate tracking
    
    Usage:
        cache = LLMCache(max_size=1000, ttl_seconds=3600)
        
        # Check cache
        cached = cache.get(messages)
        if cached:
            return cached
        
        # Call LLM
        response = llm.chat_completion(messages)
        
        # Store in cache
        cache.set(messages, response.content)
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: float = 3600,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, CacheEntry] = {}
        self._access_order: list[str] = []
        self._lock = Lock()
        
        # Stats
        self._hits = 0
        self._misses = 0
    
    def _hash_key(self, messages: list[dict]) -> str:
        """Create deterministic hash from messages."""
        content = json.dumps(messages, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get(self, messages: list[dict]) -> Optional[str]:
        """Get cached response if exists and not expired."""
        key = self._hash_key(messages)
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check TTL
            if time.time() - entry.created_at > self.ttl_seconds:
                del self._cache[key]
                self._access_order.remove(key)
                self._misses += 1
                return None
            
            # Update access order (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            
            entry.hits += 1
            self._hits += 1
            
            return entry.response
    
    def set(
        self,
        messages: list[dict],
        response: str,
        tokens_used: int = 0,
    ):
        """Cache a response."""
        key = self._hash_key(messages)
        
        with self._lock:
            # Evict if at capacity
            while len(self._cache) >= self.max_size:
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]
            
            self._cache[key] = CacheEntry(
                response=response,
                created_at=time.time(),
                tokens_saved=tokens_used,
            )
            self._access_order.append(key)
    
    def clear(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0
    
    @property
    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.1%}",
            "tokens_saved": sum(e.tokens_saved * e.hits for e in self._cache.values()),
        }


def cached_completion(cache: LLMCache):
    """
    Decorator to add caching to completion function.
    
    Usage:
        cache = LLMCache()
        
        @cached_completion(cache)
        def call_llm(messages):
            return client.chat_completion(messages)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(messages: list[dict], *args, **kwargs):
            # Check cache
            cached = cache.get(messages)
            if cached is not None:
                return cached
            
            # Call function
            result = func(messages, *args, **kwargs)
            
            # Cache result
            response = result.content if hasattr(result, 'content') else str(result)
            tokens = result.usage.get('total_tokens', 0) if hasattr(result, 'usage') else 0
            cache.set(messages, response, tokens)
            
            return result
        
        return wrapper
    return decorator
