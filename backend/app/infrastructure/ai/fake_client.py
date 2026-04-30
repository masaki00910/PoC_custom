from __future__ import annotations

import json
import logging
from collections.abc import Mapping

from app.domain.exceptions import AIPredictionError
from app.domain.interfaces.ai_client import AIClient, AIPrediction

logger = logging.getLogger(__name__)

# 漢字→対応するフルセットのカナ。整合チェックと補完の両方で使う。
_KANJI_TO_KANA_FIXTURES: list[tuple[str, str]] = [
    ("神宮前", "ジングウマエ"),
    ("歌舞伎町", "カブキチョウ"),
    ("南青山", "ミナミアオヤマ"),
    ("丸の内", "マルノウチ"),
    ("美しが丘", "ウツクシガオカ"),
]

# 漢字→補完用のフル住所カナ (都道府県+市区町村+町域)。
_KANJI_TO_FULL_KANA_FIXTURES: list[tuple[str, str]] = [
    ("神宮前", "トウキョウトシブヤクジングウマエ"),
    ("歌舞伎町", "トウキョウトシンジュククカブキチョウ"),
    ("南青山", "トウキョウトミナトクミナミアオヤマ"),
    ("丸の内", "トウキョウトチヨダクマルノウチ"),
    ("美しが丘", "カナガワケンヨコハマシアオバクウツクシガオカ"),
]

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

# 漢字住所分割 (郵政住所マスタ突合の前段) 用の固定応答。
_ADDRESS_KANJI_SPLIT_FIXTURES: list[tuple[str, Mapping[str, str]]] = [
    (
        "神宮前",
        {
            "prefecture_name": "東京都",
            "municipality_name": "渋谷区",
            "town_name": "神宮前",
        },
    ),
    (
        "歌舞伎町",
        {
            "prefecture_name": "東京都",
            "municipality_name": "新宿区",
            "town_name": "歌舞伎町",
        },
    ),
    (
        "南青山",
        {
            "prefecture_name": "東京都",
            "municipality_name": "港区",
            "town_name": "南青山",
        },
    ),
    (
        "丸の内",
        {
            "prefecture_name": "東京都",
            "municipality_name": "千代田区",
            "town_name": "丸の内",
        },
    ),
    # 郵政住所マスタフォールバックで OK になるケース (Aflac マスタには存在しない住所)
    (
        "美しが丘",
        {
            "prefecture_name": "神奈川県",
            "municipality_name": "横浜市青葉区",
            "town_name": "美しが丘",
        },
    ),
    # 郵政住所マスタでも 0 件のケース (NG)
    (
        "存在しない町",
        {
            "prefecture_name": "東京都",
            "municipality_name": "存在しない区",
            "town_name": "存在しない町",
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
            return self._predict_with_fixtures(
                prompt_name=prompt_name,
                fixtures=_ADDRESS_KANA_SPLIT_FIXTURES,
                input_text=input_payload.get("address_kana", ""),
                empty_keys=("prefecture_kana", "municipality_kana", "oaza_kana", "aza_cho_kana"),
                correlation_id=correlation_id,
            )
        if prompt_name == "address_kanji_split":
            return self._predict_with_fixtures(
                prompt_name=prompt_name,
                fixtures=_ADDRESS_KANJI_SPLIT_FIXTURES,
                input_text=input_payload.get("address_kanji", ""),
                empty_keys=("prefecture_name", "municipality_name", "town_name"),
                correlation_id=correlation_id,
            )
        if prompt_name == "address_kanji_kana_consistency":
            return self._predict_consistency(
                input_payload=input_payload,
                correlation_id=correlation_id,
            )
        if prompt_name == "address_kanji_kana_complement":
            return self._predict_complement(
                input_payload=input_payload,
                correlation_id=correlation_id,
            )
        raise AIPredictionError(f"FakeAIClient does not support prompt '{prompt_name}'")

    def _predict_consistency(
        self,
        *,
        input_payload: Mapping[str, str],
        correlation_id: str,
    ) -> AIPrediction:
        prompt_name = "address_kanji_kana_consistency"
        kanji = input_payload.get("address_kanji", "")
        kana = input_payload.get("address_kana", "")

        if not kanji or not kana:
            structured: Mapping[str, str] = {
                "check_result": "NG",
                "reason": "漢字またはカナが空文字列",
            }
            logger.info(
                "fake_ai_consistency_empty prompt=%s correlation_id=%s",
                prompt_name,
                correlation_id,
            )
            return AIPrediction(
                prompt_name=prompt_name,
                prompt_version="v1-fake",
                raw_text=json.dumps(structured, ensure_ascii=False),
                structured=structured,
            )

        for kanji_key, kana_key in _KANJI_TO_KANA_FIXTURES:
            if kanji_key in kanji:
                if kana_key in kana:
                    structured = {
                        "check_result": "OK",
                        "reason": f"漢字 '{kanji_key}' とカナ '{kana_key}' が整合",
                    }
                else:
                    structured = {
                        "check_result": "NG",
                        "reason": (
                            f"漢字 '{kanji_key}' に対応するカナ '{kana_key}' が"
                            f"住所カナ側に存在しない"
                        ),
                    }
                logger.info(
                    "fake_ai_consistency prompt=%s correlation_id=%s match=%s result=%s",
                    prompt_name,
                    correlation_id,
                    kanji_key,
                    structured["check_result"],
                )
                return AIPrediction(
                    prompt_name=prompt_name,
                    prompt_version="v1-fake",
                    raw_text=json.dumps(structured, ensure_ascii=False),
                    structured=structured,
                )

        structured = {
            "check_result": "NG",
            "reason": "住所漢字がフィクスチャに存在しない",
        }
        logger.info(
            "fake_ai_consistency_unknown prompt=%s correlation_id=%s",
            prompt_name,
            correlation_id,
        )
        return AIPrediction(
            prompt_name=prompt_name,
            prompt_version="v1-fake",
            raw_text=json.dumps(structured, ensure_ascii=False),
            structured=structured,
        )

    def _predict_complement(
        self,
        *,
        input_payload: Mapping[str, str],
        correlation_id: str,
    ) -> AIPrediction:
        prompt_name = "address_kanji_kana_complement"
        kanji = input_payload.get("address_kanji", "")

        for kanji_key, full_kana in _KANJI_TO_FULL_KANA_FIXTURES:
            if kanji_key in kanji:
                structured: Mapping[str, str] = {
                    "check_result": "OK",
                    "complement_kana_value": full_kana,
                    "reason": f"漢字 '{kanji_key}' に対応するカナを補完",
                }
                logger.info(
                    "fake_ai_complement prompt=%s correlation_id=%s match=%s",
                    prompt_name,
                    correlation_id,
                    kanji_key,
                )
                return AIPrediction(
                    prompt_name=prompt_name,
                    prompt_version="v1-fake",
                    raw_text=json.dumps(structured, ensure_ascii=False),
                    structured=structured,
                )

        structured = {
            "check_result": "NG",
            "complement_kana_value": "",
            "reason": "住所漢字がフィクスチャに存在せず補完不可",
        }
        logger.info(
            "fake_ai_complement_unknown prompt=%s correlation_id=%s",
            prompt_name,
            correlation_id,
        )
        return AIPrediction(
            prompt_name=prompt_name,
            prompt_version="v1-fake",
            raw_text=json.dumps(structured, ensure_ascii=False),
            structured=structured,
        )

    def _predict_with_fixtures(
        self,
        *,
        prompt_name: str,
        fixtures: list[tuple[str, Mapping[str, str]]],
        input_text: str,
        empty_keys: tuple[str, ...],
        correlation_id: str,
    ) -> AIPrediction:
        for substring, structured in fixtures:
            if substring in input_text:
                logger.info(
                    "fake_ai_match prompt=%s correlation_id=%s match=%s",
                    prompt_name,
                    correlation_id,
                    substring,
                )
                return AIPrediction(
                    prompt_name=prompt_name,
                    prompt_version="v1-fake",
                    raw_text=json.dumps(structured, ensure_ascii=False),
                    structured=structured,
                )

        logger.info(
            "fake_ai_unmatched prompt=%s correlation_id=%s",
            prompt_name,
            correlation_id,
        )
        empty: Mapping[str, str] = {k: "" for k in empty_keys}
        return AIPrediction(
            prompt_name=prompt_name,
            prompt_version="v1-fake",
            raw_text=json.dumps(empty, ensure_ascii=False),
            structured=empty,
        )
