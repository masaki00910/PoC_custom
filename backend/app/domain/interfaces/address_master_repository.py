from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.entities.master_data import AflacAddressMasterRecord


class AddressMasterRepository(ABC):
    """住所マスタ参照抽象。

    PoC では `InMemoryAddressMasterRepository` を使用。
    本番では `database/` リポジトリのスキーマに対応する SqlAlchemy 実装に差し替え。
    """

    @abstractmethod
    async def find_aflac_by_municipality_and_oaza_kana(
        self,
        *,
        municipality_name_kana: str,
        oaza_common_name_kana: str,
    ) -> Sequence[AflacAddressMasterRecord]:
        """元 Power Automate の `行を一覧にする（Aflac住所マスタ）` 相当。"""
        ...
