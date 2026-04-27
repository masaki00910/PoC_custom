from __future__ import annotations

from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STG = "stg"
    PRD = "prd"


class AIClientKind(StrEnum):
    FAKE = "fake"
    BEDROCK_PROXY = "bedrock_proxy"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnv = AppEnv.LOCAL
    log_level: str = "INFO"

    ai_client: AIClientKind = AIClientKind.FAKE
    bedrock_proxy_url: str = Field(default="")
    bedrock_proxy_model: str = Field(default="global.anthropic.claude-sonnet-4-6")
    bedrock_proxy_timeout_seconds: float = 30.0


def get_settings() -> Settings:
    return Settings()
