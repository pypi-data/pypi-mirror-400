import unittest
from datetime import datetime, timedelta, timezone

from amarket import Position, PositionError


class TestLongPosition(unittest.TestCase):
    def setUp(self):
        self.position = Position(Position.DIRECTION_LONG)

    def test_initialization(self):
        self.assertEqual(self.position.direction, self.position.direction)
        self.assertEqual(self.position.base_quantity, 0)
        self.assertEqual(self.position.quote_quantity, 0)
        self.assertEqual(self.position.status, Position.STATUS_NEW)
        self.assertIsInstance(self.position.created, datetime)
        self.assertEqual(self.position.created.utcoffset().total_seconds(), 0)
        self.assertIsInstance(self.position.updated, datetime)
        self.assertEqual(self.position.created, self.position.updated)
        self.assertIsNone(self.position.opened)
        self.assertIsNone(self.position.closed)
        self.assertFalse(self.position.has_trades)
        self.assertEqual(self.position.average_price, 0)
        self.assertFalse(self.position.is_closed)
        self.assertEqual(self.position.calculate_profit_loss(100), 0)
        self.assertEqual(self.position.calculate_pnl(100), 0)

    def test_open(self):
        with self.assertRaises(PositionError):
            self.position.open(10, -2)
        with self.assertRaises(PositionError):
            self.position.open(-10, -2)
        with self.assertRaises(PositionError):
            self.position.open(-10, 2)
        with self.assertRaises(PositionError):
            self.position.open(-10, 2, currency=Position.CURRENCY_QUOTE)

        opened = datetime.now(timezone.utc)
        self.position.open(7, 1.8, opened=opened, direction=Position.DIRECTION_SHORT)
        self.assertEqual(self.position.direction, Position.DIRECTION_SHORT)
        self.assertEqual(self.position.base_quantity, -7)
        self.assertEqual(self.position.quote_quantity, 12.6)
        self.assertEqual(self.position.status, Position.STATUS_OPENED)
        self.assertEqual(self.position.opened, opened)
        self.assertEqual(self.position.updated, self.position.opened)
        self.assertLess(self.position.created, self.position.opened)
        self.assertIsNone(self.position.closed)
        self.assertTrue(self.position.has_trades)
        self.assertEqual(self.position.average_price, 1.8)
        self.assertFalse(self.position.is_closed)
        self.assertAlmostEqual(self.position.calculate_profit_loss(2), -1.4)
        self.assertAlmostEqual(self.position.calculate_pnl(1.98), -0.1)

    def test_increase(self):
        with self.assertRaises(PositionError):
            self.position.increase(-5, 1.2)
        with self.assertRaises(PositionError):
            self.position.increase(5, -1.2)
        with self.assertRaises(PositionError):
            self.position.increase(5, 0)
        with self.assertRaises(PositionError):
            self.position.increase(0, 1.2)
        with self.assertRaises(PositionError):
            self.position.increase(-5, -1.2)
        with self.assertRaises(PositionError):
            self.position.increase(-5, 0)

        self.position.increase(5, 1.2)
        self.assertEqual(self.position.base_quantity, 5 * self.position.direction)
        self.assertEqual(self.position.quote_quantity, -6 * self.position.direction)
        self.assertEqual(self.position.status, Position.STATUS_OPENED)
        self.assertTrue(self.position.has_trades)
        self.assertIsInstance(self.position.opened, datetime)
        self.assertIsInstance(self.position.updated, datetime)
        self.assertEqual(self.position.opened, self.position.updated)
        self.assertGreater(self.position.updated, self.position.created)
        self.assertTrue(self.position.has_trades)
        self.assertEqual(self.position.average_price, 1.2)
        self.assertFalse(self.position.is_closed)
        self.assertAlmostEqual(self.position.calculate_profit_loss(2), 4 * self.position.direction)
        self.assertAlmostEqual(self.position.calculate_pnl(1.32), 0.1 * self.position.direction)

        self.position.increase(17, 1.7, currency=Position.CURRENCY_QUOTE,
                               updated=self.position.updated + timedelta(0, 1))
        self.assertEqual(self.position.base_quantity, 15 * self.position.direction)
        self.assertEqual(self.position.quote_quantity, -23 * self.position.direction)
        self.assertEqual(self.position.status, Position.STATUS_OPENED)
        self.assertLess(self.position.opened, self.position.updated)
        self.assertLess(self.position.created, self.position.updated)
        self.assertEqual(self.position.updated - self.position.opened, timedelta(0, 1))
        self.assertTrue(self.position.has_trades)
        self.assertEqual(self.position.average_price, 23/15)
        self.assertFalse(self.position.is_closed)

    def test_decrease(self):
        with self.assertRaises(PositionError):
            self.position.decrease(3, 1.5)

        self.position.increase(10, 1.6)
        self.position.decrease(8, 2, updated=self.position.updated + timedelta(0, 1))
        self.assertEqual(self.position.base_quantity, 2 * self.position.direction)
        self.assertEqual(self.position.quote_quantity, 0)
        self.assertEqual(self.position.status, Position.STATUS_OPENED)
        self.assertTrue(self.position.has_trades)
        self.assertIsInstance(self.position.opened, datetime)
        self.assertIsInstance(self.position.updated, datetime)
        self.assertNotEqual(self.position.opened, self.position.updated)
        self.assertGreater(self.position.updated, self.position.created)
        self.assertFalse(self.position.is_closed)

        self.position.decrease(3.4, 1.7, currency=Position.CURRENCY_QUOTE,
                               updated=self.position.updated + timedelta(0, 1))
        self.assertEqual(self.position.base_quantity, 0)
        self.assertEqual(self.position.quote_quantity, 3.4 * self.position.direction)
        self.assertLess(self.position.opened, self.position.updated)
        self.assertLess(self.position.created, self.position.updated)
        self.assertEqual(self.position.updated - self.position.opened, timedelta(0, 2))
        self.assertFalse(self.position.is_closed)

    def test_close(self):
        closed = datetime.now(timezone.utc)

        with self.assertRaises(PositionError):
            self.position.close(0)
        with self.assertRaises(PositionError):
            self.position.close(-2.8, closed=closed)

        self.position.close(2.8, closed=closed)
        self.assertEqual(self.position.base_quantity, 0)
        self.assertEqual(self.position.quote_quantity, 0)
        self.assertEqual(self.position.status, Position.STATUS_CLOSED)
        self.assertEqual(self.position.closed, closed)
        self.assertLess(self.position.created, closed)
        self.assertLess(self.position.updated, closed)
        self.assertIsNone(self.position.opened, closed)
        self.assertFalse(self.position.has_trades)
        self.assertEqual(self.position.average_price, 0)
        self.assertTrue(self.position.is_closed)

        with self.assertRaises(PositionError):
            self.position.open(10, 2.2)
        self.assertEqual(self.position.base_quantity, 0)
        self.assertEqual(self.position.quote_quantity, 0)
        self.assertEqual(self.position.status, self.position.STATUS_CLOSED)
        self.assertFalse(self.position.has_trades)
        self.assertEqual(self.position.average_price, 0)
        self.assertTrue(self.position.is_closed)

        with self.assertRaises(PositionError):
            self.position.increase(10, 2.2)
        self.assertEqual(self.position.base_quantity, 0)
        self.assertEqual(self.position.quote_quantity, 0)
        self.assertEqual(self.position.status, self.position.STATUS_CLOSED)
        self.assertFalse(self.position.has_trades)
        self.assertEqual(self.position.average_price, 0)
        self.assertTrue(self.position.is_closed)

    def test_to_dict(self):
        expected_dict = {
            'direction': self.position.direction,
            'base_quantity': 0,
            'quote_quantity': 0,
            'status': Position.STATUS_NEW,
            'created': self.position.created,
            'updated': self.position.updated,
            'opened': None,
            'closed': None,
        }
        self.assertEqual(self.position.to_dict(), expected_dict)

        self.position.open(1, 13527)
        expected_dict['status'] = Position.STATUS_OPENED
        expected_dict['base_quantity'] = 1 * self.position.direction
        expected_dict['quote_quantity'] = -13527 * self.position.direction
        expected_dict['opened'] = self.position.opened
        expected_dict['updated'] = self.position.updated
        self.assertEqual(self.position.to_dict(), expected_dict)

        self.position.increase(1, 23527)
        expected_dict['base_quantity'] = 2 * self.position.direction
        expected_dict['quote_quantity'] = (-13527-23527) * self.position.direction
        expected_dict['updated'] = self.position.updated
        self.assertEqual(self.position.to_dict(), expected_dict)

        self.position.decrease(1, 24527)
        expected_dict['base_quantity'] = 1 * self.position.direction
        expected_dict['quote_quantity'] = (-13527-23527+24527) * self.position.direction
        expected_dict['updated'] = self.position.updated
        self.assertEqual(self.position.to_dict(), expected_dict)

        self.position.close(30000)
        expected_dict['status'] = Position.STATUS_CLOSED
        expected_dict['base_quantity'] = 0
        expected_dict['quote_quantity'] = (-13527-23527+24527+30000) * self.position.direction
        expected_dict['updated'] = self.position.updated
        expected_dict['closed'] = self.position.closed
        self.assertEqual(self.position.to_dict(), expected_dict)

    def test_from_dict(self):
        with self.assertRaises(PositionError):
            Position.from_dict({})

        created = datetime.now(timezone.utc)
        opened = created + timedelta(0, 1)

        input_dict = {
            'direction': self.position.direction,
            'base_quantity': 0,
            'quote_quantity': 0,
            'status': Position.STATUS_NEW,
            'created': created
        }
        position = Position.from_dict(input_dict)
        self.assertEqual(position.direction, self.position.direction)
        self.assertEqual(position.base_quantity, 0)
        self.assertEqual(position.quote_quantity, 0)
        self.assertEqual(position.status, Position.STATUS_NEW)
        self.assertEqual(position.created, created)
        self.assertEqual(position.updated, position.created)
        self.assertIsNone(position.opened)
        self.assertIsNone(position.closed)
        self.assertFalse(position.has_trades)
        self.assertTrue(position.is_new)
        self.assertFalse(position.is_closed)
        self.assertEqual(position.average_price, 0)
        del input_dict['created']
        position = Position.from_dict(input_dict)
        self.assertEqual(position.created, position.updated)

        with self.assertRaises(PositionError):
            input_dict['base_quantity'] = 1
            Position.from_dict(input_dict)
        with self.assertRaises(PositionError):
            input_dict['base_quantity'] = -1
            input_dict['quote_quantity'] = -100
            Position.from_dict(input_dict)

        input_dict['base_quantity'] = 10
        input_dict['quote_quantity'] = -15
        input_dict['status'] = Position.STATUS_OPENED
        input_dict['created'] = created
        input_dict['opened'] = opened
        position = Position.from_dict(input_dict)
        self.assertEqual(position.direction, self.position.direction)
        self.assertEqual(position.base_quantity, 10)
        self.assertEqual(position.quote_quantity, -15)
        self.assertEqual(position.status, Position.STATUS_OPENED)
        self.assertEqual(position.created, created)
        self.assertEqual(position.updated, opened)
        self.assertEqual(position.opened, opened)
        self.assertIsNone(position.closed)
        self.assertTrue(position.has_trades)
        self.assertFalse(position.is_new)
        self.assertFalse(position.is_closed)
        self.assertEqual(position.average_price, 1.5)
        with self.assertRaises(PositionError):
            input_dict['opened'] = created - timedelta(0, 1)
            Position.from_dict(input_dict)

        input_dict['base_quantity'] = 0
        input_dict['quote_quantity'] = 15
        input_dict['status'] = Position.STATUS_CLOSED
        input_dict['opened'] = opened
        input_dict['closed'] = opened + timedelta(0, 1)
        position = Position.from_dict(input_dict)
        self.assertEqual(position.direction, self.position.direction)
        self.assertEqual(position.base_quantity, 0)
        self.assertEqual(position.quote_quantity, 15)
        self.assertEqual(position.status, Position.STATUS_CLOSED)
        self.assertEqual(position.created, created)
        self.assertEqual(position.opened, opened)
        self.assertEqual(position.closed, input_dict['closed'])
        self.assertEqual(position.updated, position.closed)
        self.assertTrue(position.has_trades)
        self.assertFalse(position.is_new)
        self.assertTrue(position.is_closed)
        self.assertEqual(position.average_price, 0)
        with self.assertRaises(PositionError):
            input_dict['closed'] = opened - timedelta(0, 1)
            Position.from_dict(input_dict)
        with self.assertRaises(PositionError):
            input_dict['status'] = Position.STATUS_OPENED
            Position.from_dict(input_dict)

        self.assertEqual(position.updated, max(position.created, position.opened, position.closed))

    def test_create_and_open(self):
        opened = datetime.now(timezone.utc)
        position = Position.create_and_open(self.position.direction, 5, 2.5, opened=opened)
        self.assertEqual(position.direction, self.position.direction)
        self.assertEqual(position.base_quantity, 5 * self.position.direction)
        self.assertEqual(position.quote_quantity, -12.5 * self.position.direction)
        self.assertEqual(position.status, Position.STATUS_OPENED)
        self.assertEqual(position.created, opened)
        self.assertEqual(position.updated, opened)
        self.assertEqual(position.opened, opened)
        self.assertIsNone(position.closed)
        self.assertTrue(position.has_trades)
        self.assertFalse(position.is_new)
        self.assertFalse(position.is_closed)
        self.assertEqual(position.average_price, 2.5)


class TestShortPosition(TestLongPosition):
    def setUp(self):
        self.created = datetime.now(timezone.utc) - timedelta(0, 1)
        self.position = Position(Position.DIRECTION_SHORT, created=self.created)

    def test_initialization(self):
        super().test_initialization()
        self.assertEqual(self.position.created, self.created)


if __name__ == '__main__':
    unittest.main()
