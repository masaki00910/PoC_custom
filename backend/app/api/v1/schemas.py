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


class CheckResultDTO(BaseModel):
    """単一 CheckResult を JSON 化した DTO (オーケストレータの結果配列要素)。"""

    model_config = ConfigDict(extra="forbid")

    rule_name: str
    rule_version: str
    status: str
    document_item: str
    document_recovery_value: str | None
    recovery_reason: str
    recovery_process: str
    details: dict[str, str]


class AddressRecoveryRequest(BaseModel):
    """`POST /v1/checks/address-recovery` のリクエスト DTO (F-05-005)。

    元 PA フローの 6 入力 (text / text_1 / text_2 / text_3 / text_4 / text_5) を構造化したもの。
    SharePoint 経由のメイン書類読取り (prompt1) は案A 同様、`address_kanji` 直接受け取りで簡略化。
    """

    model_config = ConfigDict(extra="forbid")

    application_id: UUID = Field(..., description="申込 ID (UUID)")
    document_item: str = Field(
        ...,
        description=(
            "回復対象の項目識別子。"
            "`02_policyholder_postal_code` または `02_insured_postal_code` で属性が決まる"
        ),
    )
    document_value: str = Field(
        ...,
        description="document_item の現在値。`000` / `*000` で住所3兄弟ルートに進む",
    )
    error_flag: bool = Field(default=False, description="親フローからの error_flag")
    ca_id: str = Field(
        ...,
        description=(
            "プロンプト名識別子。"
            "`住所既契約突合チェック` / `住所漢字・カナ突合チェック` / `文字数超過チェック` を含む"
        ),
    )
    address_kanji: str = Field(default="", description="申込書の住所漢字 (案A 同様直接受け取り)")
    address_kana: str = Field(default="", description="ATLAS 登録住所カナ")
    correlation_id: str | None = Field(
        default=None, description="監査ログ紐付け用 ID (省略時は自動採番)"
    )


class AddressRecoveryResponse(BaseModel):
    """`POST /v1/checks/address-recovery` のレスポンス DTO。

    元 PA フローの `回復結果` 配列に対応。実行された各ルールの結果を順に格納する。
    `results` が空の場合、PA フローの「空アクション」分岐 (= 何も実行しない) に該当する。
    """

    model_config = ConfigDict(extra="forbid")

    results: list[CheckResultDTO]
    correlation_id: str
