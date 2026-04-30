from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, CheckStatus
from app.domain.rules.address.address_kanji_kana_match import AddressKanjiKanaMatchRule
from app.domain.rules.contract.existing_contract_match import ExistingContractMatchRule
from app.domain.rules.text.char_limit_check import CharLimitCheckRule

# 元 PA フローの「属性情報の設定」Switch に対応 (document_item 値別の attribute / document_item2)
DOCUMENT_ITEM_POLICYHOLDER_POSTAL_CODE = "02_policyholder_postal_code"
DOCUMENT_ITEM_INSURED_POSTAL_CODE = "02_insured_postal_code"

CA_ID_EXISTING_CONTRACT_MATCH = "住所既契約突合チェック"
CA_ID_KANJI_KANA_MATCH = "住所漢字・カナ突合チェック"
CA_ID_CHAR_LIMIT_CHECK = "文字数超過チェック"


class DocumentAttribute(StrEnum):
    """元 PA の `属性情報` JSON の `attribute` 値。"""

    POLICYHOLDER = "契約者"
    INSURED = "被保険者"


class AddressRecoveryInput(BaseModel):
    """F-05-005 への入力 (元 PA の text / text_5 等を構造化)。"""

    model_config = ConfigDict(frozen=True)

    application: Application
    document_item: str = Field(..., description="`02_policyholder_postal_code` 等")
    document_value: str = Field(
        ...,
        description="郵便番号の値。`000` / `*000` で住所3兄弟ルートに進む",
    )
    error_flag: bool = Field(default=False, description="親フローの error_flag")
    ca_id: str = Field(
        ...,
        description="プロンプト名識別子 (`住所漢字・カナ突合チェック` 等を含む)",
    )
    correlation_id: str
    attribute: DocumentAttribute | None = Field(
        default=None,
        description=(
            "`document_item` から自動決定するが、明示指定もできる。"
            "未指定時は `_resolve_attribute()` で決まる"
        ),
    )


def _resolve_attribute(document_item: str) -> DocumentAttribute | None:
    """元 PA の Switch (属性情報の設定) を移植。"""
    if document_item == DOCUMENT_ITEM_POLICYHOLDER_POSTAL_CODE:
        return DocumentAttribute.POLICYHOLDER
    if document_item == DOCUMENT_ITEM_INSURED_POSTAL_CODE:
        return DocumentAttribute.INSURED
    return None


class RunAddressRecovery:
    """F-05-005 住所回復処理オーケストレータ。

    元 PA フロー `65f74109-84fa-f011-8406-002248f17ef0` (【エラー回復】F-05-005) を移植。
    郵便番号 / error_flag / ca_id によって複数の住所系チェックに振り分けるディスパッチャ。

    元 PA の分岐:
        IF document_value ∈ {"000", "*000"}:
            IF ca_id contains "住所既契約突合チェック":
              既契約突合 → 該当なら確定 / 該当なしなら F-05-006 にフォールバック
            ELSE: pass
        ELSE:
            IF error_flag:
                IF ca_id contains "住所漢字・カナ突合チェック":
                    F-05-006 直行
                ELSE: pass
            ELSE:
                IF ca_id contains "文字数超過チェック":
                    F-05-007
                ELSE: pass

    PoC では:
        - F-05-006 (`AddressKanjiKanaMatchRule`): T-004 で実装済
        - 既契約突合 (`ExistingContractMatchRule`): Stub (T-011 予定)
        - F-05-007 文字数超過 (`CharLimitCheckRule`): Stub (T-006 予定)
        - F-05-009 中間結果登録: 未配線 (監査ログ T-006 で対応)
    """

    def __init__(
        self,
        kanji_kana_match: AddressKanjiKanaMatchRule,
        existing_contract_match: ExistingContractMatchRule,
        char_limit_check: CharLimitCheckRule,
    ) -> None:
        self._kanji_kana_match = kanji_kana_match
        self._existing_contract_match = existing_contract_match
        self._char_limit_check = char_limit_check

    async def execute(self, request: AddressRecoveryInput) -> list[CheckResult]:
        attribute = request.attribute or _resolve_attribute(request.document_item)
        if attribute is None:
            # 元 PA の Switch default は空アクション (= 何もせず空配列を返す)
            return []

        context = CheckContext(
            correlation_id=request.correlation_id,
            attribute=attribute.value,
            document_item=request.document_item,
        )
        application = request.application

        results: list[CheckResult] = []

        if request.document_value in ("000", "*000"):
            # 郵便番号エラー系: 既契約突合 → F-05-006 フォールバック / または直接 F-05-006
            if CA_ID_EXISTING_CONTRACT_MATCH in request.ca_id:
                ec_result = await self._existing_contract_match.execute(application, context)
                results.append(ec_result)
                if ec_result.status != CheckStatus.OK:
                    # Stub または NG の場合は F-05-006 にフォールバック
                    f06_result = await self._kanji_kana_match.execute(application, context)
                    results.append(f06_result)
            # ca_id に "住所既契約突合チェック" を含まない場合は元 PA でも空アクション
            return results

        if request.error_flag:
            if CA_ID_KANJI_KANA_MATCH in request.ca_id:
                f06_result = await self._kanji_kana_match.execute(application, context)
                results.append(f06_result)
            return results

        if CA_ID_CHAR_LIMIT_CHECK in request.ca_id:
            cl_result = await self._char_limit_check.execute(application, context)
            results.append(cl_result)
        return results
