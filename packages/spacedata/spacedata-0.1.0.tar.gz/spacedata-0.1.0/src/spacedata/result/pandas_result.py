import functools
import types
import typing

if typing.TYPE_CHECKING:
    import pandas as pd

    from spacedata.result.base import SpaceDataResultBase


@functools.lru_cache(maxsize=1)
def _get_pandas() -> types.ModuleType:
    import pandas as pd

    return pd


class SpaceDataPandasResultMixin:
    async def to_pandas(self: "SpaceDataResultBase") -> "pd.DataFrame":
        try:
            pd = _get_pandas()
        except ImportError as e:
            raise ImportError(
                "Pandas is not installed. Please install it with `pip install pandas`."
            ) from e

        data = await self._get_dict_data()
        return pd.DataFrame(data)
