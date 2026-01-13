import itertools
import typing

from pydantic import SkipValidation

from spacedata.decorators.api_resource_pipeline import (
    api_lazy_result,
    api_resource_pipeline,
)
from spacedata.generators import chunked_worker_generator
from spacedata.models.neo import NeoFeedInputParams, NeoFeedResultItem
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import SpaceDataErrorResult, SpaceDataResult
from spacedata.utils import split_weekday_ranges

T = typing.TypeVar("T")


class NeoFeedResult(SpaceDataResult, typing.Generic[T]):
    URL_KEY = "nasa_jpl_url"


@api_lazy_result
async def _get_response(
    resource: BaseResourceProtocol,
    params: dict[str, typing.Any],
) -> list[NeoFeedResultItem] | SpaceDataErrorResult:
    response = await resource.client.make_request(
        method="GET",
        url=f"{resource.client.settings.neo_base_url}/feed",
        params=params,
    )

    items = (
        [{"date": date, **item} for item in entries]
        for date, entries in response.get("near_earth_objects", {}).items()
    )
    data = list(itertools.chain.from_iterable(items))
    return [NeoFeedResultItem.model_validate(item) for item in data]


@api_resource_pipeline(input_model=NeoFeedInputParams)
async def feed(
    self: typing.Annotated[BaseResourceProtocol, SkipValidation],
    *,
    input_data: NeoFeedInputParams | None = None,
    **kwargs,
) -> NeoFeedResult[NeoFeedResultItem]:
    self.client.logger.debug("Calling feed endpoint with input_data: %s", input_data)

    if input_data is None:
        raise ValueError("input_data must be provided")

    jobs = [
        lambda params={
            **input_data.model_dump(exclude_unset=True, by_alias=True),
            "start_date": start_date,
            "end_date": end_date,
        }: _get_response(self, params)
        for start_date, end_date in split_weekday_ranges(
            weekday_number=self.client.settings.cache_weekday_number,
            start=input_data.start_date,
            end=input_data.end_date,
        )
    ]

    items_generator = chunked_worker_generator(
        jobs=jobs,
        stop_on_error=True,
    )

    return NeoFeedResult(items=items_generator)
