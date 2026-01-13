"""
Pytest configuration and fixtures for chpy tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from chpy.client import ClickHouseClient
from chpy.orm import Column, Table
from chpy.tables import CryptoQuotesTable, crypto_quotes
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


@pytest.fixture
def mock_clickhouse_client():
    """Mock ClickHouse client for testing."""
    client = Mock(spec=ClickHouseClient)
    client.host = "localhost"
    client.port = 8123
    client.username = "default"
    client.password = ""
    client.database = "test_db"
    client._client = Mock()
    return client


@pytest.fixture
def mock_query_result():
    """Mock query result data."""
    return [
        {"pair": "BTC-USDT", "best_bid_price": 50000.0, "exchange": "BINANCE"},
        {"pair": "ETH-USDT", "best_bid_price": 3000.0, "exchange": "BINANCE"},
        {"pair": "BTC-USDT", "best_bid_price": 50100.0, "exchange": "KUCOIN"},
    ]


@pytest.fixture
def sample_column():
    """Sample Column object for testing."""
    return Column("test_column", String)


@pytest.fixture
def sample_table():
    """Sample Table object for testing."""
    columns = [
        Column("id", UInt64),
        Column("name", String),
        Column("value", Float64),
    ]
    return Table("test_table", "test_db", columns)


@pytest.fixture
def crypto_quotes_table(mock_clickhouse_client):
    """CryptoQuotesTable instance for testing."""
    return CryptoQuotesTable(mock_clickhouse_client)


@pytest.fixture
def escape_string_func():
    """Simple string escaping function."""
    def escape(s: str) -> str:
        return s.replace("'", "''")
    return escape

