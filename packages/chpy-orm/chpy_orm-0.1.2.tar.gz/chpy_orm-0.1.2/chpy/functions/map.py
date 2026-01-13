"""
Map functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def map(*args: Union[Column, Any]) -> Function:
    """Creates map from key-value pairs."""
    return Function("map", *args)


def mapKeys(map_col: Union[Column, dict]) -> Function:
    """Returns array of keys."""
    return Function("mapKeys", map_col)


def mapValues(map_col: Union[Column, dict]) -> Function:
    """Returns array of values."""
    return Function("mapValues", map_col)


def mapContains(map_col: Union[Column, dict], key: Any) -> Function:
    """Checks if map contains key."""
    return Function("mapContains", map_col, key)


def mapGet(map_col: Union[Column, dict], key: Any, default: Any = None) -> Function:
    """Gets value with default."""
    if default is not None:
        return Function("mapGet", map_col, key, default)
    return Function("mapGet", map_col, key)

