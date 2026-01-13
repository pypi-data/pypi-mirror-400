"""
String functions for ClickHouse.
"""

from typing import Union, List, Optional
from chpy.orm import Column
from chpy.functions.base import Function


def length(s: Union[Column, str]) -> Function:
    """Returns length of string."""
    return Function("length", s)


def empty(s: Union[Column, str]) -> Function:
    """Returns true if string is empty."""
    return Function("empty", s)


def notEmpty(s: Union[Column, str]) -> Function:
    """Returns true if string is not empty."""
    return Function("notEmpty", s)


def lengthUTF8(s: Union[Column, str]) -> Function:
    """Returns UTF-8 length."""
    return Function("lengthUTF8", s)


def lower(s: Union[Column, str]) -> Function:
    """Converts to lowercase."""
    return Function("lower", s)


def upper(s: Union[Column, str]) -> Function:
    """Converts to uppercase."""
    return Function("upper", s)


def lowerUTF8(s: Union[Column, str]) -> Function:
    """Converts to lowercase (UTF-8)."""
    return Function("lowerUTF8", s)


def upperUTF8(s: Union[Column, str]) -> Function:
    """Converts to uppercase (UTF-8)."""
    return Function("upperUTF8", s)


def reverse(s: Union[Column, str]) -> Function:
    """Reverses string."""
    return Function("reverse", s)


def reverseUTF8(s: Union[Column, str]) -> Function:
    """Reverses string (UTF-8)."""
    return Function("reverseUTF8", s)


def concat(*args: Union[Column, str]) -> Function:
    """Concatenates strings."""
    return Function("concat", *args)


def concatAssumeInjective(*args: Union[Column, str]) -> Function:
    """Concatenates strings (assumes injective)."""
    return Function("concatAssumeInjective", *args)


def substring(s: Union[Column, str], offset: Union[Column, int], length: Union[Column, int]) -> Function:
    """Extracts substring."""
    return Function("substring", s, offset, length)


def substringUTF8(s: Union[Column, str], offset: Union[Column, int], length: Union[Column, int]) -> Function:
    """Extracts substring (UTF-8)."""
    return Function("substringUTF8", s, offset, length)


def appendTrailingCharIfAbsent(s: Union[Column, str], c: str) -> Function:
    """Appends character if absent."""
    return Function("appendTrailingCharIfAbsent", s, c)


def left(s: Union[Column, str], n: Union[Column, int]) -> Function:
    """Returns left n characters."""
    return Function("left", s, n)


def right(s: Union[Column, str], n: Union[Column, int]) -> Function:
    """Returns right n characters."""
    return Function("right", s, n)


def trimLeft(s: Union[Column, str]) -> Function:
    """Removes leading whitespace."""
    return Function("trimLeft", s)


def trimRight(s: Union[Column, str]) -> Function:
    """Removes trailing whitespace."""
    return Function("trimRight", s)


def trimBoth(s: Union[Column, str]) -> Function:
    """Removes leading and trailing whitespace."""
    return Function("trimBoth", s)


def format(pattern: str, *args: Union[Column, str, int, float]) -> Function:
    """Formats string using pattern."""
    return Function("format", pattern, *args)


def formatReadableQuantity(x: Union[Column, int, float]) -> Function:
    """Formats number as readable quantity."""
    return Function("formatReadableQuantity", x)


def formatReadableSize(x: Union[Column, int, float]) -> Function:
    """Formats bytes as readable size."""
    return Function("formatReadableSize", x)


def formatReadableTimeDelta(seconds: Union[Column, int, float]) -> Function:
    """Formats seconds as time delta."""
    return Function("formatReadableTimeDelta", seconds)


def splitByChar(sep: str, s: Union[Column, str]) -> Function:
    """Splits string by character."""
    return Function("splitByChar", sep, s)


def splitByString(sep: str, s: Union[Column, str]) -> Function:
    """Splits string by string."""
    return Function("splitByString", sep, s)


def arrayStringConcat(arr: Union[Column, List[str]], sep: str) -> Function:
    """Concatenates array of strings."""
    return Function("arrayStringConcat", arr, sep)


def alphaTokens(s: Union[Column, str]) -> Function:
    """Extracts alphabetic tokens."""
    return Function("alphaTokens", s)


def extractAll(s: Union[Column, str], re: str) -> Function:
    """Extracts all matches of regex."""
    return Function("extractAll", s, re)


def extractAllGroups(s: Union[Column, str], re: str) -> Function:
    """Extracts all regex groups."""
    return Function("extractAllGroups", s, re)


def extractGroups(s: Union[Column, str], re: str) -> Function:
    """Extracts regex groups."""
    return Function("extractGroups", s, re)


def like(s: Union[Column, str], pattern: str) -> Function:
    """Pattern matching."""
    return Function("like", s, pattern)


def notLike(s: Union[Column, str], pattern: str) -> Function:
    """Negated pattern matching."""
    return Function("notLike", s, pattern)


def match(s: Union[Column, str], pattern: str) -> Function:
    """Regex matching."""
    return Function("match", s, pattern)


def multiMatchAny(s: Union[Column, str], patterns: List[str]) -> Function:
    """Matches any pattern."""
    return Function("multiMatchAny", s, patterns)


def multiMatchAnyIndex(s: Union[Column, str], patterns: List[str]) -> Function:
    """Returns index of matched pattern."""
    return Function("multiMatchAnyIndex", s, patterns)


def multiFuzzyMatchAny(s: Union[Column, str], distance: int, patterns: List[str]) -> Function:
    """Fuzzy matches any pattern."""
    return Function("multiFuzzyMatchAny", s, distance, patterns)


def replace(s: Union[Column, str], pattern: str, replacement: str) -> Function:
    """Replaces pattern."""
    return Function("replace", s, pattern, replacement)


def replaceAll(s: Union[Column, str], pattern: str, replacement: str) -> Function:
    """Replaces all occurrences."""
    return Function("replaceAll", s, pattern, replacement)


def replaceOne(s: Union[Column, str], pattern: str, replacement: str) -> Function:
    """Replaces first occurrence."""
    return Function("replaceOne", s, pattern, replacement)


def replaceRegexpOne(s: Union[Column, str], pattern: str, replacement: str) -> Function:
    """Replaces using regex."""
    return Function("replaceRegexpOne", s, pattern, replacement)


def replaceRegexpAll(s: Union[Column, str], pattern: str, replacement: str) -> Function:
    """Replaces all using regex."""
    return Function("replaceRegexpAll", s, pattern, replacement)


def position(haystack: Union[Column, str], needle: str) -> Function:
    """Returns position of needle."""
    return Function("position", haystack, needle)


def positionUTF8(haystack: Union[Column, str], needle: str) -> Function:
    """Returns position (UTF-8)."""
    return Function("positionUTF8", haystack, needle)


def positionCaseInsensitive(haystack: Union[Column, str], needle: str) -> Function:
    """Case-insensitive position."""
    return Function("positionCaseInsensitive", haystack, needle)


def positionCaseInsensitiveUTF8(haystack: Union[Column, str], needle: str) -> Function:
    """Case-insensitive position (UTF-8)."""
    return Function("positionCaseInsensitiveUTF8", haystack, needle)


def startsWith(s: Union[Column, str], prefix: str) -> Function:
    """Checks if string starts with prefix."""
    return Function("startsWith", s, prefix)


def endsWith(s: Union[Column, str], suffix: str) -> Function:
    """Checks if string ends with suffix."""
    return Function("endsWith", s, suffix)


def base64Encode(s: Union[Column, str]) -> Function:
    """Encodes to base64."""
    return Function("base64Encode", s)


def base64Decode(s: Union[Column, str]) -> Function:
    """Decodes from base64."""
    return Function("base64Decode", s)


def tryBase64Decode(s: Union[Column, str]) -> Function:
    """Decodes from base64 (returns empty on error)."""
    return Function("tryBase64Decode", s)


def hex(x: Union[Column, str, int]) -> Function:
    """Converts to hexadecimal."""
    return Function("hex", x)


def unhex(x: Union[Column, str]) -> Function:
    """Converts from hexadecimal."""
    return Function("unhex", x)


def UUIDStringToNum(s: Union[Column, str]) -> Function:
    """Converts UUID string to number."""
    return Function("UUIDStringToNum", s)


def UUIDNumToString(x: Union[Column, int]) -> Function:
    """Converts UUID number to string."""
    return Function("UUIDNumToString", x)


def bitmaskToList(x: Union[Column, int]) -> Function:
    """Converts bitmask to list."""
    return Function("bitmaskToList", x)


def bitmaskToArray(x: Union[Column, int]) -> Function:
    """Converts bitmask to array."""
    return Function("bitmaskToArray", x)

