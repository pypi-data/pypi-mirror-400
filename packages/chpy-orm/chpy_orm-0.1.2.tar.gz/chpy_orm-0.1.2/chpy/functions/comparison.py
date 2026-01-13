"""
Comparison functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def equals(a: Union[Column, Any], b: Union[Column, Any]) -> Function:
    """Returns true if a equals b."""
    return Function("equals", a, b)


def notEquals(a: Union[Column, Any], b: Union[Column, Any]) -> Function:
    """Returns true if a does not equal b."""
    return Function("notEquals", a, b)


def less(a: Union[Column, Any], b: Union[Column, Any]) -> Function:
    """Returns true if a is less than b."""
    return Function("less", a, b)


def greater(a: Union[Column, Any], b: Union[Column, Any]) -> Function:
    """Returns true if a is greater than b."""
    return Function("greater", a, b)


def lessOrEquals(a: Union[Column, Any], b: Union[Column, Any]) -> Function:
    """Returns true if a is less than or equal to b."""
    return Function("lessOrEquals", a, b)


def greaterOrEquals(a: Union[Column, Any], b: Union[Column, Any]) -> Function:
    """Returns true if a is greater than or equal to b."""
    return Function("greaterOrEquals", a, b)

