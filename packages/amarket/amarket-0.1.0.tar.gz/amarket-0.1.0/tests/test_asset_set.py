import unittest

from amarket import AssetSet, AssetSetError


class AssetSetTests(unittest.TestCase):
    def setUp(self):
        self.tickers = ['AAPL', 'GOOG']
        self.amounts = [10, 20]
        self.asset_set = AssetSet(self.tickers, self.amounts)

    def test_init_with_valid_data(self):
        tickers = ['AAPL', 'GOOG', 'MSFT']
        amounts = [10, 20, 30]
        asset_set = AssetSet(tickers, amounts)
        self.assertEqual(len(asset_set), 3)
        self.assertEqual(len(asset_set.tickers), 3)
        self.assertEqual(len(asset_set.amounts), 3)
        self.assertEqual(len(asset_set.assets), 3)
        self.assertEqual(asset_set.n, 3)
        self.assertEqual(asset_set['AAPL'], 10)
        self.assertEqual(asset_set['GOOG'], 20)
        self.assertEqual(asset_set['MSFT'], 30)

        asset_set = AssetSet([], [])
        self.assertEqual(len(asset_set), 0)
        self.assertEqual(asset_set.n, 0)

    def test_init_with_invalid_tickers(self):
        tickers = ['AAPL', 'GOOG', 123]
        amounts = [10, 20, 30]
        with self.assertRaises(AssetSetError):
            AssetSet(tickers, amounts)

    def test_init_with_invalid_amounts(self):
        tickers = ['AAPL', 'GOOG', 'MSFT']
        amounts = [10, '20', 30]
        with self.assertRaises(AssetSetError):
            AssetSet(tickers, amounts)

    def test_init_with_duplicate_tickers(self):
        tickers = ['AAPL', 'GOOG', 'AAPL']
        amounts = [10, 20, 30]
        with self.assertRaises(AssetSetError):
            AssetSet(tickers, amounts)

    def test_init_with_mismatched_lengths(self):
        tickers = ['AAPL', 'GOOG', 'MSFT']
        amounts = [10, 20]
        with self.assertRaises(AssetSetError):
            AssetSet(tickers, amounts)

    def test_setitem(self):
        asset_set = AssetSet(['AAPL'], [10])
        asset_set['GOOG'] = 20
        self.assertEqual(len(asset_set), 2)
        self.assertEqual(asset_set.n, 2)
        self.assertEqual(asset_set['AAPL'], 10)
        self.assertEqual(asset_set['GOOG'], 20)

    def test_delitem(self):
        del self.asset_set['AAPL']
        self.assertEqual(len(self.asset_set), 1)
        self.assertEqual(self.asset_set.n, 1)
        with self.assertRaises(KeyError):
            self.asset_set['AAPL']  # noqa

    def test_getitem(self):
        # with int key
        self.assertEqual(self.asset_set[0], 10)
        self.assertEqual(self.asset_set[1], 20)

        # with str key
        self.assertEqual(self.asset_set['AAPL'], 10)
        self.assertEqual(self.asset_set['GOOG'], 20)

        # with_invalid_key_type
        with self.assertRaises(TypeError):
            self.asset_set[1.5]  # noqa

        # with non-existing ticker
        with self.assertRaises(KeyError):
            self.asset_set['MSFT']  # noqa

    def test_iter(self):
        items = list(self.asset_set)
        self.assertEqual(items, self.tickers)

        items = list(dict(zip(self.tickers, self.amounts)).items())
        self.assertEqual(items, list(self.asset_set.items()))

    def test_next(self):
        iterator = iter(self.asset_set)
        self.assertEqual(next(iterator), 'AAPL')
        self.assertEqual(next(iterator), 'GOOG')
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_comparison(self):
        asset_set = AssetSet(self.tickers, [20, 30])
        self.assertNotEqual(self.asset_set, asset_set)

        asset_set = AssetSet(['AAPL', 'MSFT'], [10, 20])
        self.assertNotEqual(self.asset_set, asset_set)

        asset_set = AssetSet(self.tickers, self.amounts)
        self.assertEqual(self.asset_set, asset_set)

    def test_sub(self):
        asset_set1 = AssetSet(['AAPL', 'GOOG'], [10, 20])
        asset_set2 = AssetSet(['GOOG', 'MSFT'], [15, 25])
        result = asset_set1 - asset_set2
        self.assertEqual(len(result), 3)
        self.assertEqual(result.n, 3)
        self.assertEqual(result['AAPL'], 10)
        self.assertEqual(result['GOOG'], 5)
        self.assertEqual(result['MSFT'], -25)

        asset_set1 = AssetSet(['AAPL', 'GOOG', 'MSFT'], [10, 20, 30])
        result = asset_set1 - asset_set2
        self.assertEqual(len(result), 3)
        self.assertEqual(result.n, 3)
        self.assertEqual(result['AAPL'], 10)
        self.assertEqual(result['GOOG'], 5)
        self.assertEqual(result['MSFT'], 5)

    def test_value(self):
        prices = [100, 200]
        self.assertEqual(self.asset_set.value(prices), 5000)

        asset_set = AssetSet(['AAPL', 'GOOG', 'MSFT'], [10, 20, 30])
        prices = [100, 200, 300]
        expected_value = sum([a * p for a, p in zip(asset_set.amounts, prices)])
        self.assertEqual(asset_set.value(prices), expected_value)

        with self.assertRaises(ValueError):
            asset_set.value([100, 200])

    def test_weights(self):
        prices = [100.5, 38.12]
        value = sum([price * amount for price, amount in zip(prices, self.asset_set.amounts)])
        weights = [price * amount / value for price, amount in zip(prices, self.asset_set.amounts)]
        self.assertEqual(self.asset_set.weights(prices), weights)

    def test_sort(self):
        asset_set = AssetSet(['GOOG', 'AAPL', 'MSFT'], [20, 10, 30])
        self.assertEqual(asset_set.tickers, ['AAPL', 'GOOG', 'MSFT'])
        self.assertEqual(asset_set.amounts, [10, 20, 30])


if __name__ == '__main__':
    unittest.main()
