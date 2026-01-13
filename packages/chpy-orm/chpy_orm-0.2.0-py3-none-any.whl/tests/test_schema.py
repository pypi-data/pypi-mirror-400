"""
Tests for crypto_quotes schema (now exported from chpy.tables).
"""

import pytest
from chpy.tables import crypto_quotes, crypto_quotes_columns
from chpy.orm import Column, Table


class TestSchema:
    """Test cases for schema module."""
    
    def test_crypto_quotes_columns(self):
        """Test crypto_quotes_columns definition."""
        assert isinstance(crypto_quotes_columns, list)
        assert len(crypto_quotes_columns) > 0
        
        # Check that all items are Column objects
        for col in crypto_quotes_columns:
            assert isinstance(col, Column)
    
    def test_crypto_quotes_table(self):
        """Test crypto_quotes table instance."""
        assert isinstance(crypto_quotes, Table)
        # crypto_quotes is a Table wrapper instance
        # The wrapper's table_name property returns the full qualified name
        assert crypto_quotes.table_name == "stockhouse.crypto_quotes"
        assert crypto_quotes.database == "stockhouse"
        # The schema is self (Table wrapper), so it has the same properties
        # Access base Table properties via the schema's base class attributes
        assert crypto_quotes.schema._table_name == "crypto_quotes"
        assert crypto_quotes.schema._db_name == "stockhouse"
        assert crypto_quotes.schema._qualified_name == "stockhouse.crypto_quotes"
    
    def test_crypto_quotes_columns_exist(self):
        """Test that expected columns exist in crypto_quotes table."""
        expected_columns = [
            "pair", "best_bid_price", "best_bid_size", "best_ask_price",
            "best_ask_size", "bid_prices", "bid_sizes", "ask_prices",
            "ask_sizes", "timestamp_ms", "exchange", "sequence_number",
            "inserted_at"
        ]
        
        for col_name in expected_columns:
            col = crypto_quotes.get_column(col_name)
            assert col is not None, f"Column {col_name} not found"
            assert col.name == col_name
    
    def test_crypto_quotes_column_access(self):
        """Test column access via attributes."""
        assert crypto_quotes.pair.name == "pair"
        assert crypto_quotes.best_bid_price.name == "best_bid_price"
        assert crypto_quotes.exchange.name == "exchange"
        assert crypto_quotes.timestamp_ms.name == "timestamp_ms"
    
    def test_crypto_quotes_column_types(self):
        """Test column types."""
        assert crypto_quotes.pair.type == "String"
        assert crypto_quotes.best_bid_price.type == "Float64"
        assert crypto_quotes.timestamp_ms.type == "UInt64"
        assert crypto_quotes.exchange.type == "LowCardinality(String)"
    
    def test_crypto_quotes_column_table_reference(self):
        """Test that columns reference the table."""
        assert crypto_quotes.pair.table == crypto_quotes
        assert crypto_quotes.best_bid_price.table == crypto_quotes
    
    def test_crypto_quotes_get_all_columns(self):
        """Test get_all_columns method."""
        all_cols = crypto_quotes.get_all_columns()
        assert len(all_cols) == len(crypto_quotes_columns)
        assert all(isinstance(col, Column) for col in all_cols)
    
    def test_crypto_quotes_bracket_access(self):
        """Test bracket notation for column access."""
        assert crypto_quotes["pair"].name == "pair"
        assert crypto_quotes["best_bid_price"].name == "best_bid_price"
        
        with pytest.raises(AttributeError):
            _ = crypto_quotes["nonexistent"]

