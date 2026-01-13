import asyncio
import typing

from spacedata.result import SpaceDataErrorResult

Job = typing.Callable[[], typing.Awaitable[object]]


async def _run_job(
    idx: int,
    job,
    sem: asyncio.Semaphore,
    results: dict[int, object],
):
    async with sem:
        result = await job()
        results[idx] = result


async def _ordered_worker_generator(
    jobs: typing.Iterable[Job],
    *,
    concurrency: int = 5,
) -> typing.AsyncGenerator[object, None]:
    sem = asyncio.Semaphore(concurrency)
    results: dict[int, object] = {}
    tasks: dict[int, asyncio.Task] = {}

    jobs = list(jobs)

    for idx, job in enumerate(jobs):
        tasks[idx] = asyncio.create_task(_run_job(idx, job, sem, results))

    next_idx = 0
    total = len(tasks)

    try:
        while next_idx < total:
            await tasks[next_idx]

            yield results.pop(next_idx)
            next_idx += 1
    finally:
        for task in tasks.values():
            if not task.done():
                task.cancel()


async def _stop_on_error_generator(
    input_generator: typing.AsyncGenerator[object, None],
) -> typing.AsyncGenerator[object, None]:
    async for item in input_generator:
        if isinstance(item, SpaceDataErrorResult):
            return
        yield item


async def worker_generator(
    jobs: typing.Iterable[Job],
    *,
    concurrency: int = 5,
    items_limit: int | None = None,
    stop_on_error: bool = True,
) -> typing.AsyncGenerator[object, None]:
    count = 0

    generator = _ordered_worker_generator(jobs=jobs, concurrency=concurrency)
    if stop_on_error:
        generator = _stop_on_error_generator(generator)

    async for item in generator:
        yield item
        count += 1
        if items_limit is not None and count >= items_limit:
            return


async def chunked_worker_generator(
    jobs: typing.Iterable[Job],
    *,
    concurrency: int = 5,
    items_limit: int | None = None,
    stop_on_error: bool = True,
) -> typing.AsyncGenerator[object, None]:
    count = 0

    generator = _ordered_worker_generator(jobs=jobs, concurrency=concurrency)
    if stop_on_error:
        generator = _stop_on_error_generator(generator)

    async for chunk in generator:
        if isinstance(chunk, SpaceDataErrorResult):
            yield chunk
            if stop_on_error:
                return
            continue

        for item in chunk:
            yield item
            count += 1
            if items_limit is not None and count >= items_limit:
                return
