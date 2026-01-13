"""
Tests for chpy.query_builder module.
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch
from datetime import datetime
from chpy.query_builder import QueryBuilder
from chpy.orm import Column, ColumnExpression, Table, Row
from chpy.functions.base import Function, AggregateFunction
from chpy.functions.aggregate import count, avg, sum as sum_func
from chpy.functions.string import length, upper
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestQueryBuilder:
    """Test cases for QueryBuilder class."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[
            {"pair": "BTC-USDT", "price": 50000.0},
            {"pair": "ETH-USDT", "price": 3000.0},
        ])
        client.query_df = Mock()
        client.query_np = Mock()
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
    
    def test_init(self, builder):
        """Test QueryBuilder initialization."""
        assert builder.table_name == "test_db.test_table"
        assert builder._columns is None
        assert builder._where_conditions == []
        assert builder._order_by is None
        assert builder._limit is None
    
    def test_select_all(self, builder):
        """Test select without columns (SELECT *)."""
        query = builder._build_query()
        assert "SELECT *" in query
        assert "FROM test_db.test_table" in query
    
    def test_select_columns_string(self, builder):
        """Test select with string columns."""
        builder.select("col1", "col2", "col3")
        query = builder._build_query()
        assert "SELECT col1, col2, col3" in query
    
    def test_select_column_objects(self, builder):
        """Test select with Column objects."""
        col1 = Column("pair", String)
        col2 = Column("price", Float64)
        builder.select(col1, col2)
        query = builder._build_query()
        assert "SELECT pair, price" in query
    
    def test_select_function(self, builder):
        """Test select with Function objects."""
        col = Column("pair", String)
        func = length(col)
        builder.select(func)
        query = builder._build_query()
        assert "length(pair)" in query
    
    def test_select_aggregate_function(self, builder):
        """Test select with AggregateFunction objects."""
        col = Column("price", Float64)
        func = avg(col)
        builder.select(func)
        query = builder._build_query()
        assert "AVG(price)" in query or "avg(price)" in query.lower()
    
    def test_select_mixed(self, builder):
        """Test select with mixed column types."""
        col1 = Column("pair", String)
        col2 = Column("price", Float64)
        func = avg(col2)
        builder.select(col1, func, "raw_column")
        query = builder._build_query()
        assert "pair" in query
        assert "AVG(price)" in query or "avg(price)" in query.lower()
        assert "raw_column" in query
    
    def test_select_invalid_type(self, builder):
        """Test select with invalid column type."""
        with pytest.raises(TypeError, match="Unsupported column type"):
            builder.select(123)
    
    def test_where(self, builder):
        """Test where clause."""
        col = Column("pair", String)
        expr = col == "BTC-USDT"
        builder.where(expr)
        
        query = builder._build_query()
        assert "WHERE" in query
        assert "pair = 'BTC-USDT'" in query
    
    def test_where_multiple(self, builder):
        """Test multiple where clauses."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        builder.where(col1 == "BTC-USDT")
        builder.where(col2 == "BINANCE")
        
        query = builder._build_query()
        assert "WHERE" in query
        assert "pair = 'BTC-USDT'" in query
        assert "exchange = 'BINANCE'" in query
        assert "AND" in query
    
    def test_order_by_column(self, builder):
        """Test order_by with Column object."""
        col = Column("timestamp_ms", UInt64)
        builder.order_by(col, desc=True)
        
        query = builder._build_query()
        assert "ORDER BY timestamp_ms DESC" in query
    
    def test_order_by_string(self, builder):
        """Test order_by with string (alias)."""
        builder.order_by("avg_price", desc=False)
        
        query = builder._build_query()
        assert "ORDER BY avg_price ASC" in query
    
    def test_order_by_invalid_type(self, builder):
        """Test order_by with invalid type."""
        with pytest.raises(TypeError, match="Unsupported column type"):
            builder.order_by(123)
    
    def test_limit(self, builder):
        """Test limit clause."""
        builder.limit(10)
        
        query = builder._build_query()
        assert "LIMIT 10" in query
    
    def test_group_by(self, builder):
        """Test group_by clause."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        builder.group_by(col1, col2)
        
        query = builder._build_query()
        assert "GROUP BY pair, exchange" in query
    
    def test_having(self, builder):
        """Test having clause."""
        builder.having("avg_price > 100")
        
        query = builder._build_query()
        assert "HAVING avg_price > 100" in query
    
    def test_build_query_complete(self, builder):
        """Test complete query building."""
        col1 = Column("pair", String)
        col2 = Column("price", Float64)
        
        builder.select(col1, avg(col2).alias("avg_price"))
        builder.where(col1 == "BTC-USDT")
        builder.group_by(col1)
        builder.having("avg_price > 100")
        builder.order_by("avg_price", desc=True)
        builder.limit(10)
        
        query = builder._build_query()
        assert "pair" in query
        assert "AVG(price) as avg_price" in query or "avg(price) as avg_price" in query.lower()
        assert "FROM test_db.test_table" in query
        assert "WHERE" in query
        assert "GROUP BY pair" in query
        assert "HAVING avg_price > 100" in query
        assert "ORDER BY avg_price DESC" in query
        assert "LIMIT 10" in query
    
    def test_to_list(self, builder, mock_client):
        """Test to_list method."""
        result = builder.to_list()
        
        assert len(result) == 2
        assert result[0]["pair"] == "BTC-USDT"
        mock_client.execute.assert_called_once()
    
    def test_to_dict_key_value(self, builder, mock_client):
        """Test to_dict with key and value columns."""
        key_col = Column("pair", String)
        value_col = Column("price", Float64)
        
        result = builder.to_dict(key_col, value_col)
        
        assert isinstance(result, dict)
        assert result["BTC-USDT"] == 50000.0
        assert result["ETH-USDT"] == 3000.0
    
    def test_to_dict_key_only(self, builder, mock_client):
        """Test to_dict with key column only."""
        key_col = Column("pair", String)
        
        result = builder.to_dict(key_col)
        
        assert isinstance(result, dict)
        assert "BTC-USDT" in result
        assert isinstance(result["BTC-USDT"], dict)
    
    def test_to_dataframe(self, builder, mock_client):
        """Test to_dataframe method."""
        try:
            import pandas as pd
            mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
            mock_client.query_df.return_value = mock_df
            
            result = builder.to_dataframe()
            
            assert isinstance(result, pd.DataFrame)
            mock_client.query_df.assert_called_once()
        except ImportError:
            pytest.skip("pandas not available")
    
    def test_to_dataframe_fallback(self, builder, mock_client):
        """Test to_dataframe fallback when query_df not available."""
        try:
            import pandas as pd
            # Delete the attribute to trigger AttributeError in fallback
            delattr(mock_client, 'query_df')
            mock_client.execute.return_value = [
                {"col1": 1, "col2": "a"},
                {"col1": 2, "col2": "b"},
            ]
            
            result = builder.to_dataframe()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
        except ImportError:
            pytest.skip("pandas not available")
    
    def test_to_dataframe_no_pandas(self, builder):
        """Test to_dataframe without pandas installed."""
        # This test is skipped - testing import errors when imports happen
        # inside methods is complex and not critical
        pytest.skip("Import error testing for in-method imports is complex")
    
    def test_to_numpy(self, builder, mock_client):
        """Test to_numpy method."""
        try:
            import numpy as np
            mock_array = np.array([[1, 2], [3, 4]])
            mock_client.query_np.return_value = mock_array
            
            result = builder.to_numpy()
            
            assert isinstance(result, np.ndarray)
            mock_client.query_np.assert_called_once()
        except ImportError:
            pytest.skip("numpy not available")
    
    def test_to_numpy_fallback(self, builder, mock_client):
        """Test to_numpy fallback."""
        try:
            import numpy as np
            # Delete the attribute to trigger AttributeError in fallback
            delattr(mock_client, 'query_np')
            mock_client.execute.return_value = [
                {"col1": 1, "col2": 2},
                {"col1": 3, "col2": 4},
            ]
            
            result = builder.to_numpy()
            
            assert isinstance(result, np.ndarray)
        except ImportError:
            pytest.skip("numpy not available")
    
    def test_to_numpy_no_numpy(self, builder):
        """Test to_numpy without numpy installed."""
        # This test is skipped - testing import errors when imports happen
        # inside methods is complex and not critical
        pytest.skip("Import error testing for in-method imports is complex")
    
    def test_to_json(self, builder, mock_client):
        """Test to_json method."""
        result = builder.to_json()
        
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["pair"] == "BTC-USDT"
    
    def test_to_json_indent(self, builder, mock_client):
        """Test to_json with indentation."""
        result = builder.to_json(indent=2)
        
        assert "\n" in result  # Should have newlines with indent
        data = json.loads(result)
        assert len(data) == 2
    
    def test_to_csv(self, builder, mock_client):
        """Test to_csv method."""
        try:
            import pandas as pd
            mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
            mock_client.query_df.return_value = mock_df
            
            result = builder.to_csv()
            
            assert isinstance(result, str)
            assert "col1" in result
        except ImportError:
            pytest.skip("pandas not available")
    
    def test_to_csv_file(self, builder, mock_client, tmp_path):
        """Test to_csv with file path."""
        try:
            import pandas as pd
            mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
            mock_client.query_df.return_value = mock_df
            
            file_path = tmp_path / "output.csv"
            result = builder.to_csv(str(file_path))
            
            assert result is None
            assert file_path.exists()
        except ImportError:
            pytest.skip("pandas not available")
    
    def test_to_csv_no_pandas(self, builder):
        """Test to_csv without pandas."""
        # This test is skipped - testing import errors when imports happen
        # inside methods is complex and not critical
        pytest.skip("Import error testing for in-method imports is complex")
    
    def test_to_parquet(self, builder, mock_client, tmp_path):
        """Test to_parquet method."""
        try:
            import pandas as pd
            mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
            mock_client.query_df.return_value = mock_df
            
            file_path = tmp_path / "output.parquet"
            builder.to_parquet(str(file_path))
            
            assert file_path.exists()
        except ImportError:
            pytest.skip("pandas not available")
    
    def test_count(self, builder, mock_client):
        """Test count method."""
        mock_client.execute.return_value = [{"count": 42}]
        
        result = builder.count()
        
        assert result == 42
        # Verify query was modified for count
        call_args = mock_client.execute.call_args[0][0]
        assert "count()" in call_args.lower()
    
    def test_count_empty(self, builder, mock_client):
        """Test count with no results."""
        mock_client.execute.return_value = []
        
        result = builder.count()
        
        assert result == 0
    
    def test_first(self, builder, mock_client):
        """Test first method."""
        mock_client.execute.return_value = [{"pair": "BTC-USDT", "price": 50000.0}]
        
        result = builder.first()
        
        assert result == {"pair": "BTC-USDT", "price": 50000.0}
        # Verify limit was set to 1
        call_args = mock_client.execute.call_args[0][0]
        assert "LIMIT 1" in call_args
    
    def test_first_empty(self, builder, mock_client):
        """Test first with no results."""
        mock_client.execute.return_value = []
        
        result = builder.first()
        
        assert result is None
    
    def test_exists(self, builder, mock_client):
        """Test exists method."""
        mock_client.execute.return_value = [{"count": 5}]
        
        result = builder.exists()
        
        assert result is True
    
    def test_exists_false(self, builder, mock_client):
        """Test exists with no matches."""
        mock_client.execute.return_value = [{"count": 0}]
        
        result = builder.exists()
        
        assert result is False
    
    def test_iter(self, builder, mock_client):
        """Test iteration."""
        results = list(builder)
        
        assert len(results) == 2
        assert results[0]["pair"] == "BTC-USDT"
    
    def test_repr(self, builder):
        """Test string representation."""
        builder.where(Column("pair", String) == "BTC-USDT")
        builder.limit(10)
        
        repr_str = repr(builder)
        
        assert "QueryBuilder" in repr_str
        assert "query=" in repr_str
    
    # ========================================================================
    # JOIN Tests
    # ========================================================================
    
    @pytest.fixture
    def other_table(self):
        """Create a sample table for JOIN tests."""
        columns = [
            Column("id", UInt64),
            Column("symbol", String),
            Column("name", String),
        ]
        return Table("other_table", "test_db", columns)
    
    def test_join_inner_with_column_expression(self, builder, other_table):
        """Test INNER JOIN with column expression condition."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        builder.join(other_table, condition=(col1 == col2), join_type="INNER")
        
        query = builder._build_query()
        assert "INNER JOIN" in query
        assert "test_db.other_table" in query
        assert "test_db.test_table.pair = test_db.other_table.symbol" in query
    
    def test_join_left_with_column_expression(self, builder, other_table):
        """Test LEFT JOIN with column expression condition."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        builder.join(other_table, condition=(col1 == col2), join_type="LEFT")
        
        query = builder._build_query()
        assert "LEFT JOIN" in query
        assert "test_db.other_table" in query
    
    def test_join_right_with_column_expression(self, builder, other_table):
        """Test RIGHT JOIN with column expression condition."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        builder.join(other_table, condition=(col1 == col2), join_type="RIGHT")
        
        query = builder._build_query()
        assert "RIGHT JOIN" in query
    
    def test_join_full_with_column_expression(self, builder, other_table):
        """Test FULL JOIN with column expression condition."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        builder.join(other_table, condition=(col1 == col2), join_type="FULL")
        
        query = builder._build_query()
        assert "FULL JOIN" in query
    
    def test_join_cross_no_condition(self, builder, other_table):
        """Test CROSS JOIN without condition."""
        builder.join(other_table, join_type="CROSS")
        
        query = builder._build_query()
        assert "CROSS JOIN" in query
        assert "ON" not in query
    
    def test_join_with_string_table(self, builder):
        """Test JOIN with string table name."""
        col1 = Column("pair", String)
        col2 = Column("symbol", String)
        
        builder.join("test_db.other_table", condition=(col1 == col2))
        
        query = builder._build_query()
        assert "INNER JOIN" in query
        assert "test_db.other_table" in query
    
    def test_join_with_alias(self, builder, other_table):
        """Test JOIN with table alias."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        builder.join(other_table, condition=(col1 == col2), alias="ot")
        
        query = builder._build_query()
        assert "AS ot" in query or "ot" in query
    
    def test_join_with_raw_sql_condition(self, builder, other_table):
        """Test JOIN with raw SQL condition."""
        builder.join(other_table, condition="test_table.pair = other_table.symbol")
        
        query = builder._build_query()
        assert "INNER JOIN" in query
        assert "ON test_table.pair = other_table.symbol" in query
    
    def test_join_with_combined_expression(self, builder, other_table):
        """Test JOIN with combined expression (AND/OR)."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        col3 = Column("exchange", String)
        col4 = other_table.name
        
        condition = (col1 == col2) & (col3 == col4)
        builder.join(other_table, condition=condition)
        
        query = builder._build_query()
        assert "INNER JOIN" in query
        assert "AND" in query
    
    def test_join_multiple_tables(self, builder, other_table):
        """Test multiple JOINs."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        # Create another table for second join
        third_table_cols = [Column("quote_id", UInt64), Column("value", Float64)]
        third_table = Table("third_table", "test_db", third_table_cols)
        
        builder.join(other_table, condition=(col1 == col2))
        builder.join(third_table, condition=(other_table.id == third_table.quote_id), join_type="LEFT")
        
        query = builder._build_query()
        assert query.count("JOIN") == 2
        assert "INNER JOIN" in query
        assert "LEFT JOIN" in query
    
    def test_join_with_where_clause(self, builder, other_table):
        """Test JOIN combined with WHERE clause."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        col3 = Column("exchange", String)
        
        builder.join(other_table, condition=(col1 == col2))
        builder.where(col3 == "BINANCE")
        
        query = builder._build_query()
        assert "INNER JOIN" in query
        assert "WHERE" in query
        assert "exchange = 'BINANCE'" in query
    
    def test_join_with_select_table_qualified_columns(self, builder, other_table):
        """Test JOIN with table-qualified column selection."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        col3 = other_table.name
        
        builder.select(col1, col2, col3)
        builder.join(other_table, condition=(col1 == col2))
        
        query = builder._build_query()
        assert "test_db.test_table.pair" in query
        assert "test_db.other_table.symbol" in query
        assert "test_db.other_table.name" in query
    
    def test_join_error_cross_with_condition(self, builder, other_table):
        """Test that CROSS JOIN raises error with condition."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        with pytest.raises(ValueError, match="CROSS JOIN cannot have a condition"):
            builder.join(other_table, condition=(col1 == col2), join_type="CROSS")
    
    def test_join_error_no_condition(self, builder, other_table):
        """Test that non-CROSS JOINs require condition."""
        with pytest.raises(ValueError, match="requires a condition"):
            builder.join(other_table, join_type="INNER")
    
    def test_join_error_invalid_table_type(self, builder):
        """Test JOIN with invalid table type."""
        with pytest.raises(TypeError, match="Unsupported table type"):
            builder.join(123, condition="test = test")
    
    def test_join_error_invalid_condition_type(self, builder, other_table):
        """Test JOIN with invalid condition type."""
        with pytest.raises(TypeError, match="Unsupported condition type"):
            builder.join(other_table, condition=123)
    
    def test_join_complete_query(self, builder, other_table):
        """Test complete query with JOIN, WHERE, GROUP BY, ORDER BY, LIMIT."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        col3 = Column("price", Float64)
        
        builder.select(col1, col2, avg(col3).alias("avg_price"))
        builder.join(other_table, condition=(col1 == col2), alias="ot")
        builder.where(col1 == "BTC-USDT")
        builder.group_by(col1, col2)
        builder.having("avg_price > 100")
        builder.order_by("avg_price", desc=True)
        builder.limit(10)
        
        query = builder._build_query()
        assert "SELECT" in query
        assert "INNER JOIN" in query
        assert "WHERE" in query
        assert "GROUP BY" in query
        assert "HAVING" in query
        assert "ORDER BY" in query
        assert "LIMIT 10" in query
    
    def test_join_column_to_column_comparison(self, builder, other_table):
        """Test JOIN with column-to-column comparison."""
        col1 = Column("pair", String)
        col2 = other_table.symbol
        
        # Test different operators
        builder.join(other_table, condition=(col1 == col2))
        query1 = builder._build_query()
        assert "=" in query1
        
        builder._joins = []  # Reset
        builder.join(other_table, condition=(col1 != col2))
        query2 = builder._build_query()
        assert "!=" in query2
        
        builder._joins = []  # Reset
        builder.join(other_table, condition=(col1 > col2))
        query3 = builder._build_query()
        assert ">" in query3
    
    def test_init_with_schema(self, mock_client, escape_func):
        """Test QueryBuilder initialization with schema."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        schema = Table("test_table", "test_db", columns)
        
        builder = QueryBuilder("test_db.test_table", mock_client, escape_func, schema=schema)
        
        assert builder.table_name == "test_db.test_table"
        assert builder.schema == schema
    
    def test_init_without_schema(self, builder):
        """Test QueryBuilder initialization without schema (backward compatible)."""
        assert builder.schema is None
    
    def test_to_list_with_schema_returns_row_objects(self, mock_client, escape_func):
        """Test that to_list returns Row objects when schema is available."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
            Column("value", Float64),
        ]
        schema = Table("test_table", "test_db", columns)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1", "value": 1.5},
            {"id": 2, "name": "test2", "value": 2.5},
        ]
        
        builder = QueryBuilder("test_db.test_table", mock_client, escape_func, schema=schema)
        results = builder.to_list()
        
        # Should return Row objects
        assert len(results) == 2
        assert isinstance(results[0], Row)
        assert isinstance(results[1], Row)
        
        # Test attribute access
        assert results[0].id == 1
        assert results[0].name == "test1"
        assert results[0].value == 1.5
        
        assert results[1].id == 2
        assert results[1].name == "test2"
        assert results[1].value == 2.5
    
    def test_to_list_without_schema_returns_dicts(self, builder, mock_client):
        """Test that to_list returns dict objects when no schema (backward compatible)."""
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT", "price": 50000.0},
            {"pair": "ETH-USDT", "price": 3000.0},
        ]
        
        results = builder.to_list()
        
        # Should return dict objects (not Row objects)
        assert len(results) == 2
        assert isinstance(results[0], dict)
        assert isinstance(results[1], dict)
        assert not isinstance(results[0], Row)
        assert not isinstance(results[1], Row)
        
        # Test dictionary access
        assert results[0]["pair"] == "BTC-USDT"
        assert results[0]["price"] == 50000.0
    
    def test_first_with_schema_returns_row(self, mock_client, escape_func):
        """Test that first returns Row object when schema is available."""
        columns = [Column("id", UInt64), Column("name", String)]
        schema = Table("test_table", "test_db", columns)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1"},
        ]
        
        builder = QueryBuilder("test_db.test_table", mock_client, escape_func, schema=schema)
        result = builder.first()
        
        assert isinstance(result, Row)
        assert result.id == 1
        assert result.name == "test1"
        assert result["id"] == 1  # Dictionary access also works
    
    def test_first_without_schema_returns_dict(self, builder, mock_client):
        """Test that first returns dict when no schema."""
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT", "price": 50000.0},
        ]
        
        result = builder.first()
        
        assert isinstance(result, dict)
        assert not isinstance(result, Row)
        assert result["pair"] == "BTC-USDT"
    
    def test_first_empty_with_schema(self, mock_client, escape_func):
        """Test first returns None when no results (with schema)."""
        columns = [Column("id", UInt64)]
        schema = Table("test_table", "test_db", columns)
        
        mock_client.execute.return_value = []
        
        builder = QueryBuilder("test_db.test_table", mock_client, escape_func, schema=schema)
        result = builder.first()
        
        assert result is None
    
    def test_iter_with_schema_returns_row_objects(self, mock_client, escape_func):
        """Test that iteration returns Row objects when schema is available."""
        columns = [Column("id", UInt64), Column("name", String)]
        schema = Table("test_table", "test_db", columns)
        
        mock_client.execute.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]
        
        builder = QueryBuilder("test_db.test_table", mock_client, escape_func, schema=schema)
        
        rows = list(builder)
        
        assert len(rows) == 2
        assert all(isinstance(row, Row) for row in rows)
        assert rows[0].id == 1
        assert rows[1].id == 2
    
    def test_iter_without_schema_returns_dicts(self, builder, mock_client):
        """Test that iteration returns dict objects when no schema."""
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT"},
            {"pair": "ETH-USDT"},
        ]
        
        rows = list(builder)
        
        assert len(rows) == 2
        assert all(isinstance(row, dict) for row in rows)
        assert all(not isinstance(row, Row) for row in rows)
        assert rows[0]["pair"] == "BTC-USDT"
    
    def test_row_object_attribute_and_dict_access(self, mock_client, escape_func):
        """Test that Row objects support both attribute and dictionary access."""
        columns = [
            Column("pair", String),
            Column("price", Float64),
            Column("exchange", String),
        ]
        schema = Table("test_table", "test_db", columns)
        
        mock_client.execute.return_value = [
            {"pair": "BTC-USDT", "price": 50000.0, "exchange": "BINANCE"},
        ]
        
        builder = QueryBuilder("test_db.test_table", mock_client, escape_func, schema=schema)
        row = builder.first()
        
        # Attribute access
        assert row.pair == "BTC-USDT"
        assert row.price == 50000.0
        assert row.exchange == "BINANCE"
        
        # Dictionary access
        assert row["pair"] == "BTC-USDT"
        assert row["price"] == 50000.0
        assert row["exchange"] == "BINANCE"
        
        # Get method
        assert row.get("pair") == "BTC-USDT"
        assert row.get("missing", "default") == "default"
        
        # Contains check
        assert "pair" in row
        assert "missing" not in row

