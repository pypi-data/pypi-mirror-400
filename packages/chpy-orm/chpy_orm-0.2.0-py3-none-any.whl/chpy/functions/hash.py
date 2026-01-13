"""
Hash functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def halfMD5(x: Union[Column, str]) -> Function:
    """Half MD5 hash."""
    return Function("halfMD5", x)


def MD5(x: Union[Column, str]) -> Function:
    """MD5 hash."""
    return Function("MD5", x)


def SHA1(x: Union[Column, str]) -> Function:
    """SHA1 hash."""
    return Function("SHA1", x)


def SHA224(x: Union[Column, str]) -> Function:
    """SHA224 hash."""
    return Function("SHA224", x)


def SHA256(x: Union[Column, str]) -> Function:
    """SHA256 hash."""
    return Function("SHA256", x)


def SHA512(x: Union[Column, str]) -> Function:
    """SHA512 hash."""
    return Function("SHA512", x)


def cityHash64(x: Union[Column, str]) -> Function:
    """CityHash64."""
    return Function("cityHash64", x)


def farmHash64(x: Union[Column, str]) -> Function:
    """FarmHash64."""
    return Function("farmHash64", x)


def metroHash64(x: Union[Column, str]) -> Function:
    """MetroHash64."""
    return Function("metroHash64", x)


def sipHash64(x: Union[Column, str]) -> Function:
    """SipHash64."""
    return Function("sipHash64", x)


def sipHash128(x: Union[Column, str]) -> Function:
    """SipHash128."""
    return Function("sipHash128", x)


def xxHash32(x: Union[Column, str]) -> Function:
    """xxHash32."""
    return Function("xxHash32", x)


def xxHash64(x: Union[Column, str]) -> Function:
    """xxHash64."""
    return Function("xxHash64", x)


def murmurHash2_32(x: Union[Column, str]) -> Function:
    """MurmurHash2 32-bit."""
    return Function("murmurHash2_32", x)


def murmurHash2_64(x: Union[Column, str]) -> Function:
    """MurmurHash2 64-bit."""
    return Function("murmurHash2_64", x)


def murmurHash3_32(x: Union[Column, str]) -> Function:
    """MurmurHash3 32-bit."""
    return Function("murmurHash3_32", x)


def murmurHash3_64(x: Union[Column, str]) -> Function:
    """MurmurHash3 64-bit."""
    return Function("murmurHash3_64", x)


def murmurHash3_128(x: Union[Column, str]) -> Function:
    """MurmurHash3 128-bit."""
    return Function("murmurHash3_128", x)


def gccMurmurHash(x: Union[Column, str]) -> Function:
    """GCC MurmurHash."""
    return Function("gccMurmurHash", x)

