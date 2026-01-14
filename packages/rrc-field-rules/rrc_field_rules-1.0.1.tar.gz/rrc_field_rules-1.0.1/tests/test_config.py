"""Tests for configuration module."""

import pytest

from rrc_field_rules.config import ParserConfig


class TestParserConfig:
    """Tests for ParserConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ParserConfig(password="test_password")

        assert config.host == "localhost"
        assert config.port == 1521
        assert config.service == "FREEPDB1"
        assert config.user == "PROD_OG_OWNR"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = ParserConfig(
            host="oracle.example.com",
            port=1522,
            service="CUSTOMDB",
            user="custom_user",
            password="custom_password",
        )

        assert config.host == "oracle.example.com"
        assert config.port == 1522
        assert config.service == "CUSTOMDB"
        assert config.user == "custom_user"

    def test_dsn_property(self) -> None:
        """Test DSN string generation."""
        config = ParserConfig(
            host="myhost", port=1523, service="MYDB", password="test"
        )

        assert config.dsn == "myhost:1523/MYDB"

    def test_connection_string_property(self) -> None:
        """Test connection string generation."""
        config = ParserConfig(
            host="myhost",
            port=1523,
            service="MYDB",
            user="myuser",
            password="test",
        )

        assert config.connection_string == "myuser@myhost:1523/MYDB"

    def test_password_is_secret(self) -> None:
        """Test that password is stored as SecretStr."""
        config = ParserConfig(password="super_secret")

        # SecretStr should not reveal password in repr
        assert "super_secret" not in repr(config)
        # But should be retrievable
        assert config.password.get_secret_value() == "super_secret"

    def test_password_required(self) -> None:
        """Test that password is required."""
        with pytest.raises(Exception):  # ValidationError
            ParserConfig()  # type: ignore


class TestParserConfigEnvVars:
    """Tests for environment variable configuration."""

    def test_env_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that RRC_ prefix is used for env vars."""
        monkeypatch.setenv("RRC_HOST", "envhost")
        monkeypatch.setenv("RRC_PORT", "1999")
        monkeypatch.setenv("RRC_PASSWORD", "envpassword")

        config = ParserConfig()

        assert config.host == "envhost"
        assert config.port == 1999
        assert config.password.get_secret_value() == "envpassword"
