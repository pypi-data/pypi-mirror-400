"""
Table-specific wrappers for ClickHouse tables.
"""

from typing import Optional, List, Dict, Any, Union, ClassVar
from datetime import datetime, date
from chpy.client import ClickHouseClient
from chpy.query_builder import QueryBuilder
from chpy.orm import Table as BaseTable, Column
from chpy.types import String, Float64, UInt64, Array, LowCardinality
from chpy.config import (
    EXCHANGES,
    EXCHANGE_BASE_CURRENCIES,
    EXCHANGE_CURRENCIES,
    get_exchange_pairs,
    is_valid_pair,
    get_all_pairs,
)


class TableMeta(type):
    """
    Metaclass for Table that collects Column class attributes.
    Similar to Django's ModelBase metaclass.
    """
    def __new__(mcs, name, bases, namespace, **kwargs):
        # Collect Column instances from class attributes
        columns = []
        column_attrs = {}
        
        # Process attributes in order (preserve definition order)
        for key, value in namespace.items():
            if isinstance(value, Column):
                columns.append(value)
                column_attrs[key] = value
        
        # Store columns in class for later use
        namespace['_meta_columns'] = columns
        namespace['_meta_column_attrs'] = column_attrs
        
        # Set __annotations__ at class level for VS Code static analysis
        # Sort columns alphabetically to ensure consistent ordering
        # This helps VS Code/Pylance see columns for autocomplete
        if column_attrs:
            if '__annotations__' not in namespace:
                namespace['__annotations__'] = {}
            # Add column annotations in alphabetical order
            sorted_column_names = sorted(column_attrs.keys())
            for col_name in sorted_column_names:
                namespace['__annotations__'][col_name] = Column
        
        return super().__new__(mcs, name, bases, namespace)


class Table(BaseTable, metaclass=TableMeta):
    """
    Unified table class that combines schema definition and wrapper functionality.
    
    This class serves dual purpose:
    1. As a schema (defines columns) - provides column access with autocomplete
    2. As a wrapper (provides query/insert) - provides database operations
    
    Columns are defined as class attributes (Django-style).
    
    Example:
        >>> from chpy import ClickHouseClient
        >>> from chpy.tables import Table
        >>> from chpy.orm import Column
        >>> from chpy.types import String, UInt64
        >>> 
        >>> class MyTable(Table):
        ...     id = Column("id", UInt64)
        ...     name = Column("name", String)
        ...     
        >>> client = ClickHouseClient(...)
        >>> table = MyTable(client, "my_table", "my_db")
        >>> 
        >>> # Use as schema (direct column access)
        >>> table.id  # Column object with autocomplete
        >>> table.name  # Column object with autocomplete
        >>> 
        >>> # Use as wrapper (query/insert)
        >>> df = table.query().where(table.id > 100).to_dataframe()
        >>> table.insert([{"id": 1, "name": "test"}])
    """
    
    def __init__(
        self,
        client: ClickHouseClient,
        table_name: str,
        database: str,
        columns: Optional[List[Column]] = None
    ):
        """
        Initialize unified Table (schema + wrapper).
        
        Args:
            client: ClickHouseClient instance
            table_name: Name of the table
            database: Database name
            columns: Optional list of Column objects defining the schema.
                    If None, will use class-level Column attributes (Django-style).
        """
        # Initialize wrapper functionality first
        self._client = client
        self._database = database
        self._qualified_table_name = f"{database}.{table_name}"
        
        # Determine columns to use
        if columns is not None:
            # Explicit columns provided
            cols_to_use = columns
        elif hasattr(self.__class__, '_meta_columns') and self.__class__._meta_columns:
            # Use class-level Column attributes (Django-style)
            cols_to_use = self.__class__._meta_columns
        else:
            raise ValueError(
                f"Table '{table_name}' must define columns either as class attributes "
                f"(Django-style) or pass columns parameter to __init__"
            )
        
        # Initialize BaseTable with columns
        BaseTable.__init__(self, table_name, database, cols_to_use)
        self._schema = self  # Table is its own schema
    
    def _escape_string(self, value: str) -> str:
        """Escape string for SQL (simple escaping)."""
        return value.replace("'", "''")
    
    @property
    def client(self) -> ClickHouseClient:
        """Get the ClickHouse client."""
        return self._client
    
    @property
    def database(self) -> str:
        """Get the database name."""
        return self._database
    
    @property
    def table_name(self) -> str:
        """Get the full table name (database.table)."""
        return self._qualified_table_name
    
    @property
    def schema(self) -> 'Table':
        """Get the schema (self, since Table is its own schema)."""
        return self._schema
    
    def insert(self, data: List[Dict[str, Any]]) -> None:
        """
        Insert data into the table.
        
        Args:
            data: List of dictionaries, where keys are column names
            
        Example:
            >>> table.insert([{"id": 1, "name": "test", "value": 1.5}])
        """
        self._client.insert(self._qualified_table_name, data)
    
    def query(self) -> QueryBuilder:
        """
        Start building a query with method chaining.
        
        Returns:
            QueryBuilder instance for fluent interface
            
        Example:
            >>> # With schema (type-safe)
            >>> df = (table.query()
            ...     .where(table.id > 100)
            ...     .limit(100)
            ...     .to_dataframe())
            >>> 
            >>> # Without schema (raw SQL) - still works
            >>> df = (table.query()
            ...     .where("id > 100")
            ...     .limit(100)
            ...     .to_dataframe())
            >>> 
            >>> # Iterate over Row objects when schema is available
            >>> for row in table.query().where(table.id > 100):
            ...     print(row.id, row.name)  # Attribute-style access
        """
        return QueryBuilder(self._qualified_table_name, self._client, self._escape_string, schema=self._schema)


# Alias for Table
TableWrapper = Table


class CryptoQuotesTable(Table):
    """
    Programmatic wrapper and schema for the crypto_quotes table.
    
    This class inherits from the unified Table class, which combines
    schema definition and wrapper functionality. Columns are defined
    as class attributes (Django-style). Use table.pair, table.best_bid_price, etc. directly.
    
    Example:
        >>> from chpy import CryptoQuotesTable, ClickHouseClient
        >>> client = ClickHouseClient(...)
        >>> table = CryptoQuotesTable(client)
        >>> 
        >>> # Use as schema (direct column access)
        >>> table.pair  # Column object with autocomplete
        >>> table.best_bid_price  # Column object with autocomplete
        >>> 
        >>> # Use as wrapper (query/insert)
        >>> df = table.query().where(table.pair == "BTC-USDT").to_dataframe()
        >>> table.insert([{"pair": "BTC-USDT", "best_bid_price": 50000.0}])
    """
    
    # Define columns as class attributes (Django-style)
    pair = Column("pair", String)
    best_bid_price = Column("best_bid_price", Float64)
    best_bid_size = Column("best_bid_size", Float64)
    best_ask_price = Column("best_ask_price", Float64)
    best_ask_size = Column("best_ask_size", Float64)
    bid_prices = Column("bid_prices", Array(Float64))
    bid_sizes = Column("bid_sizes", Array(Float64))
    ask_prices = Column("ask_prices", Array(Float64))
    ask_sizes = Column("ask_sizes", Array(Float64))
    timestamp_ms = Column("timestamp_ms", UInt64)
    exchange = Column("exchange", LowCardinality(String))
    sequence_number = Column("sequence_number", UInt64)
    inserted_at = Column("inserted_at", UInt64)
    
    def __init__(self, client: ClickHouseClient, database: str = "stockhouse"):
        """
        Initialize CryptoQuotesTable as both schema and wrapper.
        
        Args:
            client: ClickHouseClient instance
            database: Database name (default: 'stockhouse')
        """
        # Initialize unified Table class (schema + wrapper)
        # Columns are automatically collected from class attributes
        super().__init__(
            client=client,
            table_name="crypto_quotes",
            database=database
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


# Export columns list (for DDL and other use cases)
crypto_quotes_columns = CryptoQuotesTable._meta_columns

# Create schema-only instance for column access without client
# This is a convenience export for accessing columns directly
from unittest.mock import MagicMock
_crypto_quotes_schema_client = MagicMock()
crypto_quotes = CryptoQuotesTable(_crypto_quotes_schema_client)

