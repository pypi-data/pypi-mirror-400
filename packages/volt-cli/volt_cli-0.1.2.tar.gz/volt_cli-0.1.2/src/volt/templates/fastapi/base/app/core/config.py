from typing import Literal, Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "__PROJECT_NAME__"
    ENVIRONMENT: Literal["local", "dev", "staging", "production"] = "local"

    @computed_field
    @property
    def DEBUG(self) -> bool:
        return self.ENVIRONMENT in ["local", "dev"]

    API_V1: str = "/api/v1"
    __DB_BLOCK__
    __AUTH_BLOCK__
    __REDIS_BLOCK__
    __OBSERVABILITY_BLOCK__


settings = Settings()
