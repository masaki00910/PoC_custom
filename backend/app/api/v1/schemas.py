from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddressMasterMatchRequest(BaseModel):
    """`POST /v1/checks/address-master-match` のリクエスト DTO。"""

    model_config = ConfigDict(extra="forbid")

    application_id: UUID = Field(..., description="申込 ID (UUID)")
    address_kana: str = Field(..., description="補完後の住所カナ (元 PA の text_4 相当)")
    attribute: str = Field("新", description="新住所/旧住所などの属性 (recovery_reason に埋め込み)")
    document_item: str = Field(
        "申込書住所カナ",
        description="回復対象の項目名 (元 PA の document_item1 相当)",
    )
    correlation_id: str | None = Field(
        default=None,
        description="監査ログ紐付け用 ID (省略時は自動採番)",
    )


class AddressMasterMatchResponse(BaseModel):
    """`POST /v1/checks/address-master-match` のレスポンス DTO。"""

    model_config = ConfigDict(extra="forbid")

    rule_name: str
    rule_version: str
    status: str
    document_item: str
    document_recovery_value: str | None
    recovery_reason: str
    recovery_process: str
    details: dict[str, str]
    correlation_id: str
