#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains classes representing position"""
from datetime import datetime, timezone

__package__ = 'amarket'

from .symbol_account_mixin import SymbolAccountMixin
from .symbol_mixin import SymbolMixin


class PositionError(Exception):
    """Wrong position"""
    pass


def validate(func):
    def func_wrapper(*args, **kwargs):  # args must be: self, quantity, price, etc.; kwargs may contain currency, limit
        self = args[0]
        quantity = args[1]
        price = args[2]
        cname = self.__class__.__name__
        fname = func.__name__

        if self.is_closed:
            raise PositionError("{}.{}({}, {}): Position is closed".format(cname, fname, quantity, price))

        if not (isinstance(quantity, (int, float)) and isinstance(price, (int, float))):
            raise PositionError("{}.{}({}, {}): Both quantity and price must be numeric"
                                .format(cname, fname, quantity, price))

        if quantity <= 0 or price <= 0:
            raise PositionError("{}.{}({}, {}): Both quantity and price have to be greater than zero"
                                .format(cname, fname, quantity, price))

        if 'limit' in kwargs:
            if not isinstance(kwargs['limit'], (int, float)) or kwargs['limit'] < 0:
                raise PositionError(f"{cname}.{fname}({quantity}, {price}, limit={kwargs['limit']}): "
                                    f"Limit price must be the number and greater than zero")

        if 'currency' in kwargs:
            currency = kwargs['currency']
            if currency not in (Position.CURRENCY_BASE, Position.CURRENCY_QUOTE):
                raise PositionError("{}.{}({}, {}, currency={}): Currency must be '{}' or '{}'"
                                    .format(cname, fname, quantity, price, currency,
                                            Position.CURRENCY_BASE, Position.CURRENCY_QUOTE))
        else:
            currency = Position.CURRENCY_BASE

        if fname == 'decrease':
            qty = quantity if currency == Position.CURRENCY_BASE else quantity / price
            if qty > self.direction * self.base_quantity:
                raise PositionError('{}.{}({}, {}, currency={}): Can not decrease position because it has no such '
                                    'currency quantity (there are only {} of base, {} of quote). '
                                    'Try Position.close({})'.format(cname, fname, quantity, price, currency,
                                                                    self.base_quantity, self.quote_quantity, price))

        return func(*args, **kwargs)
    return func_wrapper


class Position(SymbolAccountMixin, SymbolMixin):
    """Class representing market position. Support only market orders (may say it processes only trades)"""
    DIRECTION_LONG = 1
    DIRECTION_SHORT = -1

    STATUS_NEW = 0  # there are no trades executed, pending opening
    STATUS_OPENED = 1  # there are executed trades
    STATUS_CLOSED = 7  # position closed, no further position adjustment allowed

    @property
    def direction(self): return self.__direction

    @property
    def average_price(self): return -1 * self.quote_quantity / self.base_quantity if self.base_quantity != 0 else 0

    @property
    def status(self): return self._status

    @property
    def created(self): return self._created

    @property
    def updated(self): return self._updated

    @property
    def opened(self): return self._opened

    @property
    def closed(self): return self._closed

    @property
    def has_trades(self) -> bool:
        """@:returns True if position has any trades, False otherwise"""
        return True if (self.base_quantity or self.quote_quantity) and not self.is_new else False

    @property
    def is_new(self) -> bool:
        """@:returns True if position is new"""
        return self.status == self.STATUS_NEW

    @property
    def is_closed(self) -> bool:
        """@:returns True if position is closed"""
        return self.status == self.STATUS_CLOSED

    def __init__(self, direction, *args, created=None, **kwargs):
        # Check inputs
        if direction != self.DIRECTION_LONG and direction != self.DIRECTION_SHORT:
            raise PositionError('Position direction must be Position.BUY or Position.SELL')
        self.__direction = direction
        self._status = self.STATUS_NEW
        self._created = datetime.now(timezone.utc) if created is None or not isinstance(created, datetime) else created
        self._updated = self._created
        self._opened = None
        self._closed = None
        super().__init__(*args, **kwargs)

    def to_dict(self):
        return {
            'direction': self.direction,
            'base_quantity': self.base_quantity,
            'quote_quantity': self.quote_quantity,
            'status': self.status,
            'created': self.created,
            'updated': self.updated,
            'opened': self.opened,
            'closed': self.closed,
        }

    @classmethod
    def from_dict(cls, d: dict):
        for k in ['direction', 'base_quantity', 'quote_quantity', 'status']:
            if k not in d:
                raise PositionError(f'{cls.__name__}.from_dict(...): Dictionary must contain keys: '
                                    "'direction', 'base_quantity', 'quote_quantity' and 'status'")

        entity = cls(d['direction'], created=d['created'] if 'created' in d else None)
        entity._status = d['status']

        if entity.is_new:
            if d['base_quantity'] != 0 or d['quote_quantity'] != 0:
                raise PositionError(f'{cls.__name__}.from_dict(...): '
                                    f'Base and quote quantity must be zero for new position!')
        elif entity.is_closed and d['base_quantity'] > 0:
            raise PositionError(f'{cls.__name__}.from_dict(...): Base quantity must be zero for closed position!')
        elif d['base_quantity'] < 0 and d['quote_quantity'] < 0:
            raise PositionError(f'{cls.__name__}.from_dict(...): Base and quote quantities can not be negative both!')

        entity._base_quantity = d['base_quantity']
        entity._quote_quantity = d['quote_quantity']

        if 'opened' in d:
            if d['opened'] < entity.created:
                raise PositionError(f'{cls.__name__}.from_dict(...): Open time is earlier than create time!')
            if entity.is_new:
                raise PositionError(f'{cls.__name__}.from_dict(...): Open time is given but status is new!')
            entity._opened = d['opened']
            entity._updated = d['opened']

        if 'closed' in d:
            if not entity.is_closed:
                raise PositionError(f'{cls.__name__}.from_dict(...): Close time is given but status is not closed!')
            else:
                if d['closed'] < entity.opened:
                    raise PositionError(f'{cls.__name__}.from_dict(...): Close time is earlier than open time!')
            entity._closed = d['closed']
            entity._updated = d['closed']

        return entity

    @classmethod
    def create_and_open(cls, direction, quantity, price, currency='base', opened=None):
        entity = cls(direction, created=opened)
        entity.increase(quantity, price, currency=currency, updated=opened)
        return entity

    def open(self, quantity, price, currency='base', opened=None, direction=None):
        if not self.base_quantity and not self.quote_quantity and self.is_new:
            if direction == self.DIRECTION_LONG or direction == self.DIRECTION_SHORT:
                self.__direction = direction
            self.increase(quantity, price, currency=currency, updated=opened)
        else:
            raise PositionError(f'{self.__class__.__name__}.open({quantity}, {price}...): '
                                f'Try to open not new (status={self.status}) position!')

    @validate
    def increase(self, quantity, price, currency='base', updated=None):
        if currency == self.CURRENCY_BASE:
            self._base_quantity += self.direction * quantity
            self._quote_quantity -= self.direction * quantity * price
        else:
            self._base_quantity += self.direction * quantity / price
            self._quote_quantity -= self.direction * quantity
        self._status = self.STATUS_OPENED
        updated = datetime.now(timezone.utc) if updated is None or not isinstance(updated, datetime) else updated
        self._opened = updated if self._opened is None else self._opened  # first increase() call, set self._opened
        self._updated = updated

    @validate
    def decrease(self, quantity, price, currency='base', updated=None):
        if currency == self.CURRENCY_BASE:
            self._base_quantity -= self.direction * quantity
            self._quote_quantity += self.direction * quantity * price
        else:
            self._base_quantity -= self.direction * quantity / price
            self._quote_quantity += self.direction * quantity
        self._status = self.STATUS_OPENED
        self._updated = datetime.now(timezone.utc) if updated is None or not isinstance(updated, datetime) else updated

    def close(self, price, closed=None):
        if not isinstance(price, (int, float)) or price <= 0:
            raise PositionError(f'{self.__class__.__name__}.close({price}): '
                                f'Close price must be the number and greater than zero')
        if not self.is_new and self.has_trades and not self.is_closed:
            self.decrease(abs(self._base_quantity), price, currency=self.CURRENCY_BASE, updated=closed)
        self._status = self.STATUS_CLOSED
        self._closed = datetime.now(timezone.utc) if closed is None or not isinstance(closed, datetime) else closed

    def calculate_profit_loss(self, current_price):
        return (current_price - self.average_price) * self.base_quantity

    def calculate_pnl(self, current_price):
        return (current_price / self.average_price - 1 if self.average_price != 0 else 0) * self.direction


class PositionLimit(Position):
    """Position class with limit orders support"""
    # STATUS_NEW: inherited, meaning: there are no trades executed, pending opening (limit orders may exists)
    # STATUS_OPENED: inherited, meaning: there are executed trades and no limit orders waiting fulfillment
    # STATUS_CLOSED: inherited, meaning: position closed, no new orders allowed
    STATUS_PENDING = 2  # there are executed trades and there are limit orders waiting fulfillment

    # Unfilled limit order data
    limit_price: 0
    limit_side: None  # 1 for BUY, -1 for SELL (similar to Position's direction), None - no limit order
    limit_base_quantity: 0

    def __init__(self, direction):
        super().__init__(direction)
        self.cancel_limit()

    def has_limit(self): return False if self.limit_side is None else True  # True if position has unfilled limit order

    def cancel_limit(self):
        self.limit_price = 0
        self.limit_side = None
        self.limit_base_quantity = 0

    def fill_limit(self):
        if self.direction == self.limit_side:
            self.increase(self.limit_base_quantity, self.limit_price, currency=self.CURRENCY_BASE, limit=0)
        else:
            self.decrease(self.limit_base_quantity, self.limit_price, currency=self.CURRENCY_BASE, limit=0)
        self.cancel_limit()

    def to_dict(self):
        d = super().to_dict()
        d['limit_price'] = self.limit_price
        d['limit_side'] = self.limit_side
        d['limit_base_quantity'] = self.limit_base_quantity
        return d

    @validate
    def increase(self, quantity, price, currency='base', limit=0):
        limit_filled = False
        if (self.direction == self.DIRECTION_LONG and limit >= price) or \
                (self.direction == self.DIRECTION_SHORT and limit <= price):
            limit_filled = True

        if not limit or limit_filled:
            return super().increase(quantity, price, currency=currency)
        else:
            self.limit_side = self.direction
            self.limit_price = limit
            self.limit_base_quantity = quantity if currency == self.CURRENCY_BASE else quantity / limit
            self._status = self.STATUS_PENDING if self.has_trades else self.STATUS_NEW

    @validate
    def decrease(self, quantity, price, currency='base', limit=0):
        limit_filled = False
        if (self.direction == self.DIRECTION_LONG and limit <= price) or \
                (self.direction == self.DIRECTION_SHORT and limit >= price):
            limit_filled = True

        if not limit or limit_filled:
            return super().decrease(quantity, price, currency=currency)
        else:
            self.limit_side = -self.direction
            self.limit_price = limit
            self.limit_base_quantity = quantity if currency == self.CURRENCY_BASE else quantity / limit
            self._status = self.STATUS_PENDING if self.has_trades else self.STATUS_NEW


if __name__ == '__main__':
    print('Testing class Position')
    print('======================')
    for direction in (Position.DIRECTION_LONG, Position.DIRECTION_SHORT):
        for currency in (Position.CURRENCY_BASE, Position.CURRENCY_QUOTE):
            qty = 0.001 if currency == 'base' else 20
            print('Direction: {}, Currency: {}, {} units'
                  .format('LONG' if direction == Position.DIRECTION_LONG else 'SHORT', currency.upper(), qty))
            pos = Position(direction)
            print(f'Initiated: {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')
            pos.increase(qty, 20000, currency=currency)
            print(f'Increased: {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')
            pos.increase(qty, 25000, currency=currency)
            print(f'Increased: {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')
            pos.decrease(qty, 30000, currency=currency)
            print(f'Decreased: {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')
            pos.close(29000)
            print(f'Closed:    {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')
            d = {'direction': 1, 'base_quantity': 0.001, 'quote_quantity': -20.0, 'status': 1}

            pos = Position.from_dict(d)
            print("From dict: {}, AvgPrice: {}, has trades: {}, equal: {}"
                  .format(pos.to_dict(), pos.average_price, pos.has_trades, d == pos.to_dict()))

            pos = Position(direction)
            pos.open(qty, 20000, currency=currency, direction=-direction)
            print(f'Opened:    {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')
            pos.open(qty, 20000, currency=currency, direction=direction)
            print(f'Opened-2:  {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')

            pos = Position.create_and_open(direction, qty, 20000, currency=currency)
            print(f'Created:   {pos.to_dict()}, AvgPrice: {pos.average_price}, has trades: {pos.has_trades}')

            print()

    print('Testing class PositionLimit')
    print('===========================')
    pos = PositionLimit(PositionLimit.DIRECTION_LONG)
    print('Initiated: {}, AvgPrice: {}, has trades: {}'.format(pos.to_dict(), pos.average_price, pos.has_trades))
    pos.increase(qty, 20000, currency='quote', limit=21000)
    print('Increased: {}, AvgPrice: {}, has trades: {}'.format(pos.to_dict(), pos.average_price, pos.has_trades))
    pos.increase(qty, 21000, currency='quote', limit=19000)
    print('Limit    : {}, AvgPrice: {}, has trades: {}'.format(pos.to_dict(), pos.average_price, pos.has_trades))
    pos.fill_limit()
    print('Filling  : {}, AvgPrice: {}, has trades: {}'.format(pos.to_dict(), pos.average_price, pos.has_trades))
