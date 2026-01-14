"""
Time convertion utils.

    >>> parse('2017-01-24T07:51:59.000Z', 'iso')
    datetime.datetime(2017, 1, 24, 7, 51, 59)
    >>> format_ts(1485216000, 'iso')
    '2017-01-24T00:00:00.000Z'
    >>> format_ts(1485216000, '%Y-%m-%d')
    '2017-01-24'

"""

from .tm import (
    formats,
    parse_to_ts,
    parse,
    format,
    format_ts,
    utc_datetime_to_ts,
    datetime_to_ts,
    ts_to_datetime,
    ts,
    ms,
    us,
    ns,
    to_sec,
    is_timestamp,
)

__all__ = [
    "formats",
    "parse_to_ts",
    "parse",
    "format",
    "format_ts",
    "utc_datetime_to_ts",
    "datetime_to_ts",
    "ts_to_datetime",
    "ts",
    "ms",
    "us",
    "ns",
    "to_sec",
    "is_timestamp",
]

from importlib.metadata import version

__version__ = version("k3time")
