import unittest

import pandas as pd
from amarket.ohlc import cooldown, ohlc_cleanup
from amarket.test_data import DATAFRAMES


class TestOhlcFunctions(unittest.TestCase):
    def setUp(self):
        self.dataframes = DATAFRAMES

    def test_cooldown(self):
        # Test cases dictionary where key is input, value is a list of test cases
        data = {
            (): [  # test empty series
                (0, [])
            ],

            (0, 0, 0): [  # no signals case
                (1, (0, 0, 0)),
                (2, (0, 0, 0)),
            ],

            (1, 0, 0): [  # single signal
                (1, (1, 0, 0)),
                (2, (1, 0, 0)),
            ],

            (1, 1, 0): [  # multiple signals within cooldown
                (1, (1, 0, 0)),
                (2, (1, 0, 0)),
            ],

            (1, 0, 1): [  # multiple signals outside cooldown
                (1, (1, 0, 1)),
                (2, (1, 0, 0))
            ],

            (1, 0, 0, 0, 0, 1): [  # large cooldown
                (4, (1, 0, 0, 0, 0, 1))
            ],

            (1, 0, 1, 1, 0, 1): [
                (1, [1, 0, 1, 0, 0, 1]),
                (2, [1, 0, 0, 1, 0, 0]),
                (3, [1, 0, 0, 0, 0, 1]),
            ],

            (1, 1, 1, 1, 1, 1): [
                (1, [1, 0, 1, 0, 1, 0]),
                (2, [1, 0, 0, 1, 0, 0]),
            ],

            (1, 1, 1, -1, -1, -1, 0, 0, 0): [
                (2, [1, 0, 0, -1, 0, 0, 0, 0, 0]),
            ],

            (-1, 0, 1, -1, 0, 1, -1, 0, 1): [
                (2, [-1, 0, 1, -1, 0, 1, -1, 0, 1]),
                (3, [-1, 0, 1, 0, 0, 0, -1, 0, 1]),
            ],

            (1, -1, 1, -1, 1, -1, 1, -1, 1): [
                (5, [1, -1, 0, 0, 0, 0, 1, -1, 0])
            ],
        }

        for signal, test_cases in data.items():
            # First, test periods lower or equal to 0
            for period in range(-3, 1):
                self.assertEqual(pd.Series(signal).tolist(), cooldown(pd.Series(signal), period=period).tolist(),
                                 msg=f'StrategyBase.cooldown({signal}, period={period}) works wrong!')

            # Then, test with payload
            for period, expected in test_cases:
                inp = pd.Series(signal).astype(int)
                exp = pd.Series(expected).astype(int)
                self.assertEqual(exp.tolist(), cooldown(inp, period=period).tolist(),
                                 msg=f'StrategyBase.cooldown({signal}, period={period}) works wrong!')
                self.assertIsNone(pd.testing.assert_series_equal(exp, cooldown(inp, period=period)))

    def test_ohlc_cleanup(self):
        symbol, timeframe = 'BTCUSDT', '1d'
        df_key = f"{symbol}_{timeframe}"
        df = self.dataframes[df_key].copy()
        df.loc[len(df)] = [pd.to_datetime('2022-12-30', utc=True), 1, 2, 3, 4, 5]
        df.loc[len(df)] = [pd.to_datetime('2022-12-30', utc=True), 1, 2, 3, 4, 5]  # duplicate row
        df.loc[len(df)] = [pd.to_datetime('2021-01-01', utc=True), 0, 0, 0, 0, 0]  # zero volume row
        dataframe, _ = ohlc_cleanup(df, timeframe, date_index=True)

        deltas = dataframe.index.diff().dropna()
        self.assertEqual(len(dataframe), len(self.dataframes[df_key]) + 2)
        self.assertTrue(dataframe.index.is_monotonic_increasing, msg="Chronological order failed!")
        self.assertEqual(pd.Timedelta(timeframe), dataframe.index[1] - dataframe.index[0])
        self.assertTrue((deltas == (dataframe.index[1] - dataframe.index[0])).all())
        self.assertTrue((deltas == pd.Timedelta(timeframe)).all())
        self.assertTrue((dataframe.loc['2022-12-31'] == [1, 2, 3, 4, 5]).all(), msg="Backfill failed!")
        self.assertLessEqual(dataframe.duplicated().sum(), 1, msg="There is duplicated rows!")


if __name__ == '__main__':
    unittest.main()
