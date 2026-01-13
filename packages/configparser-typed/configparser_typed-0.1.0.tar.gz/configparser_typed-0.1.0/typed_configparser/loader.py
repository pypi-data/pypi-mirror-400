"""Core loader logic for typed-configparser."""

import configparser
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Type, TypeVar, get_type_hints
from pathlib import Path

from typed_configparser.errors import MissingKeyError, UnknownKeyError
from typed_configparser.casting import cast_value

T = TypeVar('T')


def load_section(
    path: str | Path,
    section: str,
    model: Type[T],
    *,
    strict: bool = True,
) -> T:
    """
    Load a section from an INI file into a typed dataclass or Pydantic model.
    
    Args:
        path: Path to the INI file
        section: Name of the section to load
        model: Dataclass or Pydantic model class
        strict: If True, raise error on unknown keys (default: True)
    
    Returns:
        An instance of the model with values from the INI file
    
    Raises:
        MissingKeyError: If a required key is missing
        UnknownKeyError: If an unknown key is found (when strict=True)
        TypeConversionError: If a value cannot be converted to the expected type
        FileNotFoundError: If the INI file doesn't exist
        configparser.Error: For INI parsing errors
    """
    path_str = str(path)
    
    # Read the INI file
    parser = configparser.ConfigParser()
    parser.read(path_str)
    
    # Check if section exists
    if not parser.has_section(section):
        raise configparser.NoSectionError(f"Section '[{section}]' not found in '{path_str}'")
    
    # Get model fields and type hints
    if is_dataclass(model):
        model_fields = {f.name: f for f in fields(model)}
        type_hints = get_type_hints(model)
    else:
        # Assume Pydantic model
        try:
            model_fields = {name: field for name, field in model.model_fields.items()}
            type_hints = {name: field.annotation for name, field in model_fields.items()}
        except AttributeError:
            raise TypeError(
                f"Model must be a dataclass or Pydantic model, got {type(model)}"
            )
    
    # Collect values from INI section
    result_dict: dict[str, Any] = {}
    ini_keys = set(parser.options(section))
    model_keys = set(model_fields.keys())
    
    # Process each model field
    for field_name, field_info in model_fields.items():
        field_type = type_hints.get(field_name, str)
        
        # Check if key exists in INI
        if field_name not in ini_keys:
            # Check if field has a default value
            if is_dataclass(model):
                has_default = (
                    field_info.default is not MISSING
                    or field_info.default_factory is not MISSING
                )
            else:
                # Pydantic
                has_default = not field_info.is_required()
            
            if not has_default:
                raise MissingKeyError(path_str, section, field_name)
            
            # Use default value (will be set by model constructor)
            continue
        
        # Get and convert value
        raw_value = parser.get(section, field_name)
        result_dict[field_name] = cast_value(
            raw_value, field_type, path_str, section, field_name
        )
    
    # Check for unknown keys (strict mode)
    if strict:
        unknown_keys = ini_keys - model_keys
        if unknown_keys:
            # Raise error for the first unknown key
            raise UnknownKeyError(path_str, section, next(iter(unknown_keys)))
    
    # Create model instance
    if is_dataclass(model):
        return model(**result_dict)
    else:
        # Pydantic
        return model(**result_dict)

