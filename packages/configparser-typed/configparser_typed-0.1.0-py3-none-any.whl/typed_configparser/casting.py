"""Type conversion helpers for INI values."""

from typing import Any, get_origin, get_args
import configparser


def cast_value(value: str, target_type: type, file_path: str, section: str, key: str) -> Any:
    """
    Convert a string value from configparser to the target type.
    
    Args:
        value: The string value from the INI file
        target_type: The target Python type (int, float, bool, str, Optional[T])
        file_path: Path to the INI file (for error messages)
        section: Section name (for error messages)
        key: Key name (for error messages)
    
    Returns:
        The converted value
    
    Raises:
        TypeConversionError: If conversion fails
    """
    from typed_configparser.errors import TypeConversionError
    
    # Handle Optional[T] types
    origin = get_origin(target_type)
    if origin is not None:
        # Check if it's Optional[T] or Union[T, None]
        args = get_args(target_type)
        if len(args) == 2 and type(None) in args:
            # It's Optional[T], get the inner type
            inner_type = next(t for t in args if t is not type(None))
            return cast_value(value, inner_type, file_path, section, key)
        # For other Union types, just try the first one
        if args:
            return cast_value(value, args[0], file_path, section, key)
    
    # Handle None type directly
    if target_type is type(None):
        return None
    
    # Handle bool
    if target_type is bool:
        return cast_bool(value, file_path, section, key)
    
    # Handle int
    if target_type is int:
        return cast_int(value, file_path, section, key)
    
    # Handle float
    if target_type is float:
        return cast_float(value, file_path, section, key)
    
    # Handle str (no conversion needed, but validate)
    if target_type is str:
        return value
    
    # Unknown type
    raise TypeConversionError(file_path, section, key, value, target_type)


def cast_bool(value: str, file_path: str, section: str, key: str) -> bool:
    """Convert string to bool using configparser's boolean conversion."""
    # configparser.getboolean() handles: yes/no, true/false, on/off, 1/0
    try:
        # Create a temporary parser to use getboolean
        parser = configparser.ConfigParser()
        parser.add_section('temp')
        parser.set('temp', 'value', value)
        return parser.getboolean('temp', 'value')
    except (ValueError, configparser.Error):
        from typed_configparser.errors import TypeConversionError
        raise TypeConversionError(file_path, section, key, value, bool)


def cast_int(value: str, file_path: str, section: str, key: str) -> int:
    """Convert string to int."""
    try:
        return int(value)
    except ValueError:
        from typed_configparser.errors import TypeConversionError
        raise TypeConversionError(file_path, section, key, value, int)


def cast_float(value: str, file_path: str, section: str, key: str) -> float:
    """Convert string to float."""
    try:
        return float(value)
    except ValueError:
        from typed_configparser.errors import TypeConversionError
        raise TypeConversionError(file_path, section, key, value, float)

