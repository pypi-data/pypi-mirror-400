# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Configuration management for pytest-jux."""

import configparser
import os
from enum import Enum
from pathlib import Path
from typing import Any


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


class StorageMode(Enum):
    """Storage modes for signed reports."""

    LOCAL = "local"  # Store locally only
    API = "api"  # Publish to API only
    BOTH = "both"  # Store locally AND publish to API
    CACHE = "cache"  # Store locally, publish when available (offline queue)


class ConfigSchema:
    """Configuration schema definition."""

    _SCHEMA: dict[str, dict[str, Any]] = {
        # Core settings
        "jux_enabled": {
            "type": "bool",
            "default": False,
            "description": "Enable pytest-jux plugin",
        },
        "jux_sign": {
            "type": "bool",
            "default": False,
            "description": "Enable report signing",
            "requires": ["jux_key_path"],
        },
        "jux_publish": {
            "type": "bool",
            "default": False,
            "description": "Enable API publishing",
            "requires": ["jux_api_url"],
        },
        # Storage settings
        "jux_storage_mode": {
            "type": "enum",
            "default": "local",
            "choices": ["local", "api", "both", "cache"],
            "description": "Storage mode",
        },
        "jux_storage_path": {
            "type": "path",
            "default": None,
            "description": "Custom storage directory path",
        },
        # Signing settings
        "jux_key_path": {
            "type": "path",
            "default": None,
            "description": "Path to signing key (PEM format)",
        },
        "jux_cert_path": {
            "type": "path",
            "default": None,
            "description": "Path to X.509 certificate",
        },
        # API settings (Jux API v1.0.0)
        "jux_api_url": {
            "type": "str",
            "default": None,
            "description": "Jux API base URL (e.g., https://jux.example.com/api/v1)",
        },
        "jux_bearer_token": {
            "type": "str",
            "default": None,
            "description": "Bearer token for remote API authentication",
        },
        "jux_api_timeout": {
            "type": "int",
            "default": 30,
            "description": "API request timeout in seconds",
        },
        "jux_api_max_retries": {
            "type": "int",
            "default": 3,
            "description": "Maximum retry attempts for transient failures",
        },
    }

    @classmethod
    def get_schema(cls) -> dict[str, dict[str, Any]]:
        """Get the configuration schema."""
        return cls._SCHEMA.copy()


class ConfigurationManager:
    """Manages pytest-jux configuration from multiple sources."""

    def __init__(self) -> None:
        """Initialize configuration manager with defaults."""
        self._config: dict[str, Any] = {}
        self._sources: dict[str, str] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default values from schema."""
        schema = ConfigSchema.get_schema()
        for key, field_info in schema.items():
            default = field_info["default"]
            if default is not None:
                if field_info["type"] == "enum":
                    default = StorageMode(default)
                elif field_info["type"] == "path" and isinstance(default, str):
                    default = Path(default).expanduser()
            self._config[key] = default
            self._sources[key] = "default"

    def get(self, key: str) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value

        Raises:
            KeyError: If key doesn't exist
        """
        if key not in self._config:
            raise KeyError(f"Configuration key not found: {key}")
        return self._config[key]

    def set(self, key: str, value: Any, source: str = "explicit") -> None:
        """Set configuration value with validation.

        Args:
            key: Configuration key
            value: Configuration value
            source: Source of the configuration

        Raises:
            KeyError: If key doesn't exist in schema
            ConfigValidationError: If value doesn't match type
        """
        schema = ConfigSchema.get_schema()
        if key not in schema:
            raise KeyError(f"Unknown configuration key: {key}")

        field_info = schema[key]
        validated_value = self._validate_value(key, value, field_info)

        self._config[key] = validated_value
        self._sources[key] = source

    def _validate_value(self, key: str, value: Any, field_info: dict[str, Any]) -> Any:
        """Validate and convert configuration value.

        Args:
            key: Configuration key
            value: Value to validate
            field_info: Schema field information

        Returns:
            Validated and converted value

        Raises:
            ConfigValidationError: If validation fails
        """
        field_type = field_info["type"]

        # Handle None values
        if value is None:
            return None

        # Type-specific validation
        if field_type == "bool":
            return self._parse_bool(value)
        elif field_type == "enum":
            return self._parse_enum(key, value, field_info)
        elif field_type == "path":
            return self._parse_path(value)
        elif field_type == "int":
            return self._parse_int(value)
        elif field_type == "str":
            return str(value)
        else:
            return value

    def _parse_int(self, value: Any) -> int:
        """Parse integer value from string or int.

        Args:
            value: Value to parse

        Returns:
            Integer value

        Raises:
            ConfigValidationError: If value can't be parsed
        """
        if isinstance(value, int):
            return value

        if isinstance(value, str):
            try:
                return int(value)
            except ValueError as e:
                raise ConfigValidationError(
                    f"Invalid integer value: {value}. Expected: numeric string or int"
                ) from e

        raise ConfigValidationError(
            f"Invalid integer value type: {type(value)}. Expected: int or str"
        )

    def _parse_bool(self, value: Any) -> bool:
        """Parse boolean value from string or bool.

        Args:
            value: Value to parse

        Returns:
            Boolean value

        Raises:
            ConfigValidationError: If value can't be parsed
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True
            elif lower_value in ("false", "0", "no", "off"):
                return False
            else:
                raise ConfigValidationError(
                    f"Invalid boolean value: {value}. Expected: true/false, 1/0, yes/no, on/off"
                )

        raise ConfigValidationError(
            f"Invalid boolean value type: {type(value)}. Expected: bool or str"
        )

    def _parse_enum(
        self, key: str, value: Any, field_info: dict[str, Any]
    ) -> StorageMode:
        """Parse enum value from string or enum.

        Args:
            key: Configuration key
            value: Value to parse
            field_info: Schema field information

        Returns:
            Enum value

        Raises:
            ConfigValidationError: If value is invalid
        """
        # Handle string values (case-insensitive)
        if isinstance(value, str):
            try:
                # Try case-insensitive match
                value_lower = value.lower()
                for choice in field_info["choices"]:
                    if choice.lower() == value_lower:
                        return StorageMode(choice)
                raise ValueError(f"Invalid choice: {value}")
            except ValueError as e:
                choices = ", ".join(field_info["choices"])
                raise ConfigValidationError(
                    f"Invalid value for {key}: {value}. Valid choices: {choices}"
                ) from e

        # Handle StorageMode enum
        if isinstance(value, StorageMode):
            return value

        raise ConfigValidationError(
            f"Invalid value type for {key}: {type(value)}. Expected: str or StorageMode"
        )

    def _parse_path(self, value: Any) -> Path:
        """Parse path value with expansion.

        Args:
            value: Value to parse

        Returns:
            Path object with ~ expanded

        Raises:
            ConfigValidationError: If value is invalid
        """
        if isinstance(value, Path):
            return value.expanduser()

        if isinstance(value, str):
            return Path(value).expanduser()

        raise ConfigValidationError(
            f"Invalid path value type: {type(value)}. Expected: str or Path"
        )

    def load_from_dict(self, values: dict[str, Any], source: str = "dict") -> None:
        """Load configuration from dictionary.

        Args:
            values: Configuration values
            source: Source identifier
        """
        for key, value in values.items():
            if key in ConfigSchema.get_schema():
                try:
                    self.set(key, value, source)
                except ConfigValidationError:
                    # Skip invalid values during batch load
                    pass

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        schema = ConfigSchema.get_schema()
        for key in schema:
            env_var = key.upper()
            if env_var in os.environ:
                try:
                    self.set(key, os.environ[env_var], f"env:{env_var}")
                except ConfigValidationError:
                    # Skip invalid env vars
                    pass

    def load_from_file(self, path: Path) -> None:
        """Load configuration from INI file.

        Args:
            path: Path to configuration file
        """
        if not path.exists():
            return

        parser = configparser.ConfigParser()
        parser.read(path)

        if "jux" in parser:
            section = parser["jux"]
            # Map INI keys (without jux_ prefix) to config keys
            for ini_key, value in section.items():
                config_key = f"jux_{ini_key}"
                if config_key in ConfigSchema.get_schema():
                    try:
                        self.set(config_key, value, f"file:{path}")
                    except ConfigValidationError:
                        # Skip invalid values
                        pass

    def validate(self, strict: bool = False) -> list[str]:
        """Validate configuration.

        Args:
            strict: If True, check for missing required dependencies

        Returns:
            List of validation errors/warnings
        """
        errors: list[str] = []
        schema = ConfigSchema.get_schema()

        if strict:
            for key, field_info in schema.items():
                # Check required dependencies
                if "requires" in field_info:
                    value = self._config.get(key)
                    if value:  # If this feature is enabled
                        for required_key in field_info["requires"]:
                            required_value = self._config.get(required_key)
                            if not required_value:
                                errors.append(
                                    f"Warning: {key} enabled but {required_key} not set"
                                )

        return errors

    def get_source(self, key: str) -> str:
        """Get source of configuration value.

        Args:
            key: Configuration key

        Returns:
            Source identifier

        Raises:
            KeyError: If key doesn't exist
        """
        if key not in self._sources:
            raise KeyError(f"Configuration key not found: {key}")
        return self._sources[key]

    def dump(self, include_sources: bool = False) -> dict[str, Any]:
        """Dump current configuration.

        Args:
            include_sources: If True, include source information

        Returns:
            Configuration dictionary
        """
        if include_sources:
            return {
                key: {"value": value, "source": self._sources[key]}
                for key, value in self._config.items()
            }
        else:
            return self._config.copy()
