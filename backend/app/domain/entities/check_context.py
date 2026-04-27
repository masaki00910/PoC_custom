from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CheckContext(BaseModel):
    """チェック実行時のメタ情報 (監査ログ・回復理由文に使う)。

    元 Power Automate の `属性情報` (text_2) JSON に含まれていたフィールドを抽出。
    """

    model_config = ConfigDict(frozen=True)

    # 監査・追跡用の相関 ID (リクエスト単位で一意)
    correlation_id: str

    # 「新住所」「旧住所」など。recovery_reason 文字列に埋め込まれる
    attribute: str

    # 回復対象の項目名 (例: 申込書住所カナ)
    document_item: str
