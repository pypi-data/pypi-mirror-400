"""
Tests for advanced DDL operations (materialized views, distributed tables).
"""

import pytest
from unittest.mock import Mock
from chpy.ddl import DDL
from chpy.client import ClickHouseClient
from chpy.orm import Table, Column
from chpy.types import String, Float64, Float32, UInt64, UInt32, UInt16, UInt8, Int64, Int32, Int16, Int8, Bool


class TestMaterializedViews:
    """Test cases for materialized views."""
    
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
    
    def test_create_materialized_view_from_strings(self, ddl, mock_client):
        """Test creating materialized view with string names."""
        columns = [
            Column("pair", String),
            Column("avg_price", Float64),
        ]
        target_table = Table("mv_target", "my_db", columns)
        
        ddl.create_materialized_view(
            "my_view",
            target_table,
            "SELECT pair, avg(price) as avg_price FROM source_table GROUP BY pair",
            database="my_db",
            order_by="pair"
        )
        
        mock_client.execute_command.assert_called_once()
        call_args = mock_client.execute_command.call_args[0][0]
        assert "CREATE MATERIALIZED VIEW IF NOT EXISTS my_db.my_view" in call_args
        assert "TO my_db.mv_target" in call_args
        assert "SELECT pair, avg(price)" in call_args
        assert "ORDER BY pair" in call_args
    
    def test_create_materialized_view_with_populate(self, ddl, mock_client):
        """Test creating materialized view with POPULATE."""
        columns = [Column("id", UInt64), Column("value", Float64)]
        target_table = Table("mv_target", "my_db", columns)
        
        ddl.create_materialized_view(
            "my_view",
            target_table,
            "SELECT * FROM source_table",
            database="my_db",
            order_by="id",
            populate=True
        )
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "POPULATE" in call_args
    
    def test_create_materialized_view_with_settings(self, ddl, mock_client):
        """Test creating materialized view with settings."""
        columns = [Column("id", UInt64)]
        target_table = Table("mv_target", "my_db", columns)
        
        ddl.create_materialized_view(
            "my_view",
            target_table,
            "SELECT * FROM source_table",
            database="my_db",
            order_by="id",
            settings={"index_granularity": 8192}
        )
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "SETTINGS" in call_args
        assert "index_granularity = 8192" in call_args
    
    def test_drop_materialized_view(self, ddl, mock_client):
        """Test dropping materialized view."""
        ddl.drop_materialized_view("my_db.my_view")
        
        mock_client.execute_command.assert_called_once_with("DROP VIEW IF EXISTS my_db.my_view")
    
    def test_drop_materialized_view_without_if_exists(self, ddl, mock_client):
        """Test dropping materialized view without IF EXISTS."""
        ddl.drop_materialized_view("my_db.my_view", if_exists=False)
        
        mock_client.execute_command.assert_called_once_with("DROP VIEW my_db.my_view")
    
    def test_create_materialized_view_errors(self, ddl):
        """Test error cases for create_materialized_view."""
        columns = [Column("id", UInt64)]
        target_table = Table("mv_target", "my_db", columns)
        
        # Missing database
        with pytest.raises(ValueError, match="database parameter is required"):
            ddl.create_materialized_view(
                "my_view",
                target_table,
                "SELECT * FROM source",
                order_by="id"
            )


class TestDistributedTables:
    """Test cases for distributed tables."""
    
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
    
    def test_create_distributed_table_from_table_object(self, ddl, mock_client):
        """Test creating distributed table from Table object."""
        columns = [
            Column("id", UInt64),
            Column("name", String),
        ]
        schema = Table("dist_table", "my_db", columns)
        
        ddl.create_distributed_table(
            schema,
            cluster="my_cluster",
            local_table="my_db.local_table"
        )
        
        mock_client.execute_command.assert_called_once()
        call_args = mock_client.execute_command.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS my_db.dist_table" in call_args
        assert "ENGINE = Distributed(my_cluster, my_db.local_table" in call_args
    
    def test_create_distributed_table_with_sharding_key(self, ddl, mock_client):
        """Test creating distributed table with sharding key."""
        columns = [Column("id", UInt64), Column("name", String)]
        schema = Table("dist_table", "my_db", columns)
        
        ddl.create_distributed_table(
            schema,
            cluster="my_cluster",
            local_table="my_db.local_table",
            sharding_key="rand()"
        )
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert ", rand()" in call_args
    
    def test_create_distributed_table_from_strings(self, ddl, mock_client):
        """Test creating distributed table with string names."""
        columns = [Column("id", UInt64), Column("name", String)]
        
        ddl.create_distributed_table(
            "dist_table",
            cluster="my_cluster",
            local_table="local_table",
            columns=columns,
            database="my_db",
            local_database="my_db"
        )
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS my_db.dist_table" in call_args
        assert "ENGINE = Distributed(my_cluster, my_db.local_table" in call_args
    
    def test_create_distributed_table_without_if_not_exists(self, ddl, mock_client):
        """Test creating distributed table without IF NOT EXISTS."""
        columns = [Column("id", UInt64)]
        schema = Table("dist_table", "my_db", columns)
        
        ddl.create_distributed_table(
            schema,
            cluster="my_cluster",
            local_table="my_db.local_table",
            if_not_exists=False
        )
        
        call_args = mock_client.execute_command.call_args[0][0]
        assert "IF NOT EXISTS" not in call_args
        assert "CREATE TABLE my_db.dist_table" in call_args
    
    def test_create_distributed_table_errors(self, ddl):
        """Test error cases for create_distributed_table."""
        # Missing columns
        with pytest.raises(ValueError, match="columns parameter is required"):
            ddl.create_distributed_table(
                "dist_table",
                cluster="my_cluster",
                local_table="local_table",
                database="my_db"
            )
        
        # Missing database
        columns = [Column("id", UInt64)]
        with pytest.raises(ValueError, match="database parameter is required"):
            ddl.create_distributed_table(
                "dist_table",
                cluster="my_cluster",
                local_table="local_table",
                columns=columns
            )
        
        # Missing local_database
        with pytest.raises(ValueError, match="local_database parameter is required"):
            ddl.create_distributed_table(
                "dist_table",
                cluster="my_cluster",
                local_table="local_table",
                columns=columns,
                database="my_db"
            )

