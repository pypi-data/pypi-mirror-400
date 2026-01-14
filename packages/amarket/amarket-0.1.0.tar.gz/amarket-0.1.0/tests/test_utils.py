#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility functions for testing."""
from decimal import Decimal


def check_primitive_types(data):
    """Recursively check that data contains only primitive types and valid nested structures.

    Args:
        data: The data to check, which can be a dict, list, or primitive type.

    Raises:
        AssertionError: If data contains non-primitive types or invalid nested structures.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            assert isinstance(key, str), f"Dict key must be a string, got {type(key)}"
            check_primitive_types(value)
    elif isinstance(data, list):
        for item in data:
            check_primitive_types(item)
    else:
        assert (
            isinstance(data, (str, int, float, bool, Decimal)) or data is None
        ), (f"Invalid type {type(data)}. "
            f"Must be a primitive type (str, int, float, bool, Decimal, None) or a nested structure.")
