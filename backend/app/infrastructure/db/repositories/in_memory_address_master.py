from __future__ import annotations

from collections.abc import Sequence

from app.domain.entities.master_data import (
    AflacAddressMasterRecord,
    JapanPostAddressMasterRecord,
)
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

# 郵政住所マスタ (KEN_ALL) フォールバック用の最小データセット。
# Aflac マスタにヒットしない場合の代替検索に使う。
# 商用接続では `database/` リポジトリ管理の `japan_post_address_master` テーブルから取得する。
_JAPAN_POST_FIXTURES: list[JapanPostAddressMasterRecord] = [
    # 横浜市青葉区美しが丘: 単一郵便番号 (フォールバック OK のシナリオ)
    JapanPostAddressMasterRecord(
        postal_code="225-0002",
        prefecture_name="神奈川県",
        municipality_name="横浜市青葉区",
        town_name="美しが丘",
        prefecture_name_kana="カナガワケン",
        municipality_name_kana="ヨコハマシアオバク",
        town_name_kana="ウツクシガオカ",
    ),
    # 港区南青山も KEN_ALL に存在 (Aflac でヒットするのでフォールバックは発動しない)
    JapanPostAddressMasterRecord(
        postal_code="107-0062",
        prefecture_name="東京都",
        municipality_name="港区",
        town_name="南青山",
        prefecture_name_kana="トウキョウト",
        municipality_name_kana="ミナトク",
        town_name_kana="ミナミアオヤマ",
    ),
]


class InMemoryAddressMasterRepository(AddressMasterRepository):
    """住所マスタ (Aflac / 郵政) の In-Memory 実装 (PoC 用)。

    商用接続では SqlAlchemy 実装に差し替える。
    """

    def __init__(
        self,
        aflac_records: Sequence[AflacAddressMasterRecord] | None = None,
        japan_post_records: Sequence[JapanPostAddressMasterRecord] | None = None,
    ) -> None:
        self._aflac_records: Sequence[AflacAddressMasterRecord] = (
            tuple(aflac_records) if aflac_records is not None else tuple(_AFLAC_FIXTURES)
        )
        self._japan_post_records: Sequence[JapanPostAddressMasterRecord] = (
            tuple(japan_post_records)
            if japan_post_records is not None
            else tuple(_JAPAN_POST_FIXTURES)
        )

    async def find_aflac_by_municipality_and_oaza_kana(
        self,
        *,
        municipality_name_kana: str,
        oaza_common_name_kana: str,
    ) -> Sequence[AflacAddressMasterRecord]:
        return tuple(
            r
            for r in self._aflac_records
            if r.municipality_name_kana == municipality_name_kana
            and r.oaza_common_name_kana == oaza_common_name_kana
        )

    async def find_japan_post_by_prefecture_municipality_town(
        self,
        *,
        prefecture_name: str,
        municipality_name: str,
        town_name: str,
    ) -> Sequence[JapanPostAddressMasterRecord]:
        return tuple(
            r
            for r in self._japan_post_records
            if r.prefecture_name == prefecture_name
            and r.municipality_name == municipality_name
            and r.town_name == town_name
        )
