"""Extensible caching system with multiple backend support.

This module provides a flexible caching abstraction that supports
multiple backends (memory, file-based) with consistent interface.

The cache system uses the Strategy pattern for backend flexibility
and supports TTL-based expiration.

Example:
    cache = get_cache()
    await cache.set("key", {"data": "value"}, ttl=60)
    value = await cache.get("key")
    await cache.delete("key")
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generic, TypeVar

from truthound_dashboard.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheEntry(Generic[T]):
    """Cache entry with value and expiration.

    Attributes:
        value: Cached value.
        expires_at: Expiration datetime.
        created_at: Creation datetime.
    """

    __slots__ = ("value", "expires_at", "created_at")

    def __init__(self, value: T, ttl_seconds: int) -> None:
        """Initialize cache entry.

        Args:
            value: Value to cache.
            ttl_seconds: Time to live in seconds.
        """
        self.value = value
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.utcnow() >= self.expires_at

    @property
    def remaining_ttl(self) -> int:
        """Get remaining TTL in seconds."""
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))


class CacheBackend(ABC):
    """Abstract base class for cache backends.

    Subclass this to implement custom cache storage backends.
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found/expired.
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl_seconds: Time to live in seconds.
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            True if key existed and was deleted.
        """
        ...

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached values."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired.

        Args:
            key: Cache key.

        Returns:
            True if key exists and is valid.
        """
        ...

    async def get_or_set(
        self,
        key: str,
        factory: Any,
        ttl_seconds: int = 60,
    ) -> Any:
        """Get value from cache or compute and cache it.

        Args:
            key: Cache key.
            factory: Callable or coroutine to compute value if not cached.
            ttl_seconds: Time to live in seconds.

        Returns:
            Cached or computed value.
        """
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        elif callable(factory):
            value = factory()
        else:
            value = factory

        await self.set(key, value, ttl_seconds)
        return value

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern.

        Default implementation does nothing. Override for pattern support.

        Args:
            pattern: Pattern to match (implementation-specific).

        Returns:
            Number of keys invalidated.
        """
        return 0


class MemoryCache(CacheBackend):
    """Thread-safe in-memory cache with TTL support.

    Uses asyncio.Lock for thread-safety in async context.
    Includes automatic cleanup of expired entries.
    """

    def __init__(self, max_size: int = 1000, cleanup_interval: int = 300) -> None:
        """Initialize memory cache.

        Args:
            max_size: Maximum number of entries to store.
            cleanup_interval: Interval for cleanup task in seconds.
        """
        self._cache: dict[str, CacheEntry[Any]] = {}
        self._lock = asyncio.Lock()
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: asyncio.Task[None] | None = None

    async def start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    async def _cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed.
        """
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)

    async def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache is full."""
        if len(self._cache) >= self._max_size:
            # Remove oldest 10% of entries
            to_remove = max(1, self._max_size // 10)
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].created_at,
            )
            for key, _ in sorted_entries[:to_remove]:
                del self._cache[key]

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.is_expired:
                del self._cache[key]
                return None
            return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """Set value in cache with TTL."""
        async with self._lock:
            await self._evict_if_needed()
            self._cache[key] = CacheEntry(value, ttl_seconds)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired:
                del self._cache[key]
                return False
            return True

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern (prefix match)."""
        async with self._lock:
            keys_to_remove = [key for key in self._cache if key.startswith(pattern)]
            for key in keys_to_remove:
                del self._cache[key]
            return len(keys_to_remove)

    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            expired_count = sum(1 for e in self._cache.values() if e.is_expired)
            return {
                "total_entries": len(self._cache),
                "expired_entries": expired_count,
                "valid_entries": len(self._cache) - expired_count,
                "max_size": self._max_size,
            }


class FileCache(CacheBackend):
    """File-based cache with TTL support.

    Stores cache entries as JSON files in a directory.
    Suitable for data that should persist across restarts.
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Initialize file cache.

        Args:
            cache_dir: Directory for cache files. Defaults to settings.cache_dir.
        """
        self._cache_dir = cache_dir or get_settings().cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Use hash for safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:32]
        return self._cache_dir / f"{key_hash}.cache"

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        cache_path = self._get_cache_path(key)

        async with self._lock:
            if not cache_path.exists():
                return None

            try:
                data = json.loads(cache_path.read_text())
                expires_at = datetime.fromisoformat(data["expires_at"])

                if datetime.utcnow() >= expires_at:
                    cache_path.unlink(missing_ok=True)
                    return None

                return data["value"]
            except (json.JSONDecodeError, KeyError, ValueError):
                cache_path.unlink(missing_ok=True)
                return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """Set value in cache with TTL."""
        cache_path = self._get_cache_path(key)
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        async with self._lock:
            data = {
                "key": key,
                "value": value,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
            }
            cache_path.write_text(json.dumps(data))

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_path = self._get_cache_path(key)

        async with self._lock:
            if cache_path.exists():
                cache_path.unlink()
                return True
            return False

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            for cache_file in self._cache_dir.glob("*.cache"):
                cache_file.unlink(missing_ok=True)

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return await self.get(key) is not None


class CacheManager:
    """Manager for multiple cache instances with namespacing.

    Provides a unified interface for managing multiple caches
    with different configurations and backends.
    """

    def __init__(self) -> None:
        """Initialize cache manager."""
        self._caches: dict[str, CacheBackend] = {}
        self._default_backend: type[CacheBackend] = MemoryCache

    def register(
        self,
        name: str,
        backend: CacheBackend | None = None,
    ) -> CacheBackend:
        """Register a cache with the manager.

        Args:
            name: Cache name/namespace.
            backend: Cache backend instance. Defaults to MemoryCache.

        Returns:
            Registered cache backend.
        """
        if name not in self._caches:
            self._caches[name] = backend or self._default_backend()
        return self._caches[name]

    def get(self, name: str) -> CacheBackend | None:
        """Get a registered cache.

        Args:
            name: Cache name/namespace.

        Returns:
            Cache backend or None if not registered.
        """
        return self._caches.get(name)

    def get_or_create(self, name: str) -> CacheBackend:
        """Get or create a cache.

        Args:
            name: Cache name/namespace.

        Returns:
            Cache backend.
        """
        return self.register(name)

    async def clear_all(self) -> None:
        """Clear all registered caches."""
        for cache in self._caches.values():
            await cache.clear()


# Singleton instances
_cache: MemoryCache | None = None
_cache_manager: CacheManager | None = None


def get_cache() -> MemoryCache:
    """Get default cache singleton.

    Returns:
        MemoryCache instance.
    """
    global _cache
    if _cache is None:
        _cache = MemoryCache()
    return _cache


def get_cache_manager() -> CacheManager:
    """Get cache manager singleton.

    Returns:
        CacheManager instance.
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def reset_cache() -> None:
    """Reset cache singletons (for testing)."""
    global _cache, _cache_manager
    _cache = None
    _cache_manager = None
