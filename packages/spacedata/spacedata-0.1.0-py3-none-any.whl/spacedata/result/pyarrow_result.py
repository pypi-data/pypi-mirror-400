import functools
import types
import typing

if typing.TYPE_CHECKING:
    import pyarrow as pa

    from spacedata.result.base import SpaceDataResultBase


@functools.lru_cache(maxsize=1)
def _get_pyarrow() -> types.ModuleType:
    import pyarrow as pa

    return pa


class SpaceDataPyarrowResultMixin:
    async def to_pyarrow(self: "SpaceDataResultBase") -> "pa.Table":
        try:
            pa = _get_pyarrow()
        except ImportError as e:
            raise ImportError(
                "PyArrow is not installedPlease install it with `pip install pyarrow`."
            ) from e

        data = await self._get_dict_data()
        return pa.Table.from_pylist(data)
