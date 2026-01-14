import unittest
from decimal import Decimal
from time import time

from amarket.constants import (
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL,
    MarketType,
)
from amarket.interfaces.i_order import IOrder
from amarket.local.local_market import LocalMarket
from amarket.local.local_order import LocalOrder
from test_utils import check_primitive_types


class TestLocalOrder(unittest.TestCase):
    """Test cases for the LocalOrder class."""

    def setUp(self):
        self.market = LocalMarket(exchange='Exchange_1', market_type="spot", symbol="BTCUSDT",
                                  base_ticker="BTC", quote_ticker="USDT", lot_precision=4, price_precision=2)
        self.order = LocalOrder(market=self.market, order_id=1001, owner='owner#1',
                                client_order_id="test_client_1", side=SIDE_BUY, order_type="LIMIT", status="NEW",
                                quantity=1.5, price=100.0, create_time=int(time()), update_time=int(time()))
        self.validation = self.order.validate()

        # Create valid order dictionaries
        self.valid_limit_order = {
            'market': self.market,
            'order_id': 123456,
            'owner': 'owner#1',
            'client_order_id': 'some_client_order_id_123456',
            'side': SIDE_BUY,
            'order_type': ORDER_TYPE_LIMIT,
            'status': 'NEW',
            'quantity': Decimal('1.0'),
            'price': Decimal('30000.0'),
            'create_time': int(time()),
            'update_time': int(time()),
            'provider_data': {'some_key': 'some_value'}
        }
        self.valid_market_order = {
            'market': self.market,
            'order_id': 654321,
            'owner': 'owner#1',
            'client_order_id': 'some_client_order_id_654321',
            'side': SIDE_SELL,
            'order_type': ORDER_TYPE_MARKET,
            'status': 'FILLED',
            'quantity': Decimal('0.5'),
            'price': None,  # Price can be None for MARKET orders
            'create_time': int(time()),
            'update_time': int(time()),
        }

    def test_initialization(self):
        """Test successful creation of a LocalOrder instance"""
        self.assertIsInstance(self.order, LocalOrder)
        self.assertIsInstance(self.order, IOrder)
        self.assertIn('success', self.validation)
        self.assertIn('errors', self.validation)
        self.assertTrue(self.validation['success'])
        self.assertEqual(self.validation['errors'], [])
        self.assertTrue(self.order.is_buy)

        # Test properties for exchange, market_type, and symbol
        self.assertEqual(self.order.exchange, self.market.exchange)
        self.assertEqual(self.order.market_type, MarketType.get_market_type_code(self.market.market_type))
        self.assertEqual(self.order.symbol, self.market.symbol)

    def test_to_dict(self):
        """Test the to_dict() method"""
        order_dict = self.order.to_dict()

        # Verify all expected fields are present and values match the order's properties
        expected_fields = ["market", "order_id", "owner", "client_order_id", "side",
                           "order_type", "status", "quantity", "price", "create_time", "update_time",
                           "check_time", "provider_data", "history", "exchange", "market_type", "symbol"]
        for field in expected_fields:
            self.assertIn(field, order_dict)
            if field == 'market':
                self.assertDictEqual(order_dict['market'], self.order.market.to_dict())
            else:
                self.assertEqual(order_dict[field], getattr(self.order, field))

        # Test that to_dict() returns only primitive types and valid nested structures
        result = self.order.to_dict()
        check_primitive_types(result)

    def test_validate(self):
        # Test validation over some missing or invalid properties
        invalid_props = {'market': None, 'order_id': 0, 'status': None}
        for prop, value in invalid_props.items():
            init_value = getattr(self.order, prop)
            setattr(self.order, f'_{prop}', value)
            result = self.order.validate()
            self.assertFalse(result["success"])
            self.assertIn(f"Invalid {prop}", result["errors"][0])
            self.assertEqual(len(result['errors']), 1)
            setattr(self.order, f'_{prop}', init_value)  # restore

        # Test valid orders creation
        for test_order in (self.valid_limit_order, self.valid_market_order):
            order = LocalOrder(**test_order)
            validation_result = order.validate()
            self.assertTrue(validation_result['success'],
                            f"Valid LIMIT order should pass validation, but validation result is: {validation_result}")
            self.assertEqual(len(validation_result['errors']), 0, "No errors expected for valid LIMIT order")

        # Test missing fields
        for field in ['market', 'order_id', 'client_order_id', 'side', 'order_type', 'status', 'quantity',
                      'create_time', 'update_time']:
            for test_order in (self.valid_limit_order, self.valid_market_order):
                order = LocalOrder(**test_order)
                setattr(order,  f'_{field}', None)
                validation_result = order.validate()
                self.assertFalse(validation_result['success'], f"Order missing {field} should fail validation")
                self.assertIn(f"Invalid {field}", validation_result['errors'][0])

        # Test invalid symbol
        order = LocalOrder(**self.valid_limit_order)
        market_symbol = order.market.symbol
        order.market._symbol = ''
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Empty symbol should fail validation")
        self.assertIn("Invalid symbol: must be a non-empty alphanumeric string without spaces",
                      validation_result['errors'])

        order.market._symbol = 12345
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Non-string symbol should fail validation")
        self.assertIn("Invalid symbol: must be a non-empty alphanumeric string without spaces",
                      validation_result['errors'])
        order.market._symbol = market_symbol  # restore the market symbol

        # Test invalid side
        order = LocalOrder(**self.valid_limit_order)
        order._side = 0  # Not SIDE_BUY or SIDE_SELL
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Invalid side should fail validation")
        self.assertIn(f"Invalid side: must be {SIDE_BUY} or {SIDE_SELL}", validation_result['errors'])

        # Test invalid order type
        order = LocalOrder(**self.valid_limit_order)
        order._order_type = 'INVALID'
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Invalid order type should fail validation")
        self.assertIn(f"Invalid order_type: must be '{ORDER_TYPE_LIMIT}' or '{ORDER_TYPE_MARKET}'",
                      validation_result['errors'])

        # Test invalid order ID
        order = LocalOrder(**self.valid_limit_order)
        for order_id, msg in ((0, 'Zero order ID should fail validationn'),
                              (-1, 'Negative order ID should fail validation'),
                              ('12345', 'Non-integer order ID should fail validation')):
            order._order_id = order_id
            validation_result = order.validate()
            self.assertFalse(validation_result['success'], msg)
            self.assertIn("Invalid order_id: must be a positive integer", validation_result['errors'])

        # Test invalid quantity
        order = LocalOrder(**self.valid_limit_order)
        for quantity, msg in ((Decimal('0'), 'Zero quantity should fail validation'),
                              (Decimal('-1.0'), 'Negative quantity should fail validation'),
                              ('1.0', 'Non-Decimal quantity should fail validation')):
            order._quantity = quantity
            validation_result = order.validate()
            self.assertFalse(validation_result['success'], msg)
            self.assertIn("Invalid quantity: must be a positive Decimal", validation_result['errors'])

        # Test invalid price for LIMIT order
        order = LocalOrder(**self.valid_limit_order)
        for price, msg in ((Decimal('0'), 'Zero price should fail validation'),
                           (Decimal('-1.0'), 'Negative price should fail validation'),
                           ('30000', 'Non-Decimal price should fail validation')):
            order._price = price
            validation_result = order.validate()
            self.assertFalse(validation_result['success'], msg)
            self.assertIn("Invalid price for LIMIT order: must be a positive Decimal", validation_result['errors'])

        # Test invalid status
        order._price = Decimal('30000')  # Reset to valid value
        order._status = ''
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Empty status should fail validation")
        self.assertIn("Invalid status: must be a non-empty string", validation_result['errors'])

        order._status = 12345
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Non-string status should fail validation")
        self.assertIn("Invalid status: must be a non-empty string", validation_result['errors'])

        # Test invalid provider_data
        order._provider_data = 'not a dict'
        validation_result = order.validate()
        self.assertFalse(validation_result['success'], "Non-dict provider_data should fail validation")
        self.assertIn("Invalid provider_data: must be a dictionary or None", validation_result['errors'])

    def test_is_buy_and_is_sell_properties(self):
        """Comprehensive test for is_buy and is_sell properties with various scenarios"""
        # Test case 1: SIDE_BUY
        buy_order = LocalOrder(market=self.market, order_id=1, owner='owner#1',
                               client_order_id="test_client_1", side=SIDE_BUY, order_type="LIMIT",
                               status="NEW", quantity=1.5, price=100.0,
                               create_time=int(time()), update_time=int(time()))
        self.assertTrue(buy_order.is_buy, "is_buy should be True when side is SIDE_BUY")
        self.assertFalse(buy_order.is_sell, "is_sell should be False when side is SIDE_BUY")

        # Test case 2: SIDE_SELL
        sell_order = LocalOrder(market=self.market, order_id=2, owner='owner#2',
                                client_order_id="test_client_2", side=SIDE_SELL, order_type="LIMIT",
                                status="NEW", quantity=1.5, price=100.0,
                                create_time=int(time()), update_time=int(time()))
        self.assertTrue(sell_order.is_sell, "is_sell should be True when side is SIDE_SELL")
        self.assertFalse(sell_order.is_buy, "is_buy should be False when side is SIDE_SELL")

        # Test case 3: Invalid side
        invalid_order = LocalOrder(market=self.market, order_id=3, owner='owner#3',
                                   client_order_id="test_client_3", side=0,  # Invalid side
                                   order_type="LIMIT", status="NEW", quantity=1.5,
                                   price=100.0, create_time=int(time()), update_time=int(time()))
        # Both properties should be False for invalid side
        self.assertFalse(invalid_order.is_buy, "is_buy should be False for invalid side")
        self.assertFalse(invalid_order.is_sell, "is_sell should be False for invalid side")

        # Validation should fail
        validation_result = invalid_order.validate()
        self.assertFalse(validation_result['success'], "Validation should fail for invalid side")
        self.assertIn("Invalid side: must be 1 or -1", validation_result['errors'])

        # Test case 4: Edge cases
        for side_value in [SIDE_BUY, SIDE_SELL, 0, 2, -2]:
            edge_order = LocalOrder(market=self.market, order_id=4, owner='owner#4',
                                    client_order_id="test_client_4", side=side_value,
                                    order_type="LIMIT", status="NEW", quantity=1.5,
                                    price=100.0, create_time=int(time()), update_time=int(time()))

            # Check property values based on side
            if side_value == SIDE_BUY:
                self.assertTrue(edge_order.is_buy, f"is_buy should be True for side={side_value}")
                self.assertFalse(edge_order.is_sell, f"is_sell should be False for side={side_value}")
            elif side_value == SIDE_SELL:
                self.assertTrue(edge_order.is_sell, f"is_sell should be True for side={side_value}")
                self.assertFalse(edge_order.is_buy, f"is_buy should be False for side={side_value}")
            else:
                self.assertFalse(edge_order.is_buy, f"is_buy should be False for invalid side={side_value}")
                self.assertFalse(edge_order.is_sell, f"is_sell should be False for invalid side={side_value}")

                # Validation should fail for invalid sides
                validation_result = edge_order.validate()
                self.assertFalse(validation_result['success'], f"Validation should fail for side={side_value}")
                self.assertIn("Invalid side: must be 1 or -1", validation_result['errors'])


if __name__ == "__main__":
    unittest.main()
