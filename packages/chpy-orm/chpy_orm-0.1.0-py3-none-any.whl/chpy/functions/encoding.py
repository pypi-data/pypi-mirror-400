"""
Encoding functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def hex(x: Union[Column, str, int]) -> Function:
    """Converts to hexadecimal."""
    return Function("hex", x)


def unhex(x: Union[Column, str]) -> Function:
    """Converts from hexadecimal."""
    return Function("unhex", x)


def base64Encode(x: Union[Column, str]) -> Function:
    """Encodes to base64."""
    return Function("base64Encode", x)


def base64Decode(x: Union[Column, str]) -> Function:
    """Decodes from base64."""
    return Function("base64Decode", x)


def tryBase64Decode(x: Union[Column, str]) -> Function:
    """Decodes from base64 (safe)."""
    return Function("tryBase64Decode", x)


def base32Encode(x: Union[Column, str]) -> Function:
    """Encodes to base32."""
    return Function("base32Encode", x)


def base32Decode(x: Union[Column, str]) -> Function:
    """Decodes from base32."""
    return Function("base32Decode", x)


def base58Encode(x: Union[Column, str]) -> Function:
    """Encodes to base58."""
    return Function("base58Encode", x)


def base58Decode(x: Union[Column, str]) -> Function:
    """Decodes from base58."""
    return Function("base58Decode", x)

