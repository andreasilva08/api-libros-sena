from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    database_url: str
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    login_max_failed_attempts: int = 5
    login_lock_minutes: int = 15
    cloud_name: str | None = Field(default=None, validation_alias="CLOUD_NAME")
    cloud_api_key: str | None = Field(default=None, validation_alias="API_KEY")
    cloud_api_secret: str | None = Field(
        default=None, validation_alias="API_SECRET"
    )
    cors_origins: list[str] = []
    environment: Literal["dev", "test", "prod"] = "dev"

    # Validador automático para corregir la URL de Render (postgres:// a postgresql://)
    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

@lru_cache
def get_settings() -> Settings:
    return Settings()