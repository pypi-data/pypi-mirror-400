"""Configuration management using Pydantic Settings."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ParserConfig(BaseSettings):
    """Configuration for Oracle database connection.

    Configuration can be provided via:
    - Direct instantiation: ParserConfig(host="localhost", password="secret")
    - Environment variables: RRC_HOST, RRC_PORT, RRC_SERVICE, RRC_USER, RRC_PASSWORD

    Attributes:
        host: Oracle database host. Defaults to "localhost".
        port: Oracle database port. Defaults to 1521.
        service: Oracle service name. Defaults to "FREEPDB1".
        user: Oracle username. Defaults to "PROD_OG_OWNR".
        password: Oracle password. Required, no default.
        expand_codes: If True, expand coded values to human-readable text.
            For example, 'O' -> 'Oil', 'N' -> 'No'. Defaults to False.
    """

    model_config = SettingsConfigDict(
        env_prefix="RRC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 1521
    service: str = "FREEPDB1"
    user: str = "PROD_OG_OWNR"
    password: SecretStr
    expand_codes: bool = False

    @property
    def dsn(self) -> str:
        """Generate Oracle DSN string."""
        return f"{self.host}:{self.port}/{self.service}"

    @property
    def connection_string(self) -> str:
        """Generate full connection string for display (password masked)."""
        return f"{self.user}@{self.dsn}"

