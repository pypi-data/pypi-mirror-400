#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Union
from unittest.mock import MagicMock

from amarket.base import MarketBase, TradingAccountBase
from amarket.constants import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL
from amarket.interfaces import IOrder
from amarket.local import LocalMarket
from amarket.types import TaggedBalancesDict


class TradingAccount1(TradingAccountBase):
    def get_api_key_permissions(self, update: bool = False) -> dict: pass
    def get_balances(self, update: bool = False) -> TaggedBalancesDict: pass
    def balance(self, ticker: str, tag: str = '') -> Decimal: pass
    def get_open_orders(self, symbol: Optional[str] = None, update: bool = False) -> dict[int, IOrder]: pass
    def is_order_open(self, order: dict | IOrder) -> bool: pass
    def get_orders(self, symbol: str, start_time: Optional[Union[int, float, str]] = None,
                   end_time: Optional[Union[int, float, str]] = None, update: bool = False) -> dict[int, IOrder]: pass

    def normalize_order(self, raw_order_data: dict) -> IOrder: pass

    def get_order(self, symbol: str, order_id: Optional[int] = None, client_order_id: Optional[str] = None,
                  update: bool = False) -> Optional[IOrder]: pass

    def send_order(self, symbol: str, side: SIDE_BUY | SIDE_SELL,
                   order_type: Union[ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, str], **kwargs) -> IOrder:
        super().send_order(symbol, side, order_type, **kwargs)
        order = MagicMock(spec=IOrder)
        order.symbol = symbol
        order.side = side
        order.order_type = order_type
        order.quantity = Decimal(kwargs.get('quantity', 1))
        order.price = Decimal(kwargs.get('price', 10000))  # hardcode this for market orders testing purposes
        order.order_id = 123456789
        return order


class TradingAccount2(TradingAccountBase):
    def get_api_key_permissions(self, update: bool = False) -> dict: pass
    def get_balances(self, update: bool = False) -> TaggedBalancesDict: pass
    def balance(self, ticker: str, tag: str = '') -> Decimal: pass
    def get_open_orders(self, symbol: Optional[str] = None, update: bool = False) -> dict[int, IOrder]: pass
    def is_order_open(self, order: dict | IOrder) -> bool: pass
    def get_orders(self, symbol: str, start_time: Optional[Union[int, float, str]] = None,
                   end_time: Optional[Union[int, float, str]] = None, update: bool = False) -> dict[int, IOrder]: pass

    def normalize_order(self, raw_order_data: dict) -> IOrder: pass

    def get_order(self, symbol: str, order_id: Optional[int] = None, client_order_id: Optional[str] = None,
                  update: bool = False) -> Optional[IOrder]: pass

    def send_order(self, symbol: str, side: SIDE_BUY | SIDE_SELL,
                   order_type: Union[ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, str], **kwargs) -> IOrder: pass


class TestTradingAccountBase(unittest.TestCase):

    def setUp(self):
        # Create credentials
        self.api_key = "test_api_key"
        self.api_secret = "test_api_secret"

        # Reset instances on every test start
        with TradingAccountBase._singleton_lock:
            TradingAccountBase._singleton_instances = {}

        # Create new Trading Account on every test start
        self.trading_account = TradingAccount1(self.api_key, self.api_secret)

    def test_singleton(self):
        # Test singleton same credentials
        instance1, instance2 = self.trading_account, TradingAccount1(self.api_key, self.api_secret)
        self.assertIs(instance1, instance2)
        self.assertEqual(1, instance1.n_instances)
        self.assertEqual(1, instance2.n_instances)
        self.assertEqual(1, len(TradingAccountBase._singleton_instances))
        self.assertEqual(1, len(TradingAccount1._singleton_instances))
        self.assertIs(TradingAccountBase._singleton_instances, TradingAccount1._singleton_instances)

        # Test singleton different symbol and timeframe
        instance3 = TradingAccount1("test_api_key_another", "test_api_secret_another")
        self.assertIs(instance1, instance2)
        self.assertIsNot(instance1, instance3)
        self.assertIsNot(instance2, instance3)
        self.assertEqual(2, len(TradingAccountBase._singleton_instances))
        self.assertEqual(2, len(TradingAccount1._singleton_instances))
        self.assertEqual(2, instance1.n_instances)
        self.assertEqual(2, instance2.n_instances)
        self.assertEqual(2, instance3.n_instances)
        self.assertIs(TradingAccountBase._singleton_instances, TradingAccount1._singleton_instances)
        self.assertIs(TradingAccountBase._singleton_instances, TradingAccount2._singleton_instances)

        # Test tbe singleton logic works right in case of another child
        instance3 = TradingAccount2(self.api_key, self.api_secret)
        self.assertIs(instance1, instance2)
        self.assertIsNot(instance3, instance1)
        self.assertIsNot(instance3, instance2)
        self.assertEqual(3, len(TradingAccountBase._singleton_instances))
        self.assertEqual(3, len(TradingAccount1._singleton_instances))
        self.assertEqual(3, len(TradingAccount2._singleton_instances))
        self.assertEqual(2, instance1.n_instances)
        self.assertEqual(2, instance2.n_instances)
        self.assertEqual(1, instance3.n_instances)
        self.assertIs(TradingAccountBase._singleton_instances, TradingAccount1._singleton_instances)
        self.assertIs(TradingAccountBase._singleton_instances, TradingAccount2._singleton_instances)

    def test_send_order(self):
        # Test valid LIMIT order
        with self.assertRaises(ValueError) as context:
            self.trading_account.send_order("BTCUSDT", SIDE_BUY, ORDER_TYPE_LIMIT)
        self.assertEqual(str(context.exception), "A LIMIT order requires both quantity and price.")

        # Test valid MARKET order with quantity
        with self.assertRaises(ValueError) as context:
            self.trading_account.send_order("BTCUSDT", SIDE_BUY, ORDER_TYPE_MARKET)
        self.assertEqual(str(context.exception), "A MARKET order requires either quantity or quote_quantity.")

        # Testing different orders
        for args, kwargs in [
            (("BTCUSDT", SIDE_SELL, ORDER_TYPE_LIMIT), {'quantity': 1, 'price': 100}),  # valid LIMIT order
            (("BTCUSDT", SIDE_BUY, ORDER_TYPE_MARKET), {'quantity': 1}),  # valid MARKET order with quantity
            (("ETHUSDT", SIDE_BUY, ORDER_TYPE_MARKET), {'quantity': 1}),  # valid MARKET order with quote_quantity
        ]:
            symbol, side, order_type = args
            order = self.trading_account.send_order(symbol, side, order_type, **kwargs)
            self.assertIsInstance(order, IOrder)
            self.assertEqual(order.order_id, 123456789)
            self.assertEqual(order.symbol, symbol)
            self.assertEqual(order.side, side)
            self.assertEqual(order.order_type, order_type)
            self.assertEqual(order.price, Decimal(kwargs.get('price', 10000)))  # Default price for market order
            self.assertIsInstance(order.quantity, Decimal)

    def test_test_order(self):
        # Test valid parameters
        self.assertTrue(self.trading_account.test_order("BTCUSDT", SIDE_BUY, "MARKET"))
        self.assertTrue(self.trading_account.test_order("BTCUSDT", SIDE_SELL, "LIMIT", price="1000"))

        # Test invalid symbol
        with self.assertRaises(ValueError):
            self.trading_account.test_order("", SIDE_BUY, "MARKET")
        with self.assertRaises(ValueError):
            self.trading_account.test_order(None, SIDE_BUY, "MARKET")

        # Test invalid side
        with self.assertRaises(ValueError):
            self.trading_account.test_order("BTCUSDT", 2, "MARKET")

        # Test invalid order type
        with self.assertRaises(ValueError):
            self.trading_account.test_order("BTCUSDT", SIDE_BUY, "STOP")

    def test_api_usage_statistics(self):
        """Test API usage statistics functionality"""
        # Test _update_api_usage with various headers
        test_headers = {
            'x-mbx-used-weight': '10',
            'x-mbx-used-weight-1m': '555',
            'retry-after': '120',
            'date': 'Mon, 01 Jan 2023 00:00:00 GMT'
        }
        self.trading_account._update_api_usage(test_headers, status_code=200)

        # Check that api_usage was updated
        api_usage = self.trading_account.api_usage
        self.assertEqual(api_usage['used_weight'], 10)
        self.assertEqual(api_usage['used_weight_1m'], 555)
        self.assertEqual(api_usage['retry_after'], 120)
        self.assertTrue(api_usage['timestamp'] > 0)
        self.assertEqual(api_usage['status_code'], 200)

        # Check that statistics were updated
        # The exact index depends on the current time, but we can check that
        # some value was updated in the statistics
        non_zero_count = sum(1 for v in self.trading_account._api_usage_statistics if v > 0)
        self.assertGreater(non_zero_count, 0)
        self.assertEqual(non_zero_count, 1)

        # Test multiple updates to ensure statistics rotation
        trading_account = TradingAccount2(self.api_key, self.api_secret, api_usage_storage_size=5)
        for i in range(10):
            expected = i * 2 + 1  # avoid zero value because later we count non-zero values
            test_headers = {
                'x-mbx-used-weight': str(i * 5),
                'x-mbx-used-weight-1m': str(expected),
                'date': f'Mon, 01 Jan 2023 00:{str(i).zfill(2)}:00 GMT'
            }
            self.trading_account._update_api_usage(test_headers, status_code=200)
            self.assertEqual(expected, next(reversed(self.trading_account._api_usage_statistics.values())))
            self.assertEqual(self.trading_account.api_usage['status_code'], 200)

            trading_account._update_api_usage(test_headers, status_code=200)
            self.assertEqual(expected, next(reversed(trading_account._api_usage_statistics.values())))
            self.assertEqual(trading_account.api_usage['status_code'], 200)

        # Check that statistics are properly rotated and updated
        non_zero_count = sum(1 for v in self.trading_account._api_usage_statistics if v > 0)
        self.assertGreater(non_zero_count, 0)
        self.assertEqual(non_zero_count, 10)

        # Check that only the last 5 entries are kept
        self.assertEqual(len(trading_account._api_usage_statistics), 5)
        self.assertEqual(len(self.trading_account._api_usage_statistics), 10)  # this must kept untouched

        # Check that the oldest entries were rotated out
        # The timestamps should be from minutes 5-9 (not 0-4)
        base_timestamp = 1672531200  # Mon, 01 Jan 2023 00:00:00 GMT
        expected_timestamps = [base_timestamp + (i * 60) for i in range(5, 10)]  # 5, 6, 7, 8, 9 minutes
        self.assertListEqual(list(trading_account._api_usage_statistics.keys()), expected_timestamps)

        # Check that values correspond to the last 5 updates (5-9)
        values = list(trading_account._api_usage_statistics.values())
        expected_values = [i * 2 + 1 for i in range(5, 10)]  # 11, 13, 15, 17, 19
        self.assertEqual(values, expected_values)

    def test_get_api_usage_statistics(self):
        """Test the get_api_usage_statistics method"""
        # Fill statistics
        for i in range(10):
            test_headers = {
                'x-mbx-used-weight': str(i * 5),
                'x-mbx-used-weight-1m': str(i * 2 + 1),
                'date': f'Mon, 01 Jan 2023 00:{str(i).zfill(2)}:00 GMT'
            }
            self.trading_account._update_api_usage(test_headers, status_code=200)

        # Test with default retention period (7200 minutes)
        stats = self.trading_account.get_api_usage_statistics(fmt=None)
        self.assertEqual(len(stats), 10)
        self.assertTrue(all(isinstance(k, int) for k in stats.keys()))  # All keys should be timestamps
        self.assertTrue(all(isinstance(v, int) for v in stats.values()))  # All values should be integers

        # Test with formatted dates
        formatted_stats = self.trading_account.get_api_usage_statistics()
        self.assertEqual(len(formatted_stats), 10)
        self.assertTrue(all(isinstance(k, str) for k in formatted_stats.keys()))  # All keys should be strings
        self.assertTrue(all(isinstance(v, int) for v in formatted_stats.values()))  # All values should be integers

        # Test that keys are properly formatted when
        for key in formatted_stats.keys():
            self.assertRegex(key, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')  # YYYY-MM-DD HH:MM:SS format

        # Test that statistics are consistent between raw and formatted versions
        raw_stats = self.trading_account.get_api_usage_statistics(fmt=None)
        formatted_stats = self.trading_account.get_api_usage_statistics()

        # Convert formatted keys back to timestamps for comparison
        timestamp_keys = []
        for formatted_key, value in formatted_stats.items():
            timestamp = datetime.strptime(formatted_key, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            timestamp_keys.append(timestamp)

        # Sort both sets of keys for comparison
        sorted_raw_keys = sorted(raw_stats.keys())
        sorted_timestamp_keys = sorted(timestamp_keys)

        # Check that all values are the same
        self.assertEqual(len(raw_stats), len(formatted_stats))
        self.assertEqual(sorted_raw_keys, sorted_timestamp_keys)
        for raw_key, formatted_key in zip(sorted_raw_keys, sorted_timestamp_keys):
            self.assertEqual(
                raw_stats[raw_key],
                formatted_stats[datetime.fromtimestamp(formatted_key, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")]
            )

        # Test with some actual API usage data
        test_headers = {
            'x-mbx-used-weight': '10',
            'x-mbx-used-weight-1m': '555',
            'retry-after': '120',
            'date': 'Mon, 01 Jan 2023 00:00:00 GMT'
        }
        self.trading_account._update_api_usage(test_headers, status_code=200)

        # Get statistics after update
        stats_after_update = self.trading_account.get_api_usage_statistics(fmt=None)
        formatted_stats_after_update = self.trading_account.get_api_usage_statistics()

        # Check that some values are non-zero
        non_zero_count = sum(1 for v in stats_after_update.values() if v > 0)
        self.assertGreater(non_zero_count, 0)

        # Check that the same non-zero count appears in both versions
        formatted_non_zero_count = sum(1 for v in formatted_stats_after_update.values() if v > 0)
        self.assertEqual(non_zero_count, formatted_non_zero_count)

    def test_new_simple_trade(self):
        """Test new_simple_trade method with various scenarios"""
        # Create respective market for order roundings
        market = LocalMarket(exchange="binance", market_type="spot", symbol="BTCUSDT", base_ticker="BTC",
                             quote_ticker="USDT", lot_precision=4, price_precision=2)

        # Manually register the market in MarketBase._singleton_instances as LocalMarket not participate in singleton
        k = (type(market), market.symbol)
        MarketBase._singleton_instances[k] = market

        # Create account and set exchange and market_type
        self.trading_account._exchange = "binance"
        self.trading_account._market_type = "spot"

        # Test invalid symbol
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("", SIDE_BUY, Decimal('0.1'), Decimal('0.05'),
                                                  exit_pct=Decimal('0.02'))
        self.assertEqual(str(context.exception), "Symbol must be a non-empty string.")

        # Test invalid side
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("BTCUSDT", 2, Decimal('0.1'), 0.05, exit_pct=Decimal('0.02'))
        self.assertEqual(str(context.exception), f"Side must be {SIDE_BUY} for BUY or {SIDE_SELL} for SELL.")

        # Test invalid lot_entry (non-positive)
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0'), Decimal('0.05'),
                                                  exit_pct=Decimal('0.02'))
        self.assertEqual(str(context.exception), "lot_entry must be positive.")

        # Test invalid lot_exit (non-positive)
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0'),
                                                  exit_pct=Decimal('0.02'))
        self.assertEqual(str(context.exception), "lot_exit must be positive.")

        # Test invalid exit_pct (non-positive)
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0.05'),
                                                  exit_pct=Decimal('0'))
        self.assertEqual(str(context.exception), "exit_pct must be positive.")

        # Test successful trade execution with exit_pct
        orders = self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, '0.1', Decimal('0.05'),
                                                       exit_pct=Decimal('0.02'))
        self.assertEqual(len(orders), 2)

        # Test validation: neither exit_pct nor exit_price provided
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0.05'))
        self.assertEqual(str(context.exception), "Either exit_pct or exit_price must be provided.")

        # Test validation: both exit_pct and exit_price provided
        with self.assertRaises(ValueError) as context:
            self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0.05'),
                                                  exit_pct=Decimal('0.02'), exit_price=Decimal('10200'))
        self.assertEqual(str(context.exception), "Only one of exit_pct or exit_price can be provided.")

        # Test successful trade execution with exit_pct
        orders = self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0.05'),
                                                       exit_pct=Decimal('0.02'))
        self.assertEqual(len(orders), 2)
        entry_order, exit_order = orders

        # Verify both orders have the expected properties
        # Check entry order (MARKET order)
        self.assertIsInstance(entry_order, MagicMock)
        self.assertEqual(entry_order.order_type, ORDER_TYPE_MARKET)
        self.assertEqual(entry_order.side, SIDE_BUY)
        self.assertEqual(entry_order.quantity, Decimal('0.1'))
        self.assertEqual(entry_order.price, Decimal('10000'))  # Default market price

        # Check exit take order (LIMIT order) with calculated price
        self.assertIsInstance(exit_order, MagicMock)
        self.assertEqual(exit_order.order_type, ORDER_TYPE_LIMIT)
        self.assertEqual(exit_order.side, SIDE_SELL)  # Opposite side
        self.assertEqual(exit_order.quantity, Decimal('0.05'))
        expected_price = Decimal('10000') + Decimal('10000') * Decimal('0.02')
        self.assertEqual(exit_order.price, expected_price)

        # Test successful trade execution with exit_price
        orders = self.trading_account.new_simple_trade("BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0.05'),
                                                       exit_price=Decimal('10200'))
        self.assertEqual(len(orders), 2)
        entry_order, exit_order = orders

        # Verify both orders have the expected properties
        # Check entry order (MARKET order)
        self.assertIsInstance(entry_order, MagicMock)
        self.assertEqual(entry_order.order_type, ORDER_TYPE_MARKET)
        self.assertEqual(entry_order.side, SIDE_BUY)
        self.assertEqual(entry_order.quantity, Decimal('0.1'))
        self.assertEqual(entry_order.price, Decimal('10000'))  # Default market price

        # Check exit take order (LIMIT order) with fixed price
        self.assertIsInstance(exit_order, MagicMock)
        self.assertEqual(exit_order.order_type, ORDER_TYPE_LIMIT)
        self.assertEqual(exit_order.side, SIDE_SELL)  # Opposite side
        self.assertEqual(exit_order.quantity, Decimal('0.05'))
        self.assertEqual(exit_order.price, Decimal('10200'))  # Fixed price from exit_price

        # Test exit-take price calculation for LONG trades (SIDE_BUY)
        orders = self.trading_account.new_simple_trade(
            "BTCUSDT", SIDE_BUY, Decimal('0.1'), Decimal('0.05'),
            exit_pct=Decimal('0.02'))  # 2% take profit
        _, exit_order = orders

        # For LONG trades, exit-take price should be entry_price + (entry_price * pct)
        expected_price = Decimal('10000') + Decimal('10000') * Decimal('0.02')
        self.assertEqual(exit_order.price, expected_price)

        # Test exit-take price calculation for SHORT trades (SIDE_SELL)
        orders = self.trading_account.new_simple_trade(
            "BTCUSDT", SIDE_SELL, Decimal('0.1'), Decimal('0.05'),
            exit_pct=Decimal('0.02'))  # 2% take profit
        _, exit_order = orders

        # For SHORT trades, exit-take price should be entry_price - (entry_price * pct)
        expected_price = Decimal('10000') - Decimal('10000') * Decimal('0.02')
        self.assertEqual(exit_order.price, expected_price)


if __name__ == '__main__':
    unittest.main()
