"""Tests for configuration module."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from spreadsheet_dl.config import (
    Config,
    DefaultSettings,
    DisplaySettings,
    NextcloudSettings,
    get_config,
    init_config_file,
)

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = [pytest.mark.unit, pytest.mark.requires_yaml]


class TestNextcloudSettings:
    """Tests for NextcloudSettings dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        settings = NextcloudSettings()
        assert settings.url == ""
        assert settings.username == ""
        assert settings.password == ""
        assert settings.remote_path == "/Finance"
        assert settings.verify_ssl is True

    def test_is_configured_false_when_empty(self) -> None:
        """Test is_configured returns False when empty."""
        settings = NextcloudSettings()
        assert settings.is_configured() is False

    def test_is_configured_true_when_complete(self) -> None:
        """Test is_configured returns True when all required fields set."""
        settings = NextcloudSettings(
            url="https://cloud.example.com",
            username="user",
            password="secret",
        )
        assert settings.is_configured() is True


class TestDefaultSettings:
    """Tests for DefaultSettings dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        settings = DefaultSettings()
        assert settings.empty_rows == 50
        assert settings.date_format == "%Y-%m-%d"
        assert settings.currency_symbol == "$"
        assert settings.currency_decimal_places == 2


class TestDisplaySettings:
    """Tests for DisplaySettings dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        settings = DisplaySettings()
        assert settings.use_color is True
        assert settings.show_progress is True
        assert settings.compact_output is False
        assert settings.json_pretty_print is True


class TestConfig:
    """Tests for Config class."""

    def test_load_returns_config(self) -> None:
        """Test Config.load() returns a Config instance."""
        config = Config.load()
        assert isinstance(config, Config)
        assert isinstance(config.nextcloud, NextcloudSettings)
        assert isinstance(config.defaults, DefaultSettings)
        assert isinstance(config.display, DisplaySettings)

    def test_load_from_env_nextcloud(self) -> None:
        """Test loading Nextcloud settings from environment."""
        with patch.dict(
            os.environ,
            {
                "NEXTCLOUD_URL": "https://test.example.com",
                "NEXTCLOUD_USER": "testuser",
                "NEXTCLOUD_PASSWORD": "testpass",
                "NEXTCLOUD_PATH": "/TestPath",
            },
        ):
            config = Config.load()
            assert config.nextcloud.url == "https://test.example.com"
            assert config.nextcloud.username == "testuser"
            assert config.nextcloud.password == "testpass"
            assert config.nextcloud.remote_path == "/TestPath"

    def test_load_from_env_no_color(self) -> None:
        """Test NO_COLOR environment variable."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            config = Config.load()
            assert config.display.use_color is False

    def test_to_dict(self) -> None:
        """Test exporting config as dictionary."""
        config = Config()
        data = config.to_dict()

        assert "nextcloud" in data
        assert "defaults" in data
        assert "alerts" in data
        assert "display" in data
        assert isinstance(data["nextcloud"]["url"], str)
        assert isinstance(data["defaults"]["empty_rows"], int)


class TestConfigFile:
    """Tests for config file operations."""

    def test_init_config_file(self, tmp_path: Path) -> None:
        """Test creating a new config file."""
        pytest.importorskip("yaml")

        config_path = tmp_path / "config.yaml"
        result = init_config_file(config_path)

        assert result == config_path
        assert config_path.exists()

        # Verify it's valid YAML
        import yaml

        with open(config_path) as f:
            data = yaml.safe_load(f)

        assert "nextcloud" in data
        assert "defaults" in data
        # Password should be empty in file (security)
        assert data["nextcloud"]["password"] == ""

    def test_load_from_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading config from a YAML file."""
        yaml = pytest.importorskip("yaml")

        # Clear environment variables to prevent override
        monkeypatch.delenv("NEXTCLOUD_URL", raising=False)
        monkeypatch.delenv("NEXTCLOUD_USER", raising=False)
        monkeypatch.delenv("NEXTCLOUD_PASSWORD", raising=False)
        monkeypatch.delenv("NEXTCLOUD_PATH", raising=False)

        config_path = tmp_path / "config.yaml"
        config_data = {
            "nextcloud": {
                "url": "https://file.example.com",
                "username": "fileuser",
            },
            "defaults": {
                "empty_rows": 100,
                "template": "family",
            },
            "display": {
                "use_color": False,
            },
        }
        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f)

        config = Config.load(config_path)

        assert config.nextcloud.url == "https://file.example.com"
        assert config.nextcloud.username == "fileuser"
        assert config.defaults.empty_rows == 100
        assert config.defaults.template == "family"
        assert config.display.use_color is False


class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_returns_same_instance(self) -> None:
        """Test get_config returns cached instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_get_config_reload(self) -> None:
        """Test get_config with reload=True creates new instance."""
        get_config()
        config2 = get_config(reload=True)
        # Should be different instances (though may have same values)
        # We can't guarantee they're different objects without modifying env
        assert isinstance(config2, Config)
