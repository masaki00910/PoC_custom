from __future__ import annotations

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, CheckStatus, Severity
from app.domain.rules.base import CheckRule

RECOVERY_PROCESS = "エラー回復(住所既契約突合チェック)よりロジック判定"


class ExistingContractMatchRule(CheckRule):
    """F-05-005 の「住所既契約突合チェック」分岐 (Stub)。

    元 PA フローは以下を行う:
      1. AI 「既契約有無チェック」(ca_prompt) で同一証券番号の既契約データ有無を判定
      2. 既契約あり → AI 「メイン書類読取り」(ca_prompt2) → AI 「既契約突合チェック」(ca_prompt3)
         で漢字住所・カナ住所と既契約データを照合
      3. 突合 OK → 直接回復値を確定
      4. 突合 NG / 既契約なし → F-05-006 (住所漢字・カナ突合) にフォールバック

    PoC スコープ外につき Stub。`status=NG` + `recovery_reason="(未実装)"` を返す。
    呼び出し側 (オーケストレータ) は status=NG を受けて F-05-006 にフォールバックする運用。

    実装予定タスク: T-011 (PoC スコープ外、要件確定後)
    """

    name = "existing_contract_match"
    category = "contract"
    severity = Severity.ERROR
    version = "0.0.0-stub"

    async def execute(
        self,
        application: Application,
        context: CheckContext,
    ) -> CheckResult:
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.NG,
            document_item=context.document_item,
            document_recovery_value=None,
            recovery_reason=(
                f"[{context.attribute}住所(既契約突合)] "
                f"住所既契約突合チェックは未実装 (T-011 予定) のためフォールバックを使用"
            ),
            recovery_process=RECOVERY_PROCESS,
            details={"stub": "true", "todo_task": "T-011"},
        )
