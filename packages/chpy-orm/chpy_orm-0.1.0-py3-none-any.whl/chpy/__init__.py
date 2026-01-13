"""
chpy - A Python wrapper for ClickHouse database operations.
"""

from chpy.client import ClickHouseClient
from chpy.tables import CryptoQuotesTable, TableWrapper
from chpy.query_builder import QueryBuilder
from chpy.schema import crypto_quotes
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
    "EXCHANGES",
    "EXCHANGE_BASE_CURRENCIES",
    "EXCHANGE_CURRENCIES",
    "get_exchange_pairs",
    "is_valid_pair",
    "get_all_pairs",
    # All functions are available via chpy.functions or direct import
]

