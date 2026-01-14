# fmt: off

from datetime import date, datetime, time, timedelta

__all__ = [
    'RICH_OBJS',
]

date_obj      = date(2023, 12, 25)
time_obj      = time(14, 30, 45)
timedelta_obj = timedelta(days=7, hours=3)
datetime_obj  = datetime(2023, 12, 25, 14, 30, 45)

RICH_OBJS = [
    date_obj,
    time_obj,
    timedelta_obj,
    datetime_obj,
]
