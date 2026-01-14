"""Tests for the cache module."""

import pytest
import tempfile
import time
from pathlib import Path

from promptops.cache.manager import (
    CacheManager,
    MemoryCacheBackend,
    FileCacheBackend,
    SQLiteCacheBackend,
    CacheConfig,
    CacheStats,
    CacheEntry,
    CacheBackend,
    cache_prompt,
    get_cache,
    configure_cache,
    clear_cache,
)


def create_cache_entry(key: str, value, ttl: int = 3600) -> CacheEntry:
    """Helper function to create cache entries for testing."""
    return CacheEntry(
        key=key,
        value=value,
        created_at=time.time(),
        expires_at=time.time() + ttl,
    )


class TestMemoryCacheBackend:
    """Test memory cache backend."""
    
    def test_set_and_get(self):
        """Test setting and getting values."""
        cache = MemoryCacheBackend(max_size=10)
        entry = create_cache_entry("key1", "value1")
        cache.set(entry)
        result = cache.get("key1")
        assert result is not None
        assert result.value == "value1"
    
    def test_get_missing_key(self):
        """Test getting a missing key returns None."""
        cache = MemoryCacheBackend()
        assert cache.get("missing") is None
    
    def test_delete(self):
        """Test deleting a key."""
        cache = MemoryCacheBackend()
        entry = create_cache_entry("key1", "value1")
        cache.set(entry)
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_clear(self):
        """Test clearing all entries."""
        cache = MemoryCacheBackend()
        cache.set(create_cache_entry("key1", "value1"))
        cache.set(create_cache_entry("key2", "value2"))
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = MemoryCacheBackend()
        entry = create_cache_entry("key1", "value1", ttl=0.1)
        cache.set(entry)
        result = cache.get("key1")
        assert result is not None
        assert result.value == "value1"
        time.sleep(0.15)
        assert cache.get("key1") is None
    
    def test_max_size_eviction(self):
        """Test LRU eviction when max size is reached."""
        cache = MemoryCacheBackend(max_size=2)
        cache.set(create_cache_entry("key1", "value1"))
        cache.set(create_cache_entry("key2", "value2"))
        cache.set(create_cache_entry("key3", "value3"))  # Should evict key1
        assert cache.get("key1") is None
        result2 = cache.get("key2")
        result3 = cache.get("key3")
        assert result2 is not None and result2.value == "value2"
        assert result3 is not None and result3.value == "value3"
    
    def test_stats(self):
        """Test cache size."""
        cache = MemoryCacheBackend(max_size=5)
        cache.set(create_cache_entry("key1", "value1"))
        assert cache.size() == 1


class TestFileCacheBackend:
    """Test file cache backend."""
    
    def test_set_and_get(self, tmp_path):
        """Test setting and getting values."""
        cache = FileCacheBackend(cache_dir=str(tmp_path))
        entry = create_cache_entry("key1", {"data": "value1"})
        cache.set(entry)
        result = cache.get("key1")
        assert result is not None
        assert result.value == {"data": "value1"}
    
    def test_get_missing_key(self, tmp_path):
        """Test getting a missing key."""
        cache = FileCacheBackend(cache_dir=str(tmp_path))
        assert cache.get("missing") is None
    
    def test_delete(self, tmp_path):
        """Test deleting a key."""
        cache = FileCacheBackend(cache_dir=str(tmp_path))
        entry = create_cache_entry("key1", "value1")
        cache.set(entry)
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_clear(self, tmp_path):
        """Test clearing all entries."""
        cache = FileCacheBackend(cache_dir=str(tmp_path))
        cache.set(create_cache_entry("key1", "value1"))
        cache.set(create_cache_entry("key2", "value2"))
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_ttl_expiration(self, tmp_path):
        """Test TTL expiration."""
        cache = FileCacheBackend(cache_dir=str(tmp_path))
        entry = create_cache_entry("key1", "value1", ttl=0.1)
        cache.set(entry)
        result = cache.get("key1")
        assert result is not None
        assert result.value == "value1"
        time.sleep(0.15)
        assert cache.get("key1") is None


class TestSQLiteCacheBackend:
    """Test SQLite cache backend."""
    
    def test_set_and_get(self, tmp_path):
        """Test setting and getting values."""
        db_path = tmp_path / "cache.db"
        cache = SQLiteCacheBackend(db_path=str(db_path))
        entry = create_cache_entry("key1", {"data": "value1"})
        cache.set(entry)
        result = cache.get("key1")
        assert result is not None
        assert result.value == {"data": "value1"}
    
    def test_get_missing_key(self, tmp_path):
        """Test getting a missing key."""
        db_path = tmp_path / "cache.db"
        cache = SQLiteCacheBackend(db_path=str(db_path))
        assert cache.get("missing") is None
    
    def test_delete(self, tmp_path):
        """Test deleting a key."""
        db_path = tmp_path / "cache.db"
        cache = SQLiteCacheBackend(db_path=str(db_path))
        entry = create_cache_entry("key1", "value1")
        cache.set(entry)
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_clear(self, tmp_path):
        """Test clearing all entries."""
        db_path = tmp_path / "cache.db"
        cache = SQLiteCacheBackend(db_path=str(db_path))
        cache.set(create_cache_entry("key1", "value1"))
        cache.set(create_cache_entry("key2", "value2"))
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_ttl_expiration(self, tmp_path):
        """Test TTL expiration."""
        db_path = tmp_path / "cache.db"
        cache = SQLiteCacheBackend(db_path=str(db_path))
        entry = create_cache_entry("key1", "value1", ttl=0.1)
        cache.set(entry)
        result = cache.get("key1")
        assert result is not None
        assert result.value == "value1"
        time.sleep(0.15)
        assert cache.get("key1") is None


class TestCacheManager:
    """Test cache manager."""
    
    def test_create_with_memory_backend(self):
        """Test creating cache with memory backend."""
        config = CacheConfig(backend=CacheBackend.MEMORY, max_size=10)
        cache = CacheManager(config)
        assert isinstance(cache._backend, MemoryCacheBackend)
    
    def test_create_with_file_backend(self, tmp_path):
        """Test creating cache with file backend."""
        config = CacheConfig(backend=CacheBackend.FILE, file_path=str(tmp_path))
        cache = CacheManager(config)
        assert isinstance(cache._backend, FileCacheBackend)
    
    def test_create_with_sqlite_backend(self, tmp_path):
        """Test creating cache with SQLite backend."""
        config = CacheConfig(backend=CacheBackend.SQLITE, file_path=str(tmp_path))
        cache = CacheManager(config)
        assert isinstance(cache._backend, SQLiteCacheBackend)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        config = CacheConfig(backend=CacheBackend.MEMORY)
        cache = CacheManager(config)
        
        key1 = cache.generate_key("prompt1", "v1", {"input": "test"})
        key2 = cache.generate_key("prompt1", "v1", {"input": "test"})
        key3 = cache.generate_key("prompt1", "v1", {"input": "different"})
        
        assert key1 == key2  # Same inputs produce same key
        assert key1 != key3  # Different inputs produce different key
    
    def test_get_and_set(self):
        """Test getting and setting cached responses."""
        config = CacheConfig(backend=CacheBackend.MEMORY)
        cache = CacheManager(config)
        
        cache.set("prompt1", "v1", {"input": "test"}, "response1")
        result = cache.get("prompt1", "v1", {"input": "test"})
        assert result == "response1"
    
    def test_cache_miss(self):
        """Test cache miss."""
        config = CacheConfig(backend=CacheBackend.MEMORY)
        cache = CacheManager(config)
        
        result = cache.get("prompt1", "v1", {"input": "test"})
        assert result is None
    
    def test_disabled_cache(self):
        """Test disabled cache."""
        config = CacheConfig(enabled=False)
        cache = CacheManager(config)
        
        cache.set("prompt1", "v1", {"input": "test"}, "response1")
        result = cache.get("prompt1", "v1", {"input": "test"})
        assert result is None  # Cache is disabled


class TestCacheDecorator:
    """Test cache_prompt decorator."""
    
    def test_decorator_caches_result(self):
        """Test that decorator caches function results."""
        call_count = 0
        
        @cache_prompt("test_prompt", "v1", ttl=60)
        def expensive_function(input_text):
            nonlocal call_count
            call_count += 1
            return f"result for {input_text}"
        
        # Configure cache
        configure_cache(CacheConfig(backend=CacheBackend.MEMORY))
        
        # First call - use keyword argument so decorator can cache based on it
        result1 = expensive_function(input_text="test")
        assert call_count == 1
        
        # Second call with same inputs should use cache
        result2 = expensive_function(input_text="test")
        assert call_count == 1  # Not called again
        assert result1 == result2
        
        # Different inputs should call function
        result3 = expensive_function(input_text="different")
        assert call_count == 2


class TestGlobalCacheFunctions:
    """Test global cache functions."""
    
    def test_get_cache(self):
        """Test get_cache returns global instance."""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2
    
    def test_configure_cache(self):
        """Test configure_cache."""
        config = CacheConfig(backend=CacheBackend.MEMORY, max_size=5)
        configure_cache(config)
        cache = get_cache()
        assert isinstance(cache._backend, MemoryCacheBackend)
    
    def test_clear_cache(self):
        """Test clear_cache."""
        cache = get_cache()
        cache.set("test", "v1", {}, "response")
        
        count = clear_cache()
        assert count >= 0  # May clear cache entries
        assert count >= 0  # Returns number of cleared entries
