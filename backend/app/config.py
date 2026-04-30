from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    STG = "stg"
    PRD = "prd"


class AIProviderKind(StrEnum):
    """AI クライアント Adapter の選択肢。

    実装の追加は `infrastructure/ai/` 配下に新クラスを置き、本 enum と
    `api/deps.py` の DI factory に分岐を追加することで完結する (ADR-0001)。
    """

    FAKE = "fake"
    BEDROCK_PROXY = "bedrock_proxy"
    # 将来追加候補: VERTEX_AI / AZURE_OPENAI / ON_PREM_LLM 等


class BedrockProxySettings(BaseModel):
    """AWS API Gateway 経由の Bedrock プロキシ設定。"""

    url: str = ""
    model: str = "global.anthropic.claude-sonnet-4-6"
    timeout_seconds: float = 30.0


class AISettings(BaseModel):
    """AI プロバイダ設定。プロバイダ別設定はネストして保持する。

    ADR-0001: フィールド名にプロバイダ名を平坦に並べてはいけない。
    新プロバイダは `<ProviderName>Settings` をネストとして追加する。
    """

    provider: AIProviderKind = AIProviderKind.FAKE
    bedrock_proxy: BedrockProxySettings = Field(default_factory=BedrockProxySettings)
    # 将来追加: vertex: VertexAISettings, azure_openai: AzureOpenAISettings, ...


class Settings(BaseSettings):
    """アプリケーション設定。

    env_nested_delimiter='__' によりネストモデルへの設定流入が可能:
        AI__PROVIDER=fake
        AI__BEDROCK_PROXY__URL=https://...
        AI__BEDROCK_PROXY__TIMEOUT_SECONDS=30
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_env: AppEnv = AppEnv.LOCAL
    log_level: str = "INFO"

    ai: AISettings = Field(default_factory=AISettings)


def get_settings() -> Settings:
    return Settings()
