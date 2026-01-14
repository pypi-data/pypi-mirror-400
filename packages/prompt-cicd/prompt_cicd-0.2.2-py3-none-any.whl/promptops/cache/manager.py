"""
Prompt Caching Manager for PromptOps.

Provides intelligent caching of LLM responses with:
- Multiple backends (memory, file, Redis)
- TTL-based expiration
- Key generation from inputs
- Cache statistics
- Decorator support
"""

import functools
import hashlib
import json
import logging
import os
import pickle
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheBackend(Enum):
    """Available cache backends."""
    MEMORY = "memory"
    FILE = "file"
    SQLITE = "sqlite"


@dataclass
class CacheConfig:
    """Configuration for the cache manager."""
    enabled: bool = True
    backend: CacheBackend = CacheBackend.MEMORY
    ttl: int = 3600  # Default 1 hour
    max_size: int = 1000  # Maximum entries
    file_path: str = ".promptops_cache"
    key_fields: Optional[List[str]] = None  # Fields to use for cache key
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheConfig":
        """Create config from dictionary."""
        backend = data.get("backend", "memory")
        if isinstance(backend, str):
            backend = CacheBackend(backend)
        
        return cls(
            enabled=data.get("enabled", True),
            backend=backend,
            ttl=data.get("ttl", 3600),
            max_size=data.get("max_size", 1000),
            file_path=data.get("file_path", ".promptops_cache"),
            key_fields=data.get("key_fields"),
        )


@dataclass
class CacheEntry:
    """A single cache entry."""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    prompt_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    @property
    def ttl_remaining(self) -> float:
        return max(0, self.expires_at - time.time())


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size": self.size,
            "max_size": self.max_size,
            "hit_rate": f"{self.hit_rate:.2%}",
        }


class BaseCacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get an entry by key."""
        pass
    
    @abstractmethod
    def set(self, entry: CacheEntry) -> None:
        """Store an entry."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete an entry."""
        pass
    
    @abstractmethod
    def clear(self) -> int:
        """Clear all entries. Returns count deleted."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get current cache size."""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """Get all cache keys."""
        pass


class MemoryCacheBackend(BaseCacheBackend):
    """In-memory cache backend using a dictionary."""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
        self._access_order: List[str] = []  # For LRU eviction
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                entry.hits += 1
                # Update access order for LRU
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return entry
            elif entry:
                # Expired, remove it
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
            return None
    
    def set(self, entry: CacheEntry) -> None:
        with self._lock:
            # Evict if at max size
            while len(self._cache) >= self._max_size and self._access_order:
                oldest = self._access_order.pop(0)
                self._cache.pop(oldest, None)
            
            self._cache[entry.key] = entry
            if entry.key in self._access_order:
                self._access_order.remove(entry.key)
            self._access_order.append(entry.key)
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
    
    def clear(self) -> int:
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._access_order.clear()
            return count
    
    def size(self) -> int:
        return len(self._cache)
    
    def keys(self) -> List[str]:
        return list(self._cache.keys())


class FileCacheBackend(BaseCacheBackend):
    """File-based cache backend using pickle files."""
    
    def __init__(self, cache_dir: str = ".promptops_cache", max_size: int = 1000):
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_size = max_size
        self._lock = threading.RLock()
        self._index_file = self._cache_dir / "index.json"
        self._index: Dict[str, float] = {}  # key -> expires_at
        self._load_index()
    
    def _load_index(self) -> None:
        """Load the cache index from disk."""
        if self._index_file.exists():
            try:
                with open(self._index_file, "r") as f:
                    self._index = json.load(f)
            except Exception:
                self._index = {}
    
    def _save_index(self) -> None:
        """Save the cache index to disk."""
        with open(self._index_file, "w") as f:
            json.dump(self._index, f)
    
    def _key_to_path(self, key: str) -> Path:
        """Convert a cache key to a file path."""
        # Use hash to create a safe filename
        safe_name = hashlib.md5(key.encode()).hexdigest()
        return self._cache_dir / f"{safe_name}.cache"
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            if key not in self._index:
                return None
            
            # Check expiration
            if time.time() > self._index[key]:
                self.delete(key)
                return None
            
            cache_file = self._key_to_path(key)
            if not cache_file.exists():
                del self._index[key]
                self._save_index()
                return None
            
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)
                    entry.hits += 1
                    # Update hits count on disk
                    with open(cache_file, "wb") as f:
                        pickle.dump(entry, f)
                    return entry
            except Exception as e:
                logger.warning(f"Failed to load cache entry: {e}")
                return None
    
    def set(self, entry: CacheEntry) -> None:
        with self._lock:
            # Evict if at max size
            while len(self._index) >= self._max_size:
                # Remove oldest (first) entry
                if self._index:
                    oldest_key = next(iter(self._index))
                    self.delete(oldest_key)
            
            cache_file = self._key_to_path(entry.key)
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump(entry, f)
                self._index[entry.key] = entry.expires_at
                self._save_index()
            except Exception as e:
                logger.warning(f"Failed to save cache entry: {e}")
    
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._index:
                del self._index[key]
                self._save_index()
                cache_file = self._key_to_path(key)
                try:
                    cache_file.unlink(missing_ok=True)
                except Exception:
                    pass
                return True
            return False
    
    def clear(self) -> int:
        with self._lock:
            count = len(self._index)
            # Delete all cache files
            for key in list(self._index.keys()):
                cache_file = self._key_to_path(key)
                try:
                    cache_file.unlink(missing_ok=True)
                except Exception:
                    pass
            self._index.clear()
            self._save_index()
            return count
    
    def size(self) -> int:
        return len(self._index)
    
    def keys(self) -> List[str]:
        return list(self._index.keys())


class SQLiteCacheBackend(BaseCacheBackend):
    """SQLite-based cache backend for persistent, queryable cache."""
    
    def __init__(self, db_path: str = ".promptops_cache/cache.db", max_size: int = 1000):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._max_size = max_size
        self._lock = threading.RLock()
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the SQLite database."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    expires_at REAL,
                    hits INTEGER DEFAULT 0,
                    prompt_name TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)")
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(str(self._db_path), timeout=10.0)
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            with self._get_connection() as conn:
                # Clean expired entries first
                conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
                
                cursor = conn.execute(
                    "SELECT key, value, created_at, expires_at, hits, prompt_name, metadata FROM cache WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    # Update hits
                    conn.execute("UPDATE cache SET hits = hits + 1 WHERE key = ?", (key,))
                    conn.commit()
                    
                    return CacheEntry(
                        key=row[0],
                        value=pickle.loads(row[1]),
                        created_at=row[2],
                        expires_at=row[3],
                        hits=row[4] + 1,
                        prompt_name=row[5],
                        metadata=json.loads(row[6]) if row[6] else {},
                    )
                return None
    
    def set(self, entry: CacheEntry) -> None:
        with self._lock:
            with self._get_connection() as conn:
                # Evict if at max size
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                count = cursor.fetchone()[0]
                
                if count >= self._max_size:
                    # Delete oldest entries
                    to_delete = count - self._max_size + 1
                    conn.execute(
                        "DELETE FROM cache WHERE key IN (SELECT key FROM cache ORDER BY created_at LIMIT ?)",
                        (to_delete,)
                    )
                
                # Insert or replace
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, created_at, expires_at, hits, prompt_name, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.key,
                        pickle.dumps(entry.value),
                        entry.created_at,
                        entry.expires_at,
                        entry.hits,
                        entry.prompt_name,
                        json.dumps(entry.metadata),
                    )
                )
                conn.commit()
    
    def delete(self, key: str) -> bool:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0
    
    def clear(self) -> int:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM cache")
                conn.commit()
                return count
    
    def size(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            return cursor.fetchone()[0]
    
    def keys(self) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT key FROM cache")
            return [row[0] for row in cursor.fetchall()]


class CacheManager:
    """
    Main cache manager for PromptOps.
    
    Provides a unified interface for caching prompt responses with:
    - Configurable backends
    - TTL-based expiration
    - Statistics tracking
    - Key generation utilities
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.stats = CacheStats(max_size=self.config.max_size)
        self._backend = self._create_backend()
    
    def _create_backend(self) -> BaseCacheBackend:
        """Create the appropriate cache backend."""
        if self.config.backend == CacheBackend.MEMORY:
            return MemoryCacheBackend(max_size=self.config.max_size)
        elif self.config.backend == CacheBackend.FILE:
            return FileCacheBackend(
                cache_dir=self.config.file_path,
                max_size=self.config.max_size,
            )
        elif self.config.backend == CacheBackend.SQLITE:
            return SQLiteCacheBackend(
                db_path=f"{self.config.file_path}/cache.db",
                max_size=self.config.max_size,
            )
        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")
    
    def generate_key(
        self,
        prompt_name: str,
        version: str,
        inputs: Dict[str, Any],
        key_fields: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a cache key from prompt inputs.
        
        Args:
            prompt_name: Name of the prompt.
            version: Prompt version.
            inputs: Input values.
            key_fields: Specific fields to use for key (None = use all).
            
        Returns:
            A unique cache key string.
        """
        fields = key_fields or self.config.key_fields
        
        if fields:
            # Use only specified fields
            key_data = {k: inputs.get(k) for k in fields if k in inputs}
        else:
            # Use all inputs
            key_data = inputs
        
        key_obj = {
            "prompt": prompt_name,
            "version": version,
            "inputs": key_data,
        }
        
        key_str = json.dumps(key_obj, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]
    
    def get(
        self,
        prompt_name: str,
        version: str,
        inputs: Dict[str, Any],
        key_fields: Optional[List[str]] = None,
    ) -> Optional[Any]:
        """
        Get a cached response if available.
        
        Args:
            prompt_name: Name of the prompt.
            version: Prompt version.
            inputs: Input values used to generate the response.
            key_fields: Specific fields to use for key.
            
        Returns:
            Cached value or None if not found.
        """
        if not self.config.enabled:
            return None
        
        key = self.generate_key(prompt_name, version, inputs, key_fields)
        entry = self._backend.get(key)
        
        if entry:
            self.stats.hits += 1
            logger.debug(f"Cache hit for {prompt_name}:{version}")
            return entry.value
        else:
            self.stats.misses += 1
            logger.debug(f"Cache miss for {prompt_name}:{version}")
            return None
    
    def set(
        self,
        prompt_name: str,
        version: str,
        inputs: Dict[str, Any],
        value: Any,
        ttl: Optional[int] = None,
        key_fields: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Cache a response.
        
        Args:
            prompt_name: Name of the prompt.
            version: Prompt version.
            inputs: Input values.
            value: Response to cache.
            ttl: Time-to-live in seconds (None = use default).
            key_fields: Specific fields to use for key.
            metadata: Additional metadata to store.
            
        Returns:
            The cache key used.
        """
        if not self.config.enabled:
            return ""
        
        key = self.generate_key(prompt_name, version, inputs, key_fields)
        ttl = ttl or self.config.ttl
        now = time.time()
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl,
            prompt_name=prompt_name,
            metadata=metadata or {},
        )
        
        # Check if we need to evict
        if self._backend.size() >= self.config.max_size:
            self.stats.evictions += 1
        
        self._backend.set(entry)
        self.stats.size = self._backend.size()
        
        logger.debug(f"Cached response for {prompt_name}:{version} (TTL: {ttl}s)")
        return key
    
    def invalidate(
        self,
        prompt_name: str,
        version: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Invalidate cached entries.
        
        Args:
            prompt_name: Name of the prompt.
            version: Prompt version.
            inputs: Specific inputs to invalidate (None = invalidate all for prompt).
            
        Returns:
            True if any entries were invalidated.
        """
        if inputs:
            key = self.generate_key(prompt_name, version, inputs)
            return self._backend.delete(key)
        else:
            # Delete all entries for this prompt
            deleted = False
            for key in self._backend.keys():
                entry = self._backend.get(key)
                if entry and entry.prompt_name == prompt_name:
                    self._backend.delete(key)
                    deleted = True
            return deleted
    
    def clear(self) -> int:
        """Clear all cached entries."""
        count = self._backend.clear()
        self.stats = CacheStats(max_size=self.config.max_size)
        logger.info(f"Cleared {count} cache entries")
        return count
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        self.stats.size = self._backend.size()
        return self.stats


# =============================================================================
# Global Cache Instance
# =============================================================================

_global_cache: Optional[CacheManager] = None
_global_lock = threading.Lock()


def get_cache() -> CacheManager:
    """Get the global cache manager instance."""
    global _global_cache
    with _global_lock:
        if _global_cache is None:
            _global_cache = CacheManager()
        return _global_cache


def configure_cache(config: Union[CacheConfig, Dict[str, Any]]) -> CacheManager:
    """Configure the global cache manager."""
    global _global_cache
    with _global_lock:
        if isinstance(config, dict):
            config = CacheConfig.from_dict(config)
        _global_cache = CacheManager(config)
        return _global_cache


def clear_cache() -> int:
    """Clear the global cache."""
    return get_cache().clear()


# =============================================================================
# Decorator
# =============================================================================


def cache_prompt(
    prompt_name: str,
    version: str,
    ttl: Optional[int] = None,
    key_fields: Optional[List[str]] = None,
):
    """
    Decorator to cache prompt execution results.
    
    Args:
        prompt_name: Name of the prompt.
        version: Prompt version.
        ttl: Time-to-live in seconds.
        key_fields: Input fields to use for cache key.
    
    Example:
        @cache_prompt("email_summary", "v1", ttl=3600)
        def summarize_email(email: str) -> str:
            return llm.complete(f"Summarize: {email}")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = get_cache()
            
            # Build inputs from args and kwargs
            inputs = kwargs.copy()
            
            # Check cache
            cached = cache.get(prompt_name, version, inputs, key_fields)
            if cached is not None:
                return cached
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(prompt_name, version, inputs, result, ttl, key_fields)
            
            return result
        
        return wrapper
    return decorator
