"""
ClickHouse-specific data type builders.
Provides helper classes and functions for constructing complex ClickHouse types.
"""

from typing import Union, List, Dict, Any, Optional


class TypeBuilder:
    """Base class for type builders."""
    
    def __str__(self) -> str:
        """Return SQL type string."""
        raise NotImplementedError
    
    def __repr__(self) -> str:
        """Return representation."""
        return f"{self.__class__.__name__}({str(self)})"


class LowCardinality(TypeBuilder):
    """
    LowCardinality type modifier for ClickHouse.
    
    Usage:
        >>> LowCardinality("String")
        >>> LowCardinality(Nullable("String"))
    """
    
    def __init__(self, inner_type: Union[str, TypeBuilder]):
        """
        Initialize LowCardinality type.
        
        Args:
            inner_type: Inner type (string or TypeBuilder instance)
        """
        self.inner_type = inner_type
    
    def __str__(self) -> str:
        inner = str(self.inner_type)
        return f"LowCardinality({inner})"


class Nullable(TypeBuilder):
    """
    Nullable type modifier for ClickHouse.
    
    Usage:
        >>> Nullable("String")
        >>> Nullable(Array("Int64"))
    """
    
    def __init__(self, inner_type: Union[str, TypeBuilder]):
        """
        Initialize Nullable type.
        
        Args:
            inner_type: Inner type (string or TypeBuilder instance)
        """
        self.inner_type = inner_type
    
    def __str__(self) -> str:
        inner = str(self.inner_type)
        return f"Nullable({inner})"


class Array(TypeBuilder):
    """
    Array type for ClickHouse.
    
    Usage:
        >>> Array("Int64")
        >>> Array(Nullable("String"))
        >>> Array(LowCardinality("String"))
    """
    
    def __init__(self, inner_type: Union[str, TypeBuilder]):
        """
        Initialize Array type.
        
        Args:
            inner_type: Inner type (string or TypeBuilder instance)
        """
        self.inner_type = inner_type
    
    def __str__(self) -> str:
        inner = str(self.inner_type)
        return f"Array({inner})"


class Tuple(TypeBuilder):
    """
    Tuple type for ClickHouse.
    
    Usage:
        >>> Tuple("String", "Int64", "Float64")
        >>> Tuple(Nullable("String"), Array("Int64"))
    """
    
    def __init__(self, *types: Union[str, TypeBuilder]):
        """
        Initialize Tuple type.
        
        Args:
            *types: Type arguments (strings or TypeBuilder instances)
        """
        self.types = types
    
    def __str__(self) -> str:
        type_strs = [str(t) for t in self.types]
        return f"Tuple({', '.join(type_strs)})"


class Map(TypeBuilder):
    """
    Map type for ClickHouse.
    
    Usage:
        >>> Map("String", "Int64")
        >>> Map("String", Nullable("Float64"))
    """
    
    def __init__(self, key_type: Union[str, TypeBuilder], value_type: Union[str, TypeBuilder]):
        """
        Initialize Map type.
        
        Args:
            key_type: Key type (string or TypeBuilder instance)
            value_type: Value type (string or TypeBuilder instance)
        """
        self.key_type = key_type
        self.value_type = value_type
    
    def __str__(self) -> str:
        return f"Map({str(self.key_type)}, {str(self.value_type)})"


class Nested(TypeBuilder):
    """
    Nested type for ClickHouse.
    
    Usage:
        >>> Nested("name", "String", "age", "Int64")
        >>> Nested(("name", "String"), ("age", "Int64"))
    """
    
    def __init__(self, *fields: Union[tuple, str]):
        """
        Initialize Nested type.
        
        Args:
            *fields: Field definitions as tuples (name, type) or alternating name, type strings
                    Examples:
                    - Nested("name", "String", "age", "Int64")
                    - Nested(("name", "String"), ("age", "Int64"))
        """
        if not fields:
            raise ValueError("Nested type requires at least one field")
        
        # Normalize to list of tuples
        self.fields = []
        if isinstance(fields[0], tuple):
            # Already in tuple format
            self.fields = list(fields)
        else:
            # Alternating name, type format
            if len(fields) % 2 != 0:
                raise ValueError("Nested type requires even number of arguments (name, type pairs)")
            for i in range(0, len(fields), 2):
                self.fields.append((fields[i], fields[i + 1]))
    
    def __str__(self) -> str:
        field_strs = [f"{name} {str(type_)}" for name, type_ in self.fields]
        return f"Nested({', '.join(field_strs)})"


class FixedString(TypeBuilder):
    """
    FixedString type for ClickHouse.
    
    Usage:
        >>> FixedString(100)
    """
    
    def __init__(self, length: int):
        """
        Initialize FixedString type.
        
        Args:
            length: Fixed string length
        """
        if length <= 0:
            raise ValueError("FixedString length must be positive")
        self.length = length
    
    def __str__(self) -> str:
        return f"FixedString({self.length})"


class Enum(TypeBuilder):
    """
    Enum type for ClickHouse.
    
    Usage:
        >>> Enum("red", 1, "green", 2, "blue", 3)
        >>> Enum({"red": 1, "green": 2, "blue": 3})
    """
    
    def __init__(self, *values: Union[str, int, Dict[str, int]]):
        """
        Initialize Enum type.
        
        Args:
            *values: Enum values as alternating name, value pairs or a single dict
                    Examples:
                    - Enum("red", 1, "green", 2)
                    - Enum({"red": 1, "green": 2})
        """
        if not values:
            raise ValueError("Enum type requires at least one value")
        
        if len(values) == 1 and isinstance(values[0], dict):
            # Single dict argument
            self.values = values[0]
        else:
            # Alternating name, value format
            if len(values) % 2 != 0:
                raise ValueError("Enum type requires even number of arguments (name, value pairs)")
            self.values = {}
            for i in range(0, len(values), 2):
                name = values[i]
                value = values[i + 1]
                if not isinstance(name, str):
                    raise ValueError(f"Enum name must be string, got {type(name)}")
                if not isinstance(value, int):
                    raise ValueError(f"Enum value must be int, got {type(value)}")
                self.values[name] = value
    
    def __str__(self) -> str:
        value_strs = [f"'{name}' = {value}" for name, value in self.values.items()]
        return f"Enum({', '.join(value_strs)})"


class IPv4(TypeBuilder):
    """IPv4 type for ClickHouse."""
    
    def __str__(self) -> str:
        return "IPv4"


class IPv6(TypeBuilder):
    """IPv6 type for ClickHouse."""
    
    def __str__(self) -> str:
        return "IPv6"


class UUID(TypeBuilder):
    """UUID type for ClickHouse."""
    
    def __str__(self) -> str:
        return "UUID"


class Date(TypeBuilder):
    """Date type for ClickHouse."""
    
    def __str__(self) -> str:
        return "Date"


class DateTime(TypeBuilder):
    """
    DateTime type for ClickHouse.
    
    Usage:
        >>> DateTime()
        >>> DateTime("UTC")
    """
    
    def __init__(self, timezone: Optional[str] = None):
        """
        Initialize DateTime type.
        
        Args:
            timezone: Optional timezone (e.g., "UTC", "America/New_York")
        """
        self.timezone = timezone
    
    def __str__(self) -> str:
        if self.timezone:
            return f"DateTime({self.timezone})"
        return "DateTime"


class DateTime64(TypeBuilder):
    """
    DateTime64 type for ClickHouse.
    
    Usage:
        >>> DateTime64(3)  # 3 decimal places
        >>> DateTime64(3, "UTC")
    """
    
    def __init__(self, precision: int = 3, timezone: Optional[str] = None):
        """
        Initialize DateTime64 type.
        
        Args:
            precision: Decimal precision (0-9)
            timezone: Optional timezone
        """
        if not (0 <= precision <= 9):
            raise ValueError("DateTime64 precision must be between 0 and 9")
        self.precision = precision
        self.timezone = timezone
    
    def __str__(self) -> str:
        parts = [str(self.precision)]
        if self.timezone:
            parts.append(f"'{self.timezone}'")
        return f"DateTime64({', '.join(parts)})"


# Convenience functions for common type combinations
def LowCardinalityNullable(inner_type: Union[str, TypeBuilder]) -> LowCardinality:
    """Create LowCardinality(Nullable(type))."""
    return LowCardinality(Nullable(inner_type))


def NullableArray(inner_type: Union[str, TypeBuilder]) -> Nullable:
    """Create Nullable(Array(type))."""
    return Nullable(Array(inner_type))


def ArrayNullable(inner_type: Union[str, TypeBuilder]) -> Array:
    """Create Array(Nullable(type))."""
    return Array(Nullable(inner_type))

