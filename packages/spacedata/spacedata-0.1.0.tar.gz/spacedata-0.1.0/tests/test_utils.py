import datetime

from spacedata.utils import split_weekday_ranges


def test_split_weekday_ranges():
    assert split_weekday_ranges(
        weekday_number=0,
        start=datetime.date(2026, 1, 2),
        end=datetime.date(2026, 1, 10),
    ) == [
        (datetime.date(2026, 1, 2), datetime.date(2026, 1, 4)),
        (datetime.date(2026, 1, 5), datetime.date(2026, 1, 10)),
    ]

    assert split_weekday_ranges(
        weekday_number=0,
        start=datetime.date(2026, 1, 5),
        end=datetime.date(2026, 1, 5),
    ) == [(datetime.date(2026, 1, 5), datetime.date(2026, 1, 5))]

    # Test Tuesday (1)
    # Jan 2, 2026 is Friday (4)
    # Next Tuesday is Jan 6, 2026
    assert split_weekday_ranges(
        weekday_number=1,
        start=datetime.date(2026, 1, 2),
        end=datetime.date(2026, 1, 10),
    ) == [
        (datetime.date(2026, 1, 2), datetime.date(2026, 1, 5)),
        (datetime.date(2026, 1, 6), datetime.date(2026, 1, 10)),
    ]


def test_split_weekday_ranges_monday():
    # Test case 1: Partial week (Mon Jan 2 to Sun Jan 10)
    assert split_weekday_ranges(
        weekday_number=0,
        start=datetime.date(2026, 1, 2),
        end=datetime.date(2026, 1, 10),
    ) == [
        (datetime.date(2026, 1, 2), datetime.date(2026, 1, 4)),
        (datetime.date(2026, 1, 5), datetime.date(2026, 1, 10)),
    ]

    # Test case 2: Full two weeks (Mon Jan 5 to Sun Jan 18)
    # Should result in two strict 7-day chunks:
    # 1. Mon Jan 5 - Sun Jan 11 (7 days)
    # 2. Mon Jan 12 - Sun Jan 18 (7 days)
    assert split_weekday_ranges(
        weekday_number=0,
        start=datetime.date(2026, 1, 5),
        end=datetime.date(2026, 1, 18),
    ) == [
        (datetime.date(2026, 1, 5), datetime.date(2026, 1, 11)),
        (datetime.date(2026, 1, 12), datetime.date(2026, 1, 18)),
    ]

    # Test case 3: Start on Monday with small range
    assert split_weekday_ranges(
        weekday_number=0,
        start=datetime.date(2026, 1, 5),
        end=datetime.date(2026, 1, 10),
    ) == [
        (datetime.date(2026, 1, 5), datetime.date(2026, 1, 10)),
    ]
