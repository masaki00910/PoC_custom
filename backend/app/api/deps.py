from __future__ import annotations

from functools import lru_cache

from app.application.run_address_recovery import RunAddressRecovery
from app.config import AIProviderKind, Settings, get_settings
from app.domain.interfaces.address_master_repository import AddressMasterRepository
from app.domain.interfaces.ai_client import AIClient
from app.domain.rules.address.address_kanji_kana_match import AddressKanjiKanaMatchRule
from app.domain.rules.address.address_master_match import AddressMasterMatchRule
from app.domain.rules.contract.existing_contract_match import ExistingContractMatchRule
from app.domain.rules.text.char_limit_check import CharLimitCheckRule
from app.infrastructure.ai.fake_client import FakeAIClient
from app.infrastructure.db.repositories.in_memory_address_master import (
    InMemoryAddressMasterRepository,
)


@lru_cache(maxsize=1)
def _settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_ai_client() -> AIClient:
    settings = _settings()
    match settings.ai.provider:
        case AIProviderKind.FAKE:
            return FakeAIClient()
        case AIProviderKind.BEDROCK_PROXY:
            # T-002 で実装予定。現時点では Fake にフォールバックせず明示エラー
            raise NotImplementedError(
                "BedrockProxyClient は次タスク (T-002) で実装します。"
                "AI__PROVIDER=fake で起動してください。"
            )


@lru_cache(maxsize=1)
def get_address_master_repository() -> AddressMasterRepository:
    return InMemoryAddressMasterRepository()


@lru_cache(maxsize=1)
def get_address_master_match_rule() -> AddressMasterMatchRule:
    return AddressMasterMatchRule(
        ai_client=get_ai_client(),
        address_repo=get_address_master_repository(),
    )


@lru_cache(maxsize=1)
def get_address_kanji_kana_match_rule() -> AddressKanjiKanaMatchRule:
    return AddressKanjiKanaMatchRule(
        ai_client=get_ai_client(),
        master_match_rule=get_address_master_match_rule(),
    )


@lru_cache(maxsize=1)
def get_existing_contract_match_rule() -> ExistingContractMatchRule:
    return ExistingContractMatchRule()


@lru_cache(maxsize=1)
def get_char_limit_check_rule() -> CharLimitCheckRule:
    return CharLimitCheckRule()


@lru_cache(maxsize=1)
def get_run_address_recovery() -> RunAddressRecovery:
    return RunAddressRecovery(
        kanji_kana_match=get_address_kanji_kana_match_rule(),
        existing_contract_match=get_existing_contract_match_rule(),
        char_limit_check=get_char_limit_check_rule(),
    )
