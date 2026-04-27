from __future__ import annotations

import json
import logging
from collections.abc import Mapping

from app.domain.exceptions import AIPredictionError
from app.domain.interfaces.ai_client import AIClient, AIPrediction

logger = logging.getLogger(__name__)

# 既知の入力サブストリング → 構造化フィールド固定応答。
# PoC 動作確認用のごく小さな辞書。実 AI 移行 (T-002) 後は不要になる。
_ADDRESS_KANA_SPLIT_FIXTURES: list[tuple[str, Mapping[str, str]]] = [
    (
        "ジングウマエ",
        {
            "prefecture_kana": "トウキョウト",
            "municipality_kana": "シブヤク",
            "oaza_kana": "ジングウマエ",
            "aza_cho_kana": "",
        },
    ),
    (
        "カブキチョウ",
        {
            "prefecture_kana": "トウキョウト",
            "municipality_kana": "シンジュクク",
            "oaza_kana": "カブキチョウ",
            "aza_cho_kana": "",
        },
    ),
    (
        "ミナミアオヤマ",
        {
            "prefecture_kana": "トウキョウト",
            "municipality_kana": "ミナトク",
            "oaza_kana": "ミナミアオヤマ",
            "aza_cho_kana": "",
        },
    ),
    (
        "マルノウチ",
        {
            "prefecture_kana": "トウキョウト",
            "municipality_kana": "チヨダク",
            "oaza_kana": "マルノウチ",
            "aza_cho_kana": "",
        },
    ),
]


class FakeAIClient(AIClient):
    """ローカル開発・テスト用の決定的 AI クライアント。

    プロンプト名と入力からあらかじめ用意した固定応答を返す。
    一致するフィクスチャが無い場合は空フィールドを返し、ルール側で NG 経路を発動できるようにする。
    """

    async def predict(
        self,
        *,
        prompt_name: str,
        input_payload: Mapping[str, str],
        correlation_id: str,
    ) -> AIPrediction:
        if prompt_name == "address_kana_split":
            return self._predict_address_kana_split(input_payload, correlation_id)
        raise AIPredictionError(f"FakeAIClient does not support prompt '{prompt_name}'")

    def _predict_address_kana_split(
        self,
        input_payload: Mapping[str, str],
        correlation_id: str,
    ) -> AIPrediction:
        address_kana = input_payload.get("address_kana", "")
        for substring, structured in _ADDRESS_KANA_SPLIT_FIXTURES:
            if substring in address_kana:
                logger.info(
                    "fake_ai_match prompt=address_kana_split correlation_id=%s match=%s",
                    correlation_id,
                    substring,
                )
                return AIPrediction(
                    prompt_name="address_kana_split",
                    prompt_version="v1-fake",
                    raw_text=json.dumps(structured, ensure_ascii=False),
                    structured=structured,
                )

        logger.info(
            "fake_ai_unmatched prompt=address_kana_split correlation_id=%s",
            correlation_id,
        )
        empty: Mapping[str, str] = {
            "prefecture_kana": "",
            "municipality_kana": "",
            "oaza_kana": "",
            "aza_cho_kana": "",
        }
        return AIPrediction(
            prompt_name="address_kana_split",
            prompt_version="v1-fake",
            raw_text=json.dumps(empty, ensure_ascii=False),
            structured=empty,
        )
