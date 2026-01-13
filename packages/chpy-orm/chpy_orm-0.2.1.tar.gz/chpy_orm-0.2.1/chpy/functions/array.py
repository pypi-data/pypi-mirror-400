"""
Array functions for ClickHouse.
"""

from typing import Union, List, Callable, Any
from chpy.orm import Column
from chpy.functions.base import Function


def array(*args: Union[Column, Any]) -> Function:
    """Creates array."""
    return Function("array", *args)


def arrayConcat(*arrays: Union[Column, List]) -> Function:
    """Concatenates arrays."""
    return Function("arrayConcat", *arrays)


def arrayElement(arr: Union[Column, List], n: Union[Column, int]) -> Function:
    """Gets element at index."""
    return Function("arrayElement", arr, n)


def has(arr: Union[Column, List], elem: Any) -> Function:
    """Checks if array contains element."""
    return Function("has", arr, elem)


def hasAll(arr1: Union[Column, List], arr2: Union[Column, List]) -> Function:
    """Checks if arr1 contains all elements of arr2."""
    return Function("hasAll", arr1, arr2)


def hasAny(arr1: Union[Column, List], arr2: Union[Column, List]) -> Function:
    """Checks if arr1 contains any element of arr2."""
    return Function("hasAny", arr1, arr2)


def indexOf(arr: Union[Column, List], elem: Any) -> Function:
    """Returns index of element."""
    return Function("indexOf", arr, elem)


def countEqual(arr: Union[Column, List], elem: Any) -> Function:
    """Counts occurrences of element."""
    return Function("countEqual", arr, elem)


def arrayEnumerate(arr: Union[Column, List]) -> Function:
    """Returns array of indices."""
    return Function("arrayEnumerate", arr)


def arrayEnumerateDense(arr: Union[Column, List]) -> Function:
    """Returns dense indices."""
    return Function("arrayEnumerateDense", arr)


def arrayEnumerateUniq(arr: Union[Column, List]) -> Function:
    """Returns unique indices."""
    return Function("arrayEnumerateUniq", arr)


def arrayPopBack(arr: Union[Column, List]) -> Function:
    """Removes last element."""
    return Function("arrayPopBack", arr)


def arrayPopFront(arr: Union[Column, List]) -> Function:
    """Removes first element."""
    return Function("arrayPopFront", arr)


def arrayPushBack(arr: Union[Column, List], elem: Any) -> Function:
    """Adds element to end."""
    return Function("arrayPushBack", arr, elem)


def arrayPushFront(arr: Union[Column, List], elem: Any) -> Function:
    """Adds element to beginning."""
    return Function("arrayPushFront", arr, elem)


def arrayResize(arr: Union[Column, List], size: Union[Column, int]) -> Function:
    """Resizes array."""
    return Function("arrayResize", arr, size)


def arraySlice(arr: Union[Column, List], offset: Union[Column, int], length: Union[Column, int]) -> Function:
    """Extracts slice."""
    return Function("arraySlice", arr, offset, length)


def arraySort(arr: Union[Column, List]) -> Function:
    """Sorts array."""
    return Function("arraySort", arr)


def arrayReverseSort(arr: Union[Column, List]) -> Function:
    """Sorts array in reverse."""
    return Function("arrayReverseSort", arr)


def arrayUniq(arr: Union[Column, List]) -> Function:
    """Returns unique elements."""
    return Function("arrayUniq", arr)


def arrayJoin(arr: Union[Column, List]) -> Function:
    """Expands array into rows."""
    return Function("arrayJoin", arr)


def arrayMap(func: str, *arrays: Union[Column, List]) -> Function:
    """Maps function over arrays."""
    return Function("arrayMap", func, *arrays)


def arrayFilter(func: str, *arrays: Union[Column, List]) -> Function:
    """Filters array elements."""
    return Function("arrayFilter", func, *arrays)


def arrayCount(func: str, *arrays: Union[Column, List]) -> Function:
    """Counts matching elements."""
    return Function("arrayCount", func, *arrays)


def arrayExists(func: str, *arrays: Union[Column, List]) -> Function:
    """Checks if any element matches."""
    return Function("arrayExists", func, *arrays)


def arrayAll(func: str, *arrays: Union[Column, List]) -> Function:
    """Checks if all elements match."""
    return Function("arrayAll", func, *arrays)


def arraySum(arr: Union[Column, List]) -> Function:
    """Sums array elements."""
    return Function("arraySum", arr)


def arrayAvg(arr: Union[Column, List]) -> Function:
    """Averages array elements."""
    return Function("arrayAvg", arr)


def arrayCumSum(arr: Union[Column, List]) -> Function:
    """Cumulative sum."""
    return Function("arrayCumSum", arr)


def arrayProduct(arr: Union[Column, List]) -> Function:
    """Product of elements."""
    return Function("arrayProduct", arr)


def arrayReduce(agg_func: str, *arrays: Union[Column, List]) -> Function:
    """Reduces array."""
    return Function("arrayReduce", agg_func, *arrays)


def arrayReverse(arr: Union[Column, List]) -> Function:
    """Reverses array."""
    return Function("arrayReverse", arr)


def arrayFlatten(arr: Union[Column, List]) -> Function:
    """Flattens nested arrays."""
    return Function("arrayFlatten", arr)


def arrayZip(*arrays: Union[Column, List]) -> Function:
    """Zips arrays."""
    return Function("arrayZip", *arrays)


def arrayAUC(arr: Union[Column, List]) -> Function:
    """Calculates AUC."""
    return Function("arrayAUC", arr)


def arrayDifference(arr: Union[Column, List]) -> Function:
    """Differences between consecutive elements."""
    return Function("arrayDifference", arr)


def arrayDistinct(arr: Union[Column, List]) -> Function:
    """Returns distinct elements."""
    return Function("arrayDistinct", arr)


def arrayIntersect(arr1: Union[Column, List], arr2: Union[Column, List]) -> Function:
    """Intersection of arrays."""
    return Function("arrayIntersect", arr1, arr2)


def arrayReduceInRanges(agg_func: str, ranges: Union[Column, List], *arrays: Union[Column, List]) -> Function:
    """Reduces in ranges."""
    return Function("arrayReduceInRanges", agg_func, ranges, *arrays)


def arraySplit(func: str, *arrays: Union[Column, List]) -> Function:
    """Splits array."""
    return Function("arraySplit", func, *arrays)


def arrayStringConcat(arr: Union[Column, List], sep: str) -> Function:
    """Concatenates string array."""
    return Function("arrayStringConcat", arr, sep)


def arrayMin(arr: Union[Column, List]) -> Function:
    """Minimum element."""
    return Function("arrayMin", arr)


def arrayMax(arr: Union[Column, List]) -> Function:
    """Maximum element."""
    return Function("arrayMax", arr)

