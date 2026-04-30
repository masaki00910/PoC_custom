from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddressMasterMatchRequest(BaseModel):
    """`POST /v1/checks/address-master-match` のリクエスト DTO。"""

    model_config = ConfigDict(extra="forbid")

    application_id: UUID = Field(..., description="申込 ID (UUID)")
    address_kana: str = Field(..., description="補完後の住所カナ (元 PA の text_4 相当)")
    address_kanji: str = Field(
        default="",
        description=(
            "契約申込書の住所漢字 (元 PA の text_3 相当)。"
            "Aflac 住所マスタにヒットしなかった場合の郵政住所マスタ (KEN_ALL) フォールバックで使用。"
        ),
    )
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


class AddressKanjiKanaMatchRequest(BaseModel):
    """`POST /v1/checks/address-kanji-kana-match` のリクエスト DTO (F-05-006)。

    案A: SharePoint からの画像取得 + メイン書類読取り AI (prompt1) はスキップし、
    呼び出し側で抽出した住所漢字を直接受け取る。
    """

    model_config = ConfigDict(extra="forbid")

    application_id: UUID = Field(..., description="申込 ID (UUID)")
    address_kanji: str = Field(
        ...,
        description="契約申込書から読み取った住所漢字 (元 PA の prompt1 出力相当)",
    )
    address_kana: str = Field(
        ...,
        description="ATLAS 登録の住所カナ (元 PA の text_3 相当)",
    )
    attribute: str = Field(
        "新", description="新住所/旧住所などの属性 (recovery_reason に埋め込み)"
    )
    document_item: str = Field(
        "申込書住所カナ",
        description="回復対象の項目名 (元 PA の document_item2 相当)",
    )
    correlation_id: str | None = Field(
        default=None,
        description="監査ログ紐付け用 ID (省略時は自動採番)",
    )


class AddressKanjiKanaMatchResponse(BaseModel):
    """`POST /v1/checks/address-kanji-kana-match` のレスポンス DTO。"""

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
