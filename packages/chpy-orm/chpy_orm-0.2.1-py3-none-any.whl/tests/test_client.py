"""
Tests for chpy.client module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from chpy.client import ClickHouseClient


class TestClickHouseClient:
    """Test cases for ClickHouseClient."""
    
    def test_init_defaults(self):
        """Test client initialization with default parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            assert client.host == "localhost"
            assert client.port == 8123
            assert client.username == "default"
            assert client.password == ""
            assert client.database == "default"
            assert client._client == mock_client
            mock_get_client.assert_called_once()
    
    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient(
                host="example.com",
                port=9000,
                username="user",
                password="pass",
                database="mydb"
            )
            
            assert client.host == "example.com"
            assert client.port == 9000
            assert client.username == "user"
            assert client.password == "pass"
            assert client.database == "mydb"
    
    def test_init_connection_error(self):
        """Test that connection errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")
            
            with pytest.raises(ConnectionError, match="Failed to connect to ClickHouse"):
                ClickHouseClient()
    
    def test_execute_success(self):
        """Test successful query execution."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_result = Mock()
            mock_result.column_names = ["col1", "col2"]
            mock_result.result_rows = [[1, "a"], [2, "b"]]
            mock_client.query.return_value = mock_result
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.execute("SELECT * FROM test")
            
            assert len(result) == 2
            assert result[0] == {"col1": 1, "col2": "a"}
            assert result[1] == {"col1": 2, "col2": "b"}
            mock_client.query.assert_called_once_with("SELECT * FROM test")
    
    def test_execute_empty_result(self):
        """Test execute with empty result."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_result = Mock()
            mock_result.column_names = ["col1"]
            mock_result.result_rows = []
            mock_client.query.return_value = mock_result
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.execute("SELECT * FROM test WHERE 1=0")
            
            assert result == []
            mock_client.query.assert_called_once_with("SELECT * FROM test WHERE 1=0")
    
    def test_execute_with_parameters(self):
        """Test query execution with parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_result = Mock()
            mock_result.column_names = ["col1"]
            mock_result.result_rows = [[1]]
            mock_client.query.return_value = mock_result
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.execute("SELECT * FROM test WHERE id = {id:Int64}", {"id": 1})
            
            assert len(result) == 1
            mock_client.query.assert_called_once_with("SELECT * FROM test WHERE id = {id:Int64}", parameters={"id": 1})
    
    def test_execute_not_connected(self):
        """Test execute when not connected."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            client = ClickHouseClient()
            client._client = None
            
            with pytest.raises(ConnectionError, match="Not connected to ClickHouse"):
                client.execute("SELECT 1")
    
    def test_execute_query_error(self):
        """Test that query errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.query.side_effect = Exception("Query failed")
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            with pytest.raises(RuntimeError, match="Query execution failed"):
                client.execute("SELECT * FROM invalid")
    
    def test_query_df(self):
        """Test query_df method."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            import pandas as pd
            mock_client = Mock()
            mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
            mock_client.query_df.return_value = mock_df
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.query_df("SELECT * FROM test")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            mock_client.query_df.assert_called_once_with("SELECT * FROM test")
    
    def test_query_df_with_parameters(self):
        """Test query_df method with parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            import pandas as pd
            mock_client = Mock()
            mock_df = pd.DataFrame({"col1": [1]})
            mock_client.query_df.return_value = mock_df
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.query_df("SELECT * FROM test WHERE id = {id:Int64}", {"id": 1})
            
            assert isinstance(result, pd.DataFrame)
            mock_client.query_df.assert_called_once_with("SELECT * FROM test WHERE id = {id:Int64}", parameters={"id": 1})
    
    def test_query_df_not_connected(self):
        """Test query_df when not connected."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            client = ClickHouseClient()
            client._client = None
            
            with pytest.raises(ConnectionError, match="Not connected to ClickHouse"):
                client.query_df("SELECT 1")
    
    def test_query_df_error(self):
        """Test that query_df errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.query_df.side_effect = Exception("Query failed")
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            with pytest.raises(RuntimeError, match="Query execution failed"):
                client.query_df("SELECT * FROM invalid")
    
    def test_query_np(self):
        """Test query_np method."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            import numpy as np
            mock_client = Mock()
            mock_array = np.array([[1, 2], [3, 4]])
            mock_client.query_np.return_value = mock_array
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.query_np("SELECT * FROM test")
            
            assert isinstance(result, np.ndarray)
            assert result.shape == (2, 2)
            mock_client.query_np.assert_called_once_with("SELECT * FROM test")
    
    def test_query_np_with_parameters(self):
        """Test query_np method with parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            import numpy as np
            mock_client = Mock()
            mock_array = np.array([[1]])
            mock_client.query_np.return_value = mock_array
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.query_np("SELECT * FROM test WHERE id = {id:Int64}", {"id": 1})
            
            assert isinstance(result, np.ndarray)
            mock_client.query_np.assert_called_once_with("SELECT * FROM test WHERE id = {id:Int64}", parameters={"id": 1})
    
    def test_query_np_not_connected(self):
        """Test query_np when not connected."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            client = ClickHouseClient()
            client._client = None
            
            with pytest.raises(ConnectionError, match="Not connected to ClickHouse"):
                client.query_np("SELECT 1")
    
    def test_query_np_error(self):
        """Test that query_np errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.query_np.side_effect = Exception("Query failed")
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            with pytest.raises(RuntimeError, match="Query execution failed"):
                client.query_np("SELECT * FROM invalid")
    
    def test_query_arrow(self):
        """Test query_arrow method."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            import pyarrow as pa
            mock_client = Mock()
            mock_table = pa.table({"col1": [1, 2], "col2": ["a", "b"]})
            mock_client.query_arrow.return_value = mock_table
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.query_arrow("SELECT * FROM test")
            
            assert isinstance(result, pa.Table)
            mock_client.query_arrow.assert_called_once_with("SELECT * FROM test")
    
    def test_query_arrow_with_parameters(self):
        """Test query_arrow method with parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            import pyarrow as pa
            mock_client = Mock()
            mock_table = pa.table({"col1": [1]})
            mock_client.query_arrow.return_value = mock_table
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            result = client.query_arrow("SELECT * FROM test WHERE id = {id:Int64}", {"id": 1})
            
            assert isinstance(result, pa.Table)
            mock_client.query_arrow.assert_called_once_with("SELECT * FROM test WHERE id = {id:Int64}", parameters={"id": 1})
    
    def test_query_arrow_not_connected(self):
        """Test query_arrow when not connected."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            client = ClickHouseClient()
            client._client = None
            
            with pytest.raises(ConnectionError, match="Not connected to ClickHouse"):
                client.query_arrow("SELECT 1")
    
    def test_query_arrow_error(self):
        """Test that query_arrow errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.query_arrow.side_effect = Exception("Query failed")
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            with pytest.raises(RuntimeError, match="Query execution failed"):
                client.query_arrow("SELECT * FROM invalid")
    
    def test_execute_command(self):
        """Test execute_command method."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            client.execute_command("CREATE TABLE test (id Int64)")
            
            mock_client.command.assert_called_once_with("CREATE TABLE test (id Int64)", parameters=None)
    
    def test_execute_command_with_parameters(self):
        """Test execute_command method with parameters."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            client.execute_command("CREATE TABLE test (id Int64) ENGINE = MergeTree() ORDER BY id", {"table_name": "test"})
            
            mock_client.command.assert_called_once_with("CREATE TABLE test (id Int64) ENGINE = MergeTree() ORDER BY id", parameters={"table_name": "test"})
    
    def test_execute_command_not_connected(self):
        """Test execute_command when not connected."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            client = ClickHouseClient()
            client._client = None
            
            with pytest.raises(ConnectionError, match="Not connected to ClickHouse"):
                client.execute_command("CREATE TABLE test (id Int64)")
    
    def test_execute_command_error(self):
        """Test that command execution errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.command.side_effect = Exception("Command failed")
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            with pytest.raises(RuntimeError, match="Command execution failed"):
                client.execute_command("INVALID COMMAND")
    
    def test_insert(self):
        """Test insert method."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            data = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
            client.insert("test_table", data)
            
            mock_client.insert.assert_called_once_with("test_table", data)
    
    def test_insert_empty_list(self):
        """Test insert with empty list does nothing."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            client.insert("test_table", [])
            
            mock_client.insert.assert_not_called()
    
    def test_insert_not_connected(self):
        """Test insert when not connected."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_get_client.return_value = Mock()
            client = ClickHouseClient()
            client._client = None
            
            with pytest.raises(ConnectionError, match="Not connected to ClickHouse"):
                client.insert("test_table", [{"id": 1}])
    
    def test_insert_error(self):
        """Test that insert errors are properly raised."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_client.insert.side_effect = Exception("Insert failed")
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            
            with pytest.raises(RuntimeError, match="Insert failed"):
                client.insert("test_table", [{"id": 1}])
    
    def test_close(self):
        """Test close method."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            client.close()
            
            mock_client.close.assert_called_once()
            assert client._client is None
    
    def test_close_when_none(self):
        """Test close method when client is already None."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            client._client = None
            client.close()  # Should not raise error
            
            assert client._client is None
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            with ClickHouseClient() as client:
                assert client._client == mock_client
            
            mock_client.close.assert_called_once()
    
    def test_del_cleanup(self):
        """Test cleanup on deletion."""
        with patch('chpy.client.clickhouse_connect.get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            
            client = ClickHouseClient()
            del client
            
            mock_client.close.assert_called_once()

