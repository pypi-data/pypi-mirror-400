"""
UUID functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def generateUUIDv4() -> Function:
    """Generates UUID v4."""
    return Function("generateUUIDv4")


def toUUID(x: Union[Column, str]) -> Function:
    """Converts to UUID."""
    return Function("toUUID", x)


def UUIDStringToNum(s: Union[Column, str]) -> Function:
    """Converts UUID string to number."""
    return Function("UUIDStringToNum", s)


def UUIDNumToString(x: Union[Column, int]) -> Function:
    """Converts UUID number to string."""
    return Function("UUIDNumToString", x)

