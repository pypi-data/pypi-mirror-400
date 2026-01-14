import unittest

from amarket.base import MarketBase
from amarket.constants.market_type import MarketType
from amarket.local import LocalMarket


class TestLocalMarket(unittest.TestCase):
    """Test cases for the LocalMarket class."""

    def setUp(self):
        """Set up test fixtures."""
        self.exchange = 'Exchange_1'
        self.market_type = MarketType.SPOT
        self.symbol = 'BTCUSDT'
        self.base_ticker = 'BTC'
        self.quote_ticker = 'USDT'
        self.lot_precision = 4
        self.price_precision = 2
        self.market = LocalMarket(self.exchange, self.market_type, self.symbol,
                                  base_ticker=self.base_ticker, quote_ticker=self.quote_ticker,
                                  lot_precision=self.lot_precision, price_precision=self.price_precision)

    def test_singleton_disabled(self):
        """Test that singleton behavior is disabled."""
        market2 = LocalMarket(self.exchange, self.market_type, self.symbol,
                              base_ticker=self.base_ticker, quote_ticker=self.quote_ticker,
                              lot_precision=self.lot_precision, price_precision=self.price_precision)
        self.assertIsNot(self.market, market2)
        self.assertDictEqual(self.market._singleton_instances, {})
        self.assertDictEqual(market2._singleton_instances, {})
        self.assertDictEqual(LocalMarket._singleton_instances, {})
        self.assertDictEqual(MarketBase._singleton_instances, {})

    def test_properties(self):
        """Test that properties are set correctly."""
        self.assertEqual(self.market.exchange, self.exchange)
        self.assertEqual(self.market.market_type, self.market_type)
        self.assertEqual(self.market.symbol, self.symbol.upper())
        self.assertEqual(self.market.base_ticker, self.base_ticker)
        self.assertEqual(self.market.quote_ticker, self.quote_ticker)
        self.assertEqual(self.market.lot_precision, self.lot_precision)
        self.assertEqual(self.market.price_precision, self.price_precision)
