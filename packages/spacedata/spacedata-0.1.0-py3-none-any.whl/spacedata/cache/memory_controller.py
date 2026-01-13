import datetime

from spacedata.cache.base import BaseCacheController, CacheEntry
from spacedata.settings import SpaceDataSettings


class InMemoryCacheController(BaseCacheController):
    def __init__(self, settings: SpaceDataSettings):
        self.settings = settings
        self.data = {}

    def get(self, key: str) -> CacheEntry | None:
        entry = self.data.get(key)
        if entry is None:
            return None
        if entry.expires_at is not None and entry.expires_at < datetime.datetime.now():
            return None
        return entry

    def set(self, key: str, data: dict | list[dict], ttl: int | None = None) -> bool:
        created_at = datetime.datetime.now()
        expires_at = None
        if ttl is not None:
            expires_at = created_at + datetime.timedelta(seconds=ttl)

        self.data[key] = CacheEntry(
            key=key,
            data=data,
            created_at=created_at,
            expires_at=expires_at,
        )
        return True
