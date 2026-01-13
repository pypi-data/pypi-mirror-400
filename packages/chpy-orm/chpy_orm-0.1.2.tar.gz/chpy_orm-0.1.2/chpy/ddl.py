"""
DDL (Data Definition Language) operations for ClickHouse.
Provides high-level methods for creating, altering, and dropping tables.
"""

from typing import Optional, List, Dict, Any, Union, Literal
from chpy.client import ClickHouseClient
from chpy.orm import Table, Column


class DDL:
    """
    DDL operations for ClickHouse tables.
    
    Provides high-level methods for table management without writing raw SQL.
    
    Example:
        >>> from chpy import ClickHouseClient
        >>> from chpy.ddl import DDL
        >>> from chpy.orm import Table, Column
        >>> from chpy.types import String, UInt64, Float64
        >>> 
        >>> client = ClickHouseClient(...)
        >>> ddl = DDL(client)
        >>> 
        >>> # Create table from schema
        >>> columns = [
        ...     Column("id", UInt64),
        ...     Column("name", String),
        ...     Column("value", Float64),
        ... ]
        >>> schema = Table("my_table", "my_db", columns)
        >>> ddl.create_table(schema, engine="MergeTree", order_by="id")
        >>> 
        >>> # Alter table
        >>> ddl.add_column("my_db.my_table", Column("new_col", String))
        >>> ddl.drop_column("my_db.my_table", "old_col")
        >>> 
        >>> # Drop table
        >>> ddl.drop_table("my_db.my_table")
    """
    
    def __init__(self, client: ClickHouseClient):
        """
        Initialize DDL operations.
        
        Args:
            client: ClickHouseClient instance
        """
        self.client = client
    
    def create_table(
        self,
        table: Union[Table, str],
        columns: Optional[List[Column]] = None,
        database: Optional[str] = None,
        engine: str = "MergeTree",
        order_by: Optional[Union[str, List[str]]] = None,
        partition_by: Optional[Union[str, List[str]]] = None,
        primary_key: Optional[Union[str, List[str]]] = None,
        settings: Optional[Dict[str, Any]] = None,
        if_not_exists: bool = True
    ) -> None:
        """
        Create a table in ClickHouse.
        
        Args:
            table: Table object or table name (if string, requires columns parameter)
            columns: List of Column objects (required if table is a string)
            database: Database name (required if table is a string, otherwise uses table.database)
            engine: Table engine (default: "MergeTree")
            order_by: Column(s) to order by (required for MergeTree)
            partition_by: Column(s) to partition by
            primary_key: Primary key column(s)
            settings: Additional table settings as dictionary
            if_not_exists: If True, adds IF NOT EXISTS clause (default: True)
            
        Example:
            >>> from chpy.orm import Table, Column
            >>> columns = [Column("id", UInt64), Column("name", String)]
            >>> schema = Table("users", "my_db", columns)
            >>> ddl.create_table(schema, order_by="id")
            >>> 
            >>> # Or with string table name
            >>> ddl.create_table("users", columns=columns, database="my_db", order_by="id")
        """
        # Determine table name and columns
        if isinstance(table, Table):
            # Use full_name and split to avoid issues if a column is named "name"
            full_name = table.full_name
            if '.' in full_name:
                database, table_name = full_name.split('.', 1)
            else:
                database = table.database
                table_name = full_name
            columns = table.get_all_columns()
        elif isinstance(table, str):
            if columns is None:
                raise ValueError("columns parameter is required when table is a string")
            if database is None:
                raise ValueError("database parameter is required when table is a string")
            table_name = table
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        # Build column definitions
        column_defs = []
        for col in columns:
            column_defs.append(f"{col.name} {col.type}")
        
        # Build CREATE TABLE statement
        if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
        full_table_name = f"{database}.{table_name}"
        if if_not_exists_clause:
            query = f"CREATE TABLE {if_not_exists_clause} {full_table_name} ({', '.join(column_defs)})"
        else:
            query = f"CREATE TABLE {full_table_name} ({', '.join(column_defs)})"
        
        # Add engine
        query += f" ENGINE = {engine}"
        
        # Add ORDER BY (required for MergeTree)
        if order_by:
            if isinstance(order_by, list):
                order_by_str = ', '.join(order_by)
            else:
                order_by_str = str(order_by)
            query += f" ORDER BY {order_by_str}"
        
        # Add PARTITION BY
        if partition_by:
            if isinstance(partition_by, list):
                partition_by_str = ', '.join(partition_by)
            else:
                partition_by_str = str(partition_by)
            query += f" PARTITION BY {partition_by_str}"
        
        # Add PRIMARY KEY
        if primary_key:
            if isinstance(primary_key, list):
                primary_key_str = ', '.join(primary_key)
            else:
                primary_key_str = str(primary_key)
            query += f" PRIMARY KEY ({primary_key_str})"
        
        # Add settings
        if settings:
            settings_list = [f"{k} = {v}" for k, v in settings.items()]
            query += f" SETTINGS {', '.join(settings_list)}"
        
        self.client.execute_command(query)
    
    def drop_table(
        self,
        table: Union[Table, str],
        database: Optional[str] = None,
        if_exists: bool = True
    ) -> None:
        """
        Drop a table.
        
        Args:
            table: Table object or table name (database.table or just table)
            database: Database name (required if table is a string without database prefix)
            if_exists: If True, adds IF EXISTS clause (default: True)
            
        Example:
            >>> ddl.drop_table("my_db.my_table")
            >>> ddl.drop_table("my_table", database="my_db")
            >>> ddl.drop_table(schema_table)
        """
        # Determine table name
        if isinstance(table, Table):
            full_table_name = table.full_name
        elif isinstance(table, str):
            if '.' in table:
                full_table_name = table
            elif database:
                full_table_name = f"{database}.{table}"
            else:
                raise ValueError("database parameter is required when table name doesn't include database")
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        if_exists_clause = "IF EXISTS" if if_exists else ""
        if if_exists_clause:
            query = f"DROP TABLE {if_exists_clause} {full_table_name}"
        else:
            query = f"DROP TABLE {full_table_name}"
        
        self.client.execute_command(query)
    
    def add_column(
        self,
        table: Union[Table, str],
        column: Column,
        database: Optional[str] = None,
        after: Optional[str] = None,
        if_not_exists: bool = True
    ) -> None:
        """
        Add a column to an existing table.
        
        Args:
            table: Table object or table name (database.table or just table)
            column: Column object to add
            database: Database name (required if table is a string without database prefix)
            after: Column name to add the new column after (optional)
            if_not_exists: If True, adds IF NOT EXISTS clause (default: True)
            
        Example:
            >>> ddl.add_column("my_db.my_table", Column("new_col", String))
            >>> ddl.add_column("my_table", Column("new_col", String), database="my_db", after="id")
        """
        # Determine table name
        if isinstance(table, Table):
            full_table_name = table.full_name
        elif isinstance(table, str):
            if '.' in table:
                full_table_name = table
            elif database:
                full_table_name = f"{database}.{table}"
            else:
                raise ValueError("database parameter is required when table name doesn't include database")
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
        after_clause = f" AFTER {after}" if after else ""
        query = f"ALTER TABLE {full_table_name} ADD COLUMN {if_not_exists_clause} {column.name} {column.type}{after_clause}"
        
        self.client.execute_command(query)
    
    def drop_column(
        self,
        table: Union[Table, str],
        column_name: str,
        database: Optional[str] = None,
        if_exists: bool = True
    ) -> None:
        """
        Drop a column from an existing table.
        
        Args:
            table: Table object or table name (database.table or just table)
            column_name: Name of the column to drop
            database: Database name (required if table is a string without database prefix)
            if_exists: If True, adds IF EXISTS clause (default: True)
            
        Example:
            >>> ddl.drop_column("my_db.my_table", "old_col")
        """
        # Determine table name
        if isinstance(table, Table):
            full_table_name = table.full_name
        elif isinstance(table, str):
            if '.' in table:
                full_table_name = table
            elif database:
                full_table_name = f"{database}.{table}"
            else:
                raise ValueError("database parameter is required when table name doesn't include database")
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        if_exists_clause = "IF EXISTS" if if_exists else ""
        if if_exists_clause:
            query = f"ALTER TABLE {full_table_name} DROP COLUMN {if_exists_clause} {column_name}"
        else:
            query = f"ALTER TABLE {full_table_name} DROP COLUMN {column_name}"
        
        self.client.execute_command(query)
    
    def modify_column(
        self,
        table: Union[Table, str],
        column: Column,
        database: Optional[str] = None
    ) -> None:
        """
        Modify a column in an existing table.
        
        Args:
            table: Table object or table name (database.table or just table)
            column: Column object with updated type
            database: Database name (required if table is a string without database prefix)
            
        Example:
            >>> ddl.modify_column("my_db.my_table", Column("name", "FixedString(100)"))
        """
        # Determine table name
        if isinstance(table, Table):
            full_table_name = table.full_name
        elif isinstance(table, str):
            if '.' in table:
                full_table_name = table
            elif database:
                full_table_name = f"{database}.{table}"
            else:
                raise ValueError("database parameter is required when table name doesn't include database")
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        query = f"ALTER TABLE {full_table_name} MODIFY COLUMN {column.name} {column.type}"
        
        self.client.execute_command(query)
    
    def rename_table(
        self,
        old_table: Union[Table, str],
        new_name: str,
        database: Optional[str] = None
    ) -> None:
        """
        Rename a table.
        
        Args:
            old_table: Table object or current table name (database.table or just table)
            new_name: New table name
            database: Database name (required if old_table is a string without database prefix)
            
        Example:
            >>> ddl.rename_table("my_db.old_table", "new_table")
        """
        # Determine table name
        if isinstance(old_table, Table):
            full_table_name = old_table.full_name
            database = old_table.database
        elif isinstance(old_table, str):
            if '.' in old_table:
                full_table_name = old_table
                database = old_table.split('.')[0]
            elif database:
                full_table_name = f"{database}.{old_table}"
            else:
                raise ValueError("database parameter is required when table name doesn't include database")
        else:
            raise TypeError(f"Unsupported table type: {type(old_table)}. Expected Table or str.")
        
        new_full_name = f"{database}.{new_name}"
        query = f"RENAME TABLE {full_table_name} TO {new_full_name}"
        
        self.client.execute_command(query)
    
    def create_database(
        self,
        database: str,
        if_not_exists: bool = True,
        engine: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a database.
        
        Args:
            database: Database name
            if_not_exists: If True, adds IF NOT EXISTS clause (default: True)
            engine: Database engine (optional)
            settings: Additional database settings as dictionary
            
        Example:
            >>> ddl.create_database("my_database")
            >>> ddl.create_database("my_database", engine="Atomic")
        """
        if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
        if if_not_exists_clause:
            query = f"CREATE DATABASE {if_not_exists_clause} {database}"
        else:
            query = f"CREATE DATABASE {database}"
        
        if engine:
            query += f" ENGINE = {engine}"
        
        if settings:
            settings_list = [f"{k} = {v}" for k, v in settings.items()]
            query += f" SETTINGS {', '.join(settings_list)}"
        
        self.client.execute_command(query)
    
    def drop_database(
        self,
        database: str,
        if_exists: bool = True
    ) -> None:
        """
        Drop a database.
        
        Args:
            database: Database name
            if_exists: If True, adds IF EXISTS clause (default: True)
            
        Example:
            >>> ddl.drop_database("my_database")
        """
        if_exists_clause = "IF EXISTS" if if_exists else ""
        if if_exists_clause:
            query = f"DROP DATABASE {if_exists_clause} {database}"
        else:
            query = f"DROP DATABASE {database}"
        
        self.client.execute_command(query)
    
    def create_materialized_view(
        self,
        view: Union[Table, str],
        to_table: Union[Table, str],
        select_query: str,
        columns: Optional[List[Column]] = None,
        database: Optional[str] = None,
        to_database: Optional[str] = None,
        engine: str = "MergeTree",
        order_by: Optional[Union[str, List[str]]] = None,
        partition_by: Optional[Union[str, List[str]]] = None,
        primary_key: Optional[Union[str, List[str]]] = None,
        settings: Optional[Dict[str, Any]] = None,
        if_not_exists: bool = True,
        populate: bool = False
    ) -> None:
        """
        Create a materialized view in ClickHouse.
        
        Args:
            view: View name (Table object or string)
            to_table: Target table name where data will be stored (Table object or string)
            select_query: SELECT query that defines the view (as SQL string)
            columns: List of Column objects for the target table (required if to_table is a string)
            database: Database name for view (required if view is a string)
            to_database: Database name for target table (required if to_table is a string)
            engine: Table engine for target table (default: "MergeTree")
            order_by: Column(s) to order by for target table (required for MergeTree)
            partition_by: Column(s) to partition by for target table
            primary_key: Primary key column(s) for target table
            settings: Additional table settings as dictionary
            if_not_exists: If True, adds IF NOT EXISTS clause (default: True)
            populate: If True, populates the view with existing data (default: False)
            
        Example:
            >>> from chpy.orm import Table, Column
            >>> columns = [Column("pair", String), Column("avg_price", Float64)]
            >>> target_table = Table("mv_target", "my_db", columns)
            >>> ddl.create_materialized_view(
            ...     "my_view",
            ...     target_table,
            ...     "SELECT pair, avg(price) as avg_price FROM source_table GROUP BY pair",
            ...     database="my_db",
            ...     order_by="pair"
            ... )
        """
        # Determine view name
        if isinstance(view, Table):
            full_view_name = view.full_name
            if '.' in full_view_name:
                database, view_name = full_view_name.split('.', 1)
            else:
                database = view.database
                view_name = full_view_name
        elif isinstance(view, str):
            if '.' in view:
                full_view_name = view
                database, view_name = full_view_name.split('.', 1)
            elif database:
                full_view_name = f"{database}.{view}"
                view_name = view
            else:
                raise ValueError("database parameter is required when view name doesn't include database")
        else:
            raise TypeError(f"Unsupported view type: {type(view)}. Expected Table or str.")
        
        # Determine target table name
        if isinstance(to_table, Table):
            full_to_name = to_table.full_name
            if '.' in full_to_name:
                to_database, to_table_name = full_to_name.split('.', 1)
            else:
                to_database = to_table.database
                to_table_name = full_to_name
            columns = to_table.get_all_columns()
        elif isinstance(to_table, str):
            if '.' in to_table:
                full_to_name = to_table
                to_database, to_table_name = full_to_name.split('.', 1)
            elif to_database:
                full_to_name = f"{to_database}.{to_table}"
                to_table_name = to_table
            else:
                raise ValueError("to_database parameter is required when to_table name doesn't include database")
        else:
            raise TypeError(f"Unsupported to_table type: {type(to_table)}. Expected Table or str.")
        
        if columns is None:
            raise ValueError("columns parameter is required when to_table is a string")
        
        # Build column definitions for target table
        column_defs = []
        for col in columns:
            column_defs.append(f"{col.name} {col.type}")
        
        # Build target table definition
        target_table_def = f"{to_database}.{to_table_name} ({', '.join(column_defs)})"
        target_table_def += f" ENGINE = {engine}"
        
        if order_by:
            if isinstance(order_by, list):
                order_by_str = ', '.join(order_by)
            else:
                order_by_str = str(order_by)
            target_table_def += f" ORDER BY {order_by_str}"
        
        if partition_by:
            if isinstance(partition_by, list):
                partition_by_str = ', '.join(partition_by)
            else:
                partition_by_str = str(partition_by)
            target_table_def += f" PARTITION BY {partition_by_str}"
        
        if primary_key:
            if isinstance(primary_key, list):
                primary_key_str = ', '.join(primary_key)
            else:
                primary_key_str = str(primary_key)
            target_table_def += f" PRIMARY KEY ({primary_key_str})"
        
        if settings:
            settings_list = [f"{k} = {v}" for k, v in settings.items()]
            target_table_def += f" SETTINGS {', '.join(settings_list)}"
        
        # Build CREATE MATERIALIZED VIEW statement
        if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
        populate_clause = "POPULATE" if populate else ""
        
        if if_not_exists_clause:
            query = f"CREATE MATERIALIZED VIEW {if_not_exists_clause} {full_view_name} TO {target_table_def} AS {select_query}"
        else:
            query = f"CREATE MATERIALIZED VIEW {full_view_name} TO {target_table_def} AS {select_query}"
        
        if populate_clause:
            query = query.replace("CREATE MATERIALIZED VIEW", f"CREATE MATERIALIZED VIEW {populate_clause}")
        
        self.client.execute_command(query)
    
    def drop_materialized_view(
        self,
        view: Union[Table, str],
        database: Optional[str] = None,
        if_exists: bool = True
    ) -> None:
        """
        Drop a materialized view.
        
        Args:
            view: View object or view name (database.view or just view)
            database: Database name (required if view is a string without database prefix)
            if_exists: If True, adds IF EXISTS clause (default: True)
            
        Example:
            >>> ddl.drop_materialized_view("my_db.my_view")
            >>> ddl.drop_materialized_view("my_view", database="my_db")
        """
        # Determine view name
        if isinstance(view, Table):
            full_view_name = view.full_name
        elif isinstance(view, str):
            if '.' in view:
                full_view_name = view
            elif database:
                full_view_name = f"{database}.{view}"
            else:
                raise ValueError("database parameter is required when view name doesn't include database")
        else:
            raise TypeError(f"Unsupported view type: {type(view)}. Expected Table or str.")
        
        if_exists_clause = "IF EXISTS" if if_exists else ""
        if if_exists_clause:
            query = f"DROP VIEW {if_exists_clause} {full_view_name}"
        else:
            query = f"DROP VIEW {full_view_name}"
        
        self.client.execute_command(query)
    
    def create_distributed_table(
        self,
        table: Union[Table, str],
        cluster: str,
        local_table: Union[Table, str],
        columns: Optional[List[Column]] = None,
        database: Optional[str] = None,
        local_database: Optional[str] = None,
        sharding_key: Optional[str] = None,
        if_not_exists: bool = True
    ) -> None:
        """
        Create a distributed table in ClickHouse.
        
        Args:
            table: Distributed table name (Table object or string)
            cluster: ClickHouse cluster name
            local_table: Local table name that the distributed table will query (Table object or string)
            columns: List of Column objects (required if table is a string)
            database: Database name for distributed table (required if table is a string)
            local_database: Database name for local table (required if local_table is a string)
            sharding_key: Optional sharding key expression (e.g., "rand()" or column name)
            if_not_exists: If True, adds IF NOT EXISTS clause (default: True)
            
        Example:
            >>> from chpy.orm import Table, Column
            >>> columns = [Column("id", UInt64), Column("name", String)]
            >>> schema = Table("dist_table", "my_db", columns)
            >>> ddl.create_distributed_table(
            ...     schema,
            ...     cluster="my_cluster",
            ...     local_table="my_db.local_table",
            ...     sharding_key="rand()"
            ... )
        """
        # Determine distributed table name
        if isinstance(table, Table):
            full_name = table.full_name
            if '.' in full_name:
                database, table_name = full_name.split('.', 1)
            else:
                database = table.database
                table_name = full_name
            columns = table.get_all_columns()
        elif isinstance(table, str):
            if columns is None:
                raise ValueError("columns parameter is required when table is a string")
            if database is None:
                raise ValueError("database parameter is required when table is a string")
            table_name = table
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        # Determine local table name
        if isinstance(local_table, Table):
            local_full_name = local_table.full_name
        elif isinstance(local_table, str):
            if '.' in local_table:
                local_full_name = local_table
            elif local_database:
                local_full_name = f"{local_database}.{local_table}"
            else:
                raise ValueError("local_database parameter is required when local_table name doesn't include database")
        else:
            raise TypeError(f"Unsupported local_table type: {type(local_table)}. Expected Table or str.")
        
        # Build column definitions
        column_defs = []
        for col in columns:
            column_defs.append(f"{col.name} {col.type}")
        
        # Build CREATE TABLE statement with Distributed engine
        if_not_exists_clause = "IF NOT EXISTS" if if_not_exists else ""
        full_table_name = f"{database}.{table_name}"
        
        if if_not_exists_clause:
            query = f"CREATE TABLE {if_not_exists_clause} {full_table_name} ({', '.join(column_defs)}) ENGINE = Distributed({cluster}, {local_full_name}"
        else:
            query = f"CREATE TABLE {full_table_name} ({', '.join(column_defs)}) ENGINE = Distributed({cluster}, {local_full_name}"
        
        if sharding_key:
            query += f", {sharding_key}"
        
        query += ")"
        
        self.client.execute_command(query)

