import typing

from pydantic import SkipValidation

from spacedata.decorators.api_resource_pipeline import (
    api_lazy_result,
    api_resource_pipeline,
)
from spacedata.generators import chunked_worker_generator
from spacedata.models.insight import InSightInput, InSightWeatherResult
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import SpaceDataResult

T = typing.TypeVar("T")


class InSightWeatherResultContainer(SpaceDataResult, typing.Generic[T]):
    pass


@api_lazy_result
async def _get_response(
    resource: BaseResourceProtocol,
    params: dict,
) -> list[InSightWeatherResult]:
    response = await resource.client.make_request(
        method="GET",
        url=f"{resource.client.settings.main_base_url}/insight_weather/",
        params=params,
    )
    return [InSightWeatherResult.model_validate(response)]


@api_resource_pipeline(input_model=InSightInput)
async def mars_weather(
    self: typing.Annotated[BaseResourceProtocol, SkipValidation],
    *,
    input_data: InSightInput | None = None,
    **kwargs,
) -> InSightWeatherResultContainer[InSightWeatherResult]:
    self.client.logger.debug("Fetching InSight Mars Weather")
    if input_data is None:
        input_data = InSightInput()

    params = input_data.model_dump(exclude_none=True, exclude_unset=True)
    params.update({"feedtype": "json", "ver": 1.0})

    jobs = [lambda: _get_response(self, params)]

    items_generator = chunked_worker_generator(jobs=jobs)

    return InSightWeatherResultContainer(items=items_generator)
