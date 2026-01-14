# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for configuration management."""

from pathlib import Path

import pytest

from pytest_jux.config import (
    ConfigSchema,
    ConfigurationManager,
    ConfigValidationError,
    StorageMode,
)


class TestConfigSchema:
    """Tests for configuration schema definition."""

    def test_schema_has_all_required_fields(self) -> None:
        """Configuration schema should define all required fields."""
        schema = ConfigSchema.get_schema()

        # Core settings
        assert "jux_enabled" in schema
        assert "jux_sign" in schema
        assert "jux_publish" in schema

        # Storage settings
        assert "jux_storage_mode" in schema
        assert "jux_storage_path" in schema

        # Signing settings
        assert "jux_key_path" in schema
        assert "jux_cert_path" in schema

        # API settings
        assert "jux_api_url" in schema
        assert "jux_bearer_token" in schema
        assert "jux_api_timeout" in schema
        assert "jux_api_max_retries" in schema

    def test_schema_field_has_type_and_default(self) -> None:
        """Each schema field should have type and default value."""
        schema = ConfigSchema.get_schema()
        field = schema["jux_enabled"]

        assert "type" in field
        assert "default" in field
        assert field["type"] == "bool"
        assert field["default"] is False

    def test_schema_enum_field_has_choices(self) -> None:
        """Enum fields should define valid choices."""
        schema = ConfigSchema.get_schema()
        field = schema["jux_storage_mode"]

        assert field["type"] == "enum"
        assert "choices" in field
        assert set(field["choices"]) == {"local", "api", "both", "cache"}
        assert field["default"] == "local"

    def test_schema_field_with_dependencies(self) -> None:
        """Fields with dependencies should declare them."""
        schema = ConfigSchema.get_schema()
        field = schema["jux_sign"]

        assert "requires" in field
        assert "jux_key_path" in field["requires"]


class TestStorageMode:
    """Tests for StorageMode enum."""

    def test_storage_mode_values(self) -> None:
        """StorageMode enum should have all expected values."""
        assert StorageMode.LOCAL.value == "local"
        assert StorageMode.API.value == "api"
        assert StorageMode.BOTH.value == "both"
        assert StorageMode.CACHE.value == "cache"

    def test_storage_mode_from_string(self) -> None:
        """StorageMode should be constructable from string."""
        assert StorageMode("local") == StorageMode.LOCAL
        assert StorageMode("api") == StorageMode.API
        assert StorageMode("both") == StorageMode.BOTH
        assert StorageMode("cache") == StorageMode.CACHE

    def test_storage_mode_invalid_value(self) -> None:
        """Invalid storage mode should raise ValueError."""
        with pytest.raises(ValueError):
            StorageMode("invalid")


class TestConfigurationManager:
    """Tests for configuration manager."""

    def test_default_configuration(self) -> None:
        """Default configuration should have disabled state."""
        config = ConfigurationManager()

        assert config.get("jux_enabled") is False
        assert config.get("jux_sign") is False
        assert config.get("jux_publish") is False
        assert config.get("jux_storage_mode") == StorageMode.LOCAL

    def test_set_and_get_value(self) -> None:
        """Should be able to set and get configuration values."""
        config = ConfigurationManager()

        config.set("jux_enabled", True)
        assert config.get("jux_enabled") is True

        config.set("jux_storage_mode", StorageMode.CACHE)
        assert config.get("jux_storage_mode") == StorageMode.CACHE

    def test_get_nonexistent_key_raises_error(self) -> None:
        """Getting non-existent key should raise KeyError."""
        config = ConfigurationManager()

        with pytest.raises(KeyError):
            config.get("nonexistent_key")

    def test_set_invalid_type_raises_error(self) -> None:
        """Setting value with wrong type should raise validation error."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError):
            config.set("jux_enabled", "not a bool")

    def test_set_invalid_enum_value_raises_error(self) -> None:
        """Setting invalid enum value should raise validation error."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError):
            config.set("jux_storage_mode", "invalid_mode")

    def test_load_from_dict(self) -> None:
        """Should load configuration from dictionary."""
        config = ConfigurationManager()
        values = {
            "jux_enabled": True,
            "jux_sign": True,
            "jux_key_path": "/path/to/key.pem",
        }

        config.load_from_dict(values)

        assert config.get("jux_enabled") is True
        assert config.get("jux_sign") is True
        assert config.get("jux_key_path") == Path("/path/to/key.pem")

    def test_load_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should load configuration from environment variables."""
        monkeypatch.setenv("JUX_ENABLED", "true")
        monkeypatch.setenv("JUX_SIGN", "true")
        monkeypatch.setenv("JUX_STORAGE_MODE", "cache")

        config = ConfigurationManager()
        config.load_from_env()

        assert config.get("jux_enabled") is True
        assert config.get("jux_sign") is True
        assert config.get("jux_storage_mode") == StorageMode.CACHE

    def test_load_from_file(self, tmp_path: Path) -> None:
        """Should load configuration from INI file."""
        config_file = tmp_path / "jux.conf"
        config_file.write_text("""[jux]
enabled = true
sign = true
key_path = ~/.config/jux/keys/key.pem
storage_mode = both
""")

        config = ConfigurationManager()
        config.load_from_file(config_file)

        assert config.get("jux_enabled") is True
        assert config.get("jux_sign") is True
        assert config.get("jux_storage_mode") == StorageMode.BOTH

    def test_configuration_precedence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Configuration sources should follow precedence order."""
        # 1. Set file config (lowest priority)
        config_file = tmp_path / "jux.conf"
        config_file.write_text("[jux]\nenabled = false\n")

        # 2. Set env var (medium priority)
        monkeypatch.setenv("JUX_ENABLED", "true")

        config = ConfigurationManager()
        config.load_from_file(config_file)
        config.load_from_env()

        # Env var should override file
        assert config.get("jux_enabled") is True

        # 3. Set explicit value (highest priority)
        config.set("jux_enabled", False)
        assert config.get("jux_enabled") is False

    def test_validate_success(self) -> None:
        """Validation should pass for valid configuration."""
        config = ConfigurationManager()
        config.set("jux_enabled", True)
        config.set("jux_sign", True)
        config.set("jux_key_path", Path("/path/to/key.pem"))

        # Should not raise
        errors = config.validate()
        assert len(errors) == 0

    def test_validate_missing_dependencies(self) -> None:
        """Validation should detect missing required dependencies."""
        config = ConfigurationManager()
        config.set("jux_enabled", True)
        config.set("jux_sign", True)
        # Missing jux_key_path

        errors = config.validate(strict=True)
        assert len(errors) > 0
        assert any("jux_key_path" in err for err in errors)

    def test_validate_publish_without_api_url(self) -> None:
        """Validation should warn if publish enabled without API URL."""
        config = ConfigurationManager()
        config.set("jux_enabled", True)
        config.set("jux_publish", True)
        # Missing jux_api_url

        errors = config.validate(strict=True)
        assert len(errors) > 0
        assert any("jux_api_url" in err for err in errors)

    def test_get_source_tracking(self, tmp_path: Path) -> None:
        """Should track where each config value came from."""
        config_file = tmp_path / "jux.conf"
        config_file.write_text("[jux]\nenabled = true\n")

        config = ConfigurationManager()
        config.load_from_file(config_file)

        source = config.get_source("jux_enabled")
        assert source == f"file:{config_file}"

    def test_dump_configuration(self) -> None:
        """Should dump current configuration as dict."""
        config = ConfigurationManager()
        config.set("jux_enabled", True)
        config.set("jux_sign", False)

        dump = config.dump()

        assert isinstance(dump, dict)
        assert dump["jux_enabled"] is True
        assert dump["jux_sign"] is False

    def test_dump_with_sources(self, tmp_path: Path) -> None:
        """Should dump configuration with source tracking."""
        config_file = tmp_path / "jux.conf"
        config_file.write_text("[jux]\nenabled = true\n")

        config = ConfigurationManager()
        config.load_from_file(config_file)

        dump = config.dump(include_sources=True)

        assert "jux_enabled" in dump
        assert dump["jux_enabled"]["value"] is True
        assert "source" in dump["jux_enabled"]


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_path_expansion(self) -> None:
        """Path values should support ~ expansion."""
        config = ConfigurationManager()
        config.set("jux_key_path", "~/keys/key.pem")

        key_path = config.get("jux_key_path")
        assert isinstance(key_path, Path)
        assert not str(key_path).startswith("~")

    def test_boolean_from_string(self) -> None:
        """Boolean values should parse from strings."""
        config = ConfigurationManager()

        config.load_from_dict({"jux_enabled": "true"})
        assert config.get("jux_enabled") is True

        config.load_from_dict({"jux_enabled": "false"})
        assert config.get("jux_enabled") is False

        config.load_from_dict({"jux_enabled": "1"})
        assert config.get("jux_enabled") is True

        config.load_from_dict({"jux_enabled": "0"})
        assert config.get("jux_enabled") is False

    def test_enum_case_insensitive(self) -> None:
        """Enum values should be case-insensitive."""
        config = ConfigurationManager()

        config.load_from_dict({"jux_storage_mode": "LOCAL"})
        assert config.get("jux_storage_mode") == StorageMode.LOCAL

        config.load_from_dict({"jux_storage_mode": "Cache"})
        assert config.get("jux_storage_mode") == StorageMode.CACHE


class TestConfigErrorPaths:
    """Tests for config error handling and edge cases."""

    def test_parse_bool_invalid_string(self) -> None:
        """Should raise error for invalid boolean string."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid boolean value"):
            config.set("jux_enabled", "maybe")

    def test_parse_bool_invalid_type(self) -> None:
        """Should raise error for invalid boolean type."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid boolean value type"):
            config.set("jux_enabled", 123)

    def test_parse_enum_invalid_type(self) -> None:
        """Should raise error for invalid enum type."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid value type"):
            config.set("jux_storage_mode", 123)

    def test_parse_path_invalid_type(self) -> None:
        """Should raise error for invalid path type."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid path value type"):
            config.set("jux_key_path", 123)

    def test_set_unknown_key(self) -> None:
        """Should raise error for unknown configuration key."""
        config = ConfigurationManager()

        with pytest.raises(KeyError, match="Unknown configuration key"):
            config.set("unknown_key", "value")

    def test_get_source_nonexistent_key(self) -> None:
        """Should raise error when getting source for nonexistent key."""
        config = ConfigurationManager()

        with pytest.raises(KeyError, match="Configuration key not found"):
            config.get_source("nonexistent_key")

    def test_load_from_env_invalid_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should skip invalid env var values."""
        config = ConfigurationManager()

        # Set invalid boolean value in env
        monkeypatch.setenv("JUX_ENABLED", "invalid")

        # Should not raise error, just skip the invalid value
        config.load_from_env()

        # Should still have default value
        assert config.get("jux_enabled") is False

    def test_load_from_dict_invalid_value(self) -> None:
        """Should skip invalid values during batch load."""
        config = ConfigurationManager()

        # Invalid enum value should be skipped
        config.load_from_dict({"jux_storage_mode": "invalid_mode"})

        # Should still have default value
        assert config.get("jux_storage_mode") == StorageMode.LOCAL

    def test_load_from_file_nonexistent(self, tmp_path: Path) -> None:
        """Should handle nonexistent config file gracefully."""
        config = ConfigurationManager()
        nonexistent_file = tmp_path / "nonexistent.ini"

        # Should not raise error
        config.load_from_file(nonexistent_file)

        # Should still have defaults
        assert config.get("jux_enabled") is False

    def test_load_from_file_invalid_value(self, tmp_path: Path) -> None:
        """Should skip invalid values in config file."""
        config_file = tmp_path / "config.ini"
        config_file.write_text(
            """[jux]
enabled = invalid_bool
storage_mode = invalid_mode
"""
        )

        config = ConfigurationManager()
        config.load_from_file(config_file)

        # Should still have default values (invalid ones skipped)
        assert config.get("jux_enabled") is False
        assert config.get("jux_storage_mode") == StorageMode.LOCAL
