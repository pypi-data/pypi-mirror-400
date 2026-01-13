"""
Window functions for ClickHouse.
"""

from typing import Union, Optional, Any
from chpy.orm import Column
from chpy.functions.base import Function


def rowNumber() -> Function:
    """Row number in partition."""
    return Function("row_number")


def rank() -> Function:
    """Rank with gaps."""
    return Function("rank")


def denseRank() -> Function:
    """Rank without gaps."""
    return Function("denseRank")


def percentRank() -> Function:
    """Percent rank."""
    return Function("percentRank")


def cumeDist() -> Function:
    """Cumulative distribution."""
    return Function("cumeDist")


def ntile(n: int) -> Function:
    """Divides into n groups."""
    return Function("ntile", n)


def lagInFrame(x: Union[Column, Any], offset: int = 1, default: Optional[Any] = None) -> Function:
    """Lag value in frame."""
    if default is not None:
        return Function("lagInFrame", x, offset, default)
    return Function("lagInFrame", x, offset)


def leadInFrame(x: Union[Column, Any], offset: int = 1, default: Optional[Any] = None) -> Function:
    """Lead value in frame."""
    if default is not None:
        return Function("leadInFrame", x, offset, default)
    return Function("leadInFrame", x, offset)


def firstValue(x: Union[Column, Any]) -> Function:
    """First value in frame."""
    return Function("firstValue", x)


def lastValue(x: Union[Column, Any]) -> Function:
    """Last value in frame."""
    return Function("lastValue", x)


def nthValue(x: Union[Column, Any], n: int) -> Function:
    """Nth value in frame."""
    return Function("nthValue", x, n)

