"""
Tests for chpy.functions module.
"""

import pytest
from chpy.functions.base import Function, AggregateFunction
from chpy.functions.aggregate import (
    count, sum, avg, min, max, any, anyHeavy, anyLast,
    groupArray, groupUniqArray, quantile, quantileExact, quantileTiming,
    stddevPop, stddevSamp, varPop, varSamp,
    uniq, uniqExact, uniqCombined, uniqHLL12, uniqTheta,
    argMin, argMax, topK, topKWeighted,
    groupBitAnd, groupBitOr, groupBitXor,
    groupArrayInsertAt, groupArrayMovingSum, groupArrayMovingAvg,
    covarPop, covarSamp, corr
)
from chpy.functions.string import (
    length, upper, lower, substring, concat, startsWith, endsWith,
    empty, notEmpty, lengthUTF8, lowerUTF8, upperUTF8, reverse, reverseUTF8,
    concatAssumeInjective, substringUTF8, appendTrailingCharIfAbsent,
    left, right, trimLeft, trimRight, trimBoth, format as format_str,
    formatReadableQuantity, formatReadableSize, formatReadableTimeDelta,
    splitByChar, splitByString, alphaTokens, extractAll, extractAllGroups,
    extractGroups, like, notLike, match, multiMatchAny, multiMatchAnyIndex,
    multiFuzzyMatchAny, replace, replaceAll, replaceOne, replaceRegexpOne,
    replaceRegexpAll, position, positionUTF8, positionCaseInsensitive,
    positionCaseInsensitiveUTF8, base64Encode as str_base64Encode,
    base64Decode as str_base64Decode, tryBase64Decode as str_tryBase64Decode,
    hex as str_hex, unhex as str_unhex, UUIDStringToNum as str_UUIDStringToNum,
    UUIDNumToString as str_UUIDNumToString, bitmaskToList, bitmaskToArray
)
from chpy.functions.date_time import (
    toYear, toMonth, toDayOfMonth, toHour, addDays, subtractDays, now, today,
    yesterday, timeSlot, toQuarter, toWeek, toDayOfYear, toDayOfWeek,
    toMinute, toSecond, toStartOfYear, toStartOfQuarter, toStartOfMonth,
    toStartOfWeek, toStartOfDay, toStartOfHour, toStartOfMinute,
    toStartOfSecond, toStartOfFiveMinute, toStartOfTenMinute,
    toStartOfFifteenMinute, toTime, toRelativeYearNum, toRelativeQuarterNum,
    toRelativeMonthNum, toRelativeWeekNum, toRelativeDayNum, toRelativeHourNum,
    toRelativeMinuteNum, toRelativeSecondNum, toISOYear, toISOWeek,
    toISOYearWeek, toMonday, toYYYYMM, toYYYYMMDD, toYYYYMMDDhhmmss,
    addYears, addQuarters, addMonths, addWeeks, addHours, addMinutes,
    addSeconds, subtractYears, subtractQuarters, subtractMonths, subtractWeeks,
    subtractHours, subtractMinutes, subtractSeconds, dateDiff, dateName,
    timeZone, timeZoneOf, toTimeZone, formatDateTime, parseDateTimeBestEffort
)
from chpy.functions.math import (
    sqrt, e, pi, exp, log, log2, log10, cbrt, pow, power, exp2, exp10,
    log1p, sign, sin, cos, tan, asin, acos, atan, atan2, sinh, cosh, tanh,
    asinh, acosh, atanh, hypot, logGamma, tgamma, lgamma, erf, erfc, erfInv, erfcInv
)
from chpy.functions.array import (
    array, arrayConcat, arrayElement, has, hasAll, hasAny, indexOf,
    countEqual, arrayEnumerate, arrayEnumerateDense, arrayEnumerateUniq,
    arrayPopBack, arrayPopFront, arrayPushBack, arrayPushFront, arrayResize,
    arraySlice, arraySort, arrayReverseSort, arrayUniq, arrayJoin, arrayMap,
    arrayFilter, arrayCount, arrayExists, arrayAll, arraySum, arrayAvg,
    arrayCumSum, arrayProduct, arrayReduce, arrayReverse, arrayFlatten,
    arrayZip, arrayAUC, arrayDifference, arrayDistinct, arrayIntersect,
    arrayReduceInRanges, arraySplit, arrayStringConcat, arrayMin, arrayMax
)
from chpy.functions.encoding import (
    hex, unhex, base64Encode, base64Decode, tryBase64Decode,
    base32Encode, base32Decode, base58Encode, base58Decode
)
from chpy.functions.geo import (
    greatCircleDistance, geoDistance, pointInPolygon, geohashEncode,
    geohashDecode, geohashesInBox
)
from chpy.functions.hash import (
    halfMD5, MD5, SHA1, SHA224, SHA256, SHA512, cityHash64, farmHash64,
    metroHash64, sipHash64, sipHash128, xxHash32, xxHash64, murmurHash2_32,
    murmurHash2_64, murmurHash3_32, murmurHash3_64, murmurHash3_128, gccMurmurHash
)
from chpy.functions.ip import (
    toIPv4, toIPv6, IPv4NumToString, IPv4StringToNum, IPv6NumToString,
    IPv6StringToNum, IPv4CIDRToRange, IPv6CIDRToRange, IPv4ToIPv6, cutIPv6
)
from chpy.functions.json import (
    JSONHas, JSONLength, JSONKey, JSONKeys, JSONExtract, JSONExtractString,
    JSONExtractInt, JSONExtractFloat, JSONExtractBool, JSONExtractRaw,
    JSONExtractArrayRaw, JSONExtractKeysAndValues, JSONExtractKeysAndValuesRaw,
    JSONExtractUInt
)
from chpy.functions.map import (
    map, mapKeys, mapValues, mapContains, mapGet
)
from chpy.functions.nullable import (
    isNull, isNotNull, assumeNotNull
)
from chpy.functions.other import (
    hostName, getMacro, FQDN, basename, visibleWidth, toTypeName, blockSize,
    blockNumber, rowNumberInBlock, rowNumberInAllBlocks, neighbor,
    runningAccumulate, runningDifference, runningDifferenceStartingWithFirstValue,
    finalizeAggregation
)
from chpy.functions.url import (
    protocol, domain, domainWithoutWWW, topLevelDomain, firstSignificantSubdomain,
    cutToFirstSignificantSubdomain, path, pathFull, queryString, fragment,
    queryStringAndFragment, extractURLParameter, extractURLParameters,
    extractURLParameterNames, cutURLParameter, cutWWW, cutQueryString,
    cutFragment, cutQueryStringAndFragment, decodeURLComponent, encodeURLComponent
)
from chpy.functions.window import (
    rowNumber, rank, denseRank, percentRank, cumeDist, ntile, lagInFrame,
    leadInFrame, firstValue, lastValue, nthValue
)
from chpy.functions.arithmetic import (
    abs, divide, plus, minus, multiply,
    intDiv, intDivOrZero, modulo, negate,
    gcd, lcm
)
from chpy.functions.rounding import (
    round, roundBankers, floor, ceil, trunc, roundToExp2,
    roundDuration, roundAge, roundDown
)
from chpy.functions.type_conversion import (
    toInt8, toInt16, toInt32, toInt64, toUInt8, toUInt16, toUInt32, toUInt64,
    toFloat32, toFloat64, toDate, toDateTime, toDateTime64, toString, toFixedString,
    toDecimal32, toDecimal64, toDecimal128, toDecimal256,
    toUUID, toIPv4, toIPv6, parseDateTimeBestEffort, parseDateTimeBestEffortUS,
    parseDateTime32BestEffort, CAST
)
from chpy.functions.conditional import if_ as if_func, coalesce, multiIf, ifNull, nullIf
from chpy.functions.comparison import (
    equals, notEquals, less, greater, lessOrEquals, greaterOrEquals
)
from chpy.functions.logical import and_, or_, not_, xor
from chpy.functions.bitwise import (
    bitAnd, bitOr, bitXor, bitNot, bitShiftLeft, bitShiftRight,
    bitRotateLeft, bitRotateRight, bitTest, bitTestAll, bitTestAny, bitCount
)
from chpy.functions.tuple import tuple as tuple_func, tupleElement, untuple
from chpy.functions.uuid import generateUUIDv4, UUIDStringToNum, UUIDNumToString
from chpy.orm import Column
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestFunction:
    """Test cases for Function base class."""
    
    def test_init_simple(self):
        """Test function initialization without arguments."""
        func = Function("now")
        assert func.func_name == "now"
        assert func.args == ()
        assert func._alias is None
    
    def test_init_with_args(self):
        """Test function initialization with arguments."""
        col = Column("pair", String)
        func = Function("length", col)
        assert func.func_name == "length"
        assert len(func.args) == 1
        assert func.args[0] == col
    
    def test_init_with_alias(self):
        """Test function initialization with alias."""
        col = Column("pair", String)
        func = Function("length", col, alias="pair_length")
        assert func._alias == "pair_length"
    
    def test_alias(self):
        """Test alias method."""
        col = Column("pair", String)
        func = length(col)
        aliased = func.alias("pair_length")
        
        assert aliased._alias == "pair_length"
        assert func._alias is None  # Original unchanged
    
    def test_to_sql_no_args(self):
        """Test SQL generation for function without arguments."""
        func = Function("now")
        sql = func.to_sql()
        assert sql == "now()"
    
    def test_to_sql_with_column(self):
        """Test SQL generation with Column argument."""
        col = Column("pair", String)
        func = Function("length", col)
        sql = func.to_sql()
        assert sql == "length(pair)"
    
    def test_to_sql_with_string(self):
        """Test SQL generation with string argument."""
        func = Function("upper", "hello")
        sql = func.to_sql()
        assert sql == "upper('hello')"
    
    def test_to_sql_with_number(self):
        """Test SQL generation with number argument."""
        func = Function("abs", -5)
        sql = func.to_sql()
        assert sql == "abs(-5)"
    
    def test_to_sql_with_alias(self):
        """Test SQL generation with alias."""
        col = Column("pair", String)
        func = Function("length", col, alias="pair_length")
        sql = func.to_sql()
        assert sql == "length(pair) as pair_length"
    
    def test_to_sql_with_list(self):
        """Test SQL generation with list argument."""
        func = Function("array", 1, 2, 3)
        sql = func.to_sql()
        assert sql == "array(1, 2, 3)"
    
    def test_to_sql_with_list_arg(self):
        """Test SQL generation with list as argument (to test list formatting)."""
        func = Function("array", [1, 2, 3])
        sql = func.to_sql()
        assert "array" in sql
        assert "1" in sql and "2" in sql and "3" in sql
    
    def test_to_sql_with_tuple_arg(self):
        """Test SQL generation with tuple as argument (to test tuple formatting)."""
        func = Function("array", (1, 2, 3))
        sql = func.to_sql()
        assert "array" in sql
        assert "1" in sql and "2" in sql and "3" in sql
    
    def test_to_sql_with_nested_function(self):
        """Test SQL generation with nested function."""
        col = Column("timestamp_ms", UInt64)
        inner = Function("divide", col, 1000)
        outer = Function("toDateTime", inner)
        sql = outer.to_sql()
        assert "toDateTime" in sql
        assert "divide" in sql
    
    def test_to_sql_escape_string(self):
        """Test SQL generation with string containing quotes."""
        func = Function("upper", "O'Brien")
        sql = func.to_sql()
        assert sql == "upper('O''Brien')"
    
    def test_to_sql_with_none(self):
        """Test SQL generation with None argument."""
        func = Function("coalesce", None, "default")
        sql = func.to_sql()
        assert "NULL" in sql
    
    def test_str(self):
        """Test string representation."""
        col = Column("pair", String)
        func = length(col)
        assert str(func) == "length(pair)"
    
    def test_repr(self):
        """Test representation."""
        col = Column("pair", String)
        func = length(col)
        assert "Function" in repr(func)


class TestAggregateFunction:
    """Test cases for AggregateFunction class."""
    
    def test_init_with_column(self):
        """Test aggregate function initialization with column."""
        col = Column("price", Float64)
        func = AggregateFunction("avg", col)
        assert func.func_name == "AVG"
        assert func.column == col
        assert func._alias is None
    
    def test_init_without_column(self):
        """Test aggregate function initialization without column (count)."""
        func = AggregateFunction("count")
        assert func.func_name == "COUNT"
        assert func.column is None
    
    def test_init_with_alias(self):
        """Test aggregate function initialization with alias."""
        col = Column("price", Float64)
        func = AggregateFunction("avg", col, alias="avg_price")
        assert func._alias == "avg_price"
    
    def test_alias(self):
        """Test alias method."""
        col = Column("price", Float64)
        func = avg(col)
        aliased = func.alias("avg_price")
        
        assert aliased._alias == "avg_price"
        assert func._alias is None
    
    def test_to_sql_with_column(self):
        """Test SQL generation with column."""
        col = Column("price", Float64)
        func = avg(col)
        sql = func.to_sql()
        assert sql == "AVG(price)"
    
    def test_to_sql_count(self):
        """Test SQL generation for count()."""
        func = count()
        sql = func.to_sql()
        assert sql == "count(*)"
    
    def test_to_sql_no_column_not_count(self):
        """Test SQL generation for aggregate function without column and not COUNT."""
        func = AggregateFunction("SUM")
        sql = func.to_sql()
        assert sql == "SUM()"
    
    def test_to_sql_with_alias(self):
        """Test SQL generation with alias."""
        col = Column("price", Float64)
        func = avg(col).alias("avg_price")
        sql = func.to_sql()
        assert sql == "AVG(price) as avg_price"
    
    def test_str(self):
        """Test string representation."""
        col = Column("price", Float64)
        func = avg(col)
        assert str(func) == "AVG(price)"
    
    def test_repr(self):
        """Test representation."""
        col = Column("price", Float64)
        func = avg(col)
        assert "AggregateFunction" in repr(func)


class TestAggregateFunctions:
    """Test cases for aggregate function factories."""
    
    def test_count(self):
        """Test count function."""
        func = count()
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "COUNT"
        assert func.column is None
    
    def test_count_with_column(self):
        """Test count with column."""
        col = Column("pair", String)
        func = count(col)
        assert func.column == col
    
    def test_sum(self):
        """Test sum function."""
        col = Column("price", Float64)
        func = sum(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "SUM"
        assert func.column == col
    
    def test_avg(self):
        """Test avg function."""
        col = Column("price", Float64)
        func = avg(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "AVG"
        assert func.column == col
    
    def test_min(self):
        """Test min function."""
        col = Column("price", Float64)
        func = min(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "MIN"
        assert func.column == col
    
    def test_max(self):
        """Test max function."""
        col = Column("price", Float64)
        func = max(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "MAX"
        assert func.column == col
    
    def test_any(self):
        """Test any function."""
        col = Column("price", Float64)
        func = any(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "ANY"
        assert func.column == col
    
    def test_anyHeavy(self):
        """Test anyHeavy function."""
        col = Column("price", Float64)
        func = anyHeavy(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "anyHeavy"
        assert func.column == col
    
    def test_anyLast(self):
        """Test anyLast function."""
        col = Column("price", Float64)
        func = anyLast(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "anyLast"
        assert func.column == col
    
    def test_groupArray(self):
        """Test groupArray function."""
        col = Column("pair", String)
        func = groupArray(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupArray"
        assert func.column == col
    
    def test_groupUniqArray(self):
        """Test groupUniqArray function."""
        col = Column("pair", String)
        func = groupUniqArray(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupUniqArray"
        assert func.column == col
    
    def test_quantile(self):
        """Test quantile function."""
        col = Column("price", Float64)
        quantile_func = quantile(0.5)
        func = quantile_func(col)
        assert isinstance(func, AggregateFunction)
        assert "quantile(0.5)" in func.func_name.lower()
        assert func.column == col
    
    def test_quantileExact(self):
        """Test quantileExact function."""
        col = Column("price", Float64)
        quantile_func = quantileExact(0.95)
        func = quantile_func(col)
        assert isinstance(func, AggregateFunction)
        assert "quantileexact(0.95)" in func.func_name.lower()
        assert func.column == col
    
    def test_quantileTiming(self):
        """Test quantileTiming function."""
        col = Column("price", Float64)
        quantile_func = quantileTiming(0.9)
        func = quantile_func(col)
        assert isinstance(func, AggregateFunction)
        assert "quantiletiming(0.9)" in func.func_name.lower()
        assert func.column == col
    
    def test_stddevPop(self):
        """Test stddevPop function."""
        col = Column("price", Float64)
        func = stddevPop(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "stddevPop"
        assert func.column == col
    
    def test_stddevSamp(self):
        """Test stddevSamp function."""
        col = Column("price", Float64)
        func = stddevSamp(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "stddevSamp"
        assert func.column == col
    
    def test_varPop(self):
        """Test varPop function."""
        col = Column("price", Float64)
        func = varPop(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "varPop"
        assert func.column == col
    
    def test_varSamp(self):
        """Test varSamp function."""
        col = Column("price", Float64)
        func = varSamp(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "varSamp"
        assert func.column == col
    
    def test_uniq(self):
        """Test uniq function."""
        col = Column("pair", String)
        func = uniq(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "uniq"
        assert func.column == col
    
    def test_uniqExact(self):
        """Test uniqExact function."""
        col = Column("pair", String)
        func = uniqExact(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "uniqExact"
        assert func.column == col
    
    def test_uniqCombined(self):
        """Test uniqCombined function."""
        col = Column("pair", String)
        func = uniqCombined(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "uniqCombined"
        assert func.column == col
    
    def test_uniqHLL12(self):
        """Test uniqHLL12 function."""
        col = Column("pair", String)
        func = uniqHLL12(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "uniqHLL12"
        assert func.column == col
    
    def test_uniqTheta(self):
        """Test uniqTheta function."""
        col = Column("pair", String)
        func = uniqTheta(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "uniqTheta"
        assert func.column == col
    
    def test_argMin(self):
        """Test argMin function."""
        col1 = Column("pair", String)
        col2 = Column("price", Float64)
        func = argMin(col1, col2)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "argMin"
    
    def test_argMax(self):
        """Test argMax function."""
        col1 = Column("pair", String)
        col2 = Column("price", Float64)
        func = argMax(col1, col2)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "argMax"
    
    def test_topK(self):
        """Test topK function."""
        col = Column("pair", String)
        topk_func = topK(10)
        func = topk_func(col)
        assert isinstance(func, AggregateFunction)
        assert "topk(10)" in func.func_name.lower()
        assert func.column == col
    
    def test_topKWeighted(self):
        """Test topKWeighted function."""
        col = Column("pair", String)
        weight_col = Column("weight", Float64)
        topk_func = topKWeighted(10)
        func = topk_func(col, weight_col)
        assert isinstance(func, AggregateFunction)
        assert "topkweighted(10)" in func.func_name.lower()
        assert func.column == col
    
    def test_groupBitAnd(self):
        """Test groupBitAnd function."""
        col = Column("flags", UInt64)
        func = groupBitAnd(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupBitAnd"
        assert func.column == col
    
    def test_groupBitOr(self):
        """Test groupBitOr function."""
        col = Column("flags", UInt64)
        func = groupBitOr(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupBitOr"
        assert func.column == col
    
    def test_groupBitXor(self):
        """Test groupBitXor function."""
        col = Column("flags", UInt64)
        func = groupBitXor(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupBitXor"
        assert func.column == col
    
    def test_groupArrayInsertAt(self):
        """Test groupArrayInsertAt function."""
        col = Column("values", "Array(Int64)")
        func = groupArrayInsertAt(col, 0)
        assert isinstance(func, AggregateFunction)
        assert "grouparrayinsertat(0)" in func.func_name.lower()
        assert func.column == col
    
    def test_groupArrayMovingSum(self):
        """Test groupArrayMovingSum function."""
        col = Column("values", "Array(Float64)")
        func = groupArrayMovingSum(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupArrayMovingSum"
        assert func.column == col
    
    def test_groupArrayMovingAvg(self):
        """Test groupArrayMovingAvg function."""
        col = Column("values", "Array(Float64)")
        func = groupArrayMovingAvg(col)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "groupArrayMovingAvg"
        assert func.column == col
    
    def test_covarPop(self):
        """Test covarPop function."""
        col1 = Column("price1", Float64)
        col2 = Column("price2", Float64)
        func = covarPop(col1, col2)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "covarPop"
    
    def test_covarSamp(self):
        """Test covarSamp function."""
        col1 = Column("price1", Float64)
        col2 = Column("price2", Float64)
        func = covarSamp(col1, col2)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "covarSamp"
    
    def test_corr(self):
        """Test corr function."""
        col1 = Column("price1", Float64)
        col2 = Column("price2", Float64)
        func = corr(col1, col2)
        assert isinstance(func, AggregateFunction)
        assert func.func_name == "CORR"


class TestStringFunctions:
    """Test cases for string functions."""
    
    def test_length(self):
        """Test length function."""
        col = Column("pair", String)
        func = length(col)
        assert func.func_name == "length"
        assert func.to_sql() == "length(pair)"
    
    def test_upper(self):
        """Test upper function."""
        col = Column("pair", String)
        func = upper(col)
        assert func.func_name == "upper"
        assert func.to_sql() == "upper(pair)"
    
    def test_lower(self):
        """Test lower function."""
        col = Column("exchange", String)
        func = lower(col)
        assert func.func_name == "lower"
        assert func.to_sql() == "lower(exchange)"
    
    def test_substring(self):
        """Test substring function."""
        col = Column("pair", String)
        func = substring(col, 1, 3)
        sql = func.to_sql()
        assert "substring" in sql.lower()
        assert "pair" in sql
    
    def test_concat(self):
        """Test concat function."""
        col1 = Column("currency", String)
        col2 = Column("base", String)
        func = concat(col1, "-", col2)
        sql = func.to_sql()
        assert "concat" in sql.lower()
    
    def test_startsWith(self):
        """Test startsWith function."""
        col = Column("pair", String)
        func = startsWith(col, "BTC")
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower() or "startswith" in sql.lower()
    
    def test_endsWith(self):
        """Test endsWith function."""
        col = Column("pair", String)
        func = endsWith(col, "USDT")
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower() or "endswith" in sql.lower()


class TestDateTimeFunctions:
    """Test cases for date/time functions."""
    
    def test_now(self):
        """Test now function."""
        func = now()
        assert func.func_name == "now"
        assert func.to_sql() == "now()"
    
    def test_today(self):
        """Test today function."""
        func = today()
        assert func.func_name == "today"
        assert func.to_sql() == "today()"
    
    def test_toYear(self):
        """Test toYear function."""
        col = Column("timestamp_ms", UInt64)
        func = toYear(col)
        assert func.func_name == "toYear"
    
    def test_toMonth(self):
        """Test toMonth function."""
        col = Column("timestamp_ms", UInt64)
        func = toMonth(col)
        assert func.func_name == "toMonth"
    
    def test_toDayOfMonth(self):
        """Test toDayOfMonth function."""
        col = Column("timestamp_ms", UInt64)
        func = toDayOfMonth(col)
        assert func.func_name == "toDayOfMonth"
    
    def test_toHour(self):
        """Test toHour function."""
        col = Column("timestamp_ms", UInt64)
        func = toHour(col)
        assert func.func_name == "toHour"
    
    def test_addDays(self):
        """Test addDays function."""
        col = Column("date", "Date")
        func = addDays(col, 7)
        sql = func.to_sql()
        assert "addDays" in sql or "adddays" in sql.lower()
    
    def test_subtractDays(self):
        """Test subtractDays function."""
        col = Column("date", "Date")
        func = subtractDays(col, 7)
        sql = func.to_sql()
        assert "subtractDays" in sql or "subtractdays" in sql.lower()


class TestMathFunctions:
    """Test cases for math functions."""
    
    def test_abs(self):
        """Test abs function."""
        col = Column("price", Float64)
        func = abs(col)
        assert func.func_name == "abs"
        assert func.to_sql() == "abs(price)"
    
    def test_sqrt(self):
        """Test sqrt function."""
        col = Column("price", Float64)
        func = sqrt(col)
        assert func.func_name == "sqrt"
        assert func.to_sql() == "sqrt(price)"
    
    def test_round(self):
        """Test round function."""
        col = Column("price", Float64)
        func = round(col)
        assert func.func_name == "round"
        assert func.to_sql() == "round(price)"
    
    def test_round_with_precision(self):
        """Test round function with precision (ClickHouse supports round(x, n))."""
        col = Column("price", Float64)
        # Even though the function signature shows one arg, Function accepts *args
        # so we can pass precision as a second argument
        func = Function("round", col, 2)
        sql = func.to_sql()
        assert "round" in sql.lower()
        assert "2" in sql
    
    def test_floor(self):
        """Test floor function."""
        col = Column("price", Float64)
        func = floor(col)
        assert func.func_name == "floor"
        assert func.to_sql() == "floor(price)"
    
    def test_ceil(self):
        """Test ceil function."""
        col = Column("price", Float64)
        func = ceil(col)
        assert func.func_name == "ceil"
        assert func.to_sql() == "ceil(price)"
    
    def test_roundBankers(self):
        """Test roundBankers function."""
        col = Column("price", Float64)
        func = roundBankers(col)
        assert func.func_name == "roundBankers"
        assert func.to_sql() == "roundBankers(price)"
    
    def test_trunc(self):
        """Test trunc function."""
        col = Column("price", Float64)
        func = trunc(col)
        assert func.func_name == "trunc"
        assert func.to_sql() == "trunc(price)"
    
    def test_roundToExp2(self):
        """Test roundToExp2 function."""
        col = Column("price", Float64)
        func = roundToExp2(col)
        assert func.func_name == "roundToExp2"
        assert func.to_sql() == "roundToExp2(price)"
    
    def test_roundDuration(self):
        """Test roundDuration function."""
        col = Column("duration", Float64)
        func = roundDuration(col)
        assert func.func_name == "roundDuration"
        assert func.to_sql() == "roundDuration(duration)"
    
    def test_roundAge(self):
        """Test roundAge function."""
        col = Column("age", Float64)
        func = roundAge(col)
        assert func.func_name == "roundAge"
        assert func.to_sql() == "roundAge(age)"
    
    def test_roundDown(self):
        """Test roundDown function."""
        col = Column("price", Float64)
        func = roundDown(col, 2)
        assert func.func_name == "roundDown"
        sql = func.to_sql()
        assert "roundDown" in sql
        assert "2" in sql


class TestTypeConversionFunctions:
    """Test cases for type conversion functions."""
    
    def test_toString(self):
        """Test toString function."""
        col = Column("price", Float64)
        func = toString(col)
        assert func.func_name == "toString"
        assert func.to_sql() == "toString(price)"
    
    def test_toInt64(self):
        """Test toInt64 function."""
        col = Column("price", Float64)
        func = toInt64(col)
        assert func.func_name == "toInt64"
        assert func.to_sql() == "toInt64(price)"
    
    def test_toFloat64(self):
        """Test toFloat64 function."""
        col = Column("price", String)
        func = toFloat64(col)
        assert func.func_name == "toFloat64"
        assert func.to_sql() == "toFloat64(price)"
    
    def test_toDateTime(self):
        """Test toDateTime function."""
        col = Column("timestamp_ms", UInt64)
        func = toDateTime(col)
        assert func.func_name == "toDateTime"
        assert func.to_sql() == "toDateTime(timestamp_ms)"
    
    def test_toInt8(self):
        """Test toInt8 function."""
        col = Column("value", String)
        func = toInt8(col)
        assert func.func_name == "toInt8"
        assert func.to_sql() == "toInt8(value)"
    
    def test_toInt16(self):
        """Test toInt16 function."""
        col = Column("value", String)
        func = toInt16(col)
        assert func.func_name == "toInt16"
        assert func.to_sql() == "toInt16(value)"
    
    def test_toInt32(self):
        """Test toInt32 function."""
        col = Column("value", String)
        func = toInt32(col)
        assert func.func_name == "toInt32"
        assert func.to_sql() == "toInt32(value)"
    
    def test_toUInt8(self):
        """Test toUInt8 function."""
        col = Column("value", String)
        func = toUInt8(col)
        assert func.func_name == "toUInt8"
        assert func.to_sql() == "toUInt8(value)"
    
    def test_toUInt16(self):
        """Test toUInt16 function."""
        col = Column("value", String)
        func = toUInt16(col)
        assert func.func_name == "toUInt16"
        assert func.to_sql() == "toUInt16(value)"
    
    def test_toUInt32(self):
        """Test toUInt32 function."""
        col = Column("value", String)
        func = toUInt32(col)
        assert func.func_name == "toUInt32"
        assert func.to_sql() == "toUInt32(value)"
    
    def test_toUInt64(self):
        """Test toUInt64 function."""
        col = Column("value", String)
        func = toUInt64(col)
        assert func.func_name == "toUInt64"
        assert func.to_sql() == "toUInt64(value)"
    
    def test_toFloat32(self):
        """Test toFloat32 function."""
        col = Column("value", String)
        func = toFloat32(col)
        assert func.func_name == "toFloat32"
        assert func.to_sql() == "toFloat32(value)"
    
    def test_toDate(self):
        """Test toDate function."""
        col = Column("timestamp", String)
        func = toDate(col)
        assert func.func_name == "toDate"
        assert func.to_sql() == "toDate(timestamp)"
    
    def test_toDateTime64(self):
        """Test toDateTime64 function."""
        col = Column("timestamp", String)
        func = toDateTime64(col, 3)
        assert func.func_name == "toDateTime64"
        sql = func.to_sql()
        assert "toDateTime64" in sql
        assert "3" in sql
    
    def test_toFixedString(self):
        """Test toFixedString function."""
        col = Column("value", String)
        func = toFixedString(col, 10)
        assert func.func_name == "toFixedString"
        sql = func.to_sql()
        assert "toFixedString" in sql
        assert "10" in sql
    
    def test_toDecimal32(self):
        """Test toDecimal32 function."""
        col = Column("value", String)
        func = toDecimal32(col, 2)
        assert func.func_name == "toDecimal32"
        sql = func.to_sql()
        assert "toDecimal32" in sql
        assert "2" in sql
    
    def test_toDecimal64(self):
        """Test toDecimal64 function."""
        col = Column("value", String)
        func = toDecimal64(col, 4)
        assert func.func_name == "toDecimal64"
        sql = func.to_sql()
        assert "toDecimal64" in sql
        assert "4" in sql
    
    def test_toDecimal128(self):
        """Test toDecimal128 function."""
        col = Column("value", String)
        func = toDecimal128(col, 6)
        assert func.func_name == "toDecimal128"
        sql = func.to_sql()
        assert "toDecimal128" in sql
        assert "6" in sql
    
    def test_toDecimal256(self):
        """Test toDecimal256 function."""
        col = Column("value", String)
        func = toDecimal256(col, 8)
        assert func.func_name == "toDecimal256"
        sql = func.to_sql()
        assert "toDecimal256" in sql
        assert "8" in sql
    
    def test_toUUID(self):
        """Test toUUID function."""
        col = Column("uuid_str", String)
        func = toUUID(col)
        assert func.func_name == "toUUID"
        assert func.to_sql() == "toUUID(uuid_str)"
    
    def test_toIPv4(self):
        """Test toIPv4 function."""
        col = Column("ip_str", String)
        func = toIPv4(col)
        assert func.func_name == "toIPv4"
        assert func.to_sql() == "toIPv4(ip_str)"
    
    def test_toIPv6(self):
        """Test toIPv6 function."""
        col = Column("ip_str", String)
        func = toIPv6(col)
        assert func.func_name == "toIPv6"
        assert func.to_sql() == "toIPv6(ip_str)"
    
    def test_parseDateTimeBestEffort(self):
        """Test parseDateTimeBestEffort function."""
        col = Column("date_str", String)
        func = parseDateTimeBestEffort(col)
        assert func.func_name == "parseDateTimeBestEffort"
        assert func.to_sql() == "parseDateTimeBestEffort(date_str)"
    
    def test_parseDateTimeBestEffortUS(self):
        """Test parseDateTimeBestEffortUS function."""
        col = Column("date_str", String)
        func = parseDateTimeBestEffortUS(col)
        assert func.func_name == "parseDateTimeBestEffortUS"
        assert func.to_sql() == "parseDateTimeBestEffortUS(date_str)"
    
    def test_parseDateTime32BestEffort(self):
        """Test parseDateTime32BestEffort function."""
        col = Column("date_str", String)
        func = parseDateTime32BestEffort(col)
        assert func.func_name == "parseDateTime32BestEffort"
        assert func.to_sql() == "parseDateTime32BestEffort(date_str)"
    
    def test_CAST(self):
        """Test CAST function."""
        col = Column("value", String)
        func = CAST(col, "Int64")
        assert func.func_name == "CAST"
        sql = func.to_sql()
        assert "CAST" in sql
        assert "Int64" in sql


class TestConditionalFunctions:
    """Test cases for conditional functions."""
    
    def test_if_(self):
        """Test if_ function."""
        col = Column("price", Float64)
        func = if_func(col > 50000, "high", "normal")
        sql = func.to_sql()
        assert "if" in sql.lower()
    
    def test_coalesce(self):
        """Test coalesce function."""
        col1 = Column("price1", Float64)
        col2 = Column("price2", Float64)
        func = coalesce(col1, col2, 0)
        sql = func.to_sql()
        assert "coalesce" in sql.lower()
    
    def test_multiIf(self):
        """Test multiIf function."""
        col1 = Column("x", Int64)
        col2 = Column("y", Int64)
        func = multiIf(col1 > 10, "high", col2 > 5, "medium", "low")
        sql = func.to_sql()
        assert "multiif" in sql.lower() or "multiIf" in sql
        assert func.func_name == "multiIf"
    
    def test_ifNull(self):
        """Test ifNull function."""
        col1 = Column("price", Float64)
        col2 = Column("default_price", Float64)
        func = ifNull(col1, col2)
        sql = func.to_sql()
        assert "ifnull" in sql.lower() or "ifNull" in sql
        assert func.func_name == "ifNull"
    
    def test_nullIf(self):
        """Test nullIf function."""
        col1 = Column("price", Float64)
        col2 = Column("other_price", Float64)
        func = nullIf(col1, col2)
        sql = func.to_sql()
        assert "nullif" in sql.lower() or "nullIf" in sql
        assert func.func_name == "nullIf"


class TestArithmeticFunctions:
    """Test cases for arithmetic functions."""
    
    def test_plus(self):
        """Test plus function."""
        col1 = Column("price1", Float64)
        col2 = Column("price2", Float64)
        func = plus(col1, col2)
        sql = func.to_sql()
        assert "plus" in sql.lower()
        assert func.func_name == "plus"
    
    def test_plus_with_number(self):
        """Test plus function with number."""
        col = Column("price", Float64)
        func = plus(col, 10)
        sql = func.to_sql()
        assert "plus" in sql.lower()
        assert "10" in sql
    
    def test_minus(self):
        """Test minus function."""
        col1 = Column("price1", Float64)
        col2 = Column("price2", Float64)
        func = minus(col1, col2)
        sql = func.to_sql()
        assert "minus" in sql.lower()
        assert func.func_name == "minus"
    
    def test_multiply(self):
        """Test multiply function."""
        col1 = Column("price", Float64)
        col2 = Column("quantity", Float64)
        func = multiply(col1, col2)
        sql = func.to_sql()
        assert "multiply" in sql.lower()
        assert func.func_name == "multiply"
    
    def test_divide(self):
        """Test divide function."""
        col1 = Column("numerator", Float64)
        col2 = Column("denominator", Float64)
        func = divide(col1, col2)
        sql = func.to_sql()
        assert "divide" in sql.lower()
        assert func.func_name == "divide"
    
    def test_intDiv(self):
        """Test intDiv function."""
        col1 = Column("a", Int64)
        col2 = Column("b", Int64)
        func = intDiv(col1, col2)
        sql = func.to_sql()
        assert "intdiv" in sql.lower() or "intDiv" in sql
        assert func.func_name == "intDiv"
    
    def test_intDivOrZero(self):
        """Test intDivOrZero function."""
        col1 = Column("a", Int64)
        col2 = Column("b", Int64)
        func = intDivOrZero(col1, col2)
        sql = func.to_sql()
        assert "intdivorzero" in sql.lower() or "intDivOrZero" in sql
        assert func.func_name == "intDivOrZero"
    
    def test_modulo(self):
        """Test modulo function."""
        col1 = Column("a", Int64)
        col2 = Column("b", Int64)
        func = modulo(col1, col2)
        sql = func.to_sql()
        assert "modulo" in sql.lower()
        assert func.func_name == "modulo"
    
    def test_negate(self):
        """Test negate function."""
        col = Column("price", Float64)
        func = negate(col)
        sql = func.to_sql()
        assert "negate" in sql.lower()
        assert func.func_name == "negate"
    
    def test_abs(self):
        """Test abs function."""
        col = Column("price", Float64)
        func = abs(col)
        sql = func.to_sql()
        assert "abs" in sql.lower()
        assert func.func_name == "abs"
    
    def test_gcd(self):
        """Test gcd function."""
        col1 = Column("a", Int64)
        col2 = Column("b", Int64)
        func = gcd(col1, col2)
        sql = func.to_sql()
        assert "gcd" in sql.lower()
        assert func.func_name == "gcd"
    
    def test_lcm(self):
        """Test lcm function."""
        col1 = Column("a", Int64)
        col2 = Column("b", Int64)
        func = lcm(col1, col2)
        sql = func.to_sql()
        assert "lcm" in sql.lower()
        assert func.func_name == "lcm"


class TestComparisonFunctions:
    """Test cases for comparison functions."""
    
    def test_equals(self):
        """Test equals function."""
        col = Column("price", Float64)
        func = equals(col, 100)
        sql = func.to_sql()
        assert "equals" in sql.lower()
        assert func.func_name == "equals"
    
    def test_notEquals(self):
        """Test notEquals function."""
        col = Column("price", Float64)
        func = notEquals(col, 100)
        sql = func.to_sql()
        assert "notequals" in sql.lower() or "notEquals" in sql
        assert func.func_name == "notEquals"
    
    def test_less(self):
        """Test less function."""
        col = Column("price", Float64)
        func = less(col, 100)
        sql = func.to_sql()
        assert "less" in sql.lower()
        assert func.func_name == "less"
    
    def test_greater(self):
        """Test greater function."""
        col = Column("price", Float64)
        func = greater(col, 100)
        sql = func.to_sql()
        assert "greater" in sql.lower()
        assert func.func_name == "greater"
    
    def test_lessOrEquals(self):
        """Test lessOrEquals function."""
        col = Column("price", Float64)
        func = lessOrEquals(col, 100)
        sql = func.to_sql()
        assert "lessorequals" in sql.lower() or "lessOrEquals" in sql
        assert func.func_name == "lessOrEquals"
    
    def test_greaterOrEquals(self):
        """Test greaterOrEquals function."""
        col = Column("price", Float64)
        func = greaterOrEquals(col, 100)
        sql = func.to_sql()
        assert "greaterorequals" in sql.lower() or "greaterOrEquals" in sql
        assert func.func_name == "greaterOrEquals"


class TestLogicalFunctions:
    """Test cases for logical functions."""
    
    def test_and_(self):
        """Test and_ function."""
        col1 = Column("flag1", UInt8)
        col2 = Column("flag2", UInt8)
        func = and_(col1, col2)
        sql = func.to_sql()
        assert "and" in sql.lower()
        assert func.func_name == "and"
    
    def test_or_(self):
        """Test or_ function."""
        col1 = Column("flag1", UInt8)
        col2 = Column("flag2", UInt8)
        func = or_(col1, col2)
        sql = func.to_sql()
        assert "or" in sql.lower()
        assert func.func_name == "or"
    
    def test_not_(self):
        """Test not_ function."""
        col = Column("flag", UInt8)
        func = not_(col)
        sql = func.to_sql()
        assert "not" in sql.lower()
        assert func.func_name == "not"
    
    def test_xor(self):
        """Test xor function."""
        col1 = Column("flag1", UInt8)
        col2 = Column("flag2", UInt8)
        func = xor(col1, col2)
        sql = func.to_sql()
        assert "xor" in sql.lower()
        assert func.func_name == "xor"


class TestBitwiseFunctions:
    """Test cases for bitwise functions."""
    
    def test_bitAnd(self):
        """Test bitAnd function."""
        col1 = Column("a", UInt64)
        col2 = Column("b", UInt64)
        func = bitAnd(col1, col2)
        sql = func.to_sql()
        assert "bitand" in sql.lower() or "bitAnd" in sql
        assert func.func_name == "bitAnd"
    
    def test_bitOr(self):
        """Test bitOr function."""
        col1 = Column("a", UInt64)
        col2 = Column("b", UInt64)
        func = bitOr(col1, col2)
        sql = func.to_sql()
        assert "bitor" in sql.lower() or "bitOr" in sql
        assert func.func_name == "bitOr"
    
    def test_bitXor(self):
        """Test bitXor function."""
        col1 = Column("a", UInt64)
        col2 = Column("b", UInt64)
        func = bitXor(col1, col2)
        sql = func.to_sql()
        assert "bitxor" in sql.lower() or "bitXor" in sql
        assert func.func_name == "bitXor"
    
    def test_bitNot(self):
        """Test bitNot function."""
        col = Column("a", UInt64)
        func = bitNot(col)
        sql = func.to_sql()
        assert "bitnot" in sql.lower() or "bitNot" in sql
        assert func.func_name == "bitNot"
    
    def test_bitShiftLeft(self):
        """Test bitShiftLeft function."""
        col = Column("a", UInt64)
        func = bitShiftLeft(col, 2)
        sql = func.to_sql()
        assert "bitshiftleft" in sql.lower() or "bitShiftLeft" in sql
        assert func.func_name == "bitShiftLeft"
    
    def test_bitShiftRight(self):
        """Test bitShiftRight function."""
        col = Column("a", UInt64)
        func = bitShiftRight(col, 2)
        sql = func.to_sql()
        assert "bitshiftright" in sql.lower() or "bitShiftRight" in sql
        assert func.func_name == "bitShiftRight"
    
    def test_bitRotateLeft(self):
        """Test bitRotateLeft function."""
        col = Column("a", UInt64)
        func = bitRotateLeft(col, 2)
        sql = func.to_sql()
        assert "bitrotateleft" in sql.lower() or "bitRotateLeft" in sql
        assert func.func_name == "bitRotateLeft"
    
    def test_bitRotateRight(self):
        """Test bitRotateRight function."""
        col = Column("a", UInt64)
        func = bitRotateRight(col, 2)
        sql = func.to_sql()
        assert "bitrotateright" in sql.lower() or "bitRotateRight" in sql
        assert func.func_name == "bitRotateRight"
    
    def test_bitTest(self):
        """Test bitTest function."""
        col = Column("a", UInt64)
        func = bitTest(col, 2)
        sql = func.to_sql()
        assert "bittest" in sql.lower() or "bitTest" in sql
        assert func.func_name == "bitTest"
    
    def test_bitTestAll(self):
        """Test bitTestAll function."""
        col = Column("a", UInt64)
        func = bitTestAll(col, 3)
        sql = func.to_sql()
        assert "bittestall" in sql.lower() or "bitTestAll" in sql
        assert func.func_name == "bitTestAll"
    
    def test_bitTestAny(self):
        """Test bitTestAny function."""
        col = Column("a", UInt64)
        func = bitTestAny(col, 3)
        sql = func.to_sql()
        assert "bittestany" in sql.lower() or "bitTestAny" in sql
        assert func.func_name == "bitTestAny"
    
    def test_bitCount(self):
        """Test bitCount function."""
        col = Column("a", UInt64)
        func = bitCount(col)
        sql = func.to_sql()
        assert "bitcount" in sql.lower() or "bitCount" in sql
        assert func.func_name == "bitCount"



class TestTupleFunctions:
    """Test cases for tuple functions."""
    
    def test_tuple(self):
        """Test tuple function."""
        col1 = Column("a", Int64)
        col2 = Column("b", String)
        func = tuple_func(col1, col2)
        assert func.func_name == "tuple"
        sql = func.to_sql()
        assert "tuple" in sql.lower()
        assert "a" in sql
        assert "b" in sql
    
    def test_tupleElement(self):
        """Test tupleElement function."""
        col = Column("t", "Tuple(Int64, String)")
        func = tupleElement(col, 1)
        assert func.func_name == "tupleElement"
        sql = func.to_sql()
        assert "tupleElement" in sql
        assert "1" in sql
    
    def test_untuple(self):
        """Test untuple function."""
        col = Column("t", "Tuple(Int64, String)")
        func = untuple(col)
        assert func.func_name == "untuple"
        assert func.to_sql() == "untuple(t)"


class TestUUIDFunctions:
    """Test cases for UUID functions."""
    
    def test_generateUUIDv4(self):
        """Test generateUUIDv4 function."""
        func = generateUUIDv4()
        assert func.func_name == "generateUUIDv4"
        assert func.to_sql() == "generateUUIDv4()"
    
    def test_UUIDStringToNum(self):
        """Test UUIDStringToNum function."""
        col = Column("uuid_str", String)
        func = UUIDStringToNum(col)
        assert func.func_name == "UUIDStringToNum"
        assert func.to_sql() == "UUIDStringToNum(uuid_str)"
    
    def test_UUIDNumToString(self):
        """Test UUIDNumToString function."""
        col = Column("uuid_num", "UInt128")
        func = UUIDNumToString(col)
        assert func.func_name == "UUIDNumToString"
        assert func.to_sql() == "UUIDNumToString(uuid_num)"


class TestArrayFunctions:
    """Test cases for array functions."""
    
    def test_array(self):
        """Test array function."""
        func = array(1, 2, 3)
        assert func.func_name == "array"
        sql = func.to_sql()
        assert "array" in sql.lower()
    
    def test_arrayConcat(self):
        """Test arrayConcat function."""
        col1 = Column("arr1", "Array(Int64)")
        col2 = Column("arr2", "Array(Int64)")
        func = arrayConcat(col1, col2)
        assert func.func_name == "arrayConcat"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayElement(self):
        """Test arrayElement function."""
        col = Column("arr", "Array(Int64)")
        func = arrayElement(col, 1)
        assert func.func_name == "arrayElement"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "1" in sql
    
    def test_has(self):
        """Test has function."""
        col = Column("arr", "Array(Int64)")
        func = has(col, 5)
        assert func.func_name == "has"
        sql = func.to_sql()
        assert "has" in sql.lower()
    
    def test_hasAll(self):
        """Test hasAll function."""
        col1 = Column("arr1", "Array(Int64)")
        col2 = Column("arr2", "Array(Int64)")
        func = hasAll(col1, col2)
        assert func.func_name == "hasAll"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_hasAny(self):
        """Test hasAny function."""
        col1 = Column("arr1", "Array(Int64)")
        col2 = Column("arr2", "Array(Int64)")
        func = hasAny(col1, col2)
        assert func.func_name == "hasAny"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_indexOf(self):
        """Test indexOf function."""
        col = Column("arr", "Array(Int64)")
        func = indexOf(col, 5)
        assert func.func_name == "indexOf"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_countEqual(self):
        """Test countEqual function."""
        col = Column("arr", "Array(Int64)")
        func = countEqual(col, 5)
        assert func.func_name == "countEqual"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayEnumerate(self):
        """Test arrayEnumerate function."""
        col = Column("arr", "Array(Int64)")
        func = arrayEnumerate(col)
        assert func.func_name == "arrayEnumerate"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayEnumerateDense(self):
        """Test arrayEnumerateDense function."""
        col = Column("arr", "Array(Int64)")
        func = arrayEnumerateDense(col)
        assert func.func_name == "arrayEnumerateDense"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayEnumerateUniq(self):
        """Test arrayEnumerateUniq function."""
        col = Column("arr", "Array(Int64)")
        func = arrayEnumerateUniq(col)
        assert func.func_name == "arrayEnumerateUniq"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayPopBack(self):
        """Test arrayPopBack function."""
        col = Column("arr", "Array(Int64)")
        func = arrayPopBack(col)
        assert func.func_name == "arrayPopBack"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayPopFront(self):
        """Test arrayPopFront function."""
        col = Column("arr", "Array(Int64)")
        func = arrayPopFront(col)
        assert func.func_name == "arrayPopFront"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayPushBack(self):
        """Test arrayPushBack function."""
        col = Column("arr", "Array(Int64)")
        func = arrayPushBack(col, 5)
        assert func.func_name == "arrayPushBack"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayPushFront(self):
        """Test arrayPushFront function."""
        col = Column("arr", "Array(Int64)")
        func = arrayPushFront(col, 5)
        assert func.func_name == "arrayPushFront"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayResize(self):
        """Test arrayResize function."""
        col = Column("arr", "Array(Int64)")
        func = arrayResize(col, 10)
        assert func.func_name == "arrayResize"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "10" in sql
    
    def test_arraySlice(self):
        """Test arraySlice function."""
        col = Column("arr", "Array(Int64)")
        func = arraySlice(col, 1, 3)
        assert func.func_name == "arraySlice"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "1" in sql
        assert "3" in sql
    
    def test_arraySort(self):
        """Test arraySort function."""
        col = Column("arr", "Array(Int64)")
        func = arraySort(col)
        assert func.func_name == "arraySort"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayReverseSort(self):
        """Test arrayReverseSort function."""
        col = Column("arr", "Array(Int64)")
        func = arrayReverseSort(col)
        assert func.func_name == "arrayReverseSort"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayUniq(self):
        """Test arrayUniq function."""
        col = Column("arr", "Array(Int64)")
        func = arrayUniq(col)
        assert func.func_name == "arrayUniq"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayJoin(self):
        """Test arrayJoin function."""
        col = Column("arr", "Array(Int64)")
        func = arrayJoin(col)
        assert func.func_name == "arrayJoin"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayMap(self):
        """Test arrayMap function."""
        col = Column("arr", "Array(Int64)")
        func = arrayMap("x -> x * 2", col)
        assert func.func_name == "arrayMap"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayFilter(self):
        """Test arrayFilter function."""
        col = Column("arr", "Array(Int64)")
        func = arrayFilter("x -> x > 0", col)
        assert func.func_name == "arrayFilter"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayCount(self):
        """Test arrayCount function."""
        col = Column("arr", "Array(Int64)")
        func = arrayCount("x -> x > 0", col)
        assert func.func_name == "arrayCount"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayExists(self):
        """Test arrayExists function."""
        col = Column("arr", "Array(Int64)")
        func = arrayExists("x -> x > 0", col)
        assert func.func_name == "arrayExists"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayAll(self):
        """Test arrayAll function."""
        col = Column("arr", "Array(Int64)")
        func = arrayAll("x -> x > 0", col)
        assert func.func_name == "arrayAll"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arraySum(self):
        """Test arraySum function."""
        col = Column("arr", "Array(Int64)")
        func = arraySum(col)
        assert func.func_name == "arraySum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayAvg(self):
        """Test arrayAvg function."""
        col = Column("arr", "Array(Int64)")
        func = arrayAvg(col)
        assert func.func_name == "arrayAvg"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayCumSum(self):
        """Test arrayCumSum function."""
        col = Column("arr", "Array(Int64)")
        func = arrayCumSum(col)
        assert func.func_name == "arrayCumSum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayProduct(self):
        """Test arrayProduct function."""
        col = Column("arr", "Array(Int64)")
        func = arrayProduct(col)
        assert func.func_name == "arrayProduct"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayReduce(self):
        """Test arrayReduce function."""
        col = Column("arr", "Array(Int64)")
        func = arrayReduce("max", col)
        assert func.func_name == "arrayReduce"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayReverse(self):
        """Test arrayReverse function."""
        col = Column("arr", "Array(Int64)")
        func = arrayReverse(col)
        assert func.func_name == "arrayReverse"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayFlatten(self):
        """Test arrayFlatten function."""
        col = Column("arr", "Array(Array(Int64))")
        func = arrayFlatten(col)
        assert func.func_name == "arrayFlatten"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayZip(self):
        """Test arrayZip function."""
        col1 = Column("arr1", "Array(Int64)")
        col2 = Column("arr2", "Array(String)")
        func = arrayZip(col1, col2)
        assert func.func_name == "arrayZip"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayAUC(self):
        """Test arrayAUC function."""
        col = Column("arr", "Array(Float64)")
        func = arrayAUC(col)
        assert func.func_name == "arrayAUC"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayDifference(self):
        """Test arrayDifference function."""
        col = Column("arr", "Array(Int64)")
        func = arrayDifference(col)
        assert func.func_name == "arrayDifference"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayDistinct(self):
        """Test arrayDistinct function."""
        col = Column("arr", "Array(Int64)")
        func = arrayDistinct(col)
        assert func.func_name == "arrayDistinct"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayIntersect(self):
        """Test arrayIntersect function."""
        col1 = Column("arr1", "Array(Int64)")
        col2 = Column("arr2", "Array(Int64)")
        func = arrayIntersect(col1, col2)
        assert func.func_name == "arrayIntersect"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayReduceInRanges(self):
        """Test arrayReduceInRanges function."""
        col = Column("arr", "Array(Int64)")
        ranges = Column("ranges", "Array(Tuple(Int64, Int64))")
        func = arrayReduceInRanges("max", ranges, col)
        assert func.func_name == "arrayReduceInRanges"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arraySplit(self):
        """Test arraySplit function."""
        col = Column("arr", "Array(Int64)")
        func = arraySplit("x -> x > 0", col)
        assert func.func_name == "arraySplit"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayStringConcat(self):
        """Test arrayStringConcat function."""
        col = Column("arr", "Array(String)")
        func = arrayStringConcat(col, ",")
        assert func.func_name == "arrayStringConcat"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayMin(self):
        """Test arrayMin function."""
        col = Column("arr", "Array(Int64)")
        func = arrayMin(col)
        assert func.func_name == "arrayMin"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_arrayMax(self):
        """Test arrayMax function."""
        col = Column("arr", "Array(Int64)")
        func = arrayMax(col)
        assert func.func_name == "arrayMax"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestExtendedDateTimeFunctions:
    """Test cases for additional date/time functions."""
    
    def test_yesterday(self):
        """Test yesterday function."""
        func = yesterday()
        assert func.func_name == "yesterday"
        assert func.to_sql() == "yesterday()"
    
    def test_timeSlot(self):
        """Test timeSlot function."""
        col = Column("dt", "DateTime")
        func = timeSlot(col)
        assert func.func_name == "timeSlot"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toQuarter(self):
        """Test toQuarter function."""
        col = Column("dt", "DateTime")
        func = toQuarter(col)
        assert func.func_name == "toQuarter"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toWeek(self):
        """Test toWeek function."""
        col = Column("dt", "DateTime")
        func = toWeek(col)
        assert func.func_name == "toWeek"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toDayOfYear(self):
        """Test toDayOfYear function."""
        col = Column("dt", "DateTime")
        func = toDayOfYear(col)
        assert func.func_name == "toDayOfYear"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toDayOfWeek(self):
        """Test toDayOfWeek function."""
        col = Column("dt", "DateTime")
        func = toDayOfWeek(col)
        assert func.func_name == "toDayOfWeek"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toMinute(self):
        """Test toMinute function."""
        col = Column("dt", "DateTime")
        func = toMinute(col)
        assert func.func_name == "toMinute"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toSecond(self):
        """Test toSecond function."""
        col = Column("dt", "DateTime")
        func = toSecond(col)
        assert func.func_name == "toSecond"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfYear(self):
        """Test toStartOfYear function."""
        col = Column("dt", "DateTime")
        func = toStartOfYear(col)
        assert func.func_name == "toStartOfYear"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfQuarter(self):
        """Test toStartOfQuarter function."""
        col = Column("dt", "DateTime")
        func = toStartOfQuarter(col)
        assert func.func_name == "toStartOfQuarter"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfMonth(self):
        """Test toStartOfMonth function."""
        col = Column("dt", "DateTime")
        func = toStartOfMonth(col)
        assert func.func_name == "toStartOfMonth"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfWeek(self):
        """Test toStartOfWeek function."""
        col = Column("dt", "DateTime")
        func = toStartOfWeek(col)
        assert func.func_name == "toStartOfWeek"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfDay(self):
        """Test toStartOfDay function."""
        col = Column("dt", "DateTime")
        func = toStartOfDay(col)
        assert func.func_name == "toStartOfDay"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfHour(self):
        """Test toStartOfHour function."""
        col = Column("dt", "DateTime")
        func = toStartOfHour(col)
        assert func.func_name == "toStartOfHour"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfMinute(self):
        """Test toStartOfMinute function."""
        col = Column("dt", "DateTime")
        func = toStartOfMinute(col)
        assert func.func_name == "toStartOfMinute"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfSecond(self):
        """Test toStartOfSecond function."""
        col = Column("dt", "DateTime")
        func = toStartOfSecond(col)
        assert func.func_name == "toStartOfSecond"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfFiveMinute(self):
        """Test toStartOfFiveMinute function."""
        col = Column("dt", "DateTime")
        func = toStartOfFiveMinute(col)
        assert func.func_name == "toStartOfFiveMinute"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfTenMinute(self):
        """Test toStartOfTenMinute function."""
        col = Column("dt", "DateTime")
        func = toStartOfTenMinute(col)
        assert func.func_name == "toStartOfTenMinute"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toStartOfFifteenMinute(self):
        """Test toStartOfFifteenMinute function."""
        col = Column("dt", "DateTime")
        func = toStartOfFifteenMinute(col)
        assert func.func_name == "toStartOfFifteenMinute"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toTime(self):
        """Test toTime function."""
        col = Column("dt", "DateTime")
        func = toTime(col)
        assert func.func_name == "toTime"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeYearNum(self):
        """Test toRelativeYearNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeYearNum(col)
        assert func.func_name == "toRelativeYearNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeQuarterNum(self):
        """Test toRelativeQuarterNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeQuarterNum(col)
        assert func.func_name == "toRelativeQuarterNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeMonthNum(self):
        """Test toRelativeMonthNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeMonthNum(col)
        assert func.func_name == "toRelativeMonthNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeWeekNum(self):
        """Test toRelativeWeekNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeWeekNum(col)
        assert func.func_name == "toRelativeWeekNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeDayNum(self):
        """Test toRelativeDayNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeDayNum(col)
        assert func.func_name == "toRelativeDayNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeHourNum(self):
        """Test toRelativeHourNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeHourNum(col)
        assert func.func_name == "toRelativeHourNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeMinuteNum(self):
        """Test toRelativeMinuteNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeMinuteNum(col)
        assert func.func_name == "toRelativeMinuteNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toRelativeSecondNum(self):
        """Test toRelativeSecondNum function."""
        col = Column("dt", "DateTime")
        func = toRelativeSecondNum(col)
        assert func.func_name == "toRelativeSecondNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toISOYear(self):
        """Test toISOYear function."""
        col = Column("dt", "DateTime")
        func = toISOYear(col)
        assert func.func_name == "toISOYear"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toISOWeek(self):
        """Test toISOWeek function."""
        col = Column("dt", "DateTime")
        func = toISOWeek(col)
        assert func.func_name == "toISOWeek"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toISOYearWeek(self):
        """Test toISOYearWeek function."""
        col = Column("dt", "DateTime")
        func = toISOYearWeek(col)
        assert func.func_name == "toISOYearWeek"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toMonday(self):
        """Test toMonday function."""
        col = Column("dt", "DateTime")
        func = toMonday(col)
        assert func.func_name == "toMonday"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toYYYYMM(self):
        """Test toYYYYMM function."""
        col = Column("dt", "DateTime")
        func = toYYYYMM(col)
        assert func.func_name == "toYYYYMM"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toYYYYMMDD(self):
        """Test toYYYYMMDD function."""
        col = Column("dt", "DateTime")
        func = toYYYYMMDD(col)
        assert func.func_name == "toYYYYMMDD"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toYYYYMMDDhhmmss(self):
        """Test toYYYYMMDDhhmmss function."""
        col = Column("dt", "DateTime")
        func = toYYYYMMDDhhmmss(col)
        assert func.func_name == "toYYYYMMDDhhmmss"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_addYears(self):
        """Test addYears function."""
        col = Column("dt", "DateTime")
        func = addYears(col, 1)
        assert func.func_name == "addYears"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "1" in sql
    
    def test_addQuarters(self):
        """Test addQuarters function."""
        col = Column("dt", "DateTime")
        func = addQuarters(col, 1)
        assert func.func_name == "addQuarters"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_addMonths(self):
        """Test addMonths function."""
        col = Column("dt", "DateTime")
        func = addMonths(col, 1)
        assert func.func_name == "addMonths"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_addWeeks(self):
        """Test addWeeks function."""
        col = Column("dt", "DateTime")
        func = addWeeks(col, 1)
        assert func.func_name == "addWeeks"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_addHours(self):
        """Test addHours function."""
        col = Column("dt", "DateTime")
        func = addHours(col, 1)
        assert func.func_name == "addHours"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_addMinutes(self):
        """Test addMinutes function."""
        col = Column("dt", "DateTime")
        func = addMinutes(col, 30)
        assert func.func_name == "addMinutes"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_addSeconds(self):
        """Test addSeconds function."""
        col = Column("dt", "DateTime")
        func = addSeconds(col, 60)
        assert func.func_name == "addSeconds"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractYears(self):
        """Test subtractYears function."""
        col = Column("dt", "DateTime")
        func = subtractYears(col, 1)
        assert func.func_name == "subtractYears"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractQuarters(self):
        """Test subtractQuarters function."""
        col = Column("dt", "DateTime")
        func = subtractQuarters(col, 1)
        assert func.func_name == "subtractQuarters"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractMonths(self):
        """Test subtractMonths function."""
        col = Column("dt", "DateTime")
        func = subtractMonths(col, 1)
        assert func.func_name == "subtractMonths"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractWeeks(self):
        """Test subtractWeeks function."""
        col = Column("dt", "DateTime")
        func = subtractWeeks(col, 1)
        assert func.func_name == "subtractWeeks"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractHours(self):
        """Test subtractHours function."""
        col = Column("dt", "DateTime")
        func = subtractHours(col, 1)
        assert func.func_name == "subtractHours"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractMinutes(self):
        """Test subtractMinutes function."""
        col = Column("dt", "DateTime")
        func = subtractMinutes(col, 30)
        assert func.func_name == "subtractMinutes"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_subtractSeconds(self):
        """Test subtractSeconds function."""
        col = Column("dt", "DateTime")
        func = subtractSeconds(col, 60)
        assert func.func_name == "subtractSeconds"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_dateDiff(self):
        """Test dateDiff function."""
        col1 = Column("dt1", "DateTime")
        col2 = Column("dt2", "DateTime")
        func = dateDiff("day", col1, col2)
        assert func.func_name == "dateDiff"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_dateName(self):
        """Test dateName function."""
        col = Column("dt", "DateTime")
        func = dateName("month", col)
        assert func.func_name == "dateName"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_timeZone(self):
        """Test timeZone function."""
        func = timeZone()
        assert func.func_name == "timeZone"
        assert func.to_sql() == "timeZone()"
    
    def test_timeZoneOf(self):
        """Test timeZoneOf function."""
        col = Column("dt", "DateTime")
        func = timeZoneOf(col)
        assert func.func_name == "timeZoneOf"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toTimeZone(self):
        """Test toTimeZone function."""
        col = Column("dt", "DateTime")
        func = toTimeZone(col, "UTC")
        assert func.func_name == "toTimeZone"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_formatDateTime(self):
        """Test formatDateTime function."""
        col = Column("dt", "DateTime")
        func = formatDateTime(col, "%Y-%m-%d")
        assert func.func_name == "formatDateTime"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_parseDateTimeBestEffort(self):
        """Test parseDateTimeBestEffort function."""
        col = Column("str", String)
        func = parseDateTimeBestEffort(col)
        assert func.func_name == "parseDateTimeBestEffort"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestEncodingFunctions:
    """Test cases for encoding functions."""
    
    def test_hex(self):
        """Test hex function."""
        col = Column("val", String)
        func = hex(col)
        assert func.func_name == "hex"
        sql = func.to_sql()
        assert "hex" in sql.lower()
    
    def test_unhex(self):
        """Test unhex function."""
        col = Column("val", String)
        func = unhex(col)
        assert func.func_name == "unhex"
        sql = func.to_sql()
        assert "unhex" in sql.lower()
    
    def test_base64Encode(self):
        """Test base64Encode function."""
        col = Column("val", String)
        func = base64Encode(col)
        assert func.func_name == "base64Encode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_base64Decode(self):
        """Test base64Decode function."""
        col = Column("val", String)
        func = base64Decode(col)
        assert func.func_name == "base64Decode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_tryBase64Decode(self):
        """Test tryBase64Decode function."""
        col = Column("val", String)
        func = tryBase64Decode(col)
        assert func.func_name == "tryBase64Decode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_base32Encode(self):
        """Test base32Encode function."""
        col = Column("val", String)
        func = base32Encode(col)
        assert func.func_name == "base32Encode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_base32Decode(self):
        """Test base32Decode function."""
        col = Column("val", String)
        func = base32Decode(col)
        assert func.func_name == "base32Decode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_base58Encode(self):
        """Test base58Encode function."""
        col = Column("val", String)
        func = base58Encode(col)
        assert func.func_name == "base58Encode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_base58Decode(self):
        """Test base58Decode function."""
        col = Column("val", String)
        func = base58Decode(col)
        assert func.func_name == "base58Decode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestGeoFunctions:
    """Test cases for geo functions."""
    
    def test_greatCircleDistance(self):
        """Test greatCircleDistance function."""
        col1 = Column("lat1", Float64)
        col2 = Column("lon1", Float64)
        col3 = Column("lat2", Float64)
        col4 = Column("lon2", Float64)
        func = greatCircleDistance(col1, col2, col3, col4)
        assert func.func_name == "greatCircleDistance"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_geoDistance(self):
        """Test geoDistance function."""
        col1 = Column("lon1", Float64)
        col2 = Column("lat1", Float64)
        col3 = Column("lon2", Float64)
        col4 = Column("lat2", Float64)
        func = geoDistance(col1, col2, col3, col4)
        assert func.func_name == "geoDistance"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_pointInPolygon(self):
        """Test pointInPolygon function."""
        col1 = Column("point", "Tuple(Float64, Float64)")
        col2 = Column("polygon", "Array(Array(Tuple(Float64, Float64)))")
        func = pointInPolygon(col1, col2)
        assert func.func_name == "pointInPolygon"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_geohashEncode(self):
        """Test geohashEncode function."""
        col1 = Column("lat", Float64)
        col2 = Column("lon", Float64)
        func = geohashEncode(col1, col2, 10)
        assert func.func_name == "geohashEncode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "10" in sql
    
    def test_geohashDecode(self):
        """Test geohashDecode function."""
        col = Column("geohash", String)
        func = geohashDecode(col)
        assert func.func_name == "geohashDecode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_geohashesInBox(self):
        """Test geohashesInBox function."""
        col1 = Column("lon_min", Float64)
        col2 = Column("lat_min", Float64)
        col3 = Column("lon_max", Float64)
        col4 = Column("lat_max", Float64)
        func = geohashesInBox(col1, col2, col3, col4, 10)
        assert func.func_name == "geohashesInBox"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "10" in sql


class TestHashFunctions:
    """Test cases for hash functions."""
    
    def test_halfMD5(self):
        """Test halfMD5 function."""
        col = Column("val", String)
        func = halfMD5(col)
        assert func.func_name == "halfMD5"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_MD5(self):
        """Test MD5 function."""
        col = Column("val", String)
        func = MD5(col)
        assert func.func_name == "MD5"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_SHA1(self):
        """Test SHA1 function."""
        col = Column("val", String)
        func = SHA1(col)
        assert func.func_name == "SHA1"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_SHA224(self):
        """Test SHA224 function."""
        col = Column("val", String)
        func = SHA224(col)
        assert func.func_name == "SHA224"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_SHA256(self):
        """Test SHA256 function."""
        col = Column("val", String)
        func = SHA256(col)
        assert func.func_name == "SHA256"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_SHA512(self):
        """Test SHA512 function."""
        col = Column("val", String)
        func = SHA512(col)
        assert func.func_name == "SHA512"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cityHash64(self):
        """Test cityHash64 function."""
        col = Column("val", String)
        func = cityHash64(col)
        assert func.func_name == "cityHash64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_farmHash64(self):
        """Test farmHash64 function."""
        col = Column("val", String)
        func = farmHash64(col)
        assert func.func_name == "farmHash64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_metroHash64(self):
        """Test metroHash64 function."""
        col = Column("val", String)
        func = metroHash64(col)
        assert func.func_name == "metroHash64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_sipHash64(self):
        """Test sipHash64 function."""
        col = Column("val", String)
        func = sipHash64(col)
        assert func.func_name == "sipHash64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_sipHash128(self):
        """Test sipHash128 function."""
        col = Column("val", String)
        func = sipHash128(col)
        assert func.func_name == "sipHash128"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_xxHash32(self):
        """Test xxHash32 function."""
        col = Column("val", String)
        func = xxHash32(col)
        assert func.func_name == "xxHash32"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_xxHash64(self):
        """Test xxHash64 function."""
        col = Column("val", String)
        func = xxHash64(col)
        assert func.func_name == "xxHash64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_murmurHash2_32(self):
        """Test murmurHash2_32 function."""
        col = Column("val", String)
        func = murmurHash2_32(col)
        assert func.func_name == "murmurHash2_32"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_murmurHash2_64(self):
        """Test murmurHash2_64 function."""
        col = Column("val", String)
        func = murmurHash2_64(col)
        assert func.func_name == "murmurHash2_64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_murmurHash3_32(self):
        """Test murmurHash3_32 function."""
        col = Column("val", String)
        func = murmurHash3_32(col)
        assert func.func_name == "murmurHash3_32"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_murmurHash3_64(self):
        """Test murmurHash3_64 function."""
        col = Column("val", String)
        func = murmurHash3_64(col)
        assert func.func_name == "murmurHash3_64"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_murmurHash3_128(self):
        """Test murmurHash3_128 function."""
        col = Column("val", String)
        func = murmurHash3_128(col)
        assert func.func_name == "murmurHash3_128"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_gccMurmurHash(self):
        """Test gccMurmurHash function."""
        col = Column("val", String)
        func = gccMurmurHash(col)
        assert func.func_name == "gccMurmurHash"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestIPFunctions:
    """Test cases for IP functions."""
    
    def test_toIPv4(self):
        """Test toIPv4 function."""
        col = Column("ip_str", String)
        func = toIPv4(col)
        assert func.func_name == "toIPv4"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toIPv6(self):
        """Test toIPv6 function."""
        col = Column("ip_str", String)
        func = toIPv6(col)
        assert func.func_name == "toIPv6"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_IPv4NumToString(self):
        """Test IPv4NumToString function."""
        col = Column("ip_num", UInt32)
        func = IPv4NumToString(col)
        assert func.func_name == "IPv4NumToString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_IPv4StringToNum(self):
        """Test IPv4StringToNum function."""
        col = Column("ip_str", String)
        func = IPv4StringToNum(col)
        assert func.func_name == "IPv4StringToNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_IPv6NumToString(self):
        """Test IPv6NumToString function."""
        col = Column("ip_num", "FixedString(16)")
        func = IPv6NumToString(col)
        assert func.func_name == "IPv6NumToString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_IPv6StringToNum(self):
        """Test IPv6StringToNum function."""
        col = Column("ip_str", String)
        func = IPv6StringToNum(col)
        assert func.func_name == "IPv6StringToNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_IPv4CIDRToRange(self):
        """Test IPv4CIDRToRange function."""
        col = Column("ip", String)
        func = IPv4CIDRToRange(col, 24)
        assert func.func_name == "IPv4CIDRToRange"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "24" in sql
    
    def test_IPv6CIDRToRange(self):
        """Test IPv6CIDRToRange function."""
        col = Column("ip", String)
        func = IPv6CIDRToRange(col, 64)
        assert func.func_name == "IPv6CIDRToRange"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "64" in sql
    
    def test_IPv4ToIPv6(self):
        """Test IPv4ToIPv6 function."""
        col = Column("ip", String)
        func = IPv4ToIPv6(col)
        assert func.func_name == "IPv4ToIPv6"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutIPv6(self):
        """Test cutIPv6 function."""
        col = Column("ip", String)
        func = cutIPv6(col, 4)
        assert func.func_name == "cutIPv6"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "4" in sql


class TestJSONFunctions:
    """Test cases for JSON functions."""
    
    def test_JSONHas(self):
        """Test JSONHas function."""
        col = Column("json", String)
        func = JSONHas(col, "$.key")
        assert func.func_name == "JSONHas"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONLength(self):
        """Test JSONLength function."""
        col = Column("json", String)
        func = JSONLength(col, "$.array")
        assert func.func_name == "JSONLength"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONKey(self):
        """Test JSONKey function."""
        col = Column("json", String)
        func = JSONKey(col, 0)
        assert func.func_name == "JSONKey"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "0" in sql
    
    def test_JSONKeys(self):
        """Test JSONKeys function."""
        col = Column("json", String)
        func = JSONKeys(col, "$")
        assert func.func_name == "JSONKeys"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtract(self):
        """Test JSONExtract function."""
        col = Column("json", String)
        func = JSONExtract(col, "$.key", "String")
        assert func.func_name == "JSONExtract"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractString(self):
        """Test JSONExtractString function."""
        col = Column("json", String)
        func = JSONExtractString(col, "$.key")
        assert func.func_name == "JSONExtractString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractInt(self):
        """Test JSONExtractInt function."""
        col = Column("json", String)
        func = JSONExtractInt(col, "$.key")
        assert func.func_name == "JSONExtractInt"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractFloat(self):
        """Test JSONExtractFloat function."""
        col = Column("json", String)
        func = JSONExtractFloat(col, "$.key")
        assert func.func_name == "JSONExtractFloat"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractBool(self):
        """Test JSONExtractBool function."""
        col = Column("json", String)
        func = JSONExtractBool(col, "$.key")
        assert func.func_name == "JSONExtractBool"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractRaw(self):
        """Test JSONExtractRaw function."""
        col = Column("json", String)
        func = JSONExtractRaw(col, "$.key")
        assert func.func_name == "JSONExtractRaw"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractArrayRaw(self):
        """Test JSONExtractArrayRaw function."""
        col = Column("json", String)
        func = JSONExtractArrayRaw(col, "$.array")
        assert func.func_name == "JSONExtractArrayRaw"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractKeysAndValues(self):
        """Test JSONExtractKeysAndValues function."""
        col = Column("json", String)
        func = JSONExtractKeysAndValues(col, "$")
        assert func.func_name == "JSONExtractKeysAndValues"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractKeysAndValuesRaw(self):
        """Test JSONExtractKeysAndValuesRaw function."""
        col = Column("json", String)
        func = JSONExtractKeysAndValuesRaw(col, "$")
        assert func.func_name == "JSONExtractKeysAndValuesRaw"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_JSONExtractUInt(self):
        """Test JSONExtractUInt function."""
        col = Column("json", String)
        func = JSONExtractUInt(col, "$.key")
        assert func.func_name == "JSONExtractUInt"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestMapFunctions:
    """Test cases for map functions."""
    
    def test_map(self):
        """Test map function."""
        col1 = Column("key", String)
        col2 = Column("val", Int64)
        func = map(col1, col2)
        assert func.func_name == "map"
        sql = func.to_sql()
        assert "map" in sql.lower()
    
    def test_mapKeys(self):
        """Test mapKeys function."""
        col = Column("map_col", "Map(String, Int64)")
        func = mapKeys(col)
        assert func.func_name == "mapKeys"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_mapValues(self):
        """Test mapValues function."""
        col = Column("map_col", "Map(String, Int64)")
        func = mapValues(col)
        assert func.func_name == "mapValues"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_mapContains(self):
        """Test mapContains function."""
        col = Column("map_col", "Map(String, Int64)")
        func = mapContains(col, "key")
        assert func.func_name == "mapContains"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_mapGet(self):
        """Test mapGet function."""
        col = Column("map_col", "Map(String, Int64)")
        func = mapGet(col, "key")
        assert func.func_name == "mapGet"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_mapGet_with_default(self):
        """Test mapGet function with default."""
        col = Column("map_col", "Map(String, Int64)")
        func = mapGet(col, "key", 0)
        assert func.func_name == "mapGet"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "0" in sql


class TestExtendedMathFunctions:
    """Test cases for additional math functions."""
    
    def test_e(self):
        """Test e function."""
        func = e()
        assert func.func_name == "e"
        assert func.to_sql() == "e()"
    
    def test_pi(self):
        """Test pi function."""
        func = pi()
        assert func.func_name == "pi"
        assert func.to_sql() == "pi()"
    
    def test_exp(self):
        """Test exp function."""
        col = Column("x", Float64)
        func = exp(col)
        assert func.func_name == "exp"
        sql = func.to_sql()
        assert "exp" in sql.lower()
    
    def test_log(self):
        """Test log function."""
        col = Column("x", Float64)
        func = log(col)
        assert func.func_name == "log"
        sql = func.to_sql()
        assert "log" in sql.lower()
    
    def test_log2(self):
        """Test log2 function."""
        col = Column("x", Float64)
        func = log2(col)
        assert func.func_name == "log2"
        sql = func.to_sql()
        assert "log2" in sql.lower()
    
    def test_log10(self):
        """Test log10 function."""
        col = Column("x", Float64)
        func = log10(col)
        assert func.func_name == "log10"
        sql = func.to_sql()
        assert "log10" in sql.lower()
    
    def test_cbrt(self):
        """Test cbrt function."""
        col = Column("x", Float64)
        func = cbrt(col)
        assert func.func_name == "cbrt"
        sql = func.to_sql()
        assert "cbrt" in sql.lower()
    
    def test_pow(self):
        """Test pow function."""
        col1 = Column("x", Float64)
        col2 = Column("y", Float64)
        func = pow(col1, col2)
        assert func.func_name == "pow"
        sql = func.to_sql()
        assert "pow" in sql.lower()
    
    def test_power(self):
        """Test power function."""
        col1 = Column("x", Float64)
        col2 = Column("y", Float64)
        func = power(col1, col2)
        assert func.func_name == "power"
        sql = func.to_sql()
        assert "power" in sql.lower()
    
    def test_exp2(self):
        """Test exp2 function."""
        col = Column("x", Float64)
        func = exp2(col)
        assert func.func_name == "exp2"
        sql = func.to_sql()
        assert "exp2" in sql.lower()
    
    def test_exp10(self):
        """Test exp10 function."""
        col = Column("x", Float64)
        func = exp10(col)
        assert func.func_name == "exp10"
        sql = func.to_sql()
        assert "exp10" in sql.lower()
    
    def test_log1p(self):
        """Test log1p function."""
        col = Column("x", Float64)
        func = log1p(col)
        assert func.func_name == "log1p"
        sql = func.to_sql()
        assert "log1p" in sql.lower()
    
    def test_sign(self):
        """Test sign function."""
        col = Column("x", Float64)
        func = sign(col)
        assert func.func_name == "sign"
        sql = func.to_sql()
        assert "sign" in sql.lower()
    
    def test_sin(self):
        """Test sin function."""
        col = Column("x", Float64)
        func = sin(col)
        assert func.func_name == "sin"
        sql = func.to_sql()
        assert "sin" in sql.lower()
    
    def test_cos(self):
        """Test cos function."""
        col = Column("x", Float64)
        func = cos(col)
        assert func.func_name == "cos"
        sql = func.to_sql()
        assert "cos" in sql.lower()
    
    def test_tan(self):
        """Test tan function."""
        col = Column("x", Float64)
        func = tan(col)
        assert func.func_name == "tan"
        sql = func.to_sql()
        assert "tan" in sql.lower()
    
    def test_asin(self):
        """Test asin function."""
        col = Column("x", Float64)
        func = asin(col)
        assert func.func_name == "asin"
        sql = func.to_sql()
        assert "asin" in sql.lower()
    
    def test_acos(self):
        """Test acos function."""
        col = Column("x", Float64)
        func = acos(col)
        assert func.func_name == "acos"
        sql = func.to_sql()
        assert "acos" in sql.lower()
    
    def test_atan(self):
        """Test atan function."""
        col = Column("x", Float64)
        func = atan(col)
        assert func.func_name == "atan"
        sql = func.to_sql()
        assert "atan" in sql.lower()
    
    def test_atan2(self):
        """Test atan2 function."""
        col1 = Column("y", Float64)
        col2 = Column("x", Float64)
        func = atan2(col1, col2)
        assert func.func_name == "atan2"
        sql = func.to_sql()
        assert "atan2" in sql.lower()
    
    def test_sinh(self):
        """Test sinh function."""
        col = Column("x", Float64)
        func = sinh(col)
        assert func.func_name == "sinh"
        sql = func.to_sql()
        assert "sinh" in sql.lower()
    
    def test_cosh(self):
        """Test cosh function."""
        col = Column("x", Float64)
        func = cosh(col)
        assert func.func_name == "cosh"
        sql = func.to_sql()
        assert "cosh" in sql.lower()
    
    def test_tanh(self):
        """Test tanh function."""
        col = Column("x", Float64)
        func = tanh(col)
        assert func.func_name == "tanh"
        sql = func.to_sql()
        assert "tanh" in sql.lower()
    
    def test_asinh(self):
        """Test asinh function."""
        col = Column("x", Float64)
        func = asinh(col)
        assert func.func_name == "asinh"
        sql = func.to_sql()
        assert "asinh" in sql.lower()
    
    def test_acosh(self):
        """Test acosh function."""
        col = Column("x", Float64)
        func = acosh(col)
        assert func.func_name == "acosh"
        sql = func.to_sql()
        assert "acosh" in sql.lower()
    
    def test_atanh(self):
        """Test atanh function."""
        col = Column("x", Float64)
        func = atanh(col)
        assert func.func_name == "atanh"
        sql = func.to_sql()
        assert "atanh" in sql.lower()
    
    def test_hypot(self):
        """Test hypot function."""
        col1 = Column("x", Float64)
        col2 = Column("y", Float64)
        func = hypot(col1, col2)
        assert func.func_name == "hypot"
        sql = func.to_sql()
        assert "hypot" in sql.lower()
    
    def test_logGamma(self):
        """Test logGamma function."""
        col = Column("x", Float64)
        func = logGamma(col)
        assert func.func_name == "logGamma"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_tgamma(self):
        """Test tgamma function."""
        col = Column("x", Float64)
        func = tgamma(col)
        assert func.func_name == "tgamma"
        sql = func.to_sql()
        assert "tgamma" in sql.lower()
    
    def test_lgamma(self):
        """Test lgamma function."""
        col = Column("x", Float64)
        func = lgamma(col)
        assert func.func_name == "lgamma"
        sql = func.to_sql()
        assert "lgamma" in sql.lower()
    
    def test_erf(self):
        """Test erf function."""
        col = Column("x", Float64)
        func = erf(col)
        assert func.func_name == "erf"
        sql = func.to_sql()
        assert "erf" in sql.lower()
    
    def test_erfc(self):
        """Test erfc function."""
        col = Column("x", Float64)
        func = erfc(col)
        assert func.func_name == "erfc"
        sql = func.to_sql()
        assert "erfc" in sql.lower()
    
    def test_erfInv(self):
        """Test erfInv function."""
        col = Column("x", Float64)
        func = erfInv(col)
        assert func.func_name == "erfInv"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_erfcInv(self):
        """Test erfcInv function."""
        col = Column("x", Float64)
        func = erfcInv(col)
        assert func.func_name == "erfcInv"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestExtendedNullableFunctions:
    """Test cases for additional nullable functions."""
    
    def test_isNull(self):
        """Test isNull function."""
        col = Column("x", "Nullable(Int64)")
        func = isNull(col)
        assert func.func_name == "isNull"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_isNotNull(self):
        """Test isNotNull function."""
        col = Column("x", "Nullable(Int64)")
        func = isNotNull(col)
        assert func.func_name == "isNotNull"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_assumeNotNull(self):
        """Test assumeNotNull function."""
        col = Column("x", "Nullable(Int64)")
        func = assumeNotNull(col)
        assert func.func_name == "assumeNotNull"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestOtherFunctions:
    """Test cases for other functions."""
    
    def test_hostName(self):
        """Test hostName function."""
        func = hostName()
        assert func.func_name == "hostName"
        assert func.to_sql() == "hostName()"
    
    def test_getMacro(self):
        """Test getMacro function."""
        func = getMacro("macro_name")
        assert func.func_name == "getMacro"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_FQDN(self):
        """Test FQDN function."""
        func = FQDN()
        assert func.func_name == "FQDN"
        assert func.to_sql() == "FQDN()"
    
    def test_basename(self):
        """Test basename function."""
        col = Column("path", String)
        func = basename(col)
        assert func.func_name == "basename"
        sql = func.to_sql()
        assert "basename" in sql.lower()
    
    def test_visibleWidth(self):
        """Test visibleWidth function."""
        col = Column("x", String)
        func = visibleWidth(col)
        assert func.func_name == "visibleWidth"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_toTypeName(self):
        """Test toTypeName function."""
        col = Column("x", Int64)
        func = toTypeName(col)
        assert func.func_name == "toTypeName"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_blockSize(self):
        """Test blockSize function."""
        func = blockSize()
        assert func.func_name == "blockSize"
        assert func.to_sql() == "blockSize()"
    
    def test_blockNumber(self):
        """Test blockNumber function."""
        func = blockNumber()
        assert func.func_name == "blockNumber"
        assert func.to_sql() == "blockNumber()"
    
    def test_rowNumberInBlock(self):
        """Test rowNumberInBlock function."""
        func = rowNumberInBlock()
        assert func.func_name == "rowNumberInBlock"
        assert func.to_sql() == "rowNumberInBlock()"
    
    def test_rowNumberInAllBlocks(self):
        """Test rowNumberInAllBlocks function."""
        func = rowNumberInAllBlocks()
        assert func.func_name == "rowNumberInAllBlocks"
        assert func.to_sql() == "rowNumberInAllBlocks()"
    
    def test_neighbor(self):
        """Test neighbor function."""
        col = Column("x", Int64)
        func = neighbor(col, 1)
        assert func.func_name == "neighbor"
        sql = func.to_sql()
        assert "neighbor" in sql.lower()
        assert "1" in sql
    
    def test_neighbor_with_default(self):
        """Test neighbor function with default."""
        col = Column("x", Int64)
        func = neighbor(col, 1, 0)
        assert func.func_name == "neighbor"
        sql = func.to_sql()
        assert "neighbor" in sql.lower()
        assert "0" in sql
    
    def test_runningAccumulate(self):
        """Test runningAccumulate function."""
        col = Column("x", Int64)
        func = runningAccumulate(col)
        assert func.func_name == "runningAccumulate"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_runningDifference(self):
        """Test runningDifference function."""
        col = Column("x", Int64)
        func = runningDifference(col)
        assert func.func_name == "runningDifference"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_runningDifferenceStartingWithFirstValue(self):
        """Test runningDifferenceStartingWithFirstValue function."""
        col = Column("x", Int64)
        func = runningDifferenceStartingWithFirstValue(col)
        assert func.func_name == "runningDifferenceStartingWithFirstValue"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_finalizeAggregation(self):
        """Test finalizeAggregation function."""
        col = Column("state", "AggregateFunction(sum, Int64)")
        func = finalizeAggregation(col)
        assert func.func_name == "finalizeAggregation"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestExtendedStringFunctions:
    """Test cases for additional string functions."""
    
    def test_empty(self):
        """Test empty function."""
        col = Column("s", String)
        func = empty(col)
        assert func.func_name == "empty"
        sql = func.to_sql()
        assert "empty" in sql.lower()
    
    def test_notEmpty(self):
        """Test notEmpty function."""
        col = Column("s", String)
        func = notEmpty(col)
        assert func.func_name == "notEmpty"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_lengthUTF8(self):
        """Test lengthUTF8 function."""
        col = Column("s", String)
        func = lengthUTF8(col)
        assert func.func_name == "lengthUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_lowerUTF8(self):
        """Test lowerUTF8 function."""
        col = Column("s", String)
        func = lowerUTF8(col)
        assert func.func_name == "lowerUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_upperUTF8(self):
        """Test upperUTF8 function."""
        col = Column("s", String)
        func = upperUTF8(col)
        assert func.func_name == "upperUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_reverse(self):
        """Test reverse function."""
        col = Column("s", String)
        func = reverse(col)
        assert func.func_name == "reverse"
        sql = func.to_sql()
        assert "reverse" in sql.lower()
    
    def test_reverseUTF8(self):
        """Test reverseUTF8 function."""
        col = Column("s", String)
        func = reverseUTF8(col)
        assert func.func_name == "reverseUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_concatAssumeInjective(self):
        """Test concatAssumeInjective function."""
        col1 = Column("s1", String)
        col2 = Column("s2", String)
        func = concatAssumeInjective(col1, col2)
        assert func.func_name == "concatAssumeInjective"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_substringUTF8(self):
        """Test substringUTF8 function."""
        col = Column("s", String)
        func = substringUTF8(col, 1, 3)
        assert func.func_name == "substringUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_appendTrailingCharIfAbsent(self):
        """Test appendTrailingCharIfAbsent function."""
        col = Column("s", String)
        func = appendTrailingCharIfAbsent(col, "/")
        assert func.func_name == "appendTrailingCharIfAbsent"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_left(self):
        """Test left function."""
        col = Column("s", String)
        func = left(col, 5)
        assert func.func_name == "left"
        sql = func.to_sql()
        assert "left" in sql.lower()
        assert "5" in sql
    
    def test_right(self):
        """Test right function."""
        col = Column("s", String)
        func = right(col, 5)
        assert func.func_name == "right"
        sql = func.to_sql()
        assert "right" in sql.lower()
        assert "5" in sql
    
    def test_trimLeft(self):
        """Test trimLeft function."""
        col = Column("s", String)
        func = trimLeft(col)
        assert func.func_name == "trimLeft"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_trimRight(self):
        """Test trimRight function."""
        col = Column("s", String)
        func = trimRight(col)
        assert func.func_name == "trimRight"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_trimBoth(self):
        """Test trimBoth function."""
        col = Column("s", String)
        func = trimBoth(col)
        assert func.func_name == "trimBoth"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_format_str(self):
        """Test format function."""
        col = Column("x", Int64)
        func = format_str("Hello %d", col)
        assert func.func_name == "format"
        sql = func.to_sql()
        assert "format" in sql.lower()
    
    def test_formatReadableQuantity(self):
        """Test formatReadableQuantity function."""
        col = Column("x", Int64)
        func = formatReadableQuantity(col)
        assert func.func_name == "formatReadableQuantity"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_formatReadableSize(self):
        """Test formatReadableSize function."""
        col = Column("x", Int64)
        func = formatReadableSize(col)
        assert func.func_name == "formatReadableSize"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_formatReadableTimeDelta(self):
        """Test formatReadableTimeDelta function."""
        col = Column("seconds", Int64)
        func = formatReadableTimeDelta(col)
        assert func.func_name == "formatReadableTimeDelta"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_splitByChar(self):
        """Test splitByChar function."""
        col = Column("s", String)
        func = splitByChar(",", col)
        assert func.func_name == "splitByChar"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_splitByString(self):
        """Test splitByString function."""
        col = Column("s", String)
        func = splitByString("::", col)
        assert func.func_name == "splitByString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_alphaTokens(self):
        """Test alphaTokens function."""
        col = Column("s", String)
        func = alphaTokens(col)
        assert func.func_name == "alphaTokens"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_extractAll(self):
        """Test extractAll function."""
        col = Column("s", String)
        func = extractAll(col, r"\d+")
        assert func.func_name == "extractAll"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_extractAllGroups(self):
        """Test extractAllGroups function."""
        col = Column("s", String)
        func = extractAllGroups(col, r"(\d+)-(\w+)")
        assert func.func_name == "extractAllGroups"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_extractGroups(self):
        """Test extractGroups function."""
        col = Column("s", String)
        func = extractGroups(col, r"(\d+)-(\w+)")
        assert func.func_name == "extractGroups"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_like(self):
        """Test like function."""
        col = Column("s", String)
        func = like(col, "%test%")
        assert func.func_name == "like"
        sql = func.to_sql()
        assert "like" in sql.lower()
    
    def test_notLike(self):
        """Test notLike function."""
        col = Column("s", String)
        func = notLike(col, "%test%")
        assert func.func_name == "notLike"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_match(self):
        """Test match function."""
        col = Column("s", String)
        func = match(col, r"\d+")
        assert func.func_name == "match"
        sql = func.to_sql()
        assert "match" in sql.lower()
    
    def test_multiMatchAny(self):
        """Test multiMatchAny function."""
        col = Column("s", String)
        func = multiMatchAny(col, ["pattern1", "pattern2"])
        assert func.func_name == "multiMatchAny"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_multiMatchAnyIndex(self):
        """Test multiMatchAnyIndex function."""
        col = Column("s", String)
        func = multiMatchAnyIndex(col, ["pattern1", "pattern2"])
        assert func.func_name == "multiMatchAnyIndex"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_multiFuzzyMatchAny(self):
        """Test multiFuzzyMatchAny function."""
        col = Column("s", String)
        func = multiFuzzyMatchAny(col, 2, ["pattern1", "pattern2"])
        assert func.func_name == "multiFuzzyMatchAny"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_replace(self):
        """Test replace function."""
        col = Column("s", String)
        func = replace(col, "old", "new")
        assert func.func_name == "replace"
        sql = func.to_sql()
        assert "replace" in sql.lower()
    
    def test_replaceAll(self):
        """Test replaceAll function."""
        col = Column("s", String)
        func = replaceAll(col, "old", "new")
        assert func.func_name == "replaceAll"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_replaceOne(self):
        """Test replaceOne function."""
        col = Column("s", String)
        func = replaceOne(col, "old", "new")
        assert func.func_name == "replaceOne"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_replaceRegexpOne(self):
        """Test replaceRegexpOne function."""
        col = Column("s", String)
        func = replaceRegexpOne(col, r"\d+", "NUM")
        assert func.func_name == "replaceRegexpOne"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_replaceRegexpAll(self):
        """Test replaceRegexpAll function."""
        col = Column("s", String)
        func = replaceRegexpAll(col, r"\d+", "NUM")
        assert func.func_name == "replaceRegexpAll"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_position(self):
        """Test position function."""
        col = Column("haystack", String)
        func = position(col, "needle")
        assert func.func_name == "position"
        sql = func.to_sql()
        assert "position" in sql.lower()
    
    def test_positionUTF8(self):
        """Test positionUTF8 function."""
        col = Column("haystack", String)
        func = positionUTF8(col, "needle")
        assert func.func_name == "positionUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_positionCaseInsensitive(self):
        """Test positionCaseInsensitive function."""
        col = Column("haystack", String)
        func = positionCaseInsensitive(col, "needle")
        assert func.func_name == "positionCaseInsensitive"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_positionCaseInsensitiveUTF8(self):
        """Test positionCaseInsensitiveUTF8 function."""
        col = Column("haystack", String)
        func = positionCaseInsensitiveUTF8(col, "needle")
        assert func.func_name == "positionCaseInsensitiveUTF8"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_str_base64Encode(self):
        """Test base64Encode function from string module."""
        col = Column("s", String)
        func = str_base64Encode(col)
        assert func.func_name == "base64Encode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_str_base64Decode(self):
        """Test base64Decode function from string module."""
        col = Column("s", String)
        func = str_base64Decode(col)
        assert func.func_name == "base64Decode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_str_tryBase64Decode(self):
        """Test tryBase64Decode function from string module."""
        col = Column("s", String)
        func = str_tryBase64Decode(col)
        assert func.func_name == "tryBase64Decode"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_str_hex(self):
        """Test hex function from string module."""
        col = Column("x", String)
        func = str_hex(col)
        assert func.func_name == "hex"
        sql = func.to_sql()
        assert "hex" in sql.lower()
    
    def test_str_unhex(self):
        """Test unhex function from string module."""
        col = Column("x", String)
        func = str_unhex(col)
        assert func.func_name == "unhex"
        sql = func.to_sql()
        assert "unhex" in sql.lower()
    
    def test_str_UUIDStringToNum(self):
        """Test UUIDStringToNum function from string module."""
        col = Column("s", String)
        func = str_UUIDStringToNum(col)
        assert func.func_name == "UUIDStringToNum"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_str_UUIDNumToString(self):
        """Test UUIDNumToString function from string module."""
        col = Column("x", Int64)
        func = str_UUIDNumToString(col)
        assert func.func_name == "UUIDNumToString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_bitmaskToList(self):
        """Test bitmaskToList function."""
        col = Column("x", Int64)
        func = bitmaskToList(col)
        assert func.func_name == "bitmaskToList"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_bitmaskToArray(self):
        """Test bitmaskToArray function."""
        col = Column("x", Int64)
        func = bitmaskToArray(col)
        assert func.func_name == "bitmaskToArray"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestURLFunctions:
    """Test cases for URL functions."""
    
    def test_protocol(self):
        """Test protocol function."""
        col = Column("url", String)
        func = protocol(col)
        assert func.func_name == "protocol"
        sql = func.to_sql()
        assert "protocol" in sql.lower()
    
    def test_domain(self):
        """Test domain function."""
        col = Column("url", String)
        func = domain(col)
        assert func.func_name == "domain"
        sql = func.to_sql()
        assert "domain" in sql.lower()
    
    def test_domainWithoutWWW(self):
        """Test domainWithoutWWW function."""
        col = Column("url", String)
        func = domainWithoutWWW(col)
        assert func.func_name == "domainWithoutWWW"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_topLevelDomain(self):
        """Test topLevelDomain function."""
        col = Column("url", String)
        func = topLevelDomain(col)
        assert func.func_name == "topLevelDomain"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_firstSignificantSubdomain(self):
        """Test firstSignificantSubdomain function."""
        col = Column("url", String)
        func = firstSignificantSubdomain(col)
        assert func.func_name == "firstSignificantSubdomain"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutToFirstSignificantSubdomain(self):
        """Test cutToFirstSignificantSubdomain function."""
        col = Column("url", String)
        func = cutToFirstSignificantSubdomain(col)
        assert func.func_name == "cutToFirstSignificantSubdomain"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_path(self):
        """Test path function."""
        col = Column("url", String)
        func = path(col)
        assert func.func_name == "path"
        sql = func.to_sql()
        assert "path" in sql.lower()
    
    def test_pathFull(self):
        """Test pathFull function."""
        col = Column("url", String)
        func = pathFull(col)
        assert func.func_name == "pathFull"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_queryString(self):
        """Test queryString function."""
        col = Column("url", String)
        func = queryString(col)
        assert func.func_name == "queryString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_fragment(self):
        """Test fragment function."""
        col = Column("url", String)
        func = fragment(col)
        assert func.func_name == "fragment"
        sql = func.to_sql()
        assert "fragment" in sql.lower()
    
    def test_queryStringAndFragment(self):
        """Test queryStringAndFragment function."""
        col = Column("url", String)
        func = queryStringAndFragment(col)
        assert func.func_name == "queryStringAndFragment"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_extractURLParameter(self):
        """Test extractURLParameter function."""
        col = Column("url", String)
        func = extractURLParameter(col, "param")
        assert func.func_name == "extractURLParameter"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_extractURLParameters(self):
        """Test extractURLParameters function."""
        col = Column("url", String)
        func = extractURLParameters(col)
        assert func.func_name == "extractURLParameters"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_extractURLParameterNames(self):
        """Test extractURLParameterNames function."""
        col = Column("url", String)
        func = extractURLParameterNames(col)
        assert func.func_name == "extractURLParameterNames"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutURLParameter(self):
        """Test cutURLParameter function."""
        col = Column("url", String)
        func = cutURLParameter(col, "param")
        assert func.func_name == "cutURLParameter"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutWWW(self):
        """Test cutWWW function."""
        col = Column("url", String)
        func = cutWWW(col)
        assert func.func_name == "cutWWW"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutQueryString(self):
        """Test cutQueryString function."""
        col = Column("url", String)
        func = cutQueryString(col)
        assert func.func_name == "cutQueryString"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutFragment(self):
        """Test cutFragment function."""
        col = Column("url", String)
        func = cutFragment(col)
        assert func.func_name == "cutFragment"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_cutQueryStringAndFragment(self):
        """Test cutQueryStringAndFragment function."""
        col = Column("url", String)
        func = cutQueryStringAndFragment(col)
        assert func.func_name == "cutQueryStringAndFragment"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_decodeURLComponent(self):
        """Test decodeURLComponent function."""
        col = Column("url", String)
        func = decodeURLComponent(col)
        assert func.func_name == "decodeURLComponent"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_encodeURLComponent(self):
        """Test encodeURLComponent function."""
        col = Column("url", String)
        func = encodeURLComponent(col)
        assert func.func_name == "encodeURLComponent"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()


class TestWindowFunctions:
    """Test cases for window functions."""
    
    def test_rowNumber(self):
        """Test rowNumber function."""
        func = rowNumber()
        assert func.func_name == "row_number"
        assert func.to_sql() == "row_number()"
    
    def test_rank(self):
        """Test rank function."""
        func = rank()
        assert func.func_name == "rank"
        assert func.to_sql() == "rank()"
    
    def test_denseRank(self):
        """Test denseRank function."""
        func = denseRank()
        assert func.func_name == "denseRank"
        assert func.to_sql() == "denseRank()"
    
    def test_percentRank(self):
        """Test percentRank function."""
        func = percentRank()
        assert func.func_name == "percentRank"
        assert func.to_sql() == "percentRank()"
    
    def test_cumeDist(self):
        """Test cumeDist function."""
        func = cumeDist()
        assert func.func_name == "cumeDist"
        assert func.to_sql() == "cumeDist()"
    
    def test_ntile(self):
        """Test ntile function."""
        func = ntile(4)
        assert func.func_name == "ntile"
        sql = func.to_sql()
        assert "ntile" in sql.lower()
        assert "4" in sql
    
    def test_lagInFrame(self):
        """Test lagInFrame function."""
        col = Column("x", Int64)
        func = lagInFrame(col, 1)
        assert func.func_name == "lagInFrame"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "1" in sql
    
    def test_lagInFrame_with_default(self):
        """Test lagInFrame function with default."""
        col = Column("x", Int64)
        func = lagInFrame(col, 1, 0)
        assert func.func_name == "lagInFrame"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "0" in sql
    
    def test_leadInFrame(self):
        """Test leadInFrame function."""
        col = Column("x", Int64)
        func = leadInFrame(col, 1)
        assert func.func_name == "leadInFrame"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "1" in sql
    
    def test_leadInFrame_with_default(self):
        """Test leadInFrame function with default."""
        col = Column("x", Int64)
        func = leadInFrame(col, 1, 0)
        assert func.func_name == "leadInFrame"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "0" in sql
    
    def test_firstValue(self):
        """Test firstValue function."""
        col = Column("x", Int64)
        func = firstValue(col)
        assert func.func_name == "firstValue"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_lastValue(self):
        """Test lastValue function."""
        col = Column("x", Int64)
        func = lastValue(col)
        assert func.func_name == "lastValue"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
    
    def test_nthValue(self):
        """Test nthValue function."""
        col = Column("x", Int64)
        func = nthValue(col, 3)
        assert func.func_name == "nthValue"
        sql = func.to_sql()
        assert func.func_name.lower() in sql.lower()
        assert "3" in sql
