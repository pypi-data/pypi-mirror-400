#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains SymbolAccountMixin and SymbolAccountError classes that implements basic symbol representation with balances
for base and quote currencies"""


class SymbolAccountError(Exception):
    """SymbolAccountMixin error"""


class SymbolAccountMixin:
    @property
    def base_quantity(self): return self._base_quantity

    @property
    def quote_quantity(self): return self._quote_quantity

    def __init__(self, *args, base_quantity=0, quote_quantity=0, **kwargs):
        if base_quantity < 0 or quote_quantity < 0:
            raise SymbolAccountError('Base and quote currencies quantity must be positive or zero!')
        self._base_quantity = base_quantity
        self._quote_quantity = quote_quantity
        if self.__class__.mro() != [self.__class__, object]:  # call parent(s).__init__ if it not 'object' only
            super().__init__(*args, **kwargs)
