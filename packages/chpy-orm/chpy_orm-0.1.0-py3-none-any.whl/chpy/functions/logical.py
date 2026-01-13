"""
Logical functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def and_(a: Union[Column, bool], b: Union[Column, bool]) -> Function:
    """Returns true if both a and b are true."""
    return Function("and", a, b)


def or_(a: Union[Column, bool], b: Union[Column, bool]) -> Function:
    """Returns true if either a or b is true."""
    return Function("or", a, b)


def not_(x: Union[Column, bool]) -> Function:
    """Returns logical negation."""
    return Function("not", x)


def xor(a: Union[Column, bool], b: Union[Column, bool]) -> Function:
    """Returns exclusive OR."""
    return Function("xor", a, b)

