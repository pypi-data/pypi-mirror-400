"""
Base ClickHouse client wrapper.
"""

from typing import Optional, List, Dict, Any
import clickhouse_connect


class ClickHouseClient:
    """
    Base client for interacting with ClickHouse database.
    
    This class provides a low-level interface to execute queries
    and manage connections to ClickHouse.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8123,
        username: str = "default",
        password: str = "",
        database: str = "default",
        **kwargs
    ):
        """
        Initialize ClickHouse client.
        
        Args:
            host: ClickHouse server hostname
            port: ClickHouse server port (default: 8123 for HTTP, 9000 for native)
            username: Username for authentication
            password: Password for authentication
            database: Default database name
            **kwargs: Additional connection parameters
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self._client = None
        self._connect(**kwargs)
    
    def _connect(self, **kwargs):
        """Establish connection to ClickHouse."""
        try:
            self._client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database,
                **kwargs
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ClickHouse: {e}")
    
    def execute(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as a list of dictionaries.
        
        Args:
            query: SQL query string
            parameters: Optional query parameters for parameterized queries
            
        Returns:
            List of dictionaries, where each dictionary represents a row
        """
        if not self._client:
            raise ConnectionError("Not connected to ClickHouse")
        
        try:
            if parameters:
                result = self._client.query(query, parameters=parameters)
            else:
                result = self._client.query(query)
            # Convert to list of dictionaries
            columns = result.column_names
            rows = []
            for row in result.result_rows:
                rows.append(dict(zip(columns, row)))
            return rows
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def query_df(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Execute a SELECT query and return results as a pandas DataFrame.
        Uses ClickHouse Connect's native query_df method for better performance.
        
        Args:
            query: SQL query string
            parameters: Optional query parameters for parameterized queries
            
        Returns:
            pandas DataFrame
        """
        if not self._client:
            raise ConnectionError("Not connected to ClickHouse")
        
        try:
            if parameters:
                return self._client.query_df(query, parameters=parameters)
            else:
                return self._client.query_df(query)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def query_np(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Execute a SELECT query and return results as a numpy array.
        Uses ClickHouse Connect's native query_np method for better performance.
        
        Args:
            query: SQL query string
            parameters: Optional query parameters for parameterized queries
            
        Returns:
            numpy array
        """
        if not self._client:
            raise ConnectionError("Not connected to ClickHouse")
        
        try:
            if parameters:
                return self._client.query_np(query, parameters=parameters)
            else:
                return self._client.query_np(query)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def query_arrow(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Execute a SELECT query and return results as a PyArrow Table.
        Uses ClickHouse Connect's native query_arrow method for better performance.
        
        Args:
            query: SQL query string
            parameters: Optional query parameters for parameterized queries
            
        Returns:
            PyArrow Table
        """
        if not self._client:
            raise ConnectionError("Not connected to ClickHouse")
        
        try:
            if parameters:
                return self._client.query_arrow(query, parameters=parameters)
            else:
                return self._client.query_arrow(query)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")
    
    def execute_command(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Execute a non-SELECT command (INSERT, CREATE, etc.).
        
        Args:
            query: SQL command string
            parameters: Optional query parameters
        """
        if not self._client:
            raise ConnectionError("Not connected to ClickHouse")
        
        try:
            self._client.command(query, parameters=parameters)
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}")
    
    def insert(self, table: str, data: List[Dict[str, Any]]) -> None:
        """
        Insert data into a table.
        
        Args:
            table: Table name (can include database, e.g., 'database.table')
            data: List of dictionaries, where keys are column names
        """
        if not data:
            return
        
        if not self._client:
            raise ConnectionError("Not connected to ClickHouse")
        
        try:
            self._client.insert(table, data)
        except Exception as e:
            raise RuntimeError(f"Insert failed: {e}")
    
    def close(self):
        """Close the connection."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()

