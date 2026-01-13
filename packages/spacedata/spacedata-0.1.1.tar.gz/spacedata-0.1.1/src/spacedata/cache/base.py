import abc
import dataclasses
import datetime

from spacedata.settings import SpaceDataSettings


@dataclasses.dataclass
class CacheEntry:
    key: str
    created_at: datetime.datetime
    expires_at: datetime.datetime | None
    data: dict | list[dict]


class BaseCacheController(abc.ABC):
    @abc.abstractmethod
    def __init__(self, settings: SpaceDataSettings):
        self.settings = settings

    @abc.abstractmethod
    def get(self, key: str) -> CacheEntry | None:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, data: dict | list[dict], ttl: int | None = None) -> bool:
        raise NotImplementedError
