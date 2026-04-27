from __future__ import annotations

from collections.abc import Sequence

from app.domain.entities.master_data import AflacAddressMasterRecord
from app.domain.interfaces.address_master_repository import AddressMasterRepository

# PoC 動作確認用の最小データセット。
# 商用接続では `database/` リポジトリ管理の `aflac_address_master` テーブルから取得する。
_AFLAC_FIXTURES: list[AflacAddressMasterRecord] = [
    AflacAddressMasterRecord(
        postal_code="150-0001",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="シブヤク",
        oaza_common_name_kana="ジングウマエ",
        aza_cho_name_kana=None,
    ),
    AflacAddressMasterRecord(
        postal_code="160-0021",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="シンジュクク",
        oaza_common_name_kana="カブキチョウ",
        aza_cho_name_kana=None,
    ),
    # 同じ大字に複数行 (字丁違い) 存在するが郵便番号は同一 → 重複削除後 1 件で OK 経路
    AflacAddressMasterRecord(
        postal_code="107-0062",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="ミナトク",
        oaza_common_name_kana="ミナミアオヤマ",
        aza_cho_name_kana="1チョウメ",
    ),
    AflacAddressMasterRecord(
        postal_code="107-0062",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="ミナトク",
        oaza_common_name_kana="ミナミアオヤマ",
        aza_cho_name_kana="2チョウメ",
    ),
    # 千代田区丸の内: 同じ大字に異なる郵便番号 → 自動回復不可 (NG 経路の検証用)
    AflacAddressMasterRecord(
        postal_code="100-0005",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="チヨダク",
        oaza_common_name_kana="マルノウチ",
        aza_cho_name_kana="1チョウメ",
    ),
    AflacAddressMasterRecord(
        postal_code="100-6390",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="チヨダク",
        oaza_common_name_kana="マルノウチ",
        aza_cho_name_kana="2チョウメ",
    ),
]


class InMemoryAddressMasterRepository(AddressMasterRepository):
    """`aflac_address_master` の In-Memory 実装 (PoC 用)。

    商用接続では SqlAlchemy 実装に差し替える。
    """

    def __init__(
        self,
        records: Sequence[AflacAddressMasterRecord] | None = None,
    ) -> None:
        self._records: Sequence[AflacAddressMasterRecord] = (
            tuple(records) if records is not None else tuple(_AFLAC_FIXTURES)
        )

    async def find_aflac_by_municipality_and_oaza_kana(
        self,
        *,
        municipality_name_kana: str,
        oaza_common_name_kana: str,
    ) -> Sequence[AflacAddressMasterRecord]:
        return tuple(
            r
            for r in self._records
            if r.municipality_name_kana == municipality_name_kana
            and r.oaza_common_name_kana == oaza_common_name_kana
        )
