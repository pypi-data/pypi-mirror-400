"""
Nullable functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def isNull(x: Union[Column, Any]) -> Function:
    """Returns true if x is null."""
    return Function("isNull", x)


def isNotNull(x: Union[Column, Any]) -> Function:
    """Returns true if x is not null."""
    return Function("isNotNull", x)


def coalesce(*args: Union[Column, Any]) -> Function:
    """Returns first non-null value."""
    return Function("coalesce", *args)


def ifNull(x: Union[Column, Any], y: Union[Column, Any]) -> Function:
    """Returns x if not null, y otherwise."""
    return Function("ifNull", x, y)


def nullIf(x: Union[Column, Any], y: Union[Column, Any]) -> Function:
    """Returns null if x equals y."""
    return Function("nullIf", x, y)


def assumeNotNull(x: Union[Column, Any]) -> Function:
    """Assumes x is not null."""
    return Function("assumeNotNull", x)

