"""
Caching utilities for SMF.
"""

import time
from typing import Any, Dict, Optional

from smf.settings import Settings, StorageBackend


class MemoryCache:
    """In-memory cache with TTL support."""

    def __init__(self, ttl: int):
        self._ttl = ttl
        self._data: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._data.get(key)
        if entry is None:
            return None
        expires_at = entry["expires_at"]
        if expires_at is not None and time.time() >= expires_at:
            self._data.pop(key, None)
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = self._ttl if ttl is None else ttl
        expires_at = None if ttl <= 0 else time.time() + ttl
        self._data[key] = {"value": value, "expires_at": expires_at}

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


def create_cache(settings: Settings) -> MemoryCache:
    if settings.cache_backend == StorageBackend.MEMORY:
        return MemoryCache(ttl=settings.cache_ttl)
    raise NotImplementedError(
        f"Cache backend '{settings.cache_backend}' is not implemented"
    )
