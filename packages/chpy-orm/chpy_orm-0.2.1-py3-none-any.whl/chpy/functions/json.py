"""
JSON functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def JSONHas(json: Union[Column, str], path: str) -> Function:
    """Checks if JSON has path."""
    return Function("JSONHas", json, path)


def JSONLength(json: Union[Column, str], path: str) -> Function:
    """Returns length of JSON element."""
    return Function("JSONLength", json, path)


def JSONKey(json: Union[Column, str], index: int) -> Function:
    """Returns key at index."""
    return Function("JSONKey", json, index)


def JSONKeys(json: Union[Column, str], path: str) -> Function:
    """Returns array of keys."""
    return Function("JSONKeys", json, path)


def JSONExtract(json: Union[Column, str], path: str, type_name: str) -> Function:
    """Extracts value as specified type."""
    return Function("JSONExtract", json, path, type_name)


def JSONExtractString(json: Union[Column, str], path: str) -> Function:
    """Extracts string value."""
    return Function("JSONExtractString", json, path)


def JSONExtractInt(json: Union[Column, str], path: str) -> Function:
    """Extracts integer value."""
    return Function("JSONExtractInt", json, path)


def JSONExtractFloat(json: Union[Column, str], path: str) -> Function:
    """Extracts float value."""
    return Function("JSONExtractFloat", json, path)


def JSONExtractBool(json: Union[Column, str], path: str) -> Function:
    """Extracts boolean value."""
    return Function("JSONExtractBool", json, path)


def JSONExtractRaw(json: Union[Column, str], path: str) -> Function:
    """Extracts raw JSON."""
    return Function("JSONExtractRaw", json, path)


def JSONExtractArrayRaw(json: Union[Column, str], path: str) -> Function:
    """Extracts array as raw JSON."""
    return Function("JSONExtractArrayRaw", json, path)


def JSONExtractKeysAndValues(json: Union[Column, str], path: str) -> Function:
    """Extracts keys and values."""
    return Function("JSONExtractKeysAndValues", json, path)


def JSONExtractKeysAndValuesRaw(json: Union[Column, str], path: str) -> Function:
    """Extracts keys and values as raw."""
    return Function("JSONExtractKeysAndValuesRaw", json, path)


def JSONExtractUInt(json: Union[Column, str], path: str) -> Function:
    """Extracts unsigned integer."""
    return Function("JSONExtractUInt", json, path)

