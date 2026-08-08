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
    APP_NAME: str = "DBReport AI"
    ENVIRONMENT: str = "development"

    CORS_ORIGINS: str = "http://localhost:3000"

    GROQ_API_KEY: str = ""

    JWT_SECRET: str = "change-this-in-production"

    ENCRYPTION_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
