from functools import wraps
from logging import Logger
from typing import Callable

from httpx import HTTPStatusError
from pydantic import ValidationError

from spacedata.exceptions import (
    SpaceDataBadRequestException,
    SpaceDataTemporalException,
)
from spacedata.result import SpaceDataErrorResult, SpaceDataResult
from spacedata.utils import get_object_from_path


def sdk_exceptions(
    func: Callable | None = None, logger_path: str = "client.logger"
) -> Callable:
    if not func:
        return lambda f: sdk_exceptions(f, logger_path=logger_path)

    if logger_path is None:
        raise ValueError("logger_path is required")

    @wraps(func)
    async def wrapper(*args, **kwargs) -> SpaceDataResult | SpaceDataErrorResult:
        logger: Logger = get_object_from_path(args[0], logger_path)

        result = None
        try:
            result = await func(*args, **kwargs)
        except ValidationError as e:
            logger.error("Validation error: %s", e)
            result = SpaceDataErrorResult(detail="Validation error", error=e)
        except HTTPStatusError as e:
            logger.error("HTTP error: %s", e)
            result = SpaceDataErrorResult(detail="HTTP error", error=e)
        except SpaceDataBadRequestException as e:
            logger.error("Bad request error: %s", e)
            result = SpaceDataErrorResult(detail="Bad request error", error=e)
        except SpaceDataTemporalException as e:
            logger.error("Temporal error: %s", e)
            result = SpaceDataErrorResult(detail="Temporal error", error=e)

        # We want to avoid raise exception to the user
        # so we return the result as SpaceDataErrorResult
        except Exception as e:
            logger.error("Unexpected error: %s", e, exc_info=True)
            result = SpaceDataErrorResult(detail="Unexpected error", error=e)

        return result

    return wrapper
