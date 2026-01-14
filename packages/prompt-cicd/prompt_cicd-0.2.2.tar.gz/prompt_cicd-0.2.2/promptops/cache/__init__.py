"""
Prompt Caching Module for PromptOps.

Provides intelligent caching of LLM responses to:
- Reduce costs on repeated identical calls
- Speed up development and testing
- Support TTL-based expiration
- Offer multiple storage backends
"""

from .manager import (
    CacheManager,
    CacheConfig,
    CacheEntry,
    CacheStats,
    get_cache,
    configure_cache,
    clear_cache,
    cache_prompt,
)

__all__ = [
    "CacheManager",
    "CacheConfig", 
    "CacheEntry",
    "CacheStats",
    "get_cache",
    "configure_cache",
    "clear_cache",
    "cache_prompt",
]
