import unittest

import numpy as np
from amarket.portfolio import Portfolio, PortfolioError


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.wealth = 10000
        self.prices = [37175, 1.0]
        self.weights = [0.7, 0.3]
        self.tickers = ['BTC', 'USDT']
        self.currency = 'USDT'
        self.n = len(self.prices)
        self.portfolio = [self.wealth*self.weights[0]/self.prices[0], self.wealth*self.weights[1]/self.prices[1]]
        self.value = self.portfolio[0] * self.prices[0] + self.portfolio[1] * self.prices[1]
        self.p = Portfolio(self.wealth, self.prices, weights=self.weights, tickers=self.tickers, currency=self.currency)
        self.p_1n = Portfolio(self.wealth, self.prices, tickers=self.tickers, currency=self.currency)
        self.p_usdt = Portfolio(self.wealth, [0, 1], weights=[0, 1], tickers=self.tickers, currency=self.currency)

    def test_initialization(self):
        # Test properties of self.p
        self.assertEqual(self.p.initial_wealth, 10000)
        self.assertEqual(self.p.wealth, 10000)
        self.assertEqual(self.p.currency, self.currency)
        self.assertEqual(self.p.n, self.n)
        self.assertSequenceEqual(self.p.tickers, self.tickers)
        self.assertEqual(len(self.p.history), 1)
        self.assertSequenceEqual(self.p.prices.tolist(), self.prices)  # prices 1 method
        self.assertTrue(np.allclose(self.p.prices, self.prices))  # prices 2 method
        self.assertSequenceEqual(self.p.weights.tolist(), self.weights)  # weights 1 method
        self.assertTrue(np.allclose(self.p.weights, self.weights))  # weights 2 method
        self.assertEqual(sum(self.p.weights), 1)
        self.assertSequenceEqual(self.p.portfolio.tolist(), self.portfolio)  # portfolio 1 method
        self.assertTrue(np.allclose(self.p.portfolio, self.portfolio))  # portfolio 2 method

        # Test properties of self.p_1n
        self.assertEqual(self.p_1n.initial_wealth, self.wealth)
        self.assertEqual(self.p_1n.wealth, self.wealth)
        self.assertEqual(self.p_1n.n, self.n)
        self.assertEqual(len(self.p_1n.history), 1)
        weights = np.empty(self.n)
        weights.fill(1/self.n)
        self.assertSequenceEqual(self.p_1n.weights.tolist(), weights.tolist())
        self.assertTrue(np.allclose(self.p_1n.weights, weights))
        self.assertEqual(sum(self.p_1n.weights), 1)
        portfolio = [self.wealth*weights[0]/self.prices[0], self.wealth*weights[1]/self.prices[1]]
        self.assertSequenceEqual(self.p_1n.portfolio.tolist(), portfolio)  # portfolio 1 method
        self.assertTrue(np.allclose(self.p_1n.portfolio, portfolio))  # portfolio 2 method

        # Test properties of self.p_usdt
        self.assertEqual(self.p_usdt.initial_wealth, self.wealth)
        self.assertEqual(self.p_usdt.wealth, self.wealth)
        self.assertEqual(self.p_usdt.n, self.n)
        self.assertEqual(len(self.p_usdt.history), 1)
        self.assertSequenceEqual(self.p_usdt.prices.tolist(), [1, 1])
        self.assertSequenceEqual(self.p_usdt.weights.tolist(), [0, 1])
        self.assertEqual(sum(self.p_usdt.weights), 1)
        self.assertSequenceEqual(self.p_usdt.portfolio.tolist(), [0, self.wealth])

        # Test raising exceptions for wrong portfolios
        for prices, weights in zip([[0, 0], [0, 0], [1, 40], [100, 22]], [[0, 0], [0, 1], [0.3, 0.9], [0.3, 0.2, 0.5]]):
            with self.assertRaises(PortfolioError):
                Portfolio(self.wealth, prices, weights=weights)
        with self.assertRaises(PortfolioError):
            Portfolio(0, self.prices, weights=self.weights)

    def test_value(self):
        self.assertEqual(self.p.value(), self.value)
        self.assertEqual(self.p.value(), self.wealth)
        self.assertEqual(self.p.value(), self.p.wealth)
        self.assertEqual(self.p.value(), self.p.initial_wealth)

        self.assertEqual(self.p_1n.value(), self.value)
        self.assertEqual(self.p_1n.value(), self.wealth)
        self.assertEqual(self.p_1n.value(), self.p_1n.wealth)
        self.assertEqual(self.p_1n.value(), self.p_1n.initial_wealth)

        self.assertEqual(self.p_usdt.value(), self.value)
        self.assertEqual(self.p_usdt.value(), self.wealth)
        self.assertEqual(self.p_usdt.value(), self.p_usdt.wealth)
        self.assertEqual(self.p_usdt.value(), self.p_usdt.initial_wealth)

    def test_rebalance(self):
        new_prices = [36500, 1]
        new_weights = [0.5, 0.5]
        self.p.rebalance(new_prices, weights=new_weights)
        self.assertEqual(len(self.p.history), 2)
        self.assertSequenceEqual(self.p.prices.tolist(), new_prices)  # prices 1 method
        self.assertTrue(np.allclose(self.p.prices, new_prices))  # prices 2 method
        self.assertSequenceEqual(self.p.weights.tolist(), new_weights)  # weights 1 method
        self.assertTrue(np.allclose(self.p.weights, new_weights))  # weights 2 method
        self.assertTrue(np.allclose(self.p.portfolio, [0.135245184, 4936.44923]))  # rebalanced portfolio

        self.p.rebalance([20000, 1], wealth=1000)  # rebalance depositing wealth
        self.assertEqual(len(self.p.history), 3)

        self.p.rebalance([25000, 1], wealth=-1000)  # rebalance withdrawing wealth
        self.assertEqual(len(self.p.history), 4)

        # Check that sells + buys = added_wealth on each history record
        for hr in self.p.history:
            diff = 0
            for i, amount in enumerate(hr['diff']):
                diff += amount * hr['prices'][i]
            self.assertAlmostEqual(hr['wealth'], diff)
            self.assertAlmostEqual(hr['wealth'], np.sum(hr['diff'] * hr['prices']))  # calculations with numpy

        with self.assertRaises(PortfolioError):
            self.p.rebalance([35000, 1], wealth=-10000000)  # try to withdraw more money than total wealth
        self.assertEqual(len(self.p.history), 4)

        self.p.rebalance([5000, 1])  # simulate that prices go very low
        self.assertLess(self.p.value(), self.p.wealth)  # and now value is less than invested wealth
        with self.assertRaises(PortfolioError):
            self.p.rebalance([10000, 1], wealth=-self.p.wealth)  # try to withdraw all invested wealth
        self.assertEqual(len(self.p.history), 5)


if __name__ == '__main__':
    unittest.main()
