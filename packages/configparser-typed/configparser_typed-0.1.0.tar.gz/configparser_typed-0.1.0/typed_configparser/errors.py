"""Custom exceptions for typed-configparser."""


class ConfigParserError(Exception):
    """Base exception for all typed-configparser errors."""

    pass


class MissingKeyError(ConfigParserError):
    """Raised when a required key is missing from the INI section."""

    def __init__(self, file_path: str, section: str, key: str):
        self.file_path = file_path
        self.section = section
        self.key = key
        super().__init__(
            f"Missing required key '{key}' in section '[{section}]' "
            f"of file '{file_path}'"
        )


class UnknownKeyError(ConfigParserError):
    """Raised when an unknown key is found in the INI section."""

    def __init__(self, file_path: str, section: str, key: str):
        self.file_path = file_path
        self.section = section
        self.key = key
        super().__init__(
            f"Unknown key '{key}' in section '[{section}]' "
            f"of file '{file_path}'"
        )


class TypeConversionError(ConfigParserError):
    """Raised when a value cannot be converted to the expected type."""

    def __init__(
        self, file_path: str, section: str, key: str, value: str, target_type: type
    ):
        self.file_path = file_path
        self.section = section
        self.key = key
        self.value = value
        self.target_type = target_type
        super().__init__(
            f"Cannot convert '{value}' to {target_type.__name__} "
            f"for key '{key}' in section '[{section}]' of file '{file_path}'"
        )

