from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.domain.entities.application import Application, ApplicationId
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckStatus
from app.domain.rules.text.char_limit_check import CharLimitCheckRule


@pytest.mark.asyncio
async def test_stub_returns_ng_with_todo_marker() -> None:
    rule = CharLimitCheckRule()
    application = Application(
        application_id=ApplicationId(UUID("11111111-2222-3333-4444-555555555555")),
        address_kana="トウキョウト",
        address_kanji="東京都",
    )
    context = CheckContext(
        correlation_id=str(uuid4()),
        attribute="契約者",
        document_item="02_policyholder_postal_code",
    )

    result = await rule.execute(application, context)

    assert result.status is CheckStatus.NG
    assert result.document_recovery_value is None
    assert result.details["stub"] == "true"
    assert result.details["todo_task"] == "T-006"
    assert "未実装" in result.recovery_reason
