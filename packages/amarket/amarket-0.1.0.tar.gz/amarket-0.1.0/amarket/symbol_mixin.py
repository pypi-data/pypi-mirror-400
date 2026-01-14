#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains SymbolMixin and SymbolError classes that implements basic symbol representation"""
from datetime import datetime, timezone
from decimal import Decimal
from math import ceil, floor
from time import time
from typing import Literal, Type, Union


class SymbolError(Exception):
    """Symbol error"""


class SymbolMixin:
    CURRENCY_BASE = 'base'
    CURRENCY_QUOTE = 'quote'

    @property
    def base_ticker(self) -> str: return self.__base_ticker

    @property
    def quote_ticker(self) -> str: return self.__quote_ticker

    @property
    def symbol(self) -> str: return self.__symbol

    @property
    def price(self) -> float: return self.__price

    @price.setter
    def price(self, value: Union[int, float, Decimal]):
        if isinstance(value, (int, float, Decimal)) and value > 0:
            self.__price = float(value)
            self.__price_timestamp = time()
        else:
            raise SymbolError('Price value must be positive non-zero int, float or decimal!')

    @property
    def price_timestamp(self) -> int:
        return round(self.__price_timestamp)

    @price_timestamp.setter
    def price_timestamp(self, value: Union[int, float, Decimal]):
        if isinstance(value, (int, float, Decimal)) and value > 0:
            self.__price_timestamp = float(value)
        else:
            raise SymbolError('Price timestamp value must be positive non-zero int, float or decimal!')

    @property
    def price_timestamp_ms(self) -> int:
        return round(self.__price_timestamp * 1000)

    @property
    def price_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.__price_timestamp, tz=timezone.utc)

    def __init__(self, *args, base_ticker='base', quote_ticker='quote', symbol='', ticker_max_length=10,
                 price=0.0, price_timestamp=0.0,
                 filter_max_quantity=0.0, filter_min_quantity=0.0, filter_step_size=0.0, filter_min_notional=0.0,
                 **kwargs):
        if not base_ticker or not quote_ticker:
            raise SymbolError('Base and quote tickers must be both set!')
        elif len(base_ticker) > ticker_max_length:
            raise SymbolError(f'Base ticker {base_ticker} exceed ticker_max_length={ticker_max_length}!')
        elif len(quote_ticker) > ticker_max_length:
            raise SymbolError(f'Quote ticker {quote_ticker} exceed ticker_max_length={ticker_max_length}!')

        self.__base_ticker = base_ticker.upper()
        self.__quote_ticker = quote_ticker.upper()
        self.__symbol = symbol if symbol and isinstance(symbol, str) else self.base_ticker + self.quote_ticker
        self.__price = price
        self.__price_timestamp = price_timestamp
        self.filter_max_quantity = Decimal(filter_max_quantity)
        self.filter_min_quantity = Decimal(filter_min_quantity)
        self.filter_step_size = Decimal(filter_step_size)
        self.filter_min_notional = Decimal(filter_min_notional)

        if self.__class__.mro() != [self.__class__, object]:  # call parent(s).__init__ if it not 'object' only
            super().__init__(*args, **kwargs)

    def filter_quantity(self, quantity: Union[int, float, Decimal], price: Union[int, float, Decimal] = 0,
                        rounding: Literal["round", "ceil", "floor"] = 'round',
                        min_quantity_pct: float = 0.5, min_notional_pct: float = 0.5,
                        return_as: Union[Type[float], Type[Decimal], Type[int], Type[str]] = float) \
            -> Union[float, Decimal, int, str]:
        """Adjust given quantity to match given filters.
        For some rounding rules explanations, @see https://stackoverflow.com/questions/68199013
        :param quantity: quantity to adjust
        :param rounding: rounding rules (rounding function name to use)
        :param price: price to use calculating MIN_NOTIONAL filter
        :param min_quantity_pct: quantity would be adjusted to match LOT_SIZE.minQty filter, if the resulting
            quantity be great or equal to min_quantity_pct * self.min_quantity, but less than self.min_quantity
        :param min_notional_pct: quantity would be adjusted to match MIN_NOTIONAL filter, if the resulting
            quote quantity be great or equal to min_notional_pct * self.min_notional, but less than self.min_notional
        :param return_as: return as given type
        :return: the adjusted quantity, matching all filters, or zero
        :raise: ValueError if given data not match some criteria (look code)
        """
        if quantity <= 0 or price < 0:
            raise ValueError(f'Quantity {quantity} must be positive non-zero and price {price} must be positive!')
        if 1 < min_quantity_pct < 0 or 1 < min_notional_pct < 0:
            raise ValueError(f'min_quantity_pct {min_quantity_pct} and min_notional_pct {min_notional_pct} both '
                             f'must be between 0..1 inclusive')

        # Set rounding function
        rfn = ceil if rounding == 'ceil' else floor if rounding == 'floor' else round

        # Applying LOT_SIZE.step_size filter if exist
        if self.filter_step_size:
            quantity = rfn(Decimal(quantity) / self.filter_step_size) * self.filter_step_size

        # Applying MIN_NOTIONAL.min_notional filter if exist and min_notional_pct rule if price is given
        if price and self.filter_min_notional and self.filter_step_size:
            price = Decimal(price)
            quote_quantity = quantity * price
            if self.filter_min_notional > quote_quantity >= Decimal(min_notional_pct) * self.filter_min_notional:
                quantity = ceil(self.filter_min_notional / price / self.filter_step_size) * self.filter_step_size
            elif quote_quantity < self.filter_min_notional:
                quantity = 0

        # Applying LOT_SIZE.min_quantity and LOT_SIZE.max_quantity filters if exist and min_quantity_pct rule
        if self.filter_min_quantity and quantity < self.filter_min_quantity:
            if quantity >= Decimal(min_quantity_pct) * self.filter_min_quantity:
                quantity = self.filter_min_quantity
            else:
                quantity = 0
        elif self.filter_max_quantity and quantity > self.filter_max_quantity:
            quantity = self.filter_max_quantity

        return return_as(quantity)
