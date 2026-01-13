"""
chpy - A Python wrapper for ClickHouse database operations.
"""

from chpy.client import ClickHouseClient
from chpy.tables import CryptoQuotesTable, TableWrapper, crypto_quotes, crypto_quotes_columns
from chpy.query_builder import QueryBuilder
from chpy.ddl import DDL
from chpy.types import (
    TypeBuilder,
    LowCardinality,
    Nullable,
    Array,
    Tuple,
    Map,
    Nested,
    FixedString,
    Enum,
    IPv4,
    IPv6,
    UUID,
    Date,
    DateTime,
    DateTime64,
    LowCardinalityNullable,
    NullableArray,
    ArrayNullable,
    # Primitive types
    String,
    Bool,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    UInt128,
    UInt256,
    Int8,
    Int16,
    Int32,
    Int64,
    Int128,
    Int256,
    Float32,
    Float64,
    Decimal32,
    Decimal64,
    Decimal128,
    Decimal256,
)
from chpy.config import (
    EXCHANGES,
    EXCHANGE_BASE_CURRENCIES,
    EXCHANGE_CURRENCIES,
    get_exchange_pairs,
    is_valid_pair,
    get_all_pairs,
)

# Import all functions from functions module
from chpy.functions import *

__version__ = "0.1.0"
__all__ = [
    "ClickHouseClient",
    "CryptoQuotesTable",
    "TableWrapper",  # Generic table wrapper
    "QueryBuilder",
    "DDL",  # DDL operations for table management
    "crypto_quotes",  # Schema table for column access
    # Type builders
    "TypeBuilder",
    "LowCardinality",
    "Nullable",
    "Array",
    "Tuple",
    "Map",
    "Nested",
    "FixedString",
    "Enum",
    "IPv4",
    "IPv6",
    "UUID",
    "Date",
    "DateTime",
    "DateTime64",
    "LowCardinalityNullable",
    "NullableArray",
    "ArrayNullable",
    # Primitive types
    "String",
    "Bool",
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "UInt128",
    "UInt256",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "Int128",
    "Int256",
    "Float32",
    "Float64",
    "Decimal32",
    "Decimal64",
    "Decimal128",
    "Decimal256",
    "EXCHANGES",
    "EXCHANGE_BASE_CURRENCIES",
    "EXCHANGE_CURRENCIES",
    "get_exchange_pairs",
    "is_valid_pair",
    "get_all_pairs",
    # All functions are available via chpy.functions or direct import
]

