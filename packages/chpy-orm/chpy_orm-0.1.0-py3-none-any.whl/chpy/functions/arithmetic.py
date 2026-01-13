"""
Arithmetic functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def plus(a: Union[Column, float, int], b: Union[Column, float, int]) -> Function:
    """Returns the sum of a and b."""
    return Function("plus", a, b)


def minus(a: Union[Column, float, int], b: Union[Column, float, int]) -> Function:
    """Returns the difference of a and b."""
    return Function("minus", a, b)


def multiply(a: Union[Column, float, int], b: Union[Column, float, int]) -> Function:
    """Returns the product of a and b."""
    return Function("multiply", a, b)


def divide(a: Union[Column, float, int], b: Union[Column, float, int]) -> Function:
    """Returns the quotient of a divided by b."""
    return Function("divide", a, b)


def intDiv(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Integer division."""
    return Function("intDiv", a, b)


def intDivOrZero(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Integer division, returns 0 on division by zero."""
    return Function("intDivOrZero", a, b)


def modulo(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Returns the remainder of division."""
    return Function("modulo", a, b)


def negate(x: Union[Column, float, int]) -> Function:
    """Returns negated value."""
    return Function("negate", x)


def abs(x: Union[Column, float, int]) -> Function:
    """Returns absolute value."""
    return Function("abs", x)


def gcd(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Returns greatest common divisor."""
    return Function("gcd", a, b)


def lcm(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Returns least common multiple."""
    return Function("lcm", a, b)

