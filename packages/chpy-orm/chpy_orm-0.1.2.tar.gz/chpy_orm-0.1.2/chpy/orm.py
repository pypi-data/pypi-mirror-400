"""
ORM-like classes for ClickHouse tables, similar to SQLAlchemy.
Provides column objects for autocomplete and type safety.
"""

from typing import Any, Optional, Union, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from chpy.query_builder import QueryBuilder


class Row:
    """
    Represents a row from a database query result.
    Allows both dictionary-style (row['key']) and attribute-style (row.key) access.
    
    Usage:
        >>> row = Row({'pair': 'BTC-USDT', 'price': 50000.0})
        >>> row.pair  # 'BTC-USDT'
        >>> row['pair']  # 'BTC-USDT'
        >>> row.price  # 50000.0
    """
    
    def __init__(self, data: dict):
        """
        Initialize a row from a dictionary.
        
        Args:
            data: Dictionary containing row data
        """
        self._data = data
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute by name (for attribute-style access)."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Row has no attribute '{name}'")
    
    def __getitem__(self, key: str) -> Any:
        """Get item by key (for dictionary-style access)."""
        return self._data[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get item by key with optional default (dictionary-style)."""
        return self._data.get(key, default)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in row."""
        return key in self._data
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Row({self._data})"
    
    def __iter__(self):
        """Iterate over keys."""
        return iter(self._data)
    
    def keys(self):
        """Get all keys."""
        return self._data.keys()
    
    def values(self):
        """Get all values."""
        return self._data.values()
    
    def items(self):
        """Get all key-value pairs."""
        return self._data.items()
    
    def to_dict(self) -> dict:
        """Convert row to dictionary."""
        return self._data.copy()


class Column:
    """
    Represents a database column, similar to SQLAlchemy's Column.
    
    Usage:
        >>> crypto_quotes.pair == "BTC-USDT"
        >>> crypto_quotes.timestamp_ms >= datetime.now()
    """
    
    def __init__(self, name: str, type_: Union[str, Any], table: Optional['Table'] = None):
        """
        Initialize a column.
        
        Args:
            name: Column name
            type_: Column type (e.g., "String", "Float64", "UInt64") or TypeBuilder instance
            table: Optional parent table
        """
        self.name = name
        # Convert TypeBuilder to string if needed
        if isinstance(type_, str):
            self.type = type_
        else:
            # Import here to avoid circular dependency
            try:
                from chpy.types import TypeBuilder as TB
                if isinstance(type_, TB):
                    self.type = str(type_)
                else:
                    # If it has __str__ method, try to convert it
                    self.type = str(type_)
            except ImportError:
                # Fallback: if it's not a string, try to convert it
                self.type = str(type_)
        self.table = table
    
    def __eq__(self, other: Any) -> 'ColumnExpression':
        """Create equality expression: column == value"""
        return ColumnExpression(self, "=", other)
    
    def __ne__(self, other: Any) -> 'ColumnExpression':
        """Create inequality expression: column != value"""
        return ColumnExpression(self, "!=", other)
    
    def __lt__(self, other: Any) -> 'ColumnExpression':
        """Create less-than expression: column < value"""
        return ColumnExpression(self, "<", other)
    
    def __le__(self, other: Any) -> 'ColumnExpression':
        """Create less-than-or-equal expression: column <= value"""
        return ColumnExpression(self, "<=", other)
    
    def __gt__(self, other: Any) -> 'ColumnExpression':
        """Create greater-than expression: column > value"""
        return ColumnExpression(self, ">", other)
    
    def __ge__(self, other: Any) -> 'ColumnExpression':
        """Create greater-than-or-equal expression: column >= value"""
        return ColumnExpression(self, ">=", other)
    
    def in_(self, values: Union[List[Any], 'Subquery']) -> 'ColumnExpression':
        """Create IN expression: column IN (value1, value2, ...) or column IN (subquery)"""
        return ColumnExpression(self, "IN", values)
    
    def not_in(self, values: Union[List[Any], 'Subquery']) -> 'ColumnExpression':
        """Create NOT IN expression: column NOT IN (value1, value2, ...) or column NOT IN (subquery)"""
        return ColumnExpression(self, "NOT IN", values)
    
    def like(self, pattern: str) -> 'ColumnExpression':
        """Create LIKE expression: column LIKE pattern"""
        return ColumnExpression(self, "LIKE", pattern)
    
    def __str__(self) -> str:
        """String representation returns column name, table-qualified if table is available."""
        if self.table:
            return f"{self.table.full_name}.{self.name}"
        return self.name
    
    def __repr__(self) -> str:
        """Representation includes table name if available."""
        if self.table:
            return f"{self.table.name}.{self.name}"
        return self.name


class Subquery:
    """
    Represents a subquery that can be used in WHERE, HAVING, SELECT, FROM clauses, etc.
    
    Usage:
        >>> subq = Subquery(query_builder)
        >>> column.in_(subq)
        >>> column == subq
        >>> builder.where(Subquery.exists(subq))
        >>> builder.select(subq.alias("subquery_result"))
    """
    
    def __init__(self, query_builder: 'QueryBuilder'):
        """
        Initialize a subquery.
        
        Args:
            query_builder: QueryBuilder instance representing the subquery
        """
        self.query_builder = query_builder
        self._alias: Optional[str] = None
    
    def to_sql(self, include_alias: bool = True) -> str:
        """
        Convert subquery to SQL string.
        
        Args:
            include_alias: Whether to include alias if set (default: True)
                          Set to False for FROM clause where alias is handled separately
        """
        sql = f"({self.query_builder._build_query()})"
        if include_alias and self._alias:
            return f"{sql} AS {self._alias}"
        return sql
    
    def alias(self, alias_name: str) -> 'Subquery':
        """
        Add an alias to the subquery (useful for SELECT and FROM clauses).
        
        Args:
            alias_name: Alias name for the subquery
            
        Returns:
            Self for method chaining
            
        Example:
            >>> subq = Subquery(other_builder).alias("subquery_result")
            >>> builder.select(subq)
        """
        self._alias = alias_name
        return self
    
    @staticmethod
    def exists(query_builder: 'QueryBuilder') -> 'SubqueryExpression':
        """
        Create an EXISTS subquery expression.
        
        Args:
            query_builder: QueryBuilder instance for the subquery
            
        Returns:
            SubqueryExpression for EXISTS clause
        """
        return SubqueryExpression("EXISTS", Subquery(query_builder))
    
    @staticmethod
    def not_exists(query_builder: 'QueryBuilder') -> 'SubqueryExpression':
        """
        Create a NOT EXISTS subquery expression.
        
        Args:
            query_builder: QueryBuilder instance for the subquery
            
        Returns:
            SubqueryExpression for NOT EXISTS clause
        """
        return SubqueryExpression("NOT EXISTS", Subquery(query_builder))


class SubqueryExpression:
    """
    Represents a subquery expression (EXISTS, NOT EXISTS).
    """
    
    def __init__(self, operator: str, subquery: Subquery):
        """
        Initialize a subquery expression.
        
        Args:
            operator: "EXISTS" or "NOT EXISTS"
            subquery: Subquery instance
        """
        self.operator = operator
        self.subquery = subquery
    
    def to_sql(self, escape_string_func, base_table_name: Optional[str] = None) -> str:
        """Convert subquery expression to SQL string."""
        # EXISTS/NOT EXISTS don't use aliases
        return f"{self.operator} {self.subquery.to_sql(include_alias=False)}"


class ColumnExpression:
    """
    Represents a column expression for WHERE clauses.
    """
    
    def __init__(self, column: Column, operator: str, value: Any):
        """
        Initialize a column expression.
        
        Args:
            column: Column object
            operator: SQL operator (=, !=, <, <=, >, >=, IN, NOT IN, LIKE)
            value: Value to compare against (can be a Subquery)
        """
        self.column = column
        self.operator = operator
        self.value = value
    
    def to_sql(self, escape_string_func, base_table_name: Optional[str] = None) -> str:
        """
        Convert expression to SQL string.
        
        Args:
            escape_string_func: Function to escape strings
            base_table_name: Optional base table name (database.table) for qualifying columns without table references
            
        Returns:
            SQL string representation
        """
        # Use table-qualified column name if table is available, or use base table if provided
        if self.column.table:
            col_name = f"{self.column.table.full_name}.{self.column.name}"
        elif base_table_name:
            col_name = f"{base_table_name}.{self.column.name}"
        else:
            col_name = self.column.name
        
        if self.operator == "IN":
            if isinstance(self.value, Subquery):
                return f"{col_name} IN {self.value.to_sql()}"
            elif isinstance(self.value, list):
                if all(isinstance(v, str) for v in self.value):
                    escaped_values = [f"'{escape_string_func(v)}'" for v in self.value]
                    return f"{col_name} IN ({', '.join(escaped_values)})"
                else:
                    values_str = ', '.join(str(v) for v in self.value)
                    return f"{col_name} IN ({values_str})"
            else:
                raise ValueError("IN operator requires a list or Subquery")
        
        elif self.operator == "NOT IN":
            if isinstance(self.value, Subquery):
                return f"{col_name} NOT IN {self.value.to_sql()}"
            elif isinstance(self.value, list):
                if all(isinstance(v, str) for v in self.value):
                    escaped_values = [f"'{escape_string_func(v)}'" for v in self.value]
                    return f"{col_name} NOT IN ({', '.join(escaped_values)})"
                else:
                    values_str = ', '.join(str(v) for v in self.value)
                    return f"{col_name} NOT IN ({values_str})"
            else:
                raise ValueError("NOT IN operator requires a list or Subquery")
        
        elif self.operator == "LIKE":
            escaped_value = escape_string_func(str(self.value))
            return f"{col_name} LIKE '{escaped_value}'"
        
        else:
            # Handle subquery comparisons
            if isinstance(self.value, Subquery):
                return f"{col_name} {self.operator} {self.value.to_sql()}"
            
            # Handle column-to-column comparisons (for JOIN conditions)
            if isinstance(self.value, Column):
                # If comparing two columns, use table-qualified name for the value column too
                if self.value.table:
                    value_str = f"{self.value.table.full_name}.{self.value.name}"
                elif base_table_name:
                    value_str = f"{base_table_name}.{self.value.name}"
                else:
                    value_str = self.value.name
                return f"{col_name} {self.operator} {value_str}"
            
            # Handle datetime conversion for timestamp columns
            if isinstance(self.value, datetime):
                if "timestamp" in col_name.lower() or "time" in col_name.lower():
                    value = int(self.value.timestamp() * 1000)  # Convert to milliseconds
                else:
                    value = self.value
            elif isinstance(self.value, str):
                escaped_value = escape_string_func(self.value)
                return f"{col_name} {self.operator} '{escaped_value}'"
            else:
                value = self.value
            
            return f"{col_name} {self.operator} {value}"
    
    def __and__(self, other: Union['ColumnExpression', 'CombinedExpression', 'SubqueryExpression']) -> 'CombinedExpression':
        """Combine expressions with AND: expr1 & expr2"""
        return CombinedExpression(self, "AND", other)
    
    def __or__(self, other: Union['ColumnExpression', 'CombinedExpression', 'SubqueryExpression']) -> 'CombinedExpression':
        """Combine expressions with OR: expr1 | expr2"""
        return CombinedExpression(self, "OR", other)
    
    def __invert__(self) -> 'ColumnExpression':
        """Negate expression: ~expr"""
        return ColumnExpression(self.column, f"NOT {self.operator}", self.value)


class CombinedExpression:
    """
    Represents a combination of expressions (AND/OR).
    """
    
    def __init__(self, left: Union[ColumnExpression, 'CombinedExpression', 'SubqueryExpression'], 
                 operator: str, right: Union[ColumnExpression, 'CombinedExpression', 'SubqueryExpression']):
        """
        Initialize a combined expression.
        
        Args:
            left: Left expression
            operator: "AND" or "OR"
            right: Right expression
        """
        self.left = left
        self.operator = operator
        self.right = right
    
    def to_sql(self, escape_string_func, base_table_name: Optional[str] = None) -> str:
        """Convert combined expression to SQL."""
        if isinstance(self.left, (ColumnExpression, CombinedExpression, SubqueryExpression)):
            left_sql = self.left.to_sql(escape_string_func, base_table_name)
        else:
            left_sql = str(self.left)
        
        if isinstance(self.right, (ColumnExpression, CombinedExpression, SubqueryExpression)):
            right_sql = self.right.to_sql(escape_string_func, base_table_name)
        else:
            right_sql = str(self.right)
        
        return f"({left_sql} {self.operator} {right_sql})"
    
    def __and__(self, other: Union[ColumnExpression, 'CombinedExpression', 'SubqueryExpression']) -> 'CombinedExpression':
        """Combine with AND: expr1 & expr2"""
        return CombinedExpression(self, "AND", other)
    
    def __or__(self, other: Union[ColumnExpression, 'CombinedExpression', 'SubqueryExpression']) -> 'CombinedExpression':
        """Combine with OR: expr1 | expr2"""
        return CombinedExpression(self, "OR", other)


# AggregateFunction moved to chpy.functions.base
# Import it from there for backward compatibility
from chpy.functions.base import AggregateFunction


# Aggregate functions moved to chpy.functions.aggregate
# Import them from there for backward compatibility
from chpy.functions.aggregate import avg, count
from chpy.functions.aggregate import min as min_, max as max_, sum as sum_


class Table:
    """
    Represents a database table with columns, similar to SQLAlchemy's Table.
    """
    
    def __init__(self, name: str, database: str, columns: List[Column]):
        """
        Initialize a table.
        
        Args:
            name: Table name
            database: Database name
            columns: List of Column objects
        """
        self.name = name
        self.database = database
        self.full_name = f"{database}.{name}"
        
        # Create column attributes dynamically
        for col in columns:
            col.table = self
            setattr(self, col.name, col)
        
        self._columns = {col.name: col for col in columns}
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name."""
        return self._columns.get(name)
    
    def get_all_columns(self) -> List[Column]:
        """Get all columns."""
        return list(self._columns.values())
    
    def __getitem__(self, name: str) -> Column:
        """Get column by name using bracket notation."""
        if name not in self._columns:
            raise AttributeError(f"Column '{name}' not found in table '{self.name}'")
        return self._columns[name]
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Table({self.full_name})"

