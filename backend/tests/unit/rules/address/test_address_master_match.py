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


def _make_application(address_kana: str) -> Application:
    return Application(
        application_id=ApplicationId(UUID("11111111-2222-3333-4444-555555555555")),
        address_kana=address_kana,
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
async def test_ng_ai_cannot_split() -> None:
    """フィクスチャに含まれない住所カナは AI 分割で空フィールドとなり NG。"""
    rule = _build_rule()
    result = await rule.execute(
        _make_application("ヘンナジュウショ"),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert "住所カナ分割" in result.recovery_reason


@pytest.mark.asyncio
async def test_ng_empty_address_kana() -> None:
    rule = _build_rule()
    result = await rule.execute(
        _make_application("   "),
        _make_context(),
    )
    assert result.status is CheckStatus.NG
    assert result.document_recovery_value is None
