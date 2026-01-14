"""
Storage backends for SMF.
"""

from typing import Any, Dict, Optional

from smf.settings import Settings, StorageBackend


class MemoryStorage:
    """Simple in-memory storage backend."""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


def create_storage(settings: Settings) -> MemoryStorage:
    if settings.storage_backend == StorageBackend.MEMORY:
        return MemoryStorage()
    raise NotImplementedError(
        f"Storage backend '{settings.storage_backend}' is not implemented"
    )
