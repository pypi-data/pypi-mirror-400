"""
Table schema definitions based on ClickHouse table structure.
Auto-generated from ClickHouse MCP schema.
"""

from chpy.orm import Table, Column
from chpy.types import String, Float64, UInt64, Array, LowCardinality

# Define crypto_quotes table columns based on ClickHouse schema
crypto_quotes_columns = [
    Column("pair", String),
    Column("best_bid_price", Float64),
    Column("best_bid_size", Float64),
    Column("best_ask_price", Float64),
    Column("best_ask_size", Float64),
    Column("bid_prices", Array(Float64)),
    Column("bid_sizes", Array(Float64)),
    Column("ask_prices", Array(Float64)),
    Column("ask_sizes", Array(Float64)),
    Column("timestamp_ms", UInt64),
    Column("exchange", LowCardinality(String)),
    Column("sequence_number", UInt64),
    Column("inserted_at", UInt64),
]

# Create table instance
crypto_quotes = Table("crypto_quotes", "stockhouse", crypto_quotes_columns)

