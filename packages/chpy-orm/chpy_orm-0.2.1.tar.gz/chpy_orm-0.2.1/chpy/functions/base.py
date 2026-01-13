"""
Base classes for ClickHouse functions.
"""

from typing import Optional, List, Any, Union, Literal
from chpy.orm import Column, ColumnExpression, CombinedExpression


class WindowSpec:
    """
    Represents a window specification for OVER clause.
    
    Usage:
        >>> WindowSpec().partition_by(col1, col2).order_by(col3)
        >>> WindowSpec().order_by(col1).rows_between(0, 2)
    """
    
    def __init__(self):
        """Initialize an empty window specification."""
        self._partition_by: Optional[List[Column]] = None
        self._order_by: Optional[List[Column]] = None
        self._order_desc: Optional[List[bool]] = None
        self._frame_type: Optional[Literal["ROWS", "RANGE"]] = None
        self._frame_start: Optional[str] = None
        self._frame_end: Optional[str] = None
    
    def partition_by(self, *columns: Column) -> 'WindowSpec':
        """
        Add PARTITION BY clause.
        
        Args:
            *columns: Column objects to partition by
            
        Returns:
            Self for method chaining
        """
        self._partition_by = list(columns)
        return self
    
    def order_by(self, *columns: Column, desc: Union[bool, List[bool]] = False) -> 'WindowSpec':
        """
        Add ORDER BY clause.
        
        Args:
            *columns: Column objects to order by
            desc: If True, order descending. Can be a list for multiple columns.
            
        Returns:
            Self for method chaining
        """
        self._order_by = list(columns)
        if isinstance(desc, bool):
            self._order_desc = [desc] * len(columns)
        else:
            self._order_desc = desc
        return self
    
    def rows_between(self, start: Union[int, str], end: Union[int, str]) -> 'WindowSpec':
        """
        Add ROWS BETWEEN frame specification.
        
        Args:
            start: Start of frame (e.g., 0, "UNBOUNDED PRECEDING", "CURRENT ROW")
            end: End of frame (e.g., 2, "UNBOUNDED FOLLOWING", "CURRENT ROW")
            
        Returns:
            Self for method chaining
        """
        self._frame_type = "ROWS"
        self._frame_start = str(start)
        self._frame_end = str(end)
        return self
    
    def range_between(self, start: Union[int, str], end: Union[int, str]) -> 'WindowSpec':
        """
        Add RANGE BETWEEN frame specification.
        
        Args:
            start: Start of frame (e.g., 0, "UNBOUNDED PRECEDING", "CURRENT ROW")
            end: End of frame (e.g., 2, "UNBOUNDED FOLLOWING", "CURRENT ROW")
            
        Returns:
            Self for method chaining
        """
        self._frame_type = "RANGE"
        self._frame_start = str(start)
        self._frame_end = str(end)
        return self
    
    def to_sql(self) -> str:
        """
        Convert window specification to SQL OVER clause.
        
        Returns:
            SQL string for OVER clause
        """
        parts = []
        
        if self._partition_by:
            col_names = ', '.join(col.name for col in self._partition_by)
            parts.append(f"PARTITION BY {col_names}")
        
        if self._order_by:
            order_parts = []
            for i, col in enumerate(self._order_by):
                direction = "DESC" if (i < len(self._order_desc) and self._order_desc[i]) else "ASC"
                order_parts.append(f"{col.name} {direction}")
            parts.append(f"ORDER BY {', '.join(order_parts)}")
        
        if self._frame_type:
            frame_spec = f"{self._frame_type} BETWEEN {self._frame_start} AND {self._frame_end}"
            parts.append(frame_spec)
        
        if not parts:
            return "OVER ()"
        
        return f"OVER ({' '.join(parts)})"


class Function:
    """
    Base class for ClickHouse functions that can be used in SELECT clauses.
    
    Usage:
        >>> length(crypto_quotes.pair)
        >>> length(crypto_quotes.pair).alias("pair_length")
    """
    
    def __init__(self, func_name: str, *args: Any, alias: Optional[str] = None):
        """
        Initialize a function.
        
        Args:
            func_name: Function name (e.g., "length", "substring", "toYear")
            *args: Function arguments (can be Column objects, values, or other functions)
            alias: Optional alias for the result column
        """
        self.func_name = func_name
        self.args = args
        self._alias = alias
        self._window_spec: Optional[WindowSpec] = None
    
    def alias(self, name: str) -> 'Function':
        """
        Set an alias for the function result.
        
        Args:
            name: Alias name
            
        Returns:
            New Function instance with alias
            
        Example:
            >>> length(crypto_quotes.pair).alias("pair_length")
        """
        new_func = Function(self.func_name, *self.args)
        new_func._alias = name
        new_func._window_spec = self._window_spec
        return new_func
    
    def over(self, window_spec: Optional[WindowSpec] = None) -> 'Function':
        """
        Add OVER clause for window functions.
        
        Args:
            window_spec: Optional WindowSpec object. If None, creates empty OVER()
            
        Returns:
            New Function instance with OVER clause
            
        Example:
            >>> from chpy.functions.window import rowNumber
            >>> from chpy.functions.base import WindowSpec
            >>> rowNumber().over(WindowSpec().partition_by(crypto_quotes.pair))
            >>> avg(crypto_quotes.price).over(WindowSpec().partition_by(crypto_quotes.exchange))
        """
        new_func = Function(self.func_name, *self.args)
        new_func._alias = self._alias
        if window_spec is None:
            window_spec = WindowSpec()
        new_func._window_spec = window_spec
        return new_func
    
    def _format_arg(self, arg: Any) -> str:
        """Format a function argument for SQL."""
        if isinstance(arg, Column):
            return arg.name
        elif isinstance(arg, (ColumnExpression, CombinedExpression)):
            # ColumnExpression and CombinedExpression require escape_string_func
            # Use a simple escape function (replace single quote with double single quote)
            def simple_escape(s: str) -> str:
                return s.replace("'", "''")
            return arg.to_sql(simple_escape)
        elif hasattr(arg, 'to_sql') and callable(getattr(arg, 'to_sql')):
            # Handle Function, AggregateFunction, or any object with to_sql method
            return arg.to_sql()
        elif isinstance(arg, str):
            escaped = arg.replace("'", "''")
            return f"'{escaped}'"  # Escape single quotes
        elif isinstance(arg, (list, tuple)):
            # Format array arguments
            formatted = ', '.join(self._format_arg(item) for item in arg)
            return f"({formatted})"
        elif arg is None:
            return "NULL"
        else:
            return str(arg)
    
    def to_sql(self) -> str:
        """
        Convert function to SQL string.
        
        Returns:
            SQL string representation (e.g., "length(pair) as pair_length")
        """
        if not self.args:
            sql = f"{self.func_name}()"
        else:
            formatted_args = ', '.join(self._format_arg(arg) for arg in self.args)
            sql = f"{self.func_name}({formatted_args})"
        
        # Add OVER clause if present
        if self._window_spec:
            sql += f" {self._window_spec.to_sql()}"
        
        if self._alias:
            sql += f" as {self._alias}"
        
        return sql
    
    def __str__(self) -> str:
        """String representation."""
        return self.to_sql()
    
    def __repr__(self) -> str:
        """Representation."""
        return f"Function({self.to_sql()})"
    
    def __add__(self, other: Any) -> 'Function':
        """Create addition expression: function + value or function + function"""
        return Function("plus", self, other)
    
    def __radd__(self, other: Any) -> 'Function':
        """Create reverse addition expression: value + function"""
        return Function("plus", other, self)
    
    def __sub__(self, other: Any) -> 'Function':
        """Create subtraction expression: function - value or function - function"""
        return Function("minus", self, other)
    
    def __rsub__(self, other: Any) -> 'Function':
        """Create reverse subtraction expression: value - function"""
        return Function("minus", other, self)
    
    def __mul__(self, other: Any) -> 'Function':
        """Create multiplication expression: function * value or function * function"""
        return Function("multiply", self, other)
    
    def __rmul__(self, other: Any) -> 'Function':
        """Create reverse multiplication expression: value * function"""
        return Function("multiply", other, self)
    
    def __truediv__(self, other: Any) -> 'Function':
        """Create division expression: function / value or function / function"""
        return Function("divide", self, other)
    
    def __rtruediv__(self, other: Any) -> 'Function':
        """Create reverse division expression: value / function"""
        return Function("divide", other, self)
    
    def __mod__(self, other: Any) -> 'Function':
        """Create modulo expression: function % value or function % function"""
        return Function("modulo", self, other)
    
    def __rmod__(self, other: Any) -> 'Function':
        """Create reverse modulo expression: value % function"""
        return Function("modulo", other, self)
    
    def __neg__(self) -> 'Function':
        """Create negation expression: -function"""
        return Function("negate", self)


class AggregateFunction:
    """
    Represents an aggregate function (AVG, COUNT, MIN, MAX, SUM, etc.).
    
    This is kept for backward compatibility and extends Function.
    
    Usage:
        >>> avg(crypto_quotes.best_bid_price)
        >>> avg(crypto_quotes.best_bid_price).alias("avg_bid")
        >>> count()
    """
    
    def __init__(self, func_name: str, column: Optional[Column] = None, alias: Optional[str] = None, second_column: Optional[Column] = None):
        """
        Initialize an aggregate function.
        
        Args:
            func_name: Function name (e.g., "avg", "count", "min", "max", "sum")
            column: Optional Column object to aggregate (None for count())
            alias: Optional alias for the result column
            second_column: Optional second column for two-argument functions (corr, covarPop, etc.)
        """
        # Preserve case for:
        # 1. Parameterized function names like "quantile(0.5)"
        # 2. CamelCase function names like "stddevPop", "varPop", "anyHeavy" (has both upper and lower)
        # 3. Functions that should remain lowercase (like "uniq")
        # Otherwise uppercase simple function names like "avg", "sum", "count" (all lowercase)
        has_upper = any(c.isupper() for c in func_name)
        has_lower = any(c.islower() for c in func_name)
        is_camel_case = has_upper and has_lower
        
        # Functions that should remain lowercase in ClickHouse
        lowercase_functions = {'uniq'}
        
        if '(' in func_name or is_camel_case or func_name.lower() in lowercase_functions:
            self.func_name = func_name
        else:
            self.func_name = func_name.upper()
        self.column = column
        self.second_column = second_column
        self._alias = alias
        self._window_spec: Optional[WindowSpec] = None
    
    def alias(self, name: str) -> 'AggregateFunction':
        """
        Set an alias for the aggregate function.
        
        Args:
            name: Alias name
            
        Returns:
            New AggregateFunction instance with alias
            
        Example:
            >>> avg(crypto_quotes.best_bid_price).alias("avg_bid")
        """
        new_func = AggregateFunction(self.func_name, self.column, second_column=self.second_column)
        new_func._alias = name
        new_func._window_spec = self._window_spec
        return new_func
    
    def over(self, window_spec: Optional[WindowSpec] = None) -> 'AggregateFunction':
        """
        Add OVER clause for window functions.
        
        Args:
            window_spec: Optional WindowSpec object. If None, creates empty OVER()
            
        Returns:
            New AggregateFunction instance with OVER clause
            
        Example:
            >>> from chpy.functions.base import WindowSpec
            >>> avg(crypto_quotes.price).over(WindowSpec().partition_by(crypto_quotes.exchange))
            >>> sum(crypto_quotes.amount).over(WindowSpec().order_by(crypto_quotes.timestamp))
        """
        new_func = AggregateFunction(self.func_name, self.column, second_column=self.second_column)
        new_func._alias = self._alias
        if window_spec is None:
            window_spec = WindowSpec()
        new_func._window_spec = window_spec
        return new_func
    
    def to_sql(self) -> str:
        """
        Convert aggregate function to SQL string.
        
        Returns:
            SQL string representation (e.g., "avg(best_bid_price) as avg_bid")
        """
        if self.second_column:
            # Two-column functions like corr, covarPop, covarSamp
            sql = f"{self.func_name}({self.column.name}, {self.second_column.name})"
        elif self.column:
            sql = f"{self.func_name}({self.column.name})"
        else:
            # For count() without column, use count(*) for SQL compatibility
            if self.func_name == "COUNT":
                sql = "count(*)"
            else:
                sql = f"{self.func_name}()"
        
        # Add OVER clause if present
        if self._window_spec:
            sql += f" {self._window_spec.to_sql()}"
        
        if self._alias:
            sql += f" as {self._alias}"
        
        return sql
    
    def __str__(self) -> str:
        """String representation."""
        return self.to_sql()
    
    def __repr__(self) -> str:
        """Representation."""
        return f"AggregateFunction({self.to_sql()})"
    
    def __add__(self, other: Any) -> 'Function':
        """Create addition expression: aggregate_function + value or aggregate_function + aggregate_function"""
        return Function("plus", self, other)
    
    def __radd__(self, other: Any) -> 'Function':
        """Create reverse addition expression: value + aggregate_function"""
        return Function("plus", other, self)
    
    def __sub__(self, other: Any) -> 'Function':
        """Create subtraction expression: aggregate_function - value or aggregate_function - aggregate_function"""
        return Function("minus", self, other)
    
    def __rsub__(self, other: Any) -> 'Function':
        """Create reverse subtraction expression: value - aggregate_function"""
        return Function("minus", other, self)
    
    def __mul__(self, other: Any) -> 'Function':
        """Create multiplication expression: aggregate_function * value or aggregate_function * aggregate_function"""
        return Function("multiply", self, other)
    
    def __rmul__(self, other: Any) -> 'Function':
        """Create reverse multiplication expression: value * aggregate_function"""
        return Function("multiply", other, self)
    
    def __truediv__(self, other: Any) -> 'Function':
        """Create division expression: aggregate_function / value or aggregate_function / aggregate_function"""
        return Function("divide", self, other)
    
    def __rtruediv__(self, other: Any) -> 'Function':
        """Create reverse division expression: value / aggregate_function"""
        return Function("divide", other, self)
    
    def __mod__(self, other: Any) -> 'Function':
        """Create modulo expression: aggregate_function % value or aggregate_function % aggregate_function"""
        return Function("modulo", self, other)
    
    def __rmod__(self, other: Any) -> 'Function':
        """Create reverse modulo expression: value % aggregate_function"""
        return Function("modulo", other, self)
    
    def __neg__(self) -> 'Function':
        """Create negation expression: -aggregate_function"""
        return Function("negate", self)


# Export WindowSpec for convenience
__all__ = ['Function', 'AggregateFunction', 'WindowSpec']

