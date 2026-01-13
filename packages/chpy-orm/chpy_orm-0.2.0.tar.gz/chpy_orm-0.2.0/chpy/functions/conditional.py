"""
Conditional functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def if_(cond: Union[Column, bool], then: Union[Column, Any], else_: Union[Column, Any]) -> Function:
    """Returns then if cond is true, else otherwise."""
    return Function("if", cond, then, else_)


def multiIf(*args: Union[Column, Any]) -> Function:
    """Multiple conditions: cond1, then1, cond2, then2, ..., else."""
    return Function("multiIf", *args)


def ifNull(x: Union[Column, Any], y: Union[Column, Any]) -> Function:
    """Returns x if not null, y otherwise."""
    return Function("ifNull", x, y)


def nullIf(x: Union[Column, Any], y: Union[Column, Any]) -> Function:
    """Returns null if x equals y."""
    return Function("nullIf", x, y)


def coalesce(*args: Union[Column, Any]) -> Function:
    """Returns first non-null value."""
    return Function("coalesce", *args)

