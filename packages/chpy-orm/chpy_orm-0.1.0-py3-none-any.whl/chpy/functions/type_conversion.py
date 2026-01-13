"""
Type conversion functions for ClickHouse.
"""

from typing import Union, Any
from chpy.orm import Column
from chpy.functions.base import Function


def toInt8(x: Union[Column, Any]) -> Function:
    """Converts to 8-bit integer."""
    return Function("toInt8", x)


def toInt16(x: Union[Column, Any]) -> Function:
    """Converts to 16-bit integer."""
    return Function("toInt16", x)


def toInt32(x: Union[Column, Any]) -> Function:
    """Converts to 32-bit integer."""
    return Function("toInt32", x)


def toInt64(x: Union[Column, Any]) -> Function:
    """Converts to 64-bit integer."""
    return Function("toInt64", x)


def toUInt8(x: Union[Column, Any]) -> Function:
    """Converts to unsigned 8-bit integer."""
    return Function("toUInt8", x)


def toUInt16(x: Union[Column, Any]) -> Function:
    """Converts to unsigned 16-bit integer."""
    return Function("toUInt16", x)


def toUInt32(x: Union[Column, Any]) -> Function:
    """Converts to unsigned 32-bit integer."""
    return Function("toUInt32", x)


def toUInt64(x: Union[Column, Any]) -> Function:
    """Converts to unsigned 64-bit integer."""
    return Function("toUInt64", x)


def toFloat32(x: Union[Column, Any]) -> Function:
    """Converts to 32-bit float."""
    return Function("toFloat32", x)


def toFloat64(x: Union[Column, Any]) -> Function:
    """Converts to 64-bit float."""
    return Function("toFloat64", x)


def toDate(x: Union[Column, Any]) -> Function:
    """Converts to Date."""
    return Function("toDate", x)


def toDateTime(x: Union[Column, Any]) -> Function:
    """Converts to DateTime."""
    return Function("toDateTime", x)


def toDateTime64(x: Union[Column, Any], precision: int) -> Function:
    """Converts to DateTime64."""
    return Function("toDateTime64", x, precision)


def toString(x: Union[Column, Any]) -> Function:
    """Converts to String."""
    return Function("toString", x)


def toFixedString(x: Union[Column, Any], n: int) -> Function:
    """Converts to FixedString of length n."""
    return Function("toFixedString", x, n)


def toDecimal32(x: Union[Column, Any], scale: int) -> Function:
    """Converts to Decimal32."""
    return Function("toDecimal32", x, scale)


def toDecimal64(x: Union[Column, Any], scale: int) -> Function:
    """Converts to Decimal64."""
    return Function("toDecimal64", x, scale)


def toDecimal128(x: Union[Column, Any], scale: int) -> Function:
    """Converts to Decimal128."""
    return Function("toDecimal128", x, scale)


def toDecimal256(x: Union[Column, Any], scale: int) -> Function:
    """Converts to Decimal256."""
    return Function("toDecimal256", x, scale)


def toUUID(x: Union[Column, Any]) -> Function:
    """Converts to UUID."""
    return Function("toUUID", x)


def toIPv4(x: Union[Column, Any]) -> Function:
    """Converts to IPv4."""
    return Function("toIPv4", x)


def toIPv6(x: Union[Column, Any]) -> Function:
    """Converts to IPv6."""
    return Function("toIPv6", x)


def parseDateTimeBestEffort(x: Union[Column, str]) -> Function:
    """Parses DateTime from string."""
    return Function("parseDateTimeBestEffort", x)


def parseDateTimeBestEffortUS(x: Union[Column, str]) -> Function:
    """Parses DateTime (US format)."""
    return Function("parseDateTimeBestEffortUS", x)


def parseDateTime32BestEffort(x: Union[Column, str]) -> Function:
    """Parses DateTime32 from string."""
    return Function("parseDateTime32BestEffort", x)


def CAST(x: Union[Column, Any], type_name: str) -> Function:
    """Casts x to specified type."""
    return Function("CAST", x, type_name)

