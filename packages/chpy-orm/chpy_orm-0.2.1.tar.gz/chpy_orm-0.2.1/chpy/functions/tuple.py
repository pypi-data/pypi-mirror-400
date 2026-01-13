"""
Tuple functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def tuple(*args: Union[Column, Any]) -> Function:
    """Creates tuple."""
    return Function("tuple", *args)


def tupleElement(tuple_col: Union[Column, tuple], n: int) -> Function:
    """Gets element at index."""
    return Function("tupleElement", tuple_col, n)


def untuple(tuple_col: Union[Column, tuple]) -> Function:
    """Expands tuple to columns."""
    return Function("untuple", tuple_col)

