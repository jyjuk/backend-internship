from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Aplication settings"""

    APP_NAME: str = "BackendIntership"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "default-secret-key"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
