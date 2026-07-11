"""Obsidian Pilot API - Configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """API settings loaded from environment variables."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "info"

    # Vault
    default_vault_path: str = ""

    # CORS
    cors_origins: str = "*"

    # Pagination
    default_page_size: int = 50
    max_page_size: int = 200

    model_config = {"env_prefix": "OBSIDIAN_PILOT_API_", "env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
