import typing

from pydantic import SkipValidation

from spacedata.decorators.api_resource_pipeline import (
    api_lazy_result,
    api_resource_pipeline,
)
from spacedata.generators import chunked_worker_generator
from spacedata.models.donki import DONKIDateRangeInput, DONKISep
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import SpaceDataResult
from spacedata.utils import split_weekday_ranges


@api_lazy_result
async def _get_response(
    resource: BaseResourceProtocol,
    params: dict[str, typing.Any],
) -> list[DONKISep]:
    response = await resource.client.make_request(
        method="GET",
        url=f"{resource.client.settings.main_base_url}/DONKI/SEP",
        params=params,
    )
    return [DONKISep.model_validate(item) for item in response]


@api_resource_pipeline(input_model=DONKIDateRangeInput)
async def sep(
    self: typing.Annotated[BaseResourceProtocol, SkipValidation],
    *,
    input_data: DONKIDateRangeInput | None = None,
    **kwargs,
) -> SpaceDataResult[DONKISep]:
    self.client.logger.debug("Calling sep endpoint with input_data: %s", input_data)

    if input_data is None:
        raise ValueError("input_data must be provided")

    ranges = split_weekday_ranges(
        weekday_number=self.client.settings.cache_weekday_number,
        start=input_data.start_date,
        end=input_data.end_date,
    )
    params = input_data.model_dump(exclude_unset=True, by_alias=True)

    jobs = [
        lambda params={
            **params,
            "startDate": range_start,
            "endDate": range_end,
        }: _get_response(self, params)
        for range_start, range_end in ranges
    ]

    items_generator = chunked_worker_generator(
        jobs=jobs,
        stop_on_error=True,
    )

    return SpaceDataResult(items=items_generator)
