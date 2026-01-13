"""
Integration tests for chpy library.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from chpy import ClickHouseClient, CryptoQuotesTable, crypto_quotes
from chpy.functions import avg, count, length, upper, toYear, toDateTime, divide
from chpy.query_builder import QueryBuilder


class TestIntegration:
    """Integration tests combining multiple components."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock(spec=ClickHouseClient)
        client.execute = Mock(return_value=[
            {"pair": "BTC-USDT", "best_bid_price": 50000.0, "exchange": "BINANCE"},
            {"pair": "ETH-USDT", "best_bid_price": 3000.0, "exchange": "BINANCE"},
        ])
        client.query_df = Mock()
        client.query_np = Mock()
        return client
    
    @pytest.fixture
    def table(self, mock_client):
        """CryptoQuotesTable instance."""
        return CryptoQuotesTable(mock_client)
    
    def test_full_query_chain(self, table, mock_client):
        """Test complete query chain from table to result."""
        result = (table.query()
            .select(crypto_quotes.pair, crypto_quotes.best_bid_price)
            .where(crypto_quotes.pair == "BTC-USDT")
            .where(crypto_quotes.exchange == "BINANCE")
            .limit(10)
            .to_list())
        
        assert len(result) == 2
        assert result[0]["pair"] == "BTC-USDT"
        mock_client.execute.assert_called_once()
    
    def test_query_with_aggregation(self, table, mock_client):
        """Test query with aggregation functions."""
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT", "avg_bid": 50000.0, "cnt": 100}
        ]
        
        result = (table.query()
            .select(
                crypto_quotes.pair,
                avg(crypto_quotes.best_bid_price).alias("avg_bid"),
                count().alias("cnt")
            )
            .where(crypto_quotes.exchange == "BINANCE")
            .group_by(crypto_quotes.pair)
            .order_by("avg_bid", desc=True)
            .limit(5)
            .to_list())
        
        assert len(result) == 1
        assert result[0]["pair"] == "BTC-USDT"
        assert result[0]["avg_bid"] == 50000.0
    
    def test_query_with_string_functions(self, table, mock_client):
        """Test query with string functions."""
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT", "pair_upper": "BTC-USDT", "pair_length": 8}
        ]
        
        result = (table.query()
            .select(
                crypto_quotes.pair,
                upper(crypto_quotes.pair).alias("pair_upper"),
                length(crypto_quotes.pair).alias("pair_length")
            )
            .where(crypto_quotes.pair == "BTC-USDT")
            .limit(1)
            .to_list())
        
        assert len(result) == 1
        assert result[0]["pair_upper"] == "BTC-USDT"
    
    def test_query_with_datetime_functions(self, table, mock_client):
        """Test query with datetime functions."""
        mock_client.execute.return_value = [
            {"timestamp_ms": 1704067200000, "year": 2024, "month": 1}
        ]
        
        result = (table.query()
            .select(
                crypto_quotes.timestamp_ms,
                toYear(toDateTime(divide(crypto_quotes.timestamp_ms, 1000))).alias("year"),
                toDateTime(divide(crypto_quotes.timestamp_ms, 1000)).alias("dt")
            )
            .where(crypto_quotes.pair == "BTC-USDT")
            .limit(1)
            .to_list())
        
        assert len(result) == 1
    
    def test_complex_where_conditions(self, table, mock_client):
        """Test complex WHERE conditions with AND/OR."""
        result = (table.query()
            .where(
                (crypto_quotes.pair == "BTC-USDT") &
                (crypto_quotes.exchange == "BINANCE")
            )
            .limit(10)
            .to_list())
        
        assert len(result) == 2
        # Verify SQL contains both conditions
        call_args = mock_client.execute.call_args[0][0]
        assert "pair = 'BTC-USDT'" in call_args
        assert "exchange = 'BINANCE'" in call_args
        assert "AND" in call_args
    
    def test_query_with_table_shortcut(self, table, mock_client):
        """Test query using table.c shortcut."""
        result = (table.query()
            .where(table.pair == "BTC-USDT")
            .where(table.best_bid_price > 50000)
            .limit(5)
            .to_list())
        
        assert len(result) == 2
        call_args = mock_client.execute.call_args[0][0]
        assert "pair = 'BTC-USDT'" in call_args
        assert "best_bid_price > 50000" in call_args
    
    def test_query_count(self, table, mock_client):
        """Test count query."""
        mock_client.execute.return_value = [{"count": 42}]
        
        count_result = (table.query()
            .where(crypto_quotes.pair == "BTC-USDT")
            .where(crypto_quotes.exchange == "BINANCE")
            .count())
        
        assert count_result == 42
    
    def test_query_first(self, table, mock_client):
        """Test first query."""
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT", "best_bid_price": 50000.0}
        ]
        
        first = (table.query()
            .where(crypto_quotes.pair == "BTC-USDT")
            .order_by(crypto_quotes.timestamp_ms, desc=True)
            .first())
        
        assert first is not None
        assert first["pair"] == "BTC-USDT"
    
    def test_query_exists(self, table, mock_client):
        """Test exists query."""
        mock_client.execute.return_value = [{"count": 1}]
        
        exists = (table.query()
            .where(crypto_quotes.pair == "BTC-USDT")
            .exists())
        
        assert exists is True
    
    def test_query_to_dict(self, table, mock_client):
        """Test to_dict output format."""
        result = (table.query()
            .select(crypto_quotes.pair, crypto_quotes.best_bid_price)
            .where(crypto_quotes.pair == "BTC-USDT")
            .limit(2)
            .to_dict(crypto_quotes.pair, crypto_quotes.best_bid_price))
        
        assert isinstance(result, dict)
        assert "BTC-USDT" in result
        assert result["BTC-USDT"] == 50000.0
    
    def test_query_iteration(self, table, mock_client):
        """Test query iteration."""
        results = []
        for row in table.query().where(crypto_quotes.pair == "BTC-USDT").limit(2):
            results.append(row)
        
        assert len(results) == 2
        assert results[0]["pair"] == "BTC-USDT"
    
    def test_multiple_aggregations(self, table, mock_client):
        """Test query with multiple aggregations."""
        mock_client.execute.return_value = [
            {
                "pair": "BTC-USDT",
                "min_bid": 49000.0,
                "max_bid": 51000.0,
                "avg_bid": 50000.0,
                "cnt": 100
            }
        ]
        
        from chpy.functions import min, max
        
        result = (table.query()
            .select(
                crypto_quotes.pair,
                min(crypto_quotes.best_bid_price).alias("min_bid"),
                max(crypto_quotes.best_bid_price).alias("max_bid"),
                avg(crypto_quotes.best_bid_price).alias("avg_bid"),
                count().alias("cnt")
            )
            .where(crypto_quotes.pair == "BTC-USDT")
            .group_by(crypto_quotes.pair)
            .to_list())
        
        assert len(result) == 1
        assert result[0]["min_bid"] == 49000.0
        assert result[0]["max_bid"] == 51000.0

