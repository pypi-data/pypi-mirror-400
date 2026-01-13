"""
Other functions for ClickHouse.
"""

from typing import Union, Any, Optional
from chpy.orm import Column
from chpy.functions.base import Function


def hostName() -> Function:
    """Returns hostname."""
    return Function("hostName")


def getMacro(name: str) -> Function:
    """Gets macro value."""
    return Function("getMacro", name)


def FQDN() -> Function:
    """Returns fully qualified domain name."""
    return Function("FQDN")


def basename(path: Union[Column, str]) -> Function:
    """Returns basename of path."""
    return Function("basename", path)


def visibleWidth(x: Union[Column, Any]) -> Function:
    """Returns visible width."""
    return Function("visibleWidth", x)


def toTypeName(x: Union[Column, Any]) -> Function:
    """Returns type name."""
    return Function("toTypeName", x)


def blockSize() -> Function:
    """Returns block size."""
    return Function("blockSize")


def blockNumber() -> Function:
    """Returns block number."""
    return Function("blockNumber")


def rowNumberInBlock() -> Function:
    """Returns row number in block."""
    return Function("rowNumberInBlock")


def rowNumberInAllBlocks() -> Function:
    """Returns row number in all blocks."""
    return Function("rowNumberInAllBlocks")


def neighbor(column: Column, offset: int, default: Optional[Any] = None) -> Function:
    """Gets neighbor value."""
    if default is not None:
        return Function("neighbor", column, offset, default)
    return Function("neighbor", column, offset)


def runningAccumulate(x: Union[Column, Any]) -> Function:
    """Running accumulation."""
    return Function("runningAccumulate", x)


def runningDifference(x: Union[Column, Any]) -> Function:
    """Running difference."""
    return Function("runningDifference", x)


def runningDifferenceStartingWithFirstValue(x: Union[Column, Any]) -> Function:
    """Running difference starting with first."""
    return Function("runningDifferenceStartingWithFirstValue", x)


def finalizeAggregation(state: Union[Column, Any]) -> Function:
    """Finalizes aggregation state."""
    return Function("finalizeAggregation", state)

