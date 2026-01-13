from cachetools import TTLCache
from typing import Any, Optional
from ..config import get_settings

settings = get_settings()


class CacheService:
    """Simple in-memory cache with TTL."""

    def __init__(self, maxsize: int = None, ttl: int = None):
        maxsize = maxsize or settings.cache_maxsize
        ttl = ttl or settings.cache_ttl
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def make_key(self, *args) -> str:
        """Create a cache key from arguments."""
        return ":".join(str(arg) for arg in args)


# Global cache instance
cache = CacheService()
