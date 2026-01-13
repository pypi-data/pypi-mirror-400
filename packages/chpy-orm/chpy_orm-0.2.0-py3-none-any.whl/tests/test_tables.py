"""
Tests for chpy.tables module.
"""

import pytest
from unittest.mock import Mock
from chpy.tables import CryptoQuotesTable, TableWrapper, Table
from chpy.client import ClickHouseClient
from chpy.orm import Column, Row
from chpy.tables import crypto_quotes
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestCryptoQuotesTable:
    """Test cases for CryptoQuotesTable class."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock(spec=ClickHouseClient)
        client.host = "localhost"
        client.port = 8123
        client.username = "default"
        client.password = ""
        client.database = "stockhouse"
        return client
    
    @pytest.fixture
    def table(self, mock_client):
        """CryptoQuotesTable instance."""
        return CryptoQuotesTable(mock_client)
    
    def test_init_default_database(self, mock_client):
        """Test initialization with default database."""
        table = CryptoQuotesTable(mock_client)
        assert table.client == mock_client
        assert table.database == "stockhouse"
        assert table.table_name == "stockhouse.crypto_quotes"
    
    def test_init_custom_database(self, mock_client):
        """Test initialization with custom database."""
        table = CryptoQuotesTable(mock_client, database="custom_db")
        assert table.database == "custom_db"
        assert table.table_name == "custom_db.crypto_quotes"
    
    def test_column_shortcuts(self, table):
        """Test column access shortcuts."""
        # Direct column access (Django-style)
        assert table.pair.name == "pair"
        assert table.best_bid_price.name == "best_bid_price"
        # Verify columns are accessible
        assert table.pair == crypto_quotes.pair
        assert table.best_bid_price == crypto_quotes.best_bid_price
    
    def test_escape_string(self, table):
        """Test string escaping."""
        result = table._escape_string("O'Brien")
        assert result == "O''Brien"
        
        result = table._escape_string("normal_string")
        assert result == "normal_string"
    
    def test_insert(self, table, mock_client):
        """Test insert method."""
        data = [
            {"pair": "BTC-USDT", "best_bid_price": 50000.0},
            {"pair": "ETH-USDT", "best_bid_price": 3000.0},
        ]
        
        table.insert(data)
        
        mock_client.insert.assert_called_once_with("stockhouse.crypto_quotes", data)
    
    def test_query(self, table):
        """Test query method returns QueryBuilder."""
        from chpy.query_builder import QueryBuilder
        
        builder = table.query()
        
        assert isinstance(builder, QueryBuilder)
        assert builder.table_name == "stockhouse.crypto_quotes"
    
    def test_get_valid_exchanges(self, table):
        """Test get_valid_exchanges method."""
        from chpy.config import EXCHANGES
        
        exchanges = table.get_valid_exchanges()
        
        assert isinstance(exchanges, list)
        assert len(exchanges) > 0
        assert exchanges == EXCHANGES.copy()
    
    def test_get_exchange_base_currencies(self, table):
        """Test get_exchange_base_currencies method."""
        currencies = table.get_exchange_base_currencies("BINANCE")
        
        assert isinstance(currencies, list)
        assert "USDT" in currencies
        
        # Test case-insensitive
        currencies2 = table.get_exchange_base_currencies("binance")
        assert currencies == currencies2
    
    def test_get_exchange_base_currencies_invalid(self, table):
        """Test get_exchange_base_currencies with invalid exchange."""
        currencies = table.get_exchange_base_currencies("INVALID")
        assert currencies == []
    
    def test_get_exchange_currencies(self, table):
        """Test get_exchange_currencies method."""
        currencies = table.get_exchange_currencies("BINANCE")
        
        assert isinstance(currencies, list)
        assert len(currencies) > 0
        assert "BTC" in currencies
        assert "ETH" in currencies
        
        # Test case-insensitive
        currencies2 = table.get_exchange_currencies("binance")
        assert currencies == currencies2
    
    def test_get_exchange_currencies_invalid(self, table):
        """Test get_exchange_currencies with invalid exchange."""
        currencies = table.get_exchange_currencies("INVALID")
        assert currencies == []
    
    def test_get_exchange_pairs(self, table):
        """Test get_exchange_pairs method."""
        pairs = table.get_exchange_pairs("BINANCE")
        
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        assert "BTC-USDT" in pairs
        assert "ETH-USDT" in pairs
        
        # Test case-insensitive
        pairs2 = table.get_exchange_pairs("binance")
        assert pairs == pairs2
    
    def test_get_exchange_pairs_invalid(self, table):
        """Test get_exchange_pairs with invalid exchange."""
        pairs = table.get_exchange_pairs("INVALID")
        assert pairs == []
    
    def test_is_valid_pair(self, table):
        """Test is_valid_pair method."""
        assert table.is_valid_pair("BTC-USDT") is True
        assert table.is_valid_pair("ETH-USDT") is True
        assert table.is_valid_pair("INVALID-PAIR") is False
        assert table.is_valid_pair("not-a-pair") is False
    
    def test_is_valid_pair_with_exchange(self, table):
        """Test is_valid_pair with specific exchange."""
        assert table.is_valid_pair("BTC-USDT", "BINANCE") is True
        assert table.is_valid_pair("BTC-USDT", "KUCOIN") is True
        assert table.is_valid_pair("BTC-IRT", "BINANCE") is False  # BINANCE doesn't support IRT
    
    def test_is_valid_pair_case_insensitive(self, table):
        """Test is_valid_pair is case-insensitive for exchange."""
        assert table.is_valid_pair("BTC-USDT", "binance") is True
        assert table.is_valid_pair("BTC-USDT", "BINANCE") is True
    
    def test_get_all_valid_pairs(self, table):
        """Test get_all_valid_pairs method."""
        pairs = table.get_all_valid_pairs()
        
        assert isinstance(pairs, list)
        assert len(pairs) > 0
        assert "BTC-USDT" in pairs
        assert "ETH-USDT" in pairs
        # Should be sorted
        assert pairs == sorted(pairs)


class TestTableWrapper:
    """Test cases for generic TableWrapper class."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock(spec=ClickHouseClient)
        client.host = "localhost"
        client.port = 8123
        client.username = "default"
        client.password = ""
        client.database = "test_db"
        return client
    
    def test_init_with_django_style_columns(self, mock_client):
        """Test initialization with Django-style column definitions."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
            value = Column("value", Float64)
        
        table = MyTable(mock_client, "my_table", "test_db")
        assert table.client == mock_client
        assert table.database == "test_db"
        assert table.table_name == "test_db.my_table"
        assert table.schema == table  # Table is its own schema
        # Direct column access (Django-style)
        assert table.id.name == "id"
        assert table.name.name == "name"
        assert table.value.name == "value"
    
    def test_init_with_explicit_columns(self, mock_client):
        """Test initialization with explicit columns parameter."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
            Column("value", Float64),
        ]
        
        table = TableWrapper(mock_client, "my_table", "test_db", columns=columns)
        assert table.client == mock_client
        assert table.database == "test_db"
        assert table.table_name == "test_db.my_table"
        assert table.schema == table  # Table is its own schema
        # Direct column access
        assert table.id.name == "id"
        assert table.name.name == "name"
        assert table.value.name == "value"
    
    def test_escape_string(self, mock_client):
        """Test string escaping."""
        class MyTable(Table):
            id = Column("id", UInt64)
        
        table = MyTable(mock_client, "my_table", "test_db")
        result = table._escape_string("O'Brien")
        assert result == "O''Brien"
        
        result = table._escape_string("normal_string")
        assert result == "normal_string"
    
    def test_insert(self, mock_client):
        """Test insert method."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
            value = Column("value", Float64)
        
        table = MyTable(mock_client, "my_table", "test_db")
        data = [
            {"id": 1, "name": "test1", "value": 1.5},
            {"id": 2, "name": "test2", "value": 2.5},
        ]
        
        table.insert(data)
        
        mock_client.insert.assert_called_once_with("test_db.my_table", data)
    
    def test_query(self, mock_client):
        """Test query method returns QueryBuilder."""
        from chpy.query_builder import QueryBuilder
        
        class MyTable(Table):
            id = Column("id", UInt64)
        
        table = MyTable(mock_client, "my_table", "test_db")
        builder = table.query()
        
        assert isinstance(builder, QueryBuilder)
        assert builder.table_name == "test_db.my_table"
    
    def test_query_with_django_style_columns(self, mock_client):
        """Test query with Django-style column definitions."""
        from chpy.query_builder import QueryBuilder
        
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
        
        table = MyTable(mock_client, "my_table", "test_db")
        builder = table.query()
        assert isinstance(builder, QueryBuilder)
        
        # Can use table columns directly in queries
        query = builder.where(table.id > 100)._build_query()
        assert "id > 100" in query
    
    def test_query_with_raw_strings(self, mock_client):
        """Test query with raw SQL strings."""
        class MyTable(Table):
            id = Column("id", UInt64)
        
        table = MyTable(mock_client, "my_table", "test_db")
        builder = table.query()
        
        # Can still use raw SQL strings
        query = builder.where("id > 100")._build_query()
        assert "id > 100" in query
    
    def test_crypto_quotes_inherits_from_table_wrapper(self, mock_client):
        """Test that CryptoQuotesTable inherits from TableWrapper."""
        crypto_table = CryptoQuotesTable(mock_client)
        
        assert isinstance(crypto_table, TableWrapper)
        assert crypto_table.table_name == "stockhouse.crypto_quotes"
        assert crypto_table.schema is not None
        # With Django-style columns, columns are directly accessible (no need for .c)
        assert crypto_table.pair is not None
        assert crypto_table.best_bid_price is not None
    
    def test_multiple_table_wrappers(self, mock_client):
        """Test creating multiple table wrappers for different tables."""
        class Table1(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
        
        class Table2(Table):
            user_id = Column("user_id", UInt64)
            email = Column("email", String)
        
        table1 = Table1(mock_client, "table1", "test_db")
        table2 = Table2(mock_client, "table2", "test_db")
        
        assert table1.table_name == "test_db.table1"
        assert table2.table_name == "test_db.table2"
        assert table1.id.name == "id"
        assert table2.user_id.name == "user_id"
        assert table1 != table2
    
    def test_table_wrapper_with_different_databases(self, mock_client):
        """Test table wrappers with different databases."""
        class MyTable(Table):
            id = Column("id", UInt64)
        
        table1 = MyTable(mock_client, "my_table", "db1")
        table2 = MyTable(mock_client, "my_table", "db2")
        
        assert table1.table_name == "db1.my_table"
        assert table2.table_name == "db2.my_table"
        assert table1.database == "db1"
        assert table2.database == "db2"
    
    def test_query_returns_row_objects_with_schema(self, mock_client):
        """Test that query returns Row objects when schema is available."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
            value = Column("value", Float64)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1", "value": 1.5},
            {"id": 2, "name": "test2", "value": 2.5},
        ]
        
        table = MyTable(mock_client, "my_table", "test_db")
        results = table.query().to_list()
        
        # Should return Row objects
        assert len(results) == 2
        assert isinstance(results[0], Row)
        assert isinstance(results[1], Row)
        
        # Test attribute access
        assert results[0].id == 1
        assert results[0].name == "test1"
        assert results[0].value == 1.5
    
    def test_iteration_returns_row_objects_with_schema(self, mock_client):
        """Test that iteration over query returns Row objects when schema is available."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]
        
        table = MyTable(mock_client, "my_table", "test_db")
        
        rows = list(table.query())
        
        assert len(rows) == 2
        assert all(isinstance(row, Row) for row in rows)
        assert rows[0].id == 1
        assert rows[1].id == 2
        assert rows[0].name == "test1"
    
    def test_iteration_returns_row_objects(self, mock_client):
        """Test that iteration returns Row objects when table has columns."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1"},
        ]
        
        table = MyTable(mock_client, "my_table", "test_db")
        
        rows = list(table.query())
        
        assert len(rows) == 1
        assert isinstance(rows[0], Row)
        assert rows[0].id == 1
    
    def test_first_returns_row_object_with_schema(self, mock_client):
        """Test that first() returns Row object when schema is available."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1"},
        ]
        
        table = MyTable(mock_client, "my_table", "test_db")
        result = table.query().first()
        
        assert isinstance(result, Row)
        assert result.id == 1
        assert result.name == "test1"
    
    def test_crypto_quotes_returns_row_objects(self, mock_client):
        """Test that CryptoQuotesTable returns Row objects (has schema)."""
        from chpy.tables import CryptoQuotesTable
        
        mock_client.execute.return_value = [
            {
                "pair": "BTC-USDT",
                "best_bid_price": 50000.0,
                "best_ask_price": 50001.0,
            },
        ]
        
        table = CryptoQuotesTable(mock_client)
        results = table.query().to_list()
        
        # CryptoQuotesTable has a schema, so should return Row objects
        assert len(results) == 1
        assert isinstance(results[0], Row)
        
        # Test attribute access
        assert results[0].pair == "BTC-USDT"
        assert results[0].best_bid_price == 50000.0
        assert results[0].best_ask_price == 50001.0
        
        # Dictionary access also works
        assert results[0]["pair"] == "BTC-USDT"
    
    def test_row_object_programmatic_iteration(self, mock_client):
        """Test programmatic iteration over Row objects."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
            value = Column("value", Float64)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1", "value": 1.5},
            {"id": 2, "name": "test2", "value": 2.5},
            {"id": 3, "name": "test3", "value": 3.5},
        ]
        
        table = MyTable(mock_client, "my_table", "test_db")
        
        # Test iteration
        ids = []
        names = []
        for row in table.query():
            assert isinstance(row, Row)
            ids.append(row.id)
            names.append(row.name)
        
        assert ids == [1, 2, 3]
        assert names == ["test1", "test2", "test3"]
        
        # Test list comprehension
        values = [row.value for row in table.query()]
        assert values == [1.5, 2.5, 3.5]
        
        # Test filtering
        filtered = [row for row in table.query() if row.value > 2.0]
        assert len(filtered) == 2
        assert all(row.value > 2.0 for row in filtered)
    
    def test_row_object_to_dict_conversion(self, mock_client):
        """Test converting Row objects to dictionaries."""
        class MyTable(Table):
            id = Column("id", UInt64)
            name = Column("name", String)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1"},
        ]
        
        table = MyTable(mock_client, "my_table", "test_db")
        row = table.query().first()
        
        # Convert to dict
        row_dict = row.to_dict()
        
        assert isinstance(row_dict, dict)
        assert row_dict == {"id": 1, "name": "test1"}
        assert row_dict is not row._data  # Should be a copy

