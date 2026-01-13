import functools
import typing

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from spacedata.exceptions import SpaceDataTemporalException
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import SpaceDataErrorResult, SpaceDataResult


def api_resource_exceptions(func) -> typing.Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> SpaceDataResult | SpaceDataErrorResult:
        resource: BaseResourceProtocol = args[0]
        client = resource.client
        settings = client.settings

        retrying = AsyncRetrying(
            stop=stop_after_attempt(settings.retry_attempts),
            wait=wait_exponential(
                multiplier=settings.retry_wait_multiplier,
                min=settings.retry_wait_min,
                max=settings.retry_wait_max,
            ),
            retry=retry_if_exception_type(SpaceDataTemporalException),
        )

        return await retrying(func, *args, **kwargs)

    return wrapper
