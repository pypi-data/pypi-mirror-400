"""
Tests for window functions with OVER clause support.
"""

import pytest
from chpy.functions.base import Function, AggregateFunction, WindowSpec
from chpy.functions.window import rowNumber, rank, denseRank
from chpy.functions.aggregate import avg, sum as sum_func, count
from chpy.orm import Column
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestWindowSpec:
    """Test cases for WindowSpec class."""
    
    def test_empty_window_spec(self):
        """Test empty window specification."""
        spec = WindowSpec()
        sql = spec.to_sql()
        assert sql == "OVER ()"
    
    def test_partition_by(self):
        """Test PARTITION BY clause."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        spec = WindowSpec().partition_by(col1, col2)
        sql = spec.to_sql()
        assert "PARTITION BY pair, exchange" in sql
        assert "OVER (" in sql
    
    def test_order_by(self):
        """Test ORDER BY clause."""
        col = Column("timestamp_ms", UInt64)
        spec = WindowSpec().order_by(col)
        sql = spec.to_sql()
        assert "ORDER BY timestamp_ms ASC" in sql
        assert "OVER (" in sql
    
    def test_order_by_desc(self):
        """Test ORDER BY DESC clause."""
        col = Column("timestamp_ms", UInt64)
        spec = WindowSpec().order_by(col, desc=True)
        sql = spec.to_sql()
        assert "ORDER BY timestamp_ms DESC" in sql
    
    def test_order_by_multiple(self):
        """Test ORDER BY with multiple columns."""
        col1 = Column("pair", String)
        col2 = Column("timestamp_ms", UInt64)
        spec = WindowSpec().order_by(col1, col2, desc=[False, True])
        sql = spec.to_sql()
        assert "ORDER BY pair ASC, timestamp_ms DESC" in sql
    
    def test_rows_between(self):
        """Test ROWS BETWEEN frame specification."""
        spec = WindowSpec().rows_between(0, 2)
        sql = spec.to_sql()
        assert "ROWS BETWEEN 0 AND 2" in sql
    
    def test_rows_between_unbounded(self):
        """Test ROWS BETWEEN with UNBOUNDED."""
        spec = WindowSpec().rows_between("UNBOUNDED PRECEDING", "CURRENT ROW")
        sql = spec.to_sql()
        assert "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in sql
    
    def test_range_between(self):
        """Test RANGE BETWEEN frame specification."""
        spec = WindowSpec().range_between(0, 2)
        sql = spec.to_sql()
        assert "RANGE BETWEEN 0 AND 2" in sql
    
    def test_complex_window_spec(self):
        """Test complex window specification with all clauses."""
        col1 = Column("pair", String)
        col2 = Column("timestamp_ms", UInt64)
        spec = (WindowSpec()
            .partition_by(col1)
            .order_by(col2, desc=True)
            .rows_between("UNBOUNDED PRECEDING", "CURRENT ROW"))
        sql = spec.to_sql()
        assert "PARTITION BY pair" in sql
        assert "ORDER BY timestamp_ms DESC" in sql
        assert "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in sql


class TestFunctionWithOver:
    """Test cases for Function with OVER clause."""
    
    def test_function_over_empty(self):
        """Test function with empty OVER clause."""
        col = Column("pair", String)
        func = Function("length", col).over()
        sql = func.to_sql()
        assert "length(pair) OVER ()" in sql
    
    def test_function_over_partition_by(self):
        """Test function with OVER PARTITION BY."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        spec = WindowSpec().partition_by(col2)
        func = Function("length", col1).over(spec)
        sql = func.to_sql()
        assert "length(pair)" in sql
        assert "PARTITION BY exchange" in sql
    
    def test_function_over_order_by(self):
        """Test function with OVER ORDER BY."""
        col1 = Column("price", Float64)
        col2 = Column("timestamp_ms", UInt64)
        spec = WindowSpec().order_by(col2)
        func = Function("firstValue", col1).over(spec)
        sql = func.to_sql()
        assert "firstValue(price)" in sql
        assert "ORDER BY timestamp_ms ASC" in sql
    
    def test_window_function_over(self):
        """Test window function with OVER clause."""
        col = Column("pair", String)
        spec = WindowSpec().partition_by(col).order_by(Column("timestamp_ms", UInt64))
        func = rowNumber().over(spec)
        sql = func.to_sql()
        assert "row_number()" in sql
        assert "PARTITION BY pair" in sql
        assert "ORDER BY timestamp_ms ASC" in sql
    
    def test_function_over_with_alias(self):
        """Test function with OVER clause and alias."""
        col = Column("pair", String)
        spec = WindowSpec().partition_by(col)
        func = Function("length", col).over(spec).alias("pair_length")
        sql = func.to_sql()
        assert "length(pair)" in sql
        assert "PARTITION BY pair" in sql
        assert "as pair_length" in sql


class TestAggregateFunctionWithOver:
    """Test cases for AggregateFunction with OVER clause."""
    
    def test_avg_over(self):
        """Test AVG with OVER clause."""
        col1 = Column("price", Float64)
        col2 = Column("exchange", String)
        spec = WindowSpec().partition_by(col2)
        func = avg(col1).over(spec)
        sql = func.to_sql()
        assert "AVG(price)" in sql
        assert "PARTITION BY exchange" in sql
    
    def test_sum_over(self):
        """Test SUM with OVER clause."""
        col1 = Column("amount", Float64)
        col2 = Column("pair", String)
        spec = WindowSpec().partition_by(col2).order_by(Column("timestamp_ms", UInt64))
        func = sum_func(col1).over(spec)
        sql = func.to_sql()
        assert "SUM(amount)" in sql
        assert "PARTITION BY pair" in sql
        assert "ORDER BY timestamp_ms ASC" in sql
    
    def test_count_over(self):
        """Test COUNT with OVER clause."""
        col = Column("pair", String)
        spec = WindowSpec().partition_by(col)
        func = count().over(spec)
        sql = func.to_sql()
        assert "count(*)" in sql
        assert "PARTITION BY pair" in sql
    
    def test_avg_over_with_frame(self):
        """Test AVG with OVER clause and frame specification."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        spec = (WindowSpec()
            .partition_by(col2)
            .order_by(Column("timestamp_ms", UInt64))
            .rows_between("UNBOUNDED PRECEDING", "CURRENT ROW"))
        func = avg(col1).over(spec)
        sql = func.to_sql()
        assert "AVG(price)" in sql
        assert "PARTITION BY pair" in sql
        assert "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in sql
    
    def test_aggregate_over_with_alias(self):
        """Test aggregate function with OVER clause and alias."""
        col1 = Column("price", Float64)
        col2 = Column("exchange", String)
        spec = WindowSpec().partition_by(col2)
        func = avg(col1).over(spec).alias("avg_price")
        sql = func.to_sql()
        assert "AVG(price)" in sql
        assert "PARTITION BY exchange" in sql
        assert "as avg_price" in sql


class TestWindowFunctionsIntegration:
    """Integration tests for window functions."""
    
    def test_rank_over(self):
        """Test rank() with OVER clause."""
        col = Column("pair", String)
        spec = WindowSpec().partition_by(col).order_by(Column("price", Float64), desc=True)
        func = rank().over(spec)
        sql = func.to_sql()
        assert "rank()" in sql
        assert "PARTITION BY pair" in sql
        assert "ORDER BY price DESC" in sql
    
    def test_dense_rank_over(self):
        """Test denseRank with OVER clause."""
        col = Column("exchange", String)
        spec = WindowSpec().partition_by(col).order_by(Column("timestamp_ms", UInt64))
        func = denseRank().over(spec)
        sql = func.to_sql()
        assert "denseRank()" in sql
        assert "PARTITION BY exchange" in sql
    
    def test_complex_window_query(self):
        """Test complex window function query."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        col3 = Column("timestamp_ms", UInt64)
        
        # Running average partitioned by pair, ordered by timestamp
        spec = (WindowSpec()
            .partition_by(col2)
            .order_by(col3)
            .rows_between("UNBOUNDED PRECEDING", "CURRENT ROW"))
        
        func = avg(col1).over(spec).alias("running_avg")
        sql = func.to_sql()
        
        assert "AVG(price)" in sql
        assert "PARTITION BY pair" in sql
        assert "ORDER BY timestamp_ms ASC" in sql
        assert "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW" in sql
        assert "as running_avg" in sql
    
    def test_multiple_window_functions(self):
        """Test multiple window functions with different specifications."""
        col1 = Column("price", Float64)
        col2 = Column("pair", String)
        col3 = Column("exchange", String)
        
        # AVG partitioned by pair
        spec1 = WindowSpec().partition_by(col2)
        func1 = avg(col1).over(spec1).alias("avg_by_pair")
        
        # SUM partitioned by exchange
        spec2 = WindowSpec().partition_by(col3)
        func2 = sum_func(col1).over(spec2).alias("sum_by_exchange")
        
        sql1 = func1.to_sql()
        sql2 = func2.to_sql()
        
        assert "AVG(price)" in sql1
        assert "PARTITION BY pair" in sql1
        assert "as avg_by_pair" in sql1
        
        assert "SUM(price)" in sql2
        assert "PARTITION BY exchange" in sql2
        assert "as sum_by_exchange" in sql2

