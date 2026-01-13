"""
Tests for ClickHouse type builders.
"""

import pytest
from chpy.types import (
    String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool,
    LowCardinality,
    Nullable,
    Array,
    Tuple,
    Map,
    Nested,
    FixedString,
    Enum,
    IPv4,
    IPv6,
    UUID,
    Date,
    DateTime,
    DateTime64,
    LowCardinalityNullable,
    NullableArray,
    ArrayNullable,
)
from chpy.orm import Column, Table


class TestTypeBuilders:
    """Test cases for type builders."""
    
    def test_low_cardinality(self):
        """Test LowCardinality type."""
        assert str(LowCardinality("String")) == "LowCardinality(String)"
        assert str(LowCardinality(Nullable("String"))) == "LowCardinality(Nullable(String))"
    
    def test_nullable(self):
        """Test Nullable type."""
        assert str(Nullable("String")) == "Nullable(String)"
        assert str(Nullable(Array("Int64"))) == "Nullable(Array(Int64))"
    
    def test_array(self):
        """Test Array type."""
        assert str(Array("Int64")) == "Array(Int64)"
        assert str(Array(Nullable("String"))) == "Array(Nullable(String))"
        assert str(Array(LowCardinality("String"))) == "Array(LowCardinality(String))"
    
    def test_tuple(self):
        """Test Tuple type."""
        assert str(Tuple("String", "Int64")) == "Tuple(String, Int64)"
        assert str(Tuple(Nullable("String"), Array("Int64"))) == "Tuple(Nullable(String), Array(Int64))"
    
    def test_map(self):
        """Test Map type."""
        assert str(Map("String", "Int64")) == "Map(String, Int64)"
        assert str(Map("String", Nullable("Float64"))) == "Map(String, Nullable(Float64))"
    
    def test_nested(self):
        """Test Nested type."""
        # Tuple format
        nested1 = Nested(("name", "String"), ("age", "Int64"))
        assert "name String" in str(nested1)
        assert "age Int64" in str(nested1)
        
        # Alternating format
        nested2 = Nested("name", "String", "age", "Int64")
        assert "name String" in str(nested2)
        assert "age Int64" in str(nested2)
    
    def test_nested_errors(self):
        """Test Nested type error cases."""
        with pytest.raises(ValueError, match="requires at least one field"):
            Nested()
        
        with pytest.raises(ValueError, match="requires even number"):
            Nested("name", "String", "age")
    
    def test_fixed_string(self):
        """Test FixedString type."""
        assert str(FixedString(100)) == "FixedString(100)"
        
        with pytest.raises(ValueError, match="must be positive"):
            FixedString(0)
    
    def test_enum(self):
        """Test Enum type."""
        # Dict format
        enum1 = Enum({"red": 1, "green": 2, "blue": 3})
        assert "'red' = 1" in str(enum1)
        assert "'green' = 2" in str(enum1)
        
        # Alternating format
        enum2 = Enum("red", 1, "green", 2)
        assert "'red' = 1" in str(enum2)
        assert "'green' = 2" in str(enum2)
    
    def test_enum_errors(self):
        """Test Enum type error cases."""
        with pytest.raises(ValueError, match="requires at least one value"):
            Enum()
        
        with pytest.raises(ValueError, match="requires even number"):
            Enum("red", 1, "green")
        
        with pytest.raises(ValueError, match="name must be string"):
            Enum(1, 2)
        
        with pytest.raises(ValueError, match="value must be int"):
            Enum("red", "1")
    
    def test_simple_types(self):
        """Test simple type builders."""
        assert str(IPv4()) == "IPv4"
        assert str(IPv6()) == "IPv6"
        assert str(UUID()) == "UUID"
        assert str(Date()) == "Date"
        assert str(DateTime()) == "DateTime"
        assert str(DateTime("UTC")) == "DateTime(UTC)"
        assert str(DateTime64(3)) == "DateTime64(3)"
        assert str(DateTime64(3, "UTC")) == "DateTime64(3, 'UTC')"
    
    def test_datetime64_errors(self):
        """Test DateTime64 error cases."""
        with pytest.raises(ValueError, match="precision must be between"):
            DateTime64(10)
        
        with pytest.raises(ValueError, match="precision must be between"):
            DateTime64(-1)
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        assert "LowCardinality(Nullable" in str(LowCardinalityNullable("String"))
        assert "Nullable(Array" in str(NullableArray("String"))
        assert "Array(Nullable" in str(ArrayNullable("String"))


class TestTypesWithColumns:
    """Test type builders with Column objects."""
    
    def test_column_with_type_builder(self):
        """Test Column with type builder."""
        col1 = Column("name", LowCardinality(String))
        assert col1.type == "LowCardinality(String)"
        
        col2 = Column("tags", Array(String))
        assert col2.type == "Array(String)"
        
        col3 = Column("metadata", Map(String, String))
        assert col3.type == "Map(String, String)"
    
    def test_column_with_nested_types(self):
        """Test Column with nested type builders."""
        col1 = Column("data", Nullable(Array(Int64)))
        assert col1.type == "Nullable(Array(Int64))"
        
        col2 = Column("info", LowCardinality(Nullable(String)))
        assert col2.type == "LowCardinality(Nullable(String))"
    
    def test_table_with_type_builders(self):
        """Test Table with columns using type builders."""
        columns = [
            Column("id", UInt64),
            Column("name", LowCardinality(String)),
            Column("tags", Array(String)),
            Column("metadata", Map(String, String)),
            Column("created_at", DateTime("UTC")),
        ]
        table = Table("test_table", "test_db", columns)
        
        assert table.id.type == "UInt64"
        assert table.name.type == "LowCardinality(String)"
        assert table.tags.type == "Array(String)"
        assert table.metadata.type == "Map(String, String)"
        assert table.created_at.type == "DateTime(UTC)"

