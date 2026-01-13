"""
Aggregate functions for ClickHouse.
"""

from typing import Optional, List, Any
from chpy.orm import Column
from chpy.functions.base import AggregateFunction


def count(column: Optional[Column] = None) -> AggregateFunction:
    """Returns the number of rows."""
    return AggregateFunction("count", column)


def sum(column: Column) -> AggregateFunction:
    """Returns the sum of all values."""
    return AggregateFunction("sum", column)


def avg(column: Column) -> AggregateFunction:
    """Returns the average of all values."""
    return AggregateFunction("avg", column)


def min(column: Column) -> AggregateFunction:
    """Returns the minimum value."""
    return AggregateFunction("min", column)


def max(column: Column) -> AggregateFunction:
    """Returns the maximum value."""
    return AggregateFunction("max", column)


def any(column: Column) -> AggregateFunction:
    """Returns any value (non-deterministic)."""
    return AggregateFunction("any", column)


def anyHeavy(column: Column) -> AggregateFunction:
    """Returns the most frequent value."""
    return AggregateFunction("anyHeavy", column)


def anyLast(column: Column) -> AggregateFunction:
    """Returns the last value."""
    return AggregateFunction("anyLast", column)


def groupArray(column: Column) -> AggregateFunction:
    """Returns an array of values."""
    return AggregateFunction("groupArray", column)


def groupUniqArray(column: Column) -> AggregateFunction:
    """Returns an array of unique values."""
    return AggregateFunction("groupUniqArray", column)


def quantile(level: float):
    """Returns quantile function factory."""
    def _quantile(column: Column) -> AggregateFunction:
        return AggregateFunction(f"quantile({level})", column)
    return _quantile


def quantileExact(level: float):
    """Returns exact quantile function factory."""
    def _quantile(column: Column) -> AggregateFunction:
        return AggregateFunction(f"quantileExact({level})", column)
    return _quantile


def quantileTiming(level: float):
    """Returns quantile timing function factory."""
    def _quantile(column: Column) -> AggregateFunction:
        return AggregateFunction(f"quantileTiming({level})", column)
    return _quantile


def stddevPop(column: Column) -> AggregateFunction:
    """Returns population standard deviation."""
    return AggregateFunction("stddevPop", column)


def stddevSamp(column: Column) -> AggregateFunction:
    """Returns sample standard deviation."""
    return AggregateFunction("stddevSamp", column)


def varPop(column: Column) -> AggregateFunction:
    """Returns population variance."""
    return AggregateFunction("varPop", column)


def varSamp(column: Column) -> AggregateFunction:
    """Returns sample variance."""
    return AggregateFunction("varSamp", column)


def covarPop(x: Column, y: Column) -> AggregateFunction:
    """Returns population covariance."""
    return AggregateFunction("covarPop", x, second_column=y)


def covarSamp(x: Column, y: Column) -> AggregateFunction:
    """Returns sample covariance."""
    return AggregateFunction("covarSamp", x, second_column=y)


def corr(x: Column, y: Column) -> AggregateFunction:
    """Returns correlation coefficient."""
    return AggregateFunction("corr", x, second_column=y)


def argMin(arg: Column, val: Column) -> AggregateFunction:
    """Returns arg value for minimum val."""
    return AggregateFunction("argMin", arg, second_column=val)


def argMax(arg: Column, val: Column) -> AggregateFunction:
    """Returns arg value for maximum val."""
    return AggregateFunction("argMax", arg, second_column=val)


def topK(n: int):
    """Returns topK function factory."""
    def _topK(column: Column) -> AggregateFunction:
        return AggregateFunction(f"topK({n})", column)
    return _topK


def topKWeighted(n: int):
    """Returns topKWeighted function factory."""
    def _topK(column: Column, weight: Column) -> AggregateFunction:
        return AggregateFunction(f"topKWeighted({n})", column, second_column=weight)
    return _topK


def groupBitAnd(column: Column) -> AggregateFunction:
    """Bitwise AND of all values."""
    return AggregateFunction("groupBitAnd", column)


def groupBitOr(column: Column) -> AggregateFunction:
    """Bitwise OR of all values."""
    return AggregateFunction("groupBitOr", column)


def groupBitXor(column: Column) -> AggregateFunction:
    """Bitwise XOR of all values."""
    return AggregateFunction("groupBitXor", column)


def groupArrayInsertAt(column: Column, pos: int) -> AggregateFunction:
    """Inserts value at position in array."""
    return AggregateFunction(f"groupArrayInsertAt({pos})", column)


def groupArrayMovingSum(column: Column) -> AggregateFunction:
    """Moving sum of array."""
    return AggregateFunction("groupArrayMovingSum", column)


def groupArrayMovingAvg(column: Column) -> AggregateFunction:
    """Moving average of array."""
    return AggregateFunction("groupArrayMovingAvg", column)


def uniq(column: Column) -> AggregateFunction:
    """Approximate count of distinct values."""
    return AggregateFunction("uniq", column)


def uniqExact(column: Column) -> AggregateFunction:
    """Exact count of distinct values."""
    return AggregateFunction("uniqExact", column)


def uniqCombined(column: Column) -> AggregateFunction:
    """Combined approximate count."""
    return AggregateFunction("uniqCombined", column)


def uniqHLL12(column: Column) -> AggregateFunction:
    """HyperLogLog approximate count."""
    return AggregateFunction("uniqHLL12", column)


def uniqTheta(column: Column) -> AggregateFunction:
    """Theta sketch approximate count."""
    return AggregateFunction("uniqTheta", column)

