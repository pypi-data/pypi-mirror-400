import functools
import types
import typing

if typing.TYPE_CHECKING:
    import polars as pl

    from spacedata.result.base import SpaceDataResultBase


@functools.lru_cache(maxsize=1)
def _get_polars() -> types.ModuleType:
    import polars as pl

    return pl


class SpaceDataPolarsResultMixin:
    async def to_polars(self: "SpaceDataResultBase") -> "pl.DataFrame":
        try:
            pl = _get_polars()
        except ImportError as e:
            raise ImportError(
                "Polars is not installed. Please install it with `pip install polars`."
            ) from e

        data = await self._get_dict_data()
        return pl.DataFrame(data)
