#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests some logic in constants module"""
import unittest

from amarket.constants import SIDE_BUY, SIDE_SELL, MarketType, Side


class TestConstants(unittest.TestCase):
    def test_market_type(self):
        # Test is_spot methods
        self.assertTrue(MarketType.is_spot(10))
        self.assertFalse(MarketType.is_spot(20))
        self.assertTrue(MarketType.is_spot('spot'))
        self.assertFalse(MarketType.is_spot('futures'))

        # Test is_futures methods
        self.assertTrue(MarketType.is_futures(20))
        self.assertFalse(MarketType.is_futures(10))
        self.assertTrue(MarketType.is_futures('futures'))
        self.assertFalse(MarketType.is_futures('spot'))

        # Test is_cross_margin methods
        self.assertTrue(MarketType.is_cross_margin(30))
        self.assertFalse(MarketType.is_cross_margin(40))
        self.assertTrue(MarketType.is_cross_margin('cross'))
        self.assertFalse(MarketType.is_cross_margin('isolated'))

        # Test is_isolated_margin methods
        self.assertTrue(MarketType.is_isolated_margin(40))
        self.assertFalse(MarketType.is_isolated_margin(30))
        self.assertTrue(MarketType.is_isolated_margin('isolated'))
        self.assertFalse(MarketType.is_isolated_margin('cross'))

        # Test possible_types
        result = MarketType.possible_types()
        for s in ('spot', 'futures', 'cross', 'isolated'):
            self.assertIn(s, result)

        # Test possible_codes
        result = MarketType.possible_codes()
        for v in (10, 20, 30, 40):
            self.assertIn(v, result)

        # Test get_market_type_code methods
        self.assertEqual(MarketType.get_market_type_code(10), 10)
        self.assertEqual(MarketType.get_market_type_code('spot'), 10)
        self.assertEqual(MarketType.get_market_type_code(20), 20)
        self.assertEqual(MarketType.get_market_type_code('futures'), 20)
        self.assertEqual(MarketType.get_market_type_code(30), 30)
        self.assertEqual(MarketType.get_market_type_code('cross'), 30)
        self.assertEqual(MarketType.get_market_type_code(40), 40)
        self.assertEqual(MarketType.get_market_type_code('isolated'), 40)

        # Test get_market_type methods
        self.assertEqual(MarketType.get_market_type(10), 'spot')
        self.assertEqual(MarketType.get_market_type('spot'), 'spot')
        self.assertEqual(MarketType.get_market_type(20), 'futures')
        self.assertEqual(MarketType.get_market_type('futures'), 'futures')
        self.assertEqual(MarketType.get_market_type(30), 'cross')
        self.assertEqual(MarketType.get_market_type('cross'), 'cross')
        self.assertEqual(MarketType.get_market_type(40), 'isolated')
        self.assertEqual(MarketType.get_market_type('isolated'), 'isolated')

        # Test invalid market type
        with self.assertRaises(ValueError):
            MarketType.get_market_type(999)

    def test_side_type(self):
        # Test is_buy method
        self.assertTrue(Side.is_buy(1))
        self.assertTrue(Side.is_buy('1'))
        self.assertFalse(Side.is_buy(-1))
        self.assertTrue(Side.is_buy('BUY'))
        self.assertTrue(Side.is_buy('LONG'))
        self.assertFalse(Side.is_buy('SELL'))
        self.assertFalse(Side.is_buy('SHORT'))

        # Test is_sell method
        self.assertTrue(Side.is_sell(-1))
        self.assertTrue(Side.is_sell('-1'))
        self.assertFalse(Side.is_sell(1))
        self.assertTrue(Side.is_sell('SELL'))
        self.assertTrue(Side.is_sell('SHORT'))
        self.assertFalse(Side.is_sell('BUY'))
        self.assertFalse(Side.is_sell('LONG'))

        # Test possible_types
        result = Side.possible_types()
        for s in ('BUY', 'SELL'):
            self.assertIn(s, result)

        # Test possible_codes
        result = Side.possible_codes()
        for v in (1, -1):
            self.assertIn(v, result)

        # Test get_code methods
        self.assertEqual(Side.get_code(1), 1)
        self.assertEqual(Side.get_code('1'), 1)
        self.assertEqual(Side.get_code('BUY'), 1)
        self.assertEqual(Side.get_code(Side.BUY), 1)
        self.assertEqual(Side.get_code('LONG'), 1)
        self.assertEqual(Side.get_code(Side.LONG), 1)
        self.assertEqual(Side.get_code(-1), -1)
        self.assertEqual(Side.get_code('-1'), -1)
        self.assertEqual(Side.get_code('SELL'), -1)
        self.assertEqual(Side.get_code(Side.SELL), -1)
        self.assertEqual(Side.get_code('SHORT'), -1)
        self.assertEqual(Side.get_code(Side.SHORT), -1)

        self.assertEqual(Side.BUY_CODE, Side.LONG)
        self.assertEqual(Side.SELL_CODE, Side.SHORT)

        # Test invalid side type
        with self.assertRaises(ValueError):
            Side.get_code(999)

        # Test constants are the same
        self.assertEqual(Side.BUY_CODE, SIDE_BUY)
        self.assertEqual(Side.SELL_CODE, SIDE_SELL)


if __name__ == '__main__':
    unittest.main()
