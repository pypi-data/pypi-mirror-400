import unittest
from unittest.mock import patch

import pandas as pd
from amarket.constants import OHLC_COLUMNS_VOLUME
from amarket.ohlc import Ohlc


class TestOhlcBase(unittest.TestCase):
    def setUp(self):
        self.timeframe = "1h"
        self.max_length = 5
        self.columns = ["date", "open", "high", "low", "close", "volume"]
        self.data = [[
            ["2025-05-05T12:00:00Z", 100.0, 105.0, 95.0, 102.0, 1000.0],
            ["2025-05-05T13:00:00Z", 102.0, 107.0, 101.0, 104.0, 1200.0]
        ], [
            ["2025-05-05T12:00:00Z", 100.0, 105.0, 95.0, 102.0, 1000.0],
            ["2025-05-05T13:00:00Z", 102.0, 107.0, 101.0, 104.0, 1200.0],
            ["2025-05-05T14:00:00Z", 104.1, 110.7, 100.0, 100.0, 123.0]
        ], [
            ["2025-05-05T15:00:00Z", 100.0, 109.0, 91.0, 98.0, 1230.0]
        ]]
        self.ohlc = Ohlc(self.timeframe, max_length=self.max_length)

    def _data(self, idx: int) -> pd.DataFrame:
        """Construct dataframe from the dummy data"""
        data = pd.DataFrame(self.data[idx], columns=self.columns)
        data['date'] = pd.to_datetime(data['date'], utc=True)
        data = data.set_index('date')
        return data

    def test_properties(self):
        self.assertEqual(self.ohlc.timeframe, self.timeframe)
        self.assertEqual(self.ohlc.timeframe_seconds, 3600)  # 1h in seconds
        self.assertIsInstance(self.ohlc.raw_data, pd.DataFrame)
        self.assertTrue(self.ohlc.raw_data.empty)
        self.assertIsInstance(self.ohlc.data, pd.DataFrame)
        self.assertTrue(self.ohlc.data.empty)
        self.assertEqual(len(self.ohlc.data), 0)
        self.assertEqual(self.ohlc.n, 0)
        self.assertIsInstance(self.ohlc.updated, int)
        self.assertEqual(self.ohlc.updated, 0)
        self.assertIsNone(self.ohlc.current)
        self.assertIsNone(self.ohlc.last)
        self.assertTrue(self.ohlc._need_update)
        self.assertIsInstance(self.max_length, int)
        self.assertIsInstance(self.ohlc.columns, list)
        self.assertListEqual([_ for _ in OHLC_COLUMNS_VOLUME], self.ohlc.columns)
        self.assertListEqual([_ for _ in self.ohlc.raw_data.columns], self.ohlc.columns)
        self.assertTrue(self.ohlc.need_update)
        self.ohlc.need_update = False
        self.assertFalse(self.ohlc.need_update)

    def test_check_with_empty_data(self):
        self.ohlc._check()
        self.assertIsInstance(self.ohlc.raw_data, pd.DataFrame)
        self.assertTrue(self.ohlc.raw_data.empty)
        self.assertEqual(len(self.ohlc.data), 0)
        self.assertEqual(self.ohlc.n, 0)
        self.assertIsNone(self.ohlc._current)
        self.assertIsNone(self.ohlc._last)
        self.assertTrue(self.ohlc._need_update)

    def test_update_adds_data(self):
        for i in range(3):
            # Update Ohlc instance with new candles
            old_updated = self.ohlc.updated  # old updated timestamp
            self.ohlc.update(self._data(i))
            self.assertGreater(self.ohlc.updated, old_updated)
            self.assertTupleEqual((2+i, 5), self.ohlc.raw_data.shape, f'Raw DataFrame Shape not match on {i} update!')
            self.assertTupleEqual((2+i, 5), self.ohlc.data.shape, f'DataFrame Shape not match on {i} update!')
            self.assertTrue(self.ohlc._need_update)  # always true, because we update now, and the test data too old

            # Check first row in DataFrame
            self.assertEqual(self.ohlc.raw_data.index[0], pd.Timestamp("2025-05-05T12:00:00Z"))
            self.assertEqual(self.ohlc.raw_data.iloc[0]["open"], 100.0)
            self.assertEqual(self.ohlc.raw_data.iloc[0]["high"], 105.0)
            self.assertEqual(self.ohlc.raw_data.iloc[0]["low"], 95.0)
            self.assertEqual(self.ohlc.raw_data.iloc[0]["close"], 102.0)
            self.assertEqual(self.ohlc.raw_data.iloc[0]["volume"], 1000.0)

            # Check second row in DataFrame
            self.assertEqual(self.ohlc.raw_data.index[1], pd.Timestamp("2025-05-05T13:00:00Z"))
            self.assertEqual(self.ohlc.raw_data.iloc[1]["open"], 102.0)
            self.assertEqual(self.ohlc.raw_data.iloc[1]["high"], 107.0)
            self.assertEqual(self.ohlc.raw_data.iloc[1]["low"], 101.0)
            self.assertEqual(self.ohlc.raw_data.iloc[1]["close"], 104.0)
            self.assertEqual(self.ohlc.raw_data.iloc[1]["volume"], 1200.0)

        else:

            # Check third row in DataFrame
            self.assertEqual(self.ohlc.raw_data.index[2], pd.Timestamp("2025-05-05T14:00:00Z"))
            self.assertEqual(self.ohlc.raw_data.iloc[2]["open"], 104.1)
            self.assertEqual(self.ohlc.raw_data.iloc[2]["high"], 110.7)
            self.assertEqual(self.ohlc.raw_data.iloc[2]["low"], 100.0)
            self.assertEqual(self.ohlc.raw_data.iloc[2]["close"], 100.0)
            self.assertEqual(self.ohlc.raw_data.iloc[2]["volume"], 123.0)

            # Check fourth row in DataFrame
            self.assertEqual(self.ohlc.raw_data.index[3], pd.Timestamp("2025-05-05T15:00:00Z"))
            self.assertEqual(self.ohlc.raw_data.iloc[3]["open"], 100.0)
            self.assertEqual(self.ohlc.raw_data.iloc[3]["high"], 109.0)
            self.assertEqual(self.ohlc.raw_data.iloc[3]["low"], 91.0)
            self.assertEqual(self.ohlc.raw_data.iloc[3]["close"], 98.0)
            self.assertEqual(self.ohlc.raw_data.iloc[3]["volume"], 1230.0)

    def test_check_with_current_time_before_current_candle_close(self):
        # Update OHLC data and check main properties after
        self.ohlc.update(self._data(0))
        self.assertEqual(2, self.ohlc.n)
        self.assertTrue(self.ohlc._need_update)  # always true, because we update now, and the test data too old

        # now call ._check() explicitly with mocked time and check state after the call
        with patch('pandas.Timestamp.utcnow', return_value=pd.Timestamp("2025-05-05T13:30:00Z")):
            self.ohlc.need_update = False  # reset the flag to make following tests pass
            self.ohlc._check()

        # note that we need to access to private attributes after ._check() as properties call _check() with actual time
        self.assertFalse(self.ohlc._need_update)
        self.assertEqual(2, self.ohlc.n)
        self.assertIsInstance(self.ohlc._current, pd.Series)
        self.assertIsInstance(self.ohlc._last, pd.Series)
        self.assertTrue(self.ohlc._current.equals(self.ohlc._raw_data.iloc[-1]))
        self.assertTrue(self.ohlc._last.equals(self.ohlc._raw_data.iloc[-2]))
        self.assertFalse(self.ohlc._need_update)

    def test_check_with_current_time_after_or_equal(self):
        dates = [
            "2025-05-05T14:00:00Z",  # _check() called exact the moment new candle must appear
            "2025-05-05T14:01:00Z",  # _check() called after the moment new candle must appear
        ]
        for date in dates:
            # Update OHLC data and check main properties
            self.ohlc.update(self._data(0))
            self.assertEqual(2, self.ohlc.n)
            self.assertEqual(2, len(self.ohlc._raw_data))
            self.assertTrue(self.ohlc._need_update)  # always true, because we update now, and the test data too old

            # now call ._check() explicitly with mocked time and check state after the call
            with patch('pandas.Timestamp.utcnow', return_value=pd.Timestamp(date)):
                self.ohlc._check()

            # note that we need to access to private attributes because properties will call _check() with actual time
            self.assertTrue(self.ohlc._need_update)
            self.assertEqual(3, self.ohlc.n)
            self.assertEqual(3, len(self.ohlc._raw_data))
            self.assertIsInstance(self.ohlc._current, pd.Series)
            self.assertIsInstance(self.ohlc._last, pd.Series)
            self.assertEqual(pd.Timestamp("2025-05-05T13:00:00Z"), self.ohlc._last.name)
            self.assertEqual(pd.Timestamp("2025-05-05T14:00:00Z"), self.ohlc._current.name)
            self.assertEqual(0, self.ohlc._current['volume'])
            self.assertTrue(self.ohlc._current.equals(self.ohlc._raw_data.iloc[-1]))
            self.assertTrue(self.ohlc._last.equals(self.ohlc._raw_data.iloc[-2]))


if __name__ == '__main__':
    unittest.main()
