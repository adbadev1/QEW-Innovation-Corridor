"""
Configuration Management
========================

Loads environment variables and provides typed configuration objects.
Uses pydantic-settings for validation and type safety.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/qew_corridor",
        description="PostgreSQL connection string"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)

    # Google Cloud Platform
    GCP_PROJECT_ID: str = Field(default="qew-innovation-pilot")
    GCP_STORAGE_BUCKET: str = Field(default="qew-camera-images-public")
    GCP_STORAGE_API_KEY: str = Field(default="")

    # Gemini AI
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-exp")

    # vRSU Service
    VRSU_SERVICE_URL: str = Field(default="http://localhost:8081")
    VRSU_ENABLED: bool = Field(default=True)

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:8200,http://localhost:3000,https://adbadev1.github.io"
    )

    # Server
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000, ge=1024, le=65535)
    API_WORKERS: int = Field(default=1, ge=1, le=16)
    LOG_LEVEL: str = Field(default="INFO")

    # Feature Flags
    ENABLE_RATE_LIMITING: bool = Field(default=False)
    ENABLE_CACHING: bool = Field(default=False)
    ENABLE_ANALYTICS: bool = Field(default=False)

    # MTO COMPASS (Future)
    MTO_COMPASS_API_URL: str = Field(default="")
    MTO_COMPASS_API_KEY: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Convert comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# Global settings instance
settings = Settings()
