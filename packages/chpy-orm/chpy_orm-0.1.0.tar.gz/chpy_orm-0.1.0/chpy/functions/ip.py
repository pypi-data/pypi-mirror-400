"""
IP address functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def toIPv4(x: Union[Column, str]) -> Function:
    """Converts to IPv4."""
    return Function("toIPv4", x)


def toIPv6(x: Union[Column, str]) -> Function:
    """Converts to IPv6."""
    return Function("toIPv6", x)


def IPv4NumToString(x: Union[Column, int]) -> Function:
    """Converts IPv4 number to string."""
    return Function("IPv4NumToString", x)


def IPv4StringToNum(s: Union[Column, str]) -> Function:
    """Converts IPv4 string to number."""
    return Function("IPv4StringToNum", s)


def IPv6NumToString(x: Union[Column, int]) -> Function:
    """Converts IPv6 number to string."""
    return Function("IPv6NumToString", x)


def IPv6StringToNum(s: Union[Column, str]) -> Function:
    """Converts IPv6 string to number."""
    return Function("IPv6StringToNum", s)


def IPv4CIDRToRange(ip: Union[Column, str], prefix: int) -> Function:
    """Converts CIDR to range."""
    return Function("IPv4CIDRToRange", ip, prefix)


def IPv6CIDRToRange(ip: Union[Column, str], prefix: int) -> Function:
    """Converts IPv6 CIDR to range."""
    return Function("IPv6CIDRToRange", ip, prefix)


def IPv4ToIPv6(x: Union[Column, str]) -> Function:
    """Converts IPv4 to IPv6."""
    return Function("IPv4ToIPv6", x)


def cutIPv6(x: Union[Column, str], bytes_to_cut: int) -> Function:
    """Cuts IPv6 address."""
    return Function("cutIPv6", x, bytes_to_cut)

