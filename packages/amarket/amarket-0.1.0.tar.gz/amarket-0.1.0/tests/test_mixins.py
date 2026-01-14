import unittest
from datetime import datetime, timezone
from decimal import Decimal
from time import time

from amarket import SymbolAccountError, SymbolAccountMixin, SymbolError, SymbolMixin


class SymbolMixinTests(unittest.TestCase):
    def setUp(self):
        self.mixin = SymbolMixin(base_ticker="btc", quote_ticker="USD")

    def test_initialization(self):
        self.assertEqual(self.mixin.base_ticker, "BTC")
        self.assertEqual(self.mixin.quote_ticker, "USD")
        self.assertEqual(self.mixin.symbol, "BTCUSD")
        with self.assertRaises(AttributeError):
            self.mixin.base_ticker = 'ETH'  # noqa
        with self.assertRaises(AttributeError):
            self.mixin.quote_ticker = 'USDT'  # noqa
        with self.assertRaises(AttributeError):
            self.mixin.symbol = 'ETHUSD'  # noqa

        mixin = SymbolMixin()
        self.assertEqual(mixin.base_ticker, SymbolMixin.CURRENCY_BASE.upper())
        self.assertEqual(mixin.quote_ticker, SymbolMixin.CURRENCY_QUOTE.upper())
        self.assertEqual(mixin.symbol, "BASEQUOTE")

    def test_init_with_empty_tickers(self):
        with self.assertRaises(SymbolError):
            SymbolMixin(base_ticker="", quote_ticker="")
        with self.assertRaises(SymbolError):
            SymbolMixin(base_ticker="", quote_ticker="USDT")
        with self.assertRaises(SymbolError):
            SymbolMixin(base_ticker="btc", quote_ticker="")

    def test_init_with_long_tickers(self):
        with self.assertRaises(SymbolError):
            SymbolMixin(base_ticker="ETHETHETHETH", quote_ticker="USD")
        with self.assertRaises(SymbolError):
            SymbolMixin(base_ticker="BTC", quote_ticker="usdusdusdusd")
        with self.assertRaises(SymbolError):
            SymbolMixin(base_ticker="ETHETHEThETH", quote_ticker="USD", ticker_max_length=11)
        mixin = SymbolMixin(base_ticker="ETHETHEThETH", quote_ticker="USD", ticker_max_length=12)
        self.assertEqual(mixin.base_ticker, "ETHETHETHETH")
        self.assertEqual(mixin.quote_ticker, "USD")
        self.assertEqual(mixin.symbol, "ETHETHETHETHUSD")

    def test_price(self):
        self.assertEqual(self.mixin.price, 0.0)
        for value, expected in [(100.0, 100.0), (Decimal('99.99'), 99.99)]:
            timestamp = time()
            self.mixin.price = value
            self.assertEqual(self.mixin.price, expected)
            self.assertGreaterEqual(self.mixin.price_timestamp, round(timestamp))
            self.assertGreaterEqual(self.mixin.price_timestamp_ms, round(timestamp * 1000))

        with self.assertRaises(SymbolError):
            self.mixin.price = -10.0

        with self.assertRaises(SymbolError):
            self.mixin.price = 'invalid'

    def test_price_timestamp(self):
        timestamp = time()
        for value, expected1, expected2, expected3 in [
            (timestamp, round(timestamp), round(timestamp*1000), datetime.fromtimestamp(timestamp, tz=timezone.utc)),
            (1234567890.123456, 1234567890, 1234567890123, datetime.fromtimestamp(1234567890.123456, tz=timezone.utc)),
        ]:
            self.mixin.price_timestamp = value
            self.assertEqual(self.mixin.price_timestamp, expected1)
            self.assertEqual(self.mixin.price_timestamp_ms, expected2)
            self.assertEqual(self.mixin.price_datetime, expected3)

        with self.assertRaises(SymbolError):
            self.mixin.price_timestamp = -10.0

        with self.assertRaises(SymbolError):
            self.mixin.price_timestamp = 'invalid'


class SymbolBalanceMixinTests(unittest.TestCase):
    def setUp(self):
        self.mixin = SymbolAccountMixin(base_quantity=10, quote_quantity=100)

    def test_initialization(self):
        self.assertEqual(self.mixin.base_quantity, 10)
        self.assertEqual(self.mixin.quote_quantity, 100)

        mixin = SymbolAccountMixin('useless_arg1', 'useless_arg2',
                                   base_quantity=0, quote_quantity=0, useless_parameter=True)
        self.assertEqual(mixin.base_quantity, 0)
        self.assertEqual(mixin.quote_quantity, 0)

        with self.assertRaises(SymbolAccountError):
            SymbolAccountMixin(base_quantity=-10, quote_quantity=100)

        with self.assertRaises(SymbolAccountError):
            SymbolAccountMixin(base_quantity=10, quote_quantity=-100)


if __name__ == '__main__':
    unittest.main()
