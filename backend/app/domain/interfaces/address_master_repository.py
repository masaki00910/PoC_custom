from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.entities.master_data import (
    AflacAddressMasterRecord,
    JapanPostAddressMasterRecord,
)


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

    @abstractmethod
    async def find_japan_post_by_prefecture_municipality_town(
        self,
        *,
        prefecture_name: str,
        municipality_name: str,
        town_name: str,
    ) -> Sequence[JapanPostAddressMasterRecord]:
        """元 Power Automate の `行を一覧にする（郵政住所マスタ）` 相当。

        `ca_prefecture_name` AND `ca_municipality_name` AND `ca_town_name` の完全一致で絞り込む。
        """
        ...
