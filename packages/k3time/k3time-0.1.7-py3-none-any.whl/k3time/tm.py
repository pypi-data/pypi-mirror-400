#!/usr/bin/env python2
# coding: utf-8

import calendar
import datetime
import time

import pytz
import tzlocal

formats = {
    "default": "%a, %d %b %Y %H:%M:%S UTC",
    "utc": "%a, %d %b %Y %H:%M:%S UTC",
    "iso": "%Y-%m-%dT%H:%M:%S.000Z",
    "archive": "%Y%m%d-%H",
    "compact": "%Y%m%d-%H%M%S",
    "daily": "%Y-%m-%d",
    "daily_compact": "%Y%m%d",
    "mysql": "%Y-%m-%d %H:%M:%S",
    "nginxaccesslog": "%d/%b/%Y:%H:%M:%S",
    "nginxerrorlog": "%Y/%m/%d %H:%M:%S",
}

ts_length = {
    "s": 10,
    "ms": 13,
    "us": 16,
    "ns": 19,
}


def parse(time_str, fmt_key, timezone=None):
    """
    parse time string to `datetime` instance.

    Args:
        time_str(str): time in string. Please refer to timeutil.formats, for example:
            `'Tue, 24 Jan 2017 07:51:59 UTC'`, `'2017-01-24T07:51:59.000Z'`.

        fmt_key(str): specifies time string format.
            It can be a named format alias, or format string:

            - 'default':        '%a, %d %b %Y %H:%M:%S UTC',
            - 'iso':            '%Y-%m-%dT%H:%M:%S.000Z',
            - 'utc':            '%a, %d %b %Y %H:%M:%S UTC',
            - 'archive':        '%Y%m%d-%H',
            - 'compact':        '%Y%m%d-%H%M%S',
            - 'daily':          '%Y-%m-%d',
            - 'mysql':          '%Y-%m-%d %H:%M:%S',
            - 'nginxaccesslog': "%d/%b/%Y:%H:%M:%S",
            - 'nginxerrorlog':  "%Y/%m/%d %H:%M:%S",

            Thus `parse(tm, "default")` is same as `parse(tm, "%a, %d %b %Y %H:%M:%S UTC")`.

        timezone: specifies a timezone to get an aware datetime object. It is a string,
            such as 'Asia/Shanghai'.

    Returns:
        datetime.

    """
    dt = datetime.datetime.strptime(time_str, _get_format(fmt_key))
    if timezone is not None:
        tz = pytz.timezone(timezone)
        dt = tz.localize(dt)

    return dt


def parse_to_ts(time_str, fmt_key):
    """
    Similar to `parse` but returns a timestamp in second instead of a `datetime`
    instance.

    Returns:
        int: timestamp.

    """
    dt = datetime.datetime.strptime(time_str, _get_format(fmt_key))
    return utc_datetime_to_ts(dt)


def format(dt, fmt_key):
    """
    convert datetime instance to specified format time string

    Args:
        dt(datetime): datetime instance

        fmt_key(str): specifies time string format.
            It can be a named format alias, or format string.

    Returns:
        str: time string in specified format.
    """
    return dt.strftime(_get_format(fmt_key))


def format_ts(ts, fmt_key, utc=True):
    """
    convert timestamp to specified format time string

    Args:
        ts(int): timestamp in second

        fmt_key(str): specifies time string format.
            It can be a named format alias, or format string.

        utc(bool): set to `True` to get utc time, set to `False` to get local time.

    Returns:
        str: formatted time string.
    """
    dt = ts_to_datetime(ts, utc)
    return format(dt, fmt_key)


def _get_format(fmt_key):
    return formats.get(fmt_key) or fmt_key


def utc_datetime_to_ts(dt):
    """
    convert datetime instance to timestamp in second

    Args:
        dt(datetime): datetime instance

    Returns:
        int: timestamp in second.
    """
    return int(calendar.timegm(dt.timetuple()))


def datetime_to_ts(dt):
    """
    convert naive or aware datetime instance to timestamp in second

    Args:
        dt(datetime): datetime instance

    Returns:
        int: timestamp in second.
    """
    epoch_dt = datetime.datetime.fromtimestamp(0, tz=pytz.utc)

    if not hasattr(dt, "tzinfo") or dt.tzinfo is None:
        local_tz = tzlocal.get_localzone()
        # tzlocal.get_localzone() returns ZoneInfo in Python 3.9+ which lacks localize()
        if hasattr(local_tz, "localize"):
            dt = local_tz.localize(dt)
        else:
            dt = dt.replace(tzinfo=local_tz)

    delta = dt - epoch_dt
    ts = delta.total_seconds()

    return ts


def ts_to_datetime(ts, utc=True):
    """
    convert timestamp in second to datetime instance

    Args:
        ts(int): timestamp in second

    Returns:
        datetime: datetime instance
    """

    if utc:
        return datetime.datetime.utcfromtimestamp(ts)
    else:
        return datetime.datetime.fromtimestamp(ts)


def ts():
    """
    get current timestamp in second

    Returns:
        int: timestamp in second
    """
    return int(time.time())


def ms():
    """
    get current timestamp in millisecond

    Returns:
        int: timestamp in millisecond
    """
    return int(time.time() * 1000)


def us():
    """
    get current timestamp in microsecond

    Returns:
        int: timestamp in microsecond
    """
    return int(time.time() * (1000**2))


def ns():
    """
    get current timestamp in nanosecond

    Returns:
        int: timestamp in nanosecond
    """
    return int(time.time() * (1000**3))


def to_sec(v):
    """
    Convert millisecond, microsecond or nanosecond to second.

    Args:
        v: timestamp in int, long, float or string.
            It can be a timestamp in second, millisecond(10e-3),
            microsecond(10e-6) or nanosecond(10e-9).

    Returns:
        int: timestamp in second.

    Raises:
        ValueError:  If `v` is not a valid timestamp.
    """

    v = float(str(v))

    if not isinstance(v, float) or v < 0:
        raise ValueError("invalid time to convert to second: {v}".format(v=v))

    num_digits = len(str(int(v)))

    if num_digits == 10:
        return int(v)
    elif num_digits == 13:
        return int(v / 1000)
    elif num_digits == 16:
        return int(v / (1000**2))
    elif num_digits == 19:
        return int(v / (1000**3))
    else:
        raise ValueError("invalid time length, not 10, 13, 16 or 19: {v}".format(v=v))


def is_timestamp(ts, unit=None):
    """
    It check if `ts` is a valid timestamp, in string or number.

    Args:

        ts: is timestamp in string or int.

        unit: specifies what the unit `ts` is in:

            -   `s`:     second
            -   `ms`:    millisecond `10^-3`
            -   `us`:    microsecond `10^-6`
            -   `ns`:    nanosecond  `10^-9`
            -   `None`:  choose automatically.

    Returns:
        bool
    """

    string = str(ts)

    if not string.isdigit():
        return False

    if unit is None:
        return len(string) in list(ts_length.values())

    if unit in ts_length:
        return len(string) == ts_length[unit]

    return False
