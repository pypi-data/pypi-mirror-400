import typing

from pydantic import SkipValidation

from spacedata.decorators.api_resource_pipeline import (
    api_lazy_result,
    api_resource_pipeline,
)
from spacedata.generators import worker_generator
from spacedata.models.neo import NeoLookupInputParams, NeoLookupResultItem
from spacedata.resources.protocol import BaseResourceProtocol
from spacedata.result import SpaceDataErrorResult, SpaceDataResult

T = typing.TypeVar("T")


class NeoLookupResult(SpaceDataResult, typing.Generic[T]):
    URL_KEY = "nasa_jpl_url"


@api_lazy_result
async def _get_response(
    resource: BaseResourceProtocol,
    asteroid_id: int,
) -> NeoLookupResultItem | SpaceDataErrorResult:
    response = await resource.client.make_request(
        "GET",
        f"{resource.client.settings.neo_base_url}/neo/{asteroid_id}",
    )
    return NeoLookupResultItem.model_validate(response)


@api_resource_pipeline(input_model=NeoLookupInputParams)
async def lookup(
    self: typing.Annotated[BaseResourceProtocol, SkipValidation],
    *,
    input_data: NeoLookupInputParams | None = None,
    **kwargs,
) -> NeoLookupResult[NeoLookupResultItem]:
    self.client.logger.debug("Calling lookup endpoint with input_data: %s", input_data)
    if input_data is None:
        raise ValueError("input_data must be provided")

    jobs = [
        lambda asteroid_id=asteroid_id: _get_response(self, asteroid_id)
        for asteroid_id in input_data.asteroid_ids
    ]

    items_generator = worker_generator(jobs=jobs)

    return NeoLookupResult(items=items_generator)
