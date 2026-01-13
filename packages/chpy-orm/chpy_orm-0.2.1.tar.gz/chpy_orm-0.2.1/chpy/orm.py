"""
ORM-like classes for ClickHouse tables, similar to SQLAlchemy.
Provides column objects for autocomplete and type safety.
"""

from typing import Any, Optional, Union, List, TYPE_CHECKING
from datetime import datetime
import inspect

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
        self._name = name
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
        self._table = table
    
    @property
    def name(self) -> str:
        """Get the column name."""
        return self._name
    
    @property
    def table(self) -> Optional['Table']:
        """Get the parent table."""
        return self._table
    
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
    
    def __add__(self, other: Any) -> Any:
        """Create addition expression: column + value or column + column"""
        from chpy.functions.base import Function
        return Function("plus", self, other)
    
    def __radd__(self, other: Any) -> Any:
        """Create reverse addition expression: value + column"""
        from chpy.functions.base import Function
        return Function("plus", other, self)
    
    def __sub__(self, other: Any) -> Any:
        """Create subtraction expression: column - value or column - column"""
        from chpy.functions.base import Function
        return Function("minus", self, other)
    
    def __rsub__(self, other: Any) -> Any:
        """Create reverse subtraction expression: value - column"""
        from chpy.functions.base import Function
        return Function("minus", other, self)
    
    def __mul__(self, other: Any) -> Any:
        """Create multiplication expression: column * value or column * column"""
        from chpy.functions.base import Function
        return Function("multiply", self, other)
    
    def __rmul__(self, other: Any) -> Any:
        """Create reverse multiplication expression: value * column"""
        from chpy.functions.base import Function
        return Function("multiply", other, self)
    
    def __truediv__(self, other: Any) -> Any:
        """Create division expression: column / value or column / column"""
        from chpy.functions.base import Function
        return Function("divide", self, other)
    
    def __rtruediv__(self, other: Any) -> Any:
        """Create reverse division expression: value / column"""
        from chpy.functions.base import Function
        return Function("divide", other, self)
    
    def __mod__(self, other: Any) -> Any:
        """Create modulo expression: column % value or column % column"""
        from chpy.functions.base import Function
        return Function("modulo", self, other)
    
    def __rmod__(self, other: Any) -> Any:
        """Create reverse modulo expression: value % column"""
        from chpy.functions.base import Function
        return Function("modulo", other, self)
    
    def __neg__(self) -> Any:
        """Create negation expression: -column"""
        from chpy.functions.base import Function
        return Function("negate", self)
    
    def __str__(self) -> str:
        """String representation returns column name, table-qualified if table is available."""
        if self._table:
            return f"{self._table._qualified_name}.{self._name}"
        return self._name
    
    def __repr__(self) -> str:
        """Representation includes table name if available."""
        if self._table:
            return f"{self._table._table_name}.{self._name}"
        return self._name


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
            col_name = f"{self.column.table._qualified_name}.{self.column.name}"
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
                    value_str = f"{self.value.table._qualified_name}.{self.value.name}"
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
        self._table_name = name
        self._db_name = database
        self._qualified_name = f"{database}.{name}"
        
        # Sort columns alphabetically before processing to ensure consistent ordering
        # This helps VS Code/Pylance show columns in a predictable order
        sorted_columns = sorted(columns, key=lambda col: col.name)
        
        # Initialize _columns first to avoid recursion in __getattr__
        # Build from sorted columns so dict insertion order is alphabetical (Python 3.7+)
        self._columns = {col.name: col for col in sorted_columns}
        
        # Create column attributes dynamically
        # Also set __annotations__ to help type checkers and IDEs with autocomplete
        # Use __dict__ to avoid triggering __getattr__
        if '__annotations__' not in self.__dict__:
            self.__annotations__ = {}
        
        for col in sorted_columns:
            col._table = self
            # Use __dict__ directly to bypass property setters (in case column name conflicts with property names)
            self.__dict__[col.name] = col
            # Add type annotation for autocomplete support
            # Python 3.7+ preserves dict insertion order, so columns will be in alphabetical order
            self.__annotations__[col.name] = Column
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name."""
        return self._columns.get(name)
    
    def get_all_columns(self) -> List[Column]:
        """Get all columns."""
        return list(self._columns.values())
    
    def __getitem__(self, name: str) -> Column:
        """Get column by name using bracket notation."""
        if name not in self._columns:
            raise AttributeError(f"Column '{name}' not found in table '{self._table_name}'")
        return self._columns[name]
    
    def __getattribute__(self, name: str):
        """
        Override to check columns first before properties.
        This ensures columns can override property names (e.g., a column named 'name').
        """
        # Check if this is a column first (before properties are checked)
        # Use object.__getattribute__ to avoid recursion
        try:
            columns = object.__getattribute__(self, '_columns')
            if name in columns:
                return columns[name]
        except AttributeError:
            # _columns doesn't exist yet (during __init__)
            pass
        
        # Fall back to normal attribute access (includes properties)
        return object.__getattribute__(self, name)
    
    def __getattr__(self, name: str) -> Column:
        """
        Get column by attribute name (fallback if not found in __getattribute__).
        This enables autocomplete for column access.
        """
        # Use __dict__ to access _columns to avoid recursion
        # Only check _columns if it exists (should always exist after __init__)
        columns = self.__dict__.get('_columns', {})
        if name in columns:
            return columns[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __dir__(self) -> List[str]:
        """
        Return list of available attributes including column names.
        This helps IDEs provide autocomplete suggestions.
        Order: columns (alphabetically) -> attributes (alphabetically) -> methods (alphabetically)
        
        Non-column attributes are private (prefixed with `_`) so that when VS Code sorts
        alphabetically, columns (which start with letters) will appear before private attributes
        (which start with `_`), achieving the desired ordering.
        """
        # Get column names - use __dict__ to avoid recursion
        # Columns are already sorted alphabetically when set in __init__
        columns = self.__dict__.get('_columns', {})
        column_names = sorted(columns.keys())  # Ensure alphabetical order
        
        # Get standard attributes from parent
        try:
            standard_attrs = list(super().__dir__())
        except AttributeError:
            standard_attrs = []
        
        # Remove column names and internal attributes from standard_attrs to avoid duplicates
        # Also filter out common internal attributes that shouldn't appear in autocomplete
        internal_attrs = {'_columns', '__dict__', '__weakref__', '__annotations__'}
        other_attrs = [
            attr for attr in standard_attrs 
            if attr not in columns and attr not in internal_attrs
        ]
        
        # Separate attributes from methods
        attributes = []
        methods = []
        
        for attr in other_attrs:
            # Handle private attributes (starting with single underscore)
            if attr.startswith('_') and not attr.startswith('__'):
                attributes.append(attr)
                continue
            
            # Handle dunder methods (special methods like __repr__, __str__, etc.)
            if attr.startswith('__') and attr.endswith('__'):
                methods.append(attr)
                continue
            
            # Check if it's a method by inspecting the class
            # Use getattr_static to avoid triggering __getattr__ or property accessors
            try:
                obj = inspect.getattr_static(self.__class__, attr, None)
                if obj is not None:
                    # Check if it's callable (method, function, builtin, or callable descriptor)
                    if inspect.ismethod(obj) or inspect.isfunction(obj) or inspect.isbuiltin(obj):
                        methods.append(attr)
                    elif callable(obj):
                        # Some descriptors might be callable, check if it's actually a method-like thing
                        methods.append(attr)
                    else:
                        attributes.append(attr)
                else:
                    # Not found on class, check if it's in instance dict (likely an attribute)
                    if attr in self.__dict__:
                        attributes.append(attr)
                    else:
                        # Default to attribute if we can't determine
                        attributes.append(attr)
            except (AttributeError, TypeError):
                # If we can't determine, treat as attribute
                attributes.append(attr)
        
        # Return: columns first, then attributes, then methods (all alphabetically sorted)
        # Note: VS Code/Pylance may sort __dir__ results alphabetically, mixing columns with other attributes.
        # However, this ordering ensures that:
        # 1. Other IDEs/tools that respect __dir__ order will show columns first
        # 2. The order is deterministic and consistent
        # For class-level column definitions (like CryptoQuotesTable), VS Code's static analysis
        # will see them, but may still sort alphabetically. This is a limitation of VS Code's autocomplete.
        result = sorted(column_names) + sorted(attributes) + sorted(methods)
        return result
    
    @property
    def table_name(self) -> str:
        """Get the table name (without database qualification)."""
        return self._table_name
    
    @property
    def db_name(self) -> str:
        """Get the database name."""
        return self._db_name
    
    @property
    def qualified_name(self) -> str:
        """Get the qualified table name (database.table)."""
        return self._qualified_name
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Table({self._qualified_name})"
    
    def __eq__(self, other: Any) -> bool:
        """Compare tables by qualified_name for equality."""
        if not isinstance(other, Table):
            return False
        return self._qualified_name == other._qualified_name

