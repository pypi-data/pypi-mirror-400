"""
Table-specific wrappers for ClickHouse tables.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from chpy.client import ClickHouseClient
from chpy.query_builder import QueryBuilder
from chpy.orm import Table
from chpy.config import (
    EXCHANGES,
    EXCHANGE_BASE_CURRENCIES,
    EXCHANGE_CURRENCIES,
    get_exchange_pairs,
    is_valid_pair,
    get_all_pairs,
)
from chpy.schema import crypto_quotes as crypto_quotes_schema


class TableWrapper:
    """
    Generic wrapper for any ClickHouse table.
    
    Provides a high-level interface to query and insert data into any table
    without writing SQL directly. Can optionally use a schema for type-safe
    column access.
    
    Example:
        >>> from chpy import ClickHouseClient, TableWrapper
        >>> from chpy.orm import Table, Column
        >>> from chpy.types import String, UInt64
        >>> 
        >>> # Create schema (optional, for type safety)
        >>> columns = [
        ...     Column("id", UInt64),
        ...     Column("name", String),
        ...     Column("value", Float64),
        ... ]
        >>> schema = Table("my_table", "my_db", columns)
        >>> 
        >>> # Create wrapper
        >>> client = ClickHouseClient(...)
        >>> table = TableWrapper(client, "my_table", "my_db", schema=schema)
        >>> 
        >>> # Query with schema columns (type-safe)
        >>> df = (table.query()
        ...     .where(schema.id > 100)
        ...     .where(schema.name == "test")
        ...     .to_dataframe())
        >>> 
        >>> # Or query without schema (using raw strings)
        >>> df = (table.query()
        ...     .where("id > 100")
        ...     .to_dataframe())
        >>> 
        >>> # Insert data
        >>> table.insert([{"id": 1, "name": "test", "value": 1.5}])
    """
    
    def __init__(
        self,
        client: ClickHouseClient,
        table_name: str,
        database: str,
        schema: Optional[Table] = None
    ):
        """
        Initialize TableWrapper for a generic table.
        
        Args:
            client: ClickHouseClient instance
            table_name: Name of the table
            database: Database name
            schema: Optional Table schema object for type-safe column access
        """
        self.client = client
        self.database = database
        self.table_name = f"{database}.{table_name}"
        self.schema = schema
        
        # Expose schema table for column access with autocomplete (if provided)
        if schema:
            self.c = schema  # Short alias for columns
            self.columns = schema  # Full access to table object
        else:
            self.c = None
            self.columns = None
    
    def _escape_string(self, value: str) -> str:
        """Escape string for SQL (simple escaping)."""
        return value.replace("'", "''")
    
    def insert(self, data: List[Dict[str, Any]]) -> None:
        """
        Insert data into the table.
        
        Args:
            data: List of dictionaries, where keys are column names
            
        Example:
            >>> table.insert([{"id": 1, "name": "test", "value": 1.5}])
        """
        self.client.insert(self.table_name, data)
    
    def query(self) -> QueryBuilder:
        """
        Start building a query with method chaining.
        
        Returns:
            QueryBuilder instance for fluent interface
            
        Example:
            >>> # With schema (type-safe)
            >>> df = (table.query()
            ...     .where(schema.id > 100)
            ...     .limit(100)
            ...     .to_dataframe())
            >>> 
            >>> # Without schema (raw SQL)
            >>> df = (table.query()
            ...     .where("id > 100")
            ...     .limit(100)
            ...     .to_dataframe())
            >>> 
            >>> # Iterate over Row objects when schema is available
            >>> for row in table.query().where(schema.id > 100):
            ...     print(row.id, row.name)  # Attribute-style access
        """
        return QueryBuilder(self.table_name, self.client, self._escape_string, schema=self.schema)


class CryptoQuotesTable(TableWrapper):
    """
    Programmatic wrapper for the crypto_quotes table.
    
    Provides a high-level interface to query crypto quotes data
    without writing SQL directly. Inherits from TableWrapper for
    generic table functionality, with additional crypto-specific methods.
    """
    
    def __init__(self, client: ClickHouseClient, database: str = "stockhouse"):
        """
        Initialize CryptoQuotesTable wrapper.
        
        Args:
            client: ClickHouseClient instance
            database: Database name (default: 'stockhouse')
        """
        # Initialize base class with crypto_quotes table and schema
        super().__init__(
            client=client,
            table_name="crypto_quotes",
            database=database,
            schema=crypto_quotes_schema
        )
    
    def get_valid_exchanges(self) -> List[str]:
        """
        Get list of valid exchange names.
        
        Returns:
            List of exchange names (uppercase)
        """
        return EXCHANGES.copy()
    
    def get_exchange_base_currencies(self, exchange: str) -> List[str]:
        """
        Get base currencies for a specific exchange.
        
        Args:
            exchange: Exchange name (case-insensitive)
            
        Returns:
            List of base currency names
        """
        return EXCHANGE_BASE_CURRENCIES.get(exchange.upper(), [])
    
    def get_exchange_currencies(self, exchange: str) -> List[str]:
        """
        Get supported currencies for a specific exchange.
        
        Args:
            exchange: Exchange name (case-insensitive)
            
        Returns:
            List of currency names
        """
        return EXCHANGE_CURRENCIES.get(exchange.upper(), [])
    
    def get_exchange_pairs(self, exchange: str) -> List[str]:
        """
        Get all valid trading pairs for an exchange.
        
        Args:
            exchange: Exchange name (case-insensitive)
            
        Returns:
            List of trading pairs in format {CURRENCY}-{BASE_CURRENCY}
        """
        return get_exchange_pairs(exchange.upper())
    
    def is_valid_pair(self, pair: str, exchange: Optional[str] = None) -> bool:
        """
        Check if a trading pair is valid.
        
        Args:
            pair: Trading pair in format {CURRENCY}-{BASE_CURRENCY}
            exchange: Optional exchange name to validate against specific exchange
            
        Returns:
            True if pair is valid
        """
        return is_valid_pair(pair, exchange.upper() if exchange else None)
    
    def get_all_valid_pairs(self) -> List[str]:
        """
        Get all valid trading pairs across all exchanges.
        
        Returns:
            List of all trading pairs
        """
        return get_all_pairs()

