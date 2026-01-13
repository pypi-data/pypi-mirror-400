import logging

from httpx import AsyncClient, Response

from spacedata.cache.base import BaseCacheController
from spacedata.cache.setup import get_cache_controller
from spacedata.exceptions import (
    SpaceDataBadRequestException,
    SpaceDataTemporalException,
)
from spacedata.logger import get_level_from_name, setup_logger
from spacedata.resources.donki import DONKIResource
from spacedata.resources.insight import InSightResource
from spacedata.resources.neo import NeoResource
from spacedata.resources.planetary import PlanetaryResource
from spacedata.settings import SpaceDataSettings


class SpaceDataClient:
    def __init__(
        self,
        api_key: str | None = None,
        logger: logging.Logger | None = None,
        settings: SpaceDataSettings | None = None,
        cache_controller: BaseCacheController | None = None,
    ) -> None:
        self.client = AsyncClient()
        self.settings = settings or SpaceDataSettings()
        self.api_key = api_key or self.settings.api_key
        self.logger = logger or setup_logger(
            __name__,
            get_level_from_name(self.settings.logging_level.value),
        )
        self.cache_controller = cache_controller or get_cache_controller(self.settings)

        self.donki = DONKIResource(client=self)
        self.neo = NeoResource(client=self)
        self.planetary = PlanetaryResource(client=self)
        self.insight = InSightResource(client=self)

    def _get_user_agent(self) -> str:
        return "SpaceDataClient/1.0"

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": self._get_user_agent(),
        }
        return headers

    def _get_query_params(self) -> dict[str, str]:
        params = {}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "SpaceDataClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    def _validate_response(self, response: Response) -> dict | list[dict]:
        if response.status_code >= 500:
            raise SpaceDataTemporalException(response.text)

        if response.status_code >= 400:
            raise SpaceDataBadRequestException(response.text)

        response.raise_for_status()
        return response.json()

    async def _make_request(
        self, method: str, url: str, params: dict | None = None, **kwargs
    ) -> dict | list[dict]:
        if params is None:
            params = {}
        query_params = self._get_query_params()
        query_params.update(params)

        headers = self._get_headers()

        self.logger.debug(
            f"Making {method} request to {url} with params:"
            f"{query_params} and kwargs {kwargs}"
        )

        response = await self.client.request(
            method,
            url,
            params=query_params,
            headers=headers,
            timeout=self.settings.http_timeout,
            **kwargs,
        )
        response = self._validate_response(response)
        return response

    def _get_cache_key(self, method: str, url: str, params: dict | None = None) -> str:
        if params is None:
            params = {}
        query_params = self._get_query_params()
        query_params.update(params)
        return f"{method}_{url}_{query_params}"

    def _handle_cache(
        self,
        method: str,
        url: str,
        params: dict | None = None,
    ) -> dict | list[dict] | None:
        if self.cache_controller is None:
            return None

        cache_key = self._get_cache_key(method, url, params)
        cached_response = self.cache_controller.get(cache_key)
        if cached_response is not None:
            self.logger.debug(f"Using cached response for {cache_key}")
            return cached_response.data
        return None

    async def make_request(
        self, method: str, url: str, params: dict | None = None, **kwargs
    ) -> dict | list[dict]:
        if self.cache_controller is None:
            return await self._make_request(method, url, params, **kwargs)

        cached_response = self._handle_cache(method, url, params)
        if cached_response is not None:
            return cached_response

        response = await self._make_request(method, url, params, **kwargs)

        self.cache_controller.set(
            key=self._get_cache_key(method, url, params),
            data=response,
            ttl=self.settings.cache_ttl,
        )
        return response


__all__ = ["SpaceDataClient"]
