import datetime
import typing


def get_object_from_path(obj, path: str) -> typing.Any:
    _path = path.split(".")
    for p in _path:
        obj = getattr(obj, p)
    return obj


def get_next_weekday_and_prefix_dates(
    weekday_number: int, date: datetime.date
) -> tuple[tuple[datetime.date, datetime.date], datetime.date] | None:
    is_weekday = date.weekday() == weekday_number
    if is_weekday:
        # in this case, there is no next weekday and prefix dates
        return None

    days_to_next_weekday = (weekday_number - date.weekday()) % 7
    next_weekday = date + datetime.timedelta(days=days_to_next_weekday)
    prefix_dates = (date, date + datetime.timedelta(days=days_to_next_weekday - 1))
    return prefix_dates, next_weekday


def split_in_ranges(
    start: datetime.date, end: datetime.date, max_delta: datetime.timedelta
) -> list[tuple[datetime.date, datetime.date]]:
    ranges = []
    current = start

    while current <= end:
        next_end = min(current + max_delta, end)
        ranges.append((current, next_end))
        current = next_end + datetime.timedelta(days=1)

    return ranges


def split_weekday_ranges(
    weekday_number: int, start: datetime.date, end: datetime.date
) -> list[tuple[datetime.date, datetime.date]]:
    prefix_result = get_next_weekday_and_prefix_dates(weekday_number, start)
    if prefix_result is None:
        return split_in_ranges(start, end, datetime.timedelta(days=6))

    prefix_dates, next_desired_weekday = prefix_result
    if prefix_dates[1] >= end:
        return [(start, end)]

    ranges = []
    ranges.append(prefix_dates)
    ranges.extend(
        split_in_ranges(next_desired_weekday, end, datetime.timedelta(days=6))
    )
    return ranges
