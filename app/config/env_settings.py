import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    DB_USER: str = Field(..., description="Database user")
    DB_PASSWORD: str = Field(..., description="Database password")
    DB_NAME: str = Field(..., description="Database name")
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, ge=1, le=65535, description="Database port")

    # Application settings
    DEBUG: bool = Field(
        default=False, description="Debug mode (verbose logging, SQL echo)"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, or production",
    )
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


try:
    settings: Settings = Settings()
except Exception as e:
    logger.error(f"Error loading settings: {e}")
    raise
