"""
Integration tests for window functions in query builder.
"""

import pytest
from unittest.mock import Mock
from chpy.query_builder import QueryBuilder
from chpy.functions.base import WindowSpec
from chpy.functions.window import rowNumber, rank
from chpy.functions.aggregate import avg, sum as sum_func, count
from chpy.orm import Column
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestWindowFunctionsInQueryBuilder:
    """Test cases for using window functions in query builder."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[])
        return client
    
    @pytest.fixture
    def escape_func(self):
        """String escape function."""
        def escape(s: str) -> str:
            return s.replace("'", "''")
        return escape
    
    @pytest.fixture
    def builder(self, mock_client, escape_func):
        """QueryBuilder instance."""
        return QueryBuilder("test_db.test_table", mock_client, escape_func)
    
    def test_window_function_in_select(self, builder):
        """Test window function in SELECT clause."""
        col1 = Column("pair", String)
        col2 = Column("timestamp_ms", UInt64)
        
        spec = WindowSpec().partition_by(col1).order_by(col2)
        builder.select(
            col1,
            rowNumber().over(spec).alias("row_num")
        )
        
        query = builder._build_query()
        assert "SELECT pair" in query
        assert "row_number()" in query
        assert "PARTITION BY pair" in query
        assert "ORDER BY timestamp_ms ASC" in query
        assert "as row_num" in query
    
    def test_aggregate_with_over_in_select(self, builder):
        """Test aggregate function with OVER in SELECT."""
        col1 = Column("price", Float64)
        col2 = Column("exchange", String)
        
        spec = WindowSpec().partition_by(col2)
        builder.select(
            col2,
            avg(col1).over(spec).alias("avg_price")
        )
        
        query = builder._build_query()
        assert "SELECT exchange" in query
        assert "AVG(price)" in query
        assert "PARTITION BY exchange" in query
        assert "as avg_price" in query
    
    def test_multiple_window_functions(self, builder):
        """Test multiple window functions in same query."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        col3 = Column("exchange", String)
        col4 = Column("timestamp_ms", UInt64)
        
        spec1 = WindowSpec().partition_by(col2)
        spec2 = WindowSpec().partition_by(col3).order_by(col4)
        
        builder.select(
            col2,
            col3,
            avg(col1).over(spec1).alias("avg_by_pair"),
            sum_func(col1).over(spec2).alias("sum_by_exchange")
        )
        
        query = builder._build_query()
        assert "AVG(price)" in query
        assert "SUM(price)" in query
        assert "PARTITION BY pair" in query
        assert "PARTITION BY exchange" in query
        assert "ORDER BY timestamp_ms ASC" in query
    
    def test_window_function_with_where(self, builder):
        """Test window function with WHERE clause."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        col3 = Column("exchange", String)
        
        spec = WindowSpec().partition_by(col2)
        builder.select(
            col2,
            avg(col1).over(spec).alias("avg_price")
        ).where(col3 == "BINANCE")
        
        query = builder._build_query()
        assert "AVG(price)" in query
        assert "PARTITION BY pair" in query
        assert "WHERE" in query
        assert "exchange = 'BINANCE'" in query
    
    def test_window_function_with_group_by(self, builder):
        """Test window function with GROUP BY (window functions can be used with aggregates)."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        col3 = Column("exchange", String)
        
        spec = WindowSpec().partition_by(col3)
        builder.select(
            col2,
            col3,
            avg(col1).over(spec).alias("window_avg"),
            avg(col1).alias("group_avg")
        ).group_by(col2, col3)
        
        query = builder._build_query()
        assert "AVG(price)" in query
        assert "PARTITION BY exchange" in query
        assert "GROUP BY pair, exchange" in query
    
    def test_complex_window_spec_in_query(self, builder):
        """Test complex window specification in query."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        col3 = Column("timestamp_ms", UInt64)
        
        spec = (WindowSpec()
            .partition_by(col2)
            .order_by(col3)
            .rows_between("UNBOUNDED PRECEDING", "CURRENT ROW"))
        
        builder.select(
            col2,
            col3,
            avg(col1).over(spec).alias("running_avg")
        )
        
        query = builder._build_query()
        assert "AVG(price)" in query
        assert "PARTITION BY pair" in query
        assert "ORDER BY timestamp_ms ASC" in query
        assert "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in query
        assert "as running_avg" in query
    
    def test_rank_with_over_in_query(self, builder):
        """Test rank() with OVER in query."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        
        spec = WindowSpec().partition_by(col2).order_by(col1, desc=True)
        builder.select(
            col2,
            col1,
            rank().over(spec).alias("price_rank")
        )
        
        query = builder._build_query()
        assert "rank()" in query
        assert "PARTITION BY pair" in query
        assert "ORDER BY price DESC" in query
        assert "as price_rank" in query
    
    def test_inline_window_spec(self, builder):
        """Test creating window spec inline in query."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        
        # Create window spec inline
        builder.select(
            col2,
            avg(col1).over(
                WindowSpec().partition_by(col2)
            ).alias("avg_price")
        )
        
        query = builder._build_query()
        assert "AVG(price)" in query
        assert "PARTITION BY pair" in query
        assert "as avg_price" in query

