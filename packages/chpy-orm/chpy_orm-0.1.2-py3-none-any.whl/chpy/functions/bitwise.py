"""
Bitwise functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def bitAnd(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Bitwise AND."""
    return Function("bitAnd", a, b)


def bitOr(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Bitwise OR."""
    return Function("bitOr", a, b)


def bitXor(a: Union[Column, int], b: Union[Column, int]) -> Function:
    """Bitwise XOR."""
    return Function("bitXor", a, b)


def bitNot(x: Union[Column, int]) -> Function:
    """Bitwise NOT."""
    return Function("bitNot", x)


def bitShiftLeft(x: Union[Column, int], n: Union[Column, int]) -> Function:
    """Left shift."""
    return Function("bitShiftLeft", x, n)


def bitShiftRight(x: Union[Column, int], n: Union[Column, int]) -> Function:
    """Right shift."""
    return Function("bitShiftRight", x, n)


def bitRotateLeft(x: Union[Column, int], n: Union[Column, int]) -> Function:
    """Rotate left."""
    return Function("bitRotateLeft", x, n)


def bitRotateRight(x: Union[Column, int], n: Union[Column, int]) -> Function:
    """Rotate right."""
    return Function("bitRotateRight", x, n)


def bitTest(x: Union[Column, int], n: Union[Column, int]) -> Function:
    """Tests bit at position n."""
    return Function("bitTest", x, n)


def bitTestAll(x: Union[Column, int], mask: Union[Column, int]) -> Function:
    """Tests if all bits in mask are set."""
    return Function("bitTestAll", x, mask)


def bitTestAny(x: Union[Column, int], mask: Union[Column, int]) -> Function:
    """Tests if any bit in mask is set."""
    return Function("bitTestAny", x, mask)


def bitCount(x: Union[Column, int]) -> Function:
    """Counts set bits."""
    return Function("bitCount", x)

