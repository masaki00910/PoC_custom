from __future__ import annotations

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, CheckStatus, Severity
from app.domain.exceptions import AIPredictionError
from app.domain.interfaces.address_master_repository import AddressMasterRepository
from app.domain.interfaces.ai_client import AIClient
from app.domain.rules.base import CheckRule

PROMPT_NAME = "address_kana_split"
RECOVERY_PROCESS = "エラー回復(AFLAC住所マスタ突合)よりロジック判定"


class AddressMasterMatchRule(CheckRule):
    """F-05-008 住所マスタ突合 (最小実装)。

    入力: `application.address_kana` (補完後の住所カナ)
    手順:
        1. AI で住所カナを 4 分割 (都道府県カナ / 市区町村カナ / 大字カナ / 字丁カナ)
        2. Aflac 住所マスタを 市区町村名カナ AND 大字・通称名カナ で絞り込み
        3. ヒットした行の郵便番号が 1 種類なら OK で回復値として返す
        4. 0 件 / 複数 → NG (郵政住所マスタフォールバックは T-003)
    """

    name = "address_master_match"
    category = "address"
    severity = Severity.ERROR
    version = "1.0.0"

    def __init__(
        self,
        ai_client: AIClient,
        address_repo: AddressMasterRepository,
    ) -> None:
        self._ai = ai_client
        self._repo = address_repo

    async def execute(
        self,
        application: Application,
        context: CheckContext,
    ) -> CheckResult:
        address_kana = (application.address_kana or "").strip()
        if not address_kana:
            return self._ng(
                context,
                reason=f"[{context.attribute}住所(〒)] 入力住所カナが空のため自動回復不可",
            )

        try:
            prediction = await self._ai.predict(
                prompt_name=PROMPT_NAME,
                input_payload={"address_kana": address_kana},
                correlation_id=context.correlation_id,
            )
        except AIPredictionError as e:
            return self._error(
                context,
                reason=f"[{context.attribute}住所(〒)] 住所カナ分割 AI 推論失敗: {e}",
            )

        municipality_kana = prediction.structured.get("municipality_kana", "").strip()
        oaza_kana = prediction.structured.get("oaza_kana", "").strip()
        if not municipality_kana or not oaza_kana:
            return self._ng(
                context,
                reason=f"[{context.attribute}住所(〒)] 住所カナ分割で市区町村/大字を特定できず",
                ai_raw=prediction.raw_text,
            )

        records = await self._repo.find_aflac_by_municipality_and_oaza_kana(
            municipality_name_kana=municipality_kana,
            oaza_common_name_kana=oaza_kana,
        )
        if not records:
            return self._ng(
                context,
                reason=f"[{context.attribute}住所(〒)] AFLAC 住所マスタにヒットせず",
                ai_raw=prediction.raw_text,
            )

        postal_codes = {r.postal_code for r in records if r.postal_code}
        if len(postal_codes) != 1:
            return self._ng(
                context,
                reason=(
                    f"[{context.attribute}住所(〒)] "
                    f"AFLAC 住所マスタの郵便番号が複数のため自動回復不可 "
                    f"(候補件数={len(postal_codes)})"
                ),
                ai_raw=prediction.raw_text,
            )

        postal_code = next(iter(postal_codes))
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.OK,
            document_item=context.document_item,
            document_recovery_value=postal_code,
            recovery_reason=f"[{context.attribute}住所(〒)]　AFLAC住所マスタより回復",
            recovery_process=RECOVERY_PROCESS,
            details={
                "ai_prompt_name": prediction.prompt_name,
                "ai_prompt_version": prediction.prompt_version,
                "ai_raw_text": prediction.raw_text,
                "matched_municipality_kana": municipality_kana,
                "matched_oaza_kana": oaza_kana,
            },
        )

    def _ng(
        self,
        context: CheckContext,
        *,
        reason: str,
        ai_raw: str | None = None,
    ) -> CheckResult:
        details = {"ai_raw_text": ai_raw} if ai_raw is not None else {}
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.NG,
            document_item=context.document_item,
            document_recovery_value=None,
            recovery_reason=reason,
            recovery_process=RECOVERY_PROCESS,
            details=details,
        )

    def _error(self, context: CheckContext, *, reason: str) -> CheckResult:
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.ERROR,
            document_item=context.document_item,
            document_recovery_value=None,
            recovery_reason=reason,
            recovery_process=RECOVERY_PROCESS,
        )
