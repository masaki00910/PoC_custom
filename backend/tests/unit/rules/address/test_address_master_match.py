from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.domain.entities.application import Application, ApplicationId
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckStatus
from app.domain.rules.address.address_master_match import AddressMasterMatchRule
from app.infrastructure.ai.fake_client import FakeAIClient
from app.infrastructure.db.repositories.in_memory_address_master import (
    InMemoryAddressMasterRepository,
)


def _build_rule() -> AddressMasterMatchRule:
    return AddressMasterMatchRule(
        ai_client=FakeAIClient(),
        address_repo=InMemoryAddressMasterRepository(),
    )


def _make_application(address_kana: str, address_kanji: str = "") -> Application:
    return Application(
        application_id=ApplicationId(UUID("11111111-2222-3333-4444-555555555555")),
        address_kana=address_kana,
        address_kanji=address_kanji,
    )


def _make_context() -> CheckContext:
    return CheckContext(
        correlation_id=str(uuid4()),
        attribute="新",
        document_item="申込書住所カナ",
    )


@pytest.mark.asyncio
async def test_ok_single_record_recovers_postal_code() -> None:
    rule = _build_rule()
    result = await rule.execute(
        _make_application("トウキョウトシブヤクジングウマエ1チョウメ"),
        _make_context(),
    )
    assert result.status is CheckStatus.OK
    assert result.document_recovery_value == "150-0001"
    assert "AFLAC住所マスタより回復" in result.recovery_reason
    assert "AFLAC住所マスタ突合" in result.recovery_process


@pytest.mark.asyncio
async def test_ok_multiple_records_same_postal_code_dedup() -> None:
    """同じ大字に複数行 (字丁違い) あるが郵便番号が一意なら OK で回復する。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application("トウキョウトミナトクミナミアオヤマ2チョウメ"),
        _make_context(),
    )
    assert result.status is CheckStatus.OK
    assert result.document_recovery_value == "107-0062"


@pytest.mark.asyncio
async def test_ng_multiple_postal_codes() -> None:
    """同じ大字に異なる郵便番号があるケースは自動回復不可で NG。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application("トウキョウトチヨダクマルノウチ1チョウメ"),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert result.document_recovery_value is None
    assert "郵便番号が複数" in result.recovery_reason


@pytest.mark.asyncio
async def test_ng_ai_cannot_split_falls_through_to_japan_post() -> None:
    """カナ分割で必須フィールドが空 → Aflac はスキップ → KEN_ALL フォールバックに合流。

    address_kanji 未指定なので KEN_ALL 側で「漢字住所未指定」NG になる。
    """
    rule = _build_rule()
    result = await rule.execute(
        _make_application("ヘンナジュウショ"),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "漢字住所未指定" in result.recovery_reason


@pytest.mark.asyncio
async def test_ng_empty_address_kana() -> None:
    rule = _build_rule()
    result = await rule.execute(
        _make_application("   "),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert result.document_recovery_value is None


# --- T-003 (KEN_ALL フォールバック) ---


@pytest.mark.asyncio
async def test_japan_post_fallback_ok_recovers_with_halfwidth_kana() -> None:
    """Aflac マスタに存在しない住所だが KEN_ALL に存在 → 郵政マスタフォールバックで OK。"""
    rule = _build_rule()
    # 住所カナは Aflac でヒットしないものを指定し、漢字側で郵政マスタにヒットさせる
    result = await rule.execute(
        _make_application(
            address_kana="カナガワケンヨコハマシアオバクウツクシガオカ",
            address_kanji="神奈川県横浜市青葉区美しが丘1丁目",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.OK
    assert result.document_recovery_value == "225-0002"
    assert "郵便局住所マスタにて強制回復" in result.recovery_reason
    assert "郵便局住所マスタ突合" in result.recovery_process
    # 半角カナ変換結果が details に格納される (F-05-007 文字数超過チェック の入力)
    assert result.details["address_kana_halfwidth"] == "ｶﾅｶﾞﾜｹﾝﾖｺﾊﾏｼｱｵﾊﾞｸｳﾂｸｼｶﾞｵｶ"


@pytest.mark.asyncio
async def test_japan_post_fallback_ng_no_match() -> None:
    """Aflac でも KEN_ALL でもヒットせず → NG (該当〒番号なし)。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application(
            address_kana="ソンザイシナイジュウショ",
            address_kanji="東京都存在しない区存在しない町1丁目",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "該当〒番号なし" in result.recovery_reason
    assert "郵便局住所マスタ突合" in result.recovery_process


@pytest.mark.asyncio
async def test_japan_post_fallback_blocked_when_kanji_missing() -> None:
    """Aflac で 0 件ヒット時に address_kanji が未指定なら、KEN_ALL に進めず NG。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application(
            address_kana="カナガワケンヨコハマシアオバクウツクシガオカ",
            address_kanji="",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "漢字住所未指定" in result.recovery_reason
