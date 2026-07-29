"""
Central place for all backend configuration.

Why this file exists:
Instead of scattering os.environ.get(...) calls across the codebase,
every setting is declared once here with a type and a default.
Pydantic validates types automatically and pydantic-settings reads
values from a .env file, so nothing sensitive is hard-coded.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General app info
    APP_NAME: str = "DBReport AI"
    ENVIRONMENT: str = "development"

    # CORS: which frontend origins are allowed to call this API.
    CORS_ORIGINS: str = "http://localhost:3000"

    # Anthropic API key for the text-to-SQL engine (used from Phase 4 onward).
    ANTHROPIC_API_KEY: str = ""

    # Secret used to sign JWT auth tokens (used from Phase 9 onward).
    JWT_SECRET: str = "change-this-in-production"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# Import this single instance anywhere you need a setting:
#   from app.core.config import settings
#   settings.APP_NAME
settings = Settings()