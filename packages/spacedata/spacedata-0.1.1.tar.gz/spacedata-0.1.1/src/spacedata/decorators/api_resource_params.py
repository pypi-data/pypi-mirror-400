import functools
import typing

from pydantic import BaseModel, ValidationError

from spacedata.result import SpaceDataErrorResult, SpaceDataResult


def _get_input_data(data: dict, input_model: type[BaseModel]) -> BaseModel:
    try:
        return input_model(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def api_resource_params(
    func: typing.Callable | None = None, input_model: type[BaseModel] | None = None
) -> typing.Callable:
    if not func:
        return lambda f: api_resource_params(f, input_model=input_model)

    if not input_model:
        raise ValueError("input_model must be provided")

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> SpaceDataResult | SpaceDataErrorResult:
        input_data = kwargs.pop("input_data", None) or _get_input_data(
            kwargs, input_model
        )
        return func(*args, input_data=input_data, **kwargs)

    return wrapper
