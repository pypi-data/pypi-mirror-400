"""
Query builder with fluent interface for method chaining.
"""

from typing import Optional, List, Dict, Any, Union, Literal, Tuple
from datetime import datetime
import json
from chpy.orm import Column, ColumnExpression, CombinedExpression, Table, Subquery, SubqueryExpression, Row
from chpy.functions.base import Function, AggregateFunction


class QueryBuilder:
    """
    Fluent query builder that supports method chaining and multiple output formats.
    
    Example:
        >>> builder = QueryBuilder(table, client)
        >>> result = (builder
        ...     .filter(pair="BTC/USD")
        ...     .filter(start_time=datetime(2024, 1, 1))
        ...     .limit(100)
        ...     .to_dataframe())
    """
    
    def __init__(self, table_name: str, client, escape_string_func, schema: Optional[Table] = None):
        """
        Initialize query builder.
        
        Args:
            table_name: Full table name (database.table)
            client: ClickHouseClient instance
            escape_string_func: Function to escape strings for SQL
            schema: Optional Table schema object for returning Row objects instead of dicts
        """
        self.table_name = table_name
        self.client = client
        self._escape_string = escape_string_func
        self.schema = schema
        
        # Query building state
        self._columns: Optional[List[str]] = None
        self._where_conditions: List[str] = []
        self._order_by: Optional[str] = None
        self._order_desc: bool = True
        self._limit: Optional[int] = None
        self._group_by: Optional[List[str]] = None
        self._having: Optional[str] = None
        self._joins: List[Dict[str, Any]] = []  # List of join specifications
        self._from_subquery: Optional[Subquery] = None  # Subquery in FROM clause (derived table)
        self._from_alias: Optional[str] = None  # Alias for FROM subquery
    
    def select(self, *columns: Union[Column, Function, AggregateFunction, Subquery, str]) -> 'QueryBuilder':
        """
        Specify columns to select using Column objects, Function objects, AggregateFunction objects, Subquery objects, or raw strings.
        
        Args:
            *columns: Column objects, Function objects, AggregateFunction objects, Subquery objects, or raw SQL strings to select.
                     If none provided, selects all.
            
        Returns:
            Self for method chaining
            
        Example:
            >>> from chpy.functions import avg, count, length, toYear
            >>> builder.select(crypto_quotes.pair, avg(crypto_quotes.best_bid_price).alias("avg_bid"))
            >>> builder.select(length(crypto_quotes.pair).alias("pair_length"))
            >>> builder.select(crypto_quotes.pair, "avg(best_bid_price) as avg_bid")  # Raw string still works
            >>> builder.select(Subquery(other_builder).alias("subquery_result"))  # Scalar subquery
        """
        if columns:
            # Convert to SQL strings
            column_strings = []
            for col in columns:
                if isinstance(col, Column):
                    # Use table-qualified name if table is available, or qualify with base table if JOINs exist
                    if col.table:
                        column_strings.append(f"{col.table._qualified_name}.{col.name}")
                    elif self._joins:
                        # Auto-qualify base table columns when JOINs are present
                        column_strings.append(f"{self.table_name}.{col.name}")
                    else:
                        column_strings.append(col.name)
                elif isinstance(col, (Function, AggregateFunction)):
                    column_strings.append(col.to_sql())
                elif isinstance(col, Subquery):
                    # Subquery in SELECT (scalar subquery)
                    column_strings.append(col.to_sql())
                elif isinstance(col, str):
                    # Raw string support
                    column_strings.append(col)
                else:
                    raise TypeError(f"Unsupported column type: {type(col)}. "
                                  f"Expected Column, Function, AggregateFunction, Subquery, or str.")
            self._columns = column_strings
        else:
            self._columns = None
        return self
    
    
    def where(self, condition: Union[ColumnExpression, CombinedExpression, SubqueryExpression, str]) -> 'QueryBuilder':
        """
        Add a WHERE condition using column expressions, subqueries, or raw SQL.
        
        Args:
            condition: ColumnExpression, CombinedExpression, SubqueryExpression, or raw SQL string
            
        Returns:
            Self for method chaining
            
        Example:
            >>> builder.where(crypto_quotes.pair == "BTC-USDT")
            >>> builder.where(crypto_quotes.best_bid_price > 50000)
            >>> builder.where((crypto_quotes.pair == "BTC-USDT") & (crypto_quotes.exchange == "BINANCE"))
            >>> builder.where(Subquery.exists(other_builder))
            >>> builder.where(crypto_quotes.pair.in_(Subquery(other_builder)))
        """
        # Pass base table name to auto-qualify columns without table references when JOINs exist
        base_table = self.table_name if self._joins else None
        
        if isinstance(condition, str):
            # Raw SQL string
            self._where_conditions.append(f"({condition})")
        elif isinstance(condition, (ColumnExpression, CombinedExpression, SubqueryExpression)):
            # Expression objects
            self._where_conditions.append(f"({condition.to_sql(self._escape_string, base_table_name=base_table)})")
        else:
            raise TypeError(f"Unsupported condition type: {type(condition)}. "
                          f"Expected ColumnExpression, CombinedExpression, SubqueryExpression, or str.")
        return self
    
    def order_by(self, column: Union[Column, str], desc: bool = True) -> 'QueryBuilder':
        """
        Specify ordering using Column object or string (for aliases).
        
        Args:
            column: Column object or string (alias name) to order by
            desc: If True, order descending (default: True)
            
        Returns:
            Self for method chaining
            
        Example:
            >>> builder.order_by(crypto_quotes.timestamp_ms, desc=True)
            >>> builder.order_by("avg_bid", desc=True)  # Order by alias
        """
        if isinstance(column, Column):
            self._order_by = column.name
        elif isinstance(column, str):
            self._order_by = column
        else:
            raise TypeError(f"Unsupported column type: {type(column)}. Expected Column or str.")
        self._order_desc = desc
        return self
    
    def limit(self, n: int) -> 'QueryBuilder':
        """
        Limit number of results.
        
        Args:
            n: Maximum number of rows to return
            
        Returns:
            Self for method chaining
        """
        self._limit = n
        return self
    
    def group_by(self, *columns: Union[Column, str]) -> 'QueryBuilder':
        """
        Group by columns using Column objects or strings (for aliases/expressions).
        
        Args:
            *columns: Column objects or strings (alias names/expressions) to group by
            
        Returns:
            Self for method chaining
            
        Example:
            >>> builder.group_by(crypto_quotes.pair, crypto_quotes.exchange)
            >>> builder.group_by("hour", crypto_quotes.pair)  # Group by alias or expression
        """
        self._group_by = [col.name if isinstance(col, Column) else col for col in columns]
        return self
    
    def having(self, condition: Union[ColumnExpression, CombinedExpression, SubqueryExpression, str]) -> 'QueryBuilder':
        """
        Add HAVING clause (for use with GROUP BY).
        
        Args:
            condition: ColumnExpression, CombinedExpression, SubqueryExpression, or raw SQL string
            
        Returns:
            Self for method chaining
            
        Example:
            >>> builder.having(avg(crypto_quotes.best_bid_price) > 100)
            >>> builder.having(Subquery.exists(other_builder))
            >>> builder.having("avg_price > 100")  # Raw SQL still works
        """
        if isinstance(condition, str):
            # Raw SQL string
            self._having = condition
        elif isinstance(condition, (ColumnExpression, CombinedExpression, SubqueryExpression)):
            # Expression objects
            base_table = self.table_name if self._joins else None
            self._having = condition.to_sql(self._escape_string, base_table_name=base_table)
        else:
            raise TypeError(f"Unsupported condition type: {type(condition)}. "
                          f"Expected ColumnExpression, CombinedExpression, SubqueryExpression, or str.")
        return self
    
    def join(
        self,
        table: Union[Table, str],
        condition: Optional[Union[ColumnExpression, CombinedExpression, str]] = None,
        join_type: Literal["INNER", "LEFT", "RIGHT", "FULL", "CROSS"] = "INNER",
        alias: Optional[str] = None
    ) -> 'QueryBuilder':
        """
        Add a JOIN clause to the query.
        
        Args:
            table: Table object or table name (database.table or just table)
            condition: JOIN condition as ColumnExpression, CombinedExpression, or raw SQL string.
                      Required for all join types except CROSS JOIN.
            join_type: Type of join - "INNER", "LEFT", "RIGHT", "FULL", or "CROSS" (default: "INNER")
            alias: Optional table alias for disambiguating columns
            
        Returns:
            Self for method chaining
            
        Example:
            >>> # Join using column expressions
            >>> builder.join(
            ...     other_table,
            ...     condition=(crypto_quotes.pair == other_table.symbol),
            ...     join_type="LEFT",
            ...     alias="ot"
            ... )
            >>> 
            >>> # Join using raw SQL
            >>> builder.join("other_db.other_table", condition="crypto_quotes.id = other_table.quote_id")
            >>> 
            >>> # CROSS JOIN (no condition needed)
            >>> builder.join("other_table", join_type="CROSS")
        """
        # Determine table name
        if isinstance(table, Table):
            table_name = table.qualified_name
        elif isinstance(table, str):
            table_name = table
        else:
            raise TypeError(f"Unsupported table type: {type(table)}. Expected Table or str.")
        
        # Validate CROSS JOIN doesn't have condition
        if join_type == "CROSS" and condition is not None:
            raise ValueError("CROSS JOIN cannot have a condition")
        
        # Validate non-CROSS joins have condition
        if join_type != "CROSS" and condition is None:
            raise ValueError(f"{join_type} JOIN requires a condition")
        
        # Validate condition type
        if condition is not None and not isinstance(condition, (ColumnExpression, CombinedExpression, str)):
            raise TypeError(f"Unsupported condition type: {type(condition)}. "
                          f"Expected ColumnExpression, CombinedExpression, or str.")
        
        # Build join specification
        join_spec = {
            "table": table_name,
            "type": join_type,
            "alias": alias,
            "condition": condition
        }
        
        self._joins.append(join_spec)
        return self
    
    def from_subquery(self, subquery: Subquery, alias: str) -> 'QueryBuilder':
        """
        Use a subquery as the FROM clause (derived table).
        
        Args:
            subquery: Subquery instance
            alias: Alias name for the derived table (required)
            
        Returns:
            Self for method chaining
            
        Example:
            >>> subq = Subquery(other_builder)
            >>> builder.from_subquery(subq, alias="derived_table")
        """
        if not alias:
            raise ValueError("Alias is required for FROM subquery")
        self._from_subquery = subquery
        self._from_alias = alias
        return self
    
    def _build_query(self) -> str:
        """Build the SQL query from current state."""
        # SELECT clause
        if self._columns is None:
            select_clause = "SELECT *"
        else:
            select_clause = f"SELECT {', '.join(self._columns)}"
        
        # FROM clause
        if self._from_subquery:
            # Use subquery as FROM (derived table)
            # Don't include alias in to_sql() since we handle it separately
            from_clause = f"FROM {self._from_subquery.to_sql(include_alias=False)} AS {self._from_alias}"
        else:
            from_clause = f"FROM {self.table_name}"
        
        # JOIN clauses
        join_clauses = []
        for join_spec in self._joins:
            join_type = join_spec["type"]
            table_name = join_spec["table"]
            alias = join_spec["alias"]
            condition = join_spec["condition"]
            
            # Build table reference with optional alias
            table_ref = table_name
            if alias:
                table_ref = f"{table_name} AS {alias}"
            
            # Build JOIN clause
            if join_type == "CROSS":
                join_clause = f"CROSS JOIN {table_ref}"
            else:
                # Convert condition to SQL
                if isinstance(condition, (ColumnExpression, CombinedExpression)):
                    # Pass base table name to auto-qualify columns without table references
                    condition_sql = condition.to_sql(self._escape_string, base_table_name=self.table_name)
                elif isinstance(condition, str):
                    condition_sql = condition
                else:
                    raise TypeError(f"Unsupported condition type: {type(condition)}. "
                                  f"Expected ColumnExpression, CombinedExpression, or str.")
                
                join_clause = f"{join_type} JOIN {table_ref} ON {condition_sql}"
            
            join_clauses.append(join_clause)
        
        join_clause_str = " ".join(join_clauses) if join_clauses else ""
        
        # WHERE clause
        where_clause = ""
        if self._where_conditions:
            where_clause = f"WHERE {' AND '.join(self._where_conditions)}"
        
        # GROUP BY clause
        group_by_clause = ""
        if self._group_by:
            group_by_clause = f"GROUP BY {', '.join(self._group_by)}"
        
        # HAVING clause
        having_clause = ""
        if self._having:
            having_clause = f"HAVING {self._having}"
        
        # ORDER BY clause
        order_clause = ""
        if self._order_by:
            order_clause = f"ORDER BY {self._order_by} {'DESC' if self._order_desc else 'ASC'}"
        
        # LIMIT clause
        limit_clause = ""
        if self._limit is not None:
            limit_clause = f"LIMIT {self._limit}"
        
        # Combine all clauses
        parts = [select_clause, from_clause, join_clause_str, where_clause, group_by_clause, 
                 having_clause, order_clause, limit_clause]
        query = " ".join(part for part in parts if part)
        
        return query
    
    def _execute(self) -> Union[List[Dict[str, Any]], List[Row]]:
        """
        Execute the query and return raw results.
        
        Returns:
            List of Row objects if schema is available, otherwise list of dictionaries
        """
        query = self._build_query()
        results = self.client.execute(query)
        
        # Convert to Row objects if schema is available
        if self.schema:
            return [Row(row) for row in results]
        return results
    
    def to_list(self) -> Union[List[Dict[str, Any]], List[Row]]:
        """
        Execute query and return as list of Row objects (if schema available) or dictionaries.
        
        Returns:
            List of Row objects if schema is available, otherwise list of dictionaries.
            Each Row/dict represents a row.
        """
        return self._execute()
    
    def to_dict(self, key_column: Column, value_column: Optional[Column] = None) -> Dict[str, Any]:
        """
        Execute query and return as dictionary.
        
        Args:
            key_column: Column object to use as dictionary keys
            value_column: Column object to use as values (None = entire row dict)
            
        Returns:
            Dictionary mapping key_column values to value_column values or row dicts
            
        Example:
            >>> builder.to_dict(crypto_quotes.pair, crypto_quotes.best_bid_price)
        """
        results = self._execute()
        key_name = key_column.name
        if value_column:
            value_name = value_column.name
            return {row[key_name]: row[value_name] for row in results}
        else:
            return {row[key_name]: row for row in results}
    
    def to_dataframe(self):
        """
        Execute query and return as pandas DataFrame.
        Uses ClickHouse Connect's native query_df method for better performance.
        
        Returns:
            pandas DataFrame
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install it with: pip install pandas")
        
        query = self._build_query()
        try:
            # Use ClickHouse Connect's native query_df for better performance
            return self.client.query_df(query)
        except AttributeError:
            # Fallback to manual conversion if query_df not available
            results = self._execute()
            if not results:
                return pd.DataFrame()
            return pd.DataFrame(results)
    
    def to_numpy(self, columns: Optional[List[str]] = None, dtype=None):
        """
        Execute query and return as numpy array.
        Uses ClickHouse Connect's native query_np method when possible.
        
        Args:
            columns: Columns to include (None = all columns, uses query_np)
            dtype: NumPy dtype (None = auto-detect)
            
        Returns:
            numpy array
        """
        try:
            import numpy as np
        except ImportError:
            raise ImportError("numpy is required. Install it with: pip install numpy")
        
        query = self._build_query()
        
        # If no column filtering needed, use native query_np for better performance
        if columns is None:
            try:
                # Use ClickHouse Connect's native query_np
                arr = self.client.query_np(query)
                if dtype is not None:
                    return arr.astype(dtype)
                return arr
            except AttributeError:
                # Fallback to manual conversion
                pass
        
        # Manual conversion when column filtering is needed
        results = self._execute()
        if not results:
            return np.array([])
        
        if columns is None:
            # Auto-select numeric columns
            if results:
                numeric_cols = [k for k, v in results[0].items() 
                              if isinstance(v, (int, float)) and not isinstance(v, bool)]
                columns = numeric_cols if numeric_cols else list(results[0].keys())
            else:
                return np.array([])
        
        # Extract values
        data = [[row[col] for col in columns] for row in results]
        return np.array(data, dtype=dtype)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Execute query and return as JSON string.
        
        Args:
            indent: JSON indentation (None = compact)
            
        Returns:
            JSON string
        """
        results = self._execute()
        return json.dumps(results, indent=indent, default=str)
    
    def to_csv(self, path: Optional[str] = None, **kwargs) -> Optional[str]:
        """
        Execute query and return as CSV string or write to file.
        Uses ClickHouse Connect's native query_df for better performance.
        
        Args:
            path: Optional file path to write CSV. If None, returns CSV string.
            **kwargs: Additional arguments passed to pandas to_csv()
            
        Returns:
            CSV string if path is None, otherwise None
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install it with: pip install pandas")
        
        # Use to_dataframe which already uses query_df internally
        df = self.to_dataframe()
        if path:
            df.to_csv(path, index=False, **kwargs)
            return None
        else:
            return df.to_csv(index=False, **kwargs)
    
    def to_parquet(self, path: str, **kwargs) -> None:
        """
        Execute query and write results to Parquet file.
        Uses ClickHouse Connect's native query_df for better performance.
        
        Args:
            path: File path to write Parquet file
            **kwargs: Additional arguments passed to pandas to_parquet()
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required. Install it with: pip install pandas")
        
        # Use to_dataframe which already uses query_df internally
        df = self.to_dataframe()
        df.to_parquet(path, index=False, **kwargs)
    
    def count(self) -> int:
        """
        Count rows matching the current filters.
        
        Returns:
            Number of rows
        """
        # Save current state
        original_columns = self._columns
        original_limit = self._limit
        
        # Build count query
        self._columns = ["count() as count"]
        self._limit = None  # Remove limit for count
        
        try:
            result = self._execute()
            count = result[0]["count"] if result else 0
        finally:
            # Restore state
            self._columns = original_columns
            self._limit = original_limit
        
        return count
    
    def first(self) -> Optional[Union[Dict[str, Any], Row]]:
        """
        Get first result.
        
        Returns:
            First row as Row object (if schema available) or dictionary, or None if no results
        """
        original_limit = self._limit
        self._limit = 1
        try:
            results = self._execute()
            return results[0] if results else None
        finally:
            self._limit = original_limit
    
    def exists(self) -> bool:
        """
        Check if any rows match the current filters.
        
        Returns:
            True if at least one row matches, False otherwise
        """
        return self.count() > 0
    
    def __iter__(self):
        """Make query builder iterable."""
        return iter(self._execute())
    
    def __repr__(self) -> str:
        """String representation showing the built query."""
        return f"QueryBuilder(query={self._build_query()})"

