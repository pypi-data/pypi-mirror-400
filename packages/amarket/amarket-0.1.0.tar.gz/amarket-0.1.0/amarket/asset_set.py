#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains AssetSet class, representing set of assets, and AssetSetError exception class"""
from decimal import Decimal
from typing import List, MappingView, Union


class AssetSetError(Exception):
    """Wrong asset set"""


class AssetSet:
    """Class representing pure set of assets. Allow to compare, subtract, etc"""
    def __init__(self, tickers: Union[List[str], MappingView],
                 amounts: Union[List[Union[float, int, Decimal]], MappingView]):
        # Early check of data
        if not all([isinstance(_, str) for _ in tickers]):
            raise AssetSetError(f'Tickers are wrong, all tickers must be strings! {tickers}')
        elif not all([isinstance(_, (int, float, Decimal)) for _ in amounts]):
            raise AssetSetError(f'Amounts are wrong, all amounts must be numbers! {amounts}')

        # Create main properties
        self.current_index = 0
        self.assets = {}
        self.tickers = [str(_) for _ in tickers]
        self.amounts = [float(_) for _ in amounts]

        # Continue checking
        if len(self.tickers) != len(set(self.tickers)):
            raise AssetSetError(f'Tickers must be unique! {self.tickers}')
        elif len(self.tickers) != len(self.amounts):
            raise AssetSetError(f'Length of tickers not equal to length of assets amounts! '
                                f'{len(self.tickers)}!={len(self.amounts)}')

        # Everything is ok, sort the portfolio by tickers alphabetically if not empty
        if self.tickers:
            self.__sort()

    def __len__(self): return len(self.assets)
    def __contains__(self, item): return item in self.assets

    def __setitem__(self, key, value):
        if key in self.assets:
            idx = self.tickers.index(key)
            self.amounts[idx] = value
            self.assets[key] = value
        else:
            need_sort = (key < self.tickers[-1]) if len(self) else False
            self.tickers.append(key)
            self.amounts.append(value)
            self.assets[key] = value
            if need_sort:
                self.__sort()

    def __delitem__(self, key):
        idx = self.tickers.index(key)
        del self.tickers[idx]
        del self.amounts[idx]
        del self.assets[key]

    def __getitem__(self, item: Union[int, str]):
        if isinstance(item, int):
            return self.amounts[item]
        elif isinstance(item, str):
            return self.assets[item]
        else:
            raise TypeError(f'Wrong key type! Must be int or str, {type(item)} given')

    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index < len(self):
            v = self.tickers[self.current_index]
            self.current_index += 1
            return v
        raise StopIteration

    def __ne__(self, other): return self.assets != other.assets
    def __eq__(self, other): return self.assets == other.assets

    def __str__(self):
        return str(self.assets)

    def __sub__(self, other):
        tickers = sorted(set(self.tickers + other.tickers))  # combined tickers list, sorted and unique
        left = {_: self.assets[_] if _ in self.assets else 0 for _ in tickers}
        right = {_: other.assets[_] if _ in other.assets else 0 for _ in tickers}
        diff = {_: left[_] - right[_] for _ in tickers}
        return self.__class__.from_dict(diff)

    @property
    def n(self): return len(self)

    def items(self): return self.assets.items()

    def __sort(self):
        self.tickers, self.amounts = zip(*sorted(zip(self.tickers, self.amounts, strict=True)), strict=True)
        self.tickers, self.amounts = list(self.tickers), list(self.amounts)
        self.assets = dict(zip(self.tickers, self.amounts, strict=True))

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d.keys(), d.values())

    def values(self, prices: List[Union[float, int, Decimal]]) -> List[float]:
        return [amount * float(price) for amount, price in zip(self.amounts, prices, strict=True)] \
            if self.amounts and prices else []

    def value(self, prices: List[Union[float, int, Decimal]]) -> float:
        return sum(self.values(prices)) if self.amounts and prices else 0

    def weights(self, prices: List[Union[float, int, Decimal]]) -> List[float]:
        values = self.values(prices)
        total_value = sum(values)
        return [value/total_value for value in values]


if __name__ == "__main__":
    # Create AssetSet of {'BTC': 0.01, 'USDT': 100}
    asset_set = AssetSet(['BTC', 'USDT'], [0.01, 100])
    print(asset_set)

    # Add 0.1 Ethereum to asset set
    asset_set['ETH'] = 0.1
    print(asset_set)

    # Get amount of BTC in asset set (get BTC balance in other words)
    print(asset_set['BTC'])
