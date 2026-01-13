import asyncio
import dataclasses
import typing

T = typing.TypeVar("T")


@dataclasses.dataclass
class SpaceDataErrorResult:
    detail: str
    error: Exception

    def __iter__(self) -> typing.Generator["SpaceDataErrorResult", None, None]:
        yield self


class SpaceDataResultBase(typing.Generic[T]):
    def __init__(self, items: typing.AsyncGenerator[T, None]) -> None:
        self._items = items
        self._cached_list: list[T] = []
        self._exhausted = False
        self._lock = asyncio.Lock()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    async def __aiter__(self) -> typing.AsyncGenerator[T, None]:
        idx = 0
        while True:
            if idx < len(self._cached_list):
                yield self._cached_list[idx]
                idx += 1
                continue

            if self._exhausted:
                break

            async with self._lock:
                if idx >= len(self._cached_list) and not self._exhausted:
                    try:
                        self._cached_list.append(await self._items.__anext__())
                    except StopAsyncIteration:
                        self._exhausted = True

    async def asend(self, value) -> T:
        return await self._items.asend(value)

    async def athrow(self, typ: type, val, tb) -> T:
        return await self._items.athrow(typ, val, tb)

    async def as_list(self) -> list[T]:
        if not self._exhausted:
            async for _ in self:
                pass
        return self._cached_list

    async def _get_dict_data(self) -> list[dict]:
        return [item.model_dump() for item in await self.as_list()]
