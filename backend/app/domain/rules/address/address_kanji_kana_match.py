from __future__ import annotations

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, CheckStatus, Severity
from app.domain.exceptions import AIPredictionError
from app.domain.interfaces.ai_client import AIClient, AIPrediction
from app.domain.rules.address.address_master_match import AddressMasterMatchRule
from app.domain.rules.base import CheckRule

PROMPT_CONSISTENCY = "address_kanji_kana_consistency"
PROMPT_COMPLEMENT = "address_kanji_kana_complement"

RECOVERY_PROCESS = "エラー回復(住所漢字・カナ突合)よりロジック判定"


class AddressKanjiKanaMatchRule(CheckRule):
    """F-05-006 住所漢字・カナ突合 (案A: SharePoint/OCR スキップ版)。

    入力:
        application.address_kanji : 契約申込書から読み取った住所漢字 (元 PA の prompt1 出力相当)
        application.address_kana  : ATLAS 登録の住所カナ (元 PA の text_3 相当)

    手順:
        1. AI 整合チェック (prompt2) で漢字とカナが意味的に一致しているか判定
        2a. 整合 OK → そのまま F-05-008 (AddressMasterMatchRule) を呼ぶ
        2b. 整合 NG → AI 補完 (prompt5) を試行
            - 補完 OK → 補完後カナで F-05-008 を呼び、recovery_reason に補完 reason を prefix
            - 補完 NG → 補完不可 NG を返す

    商用化メモ:
        元 PA は document_item1 (住所(〒)) と document_item2 (住所カナ) で複数の
        回復結果を返す前提だが、PoC では単一 CheckResult に集約する。
        商用化時に CheckRule.execute() を list[CheckResult] 返却に拡張する想定。
    """

    name = "address_kanji_kana_match"
    category = "address"
    severity = Severity.ERROR
    version = "1.0.0"

    def __init__(
        self,
        ai_client: AIClient,
        master_match_rule: AddressMasterMatchRule,
    ) -> None:
        self._ai = ai_client
        self._master_match = master_match_rule

    async def execute(
        self,
        application: Application,
        context: CheckContext,
    ) -> CheckResult:
        address_kanji = (application.address_kanji or "").strip()
        address_kana = (application.address_kana or "").strip()

        if not address_kanji or not address_kana:
            return self._ng(
                context,
                reason=(
                    f"[{context.attribute}住所漢字・カナ突合] "
                    f"住所漢字または住所カナが空のため整合チェック不可"
                ),
            )

        try:
            consistency = await self._ai.predict(
                prompt_name=PROMPT_CONSISTENCY,
                input_payload={
                    "address_kanji": address_kanji,
                    "address_kana": address_kana,
                },
                correlation_id=context.correlation_id,
            )
        except AIPredictionError as e:
            return self._error(
                context,
                reason=f"[{context.attribute}住所漢字・カナ突合] 整合チェック AI 推論失敗: {e}",
            )

        consistency_result = consistency.structured.get("check_result", "").strip()
        consistency_reason = consistency.structured.get("reason", "")

        if consistency_result == "OK":
            return await self._delegate_master_match(
                application,
                context,
                consistency_prompt=consistency,
                complement_prefix=None,
            )

        return await self._handle_inconsistent(
            application,
            context,
            consistency=consistency,
            consistency_reason=consistency_reason,
        )

    async def _handle_inconsistent(
        self,
        application: Application,
        context: CheckContext,
        *,
        consistency: AIPrediction,
        consistency_reason: str,
    ) -> CheckResult:
        try:
            complement = await self._ai.predict(
                prompt_name=PROMPT_COMPLEMENT,
                input_payload={
                    "address_kanji": application.address_kanji,
                    "address_kana": application.address_kana,
                },
                correlation_id=context.correlation_id,
            )
        except AIPredictionError as e:
            return self._error(
                context,
                reason=f"[{context.attribute}住所漢字・カナ突合] 補完 AI 推論失敗: {e}",
            )

        complement_result = complement.structured.get("check_result", "").strip()
        complement_kana = complement.structured.get("complement_kana_value", "").strip()
        complement_reason = complement.structured.get("reason", "")

        if complement_result != "OK" or not complement_kana:
            return CheckResult(
                rule_name=self.name,
                rule_version=self.version,
                severity=self.severity,
                status=CheckStatus.NG,
                document_item=context.document_item,
                document_recovery_value=None,
                recovery_reason=(
                    f"[{context.attribute}住所漢字・カナ突合] "
                    f"住所カナを補完できず自動回復不可: {complement_reason or consistency_reason}"
                ),
                recovery_process=RECOVERY_PROCESS,
                details={
                    "consistency_check_result": "NG",
                    "consistency_reason": consistency_reason,
                    "consistency_ai_raw_text": consistency.raw_text,
                    "complement_check_result": complement_result or "NG",
                    "complement_reason": complement_reason,
                    "complement_ai_raw_text": complement.raw_text,
                },
            )

        complemented = application.model_copy(update={"address_kana": complement_kana})
        prefix = f"[{context.attribute}住所カナ] {complement_reason}　"
        return await self._delegate_master_match(
            complemented,
            context,
            consistency_prompt=consistency,
            complement_prompt=complement,
            complement_prefix=prefix,
        )

    async def _delegate_master_match(
        self,
        application: Application,
        context: CheckContext,
        *,
        consistency_prompt: AIPrediction,
        complement_prompt: AIPrediction | None = None,
        complement_prefix: str | None,
    ) -> CheckResult:
        master_result = await self._master_match.execute(application, context)

        recovery_reason = master_result.recovery_reason
        if complement_prefix:
            recovery_reason = complement_prefix + recovery_reason

        merged_details = dict(master_result.details)
        merged_details["consistency_check_result"] = consistency_prompt.structured.get(
            "check_result", ""
        )
        merged_details["consistency_reason"] = consistency_prompt.structured.get("reason", "")
        merged_details["consistency_ai_raw_text"] = consistency_prompt.raw_text
        if complement_prompt is not None:
            merged_details["complement_check_result"] = complement_prompt.structured.get(
                "check_result", ""
            )
            merged_details["complement_reason"] = complement_prompt.structured.get("reason", "")
            merged_details["complement_kana_value"] = complement_prompt.structured.get(
                "complement_kana_value", ""
            )
            merged_details["complement_ai_raw_text"] = complement_prompt.raw_text

        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=master_result.status,
            document_item=master_result.document_item,
            document_recovery_value=master_result.document_recovery_value,
            recovery_reason=recovery_reason,
            recovery_process=master_result.recovery_process,
            details=merged_details,
        )

    def _ng(self, context: CheckContext, *, reason: str) -> CheckResult:
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.NG,
            document_item=context.document_item,
            document_recovery_value=None,
            recovery_reason=reason,
            recovery_process=RECOVERY_PROCESS,
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
