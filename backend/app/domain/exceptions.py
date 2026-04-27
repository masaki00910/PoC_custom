from __future__ import annotations


class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class RuleExecutionError(DomainError):
    pass


class AIPredictionError(DomainError):
    pass


class MasterDataLookupError(DomainError):
    pass
