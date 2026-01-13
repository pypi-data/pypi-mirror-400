import functools

from spacedata.cache.base import BaseCacheController
from spacedata.cache.memory_controller import InMemoryCacheController
from spacedata.settings import SpaceDataSettings


@functools.lru_cache
def _get_controller(controller_key: str) -> type[BaseCacheController] | None:
    if controller_key == "memory":
        return InMemoryCacheController
    if controller_key == "duckdb":
        from spacedata.cache.duckdb_controller import DuckDBCacheController

        return DuckDBCacheController
    return None


def get_cache_controller(settings: SpaceDataSettings) -> BaseCacheController | None:
    controllers_map = {
        "duckdb": lambda: _get_controller("duckdb"),
        "memory": lambda: _get_controller("memory"),
    }

    controller_key = (
        settings.cache_controller.lower() if settings.cache_controller else None
    )
    if controller_key is None:
        return None

    controller = controllers_map.get(controller_key)
    controller = controller() if controller is not None else controller
    if controller is None:
        raise ValueError(f"Unknown cache controller: {controller_key}")

    return controller(settings=settings)
