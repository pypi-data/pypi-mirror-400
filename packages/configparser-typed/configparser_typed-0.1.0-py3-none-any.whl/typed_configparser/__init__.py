"""A typed, validated wrapper around Python's built-in configparser."""

from typed_configparser.loader import load_section
from typed_configparser.errors import (
    ConfigParserError,
    MissingKeyError,
    UnknownKeyError,
    TypeConversionError,
)

__all__ = [
    "load_section",
    "ConfigParserError",
    "MissingKeyError",
    "UnknownKeyError",
    "TypeConversionError",
]

__version__ = "0.1.0"

