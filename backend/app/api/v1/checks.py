from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.api.deps import get_address_master_match_rule
from app.api.v1.schemas import AddressMasterMatchRequest, AddressMasterMatchResponse
from app.domain.entities.application import Application, ApplicationId
from app.domain.entities.check_context import CheckContext
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
