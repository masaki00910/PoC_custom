from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.domain.entities.application import Application, ApplicationId
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckStatus
from app.domain.rules.address.address_kanji_kana_match import AddressKanjiKanaMatchRule
from app.domain.rules.address.address_master_match import AddressMasterMatchRule
from app.infrastructure.ai.fake_client import FakeAIClient
from app.infrastructure.db.repositories.in_memory_address_master import (
    InMemoryAddressMasterRepository,
)


def _build_rule() -> AddressKanjiKanaMatchRule:
    ai_client = FakeAIClient()
    repo = InMemoryAddressMasterRepository()
    master_match = AddressMasterMatchRule(ai_client=ai_client, address_repo=repo)
    return AddressKanjiKanaMatchRule(ai_client=ai_client, master_match_rule=master_match)


def _make_application(address_kanji: str, address_kana: str) -> Application:
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
async def test_ok_consistent_delegates_to_master_match() -> None:
    """整合 OK → そのまま F-05-008 を呼び、Aflac マスタヒットで OK。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application(
            address_kanji="東京都渋谷区神宮前1-2-3",
            address_kana="トウキョウトシブヤクジングウマエ1チョウメ",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.OK
    assert result.document_recovery_value == "150-0001"
    assert result.details["consistency_check_result"] == "OK"
    # 補完は呼ばれていない
    assert "complement_check_result" not in result.details


@pytest.mark.asyncio
async def test_inconsistent_complement_ok_recovers_with_complemented_kana() -> None:
    """整合 NG → 補完 OK → 補完後カナで F-05-008 を呼び OK。"""
    rule = _build_rule()
    # 漢字は神宮前 (ジングウマエ対応) だがカナ側は無関係 (マルノウチ) → 整合 NG
    # 補完で「トウキョウトシブヤクジングウマエ」を生成 → Aflac でヒット
    result = await rule.execute(
        _make_application(
            address_kanji="東京都渋谷区神宮前1-2-3",
            address_kana="トウキョウトチヨダクマルノウチ",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.OK
    assert result.document_recovery_value == "150-0001"
    assert result.details["consistency_check_result"] == "NG"
    assert result.details["complement_check_result"] == "OK"
    assert result.details["complement_kana_value"] == "トウキョウトシブヤクジングウマエ"
    # recovery_reason に補完の reason が prefix されている
    assert "補完" in result.recovery_reason


@pytest.mark.asyncio
async def test_inconsistent_complement_ng_returns_ng() -> None:
    """整合 NG → 補完 NG (漢字フィクスチャ無し) → 補完不可 NG。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application(
            address_kanji="存在しない漢字町",
            address_kana="ジングウマエ",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert result.document_recovery_value is None
    assert result.details["consistency_check_result"] == "NG"
    assert result.details["complement_check_result"] == "NG"
    assert "補完できず" in result.recovery_reason


@pytest.mark.asyncio
async def test_empty_kanji_returns_ng() -> None:
    rule = _build_rule()
    result = await rule.execute(
        _make_application(address_kanji="", address_kana="ジングウマエ"),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "整合チェック不可" in result.recovery_reason


@pytest.mark.asyncio
async def test_empty_kana_returns_ng() -> None:
    rule = _build_rule()
    result = await rule.execute(
        _make_application(address_kanji="東京都渋谷区神宮前", address_kana="   "),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "整合チェック不可" in result.recovery_reason


@pytest.mark.asyncio
async def test_consistent_but_master_match_ng_propagates() -> None:
    """整合 OK でも F-05-008 が NG (郵便番号複数) なら NG が返る。"""
    rule = _build_rule()
    # 丸の内は Aflac マスタに郵便番号 100-0005 と 100-0006 が登録されている前提
    result = await rule.execute(
        _make_application(
            address_kanji="東京都千代田区丸の内1-2-3",
            address_kana="トウキョウトチヨダクマルノウチ1チョウメ",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "郵便番号が複数" in result.recovery_reason
    assert result.details["consistency_check_result"] == "OK"


@pytest.mark.asyncio
async def test_inconsistent_complement_ok_falls_through_to_japan_post() -> None:
    """整合 NG → 補完 OK で「カナガワケン...ウツクシガオカ」生成 →
    Aflac でヒットせず → KEN_ALL フォールバック → OK。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application(
            address_kanji="神奈川県横浜市青葉区美しが丘1丁目",
            address_kana="トウキョウトチヨダクマルノウチ",
        ),
        _make_context(),
    )
    assert result.status is CheckStatus.OK
    assert result.document_recovery_value == "225-0002"
    assert result.details["complement_check_result"] == "OK"
    assert "郵便局住所マスタにて強制回復" in result.recovery_reason
