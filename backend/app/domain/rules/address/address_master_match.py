from __future__ import annotations

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, CheckStatus, Severity
from app.domain.exceptions import AIPredictionError
from app.domain.interfaces.address_master_repository import AddressMasterRepository
from app.domain.interfaces.ai_client import AIClient
from app.domain.rules.address.kana_converter import to_halfwidth_kana
from app.domain.rules.base import CheckRule

PROMPT_KANA_SPLIT = "address_kana_split"
PROMPT_KANJI_SPLIT = "address_kanji_split"

RECOVERY_PROCESS_AFLAC = "エラー回復(AFLAC住所マスタ突合)よりロジック判定"
RECOVERY_PROCESS_JAPAN_POST = "エラー回復(郵便局住所マスタ突合)よりロジック判定"


class AddressMasterMatchRule(CheckRule):
    """F-05-008 住所マスタ突合。

    入力:
        application.address_kana  : 補完後の住所カナ (元 PA の text_4)
        application.address_kanji : 契約申込書住所漢字 (元 PA の text_3, KEN_ALL フォールバック用)

    手順:
        1. AI で住所カナを 4 分割 (都道府県カナ / 市区町村カナ / 大字カナ / 字丁カナ)
        2. Aflac 住所マスタを 市区町村名カナ AND 大字・通称名カナ で絞り込み
        3a. ヒットあり → 郵便番号重複削除 → 1 種類なら OK 回復、複数なら NG
        3b. ヒット 0 件 → 郵政住所マスタ (KEN_ALL) フォールバックへ
        4. KEN_ALL: AI で住所漢字を 3 分割 (都道府県名 / 市区町村名 / 町域名)
        5. 郵政住所マスタを 3 列完全一致で絞り込み
        6a. 1+ 件 → 郵便番号重複削除 → 1 種類なら OK + 半角カナ変換、複数なら NG
        6b. 0 件 → NG (該当〒番号なし)
    """

    name = "address_master_match"
    category = "address"
    severity = Severity.ERROR
    version = "1.1.0"

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
                process=RECOVERY_PROCESS_AFLAC,
            )

        try:
            kana_prediction = await self._ai.predict(
                prompt_name=PROMPT_KANA_SPLIT,
                input_payload={"address_kana": address_kana},
                correlation_id=context.correlation_id,
            )
        except AIPredictionError as e:
            return self._error(
                context,
                reason=f"[{context.attribute}住所(〒)] 住所カナ分割 AI 推論失敗: {e}",
                process=RECOVERY_PROCESS_AFLAC,
            )

        municipality_kana = kana_prediction.structured.get("municipality_kana", "").strip()
        oaza_kana = kana_prediction.structured.get("oaza_kana", "").strip()
        # カナ分割で必須フィールドが取れない場合は Aflac 検索をスキップ。
        # PA フローでも Aflac ヒット 0 件 → KEN_ALL フォールバックに合流するため、
        # ここでは NG 確定せず空シーケンスでフォールスルーする。
        aflac_records: tuple = ()
        if municipality_kana and oaza_kana:
            aflac_records = tuple(
                await self._repo.find_aflac_by_municipality_and_oaza_kana(
                    municipality_name_kana=municipality_kana,
                    oaza_common_name_kana=oaza_kana,
                )
            )
        if aflac_records:
            postal_codes = {r.postal_code for r in aflac_records if r.postal_code}
            if len(postal_codes) == 1:
                postal_code = next(iter(postal_codes))
                return CheckResult(
                    rule_name=self.name,
                    rule_version=self.version,
                    severity=self.severity,
                    status=CheckStatus.OK,
                    document_item=context.document_item,
                    document_recovery_value=postal_code,
                    recovery_reason=f"[{context.attribute}住所(〒)]　AFLAC住所マスタより回復",
                    recovery_process=RECOVERY_PROCESS_AFLAC,
                    details={
                        "ai_prompt_name": kana_prediction.prompt_name,
                        "ai_prompt_version": kana_prediction.prompt_version,
                        "ai_raw_text": kana_prediction.raw_text,
                        "matched_municipality_kana": municipality_kana,
                        "matched_oaza_kana": oaza_kana,
                    },
                )
            return self._ng(
                context,
                reason=(
                    f"[{context.attribute}住所(〒)] "
                    f"AFLAC 住所マスタの郵便番号が複数のため自動回復不可 "
                    f"(候補件数={len(postal_codes)})"
                ),
                process=RECOVERY_PROCESS_AFLAC,
                ai_raw=kana_prediction.raw_text,
            )

        # Aflac ヒット 0 件 → 郵政住所マスタ (KEN_ALL) フォールバック
        return await self._fallback_japan_post(application, context, kana_prediction.raw_text)

    async def _fallback_japan_post(
        self,
        application: Application,
        context: CheckContext,
        kana_ai_raw: str,
    ) -> CheckResult:
        address_kanji = (application.address_kanji or "").strip()
        if not address_kanji:
            # 元 PA フローは契約申込書 (text_3) が必ず渡る前提だが、API 経由では空のことがあり得る
            return self._ng(
                context,
                reason=(
                    f"[{context.attribute}住所(〒)] "
                    f"AFLAC 住所マスタにヒットせず、漢字住所未指定のため郵政マスタフォールバック不可"
                ),
                process=RECOVERY_PROCESS_JAPAN_POST,
                ai_raw=kana_ai_raw,
            )

        try:
            kanji_prediction = await self._ai.predict(
                prompt_name=PROMPT_KANJI_SPLIT,
                input_payload={"address_kanji": address_kanji},
                correlation_id=context.correlation_id,
            )
        except AIPredictionError as e:
            return self._error(
                context,
                reason=f"[{context.attribute}住所(〒・カナ)] 住所漢字分割 AI 推論失敗: {e}",
                process=RECOVERY_PROCESS_JAPAN_POST,
            )

        prefecture_name = kanji_prediction.structured.get("prefecture_name", "").strip()
        municipality_name = kanji_prediction.structured.get("municipality_name", "").strip()
        town_name = kanji_prediction.structured.get("town_name", "").strip()
        if not prefecture_name or not municipality_name or not town_name:
            return self._ng(
                context,
                reason=(
                    f"[{context.attribute}住所(〒・カナ)] "
                    f"住所漢字分割で都道府県/市区町村/町域を特定できず"
                ),
                process=RECOVERY_PROCESS_JAPAN_POST,
                ai_raw=kanji_prediction.raw_text,
            )

        japan_post_records = await self._repo.find_japan_post_by_prefecture_municipality_town(
            prefecture_name=prefecture_name,
            municipality_name=municipality_name,
            town_name=town_name,
        )
        if not japan_post_records:
            return self._ng(
                context,
                reason=f"[{context.attribute}住所(該当〒番号なし)]問合せ",
                process=RECOVERY_PROCESS_JAPAN_POST,
                ai_raw=kanji_prediction.raw_text,
            )

        postal_codes = {r.postal_code for r in japan_post_records if r.postal_code}
        if len(postal_codes) != 1:
            # 元 PA は「ビジネスエラー」 Scope (空) で結果配列に何も追加しない動き。
            # Python では NG として明示する。
            return self._ng(
                context,
                reason=(
                    f"[{context.attribute}住所(〒・カナ)] "
                    f"郵政住所マスタの郵便番号が複数のため自動回復不可 "
                    f"(候補件数={len(postal_codes)})"
                ),
                process=RECOVERY_PROCESS_JAPAN_POST,
                ai_raw=kanji_prediction.raw_text,
            )

        # 1 件に絞れた郵政マスタ行のカナ連結 → 全角→半角カナ変換
        # PA フローでは first(outputs('郵政重複削除')) のカナ列を結合 → MappingList で 1 文字ずつ変換。
        first_record = next(iter(japan_post_records))
        kana_concat = (
            (first_record.prefecture_name_kana or "")
            + (first_record.municipality_name_kana or "")
            + (first_record.town_name_kana or "")
        )
        halfwidth_kana = to_halfwidth_kana(kana_concat)

        postal_code = next(iter(postal_codes))
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.OK,
            document_item=context.document_item,
            document_recovery_value=postal_code,
            recovery_reason=(
                f"[{context.attribute}住所(〒・カナ)]　"
                f"郵便局住所マスタにて強制回復※「字・大字」有の場合は、除外の上、AFLAC住所マスタで要検索"
            ),
            recovery_process=RECOVERY_PROCESS_JAPAN_POST,
            details={
                "ai_prompt_name": kanji_prediction.prompt_name,
                "ai_prompt_version": kanji_prediction.prompt_version,
                "ai_raw_text": kanji_prediction.raw_text,
                "matched_prefecture_name": prefecture_name,
                "matched_municipality_name": municipality_name,
                "matched_town_name": town_name,
                "address_kana_halfwidth": halfwidth_kana,
            },
        )

    def _ng(
        self,
        context: CheckContext,
        *,
        reason: str,
        process: str,
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
            recovery_process=process,
            details=details,
        )

    def _error(self, context: CheckContext, *, reason: str, process: str) -> CheckResult:
        return CheckResult(
            rule_name=self.name,
            rule_version=self.version,
            severity=self.severity,
            status=CheckStatus.ERROR,
            document_item=context.document_item,
            document_recovery_value=None,
            recovery_reason=reason,
            recovery_process=process,
        )
