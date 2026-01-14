import unittest
from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from amarket.functions import (
    check_interval_overlap,
    convert_to_timestamp,
    find_nearest_idx,
    fmt,
    format_number,
    is_sorted,
    is_timestamp_ms,
)
from amarket.functions.utils import s_fmt


class TestFunctions(unittest.TestCase):
    def test_is_sorted(self):
        arr = [91233.01, 93212.22, 94183, 97145.19, 100_000.11, 100_000.11]
        self.assertTrue(is_sorted(arr))
        self.assertFalse(is_sorted(arr, reverse_order=True))
        self.assertTrue(is_sorted(reversed(arr), reverse_order=True))
        self.assertFalse(is_sorted(arr, unique=True))
        self.assertTrue(is_sorted(arr[:-1], unique=True))
        self.assertFalse(is_sorted(arr, reverse_order=True, unique=True))
        self.assertTrue(is_sorted(reversed(arr[:-1]), reverse_order=True, unique=True))

    def test_find_nearest_idx(self):
        arr = [91233.01, 93212.22, 94183, 97145.19, 100_000.11]
        # Format of test tuple: (input_value, closest_index, left_index, right_index)
        test = [(95000, (2, 2, 3)), (950009, (None, None, None)), (909, (None, None, None)),
                (94001.21, (2, 1, 2)), (96000, (3, 2, 3)), (99999.99, (4, 3, 4)),
                (94183, (2, 1, 3)), (100_000.11, (4, 3, 4)), (91233.01, (0, 0, 1))]
        for val, exp in test:
            self.assertEqual(find_nearest_idx(arr, val), exp)

    def test_check_interval_overlap(self):
        data = [((0, 5), (3, 4), True), ((0, 5), (3, 7), True), ((0, 5), (6, 7), False),
                ((0, 5), (-1, 6), True), ((0, 5), (-1, 3), True), ((0, 5), (7, 8), False),
                ((0, 5), (-4, 0), True), ((0, 5), (-4, -0.2), False)]
        for interval1, interval2, expected in data:
            self.assertEqual(check_interval_overlap(interval1, interval2), expected)

    def test_convert_to_timestamp(self):
        expected = 1609459200  # 2021-01-01T00:00:00 in UTC

        # Test with Unix timestamp in seconds
        self.assertEqual(convert_to_timestamp(expected), expected)

        # Test with Unix timestamp in milliseconds (should convert to seconds)
        self.assertEqual(convert_to_timestamp(expected * 1000), expected)

        # Test with ISO format datetime string
        self.assertEqual(convert_to_timestamp("2021-01-01T00:00:00"), expected)

        # Test with ISO format datetime string with timezone info
        self.assertEqual(convert_to_timestamp("2021-01-01T00:00:00+00:00"), expected)
        self.assertEqual(convert_to_timestamp("2021-01-01T00:00:00Z"), expected)

        # Test with GMT+3 timezone
        self.assertEqual(convert_to_timestamp("2021-01-01T03:00:00+03:00"), expected)

        # Test with invalid input
        self.assertIsNone(convert_to_timestamp("invalid"))

        # Test milliseconds detection using decimal digits logic
        current_ts = int(datetime.now().timestamp())
        future_ms = (current_ts + 1000) * 1000  # a milliseconds timestamp
        self.assertEqual(convert_to_timestamp(future_ms), current_ts + 1000)

        # Test with very large value that should be treated as milliseconds
        large_value = 9999999999999  # it should be treated as ms
        self.assertEqual(convert_to_timestamp(large_value), round(large_value / 1000))

    def test_fmt(self):
        # Fixed timestamp for testing (2021-01-01 12:00:00 UTC)
        fixed_ts = 1609459200
        dt_obj = datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        expected = "2021-01-01 00:00:00"

        # Test with datetime object
        self.assertEqual(expected, fmt(dt_obj))

        # Test with timestamp
        expected_format = datetime.fromtimestamp(fixed_ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(expected_format, fmt(fixed_ts))

        # Test with custom format
        custom_format = "%d/%m/%Y"
        self.assertEqual("01/01/2021", fmt(dt_obj, fmt=custom_format))

        # Test with different timezone - UTC using ZoneInfo
        utc_tz = ZoneInfo('UTC')
        dt_utc = datetime(2021, 1, 1, 0, 0, 0, tzinfo=utc_tz)
        self.assertEqual(expected, fmt(dt_utc))
        self.assertEqual(expected, fmt(fixed_ts, tz=timezone.utc))
        self.assertEqual(expected, fmt(fixed_ts, tz=utc_tz))
        self.assertEqual(expected, fmt(fixed_ts, tz='UTC'))

        # Test with different timezone - Europe/Moscow using ZoneInfo
        msk_tz = ZoneInfo('Europe/Moscow')
        dt_msk = datetime(2021, 1, 1, 3, 0, 0, tzinfo=msk_tz)
        self.assertEqual(expected, fmt(dt_msk))
        self.assertEqual(expected, fmt(dt_msk, tz=utc_tz))
        self.assertEqual(expected, fmt(dt_msk, tz='UTC'))

        # Note: The timestamp will be converted to Moscow time
        moscow_time = datetime.fromtimestamp(fixed_ts, tz=msk_tz).strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(moscow_time, fmt(fixed_ts, tz=msk_tz))

        # Test that fmt() correctly handles timestamps in milliseconds
        # Get current timestamp in seconds and milliseconds
        current_ts = int(datetime.now().timestamp())
        current_ms = current_ts * 1000
        expected_format = datetime.fromtimestamp(current_ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # Test with milliseconds timestamp - should auto-detect and convert to seconds
        self.assertEqual(expected_format, fmt(current_ms))

        # Test with future timestamps in milliseconds
        future_sec = current_ts + 1000
        future_ms = future_sec * 1000
        expected_future = datetime.fromtimestamp(future_sec, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(expected_future, fmt(future_ms))

        # Test with very large value that should be treated as milliseconds
        large_value = 9999999999999  # This should be treated as ms timestamp
        expected_large = datetime.fromtimestamp(large_value / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(expected_large, fmt(large_value))

        # Test with None timestamp and custom empty_value
        self.assertEqual("Custom Empty", fmt(None, empty_value="Custom Empty"))
        self.assertEqual("", fmt(None, empty_value=""))
        self.assertEqual("N/A", fmt(None, empty_value="N/A"))

        # Test backward compatibility - default should still be 'Never'
        self.assertEqual("Never", fmt(None))

        # Test with datetime object (should not use empty_value)
        dt_obj = datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        expected = "2021-01-01 00:00:00"
        self.assertEqual(expected, fmt(dt_obj))
        self.assertEqual(expected, fmt(dt_obj, empty_value="Custom Empty"))

    def test_is_timestamp_ms(self):
        # Get current timestamp in seconds and milliseconds
        current_ts = int(datetime.now().timestamp())
        current_ms = current_ts * 1000

        # Test with current timestamps
        self.assertTrue(is_timestamp_ms(current_ms))  # Should be true for ms timestamp
        self.assertFalse(is_timestamp_ms(current_ts))  # Should be false for seconds timestamp

        # Test with future timestamps
        future_sec = current_ts + 1000
        future_ms = future_sec * 1000
        self.assertTrue(is_timestamp_ms(future_ms))
        self.assertFalse(is_timestamp_ms(future_sec))

        # Test with negative values (should be False)
        self.assertFalse(is_timestamp_ms(-1))
        self.assertFalse(is_timestamp_ms(-current_ts))

        # Test with zero value (should be False)
        self.assertFalse(is_timestamp_ms(0))
        self.assertFalse(is_timestamp_ms("0"))

        # Test with very large value that has enough digits to be considered ms
        large_value = 9999999999999  # This should be treated as ms timestamp
        self.assertTrue(is_timestamp_ms(large_value))

        # Test with string representations
        self.assertTrue(is_timestamp_ms(str(current_ms)))  # String ms timestamp
        self.assertFalse(is_timestamp_ms(str(current_ts)))  # String seconds timestamp

        # Test with invalid strings
        self.assertFalse(is_timestamp_ms("not-a-timestamp"))
        self.assertFalse(is_timestamp_ms("123abc"))

    def test_s_fmt(self):
        """Combined test for s_fmt function covering all scenarios"""
        # Test basic functionality from docstring example
        result = s_fmt('Ziegh1xoIlievu0kid7Ub3eiPheegh6Jtichei3AAQuaisa3oob4aeNeAhmai0ch', 3, 3)
        self.assertEqual(result, 'Zie***0ch')

        # Test with a string that's too short to show both beginning and ending
        # When the total length is less than or equal to (show_beginning + show_ending)
        result = s_fmt('12345', 3, 3)  # Length = 5, show_beginning + show_ending = 6
        self.assertEqual(result, '********')  # Should return len(s) + 3 asterisks = 5 + 3 = 8

        # Test with a very short string
        result = s_fmt('12', 1, 1)  # Length = 2, show_beginning + show_ending = 2
        self.assertEqual(result, '*****')  # Should return len(s) + 3 asterisks = 2 + 3 = 5

        # Test with an empty string
        result = s_fmt('', 3, 3)
        self.assertEqual(result, '***')  # Should return len(s) + 3 asterisks = 0 + 3 = 3

        # Test with custom show_beginning parameter
        result = s_fmt('abcdefghijklmnop', 5, 2)
        self.assertEqual(result, 'abcde***op')

        # Test with custom show_ending parameter
        result = s_fmt('abcdefghijklmnopq', 2, 5)
        self.assertEqual(result, 'ab***mnopq')

        # Test with custom show_beginning and show_ending parameters
        result = s_fmt('thisisaverylongstringexample', 4, 4)
        self.assertEqual(result, 'this***mple')

        # Test with minimum values for show_beginning and show_ending
        result = s_fmt('1234567890', 1, 1)
        self.assertEqual(result, '1***0')

        # Test with single character string
        result = s_fmt('a', 1, 1)
        self.assertEqual(result, '****')  # Should return len(s) + 3 asterisks = 1 + 3 = 4

        # Test when show_beginning and show_ending are zero
        result = s_fmt('verylongstring', 0, 0)
        self.assertEqual(result, '***')

        # Test with a long string using default parameters
        long_string = 'A' * 20
        result = s_fmt(long_string)
        self.assertEqual(result, 'AAA***AAA')

    def test_format_number(self):
        """Unified test for format_number function covering all cases."""
        # Test formatting with Decimal values
        self.assertEqual(format_number(Decimal('123.456')), '123.456')
        self.assertEqual(format_number(Decimal('123.450')), '123.45')
        self.assertEqual(format_number(Decimal('123.000')), '123')
        self.assertEqual(format_number(Decimal('0.000')), '0')
        self.assertEqual(format_number(Decimal('123.456789012345')), '123.456789012345')
        self.assertEqual(format_number(Decimal('-123.456')), '-123.456')
        self.assertEqual(format_number(Decimal('-123.450')), '-123.45')
        self.assertEqual(format_number(Decimal('-123.000')), '-123')

        # Test formatting with float values (using string representation to avoid precision issues)
        self.assertEqual(format_number(123.456), '123.456')
        self.assertEqual(format_number(123.450), '123.45')
        self.assertEqual(format_number(123.000), '123')
        self.assertEqual(format_number(25.1), '25.1')
        self.assertEqual(format_number(0.000), '0')
        self.assertEqual(format_number(-25.1), '-25.1')

        # Test formatting with integer values
        self.assertEqual(format_number(123), '123')
        self.assertEqual(format_number(0), '0')
        self.assertEqual(format_number(-12), '-12')

        # Test formatting with None value
        self.assertIsNone(format_number(None))

        # Test formatting with custom precision
        self.assertEqual(format_number(Decimal('123.456789'), precision=2), '123.46')
        self.assertEqual(format_number(Decimal('123.456789'), precision=4), '123.4568')
        self.assertEqual(format_number(Decimal('123.456789'), precision=6), '123.456789')
        self.assertEqual(format_number(Decimal('123.456789'), precision=0), '123')

        # Test edge cases
        # Test very small numbers
        self.assertEqual(format_number(Decimal('0.0000001')), '0.0000001')
        self.assertEqual(format_number(Decimal('0.0000000')), '0')

        # Test very large numbers
        self.assertEqual(format_number(Decimal('123456789.123456789')), '123456789.123456789')


if __name__ == "__main__":
    unittest.main()
