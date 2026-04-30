from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AflacAddressMasterRecord(BaseModel):
    """`aflac_address_master` の参照用ビュー (突合に使う列のみ)。"""

    model_config = ConfigDict(frozen=True)

    postal_code: str | None
    prefecture_name_kana: str | None
    municipality_name_kana: str | None
    oaza_common_name_kana: str | None
    aza_cho_name_kana: str | None


class JapanPostAddressMasterRecord(BaseModel):
    """`japan_post_address_master` (KEN_ALL) の参照用ビュー。

    Aflac マスタヒット 0 件時のフォールバック (F-05-008 後段) で使う。
    元 Power Automate の `行を一覧にする（郵政住所マスタ）` Select 出力に対応する列を持つ。
    """

    model_config = ConfigDict(frozen=True)

    postal_code: str | None
    prefecture_name: str | None
    municipality_name: str | None
    town_name: str | None
    prefecture_name_kana: str | None
    municipality_name_kana: str | None
    town_name_kana: str | None
