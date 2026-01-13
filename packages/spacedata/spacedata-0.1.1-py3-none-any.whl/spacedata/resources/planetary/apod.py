import typing

from pydantic import SkipValidation

from spacedata.decorators.api_resource_pipeline import (
    api_lazy_result,
    api_resource_pipeline,
)
from spacedata.generators import chunked_worker_generator
from spacedata.models.apod import ApodInputParams, ApodResultItem
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import (
    SpaceDataErrorResult,
    SpaceDataResult,
)
from spacedata.utils import split_weekday_ranges

T = typing.TypeVar("T")


class PlanetaryApodResult(SpaceDataResult, typing.Generic[T]):
    URL_KEY = staticmethod(lambda item: item.hdurl or item.url)


@api_lazy_result
async def _get_response(
    resource: BaseResourceProtocol,
    params: dict,
) -> list[ApodResultItem] | SpaceDataErrorResult:
    response = await resource.client.make_request(
        method="GET",
        url=f"{resource.client.settings.main_base_url}/planetary/apod",
        params=params,
    )
    response = response if isinstance(response, list) else [response]
    return [ApodResultItem.model_validate(item) for item in response]


@api_resource_pipeline(input_model=ApodInputParams)
async def apod(
    self: typing.Annotated[BaseResourceProtocol, SkipValidation],
    *,
    input_data: ApodInputParams | None = None,
    **kwargs,
) -> PlanetaryApodResult[ApodResultItem]:
    self.client.logger.debug("Fetching Astronomy Picture of the Day (APOD)")
    if input_data is None:
        raise ValueError("input_data must be provided")

    params = input_data.model_dump(exclude_none=True, exclude_unset=True)

    jobs = []

    if input_data.is_date_range:
        jobs = [
            lambda params={
                **params,
                "start_date": start_date,
                "end_date": end_date,
            }: _get_response(self, params)
            for start_date, end_date in split_weekday_ranges(
                weekday_number=self.client.settings.cache_weekday_number,
                start=input_data.start_date,
                end=input_data.end_date,
            )
        ]
    else:
        jobs = [lambda: _get_response(self, params)]

    items_generator = chunked_worker_generator(jobs=jobs)

    return PlanetaryApodResult(items=items_generator)
