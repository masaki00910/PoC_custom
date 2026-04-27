from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict


class AIPrediction(BaseModel):
    """AI 推論結果。プロンプトごとに `structured` のキー集合が決まる契約。"""

    model_config = ConfigDict(frozen=True)

    prompt_name: str
    prompt_version: str
    raw_text: str
    structured: Mapping[str, str]


class AIClient(ABC):
    """AI クライアント抽象。

    実装:
    - `FakeAIClient`             : 決定的応答 (開発・テスト)
    - `BedrockProxyClient`       : 社内 API Gateway 経由 (T-002 で実装)
    - `VertexAIClient`           : 将来 (Vertex AI 移行後)
    """

    @abstractmethod
    async def predict(
        self,
        *,
        prompt_name: str,
        input_payload: Mapping[str, str],
        correlation_id: str,
    ) -> AIPrediction:
        """指定プロンプトで推論を行い、構造化フィールドを返す。

        引数:
            prompt_name: `infrastructure/ai/prompts/{prompt_name}_v{N}.txt` のキー
            input_payload: プロンプト変数。実装側がプロンプトテンプレートに差し込む
            correlation_id: 監査ログ紐付け用の相関 ID

        例外:
            AIPredictionError: 推論失敗 (タイムアウト・パース失敗等)
        """
        ...
