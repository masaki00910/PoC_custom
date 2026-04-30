from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.application.run_address_recovery import (
    AddressRecoveryInput,
    RunAddressRecovery,
)
from app.domain.entities.application import Application, ApplicationId
from app.domain.entities.check_result import CheckStatus
from app.domain.rules.address.address_kanji_kana_match import AddressKanjiKanaMatchRule
from app.domain.rules.address.address_master_match import AddressMasterMatchRule
from app.domain.rules.contract.existing_contract_match import ExistingContractMatchRule
from app.domain.rules.text.char_limit_check import CharLimitCheckRule
from app.infrastructure.ai.fake_client import FakeAIClient
from app.infrastructure.db.repositories.in_memory_address_master import (
    InMemoryAddressMasterRepository,
)


def _build_orchestrator() -> RunAddressRecovery:
    ai = FakeAIClient()
    repo = InMemoryAddressMasterRepository()
    master_match = AddressMasterMatchRule(ai_client=ai, address_repo=repo)
    kanji_kana = AddressKanjiKanaMatchRule(ai_client=ai, master_match_rule=master_match)
    return RunAddressRecovery(
        kanji_kana_match=kanji_kana,
        existing_contract_match=ExistingContractMatchRule(),
        char_limit_check=CharLimitCheckRule(),
    )


def _make_input(
    *,
    document_value: str = "000",
    error_flag: bool = False,
    ca_id: str = "住所漢字・カナ突合チェック",
    document_item: str = "02_policyholder_postal_code",
    address_kanji: str = "東京都渋谷区神宮前1-2-3",
    address_kana: str = "トウキョウトシブヤクジングウマエ1チョウメ",
) -> AddressRecoveryInput:
    application = Application(
        application_id=ApplicationId(UUID("11111111-2222-3333-4444-555555555555")),
        address_kana=address_kana,
        address_kanji=address_kanji,
    )
    return AddressRecoveryInput(
        application=application,
        document_item=document_item,
        document_value=document_value,
        error_flag=error_flag,
        ca_id=ca_id,
        correlation_id=str(uuid4()),
    )


# --- 郵便番号 "000" ルート ---


@pytest.mark.asyncio
async def test_postal_zero_with_existing_contract_falls_back_to_kanji_kana_match() -> None:
    """document_value=000 + 既契約突合 ca_id → Stub NG → F-05-006 にフォールバックして OK 回復。"""
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_value="000",
            ca_id="住所既契約突合チェック",
        )
    )
    assert len(results) == 2
    assert results[0].rule_name == "existing_contract_match"
    assert results[0].status is CheckStatus.NG
    assert results[0].details["stub"] == "true"
    # フォールバック側 (F-05-006 → F-05-008) で OK 回復
    assert results[1].rule_name == "address_kanji_kana_match"
    assert results[1].status is CheckStatus.OK
    assert results[1].document_recovery_value == "150-0001"


@pytest.mark.asyncio
async def test_postal_star_zero_treated_same_as_zero() -> None:
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(document_value="*000", ca_id="住所既契約突合チェック")
    )
    assert len(results) == 2


@pytest.mark.asyncio
async def test_postal_zero_without_existing_contract_ca_id_returns_empty() -> None:
    """document_value=000 だが ca_id が住所既契約突合でない → 元 PA は空アクション (= 空配列)。"""
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(document_value="000", ca_id="その他のチェック")
    )
    assert results == []


# --- error_flag ルート ---


@pytest.mark.asyncio
async def test_error_flag_with_kanji_kana_match_invokes_f06() -> None:
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_value="123-4567",
            error_flag=True,
            ca_id="住所漢字・カナ突合チェック",
        )
    )
    assert len(results) == 1
    assert results[0].rule_name == "address_kanji_kana_match"
    assert results[0].status is CheckStatus.OK


@pytest.mark.asyncio
async def test_error_flag_without_kanji_kana_ca_id_returns_empty() -> None:
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_value="123-4567",
            error_flag=True,
            ca_id="その他",
        )
    )
    assert results == []


# --- 文字数超過ルート ---


@pytest.mark.asyncio
async def test_no_error_flag_with_char_limit_invokes_stub() -> None:
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_value="123-4567",
            error_flag=False,
            ca_id="文字数超過チェック",
        )
    )
    assert len(results) == 1
    assert results[0].rule_name == "char_limit_check"
    assert results[0].status is CheckStatus.NG
    assert results[0].details["todo_task"] == "T-006"


@pytest.mark.asyncio
async def test_no_error_flag_without_char_limit_ca_id_returns_empty() -> None:
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_value="123-4567",
            error_flag=False,
            ca_id="その他",
        )
    )
    assert results == []


# --- document_item Switch (属性決定) ---


@pytest.mark.asyncio
async def test_unknown_document_item_returns_empty() -> None:
    """document_item が PA Switch の case に該当しない場合は空配列 (default 空アクション)。"""
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_item="99_unknown_item",
            document_value="000",
            ca_id="住所既契約突合チェック",
        )
    )
    assert results == []


@pytest.mark.asyncio
async def test_insured_document_item_resolves_attribute() -> None:
    orch = _build_orchestrator()
    results = await orch.execute(
        _make_input(
            document_item="02_insured_postal_code",
            document_value="123-4567",
            error_flag=True,
            ca_id="住所漢字・カナ突合チェック",
        )
    )
    assert len(results) == 1
    assert "被保険者" in results[0].recovery_reason
