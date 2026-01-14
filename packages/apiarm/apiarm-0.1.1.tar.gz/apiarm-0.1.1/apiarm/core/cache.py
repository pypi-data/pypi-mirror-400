"""
Response Cache - Caches API responses to reduce redundant requests.

Features:
- In-memory caching with TTL
- Cache key generation from request parameters
- Cache statistics
- Manual cache invalidation
"""

import hashlib
import json
import time
from typing import Any, Optional
from dataclasses import dataclass
from collections import OrderedDict

from ..models.response import APIResponse


@dataclass
class CacheEntry:
    """A cached response with metadata."""
    response: APIResponse
    created_at: float
    ttl: float
    hits: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return time.time() > self.created_at + self.ttl
    
    @property
    def age_seconds(self) -> float:
        """Get the age of this cache entry in seconds."""
        return time.time() - self.created_at


class ResponseCache:
    """
    In-memory cache for API responses.
    
    Uses an LRU eviction policy when max size is reached.
    Supports TTL-based expiration.
    """
    
    def __init__(
        self,
        max_size: int = 100,
        default_ttl: float = 300.0,  # 5 minutes
        enabled: bool = True,
    ):
        """
        Initialize the response cache.
        
        Args:
            max_size: Maximum number of entries to cache
            default_ttl: Default time-to-live in seconds
            enabled: Whether caching is enabled
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enabled = enabled
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[APIResponse]:
        """
        Get a cached response.
        
        Args:
            key: Cache key
            
        Returns:
            Cached response or None if not found/expired
        """
        if not self.enabled:
            return None
            
        entry = self._cache.get(key)
        
        if entry is None:
            self._misses += 1
            return None
            
        if entry.is_expired:
            del self._cache[key]
            self._misses += 1
            return None
            
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        entry.hits += 1
        self._hits += 1
        
        return entry.response
    
    def set(
        self,
        key: str,
        response: APIResponse,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Cache a response.
        
        Args:
            key: Cache key
            response: Response to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        if not self.enabled:
            return
            
        # Only cache successful responses
        if not response.success:
            return
            
        # Evict if at max size
        while len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
            
        self._cache[key] = CacheEntry(
            response=response,
            created_at=time.time(),
            ttl=ttl or self.default_ttl,
        )
        
    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count
    
    def clear_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    @staticmethod
    def generate_key(
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        body: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Generate a cache key from request parameters.
        
        Args:
            method: HTTP method
            path: Request path
            params: Query parameters
            body: Request body
            
        Returns:
            Cache key string
        """
        key_parts = [method.upper(), path]
        
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        if body:
            key_parts.append(json.dumps(body, sort_keys=True))
            
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate (0-1)."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate * 100, 1),
            "enabled": self.enabled,
        }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (simple substring match)
            
        Returns:
            Number of entries invalidated
        """
        keys_to_delete = [
            key for key in self._cache.keys()
            if pattern in key
        ]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)
