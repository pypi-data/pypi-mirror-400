"""
Rounding functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def round(x: Union[Column, float]) -> Function:
    """Rounds to nearest integer."""
    return Function("round", x)


def roundBankers(x: Union[Column, float]) -> Function:
    """Banker's rounding."""
    return Function("roundBankers", x)


def floor(x: Union[Column, float]) -> Function:
    """Rounds down."""
    return Function("floor", x)


def ceil(x: Union[Column, float]) -> Function:
    """Rounds up."""
    return Function("ceil", x)


def trunc(x: Union[Column, float]) -> Function:
    """Truncates toward zero."""
    return Function("trunc", x)


def roundToExp2(x: Union[Column, float]) -> Function:
    """Rounds to power of 2."""
    return Function("roundToExp2", x)


def roundDuration(x: Union[Column, float]) -> Function:
    """Rounds duration."""
    return Function("roundDuration", x)


def roundAge(x: Union[Column, float]) -> Function:
    """Rounds age."""
    return Function("roundAge", x)


def roundDown(x: Union[Column, float], n: int) -> Function:
    """Rounds down to n decimal places."""
    return Function("roundDown", x, n)

