import unittest
from typing import Any, Dict

from amarket.base import SignalGeneratorBase
from pandas import DataFrame, Series


class SomeSignalGeneratorForTest(SignalGeneratorBase):
    """Test implementation of SignalGeneratorBase for testing purposes."""
    def __init__(self, param1: str = "default1", param2: int = 42):
        self.param1 = param1
        self.param2 = param2

    def featurize(self, dataframe: DataFrame) -> DataFrame:
        return DataFrame([], columns=['test_col1', 'test_col2', 'mixed_col3'])

    def generate_long_signals(self, dataframe: DataFrame) -> Series: pass
    def generate_short_signals(self, dataframe: DataFrame) -> Series: pass

    @classmethod
    def get_column_to_parameters_mapping(cls) -> dict[str, list[str]]:
        return {'test_col1': ['param1'], 'test_col2': ['param2'], 'mixed_col3': ['param1', 'param2']}

    @classmethod
    def get_parameter_to_columns_mapping(cls) -> dict[str, list[str]]:
        return {'param1': ['test_col1', 'mixed_col3'], 'param2': ['test_col2', 'mixed_col3']}


class TestSignalGeneratorBase(unittest.TestCase):
    """Test cases for SignalGeneratorBase class."""

    def setUp(self):
        self.dataframe = DataFrame()
        self.signal_generator = SomeSignalGeneratorForTest()
        self.expected_default_config = {'param1': 'default1', 'param2': 42}

    def test_config_methods(self):
        # Test that get_default_config returns correct default values
        default_config = SomeSignalGeneratorForTest.get_default_parameters()
        actual_config = self.signal_generator.get_actual_parameters()
        self.assertDictEqual(default_config, self.expected_default_config)
        self.assertDictEqual(default_config, actual_config)

        # Test that validate_parameters returns True for valid configuration
        self.assertTrue(SomeSignalGeneratorForTest.validate_parameters({'param1': 'test_value', 'param2': 100}))

        # Test that validate_parameters returns False for invalid configuration
        invalid_config: Dict[str, Any] = {
            'param1': 'test_value'
            # Missing param2
        }
        self.assertFalse(SomeSignalGeneratorForTest.validate_parameters(invalid_config))

        # Test that validate_parameters returns False for empty configuration
        self.assertFalse(SomeSignalGeneratorForTest.validate_parameters({}))

    def test_hash_and_equality_magic_methods(self):
        # Test that hash method works correctly
        obj2 = SomeSignalGeneratorForTest()
        obj3 = SomeSignalGeneratorForTest(param1="different")

        # Objects with same parameters should have same hash
        self.assertEqual(hash(self.signal_generator), hash(obj2))
        self.assertIsNot(self.signal_generator, obj2)  # but they are not the same object

        # Objects with different parameters should have different hash
        self.assertNotEqual(hash(self.signal_generator), hash(obj3))
        self.assertIsNot(self.signal_generator, obj3)  # but they are not the same object

        # Test equality
        self.assertEqual(self.signal_generator, obj2)
        self.assertNotEqual(self.signal_generator, obj3)

        # Test that objects are equal to themselves
        self.assertEqual(self.signal_generator, self.signal_generator)

        # Test that different types are not equal
        self.assertNotEqual(self.signal_generator, "not_a_signal_generator")

    def test_repr_method(self):
        # Test that repr method works correctly
        repr_str = repr(self.signal_generator)
        self.assertIn("SomeSignalGeneratorForTest", repr_str)
        self.assertIn("param1='default1'", repr_str)
        self.assertIn("param2=42", repr_str)

        # Test with different parameters
        obj2 = SomeSignalGeneratorForTest(param1="custom", param2=100)
        repr_str2 = repr(obj2)
        self.assertIn("param1='custom'", repr_str2)
        self.assertIn("param2=100", repr_str2)

    def test_feature_mapping_methods(self):
        # Test get_column_to_parameter_mapping
        feature_columns = self.signal_generator.featurize(self.dataframe).columns.to_list()
        col_to_param = self.signal_generator.get_column_to_parameters_mapping()
        self.assertEqual(col_to_param,
                         {'test_col1': ['param1'], 'test_col2': ['param2'], 'mixed_col3': ['param1', 'param2']})
        self.assertListEqual(feature_columns, list(col_to_param.keys()))

        # Test get_parameter_to_column_mapping
        param_to_col = self.signal_generator.get_parameter_to_columns_mapping()
        self.assertEqual(param_to_col, {'param1': ['test_col1', 'mixed_col3'], 'param2': ['test_col2', 'mixed_col3']})

        # Test get_feature_info
        info = self.signal_generator.get_feature_info()
        self.assertIn('columns', info)
        self.assertIn('parameters', info)
        self.assertIn('column_to_parameters', info)
        self.assertIn('parameter_to_columns', info)

    def test_validate_feature_columns(self):
        valid_columns = ['test_col1', 'test_col2', 'mixed_col3']  # test with valid columns
        self.assertTrue(SomeSignalGeneratorForTest.validate_feature_columns(valid_columns))

        invalid_columns = ['test_col1', 'test_col2']  # missing 'mixed_col3'
        self.assertFalse(SomeSignalGeneratorForTest.validate_feature_columns(invalid_columns))

        extra_columns = ['test_col1', 'test_col2', 'mixed_col3', 'extra_col']  # extra columns (should still be valid)
        self.assertTrue(SomeSignalGeneratorForTest.validate_feature_columns(extra_columns))

        self.assertFalse(SomeSignalGeneratorForTest.validate_feature_columns([]))  # test with empty columns

        # Test with invalid input type - non-iterable (should not crash)
        # This would cause a TypeError when trying to convert to set
        with self.assertRaises(TypeError):
            SomeSignalGeneratorForTest.validate_feature_columns(42)

    def test_validate(self):
        result = self.signal_generator.validate()
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("errors", result)
        self.assertTrue(result['success'])
        self.assertTrue(result['success'])
        self.assertEqual(result["errors"], [])


if __name__ == '__main__':
    unittest.main()
