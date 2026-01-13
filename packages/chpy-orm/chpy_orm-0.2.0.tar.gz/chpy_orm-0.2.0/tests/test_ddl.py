"""
Tests for DDL operations.
"""

import pytest
from unittest.mock import Mock, call
from chpy.ddl import DDL
from chpy.client import ClickHouseClient
from chpy.orm import Table, Column
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestDDL:
    """Test cases for DDL class."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock ClickHouse client."""
        client = Mock(spec=ClickHouseClient)
        client.execute_command = Mock()
        return client
    
    @pytest.fixture
    def ddl(self, mock_client):
        """DDL instance."""
        return DDL(mock_client)
    
    def test_create_table_from_table_object(self, ddl, mock_client):
        """Test creating table from Table object."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
            Column("value", Float64),
        ]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by="id")
        
        mock_client.execute_command.assert_called_once()
        call_args = mock_client.execute_command.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS my_db.my_table" in call_args
        assert "id UInt64" in call_args
        assert "name String" in call_args
        assert "value Float64" in call_args
        assert "ENGINE = MergeTree" in call_args
        assert "ORDER BY id" in call_args
    
    def test_create_table_from_string(self, ddl, mock_client):
        """Test creating table from string table name."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        
        ddl.create_table("my_table", columns=columns, database="my_db", order_by="id")
        
        mock_client.execute_command.assert_called_once()
        call_args = mock_client.execute_command.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS my_db.my_table" in call_args
        assert "ORDER BY id" in call_args
    
    def test_create_table_with_partition_by(self, ddl, mock_client):
        """Test creating table with PARTITION BY."""
        columns = [Column("id", UInt64), Column("date", "Date")]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by="id", partition_by="date")
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "PARTITION BY date" in call_args
    
    def test_create_table_with_primary_key(self, ddl, mock_client):
        """Test creating table with PRIMARY KEY."""
        columns = [Column("id", UInt64), Column("name", String)]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by="id", primary_key="id")
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "PRIMARY KEY (id)" in call_args
    
    def test_create_table_with_settings(self, ddl, mock_client):
        """Test creating table with settings."""
        columns = [Column("id", UInt64)]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by="id", settings={"index_granularity": 8192})
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "SETTINGS" in call_args
        assert "index_granularity = 8192" in call_args
    
    def test_create_table_without_if_not_exists(self, ddl, mock_client):
        """Test creating table without IF NOT EXISTS."""
        columns = [Column("id", UInt64)]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by="id", if_not_exists=False)
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "IF NOT EXISTS" not in call_args
        assert "CREATE TABLE my_db.my_table" in call_args
    
    def test_create_table_custom_engine(self, ddl, mock_client):
        """Test creating table with custom engine."""
        columns = [Column("id", UInt64)]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, engine="Memory", order_by="id")
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "ENGINE = Memory" in call_args
    
    def test_drop_table_from_table_object(self, ddl, mock_client):
        """Test dropping table from Table object."""
        schema = Table("my_table", "my_db", [])
        
        ddl.drop_table(schema)
        
        mock_client.execute_command.assert_called_once_with("DROP TABLE IF EXISTS my_db.my_table")
    
    def test_drop_table_from_string(self, ddl, mock_client):
        """Test dropping table from string."""
        ddl.drop_table("my_db.my_table")
        
        mock_client.execute_command.assert_called_once_with("DROP TABLE IF EXISTS my_db.my_table")
    
    def test_drop_table_with_database_param(self, ddl, mock_client):
        """Test dropping table with database parameter."""
        ddl.drop_table("my_table", database="my_db")
        
        mock_client.execute_command.assert_called_once_with("DROP TABLE IF EXISTS my_db.my_table")
    
    def test_drop_table_without_if_exists(self, ddl, mock_client):
        """Test dropping table without IF EXISTS."""
        ddl.drop_table("my_db.my_table", if_exists=False)
        
        mock_client.execute_command.assert_called_once_with("DROP TABLE my_db.my_table")
    
    def test_add_column(self, ddl, mock_client):
        """Test adding a column."""
        new_col = Column("new_col", String)
        ddl.add_column("my_db.my_table", new_col)
        
        mock_client.execute_command.assert_called_once_with(
            "ALTER TABLE my_db.my_table ADD COLUMN IF NOT EXISTS new_col String"
        )
    
    def test_add_column_after(self, ddl, mock_client):
        """Test adding a column after another column."""
        new_col = Column("new_col", String)
        ddl.add_column("my_db.my_table", new_col, after="id")
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "AFTER id" in call_args
    
    def test_add_column_without_if_not_exists(self, ddl, mock_client):
        """Test adding column without IF NOT EXISTS."""
        new_col = Column("new_col", String)
        ddl.add_column("my_db.my_table", new_col, if_not_exists=False)
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "IF NOT EXISTS" not in call_args
    
    def test_drop_column(self, ddl, mock_client):
        """Test dropping a column."""
        ddl.drop_column("my_db.my_table", "old_col")
        
        mock_client.execute_command.assert_called_once_with(
            "ALTER TABLE my_db.my_table DROP COLUMN IF EXISTS old_col"
        )
    
    def test_drop_column_without_if_exists(self, ddl, mock_client):
        """Test dropping column without IF EXISTS."""
        ddl.drop_column("my_db.my_table", "old_col", if_exists=False)
        
        mock_client.execute_command.assert_called_once_with(
            "ALTER TABLE my_db.my_table DROP COLUMN old_col"
        )
    
    def test_modify_column(self, ddl, mock_client):
        """Test modifying a column."""
        col = Column("name", "FixedString(100)")
        ddl.modify_column("my_db.my_table", col)
        
        mock_client.execute_command.assert_called_once_with(
            "ALTER TABLE my_db.my_table MODIFY COLUMN name FixedString(100)"
        )
    
    def test_rename_table(self, ddl, mock_client):
        """Test renaming a table."""
        ddl.rename_table("my_db.old_table", "new_table")
        
        mock_client.execute_command.assert_called_once_with(
            "RENAME TABLE my_db.old_table TO my_db.new_table"
        )
    
    def test_rename_table_from_table_object(self, ddl, mock_client):
        """Test renaming table from Table object."""
        schema = Table("old_table", "my_db", [])
        ddl.rename_table(schema, "new_table")
        
        mock_client.execute_command.assert_called_once_with(
            "RENAME TABLE my_db.old_table TO my_db.new_table"
        )
    
    def test_create_database(self, ddl, mock_client):
        """Test creating a database."""
        ddl.create_database("my_database")
        
        mock_client.execute_command.assert_called_once_with(
            "CREATE DATABASE IF NOT EXISTS my_database"
        )
    
    def test_create_database_with_engine(self, ddl, mock_client):
        """Test creating database with engine."""
        ddl.create_database("my_database", engine="Atomic")
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "ENGINE = Atomic" in call_args
    
    def test_create_database_without_if_not_exists(self, ddl, mock_client):
        """Test creating database without IF NOT EXISTS."""
        ddl.create_database("my_database", if_not_exists=False)
        
        mock_client.execute_command.assert_called_once_with(
            "CREATE DATABASE my_database"
        )
    
    def test_drop_database(self, ddl, mock_client):
        """Test dropping a database."""
        ddl.drop_database("my_database")
        
        mock_client.execute_command.assert_called_once_with(
            "DROP DATABASE IF EXISTS my_database"
        )
    
    def test_drop_database_without_if_exists(self, ddl, mock_client):
        """Test dropping database without IF EXISTS."""
        ddl.drop_database("my_database", if_exists=False)
        
        mock_client.execute_command.assert_called_once_with(
            "DROP DATABASE my_database"
        )
    
    def test_create_table_multiple_order_by(self, ddl, mock_client):
        """Test creating table with multiple ORDER BY columns."""
        columns = [Column("id", UInt64), Column("timestamp", UInt64)]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by=["id", "timestamp"])
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "ORDER BY id, timestamp" in call_args
    
    def test_create_table_multiple_partition_by(self, ddl, mock_client):
        """Test creating table with multiple PARTITION BY columns."""
        columns = [Column("date", "Date"), Column("region", String)]
        schema = Table("my_table", "my_db", columns)
        
        ddl.create_table(schema, order_by="date", partition_by=["date", "region"])
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "PARTITION BY date, region" in call_args
    
    def test_create_table_errors(self, ddl):
        """Test error cases for create_table."""
        # Missing columns when table is string
        with pytest.raises(ValueError, match="columns parameter is required"):
            ddl.create_table("my_table", database="my_db", order_by="id")
        
        # Missing database when table is string
        with pytest.raises(ValueError, match="database parameter is required"):
            ddl.create_table("my_table", columns=[Column("id", UInt64)], order_by="id")
        
        # Invalid table type
        with pytest.raises(TypeError):
            ddl.create_table(123, order_by="id")
    
    def test_drop_table_errors(self, ddl):
        """Test error cases for drop_table."""
        # Missing database when table doesn't include database
        with pytest.raises(ValueError, match="database parameter is required"):
            ddl.drop_table("my_table")
        
        # Invalid table type
        with pytest.raises(TypeError):
            ddl.drop_table(123)
    
    def test_add_column_errors(self, ddl):
        """Test error cases for add_column."""
        # Missing database
        with pytest.raises(ValueError, match="database parameter is required"):
            ddl.add_column("my_table", Column("col", String))
        
        # Invalid table type
        with pytest.raises(TypeError):
            ddl.add_column(123, Column("col", String))

