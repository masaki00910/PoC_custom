from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class CheckStatus(StrEnum):
    """元 Power Automate の `check_result` 文字列を踏襲。

    OK    : 自動回復成功
    NG    : 自動回復不可 (要人手判定)
    ERROR : 実行時エラー (再試行候補)
    """

    OK = "OK"
    NG = "NG"
    ERROR = "ERROR"


class CheckResult(BaseModel):
    """1 ルール実行の結果。元 Power Automate の `回復結果作成` Compose 出力に対応。"""

    model_config = ConfigDict(frozen=True)

    rule_name: str
    rule_version: str
    severity: Severity

    status: CheckStatus
    document_item: str

    # 回復値 (郵便番号等)。NG/ERROR 時は None
    document_recovery_value: str | None = None
    recovery_reason: str
    recovery_process: str

    # AI 説明可能性: プロンプト名・モデル・生レスポンス等の参考情報
    details: dict[str, str] = {}
