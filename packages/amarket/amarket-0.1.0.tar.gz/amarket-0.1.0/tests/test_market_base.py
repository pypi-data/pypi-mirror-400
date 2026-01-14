import unittest
from decimal import (
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_FLOOR,
    ROUND_HALF_DOWN,
    ROUND_HALF_UP,
    ROUND_UP,
    Decimal,
)
from time import time
from typing import Iterable, Optional
from unittest.mock import Mock

from amarket.base import MarketBase
from amarket.constants import TIMEFRAMES
from test_utils import check_primitive_types


class Market(MarketBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exchange = 'some_exchange_1'
        self._market_type = "spot"
        self._base_ticker = "BTC"
        self._quote_ticker = "USDT"
        self._price_precision = 2
        self._lot_precision = 4

    def fetch_price(self, symbol: Optional[str] = None) -> Decimal: pass
    def fetch_ohlc(self, timeframe: str, symbol: Optional[str] = None, columns: Optional[Iterable[str]] = None,
                   index_by_date: bool = True, limit: int = 500) -> Iterable[dict]: pass


class AnotherMarket(MarketBase):
    def fetch_price(self, symbol: Optional[str] = None) -> Decimal: pass
    def fetch_ohlc(self, timeframe: str, symbol: Optional[str] = None, columns: Optional[Iterable[str]] = None,
                   index_by_date: bool = True, limit: int = 500) -> Iterable[dict]: pass


class TestMarketBase(unittest.TestCase):
    def setUp(self):
        # Clean up all singleton instances as they may exist from previous tests
        MarketBase._singleton_instances = {}

        # Create Market object
        self.symbol = "BTCUSDT"
        self.market = Market(self.symbol)

        # Create mocked Ohlc object
        self.timeframe = '1h'
        self.ohlc = Mock(timeframe=self.timeframe, need_update=True, updated=0)

    def test_singleton(self):
        # Test singleton same credentials
        instance1 = Market(self.symbol)
        instance2 = Market(self.symbol)
        self.assertIs(instance1, instance2)
        self.assertEqual(1, len(MarketBase._singleton_instances))
        self.assertEqual(1, instance1.n_instances)
        self.assertEqual(1, instance2.n_instances)

        # Test singleton different symbol
        instance3 = Market('ETHUSDT')
        self.assertIs(instance1, instance2)
        self.assertIsNot(instance1, instance3)
        self.assertIsNot(instance2, instance3)
        self.assertEqual(2, len(MarketBase._singleton_instances))
        self.assertEqual(2, instance1.n_instances)
        self.assertEqual(2, instance2.n_instances)
        self.assertEqual(2, instance3.n_instances)

        # Test tbe singleton logic works right in case of another child
        instance4 = AnotherMarket(self.symbol)
        self.assertIs(instance1, instance2)
        self.assertIsNot(instance3, instance1)
        self.assertIsNot(instance3, instance2)
        self.assertIsNot(instance4, instance1)
        self.assertIsNot(instance4, instance2)
        self.assertIsNot(instance4, instance3)
        self.assertEqual(3, len(MarketBase._singleton_instances))
        self.assertEqual(2, instance1.n_instances)
        self.assertEqual(2, instance2.n_instances)
        self.assertEqual(2, instance3.n_instances)
        self.assertEqual(1, instance4.n_instances)

    def test_initialization(self):
        self.assertGreater(self.market.initialized, 0)
        self.assertEqual(self.market.base_ticker, "BTC")
        self.assertEqual(self.market.quote_ticker, "USDT")
        self.assertEqual(self.market.exchange, 'some_exchange_1')
        self.assertEqual(self.market.market_type, 'spot')
        self.assertEqual(self.market.symbol, "BTCUSDT")
        self.assertEqual(self.market.price, Decimal(0))
        self.assertEqual(self.market.price_time, 0)
        self.assertIsInstance(self.market._ohlc, dict)
        self.assertDictEqual(self.market._ohlc, {})
        self.assertIsInstance(self.market.price_precision, int)
        self.assertEqual(self.market.price_precision, 2)
        self.assertIsInstance(self.market.price_step, Decimal)
        self.assertEqual(self.market.price_step, Decimal(0))
        self.assertIsInstance(self.market.lot_precision, int)
        self.assertEqual(self.market.lot_precision, 4)
        self.assertIsInstance(self.market.lot_step, Decimal)
        self.assertEqual(self.market.lot_step, Decimal(0))
        self.assertIsInstance(self.market.min_order_base, Decimal)
        self.assertEqual(self.market.min_order_base, Decimal(0))
        self.assertIsInstance(self.market.min_order_quote, Decimal)
        self.assertEqual(self.market.min_order_quote, Decimal(0))
        self.assertDictEqual(self.market.provider_data, {})

        # Try to get the market using get_market
        market = MarketBase.get_market(self.market.exchange, self.market.market_type, self.market.symbol)
        self.assertIsNotNone(market)
        self.assertIs(self.market, market)  # Should return the same instance

        # Test market initialization without child __init__()
        another = AnotherMarket(self.symbol)
        self.assertEqual(another.base_ticker, "")
        self.assertEqual(another.quote_ticker, "")
        self.assertEqual(another.exchange, '')
        self.assertEqual(another.market_type, '')
        self.assertIsNot(another, market)

        # Test .get_market() not found not existing market
        market = MarketBase.get_market("different_exchange", self.market.market_type, self.market.symbol)
        self.assertIsNone(market)

        # Try to get the market using lowercase symbol
        market = MarketBase.get_market(self.market.exchange, self.market.market_type, "btcusdt")
        self.assertIsNotNone(market)
        self.assertIs(self.market, market)

        # Try to get instance via another child class
        market = AnotherMarket.get_market(self.market.exchange, self.market.market_type, self.market.symbol)
        self.assertIsNotNone(market)
        self.assertIs(self.market, market)

        # Test access to timeframes
        self.assertEqual(0, len(self.market))
        for tf in TIMEFRAMES:
            self.assertNotIn(tf, self.market)
            self.assertNotIn(tf, self.market._ohlc)
        self.assertEqual(0, len(self.market))  # check the length after iterating

        # Test .min_order_base dynamic property recalculation
        self.market._min_order_quote = Decimal(5)
        self.market._price = Decimal(100000)
        self.market._lot_precision = 5
        self.assertEqual(self.market.min_order_quote, Decimal(5))
        self.assertEqual(self.market.price, Decimal(100000))
        self.assertEqual(self.market.min_order_base, Decimal(5)/Decimal(100000))
        self.assertEqual(self.market._min_order_base, Decimal(5)/Decimal(100000))
        self.market._min_order_base = Decimal(0)
        self.assertEqual(self.market._min_order_base, 0)
        self.assertEqual(self.market.min_order_base, Decimal(5)/Decimal(100000))

    # @patch('amarket.interfaces.i_ohlc.Ohlc')
    def test_access_timeframes(self):
        with self.assertRaises(ValueError):
            self.market['some_not_timeframe_key'] = self.ohlc

        with self.assertRaises(KeyError):
            _ = self.market['some_not_timeframe_key']

        with self.assertRaises(KeyError):
            _ = self.market[self.timeframe]

        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            self.market[self.timeframe] = None

        with self.assertRaises(ValueError):
            self.market['1s'] = self.ohlc  # check wrong timeframe assignment

        self.market._ohlc[self.timeframe] = self.ohlc  # direct OHLC data assignment, for testing purposes only!

        # Check the instance after adding valid OHLC data
        self.assertIn(self.timeframe, self.market)
        self.assertIn(self.timeframe, self.market._ohlc)
        self.assertEqual(1, len(self.market))
        self.assertEqual(1, len(self.market._ohlc))
        self.assertIsInstance(self.market._ohlc, dict)

        # Test iterations over existing timeframes
        cnt = 0
        for _ in self.market:
            self.assertIn(_, TIMEFRAMES)
            cnt += 1
        self.assertEqual(cnt, len(self.market))
        self.assertEqual(cnt, len(self.market._ohlc))

        # Check the OHLC storage is different for another market instance
        another_market = AnotherMarket(self.symbol)
        self.assertIsInstance(self.market._ohlc, dict)
        self.assertNotEqual(self.market._ohlc, another_market._ohlc)
        self.assertIsNot(self.market._ohlc, another_market._ohlc)
        self.assertIsNot(self.market, another_market)
        self.assertEqual(1, len(self.market))
        self.assertEqual(0, len(another_market))

        # Check the instances after adding new valid OHLC data to another market
        another_market._ohlc[self.timeframe] = Mock(timeframe=self.timeframe)
        self.assertNotEqual(self.market._ohlc, another_market._ohlc)
        self.assertIsNot(self.market._ohlc, another_market._ohlc)
        self.assertIsNot(self.market, another_market)
        self.assertEqual(1, len(self.market))
        self.assertEqual(1, len(another_market))

    def test_update(self):
        self.market._ohlc[self.timeframe] = self.ohlc
        self.market._ohlc["1d"] = Mock(timeframe='1d', need_update=True, updated=0)
        self.assertTrue(self.market[self.timeframe].need_update)
        self.assertTrue(self.market["1d"].need_update)

        # Test force update
        self.market[self.timeframe].need_update = False
        self.market["1d"].need_update = False
        self.market.update(force=[self.timeframe, "1d"])
        self.assertTrue(self.market._ohlc[self.timeframe].need_update)

    def test_update_min_fetch_interval(self):
        """Test the min_fetch_interval parameter in update method"""
        # Mock the time and fetch methods
        self.market._ohlc[self.timeframe] = self.ohlc

        # Test that min_fetch_interval defaults to 0 when not provided
        self.market.fetch_price = Mock(return_value=Decimal('1000.0'))
        self.market.fetch_ohlc = Mock()

        # Generate the function arguments to test
        values = (None, 0, 0.5, True, False, -1000, "invalid", 1000, "1000", 400, 1)
        arguments = ([{'price': True}] +
                     [{'price': True, 'min_fetch_interval': _} for _ in values] +
                     [{'force': [self.timeframe]}] +
                     [{'force': [self.timeframe], 'min_fetch_interval': _} for _ in values])

        # Test with initial price_time and ohlc.updated (both are zero) - always fetch
        for kwargs in arguments:
            self.market.update(**kwargs)
            self.market.fetch_price.assert_called_once()
            self.market.fetch_ohlc.assert_called_once()
            self.market.fetch_price.reset_mock()
            self.market.fetch_ohlc.reset_mock()
            self.market._price_time, self.market._ohlc_time = 0, 0

        # Set price_time and ohlc.updated to current time minus 10 seconds and test that update happens - always fetch
        current_time = int(time() * 1000) - 10000
        self.market._price_time, self.market._ohlc_time = current_time, current_time
        for kwargs in arguments:
            self.market.update(**kwargs)
            self.market.fetch_price.assert_called_once()
            self.market.fetch_ohlc.assert_called_once()
            self.market.fetch_price.reset_mock()
            self.market.fetch_ohlc.reset_mock()
            self.market._price_time, self.market._ohlc_time = current_time, current_time

        # Set price_time and ohlc.updated to current time and test that update happens only when:
        # min_fetch_interval is explicitly disabled (None or 0)
        current_time = int(time() * 1000)
        self.market._price_time, self.market._ohlc_time = current_time, current_time
        for kwargs in arguments:
            self.market.update(**kwargs)
            if 'min_fetch_interval' in kwargs and kwargs['min_fetch_interval'] in (None, 0):
                self.market.fetch_price.assert_called_once()
                self.market.fetch_ohlc.assert_called_once()
                self.market.fetch_price.reset_mock()
                self.market.fetch_ohlc.reset_mock()
                self.market._price_time, self.market._ohlc_time = current_time, current_time
            else:
                self.market.fetch_price.assert_not_called()
                self.market.fetch_ohlc.assert_not_called()

        # Set price_time and ohlc.updated to current time - 0.5 seconds and test that update happens only when:
        # min_fetch_interval is integer and explicitly less than 500 OR explicitly disabled (None or 0)
        current_time = int(time() * 1000) - 500
        self.market._price_time, self.market._ohlc_time = current_time, current_time
        for kwargs in arguments:
            self.market.update(**kwargs)
            in_kwargs = 'min_fetch_interval' in kwargs
            disabled = in_kwargs and kwargs['min_fetch_interval'] in (None, 0)
            is_bool = in_kwargs and kwargs['min_fetch_interval'] in (False, True)
            is_int = in_kwargs and not is_bool and isinstance(kwargs['min_fetch_interval'], int)
            is_low_positive_int = is_int and 500 > kwargs['min_fetch_interval'] > 0
            if is_low_positive_int or disabled:
                self.market.fetch_price.assert_called_once()
                self.market.fetch_ohlc.assert_called_once()
                self.market.fetch_price.reset_mock()
                self.market.fetch_ohlc.reset_mock()
                self.market._price_time, self.market._ohlc_time = current_time, current_time
            else:
                self.market.fetch_price.assert_not_called()
                self.market.fetch_ohlc.assert_not_called()

    def test_validate(self):
        # Test Market passes validation with correct properties
        result = self.market.validate()
        self.assertTrue(result["success"])
        self.assertEqual(len(result["errors"]), 0)

        # Test validation fails with invalid properties
        invalid_props = {'exchange': '', 'market_type': "", 'symbol': "", 'base_ticker': "", 'quote_ticker': "",
                         'price_precision': -1, 'lot_precision': -1}
        for prop, value in invalid_props.items():
            init_value = getattr(self.market, f"_{prop}")
            setattr(self.market, f"_{prop}", value)
            result = self.market.validate()
            self.assertFalse(result["success"])
            self.assertIn(f"Invalid {prop}", result["errors"][0])
            self.assertEqual(len(result['errors']), 1)
            setattr(self.market, f"_{prop}", init_value)  # restore

    def test_to_dict(self):
        expected_dict = {
            "exchange": 'some_exchange_1', "market_type": "spot", "symbol": "BTCUSDT",
            "base_ticker": "BTC", "quote_ticker": "USDT", "price": Decimal(0), "price_time": 0, "price_precision": 2,
            "price_step": Decimal(0), "lot_precision": 4, "lot_step": Decimal(0), "min_order_base": Decimal(0),
            "min_order_quote": Decimal(0), "provider_data": {}, "timeframes": []}

        result = self.market.to_dict()
        self.assertEqual(result, expected_dict)

        # Test with modified values
        self.market._price = Decimal('10000')
        self.market._price_time = int(time() * 1000)
        self.market._ohlc['1h'] = Mock(timeframe='1h', need_update=True, updated=0)

        expected_dict['price'] = self.market._price
        expected_dict['price_time'] = self.market._price_time
        expected_dict['timeframes'] = ['1h']

        result = self.market.to_dict()
        self.assertEqual(result, expected_dict)
        check_primitive_types(result)

    def test_round_lot(self):
        """Test the round_lot method"""
        # Test with different lot steps and values using default rounding (ROUND_HALF_EVEN)
        test_cases = [
            (Decimal('0.0001'), Decimal('0.12345'), Decimal('0.1234')),  # Normal case, precision=4
            (Decimal('0.0001'), Decimal('0.12349'), Decimal('0.1235')),  # Round up, precision=4
            (Decimal('0.0001'), Decimal('0.12341'), Decimal('0.1234')),  # Round down, precision=4
            (Decimal('0.0001'), Decimal('0.0'), Decimal('0.0')),        # Zero value, precision=4
            (Decimal('0.0001'), Decimal('1.0'), Decimal('1.0')),        # Whole number, precision=4
            (Decimal('0.000001'), Decimal('0.1234567'), Decimal('0.123457')),  # Higher precision=6, rounds to even
            (Decimal('1'), Decimal('1.7'), Decimal('2.0')),         # Zero precision should round to nearest integer
        ]

        for lot_step, value, expected in test_cases:
            self.market._lot_step = lot_step
            result = self.market.round_lot(value)
            self.assertEqual(result, expected, f"Failed for lot_step={lot_step}, value={value}")

        # Test different rounding modes with midpoint values
        midpoint_value = Decimal('0.12345')  # Will round to 0.1234 or 0.1235 depending on rounding mode
        self.market._lot_step = Decimal('0.0001')

        test_rounding_cases = [
            (None, 'ROUND_HALF_EVEN', Decimal('0.1234')),  # Default: rounds to even (4)
            (ROUND_UP, 'ROUND_UP', Decimal('0.1235')),
            (ROUND_DOWN, 'ROUND_DOWN', Decimal('0.1234')),
            (ROUND_HALF_UP, 'ROUND_HALF_UP', Decimal('0.1235')),  # Rounds away from zero on tie
            (ROUND_HALF_DOWN, 'ROUND_HALF_DOWN', Decimal('0.1234')),  # Rounds toward zero on tie
            (ROUND_CEILING, 'ROUND_CEILING', Decimal('0.1235')),
            (ROUND_FLOOR, 'ROUND_FLOOR', Decimal('0.1234')),
        ]

        for rounding, description, expected in test_rounding_cases:
            result = self.market.round_lot(midpoint_value, rounding=rounding)
            self.assertEqual(result, expected, f"Failed for rounding={description}, value={midpoint_value}")

    def test_round_price(self):
        """Test the round_price method"""
        # Test with different price steps and values using default rounding (ROUND_HALF_EVEN)
        test_cases = [
            (Decimal('0.01'), Decimal('100.1234'), Decimal('100.12')),  # Normal case, precision=2
            (Decimal('0.01'), Decimal('100.1235'), Decimal('100.12')),  # Round down at midpoint, precision=2
            (Decimal('0.01'), Decimal('100.1285'), Decimal('100.13')),  # Round up, precision=2
            (Decimal('0.01'), Decimal('100.0'), Decimal('100.00')),     # Zero value, precision=2
            (Decimal('0.01'), Decimal('101.0'), Decimal('101.00')),     # Whole number, precision=2
            (Decimal('0.0001'), Decimal('99.99995'), Decimal('100.0000')),  # Higher precision=4, rounds to even
            (Decimal('1'), Decimal('99.6'), Decimal('100.0')),        # Zero precision should round to nearest integer
        ]

        for price_step, value, expected in test_cases:
            self.market._price_step = price_step
            result = self.market.round_price(value)
            self.assertEqual(result, expected, f"Failed for price_step={price_step}, value={value}")

        # Test different rounding modes with midpoint values
        midpoint_value = Decimal('100.125')  # Will round to 100.12 or 100.13 depending on rounding mode
        self.market._price_step = Decimal('0.01')

        test_rounding_cases = [
            (None, 'ROUND_HALF_EVEN', Decimal('100.12')),  # Default: rounds to even (2)
            (ROUND_UP, 'ROUND_UP', Decimal('100.13')),
            (ROUND_DOWN, 'ROUND_DOWN', Decimal('100.12')),
            (ROUND_HALF_UP, 'ROUND_HALF_UP', Decimal('100.13')),  # Rounds away from zero on tie
            (ROUND_HALF_DOWN, 'ROUND_HALF_DOWN', Decimal('100.12')),  # Rounds toward zero on tie
            (ROUND_CEILING, 'ROUND_CEILING', Decimal('100.13')),
            (ROUND_FLOOR, 'ROUND_FLOOR', Decimal('100.12')),
        ]

        for rounding, description, expected in test_rounding_cases:
            result = self.market.round_price(midpoint_value, rounding=rounding)
            self.assertEqual(result, expected, f"Failed for rounding={description}, value={midpoint_value}")


if __name__ == "__main__":
    unittest.main()
