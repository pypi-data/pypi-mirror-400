"""
ClickHouse functions module - provides programmatic access to all ClickHouse functions.
"""

# Base classes
from chpy.functions.base import Function, AggregateFunction, WindowSpec

# Aggregate functions
from chpy.functions.aggregate import (
    count, sum, avg, min, max, any, anyHeavy, anyLast,
    groupArray, groupUniqArray, quantile, quantileExact, quantileTiming,
    stddevPop, stddevSamp, varPop, varSamp, covarPop, covarSamp, corr,
    argMin, argMax, topK, topKWeighted,
    groupBitAnd, groupBitOr, groupBitXor,
    groupArrayInsertAt, groupArrayMovingSum, groupArrayMovingAvg,
    uniq, uniqExact, uniqCombined, uniqHLL12, uniqTheta
)

# Arithmetic functions
from chpy.functions.arithmetic import (
    plus, minus, multiply, divide, intDiv, intDivOrZero, modulo, negate, abs, gcd, lcm
)

# Comparison functions
from chpy.functions.comparison import (
    equals, notEquals, less, greater, lessOrEquals, greaterOrEquals
)

# Logical functions
from chpy.functions.logical import (
    and_, or_, not_, xor
)

# String functions
from chpy.functions.string import (
    length, empty, notEmpty, lengthUTF8, lower, upper, lowerUTF8, upperUTF8,
    reverse, reverseUTF8, concat, concatAssumeInjective, substring, substringUTF8,
    appendTrailingCharIfAbsent, left, right, trimLeft, trimRight, trimBoth,
    format, formatReadableQuantity, formatReadableSize, formatReadableTimeDelta,
    splitByChar, splitByString, arrayStringConcat, alphaTokens,
    extractAll, extractAllGroups, extractGroups,
    like, notLike, match, multiMatchAny, multiMatchAnyIndex, multiFuzzyMatchAny,
    replace, replaceAll, replaceOne, replaceRegexpOne, replaceRegexpAll,
    position, positionUTF8, positionCaseInsensitive, positionCaseInsensitiveUTF8,
    startsWith, endsWith, base64Encode, base64Decode, tryBase64Decode,
    hex, unhex, UUIDStringToNum, UUIDNumToString, bitmaskToList, bitmaskToArray
)

# Date and time functions
from chpy.functions.date_time import (
    now, today, yesterday, timeSlot,
    toYear, toQuarter, toMonth, toWeek, toDayOfYear, toDayOfMonth, toDayOfWeek,
    toHour, toMinute, toSecond,
    toStartOfYear, toStartOfQuarter, toStartOfMonth, toStartOfWeek, toStartOfDay,
    toStartOfHour, toStartOfMinute, toStartOfSecond,
    toStartOfFiveMinute, toStartOfTenMinute, toStartOfFifteenMinute,
    toTime, toRelativeYearNum, toRelativeQuarterNum, toRelativeMonthNum,
    toRelativeWeekNum, toRelativeDayNum, toRelativeHourNum, toRelativeMinuteNum, toRelativeSecondNum,
    toISOYear, toISOWeek, toISOYearWeek, toMonday,
    toYYYYMM, toYYYYMMDD, toYYYYMMDDhhmmss,
    addYears, addQuarters, addMonths, addWeeks, addDays, addHours, addMinutes, addSeconds,
    subtractYears, subtractQuarters, subtractMonths, subtractWeeks, subtractDays,
    subtractHours, subtractMinutes, subtractSeconds,
    dateDiff, dateName, timeZone, timeZoneOf, toTimeZone, formatDateTime, parseDateTimeBestEffort
)

# Array functions
from chpy.functions.array import (
    array, arrayConcat, arrayElement, has, hasAll, hasAny, indexOf, countEqual,
    arrayEnumerate, arrayEnumerateDense, arrayEnumerateUniq,
    arrayPopBack, arrayPopFront, arrayPushBack, arrayPushFront, arrayResize, arraySlice,
    arraySort, arrayReverseSort, arrayUniq, arrayJoin,
    arrayMap, arrayFilter, arrayCount, arrayExists, arrayAll,
    arraySum, arrayAvg, arrayCumSum, arrayProduct, arrayReduce,
    arrayReverse, arrayFlatten, arrayZip, arrayAUC, arrayDifference, arrayDistinct,
    arrayIntersect, arrayReduceInRanges, arraySlice, arraySplit,
    arrayStringConcat, arrayMin, arrayMax
)

# Mathematical functions
from chpy.functions.math import (
    e, pi, exp, log, log2, log10, sqrt, cbrt, pow, power, exp2, exp10, log1p,
    sign, sin, cos, tan, asin, acos, atan, atan2,
    sinh, cosh, tanh, asinh, acosh, atanh,
    hypot, logGamma, tgamma, lgamma, erf, erfc, erfInv, erfcInv
)

# Rounding functions
from chpy.functions.rounding import (
    round, roundBankers, floor, ceil, trunc, roundToExp2, roundDuration, roundAge, roundDown
)

# Bitwise functions
from chpy.functions.bitwise import (
    bitAnd, bitOr, bitXor, bitNot, bitShiftLeft, bitShiftRight,
    bitRotateLeft, bitRotateRight, bitTest, bitTestAll, bitTestAny, bitCount
)

# Type conversion functions
from chpy.functions.type_conversion import (
    toInt8, toInt16, toInt32, toInt64, toUInt8, toUInt16, toUInt32, toUInt64,
    toFloat32, toFloat64, toDate, toDateTime, toDateTime64, toString, toFixedString,
    toDecimal32, toDecimal64, toDecimal128, toDecimal256,
    toUUID, toIPv4, toIPv6, parseDateTimeBestEffort, parseDateTimeBestEffortUS,
    parseDateTime32BestEffort, CAST
)

# Conditional functions
from chpy.functions.conditional import (
    if_, multiIf, ifNull, nullIf, coalesce
)

# Hash functions
from chpy.functions.hash import (
    halfMD5, MD5, SHA1, SHA224, SHA256, SHA512,
    cityHash64, farmHash64, metroHash64, sipHash64, sipHash128,
    xxHash32, xxHash64, murmurHash2_32, murmurHash2_64,
    murmurHash3_32, murmurHash3_64, murmurHash3_128, gccMurmurHash
)

# URL functions
from chpy.functions.url import (
    protocol, domain, domainWithoutWWW, topLevelDomain, firstSignificantSubdomain,
    cutToFirstSignificantSubdomain, path, pathFull, queryString, fragment,
    queryStringAndFragment, extractURLParameter, extractURLParameters,
    extractURLParameterNames, cutURLParameter, cutWWW, cutQueryString,
    cutFragment, cutQueryStringAndFragment, decodeURLComponent, encodeURLComponent
)

# JSON functions
from chpy.functions.json import (
    JSONHas, JSONLength, JSONKey, JSONKeys, JSONExtract, JSONExtractString,
    JSONExtractInt, JSONExtractFloat, JSONExtractBool, JSONExtractRaw,
    JSONExtractArrayRaw, JSONExtractKeysAndValues, JSONExtractKeysAndValuesRaw,
    JSONExtractUInt
)

# Geo functions
from chpy.functions.geo import (
    greatCircleDistance, geoDistance, pointInPolygon,
    geohashEncode, geohashDecode, geohashesInBox
)

# Nullable functions
from chpy.functions.nullable import (
    isNull, isNotNull, coalesce, ifNull, nullIf, assumeNotNull
)

# Tuple functions
from chpy.functions.tuple import (
    tuple, tupleElement, untuple
)

# Map functions
from chpy.functions.map import (
    map, mapKeys, mapValues, mapContains, mapGet
)

# Window functions
from chpy.functions.window import (
    rowNumber, rank, denseRank, percentRank, cumeDist, ntile,
    lagInFrame, leadInFrame, firstValue, lastValue, nthValue
)

# Encoding functions
from chpy.functions.encoding import (
    hex, unhex, base64Encode, base64Decode, tryBase64Decode,
    base32Encode, base32Decode, base58Encode, base58Decode
)

# UUID functions
from chpy.functions.uuid import (
    generateUUIDv4, toUUID, UUIDStringToNum, UUIDNumToString
)

# IP address functions
from chpy.functions.ip import (
    toIPv4, toIPv6, IPv4NumToString, IPv4StringToNum,
    IPv6NumToString, IPv6StringToNum, IPv4CIDRToRange, IPv6CIDRToRange,
    IPv4ToIPv6, cutIPv6
)

# Other functions
from chpy.functions.other import (
    hostName, getMacro, FQDN, basename, visibleWidth, toTypeName,
    blockSize, blockNumber, rowNumberInBlock, rowNumberInAllBlocks,
    neighbor, runningAccumulate, runningDifference, runningDifferenceStartingWithFirstValue,
    finalizeAggregation
)

# Export all functions - using * import for convenience
# Users can import specific functions or use chpy.functions.*
__all__ = [
    # Base classes
    'Function', 'AggregateFunction',
    # All aggregate functions
    'count', 'sum', 'avg', 'min', 'max', 'any', 'anyHeavy', 'anyLast',
    'groupArray', 'groupUniqArray', 'quantile', 'quantileExact', 'quantileTiming',
    'stddevPop', 'stddevSamp', 'varPop', 'varSamp', 'covarPop', 'covarSamp', 'corr',
    'argMin', 'argMax', 'topK', 'topKWeighted',
    'groupBitAnd', 'groupBitOr', 'groupBitXor',
    'groupArrayInsertAt', 'groupArrayMovingSum', 'groupArrayMovingAvg',
    'uniq', 'uniqExact', 'uniqCombined', 'uniqHLL12', 'uniqTheta',
    # All other functions are exported via * imports above
]

