"""
LRU Cache implementation for the Limitless SDK.

Provides a size-limited cache with Least Recently Used eviction policy.
"""

from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    """Size-limited cache with LRU (Least Recently Used) eviction.

    Uses OrderedDict to track access order. When cache is full,
    the least recently accessed item is evicted.

    Args:
        maxsize: Maximum number of items to cache. Defaults to 100.
    """

    def __init__(self, maxsize: int = 100):
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._maxsize = maxsize

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get value from cache, marking it as recently used.

        Args:
            key: Cache key to look up.
            default: Value to return if key not found.

        Returns:
            Cached value if found, default otherwise.
        """
        if key in self._cache:
            self._cache.move_to_end(key)  # Mark as recently used
            return self._cache[key]
        return default

    def __getitem__(self, key: str) -> Any:
        """Get value from cache using bracket notation.

        Args:
            key: Cache key to look up.

        Returns:
            Cached value.

        Raises:
            KeyError: If key not in cache.
        """
        if key in self._cache:
            self._cache.move_to_end(key)  # Mark as recently used
            return self._cache[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set value in cache, evicting LRU item if full.

        Args:
            key: Cache key.
            value: Value to cache.
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._maxsize:
                self._cache.popitem(last=False)  # Evict least recently used
        self._cache[key] = value

    def __len__(self) -> int:
        """Return number of items in cache."""
        return len(self._cache)

    def clear(self) -> None:
        """Clear all items from cache."""
        self._cache.clear()
