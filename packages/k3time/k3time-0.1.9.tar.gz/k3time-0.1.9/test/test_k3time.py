#!/usr/bin/env python2.6
# coding: utf-8

import datetime
import time
import unittest

import pytz

import k3time
import k3ut

dd = k3ut.dd

test_case = {
    "ts": {
        "day_accuracy": 1485216000,
        "hour_accuracy": 1485241200,
        "second_accuracy": 1485244319,
    },
    "format": {
        "default": "Tue, 24 Jan 2017 07:51:59 UTC",
        "iso": "2017-01-24T07:51:59.000Z",
        "utc": "Tue, 24 Jan 2017 07:51:59 UTC",
        "archive": "20170124-07",
        "compact": "20170124-075159",
        "daily": "2017-01-24",
        "daily_compact": "20170124",
        "mysql": "2017-01-24 07:51:59",
        "nginxaccesslog": "24/Jan/2017:07:51:59",
        "nginxerrorlog": "2017/01/24 07:51:59",
    },
}


class TestTimeutil(unittest.TestCase):
    def test_direct_format(self):
        for fmt_key, tm_str in list(test_case["format"].items()):
            # parse
            dt_key = k3time.parse(tm_str, fmt_key)
            dt_direct = k3time.parse(tm_str, k3time.formats[fmt_key])

            self.assertTrue(dt_key == dt_direct)

            # format
            self.assertEqual(tm_str, k3time.format(dt_key, fmt_key))
            self.assertEqual(tm_str, k3time.format(dt_key, k3time.formats[fmt_key]))

            # format_ts
            now = int(time.time())
            self.assertEqual(k3time.format_ts(now, fmt_key), k3time.format_ts(now, k3time.formats[fmt_key]))

    def test_parse(self):
        tss = test_case["ts"]

        for fmt_key, tm_str in list(test_case["format"].items()):
            dt = k3time.parse(tm_str, fmt_key)
            ts = k3time.utc_datetime_to_ts(dt)

            if fmt_key == "archive":
                self.assertEqual(tss["hour_accuracy"], ts)
                self.assertEqual(tss["hour_accuracy"], k3time.parse_to_ts(tm_str, fmt_key))
            elif fmt_key.startswith("daily"):
                self.assertEqual(tss["day_accuracy"], ts)
                self.assertEqual(tss["day_accuracy"], k3time.parse_to_ts(tm_str, fmt_key))
            else:
                self.assertEqual(tss["second_accuracy"], ts)
                self.assertEqual(tss["second_accuracy"], k3time.parse_to_ts(tm_str, fmt_key))

    def test_format(self):
        dt = k3time.ts_to_datetime(test_case["ts"]["second_accuracy"])

        for fmt_key, tm_str in list(test_case["format"].items()):
            convert_tm_str = k3time.format(dt, fmt_key)

            self.assertEqual(tm_str, convert_tm_str)

    def test_format_ts(self):
        for fmt_key, tm_str in list(test_case["format"].items()):
            convert_tm_str = k3time.format_ts(test_case["ts"]["second_accuracy"], fmt_key)

            self.assertEqual(tm_str, convert_tm_str)

    def test_ts_and_datetime_conversion(self):
        ts = k3time.ts()

        dt = k3time.ts_to_datetime(ts)
        converted_ts = k3time.utc_datetime_to_ts(dt)

        self.assertEqual(ts, converted_ts)

    def test_timestamp(self):
        cases = [
            (k3time.ts, 10, 1, 2),
            (k3time.ms, 13, 0.001, 3),
            (k3time.us, 16, 0.000001, 300),
            (k3time.ns, 19, 0.000000001, 300000),
        ]

        for timestamp_func, length, unit_ts, tolerance_ts in cases:
            ts1 = timestamp_func()

            time.sleep(unit_ts)

            ts2 = timestamp_func()

            self.assertTrue(ts1 < ts2 < ts1 + tolerance_ts)

            self.assertEqual(length, len(str(ts2)))

    def test_to_sec(self):
        ts = k3time.ts()

        cases = (
            ts,
            ts + 0.1,
            ts * 1000,
            ts * 1000 + 1,
            ts * 1000 + 0.1,
            ts * 1000 * 1000,
            ts * 1000 * 1000 + 1,
            ts * 1000 * 1000 + 0.1,
            ts * 1000 * 1000 * 1000,
            ts * 1000 * 1000 * 1000 + 1,
            ts * 1000 * 1000 * 1000 + 0.1,
        )

        for inp in cases:
            dd(inp, ts)

            self.assertEqual(ts, k3time.to_sec(inp), "convert {inp} to second".format(inp=repr(inp)))

            self.assertEqual(ts, k3time.to_sec(str(inp)), "convert {inp} to second".format(inp=repr(inp)))

    def test_to_ts_invalid_input(self):
        cases = (
            "a",
            "1",
            "1.1",
            -123456789,
            {},
            [],
            (),
            True,
            datetime.datetime.now(),
        )

        for inp in cases:
            with self.assertRaises(ValueError):
                k3time.to_sec(inp)

    def test_is_timestamp(self):
        cases = (
            (
                False,
                None,
                False,
            ),
            (
                0,
                None,
                False,
            ),
            (
                "0",
                None,
                False,
            ),
            (
                "0",
                None,
                False,
            ),
            (
                (),
                None,
                False,
            ),
            (
                [],
                None,
                False,
            ),
            (
                {},
                None,
                False,
            ),
            (
                type,
                None,
                False,
            ),
            (
                149361634,
                None,
                False,
            ),
            (
                14936163419,
                None,
                False,
            ),
            (
                149361634100,
                None,
                False,
            ),
            (
                14936163410009,
                None,
                False,
            ),
            (
                149361634100011,
                None,
                False,
            ),
            (
                14936163410001119,
                None,
                False,
            ),
            (
                149361634100011122,
                None,
                False,
            ),
            (
                14936163410001112229,
                None,
                False,
            ),
            (
                1493616341,
                None,
                True,
            ),
            (
                1493616341000,
                None,
                True,
            ),
            (
                1493616341000111,
                None,
                True,
            ),
            (
                1493616341000111222,
                None,
                True,
            ),
            (
                1493616341,
                "s",
                True,
            ),
            (
                1493616341,
                "ms",
                False,
            ),
            (
                1493616341,
                "us",
                False,
            ),
            (
                1493616341,
                "ns",
                False,
            ),
            (
                1493616341000,
                "s",
                False,
            ),
            (
                1493616341000,
                "ms",
                True,
            ),
            (
                1493616341000,
                "us",
                False,
            ),
            (
                1493616341000,
                "ns",
                False,
            ),
            (
                1493616341000111,
                "s",
                False,
            ),
            (
                1493616341000111,
                "ms",
                False,
            ),
            (
                1493616341000111,
                "us",
                True,
            ),
            (
                1493616341000111,
                "ns",
                False,
            ),
            (
                1493616341000111222,
                "s",
                False,
            ),
            (
                1493616341000111222,
                "ms",
                False,
            ),
            (
                1493616341000111222,
                "us",
                False,
            ),
            (
                1493616341000111222,
                "ns",
                True,
            ),
        )

        for s, unit, expected in cases:
            dd(s, unit, expected)

            rst = k3time.is_timestamp(s, unit=unit)
            dd("rst: ", rst)

            self.assertEqual(expected, rst)

            # test input as string
            rst = k3time.is_timestamp(str(s), unit=unit)
            dd("rst(str): ", rst)

            self.assertEqual(expected, rst)

    def test_datetime_to_ts(self):
        ts = time.time()

        dt = datetime.datetime.fromtimestamp(ts)
        r = k3time.datetime_to_ts(dt)
        self.assertAlmostEqual(ts, r, places=2)

        test_timezones = (
            "US/Pacific",
            "Europe/Warsaw",
            "Asia/Shanghai",
        )

        for timezone_name in test_timezones:
            dt = datetime.datetime.fromtimestamp(ts, tz=pytz.timezone(timezone_name))

            r = k3time.datetime_to_ts(dt)
            self.assertAlmostEqual(ts, r, places=2)

    def test_parse_with_timezone(self):
        cases = (
            ("2018-04-03 17:45:01", "Asia/Shanghai", 1522748701),
            ("2018-04-03 17:45:01", "UTC", 1522748701 + 3600 * 8),
        )

        for time_str, timezone, exp_ts in cases:
            dt = k3time.parse(time_str, "mysql", timezone=timezone)
            ts = k3time.datetime_to_ts(dt)

            self.assertEqual(exp_ts, ts)
