"""
Tests for chpy.orm module.
"""

import pytest
from datetime import datetime
from chpy.orm import Column, ColumnExpression, CombinedExpression, Table, Row
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestColumn:
    """Test cases for Column class."""
    
    def test_init(self):
        """Test column initialization."""
        col = Column("test_col", String)
        assert col.name == "test_col"
        assert col.type == "String"
        assert col.table is None
    
    def test_init_with_table(self, sample_table):
        """Test column initialization with table."""
        col = Column("test_col", String, sample_table)
        assert col.name == "test_col"
        assert col.table == sample_table
    
    def test_eq(self):
        """Test equality expression."""
        col = Column("test_col", String)
        expr = col == "value"
        
        assert isinstance(expr, ColumnExpression)
        assert expr.column == col
        assert expr.operator == "="
        assert expr.value == "value"
    
    def test_ne(self):
        """Test inequality expression."""
        col = Column("test_col", String)
        expr = col != "value"
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == "!="
        assert expr.value == "value"
    
    def test_lt(self):
        """Test less-than expression."""
        col = Column("price", Float64)
        expr = col < 100.0
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == "<"
        assert expr.value == 100.0
    
    def test_le(self):
        """Test less-than-or-equal expression."""
        col = Column("price", Float64)
        expr = col <= 100.0
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == "<="
        assert expr.value == 100.0
    
    def test_gt(self):
        """Test greater-than expression."""
        col = Column("price", Float64)
        expr = col > 100.0
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == ">"
        assert expr.value == 100.0
    
    def test_ge(self):
        """Test greater-than-or-equal expression."""
        col = Column("price", Float64)
        expr = col >= 100.0
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == ">="
        assert expr.value == 100.0
    
    def test_in_(self):
        """Test IN expression."""
        col = Column("pair", String)
        expr = col.in_(["BTC-USDT", "ETH-USDT"])
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == "IN"
        assert expr.value == ["BTC-USDT", "ETH-USDT"]
    
    def test_not_in(self):
        """Test NOT IN expression."""
        col = Column("pair", String)
        expr = col.not_in(["BTC-USDT", "ETH-USDT"])
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == "NOT IN"
        assert expr.value == ["BTC-USDT", "ETH-USDT"]
    
    def test_like(self):
        """Test LIKE expression."""
        col = Column("pair", String)
        expr = col.like("BTC-%")
        
        assert isinstance(expr, ColumnExpression)
        assert expr.operator == "LIKE"
        assert expr.value == "BTC-%"
    
    def test_str(self):
        """Test string representation."""
        col = Column("test_col", String)
        assert str(col) == "test_col"
    
    def test_repr_without_table(self):
        """Test representation without table."""
        col = Column("test_col", String)
        assert repr(col) == "test_col"
    
    def test_repr_with_table(self):
        """Test representation with table."""
        table = Table("test_table", "test_db", [])
        col = Column("test_col", String, table)
        assert repr(col) == "test_table.test_col"


class TestColumnExpression:
    """Test cases for ColumnExpression class."""
    
    def test_to_sql_equals_string(self, escape_string_func):
        """Test SQL generation for string equality."""
        col = Column("pair", String)
        expr = col == "BTC-USDT"
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "pair = 'BTC-USDT'"
    
    def test_to_sql_equals_number(self, escape_string_func):
        """Test SQL generation for number equality."""
        col = Column("price", Float64)
        expr = col == 100.0
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "price = 100.0"
    
    def test_to_sql_equals_datetime(self, escape_string_func):
        """Test SQL generation for datetime equality."""
        col = Column("timestamp_ms", UInt64)
        dt = datetime(2024, 1, 1, 12, 0, 0)
        expr = col >= dt
        
        sql = expr.to_sql(escape_string_func)
        # Should convert datetime to milliseconds timestamp
        expected_ts = int(dt.timestamp() * 1000)
        assert sql == f"timestamp_ms >= {expected_ts}"
    
    def test_to_sql_in_strings(self, escape_string_func):
        """Test SQL generation for IN with strings."""
        col = Column("pair", String)
        expr = col.in_(["BTC-USDT", "ETH-USDT"])
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "pair IN ('BTC-USDT', 'ETH-USDT')"
    
    def test_to_sql_in_numbers(self, escape_string_func):
        """Test SQL generation for IN with numbers."""
        col = Column("id", UInt64)
        expr = col.in_([1, 2, 3])
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "id IN (1, 2, 3)"
    
    def test_to_sql_not_in(self, escape_string_func):
        """Test SQL generation for NOT IN."""
        col = Column("pair", String)
        expr = col.not_in(["BTC-USDT", "ETH-USDT"])
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "pair NOT IN ('BTC-USDT', 'ETH-USDT')"
    
    def test_to_sql_like(self, escape_string_func):
        """Test SQL generation for LIKE."""
        col = Column("pair", String)
        expr = col.like("BTC-%")
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "pair LIKE 'BTC-%'"
    
    def test_to_sql_escape_string(self, escape_string_func):
        """Test SQL generation with string escaping."""
        col = Column("name", String)
        expr = col == "O'Brien"
        
        sql = expr.to_sql(escape_string_func)
        assert sql == "name = 'O''Brien'"
    
    def test_and_operator(self):
        """Test AND operator combination."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "BINANCE"
        
        combined = expr1 & expr2
        
        assert isinstance(combined, CombinedExpression)
        assert combined.operator == "AND"
        assert combined.left == expr1
        assert combined.right == expr2
    
    def test_or_operator(self):
        """Test OR operator combination."""
        col1 = Column("pair", String)
        col2 = Column("pair", String)
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "ETH-USDT"
        
        combined = expr1 | expr2
        
        assert isinstance(combined, CombinedExpression)
        assert combined.operator == "OR"
        assert combined.left == expr1
        assert combined.right == expr2
    
    def test_invert(self):
        """Test expression negation."""
        col = Column("pair", String)
        expr = col == "BTC-USDT"
        
        negated = ~expr
        
        assert isinstance(negated, ColumnExpression)
        assert negated.operator == "NOT ="
        assert negated.value == "BTC-USDT"


class TestCombinedExpression:
    """Test cases for CombinedExpression class."""
    
    def test_to_sql_and(self, escape_string_func):
        """Test SQL generation for AND expression."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "BINANCE"
        combined = expr1 & expr2
        
        sql = combined.to_sql(escape_string_func)
        assert sql == "(pair = 'BTC-USDT' AND exchange = 'BINANCE')"
    
    def test_to_sql_or(self, escape_string_func):
        """Test SQL generation for OR expression."""
        col1 = Column("pair", String)
        col2 = Column("pair", String)
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "ETH-USDT"
        combined = expr1 | expr2
        
        sql = combined.to_sql(escape_string_func)
        assert sql == "(pair = 'BTC-USDT' OR pair = 'ETH-USDT')"
    
    def test_to_sql_nested(self, escape_string_func):
        """Test SQL generation for nested expressions."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        col3 = Column("price", Float64)
        
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "BINANCE"
        expr3 = col3 > 50000
        
        combined = (expr1 & expr2) | expr3
        
        sql = combined.to_sql(escape_string_func)
        assert "(pair = 'BTC-USDT' AND exchange = 'BINANCE')" in sql
        assert "OR price > 50000" in sql
    
    def test_and_operator(self):
        """Test AND operator on CombinedExpression."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        col3 = Column("price", Float64)
        
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "BINANCE"
        expr3 = col3 > 50000
        
        combined1 = expr1 & expr2
        combined2 = combined1 & expr3
        
        assert isinstance(combined2, CombinedExpression)
        assert combined2.operator == "AND"
    
    def test_or_operator(self):
        """Test OR operator on CombinedExpression."""
        col1 = Column("pair", String)
        col2 = Column("exchange", String)
        col3 = Column("pair", String)
        
        expr1 = col1 == "BTC-USDT"
        expr2 = col2 == "BINANCE"
        expr3 = col3 == "ETH-USDT"
        
        combined1 = expr1 & expr2
        combined2 = combined1 | expr3
        
        assert isinstance(combined2, CombinedExpression)
        assert combined2.operator == "OR"


class TestTable:
    """Test cases for Table class."""
    
    def test_init(self):
        """Test table initialization."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        table = Table("test_table", "test_db", columns)
        
        assert table.name == "test_table"
        assert table.database == "test_db"
        assert table.full_name == "test_db.test_table"
        assert len(table._columns) == 2
    
    def test_column_access(self):
        """Test column access via attributes."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        table = Table("test_table", "test_db", columns)
        
        assert table.id.name == "id"
        assert table.name.name == "name"
        assert table.id.table == table
        assert table.name.table == table
    
    def test_get_column(self):
        """Test get_column method."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        table = Table("test_table", "test_db", columns)
        
        col = table.get_column("id")
        assert col is not None
        assert col.name == "id"
        
        assert table.get_column("nonexistent") is None
    
    def test_get_all_columns(self):
        """Test get_all_columns method."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        table = Table("test_table", "test_db", columns)
        
        all_cols = table.get_all_columns()
        assert len(all_cols) == 2
        assert all_cols[0].name == "id"
        assert all_cols[1].name == "name"
    
    def test_getitem(self):
        """Test bracket notation for column access."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        table = Table("test_table", "test_db", columns)
        
        assert table["id"].name == "id"
        assert table["name"].name == "name"
        
        with pytest.raises(AttributeError, match="Column 'nonexistent' not found"):
            _ = table["nonexistent"]
    
    def test_repr(self):
        """Test table representation."""
        columns = [
            Column("id", UInt64),
        ]
        table = Table("test_table", "test_db", columns)
        
        assert repr(table) == "Table(test_db.test_table)"


class TestRow:
    """Test cases for Row class."""
    
    def test_init(self):
        """Test Row initialization."""
        data = {'id': 1, 'name': 'test', 'value': 1.5}
        row = Row(data)
        
        assert row._data == data
    
    def test_attribute_access(self):
        """Test accessing row values via attributes."""
        row = Row({'id': 1, 'name': 'test', 'price': 50000.0})
        
        assert row.id == 1
        assert row.name == 'test'
        assert row.price == 50000.0
    
    def test_attribute_access_missing(self):
        """Test accessing non-existent attribute raises AttributeError."""
        row = Row({'id': 1, 'name': 'test'})
        
        with pytest.raises(AttributeError, match="Row has no attribute 'missing'"):
            _ = row.missing
    
    def test_dict_access(self):
        """Test accessing row values via dictionary syntax."""
        row = Row({'id': 1, 'name': 'test', 'price': 50000.0})
        
        assert row['id'] == 1
        assert row['name'] == 'test'
        assert row['price'] == 50000.0
    
    def test_get_method(self):
        """Test get method with and without default."""
        row = Row({'id': 1, 'name': 'test'})
        
        assert row.get('id') == 1
        assert row.get('name') == 'test'
        assert row.get('missing') is None
        assert row.get('missing', 'default') == 'default'
    
    def test_contains(self):
        """Test checking if key exists in row."""
        row = Row({'id': 1, 'name': 'test'})
        
        assert 'id' in row
        assert 'name' in row
        assert 'missing' not in row
    
    def test_repr(self):
        """Test row representation."""
        row = Row({'id': 1, 'name': 'test'})
        repr_str = repr(row)
        
        assert 'Row' in repr_str
        assert 'id' in repr_str or '1' in repr_str
    
    def test_iter(self):
        """Test iterating over row keys."""
        row = Row({'id': 1, 'name': 'test', 'value': 1.5})
        keys = list(iter(row))
        
        assert set(keys) == {'id', 'name', 'value'}
    
    def test_keys(self):
        """Test keys method."""
        row = Row({'id': 1, 'name': 'test'})
        keys = list(row.keys())
        
        assert set(keys) == {'id', 'name'}
    
    def test_values(self):
        """Test values method."""
        row = Row({'id': 1, 'name': 'test'})
        values = list(row.values())
        
        assert 1 in values
        assert 'test' in values
    
    def test_items(self):
        """Test items method."""
        row = Row({'id': 1, 'name': 'test'})
        items = dict(row.items())
        
        assert items == {'id': 1, 'name': 'test'}
    
    def test_to_dict(self):
        """Test converting row to dictionary."""
        original_data = {'id': 1, 'name': 'test', 'value': 1.5}
        row = Row(original_data)
        
        result_dict = row.to_dict()
        
        assert result_dict == original_data
        assert result_dict is not original_data  # Should be a copy
    
    def test_mixed_access(self):
        """Test mixing attribute and dictionary access."""
        row = Row({'pair': 'BTC-USDT', 'price': 50000.0})
        
        # Attribute access
        assert row.pair == 'BTC-USDT'
        
        # Dictionary access
        assert row['price'] == 50000.0
        
        # Both should work
        assert row.pair == row['pair']
        assert row.price == row['price']
    
    def test_nested_data(self):
        """Test row with nested/complex data types."""
        row = Row({
            'id': 1,
            'tags': ['tag1', 'tag2'],
            'metadata': {'key': 'value'},
            'price': None
        })
        
        assert row.id == 1
        assert row.tags == ['tag1', 'tag2']
        assert row.metadata == {'key': 'value'}
        assert row.price is None
    
    def test_empty_row(self):
        """Test row with empty data."""
        row = Row({})
        
        assert len(list(row.keys())) == 0
        assert row.to_dict() == {}
        with pytest.raises(AttributeError):
            _ = row.missing

