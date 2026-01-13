"""
Tests for subquery functionality in chpy.
"""

import pytest
from unittest.mock import Mock
from chpy.query_builder import QueryBuilder
from chpy.orm import Column, Subquery, SubqueryExpression, Table
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestSubquery:
    """Test cases for Subquery class."""
    
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
    
    @pytest.fixture
    def subquery_builder(self, mock_client, escape_func):
        """QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.other_table", mock_client, escape_func)
    
    def test_subquery_init(self, subquery_builder):
        """Test Subquery initialization."""
        subq = Subquery(subquery_builder)
        assert subq.query_builder == subquery_builder
        assert subq._alias is None
    
    def test_subquery_to_sql(self, subquery_builder):
        """Test Subquery to_sql conversion."""
        subquery_builder.select("pair").where(Column("pair", String) == "BTC-USDT")
        subq = Subquery(subquery_builder)
        
        sql = subq.to_sql()
        assert sql.startswith("(")
        assert sql.endswith(")")
        assert "SELECT pair" in sql
        assert "FROM test_db.other_table" in sql
    
    def test_subquery_with_alias(self, subquery_builder):
        """Test Subquery with alias."""
        subq = Subquery(subquery_builder).alias("subq_result")
        assert subq._alias == "subq_result"
        
        sql = subq.to_sql()
        assert "AS subq_result" in sql
    
    def test_subquery_to_sql_without_alias(self, subquery_builder):
        """Test Subquery to_sql without including alias."""
        subq = Subquery(subquery_builder).alias("subq_result")
        sql = subq.to_sql(include_alias=False)
        assert "AS subq_result" not in sql
        assert sql.startswith("(")
        assert sql.endswith(")")
    
    def test_subquery_exists(self, subquery_builder):
        """Test Subquery.exists static method."""
        expr = Subquery.exists(subquery_builder)
        assert isinstance(expr, SubqueryExpression)
        assert expr.operator == "EXISTS"
        assert isinstance(expr.subquery, Subquery)
    
    def test_subquery_not_exists(self, subquery_builder):
        """Test Subquery.not_exists static method."""
        expr = Subquery.not_exists(subquery_builder)
        assert isinstance(expr, SubqueryExpression)
        assert expr.operator == "NOT EXISTS"
        assert isinstance(expr.subquery, Subquery)


class TestSubqueryInWhere:
    """Test cases for subqueries in WHERE clause."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[
            {"pair": "BTC-USDT", "price": 50000.0},
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
    
    @pytest.fixture
    def subquery_builder(self, mock_client, escape_func):
        """QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.other_table", mock_client, escape_func)
    
    def test_where_with_subquery_in(self, builder, subquery_builder):
        """Test WHERE clause with subquery in IN operator."""
        col = Column("pair", String)
        subquery_builder.select("pair").where(Column("exchange", String) == "BINANCE")
        subq = Subquery(subquery_builder)
        
        builder.where(col.in_(subq))
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "pair IN" in query
        assert "(SELECT pair FROM test_db.other_table" in query
        assert "exchange = 'BINANCE'" in query
    
    def test_where_with_subquery_not_in(self, builder, subquery_builder):
        """Test WHERE clause with subquery in NOT IN operator."""
        col = Column("pair", String)
        subquery_builder.select("pair")
        subq = Subquery(subquery_builder)
        
        builder.where(col.not_in(subq))
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "pair NOT IN" in query
        assert "(SELECT pair FROM test_db.other_table" in query
    
    def test_where_with_subquery_comparison(self, builder, subquery_builder):
        """Test WHERE clause with subquery in comparison operator."""
        col = Column("price", Float64)
        subquery_builder.select("max_price").limit(1)
        subq = Subquery(subquery_builder)
        
        builder.where(col > subq)
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "price >" in query
        assert "(SELECT max_price FROM test_db.other_table" in query
    
    def test_where_with_subquery_equals(self, builder, subquery_builder):
        """Test WHERE clause with subquery in equality operator."""
        col = Column("pair", String)
        subquery_builder.select("pair").limit(1)
        subq = Subquery(subquery_builder)
        
        builder.where(col == subq)
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "pair =" in query
        assert "(SELECT pair FROM test_db.other_table" in query
    
    def test_where_with_exists(self, builder, subquery_builder):
        """Test WHERE clause with EXISTS subquery."""
        subquery_builder.where(Column("pair", String) == "BTC-USDT")
        exists_expr = Subquery.exists(subquery_builder)
        
        builder.where(exists_expr)
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "EXISTS" in query
        assert "(SELECT * FROM test_db.other_table" in query
        assert "pair = 'BTC-USDT'" in query
    
    def test_where_with_not_exists(self, builder, subquery_builder):
        """Test WHERE clause with NOT EXISTS subquery."""
        subquery_builder.where(Column("pair", String) == "ETH-USDT")
        not_exists_expr = Subquery.not_exists(subquery_builder)
        
        builder.where(not_exists_expr)
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "NOT EXISTS" in query
        assert "(SELECT * FROM test_db.other_table" in query
        assert "pair = 'ETH-USDT'" in query
    
    def test_where_with_exists_and_other_conditions(self, builder, subquery_builder):
        """Test WHERE clause combining EXISTS with other conditions."""
        col = Column("exchange", String)
        subquery_builder.where(Column("pair", String) == "BTC-USDT")
        exists_expr = Subquery.exists(subquery_builder)
        
        builder.where((col == "BINANCE") & exists_expr)
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "AND" in query
        assert "exchange = 'BINANCE'" in query
        assert "EXISTS" in query


class TestSubqueryInHaving:
    """Test cases for subqueries in HAVING clause."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[{"count": 10}])
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
    
    @pytest.fixture
    def subquery_builder(self, mock_client, escape_func):
        """QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.other_table", mock_client, escape_func)
    
    def test_having_with_expression(self, builder):
        """Test HAVING clause with ColumnExpression (backward compatibility)."""
        col = Column("price", Float64)
        col2 = Column("min_price", Float64)
        
        builder.having(col > col2)
        query = builder._build_query()
        
        assert "HAVING" in query
        assert "price >" in query
        assert "min_price" in query
    
    def test_having_with_exists(self, builder, subquery_builder):
        """Test HAVING clause with EXISTS subquery."""
        subquery_builder.select("pair")
        exists_expr = Subquery.exists(subquery_builder)
        
        builder.having(exists_expr)
        query = builder._build_query()
        
        assert "HAVING" in query
        assert "EXISTS" in query
        assert "(SELECT pair FROM test_db.other_table" in query
    
    def test_having_with_not_exists(self, builder, subquery_builder):
        """Test HAVING clause with NOT EXISTS subquery."""
        subquery_builder.select("pair")
        not_exists_expr = Subquery.not_exists(subquery_builder)
        
        builder.having(not_exists_expr)
        query = builder._build_query()
        
        assert "HAVING" in query
        assert "NOT EXISTS" in query
    
    def test_having_with_raw_string(self, builder):
        """Test HAVING clause with raw string (backward compatibility)."""
        builder.having("avg_price > 100")
        query = builder._build_query()
        
        assert "HAVING avg_price > 100" in query


class TestSubqueryInSelect:
    """Test cases for subqueries in SELECT clause (scalar subqueries)."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[{"result": 100}])
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
    
    @pytest.fixture
    def subquery_builder(self, mock_client, escape_func):
        """QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.other_table", mock_client, escape_func)
    
    def test_select_with_subquery(self, builder, subquery_builder):
        """Test SELECT clause with scalar subquery."""
        subquery_builder.select("max(price)").limit(1)
        subq = Subquery(subquery_builder)
        
        builder.select(Column("pair", String), subq)
        query = builder._build_query()
        
        assert "SELECT" in query
        assert "pair" in query
        assert "(SELECT max(price) FROM test_db.other_table" in query
    
    def test_select_with_subquery_alias(self, builder, subquery_builder):
        """Test SELECT clause with scalar subquery and alias."""
        subquery_builder.select("max(price)").limit(1)
        subq = Subquery(subquery_builder).alias("max_price")
        
        builder.select(subq)
        query = builder._build_query()
        
        assert "SELECT" in query
        assert "(SELECT max(price) FROM test_db.other_table" in query
        assert "AS max_price" in query
    
    def test_select_with_subquery_and_columns(self, builder, subquery_builder):
        """Test SELECT clause with subquery and other columns."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        subquery_builder.select("count()")
        subq = Subquery(subquery_builder).alias("total_count")
        
        builder.select(col1, col2, subq)
        query = builder._build_query()
        
        assert "SELECT" in query
        assert "pair" in query
        assert "exchange" in query
        assert "(SELECT count() FROM test_db.other_table" in query
        assert "AS total_count" in query


class TestSubqueryInFrom:
    """Test cases for subqueries in FROM clause (derived tables)."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[{"pair": "BTC-USDT"}])
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
    
    @pytest.fixture
    def subquery_builder(self, mock_client, escape_func):
        """QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.other_table", mock_client, escape_func)
    
    def test_from_subquery(self, builder, subquery_builder):
        """Test FROM clause with subquery (derived table)."""
        subquery_builder.select("pair", "price").where(Column("exchange", String) == "BINANCE")
        subq = Subquery(subquery_builder)
        
        builder.from_subquery(subq, alias="derived_table")
        query = builder._build_query()
        
        assert "FROM" in query
        assert "(SELECT pair, price FROM test_db.other_table" in query
        assert "AS derived_table" in query
        assert "exchange = 'BINANCE'" in query
    
    def test_from_subquery_with_select(self, builder, subquery_builder):
        """Test FROM subquery with SELECT clause."""
        subquery_builder.select("pair", "price")
        subq = Subquery(subquery_builder)
        
        builder.from_subquery(subq, alias="dt").select(Column("pair", String))
        query = builder._build_query()
        
        assert "SELECT pair" in query
        assert "FROM (SELECT pair, price FROM test_db.other_table" in query
        assert "AS dt" in query
    
    def test_from_subquery_alias_required(self, builder, subquery_builder):
        """Test that FROM subquery requires an alias."""
        subq = Subquery(subquery_builder)
        
        with pytest.raises(ValueError, match="Alias is required"):
            builder.from_subquery(subq, alias="")
    
    def test_from_subquery_complex(self, builder, subquery_builder):
        """Test complex FROM subquery with multiple clauses."""
        subquery_builder.select("pair", "price")
        subquery_builder.where(Column("exchange", String) == "BINANCE")
        subquery_builder.group_by(Column("pair", String))
        subquery_builder.order_by(Column("pair", String))
        subquery_builder.limit(100)
        subq = Subquery(subquery_builder)
        
        builder.from_subquery(subq, alias="filtered_data")
        query = builder._build_query()
        
        assert "FROM" in query
        assert "(SELECT pair, price FROM test_db.other_table" in query
        assert "WHERE" in query or "exchange = 'BINANCE'" in query
        assert "AS filtered_data" in query


class TestSubqueryExpression:
    """Test cases for SubqueryExpression class."""
    
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
    def subquery_builder(self, mock_client, escape_func):
        """QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.other_table", mock_client, escape_func)
    
    def test_subquery_expression_init(self, subquery_builder):
        """Test SubqueryExpression initialization."""
        subq = Subquery(subquery_builder)
        expr = SubqueryExpression("EXISTS", subq)
        
        assert expr.operator == "EXISTS"
        assert expr.subquery == subq
    
    def test_subquery_expression_to_sql_exists(self, subquery_builder):
        """Test SubqueryExpression to_sql for EXISTS."""
        subquery_builder.select("pair")
        subq = Subquery(subquery_builder)
        expr = SubqueryExpression("EXISTS", subq)
        
        escape_func = lambda x: x.replace("'", "''")
        sql = expr.to_sql(escape_func)
        assert sql.startswith("EXISTS")
        assert "(SELECT pair FROM test_db.other_table" in sql
    
    def test_subquery_expression_to_sql_not_exists(self, subquery_builder):
        """Test SubqueryExpression to_sql for NOT EXISTS."""
        subquery_builder.select("pair")
        subq = Subquery(subquery_builder)
        expr = SubqueryExpression("NOT EXISTS", subq)
        
        escape_func = lambda x: x.replace("'", "''")
        sql = expr.to_sql(escape_func)
        assert sql.startswith("NOT EXISTS")
        assert "(SELECT pair FROM test_db.other_table" in sql
    
    def test_subquery_expression_combine_with_and(self, subquery_builder):
        """Test combining SubqueryExpression with AND."""
        from chpy.orm import CombinedExpression
        col = Column("pair", String)
        
        exists_expr = Subquery.exists(subquery_builder)
        col_expr = col == "BTC-USDT"
        combined = col_expr & exists_expr
        
        assert isinstance(combined, CombinedExpression)
        assert combined.operator == "AND"
    
    def test_subquery_expression_combine_with_or(self, subquery_builder):
        """Test combining SubqueryExpression with OR."""
        from chpy.orm import CombinedExpression
        col = Column("pair", String)
        
        exists_expr = Subquery.exists(subquery_builder)
        col_expr = col == "BTC-USDT"
        combined = col_expr | exists_expr
        
        assert isinstance(combined, CombinedExpression)
        assert combined.operator == "OR"


class TestSubqueryComplexScenarios:
    """Test cases for complex subquery scenarios."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock()
        client.execute = Mock(return_value=[{"result": 1}])
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
    
    @pytest.fixture
    def subquery_builder1(self, mock_client, escape_func):
        """First QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.table1", mock_client, escape_func)
    
    @pytest.fixture
    def subquery_builder2(self, mock_client, escape_func):
        """Second QueryBuilder instance for subquery."""
        return QueryBuilder("test_db.table2", mock_client, escape_func)
    
    def test_nested_subqueries(self, builder, subquery_builder1, subquery_builder2):
        """Test nested subqueries."""
        # Outer subquery
        subquery_builder2.select("max_price").limit(1)
        outer_subq = Subquery(subquery_builder2)
        
        # Inner subquery that uses outer subquery
        col = Column("price", Float64)
        subquery_builder1.where(col > outer_subq)
        
        # Main query uses inner subquery
        inner_subq = Subquery.exists(subquery_builder1)
        builder.where(inner_subq)
        
        query = builder._build_query()
        assert "EXISTS" in query
        assert "(SELECT * FROM test_db.table1" in query
        assert "(SELECT max_price FROM test_db.table2" in query
    
    def test_multiple_subqueries_in_where(self, builder, subquery_builder1, subquery_builder2):
        """Test multiple subqueries in WHERE clause."""
        col1 = Column("pair", String)
        col2 = Column("price", Float64)
        
        subquery_builder1.select("pair")
        subq1 = Subquery(subquery_builder1)
        
        subquery_builder2.select("max(price)").limit(1)
        subq2 = Subquery(subquery_builder2)
        
        builder.where(col1.in_(subq1) & (col2 > subq2))
        query = builder._build_query()
        
        assert "WHERE" in query
        assert "pair IN" in query
        assert "price >" in query
        assert "(SELECT pair FROM test_db.table1" in query
        assert "(SELECT max(price) FROM test_db.table2" in query
    
    def test_subquery_in_select_and_where(self, builder, subquery_builder1, subquery_builder2):
        """Test subquery in both SELECT and WHERE clauses."""
        col = Column("pair", String)
        
        # Subquery for WHERE
        subquery_builder1.select("pair")
        subq_where = Subquery(subquery_builder1)
        
        # Subquery for SELECT
        subquery_builder2.select("count()")
        subq_select = Subquery(subquery_builder2).alias("total")
        
        builder.select(col, subq_select).where(col.in_(subq_where))
        query = builder._build_query()
        
        assert "SELECT pair" in query
        assert "(SELECT count() FROM test_db.table2" in query
        assert "AS total" in query
        assert "WHERE" in query
        assert "pair IN" in query
        assert "(SELECT pair FROM test_db.table1" in query

