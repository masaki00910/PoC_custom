from __future__ import annotations

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, CheckStatus, Severity
from app.domain.rules.base import CheckRule

RECOVERY_PROCESS = "エラー回復(文字数調整)よりロジック判定"


class CharLimitCheckRule(CheckRule):
    """F-05-007 文字数超過チェック (Stub)。

    元 PA フロー (`92c9430a-9f01-f111-8406-002248ef6599` = 【エラー回復】F-05-007) は、
    住所カナの半角 ATLAS 登録形式 (最大文字数あり) と申込書値を比較し、
    超過していれば文字数調整 AI で短縮候補を生成する。

    PoC スコープ外につき Stub。`status=NG` + `recovery_reason="(未実装)"` を返す。

    実装予定タスク: T-006
    実装時は T-003 で詳細に格納している `address_kana_halfwidth` (半角カナ変換結果) を
    入力として使う想定 → 既に必要な情報は AddressMasterMatchRule の details に揃っている。
    """

    name = "char_limit_check"
    category = "text"
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
                f"[{context.attribute}文字数超過] "
                f"文字数超過チェックは未実装 (T-006 予定)"
            ),
            recovery_process=RECOVERY_PROCESS,
            details={"stub": "true", "todo_task": "T-006"},
        )
