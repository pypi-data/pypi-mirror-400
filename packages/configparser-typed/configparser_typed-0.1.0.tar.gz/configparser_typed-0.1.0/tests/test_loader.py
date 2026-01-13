"""Tests for typed-configparser loader functionality."""

import tempfile
from pathlib import Path
from dataclasses import dataclass
import pytest

from typed_configparser import load_section
from typed_configparser.errors import (
    MissingKeyError,
    UnknownKeyError,
    TypeConversionError,
)


def create_temp_ini(content: str) -> Path:
    """Create a temporary INI file with the given content."""
    fd, path = tempfile.mkstemp(suffix='.ini')
    with open(fd, 'w') as f:
        f.write(content)
    return Path(path)


@dataclass
class ServerConfig:
    port: int
    debug: bool = False


@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    timeout: float = 30.0


@dataclass
class OptionalConfig:
    required: str
    optional: str | None = None


def test_successful_load():
    """Test successful loading of a section."""
    ini_content = """[server]
port = 8000
debug = true
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "server", ServerConfig)
        assert isinstance(config.port, int)
        assert config.port == 8000
        assert isinstance(config.debug, bool)
        assert config.debug is True
    finally:
        ini_file.unlink()


def test_missing_key():
    """Test error when a required key is missing."""
    ini_content = """[server]
debug = true
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        with pytest.raises(MissingKeyError) as exc_info:
            load_section(ini_file, "server", ServerConfig)
        assert exc_info.value.key == "port"
        assert exc_info.value.section == "server"
    finally:
        ini_file.unlink()


def test_unknown_key_strict():
    """Test error when an unknown key is found in strict mode."""
    ini_content = """[server]
port = 8000
debug = true
unknown = value
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        with pytest.raises(UnknownKeyError) as exc_info:
            load_section(ini_file, "server", ServerConfig, strict=True)
        assert exc_info.value.key == "unknown"
        assert exc_info.value.section == "server"
    finally:
        ini_file.unlink()


def test_unknown_key_lenient():
    """Test that unknown keys are ignored in lenient mode."""
    ini_content = """[server]
port = 8000
debug = true
unknown = value
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "server", ServerConfig, strict=False)
        assert config.port == 8000
        assert config.debug is True
    finally:
        ini_file.unlink()


def test_type_conversion_int():
    """Test conversion to int."""
    ini_content = """[server]
port = 8000
debug = false
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "server", ServerConfig)
        assert isinstance(config.port, int)
        assert config.port == 8000
    finally:
        ini_file.unlink()


def test_type_conversion_bool():
    """Test conversion to bool."""
    ini_content = """[server]
port = 8000
debug = yes
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "server", ServerConfig)
        assert isinstance(config.debug, bool)
        assert config.debug is True
    finally:
        ini_file.unlink()


def test_type_conversion_float():
    """Test conversion to float."""
    ini_content = """[database]
host = localhost
port = 5432
name = mydb
timeout = 45.5
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "database", DatabaseConfig)
        assert isinstance(config.timeout, float)
        assert config.timeout == 45.5
    finally:
        ini_file.unlink()


def test_wrong_type():
    """Test error when value cannot be converted to expected type."""
    ini_content = """[server]
port = not_a_number
debug = false
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        with pytest.raises(TypeConversionError) as exc_info:
            load_section(ini_file, "server", ServerConfig)
        assert exc_info.value.key == "port"
        assert exc_info.value.target_type == int
    finally:
        ini_file.unlink()


def test_default_value():
    """Test that default values are used when key is missing."""
    ini_content = """[server]
port = 8000
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "server", ServerConfig)
        assert config.debug is False  # default value
        assert config.port == 8000
    finally:
        ini_file.unlink()


def test_optional_field():
    """Test Optional fields."""
    ini_content = """[config]
required = value
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "config", OptionalConfig)
        assert config.required == "value"
        assert config.optional is None
    finally:
        ini_file.unlink()


def test_optional_field_with_value():
    """Test Optional fields with a value."""
    ini_content = """[config]
required = value
optional = optional_value
"""
    ini_file = create_temp_ini(ini_content)
    
    try:
        config = load_section(ini_file, "config", OptionalConfig)
        assert config.required == "value"
        assert config.optional == "optional_value"
    finally:
        ini_file.unlink()


def test_bool_variants():
    """Test various boolean string representations."""
    test_cases = [
        ("true", True),
        ("false", False),
        ("yes", True),
        ("no", False),
        ("on", True),
        ("off", False),
        ("1", True),
        ("0", False),
    ]
    
    for bool_str, expected in test_cases:
        ini_content = f"""[server]
port = 8000
debug = {bool_str}
"""
        ini_file = create_temp_ini(ini_content)
        
        try:
            config = load_section(ini_file, "server", ServerConfig)
            assert config.debug == expected, f"Failed for '{bool_str}'"
        finally:
            ini_file.unlink()

