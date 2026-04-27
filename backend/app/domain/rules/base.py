from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.application import Application
from app.domain.entities.check_context import CheckContext
from app.domain.entities.check_result import CheckResult, Severity


class CheckRule(ABC):
    """1 業務観点 = 1 クラス。Power Automate の 1 フローを Python に移植する単位。"""

    name: str
    category: str
    severity: Severity
    version: str

    @abstractmethod
    async def execute(
        self,
        application: Application,
        context: CheckContext,
    ) -> CheckResult:
        ...
