import functools
import typing

from pydantic import BaseModel

from spacedata.decorators.api_resource_exceptions import api_resource_exceptions
from spacedata.decorators.api_resource_params import api_resource_params
from spacedata.decorators.sdk_exceptions import sdk_exceptions
from spacedata.result import SpaceDataErrorResult, SpaceDataResult


def api_resource_pipeline(
    func: typing.Callable | None = None, input_model: type[BaseModel] | None = None
) -> typing.Callable:
    if func is None:
        return lambda f: api_resource_pipeline(f, input_model=input_model)

    @sdk_exceptions
    @api_resource_exceptions
    @api_resource_params(input_model=input_model)
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> SpaceDataResult | SpaceDataErrorResult:
        return await func(*args, **kwargs)

    return wrapper


def api_lazy_result(func: typing.Callable | None = None) -> typing.Callable:
    if func is None:
        return lambda f: api_lazy_result(f)

    @sdk_exceptions
    @api_resource_exceptions
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> SpaceDataResult | SpaceDataErrorResult:
        return await func(*args, **kwargs)

    return wrapper
