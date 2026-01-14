#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for Featurizer class"""
import unittest

import numpy as np
import pandas as pd
from amarket.ohlc import Featurizer
from amarket.test_data import DATAFRAMES


class TestFeaturizer(unittest.TestCase):
    def setUp(self):
        self.data = DATAFRAMES['BTCUSDT_1d']
        self.all_features = {'net_return', 'log_return', 'gross_return', 'gross_return_from_log_return', 'atr', 'natr',
                             'prev', 'atrp', 'rsi', 'sma', 'diff', 'div', 'mult', 'marubozu', 'diff_extrema', 'macd',
                             'wf', 'future', 'ma_cross'}
        self.featurizer = Featurizer(pd.DataFrame(self.data))

    def test_initialization(self):
        self.assertTrue(hasattr(self.featurizer, 'original'))
        self.assertTrue(hasattr(self.featurizer, 'applied'))
        self.assertTrue(hasattr(self.featurizer, 'known_features'))
        self.assertTrue(hasattr(self.featurizer, 'cols'))
        self.assertTrue(hasattr(self.featurizer, 'used'))

        self.assertIsInstance(self.featurizer.original, pd.DataFrame)
        self.assertIsInstance(self.featurizer.applied, pd.DataFrame)
        self.assertIsInstance(self.featurizer.known_features, set)
        self.assertIsInstance(self.featurizer.cols, list)
        self.assertIsInstance(self.featurizer.used, list)

        self.assertGreater(len(self.featurizer.known_features), 0)
        self.assertEqual(len(self.featurizer), len(self.data))
        self.assertListEqual(self.featurizer.cols, [])
        self.assertListEqual(self.featurizer.used, [])

        self.assertTrue(self.featurizer.original.equals(self.featurizer.applied))
        self.assertSetEqual(self.all_features, self.featurizer.get_known_features())
        self.assertSetEqual(self.all_features, self.featurizer.known_features)

    def test_apply_features(self):
        features = (self.featurizer.known_features -
                    {'div', 'mult', 'diff_extrema', 'diff', 'prev', 'future', 'net_return', 'log_return', 'ma_cross'})
        cols, used = self.featurizer.apply_features(['net_return', {'feature': 'log_return', 'use': None}]
                                                    + list(features))
        self.assertIsInstance(cols, list)
        self.assertIsInstance(used, list)
        self.assertGreater(len(cols), len(used))
        self.assertIn('net_return', cols)
        self.assertIn('net_return', used)
        self.assertIn('log_return', cols)
        self.assertNotIn('log_return', used)

    def test_validate(self):
        data = self.data.copy()
        self.featurizer.validate(pd.DataFrame(self.data))  # no exception
        with self.assertRaises(ValueError):  # exception
            del data['close']
            self.featurizer.validate(pd.DataFrame(data))
        with self.assertRaises(ValueError):  # exception
            self.featurizer.validate(pd.DataFrame({"date": [1, 2], "open": [10, 20]}))

    def test_net_return_feature(self):
        feats = ['net_return',
                 {'feature': 'net_return', 'kwargs': {'period': 2}},
                 {'feature': 'net_return', 'kwargs': {'period': 5}},]

        cols, used = self.featurizer.apply_features(feats)
        self.assertListEqual(cols, used)

        period = 1
        column = 'close'
        for f in feats:
            if isinstance(f, dict) and 'kwargs' in f and 'period' in f['kwargs']:
                period = f['kwargs']['period']
                f = f['feature']
            final = self.featurizer.applied.loc[period, column]
            initial = self.featurizer.applied.loc[period - 1, column]
            result = self.featurizer.applied.loc[period, f]
            self.assertAlmostEqual(result, (final-initial)/initial)

    def test_gross_return_features(self):
        self.featurizer.apply_features(['net_return', 'log_return', 'gross_return', 'gross_return_from_log_return'])
        self.assertTrue(np.isclose(self.featurizer.applied['gross_return'],
                                   self.featurizer.applied.gross_return_from_log_return, equal_nan=True).all())
        self.assertIsNone(pd.testing.assert_series_equal(self.featurizer.applied['gross_return'],
                                                         self.featurizer.applied.gross_return_from_log_return,
                                                         check_names=False))

    def test_rsi_feature(self):
        # Reference RSI values from TradingView, obtained manually
        expected_rsi = pd.DataFrame({
            'date': [f"2023-07-0{_}" for _ in range(1, 8)],  # 01-07 Jul, 2023
            'rsi': [66.81, 67, 70.16, 65.29, 62.18, 55.53, 59.01],
        })
        expected_rsi['date'] = pd.to_datetime(expected_rsi['date'], utc=True)
        cols, used = self.featurizer.apply_features(['rsi'])

        self.assertIsNone(pd.testing.assert_frame_equal(
            expected_rsi, self.featurizer.applied[['date'] + cols].iloc[-7:].reset_index(drop=True), atol=0.01))

        cols, used = Featurizer(self.data.iloc[-140:]).apply_features(['rsi'])
        self.assertIsNone(pd.testing.assert_frame_equal(
            expected_rsi, self.featurizer.applied[['date'] + cols].iloc[-7:].reset_index(drop=True), atol=0.01))

    def test_prev_feature(self):
        features = ['rsi', 'prev_rsi_1', 'prev_rsi_7', 'prev_diff_pct(close-sma_14)_1', 'prev_diff_pct(close-sma_14)_7',
                    {'feature': 'sma', 'kwargs': {'period': 14}},
                    {'feature': 'diff', 'args': ['close', 'sma_14']}]
        self.featurizer.apply_features(features)
        self.assertTrue(np.isclose(self.featurizer.applied['rsi'].shift(1),
                                   self.featurizer.applied['prev_rsi_1'], equal_nan=True).all())
        self.assertTrue(np.isclose(self.featurizer.applied['rsi'].shift(7), self.featurizer.applied['prev_rsi_7'],
                                   equal_nan=True).all())
        self.assertTrue(np.isclose(self.featurizer.applied['diff_pct(close-sma_14)'].shift(1),
                                   self.featurizer.applied['prev_diff_pct(close-sma_14)_1'], equal_nan=True).all())
        self.assertTrue(np.isclose(self.featurizer.applied['diff_pct(close-sma_14)'].shift(7),
                                   self.featurizer.applied['prev_diff_pct(close-sma_14)_7'], equal_nan=True).all())

    def test_future_feature(self):
        features = ["log_return", "future_log_return_1"]
        self.featurizer.apply_features(features)
        self.assertTrue(np.isclose(self.featurizer.applied['log_return'].shift(-1),
                                   self.featurizer.applied['future_log_return_1'], equal_nan=True).all())

    def test_sma_feature(self):
        # Reference SMA values from TradingView, obtained manually
        for period, data in {7: [16791.6, 16864.62, 16936.81, 17046.17, 17202.3, 17490.12, 17915.74],
                             14: [17640.2, 17944.11, 18266.45, 18585, 18858.36, 19161.2, 19569.53, 19986.67]}.items():
            cols, used = self.featurizer.apply_features([{'feature': 'sma', 'kwargs': {'period': period}}])
            self.assertListEqual(cols, used)
            name = cols[0]
            start = self.data.iloc[period-1, self.data.columns.get_loc('date')]
            expected_sma = pd.Series(data, name=name, index=pd.date_range(start=start, periods=len(data), freq='1D'))
            sma = self.featurizer.applied.set_index('date', drop=True)[name].loc[start:expected_sma.index.max()]
            self.assertTrue(np.isclose(expected_sma, sma).all())
            self.assertIsNone(pd.testing.assert_series_equal(
                expected_sma, sma, check_freq=False, check_names=False, rtol=0.01))
            self.assertTupleEqual((name,), self.featurizer.feature_sma(period=period))

    def test_diff_feature(self):
        expected_cols = ('diff(close-sma_14)', 'diff_pct(close-sma_14)')
        cols, used = self.featurizer.apply_features([{'feature': 'sma', 'kwargs': {'period': 14}},
                                                     {'feature': 'diff', 'args': ['close', 'sma_14']}])
        self.assertListEqual(['sma_14'] + list(expected_cols), cols)
        self.assertTupleEqual(expected_cols, self.featurizer.feature_diff('close', 'sma_14'))

    def test_div_feature(self):
        expected_cols = ('div(high/close)',)
        cols, used = self.featurizer.apply_features([{'feature': 'div', 'args': ['high', 'close']}])
        self.assertListEqual(list(expected_cols), cols)
        self.assertTupleEqual(expected_cols, self.featurizer.feature_div('high', 'close'))

    def test_mult_feature(self):
        expected_cols = ('mult(high*close)',)
        cols, used = self.featurizer.apply_features([{'feature': 'mult', 'args': ['high', 'close']}])
        self.assertListEqual(list(expected_cols), cols)
        self.assertTupleEqual(expected_cols, self.featurizer.feature_mult('high', 'close'))

    def test_marubozu_feature(self):
        expected_cols = ('marubozu',)
        cols, used = self.featurizer.apply_features(['marubozu'])
        self.assertListEqual(list(expected_cols), cols)
        self.assertTupleEqual(expected_cols, self.featurizer.feature_marubozu())

    def test_wf_feature(self):
        expected_cols = ('wf_bear', 'wf_bull', 'wf_bear_rt', 'wf_bull_rt')
        cols, used = self.featurizer.apply_features(['wf'])
        self.assertListEqual(list(expected_cols), cols)
        self.assertTupleEqual(expected_cols, self.featurizer.feature_wf())
        self.assertTrue(self.featurizer.applied['wf_bear'].iloc[-2:].eq(-1).all())
        self.assertTrue(self.featurizer.applied['wf_bull'].iloc[-2:].eq(-1).all())
        self.assertTrue(self.featurizer.applied['wf_bear_rt'].ne(-1).all())
        self.assertTrue(self.featurizer.applied['wf_bull_rt'].ne(-1).all())

        use = 'wf_bear_rt'
        cols, used = self.featurizer.apply_features([{'feature': 'wf', 'use': use}])
        self.assertListEqual(list(expected_cols), cols)
        self.assertListEqual([use], used)

        use = ['wf_bull_rt', 'wf_bear_rt']
        cols, used = self.featurizer.apply_features([{'feature': 'wf', 'use': use}])
        self.assertListEqual(list(expected_cols), cols)
        self.assertListEqual(use, used)

        cols, used = self.featurizer.apply_features([{'feature': 'wf', 'use': None}])
        self.assertListEqual(list(expected_cols), cols)
        self.assertListEqual([], used)


if __name__ == '__main__':
    unittest.main()
