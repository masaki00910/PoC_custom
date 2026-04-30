from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.api.deps import (
    get_address_kanji_kana_match_rule,
    get_address_master_match_rule,
    get_run_address_recovery,
)
from app.api.v1.schemas import (
    AddressKanjiKanaMatchRequest,
    AddressKanjiKanaMatchResponse,
    AddressMasterMatchRequest,
    AddressMasterMatchResponse,
    AddressRecoveryRequest,
    AddressRecoveryResponse,
    CheckResultDTO,
)
from app.application.run_address_recovery import AddressRecoveryInput, RunAddressRecovery
from app.domain.entities.application import Application, ApplicationId
from app.domain.entities.check_context import CheckContext
from app.domain.rules.address.address_kanji_kana_match import AddressKanjiKanaMatchRule
from app.domain.rules.address.address_master_match import AddressMasterMatchRule

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checks", tags=["checks"])


@router.post(
    "/address-master-match",
    response_model=AddressMasterMatchResponse,
    summary="F-05-008 住所マスタ突合 (最小実装)",
)
async def address_master_match(
    request: AddressMasterMatchRequest,
    rule: AddressMasterMatchRule = Depends(get_address_master_match_rule),
) -> AddressMasterMatchResponse:
    correlation_id = request.correlation_id or str(uuid4())

    application = Application(
        application_id=ApplicationId(request.application_id),
        address_kana=request.address_kana,
        address_kanji=request.address_kanji,
    )
    context = CheckContext(
        correlation_id=correlation_id,
        attribute=request.attribute,
        document_item=request.document_item,
    )

    # 監査: 個人情報を含む address_kana 自体はログに出さない (件数・ID のみ)
    logger.info(
        "rule_execute_start rule=%s correlation_id=%s application_id=%s",
        rule.name,
        correlation_id,
        request.application_id,
    )

    result = await rule.execute(application, context)

    logger.info(
        "rule_execute_end rule=%s correlation_id=%s status=%s",
        rule.name,
        correlation_id,
        result.status.value,
    )

    return AddressMasterMatchResponse(
        rule_name=result.rule_name,
        rule_version=result.rule_version,
        status=result.status.value,
        document_item=result.document_item,
        document_recovery_value=result.document_recovery_value,
        recovery_reason=result.recovery_reason,
        recovery_process=result.recovery_process,
        details=dict(result.details),
        correlation_id=correlation_id,
    )


@router.post(
    "/address-kanji-kana-match",
    response_model=AddressKanjiKanaMatchResponse,
    summary="F-05-006 住所漢字・カナ突合 (案A: SharePoint/OCR スキップ)",
)
async def address_kanji_kana_match(
    request: AddressKanjiKanaMatchRequest,
    rule: AddressKanjiKanaMatchRule = Depends(get_address_kanji_kana_match_rule),
) -> AddressKanjiKanaMatchResponse:
    correlation_id = request.correlation_id or str(uuid4())

    application = Application(
        application_id=ApplicationId(request.application_id),
        address_kana=request.address_kana,
        address_kanji=request.address_kanji,
    )
    context = CheckContext(
        correlation_id=correlation_id,
        attribute=request.attribute,
        document_item=request.document_item,
    )

    logger.info(
        "rule_execute_start rule=%s correlation_id=%s application_id=%s",
        rule.name,
        correlation_id,
        request.application_id,
    )

    result = await rule.execute(application, context)

    logger.info(
        "rule_execute_end rule=%s correlation_id=%s status=%s",
        rule.name,
        correlation_id,
        result.status.value,
    )

    return AddressKanjiKanaMatchResponse(
        rule_name=result.rule_name,
        rule_version=result.rule_version,
        status=result.status.value,
        document_item=result.document_item,
        document_recovery_value=result.document_recovery_value,
        recovery_reason=result.recovery_reason,
        recovery_process=result.recovery_process,
        details=dict(result.details),
        correlation_id=correlation_id,
    )


@router.post(
    "/address-recovery",
    response_model=AddressRecoveryResponse,
    summary="F-05-005 住所回復処理オーケストレータ",
)
async def address_recovery(
    request: AddressRecoveryRequest,
    orchestrator: RunAddressRecovery = Depends(get_run_address_recovery),
) -> AddressRecoveryResponse:
    correlation_id = request.correlation_id or str(uuid4())

    application = Application(
        application_id=ApplicationId(request.application_id),
        address_kana=request.address_kana,
        address_kanji=request.address_kanji,
    )
    orchestrator_input = AddressRecoveryInput(
        application=application,
        document_item=request.document_item,
        document_value=request.document_value,
        error_flag=request.error_flag,
        ca_id=request.ca_id,
        correlation_id=correlation_id,
    )

    logger.info(
        "orchestrator_start name=run_address_recovery correlation_id=%s application_id=%s",
        correlation_id,
        request.application_id,
    )

    results = await orchestrator.execute(orchestrator_input)

    logger.info(
        "orchestrator_end name=run_address_recovery correlation_id=%s result_count=%d",
        correlation_id,
        len(results),
    )

    return AddressRecoveryResponse(
        results=[
            CheckResultDTO(
                rule_name=r.rule_name,
                rule_version=r.rule_version,
                status=r.status.value,
                document_item=r.document_item,
                document_recovery_value=r.document_recovery_value,
                recovery_reason=r.recovery_reason,
                recovery_process=r.recovery_process,
                details=dict(r.details),
            )
            for r in results
        ],
        correlation_id=correlation_id,
    )
