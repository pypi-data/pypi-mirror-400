import typing

from pydantic import SkipValidation

from spacedata.decorators.api_resource_pipeline import (
    api_lazy_result,
    api_resource_pipeline,
)
from spacedata.generators import chunked_worker_generator
from spacedata.models.neo import NeoBrowseInputParams, NeoLookupResultItem
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import SpaceDataErrorResult, SpaceDataResult

T = typing.TypeVar("T")


class NeoBrowseResult(SpaceDataResult, typing.Generic[T]):
    URL_KEY = "nasa_jpl_url"


@api_lazy_result
async def _get_response(
    resource: BaseResourceProtocol,
    params: dict[str, typing.Any],
) -> list[NeoLookupResultItem] | SpaceDataErrorResult:
    response = await resource.client.make_request(
        method="GET",
        url=f"{resource.client.settings.neo_base_url}/neo/browse",
        params=params,
    )
    data = response.get("near_earth_objects", [])
    return [NeoLookupResultItem.model_validate(item) for item in data]


@api_resource_pipeline(input_model=NeoBrowseInputParams)
async def browse(
    self: typing.Annotated[BaseResourceProtocol, SkipValidation],
    *,
    input_data: NeoBrowseInputParams | None = None,
    **kwargs,
) -> NeoBrowseResult[NeoLookupResultItem]:
    self.client.logger.info("Fetching NEO browse data")

    if input_data is None:
        raise ValueError("Input data is required")

    total_pages = (input_data.limit + input_data.size - 1) // input_data.size

    params = input_data.model_dump(exclude_unset=True, by_alias=True)
    params.pop("limit", None)

    jobs = [
        lambda params={**params, "page": p}: _get_response(self, params)
        for p in range(input_data.page, input_data.page + total_pages)
    ]

    items_generator = chunked_worker_generator(
        jobs=jobs,
        items_limit=input_data.limit,
        stop_on_error=True,
    )

    return NeoBrowseResult(items=items_generator)
