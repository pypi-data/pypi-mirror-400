"""
Tests for the Response Cache module.
"""

import pytest
import time
from apiarm.core.cache import ResponseCache, CacheEntry
from apiarm.models.response import APIResponse


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""
    
    def test_create_entry(self):
        response = APIResponse(success=True, status_code=200)
        entry = CacheEntry(
            response=response,
            created_at=time.time(),
            ttl=300.0,
        )
        assert entry.hits == 0
        assert not entry.is_expired
        
    def test_expired_entry(self):
        response = APIResponse(success=True, status_code=200)
        entry = CacheEntry(
            response=response,
            created_at=time.time() - 400,  # Created 400 seconds ago
            ttl=300.0,  # TTL is 300 seconds
        )
        assert entry.is_expired


class TestResponseCache:
    """Tests for ResponseCache class."""
    
    def test_init(self):
        cache = ResponseCache()
        assert cache.max_size == 100
        assert cache.default_ttl == 300.0
        assert cache.enabled is True
        
    def test_disabled_cache(self):
        cache = ResponseCache(enabled=False)
        response = APIResponse(success=True, status_code=200, data={"test": 1})
        cache.set("key", response)
        assert cache.get("key") is None
        
    def test_set_and_get(self):
        cache = ResponseCache()
        response = APIResponse(success=True, status_code=200, data={"test": 1})
        
        cache.set("test_key", response)
        cached = cache.get("test_key")
        
        assert cached is not None
        assert cached.data == {"test": 1}
        
    def test_cache_miss(self):
        cache = ResponseCache()
        assert cache.get("nonexistent") is None
        
    def test_only_caches_successful(self):
        cache = ResponseCache()
        response = APIResponse(success=False, status_code=500)
        
        cache.set("error_key", response)
        assert cache.get("error_key") is None
        
    def test_lru_eviction(self):
        cache = ResponseCache(max_size=2)
        
        cache.set("key1", APIResponse(success=True, status_code=200))
        cache.set("key2", APIResponse(success=True, status_code=200))
        cache.set("key3", APIResponse(success=True, status_code=200))
        
        # key1 should have been evicted
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
        
    def test_generate_key(self):
        key1 = ResponseCache.generate_key("GET", "/users")
        key2 = ResponseCache.generate_key("GET", "/users")
        key3 = ResponseCache.generate_key("POST", "/users")
        
        assert key1 == key2
        assert key1 != key3
        
    def test_generate_key_with_params(self):
        key1 = ResponseCache.generate_key("GET", "/users", {"page": 1})
        key2 = ResponseCache.generate_key("GET", "/users", {"page": 2})
        
        assert key1 != key2
        
    def test_delete(self):
        cache = ResponseCache()
        response = APIResponse(success=True, status_code=200)
        
        cache.set("key", response)
        assert cache.get("key") is not None
        
        result = cache.delete("key")
        assert result is True
        assert cache.get("key") is None
        
    def test_clear(self):
        cache = ResponseCache()
        cache.set("key1", APIResponse(success=True, status_code=200))
        cache.set("key2", APIResponse(success=True, status_code=200))
        
        count = cache.clear()
        assert count == 2
        assert cache.size == 0
        
    def test_stats(self):
        cache = ResponseCache()
        response = APIResponse(success=True, status_code=200)
        
        cache.set("key", response)
        cache.get("key")  # Hit
        cache.get("key")  # Hit
        cache.get("missing")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 66.7
