import typing

from spacedata.result.base import SpaceDataErrorResult, SpaceDataResultBase
from spacedata.result.download_result import SpaceDataResultDownloadMixin
from spacedata.result.pandas_result import SpaceDataPandasResultMixin
from spacedata.result.polars_result import SpaceDataPolarsResultMixin
from spacedata.result.pyarrow_result import SpaceDataPyarrowResultMixin

T = typing.TypeVar("T")


class SpaceDataResult(
    SpaceDataResultBase,
    SpaceDataPolarsResultMixin,
    SpaceDataPandasResultMixin,
    SpaceDataPyarrowResultMixin,
    SpaceDataResultDownloadMixin,
    typing.Generic[T],
):
    pass


__all__ = ["SpaceDataResult", "SpaceDataErrorResult"]
